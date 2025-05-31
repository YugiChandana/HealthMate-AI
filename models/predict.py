import pandas as pd
import joblib

# Load all models once
models = {}
diseases = [
    'Diagnosed_diabetes', 'Risk_anxiety', 'Risk_depression', 'Risk_obesity',
    'Risk_asthma', 'Risk_migraine', 'Risk_tb', 'Risk_cancer',
    'Risk_heart_disease', 'Risk_stress_burnout'
]

for disease in diseases:
    models[disease] = joblib.load(f"{disease}_rf_model.joblib")

def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

def predict_health_risks(user_data):
    # Prepare feature dict for the model
    # Provide default values for any missing combined or dropped features
    input_features = {
        'Age': user_data.get('Age', 30),
        'Gender': user_data.get('Gender', 0),  # 0=Male,1=Female
        'BMI': user_data.get('BMI', calculate_bmi(user_data.get('Weight_kg', 70), user_data.get('Height_cm', 170))),
        'Sleep_hours': user_data.get('Sleep_hours', 7),
        'Physical_activity_mins': user_data.get('Exercise_freq', 0) * 30,  # assuming 30 mins per freq
        'Water_intake_liters': user_data.get('Water_intake_liters', 2),
        'Screen_time_hrs': 0,  # Removed, so default 0
        'Stress_level': 0,     # Removed, so default 0
        'Work_study_pressure': 0,  # Removed, so default 0
        'Junk_food_per_week': user_data.get('Junk_food_per_week', 0),
        'Fruit_veggies_per_day': user_data.get('Fruit_veggies_per_day', 3),
        'Social_interaction_hrs': 0,  # Removed, default 0
        'Family_history': user_data.get('Family_history', 0),
    }

    # Create DataFrame with columns matching training data feature order
    feature_order = [
        'Age', 'Gender', 'BMI', 'Sleep_hours', 'Physical_activity_mins',
        'Water_intake_liters', 'Screen_time_hrs', 'Stress_level',
        'Work_study_pressure', 'Junk_food_per_week', 'Fruit_veggies_per_day',
        'Social_interaction_hrs', 'Family_history'
    ]

    input_df = pd.DataFrame([input_features], columns=feature_order)

    results = {}
    for disease, model in models.items():
        proba = model.predict_proba(input_df)[:, 1][0] * 100  # risk percentage
        risk_label = "⚠️" if proba >= 20 else "✅"  # example threshold
        results[disease] = (risk_label, proba)

    return results


if __name__ == "__main__":
    # Test input example (you can modify this)
    test_input = {
        'Age': 54,
        'Gender': 1,  # Female
        'Height_cm': 165,
        'Weight_kg': 90,
        'Sleep_hours': 6,
        'Exercise_freq': 0,
        'Water_intake_liters': 1,
        'Junk_food_per_week': 5,
        'Fruit_veggies_per_day': 1,
        'Family_history': 0,
    }
    test_input['BMI'] = calculate_bmi(test_input['Weight_kg'], test_input['Height_cm'])

    predictions = predict_health_risks(test_input)
    for disease, (label, prob) in predictions.items():
        print(f"{disease}: {label} {prob:.2f}%")

