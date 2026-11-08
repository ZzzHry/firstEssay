"""Plot verified assignment data, with an explicitly reconstructed local order."""
import csv,hashlib,heapq,json,math,subprocess,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE.parent/'gantt_tasks020_lines02'
sys.path[:0]=[str(ROOT/'sub'),str(ROOT/'code'),str(ROOT/'code/dwcg')]
from bp_solution import verify_integer_assignments

def task_key(i):return (0,int(i)) if str(i).isdigit() else (1,str(i))
def order_tasks(line,assignments):
    modes=dict(assignments);indeg={i:0 for i in modes};adj={i:[] for i in modes}
    for i,j in line.get('precedence',[]):
        if i in modes and j in modes:adj[i].append(j);indeg[j]+=1
    heap=[(task_key(i),i) for i,d in indeg.items() if d==0];heapq.heapify(heap);order=[]
    while heap:
        _,i=heapq.heappop(heap);order.append(i)
        for j in adj[i]:
            indeg[j]-=1
            if indeg[j]==0:heapq.heappush(heap,(task_key(j),j))
    assert len(order)==len(modes),'Cyclic within-station task graph'
    return [(i,modes[i]) for i in order]

def main():
    data=json.loads((HERE/'instance.json').read_bytes())
    cg=json.loads((HERE/'cg_result.json').read_text());compact=json.loads((HERE/'compact_result.json').read_text())
    assert cg['global_integer_optimal_proven'] and compact['global_integer_optimal_proven']
    assert abs(cg['global_lower_bound']-compact['global_lower_bound'])<1e-6
    witness=verify_integer_assignments(data,cg['witness']['stations'],expected=cg['global_lower_bound'])
    verify_integer_assignments(data,compact['witness']['stations'],expected=compact['global_lower_bound'])
    lines={l['id']:l for l in data['lines']};chosen={};schedule=[];station_order={};unselected={}
    for line in data['lines']:
        tasks={t['id']:t for t in line['tasks']};chosen[line['id']]={}
        for s in witness['stations']:
            if s['line']!=line['id']:continue
            now=0.;ordered=order_tasks(line,s['assignments']);station_order[line['id'],s['station']]=ordered
            for pos,(i,m) in enumerate(ordered,1):
                duration=tasks[i]['modes'][m]['time'];end=now+duration
                row=dict(line=line['id'],station=s['station'],position=pos,task=i,mode=m,start=now,end=end,duration=duration)
                schedule.append(row);chosen[line['id']][i]=row;now=end
            assert abs(now-s['duration'])<1e-8 and now<=line['cycle_time']+1e-8
        for i,j in line.get('precedence',[]):
            if j in chosen[line['id']]:
                assert i in chosen[line['id']]
                a,b=chosen[line['id']][i],chosen[line['id']][j]
                assert a['station']<=b['station']
                if a['station']==b['station']:assert a['end']<=b['start']+1e-8
        unselected[line['id']]=sorted(set(tasks)-set(chosen[line['id']]),key=task_key)
    with (HERE/'schedule.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['line','station','position','task','mode','start','end','duration']);writer.writeheader();writer.writerows(schedule)
    with (HERE/'station_summary.csv').open('w',newline='') as f:
        fields=['line','station','sequence','duration','cycle_time','human','robot','fatigue_load','fatigue_budget'];writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for s in witness['stations']:
            line=lines[s['line']];writer.writerow(dict(line=s['line'],station=s['station'],sequence=' -> '.join(f'T{i}({m})' for i,m in station_order[s['line'],s['station']]) or 'Inactive',duration=s['duration'],cycle_time=line['cycle_time'],human=s['human'],robot=s['robot'],fatigue_load=s['fatigue'],fatigue_budget=-math.log1p(-line['fatigue_limit'])))

    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':10,
        'axes.labelsize':10,'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':10,
        'svg.fonttype':'none','pdf.fonttype':42,'ps.fonttype':42,'hatch.linewidth':.35})
    fig,ax=plt.subplots(figsize=(9,5.7));fig.subplots_adjust(left=.13,right=.975,bottom=.24,top=.78)
    colors={'H':'#8BB9D5','R':'#96C9AD','J':'#F2C27A'}
    rows=[];y=0
    for line in data['lines']:
        for station in range(1,len(line['stations'])+1):rows.append((line['id'],station,y));y+=1
        y+=.7
    max_cycle=max(l['cycle_time'] for l in data['lines'])
    for li,(line_id,station,y) in enumerate(rows):
        line=lines[line_id];cycle=line['cycle_time'];tasks=[r for r in schedule if r['line']==line_id and r['station']==station]
        ax.barh(y,cycle,left=0,height=.7,color='#F1F3F5',edgecolor='none',zorder=1)
        if not tasks:ax.text(cycle/2,y,'Inactive',ha='center',va='center',color='#737B80',fontsize=9)
        for r in tasks:
            ax.barh(y,r['duration'],left=r['start'],height=.7,color=colors[r['mode']],edgecolor='#54606B',linewidth=.65,zorder=3)
            ax.text((r['start']+r['end'])/2,y,'T'+r['task']+' '+r['mode'],ha='center',va='center',fontsize=9,zorder=4)
        used=sum(r['duration'] for r in tasks)
        if tasks and cycle-used>=2:ax.text((used+cycle)/2,y,'Idle',ha='center',va='center',color='#737B80',fontsize=9)
    ax.set_yticks([r[2] for r in rows],[f'{l} / S{s}' for l,s,y in rows]);ax.invert_yaxis()
    ax.set_xlim(0,max_cycle);ax.set_xticks(range(0,int(max_cycle)+1));ax.set_xlabel('Time within station cycle (synthetic units)',labelpad=9)
    ax.set_axisbelow(True)
    ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0,pad=8)
    handles=[Patch(facecolor=colors[m],edgecolor='#54606B',label=label) for m,label in [('H','H: Human'),('R','R: Robot'),('J','J: Joint')]]+[Patch(facecolor='#F1F3F5',edgecolor='none',label='Idle / inactive')]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.55,.88),ncol=4,frameon=False)
    fig.text(.13,.965,'Verified whole-line CG assignment',fontsize=13,fontweight='bold',va='top')
    resources=witness['resources_used'];fig.text(.13,.915,f"20 tasks / 2 lines   |   Profit {witness['objective']:.2f}   |   Selected {len(schedule)}/20   |   H {resources['humans']}/{data['human_limit']}, R {resources['robots']}/{data['robot_limit']}",va='top')
    omitted='; '.join(l+': '+', '.join('T'+i for i in ids) for l,ids in unselected.items())
    fig.text(.13,.135,'Within each row: topological order, with numeric task-ID tie-breaking.',fontsize=9)
    fig.text(.13,.101,'Each row has its own cycle clock; this is not a single-product end-to-end timeline.',fontsize=9)
    fig.text(.13,.067,'Station traversal: S1 -> S2 -> S3 -> S4.  Unselected: '+omitted+'.',fontsize=9)
    fig.canvas.draw()
    fig.savefig(str(OUT)+'.png',dpi=300);fig.savefig(str(OUT)+'.pdf');fig.savefig(str(OUT)+'.svg')
    svg=Path(str(OUT)+'.svg')
    svg.write_bytes(('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n').encode('utf-8'))
    fig.savefig(str(OUT)+'.tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'});plt.close(fig)
    (HERE/'verification.json').write_text(json.dumps(dict(status='PASS',compact_ip=compact['global_lower_bound'],cg_ip=cg['global_lower_bound'],both_integer_optimal_proven=True,selected_tasks=len(schedule),total_tasks=sum(len(l['tasks']) for l in data['lines']),resources=resources,unselected=unselected,all_original_constraints_checked=True,station_time_and_local_precedence_checked=True,order_source='post-solve topological reconstruction, not an optimized start-time variable',time_axis='independent local station-cycle clocks',panel_alignment='NOT APPLICABLE: a single axes'),indent=2),encoding='utf-8')
    print('PASS: original constraints, objective agreement, local sequencing and cycle limits; rendered',OUT.name)
if __name__=='__main__':main()
