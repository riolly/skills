#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["imageio-ffmpeg==0.6.0"]
# ///
"""Record actual command output to asciicast, then render a local MP4."""

import argparse
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

from finish_video import finish


def load_steps(path):
    steps = json.loads(path.read_text(encoding='utf-8'))
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
        try: status = subprocess.run(step['command']).returncode
        except OSError as error:
            # A command that cannot start is a failed step, as a shell reports it, not a helper traceback.
            print(f"{step['command'][0]}: {error.strerror}",flush=True)
            status = 126 if isinstance(error,PermissionError) else 127
        if status:
            print(f'\033[1;31mCommand exited with status {status}\033[0m',flush=True)
        time.sleep(float(step.get('pause',2.5)))
        if status: return status
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
        # Reject an unreadable captions file before the commands run, since a failed export discards their recording.
        if args.captions: json.loads(args.captions.read_text(encoding='utf-8'))
        output.parent.mkdir(parents=True,exist_ok=True)
        command = shlex.join([sys.executable,str(Path(__file__).resolve()),'--execute-steps',str(args.steps.resolve())])
        # Publish the cast, GIF, and MP4 together. A failed export leaves nothing to block the next run.
        with tempfile.TemporaryDirectory(prefix='terminal-',dir=output.parent) as temporary:
            raw_cast, raw_gif = Path(temporary)/'recording.cast',Path(temporary)/'recording.gif'
            result = subprocess.run(['asciinema','rec','--headless','--return','--quiet','--window-size','100x24',
                                     '--command',command,str(raw_cast)])
            if not raw_cast.is_file(): raise ValueError('recorder did not create a cast file')
            subprocess.run(['agg','--quiet','--font-size','22','--theme','github-dark','--no-loop',
                            '--idle-time-limit','30','--last-frame-duration','2',str(raw_cast),str(raw_gif)],check=True)
            # Reuse the checked MP4 converter. Neither recorder uploads anything.
            report = finish(raw_gif,output,args.captions,force=args.force)
            os.replace(raw_cast,cast)
            os.replace(raw_gif,gif)
        print(json.dumps({**report,'terminal_cast':str(cast),'command_exit_code':result.returncode},indent=2))
        return result.returncode
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,subprocess.CalledProcessError) as error:
        parser.exit(1,f'Terminal recording failed: {error}\n')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--execute-steps':
        sys.exit(execute_steps(Path(sys.argv[2])))
    sys.exit(main())
