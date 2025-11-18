import re
import csv
from pathlib import Path

p = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\BancoDeDadosEspacoSorriso.txt")
s = p.read_text(encoding='utf-8')
lines = s.splitlines()

rel_header_re = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*\{\s*$")
allowed_types = {'boolean','date','number','string'}

issues = []
line_no = 0
n = len(lines)

while line_no < n:
    line = lines[line_no]
    m = rel_header_re.match(line)
    if m:
        relname = m.group(1)
        # expect header types next
        if line_no + 1 >= n:
            issues.append((line_no+1, relname, 'Missing header types line'))
            line_no += 1
            continue
        header = lines[line_no+1].strip()
        cols = [c.strip() for c in header.split(',') if c.strip()]
        types = []
        for c in cols:
            if ':' not in c:
                issues.append((line_no+2, relname, f'Column without type: "{c}"'))
                types.append(None)
            else:
                name, typ = c.rsplit(':',1)
                typ = typ.strip().lower()
                if typ not in allowed_types:
                    issues.append((line_no+2, relname, f'Invalid type "{typ}" for column "{name.strip()}"'))
                types.append(typ)
        j = line_no + 2
        while j < n:
            l = lines[j].strip()
            if l == '':
                j += 1
                continue
            if l == '}':
                break
            try:
                row = next(csv.reader([l], skipinitialspace=True))
            except Exception as e:
                issues.append((j+1, relname, 'CSV parse error: '+str(e)))
                j += 1
                continue
            row = [x.strip() for x in row]
            if len(row) != len(types):
                issues.append((j+1, relname, f'Field count mismatch: expected {len(types)}, got {len(row)}'))
            else:
                for idx, (val, typ) in enumerate(zip(row, types)):
                    if typ is None:
                        continue
                    if val == '' or val.upper() == 'NULL':
                        continue
                    if typ == 'number':
                        v = val.strip('"')
                        try:
                            float(v)
                        except:
                            issues.append((j+1, relname, f'Expected number in column {idx+1} but got "{val}"'))
                    elif typ == 'date':
                        v = val.strip('"')
                        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
                            issues.append((j+1, relname, f'Expected date YYYY-MM-DD in column {idx+1} but got "{val}"'))
                    elif typ == 'boolean':
                        v = val.strip('"').lower()
                        if v not in ('true','false','1','0'):
                            issues.append((j+1, relname, f'Expected boolean in column {idx+1} but got "{val}"'))
            j += 1
        line_no = j
    line_no += 1

brace_balance = sum(l.count('{') - l.count('}') for l in lines)
if brace_balance != 0:
    issues.append((None, None, f'Unbalanced braces: net {brace_balance}'))

if not issues:
    print('OK: BancoDeDadosEspacoSorriso.txt parece estar no padrão Relax')
else:
    print(f'Found {len(issues)} issue(s) (showing up to 200):')
    for it in issues[:200]:
        lineno, rel, msg = it
        if lineno:
            print(f'  Line {lineno}: relation={rel} -> {msg}')
        else:
            print(' ', msg)
    
import sys
sys.exit(0 if not issues else 2)
