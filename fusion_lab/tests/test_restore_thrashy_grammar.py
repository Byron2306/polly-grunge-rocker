import json
import unittest
from pathlib import Path

from fusion_lab.chainsaw_diplomacy import BAR_TICKS, build_chainsaw_diplomacy

MUTES = {'PALM_MUTE_DOWNPICK', 'PALM_MUTE_GALLOP'}


class RestoreThrashGrammarTests(unittest.TestCase):
    def setUp(self):
        self.host = build_chainsaw_diplomacy()

    def _bar_signature(self, bar):
        start = bar * BAR_TICKS
        end = start + BAR_TICKS
        return tuple(
            (e.start_tick - start, e.note, e.duration_ticks, e.articulation)
            for e in self.host.tracks['RHYTHM_GUITAR'].events
            if start <= e.start_tick < end
        )

    def test_riff_does_not_repeat_as_three_bar_machine(self):
        self.assertNotEqual(self._bar_signature(0), self._bar_signature(3))
        self.assertNotEqual(self._bar_signature(4), self._bar_signature(7))

    def test_verse_kick_reinforces_majority_of_muted_attacks(self):
        verse = next(s for s in self.host.sections if s.id == 'verse1')
        start = verse.start_bar * BAR_TICKS
        end = verse.end_bar * BAR_TICKS
        mute_ticks = {
            e.start_tick
            for e in self.host.tracks['RHYTHM_GUITAR'].events
            if start <= e.start_tick < end and e.articulation in MUTES
        }
        kick_ticks = {
            e.start_tick
            for e in self.host.tracks['DRUMS'].events
            if start <= e.start_tick < end and e.note == 36
        }
        reinforced = len(mute_ticks & kick_ticks) / len(mute_ticks)
        self.assertGreaterEqual(reinforced, 0.60)

    def test_proot_profile_avoids_known_silent_mute_patch(self):
        path = Path(__file__).parents[1] / 'data' / 'production' / 'instruments.proot.json'
        layers = json.loads(path.read_text())['layers']
        for layer_name in ('rhythm_guitar_L', 'rhythm_guitar_R'):
            layer = layers[layer_name]
            fallback = layer['sfz_path']
            for articulation in ('PALM_MUTE_DOWNPICK', 'PALM_MUTE_GALLOP'):
                self.assertEqual(layer['articulations'][articulation]['sfz_path'], fallback)
                self.assertNotIn('Mute_Down.sfz', layer['articulations'][articulation]['sfz_path'])


if __name__ == '__main__':
    unittest.main()
