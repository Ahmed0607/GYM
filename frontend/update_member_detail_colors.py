import re

filepath = 'C:/Users/DELL/Desktop/GYM/frontend/src/MemberDetail.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

sessions_pattern = r'<div className="bg-gray-200/30 p-4 rounded-xl border border-gray-200/50">\s*<p className="text-sm text-gray-500 mb-1">Sessions</p>'
sessions_repl = r"""<div className={`p-4 rounded-xl border ${latestSub.total_sessions > 0 && latestSub.attended_sessions >= latestSub.total_sessions ? 'bg-rose-500/10 border-rose-500/20' : 'bg-emerald-500/10 border-emerald-500/20'}`}>
                <p className="text-sm text-gray-500 mb-1">Sessions</p>"""

validity_pattern = r'<div className="bg-gray-200/30 p-4 rounded-xl border border-gray-200/50">\s*<p className="text-sm text-gray-500 mb-1">Validity Period</p>'
validity_repl = r"""<div className={`p-4 rounded-xl border ${new Date(latestSub.end_date) < new Date() ? 'bg-rose-500/10 border-rose-500/20' : 'bg-emerald-500/10 border-emerald-500/20'}`}>
                <p className="text-sm text-gray-500 mb-1">Validity Period</p>"""

content = re.sub(sessions_pattern, sessions_repl, content)
content = re.sub(validity_pattern, validity_repl, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated MemberDetail.jsx")
