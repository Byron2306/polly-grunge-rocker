from __future__ import annotations

import argparse
import shutil
from pathlib import Path

SETS = ("METAL-GTX_Full", "METAL-GTX_XTracking")
ARTICULATIONS = ("Mute_Down", "Mute_Up", "Sus_Down", "Sus_Up")


def _strip_keyswitch_lines(text: str) -> str:
    kept: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith("sw_"):
            continue
        kept.append(line)
    return "\n".join(kept) + "\n"


def prepare_metal_gtx_sfizz_clean(individual_root: Path) -> Path:
    individual_root = Path(individual_root)
    if not individual_root.is_dir():
        raise FileNotFoundError(f"METAL_GTX_INDIVIDUAL_ROOT_MISSING: {individual_root}")

    source_samples = individual_root / "Samples"
    if not source_samples.exists():
        raise FileNotFoundError(f"METAL_GTX_COMPAT_SAMPLES_LINK_MISSING: {source_samples}")

    clean_root = individual_root / "SFIZZ_CLEAN"
    if clean_root.exists() or clean_root.is_symlink():
        if clean_root.is_symlink() or clean_root.is_file():
            clean_root.unlink()
        else:
            shutil.rmtree(clean_root)
    clean_root.mkdir(parents=True)

    # The original individual patches live one level below `Individual Patchs`,
    # so `..\\Samples\\...` resolves to `Individual Patchs/Samples`.
    # Compatibility copies live one level deeper under `SFIZZ_CLEAN/<set>`, so
    # recreate that relative layout with a symlink rather than rewriting every
    # sample opcode in the library.
    (clean_root / "Samples").symlink_to(Path("../Samples"), target_is_directory=True)

    for set_name in SETS:
        source_dir = individual_root / set_name
        if not source_dir.is_dir():
            raise FileNotFoundError(f"METAL_GTX_SET_MISSING: {source_dir}")

        destination_dir = clean_root / set_name
        destination_dir.mkdir(parents=True)

        for articulation in ARTICULATIONS:
            source = source_dir / f"{articulation}.sfz"
            if not source.is_file():
                raise FileNotFoundError(f"METAL_GTX_ARTICULATION_MISSING: {source}")

            destination = destination_dir / source.name
            destination.write_text(
                _strip_keyswitch_lines(source.read_text(errors="replace"))
            )

    return clean_root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build sfizz-safe Metal GTX individual articulation patches."
    )
    parser.add_argument("--individual-root", type=Path, required=True)
    args = parser.parse_args(argv)

    clean_root = prepare_metal_gtx_sfizz_clean(args.individual_root)
    print(f"METAL GTX SFIZZ COMPAT READY: {clean_root}")
    for set_name in SETS:
        for articulation in ARTICULATIONS:
            print(clean_root / set_name / f"{articulation}.sfz")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
