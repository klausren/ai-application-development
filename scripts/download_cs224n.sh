#!/usr/bin/env bash
# =============================================================================
# Download Stanford CS224n (Spring 2024) lecture slides
# 知乎备份脚本：下载斯坦福 CS224n 2024 春季全套课件 PDF
#
# Why a script instead of committing the PDFs?
# Stanford publishes the slides publicly at web.stanford.edu, but WITHOUT an
# explicit open-source license. Redistributing them inside this repository
# would be a copyright risk, so this repo only links to the official source.
#
# Usage / 用法:
#   bash scripts/download_cs224n.sh          # downloads into ./cs224n/
#   bash scripts/download_cs224n.sh ~/slides  # custom target directory
#
# Source: https://web.stanford.edu/class/cs224n/ (Spring 2024)
# Requires: curl. Works on macOS / Linux.
# =============================================================================
set -u

DEST="${1:-cs224n}"
BASE="https://web.stanford.edu/class/cs224n/slides"
mkdir -p "$DEST"

# lecture number | official filename
MANIFEST="
01|cs224n-spr2024-lecture01-wordvecs1.pdf
02|cs224n-spr2024-lecture02-wordvecs2.pdf
03|cs224n-spr2024-lecture03-neuralnets.pdf
04|cs224n-spr2024-lecture04-dep-parsing.pdf
05|cs224n-spr2024-lecture05-rnnlm.pdf
06|cs224n-spr2024-lecture06-fancy-rnn.pdf
07|cs224n-spr2024-lecture07-final-project.pdf
08|cs224n-spr2024-lecture08-transformers.pdf
09|cs224n-spr2024-lecture09-pretraining-updated.pdf
10|cs224n-spr2024-lecture10-prompting-rlhf.pdf
11|cs224n-spr2024-lecture11-evaluation-yann.pdf
12|cs224n-spr2024-lecture12-training-shikhar.pdf
13|cs224n-spr2024-lecture13-speech-bci.pdf
14|cs224n-spr2024-lecture14-agents-shikhar-updated.pdf
15|cs224n-spr2024-lecture15-life-after-dpo-lambert.pdf
16|cs224n-spr2024-lecture16-CNN-TreeRNN.pdf
17|cs224n-2024-lecture17-human-centered-nlp.pdf
18|cs224n-2024-lecture18-deployment-and-efficiency.pdf
19|cs224n-2024-lecture19-open-problems.pdf
"

# NOTE: lectures 17-19 use a different filename pattern (no "spr") on the
# official server -- verified against the slides directory listing.

ok=0; fail=0
echo "$MANIFEST" | while IFS='|' read -r num file; do
  [ -z "$file" ] && continue
  dest="$DEST/$file"
  if [ -s "$dest" ] && head -c 4 "$dest" | grep -q "%PDF"; then
    echo "SKIP  (exists) $file"; continue
  fi
  got=""
  for attempt in 1 2 3; do
    curl -sL --max-time 120 -o "$dest" "$BASE/$file"
    if head -c 4 "$dest" | grep -q "%PDF"; then
      echo "OK    $file ($(du -h "$dest" | cut -f1))"; got=1; break
    fi
    rm -f "$dest"; sleep 2
  done
  [ -z "$got" ] && echo "FAIL  $file  (check your network or the course site)"
done

echo ""
echo "Done. Slides saved to: $DEST"
echo "Lecture-to-week mapping: see README.md (Section: Courseware Map)."
