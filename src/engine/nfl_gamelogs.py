"""Regular-season totals by player, season and team from game logs (playoff games dropped)."""
import ijson,sys,csv,collections,glob
d,out=sys.argv[1:3]
AFL={'BOS','BUF','DTX','KAN','DEN','HOU','NYT','NYJ','OAK','LAC','SDG','MIA','CIN'}
def nreg(y,t):
    if y==1982: return 9
    if y==1987: return 15
    if y>=1978: return 16
    if y>=1961: return 14
    return 14 if (y==1960 and t in AFL) else 12
rows=[];dates=collections.defaultdict(set)
for g in ijson.items(open(glob.glob(d+'/games_*.json')[0],'rb'),'item'):
    y=int(g['year'])
    if y>1998: continue
    rows.append((g['player_id'],y,g['team'],g['date'],int(g['rushing_touchdowns'] or 0),int(g['receiving_touchdowns'] or 0),int(g['passing_yards'] or 0)))
    dates[(y,g['team'])].add(g['date'])
ok={k:set(sorted(v)[:nreg(*k)]) for k,v in dates.items()}
agg=collections.defaultdict(lambda:[0,0,0,0]);drop=0
for p,y,t,dt,a,b,c in rows:
    if dt not in ok[(y,t)]: drop+=1;continue
    x=agg[(p,y,t)];x[0]+=1;x[1]+=a;x[2]+=b;x[3]+=c
w=csv.writer(open(out,'w',newline=''));w.writerow(['pid','year','team','g','rtd','ctd','pyds'])
for (p,y,t),a in agg.items(): w.writerow([p,y,t]+a)
print(len(rows),'game rows through 1998,',drop,'playoff rows dropped ->',len(agg),'season rows')
import collections as C;print('teams by games in a season (should be 12/14/16/9/15):',sorted(C.Counter(len(v) for v in ok.values()).items()))
