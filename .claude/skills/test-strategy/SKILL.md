---
name: test-strategy
description: Derive verifiable automated tests and a repeatable feedback loop from feature success criteria and numbered functional requirements.
---

# Test strategy

When specifying, implementing, or reviewing a feature:

1. Read the accepted `intent.md` and `spec.md`. Map every measurable success criterion to at least one numbered functional requirement and at least one test.
2. Select the lightest useful level for each proof: unit tests for isolated logic, integration tests for real boundaries, and end-to-end checks for user-visible workflows.
3. Cover happy paths, failure paths, boundary conditions, and recovery where applicable; do not count mocked database behavior as proof that the actual database connection works.
4. For health checks, test the documented HTTP code and response body in both healthy and degraded states, then verify recovery if required.
5. Specify how tests are started, required dependencies, expected results, and how a failed test makes the command exit non-zero.
6. Run the relevant test commands before reporting implementation complete. Record exact commands and results; never claim a test passed if it was not run.
7. Do not delete, weaken, or skip failing tests just to obtain a passing result. Escalate unclear requirements instead of rewriting expected behavior.

## Output checklist

- Success criteria → functional requirements → tests mapping is complete.
- Automated verification covers actual failure and recovery scenarios where required.
- Test evidence or unexecuted-test limitations are reported explicitly.
