"""Fixed behavior tests for participants' submissions. Python 3.10+; stdlib only.

Usage:
    python fixtures/test_tasks.py --symbolic examples/controller.sym
    python fixtures/test_tasks.py --submission submission.py
    python fixtures/test_tasks.py --python-controller controller_submission.py
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'fixtures'))
from capabilities import controller_logs, rollup_activity
from symbolic_runtime import execute, SyntaxErrorIR

SMALL = [-2,0,1,2,3,17]
ACTIVITY_CASES = [
    ([{'event_id':' a ','device':' APS-1 ','kind':' Alert ','message':' Disk  Low ', 'timestamp':10,'severity':'warning'},
      {'event_id':'b','device':'aps-1','kind':'alert','message':'Disk Low','timestamp':20,'severity':'critical'},
      {'event_id':'c','device':'aps-1','kind':'alert','message':'Disk Low','timestamp':80,'severity':'info'}], 50, 0),
    ([{'event_id':'c','device':'A','kind':'alert','message':'M','timestamp':2,'severity':'info'},
      {'event_id':'a','device':'A','kind':'alert','message':'M','timestamp':1,'severity':'critical'},
      {'event_id':'b','device':'B','kind':'status','message':'ok','timestamp':3,'severity':'warning'}], 60, 1),
    ([{'event_id':'x','device':'A','kind':'alert','message':' M ','timestamp':1,'severity':'warning'},
      {'event_id':'y','device':'A','kind':'alert','message':'M','timestamp':4,'severity':'warning'},
      {'event_id':'z','device':'A','kind':'alert','message':'M','timestamp':9,'severity':'critical'}], 5, 0),
    ([{'event_id':'x','device':'A','kind':'alert','message':' M ','timestamp':False,'severity':'warning'},
      {'event_id':' y ','device':' A ','kind':'alert','message':' M ','timestamp':1,'severity':'CRITICAL'}], 600, 2),
    ([], 600, 0),
]


def check(actual,expected,label):
    if actual != expected:
        return {'case':label, 'pass':False,'expected':expected,'actual':actual}
    return {'case':label,'pass':True}


def run_symbolic(path):
    s=Path(path).read_text(encoding='utf-8')
    return [check(execute(s,n), controller_logs(n),f'symbolic n={n}') for n in SMALL]


def run_python_controller(path):
    spec=importlib.util.spec_from_file_location('python_controller',path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return [check(mod.controller_logs(n),controller_logs(n),f'python controller n={n}') for n in SMALL]


def run_submission(path):
    spec=importlib.util.spec_from_file_location('participant',path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    res=[]
    for n in SMALL:
        res.append(check(mod.run_controller(n),controller_logs(n),f'controller n={n}'))
    for idx,(events,window,level) in enumerate(ACTIVITY_CASES):
        expect=rollup_activity(events,window,level)
        res.append(check(mod.run_rollup(events,window,level),expect,f'rollup case {idx+1}'))
    for invalid in [(ACTIVITY_CASES[0][0],0,0),(ACTIVITY_CASES[0][0],600,3),('bad',600,0)]:
        expected_error=type(None)
        try:
            rollup_activity(*invalid)
        except Exception as e:
            expected_error=type(e)
        try:
            mod.run_rollup(*invalid)
            res.append({'case':f'error {invalid[1:]}','pass':False,'detail':'missing exception'})
        except Exception as e:
            res.append({'case':f'error {invalid[1:]}','pass':type(e) is expected_error,'actual_error':type(e).__name__})
    return res


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--symbolic')
    group.add_argument('--submission')
    group.add_argument('--python-controller')
    args=ap.parse_args()
    if args.symbolic:
        results=run_symbolic(args.symbolic)
    elif args.python_controller:
        results=run_python_controller(args.python_controller)
    else:
        results=run_submission(args.submission)
    print(json.dumps({'passed':sum(r['pass'] for r in results),'total':len(results),'cases':results},indent=2,ensure_ascii=False))
    sys.exit(0 if all(r['pass'] for r in results) else 1)
