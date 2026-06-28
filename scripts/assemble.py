#!/usr/bin/env python3
"""Render a copy pass from an account config and a pattern card.

Usage:
    python scripts/assemble.py --account accounts/cleaning-example.json \
                                --pattern patterns/Pattern-01_Price-Led-Testimonial.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "accounts" / "_schema.json"

_BEAT_HEAD = re.compile(r"^### Beat (\d+): (.+?) \((\d+:\d+-\d+:\d+)\)")
_BANNER_HEAD = re.compile(r"^### (B\d+): (.+)")
_KV = re.compile(r"^([\w][\w\s]*?):\s*(.+)")


# ---------------------------------------------------------------------------
# Account
# ---------------------------------------------------------------------------

def load_account(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def validate_account(account: dict) -> list:
    with open(SCHEMA) as f:
        schema = json.load(f)

    errors = []
    for field in schema["required"]:
        if field not in account:
            errors.append(f"missing required field: {field}")

    if "hero_price" in account and not isinstance(account["hero_price"], (int, float)):
        errors.append("hero_price must be a number")

    hex_pat = re.compile(r"^#[0-9a-fA-F]{6}$")
    for key in ("headline", "accent"):
        val = account.get("brand_colors", {}).get(key, "")
        if val and not hex_pat.match(val):
            errors.append(f"brand_colors.{key} must be a 6-digit hex color, got {val!r}")

    return errors


# ---------------------------------------------------------------------------
# Pattern parser
# ---------------------------------------------------------------------------

def parse_pattern(path: Path) -> dict:
    """Return {'beats': {N: {...}}, 'banners': {'B1': {...}}}."""
    lines = path.read_text().splitlines()
    beats: dict = {}
    banners: dict = {}
    i = 0

    while i < len(lines):
        line = lines[i]

        m = _BEAT_HEAD.match(line)
        if m:
            num, name, timing = int(m.group(1)), m.group(2), m.group(3)
            spoken_tpl: Optional[str] = None
            banner_ref: Optional[str] = None
            i += 1
            while i < len(lines) and not lines[i].startswith("### "):
                s = lines[i].strip()
                if s.startswith("> "):
                    spoken_tpl = s[2:].strip().strip('"')
                elif s.startswith("Banner:"):
                    ref = re.search(r"B\d+", s)
                    if ref:
                        banner_ref = ref.group(0)
                i += 1
            beats[num] = {
                "name": name,
                "timing": timing,
                "spoken_tpl": spoken_tpl,
                "banner_ref": banner_ref,
            }
            continue

        m = _BANNER_HEAD.match(line)
        if m:
            bid, bname = m.group(1), m.group(2)
            fields: dict = {"_name": bname}
            in_code = False
            i += 1
            while i < len(lines) and not lines[i].startswith("### "):
                l = lines[i]
                if l.strip().startswith("```"):
                    in_code = not in_code
                elif in_code:
                    kv = _KV.match(l.strip())
                    if kv:
                        fields[kv.group(1).strip().lower()] = kv.group(2).strip()
                i += 1
            banners[bid] = fields
            continue

        i += 1

    return {"beats": beats, "banners": banners}


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def _price_str(account: dict) -> str:
    p = account["hero_price"]
    return str(int(p)) if isinstance(p, float) and p == int(p) else str(p)


def substitute(tpl: str, account: dict) -> str:
    """Replace $[field] and [field] placeholders with account values."""
    price = _price_str(account)

    def val(key: str) -> str:
        if key == "hero_price":
            return price
        v = account.get(key)
        return str(v) if v is not None else f"[{key}]"

    result = re.sub(r"\$\[(\w+)\]", lambda m: f"${val(m.group(1))}", tpl)
    result = re.sub(r"\[(\w+)\]", lambda m: val(m.group(1)), result)
    return result


def resolve_color(spec: str, account: dict) -> str:
    low = spec.lower()
    if low == "accent":
        return account["brand_colors"]["accent"]
    if low == "headline":
        return account["brand_colors"]["headline"]
    return spec  # multi-part specs are a render-time decision


def render(account: dict, pattern: dict) -> list:
    out = []
    for num in sorted(pattern["beats"]):
        beat = pattern["beats"][num]
        spoken = substitute(beat["spoken_tpl"], account) if beat["spoken_tpl"] else None

        banner = None
        if beat["banner_ref"]:
            spec = pattern["banners"].get(beat["banner_ref"], {})
            banner = {
                "id": beat["banner_ref"],
                "text": substitute(spec.get("text", ""), account),
                "color": resolve_color(spec.get("color", ""), account),
                "position": spec.get("position", ""),
                "font_size": spec.get("font size", ""),
                "background": spec.get("background", ""),
            }
            if beat["banner_ref"] == "B5":
                banner["min_duration_sec"] = 1.5

        out.append({
            "beat": num,
            "name": beat["name"],
            "timing": beat["timing"],
            "spoken": spoken,
            "banner": banner,
        })
    return out


# ---------------------------------------------------------------------------
# QC gate
# ---------------------------------------------------------------------------

def qc_check(beats: list, account: dict) -> dict:
    price = _price_str(account)
    auto = []
    all_passed = True

    def fail(check, detail):
        nonlocal all_passed
        all_passed = False
        auto.append({"check": check, "status": "FAIL", "detail": detail})

    def ok(check, detail):
        auto.append({"check": check, "status": "PASS", "detail": detail})

    # Hero price present in both spoken copy and at least one banner
    spoken_hits = [b["beat"] for b in beats if b["spoken"] and f"${price}" in b["spoken"]]
    banner_hits = [b["beat"] for b in beats if b["banner"] and price in b["banner"]["text"]]
    if spoken_hits and banner_hits:
        ok("hero_price_consistent",
           f"${price} in spoken beat(s) {spoken_hits} and banner beat(s) {banner_hits}")
    else:
        parts = []
        if not spoken_hits:
            parts.append("spoken copy")
        if not banner_hits:
            parts.append("banners")
        fail("hero_price_consistent", f"${price} missing from: {', '.join(parts)}")

    # CTA banner carries a minimum duration spec
    cta = next((b for b in beats if b["banner"] and "min_duration_sec" in b["banner"]), None)
    if cta:
        ok("cta_min_duration",
           f"Beat {cta['beat']} ({cta['name']}) B5 carries {cta['banner']['min_duration_sec']}s minimum on-screen")
    else:
        fail("cta_min_duration", "No CTA banner with a minimum duration spec found")

    # No em-dashes in rendered copy
    em_hits = []
    for b in beats:
        if b["spoken"] and "—" in b["spoken"]:
            em_hits.append(f"beat {b['beat']} spoken")
        if b["banner"] and "—" in b["banner"]["text"]:
            em_hits.append(f"beat {b['beat']} banner")
    if em_hits:
        fail("no_em_dashes", f"Em-dashes in: {', '.join(em_hits)}")
    else:
        ok("no_em_dashes", "No em-dashes in rendered copy or banners")

    # No unresolved placeholders
    unresolved = []
    for b in beats:
        for label, text in (("spoken", b["spoken"]), ("banner", b["banner"]["text"] if b["banner"] else None)):
            if text and re.search(r"\[\w+\]", text):
                unresolved.append(f"beat {b['beat']} {label}: {text!r}")
    if unresolved:
        fail("no_unresolved_placeholders", "Unresolved: " + "; ".join(unresolved))
    else:
        ok("no_unresolved_placeholders", "All placeholders resolved")

    manual = [
        "Proof spelling and grammar on every overlay before export.",
        "Read the voiceover aloud. Rewrite any line that sounds written.",
        "Confirm every claim is defensible for this account.",
        "Verify CTA is high contrast against its background at render time.",
        "Verify all text inside the 10 percent edge safe zones at render time.",
    ]

    return {"auto": auto, "all_auto_passed": all_passed, "manual": manual}


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_report(account: dict, pattern_path: Path, beats: list, qc: dict):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n=== {account['account_name']} / {pattern_path.stem} ===")
    print(f"Generated: {now}\n")

    for b in beats:
        print(f"BEAT {b['beat']}: {b['name']} ({b['timing']})")
        if b["spoken"]:
            print(f'  SPOKEN:  "{b["spoken"]}"')
        if b["banner"]:
            bn = b["banner"]
            dur = f"  [min {bn['min_duration_sec']}s on screen]" if "min_duration_sec" in bn else ""
            print(f'  BANNER {bn["id"]}: "{bn["text"]}" | color {bn["color"]}{dur}')
        else:
            print("  BANNER:  none")
        print()

    print("QC GATE")
    print("-------")
    for c in qc["auto"]:
        print(f"  [{c['status']}] {c['check']}: {c['detail']}")
    print()
    print("  Manual (cannot automate):")
    for item in qc["manual"]:
        print(f"  [ ] {item}")
    print()
    print("Auto QC: PASS. Complete manual checks before shipping."
          if qc["all_auto_passed"] else
          "Auto QC: FAIL. Fix above before continuing.")
    print()


def write_json(account: dict, pattern_path: Path, beats: list, qc: dict,
               out_path: Optional[Path]) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "-", account["account_name"].lower()).strip("-")
    dest = out_path or (ROOT / "assets" / slug / pattern_path.stem / "copy_pass.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "account": account["account_name"],
        "pattern": pattern_path.stem,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "beats": beats,
        "qc": qc,
    }
    dest.write_text(json.dumps(payload, indent=2))
    return dest


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Render ad copy pass from account config and pattern card."
    )
    ap.add_argument("--account", required=True,
                    help="Account JSON (e.g. accounts/cleaning-example.json)")
    ap.add_argument("--pattern", required=True,
                    help="Pattern card markdown (e.g. patterns/Pattern-01_Price-Led-Testimonial.md)")
    ap.add_argument("--out", help="Override output JSON path")
    args = ap.parse_args()

    account_path = Path(args.account)
    pattern_path = Path(args.pattern)

    if not account_path.exists():
        print(f"Account file not found: {account_path}", file=sys.stderr)
        sys.exit(1)
    if not pattern_path.exists():
        print(f"Pattern file not found: {pattern_path}", file=sys.stderr)
        sys.exit(1)

    account = load_account(account_path)
    errors = validate_account(account)
    if errors:
        print("Account validation failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    pattern = parse_pattern(pattern_path)
    if not pattern["beats"]:
        print(f"No beats found in {pattern_path}. Check pattern card format.", file=sys.stderr)
        sys.exit(1)

    beats = render(account, pattern)
    qc = qc_check(beats, account)

    print_report(account, pattern_path, beats, qc)
    dest = write_json(account, pattern_path, beats, qc, Path(args.out) if args.out else None)
    print(f"Written: {dest}")

    sys.exit(0 if qc["all_auto_passed"] else 1)


if __name__ == "__main__":
    main()
