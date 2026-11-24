"""NFL career + per-team stats. Sources: season files 1970-1998 (name-keyed), weekly files 1999-2026 (id-keyed)."""
import csv,sys,json,glob,re,os,collections
fdp,wk,players,draft,outdir=sys.argv[1:6]
def norm(n):
    n=re.sub(r'[*+]','',n).strip();k=re.sub(r"[.'’]",'',n.lower());k=re.sub(r'\s+(jr|sr|ii|iii|iv|v)$','',k)
    return n,re.sub(r'[^a-z]','',k)
OLD={'LVR':'LV','PHO':'ARI','RAM':'LAR','BOS':'NE','NWE':'NE','OAK':'LV','RAI':'LV','SDG':'LAC','GNB':'GB','KAN':'KC','NOR':'NO','SFO':'SF','TAM':'TB'}
def oldfr(t,s):
    if 'TM' in t: return None
    if t=='STL': return 'ARI' if s<=1987 else 'LAR'
    if t=='BAL': return 'IND' if s<=1983 else 'BAL'
    if t=='HOU': return 'TEN' if s<=1996 else 'HOU'
    return OLD.get(t,t)
NEW={'LA':'LAR','STL':'LAR','OAK':'LV','SD':'LAC'}
Z=lambda:[0,0,0]  # rush td, rec td, pass yds
f0=lambda x:int(float(x or 0))
old={};pfrteam=collections.defaultdict(list)
for f in sorted(glob.glob(fdp+'/*.csv')):
    s=int(os.path.basename(f)[:4])
    for r in csv.DictReader(open(f,encoding='utf-8')):
        name,k=norm(r['Player'])
        try: by=s-int(float(r['Age']))
        except: by=None
        if s>1998: pfrteam[(k,s)].append((by,r['Tm']));continue
        key=None
        for d in (0,-1,1):
            if by is not None and (k,by+d) in old: key=(k,by+d);break
        if key is None: key=(k,by)
        e=old.setdefault(key,{'n':name,'by':by,'pos':collections.Counter(),'tot':Z(),'tm':collections.defaultdict(lambda:{'y':set(),'v':Z()}),'last':s})
        e['pos'][r['Pos']]+=1;e['last']=max(e['last'],s)
        v=[f0(r['RushingTD']),f0(r['ReceivingTD']),f0(r['PassingYds'])]
        for i in range(3): e['tot'][i]+=v[i]
        fr=oldfr(r['Tm'],s)
        if fr:
            e['tm'][fr]['y'].add(s)
            for i in range(3): e['tm'][fr]['v'][i]+=v[i]
birth={r['gsis_id']:(int(r['birth_date'][:4]) if r['birth_date'][:4].isdigit() else None) for r in csv.DictReader(open(players,encoding='utf-8'))}
new={}
for f in sorted(glob.glob(wk+'/*.csv')):
    for r in csv.DictReader(open(f,encoding='utf-8')):
        if r['season_type']!='REG': continue
        e=new.setdefault(r['player_id'],{'n':r['player_display_name'],'pos':collections.Counter(),'rows':collections.defaultdict(list),'first':int(r['season'])})
        e['pos'][r['position']]+=1
        t=r['team'];e['rows'][int(r['season'])].append((NEW.get(t,t) if t else '',[f0(r['rushing_tds']),f0(r['receiving_tds']),f0(r['passing_yards'])]))
for pid,e in new.items():
    e['tot']=Z();e['tm']=collections.defaultdict(lambda:{'y':set(),'v':Z()});k=norm(e['n'])[1];by=birth.get(pid)
    for s,rows in e['rows'].items():
        c=collections.Counter(t for t,_ in rows if t)
        if not c: continue
        if s>=2022: valid=set(c)
        else:
            cand=[x for x in pfrteam.get((k,s),[]) if by is None or x[0] is None or abs(x[0]-by)<=1]
            if len(cand)==1 and 'TM' not in cand[0][1]: valid={oldfr(cand[0][1],s)}
            elif len(cand)==1: valid={t for t,_ in c.most_common(int(cand[0][1][0]))}
            else: valid={c.most_common(1)[0][0]}
        mode=max(valid,key=lambda t:c.get(t,0))
        for t,v in rows:
            tt=t if t in valid else mode
            e['tm'][tt]['y'].add(s)
            for i in range(3): e['tm'][tt]['v'][i]+=v[i];e['tot'][i]+=v[i]
def build(posset,oldpos,statfn,detailfn,dcol,fname):
    res=[];used=set()
    for pid,e in new.items():
        if e['pos'].most_common(1)[0][0] not in posset or not e['tm']: continue
        name,k=norm(e['n']);by=birth.get(pid);o=None
        if e['first']<=2003 and by:
            for d in (0,-1,1):
                c=old.get((k,by+d))
                if c and c['last']>=1994: o=(k,by+d);break
        rec={'n':name,'tot':list(e['tot']),'tm':{t:{'y':set(x['y']),'v':list(x['v'])} for t,x in e['tm'].items()},'by':by}
        if o:
            used.add(o);c=old[o];rec['by']=c['by']
            for i in range(3): rec['tot'][i]+=c['tot'][i]
            for t,x in c['tm'].items():
                y=rec['tm'].setdefault(t,{'y':set(),'v':Z()});y['y'].update(x['y'])
                for i in range(3): y['v'][i]+=x['v'][i]
        res.append(rec)
    for key,e in old.items():
        if key in used: continue
        p={x:c for x,c in e['pos'].items() if x not in('0','')}
        if not p or max(p,key=p.get)!=oldpos or not e['tm']: continue
        res.append({'n':e['n'],'tot':list(e['tot']),'tm':{t:{'y':set(x['y']),'v':list(x['v'])} for t,x in e['tm'].items()},'by':e['by']})
    keep=[r for r in res if not (r['by'] is not None and r['by']<=1947)]
    # patch undercounted older careers from drafted players' career totals
    dr=collections.defaultdict(list)
    for r in csv.DictReader(open(draft,encoding='utf-8')):
        if r['position'] in posset: dr[norm(r['pfr_player_name'])[1]].append(r)
    byk=collections.defaultdict(list)
    for r in keep: byk[norm(r['n'])[1]].append(r)
    patched=0
    for k2,rows in dr.items():
        if len(rows)!=1 or int(rows[0]['season'])>=1999: continue
        s=int(rows[0]['season']);c=[p for p in byk.get(k2,[]) if abs(min(min(x['y']) for x in p['tm'].values())-s)<=2]
        if len(c)!=1: continue
        try: dv=dcol(rows[0])
        except: continue
        if statfn(dv)>statfn(c[0]['tot']): c[0]['tot']=dv;patched+=1
    keep.sort(key=lambda r:-statfn(r['tot']))
    P=[[r['n'],statfn(r['tot']),detailfn(r['tot']),[[t,min(x['y']),max(x['y']),statfn(x['v'])] for t,x in sorted(r['tm'].items(),key=lambda z:min(z[1]['y']))]] for r in keep]
    os.makedirs(os.path.dirname(fname),exist_ok=True)
    json.dump(P,open(fname,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    print(os.path.basename(os.path.dirname(fname)),len(P),'players, patched',patched,os.path.getsize(fname),'bytes | top:',[(p[0],p[1]) for p in P[:8]])
td=lambda v:v[0]+v[1]
build({'RB','FB','HB'},'RB',td,lambda v:'%d rushing, %d receiving'%(v[0],v[1]),lambda r:[f0(r['rush_tds']),f0(r['rec_tds']),0],outdir+'/touchdown-chase/data.json')
build({'RB','FB','HB'},'RB',td,lambda v:'%d rushing, %d receiving'%(v[0],v[1]),lambda r:[f0(r['rush_tds']),f0(r['rec_tds']),0],outdir+'/homegrown/data.json')
build({'QB'},'QB',lambda v:v[2],lambda v:'',lambda r:[0,0,f0(r['pass_yards'])],outdir+'/air-yards/data.json')
