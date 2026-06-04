import json
import os
from pathlib import Path
from typing import Any



"""
pipeline/emotion_utils.py
Load and resolve emotion mappings from configs/emotion_mapping.json.
Usage:
    from pipeline.emotion_utils import load_emotion_config, get_emotion_params
    cfg   = load_emotion_config()
    params = get_emotion_params("confident", cfg)
    # params → {"emo_id": 1, "emo_label": "confident", "description": "...", ...}
"""



# Default location of the emotion mapping file
DEFAULT_EMOTION_CONFIG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "configs", "emotion_mapping.json",
)


def load_emotion_config(config_path: str = DEFAULT_EMOTION_CONFIG) -> dict:
    """
    Load emotion_mapping.json from disk.
    Args:
        config_path: Path to the JSON file.
    Returns:
        Parsed JSON as a Python dict.
    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    config_path = str(Path(config_path).resolve())
    if not os.path.isfile(config_path):
        raise FileNotFoundError(
            f"[emotion_utils] emotion_mapping.json not found at: {config_path}"
        )
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    print(f"[emotion_utils] Loaded emotion config from: {config_path}")
    return cfg


def list_emotions(cfg: dict = None) -> list[str]:
    """
    Return a list of all emotion label names.
    Args:
        cfg: Already-loaded config dict. If None, loads from default path.
    Returns:
        List of emotion label strings.
    """
    if cfg is None:
        cfg = load_emotion_config()
    return list(cfg.get("emotions", {}).keys())


def get_emotion_params(
    emotion_label: str,
    cfg: dict = None,
    fallback: str = "neutral",
) -> dict[str, Any]:
    """
    Retrieve the full parameter block for a given emotion label.
    Args:
        emotion_label: The emotion to look up (e.g. "confident", "angry").
        cfg:           Already-loaded config dict. If None, loads from default path.
        fallback:      Label to use if emotion_label is not found.
    Returns:
        Dict containing all fields defined for that emotion in the JSON.
    Example return value:
        {
            "emo_id":        1,
            "emo_label":     "confident",
            "description":   "Assertive, clear, direct speech",
            "ditto_emo_id":  1,
            "supported":     true,
            "notes":         "Mapped to Ditto emo index 1",
            "tts_voice":     "en-US-GuyNeural",
            "tts_style":     "newscast"
        }
    """
    if cfg is None:
        cfg = load_emotion_config()

    emotions = cfg.get("emotions", {})

    if emotion_label in emotions:
        return emotions[emotion_label]

    print(
        f"[emotion_utils] Unknown emotion '{emotion_label}', "
        f"falling back to '{fallback}'."
    )
    if fallback in emotions:
        return emotions[fallback]

    # Last resort: return an empty-ish neutral block so the pipeline doesn't crash
    return {
        "emo_id": 4,
        "emo_label": "neutral",
        "description": "Default neutral emotion",
        "ditto_emo_id": 4,
        "supported": True,
        "notes": "Auto-fallback",
        "tts_voice": "en-US-AriaNeural",
        "tts_style": "neutral",
    }


def get_ditto_emo_id(emotion_label: str, cfg: dict = None) -> int:
    """
    Return just the Ditto emo_id integer for a given emotion label.
    Args:
        emotion_label: The emotion to look up.
        cfg:           Already-loaded config dict.
    Returns:
        Integer emo_id to pass to Ditto (default 4 = neutral).
    """
    params = get_emotion_params(emotion_label, cfg)
    return params.get("ditto_emo_id", 4)


def is_emotion_supported(emotion_label: str, cfg: dict = None) -> bool:
    """
    Check whether a given emotion is natively supported in Ditto.
    Args:
        emotion_label: The emotion to check.
        cfg:           Already-loaded config dict.
    Returns:
        True if supported, False otherwise.
    """
    params = get_emotion_params(emotion_label, cfg)
    return bool(params.get("supported", False))


if __name__ == "__main__":
    cfg = load_emotion_config()
    print("Available emotions:", list_emotions(cfg))
    for emo in list_emotions(cfg):
        eid  = get_ditto_emo_id(emo, cfg)
        supp = is_emotion_supported(emo, cfg)
        print(f"  {emo:12s} → emo_id={eid}, supported={supp}")
