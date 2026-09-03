# Individual demo script — Ong Xuan Son

## Evidence rule

Every live claim is tied to a timestamp plus a request, run, trace, Delta, or
MLflow identifier. A green process status by itself is not accepted as proof.
GPU, LangSmith, and live Kubernetes gates are reported `UNVERIFIED` when their
required endpoint, credential, or cluster is not legitimately available.
For this run the LangSmith credential was supplied locally and its gate passed.
Kind/Argo CD live sync, self-heal and Git rollback were also verified; only the
GPU-backed vLLM gate remains `UNVERIFIED`.

## 1. Architecture and ownership

Open `ARCHITECTURE.md` and follow IP01-IP10 from the gateway to the data/ML
plane and then the observability plane. State that this is an individual
submission while preserving component ownership for incident routing.

## 2. Happy path

1. Show `docker compose --profile full ps` and `lab28 ready`.
2. Submit document and feedback through the gateway, not directly to Kafka.
3. Record the response request ID, idempotency key, and trace ID.
4. Match the Kafka header and record offset in `ip01-kafka-consume.json`.
5. Match the Airflow DAG run ID and asset event in `ip02-airflow-run.json`.
6. Show the Delta table version/history and retained row.
7. Show Feast's entity row, freshness, and originating Delta version.
8. Show the deterministic Qdrant document ID and scored retrieval result.
9. Resolve the MLflow `champion` and match its run/version to answer evidence.
10. If a real vLLM is configured, match `/version`, served model, native metrics,
    and the model echoed by the response.

## 3. Trace and golden signals

Search Jaeger by the exact trace ID and show all required span names across at
least four services. Compare trace IDs, not span IDs. In Grafana/Prometheus show
request rate, errors, duration, saturation, Kafka lag, readiness, the loaded SLO
alert, and zero OTel exporter failures.

## 4. Incident and recovery

Use the automated J4 scenario and narrate the hypothesis first:

- Feast outage is optional and must be visible as `degraded`; an answer remains
  available without online features.
- Qdrant outage is mandatory and must become `not_ready`; the gateway removes
  the pod from routing while direct liveness remains available.
- An unparseable event is parked in the DLQ without failing a valid event in the
  same batch. Replay is manual and occurs only after the defect is fixed.

Recovery proof compares the baseline and final readiness, Delta row/version,
Qdrant point count, Kafka/DLQ offsets, and successful Feast lookup. Never use
`down -v` or reset during the incident.

## 5. Promotion and rollback

Create a release with a distinct prompt version, show its signature and
provenance tags, move `champion`, and demonstrate that serving follows the alias
without restart. Run rollback, resolve the previous complete release, and show
that serving follows it. Rollback changes model desired state, not source code.

## 6. Performance

Compare 8 and 16 workers after warm-up. Present P50/P95/P99, errors, API CPU/RAM,
Kafka lag, and vLLM queue/token metrics when available. Name the observed
bottleneck and explicitly avoid extrapolating laptop throughput to production.

## 7. GitOps

Show manifest validation, the immutable image/revision diff, Argo CD sync health,
a deliberately scoped drift and self-heal, then a desired-state revert. Finish
with replicas, gateway, readiness, and trace smoke checks. If no cluster exists,
show static validation and mark live drift/rollback `UNVERIFIED`.

## 8. Q&A prompts

- Delivery guarantee and the exact offset-commit point.
- State owner and recovery signal at every boundary.
- Why Feast degrades while Qdrant fails closed.
- Release/data/model provenance needed for incident review.
- SLO, alert action, security controls, GPU cost, and production gaps.
