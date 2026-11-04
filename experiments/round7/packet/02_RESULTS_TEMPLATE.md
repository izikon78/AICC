# Round 7 — Independent AI agent experiment results

**Model/provider:**
**Model version / configuration (if known):**
**Date:**
**Tools available and actually used:**
**Python version / OS / tokenizer version:**
**Other models' responses seen before this test?** yes/no; details:
**Any implementation automatically indexed/read?** yes/no/unknown:
**Fresh trials per arm:**

## 1. Status and verdict

| Hypothesis | Measured, partially tested, or not tested | Provisional verdict | What would change the verdict? |
|---|---|---|---|
| H1: no-body-reading reuse | | | |
| H2: native authoring | | | |
| H3: reusable validated binding | | | |

## 2. Exact test results

| Arm | Status (EXECUTED / NOT EXECUTED / CONTAMINATED) | Passed / total | Source files read | Retries | Notes |
|---|---|---:|---:|---:|---|
| A: normal Python API reuse | | | | | |
| B: registry and handles | | | | | |
| C: newly authored Python | | | | | |
| D: toy symbolic program | | | | | |
| H3 binding checks | | | | | |

Copy exact test console output here (do not fabricate):

```
[OUTPUT OR NOT EXECUTED]
```

## 3. Reproducible artifact/token accounting

| Artifact or generated content | Exact bytes/chars | Tokenizer & version | Exact tokens (if run) | How measured |
|---|---:|---|---:|---|
| Ordinary API documentation | | | | |
| Registry card + matching contract | | | | |
| Source implementation inspected | | | | |
| Python submission | | | | |
| Symbolic submission | | | | |
| Alias binding + 20 calls | | | | |
| Repeated contract + 20 calls | | | | |

**API-reported input tokens:** measured / unavailable:
**API-reported output tokens:** measured / unavailable:
**Reasoning tokens:** measured / unavailable:
**Total cost per successful task:** measured / unavailable:

## 4. Contract sufficiency and near misses

- Near-miss chosen/rejected and reason:
- Strongest contract that looked compatible but wasn't:
- Did the model need to inspect implementation? Trigger and exact file:
- Which behavior remained unspecified by a contract?
- What failed before execution vs only after tests?

## 5. H3 binding persistence

- What information was in the initial validation?
- What information was *not* reintroduced on subsequent calls?
- How were trust, revocation, policy and environment changes handled?
- Does the experiment actually test persistent model familiarity, or only smaller serialized payloads?

## 6. H2 analysis

- Was the output executable, valid and behaviorally correct?
- Was the language shorter in **model tokens**, not only characters?
- Were symbol fragments problematic for the available tokenizer?
- Did any silent logical error escape type/grammar checks?
- Would a dedicated operation-token model differ, and how could that be tested without assuming the answer?

## 7. Strongest skeptical conclusion

[Describe the strongest reason H1/H2/H3 might not be worth pursuing. Avoid numerical claims not supported by actual experiments.]

## 8. One architecture change and one decisive experiment

[Your change, a low-cost test, a strong baseline, a falsification threshold.]

## 9. Evidence labels

- **MEASURED IN THIS SESSION:**
- **REPORTED BY CLAUDE / GEMINI / GROK, NOT REPLICATED:**
- **HYPOTHESIS / EXTRAPOLATION:**

## 10. Files / commands / reproduction

[Attach generated code, or paste it here. Provide exact commands and output so the coordinating reviewer can reproduce the result.]
