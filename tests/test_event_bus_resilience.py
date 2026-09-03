from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import pytest

from lab28_platform.contracts import IngestionEvent
from lab28_platform.event_bus import BatchConsumer, dead_letter_count
from lab28_platform.settings import KafkaSettings


@dataclass
class _Message:
    payload: bytes

    def error(self) -> None:
        return None

    def headers(self) -> list[tuple[str, bytes]]:
        return []

    def value(self) -> bytes:
        return self.payload

    def topic(self) -> str:
        return "data.raw"

    def partition(self) -> int:
        return 0

    def offset(self) -> int:
        return 7

    def key(self) -> bytes:
        return b"event-key"


class _DelayedAssignmentConsumer:
    def __init__(self, event: IngestionEvent) -> None:
        self.poll_count = 0
        self.event = event

    def assignment(self) -> list[str]:
        return ["data.raw-0"] if self.poll_count >= 5 else []

    def poll(self, _timeout: float) -> _Message | None:
        self.poll_count += 1
        if self.poll_count == 6:
            return _Message(self.event.model_dump_json().encode())
        return None


def _kafka_settings() -> KafkaSettings:
    return KafkaSettings(
        bootstrap_servers="kafka:9092",
        topic_raw="data.raw",
        topic_processed="data.processed",
        topic_model_events="model.events",
        topic_dlq="data.raw.dlq",
        group_id="lab28-pipeline",
        max_delivery_attempts=3,
        delivery_timeout_seconds=10,
    )


def test_poll_batch_waits_for_delayed_group_assignment() -> None:
    event = IngestionEvent(
        event_id="event-0001",
        idempotency_key="event-key",
        entity_id="asker-1",
        payload={"kind": "feedback", "asker_id": "asker-1", "text": "useful", "rating": 5},
    )
    batch = BatchConsumer.__new__(BatchConsumer)
    batch._consumer = _DelayedAssignmentConsumer(event)

    decoded, poison = batch.poll_batch(10, idle_polls=3, poll_timeout=0, startup_polls=8)

    assert [message.event.event_id for message in decoded] == ["event-0001"]
    assert poison == []


def test_dead_letter_count_retries_transient_watermark_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Consumer:
        attempts = 0
        closed = False

        def __init__(self, _config: dict[str, Any]) -> None:
            pass

        def list_topics(self, _topic: str, *, timeout: float) -> SimpleNamespace:
            assert timeout == 0.01
            partition = SimpleNamespace()
            topic = SimpleNamespace(error=None, partitions={0: partition})
            return SimpleNamespace(topics={"data.raw.dlq": topic})

        def get_watermark_offsets(self, _partition: Any, *, timeout: float) -> tuple[int, int]:
            assert timeout == 0.01
            Consumer.attempts += 1
            if Consumer.attempts < 3:
                raise RuntimeError("coordinator loading")
            return 2, 9

        def close(self) -> None:
            Consumer.closed = True

    monkeypatch.setattr("lab28_platform.event_bus.Consumer", Consumer)
    monkeypatch.setattr("lab28_platform.event_bus.time.sleep", lambda _seconds: None)

    assert dead_letter_count(_kafka_settings(), timeout=0.01) == 7
    assert Consumer.attempts == 3
    assert Consumer.closed is True


def test_dead_letter_count_does_not_hide_persistent_broker_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Consumer:
        def __init__(self, _config: dict[str, Any]) -> None:
            pass

        def list_topics(self, _topic: str, *, timeout: float) -> None:
            raise RuntimeError("broker unavailable")

        def close(self) -> None:
            pass

    monkeypatch.setattr("lab28_platform.event_bus.Consumer", Consumer)
    monkeypatch.setattr("lab28_platform.event_bus.time.sleep", lambda _seconds: None)

    with pytest.raises(RuntimeError, match="broker unavailable"):
        dead_letter_count(_kafka_settings(), timeout=0.01)
