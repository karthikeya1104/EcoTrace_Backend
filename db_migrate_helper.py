"""
Migration: add vehicle_type and notes columns to transports table
Preserves all existing transport data
"""

import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent / "backend/ecotrace.db"

if not db_path.exists():
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Checking current schema...\n")

    cursor.execute("PRAGMA table_info(transports);")
    cols = cursor.fetchall()

    for col in cols:
        print(col)

    # Rename old table
    cursor.execute("ALTER TABLE transports RENAME TO transports_old;")
    print("\n✓ Renamed old table")

    # Create new schema (MATCH YOUR SQLAlchemy MODEL)
    cursor.execute("""
    CREATE TABLE transports (
        id INTEGER PRIMARY KEY,
        batch_id INTEGER NOT NULL,
        transporter_id INTEGER NOT NULL,

        origin TEXT NOT NULL,
        destination TEXT NOT NULL,
        distance_km FLOAT NOT NULL,

        fuel_type TEXT NOT NULL,
        vehicle_type TEXT,
        transport_emission FLOAT NOT NULL,

        notes TEXT,
        created_at DATETIME DEFAULT (datetime('now')),

        FOREIGN KEY(batch_id) REFERENCES batches(id),
        FOREIGN KEY(transporter_id) REFERENCES users(id)
    );
    """)
    print("✓ Created new transports table")

    # Copy existing data (old table has no vehicle_type & notes)
    cursor.execute("""
    INSERT INTO transports (
        id, batch_id, transporter_id,
        origin, destination, distance_km,
        fuel_type, transport_emission, created_at
    )
    SELECT 
        id, batch_id, transporter_id,
        origin, destination, distance_km,
        fuel_type, transport_emission, created_at
    FROM transports_old;
    """)
    print(f"✓ Copied {cursor.rowcount} rows")

    # Drop old table
    cursor.execute("DROP TABLE transports_old;")
    print("✓ Removed old table")

    conn.commit()
    print("\n🎉 Migration completed successfully — no data lost!")

except Exception as e:
    conn.rollback()
    print(f"\n❌ Migration failed: {e}")

finally:
    conn.close()
