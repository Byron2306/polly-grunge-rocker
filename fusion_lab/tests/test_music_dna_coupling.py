import unittest

from fusion_lab.model import HostComposition, NoteEvent, RoleTrack, Section
from fusion_lab.music_dna.coupling import extract_coupling_features


def make_host(guitar_ticks, bass_ticks, kick_ticks):
    def notes(ticks, note, role, articulation):
        return tuple(NoteEvent(t, 120, note, 100, 1 if role == 'BASS' else (9 if role == 'DRUMS' else 2), articulation, 'TEST') for t in ticks)
    return HostComposition(
        'coupling', 200, 4, 4, 480, 'E',
        (Section('riff', 0, 2),),
        {
            'DRUMS': RoleTrack('DRUMS', notes(kick_ticks, 36, 'DRUMS', 'THRASH_KICK'), None, True),
            'BASS': RoleTrack('BASS', notes(bass_ticks, 28, 'BASS', 'PICKED_FOLLOW'), 33, False),
            'RHYTHM_GUITAR': RoleTrack('RHYTHM_GUITAR', notes(guitar_ticks, 40, 'RHYTHM_GUITAR', 'PALM_MUTE_DOWNPICK'), 30, False),
            'LEAD_KEYS': RoleTrack('LEAD_KEYS', (), 29, False),
            'VOCALS': RoleTrack('VOCALS', (), 54, False),
        },
    )


class CouplingTests(unittest.TestCase):
    def test_lock_uses_timing_not_event_counts(self):
        aligned = make_host((0, 240, 480, 720), (0, 240, 480, 720), (0, 240, 480, 720))
        unrelated = make_host((0, 240, 480, 720), (120, 360, 600, 840), (120, 360, 600, 840))
        a = extract_coupling_features(aligned, tolerance_ticks=20)
        b = extract_coupling_features(unrelated, tolerance_ticks=20)
        self.assertGreater(a['guitar_kick_coupling'], 0.9)
        self.assertGreater(a['bass_guitar_lock_rate'], 0.9)
        self.assertLess(b['guitar_kick_coupling'], 0.1)
        self.assertLess(b['bass_guitar_lock_rate'], 0.1)

    def test_dense_unrelated_drums_do_not_fake_coupling(self):
        # Dense 16th-note-ish kick activity, deliberately offset so none of the
        # kicks coincide with the guitar onsets at 0, 480, and 960 ticks.
        host = make_host((0, 480, 960), (0, 480, 960), tuple(range(60, 1800, 120)))
        result = extract_coupling_features(host, tolerance_ticks=10)
        self.assertLess(result['guitar_kick_coupling'], 0.2)


if __name__ == '__main__':
    unittest.main()
