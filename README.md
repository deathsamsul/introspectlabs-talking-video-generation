# PersonaMatrix – Talking Avatar Generator


## 🎥 Demo Videos

### Full Step-by-Step Process Demo
[▶️ Watch on YouTube](https://youtu.be/jE_P-0kjTqQ)

### Generated Output
[📁 View Generated Output on Google Drive](https://drive.google.com/drive/folders/13q5T-d3zTQngqSvnbniiCB03SbIhOABc?usp=drive_link)


Convert a static character portrait + text (or audio) into a talking avatar video using [Ditto TalkingHead](https://github.com/antgroup/ditto-talkinghead).

---

## Project Structure

```
ditto-talkinghead/
├── core/                          # Existing Ditto files – do not touch
├── example/                       # Existing Ditto examples
├── scripts/                       # Existing Ditto scripts
├── checkpoints/                   # Pretrained model files (download separately)
├── inference.py                   # Existing Ditto inference – do not edit
├── stream_pipeline_offline.py     # Existing Ditto file – do not edit
├── stream_pipeline_online.py      # Existing Ditto file – do not edit
│
├── pipeline/
│   ├── tts.py                     # Text → audio (edge-tts / gTTS)
│   ├── audio_utils.py             # mp3/wav conversion + audio trimming
│   ├── ditto_runner.py            # Calls inference.py via subprocess
│   └── emotion_utils.py           # Loads and resolves emotion mapping
│
├── configs/
│   └── emotion_mapping.json       # Emotion → Ditto emo_id mapping
│
├── samples/
│   ├── character.jpg              # Your source portrait image
│   └── sample_audio.wav           # Sample audio for duration tests
│
├── outputs/                       # Generated videos and audio land here
│
├── generate_avatar.py             # Main wrapper script (entry point)
├── README.md
├── setup.md
└── technical_report.md
```

---

## Quick Start

### 1. Clone the Ditto repo and add project files

```bash
git clone https://github.com/antgroup/ditto-talkinghead
cd ditto-talkinghead

# Copy pipeline/, configs/, generate_avatar.py, README.md, setup.md
# into the cloned ditto-talkinghead/ directory
```

### 2. Install dependencies

See [setup.md](setup.md) for the full environment setup.

```bash
# Minimal extras on top of the Ditto environment
pip install edge-tts gtts
```

### 3. Download checkpoints

```bash
git lfs install
git clone https://huggingface.co/digital-avatar/ditto-talkinghead checkpoints
```

---

## Usage

### Generate from text (TTS → avatar)

```bash
python generate_avatar.py \
  --image  samples/character.jpg \
  --text   "I do not speak to impress people. I speak only when silence becomes heavier than truth." \
  --emotion confident \
  --output outputs/tts_avatar_output.mp4
```

### Generate from existing audio (no TTS)

```bash
python generate_avatar.py \
  --image  samples/character.jpg \
  --audio  samples/sample_audio.wav \
  --emotion neutral \
  --output outputs/audio_avatar_output.mp4
```

### Generate 5s / 10s / 20s duration test videos

```bash
python generate_avatar.py \
  --image  samples/character.jpg \
  --audio  samples/sample_audio.wav \
  --generate-duration-tests \
  --output outputs/generated.mp4
```

This creates `outputs/generated_5s.mp4`, `outputs/generated_10s.mp4`, and `outputs/generated_20s.mp4`.

---

## Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `--image` | Yes | – | Path to source portrait image (.jpg / .png) |
| `--text` | One of | – | Text to synthesise with TTS |
| `--audio` | these two | – | Path to existing .wav or .mp3 file (skips TTS) |
| `--emotion` | No | `neutral` | Emotion label (see below) |
| `--output` | No | `outputs/avatar_response.mp4` | Output video path |
| `--generate-duration-tests` | No | – | Generate 5s/10s/20s test videos from `--audio` |
| `--data-root` | No | auto-detected | Override Ditto checkpoint directory |
| `--cfg-pkl` | No | auto-detected | Override Ditto config pickle path |

---

## Supported Emotions

| Label | Ditto emo_id | Supported | Notes |
|---|---|---|---|
| `neutral` | 4 | ✅ | Default |
| `confident` | 1 | ✅ | Assertive motion dynamics |
| `angry` | 2 | ✅ | Stronger jaw/lip activity |
| `sad` | 3 | ✅ | Slower, softer motion |
| `teasing` | 5 | ⚠️ | Approximated – no direct Ditto class |
| `intense` | 6 | ⚠️ | Approximated – uses high-energy index |

Full details in [configs/emotion_mapping.json](configs/emotion_mapping.json).

---

## Pipeline Flow

```
Text input                Audio input
    │                         │
    ▼                         │
 TTS (edge-tts/gTTS)          │
    │                         │
    ▼                         ▼
  .mp3                     .wav/.mp3
    │                         │
    └──────────┬──────────────┘
               ▼
        ensure_wav()
        16 kHz mono WAV
               │
               ▼
        inference.py
     (Ditto subprocess)
               │
               ▼
         output.mp4
```

---

## Troubleshooting

**`edge-tts` not found**
```bash
pip install edge-tts
```

**FFmpeg not found**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg
# Conda
conda install -c conda-forge ffmpeg
```

**CUDA / GPU errors on Kaggle**
- Ensure the Kaggle accelerator is set to **GPU T4 x2**.
- Use PyTorch checkpoints (`ditto_pytorch/`) on Kaggle; TRT checkpoints require Ampere GPUs.

**Checkpoint directory not found**
- Download checkpoints as shown above. The script will print a clear warning if they are missing.

---

## License

Apache-2.0 – see [LICENSE](LICENSE).
