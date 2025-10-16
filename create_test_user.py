from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()

# Delete existing test user if exists
existing = db.query(User).filter(User.email == "test@test.com").first()
if existing:
    db.delete(existing)
    db.commit()

# Create test user
test_user = User(
    email="test@test.com",
    hashed_password=hash_password("pass123"),
    full_name="Test User",
    role="student"
)

db.add(test_user)
db.commit()
print("✓ Test user created successfully!")
print("Email: test@test.com")
print("Password: pass123")
db.close()
