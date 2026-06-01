# Security and Governance Notes

## Data Handling

This project should only process public job postings and non-confidential candidate profile information.

## Secrets

API keys are stored in `.env`, which is excluded from Git.

## Human Review

Generated CV bullets and recruiter outreach must be reviewed before use.

## Risk Controls

- Structured outputs reduce malformed responses.
- Human approval prevents automatic use of unreviewed content.
- Tracing improves auditability and debugging.
- Tests validate core workflow components.
