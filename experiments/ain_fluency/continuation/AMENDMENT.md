# Operational continuation v1.1 — 6 November 2026

Publish before resumed participant calls. This amendment preserves protocol v1
and its original stopped dataset. It does not change tasks, grading, model,
reasoning effort, response schemas, predictions or semantic retry rules.

## Why continuation is needed

The frozen run at harness commit `3e3a57b` completed seven successful scored
submissions and the eighth preparation call. Both permitted task requests for
`d30-repair-ain` then returned an account usage-limit error, with no answer,
reasoning, tools or usage counters. The runner correctly stopped and marked the
original run `incomplete_service_failure`. The service reported a reset at 5:03
AM; the user requested resumption after that time. No model correctness failure
was observed on the interrupted repair assignment.

## Fixed continuation rules

1. Preserve `results/current-agent-2026-11-06` unchanged as the original partial
   record. Copy its completed records and partial eighth stage into a separate
   `results/current-agent-2026-11-06-continuation` dataset. These are reused
   observations, not an independent replication; never pool duplicate copies.
2. Permit **one additional request** for the interrupted AIN repair, using the
   exact saved task prompt/schema and already completed preparation. Keep both
   original quota-rejected requests in its attempt list. Do not rerun any
   substantive answer or completed preparation.
3. Run the ten not-yet-started assignments in the original frozen order, with
   the original separate preparation, 300-second cap and one infrastructure
   retry only before substantive output. Stop again on exhausted access/service
   failure; no repeated automatic quota probes.
4. Use the same requested model `gpt-6.1-sol`, effort `ultra` and CLI. Verify all
   original source hashes before every assignment and at completion, plus hashes
   of this continuation adapter. Publish the adapter commit before execution.
5. Preserve all attempts and raw usage. The two rejected requests reported no
   token counters: their usage remains **unknown**, not zero. Consequently a
   complete all-attempt AIN cost and exact primary savings comparison cannot be
   computed from this record. Known completed-call subtotals may be shown as a
   clearly conditional secondary comparison, with the missing requests explicit.
6. Report completed correctness under this **amended continuation**, separately
   from the original preregistered partial outcome. The multi-hour break adds
   service/time confounding, especially to elapsed-time comparisons; model
   identifier equality does not attest an unchanged provider snapshot.

No native training or paid API-key run is introduced. No price or savings
prediction changes after seeing the initial successes. The original neutral
prediction (0% net saving versus readable IR) and conditional 10–20% scenario
remain on record. This operational change enables completion of assigned work;
it cannot turn missing resource measurements into a measured cost saving.
