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

## Environment gate

Live Kubernetes drift, self-heal, and desired-state rollback are **UNVERIFIED** on
this host. `kubectl` is installed but has no current context or reachable cluster;
Kind, Argo CD CLI, Helm, and standalone Kustomize are absent. No screenshots or
sync results were fabricated.

The checked-in Argo CD Application deliberately remains a reproducible upstream
sample pinned to `refs/tags/v3.0.0`. Before a personal live deployment, set
`repoURL` to the accessible submission repository and `targetRevision` to an
immutable submitted commit or tag. Apply the Application, introduce a harmless
replica drift, capture Argo CD self-heal, then roll desired state back through Git
and capture the successful sync and rollout history.

