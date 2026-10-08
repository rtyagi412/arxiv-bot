---
name: secure-api-review
description: Review new or changed API routes and database integration for credential exposure, unsafe error handling, and endpoint access risks.
---

# Secure API review

When creating, changing, or reviewing API endpoints:

1. Read accepted requirements and repository security conventions first; identify which routes are intentionally public and which need authentication.
2. Check that secrets are sourced from protected configuration, not committed files or hard-coded strings. Example `.env` templates must use placeholders.
3. Verify response payloads and logs never expose passwords, full credential-bearing connection URLs, internal stack traces, or database exception details.
4. Validate untrusted inputs at the API boundary and use parameterized queries if query parameters are involved.
5. Bound dependency checks with timeouts and ensure unavailable dependencies fail predictably rather than hanging or causing uncontrolled exceptions.
6. Review Compose-exposed ports and database credentials for the intended environment. Prefer least exposure consistent with the accepted design.
7. Report findings as **[BLOCKER]** for exploitable credential exposure, authentication gaps, or material security issues, and **[WATCH]** for risks needing an explicit decision. Do not silently change product behavior to resolve a trade-off.

## Output checklist

- Public route decisions are explicit.
- Secrets and internal error details stay out of API responses and logs.
- Findings identify location, impact, and recommended correction.

> This skill guides review but does not enforce policy by itself; use deterministic tests or hooks for mandatory controls.
