# Design review - evidence and criteria

Scope: web UIs on a local dev server, driven through the Playwright MCP server (`browser_*` tools). If those tools are not available, stop and say so. For native shells see the skill's Rules.

What this pass is good at: visual consistency, measurable accessibility, state coverage, obvious feature gaps. What it is not: a usability study. Models over-rate usability from static screenshots and miss problems that span several screens, so judgments lean on measured data and step-by-step flow captures.

## Evidence to gather (step 4)

1. **Start the app** with the project's own dev entrypoint (see `context.md`; if the project has a documented build-and-preview path because its dev server does not match production routing, use that). Record the URL. Seed or sign in as `context.md` or the user directs.
2. **Write `design/routes.md`**: every route/screen you will cover and, for each, which states exist (default, empty, loading, error, validation error, long content, signed-out).
3. **Per route, per viewport** - 1440x900, 768x1024, 375x812 (`browser_resize`):
   - `browser_snapshot` -> `<route>.snapshot.md` (once per route; this is the structural source of truth - headings, landmarks, names, roles).
   - `browser_take_screenshot` full page -> `<route>--<viewport>--<theme>.png`. Repeat in dark mode if the project supports it (toggle or emulate `prefers-color-scheme`).
   - Each reachable non-default state -> `...--<state>.png`.
4. **Per route, once (desktop viewport):**
   - **axe-core** -> `axe--<route>.json`. Use the project's own axe/pa11y tooling if it has any; otherwise inject axe-core into the page with `browser_evaluate` and save `axe.run()` violations. If a CSP blocks injection, record "axe not available".
   - **Target sizes** -> `targets--<route>.json` via `browser_evaluate`:
     ```js
     () => [...document.querySelectorAll('a,button,input,select,textarea,summary,[role=button],[role=link],[tabindex]:not([tabindex="-1"])')]
       .map(e => { const r = e.getBoundingClientRect(); return { el: e.tagName.toLowerCase() + (e.id ? '#' + e.id : ''), text: (e.innerText || e.getAttribute('aria-label') || '').trim().slice(0, 40), w: Math.round(r.width), h: Math.round(r.height), inline: getComputedStyle(e).display === 'inline' }; })
       .filter(x => x.w > 0 && (x.w < 24 || x.h < 24))
     ```
   - **Console and failed requests** -> `console--<route>.txt`.
   - **Keyboard pass**: Tab through the page; record focus order, any element with no visible focus indicator, any trap, anything reachable by mouse only. Add to `<route>.snapshot.md` under "Keyboard".
   - **Lighthouse** JSON if the project already has it or Lighthouse CI configured.
5. **Key flows** named in `context.md`: capture every step as a numbered sequence (`flow-<name>--01.png` ...) with a one-line neutral caption of the action taken. No commentary.
6. Close the browser and stop the server.

Automated checks catch roughly half of accessibility issues by volume; the keyboard pass and the snapshot are what cover the rest. Do not skip them.

## Dimensions (one judge each)

### usability
Nielsen's ten heuristics, applied to the flow captures and states, not single screenshots: system status visible (loading, saving, success, failure)? Errors say what happened and how to recover? Destructive actions confirmable or undoable? Empty states tell the user what to do next? Labels in the user's language, consistent between screens? Severity follows frequency x impact x persistence. Only report what the evidence shows a user hitting; "might confuse users" with no concrete step is not a finding.

### accessibility
WCAG 2.2 AA. Start from axe violations (cluster by rule and component, confirm each in the snapshot or source), then what tools miss: heading and landmark structure, accessible names that do not match visible text, focus order, focus visibility and focus not obscured (2.4.11), keyboard traps, target size (2.5.8: 24x24 CSS px minimum - inline links in text, and targets with sufficient spacing, are exempt; check before reporting), dragging alternatives (2.5.7), authentication without cognitive tests (3.3.8), reduced-motion handling, form errors tied to fields. Contrast comes from axe, never from a screenshot.

### visual-consistency
Models are reliable here. Compare across routes and viewports: spacing rhythm, type scale, color use against the project's tokens, component variants that should be one component, alignment breaks, overflow/clipping/horizontal scroll at 375 px, dark-mode misses (unthemed surfaces, invisible icons), content jumping between states. Cite two screenshots that disagree, or one screenshot plus the token/source it violates.

### feature-gap
Against what the product says it does (README, PRD, landing copy in `context.md`): promised capabilities with no UI, dead-end flows, missing states (no empty, error, or loading handling), missing table-stakes for the product type (search in a long list, undo for destructive edits, export of user data, settings users will look for). Every gap cites the promise or the dead end. Wish-list features are not findings.
