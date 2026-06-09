# Voila Windows Package EULA Plan

Milestone:

```text
v0.3.8-voila-eula-for-windows-package-plan
```

## Purpose

Plan the End User License Agreement documentation needed for Voila Windows packages before broader distribution, monetization, Supporter/Pro builds, or a private-repository transition.

This milestone is planning-only.

It does not add:

```text
runtime changes
backend changes
frontend behavior changes
dependency changes
package rebuilds
license activation
payment flow
GitHub visibility changes
final legal approval
```

## Why Voila needs a Windows package EULA

Voila is moving toward a proprietary product model:

```text
private development
controlled public releases
clear beta terms
future Supporter / Pro licensing
```

A Windows package EULA should clarify the user rights and restrictions that apply when someone downloads and runs a Voila package.

The EULA should work together with:

```text
LICENSE.txt
BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md
release notes
public download wording
controlled release policy
future Supporter / Pro terms
```

## EULA goals

The EULA should make these points clear:

```text
Voila is proprietary software
public beta use is limited to evaluation/testing unless stated otherwise
redistribution is not allowed without permission
resale is not allowed without permission
rebranding/repackaging is not allowed
generated content must be reviewed by the user
third-party components remain under their own licenses
Voila is provided as beta software without warranty
the user is responsible for documents they process
confidential/sensitive documents should not be used in public demos or feedback
```

## Package inclusion plan

For each future Windows package, include:

```text
LICENSE.txt
BETA-TERMS.md or EULA.txt
THIRD-PARTY-NOTICES.md
README-TESTERS.txt or README-WINDOWS.txt
RELEASE-NOTES.txt
SHA256 checksum published externally
```

Recommended package path:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/THIRD-PARTY-NOTICES.md
README-WINDOWS.txt
RELEASE-NOTES.txt
```

## EULA versioning

Recommended EULA version format:

```text
Voila EULA v0.1-beta
Effective date: YYYY-MM-DD
Applies to: Voila public beta / tester demo / Supporter / Pro, as stated in release notes
```

The EULA should be versioned because terms may differ between:

```text
Public Beta Runtime Package
Tester Demo Build
Supporter Build
Pro Build
Commercial / Team Build
```

## EULA acceptance options

### Current beta package

For the current ZIP-style beta package:

```text
include EULA.txt in package
reference EULA in README
reference EULA in release notes
state that using the package means accepting the beta terms/EULA
```

### Future installer

For a future Windows installer:

```text
show EULA during installation
require acceptance before install
include EULA in installed app folder
include link in About / Help later
```

### Future app UI

Later, the app may include:

```text
About dialog
License / Terms link
version and package type
publisher name
support/contact link
```

## EULA draft review

Before using the EULA commercially:

```text
review with legal counsel if needed
verify third-party notices
verify redistribution obligations
verify payment/refund wording if paid builds exist
verify consumer law requirements for target markets
verify privacy/data handling wording
verify warranty/liability limitations
```

## Not included in this milestone

This milestone does not decide:

```text
final pricing
final Supporter / Pro rights
subscription vs one-time payment
online vs offline activation
refund policy
privacy policy
installer implementation
code signing
```

## Recommended next milestone

```text
v0.3.9-voila-third-party-license-audit-plan
```

or:

```text
v0.3.9-voila-eula-draft-beta-package
```
