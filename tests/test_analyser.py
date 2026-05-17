import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from analyser import _map_to_columns, analyse_symptoms


def test_map_to_columns_translates_symptoms():
    matched = _map_to_columns('I have chest pain and high fever')
    assert 'chest_pain' in matched
    assert 'high_fever' in matched


def test_analyse_symptoms_returns_expected_structure():
    result = analyse_symptoms('I have a high fever')
    assert isinstance(result, dict)
    assert 'disease' in result
    assert 'advice' in result
    assert 'matched' in result
    assert result['language'] == 'English'
    assert 'high_fever' in result['matched']
    assert 'confidence' in result
    assert isinstance(result['confidence'], float)
    assert 0.0 <= result['confidence'] <= 1.0
    assert 'top_predictions' in result
    assert isinstance(result['top_predictions'], list)
    # New: analyzer provides an explanation list for transparency
    assert 'explanation' in result
    assert isinstance(result['explanation'], list)
