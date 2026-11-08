"""Solve one frozen existing instance; keep compact and CG in separate processes."""
import argparse,hashlib,json,platform,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--method',choices=['cg','compact'],required=True);a=parser.parse_args()
target=HERE/(a.method+'_result.json')
if target.exists():raise FileExistsError(f'Preserve existing evidence: {target}; use a new demo directory for a new solve.')
sys.path[:0]=[str(ROOT/'sub/stage9'),str(ROOT/'sub')]
raw=(HERE/'instance.json').read_bytes();data=json.loads(raw)
start=time.perf_counter()
if a.method=='cg':
    from balanced_bound import run
    result=run(data,time_limit=30,cg_fraction=.9,cg_cap_seconds=1000000,per_profile_seconds=2,
               solver='cplex_py',log_dir=HERE/'logs_cg')
else:
    from compact_solver import run
    result=run(data,time_limit=30,solver='cplex_py',log_dir=HERE/'logs_compact')
result['demo_metadata']={'input_sha256':hashlib.sha256(raw).hexdigest(),'python':platform.python_version(),
                         'elapsed_including_imports_seconds':time.perf_counter()-start,'nominal_budget_seconds':30}
with target.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,allow_nan=False)
assert result['witness'] is not None,result['status']
print(a.method,result['status'],'LB',result['global_lower_bound'],'UB',result['global_upper_bound'],
      'proven',result['global_integer_optimal_proven'],'resources',result['witness']['resources_used'],flush=True)
