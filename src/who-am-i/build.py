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
    p=ppl[pid];a,b=years(pid);c=[]
    if isP:
        role='starting pitcher' if pit[pid]['GS']>=0.5*pit[pid]['G'] else 'relief pitcher'
        c.append('I was a %s. I threw %s-handed.'%(role,HAND.get(p['throws'],'right')))
    else:
        g=app[pid];pos=max(POS[1:],key=lambda x:g[x[0]])[1]
        c.append('I was a %s. I batted %s and threw %s-handed.'%(pos.lower(),{'R':'right-handed','L':'left-handed','B':'from both sides'}.get(p['bats'],'right-handed'),HAND.get(p['throws'],'right')))
    ns=len({y for y,_,_ in stints[pid]})
    c.append('I debuted in %s, have played %s, and was still active in 2025.'%(a,plural(ns,'season')) if (not b or b>='2025') else 'I debuted in %s and played %s, through %s.'%(a,plural(ns,'season'),b))
    if p['birthCountry']=='USA' and p['birthState'] in US: c.append('I was born in %s.'%US[p['birthState']])
    else: c.append('I was born in %s.'%CTRY.get(p['birthCountry'],p['birthCountry']))
    h=[]
    if pid in hof: h.append('I am in the Hall of Fame')
    k=len(asg[pid])
    if k: h.append(('I was' if not h else 'was')+' an All-Star in '+plural(k,'season'))
    for key,lab in (('Most Valuable Player','MVP award'),('Cy Young Award','Cy Young Award'),('Gold Glove','Gold Glove'),('Silver Slugger','Silver Slugger')):
        if aw[pid][key]: h.append(('I won ' if not h else 'won ')+plural(aw[pid][key],lab))
    if aw[pid]['Rookie of the Year']: h.append(('I was' if not h else 'was')+' Rookie of the Year')
    if not h: c.append('I never made an All-Star team or won a major award.')
    else: c.append((', '.join(h[:-1])+(', and ' if len(h)>2 else ' and ' if len(h)==2 else '')+h[-1] if len(h)>1 else h[0])+'.')
    if isP:
        q=pit[pid];era=q['ER']*27/q['IPouts'] if q['IPouts'] else 0
        c.append('My career line: %d wins, %d losses, a %.2f ERA, %s strikeouts and %s.'%(q['W'],q['L'],era,format(q['SO'],','),plural(q['SV'],'save')))
    else:
        q=bat[pid];c.append('My career line: %s hits, %s, %s and a %s batting average.'%(format(q['H'],','),plural(q['HR'],'home run'),plural(q['SB'],'stolen base'),('%.3f'%(q['H']/q['AB'])).lstrip('0')))
    t=teams(pid)
    c.append('I played for the '+'; the '.join('%s (%s)'%(k,', '.join(v)) for k,v in t.items())+'.')
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
