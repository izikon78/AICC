# Final packet validation

Updated 8 November 2026. This is a known-answer packaging and compatibility
check by Codex, with prior exposure to the published results. It supplies no
new independent learned-agent or provider result.

## Current package

The archive contains 309 manifest-verified payload files and is 5,236,041 bytes.
Its SHA-256 and source revision are in PACKET_VALIDATION.json and the external
ZIP manifest. The packaging source revision is
927b73187531c97bf4b01bda7f249722971905c7. A fresh extraction into a Windows path
containing spaces verified all payload hashes, all 59 frozen approved-core files
and six pinned tokenizer assets. The package includes no prior article copies,
model weights or adapters.

## Added representation-comparison route

The new wrapper ran offline from that fresh extraction in a prepared Python
3.12 environment. All eighteen CPU package pins matched. Four regression tests,
720 decoded-stage checks and fifty literal/state probes passed. Its ledger,
totals, stage checks, probes and summary matched all five corresponding observed
JSON outputs exactly. The retained smoke/environment records identify those
checks. This route performs no model inference or training.

An independent same-session code/data review also reaggregated all 2,160 raw
ledger rows and recounted all 4,320 request/response strings with the pinned
tokenizer. Every observed token count matched. The review checked the declared
local-format boundary and the distinction from hypothetical native units and
literature-only comparisons. It found no blocker.

## Preserved baseline checks

All 256 experiment/script/tokenizer files from the previously smoke-tested
baseline packet remain byte-identical. The earlier approved-core replay passed
21 tests and all six deterministic comparisons, with all eighteen CPU package
pins matched. Its original test log, environment and comparisons remain here.
The baseline native regression passed fourteen tests; its fresh reference run
checked 360 programs on nine inputs, producing 3,240 correct checks and 120
matching assembly triplets. Processing unit checks passed 44 tests under NumPy
2.5.4, a recorded deviation from that processing study's 2.3.5 pin. No new timed
processing comparison is claimed under that environment.

The retained figure rebuild record verified 22 input hashes and reproduced all
fourteen PNG/SVG/CSV output hashes. Those figure sources and assets are unchanged
by this update. Unchanged baseline runtime/model workloads were not repeated.
No new GPU training or million-event stress run was performed.

## Build and check

From the repository root,

```text
python tools/build_final_research_packet.py --overwrite
```

The builder verifies frozen bytes and bundles the pinned tokenizer assets from
the current ZIP, its cache or verified public downloads. It excludes this
validation directory to avoid an archive-hash cycle. Source or bundled-document
changes require rebuilding and refreshing the external validation records.

The current standalone guide distinguishes independent accounting reconstruction,
exact reference replay and the additional local representation test. Their
measurement boundaries and prior-exposure disclosures remain explicit.
