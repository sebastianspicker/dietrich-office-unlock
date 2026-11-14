# Legacy binary Office support

Legacy `.xls`, `.doc`, and `.ppt` files store their data in CFBF/OLE compound
storage rather than OOXML ZIP packages. Dietrich reads those streams with
`olefile` under strict bounds and applies only structurally verified,
equal-length patches. It is not a general compound-file editor.

## What works

- Excel BIFF8 workbook protection records inside complete BOF/EOF substreams.
  An embedded chart substream nested in a worksheet (MS-XLS 2.1.7.20) is
  accepted and left unchanged; any other nesting is refused.
- Word FIB `fReadOnlyRecommended` (0x0400) and `fWriteReservation` (0x0800)
  flag bits ([MS-DOC] 2.5.2 FibBase). Other FIB bits and `lKey` are not touched.
- PowerPoint container inspection. Mutation is intentionally unavailable.

The writer keeps the compound-file layout intact by requiring replacement bytes
to match the original stream length. After writing, Dietrich reopens the output
and validates it.

## What does not

This path is not a complete CFBF writer and cannot repair damaged compound
files. Malformed BIFF walks, unrecognized Word FIB headers, PowerPoint mutation,
unknown protectors, producer-specific extensions, encryption, and record layouts
outside the implemented patterns either fail explicitly or are left unchanged.
Dietrich never scans arbitrary content for protection-looking byte strings.

The test suite builds only small synthetic byte streams; no real legacy
documents are tracked.
