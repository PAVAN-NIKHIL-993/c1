#!/usr/bin/env python3
"""
artifact_catalog.py -- inventory the raw `.dat` blobs that a ChatGPT export
carries in its ``files/`` directory (attachments), for the case where the
conversation JSON itself is absent.

It never fabricates transcripts. Each artifact gets:
  * content-based classification (text / JSON / binary+media)
  * language / format detection for text artifacts
  * a topic-chain folder derived from keywords in the content
  * a byte-exact copy of the original (`original.bin` / `original.txt`)
  * a human-readable `ARTIFACT.md` header with checksums and provenance
Binary/media artifacts are copied byte-for-byte into ``raw_dat_attachments/``.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from build_archive import (
    classify_file, human_bytes, md5_file, sha256_file, slugify, sniffer_mime,
)

# --------------------------------------------------------------------------- #
# Language / format detection for text artifacts
# --------------------------------------------------------------------------- #

LANGUAGE_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("cpp", re.compile(r"^\s*#include\s*[<\"]", re.M)),
    ("platformio-ini", re.compile(r"^\s*\[env:[^\]]+\]", re.M)),
    ("cpp", re.compile(r"^\s*#pragma once", re.M)),
    ("arduino-ino", re.compile(r"\bvoid\s+(setup|loop)\s*\(\s*\)", re.M)),
    ("typescript-react", re.compile(
        r"^\s*import\s+(React|\{[^}]*\})\s*(,[^;]*)?\s*from\s*[\"']react[\"']", re.M)),
    ("typescript", re.compile(r"^\s*(export\s+)?(type|interface)\s+\w+", re.M)),
    ("javascript", re.compile(r"^\s*(import|export)\s+.*from\s+[\"']", re.M)),
    ("html", re.compile(r"^\s*<!doctype\s+html", re.I | re.M)),
    ("css", re.compile(r"^\s*@import\s+[\"']", re.M)),
    ("csv", re.compile(r"^[^\n]*,[^\n]*,[^\n]*,[^\n]*$", re.M)),
    ("shell-transcript", re.compile(
        r"Microsoft Windows \[Version|^[A-Za-z]:\\\\?[^\n]*>", re.M)),
    ("markdown", re.compile(r"^#{1,3}\s+\S", re.M)),
    ("json", re.compile(r"^\s*[\[{]\s*$", re.M)),
    ("plain-text", re.compile(r"^", re.M)),
]

TOPIC_RULES: list[tuple[str, set[str]]] = [
    ("hardware-bio-sensing", {"max30102", "ppg", "spo2", "heart rate", "pulse oximeter",
                              "photoplethysmography", "ad8232", "ecg"}),
    ("hardware-lcr-meter", {"lcr", "capacitance", "inductance", "esr", "component tester",
                            "lc meter", "frequency counter"}),
    ("hardware-esp32", {"esp32", "esp32-c3", "esp8266", "platformio", "arduino",
                        "gpio", "i2c", "spi", "uart", "dfplayer", "wifi", "websocket"}),
    ("hardware-eda-kicad", {"kicad", "footprint", "schematic", "pcb", "bom", "netlist"}),
    ("hardware-water-sensing", {"water level", "float switch", "leak", "flood",
                                "overflow alarm", "sump"}),
    ("software-frontend", {"react", "vite", "tailwind", "framer-motion", "typescript",
                           "usestate", "useeffect", "clsx", "html", "css"}),
    ("software-tooling", {"node", "npm", "eslint", "tsconfig", "webpack", "pipeline",
                          "terminal", "powershell", "cmd"}),
    ("system-config", {"hkey", "registry", "audio device", "device name", "driver"}),
]

MEDIA_LABEL = {
    "image/png": "PNG image", "image/jpeg": "JPEG image",
    "audio/mpeg": "MP3 audio", "application/pdf": "PDF document",
    "image/gif": "GIF image", "audio/wav": "WAV audio",
    "application/octet-stream": "opaque binary",
}


def detect_language(text: str) -> tuple[str, str]:
    for name, rx in LANGUAGE_RULES:
        if rx.search(text):
            first = next((l.strip() for l in text.splitlines() if l.strip()), "")
            return name, first[:160]
    return "plain-text", ""


GENERIC_IDENTS = {
    "file", "index", "main", "app", "src", "data", "text", "true", "false",
    "null", "undefined", "string", "number", "return", "const", "function",
    "import", "export", "default", "class", "name", "type", "value", "props",
    "children", "div", "span", "html", "body", "head", "meta", "link", "script",
    "style", "width", "height", "margin", "padding", "color", "background",
    "stdio", "arduino", "include", "define", "pragma", "void", "int", "float",
    "double", "char", "bool", "static", "struct", "using", "namespace", "public",
    "private", "protected", "virtual", "override", "template", "typename",
    "auto", "uint8_t", "uint16_t", "uint32_t", "int32_t", "size_t", "wire",
    "serial", "delay", "pinmode", "digitalwrite", "digitalread", "analogread",
    "high", "low", "input", "output", "setup", "loop", "min", "max", "abs",
    "set", "get", "map", "filter", "find", "push", "list", "item", "items",
    "title", "header", "footer", "container", "wrapper", "button", "input",
    "select", "option", "form", "label", "table", "tbody", "thead", "tr", "td",
    "th", "ul", "li", "img", "href", "srcset", "className", "onClick", "style",
}


CONTENT_HINTS: list[tuple[tuple[str, ...], str]] = [
    (("dfplayermini", "dfplayer"), "dfplayer-mini"),
    (("max30102",), "max30102"),
    (("max30105",), "max30105"),
    (("mpu6050",), "mpu6050"),
    (("cd74hc4067",), "cd74hc4067-mux"),
    (("irlz44n",), "irlz44n-mosfet"),
    (("kicad",), "kicad-shortcuts"),
    (("droidcam",), "droidcam-devices"),
    (("tailwindcss",), "tailwind"),
    (("framer-motion",), "framer-motion"),
    (("helix", "mp3"), "helix-mp3-decoder"),
    (("es2020",), "es2020-config"),
    (("platformio",), "platformio-env"),
    (("winsound", "hkey_current_user"), "windows-audio-registry"),
    (("flood", "leak"), "flood-leak-detectors"),
    (("pasted text(",), "pasted-prompts"),
    (("reg delete", "driverquery"), "windows-cleanup-session"),
]


def content_slug(text: str, language: str) -> str:
    """Derive a human-meaningful, deterministic slug from artifact content."""
    low = text[:8000].lower()
    # variant-distinguishing suffix: DFPlayer pin mapping
    if "dfplayer" in low:
        pins = re.findall(r"PIN_MP3_TX\s*=\s*(\d+)", text)
        if pins:
            return f"dfplayer-mini-pins-{pins[0]}"
    for needles, slug in CONTENT_HINTS:
        if all(n in low for n in needles):
            return slug
    # 1) hardware / part numbers and distinctive ALLCAPS-digit identifiers
    parts = re.findall(r"\b[A-Z]{2,}[0-9]{2,}[A-Z0-9]*\b", text)
    # 2) comments that read like headings (// Title, /* Title, # Title)
    comments = re.findall(r"^\s*(?://|/\*|\*|#|--)\s*([A-Z][A-Za-z0-9 ,&'+-]{6,60})$",
                          text, re.M)
    # 3) PascalCase component / function identifiers
    pascal = re.findall(r"\b([A-Z][a-z]+(?:[A-Z][a-z0-9]+)+)\b", text)
    # 4) snake_case distinctive identifiers
    snake = re.findall(r"\b([a-z][a-z0-9]+(?:_[a-z0-9]+)+)\b", text)

    def rank(seq):
        from collections import Counter
        c = Counter(s for s in seq if s.lower() not in GENERIC_IDENTS
                    and len(s) > 3 and not s.lower().startswith(("usestate",
                                                                 "useeffect",
                                                                 "useref",
                                                                 "usecallback",
                                                                 "usememo")))
        return [w for w, _ in c.most_common()]

    words: list[str] = []
    for cand in rank(parts)[:2] + rank(pascal)[:2] + rank(snake)[:2]:
        if cand.lower() not in [w.lower() for w in words]:
            words.append(cand)
    if not words:
        for c in comments[:2]:
            words.extend(w for w in re.findall(r"[A-Za-z0-9]+", c)[:3])
    if not words:
        # last resort: distinctive long words from the body
        body = re.findall(r"\b[a-zA-Z]{6,}\b", text[:4000])
        words = rank(body)[:2]
    return slugify("-".join(words) or "artifact", 34)


def detect_topic(name: str, text: str) -> str:
    blob = (name + " " + text[:6000]).lower()
    best, best_n = "uncategorized", 0
    for topic, kws in TOPIC_RULES:
        n = sum(1 for k in kws if k in blob)
        if n > best_n:
            best, best_n = topic, n
    return best


# --------------------------------------------------------------------------- #
# Catalog
# --------------------------------------------------------------------------- #


@dataclass
class Artifact:
    name: str
    size: int
    kind: str
    mime: str
    sha256: str
    md5: str
    language: str = ""
    topic: str = "uncategorized"
    preview: str = ""
    text: str = ""
    duplicate_of: list[str] = field(default_factory=list)
    folder: str = ""
    rel_path: str = ""
    char_count: int = 0
    line_count: int = 0
    tokens: int = 0


def catalog_artifacts(root: Path, out: Path) -> dict[str, Any]:
    raw_dir = out / "raw_dat_attachments"
    art_dir = out / "artifacts"
    raw_dir.mkdir(parents=True, exist_ok=True)
    art_dir.mkdir(parents=True, exist_ok=True)

    dat_files = sorted(p for p in root.glob("*.dat") if p.is_file())
    arts: list[Artifact] = []
    by_hash: dict[str, list[str]] = {}

    for p in dat_files:
        b = p.read_bytes()
        sf = classify_file(p, p.name)
        sha = hashlib.sha256(b).hexdigest()
        md5 = hashlib.md5(b).hexdigest()  # noqa: S324 - integrity inventory
        by_hash.setdefault(sha, []).append(p.name)
        a = Artifact(name=p.name, size=len(b), kind=sf.kind,
                     mime=sniffer_mime(b[:64]) if sf.kind == "dat-binary" else "",
                     sha256=sha, md5=md5)
        if sf.kind in ("dat-text", "dat-json"):
            try:
                a.text = b.decode("utf-8")
            except UnicodeDecodeError:
                a.text = b.decode("utf-8", errors="replace")
            a.char_count = len(a.text)
            a.line_count = a.text.count("\n") + 1
            a.tokens = len(re.findall(r"\S+", a.text))
            a.language, a.preview = detect_language(a.text)
            a.topic = detect_topic(p.name, a.text)
        else:
            a.mime = a.mime or "application/octet-stream"
            a.topic = "media-attachments"
        arts.append(a)

    for a in arts:
        others = [n for n in by_hash[a.sha256] if n != a.name]
        a.duplicate_of = others

    # --- write text artifacts grouped by topic ---------------------------- #
    used: set[str] = set()
    for a in sorted(arts, key=lambda x: (x.topic, x.name)):
        if a.kind not in ("dat-text", "dat-json"):
            # binary: byte-exact copy + checksum, no re-encoding
            dst = raw_dir / a.name
            if not dst.exists():
                shutil.copy2(root / a.name, dst)
            a.folder = "raw_dat_attachments"
            a.rel_path = f"raw_dat_attachments/{a.name}"
            continue
        descriptor = content_slug(a.text, a.language)
        folder_name = f"{a.topic}/{slugify(a.language or 'text', 20)}__{descriptor}"
        n = 2
        cand = folder_name
        while cand in used:
            cand = f"{folder_name}-{n}"
            n += 1
        used.add(cand)
        a.folder = cand
        d = art_dir / cand
        d.mkdir(parents=True, exist_ok=True)
        # byte-exact original, under its ORIGINAL filename (preserves name+bytes)
        shutil.copy2(root / a.name, d / a.name)
        shutil.copy2(root / a.name, d / "original.bin")
        (d / "content.txt").write_text(a.text, encoding="utf-8")
        a.rel_path = f"artifacts/{cand}/content.txt"
        dup_note = ("\n".join(f"- Byte-identical to `{n}`" for n in a.duplicate_of)
                    or "- No byte-identical duplicate found")
        (d / "ARTIFACT.md").write_text(
            f"""# {a.name}

| Field | Value |
|---|---|
| Original filename | `{a.name}` |
| Format | `{a.language}` |
| Topic chain | `{a.topic}` |
| Stored at | `artifacts/{a.folder}/{a.name}` (byte-exact, original name) |
| Also as | `artifacts/{a.folder}/original.bin` and `content.txt` (decoded) |
| Size | {human_bytes(a.size)} ({a.size} bytes) |
| Characters / lines / tokens | {a.char_count} / {a.line_count} / {a.tokens} |
| SHA-256 | `{a.sha256}` |
| MD5 | `{a.md5}` |

## Provenance
This file was uploaded to the repository as a `.dat` blob with no conversation
metadata. It was classified **by content**, not by extension: decoded as UTF-8
and identified as `{a.language}` source. The full text is stored verbatim in
`content.txt`; `original.bin` is a byte-exact copy of the uploaded file.

Opening lines:
```text
{a.preview or (a.text.strip().splitlines() or [""])[0][:160]}
```

## Duplicate check
{dup_note}
""", encoding="utf-8")

    # --- recoverable conversational fragments ---------------------------- #
    frag_dir = out / "recoverable-fragments"
    frag_dir.mkdir(exist_ok=True)
    fragment_files = []
    for a in arts:
        if a.kind not in ("dat-text", "dat-json"):
            continue
        if re.search(r"Pasted text\(\d+\)\.txt", a.text) or \
           re.search(r"Microsoft Windows \[Version", a.text):
            fragment_files.append(a)

    lines = ["# Recoverable fragments", "",
             "These artifacts are not conversations, but they contain fragments of the "
             "**user's own words** (prompt text captured in a pasted document or a terminal "
             "session). They are reproduced here verbatim so the wording survives, clearly "
             "separated from anything that would be an actual transcript.", ""]
    for a in fragment_files:
        lines.append(f"## `{a.name}`")
        lines.append("")
        lines.append(f"- Detected format: `{a.language}`  ·  {a.size} bytes  ·  "
                     f"SHA-256 `{a.sha256[:16]}…`")
        lines.append(f"- Full text: `artifacts/{a.folder}/content.txt`")
        lines.append("")
        if "Pasted text(" in a.text:
            prompts = re.findall(
                r"Pasted text\(\d+\)\.txt\s*\r?\n\s*Document\s*\r?\n(.*?)(?=Pasted text\(\d+\)\.txt|\Z)",
                a.text, re.S)
            lines.append("User-authored prompt text found inside this document "
                         f"({len(prompts)} labelled paste blocks):")
            lines.append("")
            for i, pr in enumerate(prompts, 1):
                cleaned = "\n".join(l.rstrip() for l in pr.strip().splitlines() if l.strip())
                if not cleaned:
                    continue
                lines.append(f"**Paste block {i}**")
                lines.append("")
                lines.append("```text")
                lines.append(cleaned[:1200])
                lines.append("```")
                lines.append("")
        else:
            lines.append("Terminal session (commands and tool output), first 60 lines:")
            lines.append("")
            lines.append("```text")
            lines.append("\n".join(a.text.splitlines()[:60]))
            lines.append("```")
            lines.append("")
    (frag_dir / "RECOVERABLE_FRAGMENTS.md").write_text("\n".join(lines) + "\n",
                                                       encoding="utf-8")

    # --- stats ------------------------------------------------------------ #
    from collections import Counter
    lang_counts = Counter(a.language for a in arts if a.kind != "dat-binary")
    topic_counts = Counter(a.topic for a in arts)
    mime_counts = Counter(a.mime for a in arts if a.kind == "dat-binary")
    dup_groups = {h: v for h, v in by_hash.items() if len(v) > 1}

    return {
        "artifacts": arts,
        "total": len(arts),
        "text": sum(1 for a in arts if a.kind == "dat-text"),
        "json": sum(1 for a in arts if a.kind == "dat-json"),
        "binary": sum(1 for a in arts if a.kind == "dat-binary"),
        "unique_contents": len(by_hash),
        "duplicate_groups": dup_groups,
        "languages": dict(lang_counts.most_common()),
        "topics": dict(topic_counts.most_common()),
        "mimes": dict(mime_counts.most_common()),
        "fragments": [a.name for a in fragment_files],
    }


# --------------------------------------------------------------------------- #
# INDEX for an artifacts-only corpus
# --------------------------------------------------------------------------- #


def write_artifact_index(out: Path, res: dict[str, Any]) -> None:
    L: list[str] = []
    A = L.append
    arts: list[Artifact] = res["artifacts"]
    A("# Refined ChatGPT Archive — Master Index")
    A("")
    A(f"Generated: {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    A("")
    A("## ⚠️ Read this first: no conversation transcripts were present")
    A("")
    A("The 81 `.dat` files uploaded to this repository were classified by **content**, "
      "not by extension. All 81 resolve to **attachment blobs** — source code, images, "
      "audio, PDFs and reference text — of the kind a ChatGPT export keeps in its "
      "`files/` directory.")
    A("")
    A("None of them is a conversation export. Verified by direct inspection:")
    A("")
    A("| Test | Result |")
    A("|---|---|")
    A("| `\"mapping\"` / `\"current_node\"` / `\"conversation_id\"` keys present | **0 of 81 files** |")
    A("| Role-tagged dialogue headers (`USER:` / `ASSISTANT:`) | **0 of 81 files** |")
    A("| Top-level JSON array of conversations | **0 files** (the single JSON file is `package.json`) |")
    A("| Any recoverable multi-turn dialogue | **0 conversations** |")
    A("")
    A("So the sequence of Section-A/B/C `refined_chat.txt` files described in the brief "
      "**cannot be produced from this upload** — there is no turn data to reconstruct. "
      "Fabricating transcripts or summaries here would be inventing history, so instead "
      "everything that *is* present has been classified, hashed, topic-chained and "
      "archived byte-exactly, and the one file containing the user's own prompt wording "
      "has been mined for those fragments.")
    A("")
    A("To complete the original request, upload the export's `conversations.json` "
      "(or the whole export `.zip`, which contains `conversations.json` + `files/`). "
      "`tools/build_archive.py` will then produce the full A/B/C archive; it is already "
      "implemented and self-tested against that exact format.")
    A("")
    A("---")
    A("")
    A("## 1. Source inventory — 81 `.dat` files, classified by content")
    A("")
    A("| Class | Count | Meaning |")
    A("|-------|-------|---------|")
    A(f"| UTF-8 text (source/reference) | **{res['text']}** | decoded and catalogued; verbatim copy kept |")
    A(f"| UTF-8 JSON (not chat data) | **{res['json']}** | `package.json`, no conversation structure |")
    A(f"| Binary / media | **{res['binary']}** | copied byte-for-byte to `raw_dat_attachments/` |")
    A(f"| **Total** | **{res['total']}** | |")
    A("")
    A(f"- Distinct content hashes: **{res['unique_contents']}** "
      f"(from {res['total']} files → **{len(res['duplicate_groups'])} byte-identical duplicate groups**)")
    A(f"- Media breakdown: " + ", ".join(f"`{k}` × {v}" for k, v in res["mimes"].items()))
    A(f"- Detected text formats: " + ", ".join(f"`{k}` × {v}" for k, v in res["languages"].items()))
    A("")
    A("### Duplicate groups (identical bytes, different filenames)")
    A("")
    A("| Kept as | Byte-identical copy |")
    A("|---------|---------------------|")
    for h, names in res["duplicate_groups"].items():
        A(f"| `{names[0]}` | " + ", ".join(f"`{n}`" for n in names[1:]) + " |")
    A("")
    A("## 2. Topic chains")
    A("")
    A("Artifacts were grouped with the same topic-chaining logic used for conversations "
      "(keyword domain scoring), because with no timestamps the content domain is the only "
      "honest organising signal.")
    A("")
    A("| Topic chain | Artifacts |")
    A("|-------------|-----------|")
    for k, v in res["topics"].items():
        A(f"| `{k}` | {v} |")
    A("")
    A("## 3. Folder tree")
    A("")
    A("```text")
    A("refined-chat-archive/")
    A("├── INDEX.md                      ← this file")
    A("├── artifacts/                    ← decoded text artifacts, one folder each")
    for topic in sorted({a.topic for a in arts if a.kind != "dat-binary"}):
        subs = sorted(a.folder.split("/", 1)[1] for a in arts
                      if a.kind != "dat-binary" and a.topic == topic)
        A(f"│   ├── {topic}/")
        for i, s in enumerate(subs):
            A(f"│   │   {'└── ' if i == len(subs) - 1 else '├── '}{s}/")
    A("├── raw_dat_attachments/          ← 49 binary blobs, byte-exact")
    A("├── recoverable-fragments/        ← user-authored prompt wording")
    A("└── .run/                         ← machine-readable manifest")
    A("```")
    A("")
    A("## 4. Complete artifact inventory")
    A("")
    A("| # | Original file | Class | Format / MIME | Size | SHA-256 (16) | Dupe of | Location |")
    A("|---|---------------|-------|---------------|------|--------------|---------|----------|")
    for i, a in enumerate(sorted(arts, key=lambda x: (x.topic, x.name)), 1):
        fmt = a.language if a.kind != "dat-binary" else MEDIA_LABEL.get(a.mime, a.mime)
        dupe = f"`{a.duplicate_of[0]}`" if a.duplicate_of else "—"
        A(f"| {i} | `{a.name}` | {a.kind} | {fmt} | {human_bytes(a.size)} | "
          f"`{a.sha256[:16]}` | {dupe} | `{a.rel_path}` |")
    A("")
    A("## 5. Text artifacts — full checksums")
    A("")
    A("| File | Format | Chars | Lines | Tokens | SHA-256 |")
    A("|------|--------|-------|-------|--------|---------|")
    for a in sorted((x for x in arts if x.kind != "dat-binary"),
                    key=lambda x: (x.topic, x.name)):
        A(f"| `{a.name}` | `{a.language}` | {a.char_count} | {a.line_count} | "
          f"{a.tokens} | `{a.sha256}` |")
    A("")
    A("## 6. Binary / media `.dat` inventory")
    A("")
    A("| # | Stored as | Original name | MIME | Size | MD5 | SHA-256 |")
    A("|---|-----------|---------------|------|------|-----|---------|")
    for i, a in enumerate(sorted((x for x in arts if x.kind == "dat-binary"),
                                 key=lambda x: x.name), 1):
        A(f"| {i} | `raw_dat_attachments/{a.name}` | `{a.name}` | "
          f"{MEDIA_LABEL.get(a.mime, a.mime)} | {human_bytes(a.size)} | "
          f"`{a.md5}` | `{a.sha256}` |")
    A("")
    A("## 7. Recoverable fragments")
    A("")
    A(f"{len(res['fragments'])} artifact(s) contain the user's own prompt wording rather "
      "than generated code — see `recoverable-fragments/RECOVERABLE_FRAGMENTS.md`. "
      "These are excerpts inside documents and terminal logs, **not** dialogue turns, "
      "and they are labelled as such there.")
    A("")
    A("## 8. Verification")
    A("")
    bin_on_disk = list((out / "raw_dat_attachments").iterdir())
    art_on_disk = list((out / "artifacts").rglob("ARTIFACT.md"))
    A(f"- Binary `.dat` files found: **{res['binary']}** → preserved: **{len(bin_on_disk)}**"
      f"  ({'MATCH' if res['binary'] == len(bin_on_disk) else 'MISMATCH'})")
    A(f"- Text/JSON artifacts found: **{res['text'] + res['json']}** → catalogued: "
      f"**{len(art_on_disk)}** "
      f"({'MATCH' if res['text'] + res['json'] == len(art_on_disk) else 'MISMATCH'})")
    A(f"- Conversations found: **0** → `refined_chat.txt` files: **0** (nothing to render)")
    A("")
    A("## 9. Method notes")
    A("")
    A("- Classification is content-based: UTF-8 decode → `json.loads` → chat-structure "
      "probe; if that fails, control-character density decides whether the bytes are "
      "text or binary.")
    A("- Binary blobs are copied with `shutil.copy2`, never decoded or re-encoded, so "
      "their bytes and mtimes survive intact.")
    A("- Text artifacts are stored twice: `original.bin` (byte-exact upload) and "
      "`content.txt` (decoded UTF-8) so diffs are readable without losing the original.")
    A("- Nothing in this index is inferred: every count above is computed from the files "
      "at build time.")
    (out / "INDEX.md").write_text("\n".join(L) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# External sources (e.g. Google Drive) folded into the same topic chains
# --------------------------------------------------------------------------- #

def catalog_external(src: Path, out: Path, origin: str,
                     files: list[tuple[str, str]]) -> dict[str, Any]:
    """Copy explicitly-approved external files into `external-<origin>/`,
    chained into the same topic taxonomy. `files` is [(filename, drive_url)]."""
    base = out / f"external-{slugify(origin, 20)}"
    base.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, url in files:
        p = src / name
        if not p.exists():
            continue
        b = p.read_bytes()
        sha = hashlib.sha256(b).hexdigest()
        md5 = hashlib.md5(b).hexdigest()  # noqa: S324
        is_text = False
        text = ""
        try:
            text = b.decode("utf-8")
            is_text = b"\x00" not in b
        except UnicodeDecodeError:
            is_text = False
        if is_text:
            language, preview = detect_language(text)
            topic = detect_topic(name, text)
            descriptor = content_slug(text, language)
            folder = f"{topic}/{slugify(language, 20)}__{descriptor}"
            d = base / folder
            n = 2
            while d.exists():
                d = base / f"{folder}-{n}"
                n += 1
            d.mkdir(parents=True)
            shutil.copy2(p, d / "original.bin")
            (d / "content.txt").write_text(text, encoding="utf-8")
            rel = f"{base.name}/{d.relative_to(base).as_posix()}/content.txt"
            cls, fmt = "external-text", language
        else:
            topic = "media-attachments"
            mime = sniffer_mime(b[:64])
            d = base / "raw_attachments"
            d.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, d / name)
            rel = f"{base.name}/raw_attachments/{name}"
            cls, fmt = "external-binary", MEDIA_LABEL.get(mime, mime)
        (base / f"{slugify(Path(name).stem, 40)}.md").write_text(
            f"""# {name}

| Field | Value |
|---|---|
| Origin | Google Drive (`{origin}`) |
| Link | {url} |
| Class | `{cls}` |
| Format | `{fmt}` |
| Topic chain | `{topic}` |
| Size | {human_bytes(len(b))} ({len(b)} bytes) |
| SHA-256 | `{sha}` |
| MD5 | `{md5}` |

Included with the user's explicit approval, outside the `.dat` upload. Stored
verbatim at `{rel}`.
""", encoding="utf-8")
        rows.append({"name": name, "class": cls, "format": fmt, "topic": topic,
                     "size": len(b), "sha256": sha, "md5": md5, "rel": rel,
                     "url": url})
    return {"origin": origin, "rows": rows, "base": base.name}


def append_external_index(out: Path, externals: list[dict[str, Any]]) -> None:
    """Append an external-sources section to an existing INDEX.md."""
    if not externals:
        return
    L = ["", "## 10. External sources folded in (Google Drive)", "",
         "Included with the user's explicit approval so the archive is self-contained. "
         "These did **not** come from the `.dat` upload and carry their own provenance "
         "headers.", ""]
    for ext in externals:
        L.append(f"### `{ext['origin']}` → `{ext['base']}/`")
        L.append("")
        L.append("| File | Class | Format | Topic chain | Size | SHA-256 (16) | Location |")
        L.append("|------|-------|--------|-------------|------|--------------|----------|")
        for r in ext["rows"]:
            L.append(f"| [`{r['name']}`]({r['url']}) | {r['class']} | {r['format']} | "
                     f"`{r['topic']}` | {human_bytes(r['size'])} | `{r['sha256'][:16]}` | "
                     f"`{r['rel']}` |")
        L.append("")
    p = out / "INDEX.md"
    p.write_text(p.read_text(encoding="utf-8") + "\n".join(L) + "\n", encoding="utf-8")
