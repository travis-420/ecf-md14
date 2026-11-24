"""EXPLORATORY minimizer study 2 (not a gate attempt). Assemble the results section from a prose template and
generated table logs: every '{{FILE:<path relative to tier2_explore2>}}' line is replaced by that file's contents
verbatim, so tables are pasted from logs, never retyped.
Usage: python assemble2.py <template.md> <out.md>
"""
import re, sys, os
E = '/Users/420-420/ecf-md14/fullplanck/tier2_explore2'
src = open(sys.argv[1]).read()
out = re.sub(r'\{\{FILE:([^}]+)\}\}', lambda m: open(os.path.join(E, m.group(1))).read().strip('\n'), src)
assert '{{' not in out, 'unresolved placeholder'
open(sys.argv[2], 'w').write(out)
print(f'wrote {sys.argv[2]}: {len(out)} chars')
