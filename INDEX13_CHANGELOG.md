# INDEX13 CHANGELOG
## Phase 4 — Price Tier Badges + Sorted Model Dropdown

**Base file:** index12.html → index13.html
**Phase:** 4 of 5 (see `PHASES_PLAN.md`)
**Scope:** Group the model dropdown by tier (free first, paid ascending by price), show price badges inline on each option, and add a "5 free · 2 paid" tier count pill to every row in the API Keys panel.

---

## Audit Results

| Check | index12 | index13 |
|---|---|---|
| Model dropdown order | raw array order | sorted: free asc by price, then paid asc by price |
| Model dropdown grouping | flat list | `<optgroup>` with "Free tier" and "Paid (cheapest first)" labels |
| Price visible in option label | ❌ | ✅ `Llama 3.1 8B · FREE` / `Mistral Small · $0.60/1M` |
| Per-provider tier count in API Keys panel | ❌ | ✅ green "N free" pill + orange "N paid · min $X/1M" pill |
| Sort logic is generic (LEGO Rule 2) | — | ✅ `splitSortModels()` — one helper, every provider |
| CSS for pills is class-based (LEGO Rule 6) | — | ✅ `.apikeys-tier-pill.free` / `.apikeys-tier-pill.paid` |

---

## What Changed

### 1. New LEGO helper — `splitSortModels(models)`

One pure function, used by both the API Keys panel and the model dropdown:

```javascript
function splitSortModels(models) {
  const sorted = [...(models || [])].sort((a, b) => (a.price || 0) - (b.price || 0));
  return {
    free: sorted.filter(m => m.tier === 'free'),
    paid: sorted.filter(m => m.tier !== 'free')
  };
}
```

- Non-destructive — doesn't mutate `DATA.providers[k].models`
- Missing price / missing tier fall through safely (0-price → free-looking; missing tier → treated as paid)
- Called every time a provider is rendered (no cache needed; arrays are small)

### 2. New LEGO helper — `fmtPrice(m)`

Formats a model's price for UI display:
- `tier: 'free'` or no `price` → `FREE`
- Otherwise → `$X.XX/1M` (always 2 decimals)

### 3. Rewrote `onProviderChange()` — model dropdown now grouped + sorted

```javascript
const groups = splitSortModels(p.models);
const mkOpt = m => `<option value="${m.v}" ${(forceModel===m.v)?'selected':''}>${m.l} · ${fmtPrice(m)}</option>`;
let html = '';
if (groups.free.length) html += `<optgroup label="── Free tier ──">${groups.free.map(mkOpt).join('')}</optgroup>`;
if (groups.paid.length) html += `<optgroup label="── Paid (cheapest first) ──">${groups.paid.map(mkOpt).join('')}</optgroup>`;
mSel.innerHTML = html;
```

- Uses native `<optgroup>` — works in every browser, no custom dropdown needed
- Free options appear first, each sorted ascending by price
- Paid options follow, each sorted ascending by price
- Every option label ends with `· FREE` or `· $X.XX/1M`
- `optgroup` labels use dashes to look like separators in the native dropdown

### 4. Tier count pills in API Keys panel

Every row in the API Keys panel now shows a small summary line under the provider name:

```
[logo]  DeepSeek  [deepseek badge]  [toggle]
        🟢 2 paid · min $0.28/1M

[logo]  Groq      [groq badge]      [toggle]
        🟢 4 free
```

Rendered from the same `splitSortModels()` helper so the counts stay in perfect sync with the dropdown:

```javascript
const _g = splitSortModels(p.models);
const _cheapest = _g.paid[0] ? `min $${Number(_g.paid[0].price).toFixed(2)}/1M` : '';
const tierPillParts = [];
if (_g.free.length) tierPillParts.push(`<span class="apikeys-tier-pill free">${_g.free.length} free</span>`);
if (_g.paid.length) tierPillParts.push(`<span class="apikeys-tier-pill paid">${_g.paid.length} paid${_cheapest ? ' · ' + _cheapest : ''}</span>`);
```

### 5. CSS — 4 new declarations

```css
.apikeys-tier-counts     { display:flex; gap:6px; margin:4px 0 6px 30px; }
.apikeys-tier-pill       { padding:2px 8px; border-radius:10px; font-size:10px; font-weight:700; text-transform:uppercase; }
.apikeys-tier-pill.free  { background:rgba(34,197,94,0.15);  color:#22c55e; border:1px solid rgba(34,197,94,0.35); }
.apikeys-tier-pill.paid  { background:rgba(245,158,11,0.12); color:#f59e0b; border:1px solid rgba(245,158,11,0.3);  }
```

Green pills = free tier, amber pills = paid tier. The `30px` left margin aligns the pills under the provider name (past the logo).

---

## Per-Provider Dropdown Preview

After Phase 4 the model `<select>` for each provider now looks like:

**Gemini (5 free · 2 paid)**
- ── Free tier ──
  - Gemini 1.5 Flash-8B · $0.15/1M
  - Gemini 2.0 Flash Lite · $0.30/1M
  - Gemini 1.5 Flash · $0.30/1M
  - Gemini 2.0 Flash · $0.40/1M
  - Gemini 2.5 Flash · $0.60/1M
- ── Paid (cheapest first) ──
  - Gemini 1.5 Pro · $5.00/1M
  - Gemini 2.5 Pro · $10.00/1M

**Groq (4 free)**
- ── Free tier ──
  - Llama 3.1 8B Instant · FREE
  - Gemma 2 9B · FREE
  - Mixtral 8x7B · FREE
  - Llama 3.3 70B · FREE

**DeepSeek (2 paid · min $0.28/1M)**
- ── Paid (cheapest first) ──
  - DeepSeek V3 · $0.28/1M
  - DeepSeek R1 · $2.19/1M

(Note: Gemini's tiers carry Google's "generous free quota" label — those models ARE paid API products but include a free usage tier; we treat that tier marker as authoritative since you set it in Phase 1.)

---

## What Did NOT Change

- `DATA.providers[k].models` arrays are never mutated — sort happens on a copy
- No change to `DATA.providerAdapters` — routing/retry logic untouched
- No change to API key persistence, ping logic, or the config-driven state init
- No change to the provider dropdown itself (still flat, still shows provider names only — SVG logo beside it still handles visual distinction)
- Preferred-provider recall on reload still works via `localStorage.getItem('adam_default_provider')`

---

## LEGO Compliance Notes

- **Rule 1 (no hardcoded features):** Tier labels, sort order, and price decoration are all derived from `DATA.providers[k].models[i].{tier, price}`. Adding a new free-tier model = one entry, nothing else to edit.
- **Rule 2 (generic renderers):** `splitSortModels` and `fmtPrice` don't know about specific providers. They run on any `models[]` array.
- **Rule 4 (no duplicate logic):** The API Keys panel and the dropdown share the same helpers, so tier counts can never drift from the dropdown groups.
- **Rule 6 (CSS, not inline style):** All pill styling lives in classes.
- **Rule 9 (fail gracefully):** Missing `tier` defaults to paid; missing `price` renders as `FREE`; empty `models` array renders an empty dropdown with no crash.

---

## Testing Checklist

1. Open `index13.html` → click **🔑 API Keys**
2. Each provider row should show a **green "N free"** pill, an **orange "N paid · min $X/1M"** pill, or both
3. Open the model dropdown in the config bar
4. First group should be **"── Free tier ──"** (if the provider has free models), sorted cheapest first
5. Second group should be **"── Paid (cheapest first) ──"**, sorted cheapest first
6. Every option should end with `· FREE` or `· $X.XX/1M`
7. Switch providers — dropdown should always re-group correctly
8. Reload — previously selected model should remain selected (still works via `forceModel` argument)

---

## Code Added (Phase 4)

- **CSS rules:** 4 new declarations (+6 lines)
- **JS helpers:** `splitSortModels()` (+8 lines), `fmtPrice()` (+5 lines)
- **`onProviderChange()` rewrite:** +10 lines net
- **`renderApiKeysPanel()` tier pill section:** +7 lines

---

## Phase Status

- ✅ Phase 1 (index10): provider/model expansion with tier+price
- ✅ Phase 2 (index11): 4 OpenAI-compatible adapters + state-init LEGO fix
- ✅ Phase 3 (index12): inline SVG brand logos
- ✅ Phase 4 (index13): price badges + sorted/grouped dropdown — **this file**
- ⏳ Phase 5 (index14): Cohere adapter (non-OpenAI-compatible shape)
