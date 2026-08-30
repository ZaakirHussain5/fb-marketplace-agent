'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useCallback, useEffect, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Agent = {
  id: number; name: string; phone_number: string; enabled: boolean; schedule_minutes: number;
  notify_threshold: number; instructions: string; filters: Record<string, unknown>;
  last_run_at: string | null; next_run_at: string | null;
};
type Run = {
  id: number; status: string; trigger: string; collected: number; matched: number; notified: number;
  error: string | null; started_at: string | null; finished_at: string | null; created_at: string;
};
type Match = {
  id: number; score: number; reasons: string[]; risks: string[]; delivery_status: string;
  delivery_error: string | null; notified_at: string | null; created_at: string;
  listing: { title: string; price: number | null; currency: string; url: string; city: string | null; state_code: string | null };
};

export default function AgentOperationsPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [agent, setAgent] = useState<Agent | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const [a, r, m] = await Promise.all([
        fetch(`${API}/api/v1/agents/${id}`),
        fetch(`${API}/api/v1/agents/${id}/runs`),
        fetch(`${API}/api/v1/agents/${id}/matches`),
      ]);
      if (!a.ok) throw new Error('Agent not found');
      setAgent(await a.json());
      setRuns(r.ok ? await r.json() : []);
      setMatches(m.ok ? await m.json() : []);
      setError('');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load agent');
    }
  }, [id]);

  useEffect(() => { load(); const timer = setInterval(load, 10000); return () => clearInterval(timer); }, [load]);

  async function runNow() {
    setRunning(true);
    try {
      const response = await fetch(`${API}/api/v1/agents/${id}/run`, { method: 'POST' });
      if (!response.ok) throw new Error(await response.text());
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Run failed');
    } finally { setRunning(false); }
  }

  if (error && !agent) return <main style={styles.main}><Link href="/">← Agents</Link><p>{error}</p></main>;
  if (!agent) return <main style={styles.main}>Loading…</main>;

  return (
    <main style={styles.main}>
      <div style={styles.topbar}>
        <div><Link href="/">← All agents</Link><h1 style={{marginBottom: 4}}>{agent.name}</h1><div style={styles.muted}>{agent.phone_number} · {agent.enabled ? 'Active' : 'Paused'}</div></div>
        <button onClick={runNow} disabled={running} style={styles.button}>{running ? 'Running…' : 'Run now'}</button>
      </div>
      {error && <div style={styles.error}>{error}</div>}

      <section style={styles.stats}>
        <Stat label="Cadence" value={`${agent.schedule_minutes} min`} />
        <Stat label="Threshold" value={`${agent.notify_threshold}%`} />
        <Stat label="Last run" value={fmt(agent.last_run_at)} />
        <Stat label="Next run" value={fmt(agent.next_run_at)} />
      </section>

      <section style={styles.panel}>
        <h2>Instructions</h2>
        <p style={styles.muted}>{agent.instructions || 'No custom instructions.'}</p>
        <h3>Filters</h3>
        <pre style={styles.pre}>{JSON.stringify(agent.filters, null, 2)}</pre>
      </section>

      <section style={styles.panel}>
        <h2>Execution history</h2>
        <div style={{overflowX:'auto'}}><table style={styles.table}><thead><tr><th>ID</th><th>Status</th><th>Trigger</th><th>Collected</th><th>Matched</th><th>Sent</th><th>Started</th><th>Error</th></tr></thead><tbody>
          {runs.map(run => <tr key={run.id}><td>#{run.id}</td><td><span style={badge(run.status)}>{run.status}</span></td><td>{run.trigger}</td><td>{run.collected}</td><td>{run.matched}</td><td>{run.notified}</td><td>{fmt(run.started_at)}</td><td style={{maxWidth:300}}>{run.error || '—'}</td></tr>)}
          {!runs.length && <tr><td colSpan={8}>No runs yet.</td></tr>}
        </tbody></table></div>
      </section>

      <section style={styles.panel}>
        <h2>Matched listing inbox</h2>
        <div style={styles.grid}>
          {matches.map(match => <article key={match.id} style={styles.card}>
            <div style={styles.row}><strong>{match.listing.title}</strong><span style={styles.score}>{match.score}%</span></div>
            <div style={styles.muted}>{match.listing.price == null ? 'Price unavailable' : `$${Number(match.listing.price).toLocaleString()}`} · {[match.listing.city, match.listing.state_code].filter(Boolean).join(', ')}</div>
            <div style={{margin:'10px 0'}}><span style={badge(match.delivery_status)}>{match.delivery_status}</span></div>
            {match.reasons.slice(0,3).map((x,i)=><div key={i}>✓ {x}</div>)}
            {match.risks.slice(0,2).map((x,i)=><div key={i} style={{color:'#a35b00'}}>⚠ {x}</div>)}
            {match.delivery_error && <div style={styles.error}>{match.delivery_error}</div>}
            <a href={match.listing.url} target="_blank" rel="noreferrer" style={{display:'inline-block',marginTop:12}}>Open listing ↗</a>
          </article>)}
          {!matches.length && <p style={styles.muted}>No matches yet. Run the agent to test the pipeline.</p>}
        </div>
      </section>
    </main>
  );
}

function Stat({label,value}:{label:string,value:string}) { return <div style={styles.stat}><div style={styles.muted}>{label}</div><strong>{value}</strong></div>; }
function fmt(value:string|null) { return value ? new Date(value + (value.endsWith('Z') ? '' : 'Z')).toLocaleString() : '—'; }
function badge(status:string) { const ok=['succeeded','sent'].includes(status); const bad=['failed'].includes(status); return {padding:'3px 8px',borderRadius:999,fontSize:12,background:ok?'#dcfce7':bad?'#fee2e2':'#eef2ff',color:ok?'#166534':bad?'#991b1b':'#3730a3'}; }
const styles: Record<string, React.CSSProperties> = {
  main:{maxWidth:1200,margin:'0 auto',padding:'36px 24px',fontFamily:'Inter,system-ui,sans-serif',color:'#172033'},
  topbar:{display:'flex',justifyContent:'space-between',gap:24,alignItems:'center',marginBottom:24},
  button:{border:0,borderRadius:10,padding:'11px 18px',background:'#111827',color:'white',fontWeight:700,cursor:'pointer'},
  muted:{color:'#657083',fontSize:14}, error:{background:'#fff1f2',color:'#9f1239',padding:12,borderRadius:8,margin:'10px 0'},
  stats:{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(160px,1fr))',gap:12,marginBottom:20},stat:{padding:16,border:'1px solid #e5e7eb',borderRadius:12,background:'white'},
  panel:{border:'1px solid #e5e7eb',borderRadius:14,padding:20,marginBottom:20,background:'white'}, pre:{whiteSpace:'pre-wrap',background:'#f7f8fa',padding:14,borderRadius:10,fontSize:12},
  table:{width:'100%',borderCollapse:'collapse',textAlign:'left'},grid:{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(290px,1fr))',gap:14},card:{border:'1px solid #e5e7eb',borderRadius:12,padding:16},row:{display:'flex',justifyContent:'space-between',gap:12},score:{fontWeight:800,color:'#2563eb'}
};
