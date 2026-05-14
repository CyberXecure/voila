# Voila! Security Checklist

Milestone: v0.2.2-public-beta-security-hardening

## Repository security

- [ ] Branch protection enabled for `main`
- [ ] Branch protection enabled for `release/*`
- [ ] Direct pushes to protected branches disabled
- [ ] Pull request required before merge
- [ ] Secret scanning enabled
- [ ] Push protection enabled
- [ ] Dependabot alerts enabled
- [ ] Dependabot security updates enabled
- [ ] CodeQL/code scanning enabled, if available
- [ ] Repository visibility intentionally reviewed
- [ ] No final LICENSE added until licensing decision is made

## Local/generated data

- [x] `data/trash/` removed from Git tracking
- [x] `data/trash/` added to `.gitignore`
- [x] generated course files excluded from future commits
- [x] local processed PDFs excluded from future commits
- [x] logs excluded from future commits
- [ ] verify no generated local data remains tracked after commit

## Local secret audit

- [ ] No real `.env` files committed
- [ ] No passwords committed
- [ ] No API keys committed
- [ ] No private keys committed
- [ ] No certificates committed
- [ ] No payment provider secrets committed
- [ ] No customer data committed
- [ ] No local logs with personal data committed

## Release security

- [ ] Release ZIP generated from clean working tree
- [ ] SHA256 file generated
- [ ] Release notes included
- [ ] Final checklist included
- [ ] Test log included
- [ ] Release assets verified after upload
- [ ] Old stable release tag not modified

## Windows packaging

- [ ] Runtime folders reviewed before packaging
- [ ] Temporary files excluded
- [ ] Logs excluded
- [ ] Cache folders excluded
- [ ] Local machine paths avoided in documentation where possible
- [ ] Future: signed installer considered
- [ ] Future: Authenticode certificate considered

## Monetization security

- [ ] No payment secrets in public repo
- [ ] No license key implementation committed before design review
- [ ] No production webhook secrets committed
- [ ] No customer list committed
- [ ] Paid download text does not overpromise security/support
