import tempfile
import unittest
from pathlib import Path

import mido

from fusion_lab.chainsaw_diplomacy import build_chainsaw_diplomacy
from fusion_lab.production_midi import write_articulation_midis
from fusion_lab.production_model import ArticulationMap, HumanizationProfile, InstrumentProfile


class ArticulationSfzRoutingTests(unittest.TestCase):
    def test_rhythm_guitar_is_split_by_authored_articulation(self):
        host = build_chainsaw_diplomacy()
        authored = {e.articulation for e in host.tracks['RHYTHM_GUITAR'].events}
        self.assertIn('PALM_MUTE_GALLOP_DOWNPICK', authored)
        self.assertIn('CHROMATIC_POWER_DOWNPICK', authored)
        arts = {
            name: ArticulationMap(name, sfz_path=Path(f'/tmp/{name}.sfz'))
            for name in (
                'PALM_MUTE_DOWNPICK',
                'PALM_MUTE_GALLOP',
                'OPEN_RELEASE',
                'CHROMATIC_POWER',
            )
        }
        inst = InstrumentProfile('gtx', 'RHYTHM_GUITAR', Path('/tmp/fallback.sfz'), arts, 'metal-gtx')
        with tempfile.TemporaryDirectory() as d:
            result = write_articulation_midis(
                host,
                Path(d),
                'rhythm_guitar_L',
                HumanizationProfile(1988, 2, 4, 7, 8),
                inst,
            )
            self.assertEqual(set(result), set(arts))
            self.assertNotIn('PALM_MUTE_GALLOP_DOWNPICK', result)
            self.assertNotIn('CHROMATIC_POWER_DOWNPICK', result)
            for art, path in result.items():
                self.assertTrue(path.is_file())
                notes = [
                    msg.note
                    for track in mido.MidiFile(path).tracks
                    for msg in track
                    if msg.type == 'note_on' and msg.velocity > 0
                ]
                self.assertTrue(notes, art)
                self.assertTrue(all(note >= 40 for note in notes), art)

    def test_articulation_path_is_part_of_map(self):
        p = Path('/tmp/Mute_Down.sfz')
        art = ArticulationMap('PALM_MUTE', sfz_path=p)
        self.assertEqual(art.sfz_path, p)


if __name__ == '__main__':
    unittest.main()
