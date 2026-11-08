import os
import glob

files = glob.glob('src/*.jsx')
for f in files:
    content = open(f, encoding='utf-8').read()
    if 'classالاسم' in content:
        content = content.replace('classالاسم', 'className')
        open(f, 'w', encoding='utf-8').write(content)
        print(f'Fixed classالاسم in {f}')
