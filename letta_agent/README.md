# hamresan-letta-agent

Reusable Letta agent integration for host applications.

The package owns Letta SDK details and normalizes provider failures. Host applications keep their
own agent/domain contracts and adapt this package through public APIs.

Capabilities:

- create one Letta agent from an application-provided specification;
- attach a persona memory block at creation time;
- upsert a read-only account knowledge block on an existing agent;
- perform a controlled interaction with an existing agent;
- create provider conversations for an existing agent;
- interact inside a selected conversation so hosts can isolate end-user threads;
- normalize Letta SDK/API failures.

The package does not own host persistence, Instagram connection binding, persona generation,
knowledge preparation, or host conversation routing. The host remains responsible for mapping its own participant/thread identity to a Letta conversation ID.
