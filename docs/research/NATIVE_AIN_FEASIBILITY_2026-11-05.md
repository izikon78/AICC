# Is native AIN worth pursuing? A reassessment of the theory and evidence

Research initiated 5 November; completed 6 November 2026 for Izik Bachar.
Literature cutoff: sources/versions published by 5 November 2026.

## Decision

**A bounded trained-native experiment is worth pursuing. The current evidence
does not justify claiming that AIN reduces AI usage, funding a large native-model
effort, or rewriting an AI system in AIN.** The mechanism is possible in principle
and has close experimental precedents. Much of the broad idea is already prior
art; the useful open contribution is a measured advantage for this design on
correct, substantial programming work.

The next experiment should train a model to know its representation before
evaluation. Another unfamiliar-symbol prompt trial would answer a different
question. A negative result against a strong readable-IR control should be allowed
to stop expansion, even if compact machine notation remains aesthetically appealing.

This judgment is an inference from the project audit and the primary literature
below. No external paper's training/result was independently reproduced here.
No paid API call, GPU rental or model training was started by this reassessment.

## The theory being assessed

The user's central goal is to determine whether **a model trained to use AIN
natively can spend less work generating and maintaining correct software**.
Fixed language knowledge is learned before inference; it is not a recurring
language manual. AICC is the proposed additional layer for reusing governed
computation and compatibility evidence over time.

The root Version 2 challenge already says instruction vocabulary, tokenizer,
training regime and runtime must be investigated together. Draft 3, Draft 4 and
the architecture's historical H2 also retain trained-native learning. The present
clarification restores that priority; it is not a new hypothesis invented after
unfavorable current-tokenizer measurements.

| Claim | Assessment | Evidence required |
|---|---|---|
| AIN-trained AI writes correct code faster/with less usage | Plausible, untested by this project | Matched trained models; unseen construction, change, repair and handoff; total resources per correct chain |
| AIN compiles faster | Plausible for a specified toolchain, independent of generation | Same target/optimizations; parse/check/lower/backend timing and its share of total task cost |
| Architecture alignment means less "traveling" | Testable after replacing the metaphor with observables | Forward/latent steps, context work, failed choices, repairs and actual hardware work at matched correctness |
| AI software implemented in AIN runs more cheaply | Conditional systems hypothesis | A changed computation graph, kernels, fusion, scheduling or memory behavior with a strong compiler baseline |
| AICC adds lifecycle budget value | Plausible, unmeasured here | Equal conventional reuse; discovery, verification, binding, changes, maintenance and setup amortization |

The current canonical statement and distinct N1/N2/N3 labels are in
[NATIVE_HYPOTHESES.md](../ain/NATIVE_HYPOTHESES.md). They do not rename the
historical architecture's H1–H4 ledger, whose H3 meant persistent binding.

## Why the core idea is possible

Models can learn computational representations before a task. Cadmus directly
trains on an executable integer-VM vocabulary without natural-language training.
Its setting is restricted program completion, so it establishes feasibility of
native instruction learning rather than general software superiority. [S1](https://arxiv.org/html/2602.09112v1)

IRCoder provides complementary evidence for learning compiler representations
inside model weights. TyFlow goes closer to the syntax/search claim by learning
structural synthesis decisions; its method also supplies type-guided machinery.
These results make the proposal technically credible, while leaving AIN's
resource advantage and the contribution of its own design unmeasured. [S2](https://arxiv.org/html/2403.03894v3), [S3](https://arxiv.org/html/2510.10216v2)

There are identifiable mechanisms to test: fewer model-facing output positions,
less redundant context, fewer invalid choices and repair loops, or learned
abstractions that avoid rebuilding known computation. Each can move work into
training, additional model components, compiler checking or capability discovery.
The entire applicable boundary must be measured.

## Why compactness alone is insufficient

The 2024 tokenization study finds that minimizing segmentation length does not
guarantee better downstream quality. The 2026 compute-optimal study likewise
finds compression-dependent tradeoffs rather than a universal preference for
larger units. These are general-language results, not refutations of native AIN,
but they rule out assuming an efficiency win from unit count alone. [S5](https://aclanthology.org/2024.emnlp-main.40/), [S6](https://arxiv.org/html/2605.01188v2)

zip2zip demonstrates a learned compressed interface and measured throughput, with
quality losses and extra embedding/decoding work. Its units are compressed text
chunks, not new arbitrary program semantics. Coconut also has mixed outcomes:
its reasoning representation helps on some tasks but fewer steps do not preserve
all mathematical accuracy. These motivate measuring a correctness–compute
frontier rather than selecting the shortest successful-looking string. [S4](https://arxiv.org/html/2506.01084v2), [S8](https://arxiv.org/html/2412.06769v4)

An instruction cannot carry unlimited new information for free. A short reference
can denote a previously learned operation, but unfamiliar algorithms, arguments,
literal data, versioned contracts and private interfaces still have to be
represented or acquired. Ordinary function calls already reuse behavior through
short references. The AIN-specific benefit must survive that competent baseline.

## What "less traveling" can mean scientifically

In a conventional fixed-depth dense Transformer, changing a word to an opcode
does not remove the layer stack traversed by one forward step. That is an
architectural inference, not an AIN experiment. Lower uncertainty may improve
success or reduce required samples, while shorter output may reduce the number
of decoding steps. Both are useful possibilities. [S16](https://arxiv.org/html/1706.03762v7)

Measure output positions, all latent/forward steps, prefill, sampling/repair
loops, actual GPU/CPU time and memory, plus auxiliary encoding/checking work.
Human-readable source is not literally translated through an extra English
interpreter inside a Transformer. Additional computation can help correctness,
as pause-token research illustrates; deleting intermediate work is not always
an improvement. [S9](https://arxiv.org/abs/2310.02226v3)

Physical data movement is another valid mechanism, illustrated by FlashAttention,
but it concerns algorithm/layout changes. It cannot be inferred from an opaque
syntax. Competing frontends must receive the same applicable optimization. [S15](https://arxiv.org/abs/2205.14135)

## The long-term AI/AICC claim needs two experiments

Writing an AI's implementation in AIN and training an AI to generate AIN are
different proposals. Existing compiler infrastructure already lowers neural
computation graphs to optimized hardware code. A source rewrite that leaves the
same graph and kernels has no identified new execution saving. AIN could still
make authoring or optimization easier, which requires its own measurement. [S11](https://research.google/pubs/mlir-scaling-compiler-infrastructure-for-domain-specific-computation/), [S12](https://openxla.org/xla/architecture)

DroidSpeak and LatentMAS support the broader possibility of avoiding repeated
textual machine communication, under compatibility assumptions. Their caches
and latent states are not executable AIN programs, so their reported gains cannot
be used as AIN saving percentages. [S13](https://arxiv.org/html/2411.02820v4), [S14](https://arxiv.org/html/2511.20639v3)

AICC may reduce repeated discovery, implementation, verification and compatibility
work. DreamCoder is relevant prior art for learned executable libraries; Unison
already separates content identity from human names. AICC needs a measurable
governance/lifecycle contribution beyond ordinary reuse. [S10](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf), [S20](https://www.unison-lang.org/docs/the-big-idea/)

First hold capabilities constant while testing AIN. Later cross representation
with ordinary/AICC binding, using identical implementations, effect rules and
version information. Report AIN's contribution, AICC's contribution and any
interaction separately.

## What the existing project actually established

- The earlier 135 million-event worker records repeat three public datasets.
  They demonstrate algorithm/runtime behavior and binding overhead. The small
  selector network learns costs of supplied plans, not AIN semantics.
- The Codex prototype's 69 engineering methods, 27 processing workers and six
  localized agent edits establish useful tested feasibility. Numeric AIN and
  readable IR coincide structurally. No model learned AIN in its weights.
- Claude's separate graph prototype reproduces its listed tests and adds useful
  mutation/type evidence. Audit also found same-run trailing-END acceptance,
  invalid restored-state acceptance and test scripts that exit successfully
  despite failures. These must be repaired before using it as a trusted judge.
- Its independently verified `o200k_base` count is 298 program tokens in each
  matched graph form; program plus codebook is 666 for AIN versus 580 for IR.
  This is a real spelling result, not a native-trained model result or recurring
  grammar-primer charge in the native condition. Its Python token comparison is
  explicitly unmatched because it includes more operator logic.
- The measured numeric interpreter is slower than direct Python on its local
  processing workloads. That is execution behavior of this implementation, not
  trained generation or optimized compilation cost.

Preserved sources: [processing synthesis](REPLICATION_SYNTHESIS_2026-11-05.md),
[Codex first execution](../../experiments/ain_v0/FIRST_EXECUTION_REPORT.md),
[Claude branch](https://github.com/izikon78/AICC/tree/a28436311f152ce65bdb317918c49d75c256bf25/experiments/ain_v0),
and [review evidence](native-reassessment/claude-review-evidence.json).

## Primary-source evidence map

The sources are selected for direct relevance, strong controls or contrary
evidence. This is a targeted review, not an exhaustive systematic review or a
novelty/patent-priority determination. Preprints and official design documents
have different evidentiary status from peer-reviewed controlled experiments.

| Source | Relevance and boundary |
|---|---|
| S1 · [Cadmus, 2026 preprint](https://arxiv.org/html/2602.09112v1) | Learned fixed instruction tokens and executable VM tasks. Its narrow arithmetic comparison and stated training cost are not general AIN performance or a budget quote. |
| S2 · [IRCoder, 2024 v3](https://arxiv.org/html/2403.03894v3) | Paired source/LLVM-IR continued pretraining, with source-only/unpaired controls. Improved code capabilities; does not measure cheaper native-IR authoring. IR can be longer than source. |
| S3 · [TyFlow, February 2026 v2](https://arxiv.org/html/2510.10216v2) | Learned type/synthesis decisions improve selected code outcomes. Representation, pruning and dynamic context are bundled, so isolate their costs/effects. |
| S4 · [zip2zip, NeurIPS 2025 v2](https://arxiv.org/html/2506.01084v2) | Learned LZW hypertokens reduce token counts and sometimes improve hardware throughput. Quality/overhead tradeoffs and inconsistent main/appendix resource figures prevent adopting a headline AIN cost estimate. |
| S5 · [Tokenization Is More Than Compression, EMNLP 2024](https://aclanthology.org/2024.emnlp-main.40/) | 64 models show that minimum-length segmentation is not a sufficient quality objective. General NLP rather than program authoring. |
| S6 · [Compute Optimal Tokenization, May 2026 v2 preprint](https://arxiv.org/html/2605.01188v2) | Fixed-compute scaling studies find task/scale-dependent compression tradeoffs. Estimated FLOPs and text tasks are not programming invoices. |
| S7 · [Type-Constrained Code Generation, PLDI 2025](https://arxiv.org/abs/2504.09246v2) | Type constraints improve conventional-language code outcomes. Required strong control; include checker cost. |
| S8 · [Coconut, COLM 2025; August 2026 v4](https://arxiv.org/html/2412.06769v4) | Trained latent reasoning has task-dependent accuracy/efficiency. Latent steps are not executable language instructions. |
| S9 · [Pause Tokens, ICLR 2024](https://arxiv.org/abs/2310.02226v3) | Extra trained computation can improve answers. Shorter trajectories can remove useful work. |
| S10 · [DreamCoder, PLDI 2021](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf) | Joint library and synthesis-policy learning supports reusable abstractions. Specialized synthesis, not AICC lifecycle economics. |
| S11 · [MLIR, CGO 2021](https://research.google/pubs/mlir-scaling-compiler-infrastructure-for-domain-specific-computation/), [official reference](https://mlir.llvm.org/docs/LangRef/) | Machine-oriented dialects, transformations and alternate serializations already exist. They do not establish lower AI authoring cost. |
| S12 · [OpenXLA architecture, official documentation](https://openxla.org/xla/architecture) | Existing graph optimization, fusion, memory planning and hardware lowering define the systems baseline. |
| S13 · [DroidSpeak, July 2025 v4](https://arxiv.org/html/2411.02820v4) | Cross-model KV reuse avoids repeated prefill under compatibility limits. Cache reuse rather than a native code language. |
| S14 · [LatentMAS, June 2026 v3 preprint](https://arxiv.org/html/2511.20639v3) | Latent collaboration reports reduced communication/work on its benchmarks. Transfer/architecture assumptions and task scope differ from AIN. |
| S15 · [FlashAttention, 2022](https://arxiv.org/abs/2205.14135) | IO-aware algorithms reduce memory movement. A concrete systems mechanism rather than a spelling advantage. |
| S16 · [Attention Is All You Need, 2017](https://arxiv.org/html/1706.03762v7) | Layered autoregressive computation explains why units/steps and hardware work must be distinguished. |
| S17 · [Meta LLM Compiler, 2024](https://arxiv.org/abs/2407.02524) | Pretraining on IR/assembly supports compiler tasks. Training scale and its objective differ from a matched native-language cost study. |
| S18 · [Can LLMs Understand IRs?, ICML 2025](https://proceedings.mlr.press/v267/jiang25p.html) | Existing models struggle with instruction-level/control-flow reasoning. Parsing a representation is insufficient evidence of understanding; not a matched native-training test. |
| S19 · [Tokenmaxxing, October 2026 v2 preprint](https://arxiv.org/abs/2607.22807v2) | Agent trajectories vary in usage, compilation failures and redundant revisions across languages. Motivates whole-trajectory accounting; prior familiarity remains a confound. |
| S20 · [Unison, official design documentation](https://www.unison-lang.org/docs/the-big-idea/) | Content-addressed definitions and names as metadata precede the short-reference proposal. |
| S21 · [WebAssembly core introduction, official specification](https://webassembly.github.io/spec/core/intro/introduction.html) | Compact instruction formats, validation, compilation and text views are established design territory. They do not establish trained-model efficiency. |

Bibliographic versions were checked as of 5 November 2026. Numerical findings
are attributed to their authors, not independently replicated here. In particular,
do not advertise a small-training price or a frontier-model win from a narrow
paper as the expected budget/performance of this proposed AIN system.

## What would make AIN a useful contribution

The novelty cannot rest on machines using symbols, learning a DSL, generating IR,
content-addressed calls or having a human-readable projection. The remaining
candidate contribution is a specified executable design whose trained models
need measurably less work for correct complex programs under strong controls,
possibly followed by an independently measured AICC lifecycle interaction.

If a readable typed IR with equivalent tokens/constraints matches AIN, the result
can still support structured generation, while weakening the case for maintaining
a distinct opaque language. If the gains arise entirely from stronger libraries,
attribute them to reuse. If they require a different neural architecture, name
and control that change rather than crediting syntax alone.

AIN and learned readable IR both outperforming conventional source would support
the user's broader native-computational-representation hypothesis. An IR tie would
limit the AIN-specific claim, not erase that shared benefit.

## Recommended investment and stop conditions

Prepare one resource-capped native-learning pilot using the
[draft protocol](../ain/TRAINED_NATIVE_PILOT_PROTOCOL.md). Use small matched models
or explicitly labeled matched adaptation, with no fixed-language primer at test
time. Hold out program structures/task families as well as input seeds. The exact
model, data, hardware ceiling and cash cap must be frozen before a paid run.

Do not start a large commons, train a frontier model from scratch or rewrite the
AI runtime to obtain the first answer. A preliminary fluency gate must precede
cost comparisons. Failure to learn at the chosen small scale is a bounded result,
not universal impossibility; it also does not justify unlimited scaling.

For each declared condition, count all resources spent on successful and failed
attempts. Compare total inference/tool resources divided by correct completed
chains, together with success rate and uncertainty. Then report compilation,
emitted-program runtime and training amortization separately.

Let incremental setup cost over the control be `F`, and measured recurring saving
per comparable task be `s`. If both are positive, a simple break-even estimate is
`F / s` comparable tasks, before any unmodeled maintenance/change costs. If `s`
is nonpositive, repetition does not repay a positive incremental setup cost.
This is an accounting identity, not an estimated AIN price or saving.

Pause expansion of a distinct AIN design if it misses the frozen correctness gate
or practical resource margin against the strongest matched control within the budget. Publish the
negative or inconclusive result. More unreadable glyphs, more repeated processing
timings or a favorable agent opinion cannot rescue that particular experiment.

## Changes to the article and theory record

Draft 9 states trained-native learning at the beginning and separates N1a writing,
N1b compilation, N2 inference mechanisms and N3 AI/AICC systems value. It keeps
the user's beep origin and authorship, preserves negative results with their
proper scope, and moves detailed runtime/selector material to linked historical
evidence. The current roadmap now prioritizes native learning; large untrained
spelling trials are diagnostics rather than the main claim.

Historical Drafts 1/3/4/8 and agent reports remain unchanged. Earlier "validated"
and "rejected" labels are not promoted to trained-model conclusions. The supplied
conversation reconstruction remains a bounded handoff, not a verbatim transfer.
The detailed file inventory and coverage notes are in
[native-reassessment](native-reassessment/).

The completed audit indexes 85 records, 60 distinct byte contents and 25 duplicate
records. It fully reviews 50 unique narrative contents, including four PDF-only
text extracts. Supporting logs/metadata, repeated renditions, raw code appendices
and unavailable artifacts are explicitly distinguished. It does not claim every
archive member, every operational log or the missing original chat was reviewed.

Prepared by OpenAI Codex with collaboration agents under Izik Bachar's research
direction. This assessment is editorial/research advice, not independent provider
attestation, peer review or proof that the desired result will occur.
