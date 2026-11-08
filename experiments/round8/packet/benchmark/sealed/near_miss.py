"""Deliberately bad variants for semantic near-miss tests; do not inspect when solving."""
from benchmark.sealed import public_core
from decimal import Decimal
from urllib.parse import urlencode

def parse_money_bankers(value: str) -> int:
 return int((Decimal(value.strip())*100).quantize(Decimal('1'))) # HALF_EVEN

def safe_path_loose(value: str) -> str:
 return str(value).replace('..','').lstrip('/')

def group_by_eventid(events: list, window: int) -> list:
 return [{'event_id':e.get('event_id'), 'count':1} for e in events]
