// server.js
require('dotenv').config();
const express = require('express');
const fetch = require('node-fetch');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors()); // in production restrict origin

const TRANSLATOR_KEY = process.env.TRANSLATOR_KEY; // Azure key
const TRANSLATOR_ENDPOINT = process.env.TRANSLATOR_ENDPOINT; // e.g. https://api.cognitive.microsofttranslator.com
const TRANSLATOR_REGION = process.env.TRANSLATOR_REGION || ''; // region if required

if (!TRANSLATOR_KEY || !TRANSLATOR_ENDPOINT) {
  console.warn('Warning: TRANSLATOR_KEY or TRANSLATOR_ENDPOINT not set. The translate endpoint will fail without them.');
}

app.post('/api/translate', async (req, res) => {
  try {
    const { text, from, to } = req.body;
    if (!text) return res.status(400).json({ error: 'No text provided.' });

    // Build translator URL (Azure Translator Text v3)
    const params = new URLSearchParams();
    params.append('api-version', '3.0');
    params.append('to', to);
    if (from && from !== 'auto') params.append('from', from);

    const url = `${TRANSLATOR_ENDPOINT}/translate?${params.toString()}`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Ocp-Apim-Subscription-Key': TRANSLATOR_KEY,
        'Content-Type': 'application/json',
        ...(TRANSLATOR_REGION ? { 'Ocp-Apim-Subscription-Region': TRANSLATOR_REGION } : {})
      },
      body: JSON.stringify([{ Text: text }])
    });

    if (!response.ok) {
      const errText = await response.text();
      return res.status(response.status).json({ error: 'Translation API error', details: errText });
    }

    const data = await response.json();
    const translatedText = (data && data[0] && data[0].translations && data[0].translations[0] && data[0].translations[0].text) || '';

    return res.json({ translatedText });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error', details: err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Translation backend listening on ${PORT}`));
