from pathlib import Path
import re
import csv
from collections import defaultdict

P = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\BancoDeDadosEspacoSorriso.txt")
s = P.read_text(encoding='utf-8')
lines = s.splitlines()

# Parse relation blocks
rel_re = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*\{\s*$")
blocks = {}
i = 0
n = len(lines)

while i < n:
    m = rel_re.match(lines[i])
    if m:
        name = m.group(1)
        header = lines[i+1].strip()
        cols = [c.strip() for c in header.split(',') if c.strip()]
        rows = []
        j = i+2
        while j < n and lines[j].strip() != '}':
            if lines[j].strip():
                rows.append(lines[j].rstrip())
            j += 1
        blocks[name] = {'start': i, 'header': header, 'cols': cols, 'rows': rows, 'end': j}
        i = j
    i += 1

# Helper to parse CSV
def parse_row(line):
    try:
        row = next(csv.reader([line], skipinitialspace=True))
        return [c.strip() for c in row]
    except Exception:
        return [c.strip() for c in line.split(',')]

# Build maps
procedimentos = {}
if 'Procedimento' in blocks:
    for r in [parse_row(l) for l in blocks['Procedimento']['rows']]:
        if r:
            pid = int(r[0])
            tipo = r[3].strip('"')
            procedimentos[pid] = tipo

# Map cada atendimento ao tipo de procedimento
atend_tipos = defaultdict(set)
if 'ItemAtendimento' in blocks:
    for r in [parse_row(l) for l in blocks['ItemAtendimento']['rows']]:
        if r and len(r) >= 2:
            aid = int(r[0])
            pid = int(r[1])
            proc_type = procedimentos.get(pid, 'Clínico')
            atend_tipos[aid].add(proc_type)

# Update Atendimento rows
atend_rows = []
if 'Atendimento' in blocks:
    for l in blocks['Atendimento']['rows']:
        if l.strip():
            r = parse_row(l)
            if r and len(r) >= 8:
                aid = int(r[0])
                # Determine tipo: if mix of both, prioritize Ortodôntico; else use the one present
                tipos = atend_tipos.get(aid, {'Clínico'})
                if 'Ortodôntico' in tipos:
                    novo_tipo = 'Ortodôntico'
                else:
                    novo_tipo = 'Clínico'
                # Replace tipoAtendimento (position 5, 0-indexed)
                r[5] = f'"{novo_tipo}"'
                # Rebuild row
                new_row = ', '.join(str(x) for x in r)
                atend_rows.append(new_row)

# Rebuild Atendimento block
if 'Atendimento' in blocks and atend_rows:
    start = blocks['Atendimento']['start']
    end = blocks['Atendimento']['end']
    new_lines = lines[:start+2] + ['\t' + row for row in atend_rows] + lines[end:]
    P.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
    print(f'Atualizados {len(atend_rows)} registros de Atendimento com tipoAtendimento (Clínico ou Ortodôntico)')
else:
    print('Atendimento block not found or no rows')
