"""NFL career + per-team stats. Through 1998: Pro-Football-Reference game logs (regular season). 1999 on: nflverse weekly files."""
import csv,sys,json,glob,re,os,collections
reg,profiles,fdp,wk,players,outdir=sys.argv[1:7]
def norm(n):
    n=re.sub(r'[*+]','',n).strip();k=re.sub(r"[.'’]",'',n.lower());k=re.sub(r'\s+(jr|sr|ii|iii|iv|v)$','',k)
    return n,re.sub(r'[^a-z]','',k)
OLD={'LVR':'LV','PHO':'ARI','CRD':'ARI','RAM':'LAR','BOS':'NE','NWE':'NE','OAK':'LV','RAI':'LV','SDG':'LAC','GNB':'GB','KAN':'KC','NOR':'NO','SFO':'SF','TAM':'TB','NYT':'NYJ','NYY':None,'BCL':None}
CUR={'ARI','ATL','BAL','BUF','CAR','CHI','CIN','CLE','DAL','DEN','DET','GB','HOU','IND','JAX','KC','LAC','LAR','LV','MIA','MIN','NE','NO','NYG','NYJ','PHI','PIT','SEA','SF','TB','TEN','WAS'}
def oldfr(t,s):
    if 'TM' in t: return None
    if t=='STL': return 'ARI' if s<=1987 else 'LAR'
    if t=='BAL': return 'IND' if s<=1983 else 'BAL'
    if t=='HOU': return 'TEN' if s<=1996 else 'HOU'
    if t=='DTX': return 'KC' if s>=1960 else None
    f=OLD.get(t,t);return f if f in CUR else None
NEW={'LA':'LAR','STL':'LAR','OAK':'LV','SD':'LAC'}
Z=lambda:[0,0,0];f0=lambda x:int(float(x or 0))
# ---- through 1998 from game logs
prof={p['player_id']:p for p in json.load(open(profiles,encoding='utf-8'))}
old={}
for r in csv.DictReader(open(reg)):
    pid=int(r['pid']);s=int(r['year']);p=prof.get(pid)
    if not p: continue
    e=old.setdefault(pid,{'n':p['name'].strip(),'pos':(p['position'] or '').split('-')[0],'bd':p['birth_date'] or '','dy':p['draft_year'],'tot':Z(),'tm':collections.defaultdict(lambda:{'y':set(),'v':Z()}),'first':s,'last':s})
    v=[int(r['rtd']),int(r['ctd']),int(r['pyds'])];e['first']=min(e['first'],s);e['last']=max(e['last'],s)
    for i in range(3): e['tot'][i]+=v[i]
    fr=oldfr(r['team'],s)
    if fr:
        e['tm'][fr]['y'].add(s)
        for i in range(3): e['tm'][fr]['v'][i]+=v[i]
def pre1950(e):  # logs start in 1950; anyone already in the league then would get a short career total
    if e['first']>1950: return False
    dy=e['dy'];by=int(e['bd'][:4]) if e['bd'][:4].isdigit() else None
    return (dy and str(dy).isdigit() and int(dy)<1950) or (by is not None and by<=1926)
# ---- season-file team labels, used only to clean up noisy weekly team codes for 1999-2021
pfrteam=collections.defaultdict(list)
for f in sorted(glob.glob(fdp+'/*.csv')):
    s=int(os.path.basename(f)[:4])
    if s<1999: continue
    for r in csv.DictReader(open(f,encoding='utf-8')):
        try: by=s-int(float(r['Age']))
        except: by=None
        pfrteam[(norm(r['Player'])[1],s)].append((by,r['Tm']))
# ---- 1999 on
binfo={r['gsis_id']:r['birth_date'] for r in csv.DictReader(open(players,encoding='utf-8'))}
new={}
for f in sorted(glob.glob(wk+'/*.csv')):
    for r in csv.DictReader(open(f,encoding='utf-8')):
        if r['season_type']!='REG': continue
        e=new.setdefault(r['player_id'],{'n':r['player_display_name'],'pos':collections.Counter(),'rows':collections.defaultdict(list)})
        e['pos'][r['position']]+=1;t=r['team']
        e['rows'][int(r['season'])].append((NEW.get(t,t) if t else '',[f0(r['rushing_tds']),f0(r['receiving_tds']),f0(r['passing_yards'])]))
for pid,e in new.items():
    e['tot']=Z();e['tm']=collections.defaultdict(lambda:{'y':set(),'v':Z()});k=norm(e['n'])[1];bd=binfo.get(pid,'');by=int(bd[:4]) if bd[:4].isdigit() else None
    for s,rows in e['rows'].items():
        c=collections.Counter(t for t,_ in rows if t)
        if not c: continue
        if s>=2022: valid=set(c)
        else:
            cand=[x for x in pfrteam.get((k,s),[]) if by is None or x[0] is None or abs(x[0]-by)<=1]
            if len(cand)==1 and 'TM' not in cand[0][1] and oldfr(cand[0][1],s): valid={oldfr(cand[0][1],s)}
            elif len(cand)==1 and 'TM' in cand[0][1]: valid={t for t,_ in c.most_common(int(cand[0][1][0]))}
            else: valid={c.most_common(1)[0][0]}
        mode=max(valid,key=lambda t:c.get(t,0))
        for t,v in rows:
            tt=t if t in valid else mode
            e['tm'][tt]['y'].add(s)
            for i in range(3): e['tm'][tt]['v'][i]+=v[i];e['tot'][i]+=v[i]
# index older players by name + birth date for joining careers that cross 1998/1999
byname=collections.defaultdict(list)
for pid,e in old.items(): byname[norm(e['n'])[1]].append(pid)
def build(newpos,oldpos,statfn,detailfn,fname,minB=None):
    res=[];used=set();dropped=0
    for pid,e in new.items():
        if e['pos'].most_common(1)[0][0] not in newpos or not e['tm']: continue
        name,k=norm(e['n']);bd=binfo.get(pid,'');o=None
        c=[q for q in byname.get(k,[]) if old[q]['last']>=1990 and ((bd and old[q]['bd']==bd) or (not bd or not old[q]['bd']))]
        if len(c)==1: o=c[0]
        rec={'n':name,'tot':list(e['tot']),'tm':{t:{'y':set(x['y']),'v':list(x['v'])} for t,x in e['tm'].items()}}
        if o is not None:
            used.add(o);q=old[o]
            for i in range(3): rec['tot'][i]+=q['tot'][i]
            for t,x in q['tm'].items():
                y=rec['tm'].setdefault(t,{'y':set(),'v':Z()});y['y'].update(x['y'])
                for i in range(3): y['v'][i]+=x['v'][i]
        res.append(rec)
    for pid,e in old.items():
        if pid in used or not e['tm']: continue
        if not (e['pos'] in oldpos or (minB and e['pos']=='B' and statfn(e['tot'])>=minB)): continue
        if pre1950(e): dropped+=1;continue
        res.append({'n':e['n'],'tot':list(e['tot']),'tm':{t:{'y':set(x['y']),'v':list(x['v'])} for t,x in e['tm'].items()}})
    res.sort(key=lambda r:-statfn(r['tot']))
    P=[[r['n'],statfn(r['tot']),detailfn(r['tot']),[[t,min(x['y']),max(x['y']),statfn(x['v'])] for t,x in sorted(r['tm'].items(),key=lambda z:min(z[1]['y']))]] for r in res]
    os.makedirs(os.path.dirname(fname),exist_ok=True)
    json.dump(P,open(fname,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    first=min(t[1] for p in P for t in p[3])
    print(os.path.basename(os.path.dirname(fname)),len(P),'players | earliest season',first,'| left out (played before 1950)',dropped,'|',os.path.getsize(fname)//1024,'KB | top:',[(p[0],p[1]) for p in P[:10]])
    return P
td=lambda v:v[0]+v[1];det=lambda v:'%d rushing, %d receiving'%(v[0],v[1])
RB={'RB','FB','HB','TB'}
A=build({'RB','FB','HB'},RB,td,det,outdir+'/touchdown-chase/data.json',minB=10)
build({'RB','FB','HB'},RB,td,det,outdir+'/homegrown/data.json',minB=10)
Q=build({'QB'},{'QB'},lambda v:v[2],lambda v:'',outdir+'/air-yards/data.json')
for p in A:
    if p[0] in('Jim Brown','Emmitt Smith','Marcus Allen','Jerome Bettis','Curtis Martin','O.J. Simpson','Brian Mitchell','Eric Dickerson','Adrian Peterson'): print(' ',p[0],p[1],p[2],[(t[0],t[1],t[2],t[3]) for t in p[3]])
for p in Q:
    if p[0] in('Dan Marino','Brett Favre','Johnny Unitas','Warren Moon','Vinny Testaverde'): print(' ',p[0],p[1],[(t[0],t[1],t[2],t[3]) for t in p[3]])
names=collections.Counter(p[0] for p in A);print('same-name backs:',sum(1 for n,c in names.items() if c>1))
