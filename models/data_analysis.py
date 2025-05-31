import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('healthmate_10_disease_dataset.csv')

# Age distribution
plt.figure(figsize=(8,6))
sns.histplot(df['Age'], bins=20, kde=True, color='skyblue')
plt.title('Age Distribution')
plt.xlabel('Age')
plt.ylabel('Count')
plt.savefig('age_distribution.png')

# BMI distribution
plt.figure(figsize=(8,6))
sns.histplot(df['BMI'], bins=20, kde=True, color='salmon')
plt.title('BMI Distribution')
plt.xlabel('BMI')
plt.ylabel('Count')
plt.savefig('bmi_distribution.png')

print("✅ Saved plots: age_distribution.png, bmi_distribution.png")

