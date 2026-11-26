# Refined ChatGPT Archive — Master Index

Generated: 2026-11-26 10:51:26 UTC

## ⚠️ Read this first: no conversation transcripts were present

The 81 `.dat` files uploaded to this repository were classified by **content**, not by extension. All 81 resolve to **attachment blobs** — source code, images, audio, PDFs and reference text — of the kind a ChatGPT export keeps in its `files/` directory.

None of them is a conversation export. Verified by direct inspection:

| Test | Result |
|---|---|
| `"mapping"` / `"current_node"` / `"conversation_id"` keys present | **0 of 81 files** |
| Role-tagged dialogue headers (`USER:` / `ASSISTANT:`) | **0 of 81 files** |
| Top-level JSON array of conversations | **0 files** (the single JSON file is `package.json`) |
| Any recoverable multi-turn dialogue | **0 conversations** |

So the sequence of Section-A/B/C `refined_chat.txt` files described in the brief **cannot be produced from this upload** — there is no turn data to reconstruct. Fabricating transcripts or summaries here would be inventing history, so instead everything that *is* present has been classified, hashed, topic-chained and archived byte-exactly, and the one file containing the user's own prompt wording has been mined for those fragments.

To complete the original request, upload the export's `conversations.json` (or the whole export `.zip`, which contains `conversations.json` + `files/`). `tools/build_archive.py` will then produce the full A/B/C archive; it is already implemented and self-tested against that exact format.

---

## 1. Source inventory — 81 `.dat` files, classified by content

| Class | Count | Meaning |
|-------|-------|---------|
| UTF-8 text (source/reference) | **31** | decoded and catalogued; verbatim copy kept |
| UTF-8 JSON (not chat data) | **1** | `package.json`, no conversation structure |
| Binary / media | **49** | copied byte-for-byte to `raw_dat_attachments/` |
| **Total** | **81** | |

- Distinct content hashes: **76** (from 81 files → **5 byte-identical duplicate groups**)
- Media breakdown: `image/png` × 46, `audio/mpeg` × 2, `application/pdf` × 1
- Detected text formats: `cpp` × 10, `csv` × 6, `typescript-react` × 6, `javascript` × 4, `html` × 2, `css` × 1, `json` × 1, `plain-text` × 1, `typescript` × 1

### Duplicate groups (identical bytes, different filenames)

| Kept as | Byte-identical copy |
|---------|---------------------|
| `file-6Q2GXQKE35YioBr15RHDSp.dat` | `file-DnLtXXWkzehXdF1kEq6us5.dat` |
| `file_0000000014b471fab837411d781f4bce.dat` | `file_00000000bca871fdb6f7449f7e555f7e.dat` |
| `file_00000000204071fda49994955f8fbc3e.dat` | `file_00000000337871fdaea33af922aacad5.dat` |
| `file_00000000297c71fab4e12fa3b53d65c4.dat` | `file_000000004ac871fa85315bf42ca90341.dat` |
| `file_00000000ba9c71f59064540caf45ecb9.dat` | `file_00000000dff871fba2ae871b935aac57.dat` |

## 2. Topic chains

Artifacts were grouped with the same topic-chaining logic used for conversations (keyword domain scoring), because with no timestamps the content domain is the only honest organising signal.

| Topic chain | Artifacts |
|-------------|-----------|
| `media-attachments` | 49 |
| `software-frontend` | 12 |
| `hardware-esp32` | 8 |
| `hardware-bio-sensing` | 6 |
| `system-config` | 3 |
| `hardware-water-sensing` | 1 |
| `hardware-eda-kicad` | 1 |
| `hardware-lcr-meter` | 1 |

## 3. Folder tree

```text
refined-chat-archive/
├── INDEX.md                      ← this file
├── artifacts/                    ← decoded text artifacts, one folder each
│   ├── hardware-bio-sensing/
│   │   ├── cpp__max30102/
│   │   ├── cpp__max30105/
│   │   ├── cpp__max30105-2/
│   │   ├── html__max30102/
│   │   ├── typescript-react__max30102/
│   │   └── typescript__max30102/
│   ├── hardware-eda-kicad/
│   │   └── plain-text__kicad-shortcuts/
│   ├── hardware-esp32/
│   │   ├── cpp__cd74hc4067-mux/
│   │   ├── cpp__cd74hc4067-mux-2/
│   │   ├── cpp__cd74hc4067-mux-3/
│   │   ├── cpp__cd74hc4067-mux-4/
│   │   ├── cpp__esp32-adc-raw-adc-chars/
│   │   ├── cpp__helix-mp3-decoder/
│   │   ├── cpp__max30102/
│   │   └── csv__pasted-prompts/
│   ├── hardware-lcr-meter/
│   │   └── html__irlz44n-mosfet/
│   ├── hardware-water-sensing/
│   │   └── csv__flood-leak-detectors/
│   ├── software-frontend/
│   │   ├── css__tailwind/
│   │   ├── csv__es2020-config/
│   │   ├── javascript__classvalue/
│   │   ├── javascript__framer-motion/
│   │   ├── javascript__framer-motion-2/
│   │   ├── javascript__tailwind/
│   │   ├── json__tailwind/
│   │   ├── typescript-react__monitorheaderprops-monitorheader/
│   │   ├── typescript-react__strictmode/
│   │   ├── typescript-react__vertical-line-arrowheads/
│   │   ├── typescript-react__vitalsignprops-vitalsign/
│   │   └── typescript-react__waveformcanvasprops-waveformcanvas/
│   ├── system-config/
│   │   ├── csv__droidcam-devices/
│   │   ├── csv__droidcam-devices-2/
│   │   └── csv__kicad-shortcuts/
├── raw_dat_attachments/          ← 49 binary blobs, byte-exact
├── recoverable-fragments/        ← user-authored prompt wording
└── .run/                         ← machine-readable manifest
```

## 4. Complete artifact inventory

| # | Original file | Class | Format / MIME | Size | SHA-256 (16) | Dupe of | Location |
|---|---------------|-------|---------------|------|--------------|---------|----------|
| 1 | `file-6Q2GXQKE35YioBr15RHDSp.dat` | dat-text | cpp | 3.4 KB | `527e18ed43c46f25` | `file-DnLtXXWkzehXdF1kEq6us5.dat` | `artifacts/hardware-bio-sensing/cpp__max30105/content.txt` |
| 2 | `file-DnLtXXWkzehXdF1kEq6us5.dat` | dat-text | cpp | 3.4 KB | `527e18ed43c46f25` | `file-6Q2GXQKE35YioBr15RHDSp.dat` | `artifacts/hardware-bio-sensing/cpp__max30105-2/content.txt` |
| 3 | `file_0000000028b072088ec2bde51f6d5988.dat` | dat-text | html | 311 B | `77db5033e456aba2` | — | `artifacts/hardware-bio-sensing/html__max30102/content.txt` |
| 4 | `file_0000000035607207abf4e82256a30dab.dat` | dat-text | cpp | 11.6 KB | `2f6535160aa2aa56` | — | `artifacts/hardware-bio-sensing/cpp__max30102/content.txt` |
| 5 | `file_0000000073fc7208acb16b174761c059.dat` | dat-text | typescript-react | 17.6 KB | `432640e0db8d8d2d` | — | `artifacts/hardware-bio-sensing/typescript-react__max30102/content.txt` |
| 6 | `file_00000000db4c720881004debf82fa52b.dat` | dat-text | typescript | 5.4 KB | `5ccd46723327e75c` | — | `artifacts/hardware-bio-sensing/typescript__max30102/content.txt` |
| 7 | `file_000000008e1482118d3f7bbe0b28e9a4.dat` | dat-text | plain-text | 16.8 KB | `2b748dfc119eb978` | — | `artifacts/hardware-eda-kicad/plain-text__kicad-shortcuts/content.txt` |
| 8 | `file-NuAD51C94MemxsqfLtzFHb.dat` | dat-text | cpp | 4.1 KB | `825a8efed89cdcca` | — | `artifacts/hardware-esp32/cpp__esp32-adc-raw-adc-chars/content.txt` |
| 9 | `file_000000001f8472078b8fb8c0424fb462.dat` | dat-text | cpp | 13.0 KB | `ced867e9ae97d02f` | — | `artifacts/hardware-esp32/cpp__max30102/content.txt` |
| 10 | `file_00000000262c720ba55acb00183b2d2f.dat` | dat-text | cpp | 16.5 KB | `beda7d1494f302df` | — | `artifacts/hardware-esp32/cpp__cd74hc4067-mux/content.txt` |
| 11 | `file_00000000758c71f899c2d686ea413a5a.dat` | dat-text | cpp | 11.6 KB | `e8190d892458b8cf` | — | `artifacts/hardware-esp32/cpp__cd74hc4067-mux-2/content.txt` |
| 12 | `file_00000000795071f8984705f7b403e869.dat` | dat-text | cpp | 15.0 KB | `518ffff9d6acc856` | — | `artifacts/hardware-esp32/cpp__cd74hc4067-mux-3/content.txt` |
| 13 | `file_000000009a7c71fa941dd455c7620aaa.dat` | dat-text | cpp | 5.1 KB | `3a0a036bc3c004e2` | — | `artifacts/hardware-esp32/cpp__helix-mp3-decoder/content.txt` |
| 14 | `file_00000000df1871fa8397b77aafee2a6f.dat` | dat-text | cpp | 11.7 KB | `c41392dda4744433` | — | `artifacts/hardware-esp32/cpp__cd74hc4067-mux-4/content.txt` |
| 15 | `file_00000000dfb871fab99ac17eed2f9519.dat` | dat-text | csv | 11.1 KB | `1ab972ed9d86bf09` | — | `artifacts/hardware-esp32/csv__pasted-prompts/content.txt` |
| 16 | `file_00000000b2887207be39704366d0b9e0.dat` | dat-text | html | 2.6 KB | `b6c1edfc8a385e16` | — | `artifacts/hardware-lcr-meter/html__irlz44n-mosfet/content.txt` |
| 17 | `file_0000000036dc72088d101e6dce4e43d7.dat` | dat-text | csv | 12.5 KB | `15b1acfffc621977` | — | `artifacts/hardware-water-sensing/csv__flood-leak-detectors/content.txt` |
| 18 | `file-BTNC68MBF7ihGaQrAo7Mso.dat` | dat-binary | MP3 audio | 19.5 KB | `6601213aa6fb9ae1` | — | `raw_dat_attachments/file-BTNC68MBF7ihGaQrAo7Mso.dat` |
| 19 | `file-Wty5S6JrcWZtHKvCD5SZAJ.dat` | dat-binary | MP3 audio | 16.5 KB | `173d004904c95b1a` | — | `raw_dat_attachments/file-Wty5S6JrcWZtHKvCD5SZAJ.dat` |
| 20 | `file_0000000000347207b0e1a190cb9d4441.dat` | dat-binary | PNG image | 12.3 KB | `441d6aeef18e1acc` | — | `raw_dat_attachments/file_0000000000347207b0e1a190cb9d4441.dat` |
| 21 | `file_000000000130720bb574b8e6096340d3.dat` | dat-binary | PNG image | 9.5 KB | `ba112eb81a1f169d` | — | `raw_dat_attachments/file_000000000130720bb574b8e6096340d3.dat` |
| 22 | `file_00000000099071fa8e84555cad438a2d.dat` | dat-binary | PNG image | 3.0 KB | `81e5e4cb705886f3` | — | `raw_dat_attachments/file_00000000099071fa8e84555cad438a2d.dat` |
| 23 | `file_0000000015c8720b87a63fa9ad90332a.dat` | dat-binary | PNG image | 10.0 KB | `bd294993989a8b3c` | — | `raw_dat_attachments/file_0000000015c8720b87a63fa9ad90332a.dat` |
| 24 | `file_00000000197471fab39a5df9f51412bd.dat` | dat-binary | PNG image | 8.5 KB | `5f5ca3d6c45ff9af` | — | `raw_dat_attachments/file_00000000197471fab39a5df9f51412bd.dat` |
| 25 | `file_000000001a3472098f1ec512ca92d9d2.dat` | dat-binary | PNG image | 19.3 KB | `667a7d7907c52e0a` | — | `raw_dat_attachments/file_000000001a3472098f1ec512ca92d9d2.dat` |
| 26 | `file_000000001bac7207adff0cb9f2a2f87d.dat` | dat-binary | PNG image | 14.1 KB | `a38f5c062aaa1bb7` | — | `raw_dat_attachments/file_000000001bac7207adff0cb9f2a2f87d.dat` |
| 27 | `file_000000001f0872079578f4778500bc5e.dat` | dat-binary | PNG image | 14.7 KB | `8e95a2c2b83ace62` | — | `raw_dat_attachments/file_000000001f0872079578f4778500bc5e.dat` |
| 28 | `file_00000000204071fda49994955f8fbc3e.dat` | dat-binary | PNG image | 17.3 KB | `aee1a24e384bbd42` | `file_00000000337871fdaea33af922aacad5.dat` | `raw_dat_attachments/file_00000000204071fda49994955f8fbc3e.dat` |
| 29 | `file_00000000297c71fab4e12fa3b53d65c4.dat` | dat-binary | PNG image | 14.5 KB | `0be91fdcd37e7b25` | `file_000000004ac871fa85315bf42ca90341.dat` | `raw_dat_attachments/file_00000000297c71fab4e12fa3b53d65c4.dat` |
| 30 | `file_000000002b947209b7f3d39209933beb.dat` | dat-binary | PNG image | 19.0 KB | `9860412e4993ff4f` | — | `raw_dat_attachments/file_000000002b947209b7f3d39209933beb.dat` |
| 31 | `file_0000000032b47207998a59984135d8a0.dat` | dat-binary | PNG image | 6.4 KB | `458424e072a70f24` | — | `raw_dat_attachments/file_0000000032b47207998a59984135d8a0.dat` |
| 32 | `file_00000000337871fdaea33af922aacad5.dat` | dat-binary | PNG image | 17.3 KB | `aee1a24e384bbd42` | `file_00000000204071fda49994955f8fbc3e.dat` | `raw_dat_attachments/file_00000000337871fdaea33af922aacad5.dat` |
| 33 | `file_0000000039c872078f0d7682f33863a4.dat` | dat-binary | PNG image | 11.2 KB | `a7225f5c3a2f164f` | — | `raw_dat_attachments/file_0000000039c872078f0d7682f33863a4.dat` |
| 34 | `file_000000003c1072089e432122fc5cb4ef.dat` | dat-binary | PNG image | 7.0 KB | `e8a161eee7f1732d` | — | `raw_dat_attachments/file_000000003c1072089e432122fc5cb4ef.dat` |
| 35 | `file_000000004ac871fa85315bf42ca90341.dat` | dat-binary | PNG image | 14.5 KB | `0be91fdcd37e7b25` | `file_00000000297c71fab4e12fa3b53d65c4.dat` | `raw_dat_attachments/file_000000004ac871fa85315bf42ca90341.dat` |
| 36 | `file_000000004b5c71f5b06d6762e9b4ba0f.dat` | dat-binary | PNG image | 6.0 KB | `f34dd1bc7d032c17` | — | `raw_dat_attachments/file_000000004b5c71f5b06d6762e9b4ba0f.dat` |
| 37 | `file_000000004f147208b5eb0b1b8c55c587.dat` | dat-binary | PNG image | 4.9 KB | `abf5993795a90646` | — | `raw_dat_attachments/file_000000004f147208b5eb0b1b8c55c587.dat` |
| 38 | `file_0000000058f47206a1a725ab77e0488a.dat` | dat-binary | PNG image | 19.1 KB | `3b54f12d494fca4c` | — | `raw_dat_attachments/file_0000000058f47206a1a725ab77e0488a.dat` |
| 39 | `file_000000005da871fa9a139cddf5a23c22.dat` | dat-binary | PNG image | 10.7 KB | `fd0acf1829508657` | — | `raw_dat_attachments/file_000000005da871fa9a139cddf5a23c22.dat` |
| 40 | `file_000000006ddc71fa823431db2976cc14.dat` | dat-binary | PNG image | 2.7 KB | `a08a555098262707` | — | `raw_dat_attachments/file_000000006ddc71fa823431db2976cc14.dat` |
| 41 | `file_000000007880720885662fb2f586ed31.dat` | dat-binary | PNG image | 14.6 KB | `1e8e8dc75defba38` | — | `raw_dat_attachments/file_000000007880720885662fb2f586ed31.dat` |
| 42 | `file_0000000079e87207af41f7254640687c.dat` | dat-binary | PNG image | 2.6 KB | `2b39e77613ae33a7` | — | `raw_dat_attachments/file_0000000079e87207af41f7254640687c.dat` |
| 43 | `file_000000007fc47207a0e56067530752a0.dat` | dat-binary | PNG image | 19.4 KB | `9708679fbd659464` | — | `raw_dat_attachments/file_000000007fc47207a0e56067530752a0.dat` |
| 44 | `file_00000000853c71f7a2b2cdeac3e53678.dat` | dat-binary | PNG image | 10.8 KB | `9d30030d0e047283` | — | `raw_dat_attachments/file_00000000853c71f7a2b2cdeac3e53678.dat` |
| 45 | `file_000000008aa471fa9ab44c811b757d16.dat` | dat-binary | PDF document | 16.7 KB | `97a637a39883dc2b` | — | `raw_dat_attachments/file_000000008aa471fa9ab44c811b757d16.dat` |
| 46 | `file_00000000907471fbaa77009b37838e67.dat` | dat-binary | PNG image | 5.2 KB | `029ede70ba86f912` | — | `raw_dat_attachments/file_00000000907471fbaa77009b37838e67.dat` |
| 47 | `file_00000000a23c71fb89240da7d94e2837.dat` | dat-binary | PNG image | 3.8 KB | `08d4e7d201810053` | — | `raw_dat_attachments/file_00000000a23c71fb89240da7d94e2837.dat` |
| 48 | `file_00000000aeb87209a92172ab42916335.dat` | dat-binary | PNG image | 3.6 KB | `f61c0ea321255673` | — | `raw_dat_attachments/file_00000000aeb87209a92172ab42916335.dat` |
| 49 | `file_00000000b39471fa9415940412006e20.dat` | dat-binary | PNG image | 8.4 KB | `a8fa16f14890b46c` | — | `raw_dat_attachments/file_00000000b39471fa9415940412006e20.dat` |
| 50 | `file_00000000b89c71f7b3347083d93eb62b.dat` | dat-binary | PNG image | 10.8 KB | `4def3d3c3db15f70` | — | `raw_dat_attachments/file_00000000b89c71f7b3347083d93eb62b.dat` |
| 51 | `file_00000000b8f87208852a10f381b0c29d.dat` | dat-binary | PNG image | 19.0 KB | `6729de42a6d8920e` | — | `raw_dat_attachments/file_00000000b8f87208852a10f381b0c29d.dat` |
| 52 | `file_00000000ba9c71f59064540caf45ecb9.dat` | dat-binary | PNG image | 9.1 KB | `6d663009dbca5057` | `file_00000000dff871fba2ae871b935aac57.dat` | `raw_dat_attachments/file_00000000ba9c71f59064540caf45ecb9.dat` |
| 53 | `file_00000000bb847207925deda7dd751c47.dat` | dat-binary | PNG image | 15.6 KB | `93f7c1ed0829ed62` | — | `raw_dat_attachments/file_00000000bb847207925deda7dd751c47.dat` |
| 54 | `file_00000000c95871f59d29f8a145504628.dat` | dat-binary | PNG image | 14.0 KB | `37fc1baea15c0e8c` | — | `raw_dat_attachments/file_00000000c95871f59d29f8a145504628.dat` |
| 55 | `file_00000000c9a07208b0979b212678424f.dat` | dat-binary | PNG image | 9.5 KB | `a21f52d6a7b19f51` | — | `raw_dat_attachments/file_00000000c9a07208b0979b212678424f.dat` |
| 56 | `file_00000000cfac72098c23519d9e32a139.dat` | dat-binary | PNG image | 19.7 KB | `c1f3565df72bf266` | — | `raw_dat_attachments/file_00000000cfac72098c23519d9e32a139.dat` |
| 57 | `file_00000000d3c871fa829429cd9350c959.dat` | dat-binary | PNG image | 3.3 KB | `1db4eefd4011472d` | — | `raw_dat_attachments/file_00000000d3c871fa829429cd9350c959.dat` |
| 58 | `file_00000000d67c71faa769706c518210cb.dat` | dat-binary | PNG image | 10.4 KB | `7ae965678de1f234` | — | `raw_dat_attachments/file_00000000d67c71faa769706c518210cb.dat` |
| 59 | `file_00000000d9b072078de141fc1e2271b0.dat` | dat-binary | PNG image | 13.0 KB | `860d9322db14d4c5` | — | `raw_dat_attachments/file_00000000d9b072078de141fc1e2271b0.dat` |
| 60 | `file_00000000dff871fba2ae871b935aac57.dat` | dat-binary | PNG image | 9.1 KB | `6d663009dbca5057` | `file_00000000ba9c71f59064540caf45ecb9.dat` | `raw_dat_attachments/file_00000000dff871fba2ae871b935aac57.dat` |
| 61 | `file_00000000e07071f58f7678144f422f01.dat` | dat-binary | PNG image | 3.0 KB | `169bdd65875d8424` | — | `raw_dat_attachments/file_00000000e07071f58f7678144f422f01.dat` |
| 62 | `file_00000000e17871f592626e2ff7b7163f.dat` | dat-binary | PNG image | 4.7 KB | `8d6317eabcfa43bb` | — | `raw_dat_attachments/file_00000000e17871f592626e2ff7b7163f.dat` |
| 63 | `file_00000000f37071fab1b739168b64e1ce.dat` | dat-binary | PNG image | 19.4 KB | `b41da78151c7c18a` | — | `raw_dat_attachments/file_00000000f37071fab1b739168b64e1ce.dat` |
| 64 | `file_00000000f38c71fabe34737eef7f08cd.dat` | dat-binary | PNG image | 19.3 KB | `19d895ae4753aa0f` | — | `raw_dat_attachments/file_00000000f38c71fabe34737eef7f08cd.dat` |
| 65 | `file_00000000f9ec7206a53f3a4740ed1b43.dat` | dat-binary | PNG image | 17.9 KB | `2043495036b93b05` | — | `raw_dat_attachments/file_00000000f9ec7206a53f3a4740ed1b43.dat` |
| 66 | `file_00000000fca47207a07e319ce098a83f.dat` | dat-binary | PNG image | 9.7 KB | `8a9391843c2b26be` | — | `raw_dat_attachments/file_00000000fca47207a07e319ce098a83f.dat` |
| 67 | `file_0000000002187208a4fb90df01c97c87.dat` | dat-text | csv | 681 B | `2a760f56fa49b969` | — | `artifacts/software-frontend/csv__es2020-config/content.txt` |
| 68 | `file_00000000122c7208abbd0c734f8f606d.dat` | dat-text | css | 341 B | `1ccd6fa79f38ac38` | — | `artifacts/software-frontend/css__tailwind/content.txt` |
| 69 | `file_0000000018e8720896e23d20ee0186f5.dat` | dat-text | typescript-react | 1.9 KB | `260ef2bd842606d0` | — | `artifacts/software-frontend/typescript-react__monitorheaderprops-monitorheader/content.txt` |
| 70 | `file_0000000024b47208a6ee14f9719edeb5.dat` | dat-text | typescript-react | 8.0 KB | `619bbf26396136ec` | — | `artifacts/software-frontend/typescript-react__vertical-line-arrowheads/content.txt` |
| 71 | `file_0000000026d472088ad3a058f552482f.dat` | dat-text | javascript | 538 B | `18dd184b9091357f` | — | `artifacts/software-frontend/javascript__tailwind/content.txt` |
| 72 | `file_0000000032cc720889b390ec8afdf038.dat` | dat-json | json | 628 B | `e5eee82c2d420011` | — | `artifacts/software-frontend/json__tailwind/content.txt` |
| 73 | `file_0000000043707208b19912d30e2f0fa9.dat` | dat-text | typescript-react | 230 B | `f268dc44f7124001` | — | `artifacts/software-frontend/typescript-react__strictmode/content.txt` |
| 74 | `file_000000005c0c72089e77332b60c4ead4.dat` | dat-text | typescript-react | 3.5 KB | `007428af7b52270e` | — | `artifacts/software-frontend/typescript-react__waveformcanvasprops-waveformcanvas/content.txt` |
| 75 | `file_0000000099b87208ade502ff8f51c965.dat` | dat-text | javascript | 10.4 KB | `b82c326543187989` | — | `artifacts/software-frontend/javascript__framer-motion/content.txt` |
| 76 | `file_00000000bbb07208affa330d6e06279f.dat` | dat-text | typescript-react | 1.7 KB | `ed36c07db983cb86` | — | `artifacts/software-frontend/typescript-react__vitalsignprops-vitalsign/content.txt` |
| 77 | `file_00000000cc5871f89a46cd470d45f0fe.dat` | dat-text | javascript | 5.6 KB | `65c6ed89c7bc34d0` | — | `artifacts/software-frontend/javascript__framer-motion-2/content.txt` |
| 78 | `file_00000000fbac72089099b52aecf5a842.dat` | dat-text | javascript | 169 B | `d1f1e0d62cb8d8d1` | — | `artifacts/software-frontend/javascript__classvalue/content.txt` |
| 79 | `file_0000000014b471fab837411d781f4bce.dat` | dat-text | csv | 11.1 KB | `0cd2dc0889a61e4d` | `file_00000000bca871fdb6f7449f7e555f7e.dat` | `artifacts/system-config/csv__droidcam-devices/content.txt` |
| 80 | `file_0000000095d08208bdb18cbff042a2b3.dat` | dat-text | csv | 16.4 KB | `6052d2e045fa3268` | — | `artifacts/system-config/csv__kicad-shortcuts/content.txt` |
| 81 | `file_00000000bca871fdb6f7449f7e555f7e.dat` | dat-text | csv | 11.1 KB | `0cd2dc0889a61e4d` | `file_0000000014b471fab837411d781f4bce.dat` | `artifacts/system-config/csv__droidcam-devices-2/content.txt` |

## 5. Text artifacts — full checksums

| File | Format | Chars | Lines | Tokens | SHA-256 |
|------|--------|-------|-------|--------|---------|
| `file-6Q2GXQKE35YioBr15RHDSp.dat` | `cpp` | 3485 | 175 | 505 | `527e18ed43c46f25852e04fb5ce9c6c881687406aa53e24f8b69b2e50f8b0625` |
| `file-DnLtXXWkzehXdF1kEq6us5.dat` | `cpp` | 3485 | 175 | 505 | `527e18ed43c46f25852e04fb5ce9c6c881687406aa53e24f8b69b2e50f8b0625` |
| `file_0000000028b072088ec2bde51f6d5988.dat` | `html` | 311 | 13 | 25 | `77db5033e456aba264614d0f85d9c63d23929e327b1fa4390b05aa484edd4354` |
| `file_0000000035607207abf4e82256a30dab.dat` | `cpp` | 11895 | 530 | 1111 | `2f6535160aa2aa56cb71b214021f9a7f826990051d9f95e98aeb1487451ea271` |
| `file_0000000073fc7208acb16b174761c059.dat` | `typescript-react` | 17605 | 491 | 1715 | `432640e0db8d8d2d6607f06d318d30bfc1018dd361e064d61f46503b178fc311` |
| `file_00000000db4c720881004debf82fa52b.dat` | `typescript` | 5514 | 186 | 823 | `5ccd46723327e75cd2fb9d9b52635e5a144ea016ae197473412e4f5f5788171a` |
| `file_000000008e1482118d3f7bbe0b28e9a4.dat` | `plain-text` | 17243 | 199 | 1653 | `2b748dfc119eb9780b9c5538d84d0b43d1dc9ec50ef05666f8016bf445524351` |
| `file-NuAD51C94MemxsqfLtzFHb.dat` | `cpp` | 4043 | 144 | 445 | `825a8efed89cdcca3f8a8ce33698aa32723da92df39d861b98ad35adca7cdd49` |
| `file_000000001f8472078b8fb8c0424fb462.dat` | `cpp` | 13258 | 584 | 1231 | `ced867e9ae97d02f579e7c420320ecbb8f916dbc1876c9cb0dc4bfb91f7f2aa4` |
| `file_00000000262c720ba55acb00183b2d2f.dat` | `cpp` | 16880 | 813 | 1437 | `beda7d1494f302df64da2713a76a9836c0a7ce29e0acb2fcd8fc2e190ae254ef` |
| `file_00000000758c71f899c2d686ea413a5a.dat` | `cpp` | 11921 | 570 | 1033 | `e8190d892458b8cff0e7eaedf6478f365a6575d3518edeb09223f06c5f9657fc` |
| `file_00000000795071f8984705f7b403e869.dat` | `cpp` | 15309 | 697 | 1216 | `518ffff9d6acc856c1d55a1607e79710e48e0c6babd876d72be194764494cfff` |
| `file_000000009a7c71fa941dd455c7620aaa.dat` | `cpp` | 5215 | 169 | 573 | `3a0a036bc3c004e24b706a8d10c31e39d9948e22fccff6a4ee9cfd9eb8591f0a` |
| `file_00000000df1871fa8397b77aafee2a6f.dat` | `cpp` | 11950 | 572 | 1035 | `c41392dda474443371d84e51b8cbeb30393aaece76d69a925cdfb95a8c72c486` |
| `file_00000000dfb871fab99ac17eed2f9519.dat` | `csv` | 11335 | 607 | 1316 | `1ab972ed9d86bf094bfbe9148b345d9672763388666a7f748f3599bbc414f666` |
| `file_00000000b2887207be39704366d0b9e0.dat` | `html` | 2668 | 74 | 280 | `b6c1edfc8a385e162ca5e7b16539517758a39d46692ce032a4e40e33a8f5e56a` |
| `file_0000000036dc72088d101e6dce4e43d7.dat` | `csv` | 12728 | 367 | 1843 | `15b1acfffc62197799ea82b205f58a840b5707894aa560f65db2428fb63eb669` |
| `file_0000000002187208a4fb90df01c97c87.dat` | `csv` | 681 | 32 | 60 | `2a760f56fa49b96935783a2c3b4ce63d67e4547fdace88c4f4361a0c4fc10848` |
| `file_00000000122c7208abbd0c734f8f606d.dat` | `css` | 341 | 25 | 43 | `1ccd6fa79f38ac3819b227cd41f25e9013c8bf0da188c2508eccf01e477ac719` |
| `file_0000000018e8720896e23d20ee0186f5.dat` | `typescript-react` | 1991 | 67 | 189 | `260ef2bd842606d05a2f61959feebf4fcad6e2c5a12d6acc20d01c3914e1d127` |
| `file_0000000024b47208a6ee14f9719edeb5.dat` | `typescript-react` | 8227 | 285 | 1050 | `619bbf26396136ec8426fe96791b22ef93cf40a8a72918ef3c96af380f470934` |
| `file_0000000026d472088ad3a058f552482f.dat` | `javascript` | 538 | 20 | 57 | `18dd184b9091357fe23797ee047138e6af7663b59697ac45d6c3c219522db9fa` |
| `file_0000000032cc720889b390ec8afdf038.dat` | `json` | 628 | 29 | 53 | `e5eee82c2d420011873a703941c578682b447e3bd33a516031d02e36f4e9d530` |
| `file_0000000043707208b19912d30e2f0fa9.dat` | `typescript-react` | 230 | 11 | 24 | `f268dc44f71240012de0cfb1569d8ac906265cccd45eb3a99059c1a663d2f830` |
| `file_000000005c0c72089e77332b60c4ead4.dat` | `typescript-react` | 3626 | 146 | 437 | `007428af7b52270ee7da6a1b7771e0f1f3b47af17a4876b9a3e321a1b8a6fd25` |
| `file_0000000099b87208ade502ff8f51c965.dat` | `javascript` | 10659 | 590 | 764 | `b82c32654318798988eeaf9d013e5e4d79d099a112ff7fdf835c712bb5778ba2` |
| `file_00000000bbb07208affa330d6e06279f.dat` | `typescript-react` | 1734 | 77 | 177 | `ed36c07db983cb8646dbe01931aac719154784f7357c3d1e5375269a89afcf09` |
| `file_00000000cc5871f89a46cd470d45f0fe.dat` | `javascript` | 5706 | 208 | 282 | `65c6ed89c7bc34d09dfd523fc6baf53edd7da0c6b74e9b2e09a09ba516cde532` |
| `file_00000000fbac72089099b52aecf5a842.dat` | `javascript` | 169 | 7 | 22 | `d1f1e0d62cb8d8d1e04c26e14de842d8a151f75812d81b046c65b5d1fe8e4b27` |
| `file_0000000014b471fab837411d781f4bce.dat` | `csv` | 11365 | 36 | 543 | `0cd2dc0889a61e4d1cf21c816c6f6caed76b9dcf1dc9708df52dff5545b2cc26` |
| `file_0000000095d08208bdb18cbff042a2b3.dat` | `csv` | 16604 | 202 | 1093 | `6052d2e045fa3268b8d6fba35af1769f1dc547dda77463a977f2c57bb8df7409` |
| `file_00000000bca871fdb6f7449f7e555f7e.dat` | `csv` | 11365 | 36 | 543 | `0cd2dc0889a61e4d1cf21c816c6f6caed76b9dcf1dc9708df52dff5545b2cc26` |

## 6. Binary / media `.dat` inventory

| # | Stored as | Original name | MIME | Size | MD5 | SHA-256 |
|---|-----------|---------------|------|------|-----|---------|
| 1 | `raw_dat_attachments/file-BTNC68MBF7ihGaQrAo7Mso.dat` | `file-BTNC68MBF7ihGaQrAo7Mso.dat` | MP3 audio | 19.5 KB | `65899eb65c9aa4155ac386b105cd2a6a` | `6601213aa6fb9ae10e8a7036915863ff096e4ac7e3a801ec6297d3f05d506b25` |
| 2 | `raw_dat_attachments/file-Wty5S6JrcWZtHKvCD5SZAJ.dat` | `file-Wty5S6JrcWZtHKvCD5SZAJ.dat` | MP3 audio | 16.5 KB | `649f9546e9ddc3c0dd5bec0e32ce3d8c` | `173d004904c95b1aaa919614898f718d39cab064a43bc365648233dd33426e46` |
| 3 | `raw_dat_attachments/file_0000000000347207b0e1a190cb9d4441.dat` | `file_0000000000347207b0e1a190cb9d4441.dat` | PNG image | 12.3 KB | `b74bd6f4fe15fda6948d2313805fb43d` | `441d6aeef18e1accd417d0a4a1633560c1a077d3e1bdef09f7f54c4f733ac2c7` |
| 4 | `raw_dat_attachments/file_000000000130720bb574b8e6096340d3.dat` | `file_000000000130720bb574b8e6096340d3.dat` | PNG image | 9.5 KB | `9b50a55998fd6a8fa4ebf7bfc6eec251` | `ba112eb81a1f169d40f787ba993daeab2d93f700c548d37a985831d939196a42` |
| 5 | `raw_dat_attachments/file_00000000099071fa8e84555cad438a2d.dat` | `file_00000000099071fa8e84555cad438a2d.dat` | PNG image | 3.0 KB | `1835ded52371ecca4443d00c3600f381` | `81e5e4cb705886f3d5826798b41034b0ba05be864a53f89e4f4dbfbbac7ee40f` |
| 6 | `raw_dat_attachments/file_0000000015c8720b87a63fa9ad90332a.dat` | `file_0000000015c8720b87a63fa9ad90332a.dat` | PNG image | 10.0 KB | `f86dbd50a24882ce081bf10a2a25745b` | `bd294993989a8b3ccd0e0f6a2e3235c284118aaaa9672ac85cb946979cbdac09` |
| 7 | `raw_dat_attachments/file_00000000197471fab39a5df9f51412bd.dat` | `file_00000000197471fab39a5df9f51412bd.dat` | PNG image | 8.5 KB | `c37eff389316b9e29e06fa13f76c684b` | `5f5ca3d6c45ff9afb025eb5b430cc44bcb191d3aa7586808edde1a625387934f` |
| 8 | `raw_dat_attachments/file_000000001a3472098f1ec512ca92d9d2.dat` | `file_000000001a3472098f1ec512ca92d9d2.dat` | PNG image | 19.3 KB | `2e6c6e378e2241a64e0a63d9699e70ff` | `667a7d7907c52e0ac4e7dd8a469ec614b13d6c589538914e47133c9ae2b68994` |
| 9 | `raw_dat_attachments/file_000000001bac7207adff0cb9f2a2f87d.dat` | `file_000000001bac7207adff0cb9f2a2f87d.dat` | PNG image | 14.1 KB | `37fbccfa97e772de64a91d3b46440b27` | `a38f5c062aaa1bb7aa633453e19a134c8853770a744ba86cac5195ad6af1b46b` |
| 10 | `raw_dat_attachments/file_000000001f0872079578f4778500bc5e.dat` | `file_000000001f0872079578f4778500bc5e.dat` | PNG image | 14.7 KB | `c50258265acd4f7ff979d02dccb4802d` | `8e95a2c2b83ace629d61a256a0177c49e46a86a69e05d03cb97bb3cecfa4f687` |
| 11 | `raw_dat_attachments/file_00000000204071fda49994955f8fbc3e.dat` | `file_00000000204071fda49994955f8fbc3e.dat` | PNG image | 17.3 KB | `a9754f6c5e45e787b16cb9b4c7dcd92c` | `aee1a24e384bbd4257a469bd71a853de7fa2ba960ef23517782800f55f0ed723` |
| 12 | `raw_dat_attachments/file_00000000297c71fab4e12fa3b53d65c4.dat` | `file_00000000297c71fab4e12fa3b53d65c4.dat` | PNG image | 14.5 KB | `1a7b54271e2269100598759086d7ded7` | `0be91fdcd37e7b251051a41af36d7cc42a528c3a6390b05ce807ce51b2093e81` |
| 13 | `raw_dat_attachments/file_000000002b947209b7f3d39209933beb.dat` | `file_000000002b947209b7f3d39209933beb.dat` | PNG image | 19.0 KB | `32d44096e7926526efd8e5508ce7f0b2` | `9860412e4993ff4f33e08917a1dab5c19158ba801ef426649171a608c32c3751` |
| 14 | `raw_dat_attachments/file_0000000032b47207998a59984135d8a0.dat` | `file_0000000032b47207998a59984135d8a0.dat` | PNG image | 6.4 KB | `1e5ad06370d640d4ec04f3a1a7e21566` | `458424e072a70f242992367fba6425bd6b23741af4509cf50ce3d183c645714f` |
| 15 | `raw_dat_attachments/file_00000000337871fdaea33af922aacad5.dat` | `file_00000000337871fdaea33af922aacad5.dat` | PNG image | 17.3 KB | `a9754f6c5e45e787b16cb9b4c7dcd92c` | `aee1a24e384bbd4257a469bd71a853de7fa2ba960ef23517782800f55f0ed723` |
| 16 | `raw_dat_attachments/file_0000000039c872078f0d7682f33863a4.dat` | `file_0000000039c872078f0d7682f33863a4.dat` | PNG image | 11.2 KB | `2bdef50c56357a47ca1b224615e83d8a` | `a7225f5c3a2f164fb3533eafc0a4be30bf77107d030cd1662c519c57bec98fd9` |
| 17 | `raw_dat_attachments/file_000000003c1072089e432122fc5cb4ef.dat` | `file_000000003c1072089e432122fc5cb4ef.dat` | PNG image | 7.0 KB | `de4a8896dc1644e1bd57b47a6e58a416` | `e8a161eee7f1732d18d01a6cd0f01d80e8731f7fc1d597b5435ff5f83024940c` |
| 18 | `raw_dat_attachments/file_000000004ac871fa85315bf42ca90341.dat` | `file_000000004ac871fa85315bf42ca90341.dat` | PNG image | 14.5 KB | `1a7b54271e2269100598759086d7ded7` | `0be91fdcd37e7b251051a41af36d7cc42a528c3a6390b05ce807ce51b2093e81` |
| 19 | `raw_dat_attachments/file_000000004b5c71f5b06d6762e9b4ba0f.dat` | `file_000000004b5c71f5b06d6762e9b4ba0f.dat` | PNG image | 6.0 KB | `56364a7d538a555882cf012e26b2a5f1` | `f34dd1bc7d032c17575eb52a8d5ecd0150f6bd1fd9fa36fe2ee17d0f4419fcf8` |
| 20 | `raw_dat_attachments/file_000000004f147208b5eb0b1b8c55c587.dat` | `file_000000004f147208b5eb0b1b8c55c587.dat` | PNG image | 4.9 KB | `fec0285d1f3bfbb6993ab4c3455603c3` | `abf5993795a906460b9d412483941b4d95b8bf1c0e331177328f2b5ec5c0d721` |
| 21 | `raw_dat_attachments/file_0000000058f47206a1a725ab77e0488a.dat` | `file_0000000058f47206a1a725ab77e0488a.dat` | PNG image | 19.1 KB | `fd77ac408283188859defa0655c85f5d` | `3b54f12d494fca4cfcf3e66230c747eeb32a3e0eac1d67063288430c20f1ea7b` |
| 22 | `raw_dat_attachments/file_000000005da871fa9a139cddf5a23c22.dat` | `file_000000005da871fa9a139cddf5a23c22.dat` | PNG image | 10.7 KB | `1a9450340020079a2e56e93daab68c86` | `fd0acf1829508657d1b84068a0fc53d26f7f2181c47845156a149d3e48f770bc` |
| 23 | `raw_dat_attachments/file_000000006ddc71fa823431db2976cc14.dat` | `file_000000006ddc71fa823431db2976cc14.dat` | PNG image | 2.7 KB | `3cf1a88f9dbcf312674732868131fcbf` | `a08a555098262707d17b8cf4cc1c233f361cdc532e5ca0bd0b94c29accb5d23c` |
| 24 | `raw_dat_attachments/file_000000007880720885662fb2f586ed31.dat` | `file_000000007880720885662fb2f586ed31.dat` | PNG image | 14.6 KB | `e19f897121265e81fb3fa9922eeb99d8` | `1e8e8dc75defba38fc8bc17391b794fc0ba63263eb9ccdc9346089d20b46d0fe` |
| 25 | `raw_dat_attachments/file_0000000079e87207af41f7254640687c.dat` | `file_0000000079e87207af41f7254640687c.dat` | PNG image | 2.6 KB | `43eb44c0ddf7943cf3d278de3b82fbf5` | `2b39e77613ae33a757ae968ef31ea92bbc5c3285c65b817f411f0c23f1eccf4f` |
| 26 | `raw_dat_attachments/file_000000007fc47207a0e56067530752a0.dat` | `file_000000007fc47207a0e56067530752a0.dat` | PNG image | 19.4 KB | `c7e0ed33003c67e5651549d60b13fa06` | `9708679fbd6594648b9488733753398f875f3d48559b068207f38e74fa7017b5` |
| 27 | `raw_dat_attachments/file_00000000853c71f7a2b2cdeac3e53678.dat` | `file_00000000853c71f7a2b2cdeac3e53678.dat` | PNG image | 10.8 KB | `221277580867c2ad73441f931e1dbe57` | `9d30030d0e04728380c18f59d6adf8d30f6e46895fb731eeeb0097b03260f011` |
| 28 | `raw_dat_attachments/file_000000008aa471fa9ab44c811b757d16.dat` | `file_000000008aa471fa9ab44c811b757d16.dat` | PDF document | 16.7 KB | `6ccc80e2534b84690341900594b6c0c5` | `97a637a39883dc2ba4b9116bdcb4bd4ca297d6192752d6f45c693bfb050a9033` |
| 29 | `raw_dat_attachments/file_00000000907471fbaa77009b37838e67.dat` | `file_00000000907471fbaa77009b37838e67.dat` | PNG image | 5.2 KB | `3468b5d4ea691b7548f6f307d0db97ab` | `029ede70ba86f9123691b7cfaadebb99a9e9c8b55535d77d11e9ac99e4d1a042` |
| 30 | `raw_dat_attachments/file_00000000a23c71fb89240da7d94e2837.dat` | `file_00000000a23c71fb89240da7d94e2837.dat` | PNG image | 3.8 KB | `92091bc0ee70b8b365cc88a9ddf148f2` | `08d4e7d20181005313829ac93ce5f6f26385c6ed3ef13f044cfaac8df172e6ed` |
| 31 | `raw_dat_attachments/file_00000000aeb87209a92172ab42916335.dat` | `file_00000000aeb87209a92172ab42916335.dat` | PNG image | 3.6 KB | `4d1affc6d26130a2e55d47396fed02f7` | `f61c0ea321255673cdd5d37745eb8a60ad0f3ae64a90ab79d7f1e82bb61d393d` |
| 32 | `raw_dat_attachments/file_00000000b39471fa9415940412006e20.dat` | `file_00000000b39471fa9415940412006e20.dat` | PNG image | 8.4 KB | `02fec18687b532c510910cd9d548e043` | `a8fa16f14890b46c41621daa4658683a6d211599c899ff769c5245cde443956b` |
| 33 | `raw_dat_attachments/file_00000000b89c71f7b3347083d93eb62b.dat` | `file_00000000b89c71f7b3347083d93eb62b.dat` | PNG image | 10.8 KB | `4e1da24699c0df6f50a5a3655b4ae635` | `4def3d3c3db15f700a9ed56e59a57ea7dbb9cacd268258bd3f3cb1bfa2117911` |
| 34 | `raw_dat_attachments/file_00000000b8f87208852a10f381b0c29d.dat` | `file_00000000b8f87208852a10f381b0c29d.dat` | PNG image | 19.0 KB | `0775faa202c5eb6e6a798a8d4eefa7d1` | `6729de42a6d8920ebb6b169329c2823c1ba4d3486cba5b93dbfd421f8ff914ef` |
| 35 | `raw_dat_attachments/file_00000000ba9c71f59064540caf45ecb9.dat` | `file_00000000ba9c71f59064540caf45ecb9.dat` | PNG image | 9.1 KB | `5bddab642596934b1bec6edd977fc7d7` | `6d663009dbca5057302dcc0b0d18a4182b6e27804a45d7b101bec6c1fca19ec7` |
| 36 | `raw_dat_attachments/file_00000000bb847207925deda7dd751c47.dat` | `file_00000000bb847207925deda7dd751c47.dat` | PNG image | 15.6 KB | `6961b6375fcff4054bd11d0c8fc7b110` | `93f7c1ed0829ed62fe2f9913f27e76c1d3a3d8d039e1bb1f86c26ee38aa8aafc` |
| 37 | `raw_dat_attachments/file_00000000c95871f59d29f8a145504628.dat` | `file_00000000c95871f59d29f8a145504628.dat` | PNG image | 14.0 KB | `ecc5e3e2f15b8f1008bc8389ccd3396f` | `37fc1baea15c0e8ca42eb63a28348134534521ddd92b5ff8af366aded536880b` |
| 38 | `raw_dat_attachments/file_00000000c9a07208b0979b212678424f.dat` | `file_00000000c9a07208b0979b212678424f.dat` | PNG image | 9.5 KB | `4c7ed4e08370b4772da1ebedadd66375` | `a21f52d6a7b19f51a13dafb3293547e863b39b3f5765db7b427ac2004b41b35d` |
| 39 | `raw_dat_attachments/file_00000000cfac72098c23519d9e32a139.dat` | `file_00000000cfac72098c23519d9e32a139.dat` | PNG image | 19.7 KB | `878d2f9b7cd5fc6213b021423d85f644` | `c1f3565df72bf266fa69ecb2b0fd124d3b93d1fd01e9c39f124bcdc37d2a963b` |
| 40 | `raw_dat_attachments/file_00000000d3c871fa829429cd9350c959.dat` | `file_00000000d3c871fa829429cd9350c959.dat` | PNG image | 3.3 KB | `7e47c5aa04e3de9e3a454d0a52d091db` | `1db4eefd4011472d8c38545c23985752469e5c3b2882132b018400e520a903b3` |
| 41 | `raw_dat_attachments/file_00000000d67c71faa769706c518210cb.dat` | `file_00000000d67c71faa769706c518210cb.dat` | PNG image | 10.4 KB | `9b13fabf38ae9684aac97c02dfa48408` | `7ae965678de1f2344576d81571595d5c697a88283f39173bc00b69095a71c758` |
| 42 | `raw_dat_attachments/file_00000000d9b072078de141fc1e2271b0.dat` | `file_00000000d9b072078de141fc1e2271b0.dat` | PNG image | 13.0 KB | `c2a6eb4cb62aa02d2cc326328d47e8ce` | `860d9322db14d4c5bf33406fc81d15fc12f1c7e265de5ac989219e7d0c90d6fc` |
| 43 | `raw_dat_attachments/file_00000000dff871fba2ae871b935aac57.dat` | `file_00000000dff871fba2ae871b935aac57.dat` | PNG image | 9.1 KB | `5bddab642596934b1bec6edd977fc7d7` | `6d663009dbca5057302dcc0b0d18a4182b6e27804a45d7b101bec6c1fca19ec7` |
| 44 | `raw_dat_attachments/file_00000000e07071f58f7678144f422f01.dat` | `file_00000000e07071f58f7678144f422f01.dat` | PNG image | 3.0 KB | `402b11233d2bab1deb89d1717e3169d8` | `169bdd65875d8424aa493de7ac37037904f572092c263190f3a3e166d8a41d1f` |
| 45 | `raw_dat_attachments/file_00000000e17871f592626e2ff7b7163f.dat` | `file_00000000e17871f592626e2ff7b7163f.dat` | PNG image | 4.7 KB | `b92c786221290e942bc2a8e7a1fcbf22` | `8d6317eabcfa43bb18a9769baba51342e17eba74096a881b83a06a1eb05bcbe7` |
| 46 | `raw_dat_attachments/file_00000000f37071fab1b739168b64e1ce.dat` | `file_00000000f37071fab1b739168b64e1ce.dat` | PNG image | 19.4 KB | `c8ac1bbc624526687a67768fddbba560` | `b41da78151c7c18a49920620aeb02f805a9a192b5e17020846dac96ab52622f8` |
| 47 | `raw_dat_attachments/file_00000000f38c71fabe34737eef7f08cd.dat` | `file_00000000f38c71fabe34737eef7f08cd.dat` | PNG image | 19.3 KB | `887b4ff983e06383edd921f3c764732b` | `19d895ae4753aa0ffac40e674e1d9bebc51f85cac457000cfc6328beacf86d58` |
| 48 | `raw_dat_attachments/file_00000000f9ec7206a53f3a4740ed1b43.dat` | `file_00000000f9ec7206a53f3a4740ed1b43.dat` | PNG image | 17.9 KB | `2df0ac498c8c1f776557a0ebfda4be11` | `2043495036b93b05193014a445ee61a98661736a550c3f4a6888e55aceef2c96` |
| 49 | `raw_dat_attachments/file_00000000fca47207a07e319ce098a83f.dat` | `file_00000000fca47207a07e319ce098a83f.dat` | PNG image | 9.7 KB | `1c578f74ea638421dd21c137d645a294` | `8a9391843c2b26be28698e7ef26d00749633d3bdae9418d5dd6c87640eee2a0d` |

## 7. Recoverable fragments

2 artifact(s) contain the user's own prompt wording rather than generated code — see `recoverable-fragments/RECOVERABLE_FRAGMENTS.md`. These are excerpts inside documents and terminal logs, **not** dialogue turns, and they are labelled as such there.

## 8. Verification

- Binary `.dat` files found: **49** → preserved: **49**  (MATCH)
- Text/JSON artifacts found: **32** → catalogued: **32** (MATCH)
- Conversations found: **0** → `refined_chat.txt` files: **0** (nothing to render)

## 9. Method notes

- Classification is content-based: UTF-8 decode → `json.loads` → chat-structure probe; if that fails, control-character density decides whether the bytes are text or binary.
- Binary blobs are copied with `shutil.copy2`, never decoded or re-encoded, so their bytes and mtimes survive intact.
- Text artifacts are stored twice: `original.bin` (byte-exact upload) and `content.txt` (decoded UTF-8) so diffs are readable without losing the original.
- Nothing in this index is inferred: every count above is computed from the files at build time.

## 10. External sources folded in (Google Drive)

Included with the user's explicit approval so the archive is self-contained. These did **not** come from the `.dat` upload and carry their own provenance headers.

### `google-drive` → `external-google-drive/`

| File | Class | Format | Topic chain | Size | SHA-256 (16) | Location |
|------|-------|--------|-------------|------|--------------|----------|
| [`esp32_interface_df_player_mini.ino`](https://drive.google.com/file/d/1ZXEKZxr_Bsj_oyYje0L3kEbPdDfoFYuo/view) | external-text | cpp | `hardware-esp32` | 846 B | `7d18c44897292e2e` | `external-google-drive/hardware-esp32/cpp__dfplayer-mini-pins-26/content.txt` |
| [`Df_Player_mini_Arduino.ino`](https://drive.google.com/file/d/1i0mtgmK175qKYOJAn_yGkb6cOTYsUKD2/view) | external-text | cpp | `hardware-esp32` | 879 B | `c014877033b37361` | `external-google-drive/hardware-esp32/cpp__dfplayer-mini-pins-2/content.txt` |
| [`Circuit Diagram.png`](https://drive.google.com/file/d/1Cxml0qjzqg1sLnZ5xxEIVrG8jcwTzJJN/view) | external-binary | PNG image | `media-attachments` | 180.2 KB | `e074ef38323f7ca8` | `external-google-drive/raw_attachments/Circuit Diagram.png` |

