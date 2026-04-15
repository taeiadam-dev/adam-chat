# INDEX14 CHANGELOG
## Phase 5 — Cohere Provider (Non-OpenAI-Compatible Adapter)

**Base file:** index13.html → index14.html
**Phase:** 5 of 5 — **FINAL PHASE** ✅
**Version bump:** v4.7.0 → **v4.8.0**
**Scope:** Add Cohere as a 9th provider, wiring up its custom v2/chat API shape — which does NOT match the OpenAI-compatible template used by the other 4 paid providers.

---

## Audit Results

| Check | index13 | index14 |
|---|---|---|
| Provider count | 8 | **9** (Cohere added) |
| Providers using OpenAI-compatible shape | 7 | 7 |
| Providers using custom shape | 1 (Anthropic) | **2** (Anthropic, Cohere) |
| Cohere visible in config bar dropdown | ❌ | ✅ auto-appears (config-driven renderer) |
| Cohere API key slot in API Keys panel | ❌ | ✅ auto-appears (config-driven renderer) |
| Cohere logo rendered | ❌ | ✅ gradient circle mark (coral → lavender) |
| Cohere tier pills | ❌ | ✅ `4 paid · min $0.15/1M` |
| Cohere price-sorted dropdown | ❌ | ✅ Command R7B → R → R+ → A |
| UI version label | v4.7.0 | **v4.8.0** |

---

## What's Different About Cohere

Cohere's `/v2/chat` endpoint returns a different response shape from OpenAI-compatible APIs:

**OpenAI-style response** (used by DeepSeek, Groq, Mistral, Together):
```json
{ "choices": [{ "message": { "content": "hello" } }] }
```

**Cohere v2 response:**
```json
{
  "message": {
    "role": "assistant",
    "content": [{ "type": "text", "text": "hello" }]
  },
  "finish_reason": "COMPLETE"
}
```

Also:
- **Endpoint path:** `/v2/chat` (not `/chat/completions`)
- **Auth header:** lowercase `bearer {token}` (Cohere docs specify lowercase)
- **Error shape:** `{ "message": "..." }` at the top level (not `{ "error": { "message": "..." } }`)

---

## What Was Added

### 1. `PROVIDER_DEFAULTS.cohere`

```javascript
cohere: { base: 'https://api.cohere.com' }
```

### 2. `DATA.providers.cohere`

```javascript
cohere: {
  name: 'Cohere', color: '#FF7759', badge: 'cohere',
  logo: `<svg ...gradient coral→lavender circle mark...>`,
  keyPlaceholder: 'Cohere API Key (trial or paid)', hasApiKey: true,
  ping: { type: 'online' },
  models: [
    { v: 'command-r7b-12-2024',    l: 'Command R7B', tier: 'paid', price: 0.15 },
    { v: 'command-r-08-2024',      l: 'Command R',   tier: 'paid', price: 0.60 },
    { v: 'command-r-plus-08-2024', l: 'Command R+',  tier: 'paid', price: 10.00 },
    { v: 'command-a-03-2025',      l: 'Command A',   tier: 'paid', price: 10.00 }
  ]
}
```

Prices are Cohere's published USD-per-1M-output-tokens rates. Cohere offers a trial tier on every API key (20 req/min, limited monthly credits) — so your existing trial key from `IP key.txt` should work immediately without a paid subscription.

### 3. `DATA.providerAdapters.cohere`

The interesting part — the custom adapter:

```javascript
'cohere': {
  label: 'Cohere',
  defaultBase: PROVIDER_DEFAULTS.cohere.base,
  apiKeyField: 'cohere',
  requireKey: true,
  noKeyMessage: `[Cohere] No API key set. Click 🔑 API Keys in the topbar and enter your key.`,
  buildUrl:     (base, _model, _apiKey) => `${base}/v2/chat`,
  buildHeaders: (apiKey) => ({
    'Content-Type':  'application/json',
    'Accept':        'application/json',
    'Authorization': `bearer ${apiKey}`    // ← lowercase, not "Bearer"
  }),
  formatPayload: (chatHistory, systemText, model, rationActive, rationLimit) => ({
    model: model,
    messages: [
      { role: 'system', content: systemText },
      ...chatHistory.map(msg => ({ role: msg.role, content: msg.text }))
    ],
    ...(rationActive ? { max_tokens: rationLimit } : {})
  }),
  parseResponse: (json) => {
    const content = json.message?.content;
    if (Array.isArray(content)) {
      const text = content.filter(c => c && c.type === 'text').map(c => c.text).join('');
      return text || `[No response from Cohere]`;
    }
    if (typeof content === 'string') return content;
    return `[No response from Cohere]`;
  },
  retry: { maxAttempts: 2, baseDelay: 2000 },
  handleError: (status, errMsg, _attempt, _maxAttempts) => {
    if (status === 401 || status === 403) return { retry: false, message: `❌ Cohere API Key Invalid ... dashboard.cohere.com/api-keys` };
    if (status === 402)                    return { retry: false, message: `⚠️ Cohere trial credits exhausted — upgrade at dashboard.cohere.com/billing` };
    if (status === 429)                    return { retry: false, message: `⚠️ Cohere rate limit — trial keys are capped at 20 req/min. Wait a moment and try again.` };
    return null;
  }
}
```

Note the `parseResponse` — it handles three cases:
1. `content` is an array of `{type:'text', text:'...'}` (the common case — Cohere v2 standard shape)
2. `content` is a plain string (defensive fallback — some proxies flatten it)
3. Anything else → fallback error message

### 4. UI version label bumped

`v4.7.0 Active` → `v4.8.0 Active` — marks Phase 5 completion and the close of the multi-phase plan.

---

## LEGO Compliance Notes

- **Rule 1 (no hardcoded features):** Adding Cohere = one entry in `PROVIDER_DEFAULTS`, one in `DATA.providers`, one in `DATA.providerAdapters`. Zero HTML changes. Zero renderer changes. The new provider appears in the dropdown, the API Keys panel, and the tier-pill summaries automatically — because every renderer iterates the config.
- **Rule 2 (generic renderers):** `unifiedLLMRouter()` dispatches through the adapter's functions. Cohere's non-OpenAI shape is fully isolated inside its adapter — no branching in the router.
- **Rule 8 (no hardcoded keys):** Key is entered at runtime through the API Keys panel; `IP key.txt` remains a reference file, not a source of hardcoded secrets.
- **Rule 9 (fail gracefully):** `parseResponse` handles 3 response shapes. `handleError` returns `{ retry: false, message }` for 401/402/403/429 with actionable user guidance. Any other status falls through to the router's default error path.

---

## Testing Checklist

1. **Open `index14.html`** — topbar should read `v4.8.0 Active`
2. **Click 🔑 API Keys** — Cohere row should appear at the bottom with the coral/lavender logo and an amber `4 paid · min $0.15/1M` pill
3. **Paste your Cohere key** (from `IP key.txt`) and save
4. **Switch provider → Cohere** — logo badge beside the `<select>` should change to the gradient mark; model dropdown should show:
   - ── Paid (cheapest first) ──
     - Command R7B · $0.15/1M
     - Command R · $0.60/1M
     - Command R+ · $10.00/1M
     - Command A · $10.00/1M
5. **Send "hello"** — should get a response
6. **Test error handling:** temporarily mangle the key → send → should see the "Cohere API Key Invalid" message
7. **CORS:** if the browser blocks the direct call from `file://`, route through the local bridge the same way Anthropic does (set Custom IP → `http://localhost:3000`, have the bridge forward to `https://api.cohere.com`)

---

## What Did NOT Change

- No changes to any of the other 8 providers
- No changes to the router, widget system, chat state, persistence, or tier-pill rendering
- `splitSortModels()` / `fmtPrice()` / `renderApiKeysPanel()` / `onProviderChange()` all unchanged — they just see 9 providers now instead of 8
- `API_KEYS` / `API_IPS` / `PROVIDER_ENABLED` init loop from Phase 2 automatically covers Cohere because it iterates `Object.keys(DATA.providers)`

---

## Code Added (Phase 5)

- **`PROVIDER_DEFAULTS`:** +1 line
- **`DATA.providers.cohere`:** ~14 lines (entry + 4 models + SVG logo)
- **`DATA.providerAdapters.cohere`:** ~35 lines (the custom adapter)
- **Version label:** 1-character change

Total footprint: ~50 lines added, **zero lines modified** in existing provider code — a clean LEGO drop-in.

---

## Phase Status (Final)

- ✅ Phase 1 (index10): provider/model expansion with tier+price metadata
- ✅ Phase 2 (index11): 4 OpenAI-compatible adapters (DeepSeek, Groq, Mistral, Together) + state-init LEGO fix
- ✅ Phase 3 (index12): inline SVG brand logos for all 8 providers
- ✅ Phase 4 (index13): price badges + sorted/grouped model dropdown + tier-count pills
- ✅ Phase 5 (index14): Cohere adapter (custom non-OpenAI shape) — **this file**

**All 5 phases of the original `PHASES_PLAN.md` are now complete.**

Total providers: **9** (Gemini, OpenAI, Anthropic, ADAM, DeepSeek, Groq, Mistral, Together AI, Cohere)
Total models: **38** across free and paid tiers
Total inline SVG logos: **9**
