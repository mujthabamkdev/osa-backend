#!/bin/bash

# Test the OSA School API

echo "Testing OSA School API..."

# Login and get token
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"pass123"}')

echo "Login response: $LOGIN_RESPONSE"

# Extract token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "Failed to get token"
  exit 1
fi

echo "Got token: ${TOKEN:0:20}..."

# Test classes endpoint
echo "Testing classes endpoint..."
CLASSES_RESPONSE=$(curl -s http://localhost:8000/api/v1/school/courses/1/classes \
  -H "Authorization: Bearer $TOKEN")

echo "Classes response: $CLASSES_RESPONSE"