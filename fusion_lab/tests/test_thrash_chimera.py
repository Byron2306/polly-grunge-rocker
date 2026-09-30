import unittest
from fusion_lab.thrash_chimera import (
    build_thrash_host, build_thrash_chimera_registries,
    build_thrash_chimera_variants, build_thrash_chimera_expression_sets, chimera_variant_metrics,
)
from fusion_lab.expression_engine import compare_host_dimensions

class ThrashHostTests(unittest.TestCase):
    def test_control_host_is_stereotypical_thrash(self):
        h=build_thrash_host()
        self.assertEqual((h.bpm,h.numerator,h.denominator,h.tonal_center),(190,4,4,'E'))
        self.assertEqual([s.id for s in h.sections],['INTRO','VERSE_1','PRE_CHORUS','CHORUS_1','VERSE_2','CHORUS_2','SOLO','BREAK','FINAL_CHORUS','OUTRO'])
        self.assertTrue(any(e.articulation=='THRASH_GALLOP' for e in h.tracks['RHYTHM_GUITAR'].events))
        self.assertFalse(any(e.articulation in {'BLAST_BEAT','DEATH_HALF_TIME','SUSTAINED_MELODIC_LINE','ROLE_LOCAL_CYCLE'} for t in h.tracks.values() for e in t.events))
        guitar_starts={e.start_tick for e in h.tracks['RHYTHM_GUITAR'].events}
        bass_starts={e.start_tick for e in h.tracks['BASS'].events}
        self.assertTrue(guitar_starts.issubset(bass_starts))

    def test_registries_keep_identity_axes_separate(self):
        r=build_thrash_chimera_registries()
        self.assertIn('SUSTAINED_MELODIC_LINE',r.techniques)
        self.assertIn('COUNTER_MELODY',r.functions)
        self.assertNotEqual('SUSTAINED_MELODIC_LINE','COUNTER_MELODY')
        self.assertEqual(r.performers['djent_bassist'].local_cycle,(3,3,2,3,5))

class ThrashVariantsTests(unittest.TestCase):
    def setUp(self):
        self.host=build_thrash_host(); self.v=build_thrash_chimera_variants(); self.sets=build_thrash_chimera_expression_sets()

    def test_A_through_G_exist(self):
        self.assertEqual(set(self.v),set('ABCDEFG'))

    def test_single_recruit_variants_preserve_host_authority(self):
        for key in 'BCDE':
            d=compare_host_dimensions(self.host,self.v[key])
            for dim in ('tempo','meter','sections','host_riff','tonal_center'):
                self.assertTrue(d[dim],(key,dim))
        self.assertTrue(any(e.articulation=='SUSTAINED_MELODIC_LINE' for e in self.v['B'].tracks['LEAD_KEYS'].events))
        self.assertTrue(any(e.articulation=='ROLE_LOCAL_CYCLE' for e in self.v['C'].tracks['BASS'].events))
        self.assertTrue(any(e.articulation in {'SYNTH_SWELL','CHOIR_PAD'} for e in self.v['D'].tracks['LEAD_KEYS'].events))
        death={e.articulation for e in self.v['E'].tracks['DRUMS'].events}
        self.assertTrue({'DOUBLE_KICK_LOCK','BLAST_BEAT','DEATH_HALF_TIME','TOM_FILL'}.issubset(death))

    def test_djent_cycle_shares_global_clock_and_converges(self):
        self.assertEqual(self.v['C'].bpm,190)
        requests=self.sets['C']
        self.assertTrue(all(r.performer_id=='djent_bassist' for r in requests))
        self.assertTrue(any(r.technique_id=='ROLE_LOCAL_CYCLE' for r in requests))

    def test_full_chimera_contains_all_four_performers(self):
        ids={r.performer_id for r in self.sets['F']}
        self.assertEqual(ids,{'doom_guitarist','djent_bassist','prog_synth','death_drummer'})
        lead_ids={r.performer_id for r in self.sets['F'] if r.role_family=='LEAD_KEYS'}
        self.assertEqual(lead_ids,{'doom_guitarist','prog_synth'})

    def test_bad_placement_G_preserves_host_but_is_denser_than_F(self):
        for dim,val in compare_host_dimensions(self.v['F'],self.v['G']).items():
            self.assertTrue(val,(dim,val))
        mf=chimera_variant_metrics('F'); mg=chimera_variant_metrics('G')
        self.assertGreater(mg['density'],mf['density'])
        self.assertGreater(mg['saturation_controls'],mf['saturation_controls'])

if __name__=='__main__': unittest.main()
