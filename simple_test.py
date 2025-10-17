#!/usr/bin/env python3
"""
Simple test for OSA backend connectivity
"""

import asyncio
import httpx
import os

async def test_backend():
    """Test basic connectivity to OSA backend"""
    base_url = os.getenv("OSA_BASE_URL", "http://localhost:8001")
    print(f"Testing OSA Backend at: {base_url}")

    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        try:
            # Test health endpoint
            print("1. Testing health endpoint...")
            response = await client.get("/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")

            # Test courses endpoint
            print("\n2. Testing courses endpoint...")
            response = await client.get("/api/v1/courses/")
            print(f"   Status: {response.status_code}")
            courses = response.json()
            print(f"   Found {len(courses)} courses")

            if courses:
                course_id = courses[0]['id']
                print(f"\n3. Testing course details for ID {course_id}...")
                response = await client.get(f"/api/v1/courses/{course_id}")
                print(f"   Status: {response.status_code}")
                course_details = response.json()
                print(f"   Course: {course_details.get('title', 'N/A')}")

            print("\n✅ Backend connectivity test successful!")

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_backend())
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")