# Setup Guide – PersonaMatrix Talking Avatar

This guide covers environment setup for running Ditto TalkingHead on **Kaggle (T4 GPU)** and locally.

---

## Environment Details

| Item | Value |
|---|---|
| Platform tested | Kaggle Notebooks (T4 x2) |
| OS | Ubuntu 20.04 |
| Python | 3.10 |
| CUDA | 11.8 |
| PyTorch | 2.x (Kaggle default) |
| GPU | Tesla T4 (Kaggle free tier) |

---

## Step 1 – Clone the Repository

```bash
git clone https://github.com/antgroup/ditto-talkinghead
cd ditto-talkinghead
```

---

## Step 2 – Install System Dependencies

```bash
# FFmpeg (required for audio/video processing)
sudo apt-get update -qq
sudo apt-get install -y ffmpeg

# Verify
ffmpeg -version
```

---

## Step 3 – Install Python Dependencies

### Option A: Conda (recommended for local setup)

```bash
conda env create -f environment.yaml
conda activate ditto
```

### Option B: Pip (for Kaggle / Colab)

Install the core Ditto dependencies first:

```bash
pip install \
    librosa \
    tqdm \
    filetype \
    imageio \
    opencv-python-headless \
    scikit-image \
    cython \
    imageio-ffmpeg \
    colored \
    numpy==2.0.1
```

Then install the PersonaMatrix extras:

```bash
pip install edge-tts gtts
```

**Note on TensorRT:** The TRT model requires `tensorrt==8.6.1`, which needs matching CUDA/cuDNN libraries. On Kaggle with T4, use the **PyTorch checkpoint** instead (no TensorRT needed).

---

## Step 4 – Download Checkpoints

```bash
git lfs install
git clone https://huggingface.co/digital-avatar/ditto-talkinghead checkpoints
```

The `checkpoints/` directory should contain:

```
checkpoints/
├── ditto_cfg/
│   ├── v0.4_hubert_cfg_pytorch.pkl   ← use this on Kaggle/T4
│   ├── v0.4_hubert_cfg_trt.pkl
│   └── v0.4_hubert_cfg_trt_online.pkl
├── ditto_pytorch/                     ← PyTorch model (no TRT required)
│   ├── aux_models/
│   └── models/
└── ditto_trt_Ampere_Plus/             ← TRT model (Ampere GPU only)
```

---

## Step 5 – Add PersonaMatrix Files

Copy or create these files inside `ditto-talkinghead/`:

```
pipeline/
  __init__.py
  tts.py
  audio_utils.py
  ditto_runner.py
  emotion_utils.py
configs/
  emotion_mapping.json
samples/
  character.jpg        ← add your portrait image here
  sample_audio.wav     ← add a sample wav here
generate_avatar.py
README.md
setup.md
technical_report.md
```

---

## Step 6 – Smoke Test

Run a quick inference test to confirm everything works:

```bash
python inference.py \
    --data_root  ./checkpoints/ditto_pytorch \
    --cfg_pkl    ./checkpoints/ditto_cfg/v0.4_hubert_cfg_pytorch.pkl \
    --audio_path ./example/audio.wav \
    --source_path ./example/image.png \
    --output_path ./tmp/smoke_test.mp4
```

If `./tmp/smoke_test.mp4` is created, the base Ditto install is working.

---

## Step 7 – Run PersonaMatrix Pipeline

```bash
python generate_avatar.py \
    --image   samples/character.jpg \
    --text    "I do not speak to impress people." \
    --emotion confident \
    --output  outputs/tts_avatar_output.mp4
```

---

## Common Setup Issues & Fixes

| Error | Fix |
|---|---|
| `ModuleNotFoundError: librosa` | `pip install librosa` |
| `ModuleNotFoundError: edge_tts` | `pip install edge-tts` |
| `ffmpeg: command not found` | `sudo apt install ffmpeg` or `conda install -c conda-forge ffmpeg` |
| TRT engine incompatible with GPU | Switch to PyTorch checkpoints: use `ditto_pytorch/` + `v0.4_hubert_cfg_pytorch.pkl` |
| `git lfs` not installed | `sudo apt install git-lfs && git lfs install` |
| CUDA out of memory | Use one T4 instead of T4 x2; reduce `sampling_timesteps` in the config |
| `numpy` version conflict | `pip install numpy==2.0.1` |

---

## Kaggle-Specific Notes

- Set the accelerator to **GPU → T4 x2** in Notebook Settings.
- Enable **Internet** in Notebook Settings to download checkpoints.
- Kaggle's default Python environment already has `torch`, `cuda`, and most packages.
- Use the **PyTorch model** (`ditto_pytorch/`), not TRT – Kaggle T4 GPUs are Turing architecture, not Ampere.
- If HuggingFace clone is slow on Kaggle, use the Kaggle Datasets UI to import the model, or download via `huggingface_hub`:

```python
from huggingface_hub import snapshot_download
snapshot_download(repo_id="digital-avatar/ditto-talkinghead", local_dir="checkpoints")
```
