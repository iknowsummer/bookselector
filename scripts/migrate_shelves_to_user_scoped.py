"""
Database migration: Add user_id to shelves table.

This script:
1. Creates admin user if not exists
2. Creates new shelves table with user_id column
3. Migrates existing shelves to admin user (id=1)
4. Adds composite unique constraint (user_id, name)
5. Adds created_at column

IMPORTANT: Back up your database before running!
"""
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "backend" / "sqlite.db"
BACKUP_PATH = PROJECT_ROOT / "backend" / f"sqlite_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"


def backup_database():
    """Create backup before migration."""
    import shutil

    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"✓ Database backed up to: {BACKUP_PATH}")


def create_admin_user(cursor):
    """Create admin user if not exists."""
    cursor.execute("SELECT id FROM users WHERE id = 1")
    if cursor.fetchone():
        print("✓ Admin user (id=1) already exists")
        return

    cursor.execute("""
        INSERT INTO users (id, name, created_at)
        VALUES (1, 'admin', CURRENT_TIMESTAMP)
    """)
    print("✓ Created admin user (id=1)")


def migrate_shelves_table(cursor):
    """Migrate shelves table to user-scoped schema."""

    # Check if already migrated
    cursor.execute("PRAGMA table_info(shelves)")
    columns = {row[1]: row for row in cursor.fetchall()}

    if "user_id" in columns:
        print("! Migration already done (user_id exists)")
        return True

    print("Starting shelves table migration...")

    # Get existing data
    cursor.execute("SELECT id, name, memo FROM shelves")
    existing_shelves = cursor.fetchall()
    print(f"  Found {len(existing_shelves)} existing shelves")

    # Create new table with user_id
    cursor.execute("""
        CREATE TABLE shelves_new (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            memo TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE (user_id, name)
        )
    """)
    print("✓ Created new shelves table")

    # Migrate existing shelves to admin user (id=1)
    if existing_shelves:
        cursor.executemany("""
            INSERT INTO shelves_new (id, user_id, name, memo, created_at)
            VALUES (?, 1, ?, ?, CURRENT_TIMESTAMP)
        """, [(s[0], s[1], s[2]) for s in existing_shelves])
        print(f"✓ Migrated {len(existing_shelves)} shelves to admin user")

    # Create indexes
    cursor.execute("CREATE INDEX ix_shelves_user_id ON shelves_new(user_id)")
    cursor.execute("CREATE INDEX ix_shelves_name ON shelves_new(name)")
    print("✓ Created indexes")

    # Swap tables
    cursor.execute("DROP TABLE shelves")
    cursor.execute("ALTER TABLE shelves_new RENAME TO shelves")
    print("✓ Replaced old table")

    return True


def verify_migration(cursor):
    """Verify migration success."""
    print("\nVerifying migration...")

    # Check schema
    cursor.execute("PRAGMA table_info(shelves)")
    columns = {row[1]: row for row in cursor.fetchall()}
    required = {"id", "user_id", "name", "memo", "created_at"}

    if not required.issubset(columns.keys()):
        print(f"  ERROR: Missing columns: {required - columns.keys()}")
        return False
    print(f"✓ All columns present")

    # Check NOT NULL constraint
    if columns["user_id"][3] != 1:  # notnull flag
        print("  ERROR: user_id not NOT NULL")
        return False
    print("✓ user_id has NOT NULL constraint")

    # Check data integrity
    cursor.execute("SELECT COUNT(*) FROM shelves WHERE user_id IS NULL")
    if cursor.fetchone()[0] > 0:
        print("  ERROR: Found NULL user_id values")
        return False

    cursor.execute("SELECT COUNT(*) FROM shelves")
    shelf_count = cursor.fetchone()[0]
    print(f"✓ All {shelf_count} shelves have valid user_id")

    return True


def main():
    """Main migration execution."""
    print("=" * 60)
    print("Shelves Table Migration: Add user_id")
    print("=" * 60)
    print()

    backup_database()
    print()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    cursor = conn.cursor()

    try:
        create_admin_user(cursor)
        print()

        migrate_shelves_table(cursor)
        print()

        conn.commit()
        print("✓ Changes committed")
        print()

        if verify_migration(cursor):
            print("\n" + "=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)
        else:
            print("\n! Migration completed with warnings")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ ERROR: {e}")
        print(f"Restore from backup: {BACKUP_PATH}")
        sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
