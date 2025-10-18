from app.core.database import engine
from sqlalchemy import text, inspect

with engine.connect() as conn:
    # Check enrollments table structure
    inspector = inspect(engine)
    columns = inspector.get_columns('enrollments')
    print("Enrollments table columns:")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")

    # Check foreign keys
    fks = inspector.get_foreign_keys('enrollments')
    print("\nEnrollments table foreign keys:")
    for fk in fks:
        print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")