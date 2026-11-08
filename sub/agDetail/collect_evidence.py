"""Extract existing algorithm traces for documentation; never run a solver."""
import ast
import hashlib
import json
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = [
    'sub/stage11/run_plan_v2.py', 'sub/stage11/worker_v2.py',
    'sub/stage9/balanced_bound.py', 'sub/stage9/demand_balanced.py',
    'sub/stage9/cg_balanced.py', 'sub/stage9/economic_bound.py',
    'sub/line_cg.py', 'sub/stage3/persistent_line.py',
    'sub/stage6/profile_pp.py', 'sub/stage6/resource_dp.py',
    'sub/validate.py', 'sub/stage2/stage2_verify.py',
    'sub/stage7/verify7.py', 'sub/stage9/verify_economic.py',
    'code/milp/model.py', 'code/dwcg/bp_solution.py',
    'code/dwcg/node_state.py', 'code/solver_backend.py',
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_case(row):
    path = ROOT / row['source_certificate']
    raw = path.read_bytes()
    assert sha(raw) == row['certificate_sha256'], path
    result = json.loads(zlib.decompress(raw))
    base = result['base_result']
    cg = base['cg']
    return {
        'case': row['case'], 'source_certificate': path.relative_to(ROOT).as_posix(),
        'certificate_sha256': sha(raw), 'recorded_end_to_end_seconds': row['seconds'],
        'result': {k: result.get(k) for k in ('status', 'global_lower_bound',
                    'global_upper_bound', 'global_integer_optimal_proven', 'profile_calls')},
        'cg': {k: cg.get(k) for k in ('status', 'termination_reason', 'lower_bound',
                    'upper_bound', 'lp_optimal_proven', 'columns', 'pricing_calls')},
        'history': [{
            'iteration': h['iteration'], 'phase': h['phase'],
            'rmp_objective': h['rmp']['objective'], 'artificials': h['rmp']['artificials'],
            'duals': h['rmp']['duals'], 'complete_exact_pricing': h['complete_exact_pricing'],
            'pricing_status': [p['status'] for p in h['pricing']],
            'reduced_costs': [p['reduced_cost'] for p in h['pricing']],
            'repaired_upper_bound': h['repaired_upper_bound'], 'added_columns': len(h['added']),
            'phase_transition': h['phase_transition'],
        } for h in cg['history']],
    }


def main():
    files = {}
    for name in SOURCES:
        raw = (ROOT / name).read_bytes()
        tree = ast.parse(raw.decode('utf-8-sig'))
        files[name] = {'sha256': sha(raw), 'definitions': {
            node.name: node.lineno for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.ClassDef))}}
    selected = {'tasks080_lines04_conflict_candidate_seed32', 'tasks120_lines06_ratio80_seed34'}
    cases = []
    for name in ('formal600', 'robust180'):
        for row in json.loads((ROOT / f'essay/myEssay/data/{name}.json').read_bytes()):
            if row['method'] == 'balanced_bound' and row['case'] in selected:
                cases.append(read_case(row))
    assert len(cases) == 2
    gantt_path = ROOT / 'essay/add/gantt_demo_n20_L2/cg_result.json'
    gantt_raw = gantt_path.read_bytes()
    manifest = (gantt_path.parent / 'SHA256SUMS.txt').read_text(encoding='utf-8')
    expected = dict((name, digest) for digest, name in
                    (line.split('  ', 1) for line in manifest.splitlines()))
    assert sha(gantt_raw) == expected[gantt_path.relative_to(ROOT).as_posix()]
    gantt = json.loads(gantt_raw)
    cg = gantt['base_result']['cg']
    example = {
        'source': gantt_path.relative_to(ROOT).as_posix(), 'sha256': sha(gantt_raw),
        'objective': gantt['global_lower_bound'], 'upper_bound': gantt['global_upper_bound'],
        'status': gantt['status'], 'termination_reason': cg['termination_reason'],
        'cg_history_records': len(cg['history']), 'pricing_calls': cg['pricing_calls'],
        'witness': gantt['witness'],
    }
    (HERE / 'SOURCE_INDEX.json').write_text(json.dumps(files, ensure_ascii=False, indent=2), encoding='utf-8')
    (HERE / 'evidence_summary.json').write_text(json.dumps({
        'scope': 'Read-only extraction of existing evidence and byte-hash checks; no new solve or independent optimality replay.',
        'cases': cases, 'gantt_example': example,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print('PASS: indexed 18 source files; verified and extracted two archived certificates and the Gantt result')


if __name__ == '__main__':
    main()
