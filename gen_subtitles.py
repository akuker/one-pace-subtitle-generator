#!/usr/bin/env python3
"""
One Piece Anime Subtitle & OCR Pipeline

Main application for generating subtitles from video files.
Processes audio transcription, OCR of on-screen text, translation, merging, and SRT conversion.
"""

import argparse
import sys
from pathlib import Path
import pysubs2
import time

# Import processors
from lib.whisperx_processor import WhisperXProcessor
from lib.ocr_processor import OCRProcessor
from lib.translation_processor import TranslationProcessor
from lib.merger_processor import MergerProcessor
from lib.srt_converter import SRTConverter
from lib.timing_metrics import TimingMetrics


def get_video_files(input_path: Path) -> list[Path]:
    """Get list of video files (.mp4, .mkv) from input path."""
    if input_path.is_file():
        if input_path.suffix.lower() in ['.mp4', '.mkv']:
            return [input_path]
        else:
            print(f"Error: {input_path} is not a supported video file (.mp4 or .mkv)")
            return []
    elif input_path.is_dir():
        videos = []
        for ext in ['*.mp4', '*.mkv']:
            videos.extend(input_path.glob(ext))
        return sorted(videos)
    else:
        print(f"Error: {input_path} does not exist or is not a file/directory")
        return []


def phase_1_audio_transcription(video_files, force, verbose, intermediates, audio_language, output_language, timing):
    """Phase 1: Audio transcription using WhisperX."""
    phase_name = "audio_transcription"
    if verbose:
        print("Starting Phase 1: Audio Transcription")
    WhisperXProcessor.init()
    for video_path in video_files:
        base_name = video_path.stem
        video_dir = video_path.parent
        audio_output = video_dir / f"{base_name}.1.audio_only.ass"
        if force or not audio_output.exists():
            timing.start(str(video_path), phase_name)
            WhisperXProcessor.process(str(video_path), str(audio_output), verbose, intermediates, audio_language, output_language)
            timing.stop(str(video_path), phase_name)
        elif verbose:
            print(f"Skipping audio transcription for {video_path} - output exists")
    WhisperXProcessor.tear_down()


def phase_2_ocr_japanese(video_files, force, verbose, intermediates, audio_language, output_language, timing):
    """Phase 2: OCR of on-screen Japanese text."""
    phase_name = "ocr_japanese"
    if verbose:
        print("Starting Phase 2: OCR Japanese Text")
    OCRProcessor.init()
    for video_path in video_files:
        base_name = video_path.stem
        video_dir = video_path.parent
        ocr_output = video_dir / f"{base_name}.2.forced.jp.ass"
        if force or not ocr_output.exists():
            timing.start(str(video_path), phase_name)
            OCRProcessor.process(str(video_path), str(ocr_output), verbose, intermediates, audio_language, output_language)
            timing.stop(str(video_path), phase_name)
        elif verbose:
            print(f"Skipping OCR for {video_path} - output exists")
    OCRProcessor.tear_down()


def phase_3_translation(video_files, force, verbose, intermediates, audio_language, output_language, timing):
    """Phase 3: Translation of OCR text."""
    phase_name = "translation"
    if verbose:
        print("Starting Phase 3: Translation")
    TranslationProcessor.init()
    for video_path in video_files:
        base_name = video_path.stem
        video_dir = video_path.parent
        trans_output = video_dir / f"{base_name}.3.forced.en.ass"
        if force or not trans_output.exists():
            timing.start(str(video_path), phase_name)
            TranslationProcessor.process(str(video_path), str(trans_output), verbose, intermediates, audio_language, output_language)
            timing.stop(str(video_path), phase_name)
        elif verbose:
            print(f"Skipping translation for {video_path} - output exists")
    TranslationProcessor.tear_down()


def phase_4_merge_subtitles(video_files, force, verbose, intermediates, audio_language, output_language, timing):
    """Phase 4: Merge audio and translated OCR subtitles."""
    phase_name = "merge_subtitles"
    if verbose:
        print("Starting Phase 4: Merging Subtitles")
    MergerProcessor.init()
    for video_path in video_files:
        base_name = video_path.stem
        video_dir = video_path.parent
        merged_output = video_dir / f"{base_name}.ass"
        if force or not merged_output.exists():
            timing.start(str(video_path), phase_name)
            MergerProcessor.process(str(video_path), str(merged_output), verbose, intermediates, audio_language, output_language)
            timing.stop(str(video_path), phase_name)
        elif verbose:
            print(f"Skipping merging for {video_path} - output exists")
    MergerProcessor.tear_down()


def phase_5_convert_to_srt(video_files, force, verbose, intermediates, audio_language, output_language, timing):
    """Phase 5: Convert ASS to SRT."""
    phase_name = "convert_to_srt"
    if verbose:
        print("Starting Phase 5: Converting to SRT")
    SRTConverter.init()
    for video_path in video_files:
        base_name = video_path.stem
        video_dir = video_path.parent
        srt_output = video_dir / f"{base_name}.srt"
        if force or not srt_output.exists():
            timing.start(str(video_path), phase_name)
            SRTConverter.process(str(video_path), str(srt_output), verbose, intermediates, audio_language, output_language)
            timing.stop(str(video_path), phase_name)
        elif verbose:
            print(f"Skipping SRT conversion for {video_path} - output exists")
    SRTConverter.tear_down()


def main():
    parser = argparse.ArgumentParser(
        description="Generate subtitles for One Piece anime videos"
    )
    parser.add_argument(
        'input_path',
        type=Path,
        help="Path to video file or directory containing video files"
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help="Force regeneration of all subtitle files, even if they exist"
    )
    parser.add_argument(
        '--intermediates',
        action='store_true',
        help="Save intermediate files from processing steps"
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Enable verbose output"
    )
    parser.add_argument(
        '--audio-language',
        default='en',
        help="Language code for audio transcription (default: en)"
    )
    parser.add_argument(
        '--output-language',
        default='en',
        help="Language code for subtitle output (default: en)"
    )

    args = parser.parse_args()

    input_path = args.input_path
    force = args.force
    intermediates = args.intermediates
    verbose = args.verbose
    audio_language = args.audio_language
    output_language = args.output_language

    # Echo recognized arguments
    print(f"Input path: {input_path}")
    print(f"Audio language: {audio_language}")
    print(f"Output language: {output_language}")
    if force:
        print("Force regeneration enabled")
    if intermediates:
        print("Saving intermediates")
    if verbose:
        print("Verbose mode enabled")

    timing = TimingMetrics()
    start_time = time.time()

    video_files = get_video_files(input_path)
    if not video_files:
        sys.exit(1)

    # Execute all phases
    phase_1_audio_transcription(video_files, force, verbose, intermediates, audio_language, output_language, timing)
    phase_2_ocr_japanese(video_files, force, verbose, intermediates, audio_language, output_language, timing)
    phase_3_translation(video_files, force, verbose, intermediates, audio_language, output_language, timing)
    phase_4_merge_subtitles(video_files, force, verbose, intermediates, audio_language, output_language, timing)
    phase_5_convert_to_srt(video_files, force, verbose, intermediates, audio_language, output_language, timing)

    # Print per-file summaries
    for video in video_files:
        timing.print_stats(filename=str(video))

    # Print final statistics
    total_execution_time = time.time() - start_time
    print(f"\nTotal execution time: {total_execution_time:.2f}s")
    timing.print_stats()

    if verbose:
        print("Processing complete.")


if __name__ == "__main__":
    main()
