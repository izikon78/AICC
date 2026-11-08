"""ROUND-8 REFERENCE IMPLEMENTATIONS. Do not read during model authoring arms.
These are illustrative reusable functions, not audited production packages.
"""
from __future__ import annotations
import csv, gzip, hashlib, io, json, re, unicodedata
from collections import defaultdict
from copy import deepcopy
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from heapq import heappush, heappop
from urllib.parse import urlencode


def normalize_tag(value: str) -> str:
    if not isinstance(value, str): raise TypeError('tag must be str')
    result = ' '.join(unicodedata.normalize('NFKC', value).casefold().split())
    if not result: raise ValueError('empty tag')
    return result


def normalize_whitespace(value: str) -> str:
    if not isinstance(value, str): raise TypeError('text must be str')
    return ' '.join(value.split())


def parse_money(value: str) -> int:
    """Parse a decimal currency amount, return integer minor units."""
    if not isinstance(value, str): raise TypeError('money must be str')
    if not re.fullmatch(r'[+-]?\d+(?:\.\d+)?', value.strip()): raise ValueError('invalid monetary amount')
    try: amount = Decimal(value.strip())
    except InvalidOperation: raise ValueError('invalid monetary amount')
    if not amount.is_finite(): raise ValueError('nonfinite amount')
    return int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def parse_csv_table(text: str) -> list[dict]:
    if not isinstance(text, str): raise TypeError('CSV must be str')
    f=io.StringIO(text, newline='')
    reader=csv.DictReader(f)
    if not reader.fieldnames: return []
    fields=reader.fieldnames
    if len(fields)!=len(set(fields)) or any(not x for x in fields): raise ValueError('bad headers')
    out=[]
    for item in reader:
        if None in item: raise ValueError('extra CSV columns')
        if all(v in ('',None) for v in item.values()): continue
        out.append(dict(item))
    return out


def canonical_json(data) -> str:
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',',':'), allow_nan=False)


def digest_json(data) -> str:
    return hashlib.sha256(canonical_json(data).encode('utf-8')).hexdigest()


def stable_unique(rows: list[dict], field: str) -> list[dict]:
    if not isinstance(rows,list) or not isinstance(field,str): raise TypeError('invalid unique args')
    seen=set(); out=[]
    for row in rows:
        if field not in row: raise KeyError(field)
        key=canonical_json(row[field])
        if key not in seen:
            seen.add(key);out.append(deepcopy(row))
    return out


def group_by_window(events: list[dict], window: int) -> list[dict]:
    if not isinstance(window,int) or isinstance(window,bool) or window<=0: raise ValueError('window must be positive integer')
    events=list(events)
    for e in events:
        if not isinstance(e,dict): raise TypeError('event must be dict')
        if not isinstance(e.get('timestamp'),int) or isinstance(e.get('timestamp'),bool):raise TypeError('timestamp must be int')
        for key in ('device','kind','message'):
            if not isinstance(e.get(key),str): raise TypeError(key+' must be str')
    sorted_events=sorted(enumerate(events),key=lambda p:(p[1]['timestamp'],p[0]))
    groups=[]; last={}
    for _,event in sorted_events:
        key=(normalize_tag(event['device']),normalize_tag(event['kind']),normalize_whitespace(event['message']))
        if key not in last or event['timestamp']-groups[last[key]]['first'] >= window:
            groups.append({'device':key[0],'kind':key[1],'message':key[2], 'first':event['timestamp'],'last':event['timestamp'],'count':1})
            last[key]=len(groups)-1
        else:
            g=groups[last[key]]; g['last']=event['timestamp'];g['count']+=1
    return groups


def filter_by_severity(groups: list[dict], minimum: int) -> list[dict]:
    if not isinstance(minimum,int) or not 0<=minimum<=3: raise ValueError('minimum 0..3')
    severity={'debug':0,'info':1,'warning':2,'critical':3}
    out=[]
    for g in groups:
        key=normalize_tag(g.get('severity','info'))
        if key not in severity:raise ValueError('unknown severity')
        if severity[key]>=minimum:out.append(deepcopy(g))
    return out


def safe_path(path: str) -> str:
    if not isinstance(path,str): raise TypeError('path must be str')
    if '\x00' in path or '\\' in path or path.startswith('/') or re.match(r'^[a-zA-Z]:',path): raise ValueError('unsafe path')
    parts=[]
    for p in path.split('/'):
        if p in ('','.'):continue
        if p=='..':raise ValueError('traversal')
        parts.append(p)
    if not parts:raise ValueError('empty path')
    return '/'.join(parts)


def chunks(data: bytes, size: int) -> list[bytes]:
    if not isinstance(data,bytes): raise TypeError('data must be bytes')
    if not isinstance(size,int) or isinstance(size,bool) or size<=0:raise ValueError('invalid chunk size')
    return [data[i:i+size] for i in range(0,len(data),size)]


def hash_chunks(parts: list[bytes]) -> str:
    h=hashlib.sha256()
    for part in parts:
        if not isinstance(part,bytes):raise TypeError('chunk must be bytes')
        h.update(part)
    return h.hexdigest()


def gzip_deterministic(data: bytes) -> bytes:
    if not isinstance(data,bytes):raise TypeError('data must be bytes')
    return gzip.compress(data,mtime=0)


def toposort(graph: dict[str,list[str]]) -> list[str]:
    if not isinstance(graph,dict):raise TypeError('graph must be dict')
    nodes=set(graph)
    for node, deps in graph.items():
        if not isinstance(node,str) or not isinstance(deps,list):raise TypeError('invalid graph')
        if any(d not in nodes for d in deps):raise ValueError('missing dependency')
    children=defaultdict(set);counts={node:len(set(deps)) for node,deps in graph.items()}
    for node,deps in graph.items():
        for dep in set(deps):children[dep].add(node)
    heap=[]
    for node,count in counts.items():
        if not count:heappush(heap,node)
    result=[]
    while heap:
        node=heappop(heap);result.append(node)
        for nxt in sorted(children[node]):
            counts[nxt]-=1
            if counts[nxt]==0:heappush(heap,nxt)
    if len(result)!=len(nodes):raise ValueError('cycle')
    return result


def diff_by_id(before: list[dict], after: list[dict]) -> dict:
    def index(rows):
        d={}
        for row in rows:
            if not isinstance(row,dict) or 'id' not in row:raise ValueError('missing id')
            key=str(row['id'])
            if key in d:raise ValueError('duplicate id')
            d[key]=row
        return d
    x=index(before);y=index(after)
    return {'added':sorted(set(y)-set(x)),'removed':sorted(set(x)-set(y)),
            'changed':sorted(k for k in x.keys()&y.keys() if canonical_json(x[k])!=canonical_json(y[k]))}


def merge_patch(base,patch):
    if not isinstance(patch,dict):return deepcopy(patch)
    out=deepcopy(base) if isinstance(base,dict) else {}
    for k,v in patch.items():
        if v is None:out.pop(k,None)
        else:out[k]=merge_patch(out.get(k),v)
    return out


def redact_paths(data, paths: list[str]):
    out=deepcopy(data)
    for p in paths:
        if not isinstance(p,str) or not p:raise ValueError('invalid path')
        parts=p.split('.');item=out
        for seg in parts[:-1]:
            if not isinstance(item,dict) or seg not in item:break
            item=item[seg]
        else:
            if isinstance(item,dict):item.pop(parts[-1],None)
    return out


def make_query(params: dict) -> str:
    if not isinstance(params,dict):raise TypeError('params must be dict')
    pairs=[]
    for key in sorted(params):
        value=params[key]
        if isinstance(value,list): values=value
        else:values=[value]
        for entry in values:
            if entry is None:continue
            if isinstance(entry,bool):entry=str(entry).lower()
            if not isinstance(entry,(str,int,float)):raise TypeError('invalid value')
            pairs.append((str(key),str(entry)))
    return urlencode(pairs)


def png_dimensions(data: bytes) -> dict:
    if not isinstance(data,bytes):raise TypeError('data must be bytes')
    if len(data)<24 or data[:8]!=b'\x89PNG\r\n\x1a\n' or data[12:16]!=b'IHDR':raise ValueError('not a PNG header')
    width=int.from_bytes(data[16:20],'big');height=int.from_bytes(data[20:24],'big')
    if width<1 or height<1:raise ValueError('invalid dimensions')
    return {'width':width,'height':height}


def retry_delays(count:int,base_ms:int,cap_ms:int)->list[int]:
    if any(not isinstance(v,int) or isinstance(v,bool) for v in (count,base_ms,cap_ms)) or count<0 or base_ms<=0 or cap_ms<=0:raise ValueError('invalid retry policy')
    return [min(cap_ms,base_ms*(2**i)) for i in range(count)]
