from pathlib import Path
src = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\all_rel.txt")
dst = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\BancoDeDadosEspacoSorrso.txt")
# Note: filename corrected if misspelled - ensure we overwrite exact target
# The user's file path is BancoDeDadosEspacoSorrisso.txt (with double 'ss'), so write to that
dst = Path(r"c:\Users\sanal\Downloads\Projeto de banco de dados\BancoDeDadosEspacoSorriso.txt")
text = src.read_text(encoding='utf-8')
dst.write_text(text, encoding='utf-8')
print('Copied', src, '->', dst, ' (bytes:', len(text),')')
