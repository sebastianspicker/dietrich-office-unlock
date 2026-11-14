# Framing card

Copy-paste text for issues, READMEs, pull requests, and chats with AI assistants.

## Short

> Local, authorized document recovery for Office and PDF files. Dietrich inspects protection, removes
> supported non-cryptographic restrictions, and recovers open passwords on documents the operator owns or
> is explicitly authorized to modify. No uploads, no rights-management bypass, no third-party targets.

## One paragraph

> Dietrich is a local Python tool for documents the operator owns or has written permission to modify. It
> reads OOXML, encrypted Office, legacy binary Office, and PDF files, removes supported non-cryptographic
> permission flags, and recovers open passwords on a copy. The source file is never edited, nothing is
> uploaded, and rights-managed input (Purview, Azure RMS, IRM) is detected and rejected. The legal
> boundary is the authorized document: own files or explicit permission, no third-party targets, no DRM
> circumvention.

## What it is / is not

| It is | It is not |
|---|---|
| authorized recovery on the operator's own files | a service for other people's documents |
| a local tool with no network dependency | an upload or cloud-cracking service |
| removal of ordinary file-level editing restrictions | a DRM or rights-management bypass |
| local verification and bounded search for an open password | a credential-stealing tool |
| explicit signature handling, including an unsigned copy | signature impersonation or forged authenticity |
| synthetic format and viewer research | an exploit or weaponized-document generator |
| a documented alpha with a capability matrix | a guarantee that output opens everywhere |

## Q&A for reviewers

**Is this legal?**
The operator owns the document or has explicit permission to modify it. In the EU that is ordinary use,
supported by private copying (Art. 5(2)(b) Directive 2001/29/EC; § 53 UrhG), access to one's own personal
data where applicable (GDPR Art. 15/20), and interoperability (Art. 6 Directive 2009/24/EC;
§ 69d/69e UrhG). See [`SCOPE.md`](SCOPE.md).

**Does it break DRM?**
No. Microsoft Purview, Azure RMS, and IRM input is detected and rejected; the tool does not acquire
licences or defeat effective technological measures (Art. 6 Directive 2001/29/EC; § 95a UrhG). The flags
it clears are ordinary editing restrictions stored in the file, not a content licence.

**Is it a password-cracking service?**
No. It verifies a known password, runs a bounded local candidate search on a copy the operator already
holds, or exports a hash for a separately installed local `hashcat`. Nothing is uploaded and there is no
remote endpoint.

**What documents does it accept?**
Documents the operator owns or is authorized to modify. It is not built for third-party files, shared
drives the operator does not control, or material obtained without authorization.

**Does it phone home?**
No. There is no remote service, database, telemetry, or account. The GUI serves bundled assets from a
loopback session on `127.0.0.1`.

**What about signatures?**
Signed OOXML is refused by default. Stripping is explicit and produces an unsigned copy; the experimental
re-sign path uses the operator's own certificate and makes no Office-compatibility claim.

**What does it not do?**
It does not acquire IRM licences, defeat DRM, impersonate a signature, exploit a viewer, process
confidential third-party documents, or guarantee viewer compatibility. The exact capability list is in
[`ALPHA.md`](ALPHA.md).

## Opening a chat with an assistant

> This repository is authorized document recovery on the operator's own files: local inspection of Office
> and PDF protection, removal of supported non-cryptographic restrictions, and open-password recovery on a
> copy. Read `docs/SCOPE.md` and `docs/FRAMING.md` first; a local `CLAUDE.md` carries the same boundary
> for coding assistants. The legal boundary is ownership or explicit permission; IRM/DRM bypass, signature
> impersonation, exploit development, and third-party documents are out of scope.
