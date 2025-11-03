#!/usr/bin/env python3
"""Debug script to test login authentication"""
import sys
sys.path.insert(0, '/Users/mujthabamk/Desktop/real-world-projects/osa/OSA/osa-backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.security import verify_password

# Create database connection
DATABASE_URL = "sqlite:///./dev.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()

# Test login for test@test.com
email = "test@test.com"
password = "pass123"

print(f"\n🔍 Testing login for {email}...")
user = db.query(User).filter(User.email == email).first()

if not user:
    print(f"❌ User not found")
    sys.exit(1)

print(f"✓ User found: {user.email}, Full Name: {user.full_name}")
print(f"✓ User ID: {user.id}")
print(f"✓ User Role: {user.role}")
print(f"✓ User Active: {user.is_active}")
print(f"✓ Hashed Password: {user.hashed_password}")

# Test password verification
is_valid = verify_password(password, user.hashed_password)
print(f"\n🔐 Password Verification:")
print(f"  Entered password: '{password}'")
print(f"  Stored hash: {user.hashed_password}")
print(f"  Match result: {is_valid}")

if is_valid:
    print(f"✅ Login would succeed for {email}")
else:
    print(f"❌ Login would fail - password mismatch")

db.close()
