import re

def update_status_color(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update getStatusColor function
    status_pattern = r"case 'Active': return 'text-emerald-400 bg-emerald-400/10 border-emerald-500/20';\s*case 'Owed Money': return 'text-amber-400 bg-amber-400/10 border-amber-500/20';\s*case 'Expired': return 'text-rose-400 bg-rose-400/10 border-rose-500/20';"
    new_status = """case 'Active': return 'text-white bg-green-600 border-green-700';
      case 'Owed Money': return 'text-white bg-amber-500 border-amber-600';
      case 'Expired': return 'text-white bg-red-600 border-red-700';"""
    
    content = re.sub(status_pattern, new_status, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Update Members.jsx
update_status_color('C:/Users/DELL/Desktop/GYM/frontend/src/Members.jsx')

# Update Reception.jsx
with open('C:/Users/DELL/Desktop/GYM/frontend/src/Reception.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

sessions_pattern = r'<div className=\{`p-4 rounded-xl border \$\{sub\.total_sessions > 0 && sub\.attended_sessions >= sub\.total_sessions \? \'bg-rose-500/10 border-rose-500/20\' : \'bg-emerald-500/10 border-emerald-500/20\'\}`\}>\s*<p className="text-sm text-gray-500 mb-1">Sessions Attended</p>\s*<p className="font-semibold text-black">\s*<span className="text-black">\{sub\.attended_sessions\}</span>\s*<span className="text-gray-500 mx-1">/</span>\s*\{sub\.total_sessions \|\| \'∞\'\}\s*</p>\s*</div>'
sessions_repl = r"""<div className={`p-4 rounded-xl border ${sub.total_sessions > 0 && sub.attended_sessions >= sub.total_sessions ? 'bg-red-600 border-red-700 text-white' : 'bg-green-600 border-green-700 text-white'}`}>
                        <p className="text-sm text-white/80 mb-1">Sessions Attended</p>
                        <p className="font-semibold text-white">
                          <span className="text-white">{sub.attended_sessions}</span>
                          <span className="text-white/80 mx-1">/</span>
                          {sub.total_sessions || '∞'}
                        </p>
                      </div>"""

validity_pattern = r'<div className=\{`p-4 rounded-xl border \$\{new Date\(sub\.end_date\) < new Date\(\) \? \'bg-rose-500/10 border-rose-500/20\' : \'bg-emerald-500/10 border-emerald-500/20\'\}`\}>\s*<p className="text-sm text-gray-500 mb-1">Validity</p>\s*<div className="font-semibold text-black text-sm">\s*\{format\(new Date\(sub\.start_date\), \'MMM d, yyyy\'\)\} — \{format\(new Date\(sub\.end_date\), \'MMM d, yyyy\'\)\}\s*</div>\s*</div>'
validity_repl = r"""<div className={`p-4 rounded-xl border ${new Date(sub.end_date) < new Date() ? 'bg-red-600 border-red-700 text-white' : 'bg-green-600 border-green-700 text-white'}`}>
                        <p className="text-sm text-white/80 mb-1">Validity</p>
                        <div className="font-semibold text-white text-sm">
                          {format(new Date(sub.start_date), 'MMM d, yyyy')} — {format(new Date(sub.end_date), 'MMM d, yyyy')}
                        </div>
                      </div>"""

content = re.sub(sessions_pattern, sessions_repl, content)
content = re.sub(validity_pattern, validity_repl, content)

# Also update status colors in Reception.jsx
status_pattern = r"case 'Active': return 'text-emerald-400 bg-emerald-400/10 border-emerald-500/20';\s*case 'Owed Money': return 'text-amber-400 bg-amber-400/10 border-amber-500/20';\s*case 'Expired': return 'text-rose-400 bg-rose-400/10 border-rose-500/20';"
new_status = """case 'Active': return 'text-white bg-green-600 border-green-700';
      case 'Owed Money': return 'text-white bg-amber-500 border-amber-600';
      case 'Expired': return 'text-white bg-red-600 border-red-700';"""
content = re.sub(status_pattern, new_status, content)

with open('C:/Users/DELL/Desktop/GYM/frontend/src/Reception.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

# Update MemberDetail.jsx
with open('C:/Users/DELL/Desktop/GYM/frontend/src/MemberDetail.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

sessions_md_pattern = r'<div className=\{`p-4 rounded-xl border \$\{latestSub\.total_sessions > 0 && latestSub\.attended_sessions >= latestSub\.total_sessions \? \'bg-rose-500/10 border-rose-500/20\' : \'bg-emerald-500/10 border-emerald-500/20\'\}`\}>\s*<p className="text-sm text-gray-500 mb-1">Sessions</p>\s*<p className="font-semibold text-black">\s*<span className="text-cyan-400">\{latestSub\.attended_sessions\}</span>\s*<span className="text-gray-500 mx-1">/</span>\s*\{latestSub\.total_sessions \|\| \'∞\'\}\s*</p>\s*</div>'
sessions_md_repl = r"""<div className={`p-4 rounded-xl border ${latestSub.total_sessions > 0 && latestSub.attended_sessions >= latestSub.total_sessions ? 'bg-red-600 border-red-700 text-white' : 'bg-green-600 border-green-700 text-white'}`}>
                <p className="text-sm text-white/80 mb-1">Sessions</p>
                <p className="font-semibold text-white">
                  <span className="text-white">{latestSub.attended_sessions}</span>
                  <span className="text-white/80 mx-1">/</span>
                  {latestSub.total_sessions || '∞'}
                </p>
              </div>"""

validity_md_pattern = r'<div className=\{`p-4 rounded-xl border \$\{new Date\(latestSub\.end_date\) < new Date\(\) \? \'bg-rose-500/10 border-rose-500/20\' : \'bg-emerald-500/10 border-emerald-500/20\'\}`\}>\s*<p className="text-sm text-gray-500 mb-1">Validity Period</p>\s*<p className="font-semibold text-black text-sm">\s*\{format\(new Date\(latestSub\.start_date\), \'MMM d, yyyy\'\)\} — \{format\(new Date\(latestSub\.end_date\), \'MMM d, yyyy\'\)\}\s*</p>\s*</div>'
validity_md_repl = r"""<div className={`p-4 rounded-xl border ${new Date(latestSub.end_date) < new Date() ? 'bg-red-600 border-red-700 text-white' : 'bg-green-600 border-green-700 text-white'}`}>
                <p className="text-sm text-white/80 mb-1">Validity Period</p>
                <p className="font-semibold text-white text-sm">
                  {format(new Date(latestSub.start_date), 'MMM d, yyyy')} — {format(new Date(latestSub.end_date), 'MMM d, yyyy')}
                </p>
              </div>"""

content = re.sub(sessions_md_pattern, sessions_md_repl, content)
content = re.sub(validity_md_pattern, validity_md_repl, content)
content = re.sub(status_pattern, new_status, content)

with open('C:/Users/DELL/Desktop/GYM/frontend/src/MemberDetail.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated solid colors")
