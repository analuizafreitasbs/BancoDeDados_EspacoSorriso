from pathlib import Path

def remove_quotes_from_strings(content):
    """Remove double quotes from string fields in .rel format"""
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

        # Process data lines - remove quotes from string fields
        if line.startswith('\t'):
            # Split by comma and remove quotes from each field
            parts = []
            in_quotes = False
            current = ''

            i = 0
            while i < len(line):
                char = line[i]
                if char == '"':
                    in_quotes = not in_quotes
                    # Don't add the quote to current
                elif char == ',' and not in_quotes:
                    parts.append(current.strip())
                    current = ''
                else:
                    current += char
                i += 1

            if current:
                parts.append(current.strip())

            # Rejoin with commas
            result.append('\t' + ', '.join(parts))

        else:
            result.append(line)

    return '\n'.join(result)

# Process the file
P = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\BancoDeDadosEspacoSorriso.txt")
content = P.read_text(encoding='utf-8')
new_content = remove_quotes_from_strings(content)

# Save as new file
new_file = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\BancoDeDadosEspacoSorriso_no_quotes.txt")
new_file.write_text(new_content, encoding='utf-8')

print(f'Arquivo sem aspas criado: {new_file}')
