import re

filepath = 'C:/Users/DELL/Desktop/GYM/frontend/src/Dashboard.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove # from today checkins
content = content.replace('<span className="text-black font-bold text-sm">#{checkin.member_id}</span>', '<span className="text-black font-bold text-sm">{checkin.member_id}</span>')

# 2. Remove # from Members Owing Money
content = content.replace('<div className="text-xs text-gray-500">#{member.id}</div>', '<div className="text-xs text-gray-500">{member.id}</div>')

# 3. In New Subscriptions, if they navigate, maybe disable navigation for Walk-ins?
# <tr onClick={() => navigate(`/members?id=${sub.member_id}`)}> 
# Wait, let's look at `Dashboard.jsx` line 560
subs_row_pattern = r'<tr\n\s*key=\{idx\}\n\s*className="border-b border-gray-200/50 hover:bg-gray-100/20 transition-colors cursor-pointer"\n\s*onClick=\{\(\) => navigate\(`/members\?id=\$\{sub\.member_id\}`\)\}'
new_subs_row = """<tr
                        key={idx}
                        className={`border-b border-gray-200/50 transition-colors ${sub.member_id !== 'G' ? 'hover:bg-gray-100/20 cursor-pointer' : ''}`}
                        onClick={() => { if (sub.member_id !== 'G') navigate(`/members?id=${sub.member_id}`) }}"""
content = re.sub(subs_row_pattern, new_subs_row, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated Dashboard UI for IDs")
