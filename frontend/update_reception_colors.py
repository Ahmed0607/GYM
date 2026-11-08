import re

filepath = 'C:/Users/DELL/Desktop/GYM/frontend/src/Reception.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

sessions_pattern = r'<div className="bg-gray-200/30 p-4 rounded-xl border border-gray-200/50">\s*<p className="text-sm text-gray-500 mb-1">Sessions Attended</p>'
sessions_repl = r"""<div className={`p-4 rounded-xl border ${sub.total_sessions > 0 && sub.attended_sessions >= sub.total_sessions ? 'bg-rose-500/10 border-rose-500/20' : 'bg-emerald-500/10 border-emerald-500/20'}`}>
                        <p className="text-sm text-gray-500 mb-1">Sessions Attended</p>"""

validity_pattern = r'<div className="bg-gray-200/30 p-4 rounded-xl border border-gray-200/50">\s*<p className="text-sm text-gray-500 mb-1">Validity</p>'
validity_repl = r"""<div className={`p-4 rounded-xl border ${new Date(sub.end_date) < new Date() ? 'bg-rose-500/10 border-rose-500/20' : 'bg-emerald-500/10 border-emerald-500/20'}`}>
                        <p className="text-sm text-gray-500 mb-1">Validity</p>"""

content = re.sub(sessions_pattern, sessions_repl, content)
content = re.sub(validity_pattern, validity_repl, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated Reception.jsx")
