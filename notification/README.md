# hamresan-notification

Reusable, application-agnostic notification package for Python services.

The package provides a stable notification API, queue-first delivery orchestration, template rendering, and replaceable providers for SMS, email, and console output. It is designed so consuming applications depend on small contracts instead of provider-specific implementations.

## Features

- Public `NotificationSender` contract for application modules.
- Queue-first notification flow through an injected `NotificationQueue`.
- Provider abstraction and resolver for SMS, email, and console delivery.
- Built-in HTTP SMS, SMTP email, and console providers.
- Filesystem-based Jinja templates.
- Locale-aware and channel-aware templates.
- Typed JSON-compatible template variables.
- Optional FastAPI adapter.
- Strict Pyright type checking.
- Mirrored application, infrastructure, and presentation tests.

## Architecture

The package separates notification intent from delivery infrastructure:

```text
Consumer
   |
   v
NotificationSender
   |
   v
QueueNotificationService
   |
   v
NotificationQueue  <-- supplied by the host application
   |
   v
Worker / job handler
   |
   v
DeliverNotificationService
   |
   +--> MessageTemplateRenderer
   |
   +--> NotificationProviderResolver
            |
            +--> SMS provider
            +--> Email provider
            +--> Console provider
```

The package intentionally does **not** create or own Redis, ARQ, Celery, RabbitMQ, or another worker system. The host application provides a `NotificationQueue` implementation and controls retries, connections, worker lifecycle, and deployment.

Consumers such as an Identity package should depend only on the public `NotificationSender` API.

## Installation

From this monorepo:

```bash
pip install -e ./notification
```

Install the optional FastAPI integration:

```bash
pip install -e "./notification[fastapi]"
```

For local development and testing:

```bash
cd notification
make install-dev
```

## Public API

The primary API used by other modules is:

```python
from notification import NotificationChannel, SendNotification
from notification.public.services import NotificationSender
```

A consumer receives a `NotificationSender` through dependency injection and sends a command:

```python
async def send_login_code(
    sender: NotificationSender,
    phone_number: str,
    otp: str,
) -> None:
    await sender.send(
        SendNotification(
            channel=NotificationChannel.SMS,
            recipient=phone_number,
            template_key="auth.otp",
            locale="en",
            variables={"otp": otp},
        )
    )
```

The consumer does not need to know which SMS provider, queue implementation, or template renderer is being used.

## Configure the Package

Create the provider resolver and template renderer in the host application's composition root.

```python
from pathlib import Path

from jinja2 import Environment

from notification import NotificationModule, NotificationModuleConfig
from notification.domain.enums import NotificationChannel
from notification.infrastructure.providers.http_sms import HttpSmsProvider, HttpSmsSettings
from notification.infrastructure.providers.resolver import StaticNotificationProviderResolver
from notification.infrastructure.providers.smtp import SmtpEmailProvider, SmtpSettings
from notification.infrastructure.templates.filesystem import FilesystemTemplateRepository
from notification.infrastructure.templates.jinja_renderer import JinjaMessageTemplateRenderer
```

Configure templates:

```python
template_repository = FilesystemTemplateRepository(
    root=Path("templates/notifications")
)

template_renderer = JinjaMessageTemplateRenderer(
    repository=template_repository,
    environment=Environment(autoescape=False),
)
```

Configure providers:

```python
sms_provider = HttpSmsProvider(
    client=http_client,
    settings=HttpSmsSettings(
        url=settings.sms_api_url,
        api_key=settings.sms_api_key,
        sender=settings.sms_sender,
    ),
)

email_provider = SmtpEmailProvider(
    SmtpSettings(
        host=settings.smtp_host,
        port=settings.smtp_port,
        sender=settings.smtp_sender,
        username=settings.smtp_username,
        password=settings.smtp_password,
    )
)

provider_resolver = StaticNotificationProviderResolver(
    providers={
        NotificationChannel.SMS: sms_provider,
        NotificationChannel.EMAIL: email_provider,
    }
)
```

The host application must also supply its own `NotificationQueue` implementation:

```python
from notification.application.contracts.queue import NotificationQueue
from notification.application.dto import NotificationJobPayload
from notification.public.dto import NotificationReference


class ApplicationNotificationQueue(NotificationQueue):
    async def enqueue(
        self,
        payload: NotificationJobPayload,
    ) -> NotificationReference:
        job_id = await application_job_dispatcher.enqueue(
            name="notification.deliver",
            payload=payload,
        )
        return NotificationReference(job_id=job_id)
```

Then compose the module:

```python
notification_module = NotificationModule(
    NotificationModuleConfig(
        queue=notification_queue,
        renderer=template_renderer,
        provider_resolver=provider_resolver,
    )
)

notification_sender = notification_module.sender
notification_delivery_service = notification_module.delivery_service
```

`notification_sender` is what application modules should receive. `notification_delivery_service` is normally used by the worker that processes queued notification jobs.

## Worker Integration

A worker receives the serialized notification payload from the host queue, reconstructs `NotificationJobPayload`, and delegates delivery to the package:

```python
async def deliver_notification_job(payload: NotificationJobPayload) -> None:
    await notification_module.delivery_service.deliver(payload)
```

Retry and dead-letter behavior belong to the host worker infrastructure rather than this package.

## Template Structure

`FilesystemTemplateRepository` expects templates in this structure:

```text
templates/notifications/
├── en/
│   ├── sms/
│   │   └── auth.otp.j2
│   └── email/
│       └── auth.otp.j2
└── fa/
    ├── sms/
    │   └── auth.otp.j2
    └── email/
        └── auth.otp.j2
```

For example, an SMS OTP template can contain:

```jinja2
Your verification code is {{ otp }}.
```

Email templates may provide a subject and body using the package delimiter:

```jinja2
Your verification code
---subject---
Your verification code is {{ otp }}.
```

## OTP Integration Example

Identity should depend on `NotificationSender`, not on SMS or email implementations:

```text
Identity
   |
   v
NotificationSender
   |
   v
hamresan-notification
   |
   +--> Queue
   +--> Template
   +--> SMS / Email provider
```

This keeps OTP generation and verification inside Identity while notification delivery remains inside the Notification package.

## FastAPI Adapter

Install the FastAPI extra and add the optional test router:

```python
from fastapi import FastAPI

from notification.presentation.fastapi import create_notification_router

app = FastAPI()
app.include_router(create_notification_router(notification_module.sender))
```

The included endpoint is intended as an integration/testing adapter. Business modules should normally call `NotificationSender` directly rather than calling Notification over HTTP inside the same application.

## Development

Install development dependencies:

```bash
make install-dev
```

Run all quality checks:

```bash
make check
```

Or run them separately:

```bash
make lint
make format-check
make typecheck
make test
```

The package uses a `src/` layout and strict Pyright configuration. Tests mirror the package layers and independent test fakes live under `tests/support`.

## Design Rules

- Consumers depend on public contracts, not concrete providers.
- Provider selection belongs to the composition/configuration layer.
- Queue infrastructure is supplied by the host application.
- External provider communication stays inside provider adapters.
- Template rendering stays outside application services.
- Application services remain small orchestration components.
- Provider-specific response mapping stays outside service logic.
- No consuming module should know SMTP, HTTP SMS, queue, or worker implementation details.
