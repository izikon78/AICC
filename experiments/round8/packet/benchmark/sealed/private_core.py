"""Illustrative project-private implementations. No actual secrets are included."""
def risk_score_private(event: dict) -> int:
    """Toy proprietary scoring formula; NOT a security classifier or clinical decision tool."""
    return min(100,max(0, 12*int(event.get('errors',0)) + 7*int(event.get('retries',0)) + (15 if event.get('priority')=='critical' else 0)))
