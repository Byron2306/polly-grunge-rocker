#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Shape drums for aggressive thrash impact.')
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)

    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg is None:
        raise RuntimeError('FUSION_MISSING_FFMPEG')
    if not args.input.is_file():
        raise FileNotFoundError(f'FUSION_THR_DRUM_INPUT_MISSING: {args.input}')
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Let attacks through, then compress the body.  The EQ intentionally
    # emphasizes kick punch, snare crack, and cymbal bite instead of room wash.
    filters = ','.join((
        'highpass=f=32',
        'equalizer=f=72:t=q:w=0.8:g=5.0',
        'equalizer=f=210:t=q:w=1.0:g=3.0',
        'equalizer=f=3400:t=q:w=1.1:g=6.0',
        'equalizer=f=8200:t=q:w=0.9:g=2.5',
        'acompressor=threshold=0.045:ratio=4.5:attack=18:release=75:makeup=4.0',
        'asoftclip=type=tanh:threshold=0.82:output=0.95:oversample=4',
        'alimiter=limit=0.95',
    ))
    cmd=[ffmpeg,'-y','-i',str(args.input),'-af',filters,'-c:a','pcm_s16le',str(args.output)]
    try:
        subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f'FUSION_THR_DRUM_FAILED: returncode={exc.returncode}; stderr={(exc.stderr or "").strip()}'
        ) from exc
    if not args.output.is_file() or args.output.stat().st_size == 0:
        raise RuntimeError('FUSION_THR_DRUM_OUTPUT_MISSING')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
