import { useState } from 'react';
import type { CSSProperties, PointerEvent, Ref } from 'react';
import { consoleModes } from './consoleRoutes';
import type { ConsoleMode } from './consoleRoutes';
import './StudioDashboard.css';

const descriptions: Record<ConsoleMode, string> = {
  context: 'Open the composer and context tools',
  swarm: 'Explore the agent roster and roles',
  mao: 'Inspect multi-agent routing',
  kpefs: 'Inspect ecosystem vectors',
  proof: 'Review evidence and verification',
  ci: 'Check repository and workflow status',
  sim: 'Explore the simulation controls',
};

interface StudioDashboardProps {
  headingRef: Ref<HTMLHeadingElement>;
  status: 'checking' | 'available' | 'unavailable';
}

const statusLabels = {
  checking: 'Checking Studio API',
  available: 'Studio API responded',
  unavailable: 'Studio API unavailable',
};

function tilt(event: PointerEvent<HTMLDivElement>) {
  if (event.pointerType !== 'mouse' || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const scene = event.currentTarget;
  const bounds = scene.getBoundingClientRect();
  scene.style.setProperty('--tilt-x', `${(0.5 - (event.clientY - bounds.top) / bounds.height) * 16}deg`);
  scene.style.setProperty('--tilt-y', `${((event.clientX - bounds.left) / bounds.width - 0.5) * 20}deg`);
}

export function StudioDashboard({ headingRef, status }: StudioDashboardProps) {
  const [hovered, setHovered] = useState<ConsoleMode | null>(null);
  const [focused, setFocused] = useState<ConsoleMode | null>(null);
  const active = hovered ?? focused;

  return (
    <section className="studio-dashboard" aria-labelledby="studio-dashboard-title">
      <div className="studio-overview">
        <div className="studio-overview-copy">
          <p className="eyebrow">Kopano Context Studio</p>
          <h1 id="studio-dashboard-title" ref={headingRef} tabIndex={-1}>Dashboard</h1>
          <p>Choose a workspace to compose, inspect the swarm, or review its evidence.</p>
          <span className="studio-api-status" role="status" data-state={status}>{statusLabels[status]}</span>
        </div>
        <div
          className="studio-scene"
          aria-hidden="true"
          onPointerMove={tilt}
          onPointerLeave={({ currentTarget }) => {
            currentTarget.style.removeProperty('--tilt-x');
            currentTarget.style.removeProperty('--tilt-y');
          }}
        >
          <div className="studio-plane">
            <div className="studio-ring studio-ring-outer" />
            <div className="studio-ring studio-ring-inner" />
            <div className="studio-core">KC</div>
            {consoleModes.map(({ id, label }, index) => {
              const angle = index * 2 * Math.PI / consoleModes.length - Math.PI / 2;
              const position = {
                '--x': `${50 + 39 * Math.cos(angle)}%`,
                '--y': `${50 + 39 * Math.sin(angle)}%`,
              } as CSSProperties;
              return (
                <div key={id} className="studio-node" style={position} data-active={active === id}>
                  <span className="studio-node-light" />
                  <span>{label}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      <nav className="studio-destinations" aria-label="Studio modes">
        <ul>
          {consoleModes.map(({ id, label, icon }) => (
            <li key={id}>
              <a
                href={`#/console/${id}`}
                onPointerEnter={({ pointerType }) => { if (pointerType === 'mouse') setHovered(id); }}
                onPointerLeave={() => setHovered(null)}
                onFocus={() => setFocused(id)}
                onBlur={() => setFocused(null)}
              >
                <span className="studio-destination-icon" aria-hidden="true">{icon}</span>
                <span><strong>{label}</strong><small>{descriptions[id]}</small></span>
                <span className="studio-destination-arrow" aria-hidden="true">↗</span>
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </section>
  );
}
