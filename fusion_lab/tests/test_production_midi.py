import tempfile, unittest
from pathlib import Path
from fusion_lab.chainsaw_diplomacy import build_chainsaw_diplomacy
from fusion_lab.production_midi import humanize_events, write_production_midis
from fusion_lab.production_model import HumanizationProfile, InstrumentProfile, ArticulationMap


class ProductionMidiTests(unittest.TestCase):
    def setUp(self):
        self.h = build_chainsaw_diplomacy()

    def test_humanization_is_deterministic_and_two_guitars_differ(self):
        p = HumanizationProfile(44, 3, 4, 8, 8)
        e = self.h.tracks['RHYTHM_GUITAR'].events
        l1 = humanize_events(self.h, e, p, 'rhythm_guitar_L')
        l2 = humanize_events(self.h, e, p, 'rhythm_guitar_L')
        r = humanize_events(self.h, e, p, 'rhythm_guitar_R')
        self.assertEqual(l1, l2)
        self.assertNotEqual(l1, r)
        self.assertEqual([x.note for x in l1], [x.note for x in r])

    def test_rhythm_humanization_preserves_chord_cohesion_but_shapes_note_lengths(self):
        p = HumanizationProfile(44, 3, 4, 9, 10)
        source = self.h.tracks['RHYTHM_GUITAR'].events
        rendered = humanize_events(self.h, source, p, 'rhythm_guitar_L')
        source_by_key = {(e.start_tick, e.note): e for e in source}
        changed_lengths = 0
        by_original_onset = {}
        for event in rendered:
            candidates = [s for s in source if s.note == event.note and abs(s.start_tick - event.start_tick) <= 32]
            self.assertTrue(candidates)
            nearest = min(candidates, key=lambda s: abs(s.start_tick - event.start_tick))
            by_original_onset.setdefault(nearest.start_tick, set()).add(event.start_tick)
            if event.duration_ticks != nearest.duration_ticks:
                changed_lengths += 1
        self.assertTrue(all(len(onsets) == 1 for onsets in by_original_onset.values()))
        self.assertGreater(changed_lengths, 0)

    def test_phrase_boundaries_are_looser_than_sprint_interior(self):
        p = HumanizationProfile(44, 3, 4, 12, 10)
        source = self.h.tracks['RHYTHM_GUITAR'].events
        rendered = humanize_events(self.h, source, p, 'rhythm_guitar_R')
        offsets = []
        for event in rendered:
            candidates = [s for s in source if s.note == event.note and abs(s.start_tick - event.start_tick) <= 40]
            if not candidates:
                continue
            nearest = min(candidates, key=lambda s: abs(s.start_tick - event.start_tick))
            offsets.append((nearest.function, abs(event.start_tick - nearest.start_tick)))
        sprint = [offset for function, offset in offsets if function == 'RIFF_SPRINT']
        transition = [offset for function, offset in offsets if function == 'RIFF_TRANSITION']
        self.assertTrue(sprint and transition)
        self.assertLessEqual(sum(sprint) / len(sprint), sum(transition) / len(transition))

    def test_unsupported_articulation_refuses(self):
        inst = InstrumentProfile('g', 'g', Path('/tmp/g.sfz'), {'SUSTAIN': ArticulationMap('SUSTAIN')}, 'src')
        profiles = {k: HumanizationProfile(1) for k in ('rhythm_guitar_L', 'rhythm_guitar_R', 'bass', 'drums', 'lead_guitar')}
        instruments = {k: inst for k in profiles}
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, 'PRODUCTION_UNSUPPORTED_ARTICULATION'):
                write_production_midis(self.h, Path(d), profiles, instruments)


if __name__ == '__main__':
    unittest.main()
