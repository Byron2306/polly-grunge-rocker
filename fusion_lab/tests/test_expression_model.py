import unittest
from fusion_lab.expression_model import StyleTrait, Technique, Function, Performer, Opportunity

class ExpressionModelTests(unittest.TestCase):
    def test_trait_technique_function_are_independent(self):
        trem = Technique('TREMOLO_PICKING','rapid repeated picking')
        lead = Function('MELODIC_LEAD','lead line')
        bed = Function('HARMONIC_BED','sustained support')
        self.assertNotEqual(trem.id, lead.id)
        self.assertNotEqual(trem.id, bed.id)
        self.assertEqual({lead.id, bed.id}, {'MELODIC_LEAD','HARMONIC_BED'})

    def test_one_function_can_have_multiple_techniques(self):
        fn = Function('PUNCTUATION','accent')
        self.assertEqual(fn.id,'PUNCTUATION')
        self.assertNotEqual(Technique('PINCH_HARMONIC','overtone').id, Technique('TOM_FILL','fill').id)

    def test_role_affinity_does_not_define_function(self):
        p = Performer('doom','Doom Guitar',('LEAD_KEYS',),('LONG_SUSTAIN',),('SUSTAINED_MELODIC_LINE',))
        self.assertEqual(p.role_affinities,('LEAD_KEYS',))

    def test_opportunity_validation(self):
        with self.assertRaises(ValueError): Opportunity('x','VERSE',10,10,('COUNTER_MELODY',),('LEAD_KEYS',),0.5)
        with self.assertRaises(ValueError): Opportunity('x','VERSE',0,10,('COUNTER_MELODY',),('LEAD_KEYS',),1.2)

    def test_local_cycle_must_be_positive(self):
        with self.assertRaises(ValueError):
            Performer('bass','Bass',('BASS',),('PERCUSSIVE',),('ROLE_LOCAL_CYCLE',),local_cycle=(3,0,5))

if __name__=='__main__': unittest.main()
