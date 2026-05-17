"""
diet_advice.py - Diet recommendations for various health conditions
"""

DIET_ADVICE = {
    'Fungal infection': {
        'eat': ['Probiotic-rich foods (yogurt, kefir, sauerkraut)', 'Garlic and onions (antifungal properties)', 'Coconut oil', 'Ginger', 'Low-sugar fruits'],
        'avoid': ['Sugar and refined carbohydrates', 'Alcohol', 'Processed foods', 'Excessive fruit juice']
    },
    'Allergy': {
        'eat': ['Quercetin-rich foods (apples, berries, broccoli)', 'Vitamin C rich foods', 'Omega-3 fatty acids (fish, flaxseed)', 'Local honey (may help seasonal allergies)'],
        'avoid': ['Known allergens', 'Processed foods with additives', 'Alcohol (can worsen symptoms)']
    },
    'GERD': {
        'eat': ['Oatmeal', 'Ginger', 'Lean proteins', 'Vegetables (except onions, tomatoes, peppers)', 'Non-citrus fruits'],
        'avoid': ['Spicy foods', 'Citrus fruits', 'Tomatoes', 'Chocolate', 'Caffeine', 'Alcohol', 'Fatty foods']
    },
    'Chronic cholestasis': {
        'eat': ['High-fiber foods', 'Lean proteins', 'Fruits and vegetables', 'Healthy fats (avocado, olive oil)'],
        'avoid': ['Fried foods', 'Processed meats', 'Full-fat dairy', 'Alcohol', 'Refined sugars']
    },
    'Drug Reaction': {
        'eat': ['Hydrating fluids', 'Simple bland foods (if gastrointestinal symptoms)', 'Foods rich in antioxidants'],
        'avoid': ['Alcohol', 'Any suspected drug or similar compounds']
    },
    'Peptic ulcer diseae': {
        'eat': ['High-fiber foods', 'Probiotic foods (yogurt, kefir)', 'Lean proteins', 'Flavonoid-rich foods (apples, celery, cranberries)'],
        'avoid': ['Spicy foods', 'Citrus fruits', 'Tomatoes', 'Alcohol', 'Caffeine', 'Fried foods']
    },
    'AIDS': {
        'eat': ['High-protein foods (lean meat, eggs, legumes)', 'Fruits and vegetables', 'Whole grains', 'Healthy fats'],
        'avoid': ['Raw or undercooked eggs/meat', 'Unpasteurized dairy', 'Foods that risk foodborne illness']
    },
    'Diabetes': {
        'eat': ['Non-starchy vegetables', 'Whole grains in moderation', 'Lean proteins', 'Healthy fats', 'Low-glycemic index fruits'],
        'avoid': ['Sugary beverages', 'Refined grains', 'Processed snacks', 'High-glycemic index foods']
    },
    'Gastroenteritis': {
        'eat': ['BRAT diet (Bananas, Rice, Applesauce, Toast)', 'Plain crackers', 'Potatoes', 'Electrolyte-rich fluids'],
        'avoid': ['Dairy products', 'Fatty foods', 'Spicy foods', 'Caffeine', 'Alcohol']
    },
    'Bronchial Asthma': {
        'eat': ['Vitamin D rich foods', 'Magnesium rich foods (spinach, pumpkin seeds)', 'Omega-3 fatty acids', 'Antioxidant-rich fruits and vegetables'],
        'avoid': ['Sulfites (dried fruits, wine)', 'Processed foods', 'Known food triggers']
    },
    'Hypertension': {
        'eat': ['Leafy greens', 'Berries', 'Beets', 'Oats', 'Bananas', 'Fish rich in omega-3', 'Seeds (pumpkin, sunflower)'],
        'avoid': ['Salt', 'Processed foods', 'Canned soups', 'Pickles', 'Alcohol', 'Red meat']
    },
    'Migraine': {
        'eat': ['Magnesium-rich foods (spinach, nuts, seeds)', 'Omega-3 fatty acids', 'Hydration', 'Ginger'],
        'avoid': ['Aged cheeses', 'Processed meats (nitrates)', 'Alcohol (especially red wine)', 'Chocolate', 'Caffeine', 'Artificial sweeteners']
    },
    'Cervical spondylosis': {
        'eat': ['Calcium-rich foods (dairy, leafy greens)', 'Vitamin D rich foods', 'Omega-3 fatty acids', 'Collagen-rich foods (bone broth)'],
        'avoid': ['Inflammatory foods (fried, processed)', 'Excessive caffeine', 'Alcohol']
    },
    'Paralysis (brain hemorrhage)': {
        'eat': ['High-protein foods for healing', 'Fruits and vegetables', 'Whole grains', 'Healthy fats'],
        'avoid': ['High-sodium foods', 'Processed foods', 'Saturated fats']
    },
    'Jaundice': {
        'eat': ['Fresh fruits and vegetables', 'Lean proteins', 'Whole grains', 'Plenty of water', 'Herbal teas'],
        'avoid': ['Alcohol', 'Fried foods', 'Processed foods', 'Refined sugars', 'Fatty foods']
    },
    'Malaria': {
        'eat': ['Easy-to-digest foods', 'Fruits rich in vitamin C', 'Proteins', 'Plenty of fluids'],
        'avoid': ['Fried foods', 'Spicy foods', 'Processed foods', 'Caffeine']
    },
    'Chicken pox': {
        'eat': ['Soft foods', 'Cold foods to soothe mouth', 'Fruits and vegetables', 'Hydration'],
        'avoid': ['Spicy foods', 'Acidic foods', 'Crunchy foods']
    },
    'Dengue': {
        'eat': ['Hydrating fluids (water, coconut water, electrolyte drinks)', 'Easy-to-digest foods', 'Fruits and vegetables', 'Proteins'],
        'avoid': ['Oily/fried foods', 'Spicy foods', 'Caffeine', 'Alcohol']
    },
    'Typhoid': {
        'eat': ['High-calorie foods', 'Soft foods', 'Carbohydrates', 'Proteins', 'Fluids'],
        'avoid': ['High-fiber foods initially', 'Spicy foods', 'Fatty foods']
    },
    'hepatitis A': {
        'eat': ['High-calorie foods', 'Proteins', 'Fruits and vegetables', 'Plenty of fluids'],
        'avoid': ['Alcohol', 'Fatty foods', 'Processed foods']
    },
    'Hepatitis B': {
        'eat': ['Balanced diet', 'Fruits and vegetables', 'Whole grains', 'Lean proteins'],
        'avoid': ['Alcohol', 'Processed foods', 'Saturated fats']
    },
    'Hepatitis C': {
        'eat': ['Fruits and vegetables', 'Whole grains', 'Lean proteins', 'Healthy fats'],
        'avoid': ['Alcohol', 'Processed foods', 'Saturated fats']
    },
    'Hepatitis D': {
        'eat': ['Balanced diet', 'Fruits and vegetables', 'Whole grains', 'Lean proteins'],
        'avoid': ['Alcohol', 'Processed foods', 'Saturated fats']
    },
    'Hepatitis E': {
        'eat': ['Easy-to-digest foods', 'Fruits and vegetables', 'Proteins', 'Plenty of fluids'],
        'avoid': ['Alcohol', 'Fatty foods', 'Spicy foods']
    },
    'Alcoholic hepatitis': {
        'eat': ['High-protein foods', 'Fruits and vegetables', 'Whole grains', 'Plenty of fluids'],
        'avoid': ['Alcohol', 'Fatty foods', 'Processed foods', 'Excessive salt']
    },
    'Tuberculosis': {
        'eat': ['High-protein foods', 'Calorie-dense foods', 'Fruits and vegetables', 'Whole grains', 'Healthy fats'],
        'avoid': ['Processed foods', 'Excessive alcohol', 'Refined sugars']
    },
    'Common Cold': {
        'eat': ['Warm fluids (herbal tea, broth)', 'Vitamin C rich foods', 'Honey', 'Garlic', 'Soups'],
        'avoid': ['Processed foods', 'Sugary foods', 'Dairy (may increase mucus for some)']
    },
    'Pneumonia': {
        'eat': ['High-protein foods', 'Warm soups', 'Fruits and vegetables', 'Whole grains', 'Plenty of fluids'],
        'avoid': ['Processed foods', 'Fried foods', 'Excessive sugar']
    },
    'Dimorphic hemmorhoids(piles)': {
        'eat': ['High-fiber foods (whole grains, fruits, vegetables)', 'Plenty of water'],
        'avoid': ['Low-fiber foods', 'Processed foods', 'Spicy foods']
    },
    'Heart attack': {
        'eat': ['Fruits and vegetables', 'Whole grains', 'Lean proteins', 'Healthy fats (olive oil, nuts)', 'Omega-3 rich fish'],
        'avoid': ['Saturated fats', 'Trans fats', 'Excessive salt', 'Sugar', 'Processed meats']
    },
    'Varicose veins': {
        'eat': ['High-fiber foods', 'Flavonoid-rich foods (citrus, berries, onions)', 'Potassium-rich foods'],
        'avoid': ['High-sodium foods', 'Processed foods', 'Excessive alcohol']
    },
    'Hypothyroidism': {
        'eat': ['Iodine-rich foods (seaweed, fish, dairy)', 'Selenium-rich foods (Brazil nuts, sunflower seeds)', 'Zinc-rich foods', 'Fiber'],
        'avoid': ['Goitrogenic foods in excess (raw cruciferous vegetables)', 'Soy products', 'Gluten (if sensitive)']
    },
    'Hyperthyroidism': {
        'eat': ['Calcium and vitamin D rich foods', 'Protein-rich foods', 'Berries'],
        'avoid': ['Iodine-rich foods in excess', 'Stimulants (caffeine)', 'Processed foods']
    },
    'Hypoglycemia': {
        'eat': ['Complex carbohydrates', 'Protein with carbs', 'Healthy fats', 'Regular small meals'],
        'avoid': ['Simple sugars', 'Refined grains', 'Skipping meals']
    },
    'Osteoarthristis': {
        'eat': ['Omega-3 fatty acids', 'Vitamin C rich foods', 'Antioxidants', 'Collagen-rich foods'],
        'avoid': ['Processed foods', 'Excessive sugar', 'Fried foods', 'High-sodium foods']
    },
    'Arthritis': {
        'eat': ['Omega-3 rich fish', 'Fruits and vegetables', 'Whole grains', 'Spices (turmeric, ginger)'],
        'avoid': ['Processed foods', 'Red meat', 'Dairy (for some)', 'Nightshade vegetables (if sensitive)']
    },
    '(vertigo) Paroymsal  Positional Vertigo': {
        'eat': ['Hydrating fluids', 'Low-sodium foods', 'Fruits and vegetables'],
        'avoid': ['High-sodium foods', 'Caffeine', 'Alcohol', 'Processed foods']
    },
    'Acne': {
        'eat': ['Low-glycemic foods', 'Zinc-rich foods', 'Omega-3 fatty acids', 'Antioxidant-rich foods'],
        'avoid': ['High-glycemic foods', 'Dairy (for some)', 'Fried foods', 'Processed foods']
    },
    'Urinary tract infection': {
        'eat': ['Cranberries (unsweetened)', 'Blueberries', 'Probiotic foods', 'Plenty of water', 'Vitamin C rich foods'],
        'avoid': ['Caffeine', 'Alcohol', 'Spicy foods', 'Artificial sweeteners']
    },
    'Psoriasis': {
        'eat': ['Anti-inflammatory foods (fatty fish, leafy greens)', 'Antioxidant-rich foods', 'Vitamin D'],
        'avoid': ['Alcohol', 'Processed foods', 'Red meat', 'Dairy (for some)', 'Nightshade vegetables']
    },
    'Impetigo': {
        'eat': ['Protein-rich foods', 'Fruits and vegetables', 'Plenty of fluids'],
        'avoid': ['Sugary foods', 'Processed foods']
    }
}

def get_diet_advice(condition):
    """
    Return diet advice for a given condition.
    If condition not found, return generic advice.
    """
    return DIET_ADVICE.get(condition, {
        'eat': ['Balanced diet with plenty of fruits and vegetables'],
        'avoid': ['Processed foods, excessive sugar and unhealthy fats']
    })