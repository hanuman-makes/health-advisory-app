"""Train the symptom analysis model."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import SymptomDatasetLoader
from symptom_analyzer import SymptomAnalyzer
from config import MODEL_TYPE, TEST_SIZE, RANDOM_STATE, TARGET_F1_SCORE

def main():
    """Train and evaluate the symptom classifier."""

    print("=" * 60)
    print("HEALTH ADVISORY SYSTEM - Model Training")
    print("=" * 60)

    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    models_dir = os.path.join(base_dir, "models")

    # Ensure directories exist
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    # Load dataset
    print("\n[1/4] Loading dataset...")
    loader = SymptomDatasetLoader(data_dir)
    df = loader.load_dataset()
    print(f"✓ Loaded {len(df)} records")

    # Preprocess
    print("\n[2/4] Preprocessing symptoms...")
    X, y, symptom_list = loader.preprocess_symptoms(df)
    print(f"✓ Features: {X.shape[1]} symptoms")
    print(f"✓ Classes: {len(loader.label_encoder.classes_)} diseases")

    # Train model
    print(f"\n[3/4] Training {MODEL_TYPE} classifier...")
    analyzer = SymptomAnalyzer(model_type=MODEL_TYPE, models_dir=models_dir)
    result = analyzer.train(X, y, symptom_list, loader.label_encoder)

    # Evaluate
    print(f"\n[4/4] Evaluation Results:")
    print(f"  F1-Score: {result['f1_score']:.4f}")
    print(f"  Target: {TARGET_F1_SCORE}")

    if result['f1_score'] >= TARGET_F1_SCORE:
        print(f"  ✓ Model meets target performance!")
    else:
        print(f"  ⚠ Model below target. Consider adding more training data.")

    print("\n" + "=" * 60)
    print("Model training complete!")
    print(f"Model saved to: {os.path.join(models_dir, 'symptom_classifier.pkl')}")
    print("\nTo run the application:")
    print("  streamlit run src/app_final3.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
