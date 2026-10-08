# Project Instructions

## Project Overview

A Python FastAPI backend using PostgreSQL.

Development environment:
- FastAPI runs locally.
- PostgreSQL runs in Docker Compose.
- Project follows the AI-Native SDLC.

## Development Workflow

Follow this sequence:

Plan → Design → Build → Test → Deploy → Maintain

### Artifacts

Each feature lives in:

docs/features/NNN-feature-name/

Each feature contains:
- intent.md — problem, outcome, constraints, success criteria
- spec.md — requirements and technical design
- plan.md — implementation plan and verification steps

### Rules

1. Read intent.md and spec.md before planning.
2. Use Claude Code plan mode before implementation.
3. Do not implement until plan.md is approved.
4. Map implementation tasks to functional requirements.
5. Run relevant tests before reporting completion.
6. Report deviations from spec.md or plan.md.
7. Never silently introduce new requirements.

## Technology

- Language: Python
- API framework: FastAPI
- Database: PostgreSQL
- Database runtime: Docker Compose
- API runtime: Local development machine

## Skills

Use relevant project skills from .claude/skills/:

- api-design
- database-design
- test-strategy
- secure-api-review

## Security

- Never commit credentials or secrets.
- Use environment variables for configuration.
- Do not expose internal database errors in API responses.

## Verification

- Test successful API responses.
- Test dependency failure scenarios.
- Test recovery after dependencies become available.
- Report commands executed and their results.

## Project Conventions

- Keep changes scoped to the accepted feature.
- Prefer simple solutions over unnecessary abstractions.
- Keep documentation synchronized with implementation.