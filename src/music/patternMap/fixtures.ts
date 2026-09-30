import type { PatternMap } from './types.js';

export const REFERENCE_GRUNGE_PATTERN_MAP:PatternMap={
  schema:'polly.pattern-map.v1',
  trackId:'rat-hole-grunge-reference-v1',
  durationMs:8000,
  tempoRegions:[
    {startMs:0,endMs:4000,bpm:120},
    {startMs:4000,endMs:8000,bpm:60},
  ],
  meterRegions:[{startMs:0,endMs:8000,numerator:4,denominator:4}],
  sections:[
    {id:'verse',label:'Verse',startMs:0,endMs:4000},
    {id:'chorus',label:'Chorus',startMs:4000,endMs:8000},
  ],
  layers:{
    DRUMS:{role:'DRUMS',events:[{id:'drums-accent-1',role:'DRUMS',kind:'ACCENT',startMs:1950,endMs:2100,strength:.9}]},
    BASS:{role:'BASS',events:[{id:'bass-cell-1',role:'BASS',kind:'CELL',startMs:1900,endMs:2200,strength:.75,patternId:'grunge-groove-a'}]},
    RHYTHM_GUITAR:{role:'RHYTHM_GUITAR',events:[{id:'rhythm-cell-1',role:'RHYTHM_GUITAR',kind:'CELL',startMs:1900,endMs:2200,strength:.8,patternId:'grunge-riff-a'}]},
    LEAD_KEYS:{role:'LEAD_KEYS',events:[
      {id:'lead-phrase-1',role:'LEAD_KEYS',kind:'PHRASE_START',startMs:1950,endMs:2150,strength:.7},
      {id:'lead-resolution-1',role:'LEAD_KEYS',kind:'RESOLUTION',startMs:3800,endMs:4000,strength:1},
    ]},
    VOCALS:{role:'VOCALS',events:[{id:'vocals-call-1',role:'VOCALS',kind:'ONSET',startMs:1950,endMs:2150,strength:.7}]},
  },
  alignments:[
    {id:'full-band-lock-1',startMs:2000,endMs:2050,eventIds:['drums-accent-1','bass-cell-1','rhythm-cell-1','lead-phrase-1','vocals-call-1'],label:'five-layer lock'},
  ],
};
