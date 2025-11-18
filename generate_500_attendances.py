import random
from datetime import date, timedelta
from pathlib import Path

OUT = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\all_rel.txt")
random.seed(42)

# Basic catalogs
procedures = [
    (1, 'Limpeza (Profilaxia)', 'Remoção de placa e polimento', 'Clínico'),
    (2, 'Restauração', 'Restauração de cárie', 'Clínico'),
    (3, 'Canal (1 canal)', 'Tratamento endodôntico de 1 canal', 'Clínico'),
    (4, 'Clareamento', 'Clareamento em consultório', 'Clínico'),
    (5, 'Consulta Inicial', 'Avaliação clínica', 'Clínico'),
    (6, 'Extração Simples', 'Remoção de dente permanente', 'Clínico'),
    (7, 'Aparelho - Instalação', 'Instalação de aparelho fixo', 'Ortodôntico'),
    (8, 'Ajuste Aparelho', 'Ajustes periódicos do aparelho', 'Ortodôntico'),
]

dentists = [
    ("10101010101", "Dr. Juvenildo Silva Ferreira", "CRO1234", "BA", "Clínico Geral"),
    ("20202020202", "Dra. Isis Carolina", "CRO5678", "BA", "Ortodôntico"),
]

secretarias = [("90011122233", "Jaqueline Rocha")]

# Ensure specific patients exist
fixed_patients = [
    ("10000010001", "ana.luiza@example.com", "Ana Luiza"),
    ("10000010002", "joao.vitorlemos@example.com", "João Vitor Lemos"),
    ("10000010003", "grazielly.barros@example.com", "Grazielly Barros"),
    ("10000010004", "bruno.campos@example.com", "Bruno Campos"),
]

# Generate extra patients to reach a pool
num_patients = 200
patients = []
# add fixed
for cpf, email, name in fixed_patients:
    patients.append((cpf, email, name, 'BA', 'Rua Modelo', 'Centro', '45000000', str(random.randint(1,999)), 'Vitória da Conquista'))

start_cpf = 10000020000
for i in range(num_patients - len(fixed_patients)):
    cpf = str(start_cpf + i)
    email = f'user{1000+i}@example.com'
    name = f'Paciente_{i+1}'
    patients.append((cpf, email, name, 'BA', 'Rua Aleatória', 'Bairro', f'{45000000 + i%1000}', str(random.randint(1,999)), 'Vitória da Conquista'))

# Telephones
telephones = []
for p in patients:
    cpf = p[0]
    phone = f"(77){random.randint(90000,99999)}-{random.randint(1000,9999):04d}"
    telephones.append((cpf, phone))

# Generate 500 atendimentos
num_atend = 500
atendimentos = []
items = []
pagamentos = []

# date range 2024-01-01 to 2025-11-01
start_date = date(2024,1,1)
end_date = date(2025,11,1)
delta_days = (end_date - start_date).days

for aid in range(1, num_atend+1):
    d = start_date + timedelta(days=random.randint(0, delta_days))
    data_s = d.isoformat()
    obs = random.choice(['Consulta', 'Retorno', 'Urgência', 'Procedimento programado', 'Atendimento agendado'])
    valor_total = 0.0
    paciente = random.choice(patients)[0]
    secretaria = secretarias[0][0]
    parcelas = random.choice([1,1,1,2,3])
    tipo = random.choice(['Presencial','Remoto'])
    atendimentos.append((aid, data_s, obs, round(valor_total,2), parcelas, tipo, paciente, secretaria))
    # items 1-3
    num_items = random.choice([1,1,2])
    for it in range(num_items):
        proc = random.choice(procedures)
        proc_id, proc_name, proc_desc, proc_type = proc
        dent = random.choice(dentists)
        cpf_dent = dent[0]
        valor_unit = round(random.uniform(50,800),2)
        qtd = 1
        desconto = 0.0
        # commission percent
        if proc_type.lower().startswith('clínico') or 'clinico' in proc_type.lower():
            comm_pct = 0.5
        else:
            comm_pct = 0.35
        comissao = round(valor_unit * com_pct if (com_pct := comm_pct) else 0.0,2)
        valor_total += valor_unit * qtd - desconto
        items.append((aid, proc_id, cpf_dent, comissao, qtd, valor_unit, desconto))
    # update valorTotal in atendimentos list (replace last tuple)
    atendimentos[-1] = (aid, data_s, obs, round(valor_total,2), parcelas, tipo, paciente, secretaria)
    # pagamento
    idpag = aid  # one payment per atendimento, idPagamento same as atendimento for simplicity
    taxa = 0.0
    forma = random.choice(['Dinheiro','Cartão de Débito','Cartão de Crédito'])
    if forma == 'Cartão de Débito':
        taxa = round(0.02 * valor_total,2)  # clinic/dentist bear
    elif forma == 'Cartão de Crédito':
        taxa = round(0.03 * valor_total,2)  # passed to patient, still record
    valor_liq = round(valor_total - taxa,2)
    pagamentos.append((aid, idpag, data_s, round(valor_total,2), taxa, valor_liq, forma))

# Write out in .rel format
lines = []
lines.append('group: algebra')
lines.append('')

# Paciente
lines.append('Paciente = {')
lines.append('\tCPF_Paciente:string, email:string, nome:string, endereco_UF:string, endereco_rua:string, endereco_bairro:string, endereco_CEP:string, endereco_numero:string, endereco_cidade:string')
for p in patients:
    cpf,email,name,uf,rua,bairro,cep,numero,cidade = p
    lines.append(f'"{cpf}", "{email}", "{name}", "{uf}", "{rua}", "{bairro}", "{cep}", "{numero}", "{cidade}"')
lines.append('}')
lines.append('')

# Telefone_paciente
lines.append('Telefone_paciente = {')
lines.append('\tCPF_Paciente:string, telefone:string')
for t in telephones:
    cpf, tel = t
    lines.append(f'"{cpf}", "{tel}"')
lines.append('}')
lines.append('')

# Secretaria
lines.append('Secretaria = {')
lines.append('\tCPF_Secretaria:string, nome:string')
for s in secretarias:
    lines.append(f'"{s[0]}", "{s[1]}"')
lines.append('}')
lines.append('')

# Dentista
lines.append('Dentista = {')
lines.append('\tCPF_Dentista:string, nome:string, CRO:string, croUF:string, especialidade:string')
for d in dentists:
    lines.append(f'"{d[0]}", "{d[1]}", "{d[2]}", "{d[3]}", "{d[4]}"')
lines.append('}')
lines.append('')

# Procedimento
lines.append('Procedimento = {')
lines.append('\tidProcedimento:number, descricao:string, nome:string, tipoProcedimento:string')
for pr in procedures:
    lines.append(f'{pr[0]}, "{pr[2]}", "{pr[1]}", "{pr[3]}"')
lines.append('}')
lines.append('')

# Atendimento
lines.append('Atendimento = {')
lines.append('\tidAtendimento:number, data:date, observacao:string, valorTotal:number, parcelas:number, tipoAtendimento:string, CPF_Paciente:string, CPF_Secretaria:string')
for a in atendimentos:
    aid,data_s,obs,vt,parcelas,tipo,cpf_p,cpf_s = a
    lines.append(f'{aid}, "{data_s}", "{obs}", {vt}, {parcelas}, "{tipo}", "{cpf_p}", "{cpf_s}"')
lines.append('}')
lines.append('')

# ItemAtendimento
lines.append('ItemAtendimento = {')
lines.append('\tidAtendimento:number, idProcedimento:number, CPF_Dentista:string, comissaoDentista:number, qtd:number, valorUnit:number, descontoItem:number')
for it in items:
    aid,pid,cpf_d,com,qtd,vu,des = it
    lines.append(f'{aid}, {pid}, "{cpf_d}", {com}, {qtd}, {vu}, {des}')
lines.append('}')
lines.append('')

# Pagamento
lines.append('Pagamento = {')
lines.append('\tidAtendimento:number, idPagamento:number, dataRecebimento:date, valorBruto:number, taxaCartao:number, valorLiquido:number, formaPagamento:string')
for pg in pagamentos:
    aid,idp,data_s,br,taxa,vl,forma = pg
    lines.append(f'{aid}, {idp}, "{data_s}", {br}, {taxa}, {vl}, "{forma}"')
lines.append('}')
lines.append('')

OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('Escrito', OUT, 'com', num_atend, 'atendimentos')
