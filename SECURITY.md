# Security Policy

## Reporting a vulnerability

Please do not disclose security vulnerabilities in public issues. Contact the
repository owner privately through the security reporting option on GitHub.
Include the affected version, impact, reproduction steps, and any suggested
mitigation. Do not include real credentials, personal data, or private notes.

## Security notes

- Never commit `.env`, API keys, tokens, local databases, or audio recordings.
- Keep dependencies updated and review dependency alerts.
- The Streamlit interface is intended for local development. Do not expose it
  to an untrusted network without authentication, authorization, and transport
  security. Notes and chat / AI history are process-wide, not multi-user isolated.
- Voice recognition may send audio to Google's recognition service.
- Weather and Wikipedia commands make outbound HTTP requests.
