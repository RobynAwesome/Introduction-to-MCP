// This bridge requires the user's local Chromium, filesystem ledger and TTY.
// Compiling its stdio entrypoint does not create a hosted HTTP MCP service.
console.error(
  "KPGS_LOCAL_ONLY: Vercel deployment is blocked. " +
  "Run this bridge locally with npm run build && npm start, using a dedicated " +
  "loopback Chromium profile and the separate human approval CLI. " +
  "A hosted transport and authority/persistence contract require separate review."
);
process.exitCode = 1;
