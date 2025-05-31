import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import joblib

# Load dataset
df = pd.read_csv('healthmate_10_disease_dataset.csv')

# Features and targets
features = [
    'Age', 'Gender', 'BMI', 'Sleep_hours', 'Physical_activity_mins',
    'Water_intake_liters', 'Screen_time_hrs', 'Stress_level',
    'Work_study_pressure', 'Junk_food_per_week', 'Fruit_veggies_per_day',
    'Social_interaction_hrs', 'Family_history'
]

targets = [
    'Diagnosed_diabetes', 'Risk_anxiety', 'Risk_depression', 'Risk_obesity',
    'Risk_asthma', 'Risk_migraine', 'Risk_tb', 'Risk_cancer',
    'Risk_heart_disease', 'Risk_stress_burnout'
]

# Encode categorical variables
for col in ['Gender', 'Family_history']:
    df[col] = LabelEncoder().fit_transform(df[col])

for target in targets:
    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    minority_count = y_train.value_counts().min()
    if minority_count < 6:
        # Skip SMOTE if too few minority samples
        X_train_res, y_train_res = X_train, y_train
    else:
        smote = SMOTE(random_state=42, k_neighbors=3)
        X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_res, y_train_res)

    y_pred = model.predict(X_test)

    print(f"\n📍 Disease: {target}")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    print(f"Precision: {precision_score(y_test, y_pred, zero_division=0):.2f}")
    print(f"Recall: {recall_score(y_test, y_pred, zero_division=0):.2f}")

    joblib.dump(model, f"{target}_rf_model.joblib")
    print(f"Saved model to {target}_rf_model.joblib")

