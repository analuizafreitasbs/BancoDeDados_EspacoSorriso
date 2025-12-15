from pathlib import Path

def fix_rel_format_final(content):
    """Fix the .rel format for Relax compatibility"""
    lines = content.splitlines()
    result = []
    in_relation = False

    for line in lines:
        stripped = line.strip()

        # Keep group header and empty lines
        if stripped == 'group: algebra' or stripped == '':
            result.append(line)
            continue

        # Relation start
        if '=' in line and '{' in line:
            in_relation = True
            result.append(line)
            continue

        # Relation end
        if stripped == '}':
            in_relation = False
            result.append(line)
            continue

        # Header line (contains :type declarations)
        if in_relation and ':' in line and not line.startswith('\t'):
            result.append(line)
            continue

        # Data lines
        if in_relation and line.startswith('\t'):
            # Split by comma and add single quotes around string fields
            parts = line.strip().split(', ')
            fixed_parts = []

            for part in parts:
                part = part.strip()
                # Check if it's a number (no quotes needed)
                try:
                    float(part)
                    fixed_parts.append(part)
                except ValueError:
                    # It's a string, add single quotes
                    fixed_parts.append(f"'{part}'")

            result.append('\t' + ', '.join(fixed_parts))
            continue

        # Other lines
        result.append(line)

    return '\n'.join(result)

# Process the file
P = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\BancoDeDadosEspacoSorriso_no_quotes.txt")
content = P.read_text(encoding='utf-8')
new_content = fix_rel_format_final(content)

# Save as new file
new_file = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\BancoDeDadosEspacoSorriso_relax.txt")
new_file.write_text(new_content, encoding='utf-8')

print(f'Arquivo corrigido criado: {new_file}')
