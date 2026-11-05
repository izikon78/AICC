"""Standard Matplotlib figures from recorded measurements, with min/max whiskers."""
import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--dependency-dir', type=Path)
    args = parser.parse_args()
    if args.dependency_dir: sys.path.insert(0, str(args.dependency_dir.resolve()))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    out = args.results
    rows = json.loads((out / 'stress-raw.json').read_text())
    jobs = ['repeated-shuffled', 'diverse-shuffled', 'ordered-stream']
    modes = ['reference', 'static', 'aicc_static', 'learned', 'aicc_learned']
    labels = ['Reference', 'Optimized', 'AICC + optimized', 'Neural selector', 'AICC + neural']
    colors = ['#94a3b8', '#2563eb', '#059669', '#d97706', '#9333ea']
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.fonttype': 'none', 'axes.titleweight': 'bold'})
    for field, factor, title, ylabel, filename in [
        ('pipeline_seconds', 1, 'Million-event processing time', 'Seconds', 'runtime'),
        ('process_peak_working_set_bytes', 1/1048576, 'Peak process memory', 'MiB', 'memory')]:
        fig, ax = plt.subplots(figsize=(12, 6.2))
        fig.subplots_adjust(left=0.08, right=0.98, bottom=0.20, top=0.79)
        x = np.arange(len(jobs)); width = 0.15
        for i, (mode, label, color) in enumerate(zip(modes, labels, colors)):
            samples = [[r[field]*factor for r in rows if r['job']['name']==job and r['mode']==mode] for job in jobs]
            medians = np.array([np.median(s) for s in samples])
            errors = np.array([[m-min(s) for m,s in zip(medians,samples)], [max(s)-m for m,s in zip(medians,samples)]])
            ax.bar(x+(i-2)*width, medians, width, color=color, label=label, yerr=errors,
                   error_kw={'elinewidth':1, 'capsize':3, 'alpha':0.8})
        ax.set_xticks(x, ['Repeated keys\nshuffled input','Diverse keys\nshuffled input','Ordered\nstreaming input'])
        ax.set_ylabel(ylabel); ax.set_title(title+'\nMedian of 3 runs; whiskers show observed minimum/maximum',loc='left',pad=15)
        ax.grid(axis='y',alpha=0.2); ax.set_axisbelow(True)
        ax.legend(ncol=3,loc='upper left',bbox_to_anchor=(0,1.0),frameon=False,fontsize=9)
        ax.set_ylim(0, ax.get_ylim()[1]*1.18)
        fig.text(0.01,0.025,'Synthetic matched jobs. Algorithm improvements are available to ordinary and AICC paths; no billed-model-cost claim.',fontsize=9,color='#475569')
        fig.savefig(out/(filename+'.png'),dpi=170,bbox_inches='tight');fig.savefig(out/(filename+'.svg'),bbox_inches='tight')
        plt.close(fig)
    learning=json.loads((out/'learning-report.json').read_text())['training']
    history=learning['history']
    fig,ax=plt.subplots(figsize=(10,5.5))
    fig.subplots_adjust(left=0.12,right=0.98,bottom=0.20,top=0.82)
    ax.plot([r['epoch'] for r in history],[r['training_loss'] for r in history],label='Training',color='#2563eb')
    ax.plot([r['epoch'] for r in history],[r['validation_loss'] for r in history],label='Validation',color='#d97706')
    ax.axvline(learning['selected_epoch'],label='Selected epoch',color='#64748b',linestyle='--')
    ax.set_yscale('log');ax.set_xlabel('Epoch');ax.set_ylabel('Normalized log-runtime prediction MSE')
    ax.set_title('Actual local neural training: 8–32–16–3 network\nValidation selects weights; held-out/stress jobs do not',loc='left')
    ax.legend(frameon=False);ax.grid(alpha=0.2)
    fig.text(0.01,0.025,'Small cost model over supplied plans; not LLM or native-opcode training.\nLower training loss does not imply faster job execution.',fontsize=9,color='#475569')
    fig.savefig(out/'learning.png',dpi=170,bbox_inches='tight');fig.savefig(out/'learning.svg',bbox_inches='tight');plt.close(fig)
    (out/'figures-metadata.json').write_text(json.dumps({'matplotlib':matplotlib.__version__,'numpy':np.__version__,
        'whiskers':'observed min/max, not confidence intervals','source':'stress-raw.json and learning-report.json'},indent=2)+'\n',encoding='utf-8',newline='\n')
    for path in out.glob('*.svg'):
        path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())+'\n',
                        encoding='utf-8',newline='\n')


if __name__ == '__main__':main()
