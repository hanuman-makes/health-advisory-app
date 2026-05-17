# analyser.py - The main logic for symptom analysis
import pickle
import numpy as np
import pandas as pd
import os
from advice_data import ADVICE, DEFAULT_ADVICE
from multilingualprocessor import MultilingualProcessor

lang_processor = MultilingualProcessor()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    model   = pickle.load(open(os.path.join(BASE_DIR, 'disease_model.pkl'),   'rb'))
    columns = pickle.load(open(os.path.join(BASE_DIR, 'symptom_columns.pkl'), 'rb'))
except FileNotFoundError:
    print("Error: Model files not found in src folder!")
    model   = None
    columns = []

# ── Synonym / alias map ────────────────────────────────────────────────────────
# Maps everyday words → exact model column names.
# Longest phrases matched first so "chest pain" beats bare "pain".
SYNONYM_MAP = {
    # Fever
    'high fever':             'high_fever',
    'mild fever':             'mild_fever',
    'fever':                  'high_fever',
    'temperature':            'high_fever',
    'pyrexia':                'high_fever',
    # Respiratory
    'shortness of breath':    'breathlessness',
    'short of breath':        'breathlessness',
    'difficulty breathing':   'breathlessness',
    'breathless':             'breathlessness',
    'sore throat':            'throat_irritation',
    'throat irritation':      'throat_irritation',
    'runny nose':             'runny_nose',
    'continuous sneezing':    'continuous_sneezing',
    'sneezing':               'continuous_sneezing',
    'phlegm':                 'phlegm',
    'mucus':                  'phlegm',
    'blood in sputum':        'blood_in_sputum',
    'rusty sputum':           'rusty_sputum',
    # Pain (compound first, never bare 'pain')
    'chest pain':             'chest_pain',
    'back pain':              'back_pain',
    'neck pain':              'neck_pain',
    'knee pain':              'knee_pain',
    'hip pain':               'hip_joint_pain',
    'joint pain':             'joint_pain',
    'muscle pain':            'muscle_pain',
    'stomach pain':           'stomach_pain',
    'stomach ache':           'stomach_pain',
    'tummy ache':             'stomach_pain',
    'belly pain':             'belly_pain',
    'abdominal pain':         'abdominal_pain',
    'pain behind eyes':       'pain_behind_the_eyes',
    'pain behind the eyes':   'pain_behind_the_eyes',
    'head ache':              'headache',
    # Skin
    'skin rash':              'skin_rash',
    'red spots':              'red_spots_over_body',
    'yellow skin':            'yellowish_skin',
    'yellowish skin':         'yellowish_skin',
    'yellow eyes':            'yellowing_of_eyes',
    'skin peeling':           'skin_peeling',
    'pus filled pimples':     'pus_filled_pimples',
    'pimples':                'pus_filled_pimples',
    'acne':                   'pus_filled_pimples',
    'silver like dusting':    'silver_like_dusting',
    # GI / Digestive
    'loose motions':          'diarrhoea',
    'loose stools':           'diarrhoea',
    'loose stool':            'diarrhoea',
    'diarrhea':               'diarrhoea',
    'loss of appetite':       'loss_of_appetite',
    'no appetite':            'loss_of_appetite',
    'weight loss':            'weight_loss',
    'weight gain':            'weight_gain',
    'dark urine':             'dark_urine',
    'yellow urine':           'yellow_urine',
    'burning urination':      'burning_micturition',
    'burning when urinating': 'burning_micturition',
    'frequent urination':     'continuous_feel_of_urine',
    'jaundice':               ['yellowish_skin', 'yellowing_of_eyes', 'dark_urine'],
    # Neurological / General
    'blurred vision':         'blurred_and_distorted_vision',
    'visual disturbance':     'visual_disturbances',
    'tired':                  'fatigue',
    'tiredness':              'fatigue',
    'weak':                   'fatigue',
    'weakness':               'weakness_in_limbs',
    'muscle weakness':        'muscle_weakness',
    'dizzy':                  'dizziness',
    'stiff neck':             'stiff_neck',
    'loss of balance':        'loss_of_balance',
    'spinning':               'spinning_movements',
    'slurred speech':         'slurred_speech',
    'palpitation':            'palpitations',
    'fast heart rate':        'fast_heart_rate',
    'fast heart':             'fast_heart_rate',
    'sweat':                  'sweating',
    'cold hands':             'cold_hands_and_feets',
    'cold feet':              'cold_hands_and_feets',
    'swollen legs':           'swollen_legs',
    'swollen lymph':          'swelled_lymph_nodes',
    'enlarged thyroid':       'enlarged_thyroid',
    'migraine':               'headache',
}

# Conditions that require conservative handling in low-evidence cases.
# Map disease name -> list of indicator symptom columns that make the prediction more credible.
SEVERE_CONDITIONS_INDICATORS = {
    'AIDS': [
        'weight_loss', 'swelled_lymph_nodes', 'continuous_fever',
        'chronic_cough', 'night_sweats', 'loss_of_appetite'
    ],
    'Heart attack': ['chest_pain', 'sweating', 'fast_heart_rate', 'cold_hands_and_feets'],
    'Paralysis (brain hemorrhage)': ['stiff_neck', 'slurred_speech', 'loss_of_balance']
}

FILLERS = [
    'i have been having', 'i have been', 'i am having', 'i am feeling',
    'i have', 'i feel', 'i am',
    'since yesterday', 'since last', 'since', 'for the past', 'past few',
    'days', 'hours', 'week', 'weeks', 'months',
    'with some', 'with a', 'with', 'some', 'little', 'lot of',
    'a bit of', 'bit of', 'slight', 'slightly', 'very', 'also',
    'and', 'the', 'my', 'me',
]

def _clean(text):
    t = text.lower().strip()
    for filler in sorted(FILLERS, key=len, reverse=True):
        t = t.replace(filler, ' ')
    return ' '.join(t.split())

def _map_to_columns(text):
    t = _clean(text)
    matched = set()
    # 1. Multi-word phrase matching (longest first)
    for phrase in sorted(SYNONYM_MAP.keys(), key=len, reverse=True):
        if phrase in t:
            target = SYNONYM_MAP[phrase]
            if isinstance(target, list):
                for col in target:
                    if col in columns: matched.add(col)
            else:
                if target in columns: matched.add(target)
            t = t.replace(phrase, ' ')
    # 2. Single-token exact match against model columns
    for token in t.split():
        clean_tok = token.strip('.,!?;:').replace('-', '_')
        if clean_tok in columns:
            matched.add(clean_tok)
    return list(matched)


def _normalize_disease_name(name):
    return name.strip() if isinstance(name, str) else name


def analyse_symptoms(symptom_text):
    if model is None or not columns:
        return {'disease': 'Unknown', 'advice': DEFAULT_ADVICE, 'matched': []}

    # Translate Hindi/Kannada → English
    lang_data    = lang_processor.process_input(symptom_text)
    english_text = lang_data['translated_text']

    # Map to model columns
    matched = _map_to_columns(english_text)

    if not matched:
        return {
            'disease':  'Unknown',
            'advice':   DEFAULT_ADVICE,
            'matched':  [],
            'language': lang_data.get('language_name', 'English'),
        }

    # Build DataFrame so sklearn uses column names (not positional order)
    row = {col: 0 for col in columns}
    for sym in matched:
        row[sym] = 1
    df = pd.DataFrame([row], columns=columns)

    prediction = _normalize_disease_name(model.predict(df)[0])
    advice     = ADVICE.get(prediction, DEFAULT_ADVICE)

    confidence = None
    top_predictions = []
    low_confidence = False
    explanation = []
    if hasattr(model, 'predict_proba'):
        try:
            probs = model.predict_proba(df)[0]
            prob_pairs = sorted(
                [(_normalize_disease_name(name), score) for name, score in zip(model.classes_, probs)],
                key=lambda x: x[1], reverse=True
            )
            confidence = float(prob_pairs[0][1])
            top_predictions = [
                {'disease': name, 'confidence': float(score)}
                for name, score in prob_pairs[:3]
            ]
            second_best = prob_pairs[1][1] if len(prob_pairs) > 1 else 0.0
            # Basic thresholds: require a reasonably high top probability and a gap
            low_confidence = confidence < 0.60 or (confidence - second_best) < 0.15

            # Extra safety: if top prediction is a severe condition, ensure indicator
            # symptoms are present; otherwise mark low confidence and prefer safer alternatives
            top_name = prob_pairs[0][0]
            indicators = SEVERE_CONDITIONS_INDICATORS.get(top_name)
            if indicators:
                present_indicators = [s for s in indicators if s in matched]
                if not present_indicators:
                    explanation.append(
                        f"Top prediction '{top_name}' lacks specific indicator symptoms; treating as low-confidence"
                    )
                    low_confidence = True

                    safer_suggestion = None
                    safer_score = None
                    for name, score in prob_pairs[1:]:
                        if name not in SEVERE_CONDITIONS_INDICATORS:
                            safer_suggestion = name
                            safer_score = score
                            break
                    if safer_suggestion:
                        explanation.append(
                            f"Choosing safer alternative '{safer_suggestion}' instead of severe '{top_name}'"
                        )
                        prediction = safer_suggestion
                        advice = ADVICE.get(prediction, DEFAULT_ADVICE)
                        confidence = float(safer_score)
                        reordered = [{'disease': prediction, 'confidence': float(safer_score)}]
                        for name, score in prob_pairs:
                            if name == prediction:
                                continue
                            reordered.append({'disease': name, 'confidence': float(score)})
                            if len(reordered) >= 3:
                                break
                        top_predictions = reordered
                else:
                    explanation.append(f"Indicator symptoms for {top_name} present: {present_indicators}")
        except Exception:
            confidence = None
            top_predictions = []
            low_confidence = False

    return {
        'disease':        prediction,
        'advice':         advice,
        'matched':        matched,
        'language':       lang_data.get('language_name', 'English'),
        'confidence':     confidence,
        'top_predictions': top_predictions,
        'low_confidence': low_confidence,
        'explanation':    explanation,
    }
