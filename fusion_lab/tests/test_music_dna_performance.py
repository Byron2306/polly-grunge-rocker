import unittest

from fusion_lab.music_dna.performance import (
    BassPerformanceEvent,
    DrumPerformanceEvent,
    GuitarPerformanceEvent,
    KeyPerformanceEvent,
    VocalPerformanceEvent,
    to_note_event,
)


class PerformanceTests(unittest.TestCase):
    def test_guitar_event_retains_physical_intent_and_converts(self):
        event = GuitarPerformanceEvent(0, 120, 40, 108, 6, 0, 'DOWN', 0.9, 1.0, 'PALM_MUTE', 'E5', 'PEDAL')
        note = to_note_event(event, channel=2)
        self.assertEqual(note.note, 40)
        self.assertEqual(note.articulation, 'PALM_MUTE')
        self.assertEqual(note.function, 'PEDAL')
        self.assertEqual(event.string, 6)
        self.assertEqual(event.fret, 0)
        self.assertEqual(event.pick_direction, 'DOWN')

    def test_performance_bounds_are_enforced(self):
        with self.assertRaises(ValueError):
            GuitarPerformanceEvent(0, 120, 40, 100, 6, 0, 'DOWN', 1.1, 0.5, 'PALM_MUTE', None, 'PEDAL')
        with self.assertRaises(ValueError):
            DrumPerformanceEvent(0, 60, 36, 110, 'FOOT', 'KICK', 'PROPULSION', -0.1)

    def test_other_performance_types_convert(self):
        bass = BassPerformanceEvent(0, 120, 28, 95, 'PICK', 'GUITAR', 'ANCHOR')
        drum = DrumPerformanceEvent(0, 60, 36, 110, 'RIGHT_FOOT', 'KICK', 'PROPULSION', 0.8)
        key = KeyPerformanceEvent(0, 480, 60, 90, 'PAD', 'SUSTAIN')
        vocal = VocalPerformanceEvent(0, 240, None, 0.7, 'SCREAM', 'BARK')
        self.assertEqual(to_note_event(bass, 1).articulation, 'PICK')
        self.assertEqual(to_note_event(drum, 9).note, 36)
        self.assertEqual(to_note_event(key, 3).function, 'PAD')
        self.assertEqual(to_note_event(vocal, 4, fallback_note=60).note, 60)


if __name__ == '__main__':
    unittest.main()
