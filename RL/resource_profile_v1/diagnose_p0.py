"""Read-only historical profile diagnosis. No MILP solves or production DP calls."""
from pathlib import Path
from functools import lru_cache
from copy import deepcopy
import argparse, csv, hashlib, json, math, platform, subprocess, sys, time, zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'sub'))
from validate import evaluate_line, check_column, check_witness


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a, b):
    assert (a is None and b is None) or (a is not None and b is not None and abs(a-b) <= 1e-5), (a, b)


def combine(data, table, upper=False):
    """Independent backward recursion over remaining capacities, no production DP."""
    lids = [l['id'] for l in data['lines']]

    @lru_cache(None)
    def visit(k, h, r):
        if k == len(lids):
            return 0., ()
        best, path = -math.inf, ()
        for j, e in enumerate(table[lids[k]]):
            if e['human'] > h or e['robot'] > r:
                continue
            if upper:
                if e['status'] == 'infeasible':
                    continue
                coefficient = math.inf if e['upper_bound'] is None else e['upper_bound']
            else:
                if e['column'] is None:
                    continue
                coefficient = e['column']['profit']
            tail, rest = visit(k+1, h-e['human'], r-e['robot'])
            if tail == -math.inf:
                continue
            value = coefficient + tail
            if value > best:
                best, path = value, ((lids[k], j),) + rest
        return best, path

    value, path = visit(0, data['human_limit'], data['robot_limit'])
    return dict(possible=value != -math.inf,
                value=value if math.isfinite(value) else None,
                bound_status='finite' if math.isfinite(value) else 'unknown' if value == math.inf else 'no_combination',
                path=[dict(line=l, index=j) for l, j in path])


def account(data, table, cg_upper):
    low, up = combine(data, table), combine(data, table, True)
    if low['possible']:
        stations = [s for p in low['path'] for s in table[p['line']][p['index']]['column']['stations']]
        check_witness(data, dict(stations=stations, objective=low['value']), low['value'])
    bounds = [v for v in (up['value'], cg_upper) if v is not None]
    return low, up, min(bounds) if bounds else None


def make_table(data, cg, sources):
    table = {}
    for line in data['lines']:
        lid = line['id']; rows = []
        for h in range(min(len(line['stations']), data['human_limit'])+1):
            for r in range(min(len(line['stations']), data['robot_limit'])+1):
                candidates = [c for c in cg['pool'][lid] if (c['human'], c['robot']) == (h, r)]
                col = deepcopy(max(candidates, key=lambda c: c['profit'])) if candidates else None
                bs = [s['constant']+s['human']*h+s['robot']*r for s in sources[lid]]
                rows.append(dict(human=h, robot=r, status='seeded' if col else 'not_run',
                                 upper_bound=min(bs) if bs else None, column=col, attempts=0))
        table[lid] = rows
    return table


def sources_from_cg(cg):
    sources = {l: [] for l in cg['pool']}
    for c in cg['initialization']:
        b = c['column']['profit'] if c['optimal'] else c['solver'].get('best_bound')
        if b is not None and math.isfinite(b) and abs(b) < 1e19:
            sources[c['line']].append(dict(kind='economic_initialization', constant=b, human=0., robot=0.))
    for row in cg['history']:
        if row['phase'] != 2 or not row['complete_exact_pricing']:
            continue
        d = row['rmp']['duals']
        for c in row['pricing']:
            sources[c['line']].append(dict(kind='complete_phase2_pricing', iteration=row['iteration'],
                constant=d['convexity'][c['line']]+max(0., c['reduced_cost']), human=d['human'], robot=d['robot']))
    return sources


def diagnose(folder):
    data = json.loads((folder/'instance.json').read_bytes())
    r = json.loads(zlib.decompress((folder/'result.json.zlib').read_bytes()))
    b = r['base_result']; cg = b['cg']; lines = {l['id']: l for l in data['lines']}
    for lid, cols in cg['pool'].items():
        for c in cols:
            check_column(lines[lid], c)
    check_witness(data, r['witness'], r['global_lower_bound'])
    sources = sources_from_cg(cg); assert sources == b['bound_sources']
    table = make_table(data, cg, sources); initial = deepcopy(table)
    trace = r['progress_trace']; rows = []
    low0, up0, ub0 = account(data, table, cg['upper_bound'])
    trace_points = {n: next((t for t in trace if t['kind'] == 'profile_account' and t['queries'] == n), None)
                    for n in range(len(b['queries'])+1)}
    for n, q in enumerate(b['queries'], 1):
        low, up, ub = account(data, table, cg['upper_bound'])
        close(up['value'], q['upper_value'])
        choice = q['choice']; e = table[choice['line']][choice['index']]
        assert choice in q['upper_path'] and e['status'] not in ('optimal', 'infeasible')
        path_entries = [table[p['line']][p['index']] for p in q['upper_path']]
        assert len(path_entries) == len(lines) and len({p['line'] for p in q['upper_path']}) == len(lines)
        assert sum(x['human'] for x in path_entries) <= data['human_limit']
        assert sum(x['robot'] for x in path_entries) <= data['robot_limit']
        assert all(x['status'] != 'infeasible' for x in path_entries)
        if up['value'] is not None:
            close(sum(x['upper_bound'] for x in path_entries), up['value'])
        c = q['certificate']; assert c is not None
        assert c['line'] == choice['line'] and c['profile'] == [e['human'], e['robot']]
        assert c['phase'] == 2 and c['human_price'] == c['robot_price'] == c['sigma'] == 0 and c['restrictions'] == []
        col = c['column']; old_col = e['column']; old_upper = e['upper_bound']
        if col:
            check_column(lines[c['line']], col)
            assert (col['human'], col['robot']) == (e['human'], e['robot'])
            close(col['profit'], c['reduced_cost'])
        native = c['solver']; status = c['status']
        assert native['status'] == status and native['optimal'] == c['optimal']
        if status == 'infeasible':
            assert native['native_status'] == 103 and old_col is None
            e.update(status=status, upper_bound=None)
        else:
            if c['optimal']:
                assert col and native['native_status'] in (101, 102)
                close(native['best_bound'], col['profit'])
            if col and (old_col is None or col['profit'] > old_col['profit']):
                e['column'] = col
            bound = col['profit'] if c['optimal'] else native.get('best_bound')
            if bound is not None and math.isfinite(bound) and abs(bound) < 1e19:
                assert native['native_status'] in (101, 102, 107, 108)
                e['upper_bound'] = bound if old_upper is None else min(bound, old_upper)
            e['status'] = status
            if e['column'] is not None and e['upper_bound'] is not None:
                assert e['upper_bound'] >= e['column']['profit']-1e-5
        e['attempts'] += 1
        after, up_after, ub_after = account(data, table, cg['upper_bound'])
        point = trace_points[n]
        if point:
            close(point['lower_bound'], after['value']); close(point['upper_bound'], ub_after)
        lb_gain = None if low['value'] is None or after['value'] is None else after['value']-low['value']
        ub_gain = None if ub is None or ub_after is None else ub-ub_after
        rows.append(dict(query=n, line=choice['line'], human=e['human'], robot=e['robot'],
            attempt=e['attempts'], status=status, native_status=native['native_status'],
            old_local_profit=old_col['profit'] if old_col else None, returned_profit=col['profit'] if col else None,
            old_local_ub=old_upper, new_local_ub=e['upper_bound'],
            new_profile_witness=old_col is None and col is not None,
            local_profit_improved=col is not None and (old_col is None or col['profit'] > old_col['profit']+1e-5),
            lb_before=low['value'], lb_after=after['value'], ub_before=ub, ub_after=ub_after,
            lb_gain=lb_gain, ub_reduction=ub_gain, first_feasible=not low['possible'] and after['possible'],
            observed_account_seconds=point['seconds'] if point else None,
            build_seconds=c['build_seconds'], solve_wrapper_seconds=c['solve_seconds'],
            native_solve_seconds=native['solver_time'], validate_seconds=c['validate_seconds'], query_seconds=c['total_seconds']))
    assert table == b['table']
    low, up, ub = account(data, table, cg['upper_bound'])
    close(low['value'], b['global_lower_bound']); close(ub, b['global_upper_bound'])
    close(up['value'], b['upper_dp']['value'])
    economic = r['economic_evidence']['upper_bound']
    expected_final_ub = min(x for x in (ub, economic) if x is not None)
    close(expected_final_ub, r['global_upper_bound'])
    if r['global_integer_optimal_proven']:
        assert low['value'] is not None and expected_final_ub-low['value'] <= 1e-5
    final_profiles = []
    for lid, line in lines.items():
        stations = [s for s in r['witness']['stations'] if s['line'] == lid]
        v = evaluate_line(line, stations)
        candidates = [e for e in initial[lid] if (e['human'], e['robot']) == (v['human'], v['robot'])]
        seed = candidates[0]['column']; local_gain = None if seed is None else v['profit']-seed['profit']
        final_profiles.append(dict(line=lid, human=v['human'], robot=v['robot'], final_profit=v['profit'],
            present_at_cg_exit=seed is not None, cg_exit_best_profit=seed['profit'] if seed else None,
            profit_gain=local_gain,
            exact_assignment_in_cg_pool=any(c['stations'] == stations for c in cg['pool'][lid])))
    accounting = [t for t in trace if t['kind'] == 'profile_account']
    summary = dict(run=folder.name, tasks=sum(len(l['tasks']) for l in data['lines']), lines=len(lines),
        human_limit=data['human_limit'], robot_limit=data['robot_limit'], cg_status=cg['status'],
        cg_lp_optimal=cg['lp_optimal_proven'], cg_exit_lb=low0['value'], cg_exit_ub=ub0,
        final_lb=r['global_lower_bound'], final_ub=r['global_upper_bound'], integer_proven=r['global_integer_optimal_proven'],
        queries=len(rows), lb_improving_queries=[x['query'] for x in rows if (x['lb_gain'] or 0)>1e-5 or x['first_feasible']],
        ub_improving_queries=[x['query'] for x in rows if (x['ub_reduction'] or 0)>1e-5],
        infeasible_queries=sum(x['status']=='infeasible' for x in rows),
        no_immediate_global_change_queries=[x['query'] for x in rows if not x['first_feasible'] and (x['lb_gain'] or 0)<=1e-5 and (x['ub_reduction'] or 0)<=1e-5],
        query_total_seconds=sum(x['query_seconds'] for x in rows),
        query_native_seconds=sum(x['native_solve_seconds'] for x in rows),
        first_profile_account_seconds=accounting[0]['seconds'] if accounting else None,
        last_profile_account_seconds=accounting[-1]['seconds'] if accounting else None,
        historical_worker_seconds=json.loads((folder/'summary.json').read_bytes())['worker_seconds'],
        cg_timing=cg['timing'], first_verified_integer_seconds=r['first_integer_seconds'],
        final_witness_profiles=final_profiles,
        replay_status='PASS', replay_scope='historical_native_contracts_and_independent_backward_DP_and_data_witness_checks_no_solver_rerun')
    initial_rows = [dict(line=l, human=e['human'], robot=e['robot'], status=e['status'],
        profit=e['column']['profit'] if e['column'] else None, upper_bound=e['upper_bound']) for l, es in initial.items() for e in es]
    return summary, rows, initial_rows


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter(); history = ROOT/'sub/stage13/evidence/robust180'
    plan = json.loads((ROOT/'RL/resource_profile_v1/EVIDENCE_INDEX.json').read_bytes())
    assert all(digest(ROOT/e['path']) == e['sha256'] for e in plan['files'])
    source_checks = {}; artifacts = []; summaries = []; queries = []; initial = []
    for f in sorted(history.glob('*')):
        if f.is_file(): artifacts.append(dict(path=f.relative_to(ROOT).as_posix(), sha256=digest(f), bytes=f.stat().st_size))
    for folder in sorted(history.glob('*__*')):
        if not folder.is_dir(): continue
        s = json.loads((folder/'summary.json').read_bytes())
        assert digest(folder/'instance.json') == s['input_sha256']
        assert digest(folder/'result.json.zlib') == s['evidence_sha256']
        for name, sha in s['source_sha256'].items():
            assert digest(ROOT/name) == sha, name
            source_checks[name] = sha
        for f in sorted(folder.rglob('*')):
            if f.is_file(): artifacts.append(dict(path=f.relative_to(ROOT).as_posix(), sha256=digest(f), bytes=f.stat().st_size))
        if folder.name.endswith('__balanced_bound'):
            paired = history/folder.name.replace('__balanced_bound', '__compact_plain')/'instance.json'
            assert (folder/'instance.json').read_bytes() == paired.read_bytes()
            summary, qs, ins = diagnose(folder); summaries.append(summary)
            queries.extend(dict(run=folder.name, **q) for q in qs)
            initial.extend(dict(run=folder.name, **e) for e in ins)
    def write(name, value):
        (a.output/name).write_bytes((json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode())
    write('diagnostics.json', dict(status='PASS', summaries=summaries, queries=queries, initial_profiles=initial,
        missing_evidence=['No historical first-incumbent timestamps inside individual native profile calls',
                          'No counterfactual query-order outcomes; not inferable from this replay'],
        elapsed_seconds=time.perf_counter()-start))
    write('input_and_evidence_manifest.json', dict(artifacts=artifacts, verified_historical_sources=source_checks,
        plan_source_files_verified=len(plan['files']), paired_input_byte_checks=4))
    import importlib.metadata
    sys.path.insert(0, str(ROOT/'code'))
    from solver_backend import load_cplex
    cplex = load_cplex()
    write('environment.json', dict(python=sys.version, executable=sys.executable, platform=platform.platform(),
        pulp=importlib.metadata.version('pulp'), cplex_api=cplex.__version__,
        optimizer_called=False, license_solve_test='NOT RUN', script_sha256=digest(Path(__file__))))
    for name, rows in [('queries.csv', queries), ('initial_profiles.csv', initial)]:
        with (a.output/name).open('x', newline='', encoding='utf-8-sig') as f:
            w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(json.dumps(dict(status='PASS', cases=len(summaries), queries=len(queries), sources=len(source_checks),
                          artifacts=len(artifacts), seconds=time.perf_counter()-start)))


if __name__ == '__main__':
    main()
