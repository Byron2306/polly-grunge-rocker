import unittest

from fusion_lab.model import (
    CANONICAL_ROLES,
    ExperimentDefinition,
    HostComposition,
    NoteEvent,
    RoleTrack,
    Section,
)

class ModelTests(unittest.TestCase):
    def test_exactly_five_canonical_roles(self):
        self.assertEqual(CANONICAL_ROLES, ('DRUMS','BASS','RHYTHM_GUITAR','LEAD_KEYS','VOCALS'))

    def test_host_represents_locked_clock_and_tonal_center(self):
        host = HostComposition(
            id='x', bpm=138, numerator=4, denominator=4, ticks_per_beat=480,
            tonal_center='E', sections=(Section('intro',0,4),),
            tracks={role: RoleTrack(role, (), None, role=='DRUMS') for role in CANONICAL_ROLES},
        )
        self.assertEqual((host.bpm,host.numerator,host.denominator,host.tonal_center),(138,4,4,'E'))
        self.assertGreater(host.ticks_per_beat,0)

    def test_note_validation_refuses_invalid_values(self):
        bad = [
            dict(start_tick=-1,duration_ticks=1,note=60,velocity=100,channel=0),
            dict(start_tick=0,duration_ticks=0,note=60,velocity=100,channel=0),
            dict(start_tick=0,duration_ticks=1,note=-1,velocity=100,channel=0),
            dict(start_tick=0,duration_ticks=1,note=128,velocity=100,channel=0),
            dict(start_tick=0,duration_ticks=1,note=60,velocity=0,channel=0),
            dict(start_tick=0,duration_ticks=1,note=60,velocity=128,channel=0),
        ]
        for kwargs in bad:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                NoteEvent(**kwargs)

    def test_sections_cannot_overlap_or_move_backwards(self):
        tracks={role: RoleTrack(role, (), None, role=='DRUMS') for role in CANONICAL_ROLES}
        with self.assertRaises(ValueError):
            HostComposition('x',138,4,4,480,'E',(Section('a',4,2),Section('b',3,2)),tracks)
        with self.assertRaises(ValueError):
            HostComposition('x',138,4,4,480,'E',(Section('a',0,4),Section('b',3,2)),tracks)

    def test_host_track_mapping_is_immutable(self):
        tracks={role: RoleTrack(role, (), None, role=='DRUMS') for role in CANONICAL_ROLES}
        host=HostComposition('x',138,4,4,480,'E',(Section('intro',0,4),),tracks)
        with self.assertRaises(TypeError):
            host.tracks['BASS']=tracks['BASS']

if __name__=='__main__': unittest.main()
