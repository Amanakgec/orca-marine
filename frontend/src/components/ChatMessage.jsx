import { useState, useRef } from 'react';
import AgentReasoning from './AgentReasoning';
import { useSpeech } from '../hooks/useSpeech';

export default function ChatMessage({ message, language = 'en' }) {
  const { role, content, reasoning, timestamp } = message;
  const isUser = role === 'user';
  const { speak } = useSpeech(language);

  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoadingAudio, setIsLoadingAudio] = useState(false);
  const audioRef = useRef(null);

  const handleTogglePlay = async () => {
    // If currently playing, stop it
    if (isPlaying) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
      setIsPlaying(false);
      return;
    }

    // Try high-quality Neural AI Voice from backend first
    setIsLoadingAudio(true);
    try {
      if (audioRef.current) {
        audioRef.current.pause();
      }

      const params = new URLSearchParams({
        text: content,
        language: language || 'en'
      });

      const apiBase = import.meta.env.VITE_API_URL || '';
      const audio = new Audio(`${apiBase}/api/tts?${params.toString()}`);
      audioRef.current = audio;

      audio.onplay = () => {
        setIsLoadingAudio(false);
        setIsPlaying(true);
      };

      audio.onended = () => {
        setIsPlaying(false);
      };

      audio.onerror = () => {
        console.warn("Backend TTS failed, falling back to browser speech synthesis");
        setIsLoadingAudio(false);
        setIsPlaying(false);
        speak(content, language);
      };

      await audio.play();
    } catch (e) {
      console.warn("Audio playback error, using fallback:", e);
      setIsLoadingAudio(false);
      setIsPlaying(false);
      speak(content, language);
    }
  };

  // Basic markdown bold formatting
  const formatText = (text) => {
    if (!text) return '';
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return <span key={i}>{part}</span>;
    });
  };

  const formattedTime = timestamp ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';

  return (
    <div className={`message-wrapper ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-bubble">
        {content.split('\n').map((line, i) => (
          <div key={i} style={{ minHeight: '1.2em' }}>
            {formatText(line)}
          </div>
        ))}
        {reasoning && reasoning.length > 0 && (
          <AgentReasoning steps={reasoning} />
        )}
        {!isUser && content && (
          <div className="message-actions">
            <button
              className={`speak-btn ${isPlaying ? 'playing' : ''}`}
              onClick={handleTogglePlay}
              title={isPlaying ? "Click to stop" : "Listen in natural AI voice"}
              type="button"
              disabled={isLoadingAudio}
            >
              {isLoadingAudio ? (
                <span>⏳ Loading voice...</span>
              ) : isPlaying ? (
                <span>⏹️ Stop Voice</span>
              ) : (
                <span>🎙️ Natural AI Voice</span>
              )}
            </button>
          </div>
        )}
      </div>
      <div className="message-time">{formattedTime}</div>
    </div>
  );
}
