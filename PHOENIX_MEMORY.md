# 🐦‍🔥 PHOENIX MEMORY FILE
> Read this first. No exceptions. Append to SESSION LOG at the end of every session.
> Last Updated: 2026-04-13

---

## PROJECT IDENTITY

**PHOENIX** is the architect — the one reading this file and doing the work.

**ADAM** is the product — a single-file browser-based AI chat interface. It runs entirely client-side with localStorage persistence. No build tools, no framework. The only server dependency is `server.js` which acts as a CORS proxy for providers that block direct browser calls.

- **Current file:** `index14.html` — v4.8.0
- **Providers:** 9 — Gemini, OpenAI, Anthropic, ADAM Server, DeepSeek, Groq, Mistral, Together AI, Cohere
- **Models:** 38 across free and paid tiers
- **All build phases:** complete. No active phase work.

---

## ARCHITECTURE — index14.html

### DATA Object — single source of truth
```
DATA.providers        — 9 LLM providers (each has name, models, logo, color, adapter config)
DATA.providerAdapters — dispatch config per provider (buildUrl, buildHeaders, formatPayload, parseResponse)
DATA.assistants       — AI personas
DATA.bloods           — behavioral modifiers (~11 entries)
DATA.hyperBloods      — 80+ deep prompt modifiers across 10 groups
DATA.tools            — toolbar button definitions
DATA.topBarActions    — top bar button definitions
DATA.skills           — toggleable capabilities
DATA.toys             — fused logic wrappers
DATA.philosophies     — reasoning frameworks (lotfy, lego, html_lego)
DATA.exportFormats    — export format definitions
DATA.enhanceLenses    — prompt rewriter definitions (11 lenses)
DATA.addMenuItems     — add menu items
DATA.toolsMenuItems   — tools dropdown items
DATA.canvasTypes      — canvas type definitions
DATA.connectors       — external connector definitions
DATA.widgets          — floating widget definitions (quota, inception, slicer, ration)
```

### PROVIDER_DEFAULTS — base URLs
```
gemini:    https://generativelanguage.googleapis.com
openai:    https://api.openai.com
anthropic: http://localhost:3000   ← requires local bridge (server.js)
adam:      http://127.0.0.1:3000
deepseek:  https://api.deepseek.com
groq:      https://api.groq.com/openai/v1
mistral:   https://api.mistral.ai/v1
together:  https://api.together.xyz/v1
cohere:    https://api.cohere.com
```

### State Object
```
state.asst              — current assistant key
state.skills            — Set of active skill keys
state.bloods            — Set of active blood keys
state.activeToy         — current toy key or null
state.messages          — chat history array
state.attachments       — pending file attachments
state.guillotineActive  — fluff auto-regeneration
state.tribunalActive    — 3-persona deliberation mode
state.schismActive      — split A/B response mode
state.precogActive      — auto follow-up prediction
state.tollgateActive    — vague prompt blocker
state.canvasModeActive  — route output to canvas editor
state.contextDepth      — slicer depth (0 = all)
state.rationActive      — output token limiter armed
state.rationLimit       — max tokens when ration armed
state.swarmActive       — draft-critique-final loop
state.omniGlassActive   — tri-model simultaneous execution
state.activePhilosophy  — current philosophy key or null
state.cache             — echo cache for repeat queries
```

### LEGO Renderers
```
renderTopbar()           — topbar buttons from DATA.topBarActions
renderToolbar()          — input bar tools from DATA.tools
renderExportDropdown()   — export menu from DATA.exportFormats
renderEnhanceDropdown()  — enhance menu from DATA.enhanceLenses
renderAddMenu()          — add menu from DATA.addMenuItems
renderToolsMenu()        — tools dropdown from DATA.toolsMenuItems
renderCanvasMenu()       — canvas submenu from DATA.canvasTypes
renderConnectors()       — connectors list from DATA.connectors
renderApiKeysPanel()     — API key rows from DATA.providers
renderWidgets()          — floating widgets from DATA.widgets
renderLegoUI()           — master caller for all 10 renderers above
```

### Core Functions
```
unifiedLLMRouter()        — generic API dispatch via DATA.providerAdapters
sendMessage()             — main send logic with all mode branching
enhancePrompt()           — blood-based prompt rewriting
applyHyperBlood()         — hyper-blood prompt rewriting
pingAPI()                 — provider health check
saveState() / loadState() — localStorage persistence
init()                    — boot sequence, runs on page load
saveApiKeys()             — reads DOM inputs → updates API_KEYS runtime + localStorage
```

### localStorage Keys
```
adam_key_<provider>      — API key per provider (e.g. adam_key_groq)
adam_ip_<provider>       — custom endpoint per provider
adam_default_provider    — last selected provider
adam_ui_state            — full serialized state object
```

---

## POWER FEATURES

| Feature | How | What it does |
|---|---|---|
| Void | per-message button | Hides message from AI context |
| Anchor | per-message button | Pins message into system prompt |
| Inception | widget | Injects fake exchange into memory |
| Black Hole | topbar button | Compresses history into dense summary |
| Swarm | toggle | Draft → Critique → Final (3-pass) |
| Tribunal | toggle | Architect + Destroyer + Visionary → Synthesis |
| Schism | toggle | Standard vs Alternative side-by-side |
| Omni-Glass | toggle | Gemini + OpenAI + Anthropic simultaneous |
| Precog | toggle | Predicts 3 follow-up questions |
| Toll Gate | toggle | Blocks vague prompts |
| Guillotine | toggle | Auto-regenerates on fluff detection |
| Canvas Mode | toggle | Routes output to split-screen editor |
| Context Slicer | widget | Limits how many past messages AI sees |
| Output Ration | widget | Hard token cap on output |
| Echo Cache | automatic | Caches responses by prompt hash |
| Sniper | per-message button | Micro-edits one specific AI response |
| Philosophy Engine | config bar | Prepends reasoning framework to system prompt |

---

## KNOWN BUGS FIXED

| Version | Bug | Fix |
|---|---|---|
| index14.html | `saveApiKeys()` hardcoded to 4 providers — keys for Groq, DeepSeek, Mistral, Together, Cohere never saved or loaded | Changed to `Object.keys(DATA.providers).forEach(...)` |
| index14.html | `testProviderKey()` only has explicit branches for gemini, openai, anthropic, adam — the 5 newer providers fall through silently | Not yet fixed — needs LEGO refactor to use adapter config |

---

## ACTIVE PHASE PLAN — index16.html (BUG D → B → C)

**Working file:** `index16.html` (byte-identical copy of index15 made 2026-04-14, RULE 4)
**Rollback point:** `index15.html` — frozen with all model lists clean (see INDEX15_CHANGELOG.md)
**Order locked in by Adam:** D first (active money-waster), then B (small UX fix), then C (LEGO refactor)

### Phase 1 — GitHub Pages ✅ LIVE 2026-04-14
- URL: https://taeiadam-dev.github.io/adam-chat/
- Repo: https://github.com/taeiadam-dev/adam-chat
- index16.html pushed as index.html (main branch, 305KB)
- GitHub Pages enabled on main/root via API
- CRITICAL: GitHub API calls MUST go via Chrome MCP javascript_tool (Adam's browser). Bash sandbox cannot reach github.com (proxy 403). Never use python requests or curl for GitHub API.
- Next: Phase 2 = n8n Anthropic proxy workflow

### Phase D — Fix key-cache staleness ✅ SHIPPED 2026-04-14 (see INDEX16_CHANGELOG.md)
- **Symptom:** User pastes new API key in 🔑 API Keys panel → clicks Save → router still uses the OLD key. Only a full page reload picks up the new key. This is what made Together look "broken" mid-session even after the working key was saved.
- **Root cause:** Router caches `API_KEYS[provider]` at page boot and mutations to `localStorage` don't propagate.
- **Fix options (pick during phase, do not pre-commit):**
  - Option A — router reads `localStorage.getItem('adam_key_'+p)` fresh on every send (simple, slight overhead)
  - Option B — `saveApiKeys()` hot-updates `API_KEYS` in memory after writing to `localStorage` (faster, requires every save path to call it)
- **Deliverable:** index16.html with Phase D applied + INDEX16_CHANGELOG.md section "Phase D"
- **Stop condition:** live test — paste new key, click Save (no reload), send message, response uses new key → PASS. Stop and wait for Adam.

### Phase B — Persist activeProvider + activeModel in adam_ui_state
- **Symptom:** Reload the page → always lands on default Gemini, even if user was using DeepSeek/Together/etc.
- **Root cause:** `adam_ui_state` saves panel positions, theme, etc. but does not include the currently-selected provider or model.
- **Fix:** Add `activeProvider` and `activeModel` to the `saveUiState()` payload; restore them in `loadUiState()` and trigger the same `onProviderChange` / model-select pipeline that runs on user click.
- **Deliverable:** index16.html with Phase B applied + INDEX16_CHANGELOG.md section "Phase B"
- **Stop condition:** live test — switch to DeepSeek, pick a specific model, reload page, dropdowns still on DeepSeek + that model → PASS. Stop and wait for Adam.

### Phase C — LEGO refactor of testProviderKey (lowest urgency, biggest scope)
- **Symptom:** "Test Key" button only works for gemini/openai/anthropic/adam. The 5 newer providers (deepseek/groq/mistral/together/cohere) silently do nothing.
- **Root cause:** `testProviderKey()` is a switch statement with 4 hardcoded branches — direct LEGO violation.
- **Fix:** Move per-provider test logic into each provider's DATA entry as a `test: { method, path, headers, parseOk }` config, then make `testProviderKey()` a generic function that reads that config. Same pattern as the `ping` config already used.
- **Deliverable:** index16.html with Phase C applied + INDEX16_CHANGELOG.md section "Phase C"
- **Stop condition:** live test — for every one of the 9 providers, click Test Key, get correct ✅/❌ result → PASS. Stop and wait for Adam.

### Out-of-band item (whenever Adam pastes the key)
- **Cohere never live-verified.** `IP key.txt` ends abruptly at "Cohere API Key p". Need full key from Adam, then run the same PONG test that verified the others.

---

## SESSION LOG

### 2026-04-13 — All 5 build phases completed
- index9 through index14 built across 7 sessions
- 9 providers, 38 models, all LEGO violations resolved
- saveApiKeys bug found and fixed in index14.html

### 2026-04-14 — config.json scrubbed (security cleanup)
- Adam noticed config.json existed in the same folder and asked if it needed updating
- Audit: server.js (Node, what Adam runs) does NOT read config.json. Only bridge.py (Python fallback) does, and only when browser request lacks x-api-key header.
- config.json had Adam's real paid Gemini and Anthropic keys in plaintext — leak risk if folder ever shared/zipped/pushed.
- Replaced both real keys with placeholders + added `_comment` explaining the file's role and forbidding real keys
- Verified: `python3 -c "import json; json.load(open('config.json'))"` → PARSE OK
- Decision for future Phoenix: NEVER put real keys in config.json. Source of truth = localStorage + IP key.txt (for recovery). config.json stays scrubbed.

### 2026-04-14 — index16.html: Phase D shipped (key-cache staleness fix)
- Copied index15.html → index16.html per RULE 4
- Added `getApiKey(p)` and `getApiIp(p)` helpers that always read fresh from localStorage with the in-memory `API_KEYS` / `API_IPS` as fallback only
- Routed 5 critical reads through the helpers: ping endpoint base (line 2420), router pre-flight key (2845), router base URL (2849), testProviderKey key (4594), testProviderKey ip (4595)
- Live-tested with `fetch` monkey-patched to capture+abort calls (zero credit burned). Tampered localStorage → router used tampered key. Restored localStorage → router used real key. Both without page reload, both without Save button. PASS.
- Test mishap: first attempt called `unifiedLLMRouter` directly from console. That function is closure-private; the ReferenceError killed the test IIFE before it could restore the tampered Gemini key. Adam had to paste the key again. Future Phoenix: drive sends through `adamChat.sendMessage()`, never call closure-internal functions directly.
- IP key.txt rewritten with the full working key set (Gemini + Anthropic + Cohere were missing/truncated). Cohere key injected into localStorage for the first time; Cohere live-test still pending.

### 2026-04-14 — index15.html: dead-model purge (Gemini + Anthropic), keep all working tiers
- Copied index14.html → index15.html per RULE 4
- Live-probed every Gemini and Anthropic model ID with Adam's paid keys; 6 of 7 Gemini and 3 of 5 Anthropic IDs returned 404 (deprecated by providers)
- Replaced DATA.providers.gemini.models with verified-working cheap-first list: gemini-2.5-flash-lite, gemini-2.5-flash, gemini-flash-latest, gemini-pro-latest, gemini-2.5-pro
- Replaced DATA.providers.anthropic.models with verified-working cheap-first list: claude-haiku-4-5-20251001, claude-sonnet-4-5, claude-sonnet-4-6, claude-opus-4-5, claude-opus-4-6
- Adam clarification mid-session: do NOT remove expensive models — users may want them. Cheap-first ordering is enough; the user picks. Only fully-dead 404 IDs were removed.
- Live PONG test through real fetch (Gemini direct, Anthropic via bridge): 9/10 PASS. Only gemini-2.5-pro returned 503 ("high demand") — model exists, transient Google capacity, kept in list.
- Decision for future Phoenix: when adding a new Anthropic or Gemini model, live-probe it FIRST. Provider model IDs deprecate silently. Never trust documentation alone. Never delete a model from DATA without Adam's say-so just because it's expensive — sort, don't strip.
- Outstanding bugs (not fixed this session): BUG D (key cache stale until reload), BUG B (activeProvider/activeModel not in adam_ui_state), BUG C (testProviderKey only has 4 explicit branches, 5 newer providers fall through)

---

## RULES FOR FUTURE PHOENIX

### RULE 1 — READ BEFORE YOU TOUCH ANYTHING
Read this file first. Every session. No exceptions. Do not write a single line of code until you have read this file completely. If the user gives you a task and you have not read this file yet — stop and read it first.

---

### RULE 2 — LEGO OR NOTHING
Every feature is a data entry. If adding something requires touching HTML structure or JS functions — stop. The architecture is broken and that needs fixing before the feature is added.

---

### RULE 3 — NEVER BUILD WITHOUT A PHASE PLAN
Any task that touches more than one function or adds more than one thing must be broken into phases before work starts. Present the phase plan to the user and wait for confirmation before writing any code.

A phase plan looks like this:
- Phase 1 — what changes, what file is produced, what is the stop condition
- Phase 2 — same
- Each phase has exactly one deliverable and one stop signal
- After delivering a phase — stop. Do not auto-proceed. Wait for the user to confirm.

This prevents choking. If context runs out mid-phase, the next session reads this file, sees the phase plan, finds the last delivered file, and resumes from exactly where work stopped. No re-explaining. No starting over.

---

### RULE 4 — COPY THEN EDIT, NEVER EDIT IN PLACE
When modifying any HTML file:
1. Copy the current file to a new version first (e.g. index14.html → index15.html)
2. Make all changes in the new file only
3. The old file stays untouched as a rollback point
4. Never edit the active file directly

---

### RULE 5 — TEST LIVE, NEVER ASK THE USER TO TEST
After any change, run the live test yourself using the browser tools. Read the keys from `IP key.txt`, inject them into localStorage, reload the page, send a message, verify the response. Report pass or fail. The user's only job is to double-click START.bat once. Everything after that is yours.

---

### RULE 6 — SESSION LOG FORMAT
At the end of every session add one entry to SESSION LOG in this exact format:

```
### YYYY-MM-DD — What was done (one line title)
- What changed and why
- What was tested and what the result was
- Any bugs found or fixed
- Any decisions made that future Phoenix needs to know
```

Nothing else. No stories. No explanations. No re-stating rules that already exist in this file.
