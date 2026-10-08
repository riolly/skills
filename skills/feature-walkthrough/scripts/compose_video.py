#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["imageio-ffmpeg==0.6.0"]
# ///
"""Combine labelled browser or terminal clips in sequence or side by side."""

import argparse
import json
import math
import os
from pathlib import Path
import tempfile

import imageio_ffmpeg
from finish_video import make_subtitles, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path, help='JSON array of path/label/start/duration objects')
    parser.add_argument('output', type=Path)
    parser.add_argument('--layout', choices=['sequence','side-by-side'], default='sequence')
    parser.add_argument('--captions', type=Path, help='Optional captions timed to the combined output')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.suffix.lower() != '.mp4': parser.error('output must have an .mp4 extension')
    if output.exists() and not args.force: parser.error('output exists; choose another path or pass --force')
    try:
        clips = json.loads(args.manifest.read_text())
        if not isinstance(clips,list) or len(clips) < 2:
            raise ValueError('manifest must contain at least two clips')
        if args.layout == 'side-by-side' and len(clips) != 2:
            raise ValueError('side-by-side expects exactly two clips')
        durations, inputs, graph = [], [], []
        output.parent.mkdir(parents=True,exist_ok=True)
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        with tempfile.TemporaryDirectory(prefix='comparison-',dir=output.parent) as temporary:
            work = Path(temporary)
            for i, clip in enumerate(clips):
                path = Path(clip['path']).expanduser()
                if not path.is_absolute(): path = args.manifest.resolve().parent / path
                path = path.resolve()
                if path == output: raise ValueError('output must not replace an input')
                if not path.is_file(): raise ValueError(f'input does not exist: {path}')
                reader = imageio_ffmpeg.read_frames(str(path))
                try: metadata = next(reader)
                finally: reader.close()
                start = float(clip.get('start',0))
                requested = float(clip.get('duration',metadata['duration']-start))
                if not all(math.isfinite(n) for n in (start,requested)) or start < 0 or requested <= 0:
                    raise ValueError('start must be nonnegative and duration must be positive')
                duration = min(requested,metadata['duration']-start)
                if duration <= 0: raise ValueError('start must be before the end of the input')
                durations.append(duration)
                inputs += ['-ss',str(start),'-t',str(duration),'-i',str(path)]
                title = clip['label']
                if not isinstance(title,str) or not title.strip(): raise ValueError('each clip needs a nonempty label')
                if len(title) > 80: raise ValueError('keep clip labels under 80 characters')
                subtitle = work / f'title-{i}.ass'
                make_subtitles(subtitle,[{'start':0,'end':duration,'text':title}],1280,852,duration)
                subtitle.write_text(subtitle.read_text().replace(',2,32,32,24,1',',8,32,32,12,1'))
                # A fixed stage preserves aspect ratios, including terminal clips.
                graph.append(f'[{i}:v]setpts=PTS-STARTPTS,fps=30,trim=duration={duration},'
                             'scale=1280:800:force_original_aspect_ratio=decrease:force_divisible_by=2,'
                             'pad=1280:800:(ow-iw)/2:(oh-ih)/2:color=0x101010,setsar=1,'
                             f'pad=1280:852:0:52:color=0x142033,ass=filename=title-{i}.ass[v{i}]')
            streams = ''.join(f'[v{i}]' for i in range(len(clips)))
            if args.layout == 'sequence':
                graph.append(f'{streams}concat=n={len(clips)}:v=1:a=0[joined]')
                duration, width = sum(durations),1280
            else:
                graph.append(f'{streams}hstack=inputs=2:shortest=1[joined]')
                duration, width = min(durations),2560
            height = 852
            if args.captions:
                cues = json.loads(args.captions.read_text())
                if not isinstance(cues,list) or not cues: raise ValueError('captions must be a nonempty array')
                height += 112
                make_subtitles(work/'captions.ass',cues,width,height,duration,font_size=26)
                graph.append(f'[joined]pad={width}:{height}:0:0:color=0x101010,ass=filename=captions.ass[out]')
            else:
                graph.append('[joined]null[out]')
            run([ffmpeg,'-hide_banner','-loglevel','error','-nostdin','-y',*inputs,
                 '-filter_complex',';'.join(graph),'-map','[out]','-an','-c:v','libx264',
                 '-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart','output.mp4'],cwd=work)
            result = work/'output.mp4'
            run([ffmpeg,'-hide_banner','-loglevel','error','-xerror','-nostdin','-i',str(result),'-f','null','-'])
            if output.exists() and not args.force: raise ValueError('output appeared while processing')
            os.replace(result,output)
        print(json.dumps({'path':str(output),'layout':args.layout,'duration_seconds':round(duration,2),
                          'width':width,'height':height,'audio':'silent','decode_verified':True},indent=2))
    except (ValueError,KeyError,TypeError,RuntimeError,OSError) as error:
        parser.exit(1,f'Composition failed: {error}\n')


if __name__ == '__main__': main()
