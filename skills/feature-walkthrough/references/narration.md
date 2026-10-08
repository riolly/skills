# Spoken walkthroughs

Use an audible AAC track in the MP4, with the same words visible as captions. The browser recorder captures the app; narration is synthesized and added after editing. This also works across composed browser and terminal segments. It does not require microphone capture or speaking through the browser.

## Explain the work

Write a short spoken script before recording when possible, so actions have enough time. Lead with the specific outcome. For a fix, show the old failure and the corrected result when a verified baseline is available. Explain the benefit in ordinary language, point to the control, then give the viewer something to try and an observable expected result. Describe only changes actually made. A recording-tool demo must not imply that the example app was changed.

Use a conversational first-person voice where natural, as the engineer explaining their work to a colleague. Pride should come from showing a working result and explaining the decisions, rather than praise or unsupported performance claims. Avoid reading terminal logs aloud. Explain what their output proves. Leave time to inspect results and try to keep each caption to one or two lines.

## Local voice setup

The helper uses Piper 1.3.0 through `uv` and defaults to the US English LJSpeech voice at `~/.local/share/feature-walkthrough/voices/en_US-ljspeech-high.onnx`, with its `.onnx.json` config. Download those files if missing; installing the skill does not include the voice. The voice's [model card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/ljspeech/high/MODEL_CARD) identifies its source dataset as public domain. The voice is synthetic; do not present it as a human recording.

One-time voice setup:

```sh
uv run --python 3.12 --with piper-tts==1.3.0 python -m piper.download_voices \
  en_US-ljspeech-high --data-dir "$HOME/.local/share/feature-walkthrough/voices"
```

Setup downloads packages and voice files. After they are cached, speech synthesis runs locally on CPU without sending caption text to a service or requiring a paid account. Other Piper models can be passed with `--model`; check their model cards before selecting one. Python 3.12 is verified here. The helper excludes Python 3.14 due to dependency compatibility.

## Export narration and matching captions

First finish trimming and combining the footage, then add the caption band once with this helper. Caption times are relative to the final edited video, not to the raw recording. Narration is the default; a caption-only export is complete only when silent output was requested or a voice failure is reported.

```sh
uv run --python 3.12 "$WALKTHROUGH_SKILL_DIR"/scripts/narrate_video.py \
  /absolute/path/edited.mp4 /absolute/path/narrated.mp4 \
  --captions /absolute/path/captions.json --title "A concise walkthrough title"
```

Use the ordinary `start`, `end`, `text` caption JSON. The helper reads each cue verbatim, starts speech 0.12 seconds after its caption appears, and preserves silence between cues. It rejects a sentence that cannot fit its cue, rather than cutting words off or automatically rushing the voice. Shorten the sentence or extend the scene. `--length-scale` permits modest pacing changes, with 1 as normal speed and larger values slower.

For composed footage that already has titles, omit `--title` to preserve those headers. Use `--no-captions` only if the input already contains the exact matching captions. Compatible H.264 video is copied; other formats are converted for MP4 playback. By default, source audio is replaced. `--source-audio mix` retains an existing audio track quietly beneath narration and requires the input to have audio. If the original audio itself explains the behavior being tested, preserve a separate original clip and choose mixing deliberately. Composition creates silent output; add narration after composition.

Existing output requires `--force`. Export checks include full decoding, a present and non-silent audio track, and audio duration covering the video. Follow the frame, player, and downloaded-copy checks in [export quality](quality.md). Listen to the final narration when an audio playback tool is available; otherwise report that pronunciation and perceived voice quality still need a listening check. Pay attention to names, acronyms, and pauses. Regenerate mispronounced wording consistently in both speech and captions.

Deliver the MP4 with a brief instruction to enable sound if needed, and identify the synthetic voice. Keep the written explanation short. A viewer should understand and reproduce the demonstrated change by watching the video.

Sources: [Piper Python API](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md), [voice downloads](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/CLI.md), and the LJSpeech model card above. Local export verified on 2026-10-08.
