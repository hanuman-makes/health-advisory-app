"""Check if all dependencies are installed correctly."""

import sys

def check_import(module_name, package_name=None):
    """Try to import a module and report status."""
    if package_name is None:
        package_name = module_name
    try:
        __import__(module_name)
        print(f"[OK] {package_name}")
        return True
    except ImportError as e:
        print(f"[FAIL] {package_name} - {e}")
        return False

def main():
    """Check all dependencies."""

    print("=" * 60)
    print("HEALTH ADVISORY SYSTEM - Setup Check")
    print("=" * 60)

    required = [
        ('streamlit', 'Streamlit'),
        ('sklearn', 'scikit-learn'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('nltk', 'NLTK'),
        ('speech_recognition', 'SpeechRecognition'),
        ('matplotlib', 'Matplotlib'),
        ('seaborn', 'seaborn'),
        ('sqlite3', 'SQLite3 (builtin)'),
    ]

    optional = [
        ('spacy', 'spaCy (optional)'),
        ('googletrans', 'googletrans (optional)'),
    ]

    print("\nChecking Python dependencies...")
    print("-" * 40)

    all_ok = True
    for module, package in required:
        if not check_import(module, package):
            all_ok = False

    print("\nOptional dependencies (not required for basic functionality)...")
    print("-" * 40)
    for module, package in optional:
        check_import(module, package)

    # Check NLTK data
    print("\nChecking NLTK data...")
    print("-" * 40)
    try:
        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
            print("[OK] punkt tokenizer")
        except LookupError:
            print("[FAIL] punkt tokenizer - run: nltk.download('punkt')")
            all_ok = False

        try:
            nltk.data.find('corpora/stopwords')
            print("[OK] stopwords")
        except LookupError:
            print("[FAIL] stopwords - run: nltk.download('stopwords')")
            all_ok = False
    except:
        pass

    # Check directory structure
    print("\nChecking directory structure...")
    print("-" * 40)

    import os
    dirs = ['data', 'models', 'src', 'tests', 'docs']
    for d in dirs:
        if os.path.exists(d):
            print(f"[OK] {d}/")
        else:
            print(f"[FAIL] {d}/ - Missing")
            all_ok = False

    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("[OK] All checks passed! You're ready to go.")
        print("\nRun the application with:")
        print("  streamlit run src/app_final3.py")
    else:
        print("[FAIL] Some checks failed. Please install missing dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
