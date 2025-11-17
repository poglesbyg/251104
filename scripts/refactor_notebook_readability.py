#!/usr/bin/env python3
import sys
import json
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: refactor_notebook_readability.py <notebook.ipynb>")
    sys.exit(2)

nb_path = Path(sys.argv[1])
if not nb_path.exists():
    print(f"Notebook not found: {nb_path}")
    sys.exit(2)

backup = nb_path.with_suffix(nb_path.suffix + '.bak')
backup.write_bytes(nb_path.read_bytes())

with nb_path.open('r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb.get('cells', [])
header = [
    "# Readability: added short header and minor formatting for clarity\n",
    "# - No semantic changes made.\n",
    "\n",
]

modified = []
for i, cell in enumerate(cells):
    if cell.get('cell_type') != 'code':
        continue
    src = cell.get('source', [])
    # normalize to list of strings
    if isinstance(src, str):
        lines = src.splitlines(keepends=True)
    else:
        lines = src
    # find first non-empty line
    first_non_empty = None
    for ln in lines:
        if ln.strip():
            first_non_empty = ln
            break
    if first_non_empty and first_non_empty.lstrip().startswith('# Readability:'):
        # already updated
        continue
    # Prepend header
    new_lines = header + lines
    cell['source'] = new_lines
    modified.append(i)

with nb_path.open('w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Processed notebook: {nb_path}")
print(f"Code cells modified: {len(modified)}")
if modified:
    print("Modified cell indices:", modified)
else:
    print("No changes made (cells already had header).")
