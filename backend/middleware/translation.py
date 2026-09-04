from deep_translator import GoogleTranslator

class TranslationMiddleware:
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'gu': 'Gujarati',
        'mr': 'Marathi',
        'gom': 'Konkani',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'ta': 'Tamil',
        'te': 'Telugu',
        'or': 'Odia',
        'bn': 'Bengali'
    }
    
    async def translate_to_english(self, text: str, source_lang: str) -> str:
        """Translate input to English for processing using deep-translator."""
        if source_lang == 'en': return text
        try:
            # Map 'gom' (Konkani) to 'mr' (Marathi) as fallback if deep_translator lacks 'gom'
            trans_lang = 'mr' if source_lang == 'gom' else source_lang
            return GoogleTranslator(source=trans_lang, target='en').translate(text)
        except Exception as e:
            print(f"Translation to EN failed: {e}")
            return text
        
    async def translate_from_english(self, text: str, target_lang: str) -> str:
        """Translate English response to target language using deep-translator."""
        if target_lang == 'en': return text
        try:
            trans_lang = 'mr' if target_lang == 'gom' else target_lang
            return GoogleTranslator(source='en', target=trans_lang).translate(text)
        except Exception as e:
            print(f"Translation from EN failed: {e}")
            return text
        
    def detect_language(self, text: str) -> str:
        """Detect language of input text using Unicode ranges."""
        for char in text:
            code = ord(char)
            if 0x0A80 <= code <= 0x0AFF: return 'gu' # Gujarati
            if 0x0900 <= code <= 0x097F: return 'mr' # Marathi/Hindi
            if 0x0C80 <= code <= 0x0CFF: return 'kn' # Kannada
            if 0x0D00 <= code <= 0x0D7F: return 'ml' # Malayalam
            if 0x0B80 <= code <= 0x0BFF: return 'ta' # Tamil
            if 0x0C00 <= code <= 0x0C7F: return 'te' # Telugu
            if 0x0B00 <= code <= 0x0B7F: return 'or' # Odia
            if 0x0980 <= code <= 0x09FF: return 'bn' # Bengali
        return 'en'
