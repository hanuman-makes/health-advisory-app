import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from multilingualprocessor import MultilingualProcessor


def test_translate_to_english_hi_dictionary():
    processor = MultilingualProcessor()
    translated = processor.translate_to_english('बुखार और खांसी', source_lang='hi')
    assert translated in {'cough', 'fever'}


def test_process_input_english_returns_lowercase():
    processor = MultilingualProcessor()
    result = processor.process_input('I have a headache')
    assert result['language'] == 'en'
    assert result['language_name'] == 'English'
    assert result['translated_text'] == 'I have a headache'.lower()


def test_greeting_and_disclaimer_supported_languages():
    processor = MultilingualProcessor()
    assert processor.get_greeting('kn').startswith('ನಮಸ್ಕಾರ')
    assert 'चिकित्सा' in processor.get_disclaimer('hi')
