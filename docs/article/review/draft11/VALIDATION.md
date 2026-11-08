# Draft 11 publication validation

Final publication checks completed 8 November 2026. The article and branch-review
snapshot retain their 7 November research date.

## Evidence and scope

The review covers all fourteen published branch tips in `branch-snapshot.json`
and two previously local RTX 3080 studies. A final `git ls-remote --heads origin`
check on 8 November found the same fourteen tips before this article branch was
published. The inventory contains 5,859 evidence entries and 796 distinct Git
blobs. Inherited copies do not count as independent experiments.

The three review reports describe their reads, raw-data recomputations and
remaining limits. All 135 processing-worker records were reaggregated. The
controller, local adaptation, compiler and conditional-accounting aggregates were
checked against their retained records. A recovered ordering counterexample was
replayed. Historical large model sessions and fuzz suites were reviewed through
their archived execution evidence rather than rerun in full.

A separate final consistency review found no material unsupported claim or
numeric mismatch. All fourteen article-local reference targets and fourteen
pinned Git targets resolve. All ten displayed conventional/AIN code blocks match
`examples.json` exactly once. The frozen source hashes for both local studies
match their manifests. Grok's approved-core result remains pending, while its
earlier processing record is included.

## Executed checks

| Check | Result |
|---|---|
| Local adaptation data and native compiler regression suite | 14 tests passed |
| Five source/AIN illustrative pairs | All structural checks passed, 15 unique operation IDs |
| Illustrative operation contracts | 13 deterministic mock scenarios passed |
| Existing AICC processing prototype | Three binding, handoff and incompatibility checks passed |
| Four chart rebuilds | All 22 directly used frozen source hashes verified |
| Final PDF structure | 15 Letter pages, four figure images, 31 URI links |
| PDF print-safe bounds | No text or figure outside the checked bounds |
| Required article sections | All present, no TODO/TBD/FIXME placeholders |

The fourteen regression tests include actual native execution through LLVM for
all 360 compact reference targets. This publication check does not repeat model
training or inference. The five new application examples remain illustrations
with mock contract checks. Their C#, C++, Ruby and Java toolchains were not run,
and those examples make no real database or HTTP calls or OS-thread executions.
The separate AICC example runs inside the existing trusted Python prototype.

Run the focused checks from the repository root with the experiment dependencies
installed in an isolated environment,

```text
python -m unittest experiments.native_learning_gate.test_data experiments.ain_compiler_gate.test_compiler experiments.ain_compiler_gate.test_data -v
python docs/article/examples/draft11/validate_examples.py
python docs/article/examples/draft11/aicc_binding.py
```

The figure package supplies its separate Matplotlib environment and rebuild
instructions. The PDF can be rebuilt using Python with ReportLab and the Arial
and Consolas fonts supplied by Windows,

```text
python tools/build_article11_pdf.py
```

## Visual review and output identity

All fifteen PDF pages were rendered through Poppler and inspected. The review
checked readable figures and code, paired examples, table continuation headers,
reference links, page breaks and clipping. The corrected introduction heading
was rendered and inspected again in the final PDF. The machine-readable output
checks, source/PDF hashes and per-page extracted-text hashes are in
`publication-validation.json`.

The editable article is Markdown. Automatic approval review rejected the
LibreOffice installer/extraction command with the reason "blocked by policy".
Consequently a render-verified Word copy was not produced. The PDF uses bundled
ReportLab and all previous versioned drafts remain available.
