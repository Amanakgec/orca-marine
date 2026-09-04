import { useEffect } from 'react';
import { useSpeech } from '../hooks/useSpeech';

export default function VoiceButton({ onTranscript, language }) {
  const { isListening, transcript, startListening, stopListening, isSupported, setTranscript } = useSpeech(language);

  // Send transcript back when it updates and we stop listening
  useEffect(() => {
    if (!isListening && transcript) {
      onTranscript(transcript);
      setTranscript('');
    }
  }, [isListening, transcript, onTranscript, setTranscript]);

  if (!isSupported) {
    return null;
  }

  return (
    <button
      className={`icon-btn voice-btn ${isListening ? 'recording' : ''}`}
      onClick={isListening ? stopListening : startListening}
      title={isListening ? 'Listening...' : 'Click to speak'}
      type="button"
    >
      {isListening ? (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
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
