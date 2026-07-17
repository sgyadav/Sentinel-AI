import sqlite3

conn = sqlite3.connect("sentinel.db")
cursor = conn.cursor()

cursor.execute("""
SELECT
    id,
    device_id,
    hostname,
    mac_address,
    last_heartbeat,
    status
FROM devices
""")

rows = cursor.fetchall()

print(f"Total Devices: {len(rows)}")
print("-" * 100)

for row in rows:
    print(row)

conn.close()