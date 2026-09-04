import { useState, useCallback } from 'react';
import ChatSidebar from './components/ChatSidebar';
import MapView from './components/MapView';

export default function App() {
  const [hasStarted, setHasStarted] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Welcome to ORCA Marine Intelligence! I can help you with ocean conditions, safety alerts, fishing zones, and route planning along the Indian coast. Try asking me about weather near Mumbai or fishing zones near Mangalore.',
      timestamp: new Date()
    }
  ]);
  const [layers, setLayers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState('en');

  if (!hasStarted) {
    return (
      <div className="splash-screen">
        <div className="splash-content">
          <div className="splash-logo">🐋 ORCA</div>
          <h1 className="splash-title">Marine Ecosystem Reasoning with Collaborative Agents</h1>
          <p className="splash-subtitle">Empowering coastal communities with AI-driven marine intelligence.</p>
          <button className="splash-btn" onClick={() => setHasStarted(true)}>
            Enter Platform
          </button>
        </div>
      </div>
    );
  }

  const handleSend = useCallback(async (text) => {
    if (!text.trim()) return;

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
          location: 'auto', // Optionally hook up geolocation later
          language: language
        })
      });

      if (!res.ok) throw new Error(`Server returned ${res.status}`);
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
        content: `Sorry, I encountered an error connecting to the ORCA platform: ${err.message}`,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [language]);

  return (
    <div className="app-container">
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
