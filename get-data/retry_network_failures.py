"""Retry recorded network failures once; successful files are left untouched."""
import argparse
import json
import shutil
from datetime import datetime, timezone
from download_sources import ROOT, LEDGER, fetch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--since', required=True)
    args = parser.parse_args()
    latest = {}
    for line in LEDGER.read_text().splitlines():
        row = json.loads(line)
        latest[(row['source_id'], row['source_url'])] = row
    markers = ('Network is unreachable', 'Failed to resolve', 'Network is down',
               'No route to host', 'ConnectTimeoutError', 'Read timed out',
               'Connection aborted', 'Connection reset', 'RemoteDisconnected')
    queue = [r for r in latest.values() if r['source_id'] == 'lrhmaterials'
             and r['status'] == 'failed' and r.get('retrieved_at', '') >= args.since
             and any(m in r.get('error', '') for m in markers)]
    (ROOT / 'get-data/network-retry-queue.jsonl').write_text(
        ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in queue))
    counts = dict(successful=0, failed=0)
    state = ROOT / 'get-data/network-retry-state.json'

    def report(phase):
        result = dict(phase=phase, updated_at=datetime.now(timezone.utc).isoformat(),
                      total=len(queue), **counts)
        tmp = state.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(result, indent=2)); tmp.replace(state)
        print(json.dumps(result), flush=True)

    report('running')
    for row in queue:
        if shutil.disk_usage(ROOT).free < 20 * 1024**3:
            report('stopped_low_disk_space')
            return 1
        result, _ = fetch((row['source_id'], row['source_url'], row['discovered_on'],
                           row.get('language', 'unknown'), 0))
        counts[result['status']] += 1
        report('running')
    report('finished')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
