import { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import VoiceButton from './VoiceButton';

export default function ChatSidebar({ 
  messages, 
  isLoading, 
  language, 
  setLanguage, 
  vesselType = 'motorized_boat', 
  setVesselType, 
  onSend 
}) {
  const [inputText, setInputText] = useState('');
  const endOfMessagesRef = useRef(null);

  // The 8 Official ISRO SIH26176 Core Problem Scenarios
  const isroScenarios = [
    { label: "🐟 Nearest PFZ Today", query: "Where is the nearest Potential Fishing Zone today?" },
    { label: "⛵ Safe Tomorrow Morning?", query: "Is it safe to venture into the sea tomorrow morning?" },
    { label: "🌊 Tides & Sea Conditions", query: "What are the tide, weather, and sea conditions near my fishing location?" },
    { label: "⚡ Cyclone & Lightning Alerts", query: "Are there any lightning or cyclone alerts in my area?" },
    { label: "🌿 Chlorophyll & SST Fronts", query: "Which regions show high chlorophyll concentration and favourable sea surface temperature?" },
    { label: "🗺️ Safe Vessel Route", query: "What is the safest route for a fishing vessel considering weather and sea-state conditions?" },
    { label: "📉 Fish Productivity Decline", query: "Why has fish productivity declined in a particular coastal region?" },
    { label: "🚫 Avoid Restricted & MPAs", query: "Which fishing zones should be avoided due to hazardous marine conditions or geofencing restrictions?" }
  ];

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = () => {
    if (!inputText.trim() || isLoading) return;
    onSend(inputText);
    setInputText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="logo-area">
          <div className="title">🐋 ORCA</div>
          <div className="subtitle">ISRO Multi-Agent Marine Intelligence</div>
        </div>
        <div className="header-controls">
          <select 
            className="lang-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            title="Select Coastal Language"
          >
            <option value="en">English</option>
            <option value="hi">हिन्दी (Hindi)</option>
            <option value="gu">ગુજરાતી (Gujarati)</option>
            <option value="mr">मराठी (Marathi)</option>
            <option value="gom">कोंकणी (Konkani)</option>
            <option value="kn">ಕನ್ನಡ (Kannada)</option>
            <option value="ml">മലയാളം (Malayalam)</option>
            <option value="ta">தமிழ் (Tamil)</option>
            <option value="te">తెలుగు (Telugu)</option>
            <option value="or">ଓଡ଼ିଆ (Odia)</option>
            <option value="bn">বাংলা (Bengali)</option>
          </select>
          <select
            className="vessel-select"
            value={vesselType}
            onChange={(e) => setVesselType && setVesselType(e.target.value)}
            title="Select Craft Type"
          >
            <option value="motorized_boat">🚤 Motorized Boat</option>
            <option value="traditional_vallam">🛶 Traditional Craft</option>
            <option value="mechanized_trawler">🚢 Deep-Sea Trawler</option>
          </select>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <ChatMessage key={idx} message={msg} language={language} />
        ))}
        {isLoading && (
          <div className="message-wrapper assistant">
            <div className="message-bubble typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </div>

      {/* ISRO SIH26176 8 Scenario Quick Prompts */}
      <div className="quick-prompts-container">
        <div className="quick-prompts-label">🎯 ISRO Problem Scenarios (SIH26176):</div>
        <div className="quick-prompts">
          {isroScenarios.map((item, idx) => (
            <button
              key={idx}
              className="prompt-chip"
              onClick={() => onSend(item.query)}
              disabled={isLoading}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      <div className="chat-input-area">
        <div className="input-container">
          <textarea
            className="chat-input"
            placeholder="Ask about fishing, tides, weather, or routes in your language..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={isLoading}
          />
          <VoiceButton 
            onTranscript={(text) => {
               if (text) {
                 setInputText((prev) => prev ? `${prev} ${text}` : text);
               }
            }} 
            language={language} 
          />
          <button 
            className="icon-btn send-btn" 
            onClick={handleSend}
            disabled={!inputText.trim() || isLoading}
            title="Send Message"
            type="button"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
