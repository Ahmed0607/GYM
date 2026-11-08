import os
reps = {
    'src/App.jsx': [
        ('>Edit<', '>تعديل<'),
        ('>Save<', '>حفظ<'),
        ('>Cancel<', '>إلغاء<'),
        ('No Receptionist', 'بدون موظف استقبال'),
    ],
    'src/Dashboard.jsx': [
        ('Failed to load dashboard.', 'فشل تحميل لوحة التحكم.'),
        ('No check-ins today yet.', 'لا توجد عمليات دخول اليوم.'),
        ('>Owed<', '>مدين<'),
        ('No members currently owe money.', 'لا يوجد أعضاء عليهم ديون حالياً.'),
        ('>Expiry<', '>تاريخ الانتهاء<'),
        ('>Paid<', '>المدفوع<'),
        ('Sessions (blank = unlimited)', 'جلسات (فارغ = غير محدود)'),
        ('>Create<', '>إنشاء<'),
        ('>Cancel<', '>إلغاء<'),
        ('>Sessions<', '>الجلسات<'),
        ('>Unlimited<', '>غير محدود<'),
        ('>Receptionists<', '>موظفو الاستقبال<'),
        ('>ID<', '>رقم<'),
        ('>Calculate<', '>حساب<'),
        ('>Salaries<', '>رواتب<'),
        ('Repairs & Maintenance', 'إصلاح وصيانة'),
        ('>Bills<', '>فواتير<'),
        ('>Bill<', '>فاتورة<'),
        ('>Pay Day<', '>يوم الدفع<'),
        ('/ month', '/ شهر'),
        ('Last Paid:', 'آخر دفعة:'),
        ('Bonus:', 'مكافأة:'),
        ('Deduct:', 'خصم:'),
        ('>Apply<', '>تطبيق<'),
    ],
    'src/MemberDetail.jsx': [
        ('>Save<', '>حفظ<'),
        ('>Pay Debt<', '>سداد الدين<'),
        ('>Renew<', '>تجديد<'),
        ('>Delete<', '>حذف<'),
        ('>Record Payment<', '>تسجيل الدفعة<'),
        ('Current Debt:', 'الدين الحالي:'),
        ('>Confirm Payment<', '>تأكيد الدفع<'),
        ('Renew / Change Subscription', 'تجديد / تغيير الاشتراك'),
        ('>Required<', '>مطلوب<'),
        ('>Optional<', '>اختياري<'),
        ('>Amount Paid Today<', '>المبلغ المدفوع اليوم<'),
        ('>Will Owe<', '>سيتبقى (دين)<'),
        ('>Apply New Subscription<', '>تطبيق الاشتراك الجديد<'),
        ('>Yes, Delete<', '>نعم، احذف<'),
        ('Current Subscription', 'الاشتراك الحالي'),
        ('>Packages<', '>الباقات<'),
        ('Validity Period', 'فترة الصلاحية'),
        ('Financials', 'المالية'),
        ('No active subscription found.', 'لا يوجد اشتراك نشط.'),
        ('No attendance records', 'لا يوجد سجل حضور'),
    ],
    'src/Members.jsx': [
        ('>Members<', '>الأعضاء<'),
        ('Browse, search, and manage all gym members', 'تصفح وابحث وقم بإدارة جميع أعضاء الصالة'),
        ('>Clear<', '>مسح<'),
    ],
    'src/Onboarding.jsx': [
        ('>Lady<', '>سيدة<'),
        ('>Kid<', '>طفل<'),
        ('No packages available. Admin needs to configure packages in the Dashboard first.', 'لا توجد باقات متاحة. يجب على المسؤول إعداد الباقات في لوحة التحكم أولاً.'),
        ('>Create Member<', '>إنشاء عضو<'),
    ],
    'src/Reception.jsx': [
        ('>Reception<', '>الاستقبال<'),
        ('Scan ID or search name to check in', 'امسح البطاقة أو ابحث بالاسم لتسجيل الدخول'),
        ('Member Check-in', 'دخول عضو'),
        ('>Guest<', '>زائر<'),
        ('Sessions Attended', 'الجلسات المحضورة'),
        ('>Validity<', '>الصلاحية<'),
        ('>Financials<', '>المالية<'),
        ('No attendance history', 'لا يوجد سجل حضور'),
    ]
}
for f, replacements in reps.items():
    if not os.path.exists(f): continue
    content = open(f, encoding='utf-8').read()
    for en, ar in replacements:
        content = content.replace(en, ar)
    open(f, 'w', encoding='utf-8').write(content)
print('Done secondary translations')
