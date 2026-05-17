# train_model.py - Train and save the best model for the symptom analyzer
import pickle
from pathlib import Path

import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
TRAIN_PATH = ROOT_DIR / 'Training.csv'
TEST_PATH = ROOT_DIR / 'Testing.csv'
OUTPUT_DIR = BASE_DIR


def load_dataset():
    train_data = pd.read_csv(TRAIN_PATH)
    test_data = pd.read_csv(TEST_PATH)
    train_data = train_data.loc[:, ~train_data.columns.str.contains('^Unnamed')]
    test_data = test_data.loc[:, ~test_data.columns.str.contains('^Unnamed')]
    return train_data, test_data


def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    return {
        'accuracy': accuracy_score(y_test, predictions),
        'f1_weighted': f1_score(y_test, predictions, average='weighted'),
        'report': classification_report(y_test, predictions, zero_division=0),
    }


def main():
    print('=' * 70)
    print('HEALTH ADVISORY SYSTEM - Model Training')
    print('=' * 70)

    print('\n[1/5] Loading dataset...')
    train_data, test_data = load_dataset()
    print(f'✓ Loaded {len(train_data)} training records and {len(test_data)} test records')

    X_train = train_data.drop('prognosis', axis=1)
    y_train = train_data['prognosis']
    X_test = test_data.drop('prognosis', axis=1)
    y_test = test_data['prognosis']

    print('\n[2/5] Preparing candidate classifiers...')
    candidates = [
        ('RandomForest', RandomForestClassifier(n_estimators=300, random_state=42, class_weight='balanced')),
        ('LogisticRegression', LogisticRegression(max_iter=3000, class_weight='balanced', random_state=42)),
        ('BernoulliNB', BernoulliNB()),
        ('DecisionTree', DecisionTreeClassifier(random_state=42, class_weight='balanced')),
    ]

    best_score = -1.0
    best_name = None
    best_model = None
    model_summary = []

    for name, model in candidates:
        print(f'\n[3/5] Training candidate: {name}')
        model.fit(X_train, y_train)
        scores = evaluate_model(model, X_test, y_test)
        print(f'  Accuracy: {scores["accuracy"]:.4f}, Weighted F1: {scores["f1_weighted"]:.4f}')
        if hasattr(model, 'predict_proba'):
            print('  Calibrating probabilities for better confidence estimates...')
            calibrated = CalibratedClassifierCV(model, cv=5, method='isotonic')
            calibrated.fit(X_train, y_train)
            calibrated_scores = evaluate_model(calibrated, X_test, y_test)
            print(f'  Calibrated Accuracy: {calibrated_scores["accuracy"]:.4f}, Weighted F1: {calibrated_scores["f1_weighted"]:.4f}')
            model = calibrated
            scores = calibrated_scores

        model_summary.append((name, model, scores))

        if scores['f1_weighted'] > best_score:
            best_score = scores['f1_weighted']
            best_name = name
            best_model = model

    print('\n[4/5] Best candidate selection')
    print(f'  Selected model: {best_name} with weighted F1 = {best_score:.4f}')
    print('\n[5/5] Final evaluation on test set')
    final_scores = evaluate_model(best_model, X_test, y_test)
    print(f'  Accuracy: {final_scores["accuracy"]:.4f}')
    print(f'  Weighted F1: {final_scores["f1_weighted"]:.4f}')
    print('\nClassification report:')
    print(final_scores['report'])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model_path = OUTPUT_DIR / 'disease_model.pkl'
    columns_path = OUTPUT_DIR / 'symptom_columns.pkl'

    with open(model_path, 'wb') as model_file:
        pickle.dump(best_model, model_file)

    with open(columns_path, 'wb') as cols_file:
        pickle.dump(list(X_train.columns), cols_file)

    print(f'\nModel artifacts saved to: {model_path} and {columns_path}')
    print('=' * 70)


if __name__ == '__main__':
    main()
