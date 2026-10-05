# Copy part-2 CSS + sections from part2.html into general-talk.html (in place, part-1 untouched).
G='/mnt/project-files/general-talk/general-talk.html'
g=open(G).read(); p=open('/mnt/project-files/general-talk/part2.html').read()
cs='/* =====================================================================\n   PART 2'
ce='/* ---------- sidebar + controls ---------- */'
assert g.count(cs)==1 and p.count(cs)==1
gs=g.index(cs); ge=g.index(ce,gs); ps=p.index(cs); pe=p.index(ce,ps)
g=g[:gs]+p[ps:pe]+g[ge:]
def span(s):
    a=s.index('data-name="CEO-Bench title"'); a=s.rindex('<section',0,a); a=s.rindex('\n',0,a)+1
    prev=s.rindex('\n',0,a-1)+1
    if s[prev:a].strip().startswith('<!--'): a=prev
    b=s.index('data-name="Leaderboard"'); b=s.index('</section>',b)+len('</section>')
    return a,b
ga,gb=span(g); pa,pb=span(p)
g=g[:ga]+p[pa:pb]+g[gb:]
open(G,'w').write(g); print('merged', len(g))
