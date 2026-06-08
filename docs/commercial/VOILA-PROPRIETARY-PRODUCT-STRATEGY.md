# Voila Proprietary Product Strategy

## Product direction

Voila is not intended to be an open-source-first project.

The preferred direction is:

```text
proprietary product
private source repository
controlled public releases
clear beta terms
commercial licensing later
```

---

## Positioning

Voila should be positioned as a product, not as a code repository.

Public communication should focus on:

```text
what problem Voila solves
who it helps
how it turns PDFs into learning material
what the beta can do
how testers can try it
how feedback can be sent
```

Public communication should avoid:

```text
unnecessary implementation details
internal architecture exposure beyond high-level overview
commercial roadmap details that competitors can copy
unprotected source-code distribution
```

---

## Public beta value

The public beta can still be useful without exposing source code.

Public beta should provide:

```text
downloadable Windows package
clear start instructions
screenshots
release notes
known limitations
beta terms
feedback form or contact path
```

---

## Commercial protection layers

Recommended protection layers:

```text
private repository
all-rights-reserved license notice
beta terms
EULA for Windows package
third-party notices
controlled release package
SHA256 checksums
official download channel
code signing later
license keys later
```

---

## Supporter / Pro direction

Possible future model:

```text
Free beta / tester demo:
- limited page count or limited feature set
- feedback-oriented
- non-commercial use

Supporter:
- higher page limit
- early access
- priority fixes
- supporter-only builds
- personal use license

Pro:
- larger page limits
- commercial/internal use
- improved export tools
- better OCR workflows
- batch processing later
- priority support later
```

---

## Repo visibility recommendation

Recommended:

```text
make development repository private before adding stronger commercial features
keep public release packages controlled
keep public docs and website separate from source code
```

Alternative:

```text
keep a small public showcase repository
move actual source to private repository
```

---

## Decision record

Current strategic decision:

```text
Voila should proceed as a proprietary product with private development and controlled public releases.
```
