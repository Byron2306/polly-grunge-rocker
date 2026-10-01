import unittest

from fusion_lab.model import HostComposition, NoteEvent, RoleTrack, Section
from fusion_lab.music_dna.feature_extractors import extract_host_features


def host_with(guitar_events, *, bpm=200, numerator=4):
    sections = (Section('riff', 0, 2),)
    tracks = {
        'DRUMS': RoleTrack('DRUMS', (), None, True),
        'BASS': RoleTrack('BASS', (), 33, False),
        'RHYTHM_GUITAR': RoleTrack('RHYTHM_GUITAR', tuple(guitar_events), 30, False),
        'LEAD_KEYS': RoleTrack('LEAD_KEYS', (), 29, False),
        'VOCALS': RoleTrack('VOCALS', (), 54, False),
    }
    return HostComposition('fixture', bpm, numerator, 4, 480, 'E', sections, tracks)


class MusicDNAFeatureTests(unittest.TestCase):
    def test_thrashy_fixture_exposes_pedal_mute_and_attack_density(self):
        events = []
        for i in range(12):
            events.append(NoteEvent(i * 240, 120, 40, 105, 2, 'PALM_MUTE_DOWNPICK', 'RHYTHM_SUPPORT'))
        events += [
            NoteEvent(12 * 240, 240, 41, 110, 2, 'CHROMATIC_POWER', 'TURNAROUND'),
            NoteEvent(13 * 240, 240, 46, 112, 2, 'CHROMATIC_POWER', 'TURNAROUND'),
        ]
        values = extract_host_features(host_with(events)).values
        self.assertGreater(values['guitar.palm_mute_ratio'], 0.7)
        self.assertGreater(values['harmony.pedal_note_ratio'], 0.7)
        self.assertGreater(values['guitar.attack_density'], 0.4)

    def test_black_fixture_exposes_tremolo_without_palm_mute(self):
        events = [
            NoteEvent(i * 120, 100, 52 + (i % 5), 95, 2, 'TREMOLO_PICK', 'MELODIC_TEXTURE')
            for i in range(24)
        ]
        values = extract_host_features(host_with(events)).values
        self.assertGreater(values['guitar.tremolo_ratio'], 0.8)
        self.assertLess(values['guitar.palm_mute_ratio'], 0.1)

    def test_doom_fixture_is_sparse_and_sustained(self):
        events = [
            NoteEvent(0, 1440, 40, 100, 2, 'OPEN_RELEASE', 'RHYTHM_SUPPORT'),
            NoteEvent(1920, 1440, 46, 105, 2, 'OPEN_RELEASE', 'RHYTHM_SUPPORT'),
        ]
        values = extract_host_features(host_with(events, bpm=70)).values
        self.assertLess(values['guitar.attack_density'], 0.2)
        self.assertGreater(values['guitar.sustain_ratio'], 0.6)

    def test_non_four_meter_registers_odd_meter_evidence(self):
        values = extract_host_features(host_with([], numerator=7)).values
        self.assertEqual(values['arrangement.odd_meter_probability'], 1.0)

    def test_feature_extraction_is_deterministic(self):
        host = host_with([NoteEvent(0, 240, 40, 100, 2, 'PALM_MUTE_DOWNPICK', 'RHYTHM_SUPPORT')])
        self.assertEqual(extract_host_features(host).values, extract_host_features(host).values)


if __name__ == '__main__':
    unittest.main()
