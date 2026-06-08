# Voila Repository Privacy Transition Checklist

Milestone:

```text
v0.3.6-voila-repo-privacy-transition-checklist
```

## Purpose

Prepare Voila for a future transition from public source repository to private development repository.

This milestone does not change GitHub repository visibility.

It documents what must be checked before making the repository private and what should remain available publicly after the transition.

---

## Strategic direction

Voila is a proprietary product.

The intended direction is:

```text
private development repository
controlled public releases
clear beta terms
future Supporter / Pro licensing
public surface focused on product, not source code
```

---

## Transition checklist

### Repository status

```text
[ ] confirm main branch is clean
[ ] confirm all recent docs/legal/commercial milestones are merged
[ ] confirm protected branch settings are understood
[ ] confirm no pending PRs are blocked by the visibility change
[ ] confirm local repository backup exists
[ ] confirm remote origin is correct
```

### Public assets

```text
[ ] identify public beta runtime release package
[ ] identify release notes that should remain available
[ ] identify screenshots that should remain public
[ ] identify README / landing copy that should remain public
[ ] identify beta terms and license notice that should remain public
[ ] identify SHA256 checksums that should remain public
```

### Sensitive material review

```text
[ ] check repository for API keys or secrets
[ ] check repository for private documents
[ ] check repository for personal data
[ ] check repository for customer data
[ ] check repository for internal-only notes
[ ] check repository for local paths that should not be public
[ ] check release packages for bundled private data
```

### Legal/commercial material

```text
[ ] LICENSE.txt exists
[ ] BETA-TERMS.md exists
[ ] third-party notices placeholder exists
[ ] commercial strategy docs exist
[ ] controlled release policy exists
[ ] public beta wording is clear
[ ] no open-source license is accidentally implied
```

### Public communication

```text
[ ] prepare short public note if repository visibility changes
[ ] clarify that official releases remain controlled
[ ] clarify that public beta terms still apply
[ ] avoid implying product shutdown
[ ] avoid implying production readiness
[ ] avoid exposing commercial roadmap details publicly
```

---

## Recommended pre-private command checks

Run before changing visibility:

```powershell
git switch main
git fetch origin
git reset --hard origin/main
git status --short
git log -5 --oneline --decorate
```

Optional file checks:

```powershell
Get-ChildItem .\docs\legal
Get-ChildItem .\docs\commercial
Get-ChildItem .\docs\public
```

---

## What should not happen in this milestone

Do not:

```text
change GitHub visibility
delete releases
delete public beta packages
remove README
remove beta terms
remove license notice
publish a new runtime package
add payment flow
add license activation
change runtime behavior
```

---

## Completion criteria

This milestone is complete when:

```text
repository privacy transition checklist is documented
public surface after private repo is documented
migration risks are documented
controlled distribution next steps are documented
v0.3.6 checklist is documented
no runtime files changed
no repository visibility changed
```
