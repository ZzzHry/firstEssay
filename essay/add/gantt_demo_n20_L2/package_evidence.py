"""Seal this preview's evidence; run after final rendering and visual checks."""
import hashlib
import json
import platform
import subprocess
from pathlib import Path

import matplotlib
import numpy
import pulp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GIT = Path('C:/Users/Hrychang/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    cg = json.loads((HERE / 'cg_result.json').read_text(encoding='utf-8'))
    compact = json.loads((HERE / 'compact_result.json').read_text(encoding='utf-8'))
    original = ROOT / 'code/data/tasks020_lines02_each10_seed11.json'
    frozen = HERE / 'instance.json'
    assert original.read_bytes() == frozen.read_bytes()
    for r in (cg, compact):
        assert r['demo_metadata']['input_sha256'] == sha(frozen)
    sources = []
    for folder in ('code/milp', 'code/dwcg', 'sub'):
        sources.extend(p for p in (ROOT / folder).rglob('*.py') if '__pycache__' not in p.parts)
    sources.append(ROOT / 'code/solver_backend.py')
    provenance = {
        'solve_baseline_commit': '23182d7d7bf1d1272092d501e380223cdf1a832f',
        'packaging_parent_commit': subprocess.check_output(
            [str(GIT), '-c', f'safe.directory={ROOT.as_posix()}', 'rev-parse', 'HEAD'],
            cwd=ROOT, text=True).strip(),
        'source_hash_scope': 'Solver Python trees hashed at packaging; solver sources unchanged during this figure task.',
        'source_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(sources)},
        'original_input': original.relative_to(ROOT).as_posix(),
        'input_sha256': sha(frozen),
        'python': platform.python_version(),
        'pulp': pulp.__version__,
        'matplotlib': matplotlib.__version__,
        'numpy': numpy.__version__,
        'cplex_version_from_native_logs': '22.1.1.0',
        'solver_settings_from_native_logs': {'threads': 1, 'random_seed': 11},
        'scope': 'Verified small-instance assignment and reconstructed local station-cycle order; no performance comparison.',
        'raw_result_sha256': {p.name: sha(p) for p in (HERE / 'cg_result.json', HERE / 'compact_result.json')},
    }
    (HERE / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    paths = sorted(p for p in HERE.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt' and '__pycache__' not in p.parts)
    paths += sorted(HERE.parent.glob('gantt_tasks020_lines02.*'))
    paths.append(HERE.parent / '.gitattributes')
    (HERE / 'SHA256SUMS.txt').write_text(
        ''.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in paths), encoding='utf-8')
    print(f'PASS: frozen input byte identity and hashes sealed for {len(paths)} files')

if __name__ == '__main__':
    main()
