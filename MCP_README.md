# OSA MCP Server Integration

This MCP (Model Context Protocol) server integrates your Online Sharia Academy backend with AI assistants like Claude Desktop, GitHub Copilot, and other MCP-compatible tools.

## What is MCP?

MCP allows AI assistants to securely access external tools and data sources. Your OSA backend now exposes course management, student enrollment, and progress tracking functionality to AI assistants.

## Quick Start

### 1. Ensure Backend is Running

```bash
cd osa-backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 2. Start MCP Server

```bash
# Using the startup script (recommended)
./start_mcp_server.sh

# Or manually
source venv/bin/activate
python osa_mcp_server.py
```

### 3. Configure Claude Desktop

1. Open Claude Desktop
2. Go to Settings → Developer → Edit Config
3. Add the MCP server configuration (see `claude_config_example.json`)
4. Replace `your-admin-jwt-token-here` with a valid admin JWT token from your OSA backend
5. Restart Claude Desktop

## Environment Variables

- `OSA_BASE_URL`: Backend URL (default: `http://localhost:8001`)
- `OSA_API_KEY`: Admin JWT token for authenticated operations (optional but required for admin functions)

## Available Tools

### Course Management

- **get_course_details**: Get detailed course information including chapters and active class
- **list_all_courses**: List all available courses in the academy

### Student Management

- **get_student_enrollments**: Get courses a student is enrolled in with active class info
- **get_student_progress**: Get detailed progress across all courses
- **get_student_notes**: Get all notes created by a student

### Admin Operations (require OSA_API_KEY)

- **enroll_student**: Enroll a student in a course
- **update_student_active_class**: Change a student's active class for progression

## Usage Examples

Once configured, you can ask Claude things like:

- _"Show me the details of course ID 1"_
- _"What courses is student 2 enrolled in?"_
- _"Enroll student 5 in course 1"_
- _"Update student 2's active class to class 3"_
- _"What progress has student 3 made?"_
- _"Get notes from student 4"_

## Security Notes

- Admin operations require a valid JWT token in `OSA_API_KEY`
- The server makes HTTP requests to your OSA backend
- Ensure proper authentication and authorization in your backend
- Keep your JWT tokens secure

## Troubleshooting

### Backend Connection Issues

- Ensure OSA backend is running on the configured URL
- Check network connectivity
- Verify CORS settings allow the MCP server

### Authentication Issues

- Get a valid admin JWT token from your OSA backend
- Set the `OSA_API_KEY` environment variable
- Check token expiration

### Claude Desktop Issues

- Restart Claude Desktop after configuration changes
- Check the Claude Desktop logs for MCP errors
- Verify the JSON configuration syntax

## Files Created

- `osa_mcp_server.py` - Main MCP server implementation
- `start_mcp_server.sh` - Startup script
- `claude_config_example.json` - Claude Desktop configuration example
- `MCP_README.md` - This documentation
- `test_mcp_server.py` - Connection test script
