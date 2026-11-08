import os

fixes = {
    'src/Dashboard.jsx': {
        'العضوs': 'Members',
        'إجراءs': 'Actions',
        'duration_أيام': 'duration_days',
    },
    'src/Onboarding.jsx': {
        'لـmData': 'formData',
        'لـm': 'form',
    },
    'src/MemberDetail.jsx': {
        'prمنile': 'profile',
        'Prمنile': 'Profile',
        'total_جلسات': 'total_sessions',
        'attended_جلسات': 'attended_sessions',
    },
    'src/Members.jsx': {
        'handleDeleteمنتهي': 'handleDeleteExpired',
    },
    'src/Reception.jsx': {
        'total_جلسات': 'total_sessions',
        'attended_جلسات': 'attended_sessions',
    }
}

for file, replacements in fixes.items():
    if not os.path.exists(file):
        continue
    content = open(file, encoding='utf-8').read()
    for ar, en in replacements.items():
        content = content.replace(ar, en)
    open(file, 'w', encoding='utf-8').write(content)
print('Fixed variable names')
