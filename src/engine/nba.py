import csv,sys,json,os,collections
src,outdir=sys.argv[1:3]
FR={'NJN':'BRK','NYN':'BRK','BUF':'LAC','SDC':'LAC','CAP':'WAS','WSB':'WAS','BAL':'WAS','CHP':'WAS','CHZ':'WAS','CHH':'CHO','CHA':'CHO','KCO':'SAC','KCK':'SAC','CIN':'SAC','ROC':'SAC','VAN':'MEM','NOJ':'UTA','NOH':'NOP','NOK':'NOP','SEA':'OKC','MNL':'LAL','SFW':'GSW','PHW':'GSW','SYR':'PHI','FTW':'DET','STL':'ATL','MLH':'ATL','TRI':'ATL','SDR':'HOU'}
CUR={'ATL','BOS','BRK','CHO','CHI','CLE','DAL','DEN','DET','GSW','HOU','IND','LAC','LAL','MEM','MIA','MIL','MIN','NOP','NYK','OKC','ORL','PHI','PHO','POR','SAC','SAS','TOR','UTA','WAS'}
P={}
for r in csv.DictReader(open(src,encoding='utf-8')):
    if r['lg'] not in('NBA','BAA') or r['team'].endswith('TM') or r['team']=='TOT': continue
    t=FR.get(r['team'],r['team'])
    # BAL 1948-55 original Bullets are defunct, not the Wizards franchise
    if r['team']=='BAL' and int(r['season'])<1964: t='XXX'
    e=P.setdefault(r['player_id'],{'n':r['player'],'tot':[0,0],'tm':collections.defaultdict(lambda:{'y':set(),'v':[0,0]})})
    v=[int(float(r['pts'] or 0)) if r['pts'] not in('NA','') else 0,int(float(r['ast'])) if r['ast'] not in('NA','') else 0]
    for i in (0,1): e['tot'][i]+=v[i]
    if t in CUR:
        e['tm'][t]['y'].add(int(r['season']))
        for i in (0,1): e['tm'][t]['v'][i]+=v[i]
for i,g in ((0,'bucket-list'),(1,'dime-store')):
    rows=[e for e in P.values() if e['tm']];rows.sort(key=lambda e:-e['tot'][i])
    out=[[e['n'],e['tot'][i],'',[[t,min(x['y'])-1,max(x['y']),x['v'][i]] for t,x in sorted(e['tm'].items(),key=lambda z:min(z[1]['y']))]] for e in rows]
    os.makedirs(outdir+'/'+g,exist_ok=True);f=outdir+'/'+g+'/data.json'
    json.dump(out,open(f,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    print(g,len(out),os.path.getsize(f),[(p[0],p[1]) for p in out[:8]])
