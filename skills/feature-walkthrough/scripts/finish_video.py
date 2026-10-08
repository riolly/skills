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
import shutil
import struct
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


def caption_band(width):
    return font_size(width) * 2 + 24


def font_size(width):
    return max(18, round(width * 24 / 1280 / 2) * 2)


def get_ffmpeg():
    """Prefer an installed build; the packaged fallback needs no system setup."""
    local = Path.home() / ".local/share/feature-walkthrough/ffmpeg/bin/ffmpeg"
    binary = (os.environ.get("WALKTHROUGH_FFMPEG") or os.environ.get("IMAGEIO_FFMPEG_EXE")
              or shutil.which("ffmpeg") or (str(local) if local.is_file() else None)
              or imageio_ffmpeg.get_ffmpeg_exe())
    # Keep imageio's probe/decoder on the same build as the encoder.
    os.environ["IMAGEIO_FFMPEG_EXE"] = binary
    return binary


def add_encoding_arguments(parser):
    parser.add_argument("--encoder", choices=["auto", "cpu", "nvenc"], default="auto",
                        help="auto tests NVIDIA NVENC, then falls back to CPU H.264")
    parser.add_argument("--gpu", type=int, default=0, help="NVIDIA device index for NVENC")


def encoding_options(encoder="auto", gpu=0):
    if gpu < 0:
        raise ValueError("gpu must be a nonnegative NVIDIA device index")
    ffmpeg = get_ffmpeg()
    report = {"ffmpeg": ffmpeg, "encoder": "libx264", "gpu": None}
    options = ["-c:v", "libx264", "-preset", "fast", "-crf", "18"]
    if encoder != "cpu":
        nvenc = ["-c:v", "h264_nvenc", "-gpu", str(gpu), "-preset", "p5",
                 "-tune", "hq", "-rc", "vbr", "-cq", "18", "-b:v", "0"]
        try:
            test = subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin",
                                   "-f", "lavfi", "-i", "color=s=256x256:r=30", "-frames:v", "1",
                                   *nvenc, "-pix_fmt", "yuv420p", "-f", "null", "-"],
                                  capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            test = subprocess.CompletedProcess([], 1, "", "NVENC probe timed out after 30 seconds")
        if test.returncode == 0:
            options = nvenc
            report.update(encoder="h264_nvenc", gpu=gpu)
        elif encoder == "nvenc":
            raise ValueError(f"NVIDIA encoding unavailable on GPU {gpu}: {test.stderr[-2000:]}")
        else:
            report["fallback_reason"] = test.stderr[-2000:].strip()
    return options + ["-profile:v", "high", "-pix_fmt", "yuv420p", "-tag:v", "avc1"], report


def video_filters(work, original_size, duration, captions=None, title=None, max_width=None):
    """Preserve source pixels and place optional text outside the app."""
    original_width, original_height = original_size
    ratio = min(1, max_width / original_width) if max_width else 1
    width = max(2, round(original_width * ratio / 2) * 2)
    height = max(2, round(original_height * ratio / 2) * 2)
    filters = [f"scale={width}:{height}:flags=lanczos", "setsar=1", "fps=30"]
    if title:
        header = max(48, round(width * 52 / 1280 / 2) * 2)
        height += header
        make_subtitles(work / "title.ass", [{"start": 0, "end": duration, "text": title}],
                       width, height, duration, alignment=8, margin_v=12, max_lines=1)
        filters += [f"pad={width}:{height}:0:{header}:color=0x142033", "ass=filename=title.ass"]
    if captions:
        cues = json.loads(captions.read_text(encoding="utf-8"))
        if not isinstance(cues, list) or not cues:
            raise ValueError("captions must be a nonempty JSON array")
        height += caption_band(width)
        make_subtitles(work / "captions.ass", cues, width, height, duration, margin_v=12)
        filters += [f"pad={width}:{height}:0:0:color=0x101010", "ass=filename=captions.ass"]
    return filters, width, height


def make_subtitles(path, captions, width, height, duration, alignment=2, margin_v=12, max_lines=2):
    size = font_size(width)
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {width}",
        f"PlayResY: {height}", "WrapStyle: 0", "", "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, "
        "ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,DejaVu Sans,{size},&H00FFFFFF,&H00FFFFFF,"
        f"&H00101010,&H00101010,0,0,0,0,100,100,0,0,1,1,0,{alignment},32,32,{margin_v},1",
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
        wrapped = textwrap.wrap(text, width=max(24, int((width - 64) / (size * 0.65))))
        if len(wrapped) > max_lines:
            raise ValueError(f"text exceeds {max_lines} lines; shorten it or split the cue")
        rendered = r"\N".join(wrapped)
        lines.append(f"Dialogue: 0,{stamp(start)},{stamp(end)},Default,,0,0,0,,{rendered}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(command, **kwargs):
    result = subprocess.run(command, capture_output=True, text=True, **kwargs)
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:])
    return result


def probe(path):
    get_ffmpeg()
    reader = imageio_ffmpeg.read_frames(str(path))
    try:
        metadata = next(reader)
    finally:
        reader.close()
    duration = metadata["duration"]
    if not duration > 0:
        # A recording written to a pipe has no duration header; decode it to find its end.
        # Copying packets instead would stop short by the B-frame reorder delay.
        duration = imageio_ffmpeg.count_frames_and_secs(str(path))[1]
        if not duration > 0:
            raise ValueError(f"could not measure the duration of {path}")
    return duration, metadata["size"]


def portable_video(path):
    get_ffmpeg()
    reader = imageio_ffmpeg.read_frames(str(path))
    try:
        metadata = next(reader)
    finally:
        reader.close()
    return (metadata["codec"] == "h264" and metadata["pix_fmt"].split("(")[0] == "yuv420p"
            and all(n % 2 == 0 for n in metadata["size"]))


def publish(result, destination, force):
    if not portable_video(result):
        raise ValueError("output must contain H.264 video with 8-bit yuv420p pixels")
    # A renamed WebM or an unfinished MP4 can decode locally yet fail after download.
    atoms = []
    with result.open("rb") as stream:
        while stream.tell() < result.stat().st_size:
            header = stream.read(8)
            if len(header) != 8:
                raise ValueError("truncated MP4 atom")
            size, kind = struct.unpack(">I4s", header)
            header_size = 8
            if size == 1:
                size = struct.unpack(">Q", stream.read(8))[0]
                header_size = 16
            if size == 0:
                size = result.stat().st_size - stream.tell() + header_size
            if size < header_size or stream.tell() + size - header_size > result.stat().st_size:
                raise ValueError("invalid MP4 atom size")
            atoms.append(kind)
            stream.seek(size - header_size, 1)
    if (not all(kind in atoms for kind in (b"ftyp", b"moov", b"mdat"))
            or atoms.index(b"moov") > atoms.index(b"mdat")):
        raise ValueError("output must be a finalized fast-start MP4")
    run([get_ffmpeg(), "-hide_banner", "-loglevel", "error", "-xerror", "-nostdin",
         "-i", str(result), "-f", "null", "-"])
    if result.stat().st_size == 0:
        raise ValueError("FFmpeg produced an empty video")
    if destination.exists() and not force:
        raise ValueError("output appeared while processing; refusing to replace it")
    os.replace(result, destination)


def finish(source, destination, captions=None, start=0, duration=None, force=False,
           title=None, max_width=None, encoder="auto", gpu=0):
    available, (original_width, original_height) = probe(source)
    available -= start
    if available <= 0:
        raise ValueError("start must be before the end of the video")
    duration = min(available, duration) if duration is not None else available
    if max_width is not None and max_width < 2:
        raise ValueError("max-width must be at least 2")
    options, encoding = encoding_options(encoder, gpu)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Safe fixed names in an isolated directory avoid filter-path escaping.
    with tempfile.TemporaryDirectory(prefix="walkthrough-", dir=destination.parent) as temporary:
        work = Path(temporary)
        filters, width, height = video_filters(work, (original_width, original_height), duration,
                                              captions, title, max_width)
        run([
            get_ffmpeg(), "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
            "-ss", str(start), "-i", str(source), "-t", str(duration),
            "-map", "0:v:0", "-map", "0:a?", "-vf", ",".join(filters),
            *options, "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", "output.mp4",
        ], cwd=work)
        publish(work / "output.mp4", destination, force)
    return {"path": str(destination), "duration_seconds": round(duration, 2),
            "width": width, "height": height, "size_bytes": destination.stat().st_size,
            "captions": bool(captions), "title": title, "encoding": encoding,
            "portable_mp4_verified": True, "decode_verified": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--captions", type=Path, help="JSON array of start/end/text cues")
    parser.add_argument("--title", help="one-line title in a separate header above the app")
    parser.add_argument("--max-width", type=int, help="explicit downscale limit; default preserves input pixels")
    add_encoding_arguments(parser)
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
        report = finish(source, destination, args.captions, args.start, args.duration, args.force,
                        args.title, args.max_width, args.encoder, args.gpu)
        print(json.dumps(report, indent=2))
    except (KeyError, TypeError, ValueError, RuntimeError, OSError) as error:
        parser.exit(1, f"Video export failed: {error}\n")


if __name__ == "__main__":
    main()
