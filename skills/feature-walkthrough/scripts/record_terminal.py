#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["imageio-ffmpeg==0.6.0"]
# ///
"""Record actual command output to asciicast, then render a local MP4."""

import argparse
import json
import math
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time

from finish_video import main as finish_video


def load_steps(path):
    steps = json.loads(path.read_text())
    if not isinstance(steps,list) or not steps: raise ValueError('steps must be a nonempty array')
    for step in steps:
        command = step['command']
        if not isinstance(command,list) or not command or not all(isinstance(s,str) for s in command):
            raise ValueError('each command must be a nonempty argv array, not shell text')
        pause = float(step.get('pause',2.5))
        if not math.isfinite(pause) or not 0 <= pause <= 30: raise ValueError('pause must be 0–30 seconds')
    return steps


def execute_steps(path):
    steps = load_steps(path)
    print('\033[2J\033[H',end='',flush=True)
    for step in steps:
        print('\033[1;36m$ ' + shlex.join(step['command']) + '\033[0m',flush=True)
        result = subprocess.run(step['command'])
        if result.returncode:
            print(f'\033[1;31mCommand exited with status {result.returncode}\033[0m',flush=True)
        time.sleep(float(step.get('pause',2.5)))
        if result.returncode: return result.returncode
        print('',flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('steps',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--captions',type=Path)
    parser.add_argument('--force',action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.suffix.lower() != '.mp4': parser.error('output must have an .mp4 extension')
    cast, gif = output.with_suffix('.cast'),output.with_suffix('.gif')
    if args.steps.resolve() in (output,cast,gif): parser.error('output must not replace the steps file')
    if not args.force and any(p.exists() for p in (output,cast,gif)): parser.error('an output already exists; use --force to replace it')
    for tool in ('asciinema','agg'):
        if not shutil.which(tool): parser.error(f'{tool} is not installed')
    try:
        load_steps(args.steps)
        output.parent.mkdir(parents=True,exist_ok=True)
        command = shlex.join([sys.executable,str(Path(__file__).resolve()),'--execute-steps',str(args.steps.resolve())])
        record = ['asciinema','rec','--headless','--return','--quiet','--window-size','100x24','--command',command]
        if args.force: record.append('--overwrite')
        result = subprocess.run([*record,str(cast)])
        if not cast.is_file(): raise ValueError('recorder did not create a cast file')
        subprocess.run(['agg','--quiet','--font-size','22','--theme','github-dark','--no-loop',
                        '--idle-time-limit','30','--last-frame-duration','2',str(cast),str(gif)],check=True)
        # Reuse the checked MP4 converter. Neither recorder uploads anything.
        sys.argv = [str(Path(__file__).with_name('finish_video.py')),str(gif),str(output)]
        if args.captions: sys.argv += ['--captions',str(args.captions.resolve())]
        if args.force: sys.argv.append('--force')
        finish_video()
        print(json.dumps({'terminal_cast':str(cast),'command_exit_code':result.returncode}))
        return result.returncode
    except (OSError,ValueError,KeyError,TypeError,subprocess.CalledProcessError) as error:
        parser.exit(1,f'Terminal recording failed: {error}\n')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--execute-steps':
        sys.exit(execute_steps(Path(sys.argv[2])))
    sys.exit(main())
