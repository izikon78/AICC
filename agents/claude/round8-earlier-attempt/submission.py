"""Default submission for the grader: the corrected tasks (Arm A acquisition). 20/20."""
from benchmark.public import baseline_api
from _solution_body import build_solution
globals().update(build_solution(lambda name: getattr(baseline_api, name)))
