# Kubernetes and GitOps validation

## Verified locally

On 2026-09-03 the repository validators reported:

```text
Kubernetes and GitOps manifest contracts passed
OK    supported workflow is host-path and shell independent
```

The checked manifests include namespace and service account isolation, non-root
security context, dropped capabilities, read-only root filesystem, resource
requests/limits, probes, disruption budget, autoscaling, topology spread,
NetworkPolicy, ConfigMap, Service, Deployment, Gateway API routing, and an Argo CD
Application with automated prune/self-heal and revision history.

## Live GitOps validation

Live validation ran on 2026-09-03 with Kind v0.32.0, Kubernetes v1.36.1, Gateway
API v1.6.1 CRDs, and Argo CD v3.5.2. The Application uses the accessible personal
submission repository and is pinned to immutable rollback commit
`3f6f4a47607d3c29fd44eb49e04481b8b087607e`.

- Argo CD synced all ten declared resources to namespace `lab28`.
- A live ConfigMap drift changed `LAB28_VLLM_REQUIRE_REAL` from `true` to `false`.
  Automated self-heal restored `true` in approximately 2.4 seconds.
- Candidate Git commit `3a34d4dde5e113dbade1b8ddae773416def4e256`
  added `LAB28_GITOPS_RELEASE=candidate`; Argo synced that exact revision and the
  key appeared in the live ConfigMap.
- Git revert commit `3f6f4a47607d3c29fd44eb49e04481b8b087607e`
  removed the marker; Argo synced the revert and the key disappeared.

The Application is `Synced`. Workload health is honestly `Degraded`: this base
deploys the API control surface but not Kafka, Qdrant, MLflow, Feast, OTel, or a
GPU vLLM inside Kubernetes, so dependency-aware `/ready` correctly remains false.
The API image was built from this repository and live rollout exposed and fixed
an image contract bug: its original root default conflicted with `runAsNonRoot`.
The corrected image declares fixed UID/GID `10001:10001`; pods now start under the
restricted security context. No dependency or readiness response was mocked.

## Real vLLM and LangSmith validation

On 2026-09-03 a real vLLM 0.8.5 server ran under WSL2 on an NVIDIA RTX 3050
Laptop GPU (4 GB), serving `Qwen/Qwen3-0.6B`. The identity probe observed
`/health=200`, the vLLM-specific `/version`, the configured model from
`/v1/models`, and 81 native `vllm:` metric names. A full gateway request used
release version 8 from MLflow and returned a cited answer. Qwen thinking was
disabled through `chat_template_kwargs` so the bounded 96-token budget is spent
on the answer rather than hidden reasoning.

The LangSmith overlay was run with the credential held only in ignored `.env`.
Its gated test passed (`1 passed, 71 deselected`); the collector exported the
same 59 spans to its debug, Jaeger, and LangSmith exporters with no recorded
send failure. Neither the API key nor model weights are committed.
