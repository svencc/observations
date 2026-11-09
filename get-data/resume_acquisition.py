"""Verify the migrated collection, then resume supervised public downloads."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'get-data/continuation-state.json'
LOG = ROOT / 'raw-data/_provenance/continuation.log'


def state(phase, **details):
    payload = dict(phase=phase, updated_at=datetime.now(timezone.utc).isoformat(),
                   workflow_pid=os.getpid(), free_bytes=shutil.disk_usage(ROOT).free,
                   **details)
    tmp = STATE.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(payload, indent=2))
    tmp.replace(STATE)
    blockers_path = ROOT / 'get-data/manual-blockers.json'
    blockers = json.loads(blockers_path.read_text()) if blockers_path.exists() else {}
    blockers['lrhmaterials'] = dict(status=phase, updated_at=payload['updated_at'],
                                    reason='Continuation on the larger volume; see continuation-state.json.',
                                    next_step='Inspect migration-verification.json, run-state.json and downloaded.md.')
    blockers_path.write_text(json.dumps(blockers, indent=2))
    print(json.dumps(payload), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--detach', action='store_true')
    args = parser.parse_args()
    LOG.parent.mkdir(parents=True, exist_ok=True)
    if args.detach:
        with LOG.open('a') as log:
            child = subprocess.Popen([sys.executable, str(Path(__file__).resolve())],
                                     cwd=ROOT, stdin=subprocess.DEVNULL,
                                     stdout=log, stderr=subprocess.STDOUT,
                                     start_new_session=True)
        print(json.dumps(dict(workflow_pid=child.pid, log=str(LOG.relative_to(ROOT)))))
        return 0
    with (LOG.parent / 'continuation.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('Another continuation workflow is already running.', flush=True)
            return 1
        state('verifying_migration')
        with (ROOT / 'raw-data/_handover/migration-verification.log').open('w') as log:
            code = subprocess.run([sys.executable, str(ROOT / 'get-data/verify_migrated_copy.py')],
                                  cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
        if code:
            state('blocked_migration_verification', verification_exit_code=code)
            return code
        if shutil.disk_usage(ROOT).free < 20 * 1024**3:
            state('stopped_low_disk_space')
            return 1
        with (LOG.parent / 'extra-sources-continuation.log').open('a') as log:
            download = subprocess.Popen([sys.executable, str(ROOT / 'get-data/extra_sources.py')],
                                        cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        state('downloading', download_pid=download.pid)
        code = subprocess.run([sys.executable, str(ROOT / 'get-data/supervise_downloads.py'),
                               'LRHmaterials-und-Ergaenzungen=' + str(download.pid)], cwd=ROOT).returncode
        download_code = download.wait()
        state('finished' if not (code or download_code) else 'finished_with_errors',
              supervisor_exit_code=code, download_exit_code=download_code,
              note='See run-state.json and downloaded.md for coverage and validation; open sources remain.')
        return code or download_code


if __name__ == '__main__':
    raise SystemExit(main())
