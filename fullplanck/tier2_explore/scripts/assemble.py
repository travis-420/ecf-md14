"""Assemble the exploratory section: insert the markdown tables from logs/tables_<tag>.log (verbatim) into section_draft.md.
Writes section_final.md. Refuses if any @@PLACEHOLDER@@ remains."""
import re, sys
EXP = '/Users/420-420/ecf-md14/fullplanck/tier2_explore'
s = open(f'{EXP}/section_draft.md').read()
for tag, ph in [('step2', '@@TABLES_STEP2@@'), ('step3A', '@@TABLES_STEP3A@@'), ('step3B', '@@TABLES_STEP3B@@')]:
    t = open(f'{EXP}/logs/tables_{tag}.log').read()
    t = t.split(f'\n{tag} vs certified')[0].strip('\n')
    s = s.replace(ph, t)
left = re.findall(r'@@[A-Z0-9_]+@@', s)
if left:
    sys.exit(f'placeholders left: {sorted(set(left))}')
open(f'{EXP}/section_final.md', 'w').write(s)
print('ok', len(s.encode()), 'bytes')
