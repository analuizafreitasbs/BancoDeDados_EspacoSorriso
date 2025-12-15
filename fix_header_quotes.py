from pathlib import Path

def fix_header_quotes(content):
    """Remove single quotes from header lines in .rel format"""
    lines = content.splitlines()
    result = []

    for line in lines:
        # Check if this is a header line (contains :type declarations and starts with tab)
        if line.startswith('\t') and ':' in line and 'string' in line:
            # Remove single quotes from header fields
            line = line.replace("'", "")
        result.append(line)

    return '\n'.join(result)

# Process the file
P = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\BancoDeDadosEspacoSorriso_relax.txt")
content = P.read_text(encoding='utf-8')
new_content = fix_header_quotes(content)

# Save back to the same file
P.write_text(new_content, encoding='utf-8')

print(f'Cabeçalhos corrigidos no arquivo: {P}')
