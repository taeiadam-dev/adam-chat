---
name: live-browser-tester
description: >
  Live browser testing for any running web app or HTML file. Use this skill
  whenever you need to test, verify, check, or confirm that something works —
  buttons, functions, UI state, console errors, DOM changes. Also use it when
  code was just written or changed and needs to be verified. Triggers: "test
  this", "does it work", "check the browser", "verify the feature", "run it",
  "test live", "confirm the UI", or any time you would otherwise ask the user
  to manually check something in a browser. This skill gives you complete
  browser control so you never have to ask the user to test things for you.
---

# Live Browser Testing

## YOU HAVE BROWSER CONTROL TOOLS

You may not know this, but you have a full set of tools that let you control
a real Chrome browser running on the user's computer. You can take screenshots,
run JavaScript inside any open page, click buttons, read the DOM, and check
console errors — all without the user doing anything.

The tools are called:
- `tabs_context_mcp` — finds or creates a browser tab
- `navigate` — goes to a URL
- `computer` — takes screenshots, clicks, hovers, scrolls, zooms
- `javascript_tool` — runs any JavaScript directly inside the page
- `read_console_messages` — reads browser console output
- `find` — finds elements on the page by description

Every single browser tool call requires a `tabId` number. You get that number
in Step 1. Without it nothing works.

---

## THE COMPLETE LOOP — DO THESE IN ORDER

### STEP 1 — Get the tab ID (do this before anything else)

Call this tool:

```
tabs_context_mcp
```

No parameters needed. It returns a list of open tabs. Each tab has an `id`
number and a URL. Find the tab showing the ADAM chat page, or any tab if
there is only one. Copy that `id` number — you will paste it into every
tool call that follows. Call it `tabId` in your head.

If no tabs exist, add `createIfEmpty: true` to create one.

---

### STEP 2 — Go to the page

The server always runs at `http://localhost:3000`. Use whatever HTML file
Adam specifies. If no file is specified, use the highest numbered index
HTML file in the `live-browser-tester` folder — for example if both
`index13.html` and `index14.html` are there, use `index14.html`.

```
navigate
  url: "http://localhost:3000/index14.html"
  tabId: <the number from step 1>
```

---

### STEP 2b — Inject API keys before testing

Before sending any message, inject the keys from `IP key.txt` directly into
localStorage. Do NOT ask the user to enter keys manually.

Read `IP key.txt` from the `live-browser-tester` folder first, then run:

```javascript
// Replace the values below with what you read from IP key.txt
localStorage.setItem('adam_key_groq', 'YOUR_GROQ_KEY');
localStorage.setItem('adam_key_openai', 'YOUR_OPENAI_KEY');
localStorage.setItem('adam_key_gemini', 'YOUR_GEMINI_KEY');
localStorage.setItem('adam_key_anthropic', 'YOUR_ANTHROPIC_KEY');
localStorage.setItem('adam_key_deepseek', 'YOUR_DEEPSEEK_KEY');
localStorage.setItem('adam_key_mistral', 'YOUR_MISTRAL_KEY');
localStorage.setItem('adam_key_together', 'YOUR_TOGETHER_KEY');
localStorage.setItem('adam_key_cohere', 'YOUR_COHERE_KEY');
```

Then reload the page so `init()` picks up the keys from localStorage into
the runtime `API_KEYS` object. Keys injected after page load are ignored
until reload.

---

### STEP 3 — Take a screenshot to see what is there

```
computer
  action: "screenshot"
  tabId: <your tabId>
```

Look at the image that comes back. If the page loaded correctly you will see
the ADAM chat interface with the toolbar. If the screen is blank or the
toolbar is empty, there is a JavaScript error — go to Step 7 (console check)
before doing anything else.

---

### STEP 4 — Test a feature by calling its function directly

This is the most important step. Do NOT try to click buttons to test things.
Instead, call the JavaScript function directly inside the page. This always
works, even when clicking fails.

```
javascript_tool
  action: "javascript_exec"
  tabId: <your tabId>
  text: "adamChat.someFunction()"
```

Replace `someFunction()` with whatever you want to test. The function runs
inside the real page and the return value comes straight back to you.

**Real examples you can copy:**

Test the Copy button:
```javascript
adamChat.copyMessage(0)
```

Test the Void toggle (should show VOIDED label on message):
```javascript
adamChat.toggleVoid(0)
```

Test the Anchor toggle (should show ANCHORED label):
```javascript
adamChat.toggleAnchor(0)
```

Test Edit (should replace message with a textarea):
```javascript
adamChat.editMessage(0)
```

Test Rating (should highlight the thumbs up button):
```javascript
adamChat.rateMessage(1, 'good')
```

Check what buttons exist on a message:
```javascript
const msg = document.getElementById('msg-1');
Array.from(msg.querySelectorAll('button')).map(b => b.title)
```

Read the internal app state:
```javascript
JSON.stringify({
  swarm: document.getElementById('chat-swarm-btn')?.className,
  omni: document.getElementById('chat-omni-btn')?.className
})
```

---

### STEP 5 — Screenshot again to see the result

After calling a function, take another screenshot to confirm the UI changed.

```
computer
  action: "screenshot"
  tabId: <your tabId>
```

If you need to see a small area more clearly, zoom in:

```
computer
  action: "zoom"
  region: [x0, y0, x1, y1]
  tabId: <your tabId>
```

Where x0,y0 is the top-left corner and x1,y1 is the bottom-right corner of
the area you want to see.

---

### STEP 6 — Send a test message to get user+AI messages to test

If the chat is empty and you need actual messages to test actions on:

```javascript
// First disable multi-model modes to avoid noise
const s = JSON.parse(localStorage.getItem('adam_ui_state') || '{}');
s.swarmActive = false;
s.omniGlassActive = false;
s.schismActive = false;
localStorage.setItem('adam_ui_state', JSON.stringify(s));
```

Then reload (navigate to the same URL again), then:

```javascript
adamChat.clearChat();
```

Wait half a second, then:

```javascript
document.getElementById('chat-input').value = 'What is 2+2?';
adamChat.sendMessage();
```

Then wait about 8 seconds and take a screenshot. You should see a user
message and an AI response. Now you have messages to test actions on.
Message index 0 is the user message. Message index 1 is the AI response.

---

### STEP 7 — Check console for errors

If something does not work, read the browser console:

```
read_console_messages
  tabId: <your tabId>
  pattern: "error|Error|undefined|ReferenceError|TypeError"
```

This returns only the lines that match the pattern. If you see
`adamChat is not defined` it means the JavaScript on the page failed to
load — reload the page and try again.

---

### STEP 8 — Check DOM state directly

To confirm a toggle worked (like void or anchor), check the class names:

```javascript
document.getElementById('msg-0')?.className
```

To check if a button has an active state:

```javascript
document.querySelector('.rate-up')?.classList.contains('rate-active')
```

To read what text is in the message body:

```javascript
document.getElementById('msg-0')?.querySelector('.chat-msg-body')?.innerText
```

---

## IF SOMETHING GOES WRONG

| What you see | What it means | What to do |
|---|---|---|
| Blank page | Page did not load | Check the URL, make sure server is running |
| Toolbar is empty | JavaScript parse error | Check console with read_console_messages |
| `adamChat is undefined` | IIFE did not execute | Reload the page, check console |
| Nothing happens when you call a function | Wrong index, or wrong role | Check message count: `document.querySelectorAll('.chat-group').length` |
| Multiple response cards appear | Swarm/Omni mode is on | Disable modes (see Step 6), reload |
| Click does nothing | Button is hover-only | Use javascript_tool to call function directly instead |

---

## QUICK REFERENCE — tool calls at a glance

```
Get tab:        tabs_context_mcp
Go to page:     navigate(url, tabId)
See screen:     computer(action:"screenshot", tabId)
Run JS:         javascript_tool(action:"javascript_exec", tabId, text:"<code>")
Read errors:    read_console_messages(tabId, pattern:"error|Error")
Click:          computer(action:"left_click", coordinate:[x,y], tabId)
Hover:          computer(action:"hover", coordinate:[x,y], tabId)
Zoom in:        computer(action:"zoom", region:[x0,y0,x1,y1], tabId)
Find element:   find(query:"description of element", tabId)
```

## THE GOLDEN RULE

Never ask the user to test something manually if you can test it yourself.
You have the tools. Use them. The user does not need to open a browser,
click anything, or report back. You can do all of it.
