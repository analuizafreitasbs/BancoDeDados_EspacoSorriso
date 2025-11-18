import re
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

P = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\BancoDeDadosEspacoSorriso.txt")
s = P.read_text(encoding='utf-8')
lines = s.splitlines()

# parse relation blocks
rel_re = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*\{\s*$")
blocks = {}
order = []

i = 0
n = len(lines)
while i < n:
    m = rel_re.match(lines[i])
    if m:
        name = m.group(1)
        order.append((i,name))
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

# helper to parse a CSV-like row (naive split respecting quotes)
import csv

def parse_row(line):
    try:
        row = next(csv.reader([line], skipinitialspace=True))
        return [c.strip() for c in row]
    except Exception:
        return [c.strip() for c in line.split(',')]

# build maps
pacientes = {r[0].strip('"'): r for r in [parse_row(l) for l in blocks['Paciente']['rows']]} if 'Paciente' in blocks else {}
procedimentos = {int(r[0]): r for r in [parse_row(l) for l in blocks['Procedimento']['rows']]} if 'Procedimento' in blocks else {}
dentistas = {r[0].strip('"'): r for r in [parse_row(l) for l in blocks['Dentista']['rows']]} if 'Dentista' in blocks else {}
atendimentos = {int(r[0]): r for r in [parse_row(l) for l in blocks['Atendimento']['rows']]} if 'Atendimento' in blocks else {}
itemat = [parse_row(l) for l in blocks['ItemAtendimento']['rows']] if 'ItemAtendimento' in blocks else []
pagamentos = {int(r[0]): r for r in [parse_row(l) for l in blocks['Pagamento']['rows']]} if 'Pagamento' in blocks else {}

# compute sums per atendimento from items
from collections import defaultdict
sums = defaultdict(Decimal)
for r in itemat:
    # columns: idAtendimento, idProcedimento, CPF_Dentista, comissaoDentista, qtd, valorUnit, descontoItem
    aid = int(r[0])
    qtd = Decimal(r[4])
    valorUnit = Decimal(r[5])
    desconto = Decimal(r[6]) if r[6] != '' else Decimal('0')
    line_total = (valorUnit * qtd) - desconto
    sums[aid] += line_total

# fix atendimentos valorTotal if mismatch > 0.01
fixed_atend = 0
for aid, row in atendimentos.items():
    cur_val = Decimal(row[3])
    calc = sums.get(aid, Decimal('0')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if abs(cur_val - calc) > Decimal('0.01'):
        # update row[3]
        row[3] = str(calc)
        atendimentos[aid] = row
        fixed_atend += 1

# fix pagamentos: expect idAtendimento as first col, idPagamento second
fixed_pag = 0
for pid, row in pagamentos.items():
    aid = int(row[0])
    if aid in atendimentos:
        valorBruto = Decimal(row[3])
        expected = Decimal(atendimentos[aid][3])
        if valorBruto != expected:
            row[3] = str(expected)
            # recompute taxa and valorLiquido based on formaPagamento
            forma = row[6].strip('"')
            if forma == 'Cartão de Débito':
                taxa = (expected * Decimal('0.02')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            elif forma == 'Cartão de Crédito':
                taxa = (expected * Decimal('0.03')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                taxa = Decimal('0.00')
            row[4] = str(taxa)
            row[5] = str((expected - taxa).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            pagamentos[pid] = row
            fixed_pag += 1

# rebuild rows into lines
import io
out_lines = lines.copy()
# replace Atendimento rows
if 'Atendimento' in blocks:
    start = blocks['Atendimento']['start']
    end = blocks['Atendimento']['end']
    new_rows = []
    cols = blocks['Atendimento']['cols']
    for aid in sorted(atendimentos.keys()):
        row = atendimentos[aid]
        # ensure quoting for strings
        row2 = []
        for idx, val in enumerate(row):
            coldef = cols[idx]
            if ':' in coldef and coldef.split(':')[-1].strip().lower() in ('string','date'):
                row2.append(f'"{val.strip().strip("\"")}"')
            else:
                row2.append(str(val))
        new_rows.append('\t' + ', '.join(row2))
    # splice
    out_lines = out_lines[:start+2] + new_rows + out_lines[end:]

# replace Pagamento rows
if 'Pagamento' in blocks:
    # find new positions since file changed length; recalc positions
    s = '\n'.join(out_lines).splitlines()
    # find pagamento block
    start = None; end = None
    for i,l in enumerate(s):
        if l.strip().startswith('Pagamento = {'):
            start = i
            break
    if start is not None:
        for j in range(start+1, len(s)):
            if s[j].strip() == '}':
                end = j
                break
    if start is not None and end is not None:
        new_rows = []
        cols = blocks['Pagamento']['cols']
        for pid in sorted(pagamentos.keys()):
            row = pagamentos[pid]
            row2 = []
            for idx,val in enumerate(row):
                coldef = cols[idx]
                if ':' in coldef and coldef.split(':')[-1].strip().lower() in ('string','date'):
                    row2.append(f'"{val.strip().strip("\"")}"')
                else:
                    row2.append(str(val))
            new_rows.append('\t' + ', '.join(row2))
        s = s[:start+2] + new_rows + s[end:]
        out_lines = s

P.write_text('\n'.join(out_lines) + '\n', encoding='utf-8')
print('Fixed', fixed_atend, 'Atendimento rows and', fixed_pag, 'Pagamento rows in', P)
