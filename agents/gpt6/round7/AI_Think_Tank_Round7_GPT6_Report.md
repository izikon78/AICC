# Round 7 — Independent GPT-6 Experimental Results

**Model/provider:** GPT-6 / OpenAI ChatGPT  
**Date:** 2026-11-03  
**Protocol:** Round 7 packet v1.0 (as supplied)  
**Environment:** Python 3.13.5, Linux container, Python standard library; no `tiktoken`  
**Tools used:** container Python interpreter, filesystem, fixture test harness  
**Previous model analyses seen:** Yes — Claude's partial V3 review, Gemini's analyses, and Grok's questions from the prior conversation. No Round 7 results from the others seen.  
**Fresh trials per arm:** One. All arms authored in one model session. **The A/B comparison is exploratory and not independently blinded.**  
**Reference implementation exposed to model?** No. I did not open or inspect `fixtures/capabilities.py`. Python imports and a host SHA-256 digest read its bytes internally, without displaying its source. I did read `fixtures/registry.py` to understand the binding API.

## 1. Hypothesis verdicts

| Hypothesis | Status | Evidence from this run | Provisional verdict |
|---|---|---|---|
| **H1:** Reuse without reading implementations saves development cost | Partially tested | Both standard-library reuse and registry reuse pass 14/14 without inspecting implementation. Registry adds documentation/selection overhead in this fixture. | **Not established**: existing Python libraries already satisfy no-body-reading here; no total token or cost evidence. |
| **H2:** AI-native authoring outperforms mainstream languages | Toy representational feasibility tested; trained-model hypothesis not tested | Python and fixed-grammar symbolic code both pass 6/6; symbolic file is 46 bytes, Python file 350 bytes. | **Open**: byte compactness, but no native-token model, actual token usage, or cost/correctness advantage proven. |
| **H3:** Cached compatibility handles avoid repeated context | Serialized-payload simulation and toy binding guards executed | Repeating one 1,728-byte contract 20 times costs 35,000 bytes with calls; supplying it once + binding and 20 calls costs 2,198 bytes. | **Payload reduction demonstrated**, not persistent model familiarity or savings against a competent cached ordinary-library API. |

## 2. Executed tests

| Arm | Execution status | Passes | Reference implementation inspected? | Retries | Caveat |
|---|---|---:|---|---:|---|
| **A** — conventional Python API | EXECUTED, same-session exploratory | **14/14** | No | 0 | Strong baseline: ordinary preexisting functions imported without opening their source |
| **B** — registry binding | EXECUTED, same-session exploratory | **14/14** | No | 0 | Binding API inspected; model saw candidate cards and baseline contract |
| **C** — new Python | EXECUTED | **6/6** | No | 0 | Tests verify exact observable log traces at six inputs |
| **D** — toy symbolic | EXECUTED | **6/6** | No | 0 | Parser/runtime predefined operations and log templates; not an AI-trained opcode language |
| **H3** — toy trust controls | EXECUTED | **3/3 checks printed PASS** | No | 0 | Checks only effects declared in registry and a file digest mismatch |

The generated correct wrapper and two controller implementations passed on their first execution. These are *one-off, small-fixture observations*, not pass-rate estimates from multiple stochastic model trials.

## 3. Artifact sizes and input context

**Measured in this session (bytes / Unicode characters, not model tokens):**

| Artifact | Bytes | Characters | Purpose |
|---|---:|---:|---|
| `fixtures/baseline_api.md` | 1,205 | 1203 | Conventional API documentation |
| `fixtures/capability_cards.md` | 1,436 | 1424 | Registry candidates, including near misses |
| `fixtures/activity_contract.md` | 1,728 | 1728 | Behavioral contract shared by both arms |
| `fixtures/registry.py` | 1,428 | 1428 | Host binding source read as interface |
| `fixtures/capabilities.py` | 5,319 | NOT INSPECTED | Implementation file, size from file metadata ONLY |
| `submission_A.py` | 379 | 379 | Arm A wrapper |
| `submission_B.py` | 665 | 665 | Arm B wrapper |
| `controller_submission.py` | 350 | 350 | Arm C newly authored code |
| `controller_submission.sym` | 46 | 46 | Arm D symbolic program |

A's basic provided documentation is 1,205 bytes, plus a 1,728-byte common activity specification. B's registry cards add another 1,436 bytes and refer back to baseline/API behavior. Thus **B does not show documentation-byte savings over A in this fixture**. Inspecting the host's `registry.py` added additional context to B. Neither arm read the 5,319-byte reference implementation.

**Exact tiktoken counts: NOT MEASURED.** `tiktoken` is absent and an attempt to install it in the environment failed. The optional `token_measure.py` printed `NOT MEASURED: tiktoken unavailable; do not infer token numbers.` The local program sizes do not predict tokenizer efficiency. API-reported model input/output/reasoning tokens, tool-call tokens, and wall-clock per-task costs were not available. Consequently **cost per correctly completed task is UNKNOWN**.

The symbolic program is about **7.61× smaller by bytes** than this Python program, but the symbolic runtime already defines `T0`, `T1`, `!7`, and the counted-loop behavior. Their implementation/development costs and grammar context are not represented by those 46 bytes. It would be invalid to treat this as a measured 7.61× reduction in model inference.

## 4. H3: repeated contract vs. cached handle

The simulation used the **exact contents of `fixtures/activity_contract.md`**, a 1,728-byte UTF-8 file, and these illustrative per-call/bind strings:

```text
CALL rc(events,600,0)
BIND rc=cap:activity.rollup@1
```

| Payload scheme | Calls | Total serialized bytes |
|---|---:|---:|
| Full contract reprinted before *every* call | 20 | **35,000** |
| Contract once, local binding once, calls thereafter | 20 | **2,198** |
| Difference | 20 | **32,802 fewer bytes (93.72%)** |

The model did not repeatedly see these payloads; I computed exact byte counts for two constructed strings. There was **no actual 20-invocation model run with API token telemetry**, no cross-session cache, no certificate issuance, no revocation system. An ordinary Python API with cached documentation can obtain very similar payload reductions: this result is not a unique advantage of H3.

The `binding_checks.py` script printed three passes for declared unauthorized effects, an incorrect expected artifact digest, and successful re-use. The registry returns the same callable reference on repeated lookups; it does not actually mint a signed certificate, persist trust across agents, or enforce capability permissions on all possible runtime effects.

## 5. Near misses, safety and contract sufficiency

**Rejected by contract before execution:**

- `cap:controller.logs_zero_based@1`: same type as correct logging capability but wrong restart ordinal; candidate card explicitly says `run 1 of 2` instead of `run 2 of 2`.
- `cap:activity.rollup_by_eventid@1`: same function signature but groups by event ID instead of normalized behavior; candidate card explicitly identifies mismatch.
- `cap:activity.rollup_and_save@1`: declares `filesystem.write`, which is forbidden for the pure analysis request; the toy binder rejects the handle when `allowed_effects=()`.

**Adversarial executable confirmation:**

- Intentionally selecting the wrong controller handle passed **11/14**, failing controller cases at n=2,3,17. The n=2 actual string is `Restarting controller service for run 1 of 2` versus required `run 2 of 2`.
- Intentionally selecting wrong event-ID grouping passed **12/14**, failing the two rollup cases that require combining distinct event IDs into one group.
- Unauthorized `filesystem.write` handle was rejected during bind with `CapabilityDenied("denied effects: ['filesystem.write']")`.

**Strongest concern:** These near misses are helpfully described in the registry cards. A real registry can have contracts that omit or misstate exact ordering, data dependencies, locale assumptions, privacy effects, concurrency, or timing. Type agreement and signatures cannot establish observational equivalence. The fixture checks declared effects in a hard-coded map, not inferred behavior; a dishonest implementation with hidden side effects could bypass a naive policy unless the runtime independently restricts its authority. The toy checks do not establish zero-trust security.

## 6. What is withheld on the successful H1 path?

The agent did **not** read the reference capability implementation (`capabilities.py`, 5,319 bytes by filesystem metadata), its helper function internals, or its full source. It did receive API documentation, the full activity behavior contract, and for B the list of candidate cards. The host still imported and executed the implementation as normal Python code.

For this task **no capability source reading was needed in either arm**. Consequently the proper comparison is **registry B vs strong existing-library A**, not B vs regenerating all functionality from scratch. H1's unique contribution requires evidence of improved retrieval, validated selection, or reuse persistence beyond what ordinary package APIs and model context caching already offer.

## 7. Strongest skeptical conclusion

All positive correctness tests passing demonstrates executable feasibility, not the proposed architecture's economic superiority. Both A and B meet H1's no-source-reading condition. The registry adds candidate-card selection and policy mechanics, but this benchmark has no observed total-token savings relative to the strong baseline. The toy symbolic notation produces a much shorter file yet is far from a generally useful language and its model-token / reasoning costs remain unknown. The H3 payload simulation proves a trivial repeated-text saving that conventional caching also achieves.

## 8. Architectural change and decisive next experiment

**Architecture change:** Keep the reusable capability registry, verified binding cache, and AI-native authoring representation as independently testable layers. Reuse-eligible capabilities should expose a typed, machine-checkable contract, effects, and provenance. Once a consumer proves compatibility in a specific scope, a small host-enforced reference should suffice for later calls until assumptions change. New authoring language experiments must control for the ordinary-language baseline having the same capability access.

**Decisive next experiment:** Blind, randomized multiple fresh-agent trials on 100+ unfamiliar multi-file tasks with realistic repositories and near-miss APIs. Compare (A) Python/TypeScript plus good packages/docs/caching, (B) identical stack plus capability registry and verified handle cache, (C) the same capabilities with symbolic textual authoring, and (D) a model/adapter actually trained on native operation tokens. Measure API-reported input/output/reasoning tokens, cached-prompt billing, tool time, tests, retries, false reuse, security failures, and **cost per correctly completed task**. Require non-inferior correctness and safety before counting cost savings. Publish confidence intervals and failures, not just averages.

**What would change my mind:** For H1/H3, consistent net task-cost reduction over strong baseline on tasks with large reusable bodies, *without* more false matches or permission failures. For H2, a trained native-operation model matching Python's hidden-task correctness at lower all-in cost, including training amortization, verification, and debugging.

## 9. Evidence labels

- **MEASURED HERE:** 14/14 for A and B; 6/6 for C and D; three printed PASS binding checks; two deliberate near misses failed selected tests; script/document bytes and H3 serialized-payload difference.
- **REPORTED BY OTHER MODELS, NOT REPLICATED HERE:** Claude's token benchmarks and mutation-rate claims; Gemini's H1/H2 economic forecasts; Grok's concerns. This report does not use their numbers as observations.
- **HYPOTHESIS / DESIGN PROPOSAL:** Verified cross-agent binding certificates; stable native opcode vocabulary; general-purpose semantics; net token savings; zero-trust sandbox security; learnable operational intelligence.

## 10. Reproduction

Run from the directory containing `fixtures/`:

```bash
python fixtures/test_tasks.py --submission submission_A.py
python fixtures/test_tasks.py --submission submission_B.py
python fixtures/test_tasks.py --python-controller controller_submission.py
python fixtures/test_tasks.py --symbolic controller_submission.sym
python fixtures/binding_checks.py
python fixtures/test_tasks.py --submission submission_bad_zero.py
python fixtures/test_tasks.py --submission submission_bad_eventid.py
python measure_artifacts.py
```

Outputs and all generated files are bundled alongside this report. The original test fixtures remain unchanged. The exact console JSON for all four positive arms and the three binding checks is reproduced below.

### Arm A

```json
{
  "passed": 14,
  "total": 14,
  "cases": [
    {
      "case": "controller n=-2",
      "pass": true
    },
    {
      "case": "controller n=0",
      "pass": true
    },
    {
      "case": "controller n=1",
      "pass": true
    },
    {
      "case": "controller n=2",
      "pass": true
    },
    {
      "case": "controller n=3",
      "pass": true
    },
    {
      "case": "controller n=17",
      "pass": true
    },
    {
      "case": "rollup case 1",
      "pass": true
    },
    {
      "case": "rollup case 2",
      "pass": true
    },
    {
      "case": "rollup case 3",
      "pass": true
    },
    {
      "case": "rollup case 4",
      "pass": true
    },
    {
      "case": "rollup case 5",
      "pass": true
    },
    {
      "case": "error (0, 0)",
      "pass": true,
      "actual_error": "ValueError"
    },
    {
      "case": "error (600, 3)",
      "pass": true,
      "actual_error": "ValueError"
    },
    {
      "case": "error (600, 0)",
      "pass": true,
      "actual_error": "TypeError"
    }
  ]
}
```

### Arm B

```json
{
  "passed": 14,
  "total": 14,
  "cases": [
    {
      "case": "controller n=-2",
      "pass": true
    },
    {
      "case": "controller n=0",
      "pass": true
    },
    {
      "case": "controller n=1",
      "pass": true
    },
    {
      "case": "controller n=2",
      "pass": true
    },
    {
      "case": "controller n=3",
      "pass": true
    },
    {
      "case": "controller n=17",
      "pass": true
    },
    {
      "case": "rollup case 1",
      "pass": true
    },
    {
      "case": "rollup case 2",
      "pass": true
    },
    {
      "case": "rollup case 3",
      "pass": true
    },
    {
      "case": "rollup case 4",
      "pass": true
    },
    {
      "case": "rollup case 5",
      "pass": true
    },
    {
      "case": "error (0, 0)",
      "pass": true,
      "actual_error": "ValueError"
    },
    {
      "case": "error (600, 3)",
      "pass": true,
      "actual_error": "ValueError"
    },
    {
      "case": "error (600, 0)",
      "pass": true,
      "actual_error": "TypeError"
    }
  ]
}
```

### Arm C

```json
{
  "passed": 6,
  "total": 6,
  "cases": [
    {
      "case": "python controller n=-2",
      "pass": true
    },
    {
      "case": "python controller n=0",
      "pass": true
    },
    {
      "case": "python controller n=1",
      "pass": true
    },
    {
      "case": "python controller n=2",
      "pass": true
    },
    {
      "case": "python controller n=3",
      "pass": true
    },
    {
      "case": "python controller n=17",
      "pass": true
    }
  ]
}
```

### Arm D

```json
{
  "passed": 6,
  "total": 6,
  "cases": [
    {
      "case": "symbolic n=-2",
      "pass": true
    },
    {
      "case": "symbolic n=0",
      "pass": true
    },
    {
      "case": "symbolic n=1",
      "pass": true
    },
    {
      "case": "symbolic n=2",
      "pass": true
    },
    {
      "case": "symbolic n=3",
      "pass": true
    },
    {
      "case": "symbolic n=17",
      "pass": true
    }
  ]
}
```

### H3 trust checks

```text
PASS: unauthorized effect denied
PASS: mismatching artifact digest denied
PASS: reuse binding available
```

### Wrong controller near miss

```json
{
  "passed": 11,
  "total": 14,
  "cases": [
    {
      "case": "controller n=-2",
      "pass": true
    },
    {
      "case": "controller n=0",
      "pass": true
    },
    {
      "case": "controller n=1",
      "pass": true
    },
    {
      "case": "controller n=2",
      "pass": false,
      "expected": [
        "Starting controller service for 2 runs",
        "Restarting controller service for run 2 of 2"
      ],
      "actual": [
        "Starting controller service for 2 runs",
        "Restarting controller service for run 1 of 2"
      ]
    },
    {
      "case": "controller n=3",
      "pass": false,
      "expected": [
        "Starting controller service for 3 runs",
        "Restarting controller service for run 2 of 3",
        "Restarting controller service for run 3 of 3"
      ],
      "actual": [
        "Starting controller service for 3 runs",
        "Restarting controller service for run 1 of 3",
        "Restarting controller service for run 2 of 3"
      ]
    },
    {
      "case": "controller n=17",
      "pass": false,
      "expected": [
        "Starting controller service for 17 runs",
        "Restarting controller service for run 2 of 17",
        "Restarting controller service for run 3 of 17",
        "Restarting controller service for run 4 of 17",
        "Restarting controller service for run 5 of 17",
        "Restarting controller service for run 6 of 17",
        "Restarting controller service for run 7 of 17",
        "Restarting controller service for run 8 of 17",
        "Restarting controller service for run 9 of 17",
        "Restarting controller service for run 10 of 17",
        "Restarting controller service for run 11 of 17",
        "Restarting controller service for run 12 of 17",
        "Restarting controller service for run 13 of 17",
        "Restarting controller service for run 14 of 17",
        "Restarting controller service for run 15 of 17",
        "Restarting controller service for run 16 of 17",
        "Restarting controller service for run 17 of 17"
      ],
      "actual": [
        "Starting controller service for 17 runs",
        "Restarting controller service for run 1 of 17",
        "Restarting controller service for run 2 of 17",
        "Restarting controller service for run 3 of 17",
        "Restarting controller service for run 4 of 17",
        "Restarting controller service for run 5 of 17",
        "Restarting controller service for run 6 of 17",
        "Restarting controller service for run 7 of 17",
        "Restarting controller service for run 8 of 17",
        "Restarting controller service for run 9 of 17",
        "Restarting controller service for run 10 of 17",
        "Restarting controller service for run 11 of 17",
        "Restarting controller service for run 12 of 17",
        "Restarting controller service for run 13 of 17",
        "Restarting controller service for run 14 of 17",
        "Restarting controller service for run 15 of 17",
        "Restarting controller service for run 16 of 17"
      ]
    },
    {
      "case": "rollup case 1",
      "pass": true
    },
    {
      "case": "rollup case 2",
      "pass": true
    },
    {
      "case": "rollup case 3",
      "pass": true
    },
    {
      "case": "rollup case 4",
      "pass": true
    },
    {
      "case": "rollup case 5",
      "pass": true
    },
    {
      "case": "error (0, 0)",
      "pass": true,
      "actual_error": "ValueError"
    },
    {
      "case": "error (600, 3)",
      "pass": true,
      "actual_error": "ValueError"
    },
    {
      "case": "error (600, 0)",
      "pass": true,
      "actual_error": "TypeError"
    }
  ]
}
```

### Wrong event-ID grouping

```json
{
  "passed": 12,
  "total": 14,
  "cases": [
    {
      "case": "controller n=-2",
      "pass": true
    },
    {
      "case": "controller n=0",
      "pass": true
    },
    {
      "case": "controller n=1",
      "pass": true
    },
    {
      "case": "controller n=2",
      "pass": true
    },
    {
      "case": "controller n=3",
      "pass": true
    },
    {
      "case": "controller n=17",
      "pass": true
    },
    {
      "case": "rollup case 1",
      "pass": false,
      "expected": [
        {
          "device": "aps-1",
          "kind": "alert",
          "message": "Disk Low",
          "first_timestamp": 10,
          "last_timestamp": 20,
          "severity": "critical",
          "count": 2,
          "event_ids": [
            "a",
            "b"
          ]
        },
        {
          "device": "aps-1",
          "kind": "alert",
          "message": "Disk Low",
          "first_timestamp": 80,
          "last_timestamp": 80,
          "severity": "info",
          "count": 1,
          "event_ids": [
            "c"
          ]
        }
      ],
      "actual": [
        {
          "device": "aps-1",
          "kind": "alert",
          "message": "Disk Low",
          "first_timestamp": 10,
          "last_timestamp": 20,
          "severity": "critical",
          "count": 1,
          "event_ids": [
            "a"
          ]
        },
        {
          "device": "aps-1",
          "kind": "alert",
          "message": "Disk Low",
          "first_timestamp": 10,
          "last_timestamp": 20,
          "severity": "critical",
          "count": 1,
          "event_ids": [
            "b"
          ]
        },
        {
          "device": "aps-1",
          "kind": "alert",
          "message": "Disk Low",
          "first_timestamp": 80,
          "last_timestamp": 80,
          "severity": "info",
          "count": 1,
          "event_ids": [
            "c"
          ]
        }
      ]
    },
    {
      "case": "rollup case 2",
      "pass": true
    },
    {
      "case": "rollup case 3",
      "pass": false,
      "expected": [
        {
          "device": "a",
          "kind": "alert",
          "message": "M",
          "first_timestamp": 1,
          "last_timestamp": 9,
          "severity": "critical",
          "count": 3,
          "event_ids": [
            "x",
            "y",
            "z"
          ]
        }
      ],
      "actual": [
        {
          "device": "a",
          "kind": "alert",
          "message": "M",
          "first_timestamp": 1,
          "last_timestamp": 9,
          "severity": "critical",
          "count": 1,
          "event_ids": [
            "x"
          ]
        },
        {
          "device": "a",
          "kind": "alert",
          "message": "M",
          "first_timestamp": 1,
          "last_timestamp": 9,
          "severity": "critical",
          "count": 1,
          "event_ids": [
            "y"
          ]
        },
        {
          "device": "a",
          "kind": "alert",
          "message": "M",
          "first_timestamp": 1,
          "last_timestamp": 9,
          "severity": "critical",
          "count": 1,
          "event_ids": [
            "z"
          ]
        }
      ]
    },
    {
      "case": "rollup case 4",
      "pass": true
    },
    {
      "case": "rollup case 5",
      "pass": true
    },
    {
      "case": "error (0, 0)",
      "pass": true,
      "actual_error": "ValueError"
    },
    {
      "case": "error (600, 3)",
      "pass": true,
      "actual_error": "ValueError"
    },
    {
      "case": "error (600, 0)",
      "pass": true,
      "actual_error": "TypeError"
    }
  ]
}
```

### Forbidden effect bind

```text
REJECTED cap:activity.rollup_and_save@1 "denied effects: ['filesystem.write']"
```

### Token measurement availability

```text
NOT MEASURED: tiktoken unavailable; do not infer token numbers.
```

