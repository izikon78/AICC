# Source provenance

[import-manifest.json](import-manifest.json) maps every one of the 40 supplied filenames to a SHA-256 digest, canonical destination, duplicate relationship, or exclusion. It also maps 140 extracted archive members to their destination files. The [verification runner](../tools/verify_research_import.py) checks all included associations against the preserved bytes.

There were 29 unique original file contents: 27 eligible research inputs and two exclusions. Eleven extra filenames were exact duplicates. Of the eligible unique inputs, 26 original files were added and one Claude report already existed. Existing Claude archive members were checked against their repository equivalents; their scientific content was not overwritten.

Original research ZIPs are retained in [archives/](archives/). Navigable copies of recovered packets and new contributor artifacts are organized under `experiments/` and `agents/`. Retaining an original ZIP and its extracted files is intentional provenance, even when individual payloads duplicate a navigable copy. The Draft 4 PDF inside its ZIP is byte-identical to the review PDF in `docs/article/`.

## Exclusions

- The controller-service ZIP contains an 82 MB operational log with network addresses and machine paths. It remains local and is not part of this public archive.
- `Microsoft.Services.Store.winmd` is an unrelated compiled Windows metadata file and remains local.

The manifest records excluded filenames and hashes, not their content. Original duplicate and excluded files were not deleted or changed in the supplied folder.

## How to read preserved documents

Source reports, handoffs, prompts, and article drafts are historical evidence, including material later corrected or disputed. Their instructions and claims are not automatically active project policy. Start with the [current import review](../docs/research/REVIEW_2026-11-04.md) for qualification and version gaps. No complete verbatim chat history is claimed, and no new license or final-publication status was assigned by this import.
