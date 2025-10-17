#!/usr/bin/env python3
"""
OSA MCP Server - Model Context Protocol integration for Online Sharia Academy
Exposes OSA backend functionality as MCP tools for AI assistants
"""

import asyncio
import httpx
import os
from typing import Any, Dict, List, Optional
from mcp import Tool
from mcp.server import Server
from mcp.types import TextContent, PromptMessage
import mcp.server.stdio

# OSA Backend Configuration
OSA_BASE_URL = os.getenv("OSA_BASE_URL", "http://localhost:8001")
OSA_API_KEY = os.getenv("OSA_API_KEY", "")  # For authenticated requests

class OSAMCPTools:
    """OSA-specific MCP tools for course management and student interactions"""

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=OSA_BASE_URL,
            headers={"Authorization": f"Bearer {OSA_API_KEY}"} if OSA_API_KEY else {},
            timeout=30.0
        )

    async def get_course_details(self, course_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific course"""
        try:
            response = await self.client.get(f"/api/v1/courses/{course_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"Failed to get course details: {str(e)}"}

    async def list_all_courses(self) -> List[Dict[str, Any]]:
        """Get list of all available courses"""
        try:
            response = await self.client.get("/api/v1/courses/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return [{"error": f"Failed to list courses: {str(e)}"}]

    async def get_student_enrollments(self, student_id: int) -> List[Dict[str, Any]]:
        """Get enrolled courses for a specific student"""
        try:
            response = await self.client.get(f"/api/v1/students/{student_id}/enrolled-courses")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return [{"error": f"Failed to get student enrollments: {str(e)}"}]

    async def get_student_progress(self, student_id: int) -> List[Dict[str, Any]]:
        """Get progress information for a student"""
        try:
            response = await self.client.get(f"/api/v1/students/{student_id}/progress")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return [{"error": f"Failed to get student progress: {str(e)}"}]

    async def enroll_student(self, student_id: int, course_id: int) -> Dict[str, Any]:
        """Enroll a student in a course (admin only)"""
        try:
            response = await self.client.post(
                "/api/v1/admin/enroll",
                json={"student_id": student_id, "course_id": course_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"Failed to enroll student: {str(e)}"}

    async def update_student_active_class(self, enrollment_id: int, active_class_id: int) -> Dict[str, Any]:
        """Update a student's active class (admin only)"""
        try:
            response = await self.client.put(
                f"/api/v1/admin/enrollments/{enrollment_id}/active-class",
                json={"active_class_id": active_class_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"Failed to update active class: {str(e)}"}

    async def get_student_notes(self, student_id: int) -> List[Dict[str, Any]]:
        """Get notes for a specific student"""
        try:
            response = await self.client.get(f"/api/v1/students/{student_id}/notes")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return [{"error": f"Failed to get student notes: {str(e)}"}]

# Initialize the MCP server
server = Server("osa-mcp-server")
osa_tools = OSAMCPTools()

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available OSA MCP tools"""
    return [
        Tool(
            name="get_course_details",
            description="Get detailed information about a specific course including chapters, progress, and active class",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {
                        "type": "integer",
                        "description": "The ID of the course to retrieve"
                    }
                },
                "required": ["course_id"]
            }
        ),
        Tool(
            name="list_all_courses",
            description="Get a list of all available courses in the Online Sharia Academy",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_student_enrollments",
            description="Get all courses a student is enrolled in, including active class information",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "integer",
                        "description": "The ID of the student"
                    }
                },
                "required": ["student_id"]
            }
        ),
        Tool(
            name="get_student_progress",
            description="Get detailed progress information for a student across all enrolled courses",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "integer",
                        "description": "The ID of the student"
                    }
                },
                "required": ["student_id"]
            }
        ),
        Tool(
            name="enroll_student",
            description="Enroll a student in a course (requires admin privileges)",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "integer",
                        "description": "The ID of the student to enroll"
                    },
                    "course_id": {
                        "type": "integer",
                        "description": "The ID of the course to enroll in"
                    }
                },
                "required": ["student_id", "course_id"]
            }
        ),
        Tool(
            name="update_student_active_class",
            description="Update a student's active class for progression tracking (requires admin privileges)",
            inputSchema={
                "type": "object",
                "properties": {
                    "enrollment_id": {
                        "type": "integer",
                        "description": "The ID of the enrollment to update"
                    },
                    "active_class_id": {
                        "type": "integer",
                        "description": "The ID of the chapter to set as active"
                    }
                },
                "required": ["enrollment_id", "active_class_id"]
            }
        ),
        Tool(
            name="get_student_notes",
            description="Get all notes created by a specific student",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "integer",
                        "description": "The ID of the student"
                    }
                },
                "required": ["student_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute OSA MCP tools"""

    try:
        if name == "get_course_details":
            course_id = arguments["course_id"]
            result = await osa_tools.get_course_details(course_id)
            return [TextContent(
                type="text",
                text=f"Course Details for ID {course_id}:\n{result}"
            )]

        elif name == "list_all_courses":
            courses = await osa_tools.list_all_courses()
            return [TextContent(
                type="text",
                text=f"Available Courses:\n{courses}"
            )]

        elif name == "get_student_enrollments":
            student_id = arguments["student_id"]
            enrollments = await osa_tools.get_student_enrollments(student_id)
            return [TextContent(
                type="text",
                text=f"Enrolled Courses for Student {student_id}:\n{enrollments}"
            )]

        elif name == "get_student_progress":
            student_id = arguments["student_id"]
            progress = await osa_tools.get_student_progress(student_id)
            return [TextContent(
                type="text",
                text=f"Progress for Student {student_id}:\n{progress}"
            )]

        elif name == "enroll_student":
            student_id = arguments["student_id"]
            course_id = arguments["course_id"]
            result = await osa_tools.enroll_student(student_id, course_id)
            return [TextContent(
                type="text",
                text=f"Enrolled Student {student_id} in Course {course_id}:\n{result}"
            )]

        elif name == "update_student_active_class":
            enrollment_id = arguments["enrollment_id"]
            active_class_id = arguments["active_class_id"]
            result = await osa_tools.update_student_active_class(enrollment_id, active_class_id)
            return [TextContent(
                type="text",
                text=f"Updated Active Class for Enrollment {enrollment_id} to Class {active_class_id}:\n{result}"
            )]

        elif name == "get_student_notes":
            student_id = arguments["student_id"]
            notes = await osa_tools.get_student_notes(student_id)
            return [TextContent(
                type="text",
                text=f"Notes for Student {student_id}:\n{notes}"
            )]

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]

async def main():
    """Main entry point for the OSA MCP server"""
    print("Starting OSA MCP Server...", file=os.sys.stderr)
    print(f"Connecting to OSA Backend at: {OSA_BASE_URL}", file=os.sys.stderr)

    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        print(f"Server error: {e}", file=os.sys.stderr)
        raise
    finally:
        await osa_tools.client.aclose()

if __name__ == "__main__":
    asyncio.run(main())