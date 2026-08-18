FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update \
    && apt-get install --no-install-recommends -y libatomic1 \
    && rm -rf /var/lib/apt/lists/*

COPY notification /workspace/notification
COPY identity /workspace/identity
COPY store /workspace/store
COPY examples/identity_store_consumer /workspace/examples/identity_store_consumer

RUN python -m pip install --no-cache-dir -e "/workspace/notification" \
    && python -m pip install --no-cache-dir -e "/workspace/identity" \
    && python -m pip install --no-cache-dir -e "/workspace/store" \
    && python -m pip install --no-cache-dir -e "/workspace/examples/identity_store_consumer[test]"

WORKDIR /workspace/examples/identity_store_consumer

CMD ["make", "check"]
