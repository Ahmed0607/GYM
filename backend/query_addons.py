import sqlite3
conn = sqlite3.connect('gym.db')
c = conn.cursor()
c.execute("SELECT member_id, addons_usage FROM subscriptions WHERE addons_usage != '{}' AND addons_usage IS NOT NULL")
print(c.fetchall())
