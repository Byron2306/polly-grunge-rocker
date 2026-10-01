import unittest
from pathlib import Path

from fusion_lab.music_dna.production_topology import evidence_from_profiles
from fusion_lab.production_model import ArticulationMap, InstrumentProfile, ToneControls, ToneProfile, ToneStage


class TopologyEvidenceTests(unittest.TestCase):
    def test_softclip_controls_are_not_promoted_to_real_amp(self):
        tone = ToneProfile('gtr', (), controls=ToneControls(distortion=7.0, cabinet_ir=None))
        inst = InstrumentProfile(
            'gtr', 'RHYTHM_GUITAR', Path('/tmp/sus.sfz'),
            {
                'PALM_MUTE_DOWNPICK': ArticulationMap('PALM_MUTE_DOWNPICK', sfz_path=Path('/tmp/sus.sfz')),
                'OPEN_RELEASE': ArticulationMap('OPEN_RELEASE', sfz_path=Path('/tmp/sus.sfz')),
            },
            'test',
        )
        evidence = evidence_from_profiles(tone, tone, inst, inst, seed=1988)
        self.assertEqual(evidence.amp_stage_kind, 'generic_softclip')
        self.assertIsNone(evidence.cabinet_ir)
        self.assertEqual(evidence.palm_mute_signature, evidence.sustain_signature)

    def test_real_amp_stage_and_cabinet_are_exposed(self):
        stage = ToneStage('real_amp_sim', executable='amp', args=('{in}', '{out}'), asset_path=Path('/tmp/cab.wav'))
        left = ToneProfile('L', (stage,), controls=ToneControls(distortion=0.0))
        right = ToneProfile('R', (stage,), controls=ToneControls(distortion=0.0))
        inst = InstrumentProfile(
            'gtr', 'RHYTHM_GUITAR', Path('/tmp/sus.sfz'),
            {
                'PALM_MUTE_DOWNPICK': ArticulationMap('PALM_MUTE_DOWNPICK', sfz_path=Path('/tmp/mute.sfz')),
                'OPEN_RELEASE': ArticulationMap('OPEN_RELEASE', sfz_path=Path('/tmp/sus.sfz')),
            },
            'test',
        )
        evidence = evidence_from_profiles(left, right, inst, inst, seed=1988)
        self.assertEqual(evidence.amp_stage_kind, 'real_amp_sim')
        self.assertEqual(evidence.cabinet_ir, '/tmp/cab.wav')
        self.assertNotEqual(evidence.left_performance_id, evidence.right_performance_id)
        self.assertNotEqual(evidence.palm_mute_signature, evidence.sustain_signature)


if __name__ == '__main__':
    unittest.main()
