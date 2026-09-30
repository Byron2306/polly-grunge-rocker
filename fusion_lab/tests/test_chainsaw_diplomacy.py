import unittest
from fusion_lab.chainsaw_diplomacy import *
class ChainsawTests(unittest.TestCase):
    def setUp(self): self.h=build_chainsaw_diplomacy()
    def test_identity_and_form(self):
        self.assertEqual((self.h.id,self.h.bpm,self.h.numerator,self.h.denominator,self.h.tonal_center),('host-003-chainsaw-diplomacy',192,4,4,'E'))
        self.assertEqual(tuple(s.bars for s in self.h.sections),FORM_BARS); self.assertEqual(sum(FORM_BARS),64)
    def test_standard_tuned_thrashy_guitar_vocabulary(self):
        g=self.h.tracks['RHYTHM_GUITAR'].events
        self.assertGreaterEqual(min(e.note for e in g),40)
        arts={e.articulation for e in g}; self.assertTrue({'PALM_MUTE_DOWNPICK','PALM_MUTE_GALLOP','CHROMATIC_POWER','OPEN_RELEASE'}.issubset(arts))
        pcs={e.note%12 for e in g}; self.assertTrue({4,5,6,7,10,11}.issubset(pcs))
    def test_bass_drums_lead_and_vocal_windows(self):
        self.assertTrue(any(e.articulation=='PHRASE_END_FILL' for e in self.h.tracks['BASS'].events))
        d={e.articulation for e in self.h.tracks['DRUMS'].events}; self.assertIn('THRASH_SKANK',d); self.assertIn('DOUBLE_KICK_ESCALATION',d); self.assertIn('THRASH_HALF_TIME',d); self.assertNotIn('BLAST_BEAT',d)
        l=self.h.tracks['LEAD_KEYS'].events; self.assertTrue(any(e.articulation=='LEAD_FAST_RUN' for e in l)); self.assertTrue(any(e.note>=95 for e in l))
        kinds={w.kind for w in chainsaw_vocal_windows(self.h)}
        self.assertTrue({'LONG_SUSTAIN','SHORT_BARK','SYNCOPATED','CROSS_BAR','CALL','RESPONSE','HARMONIC_DOUBLE','DISSONANT_DOUBLE'}.issubset(kinds))
if __name__=='__main__': unittest.main()
