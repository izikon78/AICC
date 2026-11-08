# AIN and AICC final-draft publication

Izik Bachar, concept, architecture and research direction. Prepared with Codex
assistance. 8 November 2026. Current publication on `main`.

AIN is a reference concept for an AI-oriented language and native compiler.
The article explains how a learned operation reference can resolve a predefined
method and its approved native implementation. Current experiments implement
bounded components of that proposal.

## Article and supporting documents

AI agents should first select a review or reconstruction route in the
[agent review guide](AGENT_REVIEW.md). The article and evidence links below reveal
expected outcomes; an independent first reconstruction should follow its allowed
reading order before opening them.

Read [Giving AI a Language of Its Own](AICC_Final_Draft.md), or open
its [review PDF](AICC_Final_Draft_Review.pdf). The article preserves the origin
story, explains the theory through five conventional-language/AIN pairs,
presents selected final findings and proposes a concrete research programme.

The supporting documents stand alone,

- [AIN theory](AIN_THEORY.md) defines meaning, notation and experimental assumptions.
- [Evidence index](EVIDENCE.md) links final source, raw records, metric definitions and contributor provenance.
- [Research programme](RESEARCH_PLAN.md) gives hypotheses, proposed budgets, outcomes and decision gates.
- [Examples](examples/README.md) supply operation contracts, mock scenarios and an executable AICC binding check.
- [Figures](figures/README.md) supply charts, source data and rebuild instructions.
- [Closest related approaches](RELATED_WORK.md) distinguish reviewed systems from locally executed controls.
- [Local text comparison](../experiments/representation_comparison/README.md) provides a bounded CPU test and raw results.
- [Publication validation](VALIDATION.md) records executed checks and output identities.

No earlier article draft is required to read the publication or use its test
instructions. Frozen primary records preserve their original source and
provenance. The evidence index distinguishes executed, modeled and proposed work.

## Test package

[Download AICC_Final_Experiments_Packet.zip](downloads/AICC_Final_Experiments_Packet.zip)
and begin with [START_HERE](reproduction/START_HERE.md). Run packet commands from
the extracted packet root. The archive includes pinned tokenizer assets and
integrity manifests. It includes no model weights or saved adapters. Installing
Python dependencies may require Internet access.

| Route | Purpose and requirements |
|---|---|
| Independent reconstruction | Write a counter from the contracts and semantic traces, then preserve the first implementation and outputs before comparison |
| Exact CPU replay | Reproduce the frozen approved-core accounting with Python 3.12 and pinned packages |
| Native compiler | Check bounded compact-source execution with the shared LLVM backend and its separately pinned dependencies |
| Processing | Rerun supplied processing workloads with the declared NumPy environment and sufficient RAM/time |
| GPU adaptation | Inspect or rerun the final small-model configuration in a separately prepared CUDA/PyTorch environment |

Reading the article or expected totals counts as prior exposure. Disclose it in
a reconstruction report. Replaying saved results differs from running a fresh
model adaptation or million-event workload. Unknown authoring usage remains
unknown, and provider/model identities retain their submitters' reported status.

## The programme beyond reproduction

The six phases reproduce and stress the theory, establish operational fluency,
measure continuing work, test generalization and memory, measure AICC lifecycle
value, and replicate before scaling. The proposed next pilot uses matched
compact Python, readable IR and AIN agents on build/change/repair/handoff chains.
All attempts and tool interactions count. Sample sizes, limits and decision
margins in the programme are proposed choices rather than additional results.

The existing approved-core calculation grants fluent representation, approved
core, correct composition and equal cost per counted position. The next learned
study asks whether correct composition and lower complete-workflow costs can be
achieved together on unseen work. Shared-interface gains, AIN-specific gains,
AICC lifecycle gains and negative findings each support a distinct decision.
