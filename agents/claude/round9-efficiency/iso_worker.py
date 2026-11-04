import sys, json; sys.path.insert(0, '/home/claude/r8/AI_Think_Tank_Round8_Packet')
from benchmark.public.baseline_api import normalize_tag
for line in sys.stdin:
    print(json.dumps(normalize_tag(json.loads(line))), flush=True)
