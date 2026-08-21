import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'corpus' / 'public-repositories-v1.jsonl'
rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
assert len(rows) == 10
assert len({r['repository'] for r in rows}) == 10
for r in rows:
    assert r['evaluation_status'] == 'intake_only'
    assert r['ground_truth_status'] == 'unknown'
    assert r['revision'] == 'HEAD'
    assert r['revision_status'] == 'resolve_and_pin_at_evaluation'
print(f'VALID: {len(rows)} external repositories; no ground-truth labels asserted.')
