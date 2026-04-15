const express = require('express');
const cors    = require('cors');
const axios   = require('axios');
const path    = require('path');

const app  = express();
const PORT = 3000;

// ─── Middleware ────────────────────────────────────────────────────────────────
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.static(__dirname));   // serves index.html + any other files in folder

// ─── Anthropic Proxy ──────────────────────────────────────────────────────────
// The chat UI sends to http://localhost:3000/v1/messages
// This forwards it to the real Anthropic API, adding CORS support
app.post('/v1/messages', async (req, res) => {
  try {
    const apiKey = req.headers['x-api-key'];
    if (!apiKey) {
      return res.status(400).json({ error: { message: 'No Anthropic API key provided. Enter it in the 🔑 API Keys panel.' } });
    }

    const response = await axios.post(
      'https://api.anthropic.com/v1/messages',
      req.body,
      {
        headers: {
          'x-api-key':           apiKey,
          'anthropic-version':   req.headers['anthropic-version'] || '2023-06-01',
          'Content-Type':        'application/json'
        }
      }
    );
    res.json(response.data);

  } catch (error) {
    const status = error.response?.status || 500;
    res.status(status).json(
      error.response?.data || { error: { message: error.message } }
    );
  }
});

// ─── OpenAI Proxy (optional) ──────────────────────────────────────────────────
// Set OpenAI custom IP to http://localhost:3000 in the API Keys panel if needed
app.post('/v1/chat/completions', async (req, res) => {
  try {
    const authHeader = req.headers['authorization'];
    if (!authHeader) {
      return res.status(400).json({ error: { message: 'No OpenAI API key provided. Enter it in the 🔑 API Keys panel.' } });
    }

    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      req.body,
      {
        headers: {
          'Authorization': authHeader,
          'Content-Type':  'application/json'
        }
      }
    );
    res.json(response.data);

  } catch (error) {
    const status = error.response?.status || 500;
    res.status(status).json(
      error.response?.data || { error: { message: error.message } }
    );
  }
});

// ─── Health check ─────────────────────────────────────────────────────────────
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'ADAM Bridge is running ✅' });
});

// ─── Start ────────────────────────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log('');
  console.log('╔══════════════════════════════════════╗');
  console.log('║       ADAM BRIDGE  ✅  RUNNING       ║');
  console.log('╚══════════════════════════════════════╝');
  console.log('');
  console.log('  👉  Open your browser and go to:');
  console.log(`       http://localhost:${PORT}`);
  console.log('');
  console.log('  ℹ️   Gemini  → works directly (enter key in UI)');
  console.log('  ℹ️   Anthropic → routed through this bridge');
  console.log('  ℹ️   OpenAI   → works directly (enter key in UI)');
  console.log('');
  console.log('  ⛔  Press Ctrl + C to stop the server');
  console.log('');
});
