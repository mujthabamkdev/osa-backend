# 🚀 Backend Deployment Guide

## Environment Setup

### Required Environment Variables

Create a `.env` file in the backend root directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///./osa.db  # For development
# DATABASE_URL=postgresql://user:password@host:port/database  # For production

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-here-change-this-in-production
JWT_EXPIRATION_HOURS=24

# CORS Configuration
CORS_ORIGINS=http://localhost:4200,http://localhost:3000
# For production: CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Database Migration

Run database migrations to set up the schema:

```bash
# Set Python path and run migrations
PYTHONPATH=. alembic upgrade head
```

## Development Setup

1. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**

   ```bash
   PYTHONPATH=. alembic upgrade head
   ```

4. **Create test user (optional):**

   ```bash
   PYTHONPATH=. python create_test_user.py
   ```

5. **Start development server:**
   ```bash
   PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Production Deployment

### Railway Deployment

1. **Connect Repository:**

   - Import your GitHub repository to Railway
   - Railway will automatically detect Python/FastAPI

2. **Database Setup:**

   - Add PostgreSQL database in Railway dashboard
   - Copy the database URL from Railway

3. **Environment Variables:**

   - Set `DATABASE_URL` to Railway PostgreSQL URL
   - Set `JWT_SECRET` to a secure random string
   - Set `CORS_ORIGINS` to your frontend domain(s)

4. **Deploy:**
   - Railway will build and deploy automatically
   - Use the Dockerfile CMD for production

### Docker Deployment

1. **Build Docker image:**

   ```bash
   docker build -t osa-backend .
   ```

2. **Run container:**
   ```bash
   docker run -p 8000:8000 \
     --env-file .env \
     osa-backend
   ```

### Manual Server Deployment

1. **Install Python and dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**

3. **Run migrations:**

   ```bash
   PYTHONPATH=. alembic upgrade head
   ```

4. **Start with production ASGI server:**
   ```bash
   PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

## API Health Check

Once deployed, verify the API is working:

```bash
curl https://your-api-domain.com/api/v1/auth/login
```

Expected response: Method not allowed (405) - this confirms the API is running.

## Troubleshooting

### Common Issues

1. **Migration Errors:**

   - Ensure DATABASE_URL is correct
   - Check database permissions
   - Verify alembic is installed

2. **CORS Errors:**

   - Check CORS_ORIGINS includes your frontend domain
   - Ensure protocol (http/https) matches

3. **JWT Errors:**
   - Verify JWT_SECRET is set and secure
   - Check token expiration settings

### Logs

Check application logs for detailed error information:

- Railway: View in Railway dashboard
- Docker: `docker logs <container_id>`
- Manual: Check server logs

## Security Notes

- **Never commit .env files** to version control
- **Use strong JWT secrets** in production
- **Enable HTTPS** in production
- **Regularly update dependencies** for security patches
- **Use environment-specific configurations**</content>
  <parameter name="oldString">Setup:

Set envs: DATABASE_URL, JWT_SECRET, CORS_ORIGINS

Run migrations: alembic upgrade head
Deploy (Railway):

Attach Postgres, set envs, deploy with CMD in Dockerfile
