import asyncio
import re
from deep_translator import GoogleTranslator

class TranslationMiddleware:
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'hi': 'Hindi',
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

    GOOGLE_LANG_MAP = {
        'en': 'en',
        'hi': 'hi',
        'gu': 'gu',
        'mr': 'mr',
        'gom': 'mr',
        'kn': 'kn',
        'ml': 'ml',
        'ta': 'ta',
        'te': 'te',
        'or': 'or',
        'bn': 'bn'
    }

    def _clean_for_translation(self, text: str) -> str:
        # Remove bold markdown and excessive formatting that confuse translation endpoints
        cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        cleaned = re.sub(r'[*_#`]', '', cleaned)
        return cleaned

    def _sync_translate_to_en(self, text: str, source_lang: str) -> str:
        if source_lang == 'en' or not text.strip():
            return text
        try:
            target_source = self.GOOGLE_LANG_MAP.get(source_lang, 'auto')
            clean_text = self._clean_for_translation(text)
            translated = GoogleTranslator(source=target_source, target='en').translate(clean_text)
            return translated if translated else text
        except Exception as e:
            print(f"[Translation] Error translating to EN ({source_lang}): {e}")
            return text

    def _sync_translate_from_en(self, text: str, target_lang: str) -> str:
        if target_lang == 'en' or not text.strip():
            return text
        try:
            target = self.GOOGLE_LANG_MAP.get(target_lang, 'en')
            if target == 'en':
                return text

            # Clean markdown formatting
            clean_text = self._clean_for_translation(text)
            lines = [l.strip() for l in clean_text.split('\n') if l.strip()]

            if not lines:
                return text

            # Translate paragraph-by-paragraph for reliable results
            translator = GoogleTranslator(source='en', target=target)
            translated_lines = []
            for line in lines:
                # Keep short bullet prefixes
                prefix = ""
                if line.startswith("•"):
                    prefix = "• "
                    line = line[1:].strip()
                elif line.startswith("-"):
                    prefix = "- "
                    line = line[1:].strip()

                try:
                    res = translator.translate(line)
                    translated_lines.append(f"{prefix}{res}" if res else f"{prefix}{line}")
                except Exception:
                    translated_lines.append(f"{prefix}{line}")

            return "\n\n".join(translated_lines)
        except Exception as e:
            print(f"[Translation] Error translating from EN ({target_lang}): {e}")
            return text

    async def translate_to_english(self, text: str, source_lang: str) -> str:
        return await asyncio.to_thread(self._sync_translate_to_en, text, source_lang)

    async def translate_from_english(self, text: str, target_lang: str) -> str:
        return await asyncio.to_thread(self._sync_translate_from_en, text, target_lang)

    def detect_language(self, text: str) -> str:
        if not text:
            return 'en'
        for char in text:
            code = ord(char)
            if 0x0900 <= code <= 0x097F: return 'hi'
            elif 0x0A80 <= code <= 0x0AFF: return 'gu'
            elif 0x0B80 <= code <= 0x0BFF: return 'ta'
            elif 0x0C00 <= code <= 0x0C7F: return 'te'
            elif 0x0C80 <= code <= 0x0CFF: return 'kn'
            elif 0x0D00 <= code <= 0x0D7F: return 'ml'
            elif 0x0B00 <= code <= 0x0B7F: return 'or'
            elif 0x0980 <= code <= 0x09FF: return 'bn'
        return 'en'
