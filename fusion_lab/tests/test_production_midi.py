import tempfile, unittest
from pathlib import Path
from fusion_lab.chainsaw_diplomacy import build_chainsaw_diplomacy
from fusion_lab.production_midi import humanize_events, write_production_midis
from fusion_lab.production_model import HumanizationProfile, InstrumentProfile, ArticulationMap
class ProductionMidiTests(unittest.TestCase):
    def setUp(self): self.h=build_chainsaw_diplomacy()
    def test_humanization_is_deterministic_and_two_guitars_differ(self):
        p=HumanizationProfile(44,3,4,8,8); e=self.h.tracks['RHYTHM_GUITAR'].events
        l1=humanize_events(self.h,e,p,'rhythm_guitar_L'); l2=humanize_events(self.h,e,p,'rhythm_guitar_L'); r=humanize_events(self.h,e,p,'rhythm_guitar_R')
        self.assertEqual(l1,l2); self.assertNotEqual(l1,r); self.assertEqual([x.note for x in l1],[x.note for x in r])
    def test_unsupported_articulation_refuses(self):
        inst=InstrumentProfile('g','g',Path('/tmp/g.sfz'),{'SUSTAIN':ArticulationMap('SUSTAIN')},'src')
        profiles={k:HumanizationProfile(1) for k in ('rhythm_guitar_L','rhythm_guitar_R','bass','drums','lead_guitar')}
        instruments={k:inst for k in profiles}
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'PRODUCTION_UNSUPPORTED_ARTICULATION'): write_production_midis(self.h,Path(d),profiles,instruments)
if __name__=='__main__': unittest.main()
