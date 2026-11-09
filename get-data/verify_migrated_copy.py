"""Verify successfully downloaded files after migration; no network access."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--size-only',action='store_true');args=parser.parse_args()
    inventory=ROOT/'raw-data/_handover/copy-verification.jsonl'
    rows=[json.loads(line) for line in inventory.read_text().splitlines() if line.strip()]
    print(json.dumps({'started_at':datetime.now(timezone.utc).isoformat(),'total_files':len(rows),'total_bytes':sum(r['bytes'] for r in rows)}),flush=True)
    issues=[];checked=0
    for row in rows:
        if checked%100==0:print(json.dumps({'checked':checked,'issues':len(issues),'next_file':row['local_path']}),flush=True)
        path=ROOT/row['local_path'];reason=None
        if not path.is_file():reason='missing'
        elif path.stat().st_size!=row['bytes']:reason='size mismatch'
        elif not args.size_only:
            digest=hashlib.sha256()
            with path.open('rb') as f:
                for chunk in iter(lambda:f.read(4*1024*1024),b''):digest.update(chunk)
            if digest.hexdigest()!=row['sha256']:reason='SHA-256 mismatch'
        if reason:issues.append({'local_path':row['local_path'],'issue':reason})
        checked+=1
    result={'checked_at':datetime.now(timezone.utc).isoformat(),'mode':'size-only' if args.size_only else 'SHA-256 and size','checked_files':checked,'issues':issues}
    out=ROOT/'raw-data/_handover/migration-verification.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False));raise SystemExit(1 if issues else 0)
