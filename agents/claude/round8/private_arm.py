"""Arm C, task 9: call the opaque private capability only through the host, under scope project-a and effect project.policy."""
from benchmark.host.registry import Runtime

_rt = Runtime()
_risk = _rt.bind("private.project_risk_score@1", principal="agent-project-a", scopes=("project-a",), effects=("project.policy",))


def project_risk(event):
    return _risk(event)
