# Draft 10 validation record

6 November 2026. This record concerns the new article and replication packaging;
it is not an additional independent model-provider trial.

The article uses the frozen approved-core study at `2b6541a24ef71dcd4390f526042ebf131501fc51`
and Claude's submitted reconstruction at `e9a8a5111717a57427fac50605cf5cbe0c86b316`.
Earlier processing, interpreter and prompted-fluency performance figures are not
used as this draft's numerical evidence. Grok remains `??`, pending actual files.

The three figures derive from exact saved ledgers and Claude's separately labeled
sensitivity extension. Source identities and raw inputs are in
`figures/draft10/chart-data.json` and its companion CSV files. The article's numeric
code view is a new, explicitly labeled display projection. Its program/action
round-trip and approved execution checks pass for all 144 frozen semantic episodes;
it does not alter the frozen position counts or claim finalized AIN syntax.

The editable DOCX was rendered through the packaged `render_docx.py` rasterizer
using a Microsoft Word PDF-export adapter. The selected Windows runtime has no
bundled LibreOffice; no user-installed LibreOffice was used. Both final formats
share the same six-page Word layout. Every final page PNG was visually inspected
for clipping, code/table wrapping, chart readability and footer placement. The
agent comparison table is kept together; provenance differences are explained
in the following prose. Six source hyperlinks are preserved in the PDF.

The portable packet's smoke run extracted a fresh archive into a path containing
spaces, created a private Python environment, installed pinned dependencies and
ran the frozen reference wrapper with bundled tokenizer assets in offline mode.
All 21 tests passed, and fixtures, approved sources, totals, episodes, summary and
normalized manifest matched. All 59 frozen package hashes and six tokenizer
asset hashes passed. The package verifier rejected an altered payload and an
unsafe manifest path. These are packaging/reproduction checks, not model learning.

Python dependencies may require Internet installation on a recipient's machine.
The packet includes the pinned tokenizer and Apache license, not model weights,
credentials, GPU software or a complete offline Python distribution. The final
archive has its own file manifest and external SHA-256/size manifest.
