import unittest

from fusion_lab.chainsaw_diplomacy import BAR_TICKS, build_chainsaw_diplomacy, chainsaw_riff_schedule
from fusion_lab.model import HostComposition, NoteEvent, RoleTrack, Section
from fusion_lab.music_dna.coupling import extract_coupling_features
from fusion_lab.music_dna.riff_morphology import Gesture


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


def _bar_events(events, bar):
    start = bar * BAR_TICKS
    end = start + BAR_TICKS
    return [event for event in events if start <= event.start_tick < end]


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
        host = make_host((0, 480, 960), (0, 480, 960), tuple(range(60, 1800, 120)))
        result = extract_coupling_features(host, tolerance_ticks=10)
        self.assertLess(result['guitar_kick_coupling'], 0.2)

    def test_sprint_has_more_kick_propulsion_than_stomp(self):
        host = build_chainsaw_diplomacy()
        schedule = chainsaw_riff_schedule()
        sprint_bar = next(row.bar_index for row in schedule if row.gesture == Gesture.SPRINT)
        stomp_bar = next(row.bar_index for row in schedule if row.gesture == Gesture.STOMP)
        drums = host.tracks['DRUMS'].events
        sprint_kicks = [e for e in _bar_events(drums, sprint_bar) if e.note == 36]
        stomp_kicks = [e for e in _bar_events(drums, stomp_bar) if e.note == 36]
        self.assertGreater(len(sprint_kicks), len(stomp_kicks))

    def test_stomp_is_sparse_with_harder_landings(self):
        host = build_chainsaw_diplomacy()
        schedule = chainsaw_riff_schedule()
        stomp_bar = next(row.bar_index for row in schedule if row.gesture == Gesture.STOMP)
        sprint_bar = next(row.bar_index for row in schedule if row.gesture == Gesture.SPRINT)
        drums = host.tracks['DRUMS'].events
        stomp = _bar_events(drums, stomp_bar)
        sprint = _bar_events(drums, sprint_bar)
        self.assertLess(len(stomp), len(sprint))
        self.assertGreaterEqual(max(e.velocity for e in stomp if e.note in {36, 38}), 127)

    def test_panic_contains_double_kick_displacement(self):
        host = build_chainsaw_diplomacy()
        schedule = chainsaw_riff_schedule()
        panic_bar = next(row.bar_index for row in schedule if row.gesture == Gesture.PANIC)
        drums = _bar_events(host.tracks['DRUMS'].events, panic_bar)
        doubles = [e for e in drums if e.articulation == 'DOUBLE_KICK_ESCALATION']
        self.assertGreaterEqual(len(doubles), 4)
        self.assertTrue(any((e.start_tick - panic_bar * BAR_TICKS) % 480 not in {0, 240} for e in doubles))


if __name__ == '__main__':
    unittest.main()
