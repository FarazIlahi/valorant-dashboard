"""Export an explicit public-field allowlist from a private Excel workbook."""
import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import subprocess
import threading
import time
import webbrowser
import zipfile
import xml.etree.ElementTree as ET
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial

ROOT=Path(__file__).resolve().parent
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
FIELDS={'Riot ID':'id','Current rank':'rank','Peak rank':'peak','Comp hours':'comp','Unrated hours':'unrated','DM hours':'dm','Check status':'status','Check date':'checked','Rank verified':'rankVerified','Peak verified':'peakVerified','Comp verified':'compVerified','Unrated verified':'unratedVerified','DM verified':'dmVerified'}
STATUSES={'Verified','Partial data','Renamed — awaiting check','Not found — inconclusive','Tracker error'}

def read_rows(z,path,strings):
    xml=ET.fromstring(z.read(path))
    rows=[]
    for row in xml.findall('.//s:sheetData/s:row',NS):
        values={}
        for c in row.findall('s:c',NS):
            col=re.match(r'[A-Z]+',c.attrib['r'])[0]
            v=c.find('s:v',NS)
            val=v.text if v is not None else None
            if c.get('t')=='s':val=strings[int(val)] if val is not None else None
            elif c.get('t')=='inlineStr':val=''.join(c.itertext())
            values[col]=val
        rows.append(values)
    return rows

def number(value):
    if value in (None,''):return 0
    n=float(value)
    if not math.isfinite(n) or n<0:raise ValueError('Invalid playtime value')
    return n

def export(workbook,output=ROOT/'data.js'):
    accounts=[]
    with zipfile.ZipFile(workbook) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(n.itertext()) for n in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
        rels={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        for sheet in ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',NS):
            group=sheet.get('name')
            if group not in ('Known accounts','Uncertain accounts'):continue
            rid=sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            target=rels[rid]
            path=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            rows=read_rows(z,path,strings)
            header_index=next((i for i,r in enumerate(rows) if 'Riot ID' in r.values()),None)
            if header_index is None:raise ValueError('Missing Riot ID header in '+group)
            columns={FIELDS[v]:c for c,v in rows[header_index].items() if v in FIELDS}
            required={'id','rank','peak','comp','unrated','dm','status','rankVerified','peakVerified','compVerified','unratedVerified','dmVerified'}
            if not required.issubset(columns):raise ValueError('Required headers missing in '+group)
            for row in rows[header_index+1:]:
                if not row.get(columns['id']):continue
                a={key:row.get(col) for key,col in columns.items()}
                a['id']=str(a['id']).strip()
                for key in ('comp','unrated','dm'):a[key]=number(a[key])
                # Recompute from input cells instead of trusting stale Excel formula caches.
                a['total']=round(a['comp']+a['unrated']+a['dm'],6)
                for key in ('rankVerified','peakVerified','compVerified','unratedVerified','dmVerified'):a[key]='Yes' if a.get(key)=='Yes' else 'No'
                a['status']=a['status'] if a.get('status') in STATUSES else 'Needs checking'
                a['group']=group
                checked=a.get('checked')
                try:a['checked']=(dt.datetime(1899,12,30)+dt.timedelta(days=float(checked))).date().isoformat() if checked else None
                except (ValueError,TypeError):a['checked']=str(checked)[:10] if checked else None
                # Never export raw notes, hyperlinks, login names, passwords or login-only rows.
                missing=[label for label,flag in [('Current rank','rankVerified'),('Peak rank','peakVerified'),('Competitive hours','compVerified'),('Unrated hours','unratedVerified'),('Deathmatch hours','dmVerified')] if a[flag]!='Yes']
                a['notes']='Unverified: '+', '.join(missing) if missing else 'All five stats verified'
                accounts.append(a)
    if not accounts:raise ValueError('Workbook has no named accounts; keeping last good export')
    if len({a['id'].casefold() for a in accounts})!=len(accounts):raise ValueError('Duplicate in-game tags; keeping last good export')
    data={'accounts':accounts,'generatedAt':dt.datetime.now(dt.timezone.utc).isoformat()}
    if output.exists():
        try:
            previous=json.loads(output.read_text(encoding='utf-8').removeprefix('window.VALORANT_DATA = ').strip().removesuffix(';'))
            if previous.get('accounts')==accounts:return previous
        except (ValueError,TypeError):pass
    payload='window.VALORANT_DATA = '+json.dumps(data,ensure_ascii=True,allow_nan=False)+';\n'
    tmp=output.with_suffix('.tmp')
    tmp.write_text(payload,encoding='utf-8');os.replace(tmp,output)
    return data

def signature(path):
    stat=path.stat();return (stat.st_mtime_ns,stat.st_size)

def git(*args,root=ROOT):
    env=os.environ.copy();env['GIT_TERMINAL_PROMPT']='0';env['GCM_INTERACTIVE']='never'
    result=subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,timeout=45,env=env)
    if result.returncode:raise RuntimeError('Git sync failed during '+args[0]+'. '+result.stderr.strip())
    return result.stdout.strip()

def publish_data(root=ROOT):
    if git('branch','--show-current',root=root)!='main':raise RuntimeError('Automatic sync requires the main branch.')
    remote=git('remote','get-url','origin',root=root)
    if not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/valorant-dashboard(?:\.git)?',remote):
        raise RuntimeError('Origin must be the GitHub valorant-dashboard repository.')
    staged=git('diff','--cached','--name-only',root=root).splitlines()
    if any(p!='data.js' for p in staged):raise RuntimeError('Other files are staged. Commit or unstage them before automatic sync.')
    # Check unpushed commits before pushing: the watcher must never publish source edits.
    git('fetch','origin','main',root=root)
    ahead=git('log','--format=','--name-only','origin/main..HEAD',root=root).splitlines()
    if any(p and p!='data.js' for p in ahead):raise RuntimeError('Unpushed source edits require a manual push first.')
    git('add','--','data.js',root=root)
    if git('diff','--cached','--name-only',root=root):
        git('-c','user.name=Valorant Dashboard Sync','-c','user.email=dashboard-sync@users.noreply.github.com','commit','-m','Update dashboard data from Excel','--','data.js',root=root)
    # Explicit main target, ordinary push only. Diverged history is left for manual review.
    if git('rev-list','--count','origin/main..HEAD',root=root)!='0':
        git('push','origin','HEAD:main',root=root)
        print('Public dashboard data pushed to GitHub.',flush=True)

def watch(path,push=False):
    previous=signature(path)
    pending=push
    next_try=0
    while True:
        time.sleep(2)
        try:
            current=signature(path)
            if current!=previous:
                export(path);previous=current;pending=push;next_try=0;print('Dashboard data updated.',flush=True)
            if pending and time.monotonic()>=next_try:
                try:publish_data();pending=False
                except Exception as e:
                    print(str(e)+' Retrying in 60 seconds.',flush=True);next_try=time.monotonic()+60
        except Exception as e:print('Waiting for a readable saved workbook: '+str(e),flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workbook',type=Path,default=Path.home()/'Documents'/'Valorant Info Sheet.xlsx')
    parser.add_argument('--watch',action='store_true')
    parser.add_argument('--serve',action='store_true')
    parser.add_argument('--push',action='store_true',help='Commit and push only generated data.js to origin/main')
    args=parser.parse_args()
    data=export(args.workbook)
    print('Exported '+str(len(data['accounts']))+' in-game tags and stats. No login credentials or raw notes exported.')
    if args.push and not args.watch:publish_data()
    if args.serve:
        class Handler(SimpleHTTPRequestHandler):
            def end_headers(self):
                self.send_header('Cache-Control','no-store');super().end_headers()
            def do_GET(self):
                # Serve only public dashboard assets, never the workbook or project scripts.
                if self.path.split('?')[0] not in ('/','/index.html','/app.js','/data.js'):
                    self.send_error(404);return
                super().do_GET()
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)))
        if args.watch:threading.Thread(target=watch,args=(args.workbook,args.push),daemon=True).start()
        url='http://127.0.0.1:'+str(server.server_port)
        print('Local dashboard: '+url+' — keep this window open for automatic updates.')
        webbrowser.open(url)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
        finally:server.server_close()
    elif args.watch:watch(args.workbook,args.push)

if __name__=='__main__':main()
