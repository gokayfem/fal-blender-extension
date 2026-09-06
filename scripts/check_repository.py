"""Check Python syntax, local documentation links, and common publish mistakes."""
import ast
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

root = Path(__file__).resolve().parents[1]
names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=root, text=True).splitlines()
errors = []
for name in sorted(set(names)):
    path = root / name
    if not path.is_file():
        continue
    if path.name.startswith('.env') and path.name != '.env.example':
        errors.append(f'{name}: environment file must not be tracked')
    if path.suffix == '.py':
        try:
            source = path.read_text(encoding='utf-8-sig')
            ast.parse(source, filename=name)
            if path.name != 'check_repository.py' and re.search(r'C:[/\\]Users[/\\]|/Users/[^/]+/', source):
                errors.append(f'{name}: machine-specific home path')
        except (SyntaxError, UnicodeError) as error:
            errors.append(f'{name}: {type(error).__name__}')
    if path.suffix == '.md':
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8-sig')):
            target = unquote(target.split('#')[0].strip('<>'))
            if not target or re.match(r'^[a-z]+:', target):
                continue
            if not (path.parent / target).exists():
                errors.append(f'{name}: broken local link {target}')
    if path.suffix in {'.py', '.md', '.json', '.yml', '.yaml'}:
        text = path.read_text(encoding='utf-8-sig')
        if re.search(r'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}', text):
            errors.append(f'{name}: possible GitHub credential')
if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print(f'Repository checks passed ({len(set(names))} files).')
