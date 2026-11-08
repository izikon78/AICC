"""Deterministic host-state demonstrations; no actual agent/provider handoff."""
import json
from .benchmark import make_runtime
from .data import Job, events, output_summary
from .kernels import process_cached, process_reference
from .runtime import PermissionDenied, StaleBinding, IncompatibleCapability, ReuseUnknown


def run():
    cap = 'events.cached@1'
    job = Job('binding-scenarios', 250, 12, 0.15, False, seed=8191)
    data = list(events(job))
    expected = output_summary(process_reference(data, job.window, job.minimum))
    requirements = {'behavior': 'events-v1', 'input_order': 'any'}
    obligations = ('exact-event-groups',)
    host = make_runtime()
    binding = host.bind(cap, obligations=obligations, requirements=requirements)
    checks = []
    def output_matches(fn):
        return output_summary(fn(data, job.window, job.minimum)) == expected
    checks.append({'case': 'cold binding', 'pass': output_matches(binding)})
    checks.append({'case': '20 calls reuse one metadata fit check',
                   'pass': all(output_matches(binding) for _ in range(20)) and host.full_validations == 1})
    host.bind(cap, obligations=obligations, requirements=requirements)
    checks.append({'case': 'repeat bind can reuse exact compatibility decision', 'pass': host.validation_cache_hits == 1})
    record = json.loads(json.dumps(binding.export_record()))
    receiver = make_runtime()
    restored = receiver.restore(record, principal='anonymous', requirements=requirements, obligations=obligations)
    checks.append({'case': 'new host revalidates JSON record and current receiving requirements',
                   'pass': receiver.full_validations == 1 and output_matches(restored)})
    try:
        receiver.restore(record, principal='anonymous', requirements={'behavior': 'changed-behavior'})
    except (IncompatibleCapability, ReuseUnknown): rejected = True
    else: rejected = False
    checks.append({'case': 'incompatible receiving task cannot trust old record', 'pass': rejected})
    host.register('unrelated@1', process_reference)
    checks.append({'case': 'unrelated capability update leaves binding usable', 'pass': output_matches(binding)})
    host.update_dependencies(cap, {'kernel_module_sha256': 'different-bundle'})
    try: output_matches(binding)
    except StaleBinding: rejected = True
    else: rejected = False
    checks.append({'case': 'relevant declared dependency change rejects old alias', 'pass': rejected})
    receiver.revoke(cap)
    try: output_matches(restored)
    except StaleBinding: rejected = True
    else: rejected = False
    checks.append({'case': 'revocation rejects restored alias', 'pass': rejected})
    private = make_runtime()
    private.register('private@1', process_cached, scope='project-x')
    try: private.bind('private@1', scopes=('project-x',))
    except PermissionDenied: rejected = True
    else: rejected = False
    checks.append({'case': 'caller scope assertion does not grant host authority', 'pass': rejected})
    return {'checks': checks, 'all_pass': all(c['pass'] for c in checks),
            'scope': 'new host processes/metadata only, not model learning or cross-provider agent transfer',
            'security_limit': 'in-process trusted-host mechanisms, not isolation or real authentication',
            'validation_limit': 'full_validations counts metadata fit, not conformance proofs'}
