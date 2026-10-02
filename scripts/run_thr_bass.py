#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Shape picked bass for audible classic-thrash growl.')
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)

    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg is None:
        raise RuntimeError('FUSION_MISSING_FFMPEG')
    if not args.input.is_file():
        raise FileNotFoundError(f'FUSION_THR_BASS_INPUT_MISSING: {args.input}')
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Keep body, then deliberately expose the pick/growl band that otherwise
    # disappears under two wide rhythm guitars.
    filters = ','.join((
        'highpass=f=42',
        'lowpass=f=6500',
        'equalizer=f=105:t=q:w=0.9:g=2.5',
        'equalizer=f=780:t=q:w=1.0:g=5.5',
        'equalizer=f=1550:t=q:w=1.1:g=4.5',
        'acompressor=threshold=0.07:ratio=4:attack=6:release=90:makeup=2.2',
        'asoftclip=type=tanh:threshold=0.58:output=0.92:oversample=4',
        'alimiter=limit=0.94',
    ))
    cmd=[ffmpeg,'-y','-i',str(args.input),'-af',filters,'-c:a','pcm_s16le',str(args.output)]
    try:
        subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f'FUSION_THR_BASS_FAILED: returncode={exc.returncode}; stderr={(exc.stderr or "").strip()}'
        ) from exc
    if not args.output.is_file() or args.output.stat().st_size == 0:
        raise RuntimeError('FUSION_THR_BASS_OUTPUT_MISSING')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
