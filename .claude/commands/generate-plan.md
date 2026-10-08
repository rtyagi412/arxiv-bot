# Generate Implementation Plan

Feature directory: $ARGUMENTS

## Objective

Generate an implementation plan from an approved spec.md
following Stage 3 — Build of the AI-Native SDLC.

Work exclusively in Claude Code Plan Mode.

## Instructions

1. Read:
   - $ARGUMENTS/intent.md
   - $ARGUMENTS/spec.md
   - CLAUDE.md
   - Relevant project skills

2. Verify that:
   - intent.md is accepted.
   - spec.md contains the exact line "Spec status: approved".
   - No unresolved [BLOCKER] concerns remain.

   If any condition fails, stop and report it.

   Open non-blocker questions in spec.md do not stop the
   command. Carry them into plan section 8 and resolve them
   with the user (AskUserQuestion) before requesting approval.

3. Inspect the existing repository:
   - Project structure
   - Existing components
   - Dependencies
   - Tests and test infrastructure
   - Configuration and conventions

4. Generate an implementation plan based on the
   approved specification.

## Required Plan Sections

### 1. Overview
- Feature objective
- Reference to intent.md and spec.md
- Scope of implementation

### 2. Files to Change
- Existing files to modify
- New files to create
- Purpose of each change

### 3. Implementation Steps
- Ordered implementation tasks
- Dependencies between tasks
- Functional requirements addressed by each task

### 4. Architecture Decisions
- Proposed technical approach
- Integration with existing components
- Alternatives considered
- Reasons for choosing the approach

### 5. Risks
- What could break
- Most risky implementation step
- Compatibility concerns
- Security concerns
- Mitigation strategies

### 6. Test Plan
- Unit tests
- Integration tests
- Failure scenarios
- Recovery scenarios
- Relevant verification commands

Map every functional requirement (FR-N)
to at least one test.

### 7. Verification
- Commands to execute
- Expected results
- Acceptance criteria

### 8. Open Questions
- Unresolved technical decisions
- Dependencies requiring clarification

## Planning Rules

- Treat spec.md as the approved design.
- Do not invent requirements.
- Do not silently change architecture decisions.
- Do not introduce unnecessary abstractions.
- Prefer existing project patterns.
- Keep implementation steps small and verifiable.
- Flag deviations from spec.md.
- Do not modify implementation files.
- Do not implement code.
- Do not proceed without human approval.

## Output

Plan Mode only allows writing its own internal plan file,
so draft the complete plan there. Begin the plan with a
short summary: implementation steps, important risks,
rejected alternatives, and unresolved questions.

Request approval only by calling ExitPlanMode. Do not ask
for approval in text or with AskUserQuestion.

After approval, the first and only action is to save the
approved plan to:

$ARGUMENTS/plan.md

If plan.md exists and is non-empty, ask before
overwriting it. Then stop. Do not implement.