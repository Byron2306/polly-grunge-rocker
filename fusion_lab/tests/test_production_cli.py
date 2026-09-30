import json, tempfile, unittest
from pathlib import Path
from fusion_lab.cli import main

class ProductionCliTests(unittest.TestCase):
    def test_compose_host003_writes_structural_debug_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'host003'
            self.assertEqual(main(['compose-host003','--out',str(out)]),0)
            manifest=json.loads((out/'manifest.json').read_text())
            self.assertEqual(manifest['host_id'],'host-003-chainsaw-diplomacy')
            self.assertEqual(manifest['bpm'],192)
            self.assertEqual(manifest['bars'],64)
            self.assertTrue(manifest['vocal_windows'])

    def test_review_host003_records_human_authority_state(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'production-manifest.json'
            p.write_text(json.dumps({'authenticity_review':{'state':'PENDING','rubric':{},'notes':[]}}))
            self.assertEqual(main(['review-host003','--manifest',str(p),'--state','ADJUST','--note','more palm-mute punch']),0)
            data=json.loads(p.read_text())
            self.assertEqual(data['authenticity_review']['state'],'ADJUST')
            self.assertIn('more palm-mute punch',data['authenticity_review']['notes'])

if __name__=='__main__': unittest.main()
