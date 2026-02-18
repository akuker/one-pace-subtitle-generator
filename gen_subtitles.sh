#!/bin/bash
# Baseline script to generate subtitles using WhisperX for all .mp4 and .mkv files in the current directory.

# Loop over all .mp4 files in the current directory
for file in *.mp4 *.mkv; do
  # Check if file exists (in case there are no matches)
  [ -e "$file" ] || continue

  echo "Processing: $file"
  whisperx "$file" --compute_type float32 --model large-v2 --align_model WAV2VEC2_ASR_LARGE_LV60K_960H --language en
done

