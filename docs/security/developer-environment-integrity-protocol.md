# Sharpe Nova OS Developer Environment Integrity Protocol

Status: Required

Sharpe Nova OS treats developer environments as part of the infrastructure trust boundary. Local tooling can affect repository integrity, chronology trust, governance continuity, and the reliability of machine-native infrastructure work.

This protocol protects environmental integrity without exposing sovereign internals. It does not disclose Reflex Memory internals, policy weights, admission causality, internal thresholds, settlement secrets, private keys, wallet secrets, or facilitator credentials.

## 1. Developer Tooling Risk

Developer tooling can become an infrastructure attack surface. This includes:

- local IDEs and editor integrations
- VS Code extensions and language tooling
- terminal integrations and shell plugins
- Git helpers, credential helpers, and diff tools
- credential managers and local secret stores
- package managers and CLI tools

A compromised tool can read files, alter commits, observe terminal output, capture clipboard contents, manipulate Git operations, or expose local credentials. Nova contributors should treat the local workstation as part of the repository governance surface.

## 2. Approved Extension Posture

Editor extensions are supply-chain dependencies.

Required posture:

- install only extensions that are necessary for current Nova work
- prefer trusted publishers with clear maintenance history
- remove unused extensions
- avoid extensions that request broad terminal, file, Git, clipboard, credential, or secret access
- disable extension auto-install behavior where the editor allows it
- review editor extensions before using them in Nova repositories
- keep repository-level extension recommendations out of Nova unless explicitly reviewed

Extensions must not become implicit infrastructure policy. Convenience does not override repository integrity.

## 3. Credential Hygiene

The following credential classes require strict handling:

- GitHub tokens and GitHub CLI authentication
- CDP credentials
- x402 payer keys and facilitator credentials
- wallet and testnet secrets
- API keys
- local `.env` files
- local shell history and terminal scrollback

Rules:

- never commit secrets
- never paste secrets into chats, docs, issues, or pull requests
- rotate tokens after suspicious editor, extension, terminal, or CLI activity
- use least-privilege credentials for development and automation
- keep `.env` files untracked
- keep `.env.example` sanitized with placeholders only
- avoid commands that print tokens into logs or shell history
- prefer short-lived or revocable credentials where available

## 4. Secret Exposure Response

If a credential may have been exposed:

1. Stop active work.
2. Revoke the exposed credential.
3. Rotate the replacement credential.
4. Search repository history for related exposure.
5. Check logs, terminal scrollback, and shell history.
6. Document the event in the security chronology log without recording raw secrets.
7. Open a remediation pull request if repository changes are needed.

The chronology record should preserve what happened and what changed. It must not preserve usable credential material.

## 5. Extension Incident Response

If an editor extension or local developer tool is suspicious:

1. Disable the suspicious extension or tool.
2. Capture its name, publisher, version, install source, and observed behavior.
3. Review file access, terminal history, shell history, and recent Git activity.
4. Rotate potentially exposed credentials.
5. Reinstall the environment from a known-good baseline if needed.
6. Record the incident in the developer environment chronology.

Do not rely on partial cleanup when the affected tool had broad local access.

## 6. Local Environment Rebuild Guidance

If developer-environment compromise is suspected, prefer rebuild over partial cleanup.

A known-good rebuild may include:

- clean operating system user profile or workstation image
- freshly installed editor from the official channel
- minimal reviewed extension set
- newly authenticated GitHub CLI session
- rotated local secrets
- regenerated `.env` from sanitized `.env.example`
- fresh dependency installation from reviewed lockfiles or manifests

Rebuilds should preserve repository chronology without exposing sovereign internals or credential material.
