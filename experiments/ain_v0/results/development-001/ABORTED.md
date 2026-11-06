# Aborted measurement run

The first four workers completed their workflow but exited while collecting the
Windows process memory counter: ctypes inferred a 32-bit argument for the 64-bit
process handle. Their raw exceptions and elapsed times are preserved here.
Worker 5 (`many_keys`, readable IR, repetition 3) was interrupted when the repeated
driver fault was diagnosed. The remaining 22 workers were not started.

No timing from this run is used as a successful result. The driver now declares
the Windows API argument/return types explicitly. A 50-event AIN worker verified
the corrected output path before the new `development-002` run. The original
source hashes are in this directory's environment.json; they are not rewritten.
