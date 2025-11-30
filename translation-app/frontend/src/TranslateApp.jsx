import React, { useState } from 'react';

export default function TranslateApp() {
  const [text, setText] = useState('');
  const [from, setFrom] = useState('auto');
  const [to, setTo] = useState('fr');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const languages = [
    { code: 'auto', name: 'Auto-detect' },
    { code: 'en', name: 'English' },
    { code: 'fr', name: 'French' },
    { code: 'es', name: 'Spanish' },
    { code: 'de', name: 'German' },
    { code: 'ar', name: 'Arabic' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'zh-Hans', name: 'Chinese (Simplified)' },
  ];

  async function handleTranslate() {
    setLoading(true);
    setError(null);
    setResult('');
    try {
      const resp = await fetch('/api/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, from, to })
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      setResult(data.translatedText ?? '');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleCopy() {
    if (!result) return;
    navigator.clipboard.writeText(result);
  }

  function handleSpeak() {
    if (!result || !('speechSynthesis' in window)) return;
    const utter = new SpeechSynthesisUtterance(result);
    utter.lang = to === 'auto' ? 'en-US' : to;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);
  }

  return (
    <div style={{ maxWidth: 800, margin: '2rem auto', padding: 16, fontFamily: 'sans-serif' }}>
      <h1>Translation Tool</h1>

      <label>Source text</label>
      <textarea
        rows="6"
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="Enter text to translate..."
        style={{ width: '100%', padding: 8, marginTop: 8, marginBottom: 12 }}
      />

      <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
        <div>
          <label>From</label>
          <br />
          <select value={from} onChange={e => setFrom(e.target.value)} style={{ padding: 8 }}>
            {languages.map(l => <option key={l.code} value={l.code}>{l.name}</option>)}
          </select>
        </div>

        <div>
          <label>To</label>
          <br />
          <select value={to} onChange={e => setTo(e.target.value)} style={{ padding: 8 }}>
            {languages.filter(l => l.code !== 'auto').map(l => <option key={l.code} value={l.code}>{l.name}</option>)}
          </select>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
        <button onClick={handleTranslate} disabled={!text.trim() || loading} style={{ padding: '8px 12px' }}>
          {loading ? 'Translating...' : 'Translate'}
        </button>
        <button onClick={() => { setText(''); setResult(''); }} style={{ padding: '8px 12px' }}>Clear</button>
      </div>

      <label>Result</label>
      <div style={{ minHeight: 120, marginTop: 8, padding: 12, border: '1px solid #ddd', background: '#fafafa' }}>
        {error ? <div style={{ color: 'red' }}>{error}</div> : <pre style={{ whiteSpace: 'pre-wrap' }}>{result}</pre>}
      </div>

      <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
        <button onClick={handleCopy} disabled={!result} style={{ padding: '6px 10px' }}>Copy</button>
        <button onClick={handleSpeak} disabled={!result} style={{ padding: '6px 10px' }}>Speak</button>
      </div>

      <p style={{ marginTop: 12, color: '#666' }}>Note: This frontend calls the backend at <code>/api/translate</code>.</p>
    </div>
  );
}
