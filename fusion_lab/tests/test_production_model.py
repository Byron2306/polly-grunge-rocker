import unittest
from pathlib import Path
from fusion_lab.production_model import *
class ProductionModelTests(unittest.TestCase):
    def test_bounds_and_review(self):
        HumanizationProfile(1,10,8,20,12)
        with self.assertRaises(ValueError): HumanizationProfile(1,99,0,0,0)
        with self.assertRaises(ValueError): ToneProfile('x',(),pan=2)
        with self.assertRaises(ValueError): AuthenticityReview('NOPE',(),{})
    def test_instrument_needs_source_and_articulation(self):
        art=ArticulationMap('PALM_MUTE')
        p=InstrumentProfile('g','guitar',Path('/tmp/g.sfz'),{'PALM_MUTE':art},'src')
        self.assertIn('PALM_MUTE',p.articulations)
        with self.assertRaises(ValueError): InstrumentProfile('g','guitar',Path('/tmp/g.sfz'),{},'src')
    def test_tone_stage_cannot_encode_function(self):
        with self.assertRaises(ValueError): ToneStage('musical_function')
if __name__=='__main__': unittest.main()
