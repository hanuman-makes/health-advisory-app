"""
followup_questions.py - Defines follow-up questions for specific symptoms
"""

# Mapping from symptom column name to list of questions
# Each question is a tuple (question_text, input_type, optional_unit)
# input_type: 'text', 'number', 'select'
FOLLOWUP_QUESTIONS = {
    'high_fever': [
        ("For how many days have you had fever?", "number", "days"),
        ("What is your highest temperature reading?", "number", "°C"),
    ],
    'mild_fever': [
        ("For how many days have you had fever?", "number", "days"),
        ("What is your highest temperature reading?", "number", "°C"),
    ],
    'cough': [
        ("How long have you had this cough?", "text", "e.g., 3 days"),
        ("Is the cough dry or with phlegm?", "select", ["Dry", "With phlegm"]),
    ],
    'headache': [
        ("How long have you had this headache?", "text", "e.g., 2 days"),
        ("On a scale of 1-10, how severe is the headache?", "number", "severity (1-10)"),
    ],
    'fatigue': [
        ("How long have you felt fatigued?", "text", "e.g., 1 week"),
        ("Does fatigue affect your daily activities?", "select", ["Not at all", "Slightly", "Moderately", "Severely"]),
    ],
    'breathlessness': [
        ("When do you feel breathless?", "select", ["During exertion", "At rest", "Both"]),
        ("Do you experience difficulty breathing when lying flat?", "select", ["No", "Yes"]),
    ],
    'diarrhoea': [
        ("How many times per day do you have loose stools?", "number", "times per day"),
        ("Is there blood in your stool?", "select", ["No", "Yes"]),
    ],
    'vomiting': [
        ("How many times per day have you vomited?", "number", "times per day"),
        ("Are you able to keep liquids down?", "select", ["No", "Yes"]),
    ],
    # Generic pain symptoms
    'chest_pain': [
        ("How long have you had chest pain?", "text", "e.g., 2 hours"),
        ("On a scale of 1-10, how severe is the pain?", "number", "severity (1-10)"),
    ],
    'back_pain': [
        ("How long have you had back pain?", "text", "e.g., 3 days"),
        ("On a scale of 1-10, how severe is the pain?", "number", "severity (1-10)"),
    ],
    'stomach_pain': [
        ("How long have you had stomach pain?", "text", "e.g., 1 day"),
        ("On a scale of 1-10, how severe is the pain?", "number", "severity (1-10)"),
    ],
    'joint_pain': [
        ("How long have you had joint pain?", "text", "e.g., 2 weeks"),
        ("On a scale of 1-10, how severe is the pain?", "number", "severity (1-10)"),
    ],
    'muscle_pain': [
        ("How long have you had muscle pain?", "text", "e.g., 5 days"),
        ("On a scale of 1-10, how severe is the pain?", "number", "severity (1-10)"),
    ],
    'neck_pain': [
        ("How long have you had neck pain?", "text", "e.g., 3 days"),
        ("On a scale of 1-10, how severe is the pain?", "number", "severity (1-10)"),
    ],
    'hip_joint_pain': [
        ("How long have you had hip joint pain?", "text", "e.g., 1 month"),
        ("On a scale of 1-10, how severe is the pain?", "number", "severity (1-10)"),
    ],
    'knee_pain': [
        ("How long have you had knee pain?", "text", "e.g., 2 weeks"),
        ("On a scale of 1-10, how severe is the pain?", "number", "severity (1-10)"),
    ],
}

def get_followup_questions(symptoms):
    """
    Given a set of symptom column names, return a dict of symptom to its follow-up questions.
    """
    result = {}
    for sym in symptoms:
        if sym in FOLLOWUP_QUESTIONS:
            result[sym] = FOLLOWUP_QUESTIONS[sym]
    return result