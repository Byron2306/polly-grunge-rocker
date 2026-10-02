#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Apply CAPS AmpVTS + CabinetIV for hostile classic-thrash guitar tone.')
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mode', choices=('rhythm','lead'), default='rhythm')
    args = parser.parse_args(argv)

    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg is None:
        raise RuntimeError('FUSION_MISSING_FFMPEG')
    if not args.input.is_file():
        raise FileNotFoundError(f'FUSION_CAPS_INPUT_MISSING: {args.input}')

    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.mode == 'lead':
        amp_controls='|'.join((
            'c0=2','c1=0.78','c2=0.68','c3=0.80','c4=0',
            'c5=0.30','c6=0.84','c7=0.70','c8=0.44','c9=0.46','c10=0.82',
        ))
        cab_controls='c0=14|c1=-7'
        post=(
            'equalizer=f=1400:t=q:w=1.0:g=3.0',
            'equalizer=f=5200:t=q:w=1.0:g=-2.5',
            'aecho=0.92:0.16:72:0.22',
        )
    else:
        amp_controls='|'.join((
            'c0=2','c1=0.88','c2=0.82','c3=0.84','c4=0',
            'c5=0.26','c6=0.78','c7=0.84','c8=0.74','c9=0.30','c10=0.90',
        ))
        cab_controls='c0=18|c1=-7'
        post=(
            'equalizer=f=1800:t=q:w=1.1:g=2.5',
            'equalizer=f=4200:t=q:w=1.0:g=2.0',
        )

    filter_chain=','.join((
        'pan=mono|c0=0.5*c0+0.5*c1',
        f'ladspa=file=caps:plugin=AmpVTS:controls={amp_controls}',
        f'ladspa=file=caps:plugin=CabinetIV:controls={cab_controls}',
        *post,
        'pan=stereo|c0=c0|c1=c0',
    ))

    command=[ffmpeg,'-y','-i',str(args.input),'-af',filter_chain,'-c:a','pcm_s16le',str(args.output)]
    try:
        subprocess.run(command,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            'FUSION_CAPS_LADSPA_FAILED: '
            f'returncode={exc.returncode}; '
            f'stdout={(exc.stdout or "").strip()}; '
            f'stderr={(exc.stderr or "").strip()}; '
            f'command={command}'
        ) from exc

    if not args.output.is_file() or args.output.stat().st_size == 0:
        raise RuntimeError('FUSION_CAPS_OUTPUT_MISSING')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
