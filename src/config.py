"""Configuration settings for the Health Advisory System."""

import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Dataset URLs
# FIX: removed leading space in dataset name
KAGGLE_DATASET = "symptom-disease"
SYMPTOM_DATASET_PATH = os.path.join(DATA_DIR, "symptom_disease_dataset.csv")

# Model settings
MODEL_TYPE = "decision_tree"  # Options: "decision_tree", "naive_bayes"
TEST_SIZE = 0.2
RANDOM_STATE = 42
TARGET_F1_SCORE = 0.85

# Multilingual settings
SUPPORTED_LANGUAGES = ["en", "hi", "kn"]  # English, Hindi, Kannada
LANGUAGE_NAMES = {"en": "English", "hi": "Hindi", "kn": "Kannada"}

# Medicine reminder settings
# FIX: Use /tmp so the DB works on Streamlit Cloud (read-only filesystem).
# On a local machine this still works fine.  Reminders are ephemeral on cloud
# (lost on restart), which is acceptable for a demo/IDP deployment.
REMINDER_DB_PATH = "/tmp/medisense_reminders.db"
ALERT_SOUND = True

# Safety settings
DISCLAIMER = """
**IMPORTANT MEDICAL DISCLAIMER:**
This system provides general health information only and is NOT a substitute for professional medical advice,
diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with
any questions you may have regarding a medical condition. If you think you may have a medical emergency,
call your doctor or emergency services immediately.
"""

# Severity levels
SEVERITY_LEVELS = {
    "low": "Self-care at home may be sufficient. Monitor symptoms.",
    "medium": "Consider consulting a healthcare provider if symptoms persist or worsen.",
    "high": "Seek medical attention promptly.",
    "emergency": "Seek emergency medical care immediately!"
}