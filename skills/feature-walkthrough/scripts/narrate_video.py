#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["imageio-ffmpeg==0.6.0", "piper-tts==1.3.0"]
# ///
"""Read timed captions with a local Piper voice and export an audible MP4."""

import argparse
import json
import math
from pathlib import Path
import subprocess
import tempfile
import wave

import numpy as np
from piper import PiperVoice, SynthesisConfig
from finish_video import (add_encoding_arguments, encoding_options, get_ffmpeg, make_subtitles,
                          portable_video, probe, publish, run, video_filters)


def read_wave(path):
    with wave.open(str(path), "rb") as stream:
        if stream.getnchannels() != 1 or stream.getsampwidth() != 2:
            raise ValueError("voice must produce mono, 16-bit PCM")
        return stream.getframerate(), np.frombuffer(stream.readframes(stream.getnframes()),
                                                   dtype="<i2").astype(np.float32) / 32768


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--captions", type=Path, required=True, help="JSON start/end/text cues, also spoken verbatim")
    parser.add_argument("--model", type=Path, default=Path.home() / ".local/share/feature-walkthrough/voices/en_US-ljspeech-high.onnx")
    parser.add_argument("--length-scale", type=float, default=1, help="1 is natural speed; larger is slower")
    parser.add_argument("--no-captions", action="store_true", help="input already has the matching captions; copy its video stream")
    parser.add_argument("--title", help="one-line title in a separate header above the app")
    add_encoding_arguments(parser)
    parser.add_argument("--source-audio", choices=["replace", "mix"], default="replace",
                        help="replace source audio, or mix it quietly below narration")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    source, output, model = args.input.resolve(), args.output.resolve(), args.model.expanduser().resolve()
    if source == output: parser.error("input and output must be different files")
    if not source.is_file(): parser.error("input video does not exist")
    if output.suffix.lower() != ".mp4": parser.error("output must have an .mp4 extension")
    if output.exists() and not args.force: parser.error("output exists; choose another path or pass --force")
    if not model.is_file() or not Path(str(model) + ".json").is_file():
        parser.error("voice model/config missing; see references/narration.md for setup")
    if not math.isfinite(args.length_scale) or not 0.85 <= args.length_scale <= 1.3:
        parser.error("length-scale must be between 0.85 and 1.3; give longer speech more time")

    try:
        duration, (width, height) = probe(source)
        cues = json.loads(args.captions.read_text(encoding="utf-8"))
        if not isinstance(cues, list) or not cues: raise ValueError("captions must be a nonempty array")
        output.parent.mkdir(parents=True, exist_ok=True)
        ffmpeg = get_ffmpeg()
        with tempfile.TemporaryDirectory(prefix="narration-", dir=output.parent) as temporary:
            work = Path(temporary)
            # Validate the complete timeline before doing speech synthesis.
            make_subtitles(work / "captions.ass", cues, width, height, duration)
            voice = PiperVoice.load(str(model))
            rate = voice.config.sample_rate
            timeline = np.zeros(math.ceil(duration * rate), dtype=np.float32)
            report = []
            for i, cue in enumerate(cues):
                speech_path = work / f"cue-{i}.wav"
                with wave.open(str(speech_path), "wb") as stream:
                    voice.synthesize_wav(cue["text"], stream,
                                         syn_config=SynthesisConfig(length_scale=args.length_scale))
                actual_rate, speech = read_wave(speech_path)
                if actual_rate != rate: raise ValueError("voice sample rate changed")
                # Remove generated silence, retaining a little space around words.
                active = np.flatnonzero(np.abs(speech) > 0.003)
                if not active.size: raise ValueError(f"cue {i + 1} produced silence")
                speech = speech[max(0, active[0] - round(rate * 0.02)):
                                min(len(speech), active[-1] + round(rate * 0.15) + 1)].copy()
                length = len(speech) / rate
                start, end = float(cue["start"]), float(cue["end"])
                room = end - start - 0.12
                if length > room:
                    raise ValueError(f"cue {i + 1} needs {length + 0.12:.2f}s but has {end-start:.2f}s; "
                                     "shorten the text or extend the scene. Speech was not truncated.")
                fade = min(round(rate * 0.005), len(speech) // 2)
                speech[:fade] *= np.linspace(0, 1, fade)
                speech[-fade:] *= np.linspace(1, 0, fade)
                offset = round((start + 0.12) * rate)
                timeline[offset:offset + len(speech)] = speech
                report.append({"cue": i + 1, "start": start + 0.12, "speech_seconds": round(length, 2)})
            # One gain for the whole narration retains sentence dynamics.
            rms = float(np.sqrt(np.mean(timeline ** 2)))
            if rms < 1e-5: raise ValueError("narration is silent")
            gain = min(0.12 / rms, 0.9 / float(np.max(np.abs(timeline))))
            with wave.open(str(work / "narration.wav"), "wb") as stream:
                stream.setparams((1, 2, rate, 0, "NONE", "not compressed"))
                stream.writeframes((timeline * gain * 32767).astype("<i2").tobytes())
            command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                       "-i", str(source), "-i", "narration.wav", "-map", "0:v:0"]
            if args.source_audio == "mix":
                command += ["-filter_complex", "[0:a:0]volume=0.15[bg];[1:a:0][bg]"
                            "amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
                            "-map", "[a]"]
            else:
                command += ["-map", "1:a:0"]
            if args.no_captions and not args.title and portable_video(source):
                command += ["-c:v", "copy"]
                encoding = {"encoder": "copy", "gpu": None, "ffmpeg": ffmpeg}
            else:
                filters, width, height = video_filters(work, (width, height), duration,
                                                       None if args.no_captions else args.captions, args.title)
                options, encoding = encoding_options(args.encoder, args.gpu)
                command += ["-vf", ",".join(filters), *options]
            command += ["-c:a", "aac", "-b:a", "192k", "-t", str(duration),
                        "-movflags", "+faststart", "output.mp4"]
            run(command, cwd=work)
            result = work / "output.mp4"
            # Require an audible output track, beyond a successful video decode.
            decoded = subprocess.run([ffmpeg, "-v", "error", "-nostdin", "-i", str(result),
                                      "-map", "0:a:0", "-f", "f32le", "-ac", "1", "-ar", str(rate), "-"],
                                     capture_output=True, check=True)
            samples = np.frombuffer(decoded.stdout, dtype="<f4")
            if not samples.size or float(np.sqrt(np.mean(samples ** 2))) < 1e-5:
                raise ValueError("exported audio is silent")
            if abs(len(samples) / rate - duration) > 0.15:
                raise ValueError("exported audio does not cover the video timeline")
            publish(result, output, args.force)
        print(json.dumps({"path": str(output), "duration_seconds": duration, "voice": model.name,
                          "speech": "local synthetic narration", "audio": "AAC", "source_audio": args.source_audio,
                          "captions_added": not args.no_captions, "cues": report, "decode_verified": True,
                          "width": width, "height": height, "title": args.title, "encoding": encoding,
                          "portable_mp4_verified": True,
                          "audible_audio_verified": True}, indent=2))
    except (ValueError, TypeError, KeyError, RuntimeError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Narration export failed: {error}\n")


if __name__ == "__main__": main()
