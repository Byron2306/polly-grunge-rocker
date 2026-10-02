#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Apply CAPS AmpVTS + CabinetIV for classic-thrash rhythm tone.')
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)

    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg is None:
        raise RuntimeError('FUSION_MISSING_FFMPEG')
    if not args.input.is_file():
        raise FileNotFoundError(f'FUSION_CAPS_INPUT_MISSING: {args.input}')

    args.output.parent.mkdir(parents=True, exist_ok=True)

    # CAPS AmpVTS port order from Debian trixie caps 0.9.26:
    # over, gain, bright, power, tonestack, bass, mid, treble,
    # attack, squash, lowcut.
    amp_controls = '|'.join((
        'c0=2',      # high-overdrive mode
        'c1=0.72',   # preamp gain
        'c2=0.68',   # bright
        'c3=0.72',   # power amp
        'c4=0',      # tonestack model
        'c5=0.34',   # bass: tight, not flubby
        'c6=0.68',   # mids: classic-thrash bite
        'c7=0.76',   # treble
        'c8=0.58',   # attack
        'c9=0.48',   # squash
        'c10=0.84',  # low cut / tightening
    ))
    cab_controls = 'c0=12|c1=-6'

    # AmpVTS and CabinetIV are mono LADSPA processors. Collapse the clean
    # stereo SFZ render to mono before the amp and duplicate the processed
    # signal back to stereo; the V5 L/R performance/pan stage supplies width.
    filter_chain = ','.join((
        'pan=mono|c0=0.5*c0+0.5*c1',
        f'ladspa=file=caps:plugin=AmpVTS:controls={amp_controls}',
        f'ladspa=file=caps:plugin=CabinetIV:controls={cab_controls}',
        'pan=stereo|c0=c0|c1=c0',
    ))

    command = [
        ffmpeg, '-y',
        '-i', str(args.input),
        '-af', filter_chain,
        '-c:a', 'pcm_s16le',
        str(args.output),
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
