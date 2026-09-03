from __future__ import annotations

import json

import httpx

from lab28_platform.llm_client import VLLMClient
from lab28_platform.settings import VLLMSettings


def _settings(*, enable_thinking: bool = False) -> VLLMSettings:
    return VLLMSettings(
        base_url="http://vllm.test/v1",
        model_id="Qwen/Qwen3-0.6B",
        api_key_env="TEST_VLLM_KEY",
        timeout_seconds=5.0,
        max_tokens=96,
        temperature=0.2,
        enable_thinking=enable_thinking,
        require_real=True,
    )


def test_completion_disables_thinking_for_a_bounded_local_token_budget() -> None:
    observed: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        observed.update(json.loads(request.content))
        return httpx.Response(
            200,
            request=request,
            json={
                "model": "Qwen/Qwen3-0.6B",
                "choices": [
                    {
                        "message": {"content": "Câu trả lời [1]."},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            },
        )

    client = VLLMClient(_settings())
    client._client.close()
    client._client = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        completion = client.complete("system", "question")
    finally:
        client.close()

    assert observed["chat_template_kwargs"] == {"enable_thinking": False}
    assert completion.finish_reason == "stop"
    assert completion.text == "Câu trả lời [1]."


def test_thinking_mode_is_an_explicit_environment_switch(monkeypatch) -> None:
    monkeypatch.setenv("LAB28_VLLM_ENABLE_THINKING", "true")

    assert VLLMSettings.from_env().enable_thinking is True
