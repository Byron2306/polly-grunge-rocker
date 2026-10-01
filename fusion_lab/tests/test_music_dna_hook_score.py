import unittest

from fusion_lab.model import NoteEvent
from fusion_lab.music_dna.hook_score import score_hook


def motif(pattern, repeats, tpq=480):
    events = []
    tick = 0
    for r in range(repeats):
        for offset, note, dur in pattern:
            events.append(NoteEvent(tick + offset, dur, note, 100, 2, 'PALM_MUTE_DOWNPICK', 'RHYTHM_SUPPORT'))
        tick += tpq * 4
    return tuple(events)


class HookScoreTests(unittest.TestCase):
    def test_recurring_motif_scores_above_random_sequence(self):
        pattern = ((0, 40, 180), (240, 40, 180), (480, 43, 180), (720, 40, 180))
        repeated = motif(pattern, 4)
        randomish = tuple(
            NoteEvent(i * 240, 180, 40 + ((i * i + 3 * i + i // 3) % 11), 100, 2, 'OPEN_RELEASE', 'RHYTHM_SUPPORT')
            for i in range(16)
        )
        self.assertGreater(score_hook(repeated, 480)['total'], score_hook(randomish, 480)['total'])

    def test_exact_short_cycle_over_long_span_is_penalized(self):
        pattern = ((0, 40, 180), (240, 40, 180))
        result = score_hook(motif(pattern, 12), 480)
        self.assertGreater(result['loop_penalty'], 0.0)
        self.assertLess(result['total'], result['recurrence'])

    def test_phrase_end_mutation_is_detected(self):
        base = list(motif(((0, 40, 180), (240, 40, 180), (480, 43, 180), (720, 40, 180)), 3))
        start = 3 * 4 * 480
        base += [
            NoteEvent(start + 0, 180, 40, 100, 2, 'PALM_MUTE_DOWNPICK', 'RHYTHM_SUPPORT'),
            NoteEvent(start + 240, 180, 40, 100, 2, 'PALM_MUTE_DOWNPICK', 'RHYTHM_SUPPORT'),
            NoteEvent(start + 480, 180, 46, 112, 2, 'CHROMATIC_POWER', 'TURNAROUND'),
            NoteEvent(start + 720, 180, 47, 112, 2, 'CHROMATIC_POWER', 'TURNAROUND'),
        ]
        result = score_hook(tuple(base), 480)
        self.assertGreater(result['phrase_end_mutation'], 0.0)


if __name__ == '__main__':
    unittest.main()
