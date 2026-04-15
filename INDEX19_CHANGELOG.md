# INDEX19.HTML — CHANGELOG
**Version:** v4.9.0
**Date:** 2026-04-14
**Previous:** index18.html (v4.8.2)
**Commit:** new file on taeiadam-dev/adam-chat main, HTTP 201 CREATED
**Commit message:** `feat(test-key): LEGO refactor testProviderKey, all 9 providers now testable (Bug C) + fix anthropic dead model ID (Bug E) — v4.9.0`

---

## BUGS CLOSED

### Bug C — testProviderKey hardcoded to 4 providers
**Symptom:** In Settings → API Keys, pressing Save with keys filled in showed "🔄 Testing..." forever for 5 of 9 providers. Only gemini, openai, anthropic, and adam ever updated to 🟢/🔴. DeepSeek, Groq, Mistral, Together AI, Cohere had no visible test feedback.

**Root cause:** `testProviderKey(provider)` was a 4-branch `if/else if` that only knew how to build URLs, headers, and body payloads for the first four providers. The 5 newer providers hit no branch and fell out the function silently — the spinner stayed on the pill forever. Classic LEGO violation: adding a provider required editing the function instead of adding a DATA entry.

**Fix:** Replaced the hardcoded function body with a 30-line generic dispatcher. Added a new `.test` block to each of the 9 provider entries in `DATA.providers`, matching the existing `DATA.providers[k].ping` + `DATA.providerAdapters` dispatch pattern already used elsewhere in the file.

### Bug E — anthropic probe uses deprecated Haiku-3 model
**Symptom:** After the Bug C refactor, live test showed anthropic returning "🔴 Error 404 — check key" with a valid key, even though the bridge was up and the key was good.

**Root cause:** Bridge proxy is working fine. Anthropic cloud returns `HTTP 404 not_found_error: model: claude-3-haiku-20240307` because they deprecated the Haiku-3 family. The old testProviderKey had hardcoded this model in its probe body, so the bug has existed since the key-test feature was added — it only surfaced now because the pill used to silently stay on "🔄 Testing..." forever (Bug C masked it).

**Fix:** One-line DATA edit inside `providers.anthropic.test.body` → `claude-haiku-4-5-20251001` (cheapest live Haiku in Adam's catalog, matches the models list).

---

## FILES TOUCHED

**1 file edited** (plus 1 file copied per RULE 4):
- `index18.html` — untouched (rollback baseline)
- `index19.html` — new file, copied from index18.html then edited

---

## CHANGES INSIDE index19.html

### DATA layer additions (9 new sub-entries, 1 edit)
Added `.test` block to each of the 9 `DATA.providers[k]` entries:
- `gemini.test` — `GET /v1beta/models?key=...`, label "Invalid key"
- `openai.test` — `GET /v1/models` with Bearer, label "Invalid key"
- `anthropic.test` — `POST /v1/messages` with x-api-key + anthropic-version headers, body uses `claude-haiku-4-5-20251001`, catch message "CORS blocks browser test (normal, will work on send)"
- `adam.test` — `GET /health`, `requireKey: false`, `timeoutMs: 2000`, labels "ADAM Server online ✓" / "Server not responding" / "Server offline"
- `deepseek.test` — `GET /v1/models` with Bearer
- `groq.test` — `GET /v1/models` with Bearer (base has `/openai/v1`)
- `mistral.test` — `GET /v1/models` with Bearer
- `together.test` — `GET /v1/models` with Bearer
- `cohere.test` — `GET /v1/models` with Bearer

`.test` schema fields: `url(key, ip)`, `method` (default GET), `headers(key)`, `body(key)` (POST only), `labels {ok, bad, noKey, caught}` (each can be string or `(arg) => string`), `timeoutMs` (optional AbortController), `requireKey` (defaults to `!!p.hasApiKey`), `isOk(response)` (optional override of `r.ok`).

### JS layer — one function body replaced
**Removed:** 47-line `testProviderKey(provider)` with 4-branch `if/else if` (gemini/openai/anthropic/adam) that silently returned for the other 5.

**Added:** 30-line generic dispatcher. Reads `DATA.providers[provider].test` config. Handles no-key path, timeout, POST body, label rendering (string or function), and catch branch uniformly. Adding provider N+1 now = one `.test` entry, zero edits here.

### UI layer
**One change:** version badge `v4.8.2 Active` → `v4.9.0 Active` at line 780.

No HTML structure changes. No new attributes. No new buttons.

---

## LEGO QUALITY GATE

| Question | Answer |
|---|---|
| Is it defined in DATA? | ✅ Yes — `DATA.providers[k].test` |
| Does adding a provider's test require touching HTML? | ✅ No |
| Does adding a provider's test require touching JS functions? | ✅ No — one `.test` block, no dispatcher edits |
| Does its state save/restore automatically? | N/A (test is transient, no state) |
| Does it reference any hardcoded path or URL? | ✅ No — urls live in `cfg.url(key, ip)` |
| Can it be removed without breaking anything else? | ✅ Yes — delete the 9 `.test` blocks + restore old testProviderKey |

All 6 gates pass. Refactor is LEGO-compliant.

---

## LIVE TEST RESULTS (localhost:3000/index19.html)

**Positive run (all 9 real keys from IP key.txt):**
```
gemini     🟢 Key valid ✓
openai     🟢 Key valid ✓
anthropic  🟢 Key valid ✓      ← was 🔴 Error 404 before Bug E fix
adam       🟢 ADAM Server online ✓
deepseek   🟢 Key valid ✓       ← was silent in index18
groq       🟢 Key valid ✓       ← was silent in index18
mistral    🟢 Key valid ✓       ← was silent in index18
together   🟢 Key valid ✓       ← was silent in index18
cohere     🟢 Key valid ✓       ← was silent in index18
```
9/9 PASS.

**Negative run (bad keys injected for openai + mistral, other 7 still good):**
```
openai  (bad key) → 🔴 Invalid key              ← old label shape preserved
mistral (bad key) → 🔴 Error 401 — check key   ← new label shape
```
Both label shapes (static string vs. `(status) => string`) dispatch correctly.

**Bridge diagnosis (for the Bug E trail of evidence):**
- `POST http://localhost:3000/v1/messages` with dummy key → `HTTP 401` (bridge auth rejected, correct behavior).
- `POST http://localhost:3000/v1/messages` with REAL key + old `claude-3-haiku-20240307` body → `HTTP 404 not_found_error: model: claude-3-haiku-20240307` (Anthropic cloud deprecated).
- `POST http://localhost:3000/v1/messages` with REAL key + new `claude-haiku-4-5-20251001` body → `HTTP 200` (the fix).

---

## DEPLOY

Same pipeline as index17/index18 pushes:
1. `fetch('http://localhost:3000/index19.html')` → Blob
2. FileReader → base64
3. `PUT https://api.github.com/repos/taeiadam-dev/adam-chat/contents/index19.html` with `{ message, content, branch: 'main' }`

Response: `HTTP 201 CREATED`. New file at `github.com/taeiadam-dev/adam-chat/blob/main/index19.html`. GitHub Pages rebuild queued automatically.

---

## ROLLBACK PATH

If index19.html regresses on live:
1. Access `https://taeiadam-dev.github.io/adam-chat/index18.html` directly (already deployed, unchanged).
2. Or: in `adam-chat` repo, delete `index19.html` via GitHub UI. Pages rebuild removes it.

Local rollback: `index18.html` is untouched on disk. Phoenix next session can branch off it if `.test` schema needs redesign.

---

## CARRY-FORWARD

- **Open bugs:** none in the testProviderKey space.
- **Schema extensibility:** if a provider needs post-test side effects (e.g. caching, telemetry), add a `sideEffect(key, ip, response)` hook to the `.test` schema at that point — the dispatcher accepts it trivially.
- **Provider N+10:** add `DATA.providers[newKey] = { ..., test: { ... } }`. Zero edits to dispatcher.
- **MASTER_PLAN pending:** Phase 2 (n8n Anthropic proxy), Phase 3 (n8n Cohere proxy), Phase 4 (GitHub Actions test suite).
