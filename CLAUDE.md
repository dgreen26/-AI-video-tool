# CLAUDE.md

Operating manual for this UGC ad pipeline. Every ad this project produces follows the rules in this file. If a request conflicts with this file, this file wins unless I explicitly override it in the moment.

## Mission

Turn an account config plus a chosen pattern into a finished, captioned, exported 9:16 ad with no manual editing. Input is one account file from /accounts and one pattern card from /patterns. Output is a ready to ship vertical video in /output. No human touches a timeline.

## Hard style rules

These apply to all on-screen text and all voiceover copy, every time.

- No em-dashes, ever. Use periods or commas.
- No buzzwords, no filler, no AI-sounding language. Write the way a real person talks.
- Voiceover is plain spoken voice. Read it aloud before locking it. If it does not sound natural out of a real mouth, rewrite it.
- Every claim must be defensible for that specific account. If the account cannot back it up, it does not go on screen and it does not go in the read.

## Pattern-driven production

Every ad is built from a pattern card in /patterns. Before writing a single line of copy or planning a single beat:

1. Read the chosen pattern card in full.
2. Follow its beat structure exactly.
3. Use its banner template for on-screen banners.
4. Use its caption template for spoken-word captions.
5. Use its offer architecture for how price, sweetener, trust, and CTA are arranged.

The pattern card is the recipe. The account config fills in the ingredients. Do not invent structure that is not in the pattern.

## Format defaults

- Aspect ratio: 9:16
- Resolution: 1080x1920
- Frame rate: 30fps
- Duration: 12 to 15 seconds

## QC gate (ship or no-ship)

Run this before any ad is considered done. Every item must pass. One failure means no-ship.

- Spelling and grammar proofed on every overlay.
- Hero price is legible and identical in every beat where it appears.
- CTA is on screen at least 1.5 seconds, high contrast against its background.
- All text sits inside the 10 percent edge safe zones. Nothing within 10 percent of any edge, top, bottom, left, or right.
- Every claim is defensible for this account.

## Ship call

End every ad review with one line:

"This matches the winning pattern because ___, therefore ship, iterate, or kill."

Fill the blank with the real reason. Pick one of ship, iterate, or kill. Do not hedge.
