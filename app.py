from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
import pandas as pd
import joblib
from io import StringIO
from collections import Counter  #  NEW: for chart aggregation

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

#   In-memory state for charts (last uploaded dataset summary)
app_state = {
    'overall': None   # will store aggregated chart data after a CSV upload
}

def get_db_connection():
    conn = sqlite3.connect('eduai_db.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Load trained models
scaler = joblib.load('models/scaler.pkl')
reg_model = joblib.load('models/regression_model.pkl')
kmeans = joblib.load('models/kmeans_model.pkl')
nb_model = joblib.load('models/naive_bayes_model.pkl')

#   Set model accuracy (replace with your actual accuracy)
MODEL_ACCURACY = 85.5  # Example accuracy in percentage

#   helper to compute overall stats for charts
def compute_overall_stats(predicted_scores, risk_categories, clusters):
    # Make everything JSON-serializable
    scores = [float(x) for x in predicted_scores]
    risks = [str(x) for x in risk_categories]
    clusts = [int(x) for x in clusters]

    # Score histogram buckets for a 0–20 grading scale
    labels = ["0–5", "5–10", "10–15", "15–20"]
    counts = [0, 0, 0, 0]
    for s in scores:
        if s < 5:
            counts[0] += 1
        elif s < 10:
            counts[1] += 1
        elif s < 15:
            counts[2] += 1
        else:
            counts[3] += 1

    risk_counts = Counter(risks)
    cluster_counts = Counter(clusts)

    return {
        'score_hist': {
            'labels': labels,
            'counts': counts
        },
        'risk_counts': {
            'labels': list(risk_counts.keys()),
            'counts': list(risk_counts.values())
        },
        'cluster_counts': {
            'labels': [str(k) for k in cluster_counts.keys()],
            'counts': list(cluster_counts.values())
        },
        'avg_score': round(sum(scores) / len(scores), 2) if scores else 0.0,
        'n': len(scores)
    }

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# Signup Route - GET and POST
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    if not all([username, password, role]):
        flash('Missing required fields', 'error')
        return render_template('signup.html')

    #  FIXED: Use pbkdf2:sha256 instead of sha256
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                     (username, hashed_password, role))
        conn.commit()
        conn.close()
        flash('User registered successfully', 'success')
        return redirect(url_for('login'))
    except sqlite3.IntegrityError:
        flash('Username already exists', 'error')
        return render_template('signup.html')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('signup.html')

# Login Route - GET and POST
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form.get('username')
    password = request.form.get('password')

    if not all([username, password]):
        flash('Missing username or password', 'error')
        return render_template('login.html')

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        flash('Login successful', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials', 'error')
        return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access dashboard', 'error')
        return redirect(url_for('login'))
    #  Pass last-known overall charts (if any) so the page can render them on load
    chart_data = {'overall': app_state['overall']} if app_state.get('overall') else None
    return render_template('dashboard.html', chart_data=chart_data)

# Upload Route
@app.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session:
        flash('Please login to access this feature', 'error')
        return redirect(url_for('login'))
        
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return render_template('dashboard.html')
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return render_template('dashboard.html')
    
    if not file.filename.endswith('.csv'):
        flash('File must be a CSV', 'error')
        return render_template('dashboard.html')

    try:
        df = pd.read_csv(file)
        required_columns = ['student_id', 'age', 'studytime', 'failures', 'absences', 'G1', 'G2']
        if not all(col in df.columns for col in required_columns):
            flash('Missing required columns in CSV', 'error')
            return render_template('dashboard.html')

        # Scale features
        X = df[required_columns[1:]]  # Exclude student_id
        X_scaled = scaler.transform(X)

        # Predict scores
        predicted_scores = reg_model.predict(X_scaled)

        # Cluster assignments
        clusters = kmeans.predict(X_scaled)

        # Risk category with Naive Bayes
        risk_categories = nb_model.predict(X_scaled)

        # Prepare results
        results = []
        for i in range(len(df)):
            results.append({
                'student_id': int(df['student_id'].iloc[i]),
                'predicted_score': round(float(predicted_scores[i]), 2),
                'risk_category': str(risk_categories[i]),
                'cluster': int(clusters[i])
            })

        #   compute & store overall stats for charts
        overall = compute_overall_stats(predicted_scores, risk_categories, clusters)
        app_state['overall'] = overall

        flash('File processed successfully', 'success')
        #  Pass both table and charts to the template with model accuracy
        return render_template('dashboard.html', upload_results=results, chart_data={'overall': overall}, model_accuracy=MODEL_ACCURACY)
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return render_template('dashboard.html')

# Predict Route for individual student data
@app.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        flash('Please login to access this feature', 'error')
        return redirect(url_for('login'))
        
    try:
        required_fields = ['age', 'studytime', 'failures', 'absences', 'G1', 'G2']
        
        # Get data from form
        data = {}
        for field in required_fields:
            value = request.form.get(field)
            if not value:
                flash('Missing required fields', 'error')
                return render_template('dashboard.html')
            data[field] = float(value)
        
        # Extract features for prediction
        features = [[data[field] for field in required_fields]]
        
        # Scale features
        X_scaled = scaler.transform(features)
        
        # Make predictions
        predicted_score = float(reg_model.predict(X_scaled)[0])
        cluster = int(kmeans.predict(X_scaled)[0])
        risk_category = str(nb_model.predict(X_scaled)[0])
        
        prediction_result = {
            'predicted_score': round(predicted_score, 2),
            'risk_category': risk_category,
            'cluster': cluster
        }

        #  chart payload for a single prediction (and include last-known overall if present)
        chart_data = {'single': {'score': prediction_result['predicted_score']}}
        if app_state.get('overall'):
            chart_data['overall'] = app_state['overall']
        
        flash('Prediction completed successfully', 'success')
        return render_template('dashboard.html', prediction=prediction_result, chart_data=chart_data, model_accuracy=MODEL_ACCURACY)
        
    except Exception as e:
        flash(f'Error making prediction: {str(e)}', 'error')
        return render_template('dashboard.html')

# Protected Route Example
@app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token is missing'}), 401
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return jsonify({'message': 'Protected data', 'user': data['username']}), 200
    except:
        return jsonify({'error': 'Invalid token'}), 401

#   optional JSON endpoint to fetch the latest overall chart data
@app.route('/chart-data', methods=['GET'])
def chart_data_api():
    overall = app_state.get('overall')
    if not overall:
        return jsonify({'overall': None}), 200
    return jsonify({'overall': overall}), 200

if __name__ == '__main__':
    # Same host/port as before
    app.run(debug=True, host='0.0.0.0', port=5001)