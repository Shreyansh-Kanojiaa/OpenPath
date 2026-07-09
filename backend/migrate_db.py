"""
Idempotent migration script for adding new columns to the courses and modules tables.
Works with both SQLite and PostgreSQL.
Safe to re-run — skips columns that already exist.
"""

import os
from database import engine
from sqlalchemy import text, inspect


# Define the columns to add per table.
# Each entry: (column_name, column_sql_definition)
MIGRATIONS = {
    "users": [
        ("google_sub", "VARCHAR DEFAULT NULL"),
    ],
    "courses": [
        ("project_prompt", "TEXT DEFAULT NULL"),
        ("required_resources", "TEXT DEFAULT NULL"),  # JSON stored as TEXT
    ],
    "modules": [
        ("has_transcript", "BOOLEAN NOT NULL DEFAULT FALSE"),
        ("notes", "VARCHAR(2000) DEFAULT NULL"),
        ("completed_at", "TIMESTAMP DEFAULT NULL"),
    ],
}


def get_existing_columns(conn, table_name: str) -> set[str]:
    """Return a set of column names for the given table using SQLAlchemy Inspector."""
    insp = inspect(conn)
    columns = insp.get_columns(table_name)
    return {col["name"] for col in columns}


def migrate():
    added = []
    skipped = []

    with engine.connect() as conn:
        for table_name, columns in MIGRATIONS.items():
            existing = get_existing_columns(conn, table_name)
            print(f"\n[{table_name}] existing columns: {sorted(existing)}")

            for col_name, col_def in columns:
                if col_name in existing:
                    skipped.append(f"{table_name}.{col_name}")
                    print(f"  SKIP  {col_name} (already exists)")
                else:
                    sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}"
                    conn.execute(text(sql))
                    added.append(f"{table_name}.{col_name}")
                    print(f"  ADD   {col_name}")

        conn.commit()

    # Summary
    print("\n" + "=" * 50)
    print("Migration summary")
    print("=" * 50)
    if added:
        print(f"  Added ({len(added)}):   {', '.join(added)}")
    else:
        print("  Added: (none)")
    if skipped:
        print(f"  Skipped ({len(skipped)}): {', '.join(skipped)}")
    else:
        print("  Skipped: (none)")
    print()


if __name__ == "__main__":
    migrate()
