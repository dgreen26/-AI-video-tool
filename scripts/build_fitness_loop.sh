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
# Requires ffmpeg on PATH. If your box has no bold sans-serif font at the
# path below, set FONT=/path/to/your/Bold.ttf before running.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW="$ROOT/assets/fitness-loop/raw"
WORK="$ROOT/assets/fitness-loop/work"
OUT="$ROOT/output/fitness-loop-v1.mp4"

mkdir -p "$WORK"

FONT="${FONT:-}"
if [ -z "$FONT" ]; then
    for candidate in \
        /usr/share/fonts/truetype/dejavu/DejaVu-Sans-Bold.ttf \
        /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf \
        /usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf \
        /System/Library/Fonts/Supplemental/Arial\ Bold.ttf \
        /Library/Fonts/Arial\ Bold.ttf \
        /usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf; do
        if [ -f "$candidate" ]; then
            FONT="$candidate"
            break
        fi
    done
fi
if [ -z "$FONT" ]; then
    echo "No bold sans-serif font found. Set FONT=/path/to/Bold.ttf and re-run." >&2
    exit 1
fi
echo "Using font: $FONT"

W=1080
H=1920
HALF=960
FPS=30

# beat file | top text | bottom text | segment duration (sec)
BEATS=(
    "beat1_tired.mp4|FEEL TIRED?|DO IT ANYWAY.|2.4"
    "beat2_shoes.mp4|WANT TO QUIT?|DO ONE MORE REP.|2.4"
    "beat3_runner.mp4|THINK YOU CAN'T PUSH FURTHER?|KEEP GOING.|2.4"
    "beat4_lift.mp4|YOUR BIGGEST OPPONENT?|IT'S NOT THE COMPETITION. IT'S YOUR OWN MIND.|2.6"
    "beat5_plates.mp4|IGNORE THE WHISPERS OF WEAKNESS.|WIN THE WAR WITHIN.|2.6"
)

esc() {
    # Escape text for ffmpeg drawtext: backslash, colon, single quote.
    printf '%s' "$1" | sed -e "s/\\\\/\\\\\\\\/g" -e "s/:/\\\\:/g" -e "s/'/\\\\'/g"
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

    top_esc="$(esc "$top")"
    bottom_esc="$(esc "$bottom")"
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
        [stacked]drawtext=fontfile='${FONT}':text='${top_esc}':
             fontcolor=white:fontsize=64:borderw=4:bordercolor=black:
             x=(w-text_w)/2:y=${HALF}*0.42-text_h/2:line_spacing=8,
        drawtext=fontfile='${FONT}':text='${bottom_esc}':
             fontcolor=white:fontsize=64:borderw=4:bordercolor=black:
             x=(w-text_w)/2:y=${HALF}+${HALF}*0.42-text_h/2:line_spacing=8,
        fps=${FPS}[v]
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
