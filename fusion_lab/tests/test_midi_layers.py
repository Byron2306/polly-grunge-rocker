import tempfile, unittest
from pathlib import Path
import mido
from fusion_lab.thrash_chimera import resolve_thrash_chimera_variant, CHIMERA_PERFORMER_PROGRAMS
from fusion_lab.midi_io import write_layered_variant_midis, normalized_event_signature

class LayeredMidiTests(unittest.TestCase):
    def test_full_chimera_exports_separate_performer_layers(self):
        host, variant, expressions = resolve_thrash_chimera_variant('F')
        with tempfile.TemporaryDirectory() as td:
            paths=write_layered_variant_midis(host,variant,expressions,Path(td),CHIMERA_PERFORMER_PROGRAMS)
            self.assertIn('performer_doom_guitarist',paths)
            self.assertIn('performer_prog_synth',paths)
            self.assertIn('performer_djent_bassist',paths)
            self.assertIn('performer_death_drummer',paths)
            doom=mido.MidiFile(paths['performer_doom_guitarist'])
            prog=mido.MidiFile(paths['performer_prog_synth'])
            doom_programs=[m.program for t in doom.tracks for m in t if m.type=='program_change']
            prog_programs=[m.program for t in prog.tracks for m in t if m.type=='program_change']
            self.assertEqual(doom_programs,[29])
            self.assertEqual(prog_programs,[88])
            self.assertNotEqual(doom_programs,prog_programs)

    def test_layered_export_is_structurally_deterministic(self):
        host, variant, expressions = resolve_thrash_chimera_variant('F')
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            pa=write_layered_variant_midis(host,variant,expressions,Path(a),CHIMERA_PERFORMER_PROGRAMS)
            pb=write_layered_variant_midis(host,variant,expressions,Path(b),CHIMERA_PERFORMER_PROGRAMS)
            self.assertEqual(set(pa),set(pb))
            for k in pa:
                self.assertEqual(normalized_event_signature(pa[k]), normalized_event_signature(pb[k]), k)

if __name__=='__main__': unittest.main()
