import csv,sys,json,collections,random,os
d,out=sys.argv[1:3]
R=lambda f:csv.DictReader(open(d+'/'+f+'.csv',encoding='utf-8'))
n=lambda x:int(float(x)) if x not in('','NA') else 0
ppl={r['playerID']:r for r in R('People')}
tname={(r['yearID'],r['teamID']):r['name'] for r in R('Teams')}
bat=collections.defaultdict(lambda:collections.Counter());pit=collections.defaultdict(lambda:collections.Counter())
stints=collections.defaultdict(list)
for r in R('Batting'):
    b=bat[r['playerID']]
    for k in('G','AB','H','HR','SB','RBI'): b[k]+=n(r[k])
    stints[r['playerID']].append((int(r['yearID']),n(r['stint']),tname.get((r['yearID'],r['teamID']),r['teamID'])))
for r in R('Pitching'):
    p=pit[r['playerID']]
    for k in('G','GS','W','L','SO','SV','ER','IPouts'): p[k]+=n(r[k])
bs=collections.defaultdict(lambda:collections.defaultdict(collections.Counter));ps=collections.defaultdict(lambda:collections.defaultdict(collections.Counter))
bl=collections.defaultdict(collections.Counter);pl_=collections.defaultdict(collections.Counter)
for r in R('Batting'):
    y=int(r['yearID'])
    for k in('AB','H','X2B','X3B','HR','RBI','SB'):
        v=n(r.get(k,'0'));bs[r['playerID']][y][k]+=v
        if k in('H','HR','RBI','SB'): bl[(y,r['lgID'],k)][r['playerID']]+=v
for r in R('Pitching'):
    y=int(r['yearID'])
    for k in('W','L','SO','SV','ER','IPouts'):
        v=n(r[k]);ps[r['playerID']][y][k]+=v
        if k in('W','SO','SV'): pl_[(y,r['lgID'],k)][r['playerID']]+=v
led=collections.defaultdict(collections.Counter)
for src in (bl,pl_):
    for (y,lg,k),c in src.items():
        if lg not in('AL','NL') or y<1901: continue
        m=max(c.values())
        if m<=0: continue
        for pid,v in c.items():
            if v==m: led[pid][k]+=1
TIMES=lambda k:'once' if k==1 else 'twice' if k==2 else '%d times'%k
LEDN={'HR':'home runs','RBI':'RBI','H':'hits','SB':'stolen bases','W':'wins','SO':'strikeouts','SV':'saves'}
frn={(r['yearID'],r['teamID']):r['franchID'] for r in R('Teams')}
nfr=collections.defaultdict(set)
for r in R('Batting'): nfr[r['playerID']].add(frn.get((r['yearID'],r['teamID']),r['teamID']))
def join(h): return h[0] if len(h)==1 else ' and '.join(h) if len(h)==2 else ', '.join(h[:-1])+', and '+h[-1]
POS=[('G_p','Pitcher'),('G_c','Catcher'),('G_1b','First baseman'),('G_2b','Second baseman'),('G_3b','Third baseman'),('G_ss','Shortstop'),('G_lf','Left fielder'),('G_cf','Center fielder'),('G_rf','Right fielder'),('G_dh','Designated hitter')]
app=collections.defaultdict(collections.Counter)
for r in R('Appearances'):
    for k,_ in POS: app[r['playerID']][k]+=n(r[k])
    app[r['playerID']]['G_of']+=n(r['G_of'])
asg=collections.defaultdict(set)
for r in R('AllstarFull'): asg[r['playerID']].add(r['yearID'])
aw=collections.defaultdict(collections.Counter)
for r in R('AwardsPlayers'): aw[r['playerID']][r['awardID']]+=1
hof={r['playerID'] for r in R('HallOfFame') if r['inducted']=='Y' and r['category']=='Player'}
US={'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California','CO':'Colorado','CT':'Connecticut','DE':'Delaware','DC':'Washington, D.C.','FL':'Florida','GA':'Georgia','HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas','KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts','MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana','NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico','NY':'New York','NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma','OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina','SD':'South Dakota','TN':'Tennessee','TX':'Texas','UT':'Utah','VT':'Vermont','VA':'Virginia','WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming'}
CTRY={'D.R.':'the Dominican Republic','P.R.':'Puerto Rico','CAN':'Canada','USA':'the United States','V.I.':'the U.S. Virgin Islands','Bahamas':'the Bahamas','Netherlands':'the Netherlands','Curacao':'Curaçao'}
HAND={'R':'right','L':'left','B':'both sides'}
def plural(k,w): return '%s %s%s'%(format(k,','),w,'' if k==1 else 's')
def years(pid):
    p=ppl[pid];f=(p['finalGame'] or '')[:4];return (p['debut'][:4],f if f.isdigit() else '')
def teams(pid):
    ys=collections.OrderedDict()
    for y,s,t in sorted(stints[pid]): ys.setdefault(t,set()).add(y)
    by=collections.OrderedDict()
    for t,st in ys.items():
        sp=[];
        for y in sorted(st):
            if sp and y==sp[-1][1]+1: sp[-1][1]=y
            else: sp.append([y,y])
        by[t]=[str(a) if a==b else '%d–%d'%(a,b) for a,b in sp]
    return by
def clues(pid,isP):
    p=ppl[pid];a,b=years(pid);c=[];active=(not b or b>='2025')
    span='since %s and was still active in 2025'%a if active else 'from %s to %s'%(a,b)
    # 1. who and when
    if isP:
        role='starting pitcher' if pit[pid]['GS']>=0.5*pit[pid]['G'] else 'relief pitcher'
        c.append('I %s a %s-handed %s who %s pitched %s.'%('am' if active else 'was',HAND.get(p['throws'],'right'),role,'has' if active else '',span))
    else:
        g=app[pid];pos=max(POS[1:],key=lambda x:g[x[0]])[1].lower()
        bt={'R':'right-handed','L':'left-handed','B':'from both sides'}.get(p['bats'],'right-handed')
        c.append('I %s a %s who %s played %s. I %s %s and %s %s-handed.'%('am' if active else 'was',pos,'has' if active else '',span,'bat' if active else 'batted',bt,'throw' if active else 'threw',HAND.get(p['throws'],'right')))
    c[-1]=c[-1].replace('  ',' ')
    # 2. honors and league-leading seasons
    h=[]
    if pid in hof: h.append('am in the Hall of Fame')
    k=len(asg[pid])
    if k: h.append('was an All-Star in '+plural(k,'season'))
    for key,lab in (('Most Valuable Player','MVP award'),('Cy Young Award','Cy Young Award'),('Gold Glove','Gold Glove'),('Silver Slugger','Silver Slugger')):
        if aw[pid][key]: h.append('won '+plural(aw[pid][key],lab))
    if aw[pid]['Rookie of the Year']: h.append('was Rookie of the Year')
    t='I '+join(h)+'.' if h else 'I never made an All-Star team or won a major award.'
    L=[(LEDN[k2],v) for k2,v in led[pid].items()];L.sort(key=lambda x:-x[1])
    if L: t+=' I led my league in '+join(['%s %s'%(n2,TIMES(v)) for n2,v in L])+'.'
    c.append(t)
    # 3. best season
    if isP:
        ss=ps[pid];sp=pit[pid]['GS']>=0.5*pit[pid]['G']
        y=max(ss,key=lambda y:(ss[y]['W'],ss[y]['SO']) if sp else (ss[y]['SV'],ss[y]['SO']));q=ss[y];era=q['ER']*27/q['IPouts'] if q['IPouts'] else 0
        c.append('My best season was %d: %s, %s, a %.2f ERA and %s.'%(y,plural(q['W'],'win'),plural(q['L'],'loss').replace('losss','losses'),era,plural(q['SO'],'strikeout')) if sp else 'My best season was %d: %s, a %.2f ERA and %s.'%(y,plural(q['SV'],'save'),era,plural(q['SO'],'strikeout')))
    else:
        ss=bs[pid];tb=lambda q:q['H']+q['X2B']+2*q['X3B']+3*q['HR']
        y=max(ss,key=lambda y:tb(ss[y]));q=ss[y]
        c.append('My best season was %d: a %s average, %s, %s RBI and %s.'%(y,('%.3f'%(q['H']/q['AB'])).lstrip('0') if q['AB'] else '.000',plural(q['HR'],'home run'),q['RBI'],plural(q['SB'],'stolen base')))
    # 4. career line
    if isP:
        q=pit[pid];era=q['ER']*27/q['IPouts'] if q['IPouts'] else 0
        c.append('My career line: %s, %s, a %.2f ERA, %s and %s.'%(plural(q['W'],'win'),plural(q['L'],'loss').replace('losss','losses'),era,plural(q['SO'],'strikeout'),plural(q['SV'],'save')))
    else:
        q=bat[pid];c.append('My career line: %s, %s, %s and a %s batting average.'%(plural(q['H'],'hit'),plural(q['HR'],'home run'),plural(q['SB'],'stolen base'),('%.3f'%(q['H']/q['AB'])).lstrip('0')))
    # 5. birthplace and number of teams
    place=US[p['birthState']] if p['birthCountry']=='USA' and p['birthState'] in US else CTRY.get(p['birthCountry'],p['birthCountry']).replace('the ','')
    city=p['birthCity'] if p['birthCity'] not in('','NA') else ''
    k=len(nfr[pid])
    c.append('I was born in %s%s, and I %s.'%(city+', ' if city else '',place,('have played for one team so far' if active else 'played for one team my whole career') if k==1 else ('have played for %d teams'%k if active else 'played for %d teams'%k)))
    # 6. teams
    t=teams(pid)
    c.append('I played for the '+'; the '.join('%s (%s)'%(k2,', '.join(v)) for k2,v in t.items())+'.')
    return c
ans=[];names=[]
for pid,p in ppl.items():
    if not p['debut'] or p['debut']=='NA': continue
    a=p['debut'][:4];b=(p['finalGame'] or '')[:4]
    if not b.isdigit() or b>='2025': b='now'
    span=a+'–'+b
    isP=app[pid]['G_p']>=0.5*max(1,sum(app[pid][k] for k,_ in POS[1:])+app[pid]['G_p']) and pit[pid]['G']>0
    nm=(p['nameFirst']+' ' if p['nameFirst'] not in('','NA') else '')+p['nameLast']
    if bat[pid]['G']>=600 or pit[pid]['G']>=200: names.append([pid,nm,span])
    if int(a)<1920: continue
    B=bat[pid];Q=pit[pid]
    famous=(not isP and (B['H']>=2000 or B['HR']>=300 or len(asg[pid])>=5)) or (isP and (Q['W']>=180 or Q['SO']>=2200 or Q['SV']>=300 or len(asg[pid])>=5)) or pid in hof and int(a)>=1920
    if famous: ans.append([pid,nm,span,clues(pid,isP)])
ids={x[0] for x in names}
for x in ans:
    if x[0] not in ids: names.append(x[:3])
random.seed(820);random.shuffle(ans);names.sort(key=lambda x:x[1])
json.dump({'answers':ans,'names':names},open(out,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(len(ans),'mystery players,',len(names),'guessable names,',os.path.getsize(out)//1024,'KB')
for a in ans:
    if a[1] in('Derek Jeter','Pedro Martinez','Ichiro Suzuki','Mariano Rivera','Rickey Henderson','Shohei Ohtani'): print(a[1],a[2]);[print('  ',i+1,x) for i,x in enumerate(a[3])]
