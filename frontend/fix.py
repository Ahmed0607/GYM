import os

files = ['src/Dashboard.jsx']
reps = {
    'الباقة': 'Package',
    'السعر': 'Price',
    'تصفية': 'Filter',
    'المالية': 'Finances',
    'الأيام المتبقية': 'Days Left', # If I broke anything else?
}

for f in files:
    if os.path.exists(f):
        content = open(f, encoding='utf-8').read()
        for ar, en in reps.items():
            content = content.replace(ar, en)
        open(f, 'w', encoding='utf-8').write(content)
print('Reverted unsafe translations in Dashboard')
