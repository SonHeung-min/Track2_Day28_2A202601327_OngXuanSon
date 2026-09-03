FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir ".[retrieval,ml]"

# Match the restricted Kubernetes security context. A numeric, fixed UID/GID
# lets the kubelet verify runAsNonRoot without consulting /etc/passwd, while the
# named account keeps local diagnostics understandable.
RUN groupadd --gid 10001 lab28 \
    && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin lab28 \
    && chown -R 10001:10001 /workspace

USER 10001:10001

EXPOSE 8000
CMD ["lab28", "serve", "--host", "0.0.0.0", "--port", "8000"]
