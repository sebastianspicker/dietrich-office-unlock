"""Atomic output publish (replace or exclusive link) to avoid clobber races."""

from __future__ import annotations

import errno
import os
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from dietrich.errors import OutputExistsError


@contextmanager
def temporary_output_path(target_path: Path) -> Iterator[Path]:
    """Yield an adjacent temporary path and remove it unless publication consumed it."""
    target = Path(target_path)
    with tempfile.NamedTemporaryFile(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=target.parent,
        delete=False,
    ) as temporary_file:
        temp_path = Path(temporary_file.name)
    try:
        yield temp_path
    finally:
        temp_path.unlink(missing_ok=True)


def same_file(source: Path, target: Path) -> bool:
    """Return True when target names the source file, including links to it."""
    try:
        return os.path.samefile(source, target)
    except FileNotFoundError:
        return source.resolve(strict=True) == target.resolve(strict=False)


def publish_output(temp_path: Path, target_path: Path, *, overwrite: bool) -> None:
    """Publish a verified temporary file without a TOCTOU overwrite race."""
    if overwrite:
        os.replace(temp_path, target_path)
        return

    try:
        os.link(temp_path, target_path)
    except FileExistsError as exc:
        raise OutputExistsError(f"{target_path} already exists.") from exc
    except OSError as exc:
        if exc.errno not in _NO_HARD_LINKS:
            raise
        _copy_exclusive(temp_path, Path(target_path))
    temp_path.unlink()


# exFAT, FAT, and many SMB shares refuse hard links with one of these.
_NO_HARD_LINKS = {
    errno.EPERM,
    errno.EACCES,
    errno.ENOTSUP,
    errno.EOPNOTSUPP,
    errno.EXDEV,
    errno.ENOSYS,
    errno.EMLINK,
}


def _copy_exclusive(temp_path: Path, target_path: Path) -> None:
    """Create the target exclusively and copy into it; never replace an existing file."""
    mode = os.stat(temp_path).st_mode & 0o777
    try:
        descriptor = os.open(target_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    except FileExistsError as exc:
        raise OutputExistsError(f"{target_path} already exists.") from exc
    try:
        with os.fdopen(descriptor, "wb") as target, temp_path.open("rb") as source:
            shutil.copyfileobj(source, target)
            target.flush()
            os.fsync(target.fileno())
    except BaseException:
        target_path.unlink(missing_ok=True)  # only the partial file this call created
        raise
