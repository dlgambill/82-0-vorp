import csv,sys,json,collections
src,out,pbp=sys.argv[1],sys.argv[2],sys.argv[3]
NAME={'ATL':'Atlanta Hawks','BOS':'Boston Celtics','BRK':'Brooklyn Nets','NJN':'New Jersey Nets','NYN':'New York Nets','NYA':'New York Nets','BUF':'Buffalo Braves','SDC':'San Diego Clippers','LAC':'Los Angeles Clippers','CAP':'Capital Bullets','WSB':'Washington Bullets','WAS':'Washington Wizards','CHH':'Charlotte Hornets','CHA':'Charlotte Bobcats','CHO':'Charlotte Hornets','CHI':'Chicago Bulls','CLE':'Cleveland Cavaliers','DAL':'Dallas Mavericks','DEN':'Denver Nuggets','DNA':'Denver Nuggets','DNR':'Denver Rockets','DET':'Detroit Pistons','GSW':'Golden State Warriors','HOU':'Houston Rockets','IND':'Indiana Pacers','INA':'Indiana Pacers','KCO':'Kansas City-Omaha Kings','KCK':'Kansas City Kings','SAC':'Sacramento Kings','LAL':'Los Angeles Lakers','MEM':'Memphis Grizzlies','VAN':'Vancouver Grizzlies','MIA':'Miami Heat','MIL':'Milwaukee Bucks','MIN':'Minnesota Timberwolves','NOJ':'New Orleans Jazz','UTA':'Utah Jazz','NOH':'New Orleans Hornets','NOK':'New Orleans Hornets','NOP':'New Orleans Pelicans','NYK':'New York Knicks','OKC':'Oklahoma City Thunder','SEA':'Seattle SuperSonics','ORL':'Orlando Magic','PHI':'Philadelphia 76ers','PHO':'Phoenix Suns','POR':'Portland Trail Blazers','SAS':'San Antonio Spurs','SAA':'San Antonio Spurs','TOR':'Toronto Raptors'}
NAME.update({'MNL':'Minneapolis Lakers','SFW':'San Francisco Warriors','PHW':'Philadelphia Warriors','SYR':'Syracuse Nationals','CIN':'Cincinnati Royals','ROC':'Rochester Royals','FTW':'Fort Wayne Pistons','STL':'St. Louis Hawks','MLH':'Milwaukee Hawks','TRI':'Tri-Cities Blackhawks','SDR':'San Diego Rockets','BAL':'Baltimore Bullets','CHP':'Chicago Packers','CHZ':'Chicago Zephyrs','DLC':'Dallas Chaparrals','TEX':'Texas Chaparrals','NJA':'New Jersey Americans'})
FR={'MNL':'LAL','SFW':'GSW','PHW':'GSW','SYR':'PHI','CIN':'SAC','ROC':'SAC','FTW':'DET','STL':'ATL','MLH':'ATL','TRI':'ATL','SDR':'HOU','BAL':'WAS','CHP':'WAS','CHZ':'WAS','DLC':'SAS','TEX':'SAS','NJA':'BRK','NJN':'BRK','NYN':'BRK','NYA':'BRK','BUF':'LAC','SDC':'LAC','CAP':'WAS','WSB':'WAS','CHH':'CHO','CHA':'CHO','DNA':'DEN','DNR':'DEN','INA':'IND','KCO':'SAC','KCK':'SAC','VAN':'MEM','NOJ':'UTA','NOH':'NOP','NOK':'NOP','SEA':'OKC','SAA':'SAS'}
def slen(season,lg):
    if lg=='ABA': return 78 if season<1970 else 84
    if season<1968: return {1950:68,1951:68,1952:66,1953:70,1960:75,1961:79,1967:81}.get(season,72 if season<1960 else 80)
    return {1999:50,2012:66,2020:72,2021:72}.get(season,82)
best={}  # (fr,dec,pid)->dict
codes=collections.defaultdict(collections.Counter)
career=collections.defaultdict(set)
for r in csv.DictReader(open(src,encoding='utf-8')):
    t=r['team']
    if t not in NAME or r['lg']=='BAA' or r['pos'] in('','NA'): continue
    s=int(r['season'])
    if s>2026 or s<1950: continue
    est=r['vorp'] in('','NA')
    if est and (s>=1974 or r['ws'] in('','NA')): continue
    L=slen(s,r['lg']); g=int(r['g'])
    if g<0.6*L: continue
    v=round((-0.85+0.471*float(r['ws'])*82/L) if est else float(r['vorp'])*82/L,1)
    fr=FR.get(t,t); dec=s//10*10
    career[r['player_id']].add(r['pos'])
    codes[(fr,dec)][t]+=1
    k=(fr,dec,r['player_id'])
    e=best.setdefault(k,{'n':r['player'],'pos':set(),'v':-99,'s':s,'est':0})
    e['pos'].add(r['pos'])
    if v>e['v']: e['v']=v; e['s']=s; e['est']=int(est); e['code']=t
share=collections.defaultdict(set)
for r in csv.DictReader(open(pbp,encoding='utf-8')):
    t=r['team']
    if t not in NAME: continue
    s=int(r['season'])
    if s>2026 or int(r['g'])<0.6*slen(s,r['lg']): continue
    for pos in ['PG','SG','SF','PF','C']:
        x=r[pos.lower()+'_percent']
        if x not in('','NA') and float(x)>=20: share[(FR.get(t,t),s//10*10,r['player_id'])].add(pos)
for k,e in best.items(): e['sec']=((career[k[2]] if k[1]<2000 else set())|share[k])-e['pos']
combos=collections.defaultdict(list)
for (fr,dec,pid),e in best.items(): combos[(fr,dec)].append((pid,e))
ORDER=['PG','SG','SF','PF','C']
outc=[]
for (fr,dec),ps in sorted(combos.items()):
    ps.sort(key=lambda x:-x[1]['v'])
    keep={pid for pid,_ in ps[:12]}
    for pos in ORDER:
        keep|={pid for pid,e in [p for p in ps if pos in p[1]['pos'] or pos in p[1]['sec']][:2]}
    sel=[(pid,e) for pid,e in ps if pid in keep]
    if len(sel)<8: continue
    code=codes[(fr,dec)].most_common(1)[0][0]
    outc.append({'f':fr,'d':dec,'n':NAME[code],
      'p':[[pid,e['n'],'/'.join(p for p in ORDER if p in e['pos']),e['v'],e['s'],'/'.join(p for p in ORDER if p in e['sec']),e['est'],'' if NAME[e['code']]==NAME[code] else NAME[e['code']]] for pid,e in sel]})
json.dump(outc,open(out,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(len(outc),'combos',sum(len(c['p']) for c in outc),'players')
import os;print(os.path.getsize(out))
for c in outc:
    if (c['f'],c['d']) in [('CHI',1990),('OKC',1970),('BRK',1970),('DEN',2020)]: print(c['n'],c['d'],c['p'][:4])
tops=sorted([c['p'][0][3] for c in outc]);print('median best',tops[len(tops)//2],'min',tops[0],'max',tops[-1])

for c in outc:
    for p in c['p']:
        if p[1] in('Wilt Chamberlain','Bill Russell','Oscar Robertson','Kareem Abdul-Jabbar','Jerry West','George Mikan','Bob Pettit'): print(c['n'],c['d'],p[1:])
print(sum(1 for c in outc for p in c['p'] if p[5]),'with secondary')
import collections as C;print(sorted(C.Counter(c['d'] for c in outc).items()))
