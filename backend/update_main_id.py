import re

filepath = 'C:/Users/DELL/Desktop/GYM/backend/main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Check-ins "SS-id" -> "G"
ss_checkin_pattern = r'"member_id": f"SS-\{row\.id\}",'
content = re.sub(ss_checkin_pattern, '"member_id": "G",', content)

# 2. Append Walk-in sessions to recent_subscriptions
recent_subs_pattern = r'recent_subscriptions = \[\n        \{\n            "member_id": row\.mid,\n            "member_name": row\.name,\n            "packages": json\.loads\(row\.Subscription\.packages\) if isinstance\(row\.Subscription\.packages, str\) else row\.Subscription\.packages,\n            "amount_paid": row\.Subscription\.amount_paid,\n            "start_date": row\.Subscription\.start_date\.isoformat\(\) if row\.Subscription\.start_date else None\n        \}\n        for row in recent_sub_rows\n    \]'

new_recent_subs = """recent_subscriptions = [
        {
            "member_id": row.mid,
            "member_name": row.name,
            "packages": json.loads(row.Subscription.packages) if isinstance(row.Subscription.packages, str) else row.Subscription.packages,
            "amount_paid": row.Subscription.amount_paid,
            "start_date": row.Subscription.start_date.isoformat() if row.Subscription.start_date else None
        }
        for row in recent_sub_rows
    ]
    # Add Walk-in single sessions
    ss_recent_query = select(models.SingleSession).order_by(models.SingleSession.timestamp.desc()).limit(10)
    ss_recent_rows = (await db.execute(ss_recent_query)).scalars().all()
    recent_subscriptions.extend([
        {
            "member_id": "G",
            "member_name": row.name,
            "packages": ["Walk-in Session"],
            "amount_paid": row.amount,
            "start_date": row.timestamp.isoformat()
        }
        for row in ss_recent_rows
    ])
    # Re-sort by start_date/timestamp
    recent_subscriptions.sort(key=lambda x: x["start_date"] if x["start_date"] else "", reverse=True)
    recent_subscriptions = recent_subscriptions[:10]"""

content = re.sub(recent_subs_pattern, new_recent_subs, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated main.py")
