import unittest
from fusion_lab.glamasaurus_rex import (
    build_glamasaurus_rex, FORM_BARS, VERSE_HARMONY, PRECHORUS_HARMONY, CHORUS_HARMONY
)
from fusion_lab.model import CANONICAL_ROLES

class HostTests(unittest.TestCase):
    def setUp(self): self.host=build_glamasaurus_rex()

    def test_locked_identity_clock_and_form(self):
        h=self.host
        self.assertEqual((h.id,h.bpm,h.numerator,h.denominator,h.tonal_center),('host-001-glamasaurus-rex',138,4,4,'E'))
        self.assertEqual(FORM_BARS,(4,8,4,8,4,8,4,8,8,4,8,4))
        self.assertEqual(tuple(s.bars for s in h.sections),FORM_BARS)
        self.assertEqual(sum(FORM_BARS),72)

    def test_harmonic_skeleton_is_pinned(self):
        self.assertEqual(VERSE_HARMONY,('E5','D5','A5','E5','E5','D5','A5','B5'))
        self.assertEqual(PRECHORUS_HARMONY,('A','B','C#m','B'))
        self.assertEqual(CHORUS_HARMONY,('E','B','C#m','A','E','B','A','B'))

    def test_five_nonempty_tracks(self):
        self.assertEqual(set(self.host.tracks),set(CANONICAL_ROLES))
        for role in CANONICAL_ROLES:
            self.assertGreater(len(self.host.tracks[role].events),0,role)

    def test_drums_have_rock_control_grammar(self):
        drums=self.host.tracks['DRUMS'].events
        self.assertTrue(all(e.channel==9 for e in drums))
        tpq=self.host.ticks_per_beat
        snare_beats={(e.start_tick//tpq)%4 for e in drums if e.note==38}
        self.assertTrue({1,3}.issubset(snare_beats))
        self.assertTrue(any(e.note==49 for e in drums))

    def test_control_host_contains_no_experiment_only_articulations(self):
        banned={'TREMOLO_TEXTURE','DOOM_SUSTAIN','D_BEAT','BLAST','SLAM','DJENT_DISPLACEMENT'}
        tags={e.articulation for t in self.host.tracks.values() for e in t.events if e.articulation}
        self.assertTrue(tags.isdisjoint(banned),tags)

if __name__=='__main__': unittest.main()
