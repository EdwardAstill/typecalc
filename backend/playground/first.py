
from typecalc import parse_document
from pathlib import Path

parent_dir = Path(__file__).parent
text_path = parent_dir / 'calcs.txt'
text = open(text_path, 'r').read()
print(parse_document(text))


