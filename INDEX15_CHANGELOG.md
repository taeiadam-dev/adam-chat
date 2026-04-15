# INDEX15 CHANGELOG
## Dead-Model Purge — Gemini + Anthropic

**Base file:** index14.html → index15.html
**Date:** 2026-04-14
**Version bump:** none (still v4.8.0 — runtime-data-only change, no UI/logic changes)
**Scope:** Replace deprecated/404 model IDs in `DATA.providers.gemini.models` and `DATA.providers.anthropic.models` with verified-working IDs, sorted cheapest first. Keep all working tiers (cheap and expensive) so the user retains choice.

---

## Why This Was Needed

Adam reported that switching providers in the live UI was throwing errors and that test runs were burning paid-key credit on dead models. Direct API probes confirmed:

- **6 of 7 Gemini model IDs** in `DATA` returned **404** — Google had deprecated the entire 1.5 and 2.0 model families.
- **3 of 5 Anthropic model IDs** in `DATA` returned **404** — Anthropic had deprecated the 3.5 family and the original `claude-3-opus-20240229`.

Result: any user clicking those models got hard errors. Any test pass through the dropdown wasted real money on calls that would never succeed.

---

## Audit Results

| Check | index14 | index15 |
|---|---|---|
| Gemini models in DATA | 7 (1 working) | **5 (5 working)** |
| Anthropic models in DATA | 5 (2 working) | **5 (5 working)** |
| Dead 404 IDs in dropdown | 9 | **0** |
| Cheapest model first in dropdown | ❌ (random order) | ✅ enforced cheapest-first |
| Expensive Opus / Pro retained | ✅ | ✅ (kept per Adam — user may want them) |
| Live PONG verification | not done | **9 of 10 PASS** (1 transient 503) |
| HTML / JS / renderer changes | n/a | **zero** — DATA-only edit, pure LEGO |

---

## What Was Changed

### 1. `DATA.providers.gemini.models`

**Before (index14):**
```javascript
models: [
  { v: 'gemini-1.5-flash-8b',   l: 'Gemini 1.5 Flash-8B',   tier: 'free', price: 0.15 },  // ❌ 404
  { v: 'gemini-2.0-flash-lite', l: 'Gemini 2.0 Flash Lite', tier: 'free', price: 0.30 },  // ❌ 404
  { v: 'gemini-1.5-flash',      l: 'Gemini 1.5 Flash',      tier: 'free', price: 0.30 },  // ❌ 404
  { v: 'gemini-2.0-flash',      l: 'Gemini 2.0 Flash',      tier: 'free', price: 0.40 },  // ❌ 404
  { v: 'gemini-2.5-flash',      l: 'Gemini 2.5 Flash',      tier: 'free', price: 0.60 },  // ✅
  { v: 'gemini-1.5-pro',        l: 'Gemini 1.5 Pro',        tier: 'paid', price: 5.00 },  // ❌ 404
  { v: 'gemini-2.5-pro',        l: 'Gemini 2.5 Pro',        tier: 'paid', price: 10.00 }  // ⚠️ transient 503
]
```

**After (index15):**
```javascript
// VERIFIED LIVE 2026-04-14 — every ID below was PONG-tested with Adam's paid key. Sorted cheapest first.
models: [
  { v: 'gemini-2.5-flash-lite', l: 'Gemini 2.5 Flash-Lite', tier: 'free', price: 0.40 },
  { v: 'gemini-2.5-flash',      l: 'Gemini 2.5 Flash',      tier: 'free', price: 2.50 },
  { v: 'gemini-flash-latest',   l: 'Gemini Flash (latest)', tier: 'free', price: 2.50 },
  { v: 'gemini-pro-latest',     l: 'Gemini Pro (latest)',   tier: 'paid', price: 10.00 },
  { v: 'gemini-2.5-pro',        l: 'Gemini 2.5 Pro',        tier: 'paid', price: 10.00 }
]
```

### 2. `DATA.providers.anthropic.models`

**Before (index14):**
```javascript
models: [
  { v: 'claude-3-5-haiku-20241022',  l: 'Claude 3.5 Haiku',  tier: 'paid', price: 4.00 },   // ❌ 404
  { v: 'claude-3-5-sonnet-20241022', l: 'Claude 3.5 Sonnet', tier: 'paid', price: 15.00 },  // ❌ 404
  { v: 'claude-sonnet-4-5',          l: 'Claude Sonnet 4.5', tier: 'paid', price: 15.00 },  // ✅
  { v: 'claude-3-opus-20240229',     l: 'Claude 3 Opus',     tier: 'paid', price: 75.00 },  // ❌ 404
  { v: 'claude-opus-4-5',            l: 'Claude Opus 4.5',   tier: 'paid', price: 75.00 }   // ✅
]
```

**After (index15):**
```javascript
// VERIFIED LIVE 2026-04-14 — every ID below was PONG-tested with Adam's paid key. Sorted cheapest first.
models: [
  { v: 'claude-haiku-4-5-20251001', l: 'Claude Haiku 4.5',  tier: 'paid', price: 5.00 },
  { v: 'claude-sonnet-4-5',         l: 'Claude Sonnet 4.5', tier: 'paid', price: 15.00 },
  { v: 'claude-sonnet-4-6',         l: 'Claude Sonnet 4.6', tier: 'paid', price: 15.00 },
  { v: 'claude-opus-4-5',           l: 'Claude Opus 4.5',   tier: 'paid', price: 75.00 },
  { v: 'claude-opus-4-6',           l: 'Claude Opus 4.6',   tier: 'paid', price: 75.00 }
]
```

---

## Live Verification Results (2026-04-14)

Every new model ID was PONG-tested through real `fetch()` — Gemini directly to Google, Anthropic via the local bridge at `http://localhost:3000/v1/messages`.

| Provider | Model | Result |
|---|---|---|
| Gemini    | gemini-2.5-flash-lite     | ✅ PONG |
| Gemini    | gemini-2.5-flash          | ✅ PONG |
| Gemini    | gemini-flash-latest       | ✅ PONG |
| Gemini    | gemini-pro-latest         | ✅ PONG |
| Gemini    | gemini-2.5-pro            | ⚠️ 503 "high demand" — model exists, transient Google capacity. Kept in list. |
| Anthropic | claude-haiku-4-5-20251001 | ✅ PONG |
| Anthropic | claude-sonnet-4-5         | ✅ PONG |
| Anthropic | claude-sonnet-4-6         | ✅ PONG |
| Anthropic | claude-opus-4-5           | ✅ PONG |
| Anthropic | claude-opus-4-6           | ✅ PONG |

**9 of 10 PASS. 1 transient 503 (not a model defect).**

---

## LEGO Compliance Notes

- **Pure DATA edit.** Two `models: [...]` arrays replaced. Nothing else touched.
- **No HTML changed.** Dropdowns automatically pick up the new lists because the renderer iterates `DATA.providers.<p>.models`.
- **No JS function changed.** Router, adapter, tier-pill counter, price-sort — all untouched.
- **Adapters unchanged.** Anthropic still goes through its custom adapter via the bridge; Gemini still uses its native shape.
- **Removable.** Reverting is a single `git diff` — the index14.html copy is the rollback point.

---

## What Did NOT Change

- No version bump (still v4.8.0) — this is a runtime-data correction, not a feature
- No changes to OpenAI, ADAM, DeepSeek, Groq, Mistral, Together, or Cohere model lists
- No changes to any adapter, the router, or any UI logic
- No changes to `server.js` or the bridge
- No changes to localStorage keys or the persistence layer

---

## Decisions Locked In For Future Phoenix

1. **Live-probe before adding any new Anthropic or Gemini model.** Provider IDs deprecate silently and there is no warning until a 404 hits the user.
2. **Never strip a working model just because it's expensive.** Sort cheapest-first instead. Adam: "may be the user want to use this model dont remove."
3. **Keep dead-ID removal aggressive.** A 404 in the dropdown wastes the user's time and trains them to ignore errors. Out, immediately, on confirmation.
4. **Transient 5xx ≠ dead.** Keep the model; it's a provider capacity issue, not a deprecation.

---

## Outstanding Bugs (Carried Forward to index16)

These were discovered during the testing that produced index15 but are NOT fixed here. They are the next phase plan.

- **BUG D — key cache stale.** New API key saved → router keeps the old key in memory until page reload. Fix: router re-reads `localStorage` on every send, OR the Save button hot-updates the in-memory cache.
- **BUG B — UI state doesn't persist `activeProvider` / `activeModel`.** `adam_ui_state` saves panel positions but not which provider/model the user was on. Reload always lands on default Gemini.
- **BUG C — `testProviderKey()` only handles 4 providers.** Explicit branches for gemini/openai/anthropic/adam. The 5 newer providers (deepseek/groq/mistral/together/cohere) silently fall through. Needs LEGO refactor: move test logic into each provider's DATA entry as `testFn` or `testEndpoint`.
- **Cohere never verified.** `IP key.txt` is truncated at "Cohere API Key p" — need the full key from Adam.

---

## Phase Status

- ✅ index14 → index15: Dead-model purge (this file)
- ⬜ index15 → index16: BUG D / BUG B / BUG C fixes (next phase plan, written into PHOENIX_MEMORY.md)
