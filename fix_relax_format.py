from pathlib import Path

def fix_rel_format(content):
    """Fix the .rel format for Relax compatibility"""
    lines = content.splitlines()
    result = []

    for line in lines:
        # Skip header lines and relation definitions
        if '=' in line and '{' in line:
            result.append(line)
            continue
        elif line.strip() in ['}', 'group: algebra', '']:
            result.append(line)
            continue
        elif ':' in line and not line.startswith('\t'):  # header line
            result.append(line)
            continue

        # Process data lines
        if line.startswith('\t'):
            # Split by comma and add single quotes around string fields
            parts = line.strip().split(', ')
            fixed_parts = []

            for i, part in enumerate(parts):
                part = part.strip()
                # For string fields, add single quotes
                # Assuming all non-numeric fields are strings
                try:
                    # Try to convert to float/int - if successful, it's a number
                    float(part)
                    fixed_parts.append(part)
                except ValueError:
                    # It's a string, add single quotes
                    fixed_parts.append(f"'{part}'")

            result.append('\t' + ', '.join(fixed_parts))

        else:
            result.append(line)

    return '\n'.join(result)

# Process the file
P = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\BancoDeDadosEspacoSorriso_no_quotes.txt")
content = P.read_text(encoding='utf-8')
new_content = fix_rel_format(content)

# Save as new file
new_file = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\BancoDeDadosEspacoSorriso_relax.txt")
new_file.write_text(new_content, encoding='utf-8')

print(f'Arquivo corrigido criado: {new_file}')
