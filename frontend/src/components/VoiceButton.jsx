import { useEffect } from 'react';
import { useSpeech } from '../hooks/useSpeech';

export default function VoiceButton({ onTranscript, language }) {
  const { isListening, transcript, startListening, stopListening, isSupported, setTranscript, error } = useSpeech(language);

  // Send transcript back when speech recognition completes
  useEffect(() => {
    if (!isListening && transcript && transcript.trim().length > 0) {
      onTranscript(transcript);
      if (typeof setTranscript === 'function') {
        setTranscript('');
      }
    }
  }, [isListening, transcript, onTranscript, setTranscript]);

  if (!isSupported) {
    return (
      <button
        className="icon-btn voice-btn disabled"
        title="Speech recognition not supported in this browser"
        type="button"
        disabled
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="1" y1="1" x2="23" y2="23"></line>
          <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"></path>
          <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"></path>
          <line x1="12" y1="19" x2="12" y2="23"></line>
          <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
      </button>
    );
  }

  return (
    <button
      className={`icon-btn voice-btn ${isListening ? 'recording' : ''}`}
      onClick={isListening ? stopListening : startListening}
      title={isListening ? 'Listening (Click to stop)...' : 'Click to speak in your chosen language'}
      type="button"
    >
      {isListening ? (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="4" y="4" width="16" height="16" rx="3" ry="3" fill="#e74c3c"></rect>
        </svg>
      ) : (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
          <line x1="12" y1="19" x2="12" y2="23"></line>
          <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
      )}
    </button>
  );
}
