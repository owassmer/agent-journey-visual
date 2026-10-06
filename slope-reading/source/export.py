import json, sqlite3, glob, os, datetime, hashlib
OUT='/private/tmp/claude-501/-Users-owenwassmer-dev/bf301fa1-291c-40be-90bb-6888626158ec/scratchpad/slope/src'
T=140
def iso(ts):
    if isinstance(ts,(int,float)): return datetime.datetime.fromtimestamp(ts,datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    return (ts or '')[:19]+'Z'
def cut(s,n=T):
    s=(s or '').replace('\n',' ⏎ ')
    return s if len(s)<=n else s[:n]+f' …[+{len(s)-n} chars]'
events=[]  # (ts, source, line)
def add(ts,src,line): events.append((iso(ts),src,line))

# Hermes connor sessions
c=sqlite3.connect('file:/Users/owenwassmer/.hermes/profiles/connor/state.db?mode=ro',uri=True)
H=['20260925_194036_0dd3e1','20260926_234625_5c0cc6','20260928_172908_0aef31','20260929_020301_63c14b','20260929_175426_2e120e','20260930_144102_6fa0b2','20261004_150251_ebc057']
for sid in H:
    seen=set(); src='hermes:'+sid
    for (i,role,content,tc,tname,ts,dk) in c.execute("select id,role,content,tool_calls,tool_name,timestamp,display_kind from messages where session_id=? order by id",(sid,)):
        t=content or ''
        if role=='user':
            if t.startswith('[CONTEXT COMPACTION') or 'COMPACTION SUMMARY' in t[:300]:
                add(ts,src,f'[{i}] ~~ compaction summary inserted ({len(t)} chars; omitted) ~~'); continue
            h=hashlib.md5(t.strip().encode()).hexdigest()
            if len(t.strip())>40 and h in seen: add(ts,src,f'[{i}] ~~ replayed user text omitted ~~'); continue
            seen.add(h)
            kind='USER' if dk in (None,'steer') else f'SYSTEM-TO-AGENT({dk})'
            if kind=='USER' and t.startswith(('[ASYNC','[Background','[System','<system')): kind='SYSTEM-TO-AGENT'
            lim=6000 if kind=='USER' else 1500
            add(ts,src,f'[{i}] {kind}: {cut(t,lim)}')
        elif role=='assistant':
            h=hashlib.md5(t.strip().encode()).hexdigest()
            if len(t.strip())>40 and h in seen: add(ts,src,f'[{i}] ~~ replayed assistant text omitted ~~'); continue
            seen.add(h)
            if t.strip(): add(ts,src,f'[{i}] AGENT: {cut(t,8000)}')
            if tc:
                try:
                    for call in json.loads(tc):
                        fn=call.get('function',call); add(ts,src,f'[{i}]   → {fn.get("name")}: {cut(str(fn.get("arguments")))}')
                except Exception: add(ts,src,f'[{i}]   → tool_calls: {cut(tc)}')
        elif role=='tool':
            add(ts,src,f'[{i}]   ← {tname}: {cut(t,100)}')

# Codex sessions in Slope cwd
for f in sorted(glob.glob('/Users/owenwassmer/.codex/sessions/**/*.jsonl',recursive=True)):
    head=open(f).readline()
    if '"cwd":"/Users/owenwassmer/dev/Slope_Sparse_Events' not in head: continue
    sid=os.path.basename(f)[19:].replace('.jsonl',''); src='codex:'+sid[:60]
    for l in open(f):
        d=json.loads(l); p=d.get('payload',{}); ts=d.get('timestamp')
        if d.get('type')!='response_item': continue
        ty=p.get('type')
        if ty=='message' and p.get('role') in ('user','assistant'):
            txt=''.join(x.get('text','') for x in p.get('content',[]))
            if p['role']=='user':
                if txt.startswith('<'): continue
                add(ts,src,f'USER: {cut(txt,6000)}')
            else: add(ts,src,f'AGENT: {cut(txt,8000)}')
        elif ty in ('custom_tool_call','function_call'):
            add(ts,src,f'  → {p.get("name")}: {cut(str(p.get("input") or p.get("arguments")))}')
        elif ty in ('custom_tool_call_output','function_call_output'):
            o=p.get('output',''); o=o if isinstance(o,str) else json.dumps(o)
            add(ts,src,f'  ← {cut(o,100)}')

# Claude Code sessions in Slope cwd
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
                add(ts,src,f'USER: {cut(cont,6000)}')
            elif isinstance(cont,list):
                for x in cont:
                    if x.get('type')=='tool_result':
                        r=x.get('content'); r=r if isinstance(r,str) else json.dumps(r)
                        add(ts,src,f'  ← {cut(r,100)}')
                    elif x.get('type')=='text' and not x.get('text','').startswith('<'):
                        add(ts,src,f'USER: {cut(x["text"],6000)}')
        elif d.get('type')=='assistant':
            for x in m.get('content',[]) or []:
                if x.get('type')=='text' and x.get('text','').strip(): add(ts,src,f'AGENT: {cut(x["text"],8000)}')
                elif x.get('type')=='tool_use': add(ts,src,f'  → {x.get("name")}: {cut(json.dumps(x.get("input")))}')

events.sort(key=lambda e:e[0])
with open(os.path.join(OUT,'all.txt'),'w') as fh:
    for ts,src,line in events: fh.write(f'{ts} <{src}> {line}\n')
print(len(events))
