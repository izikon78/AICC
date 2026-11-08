# Related approaches and the scope of the comparison

Prepared 8 November 2026 under Izik Bachar's research direction. The comparisons
below use primary research papers and project documentation. They identify
overlapping mechanisms and the distinctions the AIN/AICC proposal must establish.
They supply no claim of priority, exhaustive literature coverage or independent
validation of another project's reported results.

## What was reviewed and what was executed

The local representation comparison runs the project's own declared encoders,
decoders, approved functions and fixed workflow traces. Its conventional-language
and IR controls receive the same operations and semantic information. It measures
the selected serialization and exposure rules. It does not run ToolkenGPT,
Toolscaler, DreamCoder, LILO, Voyager, CodeAct, Anthropic's platform, Cloudflare's
platform or the separate AINL runtime. No result from a local format control may
be labeled a measured result for one of those systems.

Research results and implementation descriptions below retain their authors'
reported status. A published agent benchmark, a vendor engineering example and
a project whitepaper have different evidence boundaries. Their percentages and
task-success rates cannot be ranked against this repository's fixed workflows.

## The closest mechanisms

| Approach and primary source | Relevant mechanism | Consequence for AIN/AICC positioning |
|---|---|---|
| [ToolkenGPT](https://arxiv.org/abs/2305.11554), 2023 | Learns a token embedding for a tool, then generates its arguments | Learned short references invoking established behavior are prior work. AIN needs an explicit contribution beyond the reference spelling. |
| [Toolscaler](https://aclanthology.org/2025.findings-emnlp.30/), 2025 | Encodes tools as semantic code sequences with shared subtokens | Vocabulary growth and unfamiliar tools are existing research questions; a fixed known-operation catalog is a bounded condition. |
| [DreamCoder](https://arxiv.org/abs/2006.08381), 2020 preprint | Learns reusable programming abstractions and a neural procedure for composing them | AIN's supplied approved core differs from learning the library itself. Shorter compositional programs alone do not identify a new mechanism. |
| [LILO](https://arxiv.org/abs/2310.19791), 2023 preprint, ICLR 2024 | Combines synthesis, symbolic compression and documentation to construct libraries | Library compression and making abstractions usable are linked problems. AIN's assumed fluency must remain distinct from measured learning. |
| [Voyager](https://arxiv.org/abs/2305.16291), 2023 | Retains executable skills and improves programs through feedback | Executable reuse and accumulated agent capabilities are established directions. Their presence alone does not distinguish AICC. |
| [CodeAct](https://arxiv.org/abs/2402.01030), ICML 2024 | Uses executable Python as a unified action space with interactive revision | An ordinary programming language is a serious composition control, rather than merely a verbose baseline. |
| [Code execution with MCP](https://www.anthropic.com/research/code-execution-with-mcp), Anthropic, 2025 | Composes tool calls in code, controls data exposure and persists state/functions | Context-efficient execution and continuing state already have conventional-language implementations. |
| [Code Mode](https://blog.cloudflare.com/code-mode/), Cloudflare, 2025 | Presents tools as a TypeScript API and executes compositions outside the model | Intermediate data need not pass through the model for every operation. This benefit must be separated from encoding changes. |
| [AI Native Lang / AINL](https://www.ainativelang.com/whitepaper), project whitepaper | Describes compact syntax, canonical graph IR, deterministic execution, adapters and unified workflow/memory artifacts | This is a direct architectural neighbor with a similar name. Its relationship requires explicit comparison; its documentation does not establish measured superiority here. |

## Four distinctions that keep the argument precise

The surrounding literature also helps separate the layers of the proposal,

| Additional source | Relevant boundary |
|---|---|
| [Stitch](https://arxiv.org/abs/2211.16605) | Discovers library abstractions that compress program corpora; abstraction definitions have a cost too. |
| [MemGPT](https://arxiv.org/abs/2310.08560) | Manages context through memory tiers; persistent agent memory is an established systems problem. |
| [Coconut](https://arxiv.org/abs/2412.06769) | Studies reasoning through continuous latent states, a different boundary from AIN's visible executable reference concept. |
| [DIAL/RIAL](https://arxiv.org/abs/1605.06676) | Studies learned inter-agent communication protocols rather than a native program compiler. |
| [Byte Latent Transformer](https://arxiv.org/abs/2412.09871) | Separates byte representation from dynamically sized computational patches; character counts do not fix compute. |
| [Notation Matters](https://arxiv.org/abs/2605.29676) | Tests token-oriented formats inside agent loops, including reliability effects; it does not test an already fluent native AIN model. |
| [TSCG](https://arxiv.org/abs/2605.04107) | Compiles tool schemas into compact structured text without requiring a new learned language. |
| [WebAssembly Component Model / WIT](https://component-model.bytecodealliance.org/design/wit.html) | Defines typed component interfaces and resources; WIT itself does not define implementation behavior. |

These additional systems are reviewed through primary sources, and none is run
by the local representation test. Their role is to locate the conceptual and
measurement boundaries rather than supply a performance league table.

**Learned meaning and text spelling.** A model trained to select a dedicated
operation token has a different interface from a pretrained tokenizer processing
the digits of an operation identifier. A shorter printed label need not produce
fewer text tokens. The new CPU comparison can count actual text tokens for its
declared local representations. The approved-core theory calculation separately
assigns ideal units under an already-learned interface. Neither is a reproduction
of a learned-tool-embedding model.

**Reusable implementation and new composition.** A supplied function can contain
loops, branching and significant computation. Every local arm receives the same
approved implementation. Its internal code therefore supplies no unique AIN
advantage. The remaining comparison concerns explicit choices, operands,
serialization, edits and retained records. Library induction, tool retrieval
quality and the probability of learning a correct composition belong to other
questions. The local test supplies correct workflow traces and makes those
boundaries visible.

**Data placement and compact encoding.** Running a computation over host-held data
can avoid exposing intermediate results to the agent. Compactly encoding an
exposed record can shorten the material that still enters context. Those are
separate effects. A fair mechanism comparison holds data placement fixed while
changing serialization, and reports resident and inspected-data schedules
separately. It should give Python the same handles, operations and compact memory
opportunities before interpreting a difference as language-specific.

**Persistent state and portable meaning.** Saving code or files establishes
persistence. A stronger handoff proposal must specify which task state,
requirements and dependency identities the receiving agent needs, and which
authority the receiving host grants. AIN/AICC's proposed contribution should
identify that preservation contract rather than presume persistence itself is
new. The current local fixtures demonstrate a bounded record format; they do
not establish a general portable agent substrate or production authority model.

## What the local test can contribute

A controlled CPU comparison can determine whether a particular literal text
format is shorter under the pinned tokenizer, whether the encoded artifact
round-trips to the same plan and state, and whether the decoded plan preserves
the fixture's output. Component ledgers can reveal whether a difference comes
from program text, memory, observations or repeated history. These are useful
representation and execution measurements before a learned-agent pilot.

They cannot rank the named research systems, establish how reliably a model
would generate the formats, measure a trained semantic vocabulary, or show
lower deployed inference cost. A local numeric format that loses to compact
Python remains a valid observation about that format and tokenizer. A tie under
equal encoding opportunities remains evidence of a shared mechanism.

The article should consequently state one bounded proposition: AIN/AICC explores
whether a learned computational record can preserve the information needed for
continued authoring, execution and handoff while reducing repeated interaction
demand. The novelty of a particular record design remains a question to resolve
against the close neighbors above. The present contribution is the explicit
comparison, evidence boundaries and reproducible local apparatus.

For execution commands, format definitions and the frozen evaluation rules, use
the [local representation-comparison protocol](../experiments/representation_comparison/PROTOCOL.md).
Expected numerical results belong to that versioned experiment's report. This
related-work document does not substitute a literature description for an
executed comparator.
