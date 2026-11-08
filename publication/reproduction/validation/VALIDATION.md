# Final packet validation

Checked 8 November 2026. This is a known-answer packaging and compatibility
check by Codex, with prior exposure to the published results. It makes no new
independent reconstruction claim.

The published ZIP is 5,121,982 bytes with 293 manifest-verified payload files.
Its archive hash is recorded in `PACKET_VALIDATION.json` and the external
download manifest. Six tokenizer assets and all 59 files in the original frozen
approved-core manifest verified. No previous article draft, model weights or
saved adapter files are included.

A packet was extracted into a fresh Windows directory containing spaces. Its
reference wrapper ran offline using an existing Python 3.12 environment with all
18 approved-core package pins matched. The 21 tests passed, and all six
deterministic reference comparisons matched. Setup installation was not repeated.
The preserved environment, comparison and actual test log are adjacent files.

The supplementary native regression route passed 14 tests and the processing
unit route passed 44 tests in the existing experiment environment. Its NumPy
version was 2.5.4, differing from the processing study pin of 2.3.5. No timed
processing comparison was made in that environment. A fresh
native reference execution checked 360 programs on nine inputs each, producing
3,240 correct program/input checks and 120 matching assembly triplets. Full and
compact canonical target token totals match the frozen reference. The fresh
native summary and environment manifest are preserved here.

After documentation and figure assets were added, the final ZIP was extracted
again into a new directory containing spaces. All 293 payload hashes verified.
All 256 experiment/script/tokenizer payload hashes are identical to those in the
smoke-tested extraction. All 22 figure source hashes verified from the final
extraction. These checks avoid repeating unchanged model or runtime workloads.

The final archive identifies committed source revision
`b9e514527cd303c5cd984aadf44a61ebfd30dc6f`. It was extracted and verified again
after that identity was recorded. The plotting tool's only change was terminal
newline whitespace. A fresh figure rebuild from this final extraction verified
all 22 source hashes and reproduced all fourteen PNG/SVG/CSV output hashes
identically. `figure-rebuild-comparison.json` preserves those comparisons.

No new GPU adaptation, model inference or million-event stress run was performed.
The packet preserves their final saved observations and labels fresh execution
as a separate optional route. A CPU exact replay checks the prescribed
accounting and execution records, not learned-agent efficiency.

## Build and check

From a checkout of the final branch,

```text
python tools/build_final_research_packet.py --overwrite
```

The builder verifies frozen source bytes, uses the six pinned tokenizer assets
from its cache or existing final ZIP, and downloads verified public assets only
when neither is available. An explicit `--asset-directory PATH` selects an
already prepared asset directory. Previous article drafts and earlier ZIPs are
unnecessary. The builder excludes this validation directory from the payload to
avoid an archive-hash cycle.

Rebuilding after a content change requires updating the external ZIP manifest
and validation record. Follow the packet's current standalone guide to choose
an independent reconstruction or exact-reference route.
