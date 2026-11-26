#!/usr/bin/env python3
"""
build_archive.py -- deterministic ChatGPT export -> refined-chat-archive pipeline.

Design goals
------------
* Zero omission: every message variant of every conversation is exported.
  The ChatGPT export stores conversations as a ``mapping`` graph (a forest of
  nodes).  Branches and edited messages create sibling nodes, so the set of
  *all* root->leaf paths is exported, not just the active one.  The "main"
  transcript is the path ending at ``current_node``; every other path is kept
  in ``branches/`` so no valid turn is lost.
* Deterministic: ordering, slugs, dedup and grouping are pure functions of the
  input bytes (no randomness, no sampling, no LLM calls, no truncation).
* Content-based classification of ``.dat`` files (JSON / text / binary/media).

Usage
-----
    python3 tools/build_archive.py [--root .] [--out refined-chat-archive]
                                   [--sqlite-db PATH] [--self-test]

Nothing is ever written to stdout that a caller must parse; state lives in
``<out>/.run/manifest.json``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import textwrap
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "dist", "build", ".next", ".cache",
    "refined-chat-archive", ".arena", ".local", ".npm", ".yarn",
}

CHAT_CONTAINER_KEYS = {"mapping", "conversations", "chat_messages", "messages"}
ROLE_KEYS = ("role", "author", "from", "sender")

MEDIA_MAGIC = [
    (b"\x89PNG\r\n\x1a\n", "image/png", "png"),
    (b"\xff\xd8\xff", "image/jpeg", "jpg"),
    (b"GIF87a", "image/gif", "gif"),
    (b"GIF89a", "image/gif", "gif"),
    (b"RIFF", "audio-video/riff", "riff"),
    (b"OggS", "audio/ogg", "ogg"),
    (b"ID3", "audio/mpeg", "mp3"),
    (b"\xff\xfb", "audio/mpeg", "mp3"),
    (b"fLaC", "audio/flac", "flac"),
    (b"%PDF-", "application/pdf", "pdf"),
    (b"PK\x03\x04", "application/zip", "zip"),
    (b"\x1f\x8b", "application/gzip", "gz"),
    (b"7z\xbc\xaf\x27\x1c", "application/x-7z", "7z"),
    (b"WEBP", "image/webp", "webp"),
    (b"ftyp", "video/mp4", "mp4"),
    (b"BM", "image/bmp", "bmp"),
]

RUN_DIR = ".run"

# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_file(path: Path) -> str:
    h = hashlib.md5()  # noqa: S324 - integrity inventory, not security
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sniffer_mime(head: bytes) -> str:
    for magic, mime, _ext in MEDIA_MAGIC:
        if head.startswith(magic):
            return mime
    if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "audio/wav"
    return "application/octet-stream"


def human_bytes(n: int) -> str:
    size = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{n} B"


def slugify(text: str, max_len: int = 48) -> str:
    """ASCII-ish, lowercase, hyphenated slug. Deterministic."""
    text = unicodedata.normalize("NFKD", text or "")
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if len(text) > max_len:
        cut = text[:max_len]
        text = cut.rsplit("-", 1)[0] if "-" in cut else cut
    return text or "untitled"


STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "than", "that", "this",
    "these", "those", "is", "are", "was", "were", "be", "been", "being", "to",
    "of", "in", "on", "at", "for", "with", "from", "by", "as", "it", "its",
    "i", "we", "you", "he", "she", "they", "me", "my", "our", "your", "their",
    "do", "does", "did", "can", "could", "should", "would", "will", "shall",
    "have", "has", "had", "not", "no", "yes", "there", "here", "what", "why",
    "how", "when", "where", "which", "who", "please", "help", "need", "want",
    "make", "made", "get", "got", "use", "using", "used", "about", "into",
    "some", "any", "all", "just", "like", "also", "more", "most", "very",
    "so", "up", "out", "off", "over", "under", "again", "still", "now",
    "let", "lets", "give", "tell", "show", "explain", "write", "code",
    "one", "two", "first", "last", "new", "old", "same", "other", "own",
}

TOPIC_KEYWORDS = {
    "hardware-electronics": {"esp32", "esp8266", "arduino", "stm32", "raspberry",
                             "gpio", "i2c", "spi", "uart", "circuit", "pcb",
                             "voltage", "resistor", "capacitor", "mosfet", "adc",
                             "pwm", "sensor", "relay", "ftdi", "usb", "solder",
                             "firmware", "microcontroller", "rs485", "can-bus"},
    "software-web": {"javascript", "typescript", "react", "nextjs", "node",
                     "python", "django", "flask", "api", "rest", "graphql",
                     "html", "css", "frontend", "backend", "websocket", "http",
                     "docker", "kubernetes", "nginx", "sql", "database"},
    "data-ml": {"pandas", "numpy", "pytorch", "tensorflow", "model", "dataset",
                "training", "embedding", "llm", "transformer", "vector",
                "inference", "regression", "classifier", "sklearn", "tokenizer"},
    "devops-infra": {"git", "github", "ci", "cd", "pipeline", "deploy", "aws",
                     "gcp", "azure", "terraform", "ansible", "linux", "bash",
                     "systemd", "cron", "ssh", "backup"},
    "business-writing": {"resume", "cv", "email", "essay", "cover", "letter",
                         "pitch", "marketing", "invoice", "proposal", "blog",
                         "summary", "report", "documentation"},
    "math-science": {"equation", "integral", "derivative", "matrix", "theorem",
                     "physics", "chemistry", "statistics", "probability",
                     "calculus", "algebra", "formula"},
}

# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #


@dataclass
class Msg:
    node_id: str
    seq: int
    role: str
    author_name: str
    text: str
    create_time: float | None
    iso: str
    content_type: str
    model: str | None = None
    recipient: str | None = None
    status: str | None = None
    attachments: list[dict[str, Any]] = field(default_factory=list)
    meta_extra: dict[str, Any] = field(default_factory=dict)

    @property
    def dt(self) -> dt.datetime:
        if self.create_time:
            return dt.datetime.fromtimestamp(self.create_time, dt.timezone.utc)
        return dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)


@dataclass
class Conversation:
    conv_id: str
    title: str
    create_time: float | None
    update_time: float | None
    current_node: str | None
    mapping: dict[str, dict]
    source_path: str
    source_kind: str            # json | dat-json | dat-text
    source_sha256: str
    # filled later
    main_path: list[str] = field(default_factory=list)
    branches: list[list[str]] = field(default_factory=list)
    folder: str = ""
    parent_folder: str | None = None
    chain_id: str = ""
    sort_key: tuple = ()

    @property
    def create_dt(self) -> dt.datetime:
        if self.create_time:
            return dt.datetime.fromtimestamp(self.create_time, dt.timezone.utc)
        return dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)


# --------------------------------------------------------------------------- #
# Message text extraction
# --------------------------------------------------------------------------- #


def _join_parts(parts: Any) -> str:
    if not isinstance(parts, list):
        return ""
    out = []
    for p in parts:
        if isinstance(p, str):
            out.append(p)
        elif isinstance(p, dict):
            # asset pointers / images
            if p.get("content_type") and p.get("asset_pointer"):
                out.append(f"[attachment: {p.get('asset_pointer')}]")
            elif p.get("text"):
                out.append(str(p["text"]))
            else:
                out.append(json.dumps(p, ensure_ascii=False, sort_keys=True))
        else:
            out.append(str(p))
    return "".join(out)


def extract_text(msg: dict, carry_attachments: list[dict]) -> tuple[str, str]:
    """Return (text, content_type). Never drops non-renderable payloads."""
    content = msg.get("content") or {}
    if not isinstance(content, dict):
        return str(content), "unknown"
    ctype = content.get("content_type") or "text"
    text = ""

    if ctype in ("text", "multimodal_text"):
        text = _join_parts(content.get("parts"))
    elif ctype == "code":
        text = "```" + str(content.get("language", "")) + "\n" + \
               str(content.get("text", "")) + "\n```"
    elif ctype == "execution_output":
        text = "```\n" + str(content.get("text", "")) + "\n```"
    elif ctype == "tether_browsing_display":
        text = str(content.get("result", "") or content.get("text", ""))
    elif ctype == "thoughts":
        thoughts = content.get("thoughts") or []
        lines = ["[thought] " + str(t.get("content", t)) for t in thoughts
                 if isinstance(t, dict)] if thoughts else [str(content)]
        text = "\n".join(lines)
    elif ctype == "reasoning_recap":
        text = str(content.get("content", ""))
    else:
        payload = {k: v for k, v in content.items() if k != "content_type"}
        text = f"[content_type: {ctype}]\n" + json.dumps(
            payload, ensure_ascii=False, indent=2, sort_keys=True)

    text = text or ""
    # carry attachments / refs that live at message level
    for key in ("attachments", "metadata", "files"):
        val = msg.get(key)
        if key == "attachments" and isinstance(val, list):
            for a in val:
                if isinstance(a, dict):
                    carry_attachments.append(a)
    md = msg.get("metadata") or {}
    if isinstance(md, dict) and md.get("attachments"):
        for a in md["attachments"]:
            if isinstance(a, dict):
                carry_attachments.append(a)
    return text, ctype


def normalise_role(msg: dict) -> tuple[str, str]:
    author = msg.get("author") or {}
    role = author.get("role") if isinstance(author, dict) else None
    name = author.get("name") if isinstance(author, dict) else None
    if not role:
        for k in ROLE_KEYS:
            if k in msg and isinstance(msg.get("role"), str):
                role = msg["role"]
                break
    role = str(role or "unknown")
    return role, str(name or role)


def is_hidden(msg: dict) -> bool:
    md = msg.get("metadata") or {}
    if not isinstance(md, dict):
        return False
    return bool(md.get("is_visually_hidden_from_conversation"))


# --------------------------------------------------------------------------- #
# Conversation parsing from mapping graph
# --------------------------------------------------------------------------- #


def build_mapping(conv_obj: dict) -> dict[str, dict]:
    raw = conv_obj.get("mapping")
    mapping: dict[str, dict] = {}
    if isinstance(raw, dict):
        for nid, node in raw.items():
            if isinstance(node, dict):
                mapping[str(nid)] = node
    elif isinstance(raw, list):
        for node in raw:
            if isinstance(node, dict):
                nid = str(node.get("id") or node.get("message_id")
                          or hashlib.sha1(json.dumps(node, sort_keys=True,
                                                     default=str)
                                          .encode()).hexdigest()[:16])
                mapping[nid] = node
    return mapping


def children_index(mapping: dict[str, dict]) -> dict[str | None, list[str]]:
    kids: dict[str | None, list[str]] = {}
    for nid, node in mapping.items():
        parent = node.get("parent")
        parent = str(parent) if parent else None
        kids.setdefault(parent, []).append(nid)

    def sort_key(nid: str) -> tuple:
        msg = mapping[nid].get("message") or {}
        ct = msg.get("create_time") if isinstance(msg, dict) else None
        return (ct if isinstance(ct, (int, float)) else float("inf"), nid)

    for parent in kids:
        kids[parent].sort(key=sort_key)
    return kids


def leaf_paths(mapping: dict[str, dict], current_node: str | None) -> tuple[list[str], list[list[str]]]:
    """Return (main_path, other_paths).

    A "path" is a list of node ids from a root to a leaf containing at least one
    message.  main_path prefers current_node (the ChatGPT-active thread).
    """
    kids = children_index(mapping)
    roots = kids.get(None, [])
    paths: list[list[str]] = []

    def walk(nid: str, acc: list[str]) -> None:
        acc = acc + [nid]
        nxt = kids.get(nid, [])
        if not nxt:
            paths.append(acc)
            return
        for c in nxt:
            walk(c, acc)

    for r in roots:
        walk(r, [])

    def has_msg(p: list[str]) -> bool:
        return any((mapping.get(n) or {}).get("message") for n in p)

    msg_paths = [p for p in paths if has_msg(p)]
    if not msg_paths:
        return [], []

    def last_ts(p: list[str]) -> float:
        ts = [((mapping[n].get("message") or {}).get("create_time") or 0)
              for n in p if mapping.get(n, {}).get("message")]
        return max(ts) if ts else 0.0

    main = None
    if current_node and current_node in mapping:
        ancestors = set()
        nid = current_node
        while nid:
            ancestors.add(nid)
            nid = str(mapping[nid].get("parent")) if mapping[nid].get("parent") else None
        containing = [p for p in msg_paths if p[-1] in ancestors or p[-1] == current_node]
        if containing:
            containing.sort(key=lambda p: (p[-1] == current_node, last_ts(p)), reverse=True)
            main = containing[0]
        else:
            # current_node may be a mid-path node; build path to it
            for p in msg_paths:
                if current_node in p:
                    main = p[: p.index(current_node) + 1]
                    break
    if main is None:
        msg_paths.sort(key=last_ts, reverse=True)
        main = msg_paths[0]

    others = [p for p in msg_paths if p != main]
    # de-dup identical transcripts (by node id tuple)
    seen = {tuple(main)}
    uniq = []
    for p in others:
        key = tuple(p)
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    uniq.sort(key=lambda p: (p[0], last_ts(p)))
    return main, uniq


def path_to_messages(mapping: dict[str, dict], path: list[str]) -> list[Msg]:
    out: list[Msg] = []
    for i, nid in enumerate(p for p in path if (mapping.get(p) or {}).get("message")):
        node = mapping[nid]
        msg = node.get("message") or {}
        atts: list[dict] = []
        text, ctype = extract_text(msg, atts)
        role, name = normalise_role(msg)
        ct = msg.get("create_time")
        record = msg.get("recipient")
        out.append(Msg(
            node_id=nid,
            seq=len(out) + 1,
            role=role,
            author_name=name,
            text=text,
            create_time=ct if isinstance(ct, (int, float)) else None,
            iso=(dt.datetime.fromtimestamp(ct, dt.timezone.utc)
                 .strftime("%Y-%m-%d %H:%M:%S UTC")
                 if isinstance(ct, (int, float)) else "unknown-time"),
            content_type=ctype,
            model=(msg.get("metadata") or {}).get("model_slug"),
            recipient=record if isinstance(record, str) else None,
            status=msg.get("status"),
            attachments=atts,
        ))
    return out


# --------------------------------------------------------------------------- #
# Ingestion: scanning + content-based classification
# --------------------------------------------------------------------------- #


@dataclass
class SourceFile:
    path: Path
    rel: str
    kind: str        # json | dat-json | dat-text | dat-binary | skipped
    size: int
    sha256: str = ""
    md5: str = ""
    note: str = ""


def looks_like_chat_json(obj: Any) -> bool:
    if isinstance(obj, list):
        return any(looks_like_chat_json(o) for o in obj[:50]) if obj else False
    if isinstance(obj, dict):
        keys = set(obj.keys())
        if keys & CHAT_CONTAINER_KEYS:
            return True
        return "title" in keys and "create_time" in keys
    return False


def iter_conversations(obj: Any) -> Iterator[dict]:
    """Yield conversation dicts from any export container shape."""
    if isinstance(obj, list):
        for item in obj:
            yield from iter_conversations(item)
        return
    if not isinstance(obj, dict):
        return
    if "mapping" in obj:
        yield obj
        return
    for key in ("conversations", "chats", "data", "items"):
        if isinstance(obj.get(key), list):
            yield from iter_conversations(obj[key])
            return
    # a single conversation without mapping (flat message list)
    if isinstance(obj.get("messages"), list) or isinstance(obj.get("chat_messages"), list):
        yield obj


def conv_from_flat(obj: dict, cid: str) -> Conversation:
    """Synthesise a linear mapping for exports lacking a node graph."""
    msgs = obj.get("messages") or obj.get("chat_messages") or []
    mapping: dict[str, dict] = {}
    prev = None
    for i, m in enumerate(msgs):
        nid = f"flat-{i:05d}"
        mapping[nid] = {
            "id": nid,
            "parent": prev,
            "children": [],
            "message": m if isinstance(m, dict) else {"content": {"parts": [str(m)]}},
        }
        if prev:
            mapping[prev]["children"] = [nid]
        prev = nid
    return Conversation(
        conv_id=cid,
        title=str(obj.get("title") or ""),
        create_time=obj.get("create_time"),
        update_time=obj.get("update_time"),
        current_node=prev,
        mapping=mapping,
        source_path="",
        source_kind="json",
        source_sha256="",
    )


def classify_file(path: Path, rel: str) -> SourceFile:
    size = path.stat().st_size
    head = path.open("rb").read(4096)
    sf = SourceFile(path=path, rel=rel, kind="skipped", size=size)

    is_dat = path.suffix.lower() == ".dat"
    if not is_dat:
        # .json / .jsonl (or a zip of an export)
        if path.suffix.lower() == ".zip":
            sf.kind = "zip"
            sf.note = "archive container (not auto-extracted)"
            return sf
        sf.kind = "json"
        return sf

    # --- .dat: classify by content, never by extension ----------------- #
    try:
        raw = path.read_bytes()
    except OSError as exc:                                     # pragma: no cover
        sf.kind = "dat-binary"
        sf.note = f"unreadable: {exc}"
        return sf

    text = None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = None

    if text is None:
        sf.kind = "dat-binary"
        sf.note = sniffer_mime(head)
        return sf

    stripped = text.lstrip("\ufeff \t\r\n")
    if stripped[:1] in "{[":
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            obj = None
        if obj is not None and looks_like_chat_json(obj):
            sf.kind = "dat-json"
            sf.note = "UTF-8 JSON with chat structure"
            return sf
        if obj is not None:
            sf.kind = "dat-json"
            sf.note = "UTF-8 JSON (no chat structure)"
            return sf

    # plain text?  guard against control-character soup masquerading as UTF-8
    sample = text[:4096]
    if not sample:
        sf.kind = "dat-binary"
        sf.note = "empty file"
        return sf
    ctrl = sum(1 for ch in sample
               if ord(ch) < 32 and ch not in "\n\r\t")
    if ctrl / max(len(sample), 1) > 0.02:
        sf.kind = "dat-binary"
        sf.note = f"binary-ish text ({sniffer_mime(head)})"
        return sf
    sf.kind = "dat-text"
    sf.note = "plain UTF-8 text"
    return sf


def parse_text_log(text: str, rel: str) -> tuple[list[Conversation], str]:
    """Parse a .dat plain-text conversation log. Tolerant, never lossy."""
    # 1) JSON-ish text log
    try:
        obj = json.loads(text)
        convs = [c for c in iter_conversations(obj)]
        if convs:
            return ([Conversation(conv_id=str(c.get("id") or c.get("conversation_id")
                                    or hashlib.sha256(rel.encode()).hexdigest()[:16]),
                                  title=str(c.get("title") or ""),
                                  create_time=c.get("create_time"),
                                  update_time=c.get("update_time"),
                                  current_node=c.get("current_node"),
                                  mapping=build_mapping(c),
                                  source_path=rel, source_kind="dat-json",
                                  source_sha256="")
                     for c in convs], "json")
    except json.JSONDecodeError:
        pass

    # 2) role-tagged blocks:  "USER:", "Assistant:", "[USER]", "### User"
    header = re.compile(
        r"^[\[\(]?\s*(user|human|assistant|ai|system|gpt|chatgpt|tool)\s*[\]\)]?\s*[:>-]?\s*$",
        re.IGNORECASE)
    inline = re.compile(
        r"^[\[\(]?\s*(user|human|assistant|ai|system|gpt|chatgpt)\s*[\]\)]?\s*[:>-]\s*(.+)$",
        re.IGNORECASE)

    msgs: list[dict] = []
    buf: list[str] = []
    cur_role: str | None = None

    def flush() -> None:
        nonlocal buf, cur_role
        if cur_role is not None:
            msgs.append({"author": {"role": cur_role},
                         "content": {"content_type": "text",
                                     "parts": ["\n".join(buf).strip("\n")]},
                         "create_time": None})
        buf = []

    for line in text.splitlines():
        m_inline = inline.match(line)
        m_head = header.match(line.strip())
        if m_head or m_inline:
            flush()
            cur_role = (m_inline.group(1) if m_inline else m_head.group(1)).lower()
            cur_role = {"human": "user", "ai": "assistant", "gpt": "assistant",
                        "chatgpt": "assistant"}.get(cur_role, cur_role)
            if m_inline and m_inline.group(2):
                buf.append(m_inline.group(2))
            continue
        buf.append(line)
    flush()

    if not msgs:
        # 3) unlabelled but non-empty: keep the whole text verbatim as one turn
        return ([Conversation(
            conv_id=hashlib.sha256(text.encode()).hexdigest()[:16],
            title=Path(rel).stem,
            create_time=None, update_time=None, current_node=None,
            mapping={"flat-00000": {"id": "flat-00000", "parent": None,
                                    "children": [],
                                    "message": {"author": {"role": "unknown"},
                                                "content": {"content_type": "text",
                                                            "parts": [text]},
                                                "create_time": None}}},
            source_path=rel, source_kind="dat-text", source_sha256="")],
            "verbatim")
    return ([Conversation(
        conv_id=hashlib.sha256((rel + str(len(msgs))).encode()).hexdigest()[:16],
        title=Path(rel).stem,
        create_time=None, update_time=None, current_node=None,
        mapping={f"m-{i:05d}": {"id": f"m-{i:05d}",
                                "parent": f"m-{i-1:05d}" if i else None,
                                "children": [f"m-{i+1:05d}"] if i + 1 < len(msgs) else [],
                                "message": m} for i, m in enumerate(msgs)},
        source_path=rel, source_kind="dat-text", source_sha256="")],
        "role-blocks")


def load_sqlite_conversations(db: Path) -> list[Conversation]:
    """Convert a chats.sqlite export (if present) into Conversation objects."""
    out: list[Conversation] = []
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        tables = {r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        if not {"conversations", "messages"} <= tables:
            con.close()
            return out
        msgs_by_conv: dict[str, list[dict]] = {}
        for row in con.execute("SELECT * FROM messages"):
            d = dict(row)
            cid = str(d.get("conversation_id") or d.get("conv_id") or "")
            author = d.get("author") or d.get("role") or "unknown"
            if isinstance(author, str) and author.startswith("{"):
                try:
                    author = json.loads(author).get("role", author)
                except json.JSONDecodeError:
                    pass
            content = d.get("content") or ""
            if isinstance(content, str) and content.startswith("{"):
                try:
                    cobj = json.loads(content)
                except json.JSONDecodeError:
                    cobj = None
                if isinstance(cobj, dict) and "parts" in cobj:
                    content = cobj
            parts = content.get("parts") if isinstance(content, dict) else [content]
            ctype = (content.get("content_type")
                     if isinstance(content, dict) else "text") or "text"
            msgs_by_conv.setdefault(cid, []).append({
                "author": {"role": author if isinstance(author, str) else "unknown"},
                "content": {"content_type": ctype, "parts": parts},
                "create_time": d.get("create_time"),
            })
        for row in con.execute("SELECT * FROM conversations"):
            d = dict(row)
            cid = str(d.get("id") or d.get("conversation_id") or "")
            flat = {"title": d.get("title") or "", "messages": msgs_by_conv.get(cid, [])}
            conv = conv_from_flat(flat, cid)
            conv.create_time = d.get("create_time")
            conv.update_time = d.get("update_time")
            conv.current_node = d.get("current_node")
            conv.source_path = str(db)
            conv.source_kind = "sqlite"
            out.append(conv)
        con.close()
    except sqlite3.Error:
        return out
    return out


# --------------------------------------------------------------------------- #
# Hierarchy: topic chaining
# --------------------------------------------------------------------------- #


def topic_tokens(title: str, first_user_text: str) -> set[str]:
    blob = (title + " " + first_user_text[:400]).lower()
    words = re.findall(r"[a-z0-9]{3,}", blob)
    return {w for w in words if w not in STOPWORDS}


def dominant_topic(tokens: set[str]) -> str:
    best, best_n = "general", 0
    for topic, kws in TOPIC_KEYWORDS.items():
        n = len(tokens & kws)
        if n > best_n:
            best, best_n = topic, n
    return best if best_n else "general"


def build_hierarchy(convs: list[Conversation], lookahead: int = 4,
                    jaccard_min: float = 0.34) -> None:
    """Assign folder / parent_folder / chain_id deterministically.

    Ordering: create_time asc, then title, then conv_id (stable).
    A conversation becomes a child of the most recent earlier conversation
    (within ``lookahead``) whose token Jaccard similarity clears
    ``jaccard_min`` or which shares the same explicit project tag.
    """
    convs.sort(key=lambda c: (c.create_dt, c.title.lower(), c.conv_id))
    tokens: list[set[str]] = []
    topics: list[str] = []
    for c in convs:
        first_user = ""
        for nid in c.main_path:
            m = (c.mapping.get(nid) or {}).get("message") or {}
            role, _ = normalise_role(m)
            if role == "user":
                t, _ = extract_text(m, [])
                first_user = t
                break
        tk = topic_tokens(c.title, first_user)
        tokens.append(tk)
        topics.append(dominant_topic(tk))

    used_paths: set[str] = set()
    for i, conv in enumerate(convs):
        parent_idx = None
        best_score = 0.0
        for j in range(max(0, i - lookahead), i):
            a, b = tokens[j], tokens[i]
            if not a or not b:
                continue
            inter = len(a & b)
            union = len(a | b)
            score = inter / union if union else 0.0
            same_topic_bonus = 0.05 if topics[j] == topics[i] != "general" else 0.0
            score += same_topic_bonus
            if score >= jaccard_min and score > best_score:
                parent_idx, best_score = j, score
        chain_id = f"chain-{topics[i]}"
        parent_dir = None
        if parent_idx is not None:
            parent_dir = convs[parent_idx].folder
            conv.chain_id = convs[parent_idx].chain_id or chain_id
        else:
            conv.chain_id = chain_id

        date = conv.create_dt.strftime("%Y-%m-%d")
        base = f"{date}_{slugify(conv.title or 'untitled')}"
        name = base
        candidate = f"{parent_dir}/{name}" if parent_dir else name
        n = 2
        while candidate in used_paths:
            name = f"{base}-{n}"
            candidate = f"{parent_dir}/{name}" if parent_dir else name
            n += 1
        used_paths.add(candidate)
        conv.folder = candidate
        conv.parent_folder = parent_dir


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #


def render_message(m: Msg) -> list[str]:
    label = {"user": "USER", "assistant": "ASSISTANT", "system": "SYSTEM",
             "tool": "TOOL"}.get(m.role, m.role.upper() or "UNKNOWN")
    who = f" ({m.author_name})" if m.author_name and m.author_name != m.role else ""
    attrs = [m.iso]
    if m.model:
        attrs.append(f"model={m.model}")
    if m.content_type and m.content_type != "text":
        attrs.append(f"content={m.content_type}")
    if m.status and m.status not in ("finished_successfully",):
        attrs.append(f"status={m.status}")
    lines = [f"#### [{label}]{who}  <!-- {', '.join(attrs)} -->", ""]
    body = m.text if m.text.strip() else "*(no textual content in this turn)*"
    lines.append(body)
    if m.attachments:
        lines.append("")
        lines.append("*Attachments referenced in this turn:*")
        for a in m.attachments:
            nm = a.get("name") or a.get("file_name") or a.get("id") or "attachment"
            lines.append(f"- `{nm}`  ({a.get('mime_type', 'unknown type')}, "
                         f"{a.get('size', '?')} bytes)")
    lines.append("")
    return lines


def render_transcript(msgs: list[Msg]) -> str:
    out: list[str] = []
    for m in msgs:
        out.extend(render_message(m))
        out.append("---")
        out.append("")
    return "\n".join(out)


def consolidate_questions(msgs: list[Msg]) -> str:
    users = [m for m in msgs if m.role == "user" and m.text.strip()]
    if not users:
        return "_No user turns were present in this conversation._"
    chunks: list[str] = []
    for m in users:
        t = re.sub(r"```.*?```", "[code block]", m.text, flags=re.S)
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) > 700:
            t = t[:700].rsplit(" ", 1)[0] + " …"
        if t:
            chunks.append(t)
    joined = " ".join(chunks)
    joined = re.sub(r"\s+", " ", joined).strip()
    joined = joined.replace("[code block] …", "[code block]")
    if not joined.endswith((".", "!", "?", "…", "`")):
        joined += "."
    return joined


def collect_tech(msgs: list[Msg]) -> dict[str, list[str]]:
    """Extractive inventory: code languages, commands, links, numbers."""
    langs, cmds, links, numbers = [], [], [], []
    for m in msgs:
        for lang in re.findall(r"```([a-zA-Z0-9_+-]{1,20})\b", m.text):
            if lang.lower() not in ("code",):
                langs.append(lang.lower())
        for cmd in re.findall(r"(?m)^\s*(?:\$|>)\s*(.+)$", m.text):
            cmds.append(cmd.strip())
        for url in re.findall(r"https?://[^\s)>\]]+", m.text):
            links.append(url.rstrip(".,;"))
        if m.role == "user":
            for num in re.findall(r"\b\d+(?:\.\d+)?\s?(?:v|vdc|vac|ma|a|ω|ohm|kω|"
                                  r"hz|khz|mhz|f|µf|nf|pf|mm|cm|ms|us|s|%)\b",
                                  m.text, re.IGNORECASE):
                numbers.append(num.strip())
    def uniq(seq):
        seen, out = set(), []
        for s in seq:
            if s and s not in seen:
                seen.add(s)
                out.append(s)
        return out
    return {
        "languages": uniq(langs)[:40],
        "commands": uniq(cmds)[:60],
        "links": uniq(links)[:80],
        "numbers": uniq(numbers)[:60],
    }


def render_refined_chat(conv: Conversation, main: list[Msg]) -> str:
    title = conv.title or "Untitled conversation"
    questions = consolidate_questions(main)
    tech = collect_tech(main)
    users = [m for m in main if m.role == "user"]
    assists = [m for m in main if m.role == "assistant"]
    first = main[0].iso if main else "unknown"
    last = main[-1].iso if main else "unknown"

    lines: list[str] = []
    A = lines.append
    A(f"# {title}")
    A("")
    A(f"- **Conversation ID:** `{conv.conv_id}`")
    A(f"- **Source:** `{conv.source_path}` ({conv.source_kind})")
    A(f"- **Created:** {conv.create_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}"
      f"  ·  **Last turn:** {last}")
    A(f"- **Turns:** {len(main)} total — {len(users)} user / {len(assists)} assistant"
      + (f" / {len(main) - len(users) - len(assists)} other" if len(main) - len(users) - len(assists) else ""))
    A(f"- **Topic chain:** `{conv.chain_id}`"
      + (f"  ·  **Parent topic folder:** `{conv.parent_folder}`" if conv.parent_folder else "  ·  **Root of chain**"))
    if conv.branches:
        A(f"- **Alternate branches preserved:** {len(conv.branches)} "
          f"(see `branches/` — these are edited/regenerated message paths)")
    A("")
    A("---")
    A("")
    A("## Section A — Consolidated User Questions")
    A("")
    A("> Every user prompt from this conversation, condensed into one continuous paragraph "
      "that follows the order in which the requests were made.")
    A("")
    A(questions)
    A("")
    A("---")
    A("")
    A("## Section B — Comprehensive Chat Summary & Actionable Suggestions")
    A("")
    A("### B.1 What this conversation covers")
    A("")
    A(f"The conversation opens with the request below and develops across "
      f"{len(main)} turns ({len(users)} user, {len(assists)} assistant) between {first} and {last}.")
    A("")
    if questions and not questions.startswith("_"):
        A("> " + textwrap.shorten(questions, width=460, placeholder=" …"))
        A("")
    A("### B.2 Turn-by-turn progression (complete, extracted from the transcript)")
    A("")
    for m in main:
        snippet = re.sub(r"```.*?```", " [code block] ", m.text, flags=re.S)
        snippet = re.sub(r"<(?:details|summary)[^>]*>", "", snippet)
        snippet = re.sub(r"\s+", " ", snippet).strip()
        if not snippet:
            snippet = "(no textual content)"
        snippet = textwrap.shorten(snippet, width=300, placeholder=" …")
        A(f"- **Turn {m.seq} · {m.role}** ({m.iso}) — {snippet}")
    A("")
    A("### B.3 Technical inventory preserved in the transcript")
    A("")
    if tech["languages"]:
        A("- **Code languages / fences:** " + ", ".join(f"`{x}`" for x in tech["languages"]))
    if tech["commands"]:
        A("- **Commands issued or documented:**")
        for c in tech["commands"][:25]:
            A(f"  - `{c}`")
        if len(tech["commands"]) > 25:
            A(f"  - …and {len(tech['commands']) - 25} more, all present in the full transcript below")
    if tech["numbers"]:
        A("- **Quantities / specs mentioned:** " + ", ".join(tech["numbers"][:30]))
    if tech["links"]:
        A("- **Links referenced:**")
        for u in tech["links"][:20]:
            A(f"  - {u}")
        if len(tech["links"]) > 20:
            A(f"  - …and {len(tech['links']) - 20} more in the transcript")
    if not any(tech.values()):
        A("- No code fences, commands, links or numeric specs were detected in the user turns.")
    A("")
    A("> Section C below is the authoritative record. Nothing from this conversation was "
      "dropped, condensed, or paraphrased there: every turn, code block, command, table and "
      "error log appears exactly as it was in the export.")
    A("")
    A("### B.4 Suggestions & next steps")
    A("")
    suggestions = list(SUGGESTIONS)
    if len(conv.branches):
        suggestions.insert(0,
            f"This conversation has {len(conv.branches)} alternate branch(es) where messages "
            "were edited or responses regenerated. Compare `branches/` against the main "
            "transcript before relying on any single answer — the discarded variant often "
            "contains the version that was actually correct.")
    if tech["commands"]:
        suggestions.insert(0,
            "Re-run the archived commands in a scratch environment and record the exact "
            "versions used; commands captured in old chats usually omit the toolchain "
            "version that made them work.")
    for s in suggestions:
        A(f"- {s}")
    A("")
    A("---")
    A("")
    A("## Section C — Complete Pin-to-Pin Refined Transcript")
    A("")
    A("> Chronological, first message to last response. Formatting artefacts and export "
      "noise were cleaned; content was not altered.")
    A("")
    A(render_transcript(main))
    return "\n".join(lines)


SUGGESTIONS = [
    "Freeze the decisions from this thread into a versioned document (or a repo README) so the reasoning does not live only in chat history.",
    "Any spec, formula, wiring list or pinout recovered here should be re-validated against the current datasheet before it is used in hardware — part revisions silently change pin functions and voltage limits.",
    "Where the conversation contains code that was never executed, run it under the exact dependency versions discussed; treat unverified snippets as pseudocode.",
    "Convert repeated ad-hoc commands into a checked-in script so the workflow is reproducible rather than retyped from memory.",
    "Record the open questions at the end of the thread as issues; unfinished threads are where regressions usually originate.",
]


def render_branch_file(conv: Conversation, idx: int, path: list[str]) -> str:
    msgs = path_to_messages(conv.mapping, path)
    div = [i for i, m in enumerate(msgs) if m.node_id == path[0]]
    lines = [
        f"# Branch {idx} — {conv.title or 'Untitled conversation'}",
        "",
        f"- **Conversation ID:** `{conv.conv_id}`",
        f"- **Nodes:** {len(path)}",
        f"- **Turns:** {len(msgs)}",
        f"- **Forks from:** message #{div[0] + 1 if div else 1} of the full node chain",
        "",
        "This path diverges from the main transcript because a message was edited or a "
        "response was regenerated in the original chat. It is preserved verbatim so no "
        "valid turn is lost.",
        "",
        "---",
        "",
    ]
    lines.append(render_transcript(msgs))
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# INDEX.md
# --------------------------------------------------------------------------- #


def folder_tree(convs: list[Conversation], root: str) -> list[str]:
    """ASCII tree of the generated archive (folders that actually exist)."""
    paths = sorted({c.folder for c in convs})
    tree: dict[str, Any] = {}
    for p in paths:
        parts = Path(p).parts
        node = tree
        for part in parts:
            node = node.setdefault(part, {})

    out: list[str] = [f"{root}/"]

    def walk(node: dict[str, Any], prefix: str) -> None:
        items = sorted(node.items())
        for i, (name, child) in enumerate(items):
            last = i == len(items) - 1
            out.append(f"{prefix}{'└── ' if last else '├── '}{name}/")
            walk(child, prefix + ("    " if last else "│   "))

    walk(tree, "")
    return out


def write_index(out: Path, convs: list[Conversation], sources: list[SourceFile],
                binaries: list[dict], stats: dict[str, Any]) -> None:
    L: list[str] = []
    A = L.append
    A("# Refined ChatGPT Archive — Master Index")
    A("")
    A(f"Generated: {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    A("")
    A("Pipeline: `tools/build_archive.py` (deterministic; no message was summarised away — "
      "Section C of every `refined_chat.txt` is the verbatim transcript).")
    A("")
    A("## 1. Source inventory")
    A("")
    A("| # | File | Classified as | Size | SHA-256 (first 16) | Note |")
    A("|---|------|---------------|------|--------------------|------|")
    for i, s in enumerate(sources, 1):
        A(f"| {i} | `{s.rel}` | {s.kind} | {human_bytes(s.size)} | "
          f"{'`'+s.sha256[:16]+'`' if s.sha256 else '—'} | {s.note or ''} |")
    A("")
    A("### Counts by class")
    A("")
    A("| Class | Count |")
    A("|-------|-------|")
    for k, v in stats["classes"].items():
        A(f"| {k} | {v} |")
    A("")
    A("## 2. Conversation counts")
    A("")
    A(f"- Conversation records parsed from sources (raw): **{stats['parsed_raw']}**")
    A(f"- Duplicate copies collapsed: **{stats['duplicates']}**")
    A(f"- Unique conversations found: **{stats['found']}**")
    A(f"- Conversations processed and written: **{stats['processed']}**")
    A(f"- `refined_chat.txt` files on disk: **{stats['files_on_disk']}**")
    A(f"- Alternate branch transcripts preserved: **{stats['branches']}**")
    A(f"- Binary `.dat` files preserved: **{stats['binaries']}**")
    ok_match = (stats["parsed_raw"] - stats["duplicates"] == stats["found"]
                == stats["processed"] == stats["files_on_disk"])
    A(f"- Accounting reconciles (parsed − duplicates = written = on disk): "
      f"**{'YES' if ok_match else 'NO'}**")
    if stats["duplicates"]:
        A(f"- Duplicate conversations collapsed: **{stats['duplicates']}** "
          "(identical ID + identical content hash; copies are cross-referenced, not deleted)")
    A("")
    A("## 3. Folder tree")
    A("")
    A("```text")
    L.extend(folder_tree(convs, "refined-chat-archive"))
    A("```")
    A("")
    A("## 4. Chronological sequence & topic chains")
    A("")
    A("| # | Date | Conversation | Folder | Chain | Source type | Turns |")
    A("|---|------|--------------|--------|-------|-------------|-------|")
    for i, c in enumerate(convs, 1):
        depth = len(Path(c.folder).parts) - 1
        indent = "&nbsp;&nbsp;" * depth + ("└ " if depth else "")
        A(f"| {i} | {c.create_dt.strftime('%Y-%m-%d')} | "
          f"{indent}[{c.title or 'Untitled'}]({c.folder}/refined_chat.txt) | "
          f"`{c.folder}` | `{c.chain_id}` | {c.source_kind} | {len(c.main_path)} |")
    A("")
    A("## 5. Binary / media `.dat` inventory")
    A("")
    if not binaries:
        A("_No binary or media `.dat` files were found in the workspace._")
    else:
        A("| # | File | Original name | Size | MIME (sniffed) | MD5 | SHA-256 | Related conversation |")
        A("|---|------|---------------|------|----------------|-----|---------|----------------------|")
        for i, b in enumerate(binaries, 1):
            A(f"| {i} | `raw_dat_attachments/{b['stored']}` | `{b['original']}` | "
              f"{human_bytes(b['size'])} | {b['mime']} | `{b['md5']}` | `{b['sha256']}` | "
              f"{b.get('related') or '—'} |")
    A("")
    A("## 6. Integrity manifest")
    A("")
    A("| File | SHA-256 | Bytes |")
    A("|------|---------|-------|")
    for p in sorted(out.rglob("*")):
        if p.is_file() and RUN_DIR not in p.parts and p.name != "INDEX.md":
            rel = p.relative_to(out).as_posix()
            A(f"| `{rel}` | `{sha256_file(p)}` | {p.stat().st_size} |")
    A("")
    A("## 7. Notes on method")
    A("")
    A("- `.dat` files were classified by content, never by extension: UTF-8+JSON with chat "
      "structure → parsed as JSON; valid UTF-8 text → parsed as a conversation log; "
      "non-UTF-8 or control-heavy bytes → copied byte-for-byte into `raw_dat_attachments/`.")
    A("- Conversation graphs were traversed exhaustively: the active thread "
      "(`current_node` ancestry) is the main transcript, and every other root→leaf path is "
      "written to `<conversation>/branches/` so edited and regenerated turns survive.")
    A("- Folder nesting is computed from topic similarity between consecutive conversations "
      "(title + first user prompt), so a debugging follow-up lands inside the project folder "
      "it belongs to instead of beside it.")
    (out / "INDEX.md").write_text("\n".join(L) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# Main build
# --------------------------------------------------------------------------- #


def scan_sources(root: Path) -> list[SourceFile]:
    found: list[SourceFile] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            if Path(fn).suffix.lower() not in (".json", ".dat", ".jsonl", ".zip"):
                continue
            p = Path(dirpath) / fn
            rel = p.relative_to(root).as_posix()
            found.append(classify_file(p, rel))
    for sf in found:
        if sf.kind != "skipped":
            sf.sha256 = sha256_file(sf.path)
            sf.md5 = md5_file(sf.path)
    return found


def gather_conversations(sources: list[SourceFile]) -> tuple[list[Conversation], list[str]]:
    convs: list[Conversation] = []
    warnings: list[str] = []
    for sf in sources:
        if sf.kind in ("json", "dat-json"):
            try:
                obj = json.loads(sf.path.read_text(encoding="utf-8-sig"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                warnings.append(f"{sf.rel}: cannot parse as JSON ({exc})")
                if sf.kind == "json" and sf.path.suffix.lower() == ".jsonl":
                    objs = []
                    for line in sf.path.read_text(encoding="utf-8",
                                                  errors="replace").splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            objs.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
                    obj = objs
                else:
                    continue
            for raw in iter_conversations(obj):
                cid = str(raw.get("id") or raw.get("conversation_id")
                          or hashlib.sha256(json.dumps(raw, sort_keys=True,
                                                       default=str).encode()).hexdigest()[:16])
                mapping = build_mapping(raw)
                if not mapping:
                    conv = conv_from_flat(raw, cid)
                else:
                    conv = Conversation(
                        conv_id=cid,
                        title=str(raw.get("title") or ""),
                        create_time=raw.get("create_time"),
                        update_time=raw.get("update_time"),
                        current_node=raw.get("current_node"),
                        mapping=mapping,
                        source_path=sf.rel,
                        source_kind=sf.kind,
                        source_sha256=sf.sha256,
                    )
                conv.source_path = sf.rel
                conv.source_kind = sf.kind
                conv.source_sha256 = sf.sha256
                convs.append(conv)
        elif sf.kind == "dat-text":
            try:
                text = sf.path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                warnings.append(f"{sf.rel}: not decodable as text, treated as binary")
                continue
            parsed, how = parse_text_log(text, sf.rel)
            for c in parsed:
                c.source_sha256 = sf.sha256
                convs.append(c)
            if not parsed:
                warnings.append(f"{sf.rel}: text log yielded no conversations ({how})")
    return convs, warnings


def dedupe(convs: list[Conversation]) -> tuple[list[Conversation], list[str]]:
    seen: dict[tuple, Conversation] = {}
    order: list[Conversation] = []
    dups: list[str] = []
    for c in convs:
        mapping_json = json.dumps(c.mapping, sort_keys=True, default=str)
        key = (c.conv_id, hashlib.sha256(mapping_json.encode()).hexdigest()[:16])
        if key in seen:
            dups.append(f"{c.source_path}: duplicate of {seen[key].source_path} "
                        f"(conversation {c.conv_id})")
            continue
        seen[key] = c
        order.append(c)
    return order, dups


def build(root: Path, out: Path) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    (out / RUN_DIR).mkdir(exist_ok=True)
    raw_dir = out / "raw_dat_attachments"
    raw_dir.mkdir(exist_ok=True)

    sources = scan_sources(root)
    classes: dict[str, int] = {}
    for s in sources:
        classes[s.kind] = classes.get(s.kind, 0) + 1

    # --- binary .dat inventory -------------------------------------------- #
    binaries: list[dict] = []
    used_names: set[str] = set()
    for sf in sources:
        if sf.kind != "dat-binary":
            continue
        stored = Path(sf.rel).name
        if stored in used_names:
            stem, suf = Path(stored).stem, Path(stored).suffix
            stored = f"{stem}_{sf.sha256[:8]}{suf}"
        used_names.add(stored)
        dst = raw_dir / stored
        shutil.copy2(sf.path, dst)
        head = dst.open("rb").read(64)
        binaries.append({
            "original": Path(sf.rel).name,
            "rel": sf.rel,
            "stored": stored,
            "size": sf.size,
            "sha256": sf.sha256,
            "md5": sf.md5,
            "mime": sniffer_mime(head),
            "related": "",
        })

    # --- sqlite export ---------------------------------------------------- #
    convs, warnings = gather_conversations(sources)
    for db in sorted(root.rglob("chats.sqlite")):
        if any(part in SKIP_DIRS for part in db.parts):
            continue
        convs.extend(load_sqlite_conversations(db))

    # --- parse graphs ----------------------------------------------------- #
    kept: list[Conversation] = []
    for c in convs:
        if not c.mapping:
            warnings.append(f"conversation {c.conv_id} ({c.title!r}) has no messages; skipped")
            continue
        c.main_path, c.branches = leaf_paths(c.mapping, c.current_node)
        if not c.main_path:
            warnings.append(f"conversation {c.conv_id} ({c.title!r}) produced no path; skipped")
            continue
        if not c.create_time:
            # fall back to earliest message timestamp
            ts = [m.create_time for m in path_to_messages(c.mapping, c.main_path)
                  if m.create_time]
            c.create_time = min(ts) if ts else None
        kept.append(c)

    kept, dup_notes = dedupe(kept)
    build_hierarchy(kept)

    # --- write conversation folders --------------------------------------- #
    files_written = 0
    for c in kept:
        folder = out / c.folder
        folder.mkdir(parents=True, exist_ok=True)
        main_msgs = path_to_messages(c.mapping, c.main_path)
        (folder / "refined_chat.txt").write_text(
            render_refined_chat(c, main_msgs), encoding="utf-8")
        files_written += 1
        if c.branches:
            bdir = folder / "branches"
            bdir.mkdir(exist_ok=True)
            for i, path in enumerate(c.branches, 1):
                (bdir / f"branch_{i:02d}.txt").write_text(
                    render_branch_file(c, i, path), encoding="utf-8")
        # link binary attachments that this conversation references by name
        blob = "\n".join(m.text for m in main_msgs)
        for b in binaries:
            if b["original"] and b["original"] in blob and not b["related"]:
                b["related"] = c.folder

    files_on_disk = sum(1 for _ in out.rglob("refined_chat.txt"))
    stats = {
        "classes": classes,
        "parsed_raw": len(convs),
        "found": len(kept),
        "processed": len(kept),
        "files_on_disk": files_on_disk,
        "duplicates": len(dup_notes),
        "binaries": len(binaries),
        "branches": sum(len(c.branches) for c in kept),
    }

    write_index(out, kept, sources, binaries, stats)

    manifest = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "root": str(root),
        "out": str(out),
        "stats": stats,
        "warnings": warnings,
        "duplicates": dup_notes,
        "conversations": [
            {"id": c.conv_id, "title": c.title, "folder": c.folder,
             "chain": c.chain_id, "source": c.source_path,
             "kind": c.source_kind, "turns": len(c.main_path),
             "branches": len(c.branches)}
            for c in kept
        ],
        "binaries": binaries,
        "sources": [{"rel": s.rel, "kind": s.kind, "size": s.size,
                     "sha256": s.sha256, "md5": s.md5, "note": s.note}
                    for s in sources],
    }
    (out / RUN_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / RUN_DIR / "build.log").write_text(
        "\n".join([f"warnings: {len(warnings)}"] + warnings +
                  [f"duplicates: {len(dup_notes)}"] + dup_notes), encoding="utf-8")
    return manifest


# --------------------------------------------------------------------------- #
# Self-test (uses synthetic fixtures in a temp dir, never touches data)
# --------------------------------------------------------------------------- #


def self_test() -> int:
    import tempfile

    ok = True

    def check(cond: bool, label: str) -> None:
        nonlocal ok
        print(("PASS  " if cond else "FAIL  ") + label)
        ok = ok and cond

    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "src"
        src.mkdir()
        # 1. conversation with a branch (edited user message) + tool call
        conv = {
            "id": "c-branch", "title": "ESP32 WebSocket JSON parser",
            "create_time": 1730000000.0, "update_time": 1730000500.0,
            "current_node": "a2",
            "mapping": {
                "root": {"id": "root", "parent": None, "children": ["u1"], "message": None},
                "u1": {"id": "u1", "parent": "root", "children": ["a1"],
                       "message": {"author": {"role": "user"},
                                   "content": {"content_type": "text",
                                               "parts": ["Parse JSON over an ESP32 websocket. "
                                                         "Voltage is 3.3 V."]},
                                   "create_time": 1730000001.0}},
                "a1": {"id": "a1", "parent": "u1", "children": ["u2"],
                       "message": {"author": {"role": "assistant"},
                                   "content": {"content_type": "text",
                                               "parts": ["Use ArduinoJson:\n```cpp\n"
                                                         "deserializeJson(doc, payload);\n```"]},
                                   "create_time": 1730000002.0,
                                   "metadata": {"model_slug": "gpt-4o"}}},
                "u2": {"id": "u2", "parent": "a1", "children": ["a2", "u2b"],
                       "message": {"author": {"role": "user"},
                                   "content": {"content_type": "text",
                                               "parts": ["Now add a checksum."]},
                                   "create_time": 1730000003.0}},
                "a2": {"id": "a2", "parent": "u2", "children": [],
                       "message": {"author": {"role": "assistant"},
                                   "content": {"content_type": "text",
                                               "parts": ["CRC32:\n```cpp\ncrc32(payload, len);\n```"]},
                                   "create_time": 1730000004.0}},
                # edited variant of u2 -> must be preserved
                "u2b": {"id": "u2b", "parent": "a1", "children": ["a2b"],
                        "message": {"author": {"role": "user"},
                                    "content": {"content_type": "text",
                                                "parts": ["Actually add a CRC16-CCITT instead."]},
                                    "create_time": 1730000003.5}},
                "a2b": {"id": "a2b", "parent": "u2b", "children": [],
                        "message": {"author": {"role": "assistant"},
                                    "content": {"content_type": "text",
                                                "parts": ["CCITT table..."]},
                                    "create_time": 1730000006.0}},
            },
        }
        # 2. related follow-up -> must nest under conversation 1
        follow = {
            "id": "c-follow", "title": "ESP32 websocket JSON parser CRC issue",
            "create_time": 1730003600.0,
            "current_node": "f1",
            "mapping": {
                "f0": {"id": "f0", "parent": None, "children": ["f1"], "message": None},
                "f1": {"id": "f1", "parent": "f0", "children": [],
                       "message": {"author": {"role": "user"},
                                   "content": {"content_type": "text",
                                               "parts": ["The ESP32 websocket JSON parser CRC "
                                                         "fails on large payloads."]},
                                   "create_time": 1730003601.0}},
            },
        }
        # 3. unrelated conversation -> top level
        other = {
            "id": "c-other", "title": "Sourdough starter hydration",
            "create_time": 1730100000.0, "current_node": "o1",
            "mapping": {
                "o0": {"id": "o0", "parent": None, "children": ["o1"], "message": None},
                "o1": {"id": "o1", "parent": "o0", "children": [],
                       "message": {"author": {"role": "user"},
                                   "content": {"content_type": "text",
                                               "parts": ["What hydration for rye sourdough?"]},
                                   "create_time": 1730100001.0}},
            },
        }
        (src / "conversations.json").write_text(
            json.dumps([conv, follow, other]), encoding="utf-8")
        # 4. JSON .dat (chat structure)
        (src / "export_part.dat").write_text(
            json.dumps({"conversations": [dict(other, id="c-dat",
                                               title="Sourdough rye hydration schedule")]}),
            encoding="utf-8")
        # 5. plain-text .dat
        (src / "manual_log.dat").write_text(
            "USER: How do I size a 5 V relay driver?\n"
            "The coil draws 70 mA.\n"
            "ASSISTANT: Use a 2N2222 with a 1k base resistor.\n"
            "USER: And a flyback diode?\n"
            "ASSISTANT: 1N4007 across the coil.\n", encoding="utf-8")
        # 6. binary .dat
        (src / "photo.dat").write_bytes(b"\x89PNG\r\n\x1a\n" + bytes(range(256)) * 4)
        # 7. duplicate copy of conversations.json
        (src / "conversations (1).json").write_text(
            (src / "conversations.json").read_text(), encoding="utf-8")

        out = Path(td) / "out"
        manifest = build(src, out)
        st = manifest["stats"]
        check(st["classes"].get("dat-json") == 1, "JSON .dat classified by content")
        check(st["classes"].get("dat-text") == 1, "plain-text .dat classified")
        check(st["classes"].get("dat-binary") == 1, "binary .dat classified")
        check(st["duplicates"] == 3, "duplicate conversations collapsed (3)")
        check(st["processed"] == 5,
              f"unique conversations kept = 5 ({st['processed']})")
        check(st["files_on_disk"] == st["processed"],
              f"refined_chat.txt count == unique processed conversations "
              f"({st['files_on_disk']}/{st['processed']})")
        check(st["parsed_raw"] - st["duplicates"] == st["processed"],
              "raw parsed - duplicates == processed (full accounting)")
        check(st["binaries"] == 1, "binary .dat copied to raw_dat_attachments")
        check((out / "raw_dat_attachments" / "photo.dat").exists(),
              "binary attachment preserved byte-for-byte")
        text_log = [c for c in manifest["conversations"] if c["kind"] == "dat-text"]
        check(bool(text_log) and text_log[0]["turns"] >= 4,
              "text .dat parsed into role-tagged turns")
        nested = [c for c in manifest["conversations"] if "/" in c["folder"]]
        check(bool(nested) and "esp32" in nested[0]["folder"].split("/")[0],
              f"follow-up nested inside parent topic ({nested[0]['folder'] if nested else 'none'})")
        branch_files = list(out.rglob("branches/branch_*.txt"))
        check(len(branch_files) == 1, "edited branch preserved in branches/")
        rc = (out / [c for c in manifest["conversations"]
                     if c["title"].startswith("ESP32 WebSocket")][0]["folder"]
              / "refined_chat.txt").read_text()
        for section in ("## Section A", "## Section B", "## Section C"):
            check(section in rc, f"refined_chat.txt contains {section}")
        check("deserializeJson" in rc and "crc32" in rc, "code blocks preserved verbatim")
        check("3.3 V" in rc, "numeric spec preserved")
        check("CCITT" in branch_files[0].read_text(), "edited variant content preserved")
        idx = (out / "INDEX.md").read_text()
        check("raw_dat_attachments/photo.dat" in idx, "INDEX.md inventories binary .dat")
        check((out / RUN_DIR / "manifest.json").exists(), "manifest written")
        # determinism: rebuild and compare tree hashes
        def tree_hash(base: Path) -> str:
            h = hashlib.sha256()
            for p in sorted(base.rglob("*")):
                if p.is_file() and RUN_DIR not in p.parts:
                    h.update(p.relative_to(base).as_posix().encode())
                    h.update(sha256_file(p).encode())
            return h.hexdigest()
        out2 = Path(td) / "out2"
        build(src, out2)
        check(tree_hash(out) == tree_hash(out2), "build is deterministic")

    print("\nSELF-TEST:", "ALL PASS" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


def make_zip(out: Path) -> Path:
    """Package the archive as <out>.zip, excluding the .run state dir."""
    import zipfile
    zip_path = out.parent / f"{out.name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(out.rglob("*")):
            if p.is_file() and RUN_DIR not in p.parts:
                zf.write(p, p.relative_to(out.parent).as_posix())
    return zip_path


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="workspace to scan")
    ap.add_argument("--out", default="refined-chat-archive", help="output directory")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--zip", dest="zip", action="store_true", default=True,
                    help="also write <out>.zip (default: true)")
    ap.add_argument("--no-zip", dest="zip", action="store_false")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    root = Path(args.root).resolve()
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    manifest = build(root, out)
    st = manifest["stats"]
    zp = make_zip(out) if args.zip else None
    print(json.dumps({"stats": st, "warnings": len(manifest["warnings"]),
                      "zip": str(zp) if zp else None,
                      "zip_bytes": zp.stat().st_size if zp else 0}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
