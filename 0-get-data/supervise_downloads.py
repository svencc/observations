"""Supervise detached downloads and refresh the requested Markdown logs.

Usage: python3 0-get-data/supervise_downloads.py --detach NAME=PID ...
The supervisor does not use credentials, request access, or send messages.
"""
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'0-get-data/run-state.json'

def alive(pid):
    try:
        cmd=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True).strip()
        return bool(cmd and '0-get-data/' in cmd)
    except (subprocess.CalledProcessError,ProcessLookupError):return False

def run_script(name):
    return subprocess.run([sys.executable,str(ROOT/'0-get-data'/name)],cwd=ROOT).returncode

def drive_coverage():
    ids=set()
    for name in ['drive-inventory.json','extra-drive-inventory.json']:
        p=ROOT/'raw-data/sptv-drive/_provenance'/name
        if p.exists():ids.update(row[0] for row in json.loads(p.read_text()))
    attempted=set()
    for line in (ROOT/'0-get-data/download-manifest.jsonl').read_text().splitlines():
        r=json.loads(line)
        if r['source_id']=='sptv-drive' and '/file/d/' in r['source_url']:attempted.add(r['source_url'].split('/d/')[1].split('/')[0])
    return {'inventoried_files':len(ids),'files_attempted':len(ids & attempted),'not_yet_attempted':len(ids-attempted)}

def write_state(state,tasks,**extra):
    obj={'state':state,'updated_at':datetime.now(timezone.utc).isoformat(),'supervisor_pid':os.getpid(),'tasks':tasks,**extra}
    tmp=STATE.with_suffix('.json.tmp');tmp.write_text(json.dumps(obj,indent=2));tmp.replace(STATE)

def main():
    if '--detach' in sys.argv:
        args=[a for a in sys.argv[1:] if a!='--detach']
        log=ROOT/'raw-data/_provenance/supervisor.log';log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('a') as f:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),*args],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        print(json.dumps({'supervisor_pid':child.pid,'log':str(log.relative_to(ROOT))}));return
    tasks=[]
    for arg in sys.argv[1:]:
        name,pid=arg.rsplit('=',1);tasks.append({'name':name,'pid':int(pid),'state':'running'})
    try:
        while True:
            for task in tasks:
                if task['state']=='running' and not alive(task['pid']):task['state']='exited'
            low_space=shutil.disk_usage(ROOT).free<20*1024**3
            if low_space:
                for task in tasks:
                    if task['state']=='running':os.kill(task['pid'],signal.SIGTERM);task['state']='stopped_low_disk_space'
            active=any(t['state']=='running' for t in tasks)
            write_state('running' if active else 'finalizing',tasks,drive_coverage=drive_coverage())
            run_script('write_download_report.py')
            if not active:break
            time.sleep(30)
        code_torrent=run_script('verify_torrent_files.py')
        code_validation=run_script('validate_downloads.py')
        coverage=drive_coverage()
        final='finished_with_incomplete_queue' if coverage['not_yet_attempted'] else 'finished_with_results_and_open_items'
        write_state(final,tasks,drive_coverage=coverage,verification_exit_codes={'torrent_recheck':code_torrent,'local_validation':code_validation},note='All supervised processes have ended. Consult downloaded.md for successful, failed and partial results; this is not a claim of a complete collected edition.')
        run_script('write_download_report.py')
    except Exception as e:
        write_state('supervisor_error',tasks,error=type(e).__name__+': '+str(e))
        run_script('write_download_report.py')
        raise

if __name__=='__main__':main()
