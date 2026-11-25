import json,sys,re
out,dest=sys.argv[1],sys.argv[2]
G=json.load(open(out+'/menu.json'))
extra=[dict(id='82-0',title=['82-0','VORP'],sport='NBA',accL='#d9480f',accD='#ff6b2c',menu='Draft five players from random teams and decades, then play all 82 games. Can your lineup go unbeaten?')]
if len(sys.argv)>3: extra.append(dict(id='162-0',title=['162-0','WAR'],sport='MLB',accL='#b3261e',accD='#ff7466',menu=sys.argv[3]))
extra.append(dict(id='who-am-i',title=['Who Am','I?'],sport='MLB',accL='#a3195b',accD='#ff7ab3',menu='Guess the mystery player. Every wrong guess unlocks another clue, and you get six. New player every day.'))
G=extra+G
order=['NBA','NFL','MLB'];first={'NBA':'82-0','MLB':'162-0'}
html=open('/home/claude/work/menu.html',encoding='utf-8').read()
a=html.index('  <ul class="games">');b=html.index('</main>')
sec=''
for s in order:
    gs=sorted([g for g in G if g['sport']==s],key=lambda g:(g['id']!=first.get(s),))
    sec+='  <section class="sport"><h2 class="sec">%s <span>%d game%s</span></h2>\n  <ul class="games">\n'%(s,len(gs),'' if len(gs)==1 else 's')
    for g in gs:
        sec+='    <li><a class="game" style="--cl:%s;--cd:%s" href="%s/"><span><h3>%s</h3><p>%s</p></span><span class="play" aria-hidden="true">Play →</span></a></li>\n'%(g['accL'],g['accD'],g['id'],' '.join(g['title']),g['menu'])
    sec+='  </ul></section>\n'
html=html[:a]+sec+'  <p class="note">College football and college basketball games are on the way.</p>\n'+html[b:]
css_old=html[html.index('.games{'):html.index('@media (prefers-reduced-motion')]
css_new='''.sport{display:flex;flex-direction:column;gap:10px}
.sec{font-family:var(--display);font-weight:900;font-size:30px;line-height:1;margin:0;display:flex;align-items:baseline;gap:10px;text-transform:uppercase}
.sec span{font-family:var(--body);font-size:12px;font-weight:600;letter-spacing:.09em;color:var(--muted)}
.games{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
.game{--c:var(--cl);display:grid;grid-template-columns:1fr auto;align-items:center;gap:12px;background:var(--surface);border:1px solid var(--line);border-left:6px solid var(--c);border-radius:4px;padding:12px 14px 12px 16px;color:inherit;text-decoration:none;transition:transform .2s var(--ease),border-color .2s var(--ease)}
.game:hover{transform:translateX(3px);border-color:var(--c)}
.game h3{font-family:var(--display);font-weight:900;font-size:clamp(28px,8.5cqw,38px);line-height:.95;text-transform:uppercase;margin:0 0 5px}
.game p{margin:0;font-size:14px;color:var(--muted);max-width:44ch}
.play{font-family:var(--display);font-weight:800;font-size:18px;text-transform:uppercase;letter-spacing:.04em;color:var(--c);white-space:nowrap}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .game{--c:var(--cd)}}
:root[data-theme="dark"] .game{--c:var(--cd)}
'''
html=html.replace(css_old,css_new)
html=re.sub(r'\s*--hoops:[^;]+; --turf:[^;]+;','',html)
open(dest,'w',encoding='utf-8').write(html);print('menu',len(G),'games')
