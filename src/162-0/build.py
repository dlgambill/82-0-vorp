import csv,sys,json,collections,os,random,statistics as st
war,teams,out=sys.argv[1:4]
nm=collections.defaultdict(collections.Counter);cur=set()
for r in csv.DictReader(open(teams,encoding='utf-8')):
    y=int(r['yearID']);nm[(r['franchID'],y//10*10)][r['name']]+=1
    if y==2025: cur.add(r['franchID'])
f=lambda x:float(x) if x not in('','NA') else 0.0
HP=['C','1B','2B','3B','SS','LF','CF','RF']
best={}
for r in csv.DictReader(open(war,encoding='utf-8')):
    fr=r['franch_ID']
    if fr not in cur or r['lg_ID'] not in('AL','NL'): continue
    y=int(r['year_ID']);dec=y//10*10;sc=f(r['sched'])/162 or 1
    pid=r['key_bbref']
    # hitter line
    if f(r['pa'])>=300*sc:
        pos={p for p in HP if f(r['gms_'+p])>=20*sc}
        of=f(r['gms_OF'])
        if of>=20*sc and not pos&{'LF','CF','RF'}: pos|={'LF','CF','RF'}
        if not pos and f(r['gms_DH'])>=20*sc: pos={'DH'}
        if pos:
            k=(fr,dec,pid,'H');e=best.setdefault(k,{'n':r['player_name'],'pos':set(),'v':-99,'s':y})
            e['pos']|=pos;v=round(f(r['bwar162']),1)
            if v>e['v']: e['v']=v;e['s']=y
    if f(r['starts'])>=15*sc and f(r['innings'])>=100*sc:
        k=(fr,dec,pid,'P');e=best.setdefault(k,{'n':r['player_name'],'pos':{'SP'},'v':-99,'s':y})
        v=round(f(r['pwar162']),1)
        if v>e['v']: e['v']=v;e['s']=y
combos=collections.defaultdict(list)
for (fr,dec,pid,kind),e in best.items(): combos[(fr,dec)].append((pid,kind,e))
ORDER=HP+['DH','SP'];outc=[]
for (fr,dec),ps in sorted(combos.items()):
    H=sorted([p for p in ps if p[1]=='H'],key=lambda x:-x[2]['v']);Pp=sorted([p for p in ps if p[1]=='P'],key=lambda x:-x[2]['v'])
    if len(H)<9 or len(Pp)<5: continue
    keep={p[0] for p in H[:12]}
    for pos in HP: keep|={p[0] for p in [x for x in H if pos in x[2]['pos']][:2]}
    sel=[p for p in H if p[0] in keep]+Pp[:8]
    name=nm[(fr,dec)].most_common(1)[0][0] if nm[(fr,dec)] else fr
    outc.append({'f':fr,'d':dec,'n':name,'p':[[pid,e['n'],'/'.join(x for x in ORDER if x in e['pos']),e['v'],e['s']] for pid,kind,e in sel]})
json.dump(outc,open(out,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(len(outc),'combos',sum(len(c['p']) for c in outc),'entries',os.path.getsize(out),'bytes')
for c in outc:
    if (c['f'],c['d']) in (('NYY',1920),('SFG',2000),('BOS',2000)): print(c['n'],c['d'],[(p[1],p[2],p[3],p[4]) for p in c['p'][:5]],[(p[1],p[3]) for p in c['p'] if p[2]=='SP'][:3])
# how much WAR is reachable in 14 rounds taking the best available each spin?
SL=HP+['DH']+['SP']*5;random.seed(5);tot=[]
def elig(p,s): return (s=='SP' and p[2]=='SP') or (s!='SP' and p[2]!='SP' and (s=='DH' or s in p[2].split('/')))
for _ in range(600):
    open_=list(SL);used=set();t=0;usedc=set()
    while open_:
        ci=random.choice([i for i in range(len(outc)) if i not in usedc and any(p[0] not in used and any(elig(p,s) for s in set(open_)) for p in outc[i]['p'])])
        usedc.add(ci);c=[p for p in outc[ci]['p'] if p[0] not in used and any(elig(p,s) for s in set(open_))]
        p=max(c,key=lambda p:p[3]);used.add(p[0]);t+=p[3]
        ss=[s for s in set(open_) if elig(p,s)];s=next((x for x in ss if x!='DH'),ss[0]);open_.remove(s)
    tot.append(t)
q=sorted(tot);print('best-available team WAR: avg %.0f  5%% %.0f  median %.0f  95%% %.0f  max %.0f'%(st.mean(tot),q[30],q[300],q[570],q[-1]))
