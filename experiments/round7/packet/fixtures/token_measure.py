"""Optional exact textual artifact token counts. Does NOT measure agent reasoning tokens.
Install separately if missing: pip install tiktoken
"""
from pathlib import Path
import hashlib
import sys
try:
    import tiktoken
except ImportError:
    print('NOT MEASURED: tiktoken unavailable; do not infer token numbers.')
    sys.exit(2)

ROOT=Path(__file__).resolve().parent.parent
FILES=['fixtures/baseline_api.md','fixtures/capability_cards.md','fixtures/activity_contract.md',
       'fixtures/capabilities.py','fixtures/registry.py','fixtures/symbolic_runtime.py']
enc=tiktoken.get_encoding('o200k_base')
for name in FILES:
    b=(ROOT/name).read_bytes()
    s=b.decode('utf-8')
    print(name, 'bytes=',len(b),'tokens=',len(enc.encode(s)), 'sha256=',hashlib.sha256(b).hexdigest()[:16])
