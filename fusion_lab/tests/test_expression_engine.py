import unittest
from fusion_lab.model import HostComposition, Section, RoleTrack, NoteEvent, CANONICAL_ROLES
from fusion_lab.expression_model import *
from fusion_lab.expression_engine import *

def host():
    tracks={r:RoleTrack(r,(NoteEvent(0,120,40+i,90,9 if r=='DRUMS' else i),),None if r=='DRUMS' else i, r=='DRUMS') for i,r in enumerate(CANONICAL_ROLES)}
    return HostComposition('h',190,4,4,480,'E',(Section('VERSE',0,4),),tracks)

def regs(handler=None):
    tr={'LONG':StyleTrait('LONG','long')}
    te={'SUSTAINED_MELODIC_LINE':Technique('SUSTAINED_MELODIC_LINE','sustain'), 'DRONE_ANCHOR':Technique('DRONE_ANCHOR','drone')}
    fn={'COUNTER_MELODY':Function('COUNTER_MELODY','counter'), 'RESOLUTION':Function('RESOLUTION','resolve')}
    p={'doom':Performer('doom','Doom',('LEAD_KEYS',),('LONG',),tuple(te))}
    handlers={'SUSTAINED_MELODIC_LINE': handler or (lambda h,r,p,o:(NoteEvent(o.start_tick,240,64,80,3,'SUSTAINED_MELODIC_LINE',r.function_id),)),
              'DRONE_ANCHOR':lambda h,r,p,o:(NoteEvent(o.start_tick,360,52,70,3,'DRONE_ANCHOR',r.function_id),)}
    return ExpressionRegistries(tr,te,fn,p,handlers)

class EngineTests(unittest.TestCase):
    def setUp(self):
        self.h=host(); self.o=Opportunity('o','VERSE',0,960,('COUNTER_MELODY','RESOLUTION'),('LEAD_KEYS',),0.8,960)
        self.r=ExpressionRequest('doom','LONG','SUSTAINED_MELODIC_LINE','COUNTER_MELODY','o','LEAD_KEYS','HOST_CLOCK','HOST_HARMONY','DOOM_GUITAR','SPARSE')

    def test_invalid_reference_refused(self):
        bad=ExpressionRequest('doom','NOPE','SUSTAINED_MELODIC_LINE','COUNTER_MELODY','o','LEAD_KEYS','HOST_CLOCK','HOST_HARMONY','X','SPARSE')
        with self.assertRaisesRegex(ValueError,'unknown trait'): resolve_expression(self.h,bad,regs(),self.o)

    def test_opportunity_function_and_role_enforced(self):
        bad=ExpressionRequest('doom','LONG','SUSTAINED_MELODIC_LINE','PUNCTUATION','o','LEAD_KEYS','x','x','x','x')
        with self.assertRaises(ValueError): resolve_expression(self.h,bad,regs(),self.o)
        bad2=ExpressionRequest('doom','LONG','SUSTAINED_MELODIC_LINE','COUNTER_MELODY','o','BASS','x','x','x','x')
        with self.assertRaises(ValueError): resolve_expression(self.h,bad2,regs(),self.o)

    def test_multiple_expressions_can_overlap_role_family(self):
        e1=resolve_expression(self.h,self.r,regs(),self.o)
        r2=ExpressionRequest('doom','LONG','DRONE_ANCHOR','RESOLUTION','o','LEAD_KEYS','HOST_CLOCK','HOST_HARMONY','DRONE','SPARSE')
        e2=resolve_expression(self.h,r2,regs(),self.o)
        v=apply_expressions(self.h,(e1,e2))
        self.assertEqual(len(v.tracks['LEAD_KEYS'].events),3)
        self.assertEqual(len(self.h.tracks['LEAD_KEYS'].events),1)

    def test_frozen_dimensions_refuse_tempo_meter_sections_or_riff_change(self):
        changed=HostComposition('x',191,4,4,480,'E',self.h.sections,self.h.tracks)
        with self.assertRaises(ValueError): assert_frozen_dimensions(self.h,changed,('tempo',),())
        self.assertTrue(compare_host_dimensions(self.h,self.h)['host_riff'])

    def test_density_budget_refused_unless_saturation_control(self):
        def dense(h,r,p,o):
            return tuple(NoteEvent(i*60,240,64,80,3,'DENSE',r.function_id) for i in range(12))
        with self.assertRaisesRegex(ValueError,'density budget'):
            resolve_expression(self.h,self.r,regs(dense),self.o)
        sat=ExpressionRequest(self.r.performer_id,self.r.trait_id,self.r.technique_id,self.r.function_id,self.r.opportunity_id,self.r.role_family,self.r.rhythmic_policy,self.r.harmonic_policy,self.r.timbral_policy,'SATURATION_CONTROL')
        e=resolve_expression(self.h,sat,regs(dense),self.o)
        self.assertGreater(expression_density((e,),self.o),0.8)

class TechniqueHandlerTests(unittest.TestCase):
    def test_standard_handlers_cover_required_families_and_preserve_clock(self):
        h=host(); o=Opportunity('o','VERSE',0,1920,('COUNTER_MELODY','RESOLUTION','COUNTER_RHYTHM','TEXTURAL_ATMOSPHERE','PROPULSION','ESCALATION'),('LEAD_KEYS','BASS','DRUMS'),1.0,1920)
        handlers=standard_technique_handlers()
        for tech in ('SUSTAINED_MELODIC_LINE','ROLE_LOCAL_CYCLE','SYNTH_SWELL','BLAST_BEAT','DEATH_HALF_TIME','TOM_FILL'):
            self.assertIn(tech,handlers)
        p=Performer('doom','Doom',('LEAD_KEYS',),('LONG',),('SUSTAINED_MELODIC_LINE',))
        r=ExpressionRequest('doom','LONG','SUSTAINED_MELODIC_LINE','COUNTER_MELODY','o','LEAD_KEYS','HOST_CLOCK','HOST_HARMONY','DOOM','SPARSE')
        ev=handlers['SUSTAINED_MELODIC_LINE'](h,r,p,o)
        self.assertGreaterEqual(ev[0].duration_ticks,h.ticks_per_beat*2)
        self.assertEqual(h.bpm,190)

    def test_sustained_melodic_line_is_a_sparse_multi_note_doom_melody(self):
        h=host(); o=Opportunity('o','VERSE',0,7680,('COUNTER_MELODY',),('LEAD_KEYS',),1.0,7680)
        p=Performer('doom','Doom',('LEAD_KEYS',),('LONG',),('SUSTAINED_MELODIC_LINE',))
        r=ExpressionRequest('doom','LONG','SUSTAINED_MELODIC_LINE','COUNTER_MELODY','o','LEAD_KEYS','HOST_CLOCK','HOST_HARMONY','DOOM','SPARSE')
        ev=standard_technique_handlers()['SUSTAINED_MELODIC_LINE'](h,r,p,o)
        self.assertGreaterEqual(len(ev),3)
        self.assertGreater(len({x.note for x in ev}),1)
        self.assertTrue(all(x.duration_ticks >= h.ticks_per_beat*2 for x in ev))
        self.assertTrue(all((x.start_tick-o.start_tick) % (h.ticks_per_beat*2) == 0 for x in ev))
        self.assertLessEqual(max(x.start_tick+x.duration_ticks for x in ev),o.end_tick)

    def test_same_sustain_technique_can_serve_countermelody_and_resolution(self):
        h=host(); o=Opportunity('o','VERSE',0,1920,('COUNTER_MELODY','RESOLUTION'),('LEAD_KEYS',),1.0)
        p=Performer('doom','Doom',('LEAD_KEYS',),('LONG',),('SUSTAINED_MELODIC_LINE',))
        handler=standard_technique_handlers()['SUSTAINED_MELODIC_LINE']
        funcs=[]
        for fn in ('COUNTER_MELODY','RESOLUTION'):
            r=ExpressionRequest('doom','LONG','SUSTAINED_MELODIC_LINE',fn,'o','LEAD_KEYS','HOST_CLOCK','HOST_HARMONY','DOOM','SPARSE')
            funcs.append(handler(h,r,p,o)[0].function)
        self.assertEqual(funcs,['COUNTER_MELODY','RESOLUTION'])

    def test_role_local_cycle_uses_global_ticks_and_converges(self):
        h=host(); o=Opportunity('o','VERSE',0,1920,('COUNTER_RHYTHM',),('BASS',),1.0,1920)
        p=Performer('bass','Djent Bass',('BASS',),('PERCUSSIVE',),('ROLE_LOCAL_CYCLE',),local_cycle=(3,3,2,3,5))
        r=ExpressionRequest('bass','PERCUSSIVE','ROLE_LOCAL_CYCLE','COUNTER_RHYTHM','o','BASS','LOCAL_CYCLE','HOST_HARMONY','THUMB','MEDIUM')
        ev=standard_technique_handlers()['ROLE_LOCAL_CYCLE'](h,r,p,o)
        self.assertEqual(ev[0].start_tick,0)
        self.assertLess(ev[-1].start_tick,o.convergence_tick)
        self.assertEqual(sum(p.local_cycle),16)

    def test_death_handlers_use_percussion_channel(self):
        h=host(); o=Opportunity('o','VERSE',0,960,('ESCALATION',),('DRUMS',),1.0)
        p=Performer('death','Death Drummer',('DRUMS',),('EXTREME_DENSITY',),('BLAST_BEAT',))
        r=ExpressionRequest('death','EXTREME_DENSITY','BLAST_BEAT','ESCALATION','o','DRUMS','HOST_CLOCK','N/A','DEATH_KIT','HIGH')
        ev=standard_technique_handlers()['BLAST_BEAT'](h,r,p,o)
        self.assertTrue(ev)
        self.assertTrue(all(x.channel==9 for x in ev))

if __name__=='__main__': unittest.main()
