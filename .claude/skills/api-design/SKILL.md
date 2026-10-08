---
name: api-design
description: Apply consistent API contract and error-handling standards when designing, implementing, or reviewing FastAPI endpoints, including health endpoints.
---

# API design

When designing, implementing, or reviewing FastAPI endpoints:

1. Read the accepted feature `intent.md` and `spec.md` before proposing endpoint behavior. Do not invent contracts not present in the spec; flag missing decisions.
2. Define each route's HTTP method and path, input and output schemas, expected status codes, and error responses.
3. Use consistent JSON response shapes and validate request inputs at the boundary. Avoid exposing internal implementation details through error payloads.
4. Distinguish an API responding successfully from its dependencies being healthy. For a composite health endpoint, expose component statuses and an overall status only as defined by the feature spec.
5. Keep health checks bounded so a failed dependency cannot indefinitely block a response. Do not leak connection strings, credentials, stack traces, or database errors in responses.
6. Propose tests that exercise successful responses, documented failures, and recovery paths. Keep requirements traceable to the numbered functional requirements in `spec.md`.

## Output checklist

- Endpoint contracts and status codes are explicit.
- Ambiguities or trade-offs are listed for review, not silently decided.
- Each documented response can be verified by tests.
