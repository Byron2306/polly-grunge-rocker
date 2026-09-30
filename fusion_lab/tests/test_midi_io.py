import tempfile, unittest
from pathlib import Path
import mido
from fusion_lab.glamasaurus_rex import build_glamasaurus_rex
from fusion_lab.midi_io import write_role_midis, normalized_event_signature, host_manifest
from fusion_lab.model import CANONICAL_ROLES

class MidiIoTests(unittest.TestCase):
    def test_writes_five_deterministic_isolated_stems(self):
        host=build_glamasaurus_rex()
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            pa=write_role_midis(host,Path(a)); pb=write_role_midis(host,Path(b))
            self.assertEqual(tuple(pa),CANONICAL_ROLES)
            self.assertEqual([p.name for p in pa.values()],['drums.mid','bass.mid','rhythm_guitar.mid','lead_keys.mid','vocals.mid'])
            for role in CANONICAL_ROLES:
                self.assertEqual(normalized_event_signature(pa[role]),normalized_event_signature(pb[role]))
                mf=mido.MidiFile(pa[role])
                merged=list(mido.merge_tracks(mf.tracks))
                self.assertTrue(any(msg.type=='set_tempo' and round(mido.tempo2bpm(msg.tempo))==138 for msg in merged))
                self.assertTrue(any(msg.type=='time_signature' and msg.numerator==4 and msg.denominator==4 for msg in merged))
                channels={msg.channel for msg in merged if hasattr(msg,'channel') and msg.type in {'note_on','note_off'}}
                expected={9} if role=='DRUMS' else {host.tracks[role].events[0].channel}
                self.assertEqual(channels,expected)

    def test_manifest_has_role_and_host_signatures(self):
        host=build_glamasaurus_rex()
        with tempfile.TemporaryDirectory() as d:
            paths=write_role_midis(host,Path(d))
            manifest=host_manifest(host,paths)
            self.assertEqual(manifest['host_id'],host.id)
            self.assertEqual(set(manifest['role_signatures']),set(CANONICAL_ROLES))
            self.assertRegex(manifest['host_structural_signature'],r'^[0-9a-f]{64}$')

if __name__=='__main__': unittest.main()
