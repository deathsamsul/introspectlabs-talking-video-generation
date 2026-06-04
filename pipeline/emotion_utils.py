{
  "_comment": "PersonaMatrix emotion mapping for Ditto TalkingHead inference.",
  "_version": "1.0.0",
  "_ditto_emo_range": "0-7 (integer index passed to Ditto via --emo flag)",
  "_supported_note": "Ditto supports emo_id 0-7. Unsupported emotions are approximated with the closest supported id.",

  "emotions": {
    "neutral": {
      "emo_id": 0,
      "emo_label": "neutral",
      "description": "Calm, balanced, everyday speech. No strong affective colouring.",
      "ditto_emo_id": 4,
      "supported": true,
      "notes": "Ditto default. emo_id 4 is the stable neutral index in the pretrained model.",
      "tts_voice": "en-US-AriaNeural",
      "tts_style": "neutral"
    },

    "confident": {
      "emo_id": 1,
      "emo_label": "confident",
      "description": "Assertive, clear, direct delivery. Elevated head pose, steady gaze.",
      "ditto_emo_id": 1,
      "supported": true,
      "notes": "Ditto emo_id 1 produces slightly more assertive motion dynamics.",
      "tts_voice": "en-US-GuyNeural",
      "tts_style": "newscast"
    },

    "angry": {
      "emo_id": 2,
      "emo_label": "angry",
      "description": "Forceful, intense speech. Tighter lip movement, stronger jaw activity.",
      "ditto_emo_id": 2,
      "supported": true,
      "notes": "Ditto emo_id 2. Visible in motion amplitude; full facial anger is limited.",
      "tts_voice": "en-US-TonyNeural",
      "tts_style": "angry"
    },

    "sad": {
      "emo_id": 3,
      "emo_label": "sad",
      "description": "Slower, softer delivery. Slightly downward head tilt.",
      "ditto_emo_id": 3,
      "supported": true,
      "notes": "Ditto emo_id 3. Subtle effect on motion; brow/eye emotion not fully rendered.",
      "tts_voice": "en-US-JennyNeural",
      "tts_style": "sad"
    },

    "teasing": {
      "emo_id": 4,
      "emo_label": "teasing",
      "description": "Playful, light-hearted tone. Slight smirk-like motion if available.",
      "ditto_emo_id": 5,
      "supported": false,
      "notes": "No direct Ditto mapping. Approximated with emo_id 5 (happy-adjacent). Full teasing expression not supported in v0.4.",
      "tts_voice": "en-US-AnaNeural",
      "tts_style": "cheerful"
    },

    "intense": {
      "emo_id": 5,
      "emo_label": "intense",
      "description": "High-energy, passionate delivery. Amplified motion dynamics.",
      "ditto_emo_id": 6,
      "supported": false,
      "notes": "Approximated with emo_id 6 (surprise/high-energy). Ditto v0.4 has no explicit 'intense' class.",
      "tts_voice": "en-US-DavisNeural",
      "tts_style": "excited"
    }
  },

  "supported_controls": {
    "emo_id": "Passes integer emotion index to Ditto condition handler. Range 0-7.",
    "lip_sync": "Audio-driven lip sync is fully supported via HuBERT audio features.",
    "head_pose": "Head pose (pitch/yaw/roll) is passable via ctrl_info in inference.",
    "eye_blink": "Automatic eye blink is enabled by default for image sources.",
    "fade_in_out": "Fade-in and fade-out are supported via setup_Nd() in StreamSDK."
  },

  "unsupported_controls": {
    "brow_raise": "No explicit brow-raise control in Ditto v0.4 inference API.",
    "smile_intensity": "Smile magnitude is not independently controllable.",
    "gaze_direction": "Eye-ball gaze direction is not precisely controllable in v0.4.",
    "tongue_visibility": "Inner mouth / tongue detail is not rendered.",
    "full_body": "Ditto is a talking-HEAD model only; no body/hand animation."
  }
}
