import csv,sys,json,glob,re,os,collections,random
fdp,wk,players,out,draft=sys.argv[1:6]
def norm(n):
    n=re.sub(r'[*+]','',n).strip()
    k=re.sub(r"[.'’]",'',n.lower())
    k=re.sub(r'\s+(jr|sr|ii|iii|iv|v)$','',k)
    return n,re.sub(r'[^a-z]','',k)
OLD={'LVR':'LV','PHO':'ARI','RAM':'LAR','BOS':'NE','NWE':'NE','TEN':'TEN','OAK':'LV','RAI':'LV','SDG':'LAC','GNB':'GB','KAN':'KC','NOR':'NO','SFO':'SF','TAM':'TB'}
def oldfr(t,s):
    if 'TM' in t: return None
    if t=='STL': return 'ARI' if s<=1987 else 'LAR'
    if t=='BAL': return 'IND' if s<=1983 else 'BAL'
    if t=='HOU': return 'TEN' if s<=1996 else 'HOU'
    return OLD.get(t,t)
NEW={'LA':'LAR','STL':'LAR','OAK':'LV','SD':'LAC'}
# ---- 1970-1998 from season files (no ids: key on name + birth year)
old={}
pfrteam=collections.defaultdict(list)
for f in sorted(glob.glob(fdp+'/*.csv')):
    s=int(os.path.basename(f)[:4])
    for r in csv.DictReader(open(f,encoding='utf-8')):
        name,k=norm(r['Player'])
        try: by=s-int(float(r['Age']))
        except: by=None
        if s>1998:
            pfrteam[(k,s)].append((by,r['Tm']));continue
        key=None
        for d in (0,-1,1):
            if by is not None and (k,by+d) in old: key=(k,by+d);break
        if key is None: key=(k,by)
        e=old.setdefault(key,{'n':name,'by':by,'pos':collections.Counter(),'ru':0,'re':0,'tm':collections.defaultdict(set),'last':s,'first':s,'unk':0})
        e['pos'][r['Pos']]+=1;e['ru']+=int(float(r['RushingTD'] or 0));e['re']+=int(float(r['ReceivingTD'] or 0));e['last']=max(e['last'],s)
        fr=oldfr(r['Tm'],s)
        if fr: e['tm'][fr].add(s)
        else: e['unk']+=1
# ---- 1999-2025 from weekly files
birth={r['gsis_id']:(int(r['birth_date'][:4]) if r['birth_date'][:4].isdigit() else None) for r in csv.DictReader(open(players,encoding='utf-8'))}
new={}
for f in sorted(glob.glob(wk+'/*.csv')):
    for r in csv.DictReader(open(f,encoding='utf-8')):
        if r['season_type']!='REG': continue
        e=new.setdefault(r['player_id'],{'n':r['player_display_name'],'pos':collections.Counter(),'ru':0,'re':0,'wk':collections.defaultdict(collections.Counter),'first':int(r['season'])})
        e['pos'][r['position']]+=1
        e['ru']+=int(float(r['rushing_tds'] or 0));e['re']+=int(float(r['receiving_tds'] or 0))
        t=r['team']
        if t: e['wk'][int(r['season'])][NEW.get(t,t)]+=1
# weekly team codes are noisy before 2022: trust the season file's team, use weekly counts only to resolve multi-team seasons
for pid,e in new.items():
    e['tm']=collections.defaultdict(set);k=norm(e['n'])[1];by=birth.get(pid)
    for s,c in e['wk'].items():
        if s>=2022:
            for t in c: e['tm'][t].add(s)
            continue
        cand=[x for x in pfrteam.get((k,s),[]) if by is None or x[0] is None or abs(x[0]-by)<=1]
        if len(cand)==1 and 'TM' not in cand[0][1]: e['tm'][oldfr(cand[0][1],s)].add(s)
        elif len(cand)==1:
            n=int(cand[0][1][0])
            for t,_ in c.most_common(n): e['tm'][t].add(s)
        else: e['tm'][c.most_common(1)[0][0]].add(s)
# ---- merge
res=[];used=set();dropped=0
for pid,e in new.items():
    if e['pos'].most_common(1)[0][0] not in('RB','FB','HB'): continue
    name,k=norm(e['n']);by=birth.get(pid)
    o=None
    if e['first']<=2003 and by:
        for d in (0,-1,1):
            c=old.get((k,by+d))
            if c and c['last']>=1994: o=(k,by+d);break
    rec={'n':name,'ru':e['ru'],'re':e['re'],'tm':{t:set(v) for t,v in e['tm'].items()},'by':by}
    if o:
        used.add(o);c=old[o];rec['ru']+=c['ru'];rec['re']+=c['re'];rec['by']=c['by']
        for t,v in c['tm'].items(): rec['tm'].setdefault(t,set()).update(v)
    res.append(rec)
for key,e in old.items():
    if key in used: continue
    p=[x for x in e['pos'] if x not in('0','')]
    if not p or collections.Counter({x:e['pos'][x] for x in p}).most_common(1)[0][0]!='RB': continue
    if e['last']>=1998 and e['by'] and e['by']>=1970: pass
    res.append({'n':e['n'],'ru':e['ru'],'re':e['re'],'tm':dict(e['tm']),'by':e['by']})
keep=[]
for r in res:
    if r['by'] is not None and r['by']<=1947: dropped+=1;continue
    if not r['tm']: continue
    keep.append(r)
# ---- patch older careers from career totals of drafted players (season files miss some part-time seasons)
dr=collections.defaultdict(list)
for r in csv.DictReader(open(draft,encoding='utf-8')):
    if r['position'] in('RB','FB','HB'): dr[norm(r['pfr_player_name'])[1]].append(r)
byk=collections.defaultdict(list)
for r in keep: byk[norm(r['n'])[1]].append(r)
patched=0
for k2,rows in dr.items():
    if len(rows)!=1: continue
    r=rows[0];s=int(r['season'])
    if s>=1999: continue
    c=[p for p in byk.get(k2,[]) if abs(min(min(v) for v in p['tm'].values())-s)<=2]
    if len(c)!=1: continue
    try: ru=int(float(r['rush_tds'] or 0));re_=int(float(r['rec_tds'] or 0))
    except: continue
    p=c[0]
    if ru+re_>p['ru']+p['re']: p['ru']=ru;p['re']=re_;patched+=1
print('patched from career totals',patched)
def spans(ys):
    ys=sorted(ys);o=[];a=b=ys[0]
    for y in ys[1:]:
        if y==b+1: b=y
        else: o.append([a,b]);a=b=y
    o.append([a,b]);return o
keep.sort(key=lambda r:-(r['ru']+r['re']))
P=[[r['n'],r['ru'],r['re'],[[t,min(v),max(v)] for t,v in sorted(r['tm'].items(),key=lambda x:min(x[1]))]] for r in keep]
json.dump(P,open(out,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(len(P),'RBs; dropped pre-1970 era',dropped,'; bytes',os.path.getsize(out))
for p in P[:25]: print(p[0],p[1]+p[2],p[1],p[2],' '.join(t[0] for t in p[3]))
names=collections.Counter(p[0] for p in P);print('dupe names',[n for n,c in names.items() if c>1][:30])
per=collections.Counter(t[0] for p in P for t in p[3]);print(len(per),sorted(per.items(),key=lambda x:x[1]))

for p in P:
    if p[0] in('Fred Taylor','Adrian Peterson','Frank Gore','Marshawn Lynch','Eric Dickerson','Ricky Williams','LeSean McCoy'): print(p)
