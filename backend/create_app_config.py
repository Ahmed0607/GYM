import sqlite3
conn = sqlite3.connect('gym.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS app_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key VARCHAR UNIQUE,
        value VARCHAR
    )
''')
cursor.execute("INSERT OR IGNORE INTO app_config (key, value) VALUES ('admin_pin', '1111')")
conn.commit()
conn.close()
