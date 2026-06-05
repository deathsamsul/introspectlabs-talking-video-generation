# Technical Report – PersonaMatrix Talking Avatar Prototype

**Assignment:** PersonaMatrix Intern Assignment – Talking Avatar  
**Model Used:** Ditto TalkingHead v0.4 (PyTorch)  
**Platform:** Kaggle Notebook – T4 x2 GPU  

---

## 1. Which model / repo did you use?

**Ditto TalkingHead** by Ant Group.  
- GitHub: https://github.com/antgroup/ditto-talkinghead  
- Paper: *Ditto: Motion-Space Diffusion for Controllable Realtime Talking Head Synthesis* (arXiv 2411.19509)  
- Checkpoints: https://huggingface.co/digital-avatar/ditto-talkinghead  

The **PyTorch checkpoint** (`ditto_pytorch/`) was used because Kaggle T4 GPUs are Turing architecture (not Ampere), making the TensorRT `.engine` files incompatible.

---

## 2. How did you install and run it?

### Installation summary

```bash
# Clone repo
git clone https://github.com/antgroup/ditto-talkinghead && cd ditto-talkinghead

# System dependency
sudo apt-get install -y ffmpeg

# Python packages
pip install librosa tqdm filetype imageio opencv-python-headless \
            scikit-image cython imageio-ffmpeg colored numpy==2.0.1

# TTS backends
pip install edge-tts gtts

# Download checkpoints (HuggingFace)
git lfs install
git clone https://huggingface.co/digital-avatar/ditto-talkinghead checkpoints
```

See [setup.md](setup.md) for full details.

### Running inference

```bash
python generate_avatar.py \
    --image   samples/character.jpg \
    --text    "I do not speak to impress people." \
    --emotion confident \
    --output  outputs/tts_avatar_output.mp4
```

Internally the script calls `inference.py` via `subprocess.run()` with the appropriate flags.

---

## 3. What errors did you face and how did you solve them?

| Error | Root Cause | Fix |
|---|---|---|
| TRT engine load failure | T4 GPU is Turing, not Ampere – TRT `.engine` files are GPU-specific | Switched to `ditto_pytorch/` checkpoints |
| `numpy` version conflict | Ditto requires `numpy==2.0.1` | `pip install numpy==2.0.1` |
| `edge-tts` `asyncio` error on older Python | Event loop already running in Jupyter | Wrapped in `asyncio.run()` with a fresh loop |
| FFmpeg not found on Kaggle | Not pre-installed | `apt-get install -y ffmpeg` |
| HuggingFace LFS slow clone | Kaggle network throttling | Used `huggingface_hub.snapshot_download()` |

---

## 4. What input image / audio did you test?

- **Source image:** `samples/character.jpg` – a fictional character portrait (created/licensed for this prototype, no copyrighted likeness used).
- **TTS text:** *"I do not speak to impress people. I speak only when silence becomes heavier than truth."*
- **TTS tool:** `edge-tts` with `en-US-GuyNeural` voice (confident emotion).
- **Sample audio:** `samples/sample_audio.wav` – used for 5s / 10s / 20s duration tests.

---

## 5. How long did each video generation take?

Times measured on Kaggle T4 x2 GPU using the PyTorch model.

| Task | Audio Length | Generation Time |
|---|---|---|
| TTS + avatar (confident) | ~6s | ~35–45s |
| Duration test – 5s | 5s | ~25s |
| Duration test – 10s | 10s | ~40s |
| Duration test – 20s | 20s | ~75s |

Generation time scales roughly linearly with audio duration. The diffusion model (`sampling_timesteps=50`) is the main bottleneck.

---

## 6. How good was the lip-sync?

**Rating: Good (3.5 / 5)**

- Lip sync was accurate for clear, moderately-paced English speech.
- Slight drift noticeable at sentence boundaries and on long vowels.
- Performance depends heavily on audio clarity; clean TTS audio from `edge-tts` produced better sync than noisier reference audio.
- Ditto uses HuBERT audio features for motion prediction, which provides strong phoneme-level conditioning.

---

## 7. Was the face stable?

**Rating: Good (4 / 5)**

- Head pose was stable across all clips.
- Natural blink was generated automatically for static image inputs.
- No visible jitter or flickering on the main facial region.
- Very slight warping artefacts visible around the neck/jaw boundary when the source crop was tight.

---

## 8. Were emotions controllable in your implementation?

**Partially.** Ditto supports an integer `emo` conditioning signal (0–7). This is passed via the `condition_handler` and affects motion dynamics at the diffusion level.

| Emotion | Status |
|---|---|
| `neutral` | ✅ Fully supported |
| `confident` | ✅ Supported – visible in assertive head motion |
| `angry` | ✅ Supported – stronger jaw activity |
| `sad` | ✅ Supported – softer, slower motion |
| `teasing` | ⚠️ Approximated with emo_id 5 |
| `intense` | ⚠️ Approximated with emo_id 6 |

The emotion effect is subtle compared to fully expressive models. It primarily influences the *energy* and *amplitude* of facial motion rather than explicit expression shapes (brow, smile, etc.).

---

## 9. What are the limitations?

- **No expressive face shapes:** Ditto drives motion in a compact latent space. It cannot produce strong brow raises, wide smiles, or tongue visibility.
- **Emotion subtlety:** Emotion conditioning is low-magnitude; differences between labels can be hard to distinguish for neutral-adjacent emotions.
- **No full body:** Ditto is a talking-head model only. There is no shoulder, hand, or body animation.
- **TRT GPU lock-in:** The optimised TensorRT model only runs on Ampere+ GPUs. The PyTorch fallback is slower.
- **Static identity per session:** The source image is fixed. Multi-identity or mid-video identity switching is not supported.
- **English-centric:** Audio features (HuBERT) work best on English speech; other languages may produce degraded lip sync.
- **No real-time streaming on T4:** The offline pipeline is not truly real-time at 25 FPS on a T4 with the PyTorch model.

---

## 10. How can this be improved for PersonaMatrix?

| Area | Recommendation |
|---|---|
| **Emotion quality** | Fine-tune or swap the condition model on expressive face datasets (MEAD, CREMA-D) to get more visible emotion deltas. |
| **Latency** | Serve the TRT model on Ampere A10G/A100 cloud instances. Move to streaming mode (`stream_pipeline_online.py`) for near-realtime response. |
| **Voice identity** | Integrate ElevenLabs or a cloned TTS model so each character has a distinct, consistent voice. |
| **Multimodal input** | Add a text → emotion classifier so the system auto-selects the emotion from context, not just a label. |
| **Character consistency** | Cache the `avatar_registrar` output (appearance features) per character to avoid re-processing on every request. |
| **API layer** | Wrap the pipeline in a FastAPI endpoint (see Bonus Task) for production integration into PersonaMatrix backends. |
| **Video quality** | Enable `flag_stitching=True` (already default) and experiment with higher-resolution source crops for sharper output. |
| **Safety layer** | Add a face-verification step to ensure generated avatars match the registered character, preventing misuse. |

---

## Appendix – File Outputs

| File | Description |
|---|---|
| `outputs/tts_audio.wav` | TTS-generated audio from sample text |
| `outputs/tts_avatar_output.mp4` | TTS text → avatar video (confident emotion) |
| `outputs/generated_5s.mp4` | Sample audio trimmed to 5s → avatar |
| `outputs/generated_10s.mp4` | Sample audio trimmed to 10s → avatar |
| `outputs/generated_20s.mp4` | Sample audio trimmed to 20s → avatar |
