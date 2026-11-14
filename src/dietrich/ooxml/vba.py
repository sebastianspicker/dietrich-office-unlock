"""Clear VBA project password verifier fields (CMG/DPB/GC) when present as text."""

from __future__ import annotations

import re

from dietrich.safety.cfb import CFBF_MAGIC, patch_stream_bytes, read_stream_bytes

# MS-OVBA §2.3.1: ProjectProtectionState, ProjectPassword and ProjectVisibilityState
# are `CMG=`, `DPB=` and `GC=` lines in the PROJECT stream's leading property block.
_LINE_RE = re.compile(rb"^(?P<key>CMG|DPB|GC)=(?P<val>[^\r\n]*)", re.MULTILINE)
_SECTION_RE = re.compile(rb"^\[", re.MULTILINE)


def unlock_vba_project(data: bytes) -> tuple[bytes, int]:
    """Clear VBA project password verifier fields.

    Returns (new_bytes, number_of_fields_touched).
    """
    if not data:
        return data, 0

    # A compound file is only edited through its PROJECT stream's sector chain.
    if data[:8] == CFBF_MAGIC:
        return _try_unlock_ole_vba(data)

    return _clear_vba_keys_in_bytes(data)


def _try_unlock_ole_vba(data: bytes) -> tuple[bytes, int]:
    """Patch PROJECT streams in place; leave malformed compound files unchanged."""
    try:
        import olefile
    except ImportError:
        return data, 0
    try:
        streams = read_stream_bytes(data)
        patches: dict[str, bytes] = {}
        touched_total = 0
        for name, raw in streams.items():
            if name.rsplit("/", 1)[-1].upper() != "PROJECT":
                continue
            patched, touched = _clear_vba_keys_in_bytes(raw)
            if touched:
                patches[name] = patched
                touched_total += touched
        if not patches:
            return data, 0
        result, applied = patch_stream_bytes(data, patches)
    except (OSError, ValueError, olefile.olefile.OleFileError):
        return data, 0
    if len(applied) != len(patches):
        return data, 0
    return result, touched_total


def _clear_vba_keys_in_bytes(data: bytes) -> tuple[bytes, int]:
    """Replace CMG=/DPB=/GC= values with an empty quoted string padded to the same length."""
    touched = 0

    def repl(match: re.Match[bytes]) -> bytes:
        """Regex replace callback for one CMG/DPB/GC field."""
        nonlocal touched
        old_full = match.group(0)
        new_full = match.group("key") + b'=""'
        # Same length keeps stream sizes and sector chains intact.
        if len(new_full) > len(old_full):
            return old_full
        new_full = new_full.ljust(len(old_full), b" ")
        if new_full != old_full:
            touched += 1
        return new_full

    section = _SECTION_RE.search(data)
    end = section.start() if section else len(data)
    return _LINE_RE.sub(repl, data[:end]) + data[end:], touched
