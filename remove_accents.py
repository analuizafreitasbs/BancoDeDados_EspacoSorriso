import unicodedata
from pathlib import Path

def remove_accents(text):
    """Remove accents from text while preserving structure."""
    if isinstance(text, str):
        nfkd = unicodedata.normalize('NFKD', text)
        return ''.join([c for c in nfkd if not unicodedata.combining(c)])
    return text

P = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\BancoDeDadosEspacoSorriso.txt")
s = P.read_text(encoding='utf-8')
s_clean = remove_accents(s)
P.write_text(s_clean, encoding='utf-8')
print('Acentos removidos de', P)
