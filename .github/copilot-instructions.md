# Project: One Piece Anime Subtitle & OCR Pipeline

## Context
I am building a Python-based pipeline to process anime video files (specifically One Piece). The goal is to generate a single subtitle file that contains both spoken audio transcription and OCR-translated on-screen Japanese text.

## Hardware & Environment
- **GPU:** NVIDIA RTX 3060 (8GB VRAM).
- **Execution:** Local-only. No cloud APIs.
- **Language:** Python 3.10+.

## Tech Stack
1.  **Audio Transcription:** `whisperx` (Model: `large-v2` or `large-v3`, Compute: `float16`).
2.  **OCR:** `manga-ocr` (Vision Transformer specialized for Japanese manga/anime fonts).
3.  **Translation:** `Helsinki-NLP/opus-mt-ja-en` (MarianMT) running via HuggingFace Transformers.
4.  **Video Processing:** `opencv-python` (cv2) for frame extraction and preprocessing.

## Architecture & Constraints
### 1. VRAM Management (Critical)
- **Constraint:** The RTX 3060 cannot hold Whisper, Manga-OCR, and MarianMT in memory simultaneously.
- **Strategy:** Implement a strict **Sequential Pipeline**:
    1.  Load Whisper -> Transcribe -> Unload Model -> `gc.collect()` / `torch.cuda.empty_cache()`.
    2.  Load Manga-OCR -> Scan Video -> Unload Model -> Clean GPU.
    3.  Load Translator -> Translate Text -> Unload Model -> Clean GPU.

### 2. OCR Optimization
- **Do NOT** scan every frame.
- **Preprocessing:** Convert frames to Grayscale and apply CLAHE (Contrast Limited Adaptive Histogram Equalization). Do NOT use binary thresholding (B&W) as it degrades transformer model accuracy.
- **Filtering:** Use OpenCV to calculate frame difference (hashing or pixel diff). Only run OCR if the scene has changed or text has appeared.

### 3. Output Formatting
- **Format:** Save as `.srt` or `.ass`.
- **Differentiation:**
    - **Spoken Audio:** Standard formatting.
    - **OCR Text:** Must be visually distinct (e.g., `<font color="#00FFFF">` for Cyan or similar distinct color).

## Coding Style
- Use `pathlib` for file handling.
- Use `subprocess` only if a Python library alternative is unavailable or significantly slower.
- Error handling: Gracefully skip corrupt frames without crashing the batch job.