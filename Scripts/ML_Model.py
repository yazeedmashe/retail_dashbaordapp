import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import sqlite3
from sklearn.model_selection import cross_val_score

# Load data
db = sqlite3.connect(r"Database/retail_analytics.db")
df = pd.read_sql('SELECT price, cost_price, quantity, brand, category, profitability, region, month, quarter, weekday FROM cleaned_data', db)

# Features & Target
X = df.drop('Profitability', axis=1)
y = df['Profitability']

# One-hot encoding for categorical features
X = pd.get_dummies(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model
model = RandomForestClassifier(max_depth=10, min_samples_leaf=5, random_state=42)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluation
print("Training Accuracy:", model.score(X_train, y_train))
print("Test Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
scores = cross_val_score(model, X, y, cv=5)
print(scores.mean())