import { useState, useCallback } from 'react';
import ChatSidebar from './components/ChatSidebar';
import MapView from './components/MapView';

export default function App() {
  const [showIntro, setShowIntro] = useState(true);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Welcome to ORCA Marine Intelligence! 🐋 I can help you with real-time ocean conditions, safety alerts, potential fishing zones (PFZ), and safe route planning along the Indian coast. Try asking about fishing in Kochi or wave heights in Mumbai.',
      timestamp: new Date()
    }
  ]);
  const [layers, setLayers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState('en');

  const handleSend = useCallback(async (text) => {
    if (!text.trim()) return;
    if (showIntro) setShowIntro(false);

    const userMsg = {
      role: 'user',
      content: text,
      timestamp: new Date()
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          location: 'auto',
          language: language
        })
      });

      if (!res.ok) throw new Error(`Server returned status ${res.status}`);
      const data = await res.json();

      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: data.text_response,
        reasoning: data.agent_reasoning,
        layers: data.geojson_layers,
        timestamp: new Date()
      }]);

      if (data.geojson_layers && data.geojson_layers.length > 0) {
        setLayers(data.geojson_layers);
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: `Sorry, could not fetch marine data: ${err.message}. Please verify the backend is running.`,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [language, showIntro]);

  return (
    <div className="app-container">
      {/* Aesthetic Hero Modal Overlay (dismissible on click) */}
      {showIntro && (
        <div className="splash-screen" onClick={() => setShowIntro(false)}>
          <div className="splash-content" onClick={(e) => e.stopPropagation()}>
            <div className="splash-logo">🐋</div>
            <div className="splash-tagline">ISRO SIH26176 · ORCA</div>
            <h1 className="splash-title">Marine Ecosystem Reasoning with Collaborative Agents</h1>
            <p className="splash-subtitle">
              AI-powered ocean intelligence for India's coastal communities —<br />
              Potential Fishing Zones (PFZ), safety alerts, routing &amp; live ocean data.
            </p>
            <div className="splash-features">
              <div className="splash-feature"><span>🌊</span><span>Ocean Data</span></div>
              <div className="splash-feature"><span>🎣</span><span>Fishing Zones</span></div>
              <div className="splash-feature"><span>⚠️</span><span>Safety Alerts</span></div>
              <div className="splash-feature"><span>🗺️</span><span>Safe Routing</span></div>
              <div className="splash-feature"><span>🗣️</span><span>11 Languages</span></div>
            </div>
            <button className="splash-btn" onClick={() => setShowIntro(false)} type="button">
              🚀 Explore Marine Map
            </button>
            <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: '#94a3b8', cursor: 'pointer' }} onClick={() => setShowIntro(false)}>
              (Click anywhere to start)
            </div>
          </div>
        </div>
      )}

      <ChatSidebar
        messages={messages}
        isLoading={isLoading}
        language={language}
        setLanguage={setLanguage}
        onSend={handleSend}
      />
      <MapView layers={layers} />
    </div>
  );
}
