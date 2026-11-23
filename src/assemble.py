import json,sys
c=json.load(open(sys.argv[1],encoding='utf-8'))
def row(p):
    r=[p[1],p[2],p[3],p[4],p[5],p[6],p[7]]
    while r[-1] in ('',0): r.pop()
    return r
for x in c: x['p']=[row(p) for p in x['p']]
d=json.dumps(c,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
open(sys.argv[3],'w',encoding='utf-8').write(open(sys.argv[2],encoding='utf-8').read().replace('__DATA__',d))
print(len(d))
