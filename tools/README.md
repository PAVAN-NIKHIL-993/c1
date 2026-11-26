# ChatGPT Export → Refined Archive Pipeline

`tools/build_archive.py` turns a ChatGPT data export (plus any stray `.dat`
files) into `refined-chat-archive/` — a topic-chained folder tree with one
`refined_chat.txt` per conversation.

## Run

```bash
# put the export anywhere inside the repo (subdirectories are scanned), e.g.
#   ./export/conversations.json  ./export/user.json  ./export/chat.html  ./misc/photo.dat

python3 tools/build_archive.py --root . --out refined-chat-archive
python3 tools/build_archive.py --self-test     # 20 assertions, synthetic fixtures
```

Outputs: `refined-chat-archive/INDEX.md`, one `refined_chat.txt` per
conversation, `refined-chat-archive/raw_dat_attachments/` (byte-exact copies of
binary `.dat` files), `refined-chat-archive/.run/manifest.json` (machine-readable
run state), and `refined-chat-archive.zip`.

## What it guarantees

| Requirement | How it is met |
|---|---|
| `.dat` classified by content | UTF-8 + JSON with chat structure → parsed as JSON; valid UTF-8 text → parsed as a conversation log (`USER:` / `Assistant:` blocks, inline or standalone); non-UTF-8 or control-heavy bytes → copied untouched to `raw_dat_attachments/` with SHA-256 + MD5 in `INDEX.md`. |
| Zero omission | The export's `mapping` is a graph. The `current_node` ancestry is written as the main transcript; **every other root→leaf path** (edited messages, regenerated responses) is written to `<conversation>/branches/branch_NN.txt`. Nothing is truncated or sampled. |
| `.dat` inventory | Every binary `.dat` gets original name, size, sniffed MIME, MD5, SHA-256, and a link to the conversation that references it. |
| Topic chaining | Conversations are sorted chronologically, then each is nested under the most recent earlier conversation with sufficient token overlap (title + first user prompt, Jaccard ≥ 0.34, lookahead 4). Unrelated chats stay top-level. |
| Deterministic | No randomness, no LLM summarisation, no network. Rebuilding from the same bytes yields a byte-identical tree (asserted in `--self-test`). |
| Count reconciliation | `parsed_raw − duplicates == processed == refined_chat.txt files on disk`, printed in `INDEX.md §2`. |

## Section layout of each `refined_chat.txt`

- **A — Consolidated User Questions**: all user prompts in order, one paragraph.
- **B — Summary & Suggestions**: turn-by-turn progression, extracted technical
  inventory (code fences, commands, links, numeric specs), and next steps.
- **C — Complete Pin-to-Pin Refined Transcript**: every turn, verbatim, with
  timestamp/model attribution in HTML comments so the text stays copy-ready.

## Scope note

Section B is *extractive* (derived from the transcript), not an LLM paraphrase,
precisely so the pipeline stays deterministic and re-runnable offline. Section C
is the authoritative record: nothing there is summarised.
