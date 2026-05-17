"""Multilingual support module for Hindi and Kannada."""

import re

# Try to import googletrans, but handle if it's not available
try:
    from googletrans import Translator, LANGUAGES
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    Translator = None
    LANGUAGES = {}

class MultilingualProcessor:
    """Handle multilingual symptom input (English, Hindi, Kannada)."""

    def __init__(self):
        if GOOGLETRANS_AVAILABLE:
            self.translator = Translator()
        else:
            self.translator = None
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'kn': 'Kannada'
        }

        # Common symptom translations (fallback if API fails)
        self.symptom_dictionary = {
            'hi': {
                'खांसी': 'cough',
                'बुखार': 'fever',
                'सिरदर्द': 'headache',
                'जुकाम': 'cold',
                'दर्द': 'pain',
                'चक्कर': 'dizziness',
                'थकान': 'fatigue',
                'उल्टी': 'vomiting',
                'दस्त': 'diarrhea',
                'सांस फूलना': 'shortness_of_breath',
                'छींक': 'sneezing',
                'गले में दर्द': 'sore_throat',
                'पेट दर्द': 'stomach_pain',
                'सीने में दर्द': 'chest_pain',
                'सर्दी': 'cold',
                'तेज बुखार': 'high_fever',
                'कमजोरी': 'weakness',
                'भूख न लगना': 'loss_of_appetite',
                'आंखों में खुजली': 'itchy_eyes',
                'चिंता': 'anxiety',
                'घबराहट': 'nervousness',
                'प्यास': 'thirst',
                'शुष्क मुंह': 'dry_mouth'
            },
            'kn': {
                'ಕೆಮ್ಮು': 'cough',
                'ಜ್ವರ': 'fever',
                'ತಲೆನೋವು': 'headache',
                'ಶೀತ': 'cold',
                'ನೋವು': 'pain',
                'ತಲೆತಿರುಗುವುದು': 'dizziness',
                'ಅನಾರೋಗ್ಯ': 'fatigue',
                'ವಾಂತಿ': 'vomiting',
                'ಜುಳುಜುಳು': 'diarrhea',
                'ಉಸಿರಾಟದ ತೊಂದರೆ': 'shortness_of_breath',
                'ಸೀನು': 'sneezing',
                'ಗಂಟಲು ನೋವು': 'sore_throat',
                'ಹೊಟ್ಟೆ ನೋವು': 'stomach_pain',
                'ಎದೆಯ ನೋವು': 'chest_pain',
                'ಶೀತ': 'cold',
                'ಹೆಚ್ಚಿನ ಜ್ವರ': 'high_fever',
                'ದೌರ್ಬಲ್ಯ': 'weakness',
                'ಹಸಿವಿಲ್ಲ': 'loss_of_appetite',
                'ಕಣ್ಣುಗಳಲ್ಲಿ ತುರಿಕೆ': 'itchy_eyes',
                'ಚಿಂತೆ': 'anxiety',
                'ಆತಂಕ': 'nervousness',
                'ದಾಹ': 'thirst',
                'ಒಣ ಬಾಯಿ': 'dry_mouth'
            }
        }

    def detect_language(self, text):
        """Detect language of input text."""
        try:
            if GOOGLETRANS_AVAILABLE and self.translator:
                detection = self.translator.detect(text)
                return detection.lang
        except Exception as e:
            # Fallback detection based on character ranges
            if any('\u0900' <= c <= '\u097F' for c in text):
                return 'hi'
            elif any('\u0C80' <= c <= '\u0CFF' for c in text):
                return 'kn'
            else:
                return 'en'

    def translate_to_english(self, text, source_lang=None):
        """Translate text to English."""
        if source_lang == 'en' or not text:
            return text

        try:
            # First try dictionary lookup for known symptoms
            translated = self._dictionary_lookup(text, source_lang)
            if translated:
                return translated

            # Fall back to Google Translate if available
            if GOOGLETRANS_AVAILABLE and self.translator:
                result = self.translator.translate(text, dest='en', src=source_lang)
                return result.text.lower()
            else:
                # Use fallback if no translation service available
                return self._extract_symptoms_fallback(text, source_lang)
        except Exception as e:
            print(f"Translation error: {e}")
            # Return original with basic symptom extraction
            return self._extract_symptoms_fallback(text, source_lang)

    def _dictionary_lookup(self, text, lang):
        """Look up symptoms in the local dictionary."""
        if lang not in self.symptom_dictionary:
            return None

        text_lower = text.lower()
        dictionary = self.symptom_dictionary[lang]

        for symptom_trans, symptom_en in dictionary.items():
            if symptom_trans.lower() in text_lower:
                return symptom_en

        return None

    def _extract_symptoms_fallback(self, text, lang):
        """Fallback symptom extraction when translation fails."""
        # Simple keyword matching
        symptom_keywords = {
            'hi': {
                'खांसी': 'cough', 'बुखार': 'fever', 'सिरदर्द': 'headache',
                'दर्द': 'pain', 'चक्कर': 'dizziness', 'थकान': 'fatigue'
            },
            'kn': {
                'ಕೆಮ್ಮು': 'cough', 'ಜ್ವರ': 'fever', 'ತಲೆನೋವು': 'headache',
                'ನೋವು': 'pain', 'ತಲೆತಿರುಗುವುದು': 'dizziness', 'ಅನಾರೋಗ್ಯ': 'fatigue'
            }
        }

        if lang in symptom_keywords:
            for keyword, symptom in symptom_keywords[lang].items():
                if keyword in text:
                    return symptom

        return text

    def translate_symptoms(self, symptoms_list, source_lang):
        """Translate a list of symptoms to English."""
        translated = []
        for symptom in symptoms_list:
            trans = self.translate_to_english(symptom, source_lang)
            if trans:
                translated.append(trans)
        return translated

    def get_greeting(self, lang='en'):
        """Get greeting in specified language."""
        greetings = {
            'en': 'Hello! Please describe your symptoms.',
            'hi': 'नमस्ते! कृपया अपने लक्षण बताएं।',
            'kn': 'ನಮಸ್ಕಾರ! ದಯವಿಟ್ಟು ನಿಮ್ಮ ರೋಲಕ್ಷಣಗಳನ್ನು ವಿವರಿಸಿ.'
        }
        return greetings.get(lang, greetings['en'])

    def get_disclaimer(self, lang='en'):
        """Get medical disclaimer in specified language."""
        disclaimers = {
            'en': "This is not medical advice. Please consult a healthcare professional.",
            'hi': "यह चिकित्सा सलाह नहीं है। कृपया स्वास्थ्य पेशेवर से परामर्श करें।",
            'kn': "ಇದು ವೈದ್ಯಕೀಯ ಸಲಹೆಯ ಅಲ್ಲ. ದಯವಿಟ್ಟು ಆರೋಗ್ಯ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ."
        }
        return disclaimers.get(lang, disclaimers['en'])

    def process_input(self, text):
        """Process multilingual input and return English text."""
        detected_lang = self.detect_language(text)

        if detected_lang in ['hi', 'kn']:
            translated = self.translate_to_english(text, detected_lang)
            return {
                'original_text': text,
                'language': detected_lang,
                'language_name': self.supported_languages.get(detected_lang, 'Unknown'),
                'translated_text': translated
            }
        else:
            return {
                'original_text': text,
                'language': 'en',
                'language_name': 'English',
                'translated_text': text.lower()
            }
