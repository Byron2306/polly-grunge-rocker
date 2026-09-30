import json, tempfile, unittest
from pathlib import Path
from fusion_lab.cli import main

class ChimeraCliTests(unittest.TestCase):
    def test_experiment_002_writes_A_to_G_and_unresolved_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'exp-002'
            rc=main(['experiment-002','--out',str(root)])
            self.assertEqual(rc,0)
            self.assertEqual({p.name for p in root.iterdir() if p.is_dir()},set('ABCDEFG'))
            meta=json.loads((root/'experiment.json').read_text())
            self.assertEqual(meta['id'],'exp-002-thrash-chimera')
            self.assertEqual(meta['conclusion_status'],'UNRESOLVED')
            self.assertIn('STYLE != FUNCTION',meta['laws'])
            self.assertTrue((root/'F'/'performer_doom_guitarist.mid').is_file())
            self.assertTrue((root/'F'/'performer_prog_synth.mid').is_file())
            self.assertTrue((root/'G'/'performer_death_drummer.mid').is_file())

    def test_parser_rejects_unknown_variant_command_cleanly(self):
        with self.assertRaises(SystemExit):
            main(['nope'])

if __name__=='__main__': unittest.main()
