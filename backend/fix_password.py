import sqlite3
import hashlib

conn = sqlite3.connect('sentinel.db')
cursor = conn.cursor()

# Calculate correct hash
password_hash = "sha256:" + hashlib.sha256("Admin1234".encode()).hexdigest()
print(f"Updating password hash to: {password_hash}")

cursor.execute("UPDATE users SET password = ? WHERE username='admin'", (password_hash,))
conn.commit()

# Verify
cursor.execute("SELECT username, password FROM users WHERE username='admin'")
row = cursor.fetchone()
print(f"Verified - User: {row[0]}, Hash: {row[1][:50]}...")

conn.close()
