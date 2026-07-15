import sqlite3

try:
    conn = sqlite3.connect('backend/sentinel.db', timeout=5)
    cursor = conn.cursor()
    
    # Check and fix USB Events table
    cursor.execute("PRAGMA table_info(usb_events)")
    usb_cols = [row[1] for row in cursor.fetchall()]
    print('USB Events columns:', usb_cols)
    
    if 'created_at' not in usb_cols:
        print('Adding created_at to usb_events...')
        cursor.execute('ALTER TABLE usb_events ADD COLUMN created_at DATETIME')
        cursor.execute('UPDATE usb_events SET created_at = event_time')
    
    # Check ProcessDB table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processes'")
    if not cursor.fetchone():
        print('Creating processes table...')
        cursor.execute('''
            CREATE TABLE processes (
                id INTEGER PRIMARY KEY,
                hostname TEXT NOT NULL,
                pid INTEGER NOT NULL,
                name TEXT NOT NULL,
                cpu_percent FLOAT DEFAULT 0,
                memory_percent FLOAT DEFAULT 0,
                username TEXT DEFAULT 'Unknown',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        print('Processes table already exists')
    
    conn.commit()
    print('Database migration complete!')
    conn.close()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
