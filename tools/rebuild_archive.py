#!/usr/bin/env python3
"""
rebuild_archive.py -- one command to reproduce refined-chat-archive/ exactly.

Steps
  1. If conversation data exists (conversations.json / chat-structure .dat /
     chats.sqlite), run the full A/B/C pipeline from build_archive.py.
  2. Always run the artifact catalog over the `.dat` blobs present in the repo.
  3. Append the approved Google Drive sources (if their local copies are present).
  4. Package refined-chat-archive.zip.

    python3 tools/rebuild_archive.py
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from artifact_catalog import (  # noqa: E402
    append_external_index, catalog_artifacts, catalog_external, write_artifact_index,
)
from build_archive import build, make_zip, scan_sources  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "refined-chat-archive"

DRIVE_SOURCES = [
    ("esp32_interface_df_player_mini.ino",
     "https://drive.google.com/file/d/1ZXEKZxr_Bsj_oyYje0L3kEbPdDfoFYuo/view"),
    ("Df_Player_mini_Arduino.ino",
     "https://drive.google.com/file/d/1i0mtgmK175qKYOJAn_yGkb6cOTYsUKD2/view"),
    ("Circuit Diagram.png",
     "https://drive.google.com/file/d/1Cxml0qjzqg1sLnZ5xxEIVrG8jcwTzJJN/view"),
]


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / ".run").mkdir(exist_ok=True)

    # 1) conversation pipeline -------------------------------------------------
    sources = scan_sources(ROOT)
    chat_sources = [s for s in sources if s.kind in ("json", "dat-json", "dat-text")]
    conv_count = 0
    if chat_sources:
        manifest = build(ROOT, OUT)
        conv_count = manifest["stats"]["processed"]
        print(f"[chats] {conv_count} conversation(s) rendered from "
              f"{len(chat_sources)} chat-capable source file(s)")

    # 2) artifact catalog ------------------------------------------------------
    res = catalog_artifacts(ROOT, OUT)
    print(f"[artifacts] {res['total']} .dat files: {res['text']} text, "
          f"{res['json']} json, {res['binary']} binary")

    # 3) index ---------------------------------------------------------------
    if conv_count:
        # build_archive already wrote a conversation index; keep it and append
        idx = OUT / "INDEX.md"
        idx.write_text(idx.read_text(encoding="utf-8").rstrip() + "\n", encoding="utf-8")
    else:
        write_artifact_index(OUT, res)

    # 4) approved external sources -------------------------------------------
    exts = []
    drive_dir = ROOT / "google_drive"
    if drive_dir.is_dir():
        present = [(n, u) for n, u in DRIVE_SOURCES if (drive_dir / n).exists()]
        if present:
            exts.append(catalog_external(drive_dir, OUT, "google-drive", present))
            append_external_index(OUT, exts)
            print(f"[external] {len(present)} Google Drive file(s) folded in")

    # 5) manifest + zip -------------------------------------------------------
    (OUT / ".run" / "manifest.json").write_text(json.dumps({
        "conversations_rendered": conv_count,
        "artifacts": {
            "total": res["total"], "text": res["text"], "json": res["json"],
            "binary": res["binary"], "unique_contents": res["unique_contents"],
            "duplicate_groups": len(res["duplicate_groups"]),
            "topics": res["topics"], "languages": res["languages"],
            "mimes": res["mimes"],
        },
        "external_sources": [e["rows"] for e in exts],
        "verification": {
            "binary_preserved": len(list((OUT / "raw_dat_attachments").iterdir())),
            "text_catalogued": len(list((OUT / "artifacts").rglob("ARTIFACT.md"))),
        },
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    zp = make_zip(OUT)
    print(f"[zip] {zp.relative_to(ROOT)} ({zp.stat().st_size:,} bytes)")
    print(f"[done] {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
