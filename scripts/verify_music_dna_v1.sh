#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

printf '\n=========================================\n'
printf ' MUSIC DNA V1 VERIFICATION\n'
printf '=========================================\n\n'

python -m unittest \
  fusion_lab.tests.test_music_dna_model \
  fusion_lab.tests.test_music_dna_profiles \
  fusion_lab.tests.test_music_dna_corpus_summary \
  fusion_lab.tests.test_music_dna_features \
  fusion_lab.tests.test_music_dna_coupling \
  fusion_lab.tests.test_music_dna_hook_score \
  fusion_lab.tests.test_music_dna_validator \
  fusion_lab.tests.test_music_dna_blend \
  fusion_lab.tests.test_music_dna_performance \
  fusion_lab.tests.test_music_dna_ingestion \
  fusion_lab.tests.test_music_dna_production_truth \
  fusion_lab.tests.test_music_dna_topology_evidence \
  fusion_lab.tests.test_music_dna_audio_truth \
  fusion_lab.tests.test_real_amp_cab_chain \
  fusion_lab.tests.test_chainsaw_music_dna \
  fusion_lab.tests.test_chainsaw_isolated_guitar_gate \
  -v

printf '\n--- full Fusion Lab suite ---\n'
python -m unittest discover -s fusion_lab/tests -v

printf '\n--- diff whitespace check ---\n'
git diff --check

printf '\n=========================================\n'
printf ' MUSIC DNA V1 TEST GAUNTLET PASS\n'
printf '=========================================\n'
