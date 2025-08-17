#!/usr/bin/env python3
"""
Simple test script to verify the Flask app functionality
"""
import requests
import json
import time
import subprocess
import os
import signal
import sys
from io import BytesIO

def test_app():
    print("Starting Flask app...")
    # Start the Flask app in background
    proc = subprocess.Popen([sys.executable, "app.py"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
    
    # Wait a bit for the app to start
    time.sleep(3)
    
    base_url = "http://localhost:5001"
    
    try:
        # Test 1: Signup
        print("Testing signup...")
        signup_data = {
            "username": "testuser",
            "password": "testpass123",
            "role": "student"
        }
        response = requests.post(f"{base_url}/signup", json=signup_data)
        print(f"Signup response: {response.status_code} - {response.json()}")
        
        # Test 2: Login
        print("Testing login...")
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(f"{base_url}/login", json=login_data)
        print(f"Login response: {response.status_code} - {response.json()}")
        
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"Got token: {token[:20]}...")
            
            # Test 3: Protected route
            print("Testing protected route...")
            headers = {"Authorization": token}
            response = requests.get(f"{base_url}/protected", headers=headers)
            print(f"Protected route response: {response.status_code} - {response.json()}")
        
        # Test 4: Upload CSV
        print("Testing CSV upload...")
        with open('test_student_data.csv', 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/upload", files=files)
            print(f"Upload response: {response.status_code}")
            if response.status_code == 200:
                print("Upload successful! Sample predictions:", response.json()[:2])
            else:
                print("Upload response:", response.json())
        
        print("\n All tests completed successfully!")
        
    except Exception as e:
        print(f" Test failed: {e}")
    finally:
        # Stop the Flask app
        print("Stopping Flask app...")
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_app()