import argparse
import os
import sys
import time
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so pipeline imports work correctly
# regardless of where the script is invoked from.
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


#TODO: create this pipelines functions 
# from pipeline.tts import generate_tts
# from pipeline.audio_utils import ensure_wav, cut_audio_to_duration, get_audio_duration
# from pipeline.ditto_runner import run_ditto, resolve_checkpoints
# from pipeline.emotion_utils import load_emotion_config, get_emotion_params, is_emotion_supported



# module docs for helper functions for debugging and testinf
"""
generate_avatar.py
PersonaMatrix – Talking Avatar Generator
=========================================
Converts a static character portrait + text (or audio) into a talking avatar video
using Ditto TalkingHead.

Usage examples:
    # Text input with emotion
    python generate_avatar.py \
        --image samples/character.jpg \
        --text "I do not speak to impress people." \
        --emotion confident \
        --output outputs/tts_avatar_output.mp4

    # Pre-existing audio input (skip TTS)
    python generate_avatar.py \
        --image samples/character.jpg \
        --audio samples/sample_audio.wav \
        --emotion neutral \
        --output outputs/audio_avatar_output.mp4

    # Generate 3 duration videos from a source audio
    python generate_avatar.py \
        --image samples/character.jpg \
        --audio samples/sample_audio.wav \
        --generate-duration-tests \
        --output outputs/generated.mp4

Optional flags:
    --data-root   PATH   Override Ditto checkpoint directory.
    --cfg-pkl     PATH   Override Ditto config pickle path.
"""



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print_banner():
    print("=" * 60)
    print("  PersonaMatrix – Talking Avatar Generator")
    print("=" * 60)


def _validate_image(image_path: str) -> str:
    image_path = str(Path(image_path).resolve())
    if not os.path.isfile(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        sys.exit(1)
    ext = Path(image_path).suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        print(f"[WARNING] Unexpected image extension '{ext}'. Proceeding anyway.")
    return image_path


def _ensure_output_dir(output_path: str) -> str:
    output_path = str(Path(output_path).resolve())
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    return output_path


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

def generate_avatar(
    image_path:  str,
    text:        str   = None,
    audio_path:  str   = None,
    emotion:     str   = "neutral",
    output_path: str   = "outputs/avatar_response.mp4",
    data_root:   str   = None,
    cfg_pkl:     str   = None, ) -> dict:
    """
    Full pipeline: text/audio + image → talking avatar video.
    Returns a dict with keys: output_path, generation_time_sec, audio_path.
    """
    t_start = time.time()

    # --- Resolve checkpoints ---
    if data_root is None or cfg_pkl is None:
        _data_root, _cfg_pkl = resolve_checkpoints()
        data_root = data_root or _data_root
        cfg_pkl   = cfg_pkl   or _cfg_pkl

    # --- Validate inputs ---
    if not text and not audio_path:
        raise ValueError("Provide either --text or --audio.")
    image_path  = _validate_image(image_path)
    output_path = _ensure_output_dir(output_path)

    # --- Load emotion config ---
    emotion_cfg = load_emotion_config()
    emo_params  = get_emotion_params(emotion, emotion_cfg)
    print(f"\n[pipeline] Emotion      : {emotion}")
    print(f"[pipeline]   ditto_emo_id={emo_params['ditto_emo_id']}  "
          f"supported={emo_params['supported']}")
    if not is_emotion_supported(emotion, emotion_cfg):
        print(f"[pipeline]   NOTE: '{emotion}' is approximated – "
              f"see emotion_mapping.json for details.")

    # --- Step 1: Generate / resolve audio ---
    with tempfile.TemporaryDirectory() as tmpdir:

        if text:
            print(f"\n[pipeline] Step 1 – TTS: '{text[:60]}{'...' if len(text)>60 else ''}'")
            tmp_mp3 = os.path.join(tmpdir, "tts_raw.mp3")
            generate_tts(text, tmp_mp3, emotion=emotion)

            # Convert to 16 kHz mono WAV for Ditto
            final_wav = os.path.join(tmpdir, "tts_audio.wav")
            ensure_wav(tmp_mp3, final_wav)

            # Also save a copy to outputs/
            tts_out_wav = _ensure_output_dir(
                os.path.join(os.path.dirname(output_path), "tts_audio.wav")
            )
            import shutil
            shutil.copy2(final_wav, tts_out_wav)
            print(f"[pipeline] TTS wav saved → {tts_out_wav}")

        else:
            print(f"\n[pipeline] Step 1 – Audio provided: {audio_path}")
            final_wav = os.path.join(tmpdir, "input_norm.wav")
            ensure_wav(audio_path, final_wav)

        audio_dur = get_audio_duration(final_wav)
        print(f"[pipeline] Audio duration: {audio_dur:.2f}s")

        # --- Step 2: Run Ditto inference ---
        print(f"\n[pipeline] Step 2 – Ditto inference…")
        t_ditto = time.time()
        run_ditto(
            image_path  = image_path,
            audio_path  = final_wav,
            output_path = output_path,
            data_root   = data_root,
            cfg_pkl     = cfg_pkl,
        )
        ditto_time = time.time() - t_ditto

    total_time = time.time() - t_start
    print("\n" + "=" * 60)
    print(f"  Output video    : {output_path}")
    print(f"  Ditto time      : {ditto_time:.1f}s")
    print(f"  Total time      : {total_time:.1f}s")
    print("=" * 60 + "\n")

    return {
        "output_path":         output_path,
        "generation_time_sec": round(total_time, 2),
        "ditto_time_sec":      round(ditto_time, 2),
        "audio_duration_sec":  round(audio_dur, 2),
    }


def generate_duration_tests(
    image_path: str,
    audio_path: str,
    output_dir: str  = "outputs",
    data_root:  str  = None,
    cfg_pkl:    str  = None, ) -> list[dict]:
    """
    Generate three test videos at 5s, 10s, and 20s from a sample audio.
    Returns list of result dicts.
    """
    if data_root is None or cfg_pkl is None:
        _data_root, _cfg_pkl = resolve_checkpoints()
        data_root = data_root or _data_root
        cfg_pkl   = cfg_pkl   or _cfg_pkl

    image_path = _validate_image(image_path)
    os.makedirs(output_dir, exist_ok=True)

    results = []
    for duration in (5, 10, 20):
        print(f"\n{'='*60}")
        print(f"  Generating {duration}s test video…")
        print(f"{'='*60}")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Normalise source audio
            norm_wav = os.path.join(tmpdir, "norm.wav")
            ensure_wav(audio_path, norm_wav)

            # Cut to target duration
            cut_wav = os.path.join(tmpdir, f"cut_{duration}s.wav")
            cut_audio_to_duration(norm_wav, cut_wav, duration)

            out_mp4 = os.path.join(output_dir, f"generated_{duration}s.mp4")
            t0 = time.time()
            run_ditto(
                image_path  = image_path,
                audio_path  = cut_wav,
                output_path = out_mp4,
                data_root   = data_root,
                cfg_pkl     = cfg_pkl,
            )
            elapsed = time.time() - t0

        print(f"  {out_mp4}  ({elapsed:.1f}s)")
        results.append({"duration": duration, "output": out_mp4, "time_sec": round(elapsed, 2)})

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="PersonaMatrix – Talking Avatar Generator",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Required
    p.add_argument(
        "--image", required=True,
        help="Path to source portrait image (.jpg / .png)",
    )

    # Input source: one of text or audio
    grp = p.add_mutually_exclusive_group()
    grp.add_argument(
        "--text", default=None,
        help="Text string to synthesise with TTS and then animate.",
    )
    grp.add_argument(
        "--audio", default=None,
        help="Path to pre-existing audio file (.wav or .mp3). Skips TTS.",
    )

    p.add_argument(
        "--emotion", default="neutral",
        help=(
            "Emotion label. One of: neutral, confident, angry, sad, teasing, intense.\n"
            "Default: neutral"
        ), )
    
    p.add_argument(
        "--output", default="outputs/avatar_response.mp4",
        help="Path for the output video (.mp4). Default: outputs/avatar_response.mp4",)

    # Duration test mode
    p.add_argument(
        "--generate-duration-tests", action="store_true",
        help=(
            "Generate 3 test videos at 5s, 10s, and 20s from --audio.\n"
            "Requires --audio. Output goes to the same directory as --output."
        ),)

    # Checkpoint overrides
    p.add_argument("--data-root", default=None, help="Override Ditto checkpoint directory.")
    p.add_argument("--cfg-pkl",   default=None, help="Override Ditto config pickle path.")

    return p


def main():
    _print_banner()
    parser = build_parser()
    args   = parser.parse_args()

    # ── Duration test mode ───────────────────────────────────────────────
    if args.generate_duration_tests:
        if not args.audio:
            print("[ERROR] --generate-duration-tests requires --audio.")
            sys.exit(1)
        output_dir = str(Path(args.output).parent)
        results = generate_duration_tests(
            image_path = args.image,
            audio_path = args.audio,
            output_dir = output_dir,
            data_root  = args.data_root,
            cfg_pkl    = args.cfg_pkl,)
        
        print("\nDuration test summary:")
        for r in results:
            print(f"  {r['duration']:>3}s  →  {r['output']}  ({r['time_sec']}s)")
        return

    # ── Normal single-video mode ─────────────────────────────────────────
    if not args.text and not args.audio:
        print("[ERROR] Provide either --text or --audio.")
        parser.print_help()
        sys.exit(1)

    result = generate_avatar(
        image_path  = args.image,
        text        = args.text,
        audio_path  = args.audio,
        emotion     = args.emotion,
        output_path = args.output,
        data_root   = args.data_root,
        cfg_pkl     = args.cfg_pkl,)

    print(f"Output path      : {result['output_path']}")
    print(f"Generation time  : {result['generation_time_sec']}s")


if __name__ == "__main__":
    main()
