# Security Policy

Sharpe Nova OS treats developer environments, credentials, governance records, and continuity artifacts as part of the infrastructure trust boundary.

## Reporting Vulnerabilities

Report suspected vulnerabilities privately to the repository owner or maintainer. Do not open public issues containing secrets, exploit details, credential material, or private infrastructure data.

## Secrets

Do not commit credentials, API keys, private keys, seed phrases, wallet material, bearer tokens, or local environment files. Use `.env.example` for placeholders only.

If a secret is exposed, rotate it immediately and record the response in the appropriate security or continuity chronology.

## Relevant Docs

- [docs/security/developer-environment-integrity-protocol.md](docs/security/developer-environment-integrity-protocol.md)
- [docs/continuity/model-provider-independence-protocol.md](docs/continuity/model-provider-independence-protocol.md)
- [docs/continuity/business-workspace-continuity-protocol.md](docs/continuity/business-workspace-continuity-protocol.md)

