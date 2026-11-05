"""Recompute recorded results and draw publication figures; no new benchmarks/API calls."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
RUNS=[('Original Windows','full-2026-11-05'),
      ('Claude Linux','anthropic-claude-opus-5.5-2026-11-05-trackA-002'),
      ('Grok Windows','grok-4.7-2026-11-05-trackA-001')]
JOBS=['repeated-shuffled','diverse-shuffled','ordered-stream']
MODES=['reference','static','aicc_static','learned','aicc_learned']

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'docs/article/figures/draft8')
    parser.add_argument('--dependency-dir',type=Path)
    args=parser.parse_args()
    if args.dependency_dir:sys.path.insert(0,str(args.dependency_dir.resolve()))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import FancyBboxPatch
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    plots=[];summaries=[];raw_csv=[];source_hashes={};runs=[]
    for label,dirname in RUNS:
        folder=ROOT/'experiments/processing_study/results'/dirname
        read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
        raw=read('stress-raw.json');recorded=read('stress-summary.json');learning=read('learning-report.json')
        assert len(raw)==45 and len({(r['job']['name'],r['mode'],r['repeat']) for r in raw})==45
        for name in ('stress-raw.json','stress-summary.json','learning-report.json','run-config.json','run-metadata.json'):
            source_hashes[str((folder/name).relative_to(ROOT)).replace('\\','/')]=hashlib.sha256((folder/name).read_bytes()).hexdigest()
        table={}
        for job in JOBS:
            assert len({json.dumps(r['output'],sort_keys=True) for r in raw if r['job']['name']==job})==1
            for mode in MODES:
                rows=[r for r in raw if r['job']['name']==job and r['mode']==mode]
                assert len(rows)==3 and {r['repeat'] for r in rows}=={0,1,2}
                result={'run':label,'job':job,'mode':mode,
                    'pipeline_median_seconds':statistics.median(r['pipeline_seconds'] for r in rows),
                    'worker_median_seconds':statistics.median(r['worker_wall_seconds'] for r in rows),
                    'peak_median_mib':statistics.median(r['process_peak_working_set_bytes']/1048576 for r in rows)}
                match=next(r for r in recorded if r['job']==job and r['mode']==mode)
                for key,other in [('pipeline_median_seconds','median_pipeline_seconds'),('worker_median_seconds','median_worker_wall_seconds'),('peak_median_mib','median_peak_mib')]:
                    assert abs(result[key]-match[other])<1e-9
                table[(job,mode)]=result;summaries.append(result)
        sums={m:sum(table[(j,m)]['pipeline_median_seconds'] for j in JOBS) for m in MODES}
        workers={m:sum(table[(j,m)]['worker_median_seconds'] for j in JOBS) for m in MODES}
        timed=[r for r in raw if r['mode']=='aicc_static']
        assert len(timed)==9 and all(r['worker_wall_seconds']>=r['pipeline_seconds'] for r in timed)
        total_wall=sum(r['worker_wall_seconds'] for r in timed)
        pipeline=sum(r['pipeline_seconds'] for r in timed)
        runs.append({'label':label,'directory':dirname,
            'ordinary_pipeline_saved_percent':100*(1-sums['static']/sums['reference']),
            'aicc_pipeline_saved_percent':100*(1-sums['aicc_static']/sums['reference']),
            'aicc_worker_saved_percent':100*(1-workers['aicc_static']/workers['reference']),
            'memory_saved_percent':[100*(1-table[(j,'static')]['peak_median_mib']/table[(j,'reference')]['peak_median_mib']) for j in JOBS],
            'learned_extra_kernel_percent':100*(learning['held_out_kernel_evaluation']['learned_kernel_seconds']/learning['held_out_kernel_evaluation']['static_kernel_seconds']-1),
            'pie_pipeline_seconds':pipeline,'pie_other_worker_seconds':total_wall-pipeline,'pie_worker_seconds':total_wall,
            'pie_pipeline_percent':100*pipeline/total_wall})
        for r in raw:
            raw_csv.append({'run':label,'job':r['job']['name'],'mode':r['mode'],'repeat':r['repeat'],
                'pipeline_seconds':r['pipeline_seconds'],'worker_wall_seconds':r['worker_wall_seconds'],
                'peak_mib':r['process_peak_working_set_bytes']/1048576,'output_sha256':r['output']['sha256']})
    for job in JOBS:
        assert len({r['output_sha256'] for r in raw_csv if r['job']==job})==1
    plt.rcParams.update({'font.size':10,'axes.titleweight':'bold','axes.spines.top':False,'axes.spines.right':False,
                         'svg.fonttype':'none','savefig.facecolor':'white'})
    colors=['#334155','#0f766e','#7c3aed']
    def save(fig,name):
        fig.savefig(out/(name+'.png'),dpi=220,bbox_inches='tight')
        fig.savefig(out/(name+'.svg'),bbox_inches='tight')
        plt.close(fig);plots.append(name)
    fig,ax=plt.subplots(figsize=(7,3.9));fig.subplots_adjust(bottom=.24,top=.80,left=.10,right=.98)
    x=np.arange(3);width=.32
    for shift,key,label,color,hatch in [(-.5,'ordinary_pipeline_saved_percent','Ordinary optimized','#64748b',''),
                                      (.5,'aicc_pipeline_saved_percent','AICC with same optimization','#2563eb','//')]:
        bars=ax.bar(x+shift*width,[r[key] for r in runs],width,label=label,color=color,hatch=hatch)
        ax.bar_label(bars,fmt='%.1f%%',padding=3,fontsize=10)
    ax.set_xticks(x,[r['label'].replace(' ','\n',1) for r in runs]);ax.set_ylim(0,45)
    ax.set_ylabel('Less pipeline time versus own reference (%)')
    ax.set_title('Optimization gains repeat across the three runs',loc='left',pad=30)
    ax.legend(loc='upper left',bbox_to_anchor=(0,1.14),frameon=False,ncol=2,fontsize=9)
    ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    fig.text(.02,.015,'Equal mix: sums of three job medians; 3 repeats per cell. Shared algorithms, not isolated AICC benefit.',fontsize=8)
    save(fig,'processing-gains')
    fig,ax=plt.subplots(figsize=(7,3.9));fig.subplots_adjust(bottom=.24,top=.81,left=.10,right=.98)
    for i,r in enumerate(runs):
        bars=ax.bar(x+(i-1)*.24,r['memory_saved_percent'],.24,label=r['label'],color=colors[i],hatch=['','//','..'][i])
        ax.bar_label(bars,fmt='%.1f',padding=2,fontsize=8)
    ax.set_xticks(x,['Repeated keys','Diverse keys','Ordered stream']);ax.set_ylim(0,88)
    ax.set_ylabel('Lower peak process memory (%)');ax.set_title('Memory improvements reproduce by workload',loc='left',pad=30)
    ax.legend(loc='upper left',bbox_to_anchor=(0,1.15),ncol=3,frameon=False,fontsize=8.5)
    ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    fig.text(.02,.015,'Ordinary optimized versus own reference. Windows working set and Linux RSS are different OS metrics.',fontsize=8)
    save(fig,'memory-gains')
    fig,ax=plt.subplots(figsize=(7,3.4));fig.subplots_adjust(bottom=.23,top=.80,left=.10,right=.98)
    values=[r['learned_extra_kernel_percent'] for r in runs]
    bars=ax.bar(x,values,color=colors,width=.55)
    for bar,value in zip(bars,values):
        ax.text(bar.get_x()+bar.get_width()/2,max(value,0)+.08,'Practical tie' if abs(value)<.01 else f'+{value:.2f}%',ha='center',fontsize=10)
    ax.axhline(0,color='black',lw=.8);ax.set_ylim(-.25,3.7)
    ax.set_xticks(x,[r['label'].replace(' ','\n',1) for r in runs]);ax.set_ylabel('Extra selected kernel time (%)')
    ax.set_title('This neural selector did not establish an advantage',loc='left',pad=15)
    ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    fig.text(.02,.015,'24 held-out calibration jobs per run; excludes selection overhead. This is not native-language training.',fontsize=8)
    save(fig,'neural-selection')
    fig,axes=plt.subplots(1,3,figsize=(7,3.2));fig.subplots_adjust(top=.79,bottom=.18,wspace=.25)
    for ax,r in zip(axes,runs):
        ax.pie([r['pie_pipeline_seconds'],r['pie_other_worker_seconds']],colors=['#2563eb','#cbd5e1'],startangle=90,
               autopct='%1.0f%%',pctdistance=.76,textprops={'fontsize':10},wedgeprops={'width':.45,'edgecolor':'white'})
        ax.set_title(r['label'],fontsize=10,pad=4)
    fig.suptitle('Where complete worker time went',x=.02,ha='left',fontsize=12,fontweight='bold')
    fig.legend(['Timed pipeline','Other worker elapsed time'],loc='lower center',bbox_to_anchor=(.5,.075),ncol=2,frameon=False,fontsize=9)
    fig.text(.02,.005,'9 AICC-static workers per run; sums of actual times. Other includes startup, preparation, loading and hashing.',fontsize=8)
    save(fig,'worker-time-pies')
    fig,ax=plt.subplots(figsize=(7,3.6));ax.set_xlim(0,10);ax.set_ylim(0,4.8);ax.axis('off')
    def box(x0,y0,w,h,label,fill):
        ax.add_patch(FancyBboxPatch((x0,y0),w,h,boxstyle='round,pad=0.06',facecolor=fill,edgecolor='#64748b',lw=.8))
        ax.text(x0+w/2,y0+h/2,label,ha='center',va='center',fontsize=10)
    for y,label in [(3.05,'Conventional source'),(1.9,'Structured\nprogram IR'),(.75,'AIN operation form')]:
        box(.2,y,2.7,.75,label,'#f1f5f9')
        ax.annotate('',xy=(4.0,2.275),xytext=(3.0,y+.375),arrowprops={'arrowstyle':'->','color':'#64748b'})
    box(4.1,1.825,2.3,.9,'Same typed\nsemantic core','#dbeafe')
    ax.annotate('',xy=(7.2,2.275),xytext=(6.5,2.275),arrowprops={'arrowstyle':'->','color':'#64748b'})
    box(7.3,1.825,2.3,.9,'Same behavioral\nchecks and tasks','#dcfce7')
    ax.text(.2,4.55,'AIN comparison design',fontsize=12,fontweight='bold')
    ax.text(.2,4.10,'Proposed study; no AIN compiler or native-operation model has been evaluated',fontsize=9)
    ax.text(.2,.12,'Keep libraries, task evidence and runtime behavior equal; isolate how the program is represented.',fontsize=9)
    save(fig,'ain-comparison-design')
    for path in out.glob('*.svg'):
        path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    for filename,rows in [('summary-data.csv',summaries),('worker-data.csv',raw_csv)]:
        with (out/filename).open('w',encoding='utf-8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    metadata={'scope':'Recorded processing studies, not AIN performance measurements','source_sha256':source_hashes,
              'completed_workers':len(raw_csv),'unique_dataset_shapes':3,'runs':runs,'figures':plots,
              'pie_definition':'For each run, sum pipeline_seconds and sum(worker_wall_seconds-pipeline_seconds) over nine aicc_static workers. This is a partition of total actual worker time, not sums of medians or billing.',
              'matplotlib':matplotlib.__version__,'no_new_benchmark_executed':True}
    (out/'figure-data.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'figures':plots,'completed_workers':len(raw_csv),'runs':[{'label':r['label'],'pie_pipeline_percent':r['pie_pipeline_percent']} for r in runs]}))

if __name__=='__main__':main()
