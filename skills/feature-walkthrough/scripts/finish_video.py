#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["imageio-ffmpeg==0.6.0"]
# ///
"""Trim a recording, optionally add captions, and verify a portable MP4."""

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap

import imageio_ffmpeg


def seconds(value):
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("must be a finite, nonnegative number")
    return number


def stamp(value):
    centiseconds = round(value * 100)
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    whole, fraction = divmod(remainder, 100)
    return f"{hours}:{minutes:02}:{whole:02}.{fraction:02}"


def make_subtitles(path, captions, width, height, duration, font_size=None):
    font_size = font_size or max(18, round(width * 26 / 1280))
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {width}",
        f"PlayResY: {height}", "WrapStyle: 0", "", "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, "
        "ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,DejaVu Sans,{font_size},&H00FFFFFF,&H00FFFFFF,"
        "&H00101010,&H00101010,0,0,0,0,100,100,0,0,1,1,0,2,32,32,24,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    previous_end = 0.0
    for cue in captions:
        if not isinstance(cue, dict):
            raise ValueError("each caption must be an object with start, end, and text")
        start, end = float(cue["start"]), float(cue["end"])
        if not (math.isfinite(start) and math.isfinite(end)
                and 0 <= start < end <= duration + 0.05):
            raise ValueError(f"caption must fit within the {duration:.2f}s output: {cue}")
        if start < previous_end:
            raise ValueError("captions must be ordered and must not overlap")
        previous_end = end
        if not isinstance(cue["text"], str) or not cue["text"].strip():
            raise ValueError("caption text must be a nonempty string")
        # Treat captions as plain text, not ASS formatting commands.
        text = " ".join(cue["text"].split()).translate(str.maketrans({
            "\\": "＼", "{": "｛", "}": "｝",
        }))
        wrapped = textwrap.wrap(text, width=max(24, int((width - 64) / (font_size * 0.55))))
        if len(wrapped) > 2:
            raise ValueError("a caption exceeds two lines; shorten it or split the cue")
        rendered = r"\N".join(wrapped)
        lines.append(f"Dialogue: 0,{stamp(start)},{stamp(end)},Default,,0,0,0,,{rendered}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(command, **kwargs):
    result = subprocess.run(command, capture_output=True, text=True, **kwargs)
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--captions", type=Path, help="JSON array of start/end/text cues")
    parser.add_argument("--start", type=seconds, default=0, help="seconds to trim from the start")
    parser.add_argument("--duration", type=seconds, help="maximum output duration in seconds")
    parser.add_argument("--force", action="store_true", help="replace an existing output")
    args = parser.parse_args()
    source, destination = args.input.resolve(), args.output.resolve()
    if not source.is_file():
        parser.error("input video does not exist")
    if source == destination:
        parser.error("input and output must be different files")
    if destination.suffix.lower() != ".mp4":
        parser.error("output must have an .mp4 extension")
    if destination.exists() and not args.force:
        parser.error("output exists; choose another path or pass --force")
    if args.duration == 0:
        parser.error("duration must be positive")

    try:
        reader = imageio_ffmpeg.read_frames(str(source))
        try:
            metadata = next(reader)
        finally:
            reader.close()
        available = metadata["duration"] - args.start
        if available <= 0:
            parser.error("start must be before the end of the video")
        duration = min(available, args.duration) if args.duration is not None else available
        original_width, original_height = metadata["size"]
        ratio = min(1, 1280 / original_width)
        width = max(2, round(original_width * ratio / 2) * 2)
        height = max(2, round(original_height * ratio / 2) * 2)
        filters = [f"scale={width}:{height}", "setsar=1"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        # Safe fixed names in an isolated directory avoid filter-path escaping.
        with tempfile.TemporaryDirectory(prefix="walkthrough-", dir=destination.parent) as temporary:
            work = Path(temporary)
            if args.captions:
                captions = json.loads(args.captions.read_text(encoding="utf-8"))
                if not isinstance(captions, list) or not captions:
                    raise ValueError("captions must be a nonempty JSON array")
                height += max(112, round(width * 112 / 1280 / 2) * 2)
                make_subtitles(work / "captions.ass", captions, width, height, duration)
                filters += [f"pad={width}:{height}:0:0:color=0x101010", "ass=filename=captions.ass"]
            run([
                ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                "-ss", str(args.start), "-i", str(source), "-t", str(duration),
                "-map", "0:v:0", "-map", "0:a?", "-vf", ",".join(filters),
                "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart", "output.mp4",
            ], cwd=work)
            output = work / "output.mp4"
            run([ffmpeg, "-hide_banner", "-loglevel", "error", "-xerror", "-nostdin",
                 "-i", str(output), "-f", "null", "-"])
            if output.stat().st_size == 0:
                raise ValueError("FFmpeg produced an empty video")
            if destination.exists() and not args.force:
                raise ValueError("output appeared while processing; refusing to replace it")
            os.replace(output, destination)
        print(json.dumps({"path": str(destination), "duration_seconds": round(duration, 2),
                          "width": width, "height": height, "size_bytes": destination.stat().st_size,
                          "captions": bool(args.captions), "decode_verified": True}, indent=2))
    except (KeyError, TypeError, ValueError, RuntimeError, OSError) as error:
        parser.exit(1, f"Video export failed: {error}\n")


if __name__ == "__main__":
    main()
