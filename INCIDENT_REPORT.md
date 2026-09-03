# Failure and recovery record

## Scope

This record comes from the live `IT-J4-degraded-recovery` journey on 2026-09-03.
Its focused run completed with `9 passed, 4 deselected`. After the recovery and
idempotent-trigger hardening, the final combined non-GPU/non-LangSmith suite
completed with `56 passed, 16 deselected`. The LangSmith gate was then supplied
legitimately and passed separately; the remaining unavailable assertions require
the environment-gated real vLLM service.

## Dependency outages

| Injection | Expected signal | Observed behavior | Recovery proof |
|---|---|---|---|
| Stop Feast | Optional dependency is unavailable | API readiness reported `degraded`; policy evaluation remained stable | Feast restarted healthy and the final readiness verdict matched the baseline |
| Stop Qdrant | Mandatory retrieval dependency is unavailable | Direct API readiness failed closed and Envoy stopped routing to the unready API | Qdrant restarted healthy; direct and gateway readiness recovered |

The test fixtures restore each container in a `finally` block, so an assertion
failure cannot leave the platform intentionally degraded.

## Poison event and DLQ

- Poison-batch Airflow run: `it-4ee80404`.
- Valid companion entity: `it-j4-cea7ad6e`.
- Drain result: polled 2, processed 1, dead-lettered 1.
- Delta feedback version after the batch: 7.
- The exact invalid bytes were retained in the DLQ envelope and the valid companion
  record reached Delta in the same batch.

This proves that one unparseable event is isolated rather than dropping or failing
the complete batch.

## Replay and no-data-loss proof

- Replay Airflow run: `it-3d0368bc`.
- Replayed entity: `it-j4-replay-8f9fdb97`.
- Drain result: polled 3, processed 2, dead-lettered 0.
- Delta feedback version after replay: 8.
- The replay command refused to reinject a payload that still could not be parsed.
- The well-formed replay reached Delta and the journey asserted exactly one row for
  its idempotency key after replay.

The platform ended with all Compose services healthy and with the same readiness
verdict it had before fault injection. This is at-least-once delivery plus
idempotent merge, not an exactly-once claim.

## Reliability corrections discovered during the combined run

Two cross-journey races were corrected without weakening the acceptance tests:

- The Kafka consumer now gives initial group assignment a bounded grace period
  and only stops after consecutive idle polls. This prevents a successful but
  empty DAG run while the coordinator is loading.
- An Airflow trigger reuses one `dag_run_id`; after a response timeout the client
  first queries that ID before retrying. This resolves the ambiguous POST outcome
  and prevents an unobserved run from consuming the next journey's records.

The final combined suite (`56 passed`) is the regression proof for both changes.
