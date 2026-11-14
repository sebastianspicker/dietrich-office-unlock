# Dietrich

**The office picklock.**

Dietrich is a local Python tool for documents you own or are authorized to
modify. It inspects protection in Microsoft Office and PDF files, removes
supported non-cryptographic restrictions, and recovers open passwords — all
without sending your files anywhere.

_Claude was used to polish and proof-read the code and documentation of this repository._

This is authorized document recovery: the operator owns the file or has explicit
permission to modify it, and every operation runs on a local copy. That boundary
is what makes the work lawful in the EU — see
[Scope and legal basis](#scope-and-legal-basis) and [docs/SCOPE.md](docs/SCOPE.md).
Dietrich does not acquire rights-management licences, bypass DRM/IRM, or target
third-party documents.

<details>
<summary>Status and limitations</summary>

Dietrich is independently developed experimental document-recovery software. Developed
independently alongside my main professional work. Version 0.4.0a5 is an alpha: commands,
Python APIs and output formats may change. Its format-specific capabilities and
experimental operations are a foundation to review and test against your own documents,
rather than a ready-to-use recovery service.

**Authorized use.** Use only documents you own or have explicit permission to
modify. Password recovery and restriction removal grant no permission to access
someone else's files; Dietrich is not a service for third-party documents, DRM,
or rights-managed content. Keep independent originals and verify output in the
intended Office or PDF viewer.

</details>

[![CI](https://github.com/sebastianspicker/dietrich-office-unlock/actions/workflows/ci.yml/badge.svg)](https://github.com/sebastianspicker/dietrich-office-unlock/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)](docs/ALPHA.md)

You get a command-line interface, a local graphical interface, an optional
Textual terminal interface, and a small Python API.

## Screenshot tour

The graphical interface walks through four steps and runs the same Python
operations as the CLI. Every document stays on your machine.

| | |
| --- | --- |
| ![Choose a local file](site/screenshots/01-choose.png) | ![Review detected restrictions and the output path](site/screenshots/02-review.png) |
| **1 · Choose a file** — pick a local Office or PDF document. | **2 · Review restrictions** — choose what to remove and where to save. |
| ![Validation checklist while the working copy is created](site/screenshots/03-processing.png) | ![Saved working copy with removal counts and warnings](site/screenshots/04-result.png) |
| **3 · Validate and save** — the copy is reopened and checked before publication. | **4 · Read the result** — removal counts, warnings, and the saved path. |

The interface adapts to narrow screens too —
[390&nbsp;px review capture](site/screenshots/05-review-mobile.png).

Want to click through without installing anything? The
[Instrument Workbench demo](https://sebastianspicker.github.io/dietrich-office-unlock/) is a
static, fixture-only simulation of the terminal interface. It cannot select,
upload, inspect, or change files, and it never runs Dietrich.

## What Dietrich does

For supported restriction removal, the default workflow keeps the original separate:

```mermaid
flowchart LR
  A[Authorized document] --> B[Inspect restrictions]
  B --> C[Create working copy]
  C --> D[Validate file structure]
  D --> E[Save separate output]
```

Format validation does not replace checking the result in your Office or PDF viewer.

- Inspects OOXML, encrypted Office, legacy binary Office, and PDF inputs.
- Removes supported worksheet, workbook, document, presentation, and PDF
  permission restrictions.
- Verifies passwords, runs bounded local candidate searches, exports recovery
  hashes, or drives a separately installed `hashcat`.
- Refuses rights-managed input and signed OOXML by default.
- Creates a validated side-by-side working copy and leaves the source untouched.

Support varies by format. Legacy `.ppt` mutation is unavailable, VBA verifier
clearing and OOXML re-signing are experimental, and Dietrich does not acquire IRM
licenses or verify how output looks in Microsoft Office, LibreOffice, or
third-party PDF viewers. The [capability matrix](docs/ALPHA.md) lists exact
coverage.

## Requirements

- Python 3.11 to 3.13. CI uses Python 3.12 on Ubuntu for Dependabot pull requests
  or explicit manual runs.
- Optional Python dependencies for the features you use:
  `msoffcrypto-tool`, `pikepdf`, `olefile`, `cryptography`, and `textual`.
  The tested versions are the ones locked in `uv.lock` (currently
  msoffcrypto-tool 6.0.0, pikepdf 10.11.0, olefile 0.47, cryptography 50.0.0,
  lxml 6.1.1, textual 8.2.8). Older versions that the declared minimums in
  `pyproject.toml` still allow are not tested. The locked PDF dependency path
  uses Pillow 13.0.0.
- A separately installed `hashcat` executable on `PATH` for `--hashcat`.

## Install

From a checkout, create a virtual environment and install the extras you need:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[full]'
```

Swap `full` for one or more of `crypto`, `pdf`, `legacy`, `sign`, or `ui` to
install only selected features. There is no PyPI package yet.

## Command line

Inspect a file without writing anything:

```bash
dietrich report.xlsx --inspect
dietrich report.xlsx --inspect --json
```

Create an editable working copy:

```bash
dietrich report.xlsx
dietrich report.xlsx --output report_editable.xlsx
dietrich report.xlsx --worksheets-only
```

Output defaults to `NAME_unprotected.EXT` beside the input. An existing target
is rejected unless you pass `--force`.

Supply or search for an open password:

```bash
dietrich secret.xlsx --password 'known-password'
dietrich secret.xlsx --wordlist passwords.txt
dietrich secret.xlsx --mask 'Office-?d?d?d?d'
dietrich secret.xlsx --brute --charset digits --max-length 4
```

Candidate searches default to a ceiling of 5,000,000. Export a hash, or hand the
job to a local `hashcat`:

```bash
dietrich secret.xlsx --export-hash hashcat
dietrich secret.xlsx --hashcat --wordlist passwords.txt
```

Signed OOXML packages are refused by default. Stripping signatures produces an
unsigned copy:

```bash
dietrich signed.xlsx --strip-signatures --output unsigned.xlsx
```

Run `dietrich --help` for every option.

## Graphical interface

```bash
dietrich-gui
dietrich-gui report.xlsx
```

The local browser interface guides you through choosing a document, reviewing
its restrictions, creating a separate working copy, and reading the validated
result. Advanced controls cover password recovery, signature handling, VBA,
re-signing, and hash export. Nothing is uploaded to a remote service.

The launcher opens a session URL on `127.0.0.1`. Keep that URL private — it
grants access to the local session. Use `--no-browser` to open it yourself, and
press Ctrl+C in the launching terminal to stop after active-operation cleanup.
Closing the tab does not stop the Python process. See the
[graphical interface guide](docs/GUI.md) for details.

## Terminal interface

Install the `ui` or `full` extra, then run:

```bash
dietrich --tui
dietrich-tui report.xlsx
```

The TUI calls the same application operations as the CLI, and its recent-path
list lives only for the current process. Keyboard commands: `i` inspect, `u`
unlock, `e` export a hash, `Escape` cancel, `?` help, and `q` quit after cleanup.
See the [terminal interface guide](docs/TUI.md) for details.

## Python API

The supported top-level functions are `inspect_document`, `unlock_document`,
`inspect_workbook`, `unlock_workbook`, and `export_document_hash`.

```python
from pathlib import Path

from dietrich import inspect_document, unlock_document

report = inspect_document(Path("report.xlsx"))
result = unlock_document(Path("report.xlsx"), Path("report_editable.xlsx"))
```

All five functions accept an optional keyword-only `control=OperationControl()`.
Use a fresh control for each operation. Another thread can call `control.cancel()`
and poll its `phase` and `cancellation_requested` properties. An accepted request
raises `OperationCancelledError` before publication; once publication begins,
`cancel()` returns `False` and the caller waits for the result. Native calls
finish before cancellation takes effect. Both types are exported from `dietrich`.

Internal format modules are not compatibility facades.

## How it stays local and safe

Dietrich has no remote service, database, or persistent state. It works on one
document at a time and publishes a new file rather than editing the original.

- Output defaults to a new sibling path, and `--force` is required to replace an
  existing target.
- Successful publication validates an unpublished candidate, writes a
  mode-`0600` temporary file, and performs one atomic replace.
- ZIP input is bounded: 10,000 members, 64 MiB per member, 512 MiB total, and a
  100:1 compression ratio. Duplicate and encrypted entries are rejected.
- The graphical interface serves a bundled frontend from an authenticated
  loopback session; it has no upload route and no general file download.

Read [SECURITY.md](SECURITY.md) for the full trust model.

## Scope and legal basis

Dietrich is built for an operator working on their own documents, or on
documents they have explicit permission to modify — a lost password, an
authorized migration, or an inherited archive they are entitled to open. The
full boundary is in [docs/SCOPE.md](docs/SCOPE.md); copy-paste wording for
issues and AI assistants is in [docs/FRAMING.md](docs/FRAMING.md).

- **Authorized input only.** The operator owns the file or has permission to
  modify it. Dietrich is not a service for opening other people's documents.
- **Local by design.** No upload, remote endpoint, account, or licence server.
  The graphical interface binds to `127.0.0.1`.
- **No rights-management bypass.** Purview, Azure RMS, and IRM input is detected
  and rejected; the tool does not acquire licences or defeat DRM.
- **Ordinary editing flags and open passwords.** Worksheet, workbook, document,
  presentation, and PDF permission flags are editing restrictions stored in the
  file. Password recovery verifies candidates locally against a copy you
  already hold.
- **Copies, not edits.** The source is left untouched and a validated sibling
  file is published.

In the EU, working on a document you own or are authorized to modify rests on
ordinary use and private copying (Art. 5(2)(b) Directive 2001/29/EC; § 53 UrhG),
and on access to your own personal data where applicable (GDPR Art. 15 and 20).
Format interoperability follows Art. 6 Directive 2009/24/EC and § 69d/69e UrhG.
Dietrich does not circumvent effective technological measures under Art. 6
Directive 2001/29/EC or § 95a UrhG. This is the project's own reading of the
rules, not legal advice.

## Repository map

| Path | Purpose |
| --- | --- |
| `src/dietrich/cli.py` | The `dietrich` command: flag parsing and output |
| `src/dietrich/dispatch.py` | Public facade that the CLI, GUI, TUI, and API call |
| `src/dietrich/domain/` | Typed assessments and unpublished artifact records |
| `src/dietrich/application/` | Assessment, recovery, hash-export, and make-editable use cases |
| `src/dietrich/ooxml/` | OOXML inspection, encryption, signatures, and candidate writing |
| `src/dietrich/pdf/` | PDF inspection, recovery, hash export, and candidate writing |
| `src/dietrich/legacy/` | Verified legacy Office inspection and equal-length transforms |
| `src/dietrich/crypto/` | Bounded password candidates and local hashcat integration |
| `src/dietrich/safety/` | Bounded container access and the sole artifact transaction |
| `src/dietrich/tui/` | Optional Textual adapter and packaged styles |
| `src/dietrich/gui/` | Local graphical adapter and bundled browser assets |
| `src/dietrich/research/` | Lab-only `dietrich-research` mutation generator |
| `scripts/` | Benchmarks and the built-artifact check |
| `site/` | Separately deployable static mock-data simulation |
| `docs/SCOPE.md` | Authorized-use boundary and legal basis |
| `docs/FRAMING.md` | Copy-paste wording for issues and AI prompts |

The [architecture guide](docs/ARCHITECTURE.md) is the source of truth for
component ownership, dependency direction, runtime flows, and safety invariants.
Its sequence diagrams show what happens, file by file, when you unlock a
document, recover a password, or press a button in the graphical interface.

## Development

Install the locked development environment. The `demo` group carries the
Playwright runtime that `pyright` needs:

```bash
uv sync --locked --all-extras --group demo
```

Run the repository gate from the root:

```bash
uv lock --check --offline
uv run ruff check src examples scripts
uv run ruff format --check src examples scripts
uv run pyright
```

The release gate also builds source and wheel distributions offline. See
[CONTRIBUTING.md](CONTRIBUTING.md) for change requirements and
[docs/RELEASE.md](docs/RELEASE.md) for distribution and Pages deployment.

## Troubleshooting

| Exit code | Meaning |
| ---: | --- |
| 0 | Operation completed |
| 1 | Password search exhausted without a match |
| 2 | Invalid arguments, unsupported or unsafe input, an output collision, or another operation error |
| 3 | A required optional dependency is not installed |

- Missing optional dependency? Install the matching project extra.
- `hashcat` not found? Install it separately and confirm it is on `PATH`.
- Output collision? Choose another path, or use `--force` after checking the
  target.
- IRM-protected input needs a valid license in an authorized application, so
  Dietrich cannot process it.
- Unsafe archives are rejected rather than processed with relaxed limits.

## Security and research

Work on copies of important documents. Decrypted output, unsigned copies,
password lists, exported hashes, certificates, and private keys are all
sensitive. Trust boundaries and vulnerability reporting live in
[SECURITY.md](SECURITY.md), and the authorized-use boundary in
[docs/SCOPE.md](docs/SCOPE.md).

Focused notes cover [legacy binary Office](docs/research/LEGACY_BINARY.md),
[OOXML signatures](docs/research/SIGNATURES.md), and
[OOXML mutation research](docs/research/VIEWER_ROBUSTNESS.md).

## License

Dietrich is licensed under the [MIT License](LICENSE).
