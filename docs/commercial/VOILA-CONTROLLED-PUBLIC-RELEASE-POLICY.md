# Voila Controlled Public Release Policy

## Purpose

This document defines a safer release policy for Voila as a proprietary product.

The goal is to keep public distribution controlled while maintaining tester trust.

---

## Official public release channel

Recommended official channels:

```text
GitHub Releases while repository remains public or controlled
CX Trading / CyberXecure website later
direct tester links for private builds
```

Avoid:

```text
random file sharing links
unversioned ZIP files
old packages without terms
packages without checksums
packages that mix internal and public artifacts
```

---

## Required release assets

Each public package should include or link to:

```text
version number
release notes
ZIP or installer
SHA256 checksum
README / tester instructions
license notice
beta terms or EULA
known limitations
```

---

## Release classification

Use clear labels:

```text
Public Beta Runtime Package
Tester Demo Build
Language Pack Release Candidate
Internal Build
Supporter Build
Pro Build
```

Do not mix these labels.

---

## Page-limit policy

Some builds may have limits.

Recommended wording:

```text
Public beta runtime package:
- intended for public evaluation
- limits described in release notes

Tester demo build:
- may include strict page limits
- intended for selected testers
- not necessarily the same as public runtime package

Pro / Supporter builds later:
- limits defined by license tier
```

---

## Before publishing a package

Checklist:

```text
[ ] package version is clear
[ ] package type is clear
[ ] release notes are clear
[ ] beta terms / EULA included
[ ] SHA256 generated
[ ] no secrets included
[ ] no private documents included
[ ] no internal-only docs included by mistake
[ ] third-party obligations reviewed
[ ] package starts locally
[ ] package stops cleanly
```

---

## Public communication

Use simple wording:

```text
Voila is proprietary beta software.
Official packages are distributed only through controlled release channels.
Do not redistribute or repackage Voila without permission.
```

---

## Future improvements

Later:

```text
installer instead of ZIP
digital code signing
license activation
supporter/pro release channels
download page on official website
private tester portal
```
