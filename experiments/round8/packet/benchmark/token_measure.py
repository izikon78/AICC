"""Tokenizer accounting, optional tiktoken; never invent API usage costs."""
import argparse, json, pathlib
p=argparse.ArgumentParser();p.add_argument('files',nargs='+');p.add_argument('--encoding',default='o200k_base');args=p.parse_args()
try:
 import tiktoken
 enc=tiktoken.get_encoding(args.encoding)
except Exception as e:
 enc=None;print('MODEL TOKENS NOT MEASURED:',e)
for filename in args.files:
 data=pathlib.Path(filename).read_bytes()
 try:s=data.decode('utf-8')
 except UnicodeDecodeError:
  print(json.dumps({'file':filename,'bytes':len(data),'tokens':None,'note':'binary'}));continue
 print(json.dumps({'file':filename,'bytes':len(data),'characters':len(s),'tokens':len(enc.encode(s)) if enc else None,'encoding':args.encoding if enc else None}))
