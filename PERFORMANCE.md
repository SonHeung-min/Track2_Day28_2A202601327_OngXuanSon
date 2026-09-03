# Performance profile

## Environment and method

- Measured: 2026-09-03, after the Full Compose stack and dependency caches were warm.
- Host: 12th Gen Intel Core i5-12450H, 8 cores / 12 logical processors, 16 GB RAM.
- GPU: NVIDIA GeForce RTX 3050 Laptop GPU, 4096 MiB.
- Dataset at measurement time: 15 Qdrant points; Delta documents v4 (15 rows) and
  feedback v9 (19 rows).
- Target: `http://localhost:8080/ready` through Envoy, 200 requests per profile.
- Gateway policy: token bucket capacity 10, refill 10 tokens/second.
- Warm-up: the Full integration journeys and three direct readiness probes were run
  before the recorded profiles.

The load probe preserves HTTP 429 separately from transport failures and reports
wall time, total response throughput, and error rate. Total response throughput
includes rejected requests; it is not accepted application throughput.

## Results

| Workers | HTTP 200 | HTTP 429 | Transport failures | Error rate | Elapsed | Total responses/s | P50 | P95 | P99 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 | 27 | 173 | 0 | 86.5% | 2.140 s | 93.44 | 6.37 ms | 545.43 ms | 646.30 ms |
| 16 | 14 | 186 | 0 | 93.0% | 1.040 s | 192.35 | 7.60 ms | 732.06 ms | 972.73 ms |

Observed post-run resource snapshots (not peak samples):

| Profile | API CPU | API RAM | Gateway CPU | Gateway RAM | Kafka lag (`lab28-pipeline`) |
|---|---:|---:|---:|---:|---:|
| 8 workers | 111.86% | 197.7 MiB | 0.64% | 28.62 MiB | 0 |
| 16 workers | 24.17% | 238.2 MiB | 0.59% | 27.86 MiB | 0 |

## Interpretation

The first bottleneck is the intentional Envoy admission policy, not Kafka: every
classified failure was HTTP 429 and the primary pipeline lag remained zero. Moving
from 8 to 16 workers increased rejected work and tail latency without increasing
useful accepted traffic. Clients should honor 429 with jittered backoff; operators
should tune the bucket from an agreed SLO and measured downstream capacity rather
than merely raising concurrency.

The readiness endpoint fans out to Kafka, MLflow, Qdrant, Feast, and vLLM. It is a
deliberately expensive baseline and should not be mistaken for the latency of a
single in-process health check. CPU snapshots taken after a burst are timing
sensitive, so they are reported as observations rather than claimed maxima.

`/api/v1/ask` is **UNVERIFIED** in this environment because no real vLLM endpoint
or instructor-issued remote endpoint is available. The configured laptop GPU has
4 GB VRAM and was not used to fabricate an OpenAI-compatible substitute. Therefore
vLLM queue/token metrics and answer latency are also UNVERIFIED. No production
capacity is extrapolated from this laptop profile.

