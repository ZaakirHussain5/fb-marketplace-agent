"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type Agent = {
  id: number;
  name: string;
  phone_number: string;
  instructions: string;
  enabled: boolean;
  schedule_minutes: number;
  notify_threshold: number;
  filters: {
    category?: string;
    min_price?: number;
    max_price?: number;
    keywords?: string[];
    exclude_keywords?: string[];
    locations?: Array<{
      state_code: string;
      city?: string;
      radius_miles?: number;
    }>;
  };
  last_run_at: string | null;
  created_at: string;
  updated_at: string;
};

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const STATES = [
  ["AL", "Alabama"], ["AK", "Alaska"], ["AZ", "Arizona"], ["AR", "Arkansas"],
  ["CA", "California"], ["CO", "Colorado"], ["CT", "Connecticut"], ["DE", "Delaware"],
  ["FL", "Florida"], ["GA", "Georgia"], ["HI", "Hawaii"], ["ID", "Idaho"],
  ["IL", "Illinois"], ["IN", "Indiana"], ["IA", "Iowa"], ["KS", "Kansas"],
  ["KY", "Kentucky"], ["LA", "Louisiana"], ["ME", "Maine"], ["MD", "Maryland"],
  ["MA", "Massachusetts"], ["MI", "Michigan"], ["MN", "Minnesota"], ["MS", "Mississippi"],
  ["MO", "Missouri"], ["MT", "Montana"], ["NE", "Nebraska"], ["NV", "Nevada"],
  ["NH", "New Hampshire"], ["NJ", "New Jersey"], ["NM", "New Mexico"], ["NY", "New York"],
  ["NC", "North Carolina"], ["ND", "North Dakota"], ["OH", "Ohio"], ["OK", "Oklahoma"],
  ["OR", "Oregon"], ["PA", "Pennsylvania"], ["RI", "Rhode Island"], ["SC", "South Carolina"],
  ["SD", "South Dakota"], ["TN", "Tennessee"], ["TX", "Texas"], ["UT", "Utah"],
  ["VT", "Vermont"], ["VA", "Virginia"], ["WA", "Washington"], ["WV", "West Virginia"],
  ["WI", "Wisconsin"], ["WY", "Wyoming"]
];

const initialForm = {
  name: "",
  phone_number: "",
  instructions: "Notify me only for listings that look legitimate and clearly match my criteria.",
  enabled: true,
  schedule_minutes: 30,
  notify_threshold: 80,
  category: "vehicles",
  min_price: "",
  max_price: "",
  keywords: "",
  exclude_keywords: "",
  state_code: "CA",
  city: "",
  radius_miles: "50",
};

function tagList(value: string) {
  return value.split(",").map((x) => x.trim()).filter(Boolean);
}

export default function Home() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [panelOpen, setPanelOpen] = useState(false);
  const [editing, setEditing] = useState<Agent | null>(null);
  const [form, setForm] = useState(initialForm);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");

  async function loadAgents() {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/v1/agents`, { cache: "no-store" });
      if (!res.ok) throw new Error("Could not load agents");
      setAgents(await res.json());
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load agents");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadAgents(); }, []);

  const visible = useMemo(() => {
    const q = query.toLowerCase();
    return agents.filter((a) => !q || `${a.name} ${a.phone_number} ${a.filters.category ?? ""}`.toLowerCase().includes(q));
  }, [agents, query]);

  function openCreate() {
    setEditing(null);
    setForm(initialForm);
    setPanelOpen(true);
  }

  function openEdit(agent: Agent) {
    const loc = agent.filters.locations?.[0];
    setEditing(agent);
    setForm({
      name: agent.name,
      phone_number: agent.phone_number,
      instructions: agent.instructions,
      enabled: agent.enabled,
      schedule_minutes: agent.schedule_minutes,
      notify_threshold: agent.notify_threshold,
      category: agent.filters.category ?? "",
      min_price: agent.filters.min_price?.toString() ?? "",
      max_price: agent.filters.max_price?.toString() ?? "",
      keywords: (agent.filters.keywords ?? []).join(", "),
      exclude_keywords: (agent.filters.exclude_keywords ?? []).join(", "),
      state_code: loc?.state_code ?? "CA",
      city: loc?.city ?? "",
      radius_miles: loc?.radius_miles?.toString() ?? "50",
    });
    setPanelOpen(true);
  }

  async function saveAgent(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");
    const payload = {
      name: form.name,
      phone_number: form.phone_number,
      instructions: form.instructions,
      enabled: form.enabled,
      schedule_minutes: Number(form.schedule_minutes),
      notify_threshold: Number(form.notify_threshold),
      filters: {
        category: form.category || undefined,
        min_price: form.min_price ? Number(form.min_price) : undefined,
        max_price: form.max_price ? Number(form.max_price) : undefined,
        keywords: tagList(form.keywords),
        exclude_keywords: tagList(form.exclude_keywords),
        locations: [{
          state_code: form.state_code,
          city: form.city || undefined,
          radius_miles: form.radius_miles ? Number(form.radius_miles) : undefined,
        }],
      },
    };
    try {
      const url = editing ? `${API}/api/v1/agents/${editing.id}` : `${API}/api/v1/agents`;
      const res = await fetch(url, {
        method: editing ? "PATCH" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Could not save agent");
      setPanelOpen(false);
      await loadAgents();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save agent");
    } finally {
      setSaving(false);
    }
  }

  async function toggle(agent: Agent) {
    await fetch(`${API}/api/v1/agents/${agent.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: !agent.enabled }),
    });
    loadAgents();
  }

  async function remove(agent: Agent) {
    if (!window.confirm(`Delete ${agent.name}?`)) return;
    await fetch(`${API}/api/v1/agents/${agent.id}`, { method: "DELETE" });
    loadAgents();
  }

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="brandMark">M</span><span>Marketplace Agent</span></div>
        <nav>
          <button className="navItem active">Agents</button>
          <button className="navItem">Listings</button>
          <button className="navItem">Notifications</button>
          <button className="navItem">Settings</button>
        </nav>
        <div className="sideFoot">US marketplace monitoring</div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">CONTROL CENTER</p>
            <h1>Marketplace agents</h1>
            <p className="muted">Manage independent search agents and WhatsApp destinations.</p>
          </div>
          <button className="primary" onClick={openCreate}>+ New agent</button>
        </header>

        <section className="stats">
          <div className="stat"><span>Total agents</span><strong>{agents.length}</strong></div>
          <div className="stat"><span>Active</span><strong>{agents.filter((a) => a.enabled).length}</strong></div>
          <div className="stat"><span>Paused</span><strong>{agents.filter((a) => !a.enabled).length}</strong></div>
          <div className="stat"><span>Default cadence</span><strong>30m</strong></div>
        </section>

        <div className="toolbar">
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search agents, phone numbers or categories" />
          <span>{visible.length} shown</span>
        </div>

        {error && <div className="error">{error}</div>}

        <section className="grid">
          {loading ? <div className="empty">Loading agents…</div> : visible.map((agent) => {
            const loc = agent.filters.locations?.[0];
            return (
              <article className="agentCard" key={agent.id}>
                <div className="agentHead">
                  <div>
                    <div className="statusRow"><span className={agent.enabled ? "dot on" : "dot"} />{agent.enabled ? "Active" : "Paused"}</div>
                    <h2>{agent.name}</h2>
                    <p>{agent.phone_number}</p>
                  </div>
                  <button className="kebab" onClick={() => openEdit(agent)}>Edit</button>
                </div>

                <div className="chips">
                  {agent.filters.category && <span>{agent.filters.category}</span>}
                  {loc?.state_code && <span>{loc.city ? `${loc.city}, ` : ""}{loc.state_code}</span>}
                  {loc?.radius_miles && <span>{loc.radius_miles} mi</span>}
                </div>

                <div className="range">
                  <div><small>Price range</small><b>${agent.filters.min_price ?? 0} – ${agent.filters.max_price ?? "Any"}</b></div>
                  <div><small>Min score</small><b>{agent.notify_threshold}/100</b></div>
                  <div><small>Checks every</small><b>{agent.schedule_minutes} min</b></div>
                </div>

                <p className="instructions">{agent.instructions || "No custom instructions."}</p>

                <div className="cardActions">
                  <button onClick={() => toggle(agent)}>{agent.enabled ? "Pause" : "Activate"}</button>
                  <button onClick={() => openEdit(agent)}>Configure</button>
                  <button className="dangerLink" onClick={() => remove(agent)}>Delete</button>
                </div>
              </article>
            );
          })}
          {!loading && visible.length === 0 && <div className="empty">No agents yet. Create your first monitoring agent.</div>}
        </section>
      </section>

      {panelOpen && <div className="overlay" onMouseDown={() => setPanelOpen(false)}>
        <aside className="drawer" onMouseDown={(e) => e.stopPropagation()}>
          <div className="drawerHead">
            <div><p className="eyebrow">AGENT CONFIGURATION</p><h2>{editing ? "Edit agent" : "New agent"}</h2></div>
            <button className="close" onClick={() => setPanelOpen(false)}>×</button>
          </div>
          <form onSubmit={saveAgent}>
            <div className="formSection"><h3>Identity & delivery</h3>
              <label>Agent name<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="California Toyota deals" /></label>
              <label>WhatsApp phone number<input required value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} placeholder="+14155552671" /></label>
            </div>

            <div className="formSection"><h3>Marketplace filters</h3>
              <div className="twoCols">
                <label>Category<select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}><option value="vehicles">Vehicles</option><option value="electronics">Electronics</option><option value="home">Home & garden</option><option value="property">Property rentals</option><option value="other">Other</option></select></label>
                <label>State<select value={form.state_code} onChange={(e) => setForm({ ...form, state_code: e.target.value })}>{STATES.map(([code, name]) => <option key={code} value={code}>{name}</option>)}</select></label>
                <label>City<input value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} placeholder="San Diego" /></label>
                <label>Radius (miles)<input type="number" min="1" max="500" value={form.radius_miles} onChange={(e) => setForm({ ...form, radius_miles: e.target.value })} /></label>
                <label>Minimum price<input type="number" min="0" value={form.min_price} onChange={(e) => setForm({ ...form, min_price: e.target.value })} placeholder="5000" /></label>
                <label>Maximum price<input type="number" min="0" value={form.max_price} onChange={(e) => setForm({ ...form, max_price: e.target.value })} placeholder="18000" /></label>
              </div>
              <label>Keywords<input value={form.keywords} onChange={(e) => setForm({ ...form, keywords: e.target.value })} placeholder="Toyota, Camry, hybrid" /><small>Comma-separated</small></label>
              <label>Exclude keywords<input value={form.exclude_keywords} onChange={(e) => setForm({ ...form, exclude_keywords: e.target.value })} placeholder="salvage, parts, wanted" /></label>
            </div>

            <div className="formSection"><h3>Agent behavior</h3>
              <label>Instructions<textarea rows={5} value={form.instructions} onChange={(e) => setForm({ ...form, instructions: e.target.value })} /></label>
              <div className="twoCols">
                <label>Check every<select value={form.schedule_minutes} onChange={(e) => setForm({ ...form, schedule_minutes: Number(e.target.value) })}><option value={15}>15 minutes</option><option value={30}>30 minutes</option><option value={60}>1 hour</option><option value={180}>3 hours</option><option value={360}>6 hours</option></select></label>
                <label>Notification score<input type="number" min="0" max="100" value={form.notify_threshold} onChange={(e) => setForm({ ...form, notify_threshold: Number(e.target.value) })} /></label>
              </div>
              <label className="toggleRow"><input type="checkbox" checked={form.enabled} onChange={(e) => setForm({ ...form, enabled: e.target.checked })} /> Activate immediately</label>
            </div>

            <div className="drawerActions"><button type="button" onClick={() => setPanelOpen(false)}>Cancel</button><button className="primary" disabled={saving}>{saving ? "Saving…" : editing ? "Save changes" : "Create agent"}</button></div>
          </form>
        </aside>
      </div>}
    </main>
  );
}
