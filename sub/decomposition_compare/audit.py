"""Independent small full-column oracles and saved-certificate arithmetic audit."""
import argparse, csv, importlib.util, json, sys, time, zlib
from pathlib import Path
from copy import deepcopy
from run import ROOT,dump
sys.path[:0]=[str(ROOT/'sub'),str(ROOT/'code'),str(ROOT/'code/dwcg'),str(ROOT/'sub/stage2'),str(ROOT/'sub/stage9')]
from solver_backend import BackendConfig,use_backend,make_solver,objective_value
from validate import enumerate_line,solve_full,check_witness,close
from stage2_verify import audit as line_audit
from verify_economic import audit as full_audit
spec=importlib.util.spec_from_file_location('task01_independent',ROOT/'docs/research_audit/independent_validation.py')
oracle=importlib.util.module_from_spec(spec);sys.modules[spec.name]=oracle;spec.loader.exec_module(oracle)

def station_audit(data,r):
    lines={l['id']:l for l in data['lines']};checked=0;bounds=[]
    for block in r['saved_pool']:
        for c in block['columns']:
            p=oracle.pattern(lines[block['line']],block['station'],c['assignments'])
            for k in ('profit','duration','fatigue','recovery','active','human','robot'):close(getattr(p,k),c[k])
    for h in r['history']:
        if 'duals' not in h:continue
        duals={tuple(d['row']):d['value'] for d in h['duals']}
        close(sum(oracle.rowspec(data)[k][1]*v for k,v in duals.items()),h['objective'])
        arts={tuple(d['row']):d['value'] for d in h.get('artificial_rows',[])}
        oracle.witness(data,h['rmp_solution'],h['objective'],h['phase'],arts)
        for c in h['pricing']:
            if not c.get('optimal'):continue
            p=oracle.pattern(lines[c['line']],c['station'],c['assignments'])
            close(oracle.rc(lines[c['line']],c['station'],p,duals,h['phase']),c['reduced_cost']);checked+=1
        if h.get('complete_pricing'):
            assert len(h['pricing'])==sum(len(l['stations']) for l in data['lines'])
            value=h['objective']+sum(max(0,c['reduced_cost']) for c in h['pricing']);close(value,h['lp_upper_bound'])
            if h['phase']==2:bounds.append(value)
    return dict(status='PASS',pricing_arithmetic_checked=checked,complete_profit_bounds=bounds)

def tiny_oracle(data):
    # Two independently enumerated column universes; line columns compressed only
    # by identical H/R coefficients and maximal profit, preserving full LP and IP.
    station=oracle.enumerate_patterns(data);line={};rawcounts={}
    for l in data['lines']:
        cols=enumerate_line(l);rawcounts[l['id']]=len(cols);best={}
        for c in cols:
            k=c['human'],c['robot']
            if k not in best or c['profit']>best[k]['profit']:best[k]=c
        line[l['id']]=list(best.values())
    values={}
    for ip in (False,True):
        m,_=oracle.full_model(data,station,integer=ip);info=oracle.solve_problem(m,ip)
        assert info['optimal'];values['station_IP' if ip else 'station_LP']=objective_value(m)
        answer=solve_full(data,line,ip);assert answer['optimal'];values['line_IP' if ip else 'line_LP']=answer['objective']
    for ip in (False,True):
        model=oracle.common.compact.build_model(data)
        if not ip:
            for v in model.problem.variables():v.cat='Continuous'
        info=oracle.solve_problem(model.problem,ip);assert info['optimal']
        values['compact_IP' if ip else 'compact_LP']=objective_value(model.problem)
    close(values['station_IP'],values['line_IP']);close(values['station_IP'],values['compact_IP'])
    assert values['compact_IP']<=values['line_LP']+1e-5<=values['station_LP']+2e-5<=values['compact_LP']+3e-5
    return dict(values=values,station_columns=sum(map(len,station.values())),raw_line_columns=rawcounts,
                compressed_line_columns=sum(map(len,line.values())))

def main():
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args()
    out=a.directory/'validation';out.mkdir(exist_ok=False);start=time.perf_counter();rows=[];curves=[];checks=[]
    protocol=json.loads((a.directory/'protocol.json').read_bytes())
    import hashlib
    for name,sha in protocol['source_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
    timing={ (r['case'],r['method']):r for r in json.loads((a.directory/'accounting.json').read_bytes())}
    for case in protocol['cases']:
        d=json.loads((a.directory/(case['name']+'.json')).read_bytes())
        for method in protocol['methods']:
            folder=a.directory/f"{case['name']}__{method}";s=json.loads((folder/'summary.json').read_bytes());blob=(folder/'certificate.json.zlib').read_bytes()
            assert hashlib.sha256(blob).hexdigest()==s['certificate_sha256']
            assert hashlib.sha256((folder/'instance.json').read_bytes()).hexdigest()==s['input_sha256']==case['input_sha256']
            assert s['error'] is None,s['error'];r=json.loads(zlib.decompress(blob))
            if s['witness']:check_witness(d,s['witness'],s['lb'])
            with use_backend(BackendConfig(name='cplex_py',threads=1,seed=11,deadline=time.perf_counter()+90)):
                if method=='station_root':check=station_audit(d,r)
                elif method=='line_root':check=line_audit(d,r,enumerate_pricing=False)
                elif method=='line_full':check=full_audit(d,r)
                else:
                    assert r['solver_result']['optimal']==s['integer_proven']
                    check=dict(status='PASS',scope='native_status_and_original_witness')
            checks.append(dict(case=case['name'],method=method,checks=check))
            if s['integer_proven']:assert s['lb'] is not None and s['ub']-s['lb']<=1e-5
            root=r.get('base_result',{}).get('cg',r);last={}
            for h in root.get('history',[]):
                obj=h.get('objective',h.get('rmp',{}).get('objective'));phase=h['phase']
                if obj is None:continue
                if phase in last:assert obj>=last[phase]-1e-5
                last[phase]=obj
                curves.append(dict(case=case['name'],method=method,phase=phase,iteration=h['iteration'],rmp_objective=obj,
                    repaired_upper_bound=h.get('lp_upper_bound',h.get('repaired_upper_bound')),
                    pricing_blocks=len(h.get('pricing',[])),complete_pricing=h.get('complete_pricing',h.get('complete_exact_pricing',False))))
            t=timing[case['name'],method]
            rows.append(dict(case=case['name'],method=method,status=s['status'],lb=s['lb'],ub=s['ub'],
                gap=None if s['lb'] is None or s['ub'] is None else s['ub']-s['lb'],integer_proven=s['integer_proven'],
                lp_objective=s.get('lp_objective'),lp_proven=s.get('lp_proven'),e2e_seconds=t['e2e_seconds'],
                phase1=s['phase1_rmp_solves'],phase2=s['phase2_rmp_solves'],pricing_calls=s['pricing_calls'],columns=s['columns'],
                profile_calls=s['profile_calls'],hard_stop=t['hard_stop'],over_budget=t['over_budget_seconds']))
    tiny={}
    with use_backend(BackendConfig(name='cplex_py',threads=1,seed=11,deadline=time.perf_counter()+120)):
        for name in ('two_lines','n6'):
            data=json.loads((a.directory/(name+'.json')).read_bytes());tiny[name]=tiny_oracle(data)
            for row in rows:
                if row['case']!=name:continue
                v=tiny[name]['values'];assert row['ub']>=v['compact_IP']-1e-5
                if row['lp_proven']:close(row['lp_objective'],v['station_LP' if row['method']=='station_root' else 'line_LP'])
                if row['integer_proven']:close(row['lb'],v['compact_IP'])
    # Deliberate falsification of saved station arithmetic must be rejected.
    r=json.loads(zlib.decompress((a.directory/'two_lines__station_root/certificate.json.zlib').read_bytes()))
    bad=deepcopy(r);next(h for h in bad['history'] if h.get('complete_pricing'))['lp_upper_bound']-=1
    try:station_audit(json.loads((a.directory/'two_lines.json').read_bytes()),bad)
    except AssertionError:rejected=True
    else:rejected=False
    assert rejected
    dump(out/'audit.json',dict(status='PASS',checks=checks,tiny_oracles=tiny,forged_bound_rejected=rejected,seconds=time.perf_counter()-start))
    for name,records in [('results.csv',rows),('convergence.csv',curves)]:
        with (out/name).open('x',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)
    dump(out/'results.json',rows);print(json.dumps(dict(status='PASS',runs=len(rows),tiny_oracles=tiny,seconds=time.perf_counter()-start)),flush=True)

if __name__=='__main__':main()
