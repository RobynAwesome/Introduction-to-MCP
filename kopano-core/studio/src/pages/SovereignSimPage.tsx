import { motion, AnimatePresence } from 'framer-motion';
import { useCallback, useEffect, useRef, useState } from 'react';
import { getApiBase } from '../apiBase';

interface WorldRegion {
  region_id: string;
  kind: string;
  domain?: string;
  codename?: string;
  status?: string;
  agent_count?: number;
  landlord_agent?: string;
  pavement_target?: string;
  domain_label?: string;
  agents_sample?: string[];
}

interface TickResult {
  agent_id: string;
  proceed: boolean;
  event: string;
  token?: string | null;
  plot?: string;
}

interface PlayScore {
  turns: number;
  tokens_collected: number;
  sever_total: number;
  agents_cooked: number;
}

interface SimUi {
  activation_allowed?: boolean;
  gate_verdict?: string;
  agent_total?: number;
  play_score?: PlayScore;
  regions?: WorldRegion[];
  world?: {
    bootstrapped?: boolean;
    regions?: WorldRegion[];
    last_tick?: {
      tick_id?: string;
      proceed_count?: number;
      sever_count?: number;
      results?: TickResult[];
      play_score?: PlayScore;
    };
    play_score?: PlayScore;
  };
  triad?: Record<string, { mode?: string }>;
  kopano_context?: { host?: string };
}

const api = () => `${getApiBase()}/api/kc/phu`;

export function SovereignSimPage() {
  const [ui, setUi] = useState<SimUi | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [playing, setPlaying] = useState(true);
  const [lastResults, setLastResults] = useState<TickResult[]>([]);
  const [flash, setFlash] = useState('');
  const bootOnce = useRef(false);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  const refresh = useCallback(async () => {
    const res = await fetch(`${api()}/sovereign-sim/ui`);
    if (!res.ok) throw new Error(await res.text());
    const data = (await res.json()) as SimUi;
    setUi(data);
    const results = data.world?.last_tick?.results;
    if (results?.length) setLastResults(results);
    return data;
  }, []);

  const playTurn = useCallback(async () => {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`${api()}/sovereign-sim/play`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sample_size: 12 }),
      });
      if (!res.ok) throw new Error(await res.text());
      const tick = await res.json();
      if (tick.verdict === 'BLOCKED') {
        setError(tick.message || 'Gate blocked');
        setPlaying(false);
        return;
      }
      setLastResults(tick.results || []);
      setFlash(`Turn ${tick.play_score?.turns ?? '—'} · +${tick.proceed_count} tokens`);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Play turn failed');
      setPlaying(false);
    } finally {
      setBusy(false);
    }
  }, [refresh]);

  useEffect(() => {
    void (async () => {
      try {
        const data = await refresh();
        if (!bootOnce.current) {
          bootOnce.current = true;
          if (!data.world?.bootstrapped) {
            await fetch(`${api()}/sovereign-sim/bootstrap`, { method: 'POST' });
            await refresh();
          }
          await playTurn();
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'SIM API unreachable — is the backend on :8001?');
      }
    })();
  }, [refresh, playTurn]);

  useEffect(() => {
    if (timer.current) {
      clearInterval(timer.current);
      timer.current = null;
    }
    if (playing) {
      timer.current = setInterval(() => {
        if (!busy) void playTurn();
      }, 4000);
    }
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, [playing, busy, playTurn]);

  const score = ui?.play_score || ui?.world?.play_score || {
    turns: 0,
    tokens_collected: 0,
    sever_total: 0,
    agents_cooked: 0,
  };
  const regions = ui?.world?.regions || ui?.regions || [];
  const plots = regions.filter((r) => r.kind === 'hood_plot');
  const sectors = regions.filter((r) => r.kind === 'thesis_sector');

  return (
    <motion.div
      className="sovereign-play"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      <header className="sovereign-play-hero">
        <div>
          <span className="eyebrow">KPGS Sovereign SIM</span>
          <h2>Play the hood</h2>
          <p>
            You watch GUI tokens only. 300 guilded renters cook on infinite-hood plots.
            Gate {ui?.gate_verdict ?? '…'} · {ui?.agent_total ?? 0} agents.
          </p>
        </div>
        <div className="sovereign-scoreboard">
          <div><strong>{score.turns}</strong><span>turns</span></div>
          <div><strong>{score.tokens_collected}</strong><span>tokens</span></div>
          <div><strong>{score.agents_cooked}</strong><span>cooked</span></div>
          <div><strong>{score.sever_total}</strong><span>severed</span></div>
        </div>
      </header>

      <div className="sovereign-play-actions">
        <button
          type="button"
          className="action-button primary"
          disabled={busy}
          onClick={() => { void playTurn(); }}
        >
          {busy ? 'Cooking…' : 'Next turn'}
        </button>
        <button
          type="button"
          className={`action-button ghost ${playing ? 'active' : ''}`}
          onClick={() => setPlaying((v) => !v)}
        >
          {playing ? 'Pause auto-play' : 'Resume auto-play'}
        </button>
        <button
          type="button"
          className="action-button ghost"
          onClick={() => { void refresh(); }}
        >
          Refresh
        </button>
        {flash && <span className="sovereign-flash">{flash}</span>}
      </div>

      {error && <p className="god-dock-error">{error}</p>}

      <section className="sovereign-play-grid">
        <motion.article className="glass-card sovereign-feed-card" layout>
          <div className="card-topline">
            <span className="eyebrow">Live GUI tokens</span>
            <span className={`signal-chip ${playing ? 'live' : 'neutral'}`}>
              {playing ? 'AUTO' : 'PAUSED'}
            </span>
          </div>
          <ul className="sovereign-feed">
            <AnimatePresence initial={false}>
              {lastResults.map((row) => (
                <motion.li
                  key={`${row.agent_id}-${row.event}`}
                  className={row.proceed ? 'proceed' : 'sever'}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                >
                  <code>{row.agent_id}</code>
                  <span>{row.plot || 'plot'}</span>
                  <strong>{row.event}</strong>
                </motion.li>
              ))}
            </AnimatePresence>
            {!lastResults.length && <li className="empty">Waiting for first cook…</li>}
          </ul>
        </motion.article>

        <motion.article className="glass-card" layout>
          <div className="card-topline">
            <span className="eyebrow">Thesis sectors</span>
            <span className="signal-chip live">{sectors.length}</span>
          </div>
          <div className="sovereign-region-grid">
            {sectors.map((r) => (
              <article key={r.region_id} className="sovereign-region-card thesis">
                <strong>{r.codename || r.region_id}</strong>
                <span>{r.domain_label}</span>
                <p>{r.pavement_target}</p>
              </article>
            ))}
          </div>
          <div className="card-topline" style={{ marginTop: '1rem' }}>
            <span className="eyebrow">Hood plots</span>
            <span className="signal-chip live">{plots.length}</span>
          </div>
          <div className="sovereign-region-grid">
            {plots.map((r) => (
              <article
                key={r.region_id}
                className={`sovereign-region-card plot ${r.status === 'active' ? 'active' : 'parked'}`}
              >
                <strong>{r.domain || r.region_id}</strong>
                <span>{r.landlord_agent}</span>
                <p>{r.agent_count ?? 0} renters</p>
              </article>
            ))}
          </div>
        </motion.article>
      </section>

      <p className="swarm-footnote sovereign-play-footnote">
        Triad: KC {ui?.triad?.kc?.mode ?? 'Save|Watch'} · Cassy {ui?.triad?.cassy?.mode ?? 'execute'} ·{' '}
        Context {ui?.kopano_context?.host ?? 'context.kopanolabs.com'} — tokens leave only through GUI.
      </p>
    </motion.div>
  );
}
