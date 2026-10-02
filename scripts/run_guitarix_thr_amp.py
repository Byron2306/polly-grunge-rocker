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

    lv2file = shutil.which('lv2file')
    ffmpeg = shutil.which('ffmpeg')
    if lv2file is None:
        raise RuntimeError('FUSION_MISSING_LV2FILE')
    if ffmpeg is None:
        raise RuntimeError('FUSION_MISSING_FFMPEG')
    if not args.input.is_file():
        raise FileNotFoundError(f'FUSION_GUITARIX_INPUT_MISSING: {args.input}')

    args.output.parent.mkdir(parents=True, exist_ok=True)
    mono_out = args.output.with_suffix('.guitarix-mono.wav')

    # Conservative 1980s-thrash baseline. GxAmplifier-X contains amp head,
    # tonestack, and cabinet simulation in one verified LV2 processor.
    # Clipping is intentional in a distorted guitar stage, so lv2file's
    # clipping detector must not turn expected saturation into a hard failure.
    command = [
        lv2file,
        '-i', str(args.input),
        '-o', str(mono_out),
        '-m',
        '--ignore-clipping',
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
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        stdout = (exc.stdout or '').strip()
        stderr = (exc.stderr or '').strip()
        raise RuntimeError(
            'FUSION_GUITARIX_LV2_FAILED: '
            f'returncode={exc.returncode}; stdout={stdout}; stderr={stderr}; '
            f'command={command}'
        ) from exc

    if not mono_out.is_file() or mono_out.stat().st_size == 0:
        raise RuntimeError('FUSION_GUITARIX_MONO_OUTPUT_MISSING')

    try:
        subprocess.run(
            [ffmpeg, '-y', '-i', str(mono_out), '-ac', '2', '-c:a', 'pcm_s16le', str(args.output)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            'FUSION_GUITARIX_STEREO_CONVERT_FAILED: '
            f'returncode={exc.returncode}; stderr={(exc.stderr or "").strip()}'
        ) from exc

    try:
        mono_out.unlink()
    except FileNotFoundError:
        pass

    if not args.output.is_file() or args.output.stat().st_size == 0:
        raise RuntimeError('FUSION_GUITARIX_OUTPUT_MISSING')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
