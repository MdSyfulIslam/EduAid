# 🎓 EduAID – Student Performance Prediction System (Web-Based)

A **Flask-powered machine learning application** that predicts student performance from both **individual inputs** and **bulk CSV uploads**. The system integrates **Regression**, **Naive Bayes**, and **K-Means Clustering** to evaluate grades, classify risk levels, and group students into performance clusters.  
This project was developed as part of the **Artificial Intelligence (CSE-315)** course at **Green University of Bangladesh**.

---

## 📋 Table of Contents

- [🔍 Project Overview](#-project-overview)  
- [🎯 Features](#-features)  
- [⚙️ Tools & Technologies](#️-tools--technologies)  
- [🧠 Machine Learning Models Used](#-machine-learning-models-used)  
- [📊 Testing & Results](#-testing--results)  
- [🧪 Limitations](#-limitations)  
- [📈 Future Improvements](#-future-improvements)  
- [👨‍💻 Authors](#-authors)  
- [📎 References](#-references)  

---

## 🔍 Project Overview

**EduAID** is a **student performance prediction system** that enables teachers and administrators to:

- Predict a student’s final grade from key academic indicators  
- Classify students into **risk categories** (Low, Medium, High)  
- Group students into **performance clusters** using unsupervised learning  
- Visualize results via **charts and dashboards** for better decision-making  

The tool helps educators identify at-risk students early and take preventive measures.

---

## 🎯 Features

- 🎓 **Individual Prediction** – Enter details (age, study time, past failures, absences, grades G1 & G2) to predict performance  
- 📂 **Bulk Prediction** – Upload CSV dataset for batch predictions  
- 📊 **Visualization Dashboard** – Displays **histograms, bar charts, and doughnut charts**  
- ⚡ **Real-time Feedback** – Instantly shows predicted scores, clusters, and categories  
- 🛡️ **Secure Access** – User authentication with login/signup system  
- 📑 **Database Integration** – SQLite for storing users  
- 📈 **Model Accuracy Display** – Shows accuracy of the trained ML model  

---

## ⚙️ Tools & Technologies

- **Flask (Python)** – Backend framework  
- **SQLite3** – Lightweight database for user management  
- **Pandas & NumPy** – Data preprocessing and manipulation  
- **Scikit-learn** – ML models (Regression, Naive Bayes, KMeans)  
- **Joblib** – Model persistence (saving/loading)  
- **Chart.js** – Interactive data visualization    

---

## 🧠 Machine Learning Models Used

### 📈 Linear Regression
- Predicts final grade (0–20 scale) based on input features  
- Provides **numerical score output**  

### 🧮 Naive Bayes Classifier
- Classifies student into **risk categories** (e.g., High, Medium, Low)  
- Based on probabilities of poor/good performance  

### 🧩 K-Means Clustering
- Groups students into **clusters of similar performance**  
- Provides insights on patterns among students  

---

## 📊 Testing & Results

### ✅ Model Performance

| Model             | Accuracy | Use Case                          |
|-------------------|----------|-----------------------------------|
| Regression        | ~85%     | Predicts numerical final grade    |
| Naive Bayes       | ~82%     | Risk category classification      |
| K-Means Clustering| N/A      | Groups students into clusters     |

### 📊 Dashboard Visuals
- Histogram of predicted scores  
- Bar chart of **risk categories**  
- Cluster distribution chart  
- Doughnut chart for single student prediction  

---

## 🧪 Limitations

- ⚠️ Accuracy depends heavily on dataset quality  
- ❌ Currently trained on **small datasets**  
- ❌ Does not consider external factors (e.g., family, motivation)  
- ❌ Basic authentication, no role-based permissions yet  

---

## 📈 Future Improvements

- 📂 Add **support for larger datasets** and optimization for speed  
- ☁️ Deploy to **cloud platforms (Heroku/AWS)** for accessibility  
- 🔐 Role-based access (Admin, Teacher, Student)  
- 📱 Build a **mobile-friendly version**  
- 📊 Add **more advanced ML models** (Random Forest, Neural Networks)  
- 🔎 Feature importance analysis to identify key student performance drivers  

---

## 👨‍💻 Authors
**Md Syful Islam** – Student ID: 222002111 
**Asraful Islam Apo** – Student ID: 221002172
**Al_Motakabbir Mahmud Shihab** – Student ID: 222002061

📚 B.Sc. in CSE (Day), Green University of Bangladesh  
🧑‍🏫 **Course:** Machine Learning Lab (CSE-412)  
📚 **Section:** 222-D3  
📅 **Submitted on:** 17 August 2025  

---

## 📎 References
 
1. Educational datasets for student performance – UCI ML Repository  

---
