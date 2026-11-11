# KC Studio dashboard and seven detail modes

Draft implementation specification for [issue #110](https://github.com/RobynAwesome/Introduction-to-MCP/issues/110). Codex Forge is the owner-directed stateless renter. `I_AM_STATELESS_RENTER_NOT_LANDLORD`. Entry acknowledged at `2026-11-07T16:53:05Z`.

## Visitor journey

Open the Studio and see a concise dashboard with a spatial map of the seven destinations. Each destination has a plain-language description and a direct link. Open Context to work with the composer, Swarm to see the roster, MAO to inspect routing, KPEFS to explore its controls, Proof to inspect evidence, CI to inspect repository checks, or Sovereign SIM to inspect simulations. A persistent Dashboard control returns to the overview. Browser history and direct mode URLs reopen the selected detail.

Use `#/console` for the overview and `#/console/<mode>` for detail routes. The Studio root opens the dashboard. Keep explicit Council, Labs, Forge, CRUD and Admin routes. Carry the status contract and unavailable states from [PR #365](https://github.com/RobynAwesome/Introduction-to-MCP/pull/365) forward as the dependency.

## Spatial behavior

The dashboard uses a single seven-point instrument with a central KC marker, perspective, a tilted plane, and a raised focus layer. Focusing or hovering a destination highlights the corresponding point. The pointer can gently tilt the instrument on devices with a fine pointer. The seven HTML links carry all navigation and keyboard interaction. The diagram is decorative to assistive technology. A reduced-motion preference keeps the same diagram and navigation with stationary layers. Use CSS perspective and existing React and Studio styles. This slice requires no external scene assets, renderer dependency, account, or simulation command.

The overview reports only status transport state from the existing validated API response. Evidence counts and pass/fail remain in their established detail views. Missing or malformed status is visible as unavailable. Opening a mode performs navigation and its existing reads. Operational commands remain in the detail views with their existing controls.

## Evidence and feedback loops

| Population | Input and constraint | Readback |
| --- | --- | --- |
| Cloud GSMB | Master `0a8950277656266273b813ce85f93c4230d4b0ff` and #365 `91052744b19a093c996d7cf510a9a015f838bbd6`. Preserve the seven existing modes, status guard and responsive drawers. | Compare the branch with #365, exercise all seven routes, and carry results to root `NOW.md`. |
| Local GSMB | The admitted Home and Legacy records establish a front door to current information, provenance, and continuity. The Local root has a privacy hold for excluded material. | Keep the same clear route from overview to evidence, mark unknowns explicitly, and retain private source material in Local. |
| Drive and owner decisions | The November orientation retained #110's hosted-runtime acceptance hold. The current owner direction selects Studio with the Dashboard entrance. It leaves the backend and receipt store unresolved. | Compare the candidate against the owner direction and keep hosted response and restart retrieval as separate release acceptance checks. |

## Reference observation

The [owner's REA fork](https://github.com/RobynAwesome/rea/tree/b4938aed58737293a6987630476632619713f5cd) defines a browser scenario with declared actions and separate runtime evidence. REA 6.7.0 captured the [Bruno Simon portfolio](https://bruno-simon.com/) in a temporary Edge profile. Both navigation and the settle step completed. The DOM contained a canvas, explicit interaction and recovery controls, and quality options. The selected accessibility capture was sparse. This informed the separation of scene, controls and recovery in Studio. The [NASA Eyes interface](https://science.nasa.gov/eyes/faq/) separately documents browser-based 3D exploration across device classes. Its application served as a design reference from documentation.

REA Evidence `ev_98c93d3a3ee1a10f87f13740a38ade131ef563b6f19d771eb08c887c0d088d6e`, retained local JSON SHA-256 `068a70ff533680f3bd95d735b8bdf537fac7d55b927b2af74f1e02909b10483f`. The 6.7.0 CLI entry could not load an MCP client export on this Windows installation. The same installed release's browser provider, schema and evidence service completed the capture directly. No external code or visual assets are included in Studio.

## Acceptance checks

1. Root loads the Dashboard. Each of the seven links opens the intended detail and can be revisited by URL and browser history. The Dashboard can be reached from detail.
2. Keyboard focus is visible, the diagram follows the selected link, and route changes move focus to the destination heading. At 390 px links remain usable and the page has no horizontal overflow. Reduced-motion settings preserve full navigation without tilt.
3. Status fixtures include valid, unavailable, and malformed successful responses. Proof and CI retain the known #365 behavior, and entry does not call an operational POST.
4. Studio build, UI checks and browser interaction run locally. Record the worktree and revision. Review the stacked source change independently of the hosting cutover.
5. For release, attach the approved Studio hostname, backend and durable receipt store, then capture one hosted chat response and retrieval of the same receipt across a restart or replica change. Azure deploy evidence remains under [#211](https://github.com/RobynAwesome/Introduction-to-MCP/issues/211).

## Implementation readback — 2026-11-11 SAST

- **Cloud GSMB.** Compared the Studio against #365 at its recorded head. Cloud master had advanced to `a4be401d1f2cc837b57230a8d32d1b627b860047` without changes to Studio or the canonical navigation file since the spec baseline. Studio build, UI checks and lint passed. Lint retained five existing warnings and Vite reported the existing chunk-size warning.
- **Local GSMB.** Used the admitted Home and Legacy guidance for an entrance that leads directly to current work and evidence. In Edge, pointer motion and focused destinations changed the same map. All seven links worked by keyboard, history restored Dashboard and detail focus, and a direct Proof link survived reload. On the first mobile run the operator panel obscured the CI link. The panel now opens from its launcher. The 390 px retest passed without horizontal overflow, and reduced motion kept the scene stationary.
- **Drive and owner decisions.** Checked the built journey against the owner direction and the Drive orientation's runtime boundary. The seven destinations share one Studio, and the Dashboard reported valid, malformed and unavailable status fixtures accurately. The browser recorded GET requests only and no page errors. Hosted chat and restart-safe receipt retrieval await an approved backend and receipt store.

KPEFS primary V2_ANIMAL for reliable navigation, secondary V4_DIASPORA for continuity. Bracket and BlackMask scope covers an isolated Cloud-derived candidate, a public reference capture, and a local browser run with fixtures. The author reviewed the stated acceptance checks against the results. Runtime acceptance remains open.
