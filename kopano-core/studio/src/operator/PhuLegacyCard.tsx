import { motion } from 'framer-motion';
import { useCallback, useEffect, useState } from 'react';
import { getApiBase } from '../apiBase';
import { useOperator } from './OperatorProvider';

interface SubBrainRow {
  id: string;
  display_name: string;
  attachment: string;
  return_gate: string;
  vault_present: boolean;
}

interface PhuStatus {
  title?: string;
  subtitle?: string;
  breaking_point_protocol?: string;
  bracket_protocol?: {
    breaking_point?: boolean;
    tagline?: string;
    counts?: { attached?: number; detached?: number };
  };
  main_brain?: { population_ratio?: number; present?: number; total?: number };
  sub_brains?: SubBrainRow[];
}

export function PhuLegacyCard() {
  const { isGodMode, runAction } = useOperator();
  const [phu, setPhu] = useState<PhuStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [renterId, setRenterId] = useState('');
  const [hoodAck, setHoodAck] = useState('');

  const refresh = useCallback(async () => {
    try {
      const res = await fetch(`${getApiBase()}/api/kc/phu/ecosystem`);
      if (!res.ok) {
        throw new Error(await res.text());
      }
      setPhu(await res.json());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Phu status failed');
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const bp = phu?.bracket_protocol;
  const detached = phu?.sub_brains?.filter((s) => s.attachment === 'detached') ?? [];

  return (
    <motion.div className="swarm-panel swarm-phu-card" layout>
      <h4>Kopano-Phu · Cassy legacy</h4>
      <p className="swarm-footnote">
        {phu?.subtitle ?? 'Kopano Labs × Ama-Phu Entertainment'}
      </p>
      <div className="swarm-phu-metrics">
        <span className={bp?.breaking_point ? 'swarm-badge ok' : 'swarm-badge warn'}>
          {bp?.breaking_point ? 'Breaking Point' : 'Arming'}
        </span>
        <span className="swarm-badge neutral">
          Main Brain {Math.round((phu?.main_brain?.population_ratio ?? 0) * 100)}%
        </span>
        <span className="swarm-badge neutral">
          {bp?.counts?.attached ?? 0} attached · {bp?.counts?.detached ?? 0} detached
        </span>
      </div>
      {detached.length > 0 && (
        <p className="swarm-footnote">
          Detached: {detached.map((d) => d.display_name).join(', ')}
        </p>
      )}
      <div className="god-dock-actions">
        <button type="button" className="action-button ghost" onClick={() => { void refresh(); }}>
          Refresh Phu
        </button>
      </div>
      {isGodMode && (
        <div className="god-dock-panel">
          <p>Persisted PHU actions require an explicit renter entry. Type the acknowledgement exactly; it is not prefilled.</p>
          <label className="field-shell">
            <span>Renter ID</span>
            <input value={renterId} autoComplete="off" onChange={(e) => setRenterId(e.target.value)} />
          </label>
          <label className="field-shell">
            <span>Type exactly: I_AM_STATELESS_RENTER_NOT_LANDLORD</span>
            <input value={hoodAck} autoComplete="off" spellCheck={false} onChange={(e) => setHoodAck(e.target.value)} />
          </label>
          <div className="god-dock-actions">
            <button
              type="button"
              className="action-button primary"
              disabled={!renterId.trim() || !hoodAck.trim()}
              onClick={() => {
                void runAction('phu_reattach_subbrains', true, {
                  renterId,
                  renterClass: 'stateless_renter',
                  hoodAck,
                });
              }}
            >
              Reattach sub-brains
            </button>
            <button
              type="button"
              className="action-button primary"
              disabled={!renterId.trim() || !hoodAck.trim()}
              onClick={() => {
                void runAction('phu_populate_main_brain', true, {
                  renterId,
                  renterClass: 'stateless_renter',
                  hoodAck,
                });
              }}
            >
              Populate Main Brain
            </button>
          </div>
        </div>
      )}
      {error && <p className="god-dock-error">{error}</p>}
    </motion.div>
  );
}
