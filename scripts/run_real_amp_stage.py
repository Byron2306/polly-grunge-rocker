#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import subprocess


REQUIRED_PLACEHOLDERS = ('{input}', '{output}', '{cab}')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Run a configured real amp/cab processor for Fusion Lab.')
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cab', type=Path, required=True)
    args = parser.parse_args(argv)

    template = os.environ.get('FUSION_REAL_AMP_COMMAND_TEMPLATE', '').strip()
    if not template:
        raise RuntimeError('FUSION_REAL_AMP_COMMAND_TEMPLATE_UNSET')
    missing = [token for token in REQUIRED_PLACEHOLDERS if token not in template]
    if missing:
        raise RuntimeError('FUSION_REAL_AMP_TEMPLATE_MISSING_PLACEHOLDERS: ' + ','.join(missing))
    if not args.input.is_file():
        raise FileNotFoundError(f'FUSION_REAL_AMP_INPUT_MISSING: {args.input}')
    if not args.cab.is_file():
        raise FileNotFoundError(f'FUSION_REAL_AMP_CAB_MISSING: {args.cab}')

    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = template.format(
        input=str(args.input),
        output=str(args.output),
        cab=str(args.cab),
    )
    argv2 = shlex.split(command)
    if not argv2:
        raise RuntimeError('FUSION_REAL_AMP_COMMAND_EMPTY')
    subprocess.run(argv2, check=True)
    if not args.output.is_file() or args.output.stat().st_size == 0:
        raise RuntimeError('FUSION_REAL_AMP_OUTPUT_MISSING')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
