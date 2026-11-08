"""Execute the article's shared-binding example against the existing prototype."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from experiments.processing_study.aicc_processing.benchmark import make_runtime
from experiments.processing_study.aicc_processing.data import Job, events, output_summary
from experiments.processing_study.aicc_processing.kernels import process_reference
from experiments.processing_study.aicc_processing.runtime import IncompatibleCapability


def validate():
    job = Job("article-binding-example", 50, 10, 0.15, False, seed=1107)
    records = list(events(job))
    requirements = {"behavior": "events-v1", "input_order": "any"}
    obligations = ("exact-event-groups",)
    expected = output_summary(process_reference(records, job.window, job.minimum))
    host = make_runtime()
    binding = host.bind("events.cached@1", obligations=obligations, requirements=requirements)
    result = output_summary(binding(records, job.window, job.minimum))
    handoff_record = binding.export_record()
    receiver = make_runtime()
    restored = receiver.restore(handoff_record, principal="anonymous",
                                requirements=requirements, obligations=obligations)
    received = output_summary(restored(records, job.window, job.minimum))
    rejected = False
    try:
        receiver.restore(handoff_record, principal="anonymous",
                         requirements={"behavior": "different-event-rules"})
    except IncompatibleCapability:
        rejected = True
    checks = {"bound_call_matches_reference": result == expected,
              "compatible_handoff_matches_reference": received == expected,
              "incompatible_receiving_requirements_rejected": rejected}
    if not all(checks.values()):
        raise AssertionError(checks)
    return {"scope": "In-process example against the preserved processing prototype",
            "model_calls": 0, "checks": checks, "output_signature": expected}


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
