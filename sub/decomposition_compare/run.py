"""Frozen-input exploratory comparison; isolated single-thread workers, no RL."""
from pathlib import Path
import argparse, dataclasses, hashlib, json, subprocess, sys, time, traceback, zlib

ROOT=Path(__file__).resolve().parents[2]

def dump(path, obj):
    raw=json.dumps(obj,ensure_ascii=False,allow_nan=False,indent=2).encode()
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_bytes(raw);temp.replace(path)

def worker(a):
    started=time.perf_counter();raw=a.instance.read_bytes();data=json.loads(raw)
    a.output.mkdir(parents=True,exist_ok=False);(a.output/'instance.json').write_bytes(raw)
    sys.path[:0]=[str(ROOT/'code/dwcg'),str(ROOT/'code'),str(ROOT/'sub')]
    from solver_backend import BackendConfig,use_backend,make_solver
    from bp_solution import verify_integer_assignments
    from validate import check_witness
    result={};pool=None;witness=None;events=[];error=None
    try:
        if a.method=='station_root':
            from solve import run_cg
            from master import build_master,decode_integer
            cg_deadline=a.deadline-2
            try:
                with use_backend(BackendConfig(name='cplex_py',threads=1,seed=11,deadline=cg_deadline,log_dir=str(a.output/'logs')),events):
                    result,pool=run_cg(data,max_iterations=1000,recover=False)
            except Exception as e:
                if not hasattr(e,'cg_result'):raise
                result,pool=e.cg_result,e.cg_pool
                result['adapter_caught_exception']=repr(e)
            recovery=None
            if pool and time.perf_counter()<a.deadline:
                with use_backend(BackendConfig(name='cplex_py',threads=1,seed=11,deadline=a.deadline,log_dir=str(a.output/'logs')),events):
                    m=build_master(data,pool,integer=True);m.problem.solve(make_solver(role='recovery',gap=0))
                    recovery=dict(m.problem.backend_result)
                    if recovery['has_incumbent']:
                        decode_integer(data,pool,m)
                        stations=[dict(line=l,station=s,assignments=list(next(col for p,col in enumerate(cs) if m.variables[l,s,p].value()>.5).assignments)) for (l,s),cs in pool.items()]
                        witness=verify_integer_assignments(data,stations,expected=m.value());check_witness(data,witness,witness['objective'])
            complete=[h for h in result['history'] if h['phase']==2 and h.get('complete_pricing')]
            ub=min((h['lp_upper_bound'] for h in complete),default=None)
            lb=witness['objective'] if witness else None
            summary=dict(status=result['status'],lb=lb,ub=ub,lp_objective=result.get('lp_objective'),
                lp_proven=result.get('lp_converged',False),integer_proven=lb is not None and ub is not None and abs(ub-lb)<=1e-5,
                witness=witness,recovery=recovery,pricing_calls=sum(len(h.get('pricing',[])) for h in result['history']),
                columns=sum(map(len,pool.values())),profile_calls=0)
            result['saved_pool']=[dict(line=l,station=s,columns=[dataclasses.asdict(c) for c in cs]) for (l,s),cs in pool.items()]
            result['adapter_solver_events']=events
        elif a.method=='line_root':
            sys.path[:0]=[str(ROOT/'sub/stage9'),str(ROOT/'sub/stage3')]
            from cg_balanced import run
            result=run(data,time_limit=max(.001,a.deadline-time.perf_counter()),init_seconds=.5,quota=False,pricing='rebuild',log_dir=a.output/'logs')
            summary=dict(status=result['status'],lb=result['lower_bound'],ub=result['upper_bound'],lp_objective=result['lp_objective'],
                lp_proven=result['lp_optimal_proven'],integer_proven=result['global_integer_optimal_proven'],witness=result['witness'],
                pricing_calls=result['pricing_calls'],columns=sum(map(len,result['pool'].values())),profile_calls=0)
        elif a.method=='line_full':
            sys.path.insert(0,str(ROOT/'sub/stage9'))
            from balanced_bound import run
            result=run(data,time_limit=max(.001,a.deadline-time.perf_counter()),cg_fraction=.9,cg_cap_seconds=1000000,log_dir=a.output/'logs')
            c=result['base_result']['cg']
            summary=dict(status=result['status'],lb=result['global_lower_bound'],ub=result['global_upper_bound'],lp_objective=c['lp_objective'],
                lp_proven=c['lp_optimal_proven'],integer_proven=result['global_integer_optimal_proven'],witness=result['witness'],
                pricing_calls=c['pricing_calls'],columns=sum(map(len,c['pool'].values())),profile_calls=result['profile_calls'])
        else:
            from compact_solver import run
            result=run(data,time_limit=max(.001,a.deadline-time.perf_counter()),log_dir=a.output/'logs')
            summary=dict(status=result['status'],lb=result['global_lower_bound'],ub=result['global_upper_bound'],lp_objective=None,
                lp_proven=None,integer_proven=result['global_integer_optimal_proven'],witness=result['witness'],pricing_calls=0,columns=0,profile_calls=0)
        if summary['witness']:check_witness(data,summary['witness'],summary['lb'])
        if summary['lb'] is not None and summary['ub'] is not None:assert summary['ub']>=summary['lb']-1e-5
        history=result.get('history',result.get('base_result',{}).get('cg',{}).get('history',[]))
        summary['phase1_rmp_solves']=sum(h['phase']==1 for h in history)
        summary['phase2_rmp_solves']=sum(h['phase']==2 for h in history)
        summary['complete_pricing_rounds']=sum(h.get('complete_pricing',h.get('complete_exact_pricing',False)) for h in history)
    except Exception:
        error=traceback.format_exc();summary=dict(status='adapter_error',lb=None,ub=None,integer_proven=False,error=error)
    tick=time.perf_counter();blob=zlib.compress(json.dumps(result,allow_nan=False).encode())
    (a.output/'certificate.json.zlib').write_bytes(blob)
    summary.update(method=a.method,input_sha256=hashlib.sha256(raw).hexdigest(),certificate_sha256=hashlib.sha256(blob).hexdigest(),
                   worker_seconds=time.perf_counter()-started,persistence_seconds=time.perf_counter()-tick,error=error)
    dump(a.output/'summary.json',summary)
    print(json.dumps({k:summary[k] for k in ('method','status','lb','ub','integer_proven')},ensure_ascii=False),flush=True)
    if error:raise SystemExit(1)

def main():
    p=argparse.ArgumentParser();p.add_argument('--worker',action='store_true');p.add_argument('--method');p.add_argument('--instance',type=Path)
    p.add_argument('--deadline',type=float);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.worker:return worker(a)
    a.output.mkdir(parents=True,exist_ok=False)
    cases=[('two_lines','code/milp/examples/two_lines.json',20),('n6','code/data/tasks006_lines01_each06_seed13.json',20),
        ('n80_L4','sub/stage12/evidence/formal600/tasks080_lines04_conflict_candidate_seed32__balanced_bound/instance.json',30),
        ('n120_L6_tight','sub/stage13/evidence/robust180/tasks120_lines06_ratio80_seed34__balanced_bound/instance.json',30),
        ('n80_L2_hard','sub/stage13/evidence/robust180/tasks080_lines02_conflict_candidate_seed31__balanced_bound/instance.json',30)]
    methods=['station_root','line_root','line_full','compact'];manifest=[]
    for name,path,budget in cases:
        target=a.output/(name+'.json');target.write_bytes((ROOT/path).read_bytes())
        manifest.append(dict(name=name,source=path,input_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),budget=budget))
    sources={}
    for directory in ('code','sub'):
        for f in (ROOT/directory).rglob('*.py'):
            if any(x in f.parts for x in ('evidence','__pycache__','.venv')):continue
            sources[f.relative_to(ROOT).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
    dump(a.output/'protocol.json',dict(cases=manifest,methods=methods,threads=1,seed=11,mip_gap=0,
        reserve_seconds=5,watchdog_grace_seconds=3,source_sha256=sources,scope='exploratory_single_seed_no_paper_claim',
        station_cg_reserves_additional_seconds_for_final_recovery=2,line_root_pricing='rebuild',line_full_pricing='warm'))
    accounting=[]
    for i,(name,_,budget) in enumerate(cases):
        # Balanced cyclic order; all methods serial, each same frozen input.
        order=methods[i%4:]+methods[:i%4]
        for method in order:
            out=a.output/f'{name}__{method}';start=time.perf_counter()
            command=[sys.executable,__file__,'--worker','--method',method,'--instance',str(a.output/(name+'.json')),
                     '--deadline',str(start+budget-5),'--output',str(out)]
            with (a.output/f'{name}__{method}.stdout.txt').open('x',encoding='utf-8') as log:
                process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
                try:code=process.wait(timeout=budget+3);hard=False
                except subprocess.TimeoutExpired:process.kill();code=process.wait();hard=True
            elapsed=time.perf_counter()-start
            row=dict(case=name,method=method,budget=budget,e2e_seconds=elapsed,over_budget_seconds=max(0,elapsed-budget),hard_stop=hard,exit_code=code)
            accounting.append(row);dump(a.output/'accounting.json',accounting)
            print(json.dumps(row),flush=True)

if __name__=='__main__':main()
