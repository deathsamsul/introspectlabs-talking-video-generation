import os
import asyncio
import subprocess
from pathlib import Path

"""
pipeline/tts.py
Text → TTS audio (mp3 or wav)
Supported backends (in priority order):
  1. edge-tts   (Microsoft Edge TTS - free, no API key, best quality)
  2. gtts        (Google TTS - free, no API key)
Install:
    pip install edge-tts gtts
"""

# ---------------------------------------------------------------------------
# Edge-TTS backend (preferred)
# ---------------------------------------------------------------------------

EDGE_TTS_VOICES = {
    "neutral":    "en-US-AriaNeural",
    "confident":  "en-US-GuyNeural",
    "angry":      "en-US-TonyNeural",
    "sad":        "en-US-JennyNeural",
    "teasing":    "en-US-AnaNeural",
    "intense":    "en-US-DavisNeural",
}

EDGE_TTS_STYLES = {
    "neutral":   "neutral",
    "confident": "newscast",
    "angry":     "angry",
    "sad":       "sad",
    "teasing":   "cheerful",
    "intense":   "excited",
}


async def _edge_tts_generate(text: str, output_path: str, emotion: str = "neutral") -> None:
    """Async helper that calls edge-tts to generate speech."""
    import edge_tts

    voice = EDGE_TTS_VOICES.get(emotion, EDGE_TTS_VOICES["neutral"])
    style = EDGE_TTS_STYLES.get(emotion, "neutral")

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def generate_tts_edge(text: str, output_path: str, emotion: str = "neutral") -> str:
    """
    Generate TTS audio using edge-tts.
    Args:
        text:        Input text string.
        output_path: Destination file path (.mp3 or .wav).
        emotion:     Emotion label (neutral / confident / angry / sad / teasing / intense).
    Returns:
        Absolute path to generated audio file.
    """
    output_path = str(Path(output_path).resolve())
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    asyncio.run(_edge_tts_generate(text, output_path, emotion))
    print(f"[tts] edge-tts → {output_path}")
    return output_path


# ---------------------------------------------------------------------------
# gTTS backend (fallback)
# ---------------------------------------------------------------------------

def generate_tts_gtts(text: str, output_path: str, emotion: str = "neutral") -> str:
    """
    Generate TTS audio using gTTS (Google Text-to-Speech).
    Note: gTTS does not support emotion styles.
    Args:
        text:        Input text string.
        output_path: Destination file path (.mp3).
        emotion:     Ignored (gTTS has no style support).
    Returns:
        Absolute path to generated audio file.
    """
    from gtts import gTTS

    output_path = str(Path(output_path).resolve())
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(output_path)
    print(f"[tts] gtts → {output_path}")
    return output_path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_tts(text: str, output_path: str, emotion: str = "neutral") -> str:
    """
    Generate TTS audio. Tries edge-tts first, falls back to gTTS.
    Args:
        text:        Input text string.
        output_path: Destination file path (.mp3 or .wav).
        emotion:     Emotion label used to select voice / style.
    Returns:
        Absolute path to generated audio file.
    Raises:
        RuntimeError: If both backends fail.
    """
    if not text or not text.strip():
        raise ValueError("[tts] Text input is empty.")

    # Try edge-tts first
    try:
        import edge_tts  # noqa: F401
        return generate_tts_edge(text, output_path, emotion)
    except ImportError:
        print("[tts] edge-tts not installed, trying gtts...")
    except Exception as e:
        print(f"[tts] edge-tts failed: {e}, trying gtts...")

    # Fallback: gTTS
    try:
        import gtts  # noqa: F401
        # gTTS only produces mp3; adjust extension if needed
        mp3_path = str(Path(output_path).with_suffix(".mp3"))
        result = generate_tts_gtts(text, mp3_path, emotion)
        # If caller asked for mp3, we are done
        if output_path.endswith(".mp3"):
            return result
        # Otherwise return mp3 path; audio_utils will convert later
        return result
    except ImportError:
        pass
    except Exception as e:
        print(f"[tts] gtts failed: {e}")

    raise RuntimeError(
        "[tts] No TTS backend available. "
        "Install at least one: pip install edge-tts  OR  pip install gtts"
    )


if __name__ == "__main__":
    # Quick smoke test
    sample_text = (
        "I do not speak to impress people. "
        "I speak only when silence becomes heavier than truth."
    )
    out = generate_tts(sample_text, "/tmp/test_tts.mp3", emotion="confident")
    print("Generated:", out)
