# PROVIDER EXPANSION — PHASED EXECUTION PLAN
## Build from index9.html (v4.7.0) through index14.html

**Goal:** Expand AI provider list with more models (free→paid sorted by output price), add 5 new providers (DeepSeek, Groq, Mistral, Together AI, Cohere), add inline SVG brand logos, surface price/tier info in model picker.

**Baseline:** `index9.html` — LEGO-compliant, all 6 violations resolved, `renderApiKeysPanel()` and `renderTopbar()` auto-generate from `DATA.providers`.

**Core rule:** Each phase produces a new `indexN.html` + `INDEXN_CHANGELOG.md`. Stop at end of each phase. User tests. Only proceed when user confirms.

---

## USER DECISIONS (LOCKED)

| Decision | Answer |
|---|---|
| Which new providers? | All — DeepSeek, Groq, Mistral, Together AI, Cohere |
| OpenRouter as catch-all? | **No.** Individual providers only — user wants per-model control |
| Logo approach | Inline SVG in config (offline, LEGO-compliant) |
| Pre-fill keys from `IP key.txt`? | **No.** Keys entered at runtime via API Keys panel — no hardcoding |
| Cohere timing | **Deferred to Phase 5** — non-OpenAI-compatible, would slow Phase 2 |

---

## PHASE 1 → index10.html
### Data Expansion — Providers + Model Catalog

**Scope:** Pure config changes. No new renderers, no new adapter logic.

**Changes to DATA.providers:**
- Expand existing model lists and add `tier` + `price` fields to every model entry:
  - **Gemini:** add 2.5 Pro, 2.5 Flash, 2.0 Flash Lite (total 5 models, sorted by output price)
  - **OpenAI:** add GPT-4.1, 4.1 Mini, 4.1 Nano, o4-mini (total 7 models, sorted)
  - **Anthropic:** add Haiku 3.5, expand order (total 4+ models, sorted)
- Add 4 new provider entries (Cohere deferred to Phase 5):
  - **DeepSeek:** DeepSeek-V3, DeepSeek-R1
  - **Groq:** Llama 3.3 70B, Llama 3.1 8B, Gemma 2 9B, Mixtral 8x7B (all free tier)
  - **Mistral:** Mistral Small, Medium, Large, Codestral
  - **Together AI:** Llama 3.3 70B, Llama 3.1 405B, Mixtral 8x22B, Qwen 2.5 72B

**New model entry shape:**
```javascript
{ v: 'model-id', l: 'Display Label', tier: 'free' | 'paid', price: 0.28 }
```
(`price` = USD per 1M output tokens. `tier: 'free'` = free tier / free provider.)

**Changes to PROVIDER_DEFAULTS:**
- Add base URLs for DeepSeek, Groq, Mistral, Together (4 new entries)

**What does NOT change in Phase 1:**
- `DATA.providerAdapters` — new providers will appear in UI but cannot send yet (deferred to Phase 2)
- No renderer changes — `renderApiKeysPanel()` auto-picks up the new providers because it iterates `DATA.providers`
- Existing model dropdown will show models but without tier badges (added Phase 4)

**Deliverable:** `index10.html` + `INDEX10_CHANGELOG.md`
**Risk:** Low. No logic changes.
**Estimated context:** Small — mostly additions to the DATA object.

---

## PHASE 2 → index11.html
### Adapters for 4 OpenAI-Compatible Providers

**Scope:** Wire up `unifiedLLMRouter()` to actually send through DeepSeek, Groq, Mistral, Together.

**Changes to DATA.providerAdapters:**
- Add `deepseek` adapter — OpenAI-compatible chat completions format
- Add `groq` adapter — OpenAI-compatible
- Add `mistral` adapter — OpenAI-compatible
- Add `together` adapter — OpenAI-compatible

All four share the same payload/response shape as OpenAI:
```javascript
buildUrl: (base, model, apiKey) => `${base}/chat/completions`
buildHeaders: (apiKey) => ({ 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' })
formatPayload: (history, system, model, rationActive, rationLimit) => ({
  model, messages: [{role:'system', content: system}, ...history], ...
})
parseResponse: (json) => json.choices[0].message.content
```

**Changes to DATA.providers[key].ping:**
- All 4 new providers get `{ type: 'online' }` ping config (cloud APIs — check `navigator.onLine`)

**What does NOT change in Phase 2:**
- No HTML changes
- No renderer changes
- Existing adapters untouched

**Deliverable:** `index11.html` + `INDEX11_CHANGELOG.md`
**Risk:** Low-Medium. 4 adapters, all cloned from OpenAI pattern.
**Estimated context:** Small-Medium — 4 adapter entries.

**Testing checkpoint:** User can paste keys in API Keys panel and successfully send messages through each new provider before we move to Phase 3.

---

## PHASE 3 → index12.html
### Inline SVG Brand Logos

**Scope:** Replace the colored dot in API Keys panel with actual brand SVG logos.

**Changes to DATA.providers:**
- Add `logo` field to all 8 providers (existing 4 + 4 new from Phase 1):
  - Google Gemini, OpenAI, Anthropic, ADAM Server, DeepSeek, Groq, Mistral, Together AI
- Each `logo` holds a minified inline SVG string (Simple Icons brand marks, ~200-500 chars each)
- ADAM Server gets a custom SVG (not a real brand) — likely a stylized "A" or node icon

**Changes to renderApiKeysPanel():**
- Replace `<div class="apikeys-provider-dot">` with `<div class="apikeys-provider-logo">${p.logo}</div>`
- SVG inherits `provider.color` via `fill: currentColor`

**New CSS (minimal):**
```css
.apikeys-provider-logo { width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; }
.apikeys-provider-logo svg { width: 18px; height: 18px; fill: currentColor; }
```

**What does NOT change in Phase 3:**
- No new providers
- No new adapters
- Topbar and other UI keep colored dots unless scope is explicitly expanded

**Deliverable:** `index12.html` + `INDEX12_CHANGELOG.md`
**Risk:** Low. Pure visual layer.
**Estimated context:** Medium — 8 SVG strings are bulky but each is just one config field.

---

## PHASE 4 → index13.html
### Price Tier Badges + Sorted Model Dropdown

**Scope:** Make the model picker show `FREE` badges or `$X.XX/1M` price, sort free→paid by price ascending.

**Changes to model dropdown renderer:**
- Locate current model dropdown build logic (likely in `renderConfigBar()` or a `renderModels()` function — will verify in Phase 4)
- Read `tier` and `price` from each model entry
- Render tier badge: green `FREE` for free models, muted `$X.XX/1M` for paid
- Sort: free first, then paid ascending by price

**New CSS:**
```css
.model-tier-free { color: var(--green); font-size: 10px; font-weight: 700; }
.model-tier-price { color: var(--faint); font-size: 10px; }
```

**What does NOT change in Phase 4:**
- No new providers
- No new adapters
- No HTML structure changes

**Deliverable:** `index13.html` + `INDEX13_CHANGELOG.md`
**Risk:** Low-Medium. Need to locate and update current dropdown logic without breaking switchProvider/switchModel flow.
**Estimated context:** Small-Medium.

---

## PHASE 5 → index14.html
### Cohere Provider (Deferred from Phase 1/2)

**Scope:** Add Cohere as a standalone phase because its API is not OpenAI-compatible.

**Changes to DATA.providers:**
- Add `cohere` entry with: color (#39594D), badge, keyPlaceholder, hasApiKey, ping config, logo (Phase 3 style), models array:
  - Command R (paid, ~$1.50/1M)
  - Command R+ (paid, ~$15/1M)
  - Command A (paid, newest)

**Changes to PROVIDER_DEFAULTS:**
- Add Cohere base URL: `https://api.cohere.com/v2`

**Changes to DATA.providerAdapters:**
- Add `cohere` adapter with custom format:
  - `buildUrl: (base) => `${base}/chat``
  - `buildHeaders: (apiKey) => ({ Authorization: `bearer ${apiKey}`, ... })`
  - `formatPayload: (history, system, model) => ({ model, messages: [...], preamble: system })` — Cohere uses `preamble` not system role
  - `parseResponse: (json) => json.message.content[0].text` — Cohere nests differently

**What does NOT change in Phase 5:**
- No changes to the 4 OpenAI-compatible adapters from Phase 2
- No renderer changes (already supports new providers via LEGO auto-build)

**Deliverable:** `index14.html` + `INDEX14_CHANGELOG.md`
**Risk:** Medium. Custom adapter needs careful testing against Cohere's actual response shape.
**Estimated context:** Small.

---

## PHASE SEQUENCING RULES

1. **Start each phase by copying prior index:** `indexN-1.html` → `indexN.html` is the first action of every phase. No in-place edits.
2. **No scope creep:** Each phase only does what its section describes. If something feels out of scope, defer to a later phase.
3. **Changelog is mandatory:** Every phase ends with `INDEXN_CHANGELOG.md` in the same format as `INDEX8_CHANGELOG.md` / `INDEX9_CHANGELOG.md`.
4. **Update ADAM_MEMORY.md:** At end of each phase, append a session log entry with what was built.
5. **Stop signal:** After delivering the phase's files, send a short completion message and wait. Do not auto-proceed to the next phase.

---

## WHAT EACH PHASE TOUCHES — QUICK REFERENCE

| Phase | File | DATA.providers | DATA.providerAdapters | PROVIDER_DEFAULTS | Renderers | CSS | HTML |
|---|---|---|---|---|---|---|---|
| 1 | index10 | +4 new, +model fields | — | +4 | — | — | — |
| 2 | index11 | — | +4 adapters | — | — | — | — |
| 3 | index12 | +logo field × 8 | — | — | renderApiKeysPanel() update | +2 rules | — |
| 4 | index13 | — | — | — | model dropdown update | +2 rules | — |
| 5 | index14 | +1 (Cohere) | +1 adapter (custom) | +1 | — | — | — |

---

## RESUMPTION PROTOCOL

If a session runs out of context mid-phase:

1. Next session reads `ADAM_MEMORY.md` first
2. Then reads this `PHASES_PLAN.md` to find current phase
3. Checks `build bridge/` for the latest `indexN.html` to determine where work stopped
4. Reads the partial changelog (if any) to see what's already done in the current phase
5. Resumes from the first uncompleted step in the active phase's scope

---

## CURRENT STATE (updated 2026-04-13 — ALL PHASES COMPLETE)

- **Active version:** `index14.html` (**v4.8.0**)
- **Status:** ✅ All 5 phases delivered.
- **Phase 1 → index10.html** ✅ (provider/model expansion with tier+price)
- **Phase 2 → index11.html** ✅ (DeepSeek, Groq, Mistral, Together adapters + state-init LEGO fix)
- **Phase 3 → index12.html** ✅ (inline SVG brand logos for all 8 providers)
- **Phase 4 → index13.html** ✅ (sorted/grouped dropdown + tier pills)
- **Phase 5 → index14.html** ✅ (Cohere provider with custom non-OpenAI v2/chat adapter)
- **Final provider count:** 9 (Gemini, OpenAI, Anthropic, ADAM, DeepSeek, Groq, Mistral, Together AI, Cohere)
- **Final model count:** 38 models across free + paid tiers
- **Keys file:** `IP key.txt` reference only. All keys entered at runtime through the 🔑 API Keys panel.

---

## FINAL NOTE

LEGO Rule 3 — "one entry to add a feature" — is the contract for this entire plan. After Phase 5, adding a new AI provider = adding one entry to `DATA.providers` + one entry to `DATA.providerAdapters` (if non-OpenAI-compatible). No HTML touched. No renderer touched. No CSS touched. This is the finish line.
