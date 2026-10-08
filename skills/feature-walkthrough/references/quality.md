# Export quality

## Capture readable text

Use native pixels and readable framing. The portable recorder captures 1920×1080 by default. For T3, start at 1280×900 and inspect a short raw recording before choosing larger dimensions. In local testing, a 1920×1080 T3 clip softened app text while a 1280-pixel-wide capture kept it sharp. A large reported frame size alone does not prove native detail. Inspect actual pixels before editing and increase zoom or frame fewer controls when needed. Upscaling an existing low-resolution clip cannot recover its text.

In T3, temporary page zoom can be applied with `preview_evaluate`: save `document.documentElement.style.zoom`, then set it to `'1.25'` and reinspect the controls. Restore the saved value after recording. This changes only the recording tab's presentation; keep it out of the app's source. Reapply after navigation if needed.

`finish_video.py` and `narrate_video.py` preserve source resolution. An explicit `finish_video.py --max-width` is available when a smaller delivery is required. Use labelled sequential chapters for comparisons viewed in a small player. Side-by-side output preserves two 1920-pixel stages and needs a wide player or fullscreen viewing.

Add captions once, after trimming or composition. The footer reserves two caption lines plus 24 pixels of padding. A supplied `--title` gets a separate header; composed clips already have source labels. Inspect a frame where both title and captions are present. Relevant app content must remain visible between them.

## NVIDIA encoding

Encoding selection is shared by the finishing, composition, and narration helpers. `--encoder auto` runs a real NVENC encoding probe on NVIDIA device `--gpu 0`. A working probe selects `h264_nvenc`; otherwise the JSON report records the CPU fallback and its reason. Use `--encoder nvenc --gpu 0` when GPU use is required, so an unavailable NVIDIA encoder fails explicitly. Use `--encoder cpu` for software H.264.

The FFmpeg supplied by `imageio-ffmpeg==0.6.0` lacks NVENC. Select a build with both `h264_nvenc` and the `ass` subtitle filter. The helpers look first at `WALKTHROUGH_FFMPEG`, then `IMAGEIO_FFMPEG_EXE`, an `ffmpeg` on PATH, a skill-local binary at `~/.local/share/feature-walkthrough/ffmpeg/bin/ffmpeg`, and finally the packaged fallback. For example:

```sh
export WALKTHROUGH_FFMPEG="$HOME/.local/share/feature-walkthrough/ffmpeg/bin/ffmpeg"
"$WALKTHROUGH_FFMPEG" -hide_banner -encoders
"$WALKTHROUGH_FFMPEG" -hide_banner -filters
uv run "$WALKTHROUGH_SKILL_DIR"/scripts/finish_video.py \
  /absolute/path/raw.webm /absolute/path/edited.mp4 --encoder nvenc --gpu 0
```

An encoder name in the build is insufficient; the driver's runtime probe must pass. Use `nvidia-smi` to identify the intended NVIDIA device. NVENC selects NVIDIA hardware rather than Intel integrated graphics. Captions, audio processing, Piper speech synthesis, and decoding checks still use CPU. Browser rendering and T3's raw recorder choose their own GPU; these helper options control final video encoding.

For Linux without system FFmpeg, obtain a build from the Linux build providers linked by [FFmpeg downloads](https://ffmpeg.org/download.html). On this machine, BtbN's `ffmpeg-n8.1-latest-linux64-gpl-8.1.tar.xz` was verified against its release checksum and extracted under the skill-local directory above. Keep binaries outside the repository and check a fresh release's checksum before running it. See [NVIDIA's FFmpeg guide](https://docs.nvidia.com/video-technologies/video-codec-sdk/13.0/ffmpeg-with-nvidia-gpu/index.html) for driver and encoder requirements.

## Final playback

1. Collect the final helper report. Require `portable_mp4_verified` and `decode_verified`. Narrated output also requires `audible_audio_verified`. These checks verify 8-bit H.264, a finalized MP4 whose metadata precedes its media, complete decoding, and a non-silent narration track covering the timeline.
2. Extract and inspect frames at the title, each action's result, and caption transitions. Read the smallest relevant text at the intended display size. Check the full frame, including both bands. If source text is too small, record again with better framing.
3. Serve the final file from a local HTTP server with byte-range support and open it in a `<video controls>` player with a download link. In T3, use the shared preview. Start playback, confirm `currentTime` advances, seek into a later scene, and verify that `currentTime` reaches that scene. Check `videoWidth`, `videoHeight`, and `error`. Listen when an audio playback tool is available. A successful FFmpeg decode alone does not prove player compatibility or voice quality.
4. Save the bytes from the download URL to a separate local `.mp4`. Compare SHA-256 hashes and open the downloaded copy in the same player. Verify advancing playback and seeking again. This tests the exported file and its transfer; it cannot prove every external player supports it.
5. Embed and link that verified final MP4. Report any player, download, or listening check that could not run, with the written steps to try.

The input recording is never a substitute for the finished MP4. Captioned output alone does not satisfy a narrated walkthrough. An `.mp4` filename alone does not prove its container or codecs.

For the player test, a request with `Range: bytes=0-99` must return `206 Partial Content`, `Accept-Ranges: bytes`, and `Content-Range`. A basic `python -m http.server` lacks this support and can prevent seeking even when the whole video is buffered. Use the app's static server or, with Node available, `npx --yes http-server@14.1.1 /absolute/path/artifacts/walkthrough -p 8767 -c-1`. Check the actual response before diagnosing a video export failure.
