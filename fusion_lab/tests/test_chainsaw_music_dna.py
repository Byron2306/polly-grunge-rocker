import unittest
from pathlib import Path

from fusion_lab.chainsaw_diplomacy import BAR_TICKS, build_chainsaw_diplomacy, chainsaw_riff_schedule
from fusion_lab.music_dna.analysis import analyze_host
from fusion_lab.music_dna.genre_profiles import load_seed_genre_profiles


DATA_ROOT = Path(__file__).resolve().parents[1] / 'data' / 'music_dna' / 'genres'


class ChainsawMusicDNATests(unittest.TestCase):
    def test_chainsaw_analysis_is_deterministic_and_explainable(self):
        profile = load_seed_genre_profiles(DATA_ROOT)['THRASH_CLASSIC']
        host = build_chainsaw_diplomacy()
        a = analyze_host(host, profile)
        b = analyze_host(host, profile)
        self.assertEqual(a.to_dict(), b.to_dict())
        self.assertEqual(a.genre_profile, 'THRASH_CLASSIC')
        self.assertIn('guitar_kick_coupling', a.coupling)
        self.assertIn('total', a.hook_score)
        self.assertIn('riff_family_count', a.riff_structure)
        self.assertIn(a.decision.state.value, {'ALLOW', 'MUTATE', 'REJECT'})

    def test_chainsaw_report_contains_no_opaque_only_score(self):
        profile = load_seed_genre_profiles(DATA_ROOT)['THRASH_CLASSIC']
        report = analyze_host(build_chainsaw_diplomacy(), profile)
        payload = report.to_dict()
        self.assertIn('reasons', payload['decision'])
        self.assertIn('feature_vector', payload)
        self.assertIn('coupling', payload)
        self.assertIn('hook_score', payload)
        self.assertIn('riff_structure', payload)

    def test_chainsaw_enters_preferred_classic_thrash_envelope(self):
        profile = load_seed_genre_profiles(DATA_ROOT)['THRASH_CLASSIC']
        report = analyze_host(build_chainsaw_diplomacy(), profile)
        values = report.feature_vector
        self.assertEqual(report.decision.state.value, 'ALLOW', report.decision.reasons)
        self.assertGreaterEqual(values['guitar.downpick_ratio'], 0.55)
        self.assertGreaterEqual(values['guitar.gallop_rate'], 0.12)
        self.assertGreaterEqual(values['harmony.chromaticity'], 0.30)
        self.assertGreaterEqual(values['harmony.tritone_rate'], 0.08)
        self.assertGreaterEqual(values['drums.double_kick_density'], 0.12)
        self.assertGreaterEqual(values['bass.fill_probability'], 0.08)
        self.assertLessEqual(report.coupling['bass_guitar_lock_rate'], 0.90)
        self.assertGreaterEqual(report.coupling['bass_kick_lock_rate'], 0.45)
        self.assertGreaterEqual(report.riff_structure['riff_family_count'], 5)
        self.assertLessEqual(report.riff_structure['longest_same_family_run_bars'], 4)
        self.assertGreaterEqual(report.riff_structure['gesture_diversity'], 5)

    def test_explicit_riff_schedule_covers_five_physical_behaviors(self):
        schedule = chainsaw_riff_schedule()
        families = {row.family_id for row in schedule}
        gestures = {row.gesture.value for row in schedule}
        self.assertTrue({'A_HOOK', 'B_SPRINT', 'C_STOMP', 'D_PANIC', 'E_TRANSITION'}.issubset(families))
        self.assertTrue({'HOOK', 'SPRINT', 'STOMP', 'PANIC', 'TRANSITION'}.issubset(gestures))
        self.assertEqual(len(schedule), 64)

    def test_gallop_cells_keep_explicit_downpick_anchor_semantics(self):
        host = build_chainsaw_diplomacy()
        rhythm = host.tracks['RHYTHM_GUITAR'].events
        hybrid = [e for e in rhythm if e.articulation and 'GALLOP' in e.articulation and 'DOWNPICK' in e.articulation]
        self.assertTrue(hybrid)

    def test_sections_do_not_all_recycle_the_same_opening_riff_cell(self):
        host = build_chainsaw_diplomacy()
        rhythm = host.tracks['RHYTHM_GUITAR'].events
        signatures = []
        for section in host.sections:
            start = section.start_bar * BAR_TICKS
            end = start + BAR_TICKS
            cells = tuple(
                (event.start_tick - start, event.note, event.duration_ticks, event.articulation)
                for event in rhythm
                if start <= event.start_tick < end
            )
            signatures.append(cells)
        self.assertGreaterEqual(len(set(signatures)), 4)

    def test_lead_stays_in_guitar_like_register_and_uses_phrase_space(self):
        host = build_chainsaw_diplomacy()
        lead = host.tracks['LEAD_KEYS'].events
        self.assertTrue(lead)
        self.assertLessEqual(max(event.note for event in lead), 84)
        self.assertGreaterEqual(min(event.note for event in lead), 52)
        starts = sorted(event.start_tick for event in lead)
        self.assertTrue(any(b - a >= 480 for a, b in zip(starts, starts[1:])))

    def test_rhythm_section_keeps_aggro_velocity_and_double_kick_pressure(self):
        host = build_chainsaw_diplomacy()
        drums = host.tracks['DRUMS'].events
        bass = host.tracks['BASS'].events
        backbeats = [e for e in drums if e.function == 'BACKBEAT']
        double_kicks = [e for e in drums if e.articulation == 'DOUBLE_KICK_ESCALATION']
        picked_bass = [e for e in bass if e.articulation == 'PICKED_FOLLOW']
        self.assertTrue(backbeats)
        self.assertGreaterEqual(min(e.velocity for e in backbeats), 123)
        self.assertGreaterEqual(len(double_kicks), 24)
        self.assertTrue(picked_bass)
        self.assertGreaterEqual(min(e.velocity for e in picked_bass), 98)

    def test_family_boundaries_trigger_transition_fills(self):
        host = build_chainsaw_diplomacy()
        schedule = chainsaw_riff_schedule()
        boundaries = {
            row.bar_index * BAR_TICKS
            for previous, row in zip(schedule, schedule[1:])
            if previous.family_id != row.family_id
        }
        bass_fills = [e for e in host.tracks['BASS'].events if e.function == 'GROOVE_FILL']
        drum_fills = [e for e in host.tracks['DRUMS'].events if e.function == 'TRANSITION']
        self.assertTrue(any(any(abs(e.start_tick - boundary) <= BAR_TICKS for boundary in boundaries) for e in bass_fills))
        self.assertTrue(any(any(abs(e.start_tick - boundary) <= BAR_TICKS for boundary in boundaries) for e in drum_fills))


if __name__ == '__main__':
    unittest.main()
