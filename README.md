# Smart Health Advisory & Medicine Reminder System

AI-Powered Symptom Guidance with Multilingual Support & Smart Medicine Reminders

## Project Overview

An intelligent, low-cost, accessible system that offers safe, non-prescriptive health guidance based on entered symptoms, provides timely medicine reminders, and communicates in regional languages (English, Hindi, Kannada).

## Team
- **Institution:** Malnad College of Engineering, Hassan
- **Course:** Interdisciplinary Project Work (CSE + Robotics & AI)
- **Academic Year:** 2025-2026 Semester II
- **Team Size:** 6 Members

## Features

1. **🩺 AI-Powered Symptom Analysis** - ML-powered disease prediction across 41 conditions and 132 symptoms.
2. **🌐 Multilingual Support** - English, Hindi, and Kannada (auto-detected and translated).
3. **🎤 Voice Input** - Hands-free symptom entry via speech recognition (with file upload fallback).
4. **💊 Smart Medicine Reminders** - Persistent scheduling backed by SQLite. Includes an active alarm system that triggers browser chimes, visual banners, and system notifications when it's time to take your medicine.
5. **📊 Live Health Dashboard** - Tracks medication adherence with an animated donut chart and KPIs for taken/missed/scheduled doses.
6. **🥗 Diet Planner** - Condition-specific nutritional guidance (what to eat and avoid) based on predicted diseases.
7. **📅 Doctor Finder** - Local doctor search integration with Google Maps.
8. **🔒 Privacy-First** - All data is stored locally with zero cloud tracking.
9. **✨ Beautiful Streamlit UI** - Responsive, mobile-friendly interface with quick-select symptom chips and animated scan-lines.

## Technology Stack

- Python 3.x
- scikit-learn (BernoulliNB, RandomForest, LogisticRegression with calibrated probabilities)
- NLTK / spaCy (NLP)
- googletrans / IndicNLP (Multilingual)
- SpeechRecognition (Voice)
- Streamlit (UI)
- SQLite (Storage)

## Installation

```bash
# Clone or navigate to project directory
cd health_advisory_system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Running the Application

```bash
streamlit run src/app.py
```

## Running Tests

```bash
pytest
```

## Voice input notes

- The app uses a lightweight RMS-based silence detector to auto-stop voice recording by default. This avoids extra native dependencies and works across platforms.
- If you prefer WebRTC VAD for higher accuracy, you can install it manually (requires build tools on Windows):

```powershell
# Option 1 (recommended on Windows): install Visual C++ Build Tools, then
pip install webrtcvad
# Option 2 (conda):
conda install -c conda-forge webrtcvad
```

After installing `webrtcvad`, you can adjust the VAD settings in the app UI if you later enable it.

## Retraining the Model

The training pipeline now selects the best model using weighted F1 and calibrates probabilities for safer real-world predictions.

```bash
cd health_advisory_system
venv\Scripts\activate
python -m pip install -r requirements.txt
python src/train_model.py
```

This keeps the model artifacts current in:
- `src/disease_model.pkl`
- `src/symptom_columns.pkl`

After training, launch the app with:

```bash
streamlit run src/app.py
```

## Project Structure

```
health_advisory_system/
├── data/                   # Datasets and database
├── models/                 # Trained ML models
├── src/                    # Source code
│   ├── app.py              # Main Streamlit application
│   ├── config.py           # Configuration settings
│   ├── analyser.py         # AI symptom classifier
│   ├── multilingualprocessor.py # Translation module
│   ├── voice_input.py      # Speech recognition
│   └── reminder_system.py  # Medicine reminders
├── tests/                  # Unit tests
├── docs/                   # Documentation
└── requirements.txt        # Dependencies
```

## Ethical Boundaries

- Never prescribes medicines or suggests dosage
- Never replaces professional medical consultation
- Provides only general health advice (rest, hydration, diet tips)
- Recommends seeking medical attention when appropriate

## License

Academic Project - Malnad College of Engineering
