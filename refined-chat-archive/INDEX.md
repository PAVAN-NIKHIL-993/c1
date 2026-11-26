# Refined ChatGPT Archive — Master Index

Generated: 2026-11-26 10:42:10 UTC

Pipeline: `tools/build_archive.py` (deterministic; no message was summarised away — Section C of every `refined_chat.txt` is the verbatim transcript).

## 1. Source inventory

| # | File | Classified as | Size | SHA-256 (first 16) | Note |
|---|------|---------------|------|--------------------|------|

### Counts by class

| Class | Count |
|-------|-------|

## 2. Conversation counts

- Conversation records parsed from sources (raw): **0**
- Duplicate copies collapsed: **0**
- Unique conversations found: **0**
- Conversations processed and written: **0**
- `refined_chat.txt` files on disk: **0**
- Alternate branch transcripts preserved: **0**
- Binary `.dat` files preserved: **0**
- Accounting reconciles (parsed − duplicates = written = on disk): **YES**

## 3. Folder tree

```text
refined-chat-archive/
```

## 4. Chronological sequence & topic chains

| # | Date | Conversation | Folder | Chain | Source type | Turns |
|---|------|--------------|--------|-------|-------------|-------|

## 5. Binary / media `.dat` inventory

_No binary or media `.dat` files were found in the workspace._

## 6. Integrity manifest

| File | SHA-256 | Bytes |
|------|---------|-------|

## 7. Notes on method

- `.dat` files were classified by content, never by extension: UTF-8+JSON with chat structure → parsed as JSON; valid UTF-8 text → parsed as a conversation log; non-UTF-8 or control-heavy bytes → copied byte-for-byte into `raw_dat_attachments/`.
- Conversation graphs were traversed exhaustively: the active thread (`current_node` ancestry) is the main transcript, and every other root→leaf path is written to `<conversation>/branches/` so edited and regenerated turns survive.
- Folder nesting is computed from topic similarity between consecutive conversations (title + first user prompt), so a debugging follow-up lands inside the project folder it belongs to instead of beside it.
