from pathlib import Path
from html import escape

OUT = Path(__file__).parent
parts = []
def add(s): parts.append(s)
def text(x,y,s,size=20,color='#233039',weight=400):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(s)}</text>')
def path(d,color,width=3,dotted=False,opacity=1):
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"'+(' stroke-dasharray="1 10"' if dotted else '')+'/>')
def circle(x,y,r,color,fill='none',width=2):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" stroke="{color}" fill="{fill}" stroke-width="{width}"/>')
INK='#243039'; MUTED='#63717a'; REF='#71828c'; IDEAL='#c6cecf'; GOLD='#b39a66'
COLORS=['#bd5949','#a67834','#8563aa','#267e74']
reality='M45 270 C100 274 125 300 173 246 S230 160 282 184 S330 252 378 177 S440 123 480 141 S534 75 575 100 S628 87 665 65'
add('<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1510" viewBox="0 0 1800 1510" role="img" aria-labelledby="title desc">')
add('<title id="title">What steers an agent?</title><desc id="desc">Four conceptual diagrams compare precedent lock-in, rigid guardrails, reactive overcorrection, and principled adaptation. Each uses the same realistic journey, hindsight straight line, and provisional destination. All agent paths and boundaries are dotted.</desc>')
add('<rect width="1800" height="1510" fill="#f6f5f0"/><g font-family="Helvetica Neue,Arial,sans-serif">')
text(70,65,'FAITHFUL DELEGATION  /  A VISUAL MODEL',17,MUTED,600)
text(70,129,'What steers an agent?',55,INK,600)
text(70,174,'Stable purpose. Revisable understanding. Adaptable execution.',27,MUTED)
path('M70 222 L125 222',REF,3); text(140,229,'Realistic journey',19)
path('M355 222 L410 222',IDEAL,2); text(425,229,'Hindsight ideal',19)
path('M630 222 L685 222',INK,4,True); text(700,229,'Agent path',19)
path('M875 222 L930 222',INK,2,True,.55); text(945,229,'Agent boundaries',19)
circle(1195,222,8,GOLD);text(1215,229,'Provisional destination',19)
text(70,272,'Same starting point and reference journey in every panel. Space represents possible work states, not a measured time series.',18,MUTED)

titles=['Precedent lock-in','Rigid guardrails','Reactive overcorrection','Principled adaptation']
subs=['The first direction becomes the whole strategy.','The rules become the steering mechanism.','Each correction rewrites the local rulebook.','Purpose and context guide the next decision.']
captions=[
 ['An early pattern is extrapolated after its relevance fades.', 'No boundary interrupts the drift.'],
 ['The agent complies with a corridor aimed at the wrong outcome.', 'Every turn is a collision with “always” or “never.”'],
 ['Local feedback swings both behavior and its boundaries.', 'The response reverses direction instead of correcting proportionally.'],
 ['Research and judgment avoid some of the reference journey’s detours.', 'Boundaries catch exceptions; they rarely dictate the route.']
]
for i in range(4):
    ox=70+(i%2)*850; oy=305+(i//2)*555; c=COLORS[i]
    add(f'<g transform="translate({ox} {oy})">')
    add('<rect width="810" height="525" rx="16" fill="#fffefa" stroke="#e0e3df"/>')
    text(27,44,f'0{i+1}',21,c,600);text(76,45,titles[i],29,INK,600)
    text(27,79,subs[i],19,MUTED)
    add('<g transform="translate(30 113)">')
    path('M45 270 L665 65',IDEAL,2)
    path(reality,REF,3)
    # Earlier destination estimates: hollow, increasingly legible, linked in order.
    path('M603 27 Q635 18 651 35 Q677 37 665 65',GOLD,1.3,False,.45)
    circle(603,27,6,'#e0d8c4');circle(651,35,6,'#cbbd9b');circle(665,65,9,GOLD)
    if i==0:
        path('M45 270 L700 320',c,4.5,True)
        circle(700,320,5,c,c)
        text(365,289,'Early precedent → persistent drift',17,c)
        text(547,10,'Destination evolves',15,MUTED)
    elif i==1:
        path('M45 245 L705 135',c,2.4,True,.6)
        path('M45 300 L705 234',c,2.4,True,.6)
        path('M45 270 L115 233.33 L210 283.5 L310 200.83 L410 263.5 L510 167.5 L610 243.5 L705 178',c,4.5,True)
        circle(705,178,5,c,c)
        text(493,286,'Bounded, but misdirected',17,c)
    elif i==2:
        # The corridor bends and changes width at feedback events; it stays around the path.
        upper=[(45,240),(140,246),(245,112),(340,202),(438,69),(535,153),(630,35),(704,105)]
        lower=[(45,299),(140,310),(245,173),(340,287),(438,151),(535,218),(630,111),(704,193)]
        def poly(points): return 'M'+' L'.join(f'{x} {y}' for x,y in points)
        path(poly(upper),c,2.4,True,.6);path(poly(lower),c,2.4,True,.6)
        route=[(45,270),(140,305),(245,112),(340,285),(438,69),(535,217),(630,35),(704,159)]
        path(poly(route),c,4.5,True);circle(704,159,5,c,c)
        for x,y,label,tx,ty in [(245,112,'“Never do that”',153,61),(340,285,'“Do the opposite”',294,312)]:
            circle(x,y,9,c)
            path(f'M{x} {y-12 if ty<y else y+12} L{x} {ty+8 if ty<y else ty-21}',c,1,False,.5)
            text(tx,ty,label,17,c)
    else:
        path('M45 232 C150 228 178 126 275 137 S355 134 402 94 S484 72 538 55 S621 13 704 30',c,2.4,True,.6)
        path('M45 310 C144 318 198 227 270 241 S364 246 409 199 S478 161 539 150 S624 112 704 106',c,2.4,True,.6)
        path('M45 270 C122 286 171 180 258 188 S348 205 402 156 S480 128 536 112 S621 83 665 65',c,4.5,True)
        text(370,284,'Anticipate • contextualize • adjust',17,c)
        text(370,311,'Guardrails remain a second defense.',16,MUTED)
    circle(45,270,5,INK,INK)
    text(13,327,'Start',15,MUTED)
    add('</g>')
    # Captions sit below the plotting area; panel 1 drift needs a taller graph margin.
    add('</g>')

# Dedicated caption strips keep interpretation separate from trajectory marks.
for i in range(4):
    ox=70+(i%2)*850; oy=305+(i//2)*555
    # Place captions near the lower edge, with an opaque backdrop over unused graph space.
    add(f'<rect x="{ox+22}" y="{oy+445}" width="766" height="67" rx="6" fill="#fffefa"/>')
    for j,line in enumerate(captions[i]):text(ox+27,oy+468+j*25,line,18,MUTED)
text(70,1431,'The aim: sound judgment that reduces the need for intervention.',30,INK,500)
text(70,1471,'Conceptual, not empirical. The straight line is a hindsight reference; fewer turns alone do not prove better decisions.',18,MUTED)
add('</g></svg>')
(OUT/'agent-journeys.svg').write_text('\n'.join(parts))
print(OUT/'agent-journeys.svg')
