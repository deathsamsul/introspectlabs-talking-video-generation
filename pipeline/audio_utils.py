import os
import subprocess
from pathlib import Path


"""
pipeline/audio_utils.py
Audio helpers:
  - mp3  → wav  (FFmpeg)
  - wav  → trimmed wav at given duration  (FFmpeg)
  - wav  → looped/padded wav to reach target duration (FFmpeg)
"""

# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _run_ffmpeg(cmd: list, description: str = "") -> None:
    """Run an FFmpeg command and raise on failure."""
    full_cmd = ["ffmpeg", "-loglevel", "error", "-y"] + cmd
    print(f"[audio_utils] {description}")
    print(f"[audio_utils] running: {' '.join(full_cmd)}")
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"[audio_utils] FFmpeg failed ({description}):\n"
            f"  stdout: {result.stdout}\n"
            f"  stderr: {result.stderr}"
        )


def _ensure_dir(path: str) -> str:
    """Create parent directories and return the resolved path."""
    p = str(Path(path).resolve())
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    return p


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def mp3_to_wav(mp3_path: str, wav_path: str) -> str:
    """
    Convert an MP3 file to a 16 kHz mono WAV (the format Ditto expects).
    Args:
        mp3_path: Path to the source .mp3 file.
        wav_path: Destination .wav path.
    Returns:
        Resolved path to the output WAV file.
    """
    mp3_path = str(Path(mp3_path).resolve())
    wav_path = _ensure_dir(wav_path)

    if not os.path.isfile(mp3_path):
        raise FileNotFoundError(f"[audio_utils] mp3 not found: {mp3_path}")

    _run_ffmpeg(
        ["-i", mp3_path, "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le", wav_path],
        description=f"mp3→wav  {mp3_path} → {wav_path}",
    )
    print(f"[audio_utils] wav saved → {wav_path}")
    return wav_path


def wav_to_wav(input_wav: str, output_wav: str) -> str:
    """
    Re-encode any WAV to 16 kHz mono PCM WAV (normalise sample rate/channels).
    Args:
        input_wav:  Source .wav path.
        output_wav: Destination .wav path.
    Returns:
        Resolved path to the output WAV file.
    """

    input_wav  = str(Path(input_wav).resolve())
    output_wav = _ensure_dir(output_wav)

    if not os.path.isfile(input_wav):
        raise FileNotFoundError(f"[audio_utils] wav not found: {input_wav}")

    _run_ffmpeg(
        ["-i", input_wav, "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le", output_wav],
        description=f"wav→wav  {input_wav} → {output_wav}",
    )
    print(f"[audio_utils] wav saved → {output_wav}")
    return output_wav


def get_audio_duration(wav_path: str) -> float:
    """
    Return the duration of a WAV file in seconds using FFprobe.
    Args:
        wav_path: Path to the .wav file.
    Returns:
        Duration in seconds (float).
    """
    wav_path = str(Path(wav_path).resolve())
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        wav_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"[audio_utils] ffprobe failed: {result.stderr}")
    return float(result.stdout.strip())


def cut_audio_to_duration(input_wav: str, output_wav: str, duration_sec: float) -> str:
    """
    Cut (or loop/pad) a WAV file to exactly *duration_sec* seconds.
    - If the input is longer  → trim to duration_sec.
    - If the input is shorter → loop until duration_sec is reached.
    Args:
        input_wav:    Source .wav path.
        output_wav:   Destination .wav path.
        duration_sec: Target duration in seconds.
    Returns:
        Resolved path to the output WAV file.
    """
    input_wav  = str(Path(input_wav).resolve())
    output_wav = _ensure_dir(output_wav)

    if not os.path.isfile(input_wav):
        raise FileNotFoundError(f"[audio_utils] input wav not found: {input_wav}")

    src_duration = get_audio_duration(input_wav)

    if src_duration >= duration_sec:
        # Trim
        _run_ffmpeg(
            ["-i", input_wav, "-t", str(duration_sec),
             "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le", output_wav],
            description=f"trim to {duration_sec}s",
        )
    else:
        # Loop until long enough, then trim
        _run_ffmpeg(
            ["-stream_loop", "-1", "-i", input_wav,
             "-t", str(duration_sec),
             "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le", output_wav],
            description=f"loop+trim to {duration_sec}s",
        )

    print(f"[audio_utils] cut/padded → {output_wav}  ({duration_sec}s)")
    return output_wav


def ensure_wav(audio_path: str, output_wav: str) -> str:
    """
    Accept either .mp3 or .wav and return a normalised 16 kHz mono WAV.
    Args:
        audio_path: Path to .mp3 or .wav file.
        output_wav: Destination .wav path.
    Returns:
        Resolved path to the output WAV file.
    """
    ext = Path(audio_path).suffix.lower()
    if ext == ".mp3":
        return mp3_to_wav(audio_path, output_wav)
    elif ext in (".wav", ".wave"):
        return wav_to_wav(audio_path, output_wav)
    else:
        # Try converting unknown format via FFmpeg anyway
        print(f"[audio_utils] unknown ext '{ext}', attempting generic conversion…")
        return mp3_to_wav(audio_path, output_wav)


if __name__ == "__main__":
    # Quick smoke test
    import sys
    if len(sys.argv) < 2:
        print("Usage: python audio_utils.py <input.mp3|wav>")
        sys.exit(1)
    src = sys.argv[1]
    out_wav = "/tmp/test_out.wav"
    ensure_wav(src, out_wav)
    dur = get_audio_duration(out_wav)
    print(f"Duration: {dur:.2f}s")

    for sec in (5, 10, 20):
        cut_audio_to_duration(out_wav, f"/tmp/test_{sec}s.wav", sec)
