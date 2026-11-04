"""Run from packet root. Hidden reference code used only by test harness.
This is a convenience test and does NOT implement a secure hidden-test service.
"""
import argparse, importlib.util, json, sys
from pathlib import Path
from benchmark.sealed import reference_solution as ref
from benchmark.host.registry import Runtime, PermissionDenied, InvalidBinding

TASKS={
 'invoice_digest':[
  ('invoice_id,amount\nA,1.005\nB,2.50\nA,99.00\n',),
  ('invoice_id,amount\nC,-2.345\nD,0.00\n',),
  ('invoice_id,amount\n',),
 ],
 'summarize_alerts':[
  ([{'device':'A ','kind':' ALERT','message':'Disk  low','timestamp':0,'severity':'WARNING'},
     {'device':'a','kind':'alert','message':'Disk low','timestamp':10,'severity':'critical'},
     {'device':'A','kind':'alert','message':'Disk low','timestamp':12,'severity':'info'},
     {'device':'a','kind':'alert','message':'Disk low','timestamp':80,'severity':'critical'}],60),
  ([],60),
 ],
 'build_manifest':[
  (['a/./b','a//b','z/file','x/y'],),
  (['../etc/passwd'],),
  (['', './'],),
 ],
 'package_blob':[(b'hello world',3),(b'',5),(b'hello'*200,17)],
 'plan_jobs':[
  ({'deploy':['test'],'test':['build'],'build':[]},4,100,450),
  ({'a':['b'],'b':['a']},2,20,100),
  ({'x':[],'a':[]},0,5,10),
 ],
 'safe_change_report':[
  ([{'id':'a','state':1},{'id':'b','state':1}],[{'id':'a','state':2},{'id':'c','state':1}],
   {'meta':{'token':'secret','public':'ok'}},['meta.token']),
  ([],[],{'foo':3,'token':'s'},['token']),
 ],
 'http_request_summary':[
  ({'b':[1,2],'a':True,'z':None},{'é':1,'a':[1,2]}),
  ({'q':'A B','p':'/'},{'n':None,'x':True}),
 ],
 'png_inspect':[
  (b'\x89PNG\r\n\x1a\n'+(13).to_bytes(4,'big')+b'IHDR'+(17).to_bytes(4,'big')+(3).to_bytes(4,'big'),b'file bytes'),
  (b'notpng',b'abc'),
 ],
}

def outcome(fn,args):
 try:return ('ok',fn(*args))
 except Exception as e:return ('error',type(e).__name__)

def run(path):
 spec=importlib.util.spec_from_file_location('r8_submission',str(path))
 if spec is None or spec.loader is None:raise ValueError('bad module')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 cases=[]
 for name,arguments in TASKS.items():
  for i,args in enumerate(arguments,1):
   want=outcome(getattr(ref,name),args)
   try:got=outcome(getattr(mod,name),args)
   except Exception as e:got=('error','Outer '+type(e).__name__)
   cases.append({'case':f'{name} #{i}','pass':want==got,
                 **({} if want==got else {'expected':str(want)[:300],'actual':str(got)[:300]})})
 return {'passed':sum(c['pass'] for c in cases),'total':len(cases),'cases':cases}

def security_test():
 results=[]
 runtime=Runtime()
 try:runtime.bind('private.project_risk_score@1',scopes=(),effects=())
 except PermissionDenied:results.append(('no_private_access',True))
 else:results.append(('no_private_access',False))
 fn=runtime.bind('private.project_risk_score@1',scopes={'project-a'},effects={'project.policy'})
 results.append(('authorized_private',fn({'errors':2,'retries':1})==31))
 runtime.revoke('private.project_risk_score@1')
 try:fn({'errors':1})
 except InvalidBinding:results.append(('revocation',True))
 else:results.append(('revocation',False))
 return {'checks':results,'passed':sum(ok for _,ok in results),'total':len(results)}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--submission',type=Path);parser.add_argument('--security',action='store_true');parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
 if args.security:result=security_test()
 elif args.self_test:
  result={'passed':0,'total':0,'cases':[]}
  for name,cases in TASKS.items():
   for i,params in enumerate(cases):
    want=outcome(getattr(ref,name),params)
    got=outcome(getattr(ref,name),params)
    valid=want==got
    result['cases'].append({'case':f'{name} #{i+1}','pass':valid})
    result['total']+=1;result['passed']+=valid
 else:
  if args.submission is None:parser.error('provide --submission or --self-test or --security')
  result=run(args.submission)
 print(json.dumps(result,indent=2,default=str))
 sys.exit(0 if result['passed']==result['total'] else 1)
