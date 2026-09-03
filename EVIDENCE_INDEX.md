# Evidence index

Runtime evidence is generated under `evidence/`. `.gitignore` denies new files
there by default and explicitly permits only the reviewed submission artifacts
listed below. This keeps credentials, databases, caches and transient dumps out
of Git while allowing the required evidence to travel with the GitHub submission.

| Integration point | Required artifact | Generator |
|---|---|---|
| IP01 | `evidence/ip01-kafka-consume.json` | J1 golden-path test |
| IP02 | `evidence/ip02-airflow-run.json` | J1 golden-path test |
| IP03 | `evidence/ip03-delta-history.json` | `lab28 evidence` |
| IP04 | `evidence/ip04-feast-online.json` | J1 golden-path test |
| IP05 | `evidence/ip05-qdrant-search.json` | `lab28 evidence` |
| IP06 | `evidence/ip06-mlflow-release.json` | J3 promotion/rollback test |
| IP07 | `evidence/ip07-vllm-identity.json` | `lab28 evidence` with real vLLM |
| IP08 | `evidence/ip08-gateway.json` | gateway rate-limit test |
| IP09 | `evidence/ip09-prometheus-targets.json` | Prometheus target test |
| IP09 | `evidence/ip09-grafana-dashboards.json` | Grafana provisioning test |
| IP10 | `evidence/ip10-trace.json` | trace-span coverage test |
| IP10 | `evidence/ip10-langsmith-export.json` | LangSmith gate and collector counters |
| GitOps | `evidence/gitops-live.json` | Kind/Argo sync, drift, self-heal and Git revert |
| Summary | `evidence/integration-report.json` | `lab28 evidence` |
| Fast suite | `evidence/fast-suite.txt` | `uv run pytest tests -q` |

The final review checks that IP01 has `traceparent`, IP02 has a successful run
and asset event, IP03 has history/time travel, IP04 has freshness and
`delta_version`, IP05 has deterministic IDs and scores, IP06 has provenance,
IP07 reports `is_real_vllm=true` **only when its GPU gate is actually run**, IP08
contains both 200 and 429 plus request ID,
IP09 has healthy targets/dashboard/alert, and IP10 contains every required span
under one trace ID with no error status.

On 2026-09-03 the 4 GB RTX 3050 laptop ran vLLM 0.8.5 with
`Qwen/Qwen3-0.6B`. IP07 records `is_real_vllm=true`, the served model, and 81
native `vllm:` metrics. A gateway RAG request returned a grounded answer with
the MLflow release and trace ID; no OpenAI-shaped mock was used. The in-process
summary remains 83 because it deliberately cannot self-probe the
external Airflow, gateway, dashboard, and trace evidence for IP02/IP08/IP09/IP10;
those JSON artifacts were produced separately by the live tests. The non-gated
integration suite still completed with `56 passed, 16 deselected`. The separately
gated LangSmith test subsequently completed with `1 passed, 71 deselected`; the
collector exported spans to Jaeger and `otlphttp/langsmith` with zero observed
LangSmith send failures.
