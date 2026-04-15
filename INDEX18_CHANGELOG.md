# INDEX18 CHANGELOG
## Persist activeProvider + activeModel across reload — reload now restores the exact provider and model the user picked

**Base file:** index17.html → index18.html
**Date:** 2026-04-14
**Version bump:** v4.8.1 → **v4.8.2** (state-persistence fix, no UI surface change)
**Scope:** Two existing functions extended + one new helper. No HTML structure change beyond a single `onchange` attribute.
**Deploy target:** GitHub Pages — https://taeiadam-dev.github.io/adam-chat/
**Commit:** `0fdbc4af30a4302b41afe0d66c194a4af254f5f3` on `taeiadam-dev/adam-chat` `main`

| Phase | Bug | Status |
|---|---|---|
| B | `activeProvider` persisted but `activeModel` was NOT — and the provider restore path forced the assistant's hardcoded default model, overriding the user's choice. Reload always snapped the model back. | ✅ SHIPPED to GitHub Pages |
| C | `testProviderKey()` only has explicit branches for gemini/openai/anthropic/adam — the 5 newer providers silently do nothing. | ⬜ pending (carried over) |

---

## Phase B — activeProvider + activeModel persistence (SHIPPED)

### Symptom (continuation of Adam's bug report from index17 session)
> "`adam_ui_state` does not persist `activeProvider` / `activeModel` — reload always lands on default Gemini."

Reproducible: open `https://taeiadam-dev.github.io/adam-chat/`, pick Groq + `llama-3.3-70b-versatile`, send a message, verify routing. Refresh the page. Dropdowns snap back to Gemini + `gemini-2.5-flash-lite`. Every reload wipes the user's choice.

### Root cause — two gaps in the persistence layer

1. **Model had NO persistence hook at all.** The `<select id="chat-cfg-model">` element had no `onchange` handler, there was no `onModelChange()` function anywhere in the codebase, and no `adam_default_model` localStorage key existed. The model dropdown was effectively write-only.

2. **Provider restore was HALF-correct.** `onProviderChange()` already wrote `adam_default_provider` to localStorage (line 3695 in index17), and `renderConfigBar()` already read it back (line 3643). But when `renderConfigBar()` finished picking the provider it called `onProviderChange(a.model)` — forcing the model list to select the **assistant's hardcoded default** (e.g. `DATA.assistants.adam.model`), not whatever the user picked last.

So even if the user picked Groq + 70B, reload would restore provider=Groq (via the existing path) but hard-reset the model back to Groq's first option or the assistant's default. Provider name stayed visible; user's actual model choice was lost.

### Fix — 6 surgical edits, one new helper

Pattern: follow the existing `adam_default_provider` convention (direct localStorage key, not inside `adam_ui_state`). Add a matching `adam_default_model` key. Wire a tiny `onModelChange()` handler. Guard the restore against cross-provider id leaks.

**Edit 1 — line 780:** version badge `v4.8.0 Active` → `v4.8.2 Active`.

**Edit 2 — line 817:** attach the missing onchange handler:
```html
<select class="chat-select" id="chat-cfg-model" onchange="adamChat.onModelChange()">
```

**Edit 3 — new function + tail-call from `onProviderChange()` (line ~3697):**
```javascript
// ...existing onProviderChange() body...
localStorage.setItem('adam_default_provider', provKey);
// ── Phoenix Bug B fix (v4.8.2) ─────────────────────────────────────────
// After repopulating the model list, persist whichever model is now
// selected (forced value OR the dropdown's first-option fallback).
onModelChange();
pingAPI(false);
}

// ── Phoenix Bug B fix (v4.8.2) ───────────────────────────────────────────
// Persist the user's model choice so reload restores it. Wired from
// <select id="chat-cfg-model" onchange="adamChat.onModelChange()"> and
// also called at the tail of onProviderChange() to capture auto-selected
// first-option fallbacks after provider switches.
function onModelChange() {
  const mSel = el('chat-cfg-model');
  if (mSel && mSel.value) {
    localStorage.setItem('adam_default_model', mSel.value);
  }
}
```

**Edit 4 — `renderConfigBar()` restore path (line 3657):** prefer the saved model ONLY if it exists in the current provider's catalog, otherwise fall back to the assistant default. This guards against cross-provider leak (e.g. saved Groq id restored into an Anthropic provider that doesn't offer it).
```javascript
const savedModel = localStorage.getItem('adam_default_model');
const provObj = DATA.providers[pSel.value];
const modelIsValidForProvider = provObj && Array.isArray(provObj.models)
  && provObj.models.some(m => m.v === savedModel);
const restoreModel = modelIsValidForProvider ? savedModel : a.model;
onProviderChange(restoreModel);
```

**Edit 5 — public API export (line 4747):** add `onModelChange` alongside `onProviderChange` so inline HTML handlers can reach it.

**Edit 6 — parse check:** `new Function(embeddedScript)` passes. 258,653 chars of JS parses cleanly.

### Why tail-call `onModelChange()` at the end of `onProviderChange()`?
Two user paths need persistence, both must save:

- Path A: user picks a model from the dropdown → native `onchange` fires `adamChat.onModelChange()` → saved ✅
- Path B: user picks a different provider → model list rebuilds → first option auto-selected by the browser → without a tail-call, nothing saves until the user also manually clicks the model dropdown. With the tail-call, the auto-selected first-option IS the saved default immediately.

One helper covers both paths. LEGO-consistent.

### LEGO compliance
- **DATA untouched.** Zero new config entries.
- **HTML structure untouched** except a single `onchange` attribute on an existing `<select>`.
- **Two existing JS functions extended** (`onProviderChange`, `renderConfigBar`) and **one tiny new helper** (`onModelChange`, 5 lines of body). Acceptable — this is a state-layer fix, not a feature add.
- **Removable.** Delete `onModelChange`, the onchange attribute, the tail-call, and the renderConfigBar guard block → old behavior restored.
- **Follows existing persistence pattern** (`adam_default_provider`) rather than inventing a new one. New key `adam_default_model` is a drop-in sibling.

### Deploy path (same pipeline as Phase E)
Browser fetches `http://localhost:3000/index18.html` → FileReader base64 → GitHub Contents API GET (for prev SHA) → PUT with new base64 + commit message. Single `javascript_tool` call. 307,192 text bytes → 418,368 base64 bytes pushed in one round-trip. Previous blob SHA `5ce887d0c0` → new blob SHA `3b721ba70e`.

### Live verification

**Local stage (http://localhost:3000/index18.html) — 6 tests:**

| # | Test | Result |
|---|---|---|
| 1 | Set Groq + `llama-3.3-70b-versatile`, reload, verify restore + model list is Groq-only | PASS ✅ |
| 2 | Send real message on restored state, fetch-spy confirms only `api.groq.com` hit, reply identified as Meta Llama | PASS ✅ |
| 3 | Set Gemini + `gemini-2.5-pro` (non-default), reload, verify restore | PASS ✅ |
| 4 | Force invalid state (Groq model id saved under Gemini provider), reload, guard must fall back + overwrite stale value with valid Gemini model | PASS ✅ — fell back to `gemini-2.5-flash-lite`, stored value updated |
| 5 | Set Mistral + `codestral-latest` (2nd option), reload, verify restore | PASS ✅ |
| 6 | Set DeepSeek + `deepseek-reasoner` (last option), reload, verify restore + list is DeepSeek-only | PASS ✅ |

**Live stage (https://taeiadam-dev.github.io/adam-chat/ AFTER Pages rebuilt) — 4 tests:**

| # | Provider / Model | Post-reload state | Verdict |
|---|---|---|---|
| 1 | **Groq** / `llama-3.3-70b-versatile` | provider + model restored, list is Groq-only | PASS ✅ |
| 2 | **Gemini** / `gemini-2.5-pro` | provider + model restored, list is Gemini-only | PASS ✅ |
| 3 | **DeepSeek** / `deepseek-reasoner` | provider + model restored, list is DeepSeek-only | PASS ✅ |
| 4 | **Cohere** / `command-a-03-2025` | provider + model restored, list is Cohere-only | PASS ✅ |

Live fetch also confirmed the raw index.html on Pages contains `v4.8.2 Active`, the `onchange="adamChat.onModelChange()"` attribute, the `adam_default_model` localStorage key references, and the function definition.

### Post-test cleanup
Reset the test browser's `adam_default_provider` + `adam_default_model` back to Gemini / `gemini-2.5-flash-lite` so next page visit lands on a friendly baseline (free tier, fast model, no mixed-content dependency).

### What this did NOT fix
- **BUG C still open.** `testProviderKey()` only handles 4 of 9 providers. The 5 newer providers' Test Key buttons still silently do nothing. Fix scheduled for index19.html as a LEGO refactor — move per-provider test config into `DATA.providers[k].test` so the test dispatcher becomes generic.
- **Mixed-content on Anthropic / ADAM from GitHub Pages.** Still required until MASTER_PLAN phase 2 (n8n proxy) lands.
- **`state.activeProvider` / `state.activeModel` on the state object itself.** The fix uses direct localStorage keys (following the existing `adam_default_provider` pattern) rather than adding two new fields to the `state` object. Keeps the `PERSIST_KEYS` allowlist untouched. If a later phase needs these values on `state` for non-persistence reasons, they can be added then without breaking this fix.

---

## Phase C — testProviderKey LEGO refactor (pending)

Plan unchanged. Target: index19.html. Move per-provider test config (`url`, `headers`, `method`, `payload`, `successCheck`) into `DATA.providers[k].test` so the test dispatcher is data-driven. Matches the `DATA.providerAdapters` pattern.

---

## Decision log (this session)

| Decision | Reason |
|---|---|
| Store model as top-level localStorage key `adam_default_model`, NOT inside `adam_ui_state`. | Follows the existing `adam_default_provider` convention for the same-tier setting. Keeps `PERSIST_KEYS` / `saveState()` scope unchanged. Two siblings are clearer than one sibling + one nested field. |
| Tail-call `onModelChange()` from inside `onProviderChange()`. | Captures the auto-selected first-option after a provider switch without requiring the user to touch the model dropdown. Removes a whole class of "why didn't it save" bug reports. |
| Guard `renderConfigBar` restore against cross-provider id leak. | Prevents a forced-selection crash if the user saved a Groq-only id then later switched to an Anthropic-only assistant. Silently falls back to the assistant default and overwrites storage with the valid value on next save. |
| Push as `index.html` on `main`, no PR. | Same rationale as Phase E: single-function state-layer fix with live verification in the same session. A PR gate adds nothing here. |
| Reuse the Phase E deploy pipeline (browser fetch from localhost → base64 → PUT) unchanged. | Proven in the index17 session. One javascript_tool call pushes 307KB. No chunking, no curl, no staging. |
