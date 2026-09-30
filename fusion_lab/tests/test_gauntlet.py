import json, os, tempfile, unittest
from pathlib import Path
from fusion_lab.cli import main
from fusion_lab.model import CANONICAL_ROLES

class CliTests(unittest.TestCase):
    def test_compose_verify_and_experiment_use_deterministic_paths_without_display(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); host=root/'host'; exp=root/'exp'
            self.assertEqual(main(['compose','--out',str(host)]),0)
            self.assertTrue((host/'manifest.json').is_file())
            self.assertEqual(sorted(p.name for p in host.glob('*.mid')),sorted(['drums.mid','bass.mid','rhythm_guitar.mid','lead_keys.mid','vocals.mid']))
            self.assertEqual(main(['verify-host','--dir',str(host)]),0)
            self.assertEqual(main(['experiment-001','--out',str(exp)]),0)
            for variant in ('A','B1','B2','C'):
                self.assertTrue((exp/variant/'rhythm_guitar.mid').is_file())
            meta=json.loads((exp/'experiment.json').read_text())
            self.assertEqual(meta['conclusion_status'],'UNRESOLVED')
            self.assertEqual(meta['variants'],['A','B1','B2','C'])

class FullGauntletTests(unittest.TestCase):
    def test_headless_fusion_lab_foundation(self):
        from dataclasses import replace
        from fusion_lab.glamasaurus_rex import build_glamasaurus_rex
        from fusion_lab.midi_io import write_role_midis, normalized_event_signature, host_manifest, host_structural_signature
        from fusion_lab.experiment import EXPERIMENT_001, build_experiment_001, compare_dimensions, assert_experiment_contract
        from fusion_lab.model import RoleTrack

        host=build_glamasaurus_rex()
        self.assertEqual((host.bpm,host.numerator,host.denominator,len(host.tracks)),(138,4,4,5))
        before=host_structural_signature(host)
        variants=build_experiment_001(host)
        self.assertEqual(host_structural_signature(host),before)

        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            pa=write_role_midis(host,Path(a)); pb=write_role_midis(host,Path(b))
            self.assertEqual({r:normalized_event_signature(pa[r]) for r in CANONICAL_ROLES},{r:normalized_event_signature(pb[r]) for r in CANONICAL_ROLES})
            generated=host_manifest(host,pa)
            frozen=json.loads((Path(__file__).parents[1]/'data/host-001/manifest.json').read_text())
            self.assertEqual(generated,frozen)

        b1=compare_dimensions(host,variants['B1'],'RHYTHM_GUITAR')
        for key in EXPERIMENT_001.frozen_dimensions: self.assertTrue(b1[key],key)
        self.assertFalse(b1['articulation'])
        b2=compare_dimensions(host,variants['B2'],'RHYTHM_GUITAR')
        self.assertFalse(b2['voicing']); self.assertFalse(b2['register'])
        self.assertGreater(len(variants['C'].tracks['RHYTHM_GUITAR'].events),len(variants['B1'].tracks['RHYTHM_GUITAR'].events))
        self.assertGreater(len(variants['C'].tracks['RHYTHM_GUITAR'].events),len(variants['B2'].tracks['RHYTHM_GUITAR'].events))

        track=variants['B1'].tracks['RHYTHM_GUITAR']; events=list(track.events); bt=host.numerator*host.ticks_per_beat
        root=min(e.note for e in host.tracks['RHYTHM_GUITAR'].events if e.start_tick<bt)%12
        events=[replace(e,note=e.note+1) if e.start_tick<bt and e.note%12==root else e for e in events]
        tracks=dict(variants['B1'].tracks); tracks['RHYTHM_GUITAR']=RoleTrack('RHYTHM_GUITAR',tuple(events),track.program)
        with self.assertRaisesRegex(ValueError,'FUSION_EXPERIMENT_FROZEN_DIMENSION'):
            assert_experiment_contract(EXPERIMENT_001,host,replace(variants['B1'],tracks=tracks))

        lab_root=Path(__file__).parents[1]
        forbidden=('import requests','urllib.request','DISPLAY','X11','VNC','openai','suno')
        for py in lab_root.glob('*.py'):
            text=py.read_text().lower()
            for token in forbidden:
                self.assertNotIn(token.lower(),text, f'{py.name}: {token}')
        for py in lab_root.glob('*.py'):
            self.assertNotIn('src/',py.read_text())

        meta=json.loads((lab_root/'data/experiments/exp-001-style-not-function.json').read_text())
        self.assertEqual(meta['conclusion_status'],'UNRESOLVED')
        self.assertEqual(meta['hypothesis'],EXPERIMENT_001.hypothesis)

if __name__=='__main__': unittest.main()
