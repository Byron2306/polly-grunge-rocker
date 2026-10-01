import tempfile
import unittest
from pathlib import Path

import mido

from fusion_lab.music_dna.ingestion import ingest_midi, ingest_musicxml


class IngestionTests(unittest.TestCase):
    def test_midi_ingestion_is_deterministic_and_aggregate_only(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'fixture.mid'
            midi = mido.MidiFile(ticks_per_beat=480)
            track = mido.MidiTrack(); midi.tracks.append(track)
            track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(200), time=0))
            for note in (40, 40, 41, 46):
                track.append(mido.Message('note_on', note=note, velocity=100, time=0))
                track.append(mido.Message('note_off', note=note, velocity=0, time=120))
            midi.save(path)
            a = ingest_midi(path, genre='thrash', artist='Fixture', track='Fixture')
            b = ingest_midi(path, genre='thrash', artist='Fixture', track='Fixture')
            self.assertEqual(a, b)
            self.assertIn('tempo_bpm', a.features)
            self.assertNotIn('notes', a.features)
            self.assertNotIn('tab', a.features)

    def test_musicxml_ingestion_extracts_aggregate_pitch_and_duration_features(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'fixture.musicxml'
            path.write_text('''<?xml version="1.0"?><score-partwise version="3.1"><part-list><score-part id="P1"><part-name>Guitar</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions><time><beats>4</beats><beat-type>4</beat-type></time></attributes><direction><sound tempo="180"/></direction><note><pitch><step>E</step><octave>2</octave></pitch><duration>1</duration></note><note><pitch><step>F</step><octave>2</octave></pitch><duration>1</duration></note></measure></part></score-partwise>''')
            obs = ingest_musicxml(path, genre='black_metal', artist='Fixture', track='Fixture')
            self.assertEqual(obs.features['tempo_bpm'], 180.0)
            self.assertGreater(obs.features['chromatic_step_ratio'], 0.0)
            self.assertNotIn('notes', obs.features)


if __name__ == '__main__':
    unittest.main()
