# AICC and AI-native language efficiency: independent research report

**Author:** Claude Opus 5.5 (Anthropic) · **Date:** 2026-11-03 · **Status:** independent research, not a validation of AICC

## Summary

**Three findings.**

1. **No measured economic advantage for AICC or for the symbolic language exists yet, in our work or in the literature.**
2. **Published industry results show the mechanisms behind AICC already deliver large savings in shipping tools:** load capabilities on demand, keep implementations out of model context, resolve operations deterministically. AICC must therefore beat those tools, not a naive baseline.
3. **The protocol's proposed study sizes cannot detect a 15% saving under realistic run-to-run variance** (simulated power 5–42%). A decisive study needs either a pre-registered effect threshold of at least 30%, or several hundred tasks.

**The three questions in brief:**
- *Token efficiency:* not measured as billed tokens. Tokenizer counts show the AICC solution text was 35% larger than the conventional one, and the symbolic program was not smaller than equivalent Python under a fair comparison.
- *Cost:* not measured. Caching discounts limit what removing repeated context can save to a fraction of the naive estimate. Per-capability registry curation is large; its dollar cost is not measured.
- *Computing time:* inference latency not measured. Runtime overheads were measured: tens of microseconds per call for revalidation and process isolation, 34 ms if a process is spawned per call, and 5–65× slowdowns for *interpreted* symbolic code. Compiling to the host language removes the last.

### Evidence labels used throughout

| Label | Meaning |
|---|---|
| **MEASURED** | Produced by code I ran this session; scripts and logs are in the bundle |
| **TOKENIZER** | tiktoken 0.14.0, `o200k_base`, applied to text artefacts. **Never** billed inference tokens |
| **LITERATURE** | A published result, linked; not replicated by me |
| **MODEL** / **SIMULATION** | Arithmetic or simulation under stated assumptions |
| **OPINION** | Architectural judgement |
| **NOT MEASURED** / **NOT EXECUTED** | Could not be done in this environment |

**Environment.**
- Hardware: a sandbox with 1 vCPU (Intel Xeon, 2.10 GHz).
- Software: Python 3.12.3, Node 22.22.2.
- No model API key, so no API usage objects, billing data, reasoning-token counts or inference latency could be collected.
- **API-billed tokens: NOT MEASURED. Inference cost: NOT MEASURED. Inference latency: NOT MEASURED.**

**Independence.**
- I did not read other agents' Round 9 conclusions.
- I authored the Round 7 and Round 8 artefacts reused here, in this same conversation.
- Any comparison between arms is therefore **same-session and contaminated**.

---

## 1. Scientific and technical references (verified this session)

| # | Source | What it reports | Relevance |
|---|---|---|---|
| 1 | Bai et al., [*How Do AI Agents Spend Your Money?*](https://arxiv.org/pdf/2604.22750), arXiv 2604.22750, Apr 2026 (NeurIPS 2026) | Eight frontier LLMs on SWE-bench Verified. Input tokens, not output, drive agentic coding cost even with caching. Runs on the same task differ by up to 30× in total tokens. Higher usage does not mean higher accuracy | AICC's only plausible token lever is context ingestion. Variance forces many trials |
| 2 | Ghoshal et al., [*Scaling Enterprise Cloud Agents to Thousands of APIs*](https://aclanthology.org/2026.emnlp-industry.179/), EMNLP 2026 Industry, pp. 3040–3055 | A deterministic Operation-Resolver MCP over 280+ SDK clients (~8K operations): success 68% → 77%; total tokens −54.1%; median latency −43.3%; LLM calls −37.8%; tool errors −52.4% | Closest published analogue to AICC's discover/inspect/bind. Its baseline was a production design, not modern tool search |
| 3 | Liu et al., [*CompactionBench*](https://www.microsoft.com/en-us/research/publication/benchmarking-long-horizon-agent-context-compaction-with-compactionbench/), Microsoft Research, Oct 2026 | 13.5M Copilot agentic sessions: the 7.8% that trigger compaction account for 44.2% of tokens, and compaction breaks prefix-cache reuse. Asynchronous compaction cut total cost up to 25.4% and agent time 9.6% | Cache-preserving harness design is a measured, large lever that AICC must outperform |
| 4 | OpenAI, [Agents API observability and usage](https://developers.openai.com/api/docs/guides/agents-api/observability) | Usage reports input (with cached), output (with reasoning) and root/subagent turns. It is best-effort, can be null, is not a final bill, and has no cache-write count | Usage objects alone cannot give exact cost; billing exports are required |
| 5 | OpenAI, [Tool search](https://developers.openai.com/api/docs/guides/tools-tool-search) | Deferred tool loading injects discovered definitions at the end of context to preserve the cache. Discovery adds a step and depends on finding the right tool | AICC's discovery-and-binding idea already ships in a mainstream API: the strong baseline |
| 6 | Anthropic Engineering, [*Code execution with MCP*](https://www.anthropic.com/engineering/code-execution-with-mcp), Nov 2025 | Tools presented as code APIs, loaded on demand, intermediate data kept out of context. One worked example: 150,000 → 2,000 tokens (98.7%). Requires sandboxing and monitoring | Same goal as AICC (don't reprocess what exists); a single example, not a benchmark |
| 7 | AIMultiple, [code-execution MCP replication](https://research.aimultiple.com/code-execution-with-mcp) (industry write-up) | 78.5% fewer input tokens but 2.2× more output tokens; both arms 100% success with GPT-4.1 | Savings on input can be partly offset by output, which costs more per token |
| 8 | Prompt-caching prices, provider docs as summarised by [OpenRouter](https://openrouter.ai/docs/features/prompt-caching) and [DevelopersDigest](https://www.developersdigest.tech/models/cost-levers/anthropic) | Anthropic: cache reads 0.1× base input (0.05× on Opus 5.5 and Sonnet 5.5; 0.025× on Fable/Mythos 5.1); 5-minute writes 1.25×, 1-hour writes 2×. OpenAI: reads 0.25–0.5× depending on model | Removing already-cached context saves 50–97.5% less than a raw token count implies. Secondary sources; re-check current pricing pages |
| 9 | Jangda et al., [*Not So Fast*](https://usenix.org/conference/atc19/presentation/jangda), USENIX ATC 2019 | SPEC CPU compiled to WebAssembly ran 45–55% slower on average than native (peaks 2.08–2.5×) | Runtime cost of sandboxed variants; dated, since runtimes have improved |
| 10 | Wu, Anderson, Guha, [*The Best Programming Language for Tokenmaxxing*](https://arxiv.org/abs/2607.22807), Jul 2026 | Agents spend far more tokens in unfamiliar languages through retries and detours | Direct risk for a new symbolic language with untrained models |
| 11 | Dagan et al., ICML 2024; Cassano et al., MultiPL-T, OOPSLA 2024; Mündler et al., PLDI 2025; Wang et al., CodeAct, ICML 2024 | Tokenizer specialisation needs substantial training; low-resource languages lag; type-constrained decoding cuts compile errors; code actions beat JSON actions | Background for H2 (verified earlier in this conversation) |

---

## 2. Comparison of existing industry approaches

| Approach | What it saves | Measured effect (LITERATURE) | How it relates to AICC |
|---|---|---|---|
| Packages, documentation, LSP, search (today's baseline) | Never reads implementation source | No source read in Round 7 or Round 8 (MEASURED, ours) | AICC Arm B adds nothing measured over it so far |
| Deferred tool loading / tool search [5] | Tool-definition context; cache-preserving | Vendor docs promise savings without a figure | Same mechanism as AICC discovery and binding |
| Code execution with MCP, "Code Mode" [6][7] | Definitions and intermediate data in context | 98.7% in one example; 78.5% input reduction (but 2.2× output) in one replication | Same goal; no shared registry needed |
| Deterministic operation resolver [2] | Discovery calls, context growth, invocation errors | −54.1% tokens, −43.3% median latency, +9 points success | The best evidence that AICC-like resolution helps *at large catalog scale* |
| Context compaction (asynchronous) [3] | Long-session history; preserves cache | −25.4% cost, −9.6% time | Orthogonal; a stronger baseline must include it |
| Prompt caching [8] | Repeated prefix cost | Reads at 2.5–50% of base input price | Shrinks AICC's savings from "not repeating contracts" |

**Implication (OPINION):** the incremental space left for AICC is narrow. It is what a *shared, cross-provider, verified* registry adds beyond each vendor's tool search and code execution. Plausible additions are behavioural guarantees (conformance-tested contracts), cross-provider reuse, and persistent validated decisions. None has been measured.

---

## 3. Experimental results and measurements

### 3.1 Tokenizer measurements of required artefacts (TOKENIZER, MEASURED)

| Approach | Artefact | Bytes | o200k tokens |
|---|---|---:|---:|
| A conventional | Round 8 tasks 1–8 solution | 2,122 | 528 |
| B AICC | Round 8 tasks 1–8 solution, same behaviour via bindings | 2,681 | **713** |
| A and B | Shared contract + task text both arms read | 7,615 | 1,682 |
| A conventional | Round 7 controller in Python, full file | 549 | 139 |
| A conventional | Same, with host-held message templates like the symbolic version | 61 | **27** |
| C symbolic | Round 7 controller in the toy grammar | 45 | **29** |
| C symbolic | Grammar documentation its author had to read | 4,573 | 1,143 |
| C symbolic | Language A controller / its reference sheet (per session) | 140 / 968 | 47 / 317 |
| D symbolic + AICC | — | — | **NOT EXECUTED**: neither toy grammar can express the Round 8 tasks (no dicts, lists, sorting or library calls) |

**Reading:** AICC binding syntax made the solution 35% *larger* (713 against 528 tokens). The symbolic program saves nothing against Python given the same templates (29 against 27). Symbolic authoring carries a large documentation cost unless a model has been trained on the language.

### 3.2 Runtime overhead (MEASURED; median per call, 15 repetitions; full p95 values in `runtime_output.txt`)

| Experiment | Variant | Median |
|---|---|---:|
| E1 binding, `normalize_tag` | Direct import | 0.26 µs |
| | Ordinary policy wrapper (revocation set, expiry) | 0.43 µs |
| | AICC mock binding, revalidated every call (file re-hash) | **14.97 µs (58×)** |
| E1 binding, `digest_json` | Direct / ordinary wrapper / AICC mock | 3.33 / 3.59 / **18.91 µs** |
| E1 binding, `group_by_window` (50 events) | Direct / ordinary wrapper / AICC mock | 72.2 / 71.9 / **89.1 µs (+23%)** |
| E1 binding | `bind()`, one-time per capability | 15.7 µs |
| E2 isolation, one call | In-process | 0.26 µs |
| | Persistent isolated worker process (pipes) | **13.0 µs** |
| | Spawn a fresh process per call | **34.0 ms** |
| E2b WebAssembly in Node, controller n=1000 | Plain JS / Wasm with host imports | 23.1 / **30.8 µs (+33%)**; instantiation 165 µs |
| E3 symbolic, controller n=3 | Native Python | 0.64 µs |
| | Language A compiled to Python | 0.67 µs |
| | Round 7 runtime (parse + interpret) | 27.6 µs |
| | Language A interpreter | 14.9 µs |
| | Language B decode + interpret | 41.6 µs |
| E3 symbolic, controller n=1000 | Native Python | 185 µs |
| | Language A compiled to Python | 205 µs |
| | Round 7 runtime | 950 µs (5.1×) |
| | Language A interpreter | 4,136 µs (22×) |
| | Language B decode + interpret | 4,284 µs (23×) |

**Reading:** revalidating every call by re-hashing a file costs about 15 µs, negligible beside model latency but 58× on trivial hot-path functions. Validating once at bind time against immutable artefacts removes it; an ordinary wrapper costs 0.2 µs. Isolation is cheap with a pooled worker (13 µs) and expensive with spawn-per-call (34 ms). Symbolic code should be compiled, not interpreted.

### 3.3 Harness trials (MEASURED; 10 randomised trials per arm, fresh process each)

| Arm | Task | Pass | Wall time p50 / max | CPU p50 | Peak RSS |
|---|---|---|---:|---:|---:|
| A | Round 8 composition T1–T8 | 20/20 ×10 | 19.2 / 21.0 ms | 19.0 ms | 17.2 MB |
| B | Round 8 composition T1–T8 | 20/20 ×10 | 20.3 / 47.8 ms | 20.3 ms | 17.2 MB |
| B (security) | Private-scope checks | 3/3 ×10 | 17.4 / 29.2 ms | 17.3 ms | 17.2 MB |
| A | Round 7 controller | 6/6 ×10 | 17.6 / 18.5 ms | 17.3 ms | 13.5 MB |
| C | Round 7 controller (symbolic) | 6/6 ×10 | 17.7 / 29.8 ms | 17.5 ms | 13.5 MB |

These rows time the *harness executing finished code*. They are **not** agent development time. All 50 rows are in `AICC_Efficiency_Measurements_Claude.csv`.

### 3.4 Upper bound on caching-aware savings (MODEL)

If the 1,682 tokens of shared contract text vanished from every turn, the savings in base-input-token equivalents would be:

| Turns | Without caching | With caching, read 0.10× | With caching, read 0.05× |
|---:|---:|---:|---:|
| 5 | 8,410 | 2,775 | 2,439 |
| 20 | 33,640 | 5,298 | 3,700 |
| 50 | 84,100 | 10,344 | 6,223 |
| 100 | 168,200 | 18,754 | 10,428 |

With caching, the saving is 11–33% of the naive figure. Agentic coding trajectories are reported to differ by millions of tokens per task [1], so this pilot's contract text is a small share of plausible task cost (estimate).

### 3.5 Statistical power of the protocol's designs (SIMULATION, `power_sim.py`)

| Design | Run-to-run spread σ | Analysis | False-positive rate | Power to detect a true 15% saving |
|---|---:|---|---:|---:|
| Pilot, 12 tasks × 3 trials | 0.5 / 1.0 | Two-level bootstrap | 0.02 / 0.04 | **0.10 / 0.05** |
| Expanded, 30 × 10 | 0.5 / 1.0 | Two-level bootstrap | 0.01 / 0.01 | **0.42 / 0.13** |
| Expanded, 30 × 10 | 0.5 / 1.0 | Tasks-only bootstrap | 0.09 / 0.10 (anti-conservative) | 0.76 / 0.32 |

At σ = 1.0 with the two-level bootstrap:

| Design | Power to detect a true 15% saving | Power to detect a true 30% saving |
|---|---:|---:|
| 60 × 10 | 0.21 | 0.87 |
| 100 × 10 | 0.39 | 0.97 |
| 200 × 5 | 0.47 | 0.99 |

**Assumptions:** log-normal cost per trial; task-level heterogeneity (sd 0.5); success probability 0.8 in both arms; σ = 1.0 chosen to reflect the heavy variance in [1].

**Consequences:**
- A 15% target is not decidable at feasible sizes. Pre-register a target of at least 30%, or plan for more than 1,000 task-trials per arm.
- Resample trials within tasks, not only tasks: tasks-only resampling roughly doubles false positives.
- My own harness's dry run on synthetic, identical arms produced a spurious 24% "saving" from a chance success-rate gap. Small studies will produce such artefacts.

---

## 4. Expected advantages and disadvantages (OPINION, grounded in the evidence above)

| Approach | Plausible advantages | Disadvantages and cases where it is worse |
|---|---|---|
| **A, modern baseline** | Mature ecosystems, tool search, code execution, caching, compaction; no curation cost | Re-reads docs across sessions without persistent memory; catalog discovery degrades at very large scale [2] |
| **B, AICC** | Large catalogs (thousands of operations) where deterministic resolution helps [2]; machine-checkable contracts and authorisation; cross-provider reuse *if* contracts are conformance-tested | Larger call syntax (+35% tokens here); discovery and verification steps; contract curation (Round 8: 18 probes, a 625-token contract, 23 KB of tables and 1,206 conformance vectors for one function); cross-provider divergence (Round 8: 46% agreement for a naive variant); savings shrink under caching; worse for small catalogs, single sessions, thin functions and fast-changing requirements |
| **C, symbolic authoring** | Possibly shorter outputs after training; constrained decoding over a closed vocabulary | No measured token saving (29 vs 27); 317–1,143 tokens of documentation per session; retries in unfamiliar languages [10]; 5–65× runtime cost if interpreted |
| **D, combined** | Only if both B and C have independent value | Not expressible with current prototypes; compounds both sets of costs |
| **E, trained operation tokens** | Shorter outputs and exact constrained decoding | Training cost, regression risk, lost names channel; untested |

---

## 5. Technical obstacles

1. **Telemetry:** cost claims need billing exports, not usage objects. Usage is best-effort and omits cache writes [4].
2. **Variance:** run-to-run spread of up to 30× [1] makes moderate effects statistically undetectable without very large studies (Section 3.5).
3. **Contract sufficiency:** Round 8 found 11 of 16 cross-provider equivalence checks UNKNOWN. Making one function interoperable required normative Unicode tables.
4. **Cache interaction:** the registry must not break prefix caches; tool search solves this by appending definitions [5]. Cached input is billed at 2.5–50% of base price [8].
5. **Registry economics:** curation, security review, conformance testing and revalidation must be amortised over real reuse counts, none of which are measured yet.
6. **Isolation:** real private execution needs process, WebAssembly or TEE boundaries (13 µs to 34 ms per call here, plus Wasm compute overhead [9]) and key custody. The mock had none of this.
7. **Expressiveness:** the symbolic prototypes cannot express ordinary composition tasks, so Arm D cannot be run.

---

## 6. Independent assessment

**H1, public reusable capabilities: undemonstrated; plausible only in a narrow regime.**
- *Evidence:* Round 7 and Round 8 show no advantage over a strong baseline. The token and cost levers exist in literature [2][5][6], but they are already available without a commons.
- *Where it could win:* very large capability catalogs, multi-provider settings that need behavioural guarantees, and repeated multi-session maintenance.
- *Confidence:* low that it beats a modern baseline at a ≥30% cost improvement.

**H2, AI-native language: not tested; prior evidence negative.**
- *Evidence:* no trained model exists. Toy artefacts show no saving under a fair comparison and large documentation overhead. Interpreted runtimes are slow.
- *Confidence:* low, pending an equal-budget trained-model study.

**H3, persistent scoped binding: no benefit beyond ordinary caching demonstrated.**
- *Evidence:* within-session savings are already captured by cache-preserving tool loading. Cross-session value is unmeasured. Per-call revalidation has a measurable runtime cost unless validation happens once at bind time.
- *Confidence:* low to moderate that cross-session persistence yields a small saving. The stakes per turn are small under caching.

**H4, public/private federation: not established.**
- *Evidence:* the mechanisms are known (process, WebAssembly and TEE isolation; KMS), with measured runtime cost here. Security and economics in a real host are untested.
- *Confidence:* it is feasible as engineering; there is no evidence of an economic advantage.

**Overall (OPINION):** the commons deserves further study as a *standard for conformance-tested shared contracts*, evaluated on large catalogs and multi-session work. It does not yet warrant claims of token, cost or time savings. The symbolic language should be separated entirely, and studied only with a trained model.

---

## 7. Proposed decisive benchmark (PROPOSED; harness provided)

**Primary endpoint:** amortised cost per successful task, B against A, paired by task. Cost comes from billing exports plus tool, compute and amortised registry cost. Analyse with a two-level bootstrap (`decisive_benchmark_harness.py`, tested in dry-run mode only).

**Arms:**
- A: packages, docs, tool search with deferred loading, code execution, prompt caching, compaction.
- A+: A plus conformance vectors.
- B: AICC registry and bindings, same implementations.
- C: symbolic authoring with A's tools.
- D: B plus C.
- E: separate study with a trained operation-token model.

**Task families:** the protocol's five families, plus two where AICC could plausibly win:
- *Large catalog:* at least 1,000 capabilities with near-misses.
- *Multi-session maintenance:* at least 5 sessions per project, with requirement changes and library-version drift.

**Size:** at least 60 tasks × 10 independent trials per arm, which gives about 0.87 power for a true 30% saving at σ = 1.0. A 15% target needs more than 200 × 5 and still stays under 50% power, so pre-register **≥30%** unless variance proves lower in the pilot.

**Telemetry, per trial:**
- uncached input, cached input, cache-write, output and reasoning tokens (root and subagents);
- billed cost; wall, model, tool, bind and verification time;
- CPU; peak RSS; retries; source reads;
- every failed and incomplete trial.

**Cold versus warm:** report cold-start and warm workflows separately, and per task family.

**Registry cost:** log curation hours and tokens per capability (contracts, conformance vectors, security review) and amortise them over *measured* reuse.

**Decision rule, pre-registered:** B beats A only if its cost-per-success confidence interval excludes zero at a ≥30% reduction, with non-inferior correctness and safety (margin 2 points). Report results per family and per provider. Thresholds must not change after results are seen.

**Isolation cost:** measure the runtime overhead of real isolation (pooled worker, WebAssembly, TEE) separately; numbers here suggest microseconds per call when workers are pooled.

---

## 8. Limitations and reproduction

**Limitations:**
- No model API access: every billed-token, cost and inference-latency figure is NOT MEASURED.
- Harness trials time finished code, not development.
- Single-vCPU sandbox timings are noisy and hardware-specific.
- The simulations depend on the stated variance assumptions.
- Pricing data comes from secondary summaries of provider documentation.
- I authored the reused artefacts in this conversation.

**Reproduction:** `run_all.sh` requires the Round 7 and Round 8 packet directories, with my earlier submissions, at the paths listed in the scripts.

| File | Purpose |
|---|---|
| `bench_runtime.py` | E1–E3 |
| `bench_wasm.js`, `controller.wat` | E2b |
| `harness_trials.py`, `trial_wrapper.py` | E4 |
| `token_table.py` | Tokenizer counts |
| `cost_model.py` | Caching-aware cost model |
| `power_sim.py`, `power_sim_ext.py` | Power simulations |
| `build_csv.py` | Builds the measurement CSV |
| `decisive_benchmark_harness.py` | Proposed benchmark harness |
| `*_output.txt`, `*.json` | Logs and raw results |
| `AICC_Efficiency_Measurements_Claude.csv` | 55 rows: 50 harness trials, 3 authoring rows, and NOT EXECUTED rows for D and E |
| `dry_run_trials.csv` | **Synthetic** test fixture, not data |
