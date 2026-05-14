# Security Policy

Voila! is currently in public beta.

This document explains how to report security issues and what security expectations apply during the beta phase.

## Supported versions

| Version | Status |
|---|---|
| v0.2.x public beta | Supported for security review and fixes |
| v0.1.x internal/pre-release milestones | Not actively supported |

## Reporting a vulnerability

Please do not open a public GitHub issue for sensitive security vulnerabilities.

If you believe you found a security issue, please contact the maintainer privately.

Include, if possible:

- affected version
- operating system
- clear reproduction steps
- expected behavior
- actual behavior
- screenshots or logs, if useful
- whether sensitive data may be exposed

## Public beta security expectations

Voila! is currently a public beta. It is provided for evaluation, feedback, and early testing.

Do not use the public beta for sensitive, regulated, confidential, or production-critical workflows unless you have independently reviewed the risks.

## Sensitive files

Do not commit:

- passwords
- API keys
- private keys
- certificates
- real `.env` files
- payment provider secrets
- customer data
- private business documents
- production signing keys
- local runtime caches
- generated logs with personal data
- generated courses or processed PDFs from local testing

## Release integrity

Public release packages should include:

- release notes
- checksum file
- test log
- final checklist

Users should verify release files against the published checksum when possible.

## Commercial/security roadmap

Future commercial or business builds may include additional security measures such as:

- signed Windows installer
- signed binaries
- private support channel
- controlled update channel
- commercial usage terms
- stronger supply-chain checks
