#!/usr/bin/env bash
#
# Builds the "FEEL TIRED? / DO IT ANYWAY." split-screen motivational loop
# from 5 raw Higgsfield clips into one 1080x1920 30fps vertical reel.
#
# Usage:
#   1. Download the 5 raw clips from the Higgsfield generation widget and
#      save them into assets/fitness-loop/raw/ with these exact names:
#        beat1_tired.mp4   beat2_shoes.mp4   beat3_runner.mp4
#        beat4_lift.mp4    beat5_plates.mp4
#   2. ./scripts/build_fitness_loop.sh
#   3. Output lands at output/fitness-loop-v1.mp4
#
# Requires ffmpeg (built with libass) on PATH and a "DejaVu Sans" or other
# bold sans-serif family findable by fontconfig. Override the family with
# FONT_FAMILY=... if you don't have DejaVu Sans installed.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW="$ROOT/assets/fitness-loop/raw"
WORK="$ROOT/assets/fitness-loop/work"
OUT="$ROOT/output/fitness-loop-v1.mp4"

mkdir -p "$WORK"

FONT_FAMILY="${FONT_FAMILY:-DejaVu Sans}"

W=1080
H=1920
HALF=960
FPS=30

# beat file | top text | bottom text | segment duration (sec)
BEATS=(
    "beat1_tired.mp4|FEEL TIRED?|DO IT ANYWAY.|2.4"
    "beat2_shoes.mp4|WANT TO QUIT?|DO ONE MORE REP.|2.4"
    "beat3_runner.mp4|THINK YOU CAN'T PUSH FURTHER?|KEEP GOING.|2.4"
    "beat4_lift.mp4|YOUR BIGGEST OPPONENT?|IT'S NOT THE COMPETITION.\\NIT'S YOUR OWN MIND.|2.6"
    "beat5_plates.mp4|IGNORE THE WHISPERS OF WEAKNESS.|WIN THE WAR WITHIN.|2.6"
)

write_ass() {
    # $1 = output .ass path, $2 = top text, $3 = bottom text, $4 = duration
    local path="$1" top="$2" bottom="$3" dur="$4"
    local top_y=$(python3 -c "print(int(${HALF}*0.42))")
    local bot_y=$(python3 -c "print(int(${HALF}+${HALF}*0.42))")
    local end
    end=$(python3 -c "
d = $dur
h = int(d // 3600)
m = int((d % 3600) // 60)
s = d % 60
print(f'{h}:{m:02d}:{s:05.2f}')
")
    cat > "$path" <<EOF
[Script Info]
ScriptType: v4.00+
PlayResX: ${W}
PlayResY: ${H}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,${FONT_FAMILY},64,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,0,5,20,20,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,${end},Default,,0,0,0,,{\\pos(540,${top_y})}${top}
Dialogue: 0,0:00:00.00,${end},Default,,0,0,0,,{\\pos(540,${bot_y})}${bottom}
EOF
}

SEGMENTS=()
i=0
for row in "${BEATS[@]}"; do
    i=$((i + 1))
    IFS='|' read -r file top bottom dur <<< "$row"
    src="$RAW/$file"
    if [ ! -f "$src" ]; then
        echo "Missing raw clip: $src" >&2
        echo "Download it from the Higgsfield widget first (see script header)." >&2
        exit 1
    fi

    assfile="$WORK/beat${i}.ass"
    write_ass "$assfile" "$top" "$bottom" "$dur"

    seg="$WORK/beat${i}_final.mp4"
    SEGMENTS+=("$seg")

    # Top half: source clip, straight. Bottom half: mirrored, for a related
    # but distinct framing (matches the reference's two-angle split look).
    # Both forced to true grayscale + contrast lift for consistent B&W
    # across all five beats regardless of per-clip color cast.
    ffmpeg -y -ss 0.3 -t "$dur" -i "$src" -filter_complex "
        [0:v]scale=${W}:${HALF}:force_original_aspect_ratio=increase,
             crop=${W}:${HALF},
             eq=contrast=1.25:brightness=-0.02,
             hue=s=0,
             format=yuv420p[top];
        [0:v]hflip,
             scale=${W}:${HALF}:force_original_aspect_ratio=increase,
             crop=${W}:${HALF},
             eq=contrast=1.25:brightness=-0.02,
             hue=s=0,
             format=yuv420p[bot];
        [top][bot]vstack=inputs=2[stacked];
        [stacked]ass='${assfile}',fps=${FPS}[v]
    " -map "[v]" -an -c:v libx264 -pix_fmt yuv420p -crf 18 "$seg"
done

# Concatenate the 5 beats into the final loop.
LIST="$WORK/concat_list.txt"
: > "$LIST"
for seg in "${SEGMENTS[@]}"; do
    echo "file '$seg'" >> "$LIST"
done

mkdir -p "$(dirname "$OUT")"
ffmpeg -y -f concat -safe 0 -i "$LIST" -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart "$OUT"

echo
echo "Done: $OUT"
echo "Total duration target: $(python3 -c "print(2.4+2.4+2.4+2.6+2.6)")s (12-15s format default)"
