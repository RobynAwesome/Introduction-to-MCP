export const consoleModes = [
  { id: 'context', label: 'Context', icon: '⌘' },
  { id: 'swarm', label: 'Swarm', icon: '◎' },
  { id: 'mao', label: 'MAO', icon: '⬡' },
  { id: 'kpefs', label: 'KPEFS', icon: '◈' },
  { id: 'proof', label: 'Proof', icon: '✓' },
  { id: 'ci', label: 'CI', icon: '∿' },
  { id: 'sim', label: 'Sovereign SIM', icon: '▣' },
] as const;

export type ConsoleMode = (typeof consoleModes)[number]['id'];

export function readConsoleMode() {
  const hash = window.location.hash.toLowerCase();
  return consoleModes.find(({ id }) => hash === `#/console/${id}`)?.id ?? null;
}

export function subscribeToConsoleRoute(listener: () => void) {
  window.addEventListener('hashchange', listener);
  return () => window.removeEventListener('hashchange', listener);
}
