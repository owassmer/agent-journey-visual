import json, sqlite3, glob, os, datetime, hashlib
BASE='/private/tmp/claude-501/-Users-owenwassmer-dev/bf301fa1-291c-40be-90bb-6888626158ec/scratchpad/slope'
SRC=BASE+'/src2'; FULL=SRC+'/full'
os.makedirs(FULL,exist_ok=True)
PREV_RES=900; PREV_CALL=300
events=[]; seq=[0]
def iso(ts):
    if isinstance(ts,(int,float)): return datetime.datetime.fromtimestamp(ts,datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    return (ts or '')[:19]+'Z'
def add(ts,src,line): events.append((iso(ts),src,line))
def stored(kind,text,prev):
    """Return inline preview; store full text if longer than preview."""
    text=text or ''
    seq[0]+=1; rid=f'{kind}{seq[0]:06d}'
    if len(text)<=prev: return f'[{rid}] {text}'
    open(f'{FULL}/{rid}.txt','w').write(text)
    return f'[{rid} · {len(text)} chars · full: src2/full/{rid}.txt] {text[:prev]} …'

c=sqlite3.connect('file:/Users/owenwassmer/.hermes/profiles/connor/state.db?mode=ro',uri=True)
H=['20260925_194036_0dd3e1','20260926_234625_5c0cc6','20260928_172908_0aef31','20260929_020301_63c14b','20260929_175426_2e120e','20260930_144102_6fa0b2','20261004_150251_ebc057']
for sid in H:
    seen=set(); src='hermes:'+sid
    for (i,role,content,tc,tname,ts,dk) in c.execute("select id,role,content,tool_calls,tool_name,timestamp,display_kind from messages where session_id=? order by id",(sid,)):
        t=content or ''
        if role=='user':
            if t.startswith('[CONTEXT COMPACTION') or 'COMPACTION SUMMARY' in t[:300]:
                add(ts,src,f'[{i}] ~~ compaction summary inserted ({len(t)} chars) — the agent continued from this summary: '+stored('S',t,600)+' ~~'); continue
            h=hashlib.md5(t.strip().encode()).hexdigest()
            if len(t.strip())>40 and h in seen: add(ts,src,f'[{i}] ~~ replayed user text omitted ~~'); continue
            seen.add(h)
            kind='USER' if dk in (None,'steer') else f'SYSTEM-TO-AGENT({dk})'
            if kind=='USER' and t.startswith(('[ASYNC','[Background','[System','<system')): kind='SYSTEM-TO-AGENT'
            add(ts,src,f'[{i}] {kind}: '+(t if kind=='USER' else stored('M',t,1500)))
        elif role=='assistant':
            h=hashlib.md5(t.strip().encode()).hexdigest()
            if len(t.strip())>40 and h in seen: add(ts,src,f'[{i}] ~~ replayed assistant text omitted ~~'); continue
            seen.add(h)
            if t.strip(): add(ts,src,f'[{i}] AGENT: {t}')
            if tc:
                try:
                    for call in json.loads(tc):
                        fn=call.get('function',call); add(ts,src,f'[{i}]   → CALL {fn.get("name")}: '+stored('C',str(fn.get("arguments")),PREV_CALL))
                except Exception: add(ts,src,f'[{i}]   → CALL: '+stored('C',tc,PREV_CALL))
        elif role=='tool':
            add(ts,src,f'[{i}]   ← RESULT {tname}: '+stored('R',t,PREV_RES))

for f in sorted(glob.glob('/Users/owenwassmer/.codex/sessions/**/*.jsonl',recursive=True)):
    if '"cwd":"/Users/owenwassmer/dev/Slope_Sparse_Events' not in open(f).readline(): continue
    sid=os.path.basename(f)[19:].replace('.jsonl',''); src='codex:'+sid[:60]
    for l in open(f):
        d=json.loads(l); p=d.get('payload',{}); ts=d.get('timestamp')
        if d.get('type')!='response_item': continue
        ty=p.get('type')
        if ty=='message' and p.get('role') in ('user','assistant'):
            txt=''.join(x.get('text','') for x in p.get('content',[]))
            if p['role']=='user':
                if txt.startswith('<'): continue
                add(ts,src,f'USER: {txt}')
            else: add(ts,src,f'AGENT: {txt}')
        elif ty in ('custom_tool_call','function_call'):
            add(ts,src,f'  → CALL {p.get("name")}: '+stored('C',str(p.get("input") or p.get("arguments")),PREV_CALL))
        elif ty in ('custom_tool_call_output','function_call_output'):
            o=p.get('output',''); o=o if isinstance(o,str) else json.dumps(o)
            add(ts,src,'  ← RESULT: '+stored('R',o,PREV_RES))

for f in sorted(glob.glob('/Users/owenwassmer/.claude/projects/-Users-owenwassmer-dev-Slope-Sparse-Events/*.jsonl')):
    src='claudecode:'+os.path.basename(f)[:8]
    for l in open(f):
        try: d=json.loads(l)
        except: continue
        ts=d.get('timestamp'); m=d.get('message',{})
        if d.get('isSidechain'): continue
        if d.get('type')=='user':
            cont=m.get('content')
            if isinstance(cont,str):
                if d.get('isMeta') or cont.startswith('<'): continue
                add(ts,src,f'USER: {cont}')
            elif isinstance(cont,list):
                for x in cont:
                    if x.get('type')=='tool_result':
                        r=x.get('content'); r=r if isinstance(r,str) else json.dumps(r)
                        add(ts,src,'  ← RESULT: '+stored('R',r,PREV_RES))
                    elif x.get('type')=='text' and not x.get('text','').startswith('<'):
                        add(ts,src,f'USER: {x["text"]}')
        elif d.get('type')=='assistant':
            for x in m.get('content',[]) or []:
                if x.get('type')=='text' and x.get('text','').strip(): add(ts,src,f'AGENT: {x["text"]}')
                elif x.get('type')=='tool_use': add(ts,src,f'  → CALL {x.get("name")}: '+stored('C',json.dumps(x.get("input")),PREV_CALL))

events.sort(key=lambda e:e[0])
out=[]
for ts,src,line in events:
    first=True
    for part in line.split('\n'):
        part=(f'{ts} <{src}> ' if first else '    ')+part; first=False
        while len(part)>1500:
            cut=part.rfind(' ',0,1500); cut=cut if cut>1000 else 1500
            out.append(part[:cut]); part='    '+part[cut:].lstrip()
        out.append(part)
open(SRC+'/all.txt','w').write('\n'.join(out)+'\n')
print('events',len(events),'lines',len(out),'MB',round(sum(map(len,out))/1e6,1),'stored files',len(os.listdir(FULL)))
