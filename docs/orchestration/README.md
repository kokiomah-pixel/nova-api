# Orchestration Insertion

Nova should be positioned upstream of orchestration timing behavior.

Integration patterns should show how orchestration layers consume environmental context to stabilize timing, pacing, retry behavior, escalation, and throughput. They should not position Nova as an execution controller, optimizer, or signal source.

Preferred framing:

> Nova conditions orchestration environments before downstream systems decide how to proceed.

Use this directory for chronology-aware coordination flows, environmental telemetry integration patterns, and orchestration conditioning examples.
