import sqlite3
from datetime import datetime, timezone

conn = sqlite3.connect('gym.db')
cursor = conn.cursor()

cursor.execute('SELECT id FROM members WHERE status = "Expired" AND expired_at IS NULL')
expired_members = cursor.fetchall()

for member in expired_members:
    member_id = member[0]
    cursor.execute('SELECT end_date FROM subscriptions WHERE member_id = ? ORDER BY id DESC LIMIT 1', (member_id,))
    sub = cursor.fetchone()
    if sub and sub[0]:
        cursor.execute('UPDATE members SET expired_at = ? WHERE id = ?', (sub[0], member_id))
    else:
        cursor.execute('UPDATE members SET expired_at = ? WHERE id = ?', (datetime.now(timezone.utc).isoformat(), member_id))

conn.commit()
conn.close()
