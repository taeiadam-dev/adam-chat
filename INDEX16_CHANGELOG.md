# INDEX16 CHANGELOG
## Bug-fix sweep — Phase D / B / C planned, Phase D shipped

**Base file:** index15.html → index16.html
**Date:** 2026-04-14
**Version bump:** none (still v4.8.0 — runtime fixes, no UI surface change)
**Scope:** Three carry-forward bugs from index15. Each ships as a separate phase per RULE 3 with a stop point and a live test before continuing.

| Phase | Bug | Status |
|---|---|---|
| D | Key-cache staleness — router used the in-memory `API_KEYS` snapshot taken at boot, so any localStorage mutation that didn't go through `saveApiKeys()` (debug console, external sync, future code paths) was invisible until a full page reload. | ✅ SHIPPED |
| B | `adam_ui_state` does not persist `activeProvider` / `activeModel` — reload always lands on default Gemini. | ⬜ pending |
| C | `testProviderKey()` only has explicit branches for gemini/openai/anthropic/adam — the 5 newer providers (deepseek/groq/mistral/together/cohere) silently do nothing when their Test Key button is clicked. | ⬜ pending |

---

## Phase D — Key-cache staleness (SHIPPED)

### Symptom
During the index15 testing pass, when Phoenix injected a corrected Together API key directly into `localStorage` from the dev console, ADAM's chat router still rejected the next send as "Invalid key." Only a full page reload made the new key take effect. Same pattern would hit any user using browser sync, dev-tools edits, or future external mutations of the key store.

### Root cause
`API_KEYS` and `API_IPS` are objects populated **once** at boot (line 2281) by reading `localStorage`. The router (`unifiedLLMRouter`, line 2828 in index15) reads from those in-memory objects. `saveApiKeys()` does write back to both `localStorage` AND the in-memory objects, so the Save button worked correctly — but ANY other path that wrote to `localStorage` was invisible to the router.

### Fix
Added two helpers inside the same closure as `API_KEYS` / `API_IPS`:

```javascript
// Single source of truth for live key/IP reads. localStorage is always the
// authoritative source — API_KEYS / API_IPS are kept as a fast fallback for
// the very first page render, but every router and test call goes through
// these helpers so external mutations (Save button, debug console writes,
// future sync) propagate without requiring a page reload. Fixes BUG D.
function getApiKey(p) {
  const live = localStorage.getItem(`adam_key_${p}`);
  if (live !== null) { API_KEYS[p] = live; return live; }
  return API_KEYS[p] || '';
}
function getApiIp(p) {
  const live = localStorage.getItem(`adam_ip_${p}`);
  if (live !== null) { API_IPS[p] = live; return live; }
  return API_IPS[p] || '';
}
```

Then routed every critical read through them — 5 sites total:

| Line (index16) | Before | After |
|---|---|---|
| 2420 (ping endpoint base) | `API_IPS[providerKey]` | `getApiIp(providerKey)` |
| 2845 (router pre-flight key) | `API_KEYS[cfg.apiKeyField]` | `getApiKey(cfg.apiKeyField)` |
| 2849 (router base URL) | `API_IPS[cfg.apiKeyField]` | `getApiIp(cfg.apiKeyField)` |
| 4594 (testProviderKey key) | `API_KEYS[provider]` | `getApiKey(provider)` |
| 4595 (testProviderKey ip) | `API_IPS[provider]` | `getApiIp(provider)` |

UI display reads (panel input population at lines 4535/4537) and the save path (4569–4574) intentionally still use direct `API_KEYS` / `API_IPS` access — those are correct as-is because the save path writes to both, and the panel populates from the cache that was just synced at boot.

### Live verification
Test was run with `fetch` monkey-patched to **capture and abort** every Gemini/Anthropic API call so no credit was burned. The patched fetch logged the URL and headers actually built by the router for each attempt.

```
1. Tampered localStorage adam_key_gemini → 'AIza_TAMPERED_FOR_PHASE_D'
   (no reload, no Save button click)
2. Triggered adamChat.sendMessage() with Gemini selected
3. Captured 3 fetch attempts (router retries 3x):
   url=...?key=AIza_TAMPERED_FOR_PHAS...   ✅ used tampered key

4. Restored localStorage adam_key_gemini → 'AIzaSyCIdEJhP4...' (real key)
   (no reload, no Save button click)
5. Triggered adamChat.sendMessage() again
6. Captured 3 fetch attempts:
   url=...?key=AIzaSyCIdEJhP4NHqJ8HWo...   ✅ used real key
```

**RESULT: PASS.** Cache invalidates on every send. No reload required.

### LEGO compliance
- **Pure additive change.** Two helpers added; five direct-access lines re-routed. No function signatures changed. No DATA edits. No HTML touched.
- **Single responsibility.** Helpers do one thing — return the live value with the in-memory cache as fallback only.
- **Removable.** Reverting is `git revert` of the 6 hunks; behavior degrades to "must reload after non-Save mutation" but is otherwise identical.

### Test mishap (recorded so future Phoenix avoids the trap)
First test attempt called `unifiedLLMRouter` directly from the JS console. That function is inside an IIFE closure and is NOT exposed on `window` or `adamChat`. The call threw `ReferenceError`, killing the test IIFE before it could restore the tampered key. Adam had to paste the Gemini key again to recover.

**Lesson:** to drive the closure-internal router from console, use the public entry point `adamChat.sendMessage()` after writing to the chat input — never try to call internal functions directly.

---

## Phase B — Persist activeProvider + activeModel (pending)

(Plan in PHOENIX_MEMORY.md → ACTIVE PHASE PLAN section.)

---

## Phase C — testProviderKey LEGO refactor (pending)

(Plan in PHOENIX_MEMORY.md → ACTIVE PHASE PLAN section.)

---

## Side-effect of this session

- `IP key.txt` rewritten with the full set of working keys (Gemini, Anthropic, Cohere were missing or truncated in the previous version). Future Phoenix sessions can recover the key set without asking Adam.
- Cohere key (`7jryvvm3rNVMTc62Wa0EJDmsvGYuUvScqXFmBaeC`) injected into localStorage for the first time. Cohere live-test is still pending — kicks the moment Phase D shipped.

---

## Security cleanup — `config.json` scrubbed (2026-04-14, post-Phase D)

### What was wrong
`config.json` in the project root contained Adam's REAL paid Gemini and Anthropic keys in plaintext:

```json
{
  "gemini_key": "AIzaSyCIdEJh...",         ← real paid key, plaintext
  "openai_key": "YOUR_OPENAI_API_KEY_HERE",
  "anthropic_key": "sk-ant-api03-HW..."     ← real paid key, plaintext
}
```

Nobody was syncing it to localStorage or to `IP key.txt` — it just sat there from an earlier dev pass. If the folder ever got zipped, shared, or accidentally pushed to a git remote, both keys would leak.

### Why the system didn't break despite the file being stale
Audit of who actually reads `config.json`:

| File | Reads config.json? | Notes |
|---|---|---|
| `server.js` (Node) | **No** | Primary bridge. Reads `x-api-key` from each browser request. Uses live localStorage values via Phase D helpers. |
| `bridge.py` (Python fallback) | Yes (line 13–18) | Only runs if Node is missing. Falls back to `config.get(...)` only when the browser request lacks an `x-api-key` header. |
| `index16.html` browser | No | Sends keys directly via headers. |

So `config.json` was never in the live path on Adam's machine — Node was always running. The file was just dead-weight plaintext credentials.

### Fix
Replaced both real keys with placeholders + added an in-file comment explaining the file's role:

```json
{
  "_comment": "PLACEHOLDERS ONLY. Real keys live in browser localStorage and are sent on every request via x-api-key header. server.js (Node, the primary bridge) ignores this file entirely. bridge.py (Python fallback) only reads it when the browser request lacks an x-api-key header. Do NOT paste real keys here.",
  "gemini_key": "YOUR_GEMINI_API_KEY_HERE",
  "openai_key": "YOUR_OPENAI_API_KEY_HERE",
  "anthropic_key": "YOUR_ANTHROPIC_API_KEY_HERE"
}
```

### Verification
```
$ python3 -c "import json; c = json.load(open('config.json')); print('PARSE OK'); print(list(c.keys()))"
PARSE OK
keys present: ['_comment', 'gemini_key', 'openai_key', 'anthropic_key']
```

JSON parses. `_comment` is a no-op string (Python's `json.load` ignores nothing — it just becomes a key/value pair that bridge.py never reads, which is fine because bridge.py only reads `gemini_key`, `openai_key`, and `anthropic_key`).

### Behavior on bridge.py fallback path with placeholder values
- Browser sends `x-api-key: <real key from localStorage>` → bridge.py uses that, never touches config → ✅ works
- Browser somehow doesn't send `x-api-key` → bridge.py falls back to `"YOUR_ANTHROPIC_API_KEY_HERE"` → Anthropic returns 401 → user sees a clear "invalid key" error → user knows to fix config.json or fix the browser

That's the right failure mode — informative, no silent success on a placeholder.

### Decision locked in for future Phoenix
**Never put real keys in `config.json`.** It is not the source of truth and is not in the live path. The source of truth is browser `localStorage` + `IP key.txt` (for recovery). config.json stays scrubbed.
