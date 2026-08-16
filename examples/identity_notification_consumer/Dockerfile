FROM python:3.12-slim

WORKDIR /workspace

COPY notification /workspace/notification
COPY identity /workspace/identity
COPY examples/identity_notification_consumer /workspace/examples/identity_notification_consumer

RUN python -m pip install --no-cache-dir -e "/workspace/notification" \
    && python -m pip install --no-cache-dir -e "/workspace/identity" \
    && python -m pip install --no-cache-dir -e "/workspace/examples/identity_notification_consumer[test]"

WORKDIR /workspace/examples/identity_notification_consumer

CMD ["make", "check"]
