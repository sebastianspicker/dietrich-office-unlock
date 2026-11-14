# Changelog

All notable changes to Dietrich are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[PEP 440](https://peps.python.org/pep-0440/) version identifiers.

Dietrich is pre-1.0 alpha software: commands, Python APIs, and output formats
can change between releases until a stable release is tagged.

## [Unreleased]

### Fixed

- An unlock no longer replaces its own input. `--output` naming the input file (or
  a link to it) is refused on every interface, even with `--force`.
- PDF hash export: R4 lines carry the real `/EncryptMetadata` flag, and R5/R6
  lines use the `pdf2john` layout (48-byte U/O, no `/Perms`). R5 now maps to
  hashcat mode 10600.
- Signature stripping keeps `[Content_Types].xml` `Default` entries and the
  original XML bytes, and detects packages signed through the
  `digital-signature/origin` relationship outside `_xmlsignatures/`.
- `--vba` patches the PROJECT stream through its sector chain and reports only
  changes it made. `LogGC=` and other non-verifier lines are left alone.
- Legacy `.doc` read-only/write-reservation flags use the MS-DOC bits (0x0400,
  0x0800); `lKey` is no longer touched. Encrypted legacy `.xls`/`.doc` files are
  detected at inspection and never soft-patched. `.xls` files with embedded
  charts are accepted, and `--worksheets-only` is honoured for `.xls`.
- hashcat results in `$HEX[...]` form are decoded and verified before use; hashcat
  error exits are reported with an output tail. `--hashcat-arg` can no longer
  override controlled options through attached or abbreviated forms.
- Local masks follow hashcat: `?a` is 95 printable characters, `?s` includes
  space, `?h`/`?H` are added, and unknown tokens are rejected. A charset without
  a maximum length searches up to length 4.
- Malformed input (corrupt deflate members, deep CFB directory trees, oversized
  ZIP central directories, UTF-16 XML parts, bad agile `EncryptionInfo` XML,
  `~unknownuser` paths, missing files) gives a plain error instead of a
  traceback or a corrupt output.
- Publication works on filesystems without hard links and skips the directory
  fsync on Windows. The GUI launcher no longer passes the session token on the
  browser command line.

### Changed

- Documented the authorized-use boundary and legal basis in `CLAUDE.md`,
  `docs/SCOPE.md`, and `docs/FRAMING.md`, and aligned `README.md`,
  `CONTRIBUTING.md`, and `SECURITY.md` with the same wording. No behavior
  changed.
- Redesigned the static `site/` demo around a "shear line" concept: the
  fixture-only Instrument Workbench now reads as a local document-locksmith's
  bench, with a locked-to-open readout gauge, a spec-sheet findings list, and a
  reworked screenshot tour. Behaviour, fixtures, the simulation/authorization
  notices, keyboard shortcuts, and the no-network/no-storage guarantees are
  unchanged; the work is markup and styling only (system fonts, no new assets).
- The experimental OOXML mutation-research generator moved out of the main
  `dietrich` command into its own `dietrich-research` console entry point (also
  runnable as `python -m dietrich.research`). The capability is unchanged; only
  its entry point moved, so the product CLI now contains document-assessment
  flags only.

### Added

- The public `dietrich` package now exports the assessment vocabulary returned
  by `inspect_document`/`inspect_workbook`: `ProtectionLayer`, `CapabilityCode`,
  `BlockerCode`, `Capability`, and `Blocker`. Callers can import and annotate
  with these instead of comparing attribute strings.

### Removed

- **Breaking (experimental):** removed the `--research-fuzz`, `--fuzz-count`, and
  `--fuzz-seed` flags from the `dietrich` command. There is no deprecation shim;
  old invocations now fail with an argparse error. Migrate:
  `dietrich IN --research-fuzz --fuzz-count N --fuzz-seed S` becomes
  `dietrich-research IN --count N --seed S`.
- Deleted the unused `dietrich.types` compatibility shim. Its names are the
  domain models already exported from the top-level `dietrich` package.

### Fixed

- Hardened untrusted Office and PDF parsing: Agile password work factors are
  capped, CFB parser failures remain fail-closed, raw PDF encryption dictionaries
  use bounded structural indexing, and malformed marked custom properties no
  longer enter a regular-expression recovery path.
- Legacy CFB mutation now validates exact FAT and MiniFAT chain lengths, rejects
  cycles and invalid sectors, and resolves streams by complete storage identity;
  ambiguous duplicate stream names are rejected.
- Documented toolchain commands (`README.md`, `CONTRIBUTING.md`)
  now match CI: the type-check and demo lanes require the `demo` dependency
  group, and linting covers `scripts`.

## [0.4.0a5]

Alpha snapshot. See [docs/ALPHA.md](docs/ALPHA.md) for the current capability
and compatibility matrix, and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for
component ownership and safety invariants.
