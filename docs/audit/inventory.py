"""Rebuild a static inventory without importing or executing application code."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / 'srcs/requirements/app'
OUT = Path(__file__).resolve().parent


def generate():
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    paths = sorted({ROOT / n for n in names if n.endswith('.py') and n.startswith('srcs/requirements/app/')})
    definitions, calls, modules = [], [], []
    for path in paths:
        source = path.read_text()
        tree = ast.parse(source)
        relative = str(path.relative_to(ROOT))
        modules.append({'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

        class Visitor(ast.NodeVisitor):
            stack = []

            def visit_ClassDef(self, node):
                self.stack.append(node.name)
                self.generic_visit(node)
                self.stack.pop()

            def visit_FunctionDef(self, node):
                qualified = '.'.join(self.stack + [node.name])
                doc = ast.get_docstring(node)
                definitions.append({'path': relative, 'line': node.lineno, 'end_line': node.end_lineno,
                                    'name': node.name, 'qualified': qualified,
                                    'signature': ast.unparse(node.args),
                                    'role_documented': doc or None,
                                    'test': '/tests/' in relative,
                                    'operations': sorted({ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)})})
                self.stack.append(node.name)
                self.generic_visit(node)
                self.stack.pop()

            visit_AsyncFunctionDef = visit_FunctionDef

            def visit_Call(self, node):
                name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else None
                if name:
                    calls.append({'name': name, 'expression': ast.unparse(node.func), 'path': relative,
                                  'line': node.lineno, 'caller': '.'.join(self.stack) or '<module>'})
                self.generic_visit(node)

        Visitor().visit(tree)
    for entry in definitions:
        entry['candidate_usages'] = [c for c in calls if c['name'] == entry['name']]
    payload = {'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'scope': 'Working tree, including non-ignored untracked Python files',
               'limitations': 'Name matching only: aliases, callbacks and dynamic dispatch need manual verification. No candidate does not prove dead code.',
               'modules': modules, 'definitions': definitions}
    (OUT / 'functions.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    lines = ['# Inventaire des fonctions Intelium', '',
             f'{len(modules)} fichiers Python, {len(definitions)} fonctions ou méthodes, dont {sum(d["test"] for d in definitions)} dans les tests.', '',
             'Régénération depuis la racine : `python3 docs/audit/inventory.py`.', '',
             'Les usages sont des candidats par nom, pas un graphe résolu. Les constructeurs, alias, callbacks et méthodes polymorphes nécessitent une lecture manuelle. Les opérations incluent celles des fonctions imbriquées. Les rôles proviennent des docstrings ; leur absence est signalée. Le JSON fournit signatures, opérations et tous les usages candidats.', '']
    for module in modules:
        relative = module['path']
        lines += ['## ' + relative.removeprefix('srcs/requirements/app/'), '']
        for d in [d for d in definitions if d['path'] == relative]:
            role = ' '.join((d['role_documented'] or 'Rôle non documenté ; consulter les opérations et le corps de la fonction.').split())
            link = '../../' + relative + '#L' + str(d['line'])
            lines += [f'- [`{d["qualified"]}`]({link}) — {role}',
                      f'  Appels effectués : {", ".join(d["operations"]) or "aucun appel explicite"}. Usages candidats : {len(d["candidate_usages"])}.']
        lines += ['']
    (OUT / 'FUNCTIONS.md').write_text('\n'.join(lines).rstrip() + '\n')
    print(f'{len(modules)} modules; {len(definitions)} definitions')


if __name__ == '__main__':
    generate()
