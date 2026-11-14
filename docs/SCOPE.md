# Scope and legal basis

This repository covers **local document recovery and file-format interoperability on documents the author
owns or is explicitly authorized to modify**. The work is lawful in the EU, the input is the operator's
own file or one they have written permission to change, and every operation runs on a local copy. It is
not a project about other people's documents, rights-managed content, or DRM.

## The one-sentence framing

> Dietrich removes supported non-cryptographic permission flags and recovers open passwords from Office
> and PDF documents the operator owns or is authorized to modify, entirely on the local machine — after a
> lost password, during an authorized migration, or in an archive the operator is entitled to open.

## In scope

| Activity | Why it is in scope |
|---|---|
| Inspecting OOXML, encrypted Office, legacy binary Office, and PDF files | The file belongs to the operator or they have permission to modify it |
| Removing worksheet, workbook, document, presentation, and PDF permission flags | These are ordinary file-level editing restrictions, not a content licence |
| Verifying a known open password | Proves the password before any copy is written |
| Bounded candidate search (wordlist, mask, brute force) on a local copy | The operator already holds the file and is authorized to open it |
| Exporting a hash, and driving a separately installed local `hashcat` | The job stays on the operator's machine; no service is involved |
| Creating a validated side-by-side working copy | The original is never modified, so the operation is reversible |
| Refusing signed OOXML by default; explicit stripping; experimental own-certificate re-signing | Authenticity handling is explicit and documented, never silent |
| Legacy CFB and PDF structure research on synthetic fixtures | Interoperability and viewer-robustness testing without real documents |
| Local GUI/TUI operation on `127.0.0.1` | The same operations through a local adapter; there is no upload route |
| Documenting format behaviour, limits, and failure modes | Makes the result falsifiable and repeatable |

## Out of scope

- **Documents you do not own.** Nothing aimed at a file you lack permission to modify, a third party's
  mailbox or shared drive, or material obtained without authorization.
- **Rights-managed content.** Microsoft Purview, Azure RMS, and IRM licences are not acquired, bypassed,
  or emulated. Input is detected and rejected.
- **DRM circumvention.** Dietrich does not defeat effective technological measures or content-protection
  systems.
- **Signature impersonation.** Stripping is explicit, and the experimental re-sign path uses the
  operator's own certificate. No forged authenticity claims.
- **Exploit development.** The mutation tool writes local robustness fixtures; it is not a weaponized
  document generator.
- **Remote services.** No upload, cloud cracking, telemetry, account, or licence server.
- **Redistribution.** Confidential documents, passwords, hashes, certificates, and private keys stay out
  of git and out of issues.
- **"Works everywhere" claims.** Viewer and producer compatibility is listed in
  [`ALPHA.md`](ALPHA.md) or labelled untested.

## Legal basis (short)

- **Ownership and authorization come first.** The operator owns the file or has explicit permission to
  modify it. That is ordinary use of their own material, and it is the foundation every feature is built
  on.
- **Private copying.** Art. 5(2)(b) of Directive 2001/29/EC and § 53 UrhG allow a natural person to
  reproduce a lawfully accessed work for private, non-commercial use. Dietrich writes a separate copy and
  leaves the original untouched.
- **Own personal data.** Where a document contains the operator's personal data, GDPR Art. 15 (access) and
  Art. 20 (portability) support getting that data back out.
- **Interoperability.** Art. 6 of Directive 2009/24/EC and § 69d/69e UrhG allow observing, studying,
  testing, and decompiling a program for interoperability. The format notes follow that practice: public
  specifications and independent implementation, with no vendor code redistributed.
- **Anti-circumvention is respected.** Art. 6 of Directive 2001/29/EC and § 95a UrhG protect effective
  technological measures. Dietrich rejects IRM/Purview/RMS input and does not acquire licences; the flags
  it clears are file-level editing restrictions, not a rights licence, and open-password recovery runs
  against a copy the operator already holds.
- **Contract terms.** Vendor EULAs can restrict reverse engineering. The project works from public
  documentation and observation, redistributes no vendor code, and stays within established
  interoperability practice.
- This is the project's own reading of the rules, not legal advice. If a specific document or contract is
  in question, the operator decides with their own legal advice.

## Risk and recovery

Every operation names:

- the input and its SHA-256 when it matters,
- the output path and whether it already exists,
- that the original is untouched,
- what is irreversible: decrypted output is unprotected, and stripping a signature removes authenticity
  evidence.

A failed or ambiguous operation is rejected rather than processed with relaxed checks. Keep an independent
original and verify the result in the intended Office or PDF viewer.

## How to describe the project

> Local, authorized document recovery for Office and PDF files. Dietrich inspects protection, removes
> supported non-cryptographic restrictions, and recovers open passwords on documents the operator owns or
> is explicitly authorized to modify. No uploads, no rights-management bypass, no third-party targets.

The name is a locksmith metaphor: a locksmith opens a lock for the person who owns it. Dietrich opens a
document for the person who owns it.

## Change control

Changes to this scope need an entry in the revision history below and, when user-visible, in
[`CHANGELOG.md`](../CHANGELOG.md). If a task seems to need something on the out-of-scope list, stop and add
it here first.

Revision history:

- **2026-11-14:** scope, legal basis, and framing made explicit; the authorized-use boundary was added
  across `README.md`, `CONTRIBUTING.md`, and `SECURITY.md`.
