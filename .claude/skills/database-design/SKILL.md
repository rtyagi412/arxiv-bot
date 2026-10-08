---
name: database-design
description: Apply safe PostgreSQL connectivity, configuration, and lifecycle practices when designing, implementing, or reviewing database integration.
---

# Database design

When designing, implementing, or reviewing PostgreSQL integration:

1. Read the feature's accepted intent and spec; keep the proposed database scope limited to what they require.
2. Keep database credentials and connection settings in environment-based configuration; provide a safe example configuration, never real secrets.
3. State how the application reaches PostgreSQL from its actual runtime location. In particular, a local host process and a Compose container have different networking assumptions.
4. Use bounded connection and query timeouts for availability checks. Prefer a simple actual database query over a container-running check when the requirement is database connectivity.
5. Ensure transient database unavailability is handled without crashing unrelated API routes when the feature requires a degraded response.
6. Document startup, stop, restart, and recovery behavior. Do not introduce migrations, application tables, or persistence models unless they are explicitly in scope.
7. Avoid logging passwords, full connection URLs containing credentials, or sensitive query parameters.

## Output checklist

- Connectivity and environment configuration are documented.
- Unavailable and recovered database behavior is testable.
- Any security, operational, or lifecycle trade-off is flagged for review.
