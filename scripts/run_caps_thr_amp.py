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
    #
    # V5.1 deliberately trades niceness for hostility: more pre/power drive,
    # less squash, leaner lows, and more upper-mid/pick aggression.
    amp_controls = '|'.join((
        'c0=2',      # high-overdrive mode
        'c1=0.88',   # hotter preamp
        'c2=0.82',   # more bright edge
        'c3=0.84',   # harder power-stage push
        'c4=0',      # tonestack model
        'c5=0.26',   # lean lows so the bass owns the floor
        'c6=0.78',   # upper-mid bark
        'c7=0.84',   # hostile treble bite
        'c8=0.74',   # pick attack
        'c9=0.30',   # less polite compression/squash
        'c10=0.90',  # aggressive low cut / tightening
    ))
    # CabinetIV model 18 is used here as a deliberately harder/leaner voice
    # than the previous neutral model 12.  Final output gain leaves headroom.
    cab_controls = 'c0=18|c1=-7'

    filter_chain = ','.join((
        'pan=mono|c0=0.5*c0+0.5*c1',
        f'ladspa=file=caps:plugin=AmpVTS:controls={amp_controls}',
        f'ladspa=file=caps:plugin=CabinetIV:controls={cab_controls}',
        'equalizer=f=1800:t=q:w=1.1:g=2.5',
        'equalizer=f=4200:t=q:w=1.0:g=2.0',
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
