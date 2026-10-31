# Dietrich alpha: known issues

This is an early test release. These are the problems we know about. Please
don't report them again unless you have new details, such as a file that shows
the problem or a case where the workaround doesn't help.

## Encrypted Office files may be refused

Some password-encrypted Excel, Word or PowerPoint files are rejected with:

> is not a readable OLE/CFB file: CFB sector chain exceeds the declared size

We have seen this with files encrypted by third-party tools. We have not yet
confirmed whether files saved from Microsoft Office itself are affected.

- **Workaround:** none yet. Open the file in Office with its password and save an
  unencrypted copy, or decrypt it with the tool that encrypted it. Hash export and
  hashcat hand-off for such files are blocked by the same check.
- **Please report:** whether the file was saved from Office (and which version) or
  from another tool. Only share a file if it holds no real data. A freshly created
  test document with a throwaway password is ideal.

## Office hash lines from earlier builds

Builds before this alpha exported Office recovery hashes with their fields run
together, and hashcat did not accept them. Export the hash again with this
version. Lines starting with `$office$*` are in the correct format.

## Parallel password search can fail on locked-down machines

With more than one worker (`--workers 2` or higher, or the workers field in the
graphical and terminal interfaces), some sandboxed or locked-down systems block
the local connection that parallel search needs. You will see a technical error
printout followed by:

> error: parallel password search could not start its local worker manager ... Retry with a single worker (--workers 1).

- **Workaround:** use one worker (the default). It's slower but works everywhere.
  The extra printout above the error line is harmless.

## Platform coverage

- Automated checks currently run on Linux with Python 3.12 only. macOS works in
  our own use. Windows is best-effort: stopping a password search there may leave
  helper processes running until they finish.
- Python 3.11 to 3.13 is the supported range. Newer Python versions installed
  and ran fine in our checks but are not officially covered.

## How to report a bug

Please include:

1. Your operating system and version, and the output of `python3 --version`.
2. The Dietrich version, from
   `python3 -c "import dietrich; print(dietrich.__version__)"` run in the same
   environment you installed Dietrich into.
3. The exact command or the steps you clicked, and what you expected to happen.
4. The full error output. On the command line, copy everything printed, including
   any technical printout above the `error:` line. Adding `--json` to an
   `--inspect` run gives a machine-readable description of the file that is safe
   to share (it contains no document contents or passwords).
5. Whether the problem still happens with `--workers 1`, if you were searching for
   a password.

Do **not** attach real documents, passwords or recovered passwords. If a file is
needed to reproduce the problem, make a small new test file that shows it.
