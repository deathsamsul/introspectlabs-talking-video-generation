import os
import subprocess
import sys
from pathlib import Path

"""
pipeline/ditto_runner.py
Thin wrapper that calls inference.py via subprocess.
Usage:
    from pipeline.ditto_runner import run_ditto

    run_ditto(
        image_path  = "samples/character.jpg",
        audio_path  = "outputs/tts_audio.wav",
        output_path = "outputs/tts_avatar_output.mp4",
    )
"""


# ---------------------------------------------------------------------------
# Default checkpoint paths (edit here or pass explicitly to run_ditto)
# ---------------------------------------------------------------------------

# Kaggle/Colab GPU path — adjust to your actual checkpoint location
DEFAULT_DATA_ROOT = "./checkpoints/ditto_pytorch"
DEFAULT_CFG_PKL   = "./checkpoints/ditto_cfg/v0.4_hubert_cfg_pytorch.pkl"

# TRT path (alternative for machines with Ampere+ GPUs)
TRT_DATA_ROOT = "./checkpoints/ditto_trt_Ampere_Plus"
TRT_CFG_PKL   = "./checkpoints/ditto_cfg/v0.4_hubert_cfg_trt.pkl"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_ditto(
    image_path:  str,
    audio_path:  str,
    output_path: str,
    data_root:   str  = DEFAULT_DATA_ROOT,
    cfg_pkl:     str  = DEFAULT_CFG_PKL,
    python_bin:  str  = sys.executable,
    inference_script: str = "inference.py",
    extra_args:  list = None,
) -> str:
    """
    Call Ditto's inference.py via subprocess.

    Args:
        image_path:        Path to source portrait image (.jpg / .png).
        audio_path:        Path to input audio (.wav, 16 kHz mono recommended).
        output_path:       Destination video path (.mp4).
        data_root:         Path to Ditto model checkpoint directory.
        cfg_pkl:           Path to Ditto config pickle.
        python_bin:        Python interpreter to use (default: current env).
        inference_script:  Path to inference.py (default: ./inference.py).
        extra_args:        Optional list of extra CLI flags for inference.py.

    Returns:
        Resolved path to the generated .mp4 file.

    Raises:
        FileNotFoundError: If any required input file is missing.
        RuntimeError:      If inference.py exits with a non-zero code.
    """
    # Resolve & validate paths
    image_path       = str(Path(image_path).resolve())
    audio_path       = str(Path(audio_path).resolve())
    output_path      = str(Path(output_path).resolve())
    inference_script = str(Path(inference_script).resolve())

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"[ditto_runner] Image not found: {image_path}")
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"[ditto_runner] Audio not found: {audio_path}")
    if not os.path.isfile(inference_script):
        raise FileNotFoundError(f"[ditto_runner] inference.py not found: {inference_script}")

    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Build the subprocess command
    cmd = [
        python_bin,
        inference_script,
        "--data_root",   data_root,
        "--cfg_pkl",     cfg_pkl,
        "--audio_path",  audio_path,
        "--source_path", image_path,
        "--output_path", output_path,
    ]
    if extra_args:
        cmd.extend(extra_args)

    print("[ditto_runner] Running Ditto inference...")
    print(f"[ditto_runner] Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"[ditto_runner] inference.py exited with code {result.returncode}."
        )

    if not os.path.isfile(output_path):
        raise RuntimeError(
            f"[ditto_runner] Inference finished but output not found: {output_path}"
        )

    print(f"[ditto_runner] Video saved → {output_path}")
    return output_path


def resolve_checkpoints(prefer_pytorch: bool = True) -> tuple[str, str]:
    """
    Auto-detect which checkpoint set to use.

    Returns:
        (data_root, cfg_pkl) tuple.
    """
    if prefer_pytorch and os.path.isdir(DEFAULT_DATA_ROOT):
        print(f"[ditto_runner] Using PyTorch checkpoints: {DEFAULT_DATA_ROOT}")
        return DEFAULT_DATA_ROOT, DEFAULT_CFG_PKL

    if os.path.isdir(TRT_DATA_ROOT):
        print(f"[ditto_runner] Using TRT checkpoints: {TRT_DATA_ROOT}")
        return TRT_DATA_ROOT, TRT_CFG_PKL

    if os.path.isdir(DEFAULT_DATA_ROOT):
        return DEFAULT_DATA_ROOT, DEFAULT_CFG_PKL

    # Return defaults and let inference.py report a clear error
    print(
        "[ditto_runner] WARNING: No checkpoint directory found. "
        f"Expected '{DEFAULT_DATA_ROOT}' or '{TRT_DATA_ROOT}'. "
        "Please download checkpoints first."
    )
    return DEFAULT_DATA_ROOT, DEFAULT_CFG_PKL


if __name__ == "__main__":
    # Quick smoke test
    data_root, cfg_pkl = resolve_checkpoints()
    run_ditto(
        image_path  = "samples/character.jpg",
        audio_path  = "samples/sample_audio.wav",
        output_path = "outputs/test_runner.mp4",
        data_root   = data_root,
        cfg_pkl     = cfg_pkl,
    )
