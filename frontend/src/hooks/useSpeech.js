import { useState, useCallback, useEffect, useRef } from 'react';

export function useSpeech(language = 'en') {
  const [transcript, setTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  const langMap = {
    'en': 'en-IN',
    'gu': 'gu-IN',
    'mr': 'mr-IN',
    'gom': 'gom-IN',
    'kn': 'kn-IN',
    'ml': 'ml-IN',
    'ta': 'ta-IN',
    'te': 'te-IN',
    'or': 'or-IN',
    'bn': 'bn-IN'
  };

  const isSupported = 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;

  useEffect(() => {
    if (!isSupported) return;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onresult = (event) => {
      const current = event.resultIndex;
      const result = event.results[current][0].transcript;
      setTranscript(result);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
  }, [isSupported]);

  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = langMap[language] || 'en-IN';
    }
  }, [language]);

  const startListening = useCallback(() => {
    if (!isSupported || !recognitionRef.current) return;
    setTranscript('');
    try {
      recognitionRef.current.start();
      setIsListening(true);
    } catch (e) {
      console.error(e);
    }
  }, [isSupported]);

  const stopListening = useCallback(() => {
    if (!isSupported || !recognitionRef.current) return;
    recognitionRef.current.stop();
    setIsListening(false);
  }, [isSupported]);

  const speak = useCallback((text) => {
    if (!('speechSynthesis' in window)) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langMap[language] || 'en-IN';
    window.speechSynthesis.speak(utterance);
  }, [language]);

  return {
    transcript,
    isListening,
    startListening,
    stopListening,
    speak,
    isSupported
  };
}
