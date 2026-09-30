import type { AuthoringSession } from './types.js';

export function formatAuthoringReport(session:AuthoringSession):string{
  const corrections=new Map(session.corrections.map(x=>[x.candidateId,x]));
  const lines=[
    `session: ${session.sessionId}`,
    `track: ${session.trackId}`,
    `durationMs: ${session.durationMs}`,
    `inputs: ${session.inputs.length}`,
    '',
    'ADVISORY CANDIDATES',
  ];
  if(session.candidates.length===0) lines.push('  (none)');
  for(const candidate of session.candidates){
    const correction=corrections.get(candidate.id);
    const bits=[
      candidate.id,
      candidate.kind,
      candidate.role??'-',
      `confidence=${candidate.confidence.toFixed(3)}`,
    ];
    if(candidate.startMs!==undefined) bits.push(`time=${candidate.startMs.toFixed(1)}ms`);
    if(candidate.bpm!==undefined) bits.push(`bpm=${candidate.bpm.toFixed(2)}`);
    bits.push(`review=${correction?.decision??'UNREVIEWED'}`);
    lines.push(`  ${bits.join(' | ')}`);
  }
  lines.push('','HUMAN REVIEW');
  if(session.corrections.length===0) lines.push('  (none: candidates remain suggestions only)');
  for(const correction of session.corrections){
    const adjusted=[
      correction.startMs!==undefined?`startMs=${correction.startMs}`:'',
      correction.endMs!==undefined?`endMs=${correction.endMs}`:'',
      correction.bpm!==undefined?`bpm=${correction.bpm}`:'',
    ].filter(Boolean).join(', ');
    lines.push(`  ${correction.candidateId}: ${correction.decision}${adjusted?` (${adjusted})`:''}`);
  }
  lines.push('','Candidate confidence is advisory. Only ACCEPT or ADJUST becomes export-authoritative.');
  return lines.join('\n');
}
