from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    print("Current tables in database:")
    for row in result:
        print(f"  - {row[0]}")