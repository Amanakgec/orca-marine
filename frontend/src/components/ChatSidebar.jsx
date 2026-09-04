import { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import VoiceButton from './VoiceButton';

export default function ChatSidebar({ messages, isLoading, language, setLanguage, onSend }) {
  const [inputText, setInputText] = useState('');
  const endOfMessagesRef = useRef(null);

  const quickPrompts = [
    { label: "🐟 Fishing in Kochi", query: "Show potential fishing zones near Kochi" },
    { label: "🌊 Weather in Mumbai", query: "What are the ocean weather and wave conditions off Mumbai?" },
    { label: "⚠️ Risk at Rameswaram", query: "Check safety risk and IMBL boundary near Rameswaram" },
    { label: "🗺️ Route Vizag to Chennai", query: "Compute a safe navigation route from Vizag to Chennai" }
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
          <div className="subtitle">Marine Intelligence Swarm</div>
        </div>
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

      {/* Quick Prompt Chips */}
      <div className="quick-prompts">
        {quickPrompts.map((item, idx) => (
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

      <div className="chat-input-area">
        <div className="input-container">
          <textarea
            className="chat-input"
            placeholder="Ask about fishing, weather, or routes in your language..."
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
