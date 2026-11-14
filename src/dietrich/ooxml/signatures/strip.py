"""Remove OOXML signature parts and their content types and relationships."""

from __future__ import annotations

import posixpath
from pathlib import PurePosixPath

from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException

from dietrich.errors import InvalidDocumentError
from dietrich.ooxml.xml_strip import find_matching_ranges, local_name, remove_ranges
from dietrich.safety.zip_archive import ROOT_RELATIONSHIPS, is_signed_package_member

CONTENT_TYPES = "[Content_Types].xml"
RELS_CANDIDATES = (
    "_rels/.rels",
    "xl/_rels/workbook.xml.rels",
    "word/_rels/document.xml.rels",
    "ppt/_rels/presentation.xml.rels",
)

# ECMA-376 Part 2 digital-signature content types: origin, xmlsignature, certificate.
_SIGNATURE_CONTENT_TYPE_PREFIX = "application/vnd.openxmlformats-package.digital-signature-"
_SIGNATURE_RELATIONSHIP_PREFIX = (
    "http://schemas.openxmlformats.org/package/2006/relationships/digital-signature/"
)


def strip_signature_members(
    names: list[str],
    read,
) -> tuple[set[str], dict[str, bytes]]:
    """Return (members_to_skip, rewritten_parts).

    Removes `_xmlsignatures/*`, parts reached from the origin relationship, and signature
    relationship/content-type entries. Does not forge signatures.
    """
    skip = _signed_members(names, read)

    rewritten: dict[str, bytes] = {}
    if not skip:
        return skip, rewritten

    if CONTENT_TYPES in names:
        rewritten[CONTENT_TYPES] = _strip_content_types(read(CONTENT_TYPES), skip, names)

    rewritten.update(_signature_relationship_parts(names, read, rewritten))

    return skip, rewritten


def _signed_members(names: list[str], read) -> set[str]:
    """Normalize package members that must be removed with a signature."""
    present = {name.replace("\\", "/").lower(): name for name in names}
    skip = {name.replace("\\", "/") for name in names if is_signed_package_member(name)}
    return skip | _origin_members(present, read)


def _origin_members(present: dict[str, str], read) -> set[str]:
    """Follow digital-signature relationships from `_rels/.rels` (origin, signature, certificate).

    System.IO.Packaging stores these outside `_xmlsignatures/`, e.g. under
    `package/services/digital-signature/`.
    """
    found: set[str] = set()
    pending = _signature_targets(ROOT_RELATIONSHIPS, "", present, read)
    while pending:
        part = present.get(pending.pop().lower())
        if part is None or part in found:
            continue
        found.add(part)
        directory, base = posixpath.split(part)
        rels = present.get(posixpath.join(directory, "_rels", base + ".rels").lower())
        if rels is not None:
            found.add(rels)
            pending.extend(_signature_targets(rels, part, present, read))
    return found


def _signature_targets(rels: str, source: str, present: dict[str, str], read) -> list[str]:
    """Return package-relative targets of digital-signature relationships in one .rels part."""
    if rels.lower() not in present:
        return []
    try:
        root = ElementTree.fromstring(read(present[rels.lower()]))
    except (DefusedXmlException, ElementTree.ParseError) as exc:
        raise InvalidDocumentError(f"{rels} is not valid XML: {exc}") from exc
    targets: list[str] = []
    for element in root.iter():
        attrs = element.attrib
        if (
            local_name(element.tag) != "Relationship"
            or attrs.get("TargetMode") == "External"
            or not attrs.get("Type", "").startswith(_SIGNATURE_RELATIONSHIP_PREFIX)
        ):
            continue
        target = attrs.get("Target", "")
        if target.startswith("/"):
            targets.append(posixpath.normpath(target).lstrip("/"))
        else:
            targets.append(posixpath.normpath(posixpath.join(posixpath.dirname(source), target)))
    return targets


def _signature_relationship_parts(
    names: list[str], read, rewritten: dict[str, bytes]
) -> dict[str, bytes]:
    """Rewrite standard and discovered relationship parts that reference signatures."""
    rewritten_parts: dict[str, bytes] = {}
    for name in names:
        normalized = name.replace("\\", "/")
        if normalized in rewritten or not normalized.endswith(".rels"):
            continue
        data = read(name)
        if normalized in RELS_CANDIDATES or _mentions_signature(data):
            rewritten_parts[normalized] = _strip_relationships(data, normalized)
    return rewritten_parts


def _mentions_signature(data: bytes) -> bool:
    """Detect a relationship payload that needs signature-target removal."""
    lowered = data.lower()
    return any(
        marker in lowered
        for marker in (b"_xmlsignatures", b"digital-signature", b"digitalsignature")
    )


def _strip_content_types(source: bytes, skip: set[str], names: list[str]) -> bytes:
    """Drop Overrides for removed parts and signature Defaults no kept part uses."""
    skipped = {name.lower() for name in skip}
    kept_extensions = {
        PurePosixPath(name.replace("\\", "/")).suffix.lstrip(".").lower()
        for name in names
        if name.replace("\\", "/").lower() not in skipped
    }

    def is_signature_entry(name: str, attrs: dict[str, str]) -> bool:
        if name == "Override":
            part = attrs.get("PartName", "").lstrip("/").lower()
            # An empty part name never matches; ECMA-376 Part 2 §10.1.2 needs every part typed.
            return bool(part) and part in skipped
        if name == "Default":
            content_type = attrs.get("ContentType", "").lower()
            extension = attrs.get("Extension", "").lower()
            return (
                content_type.startswith(_SIGNATURE_CONTENT_TYPE_PREFIX)
                and extension not in kept_extensions
            )
        return False

    return remove_ranges(source, find_matching_ranges(source, is_signature_entry, CONTENT_TYPES))


def _strip_relationships(source: bytes, path: str) -> bytes:
    """Drop signature relationships while preserving all other bytes."""

    def matches(name: str, attrs: dict[str, str]) -> bool:
        return name == "Relationship" and _is_signature_relationship(attrs)

    return remove_ranges(source, find_matching_ranges(source, matches, path))


def _is_signature_relationship(attrs: dict[str, str]) -> bool:
    """Return whether a relationship target or type references a signature."""
    target = attrs.get("Target", "").lower()
    rel_type = attrs.get("Type", "").lower()
    return (
        "_xmlsignatures" in target
        or "digitalsignature" in target
        or any(marker in rel_type for marker in ("digitalsignature", "digital-signature"))
    )
