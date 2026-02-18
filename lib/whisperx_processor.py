import os
import gc
import torch
import whisperx
import pysubs2
from pathlib import Path

class WhisperXProcessor:
    _initialized = False
    model = None
    align_model = None

    @classmethod
    def init(cls):
        """Initialize WhisperX model and setup."""
        if cls._initialized:
            return
        print("Initializing WhisperX model...")
        
        # Set HuggingFace cache directory
        models_dir = Path.cwd() / "models"
        models_dir.mkdir(exist_ok=True)
        os.environ["HF_HOME"] = str(models_dir)
        
        # Load WhisperX model
        cls.model = whisperx.load_model("large-v2", device="cuda", compute_type="float16")
        
        # Load alignment model for English
        cls.align_model = whisperx.load_align_model(language_code="en", device="cuda")
        
        cls._initialized = True
        print("WhisperX model initialized.")

    @classmethod
    def process(cls, input_filename, output_filename, verbose=False, intermediates=False, audio_language='en', output_language='en'):
        """Process audio transcription."""
        if not cls._initialized:
            raise RuntimeError("WhisperXProcessor not initialized. Call init() first.")
        
        if verbose:
            print(f"Processing WhisperX for {input_filename} -> {output_filename} (language: {audio_language})")
        
        # Load audio
        audio = whisperx.load_audio(input_filename)
        
        # Transcribe
        result = cls.model.transcribe(audio, batch_size=16, language=audio_language)
        
        # Align
        metadata = whisperx.load_metadata(audio_language)
        result_aligned = whisperx.align(result["segments"], cls.align_model, metadata, audio, "cuda")
        
        # Create ASS subtitles
        subs = pysubs2.Subtitles()
        for segment in result_aligned["segments"]:
            start_ms = int(segment["start"] * 1000)
            end_ms = int(segment["end"] * 1000)
            text = segment["text"]
            subs.append(pysubs2.Subtitle(start=start_ms, end=end_ms, text=text))
        
        # Save as ASS
        subs.save(output_filename, format_="ass")
        
        if verbose:
            print(f"Subtitles saved to {output_filename}")

    @classmethod
    def tear_down(cls):
        """Unload WhisperX model."""
        if not cls._initialized:
            return
        print("Tearing down WhisperX model...")
        
        # Unload models
        if cls.model is not None:
            del cls.model
            cls.model = None
        if cls.align_model is not None:
            del cls.align_model
            cls.align_model = None
        
        # Clean up GPU memory
        gc.collect()
        torch.cuda.empty_cache()
        
        cls._initialized = False
        print("WhisperX model torn down.")