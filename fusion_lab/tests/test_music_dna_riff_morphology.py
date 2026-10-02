import unittest

from fusion_lab.model import HostComposition, NoteEvent, RoleTrack, Section
from fusion_lab.music_dna.riff_morphology import Gesture, analyze_riff_morphology, signature_for_bar

TPQ = 480
BAR = TPQ * 4


def _tracks(rhythm):
    return {
        'DRUMS': RoleTrack('DRUMS', (), None, True),
        'BASS': RoleTrack('BASS', (), 33, False),
        'RHYTHM_GUITAR': RoleTrack('RHYTHM_GUITAR', tuple(rhythm), 30, False),
        'LEAD_KEYS': RoleTrack('LEAD_KEYS', (), 29, False),
        'VOCALS': RoleTrack('VOCALS', (), 54, False),
    }


def _host(rhythm, bars=4, sections=None):
    if sections is None:
        sections = (Section('main', 0, bars),)
    return HostComposition('fixture', 192, 4, 4, TPQ, 'E', tuple(sections), _tracks(rhythm))


def _cell(base, root=40, art='PALM_MUTE_DOWNPICK'):
    return (
        NoteEvent(base + 0, 160, root, 104, 2, art, 'RHYTHM_SUPPORT'),
        NoteEvent(base + 240, 160, root, 101, 2, art, 'RHYTHM_SUPPORT'),
        NoteEvent(base + 480, 240, root + 6, 114, 2, 'CHROMATIC_POWER', 'TURNAROUND'),
        NoteEvent(base + 960, 720, root + 7, 118, 2, 'OPEN_RELEASE', 'TURNAROUND'),
    )


class RiffMorphologyTests(unittest.TestCase):
    def test_transposed_copy_has_same_morphology_signature(self):
        a = signature_for_bar(_cell(0, 40), 0, BAR)
        b = signature_for_bar(_cell(0, 45), 0, BAR)
        self.assertEqual(a.pitch_contour, b.pitch_contour)
        self.assertEqual(a.onset_pattern, b.onset_pattern)
        self.assertEqual(a.cadence_shape, b.cadence_shape)

        report = analyze_riff_morphology(_host(_cell(0, 40) + _cell(BAR, 45), bars=2))
        self.assertEqual(report.riff_family_count, 1)

    def test_same_pedal_with_different_rhythm_and_cadence_is_distinct(self):
        first = _cell(0, 40)
        second = (
            NoteEvent(BAR + 0, 120, 40, 108, 2, 'PALM_MUTE_GALLOP', 'RHYTHM_SUPPORT'),
            NoteEvent(BAR + 120, 120, 40, 105, 2, 'PALM_MUTE_GALLOP', 'RHYTHM_SUPPORT'),
            NoteEvent(BAR + 240, 120, 40, 110, 2, 'PALM_MUTE_GALLOP', 'RHYTHM_SUPPORT'),
            NoteEvent(BAR + 720, 120, 46, 120, 2, 'CHROMATIC_POWER', 'TURNAROUND'),
        )
        report = analyze_riff_morphology(_host(first + second, bars=2))
        self.assertEqual(report.riff_family_count, 2)

    def test_empty_rhythm_track_reports_zero_families(self):
        report = analyze_riff_morphology(_host((), bars=2))
        self.assertEqual(report.riff_family_count, 0)
        self.assertEqual(report.families, ())

    def test_bar_boundary_onsets_are_counted_once(self):
        events = (
            NoteEvent(BAR - 120, 240, 40, 100, 2, 'OPEN_RELEASE', 'RHYTHM_SUPPORT'),
            NoteEvent(BAR, 120, 43, 100, 2, 'OPEN_RELEASE', 'RHYTHM_SUPPORT'),
        )
        left = signature_for_bar(events, 0, BAR)
        right = signature_for_bar(events, BAR, BAR)
        self.assertEqual(len(left.onset_pattern), 1)
        self.assertEqual(len(right.onset_pattern), 1)

    def test_register_shift_does_not_create_fake_family(self):
        events = _cell(0, 40) + _cell(BAR, 52)
        report = analyze_riff_morphology(_host(events, bars=2))
        self.assertEqual(report.riff_family_count, 1)

    def test_repetitive_song_reports_long_run_and_low_section_contrast(self):
        events = tuple(e for bar in range(8) for e in _cell(bar * BAR, 40))
        sections = (Section('a', 0, 4), Section('b', 4, 4))
        report = analyze_riff_morphology(_host(events, bars=8, sections=sections))
        self.assertEqual(report.longest_same_family_run_bars, 8)
        self.assertLessEqual(report.section_riff_contrast, 0.05)
        self.assertGreaterEqual(report.riff_family_recurrence, 0.95)

    def test_multi_riff_song_reports_family_and_gesture_diversity(self):
        events = []
        for bar in range(4):
            if bar % 2 == 0:
                events.extend(_cell(bar * BAR, 40))
            else:
                base = bar * BAR
                events.extend((
                    NoteEvent(base, 120, 40, 112, 2, 'PALM_MUTE_GALLOP_DOWNPICK', 'RHYTHM_SUPPORT'),
                    NoteEvent(base + 120, 120, 40, 108, 2, 'PALM_MUTE_GALLOP', 'RHYTHM_SUPPORT'),
                    NoteEvent(base + 240, 120, 46, 118, 2, 'CHROMATIC_POWER', 'TURNAROUND'),
                ))
        report = analyze_riff_morphology(
            _host(tuple(events), bars=4),
            explicit_gestures={0: Gesture.HOOK, 1: Gesture.SPRINT, 2: Gesture.HOOK, 3: Gesture.SPRINT},
        )
        self.assertGreaterEqual(report.riff_family_count, 2)
        self.assertGreaterEqual(report.gesture_diversity, 2)
        self.assertLess(report.longest_same_family_run_bars, 4)


if __name__ == '__main__':
    unittest.main()
