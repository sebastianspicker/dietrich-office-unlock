# Contributing

Thanks for helping with Dietrich. Contributions should be focused, testable, and
limited to authorized document workflows.

## Before you start

Read [docs/SCOPE.md](docs/SCOPE.md). Dietrich works on documents the operator
owns or has explicit permission to modify; changes aimed at third-party files,
rights-managed content, or DRM are out of scope. If a change needs to widen the
boundary, update `docs/SCOPE.md` first and say why.

## Set up

Install [uv](https://docs.astral.sh/uv/), then from the repository root. The
`demo` group carries the Playwright runtime that `pyright` and the browser/demo
tests need:

```bash
uv sync --locked --all-extras --group demo
```

CI runs on Python 3.12 on Ubuntu; 3.11 to 3.13 are supported. `.python-version`
pins local development to 3.12 to match CI. Do not update `uv.lock` as a
side effect of an unrelated change.

## Make a change

1. Trace the use case in `src/dietrich/application/` to its format
   implementation.
2. Reproduce the current behavior with the narrowest relevant test.
3. Change the shared implementation instead of duplicating policy in the CLI or
   TUI.
4. Add synthetic tests for success, failure, and output safety.
5. Update the documentation that owns any changed flags, fields, dependencies,
   format support, or architectural boundary.
6. Run the repository gate.

### Where changes belong

| Change | Lives in |
| --- | --- |
| A new document semantic for one format | that format package |
| Cross-format workflow policy | `application/` |
| Pure shared records | `domain/` |
| Untrusted I/O limits and final publication | `safety/` |
| Input collection or rendering | `cli.py`, `gui/`, or `tui/` |

Format writers create and validate unpublished candidates. They do not choose
final targets or overwrite policy, and the only publisher is
`safety/artifact_transaction.py`.

### What not to add

Do not add private, licensed, institutional, or identifying documents. Tests must
build the smallest synthetic data they need at runtime. Do not add IRM bypasses,
DRM circumvention, signature impersonation, document exploits, remote
password-cracking services, or features aimed at files the operator does not own
or have permission to modify.

## Verify

CI runs automatically only for pull requests authored by `dependabot[bot]`; other changes
can use **Run workflow** after local verification. Pages publishing requires a separate
manual run on `main`; see [release and distribution](docs/RELEASE.md).

Run from the repository root:

```bash
uv lock --check --offline
uv run ruff check src examples scripts
uv run ruff format --check src examples scripts
uv run pyright
```

For the offline distribution build, use a fresh output directory:

```bash
build_dir="$(mktemp -d)"
uv build --offline --no-sources --no-create-gitignore --out-dir "$build_dir"
```

Packaging or entry-point changes also require:

```bash
uv run python scripts/check_distributions.py "$build_dir" --python 3.12
```

That script checks archive boundaries, the bundled TUI stylesheets, and the GUI
assets, installs each artifact in its own clean environment, and smokes every
console entry point (`dietrich`, `dietrich-tui`, `dietrich-gui`,
`dietrich-research`) outside the checkout.

For static demo work, run the checks listed in [site/README.md](site/README.md).

The demo dependency group does not change installed package requirements. Terminal changes need
a manual pass over focus order, labels, narrow layouts, busy states, and failure
messages.

## Open a pull request

State clearly:

- the behavior changed and the formats affected;
- security, compatibility, and output-safety implications;
- the exact checks run and their results;
- dependency, viewer, platform, or clean-install validation you did not perform.

Do not mix unrelated formatting or documentation changes into a functional
patch, and do not commit generated captures.
