# Generate Specification

Feature directory: $ARGUMENTS

## Objective

Convert an accepted intent.md into a technical spec.md
following Stage 2 — Design of the AI-Native SDLC.

## Instructions

1. Read $ARGUMENTS/intent.md.
2. Verify that the intent status is accepted.
   If not, stop and request approval.
3. Read CLAUDE.md and inspect the existing repository.
4. Apply relevant skills from .claude/skills/.
5. Generate $ARGUMENTS/spec.md.

## Specification Requirements

Include:

- Functional requirements (FR-1, FR-2, ...)
- Non-functional requirements
- Architecture and components
- Data flow and API contracts
- Data models and configuration
- Error handling and edge cases
- Test strategy
- Dependencies on earlier and future intents
- Areas of concern
- Open questions

## Traceability

Map every success criterion in intent.md to:
- At least one functional requirement
- At least one verification test

## Areas of Concern

Flag contradictions, security risks, assumptions,
scope creep, and unresolved trade-offs.

Classify each as:
- [BLOCKER]: Must resolve before implementation.
- [WATCH]: Risk requiring attention.

Provide recommendations without silently resolving trade-offs.

## Constraints

- Treat intent.md as the source of truth.
- Do not modify intent.md.
- Do not invent product requirements.
- Do not write implementation code.
- Do not generate plan.md.
- Do not proceed to Build without human approval.

## Output

Write spec.md in the feature directory.

Summarize requirements, architecture decisions,
areas of concern, and unresolved questions.

Request approval before proceeding.