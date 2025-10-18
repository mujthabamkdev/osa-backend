#!/usr/bin/env python3
"""
Create sample users for all roles in the OSA system
"""

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()

# Sample users for each role
sample_users = [
    {
        "email": "admin@example.com",
        "password": "admin123",
        "full_name": "System Administrator",
        "role": "admin"
    },
    {
        "email": "teacher@example.com",
        "password": "teacher123",
        "full_name": "Ahmad Al-Teacher",
        "role": "teacher"
    },
    {
        "email": "student@example.com",
        "password": "student123",
        "full_name": "Fatima Al-Student",
        "role": "student"
    },
    {
        "email": "parent@example.com",
        "password": "parent123",
        "full_name": "Omar Al-Parent",
        "role": "parent"
    }
]

print("Creating sample users for all roles...")
print("=" * 50)

for user_data in sample_users:
    # Check if user already exists
    existing = db.query(User).filter(User.email == user_data["email"]).first()
    if existing:
        print(f"✓ User {user_data['email']} already exists - updating...")
        existing.hashed_password = hash_password(user_data["password"])
        existing.full_name = user_data["full_name"]
        existing.role = user_data["role"]
    else:
        print(f"✓ Creating user {user_data['email']}...")
        new_user = User(
            email=user_data["email"],
            hashed_password=hash_password(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"]
        )
        db.add(new_user)

db.commit()

# Display all users
print("\nSample users created/updated:")
print("=" * 50)
users = db.query(User).all()
for user in users:
    print(f"Role: {user.role.upper()}")
    print(f"  Email: {user.email}")
    print(f"  Password: {user.email.split('@')[0]}123")  # Pattern: role123
    print(f"  Full Name: {user.full_name}")
    print()

db.close()
print("Sample users setup complete!")