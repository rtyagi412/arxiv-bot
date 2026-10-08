# Implement Approved Plan

Feature directory: $ARGUMENTS

## Objective

Implement the approved plan.md following the
AI-Native SDLC Build → Test workflow.

## 1. Preconditions

Read:
- $ARGUMENTS/intent.md
- $ARGUMENTS/spec.md
- $ARGUMENTS/plan.md
- CLAUDE.md
- Relevant project skills

Verify:
- intent.md is accepted.
- spec.md is approved.
- plan.md exists and contains implementation steps.
- The user has explicitly approved plan.md.
- No unresolved [BLOCKER] concerns remain.

If any condition is not satisfied, stop and report it.

Do not interpret the existence of plan.md as approval.

## 2. Validate the Plan

Before implementation:

1. Inspect the existing repository.
2. Compare plan.md against spec.md.
3. Identify missing functional requirements.
4. Identify conflicting architecture decisions.
5. Identify missing verification steps.

If significant deviations exist, stop and request
clarification before modifying code.

## 3. Implementation

Implement the approved plan in the specified order.

Rules:

- Follow plan.md as the implementation source.
- Follow spec.md as the requirements source.
- Apply relevant project skills.
- Follow CLAUDE.md conventions.
- Keep changes within the approved scope.
- Prefer existing project patterns.
- Do not introduce unnecessary abstractions.
- Do not silently change architecture decisions.
- Never hardcode credentials or secrets.

For each implementation step:

1. Implement the required changes.
2. Add or update relevant tests.
3. Run focused tests.
4. Fix failures.
5. Continue to the next step.

If implementation must deviate from plan.md,
explain the deviation and request approval before
changing the plan or proceeding.

## 4. Testing

After implementation:

1. Run the relevant test suite.
2. Run configured lint and formatting checks.
3. Run integration tests where available.
4. Verify success criteria from intent.md.
5. Verify every functional requirement from spec.md.

Do not delete, weaken, or skip failing tests
to make implementation appear successful.

## 5. Independent Verification

Invoke the verifier agent:

.claude/agents/verifier.md

Ask it to:

- Read spec.md and plan.md.
- Run relevant verification commands.
- Validate every success criterion.
- Verify failure and recovery scenarios.
- Report Passed, Failed, or Not Tested.
- Report findings without modifying code.

If verification fails, fix implementation issues
and rerun verification.

## 6. Code Review

Invoke the code-reviewer agent:

.claude/agents/code-reviewer.md

Ask it to review:

- Functional correctness
- Compliance with spec.md and plan.md
- Security vulnerabilities
- Error handling
- Missing tests
- Unnecessary complexity

Classify findings as:

- Important: Breaks behavior, leaks data,
  or violates requirements.
- Nit: Minor improvements.

Report at most five nits.

Fix Important findings and rerun relevant tests.

## 7. Completion Report

Provide:

### Implementation Summary
- Files created
- Files modified
- Functional requirements implemented

### Verification Results
- Tests executed
- Passed tests
- Failed tests
- Tests not executed and why

### Code Review
- Important findings
- Remaining nits

### Deviations
- Differences from the approved plan
- Unresolved concerns

### Final Status
- Complete
- Partial
- Blocked

Only report Complete when all required
verification checks pass.

## 8. Restrictions

- Do not modify approved intent.md or spec.md.
- Do not rewrite approved plan.md without permission.
- Do not commit or push changes automatically.
- Do not deploy to production.
- Do not report success without verification evidence.
- Stop and request approval for out-of-scope changes.

## Output

Implement the feature in the repository.

Do not create a new implementation plan.

Stop after implementation, testing, verification,
and review.

Wait for human approval before committing or deploying.