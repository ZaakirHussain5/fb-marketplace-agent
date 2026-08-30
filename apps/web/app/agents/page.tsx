'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Agent = {
  id: number;
  name: string;
  phone_number: string;
  enabled: boolean;
  schedule_minutes: number;
  notify_threshold: number;
  last_run_at: string | null;
  next_run_at: string | null;
};

export default function OperationsIndex() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`${API}/api/v1/agents`)
      .then(async response => {
        if (!response.ok) throw new Error('Could not load agents');
        setAgents(await response.json());
      })
      .catch(error => setError(error.message));
  }, []);

  return (
    <main style={{maxWidth:1100,margin:'0 auto',padding:'40px 24px',fontFamily:'Inter,system-ui,sans-serif',color:'#172033'}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:24}}>
        <div><p style={{fontSize:12,letterSpacing:1.4,color:'#64748b'}}>OPERATIONS</p><h1>Agent orchestrator</h1><p style={{color:'#64748b'}}>Run agents and inspect execution history, matches and WhatsApp delivery.</p></div>
        <Link href="/">Management</Link>
      </div>
      {error && <div style={{background:'#fff1f2',color:'#9f1239',padding:12,borderRadius:8}}>{error}</div>}
      <div style={{display:'grid',gap:12}}>
        {agents.map(agent => (
          <Link key={agent.id} href={`/agents/${agent.id}`} style={{textDecoration:'none',color:'inherit'}}>
            <article style={{border:'1px solid #e5e7eb',borderRadius:14,padding:18,display:'grid',gridTemplateColumns:'2fr 1fr 1fr 1fr',gap:16,alignItems:'center',background:'white'}}>
              <div><strong>{agent.name}</strong><div style={{fontSize:13,color:'#64748b'}}>{agent.phone_number}</div></div>
              <div><small>Status</small><div>{agent.enabled ? 'Active' : 'Paused'}</div></div>
              <div><small>Cadence</small><div>{agent.schedule_minutes} min</div></div>
              <div><small>Next run</small><div>{agent.next_run_at ? new Date(agent.next_run_at + 'Z').toLocaleString() : '—'}</div></div>
            </article>
          </Link>
        ))}
        {!agents.length && !error && <p style={{color:'#64748b'}}>No agents configured yet.</p>}
      </div>
    </main>
  );
}
