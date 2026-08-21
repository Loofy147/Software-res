from __future__ import annotations
import argparse, json
from pathlib import Path
REQUIRED={"record_id","project_id","patch_id","repository","revision","commit_url","evaluation_status","ground_truth_status"}
def main():
 p=argparse.ArgumentParser(); p.add_argument('dataset',type=Path); a=p.parse_args(); rows=[]; seen=set()
 for i,line in enumerate(a.dataset.read_text(encoding='utf-8').splitlines(),1):
  if not line.strip(): continue
  r=json.loads(line); miss=sorted(REQUIRED-set(r))
  if miss: raise SystemExit(f'line {i}: missing {miss}')
  if r['record_id'] in seen: raise SystemExit(f'duplicate {r["record_id"]}')
  seen.add(r['record_id'])
  if len(r['revision'])!=40: raise SystemExit(f'line {i}: invalid git sha {r["revision"]!r}')
  if not r['commit_url'].startswith('https://github.com/'): raise SystemExit(f'line {i}: invalid commit_url')
  if r['evaluation_status']!='metadata_only': raise SystemExit(f'line {i}: evaluation_status must be metadata_only')
  if r['ground_truth_status']!='unknown': raise SystemExit(f'line {i}: ground_truth_status must be unknown')
  rows.append(r)
 if len(rows)<10: raise SystemExit('corpus must contain at least 10 real records')
 print(json.dumps({'records':len(rows),'projects':len({r['project_id'] for r in rows}),'source_kinds':sorted({r.get('source_kind') for r in rows}),'evaluation_statuses':sorted({r['evaluation_status'] for r in rows}),'ground_truth_statuses':sorted({r['ground_truth_status'] for r in rows})},indent=2))
if __name__=='__main__': main()
