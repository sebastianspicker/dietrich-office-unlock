"""Reject hostile or unsafe OOXML ZIP metadata before member reads."""

from __future__ import annotations

import os
import struct
import zipfile
import zlib
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import unquote

from dietrich.errors import EncryptedDocumentError, SignedDocumentError, UnsafeArchiveError
from dietrich.operation import checkpoint
from dietrich.safety.bounded_io import read_zip_member_prefix
from dietrich.safety.snapshot import snapshot_checked

MAX_ARCHIVE_MEMBERS = 10_000
MAX_MEMBER_UNCOMPRESSED_BYTES = 64 * 1024 * 1024
MAX_TOTAL_UNCOMPRESSED_BYTES = 512 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100
# zipfile parses the whole declared central directory, whatever the entry count says;
# 512 bytes per allowed member is far above real OOXML part names.
MAX_CENTRAL_DIRECTORY_BYTES = MAX_ARCHIVE_MEMBERS * 512
SIGNED_PACKAGE_PREFIX = "_xmlsignatures/"
ROOT_RELATIONSHIPS = "_rels/.rels"
# ECMA-376 Part 2: the package relationship that names the signature origin part.
SIGNATURE_ORIGIN_RELATIONSHIP = (
    "http://schemas.openxmlformats.org/package/2006/relationships/digital-signature/origin"
)
MAX_ROOT_RELATIONSHIPS_BYTES = 1024 * 1024


def check_central_directory(path: Path) -> None:
    """Reject a declared central directory over the limits before `zipfile.ZipFile` loads it.

    Reads only the End Of Central Directory record and, when present, the ZIP64 locator
    and record (APPNOTE.TXT 4.3.14-4.3.16). Missing records are left to `zipfile`.
    """
    with Path(path).open("rb") as handle:
        size = handle.seek(0, os.SEEK_END)
        tail_start = max(0, size - (22 + 0xFFFF))
        handle.seek(tail_start)
        tail = handle.read()
        position = tail.rfind(b"PK\x05\x06")
        if position < 0 or position + 22 > len(tail):
            return
        _sig, _disk, _cd_disk, disk_entries, total, cd_size, _offset, _comment = struct.unpack_from(
            "<4sHHHHIIH", tail, position
        )
        counts, sizes = [disk_entries, total], [cd_size]
        zip64 = _zip64_counts(handle, tail_start + position - 20, size)
        if zip64:
            counts, sizes = [c for c, _s in zip64], [s for _c, s in zip64]
    if max(counts) > MAX_ARCHIVE_MEMBERS:
        raise UnsafeArchiveError(
            f"archive declares {max(counts)} entries; the limit is {MAX_ARCHIVE_MEMBERS}."
        )
    if max(sizes) > MAX_CENTRAL_DIRECTORY_BYTES:
        raise UnsafeArchiveError(
            f"archive central directory declares {max(sizes)} bytes; the limit is "
            f"{MAX_CENTRAL_DIRECTORY_BYTES}."
        )


def _zip64_counts(handle, locator_at: int, size: int) -> list[tuple[int, int]]:
    """Return (entry count, directory size) pairs from ZIP64 records zipfile may use."""
    if locator_at < 0:
        return []
    handle.seek(locator_at)
    locator = handle.read(20)
    if len(locator) != 20 or locator[:4] != b"PK\x06\x07":
        return []
    (record_offset,) = struct.unpack_from("<Q", locator, 8)
    found: list[tuple[int, int]] = []
    # zipfile tries the locator's offset, then the record directly before the locator.
    for offset in {record_offset, locator_at - 56}:
        if not 0 <= offset <= size - 56:
            continue
        handle.seek(offset)
        record = handle.read(56)
        if record[:4] != b"PK\x06\x06":
            continue
        disk_entries, total, cd_size = struct.unpack_from("<QQQ", record, 24)
        found.extend(((disk_entries, cd_size), (total, cd_size)))
    return found


def is_signed_package_member(name: str) -> bool:
    """Identify the OOXML digital-signature part namespace without reading member data."""
    return name.replace("\\", "/").lower().startswith(SIGNED_PACKAGE_PREFIX)


def package_is_signed(names: list[str] | tuple[str, ...]) -> bool:
    """True if any member is a digital-signature part."""
    return any(is_signed_package_member(name) for name in names)


def archive_is_signed(archive: zipfile.ZipFile) -> bool:
    """True for `_xmlsignatures/` parts or a signature origin relationship in `_rels/.rels`.

    System.IO.Packaging stores signatures elsewhere and links them only from `_rels/.rels`.
    """
    names = archive.namelist()
    if package_is_signed(names):
        return True
    if ROOT_RELATIONSHIPS not in names:
        return False
    if archive.getinfo(ROOT_RELATIONSHIPS).flag_bits & (0x01 | 0x40):
        return False  # encrypted entries are rejected by reject_encrypted_entries
    # shortcut: only a bounded prefix is searched; a real root .rels is a few hundred bytes.
    prefix = read_zip_member_prefix(archive, ROOT_RELATIONSHIPS, MAX_ROOT_RELATIONSHIPS_BYTES)
    return SIGNATURE_ORIGIN_RELATIONSHIP.encode() in prefix


def reject_encrypted_entries(archive: zipfile.ZipFile) -> None:
    """Raise if ZIP entries use traditional ZIP encryption flags."""
    encrypted_names = tuple(
        info.filename for info in archive.infolist() if info.flag_bits & (0x01 | 0x40)
    )
    if encrypted_names:
        sample = ", ".join(encrypted_names[:3])
        suffix = "" if len(encrypted_names) <= 3 else ", ..."
        raise EncryptedDocumentError(f"encrypted ZIP entries are unsupported: {sample}{suffix}")


def compression_ratio_exceeds_limit(info: zipfile.ZipInfo) -> bool:
    """Return whether ZIP metadata describes a potentially explosive member."""
    if info.file_size == 0:
        return False
    if info.compress_size == 0:
        return True
    return info.file_size > info.compress_size * MAX_COMPRESSION_RATIO


def validate_archive_safety(
    archive: zipfile.ZipFile,
    *,
    allow_signed: bool = False,
) -> None:
    """Reject archives whose metadata is unsafe to process before reading members."""
    checkpoint()
    entries = archive.infolist()
    if len(entries) > MAX_ARCHIVE_MEMBERS:
        raise UnsafeArchiveError(
            f"archive has {len(entries)} entries; the limit is {MAX_ARCHIVE_MEMBERS}."
        )

    names = [info.filename for info in entries]

    if not allow_signed and archive_is_signed(archive):
        raise SignedDocumentError(
            "digitally signed OOXML packages are unsupported because rewriting invalidates "
            "signatures. Pass strip_signatures=True / --strip-signatures for an unsigned copy."
        )

    if snapshot_checked(archive.filename):
        return
    reject_encrypted_entries(archive)
    _reject_duplicate_names(names)
    total_size = 0
    for info in entries:
        checkpoint()
        _validate_member_limits(info)
        total_size += info.file_size
        if total_size > MAX_TOTAL_UNCOMPRESSED_BYTES:
            raise UnsafeArchiveError(
                f"archive expands to more than {MAX_TOTAL_UNCOMPRESSED_BYTES} bytes."
            )

    snapshot_checked(archive.filename, remember=True)


def verify_archive_crc(archive: zipfile.ZipFile) -> str | None:
    """Read every member fully, preserving CRC verification with bounded checkpoints."""
    for info in archive.infolist():
        checkpoint()
        try:
            with archive.open(info) as member:
                while member.read(1024 * 1024):
                    checkpoint()
        except (zipfile.BadZipFile, zlib.error, EOFError):
            return info.filename
    checkpoint()
    return None


def _reject_duplicate_names(names: list[str]) -> None:
    """Reject unsafe or duplicate names after OPC URI normalization."""
    canonical = [_canonical_member_name(name) for name in names]
    if len(canonical) != len(set(canonical)):
        raise UnsafeArchiveError("archive contains duplicate or aliased member names.")


def _canonical_member_name(name: str) -> str:
    """Return a comparison form for one safe package-relative OPC part name."""
    if _raw_member_name_is_unsafe(name):
        raise UnsafeArchiveError(f"archive member has an unsafe package name: {name!r}")
    decoded = unquote(name)
    if _decoded_member_name_is_unsafe(decoded):
        raise UnsafeArchiveError(f"archive member has an unsafe package name: {name!r}")
    if _has_control_characters(decoded):
        raise UnsafeArchiveError(f"archive member has control characters: {name!r}")
    normalized = decoded.rstrip("/")
    if not normalized:
        raise UnsafeArchiveError(f"archive member has an unsafe package name: {name!r}")
    parts = PurePosixPath(normalized).parts
    if _has_path_traversal(parts):
        raise UnsafeArchiveError(f"archive member has path traversal: {name!r}")
    return "/".join(parts)


def _raw_member_name_is_unsafe(name: str) -> bool:
    return not name or "\\" in name or "?" in name or "#" in name


def _decoded_member_name_is_unsafe(name: str) -> bool:
    return name.startswith("/") or "\\" in name or bool(PureWindowsPath(name).drive)


def _has_control_characters(name: str) -> bool:
    return any(ord(character) < 32 or ord(character) == 127 for character in name)


def _has_path_traversal(parts: tuple[str, ...]) -> bool:
    return any(part in {"", ".", ".."} for part in parts)


def _validate_member_limits(info: zipfile.ZipInfo) -> None:
    """Validate one member's expansion and compression limits."""
    if info.file_size > MAX_MEMBER_UNCOMPRESSED_BYTES:
        raise UnsafeArchiveError(
            f"{info.filename} expands to {info.file_size} bytes; the per-member limit is "
            f"{MAX_MEMBER_UNCOMPRESSED_BYTES}."
        )
    if compression_ratio_exceeds_limit(info):
        raise UnsafeArchiveError(
            f"{info.filename} exceeds the compression ratio limit of {MAX_COMPRESSION_RATIO}:1."
        )
