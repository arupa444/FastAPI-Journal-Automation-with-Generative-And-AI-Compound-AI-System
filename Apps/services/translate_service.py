# File: Apps/services/translate_service.py
from Apps.library_import import GoogleTranslator, Dict, Any, time


class TranslationService:
    """Service class for text and dictionary translation."""

    def __init__(self, max_len: int = 4900):
        """
        Initialize the translation service.
        :param max_len: Maximum characters per translation request (API limit ~5000 chars).
        """
        self.max_len = max_len

    # ==========================
    # 🧩 Text Translation
    # ==========================
    def split_and_translate(self, text: str, dest_lang: str) -> str:
        """
        Splits large text into manageable chunks and translates each chunk separately.

        Args:
            text (str): Input text to translate.
            dest_lang (str): Target language code (e.g. 'fr', 'es', 'hi').

        Returns:
            str: The fully translated text.
        """
        if not text:
            return ""

        # If text is short enough, translate directly
        if len(text) <= self.max_len:
            return self._safe_translate(text, dest_lang)

        paragraphs = text.split("\n\n")  # preserve logical paragraph breaks
        chunks, current = [], ""

        for para in paragraphs:
            if len(current) + len(para) + 2 <= self.max_len:
                current += para + "\n\n"
            else:
                chunks.append(current.strip())
                current = para + "\n\n"
        if current.strip():
            chunks.append(current.strip())

        translated_chunks = [self._safe_translate(chunk, dest_lang) for chunk in chunks]

        return "\n\n".join(translated_chunks)

    # ==========================
    # 🧠 Dictionary Translation
    # ==========================
    def translate_dict(
        self, input_dict: Dict[str, Any], dest_lang: str
    ) -> Dict[str, Any]:
        """
        Translate all string values inside a dictionary.

        Args:
            input_dict (dict): Dictionary containing string values to translate.
            dest_lang (str): Target language code.

        Returns:
            dict: Dictionary with translated values.
        """
        translated = {}
        for key, value in input_dict.items():
            if isinstance(value, str):
                translated[key] = self.split_and_translate(value, dest_lang)
            else:
                translated[key] = value  # leave non-string data unchanged
        return translated

    # ==========================
    # 🛡️ Private Helper
    # ==========================
    def _safe_translate(self, text: str, dest_lang: str) -> str:
        """Safely call the translation API with basic retry logic."""
        try:
            return GoogleTranslator(source="auto", target=dest_lang).translate(text)
        except Exception as e:
            print(f"[WARN] Translation failed: {e}. Retrying...")
            time.sleep(2)
            try:
                return GoogleTranslator(source="auto", target=dest_lang).translate(text)
            except Exception:
                return text  # fallback to original if all retries fail
