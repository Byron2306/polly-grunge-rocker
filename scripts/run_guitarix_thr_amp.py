#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess

AMP_URI = 'http://guitarix.sourceforge.net/plugins/gx_amp#GUITARIX'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Apply Guitarix GxAmplifier-X for classic-thrash rhythm tone.')
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)

    exe = shutil.which('lv2file')
    if exe is None:
        raise RuntimeError('FUSION_MISSING_LV2FILE')
    if not args.input.is_file():
        raise FileNotFoundError(f'FUSION_GUITARIX_INPUT_MISSING: {args.input}')

    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Conservative 1980s-thrash baseline. GxAmplifier-X contains amp head,
    # tonestack, and cabinet simulation in one verified LV2 processor.
    command = [
        exe,
        '-i', str(args.input),
        '-o', str(args.output),
        '-m',
        '-p', 'MasterGain:-10.0',
        '-p', 'PreGain:7.0',
        '-p', 'Distortion:65.0',
        '-p', 'Drive:0.65',
        '-p', 'Middle:0.62',
        '-p', 'Bass:0.46',
        '-p', 'Treble:0.64',
        '-p', 'Cabinet:9.0',
        '-p', 'Presence:6.0',
        AMP_URI,
    ]
    subprocess.run(command, check=True)
    if not args.output.is_file() or args.output.stat().st_size == 0:
        raise RuntimeError('FUSION_GUITARIX_OUTPUT_MISSING')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
