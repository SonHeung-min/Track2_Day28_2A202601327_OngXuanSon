# Lab 28 reflection and production-readiness answers

## Engineering trade-offs

### Why at-least-once Kafka plus idempotency?

At-least-once delivery avoids losing an accepted event when a consumer fails
between processing and offset commit. Duplicates are handled at the state
boundary rather than hidden in transport: Delta MERGE uses the idempotency key,
Feast derives one entity update from the deduplicated table, and Qdrant uses a
stable UUID from `doc_id`. The cost is extra storage/compute for redelivery and
the requirement that every downstream write remain idempotent.

### Why commit after Delta MERGE?

Committing first creates an unrecoverable loss window: Kafka would consider a
message consumed even if the durable write failed. Committing after MERGE can
repeat work after a crash, but the deterministic merge source turns that repeat
into a safe update. Invalid payloads are parked in the DLQ; transient dependency
failures are retried rather than mislabeled as bad data.

### Why separate Delta, Feast, and Qdrant paths?

Delta is the auditable offline source and preserves versions/time travel. Feast
serves low-latency entity features with freshness metadata. Qdrant serves vector
retrieval and uses deterministic point identity. Keeping the contracts separate
prevents an online cache from becoming the system of record and makes each
failure attributable to an owner.

### Why distinguish `ready`, `degraded`, and `not_ready`?

Liveness only says the process can answer HTTP. Readiness protects traffic when
a mandatory dependency cannot support a valid answer. Optional failure remains
visible as `degraded`, allowing a reduced-quality response without removing all
healthy pods from rotation. A mandatory failure is `not_ready` and returns 503
so the gateway fails closed.

### Why use an MLflow alias for promotion and rollback?

A release includes prompt version, vLLM model ID, embedding model ID, Qdrant
collection, feature service, retrieval parameters, Delta version, signature,
run ID, and Git provenance. Moving the `champion` alias changes one complete,
auditable bundle. Serving resolves the alias at request time, so promotion and
rollback do not require a code edit or process restart.

### Why require real-vLLM identity?

OpenAI-compatible JSON alone does not prove the intended inference engine is in
use. The gate therefore combines `/version`, the configured model in
`/v1/models`, and native `vllm:` Prometheus series. When no legitimate GPU
endpoint is available, the submission reports the gate as `UNVERIFIED` instead
of substituting a mock.

### Why local OTLP evidence plus an optional LangSmith leg?

Jaeger provides deterministic, credential-free evidence for local testing. The
same collector can export to LangSmith when a legitimate API key is supplied.
This keeps trace-continuity testing reproducible while making the external gate
explicit and preventing secrets from entering the repository.

## SLO and operational interpretation

The primary serving indicators are request rate, error rate, duration, and
saturation. Kafka consumer lag measures asynchronous freshness; feature
freshness and Delta version connect online responses back to durable data. A
useful alert must identify a user-impacting symptom, carry severity and context,
and point to an owner/runbook. Readiness is a traffic-control signal, not a
substitute for an SLO.

Load-test conclusions are valid only with hardware, model, corpus, warm-up,
request count, concurrency, degraded policy, and P50/P95/P99 recorded. Laptop
results are a comparative profile and are not a claim of production capacity.

## Security and privacy

- Secrets belong in environment injection or a secret manager, never Git,
  ConfigMap, notebook output, screenshots, or evidence JSON.
- The API container runs non-root with a read-only filesystem, no privilege
  escalation, and all Linux capabilities dropped.
- NetworkPolicy narrows ingress to the gateway and limits egress; production
  additionally requires TLS/mTLS, authenticated clients, authorization, audit
  retention, and controlled egress to external inference/tracing endpoints.
- Evidence retains identifiers, versions, statuses, and hashes rather than user
  text. Runtime databases, caches, `.lab28/`, and model weights are excluded.

## Production gaps

The lab is a production-readiness demonstration, not a complete production
deployment. Remaining work includes multi-broker Kafka and tested backup/DR;
object storage plus a production Delta catalog and concurrency controls;
managed databases for Airflow/MLflow/Feast; HA Qdrant with snapshots; end-to-end
TLS, identity/RBAC and secret rotation; image signing/SBOM and vulnerability
policy; alert routing and on-call ownership; autoscaling from workload metrics;
GPU capacity/cost controls; model safety, quality and drift evaluation; retention
and deletion policy; multi-zone failure testing; and capacity tests on target
hardware with representative traffic.

## GitOps decision

Deploy immutable images and change only desired state in Git. Argo CD detects
drift and self-heals it. Rollback reverts the desired Git revision or image tag,
then verifies replicas, gateway routing, readiness, and trace continuity. Live
edits are diagnostic only and must never become undocumented desired state.

The checked-in Argo CD Application points at the accessible personal repository
and an immutable, live-validated rollback commit. The recorded Kind exercise
proved sync, drift self-heal, and desired-state rollback through a Git revert;
workload dependency health is reported separately and was not fabricated.

## Contribution

This is an individual submission by Ong Xuan Son. The contributor implemented
and verified the student-owned IP01/IP03/IP04/IP07-IP08 functions and owns the
end-to-end validation, evidence collection, incident exercise, performance
analysis, Kubernetes/GitOps explanation, documentation, and demo narrative for
IP01-IP10.
