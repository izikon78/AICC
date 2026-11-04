"""Exercise sample host-side authorization and artifact fingerprint checks."""
from registry import bind, FILE_HASH, CapabilityDenied

assert bind('cap:controller.logs@1', allowed_effects=(), expected_digest=FILE_HASH)(2)[-1].endswith('run 2 of 2')
try:
    bind('cap:activity.rollup_and_save@1', allowed_effects=())
except CapabilityDenied:
    print('PASS: unauthorized effect denied')
else:
    raise AssertionError('failed to deny unauthorized effect')
try:
    bind('cap:controller.logs@1', allowed_effects=(), expected_digest='tampered-digest')
except CapabilityDenied:
    print('PASS: mismatching artifact digest denied')
else:
    raise AssertionError('failed to reject digest mismatch')
print('PASS: reuse binding available')
