"""EXPLORATORY minimizer study 2 (not a gate attempt). Fill the prose placeholders («...») of section_template.md
from the parts/ files and the values below, then hand the result to assemble2.py (which pastes {{FILE:...}} logs).
Usage: python fill_section.py <values.json> <out_template.md>"""
import json, sys, os
E = '/Users/420-420/ecf-md14/fullplanck/tier2_explore2'
V = json.load(open(sys.argv[1]))
t = open(os.path.join(E, 'section_template.md')).read()
part = lambda n: open(os.path.join(E, 'parts', n)).read().strip('\n')
t = t.replace('«SUMMARY»', part('summary.md')).replace('«STEP1»', part('step1.md'))
t = t.replace('«STEP2SUMMARY»', part('step2summary.md'))
s34 = part('step34.md').replace('«STEP3BODY»', part('step3body.md')).replace('«STEP4BODY»', part('step4body.md'))
t = t.replace('«STEP3»\n\n«STEP4»', s34)
t = t.replace('«STEP5»', part('step5.md')).replace('«NOTES»', part('notes.md'))
for k, v in V.items():
    assert f'«{k}»' in t, k
    t = t.replace(f'«{k}»', v)
assert '«' not in t, [t[i - 20:i + 30] for i in range(len(t)) if t[i] == '«'][:5]
open(sys.argv[2], 'w').write(t)
print('filled', sys.argv[2], len(t))
