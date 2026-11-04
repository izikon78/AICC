"""Non-production mock binder, with revocation and scopes; NOT an execution sandbox.
The underlying Python code is directly importable if the caller has file access.
"""
import hashlib, os, time
from benchmark.sealed import public_core, private_core, near_miss

_FUNCTIONS={f'pub.{name}@1':getattr(public_core,name) for name in [
 'normalize_tag','normalize_whitespace','parse_money','parse_csv_table',
 'canonical_json','digest_json','stable_unique','group_by_window',
 'filter_by_severity','safe_path','chunks','hash_chunks',
 'gzip_deterministic','toposort','diff_by_id','merge_patch',
 'redact_paths','make_query','png_dimensions','retry_delays']}
_FUNCTIONS['private.project_risk_score@1']=private_core.risk_score_private
_FUNCTIONS['candidate.parse_money_bankers@1']=near_miss.parse_money_bankers
_FUNCTIONS['candidate.safe_path_loose@1']=near_miss.safe_path_loose
_FUNCTIONS['candidate.group_by_eventid@1']=near_miss.group_by_eventid

_METADATA={key:{'effects':set(), 'scope':'public','path':public_core.__file__} for key in _FUNCTIONS if key.startswith('pub.')}
for name in ('candidate.parse_money_bankers@1','candidate.safe_path_loose@1','candidate.group_by_eventid@1'):
 _METADATA[name]={'effects':set(),'scope':'public','path':near_miss.__file__}
_METADATA['private.project_risk_score@1']={'effects':{'project.policy'},'scope':'project-a','path':private_core.__file__}
class PermissionDenied(Exception):pass
class InvalidBinding(Exception):pass

class Runtime:
 def __init__(self):
  self.revision=0;self.revoked=set()
 def revoke(self,cap):
  self.revoked.add(cap);self.revision+=1
 def bind(self,cap, principal='anonymous', scopes=(), effects=(), ttl_seconds=600):
  if cap not in _FUNCTIONS:raise KeyError(cap)
  meta=_METADATA[cap]; granted=set(scopes); allowed=set(effects)
  if meta['scope']!='public' and meta['scope'] not in granted:raise PermissionDenied('scope')
  if not meta['effects'].issubset(allowed):raise PermissionDenied('effects')
  if cap in self.revoked:raise PermissionDenied('revoked')
  source_hash=hashlib.sha256(open(meta['path'],'rb').read()).hexdigest()
  revision=self.revision;expiry=time.monotonic()+ttl_seconds
  fn=_FUNCTIONS[cap]
  def invocation(*args,**kwargs):
   if time.monotonic()>expiry:raise InvalidBinding('expired')
   if self.revision!=revision or cap in self.revoked:raise InvalidBinding('policy changed')
   if meta['scope']!='public' and meta['scope'] not in granted:raise PermissionDenied('scope')
   if not meta['effects'].issubset(allowed):raise PermissionDenied('effects')
   if hashlib.sha256(open(meta['path'],'rb').read()).hexdigest()!=source_hash:raise InvalidBinding('artifact changed')
   return fn(*args,**kwargs)
  return invocation
