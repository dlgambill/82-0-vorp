import csv,sys,json,os,collections
d,outdir=sys.argv[1:3]
fr={};cur=set()
for r in csv.DictReader(open(d+'/Teams.csv',encoding='utf-8')):
    fr[(r['yearID'],r['teamID'])]=r['franchID']
    if r['yearID']=='2025': cur.add(r['franchID'])
name={r['playerID']:((r['nameFirst']+' ') if r['nameFirst'] not in('','NA') else '')+r['nameLast'] for r in csv.DictReader(open(d+'/People.csv',encoding='utf-8'))}
gp=collections.Counter();ga=collections.Counter()
for r in csv.DictReader(open(d+'/Appearances.csv',encoding='utf-8')):
    f=lambda x:int(float(x)) if x not in('','NA') else 0
    gp[r['playerID']]+=f(r['G_p']);ga[r['playerID']]+=f(r['G_all'])
def load(file,cols):
    P={}
    for r in csv.DictReader(open(d+'/'+file,encoding='utf-8')):
        e=P.setdefault(r['playerID'],{'tot':[0]*len(cols),'tm':collections.defaultdict(lambda:{'y':set(),'v':[0]*len(cols)})})
        v=[int(float(r[c])) if r[c] not in('','NA') else 0 for c in cols]
        f=fr.get((r['yearID'],r['teamID']))
        for i in range(len(cols)): e['tot'][i]+=v[i]
        if f in cur:
            e['tm'][f]['y'].add(int(r['yearID']))
            for i in range(len(cols)): e['tm'][f]['v'][i]+=v[i]
    return P
def write(g,P,i,keepfn):
    rows=[(pid,e) for pid,e in P.items() if e['tm'] and keepfn(pid)];rows.sort(key=lambda x:-x[1]['tot'][i])
    out=[[name.get(pid,pid),e['tot'][i],'',[[t,min(x['y']),max(x['y']),x['v'][i]] for t,x in sorted(e['tm'].items(),key=lambda z:min(z[1]['y']))]] for pid,e in rows]
    os.makedirs(outdir+'/'+g,exist_ok=True);f=outdir+'/'+g+'/data.json'
    json.dump(out,open(f,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    print(g,len(out),os.path.getsize(f),[(p[0],p[1]) for p in out[:8]])
B=load('Batting.csv',['HR','H']);Pi=load('Pitching.csv',['SO','G'])
hitter=lambda pid:not (ga[pid] and gp[pid]>=0.5*ga[pid])
write('home-run-chase',B,0,hitter);write('hit-parade',B,1,hitter)
write('k-count',Pi,0,lambda pid:Pi[pid]['tot'][1]>=50 or (ga[pid] and gp[pid]>=0.3*ga[pid]))
print(sorted(cur))
