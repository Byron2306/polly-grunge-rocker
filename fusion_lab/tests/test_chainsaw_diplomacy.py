import unittest
from fusion_lab.chainsaw_diplomacy import *


class ChainsawTests(unittest.TestCase):
    def setUp(self):
        self.h = build_chainsaw_diplomacy()

    def test_identity_and_form(self):
        self.assertEqual(
            (self.h.id, self.h.bpm, self.h.numerator, self.h.denominator, self.h.tonal_center),
            ('host-003-chainsaw-diplomacy', 192, 4, 4, 'E'),
        )
        self.assertEqual(tuple(s.bars for s in self.h.sections), FORM_BARS)
        self.assertEqual(sum(FORM_BARS), 64)

    def test_standard_tuned_thrashy_guitar_vocabulary(self):
        guitar = self.h.tracks['RHYTHM_GUITAR'].events
        self.assertGreaterEqual(min(e.note for e in guitar), 40)
        arts = {e.articulation for e in guitar}
        self.assertTrue({'PALM_MUTE_DOWNPICK', 'PALM_MUTE_GALLOP', 'CHROMATIC_POWER', 'OPEN_RELEASE'}.issubset(arts))
        self.assertTrue(any(a and 'GALLOP' in a and 'DOWNPICK' in a for a in arts))
        pcs = {e.note % 12 for e in guitar}
        self.assertTrue({4, 5, 6, 7, 10, 11}.issubset(pcs))

    def test_bass_drums_lead_and_vocal_windows(self):
        self.assertTrue(any(e.articulation == 'PHRASE_END_FILL' for e in self.h.tracks['BASS'].events))
        drum_arts = {e.articulation for e in self.h.tracks['DRUMS'].events}
        self.assertIn('THRASH_SKANK', drum_arts)
        self.assertIn('DOUBLE_KICK_ESCALATION', drum_arts)
        self.assertIn('THRASH_HALF_TIME', drum_arts)
        self.assertNotIn('BLAST_BEAT', drum_arts)
        lead = self.h.tracks['LEAD_KEYS'].events
        self.assertTrue(any(e.articulation == 'LEAD_FAST_RUN' for e in lead))
        self.assertGreaterEqual(max(e.note for e in lead), 72)
        self.assertLessEqual(max(e.note for e in lead), 84)
        kinds = {w.kind for w in chainsaw_vocal_windows(self.h)}
        self.assertTrue({'LONG_SUSTAIN', 'SHORT_BARK', 'SYNCOPATED', 'CROSS_BAR', 'CALL', 'RESPONSE', 'HARMONIC_DOUBLE', 'DISSONANT_DOUBLE'}.issubset(kinds))

    def test_riff_schedule_has_five_distinct_jobs(self):
        schedule = chainsaw_riff_schedule()
        self.assertEqual(len(schedule), 64)
        self.assertEqual(
            {row.family_id for row in schedule},
            {'A_HOOK', 'B_SPRINT', 'C_STOMP', 'D_PANIC', 'E_TRANSITION'},
        )


if __name__ == '__main__':
    unittest.main()
