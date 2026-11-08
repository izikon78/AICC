# Giving AI a Language of Its Own

AIN/AICC working paper, primary evidence and reproducible experiments.
Concept, architecture and research direction by **Izik Bachar**.
Current publication on `main`, dated 8 November 2026.

**AIN (AI Native Language) is a reference concept** for an AI-oriented language
and native compilation architecture. AICC (AI Computational Commons) is the
companion proposal for approved, versioned capabilities. The complete proposed
system remains conceptual; this repository supplies bounded implementations,
measurements and a research programme.

## AI agents and independent reviewers start here

Read the [agent review guide](publication/AGENT_REVIEW.md) before choosing a route.
Prior AIN knowledge is unnecessary.

- **Independent reconstruction:** begin with the [pre-comparison instructions](publication/reproduction/INDEPENDENT_RECONSTRUCTION.md)
  and [standalone theory](publication/AIN_THEORY.md). Preserve the first counter,
  outputs, hashes and read order before consulting the article or expected results.
- **Technical article review or exact replay:** follow the [review guide](publication/AGENT_REVIEW.md)
  and [testing instructions](publication/reproduction/START_HERE.md). Disclose
  earlier exposure to the article or results.

The article, evidence index and saved results reveal expected outcomes. Reading
those first changes the status of an independent reconstruction. First attempts,
failures and corrections should remain separately identifiable.

## Read the publication

- [Article in Markdown](publication/AICC_Final_Draft.md)
- [Review PDF](publication/AICC_Final_Draft_Review.pdf)
- [AIN reference theory and native method explanation](publication/AIN_THEORY.md)
- [Selected final experiments and primary evidence](publication/EVIDENCE.md)
- [Related approaches, including AINL](publication/RELATED_WORK.md)
- [Five source/AIN examples and contract checks](publication/examples/README.md)
- [Figures, CSV inputs and source identities](publication/figures/README.md)
- [Research programme and proposed next studies](publication/RESEARCH_PLAN.md)
- [Publication validation](publication/VALIDATION.md)

The article explains `!501(config)` as a learned reference to a predefined
`ConnectToDB(config)` capability whose approved implementation can be lowered or
linked into native execution. Compilation, text-token measurements, conditional
learned-unit accounting and future trained-agent behavior have separate scope.
Related external projects are reviewed through their publications; their full
runtimes were not benchmarked by the local comparison.

## Download and run the tests

Download the [portable final-experiment package](https://github.com/izikon78/AICC/raw/refs/heads/main/publication/downloads/AICC_Final_Experiments_Packet.zip)
and its [SHA-256/size manifest](publication/downloads/AICC_Final_Experiments_Packet.manifest.json).
The ZIP contains source, saved records, pinned tokenizer assets and current guides.
It includes no model weights or saved adapters. Dependency installation may need
Internet access; the primary CPU replay then runs offline.

From the extracted packet root with Python 3.12,

```text
python scripts/verify_packet.py
python scripts/setup.py
python scripts/run_reference.py --output work/reference-001
python scripts/run_representation_comparison.py --output work/text-comparison-001
```

Use fresh output directories. Select the independent route before executing a
known-answer replay if you want an independent first implementation.
Native compiler, processing and optional GPU adaptation routes are documented in
[the supplementary tests](publication/reproduction/SUPPLEMENTARY_TESTS.md).

For repository checkouts, the [local comparison protocol](experiments/representation_comparison/PROTOCOL.md)
and [observed report](experiments/representation_comparison/results/comparison-v1/REPORT.md)
provide the exact formats, measurement boundaries and raw output locations.
Return a review with source/input/output hashes, environment, read order,
deviations and all attempts, as described in the agent guide.

Earlier drafts and experimental records retain their original paths and history.
The current publication entry point is [publication/README.md](publication/README.md).
