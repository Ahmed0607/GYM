import sqlite3

c = sqlite3.connect('gym.db')
print(c.execute("SELECT sql FROM sqlite_master WHERE name='package_rules'").fetchone()[0])
print(c.execute("SELECT sql FROM sqlite_master WHERE name='subscriptions'").fetchone()[0])

try:
    c.execute("ALTER TABLE package_rules ADD COLUMN is_addon BOOLEAN DEFAULT 0")
    print("Added is_addon to package_rules")
except Exception as e:
    print(f"Error adding is_addon to package_rules: {e}")

try:
    c.execute("ALTER TABLE subscriptions ADD COLUMN addons_usage JSON DEFAULT '{}'")
    print("Added addons_usage to subscriptions")
except Exception as e:
    print(f"Error adding addons_usage to subscriptions: {e}")

c.commit()
c.close()
