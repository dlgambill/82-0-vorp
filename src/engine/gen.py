import json,sys,os,random,statistics as st
out=sys.argv[1]
NFL={"ARI":["Arizona Cardinals","Includes the St. Louis and Phoenix Cardinals"],"ATL":["Atlanta Falcons"],"BAL":["Baltimore Ravens"],"BUF":["Buffalo Bills"],"CAR":["Carolina Panthers"],"CHI":["Chicago Bears"],"CIN":["Cincinnati Bengals"],"CLE":["Cleveland Browns"],"DAL":["Dallas Cowboys"],"DEN":["Denver Broncos"],"DET":["Detroit Lions"],"GB":["Green Bay Packers"],"HOU":["Houston Texans"],"IND":["Indianapolis Colts","Includes the Baltimore Colts"],"JAX":["Jacksonville Jaguars"],"KC":["Kansas City Chiefs"],"LAC":["Los Angeles Chargers","Includes the San Diego Chargers"],"LAR":["Los Angeles Rams","Includes the St. Louis Rams"],"LV":["Las Vegas Raiders","Includes the Oakland and Los Angeles Raiders"],"MIA":["Miami Dolphins"],"MIN":["Minnesota Vikings"],"NE":["New England Patriots"],"NO":["New Orleans Saints"],"NYG":["New York Giants"],"NYJ":["New York Jets"],"PHI":["Philadelphia Eagles"],"PIT":["Pittsburgh Steelers"],"SEA":["Seattle Seahawks"],"SF":["San Francisco 49ers"],"TB":["Tampa Bay Buccaneers"],"TEN":["Tennessee Titans","Includes the Houston Oilers"],"WAS":["Washington Commanders","Includes every Washington era"]}
NBA={"ATL":["Atlanta Hawks","Includes the St. Louis, Milwaukee and Tri-Cities Hawks"],"BOS":["Boston Celtics"],"BRK":["Brooklyn Nets","Includes the New Jersey and New York Nets (NBA years)"],"CHO":["Charlotte Hornets","Includes the Bobcats and the original Hornets"],"CHI":["Chicago Bulls"],"CLE":["Cleveland Cavaliers"],"DAL":["Dallas Mavericks"],"DEN":["Denver Nuggets"],"DET":["Detroit Pistons","Includes the Fort Wayne Pistons"],"GSW":["Golden State Warriors","Includes the San Francisco and Philadelphia Warriors"],"HOU":["Houston Rockets","Includes the San Diego Rockets"],"IND":["Indiana Pacers"],"LAC":["Los Angeles Clippers","Includes the San Diego Clippers and Buffalo Braves"],"LAL":["Los Angeles Lakers","Includes the Minneapolis Lakers"],"MEM":["Memphis Grizzlies","Includes the Vancouver Grizzlies"],"MIA":["Miami Heat"],"MIL":["Milwaukee Bucks"],"MIN":["Minnesota Timberwolves"],"NOP":["New Orleans Pelicans","Includes the New Orleans Hornets"],"NYK":["New York Knicks"],"OKC":["Oklahoma City Thunder","Includes the Seattle SuperSonics"],"ORL":["Orlando Magic"],"PHI":["Philadelphia 76ers","Includes the Syracuse Nationals"],"PHO":["Phoenix Suns"],"POR":["Portland Trail Blazers"],"SAC":["Sacramento Kings","Includes the Kansas City Kings and the Royals"],"SAS":["San Antonio Spurs"],"TOR":["Toronto Raptors"],"UTA":["Utah Jazz","Includes the New Orleans Jazz"],"WAS":["Washington Wizards","Includes the Bullets, Zephyrs and Packers"]}
MLB={"ANA":["Los Angeles Angels","Includes the California and Anaheim Angels"],"ARI":["Arizona Diamondbacks"],"ATL":["Atlanta Braves","Includes the Boston and Milwaukee Braves"],"BAL":["Baltimore Orioles","Includes the St. Louis Browns"],"BOS":["Boston Red Sox"],"CHC":["Chicago Cubs"],"CHW":["Chicago White Sox"],"CIN":["Cincinnati Reds"],"CLE":["Cleveland Guardians","Includes the Cleveland Indians and Naps"],"COL":["Colorado Rockies"],"DET":["Detroit Tigers"],"FLA":["Miami Marlins","Includes the Florida Marlins"],"HOU":["Houston Astros","Includes the Colt .45s"],"KCR":["Kansas City Royals"],"LAD":["Los Angeles Dodgers","Includes the Brooklyn Dodgers"],"MIL":["Milwaukee Brewers","Includes the Seattle Pilots"],"MIN":["Minnesota Twins","Includes the original Washington Senators"],"NYM":["New York Mets"],"NYY":["New York Yankees","Includes the Highlanders"],"OAK":["Athletics","Includes the Oakland, Kansas City and Philadelphia Athletics"],"PHI":["Philadelphia Phillies"],"PIT":["Pittsburgh Pirates"],"SDP":["San Diego Padres"],"SEA":["Seattle Mariners"],"SFG":["San Francisco Giants","Includes the New York Giants"],"STL":["St. Louis Cardinals"],"TBD":["Tampa Bay Rays","Includes the Devil Rays"],"TEX":["Texas Rangers","Includes the second Washington Senators"],"TOR":["Toronto Blue Jays"],"WSN":["Washington Nationals","Includes the Montreal Expos"]}
NFLNOTE=["Who is in the pool.","Players whose careers started in 1950 or later. The game-by-game records behind the older numbers begin in 1950, so the 70 or so players who were already in the league then are left out so nobody shows a short total."]
FR=["Teams follow the franchise.","A team includes its earlier cities and names. Years next to a name are his first and last season with that team."]
G=[
 dict(id="touchdown-chase",title=["Touchdown","Chase"],sport="NFL",league="NFL",teams=NFL,accL="#17703f",accD="#4bc884",rounds=20,target=1800,scope="career",unit="touchdowns",abbr="TD",noun="running back",nouns="running backs",eyebrow="NFL running backs · career touchdowns",
      step3="His career touchdowns go on your total, including the ones he scored for other teams.",tip="A star who made a late-career stop somewhere still brings his whole career with him.",
      menu="20 random teams, 20 running backs. You see names, not numbers. Reach 1,800 career touchdowns.",
      counts=[["Touchdowns are rushing plus receiving,","regular season only, through week 12 of the 2026 season. Return and passing touchdowns are not counted."],NFLNOTE,FR]),
 dict(id="homegrown",title=["Home","Grown"],sport="NFL",league="NFL",teams=NFL,accL="#8a5a00",accD="#e3a83a",rounds=20,scope="team",unit="touchdowns",abbr="TD",noun="running back",nouns="running backs",eyebrow="NFL running backs · touchdowns for that team only",
      step3="Only the touchdowns he scored for that team go on your total.",tip="A legend on his last stop is worth almost nothing here.",
      menu="Touchdown Chase with a twist. Only the touchdowns a back scored for that team count.",
      counts=[["Touchdowns are rushing plus receiving","scored for the team you drew, regular season only, through week 12 of the 2026 season."],NFLNOTE,FR]),
 dict(id="air-yards",title=["Air","Yards"],sport="NFL",league="NFL",teams=NFL,accL="#1d5fa8",accD="#62a8f5",rounds=10,scope="career",unit="passing yards",abbr="YDS",noun="quarterback",nouns="quarterbacks",eyebrow="NFL quarterbacks · career passing yards",
      step3="His career passing yards go on your total, including the ones he threw for other teams.",tip="Remember where the greats finished up.",
      menu="10 random teams, 10 quarterbacks. Stack up career passing yards without seeing the numbers.",
      counts=[["Passing yards are regular season only,","through week 12 of the 2026 season."],NFLNOTE,FR]),
 dict(id="bucket-list",title=["Bucket","List"],sport="NBA",league="NBA",teams=NBA,accL="#d9480f",accD="#ff6b2c",rounds=12,scope="career",unit="points",abbr="PTS",noun="player",nouns="players",eyebrow="NBA players · career points",
      step3="His career points go on your total, including the ones he scored for other teams.",tip="Late-career ring chasing counts in your favor.",
      menu="12 random teams, 12 players. Pile up career points without seeing the numbers.",
      counts=[["Points are regular season only,","NBA and BAA, through the current 2026-27 season so far. ABA points are not counted, which matches the NBA record book."],["Who is in the pool.","Everyone who has played a regular season game for the franchise, back to 1946."],FR]),
 dict(id="dime-store",title=["Dime","Store"],sport="NBA",league="NBA",teams=NBA,accL="#7a3fb0",accD="#b98af0",rounds=12,scope="career",target=100000,unit="assists",abbr="AST",noun="player",nouns="players",eyebrow="NBA players · career assists",
      step3="His career assists go on your total, including the ones he handed out for other teams.",tip="Point guards travel. Use that.",
      menu="12 random teams, 12 players. Career assists this time, so think point guards.",
      counts=[["Assists are regular season only,","NBA and BAA, through the current 2026-27 season so far. ABA assists are not counted."],["Who is in the pool.","Everyone who has played a regular season game for the franchise, back to 1946."],FR]),
 dict(id="home-run-chase",title=["Home Run","Chase"],sport="MLB",league="MLB",teams=MLB,accL="#b3261e",accD="#ff7466",rounds=15,scope="career",unit="home runs",abbr="HR",noun="hitter",nouns="hitters",eyebrow="MLB hitters · career home runs",
      step3="His career home runs go on your total, including the ones he hit for other teams.",tip="Sluggers bounce around late. Know where they landed.",
      menu="15 random teams, 15 hitters. Stack career home runs without seeing the numbers.",
      counts=[["Home runs are regular season only,","through the 2025 season. The 2026 season is not in the data yet."],["Who is in the pool.","Every non-pitcher who has played for the franchise, back to 1876. Negro Leagues statistics are not in this data set."],FR]),
 dict(id="catch-rickey",title=["Catch","Rickey"],sport="MLB",league="MLB",teams=MLB,accL="#0b6b4f",accD="#3fd0a0",rounds=4,target=1407,respins=1,top=15,scope="team",unit="stolen bases",abbr="SB",noun="player",nouns="players",eyebrow="MLB · stolen bases for that team only",
      big="1,406",pitch="Rickey Henderson stole 1,406 bases. You get four players to steal more.",win="You caught Rickey",lose="Rickey is still safe",
      step2="You see that team's 15 all-time leading base stealers, A to Z, with no numbers. Pick one.",
      step3="Only the bases he stole for that team go on your total. Beat 1,406 and you win.",tip="Rickey himself is off the board.",
      menu="Rickey Henderson stole 1,406 bases. You get four teams and one respin to out-steal him, picking from each team's top 15.",
      counts=[["Stolen bases are regular season only","and only for the team you drew, through the 2025 season. The 2026 season is not in the data yet."],["The number to beat.","Rickey Henderson's 1,406 career steals is the all-time record. You need 1,407, and he is not in the player pool."],["Who is in the pool.","Each franchise's 15 all-time leaders in stolen bases for that franchise, listed alphabetically. Negro Leagues statistics are not in this data set."],FR]),
 dict(id="k-count",title=["K","Count"],sport="MLB",league="MLB",teams=MLB,accL="#0f6b78",accD="#4fc3d1",rounds=15,scope="career",unit="strikeouts",abbr="K",noun="pitcher",nouns="pitchers",eyebrow="MLB pitchers · career strikeouts",
      step3="His career strikeouts go on your total, including the ones he threw for other teams.",tip="Aces get traded at the deadline. That helps you.",
      menu="15 random teams, 15 pitchers. Career strikeouts, names only.",
      counts=[["Strikeouts are regular season only,","through the 2025 season. The 2026 season is not in the data yet."],["Who is in the pool.","Everyone who pitched regularly for the franchise, back to 1876. Negro Leagues statistics are not in this data set."],FR]),
 dict(id="hit-parade",title=["Hit","Parade"],sport="MLB",league="MLB",teams=MLB,accL="#5a6b12",accD="#b5cc4a",rounds=15,scope="team",unit="hits",abbr="H",noun="hitter",nouns="hitters",eyebrow="MLB hitters · hits for that team only",
      step3="Only the hits he got for that team go on your total.",tip="Think lifers, not rentals.",
      menu="15 random teams, 15 hitters. Only the hits a player got for that team count.",
      counts=[["Hits are regular season only","and only for the team you drew, through the 2025 season. The 2026 season is not in the data yet."],["Who is in the pool.","Every non-pitcher who has played for the franchise, back to 1876. Negro Leagues statistics are not in this data set."],FR]),
]
eng=open(os.path.dirname(os.path.abspath(__file__))+'/engine.html',encoding='utf-8').read()
menu=[]
for g in G:
    d=out+'/'+g['id'];P=json.load(open(d+'/data.json',encoding='utf-8'))
    team=g['scope']=='team'
    if g.get('top'):  # keep only each team's top N by value for that team
        keep=set()
        for t in g['teams']:
            for v,i in sorted(((x[3],i) for i,p in enumerate(P) for x in p[3] if x[0]==t),reverse=True)[:g['top']]: keep.add((i,t))
        P=[[p[0],p[1],p[2],[x for x in p[3] if (i,x[0]) in keep]] for i,p in enumerate(P)];P=[p for p in P if p[3]]
        json.dump(P,open(d+'/data.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    if not team:  # career games do not need per-team values
        P=[[p[0],p[1],p[2],[t[:3] for t in p[3]]] for p in P]
        json.dump(P,open(d+'/data.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    T=sorted(g['teams']);val=(lambda i,t:next(x[3] for x in P[i][3] if x[0]==t)) if team else (lambda i,t:P[i][1])
    ro={t:sorted([i for i,p in enumerate(P) if any(x[0]==t for x in p[3])],key=lambda i:-val(i,t)) for t in T}
    assert all(len(ro[t])>=g['rounds'] for t in T),g['id']
    random.seed(11);res=[]
    for _ in range(400):
        used=set();tot=0
        for t in random.choices(T,k=g['rounds']):
            c=next(i for i in ro[t] if i not in used);used.add(c);tot+=val(c,t)
        res.append(tot)
    avg=st.mean(res)
    if 'target' not in g:
        raw=avg*0.87;step=10**(len(str(int(raw)))-2);g['target']=int(round(raw/step)*step)
    print('%-16s rounds %2d  top-pick avg %9.0f  min %8d  target %8d (%.0f%%)  pool/team %d-%d  data %dKB'%(g['id'],g['rounds'],avg,min(res),g['target'],100*g['target']/avg,min(map(len,ro.values())),max(map(len,ro.values())),os.path.getsize(d+'/data.json')//1024))
    cfg={k:g[k] for k in('id','title','league','teams','rounds','target','scope','unit','abbr','noun','nouns','eyebrow','step3','tip','counts','respins','big','pitch','win','lose','step2') if k in g}
    html=eng.replace('__TITLE__',' '.join(g['title'])).replace('__ACC_L__',g['accL']).replace('__ACC_D__',g['accD']).replace('__CFG__',json.dumps(cfg,ensure_ascii=False).replace('</','<\\/'))
    open(d+'/index.html','w',encoding='utf-8').write(html)
    menu.append({k:g[k] for k in('id','title','sport','accL','accD','menu')})
json.dump(menu,open(out+'/menu.json','w'),indent=1)
