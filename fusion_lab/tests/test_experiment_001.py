import unittest
from dataclasses import replace
from fusion_lab.glamasaurus_rex import build_glamasaurus_rex
from fusion_lab.experiment import EXPERIMENT_001, build_experiment_001, compare_dimensions, assert_experiment_contract
from fusion_lab.model import HostComposition, RoleTrack

class Experiment001Tests(unittest.TestCase):
    def setUp(self):
        self.host=build_glamasaurus_rex(); self.variants=build_experiment_001(self.host)

    def test_a_is_identical_control(self):
        self.assertEqual(self.variants['A'],self.host)
        self.assertTrue(all(compare_dimensions(self.host,self.variants['A'],'RHYTHM_GUITAR').values()))

    def test_b1_preserves_function_and_macro_structure_but_changes_texture(self):
        dims=compare_dimensions(self.host,self.variants['B1'],'RHYTHM_GUITAR')
        for name in ('global_clock','sections','other_roles','function','harmonic_roots','phrase_bounds','chord_change_grid'):
            self.assertTrue(dims[name],name)
        self.assertFalse(dims['articulation'])
        self.assertFalse(dims['performance_density'])
        arts={e.articulation for e in self.variants['B1'].tracks['RHYTHM_GUITAR'].events}
        self.assertIn('TREMOLO_TEXTURE',arts)

    def test_b2_preserves_host_function_but_changes_voicing_and_register(self):
        dims=compare_dimensions(self.host,self.variants['B2'],'RHYTHM_GUITAR')
        for name in ('global_clock','sections','other_roles','function','harmonic_roots','phrase_bounds','chord_change_grid'):
            self.assertTrue(dims[name],name)
        self.assertFalse(dims['voicing'])
        self.assertFalse(dims['register'])

    def test_c_saturates_guest_vocabulary_beyond_chorus(self):
        c=self.variants['C'].tracks['RHYTHM_GUITAR'].events
        host=self.host.tracks['RHYTHM_GUITAR'].events
        self.assertGreater(len(c),len(host)*2)
        non_chorus_tremolo=[e for e in c if e.articulation=='TREMOLO_TEXTURE' and e.start_tick < self.host.sections[3].start_bar*4*self.host.ticks_per_beat]
        self.assertTrue(non_chorus_tremolo)

    def test_contract_rejects_hidden_harmony_or_timing_mutation(self):
        b1=self.variants['B1']; track=b1.tracks['RHYTHM_GUITAR']; events=list(track.events)
        root=min(e.note for e in self.host.tracks['RHYTHM_GUITAR'].events if e.start_tick < 4*self.host.ticks_per_beat) % 12
        events=[replace(e,note=e.note+1) if e.start_tick < 4*self.host.ticks_per_beat and e.note%12==root else e for e in events]
        tracks=dict(b1.tracks); tracks['RHYTHM_GUITAR']=RoleTrack('RHYTHM_GUITAR',tuple(events),track.program)
        bad=replace(b1,tracks=tracks)
        with self.assertRaisesRegex(ValueError,'FUSION_EXPERIMENT_FROZEN_DIMENSION'):
            assert_experiment_contract(EXPERIMENT_001,self.host,bad)

    def test_all_authored_variants_satisfy_common_contract(self):
        for name,v in self.variants.items():
            with self.subTest(name=name): assert_experiment_contract(EXPERIMENT_001,self.host,v)

if __name__=='__main__': unittest.main()
