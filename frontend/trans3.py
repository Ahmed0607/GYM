import os
import re

replacements = {
    'src/MemberDetail.jsx': {
        r'>\s*Save\s*<': '>حفظ<',
        r'>\s*Edit Profile\s*<': '>تعديل الملف الشخصي<',
        r'>\s*Record Payment\s*<': '>تسجيل الدفعة<',
        r'>\s*Confirm Payment\s*<': '>تأكيد الدفع<',
        r'>\s*Apply New Subscription\s*<': '>تطبيق الاشتراك الجديد<',
        r'>\s*Yes, Delete\s*<': '>نعم، احذف<',
        r'>\s*Sessions\s*<': '>جلسات<',
    },
    'src/App.jsx': {
        r'>\s*GLOBAL MOCK TIME:\s*<': '>الوقت الوهمي:<',
        r'>\s*Edit\s*<': '>تعديل<',
        r'>\s*Save\s*<': '>حفظ<',
        r'>\s*Cancel\s*<': '>إلغاء<',
    },
    'src/Dashboard.jsx': {
        r'>\s*Subscription Packages\s*<': '>باقات الاشتراك<',
        r'>\s*Add Package\s*<': '>إضافة باقة<',
        r'>\s*New Package\s*<': '>باقة جديدة<',
        r'>\s*Price \(\$\)\s*<': '>السعر ($)<',
        r'>\s*Create\s*<': '>إنشاء<',
        r'>\s*Cancel\s*<': '>إلغاء<',
        r'>\s*Price\s*<': '>السعر<',
        r'>\s*Actions\s*<': '>إجراءات<',
        r'>\s*Unlimited\s*<': '>غير محدود<',
        r'>\s*Receptionists\s*<': '>موظفو الاستقبال<',
        r'>\s*Calculate\s*<': '>حساب<',
        r'>\s*Clear Filter\s*<': '>مسح التصفية<',
        r'>\s*Salaries\s*<': '>رواتب<',
        r'>\s*Bills\s*<': '>فواتير<',
        r'>\s*Staff Members\s*<': '>الموظفين<',
    },
    'src/Onboarding.jsx': {
        r'>\s*Optional\s*<': '>اختياري<',
    },
    'src/Members.jsx': {
        r'>\s*Clear\s*<': '>مسح<',
    }
}

for file, patterns in replacements.items():
    if not os.path.exists(file): continue
    content = open(file, encoding='utf-8').read()
    for pat, rep in patterns.items():
        content = re.sub(pat, rep, content)
    open(file, 'w', encoding='utf-8').write(content)
print("Done translating remaining text with regex")
