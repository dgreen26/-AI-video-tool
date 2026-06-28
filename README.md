# UGC Ad Pipeline

Turns an account config plus a chosen pattern into a finished, captioned, exported 9:16 ad with no manual editing. Built for a local-services ad agency.

The full operating manual lives in CLAUDE.md. Read it before producing any ad. The short version is below.

## How it works

One ad is built from two inputs:

1. An account file in /accounts (the ingredients: price, offer, trust line, colors, setting).
2. A pattern card in /patterns (the recipe: beat structure, banner template, caption template, offer architecture).

The pattern is the structure. The account fills it in. Output lands in /output.

## Folder map

- /patterns   reusable ad pattern cards
- /accounts   one config file per client, plus _schema.json
- /assets     generated talent clips, voiceover, timestamps
- /output     finished ads
- /scripts    pipeline code

## Accounts

Each client gets one JSON file in /accounts that matches /accounts/_schema.json. Start from /accounts/cleaning-example.json as a working reference. All twelve fields are required. A typo in a key fails validation on purpose.

## Hard rules

These are enforced on every ad. Full detail in CLAUDE.md.

- No em-dashes anywhere, on screen or in voiceover.
- No buzzwords, no filler, no AI-sounding language.
- Every claim must be defensible for that account.
- 9:16, 1080x1920, 30fps, 12 to 15 seconds.
- QC gate must pass before anything ships. Hero price legible and identical in every beat, CTA on screen at least 1.5 seconds at high contrast, all text inside the 10 percent edge safe zones.

## Status

Phase 1. Knowledge and config layer only. The assembler and generation code are not built yet.
