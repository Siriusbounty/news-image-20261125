# news-image-20261125 entry.
#
# The entry is a program that writes one image summing up the world's news
# of Wednesday 25 November 2026 to /output/entry.png. The image itself
# (entry.png, a newspaper front page drawn in-session from the day's wire
# reports) ships in this repository; the program copies it to the output
# directory after checking it is a whole PNG or JPEG inside the gate's
# limits. No network, no secrets, Python standard library only.
#
# Run it outside the grader with:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import struct
import sys
from pathlib import Path

OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
HERE = Path(__file__).resolve().parent
SRC = HERE / "entry.png"

data = SRC.read_bytes()

# The gate takes a whole PNG or JPEG of at most 1 MiB: refuse anything else.
PNG_MAGIC = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
is_png = data[:8] == PNG_MAGIC
is_jpeg = len(data) >= 3 and data[0] == 0xFF and data[1] == 0xD8 and data[2] == 0xFF
if not is_png and not is_jpeg:
    raise SystemExit("entry.png is not a PNG or JPEG")
if len(data) > 1048576:
    raise SystemExit("entry.png exceeds 1 MiB")
if is_png:
    # PNG header: width and height sit at bytes 16-23 (big-endian uint32s).
    width, height = struct.unpack(">II", data[16:24])
    if width > 1024 or height > 1024:
        raise SystemExit(f"entry.png is {width}x{height}, over the 1024x1024 cap")
if is_jpeg:
    # JPEG: walk the marker segments to a start-of-frame segment, whose
    # payload carries height then width (big-endian uint16s after the
    # length and precision bytes); enforce the same 1024x1024 cap.
    pos = 2
    width = height = None
    while pos + 4 <= len(data) and data[pos] == 0xFF:
        marker = data[pos + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[pos + 5:pos + 9])
            break
        if marker == 0xDA:
            break
        seg_len = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        if seg_len < 2:
            break
        pos += 2 + seg_len
    if width is not None and (width > 1024 or height > 1024):
        raise SystemExit(f"entry image is {width}x{height}, over the 1024x1024 cap")

os.makedirs(OUT_DIR, exist_ok=True)
Path(OUT_DIR, "entry.png").write_bytes(data)
print(f"wrote {OUT_DIR}/entry.png ({len(data)} bytes)", file=sys.stderr)
