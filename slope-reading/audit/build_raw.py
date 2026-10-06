import sqlite3,json,glob,os,hashlib,collections
from pathlib import Path
BASE=Path('/Users/owenwassmer/dev/agent-journey-visual/slope-reading/audit'); OUT=BASE/'raw-source';OUT.mkdir(exist_ok=True)
H=['20260925_194036_0dd3e1','20260926_234625_5c0cc6','20260928_172908_0aef31','20260929_020301_63c14b','20260929_175426_2e120e','20260930_144102_6fa0b2','20261004_150251_ebc057']
manifest=[];counts=collections.Counter();dups=[]
def default(x):
 if isinstance(x,bytes):return {'encoding':'hex','data':x.hex()}
 raise TypeError(type(x))
def write(path,events):
 n=0;types=collections.Counter()
 with open(path,'w') as f:
  for e in events:f.write(json.dumps(e,ensure_ascii=False,default=default)+'\n');n+=1;types[e['event_type']]+=1
 return {'output':str(path),'events':n,'event_types':dict(types),'bytes':path.stat().st_size}
c=sqlite3.connect('file:/Users/owenwassmer/.hermes/profiles/connor/state.db?mode=ro',uri=True);c.row_factory=sqlite3.Row
c.execute('BEGIN')
for sid in H:
 rows=[dict(r) for r in c.execute('select * from messages where session_id=? order by id',(sid,))];session=dict(c.execute('select * from sessions where id=?',(sid,)).fetchone());seen={}
 ev=[{'actor':'hermes:'+sid,'event_type':'session_metadata','source':{'database':'/Users/owenwassmer/.hermes/profiles/connor/state.db','table':'sessions','id':sid},'sequence':0,'timestamp':session['started_at'],'raw':session}]
 for seq,r in enumerate(rows,1):
  ev.append({'actor':'hermes:'+sid,'event_type':'message:'+r['role'],'source':{'database':'/Users/owenwassmer/.hermes/profiles/connor/state.db','table':'messages','id':r['id']},'sequence':seq,'timestamp':r['timestamp'],'raw':r});counts['hermes_'+r['role']]+=1
  t=r['content'] or ''
  if r['role'] in ['user','assistant']:
   if r['role']=='user' and (t.startswith('[CONTEXT COMPACTION') or 'COMPACTION SUMMARY' in t[:300]):continue
   h=hashlib.md5(t.strip().encode()).hexdigest()
   if len(t.strip())>40 and h in seen:
    counts['export_dropped_repeated_'+r['role']]+=1
    if r['tool_calls']:counts['export_dropped_assistant_with_tool_calls']+=1;dups.append({'session':sid,'id':r['id'],'prior':seen[h]})
   seen[h]=r['id']
 item=write(OUT/('hermes-'+sid+'.jsonl'),ev);item['source']={'database':'/Users/owenwassmer/.hermes/profiles/connor/state.db','session':sid};manifest.append(item)
files=[]
for f in sorted(glob.glob('/Users/owenwassmer/.codex/sessions/**/*.jsonl',recursive=True)):
 with open(f) as h:first=h.readline()
 if '"cwd":"/Users/owenwassmer/dev/Slope_Sparse_Events' in first:files.append(('codex',f))
files += [('claudecode',f) for f in sorted(glob.glob('/Users/owenwassmer/.claude/projects/-Users-owenwassmer-dev-Slope-Sparse-Events/*.jsonl'))]
for platform,f in files:
 def events():
  for n,line in enumerate(open(f),1):
   try:d=json.loads(line)
   except Exception as e:d={'parse_error':str(e),'original_line':line}
   ty=d.get('type','unknown');actor=platform+':'+(d.get('sessionId') or Path(f).stem)
   p=d.get('payload',{})
   if platform=='codex' and ty=='response_item' and p.get('type')=='message':
    role=p.get('role');counts['codex_message_'+str(role)]+=1
    if role=='user' and ''.join(x.get('text','') for x in p.get('content',[])).startswith('<'):counts['codex_dropped_user_xml']+=1
   counts[platform+'_event_'+ty]+=1
   yield {'actor':actor,'event_type':ty,'source':{'file':f,'line':n},'sequence':n,'timestamp':d.get('timestamp'),'raw':d}
 item=write(OUT/(platform+'-'+Path(f).name),events());item['source']={'file':f,'sha256':hashlib.sha256(Path(f).read_bytes()).hexdigest()};manifest.append(item)
result={'schema':'Each record retains untouched raw event/DB row, original source locator, actor, source sequence, full-precision timestamp. No deduplication/filtering/semantic classification. Raw bytes encoded as hex where needed. Actor knowledge follows actor sequence, not global wall time.','files':manifest,'counts':dict(counts),'repeated_assistant_records_with_calls_dropped_by_previous_export':dups}
(BASE/'raw-source-manifest.json').write_text(json.dumps(result,indent=2));print(json.dumps({'files':len(manifest),'events':sum(x['events'] for x in manifest),'bytes':sum(x['bytes'] for x in manifest),'counts':dict(counts)},indent=2))
