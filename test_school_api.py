#!/usr/bin/env python3
"""
Test script for the school API endpoints
"""

import urllib.request
import urllib.parse
import json

BASE_URL = "http://localhost:8000"

def login():
    """Login and get token"""
    data = json.dumps({"email": "test@test.com", "password": "pass123"}).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/v1/auth/login",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("token")
    except urllib.error.HTTPError as e:
        print(f"Login failed: {e.code} - {e.read().decode('utf-8')}")
        return None

def test_classes(token):
    """Test the classes endpoint"""
    req = urllib.request.Request(
        f"{BASE_URL}/api/v1/school/courses/1/classes",
        headers={'Authorization': f'Bearer {token}'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            classes = json.loads(response.read().decode('utf-8'))
            print(f"Classes endpoint: 200")
            print(f"Found {len(classes)} classes:")
            for cls in classes:
                print(f"  - {cls['name']} (Year {cls['year']})")
    except urllib.error.HTTPError as e:
        print(f"Classes endpoint failed: {e.code} - {e.read().decode('utf-8')}")

def main():
    print("Testing OSA School API...")

    # Login
    token = login()
    if not token:
        return

    print("Login successful!")

    # Test classes endpoint
    test_classes(token)

if __name__ == "__main__":
    main()