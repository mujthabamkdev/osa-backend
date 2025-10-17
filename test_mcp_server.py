#!/usr/bin/env python3
"""
Test script for OSA MCP Server
Run this to verify the MCP server can connect to the OSA backend
"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from osa_mcp_server import OSAMCPTools

async def test_osa_connection():
    """Test basic connectivity to OSA backend"""
    print("Testing OSA Backend Connection...")
    print(f"OSA_BASE_URL: {os.getenv('OSA_BASE_URL', 'http://localhost:8001')}")

    tools = OSAMCPTools()

    try:
        # Test listing courses
        print("\n1. Testing course listing...")
        courses = await tools.list_all_courses()
        print(f"Raw response: {courses}")

        if courses and len(courses) > 0 and not courses[0].get('error'):
            print(f"✅ Found {len(courses)} courses")
            # Test getting course details
            course_id = courses[0].get('id', 1)
            print(f"\n2. Testing course details for course {course_id}...")
            course_details = await tools.get_course_details(course_id)
            print(f"Raw course details: {course_details}")
            if not course_details.get('error'):
                print(f"✅ Course title: {course_details.get('title', 'N/A')}")
        else:
            print("❌ No courses found or error in response")

        # Test student enrollments (assuming student ID 2 exists)
        print("\n3. Testing student enrollments...")
        enrollments = await tools.get_student_enrollments(2)
        print(f"Raw enrollments: {enrollments}")
        if enrollments and not enrollments[0].get('error'):
            print(f"✅ Student 2 has {len(enrollments)} enrollments")
        else:
            print("❌ Error getting student enrollments")

        print("\n✅ OSA Backend connection successful!")
        print("MCP Server is ready to use.")
        return True

    except Exception as e:
        print(f"\n❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        print("Make sure your OSA backend is running on the configured URL")
        return False

    finally:
        await tools.client.aclose()

if __name__ == "__main__":
    success = asyncio.run(test_osa_connection())
    sys.exit(0 if success else 1)