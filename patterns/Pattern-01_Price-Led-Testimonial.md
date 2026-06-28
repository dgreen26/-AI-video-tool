# Pattern-01: Price-Led Testimonial

A 12-15 second UGC pattern. The hook is the price. The structure is a real-person testimonial that earns the price reveal by landing the transformation before the CTA.

---

## Beat structure

Five beats. Total runtime 12-15 seconds. Timestamps are targets, not hard cuts.

### Beat 1: Price Hook (0:00-0:02)

Talent looks directly into camera. No warmup. Lead with the price.

Spoken:
> "We just got [service_descriptor] for $[hero_price]."

Banner: Price stamp, centered, large. See banner template B1.

### Beat 2: Benefit Setup (0:02-0:05)

Talent stays on camera. Deliver the payoff line. Keep it personal and plain.

Spoken:
> "And honestly? [benefit_line]."

No banner. Let the face carry it.

### Beat 3: Transformation (0:05-0:09)

Widen slightly or cut to B-roll of the service in action. Talent continues or cuts back to face.

Spoken:
> "[transformation_line]."

Banner: Short transformation label, lower third. See banner template B3.

### Beat 4: Trust Line (0:09-0:11)

Return to talent face. Credibility line, delivered flat, not salesy.

Spoken:
> "[trust_line]."

No banner. Trust lines land harder without a graphic competing.

### Beat 5: Sweetener and CTA (0:11-0:15)

Talent delivers sweetener first, then CTA. Banner must be on screen for the full CTA duration, minimum 1.5 seconds.

Spoken:
> "[sweetener]. [cta]."

Banner: CTA stamp. See banner template B5. High contrast required.

---

## Banner templates

All text inside 10 percent edge safe zones. Nothing within 10 percent of any edge.

### B1: Price stamp

```
Position: center screen, vertically centered between 35% and 65% of frame height
Font size: large (target 96-120px at 1080x1920)
Color: accent
Text: $[hero_price]
Background: none, or tight semi-transparent pill if legibility requires it
```

### B3: Transformation label

```
Position: lower third, above 10% bottom safe zone
Font size: medium (target 52-64px at 1080x1920)
Color: headline
Text: [transformation_line]
Note: truncate to one short phrase if needed
Background: none
```

### B5: CTA stamp

```
Position: lower third, above 10% bottom safe zone
Font size: medium (target 52-64px at 1080x1920)
Color: high contrast against background, use accent if readable, else white with dark backing
Text: [cta]
Minimum on-screen duration: 1.5 seconds
```

---

## Caption template

Captions follow the spoken word exactly. No paraphrasing.

- Font: clean sans-serif, one word group at a time
- Size: readable without audio, target 42-52px at 1080x1920
- Color: white with dark drop shadow or outline
- Position: center of frame, below midpoint, inside safe zones
- Sync: word-accurate to the audio track

Do not auto-generate captions and call it done. Proof every line against the voiceover before export.

---

## Offer architecture

The price leads. The benefit earns it. The transformation proves it. The trust line removes doubt. The sweetener tips the action.

Order is fixed:

1. Price (Beat 1)
2. Benefit (Beat 2)
3. Transformation (Beat 3)
4. Trust (Beat 4)
5. Sweetener then CTA (Beat 5)

Do not rearrange. Do not combine beats. If the account does not have a clean value for a field, fix the account config, not the pattern.

---

## Schema fields used

This pattern draws on all required fields from accounts/_schema.json:

| Pattern slot | Schema field |
|---|---|
| Output file naming | account_name |
| B1 price stamp | hero_price |
| Beat 1 spoken | service_descriptor, hero_price |
| Beat 2 spoken | benefit_line |
| Beat 3 spoken | transformation_line |
| B3 label | transformation_line |
| Beat 4 spoken | trust_line |
| Beat 5 spoken | sweetener, cta |
| B5 stamp | cta |
| Banner colors | brand_colors.headline, brand_colors.accent |
| Talent clip prompt | setting, background_action |

Every field is used. No field is optional in this pattern.

---

## Hard rules (inherit from CLAUDE.md, restated here for the checklist)

- No em-dashes in spoken copy or banners. Periods and commas only.
- No buzzwords, no filler.
- hero_price must be identical in Beat 1 spoken and the B1 banner. One number, everywhere.
- CTA banner on screen minimum 1.5 seconds.
- All text inside 10 percent safe zones on all four edges.
- Every claim traceable to the account config.
- Read the voiceover aloud before locking. If it sounds written, rewrite it.
