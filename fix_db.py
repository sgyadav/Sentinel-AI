"""
SENTINEL AI database cleanup and migration utility.

Run from the project root:
    python fix_db.py

What it does:
- creates a timestamped backup of backend/sentinel.db
- adds missing production columns used by the active backend
- removes obvious test employees/devices/assignments
- normalizes endpoints to AGT-xxxxx IDs
- consolidates duplicate endpoint rows by hostname/MAC/agent ID
- removes invalid process rows and invalid assignments
"""

import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "backend" / "sentinel.db"


def table_exists(cursor, table):
    return cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone() is not None


def columns(cursor, table):
    if not table_exists(cursor, table):
        return set()
    return {row[1] for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()}


def add_column(cursor, table, name, definition):
    existing = columns(cursor, table)
    if table_exists(cursor, table) and name not in existing:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")


def next_agent_id(existing_ids):
    max_number = 0
    for value in existing_ids:
        match = re.fullmatch(r"AGT-(\d{5,})", str(value or ""))
        if match:
            max_number = max(max_number, int(match.group(1)))
    return f"AGT-{max_number + 1:05d}"


def is_test_device(row):
    _, device_id, hostname, ip_address, mac_address = row
    values = " ".join(str(value or "") for value in [device_id, hostname, ip_address, mac_address]).lower()
    test_tokens = ["pc-001", "pc-auto", "dev001", "test-device", "dummy", "sample"]
    return any(token in values for token in test_tokens)


def cleanup():
    if not DB_PATH.exists():
        raise SystemExit(f"Database not found: {DB_PATH}")

    backup = DB_PATH.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    shutil.copy2(DB_PATH, backup)
    print(f"Backup created: {backup}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    add_column(cursor, "devices", "device_id", "TEXT")
    add_column(cursor, "devices", "device_type", "TEXT DEFAULT 'Laptop'")
    add_column(cursor, "devices", "os_version", "TEXT DEFAULT ''")
    add_column(cursor, "processes", "agent_id", "TEXT DEFAULT ''")
    add_column(cursor, "processes", "classification", "TEXT DEFAULT 'Safe'")
    add_column(cursor, "processes", "risk_score", "REAL DEFAULT 0")
    add_column(cursor, "processes", "reason", "TEXT DEFAULT ''")
    add_column(cursor, "usb_events", "agent_id", "TEXT DEFAULT ''")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS endpoint_sessions (
            id INTEGER PRIMARY KEY,
            agent_id TEXT NOT NULL,
            hostname TEXT NOT NULL,
            username TEXT NOT NULL,
            ip_address TEXT DEFAULT '',
            login_time DATETIME NOT NULL,
            logout_time DATETIME,
            session_duration INTEGER,
            status TEXT DEFAULT 'Active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY,
            actor TEXT DEFAULT 'system',
            action TEXT NOT NULL,
            resource_type TEXT DEFAULT '',
            resource_id TEXT DEFAULT '',
            details TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    removed = {
        "employees": 0,
        "devices": 0,
        "assignments": 0,
        "processes": 0,
        "duplicates": 0,
    }

    if table_exists(cursor, "employees"):
        removed["employees"] = cursor.execute("""
            DELETE FROM employees
            WHERE lower(employee_id) LIKE '%test%'
               OR lower(name) LIKE '%test employee%'
               OR lower(email) LIKE 'test@%'
        """).rowcount

    if table_exists(cursor, "devices"):
        device_rows = cursor.execute(
            "SELECT id, device_id, hostname, ip_address, mac_address FROM devices ORDER BY id"
        ).fetchall()
        for row in device_rows:
            if is_test_device(tuple(row)):
                old_id = row["device_id"]
                hostname = row["hostname"]
                cursor.execute("DELETE FROM devices WHERE id=?", (row["id"],))
                if table_exists(cursor, "assignments"):
                    cursor.execute("DELETE FROM assignments WHERE device_id=?", (old_id,))
                if table_exists(cursor, "processes"):
                    cursor.execute("DELETE FROM processes WHERE hostname=?", (hostname,))
                removed["devices"] += 1

    if table_exists(cursor, "devices"):
        rows = cursor.execute(
            "SELECT id, device_id, hostname, mac_address, last_heartbeat FROM devices ORDER BY id"
        ).fetchall()
        existing_ids = [row["device_id"] for row in rows]
        for row in rows:
            old_id = row["device_id"]
            if old_id and re.fullmatch(r"AGT-\d{5,}", str(old_id)):
                continue
            new_id = next_agent_id(existing_ids)
            existing_ids.append(new_id)
            cursor.execute("UPDATE devices SET device_id=? WHERE id=?", (new_id, row["id"]))
            for table in ["assignments", "processes", "usb_events", "endpoint_sessions", "threats"]:
                if table_exists(cursor, table) and "agent_id" in columns(cursor, table):
                    cursor.execute(f"UPDATE {table} SET agent_id=? WHERE agent_id=?", (new_id, old_id))
                if table_exists(cursor, table) and "device_id" in columns(cursor, table):
                    cursor.execute(f"UPDATE {table} SET device_id=? WHERE device_id=?", (new_id, old_id))

    if table_exists(cursor, "devices"):
        rows = cursor.execute(
            "SELECT id, device_id, hostname, mac_address, last_heartbeat FROM devices ORDER BY hostname, mac_address, id"
        ).fetchall()
        seen = {}
        for row in rows:
            key = (row["mac_address"] or row["hostname"] or row["device_id"]).lower()
            if key not in seen:
                seen[key] = row
                continue
            keep = seen[key]
            old_id = row["device_id"]
            keep_id = keep["device_id"]
            cursor.execute("DELETE FROM devices WHERE id=?", (row["id"],))
            if table_exists(cursor, "assignments"):
                cursor.execute("UPDATE assignments SET device_id=? WHERE device_id=?", (keep_id, old_id))
            if table_exists(cursor, "processes"):
                cursor.execute("UPDATE processes SET agent_id=? WHERE agent_id=?", (keep_id, old_id))
            if table_exists(cursor, "usb_events"):
                cursor.execute("UPDATE usb_events SET agent_id=? WHERE agent_id=?", (keep_id, old_id))
            if table_exists(cursor, "threats"):
                cursor.execute("UPDATE threats SET device_id=? WHERE device_id=?", (keep_id, old_id))
            removed["duplicates"] += 1

    if table_exists(cursor, "assignments"):
        removed["assignments"] += cursor.execute("""
            DELETE FROM assignments
            WHERE employee_id NOT IN (SELECT employee_id FROM employees)
               OR device_id NOT IN (SELECT device_id FROM devices)
        """).rowcount
        duplicate_assignments = cursor.execute("""
            SELECT device_id, MIN(id) AS keep_id
            FROM assignments
            WHERE is_active = 1
            GROUP BY device_id
            HAVING COUNT(*) > 1
        """).fetchall()
        for item in duplicate_assignments:
            removed["assignments"] += cursor.execute(
                "UPDATE assignments SET is_active=0 WHERE device_id=? AND id<>?",
                (item["device_id"], item["keep_id"]),
            ).rowcount

    if table_exists(cursor, "processes"):
        removed["processes"] = cursor.execute(
            "DELETE FROM processes WHERE name IS NULL OR trim(name)=''"
        ).rowcount

    cursor.execute("""
        INSERT INTO audit_logs (actor, action, resource_type, details, created_at)
        VALUES ('system', 'Database Cleanup', 'database', ?, CURRENT_TIMESTAMP)
    """, (str(removed),))

    conn.commit()
    conn.close()

    print("Cleanup complete:")
    for key, value in removed.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    cleanup()
