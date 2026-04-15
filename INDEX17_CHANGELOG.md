# INDEX17 CHANGELOG
## Echo Cache provider-scoping — provider dropdown now actually switches providers on GitHub Pages

**Base file:** index16.html → index17.html
**Date:** 2026-04-14
**Version bump:** v4.8.0 → **v4.8.1** (runtime fix, no UI surface change)
**Scope:** One-function edit. Cache key in `sendMessage()` is now scoped by `provider::model::prompt`.
**Deploy target:** GitHub Pages — https://taeiadam-dev.github.io/adam-chat/
**Commit:** `8227470ccc664f5d8ed5dd8874a3009f72086da0` on `taeiadam-dev/adam-chat` `main`

| Phase | Bug | Status |
|---|---|---|
| E | Echo Cache cross-provider replay — switching the provider dropdown and re-sending the same prompt returned the PREVIOUS provider's cached reply. Looked exactly like "the provider dropdown does nothing." | ✅ SHIPPED to GitHub Pages |
| B | `adam_ui_state` does not persist `activeProvider` / `activeModel` — reload always lands on default Gemini. | ⬜ pending (carried over from index16) |
| C | `testProviderKey()` only has explicit branches for gemini/openai/anthropic/adam — the 5 newer providers silently do nothing. | ⬜ pending (carried over from index16) |

---

## Phase E — Echo Cache provider-scoping (SHIPPED)

### Symptom (Adam's report, 2026-04-14)
> "The live page on GitHub Pages does not switch providers. I select Groq or Google, but the AI still responds as Anthropic."

Reproducible: open `https://taeiadam-dev.github.io/adam-chat/`, pick Anthropic, send "hi", get Claude's reply. Switch to Groq or Gemini, send "hi" again, get the SAME Claude-flavored reply with no network call to Groq/Gemini. Every subsequent "hi" on any provider replays the first cached answer.

### Root cause (NOT the provider router)
Diagnosed on the live page with a fetch interceptor. The provider router, the model dropdown, and the adapter dispatch are all correct. Provider switch → `onProviderChange()` rebuilds model dropdown → `sendMessage()` → `unifiedLLMRouter()` → `DATA.providerAdapters[providerKey]` → POST to the right host.

The real culprit is the Semantic Echo Cache at line 3805 of `sendMessage()`:

```javascript
// index16.html — cache keyed by prompt text ALONE
const cleanText = text.toLowerCase();
if (state.cache[cleanText] && !state.schismActive && ...) {
    appendMessage('user', text, []);
    appendMessage('assistant', state.cache[cleanText], []);   // ← replays stale reply
    showToast("🦇 Echo Cache hit!");
    return;                                                    // ← never calls the router
}
```

Consequence: once ANY provider has answered a given prompt, every other provider returns that same answer for the same prompt — without ever touching the network. The provider dropdown appears dead.

### Fix
Scope the cache key by the currently-selected provider and model. Every (provider, model) pair now owns its own cache bucket.

```javascript
// index17.html — cache keyed by provider + model + prompt (v4.8.1)
// LEGO fix: switching providers never replays a stale answer from a different
// provider. Without this, picking Groq/Gemini after Anthropic would hit the
// cache and replay the Anthropic response without ever calling the new provider.
const _cacheProv  = el('chat-cfg-provider')?.value || '';
const _cacheModel = el('chat-cfg-model')?.value || '';
const cleanText = `${_cacheProv}::${_cacheModel}::${text.toLowerCase()}`;
if (state.cache[cleanText] && !state.schismActive && ...) {
    ...
}
```

The cache save at line 3955 (`state.cache[cleanText] = responseText;`) now uses the same scoped key automatically — no second edit needed.

### LEGO compliance
- **One function touched.** Only `sendMessage()`.
- **No DATA edits, no HTML edits, no new CSS, no new renderer.**
- **Pure additive logic.** Two local const reads + a template-literal concatenation. Everything else in `sendMessage()` is byte-identical to index16.
- **Removable.** Reverting the 6-line hunk restores old behavior cleanly.

### Deploy path (new pattern — documented for future Phoenix)
The sandbox cannot reach github.com, so the GitHub Contents API PUT has to go through the browser. Historically that meant chunking the 311KB file across many javascript_tool calls. Not needed anymore:

1. Write `index17.html` into the mounted build-bridge folder — this IS Adam's local disk.
2. Adam's local `server.js` on `http://localhost:3000` already serves the entire `live-browser-tester/` directory. The new file is live at `http://localhost:3000/index17.html` the instant the Write finishes.
3. From the Chrome tab on `https://taeiadam-dev.github.io`, `fetch('http://localhost:3000/index17.html')` works (server.js sets permissive CORS). Browser reads the file in one go.
4. `btoa(unescape(encodeURIComponent(src)))` → base64 in one browser call.
5. PUT to `https://api.github.com/repos/taeiadam-dev/adam-chat/contents/index.html` with the base64 body and the previous blob SHA.

One javascript_tool call pushes the whole file. No chunking. No Gist staging. No curl.

### Live verification (on https://taeiadam-dev.github.io/adam-chat/, AFTER Pages rebuilt)

**Test 1 — cache-bleed regression test (the original bug):**
```
1. Clear localStorage, set Groq + Gemini keys, reload.
2. Select Groq → send "hi" → fetch: api.groq.com/openai/v1/chat/completions → Groq reply.
3. Switch to Gemini → send the SAME "hi" → fetch: generativelanguage.googleapis.com → Gemini reply (different text).
```
If the bug were still present, step 3 would make zero network calls and replay Groq's text. It did not. ✅ PASS.

**Test 2 — full 9-provider sweep with a UNIQUE prompt per provider (cache can't mask):**

| Provider | Model | Fetch host | Verdict |
|---|---|---|---|
| gemini | gemini-2.5-flash-lite | generativelanguage.googleapis.com | PASS — replied "BANANA" |
| openai | gpt-4.1-nano | api.openai.com | PASS routing — HTTP 429 quota exceeded on the account (not a routing bug) |
| anthropic | claude-haiku-4-5 | localhost:3000 (Node bridge) | PASS routing — Claude answered as Claude, refused the persona prompt (model behavior, not routing) |
| adam | adam-v1 | 127.0.0.1:3000 | PASS routing — server.js returned "No OpenAI API key" (server config issue, not routing) |
| deepseek | deepseek-chat | api.deepseek.com | PASS — replied "FIG" |
| groq | llama-3.1-8b-instant | api.groq.com | PASS — replied "GRAPE" |
| mistral | mistral-small-latest | api.mistral.ai | PASS — replied "HONEYDEW" |
| together | Llama-3.3-70B-Instruct-Turbo | api.together.xyz | PASS — replied "KIWI" |
| cohere | command-r7b-12-2024 | api.cohere.com | PASS — replied "LEMON" |

**Test 3 — model-level routing inside a single provider:**
- Groq → `llama-3.3-70b-versatile` → `api.groq.com/openai/v1/chat/completions` → replied "MANGO"
- Gemini → `gemini-2.5-flash` → fetch URL path contains `/models/gemini-2.5-flash:generateContent` → replied "NECTARINE"

9/9 providers route to the correct host. Model switching inside a provider also routes correctly (model string is embedded in the URL / payload as expected by each adapter).

### Interpretation for Adam
The three provider tests that returned a non-fruit reply are NOT routing bugs:

- **OpenAI 429** — the OpenAI account is out of quota. Top up at https://platform.openai.com or swap the key.
- **Anthropic "I'm Claude"** — Claude refused the "reply with exactly the word DATE" prompt treating it as a jailbreak. The fact that a Claude-style refusal came back proves the Anthropic bridge worked. A neutral prompt ("say hello in one word") will comply.
- **ADAM local server "No OpenAI API key"** — server.js on 127.0.0.1:3000 is trying to proxy to OpenAI and has no OpenAI key configured in its own env. Server-side config, unrelated to the dropdown.

### What this did NOT fix
- **BUG B still open.** On a fresh reload with no `adam_default_provider` in localStorage, the page still lands on whatever `DATA.assistants[state.asst].provider` says. If a user expects the provider they picked last time to stick, they'll still see the reset. Fix scheduled for index18.html.
- **BUG C still open.** Test Key button is still dead for deepseek/groq/mistral/together/cohere. Fix scheduled for index18.html or index19.html per MASTER_PLAN phase 6.
- **Mixed-content on Anthropic/ADAM from GitHub Pages.** These two providers point at `http://localhost:3000` from an `https://` origin. Works right now because Adam's local bridge is running and Chrome accepts the explicit cross-origin fetch. MASTER_PLAN phase 2 (n8n proxy) replaces these with `https://taeiadam.app.n8n.cloud/webhook/...` and removes the mixed-content dependency entirely.

---

## Phase B — Persist activeProvider + activeModel (pending)

Plan unchanged from INDEX16_CHANGELOG. Target: index18.html.

---

## Phase C — testProviderKey LEGO refactor (pending)

Plan unchanged from INDEX16_CHANGELOG. Target: index18.html or index19.html.

---

## Decision log (this session)

| Decision | Reason |
|---|---|
| Keep the Echo Cache alive, don't gut it. | Adam wants the 0-token repeat-prompt savings. Scoping the key preserves the benefit and removes the bug. |
| Cache key format is `${provider}::${model}::${text.toLowerCase()}` — not a hash. | Human-readable, trivially debuggable in DevTools, and collision risk is irrelevant because the space is per-browser. |
| Push index17.html → as `index.html` on `main`. No feature branch, no PR. | Single-file single-function fix with a live verification in the same session. A PR gate adds nothing here. When BUG B + BUG C land together, those go on a feature branch. |
| Use `fetch('http://localhost:3000/index17.html')` from the Pages tab as the staging bridge for large-file pushes. | Replaces the painful base64-chunk-paste dance described in the SKILL.md. Works because server.js already serves the live-browser-tester folder with open CORS. Documented above for future Phoenix. |
