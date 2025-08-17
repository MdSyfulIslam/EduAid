import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler
import joblib

# Load dataset
data = pd.read_csv('static/student_data.csv', sep=';')

# Select features and target for regression
features = ['age', 'studytime', 'failures', 'absences', 'G1', 'G2']
X = data[features]
y = data['G3']  # Predict final grade

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, 'models/scaler.pkl')

# Train regression model
reg_model = LinearRegression()
reg_model.fit(X_scaled, y)
joblib.dump(reg_model, 'models/regression_model.pkl')

# Train K-Means clustering
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X_scaled)
joblib.dump(kmeans, 'models/kmeans_model.pkl')

# Create labels for Naive Bayes (e.g., High: G3 >= 15, Medium: 10-14, Low: <10)
y_nb = pd.cut(data['G3'], bins=[-1, 9, 14, 20], labels=['Low', 'Medium', 'High'])
nb_model = GaussianNB()
nb_model.fit(X_scaled, y_nb)
joblib.dump(nb_model, 'models/naive_bayes_model.pkl')

print("Models trained and saved successfully!")