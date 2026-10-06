from pathlib import Path
from xml.etree import ElementTree as ET
import math
import resvg_py
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

ROOT=Path(__file__).parent
TMP=ROOT/'tmp/pdfs'; OUT=ROOT/'output/pdf'; TMP.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
for name,file in [('Sans','Arial.ttf'),('Bold','Arial Bold.ttf'),('Italic','Arial Italic.ttf'),('Serif','Georgia.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/System/Library/Fonts/Supplemental/'+file))
W,H=595.28,841.89; M=42; CW=W-2*M
BG='#F7F6F1'; INK='#26343C'; MUTED='#606F77'; LIGHT='#DDE3E0'; TEAL='#277D73'; RED='#BD5949'; PURPLE='#8563AA'; GOLD='#A67834'
c=canvas.Canvas(str(OUT/'faithful-delegation.pdf'),pagesize=(W,H))
c.setTitle('Faithful delegation: Purpose, judgment, and proportionate steering')
c.setAuthor('Owen Wassmer')
c.setSubject('A conceptual synthesis of Agent Insights and a visual model of agent navigation')
style=ParagraphStyle('body',fontName='Sans',fontSize=11.2,leading=16.5,textColor=HexColor(INK),spaceAfter=10)
small=ParagraphStyle('small',parent=style,fontSize=9.1,leading=12.8,textColor=HexColor(MUTED))
lead=ParagraphStyle('lead',parent=style,fontSize=14,leading=20,textColor=HexColor(MUTED))
all_text=[]
def txt(x,y,s,size=11,color=INK,font='Sans'):
    c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(x,H-y,s);all_text.append(s)
def para(s,y,x=M,width=CW,sty=style):
    p=Paragraph(s,sty); w,h=p.wrap(width,H);p.drawOn(c,x,H-y-h);all_text.append(s)
    assert y+h<807, (s[:70],y+h)
    return y+h+11

def line(x1,y1,x2,y2,color=LIGHT,width=1,dash=None):
    c.setStrokeColor(HexColor(color));c.setLineWidth(width);c.setDash(dash or []);c.line(x1,H-y1,x2,H-y2);c.setDash([])
def circle(x,y,r,color=TEAL,fill=False):
    c.setStrokeColor(HexColor(color));c.setFillColor(HexColor(color));c.setLineWidth(1.3);c.circle(x,H-y,r,fill=int(fill),stroke=1)
def arrow(x,y,dx,dy,color=TEAL,width=1.3):
    line(x,y,x+dx,y+dy,color,width);a=math.atan2(dy,dx);L=4
    for off in [-.48,.48]:line(x+dx,y+dy,x+dx-L*math.cos(a+off),y+dy-L*math.sin(a+off),color,width)
def curve(coords,color=TEAL,width=2.5,dotted=False):
    p=c.beginPath();p.moveTo(coords[0],H-coords[1]);
    for k in range(2,len(coords),6):p.curveTo(coords[k],H-coords[k+1],coords[k+2],H-coords[k+3],coords[k+4],H-coords[k+5])
    c.setStrokeColor(HexColor(color));c.setLineWidth(width);c.setLineCap(1);c.setDash([.4,5] if dotted else []);c.drawPath(p);c.setDash([])
def box(x,y,w,h,fill='#FFFEFA',stroke=LIGHT,r=9):
    c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke));c.setLineWidth(.7);c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=1)
def start(n,label,title=None,sub=None):
    c.setFillColor(HexColor(BG));c.rect(0,0,W,H,fill=1,stroke=0)
    txt(M,28,'FAITHFUL DELEGATION',8,MUTED,'Bold');
    c.setFont('Sans',8);c.drawRightString(W-M,H-28,label.upper())
    line(M,805,W-M,805,LIGHT,.7)
    txt(M,821,'Purpose, judgment, and proportionate steering',8,MUTED)
    c.setFont('Sans',8);c.drawRightString(W-M,H-821,f'{n:02d} / 07')
    if title:txt(M,66,title,27,INK,'Bold')
    if sub:para(sub,83,sty=small)
def finish():c.showPage()
def heading(s,y):txt(M,y,s,15,INK,'Bold');return y+12

# Reuse all four exact trajectory panels from the established visual.
svg=(ROOT/'agent-journeys.svg').read_text()
for i in range(4):
    root=ET.fromstring(svg); ox=70+(i%2)*850;oy=305+(i//2)*555
    root.set('viewBox',f'{ox} {oy} 810 525');root.set('width','1620');root.set('height','1050')
    (TMP/f'panel-{i+1}.png').write_bytes(resvg_py.svg_to_bytes(svg_string=ET.tostring(root,encoding='unicode')))

start(1,'The central idea')
txt(M,89,'Faithful delegation',35,INK,'Bold')
para('Purpose, judgment, and proportionate steering',109,sty=lead)
y=para('An agent should carry a usable understanding of the work through changing circumstances. That understanding gives its decisions continuity and helps it recognize when a correction is needed.',160)
y=para('The aim is useful completion with an appropriate level of human involvement. The user contributes decisions, knowledge, and authority where they are needed. The agent manages ordinary navigation and preserves the purpose already entrusted to it.',y)
# Opening diagram: durable purpose and contextual path.
box(M,292,CW,204)
txt(M+19,318,'Stable purpose',13,INK,'Bold');txt(M+19,338,'Revisable understanding. Adaptable execution.',10,MUTED)
curve([M+25,456,M+100,465,M+130,366,M+210,401,M+285,435,M+333,363,M+445,359],TEAL,2.5,True)
curve([M+25,433,M+100,435,M+135,345,M+210,378,M+300,411,M+345,335,M+462,333],'#9DBDB4',1.2,True)
curve([M+25,479,M+110,490,M+145,391,M+210,425,M+290,458,M+350,391,M+462,387],'#9DBDB4',1.2,True)
circle(M+25,456,3,INK,True);circle(M+445,359,6,GOLD);circle(M+424,348,4,'#D5C5A3');circle(M+405,354,3,'#E2D9C6')
txt(M+330,475,'A provisional destination',9,MUTED)
y=heading('Understanding gives adaptation continuity',530)
y=para('Instructions, examples, corrections, and approvals provide evidence about the intended outcome. The agent needs to understand why that outcome matters, which commitments apply, and how much discretion it has. People may refine their priorities as the work becomes concrete.',y)
y=para('Good judgment responds to changes that affect the decision. It also preserves conclusions whose basis remains sound. Research and broader context can help the agent anticipate consequences and avoid unnecessary detours.',y)
y=para('This report develops a conceptual model of that behavior. The trajectories and directional fields illustrate relationships; they are not measurements or claims of demonstrated performance.',y,sty=small)
finish()

for page,indices,title,sub in [(2,[1,2],'When direction loses its basis','An early pattern or a fixed rule can keep steering after its relevance has faded.'),(3,[3,4],'How adaptation is guided','The quality of a turn depends on the understanding and evidence behind it.')]:
    start(page,'Four trajectories',title,sub)
    # Shared compact legend.
    xx=M+4
    for label,col,dot in [('Journey','#71828C',False),('Hindsight ideal','#C6CECF',False),('Agent path',INK,True),('Boundaries','#9AA6A9',True)]:
        line(xx,108,xx+22,108,col,2 if label=='Agent path' else 1.2,[.5,3] if dot else None)
        txt(xx+28,111,label,8,MUTED);xx+=125
    for j,idx in enumerate(indices):
        width=CW;height=width*525/810;top=124+j*(height+13)
        c.drawImage(str(TMP/f'panel-{idx}.png'),M,H-top-height,width=width,height=height)
    finish()

start(4,'A model of navigation','A field of informed direction')
y=para('Each point in a state space represents a situation: available evidence, uncertainty, commitments, possible actions, and the current understanding of the desired outcome. The agent moves through this space as it acts and learns.',91)
y=para('At a given point, a vector represents a proposed direction. Organizing understanding supplies a coherent field of directions across possible situations. The same purpose can support different actions as conditions change.',y)
box(M,245,CW,241)
txt(M+17,269,'Organizing understanding across changing states',11,INK,'Bold')
# Coherent directional field.
for row in range(5):
    for col in range(11):
        x=M+26+col*43;y0=294+row*33
        slope=-.38+.34*math.sin(col*.7+row*.16)
        arrow(x,y0,21,21*slope,'#B8CCC4',.85)
curve([M+24,443,M+100,450,M+134,351,M+220,371,M+293,391,M+350,323,M+466,306],TEAL,2.7,True)
circle(M+24,443,3,INK,True);circle(M+466,306,6,GOLD)
arrow(M+224,379,15,-18,PURPLE,1.7);txt(M+242,409,'Self-steering',9,PURPLE)
txt(M+17,472,'A two-dimensional projection of a richer work state.',8.5,MUTED)
y=heading('Read each vector in context',519)
y=para('Direction describes the next action. Strength describes how firmly the available reasons support it. Scope and persistence describe where those reasons apply and how long they remain relevant. A firm instruction can govern a single decision; an enduring principle can shape many decisions.',y)
y=para('In these illustrations, arrow length shows the size of an adjustment, and a shaded region shows its scope. The background field represents continuing guidance. Authority is expressed separately through the user’s decisions and the limits on delegated action.',y)
y=para('The destination remains provisional. Its earlier positions show how the desired outcome can evolve. The straight line in the trajectory diagrams is a hindsight reference to the destination shown. The realistic journey is a useful comparison, and its detours may include opportunities for improvement.',y)
finish()

start(5,'Proportionate change','Give each correction its scope')
y=para('A correction can change one action, supply a missing fact, establish a continuing constraint, or revise the desired outcome. The agent should identify that effect and update the parts of the work that depend on it.',91)
y=para('Taking an instruction seriously means honoring its meaning and authority at the right scope. An explicit decision within the user’s authority governs the work. Context helps determine its application and duration.',y)
# Two mini-panels showing localized and broad effects.
by=236;pw=(CW-16)/2
for j in range(2):box(M+j*(pw+16),by,pw,233)
for j,title in enumerate(['A local correction','A changed destination']):txt(M+j*(pw+16)+15,by+26,title,12,INK,'Bold')
x=M
c.setFillColor(HexColor('#EEE8F3'));c.ellipse(x+73,H-410,x+158,H-305,fill=1,stroke=0)
curve([x+17,426,x+64,423,x+74,378,x+102,371,x+153,362,x+177,344,x+224,342],TEAL,2.2,True)
arrow(x+105,377,10,-25,PURPLE,1.8)
circle(x+224,342,5,GOLD);txt(x+15,450,'Bounded effect; purpose carries forward.',8.6,MUTED)
x=M+pw+16
c.setFillColor(HexColor('#E8F0EB'));c.roundRect(x+67,H-427,pw-83,126,8,fill=1,stroke=0)
curve([x+17,426,x+65,421,x+111,382,x+216,387],'#C6CECF',1.7,True)
curve([x+17,426,x+65,421,x+95,330,x+216,315],TEAL,2.2,True)
circle(x+216,387,5,'#C6CECF');circle(x+216,315,6,GOLD);arrow(x+188,375,0,-48,GOLD,1.5)
txt(x+15,450,'A broader revision follows the decision.',8.6,MUTED)
y=heading('Learn the reason for the turn',501)
y=para('Before generalizing feedback, identify what changed. The cause may be a missing fact, a misunderstood relationship, an unclear preference, an ineffective method, or a genuine change in purpose. Each cause calls for a different response.',y)
y=para('Make the smallest correction that fully addresses the cause. Preserve the context that explains when the lesson applies. Update affected plans, dependencies, and commitments together. Existing guidance can be narrowed, replaced, or removed as understanding improves.',y)
y=para('Self-steering usually produces smaller adjustments because it happens before drift becomes large. A major discovery can still justify a substantial turn within the agent’s authority. The size of a correction should follow its consequences and scope, rather than who first noticed the problem.',y)
finish()

start(6,'Judgment through execution','Steer when the work calls for it')
y=para('Self-steering combines lightweight awareness during ordinary work with deeper reassessment at meaningful moments. Useful triggers include new evidence, an unexpected result, a major commitment, changed dependencies, or accumulating signs of drift.',91)
y=para('The depth of reassessment should reflect the uncertainty, consequence, and reversibility of the next action. Focused research can resolve uncertainty that matters to that decision. Other uncertainty can remain open while useful, authorized work continues.',y)
box(M,249,CW,149)
labels=[('Observe','Notice relevant change'),('Reassess','Apply purpose and context'),('Act','Take an authorized step'),('Verify','Check the real effect')]
for i,(a,b) in enumerate(labels):
    xx=M+18+i*126
    circle(xx+8,289,7,TEAL);txt(xx,319,a,11,INK,'Bold')
    para(b,331,x=xx,width=107,sty=small)
    if i<3:arrow(xx+25,289,77,0,'#9DBDB4',1.2)
line(M+404,376,M+27,376,'#9DBDB4',1)
arrow(M+27,376,0,-64,'#9DBDB4',1)
y=heading('Use human involvement where it contributes',433)
y=para('The user supplies preferences, consequential choices, and authority that the agent cannot legitimately supply for itself. Questions should make the unresolved decision concrete. The agent should carry forward established purpose so the user can focus on what genuinely needs their involvement.',y)
y=para('Autonomy should grow with understanding and remain within the discretion granted. User involvement can be frequent when goals are being discovered. More settled work can support longer periods of independent execution. Repeated reminders of the same basic purpose are evidence that delegation is failing.',y)
y=heading('Carry decisions into observable outcomes',y+13)
y=para('A sound recommendation must connect to action and a verified result. Preserve ongoing work through interruptions, recover without duplicating commitments, and report uncertain effects accurately. Consequential limits should be enforced in the tools and systems that perform the work.',y)
y=para('Reliable operation also needs recovery paths, feasible alternatives, and people able to intervene. Keep the connection between purpose, state, authority, action, and outcome durable as prompts, models, and other implementation choices change.',y)
finish()

start(7,'Learning and practical value','Prove the understanding in use')
y=para('Adaptation happens within the current task as facts and conditions change. Learning improves later decisions through experience. A successful adjustment is a starting point for a lesson whose value must be tested in other situations.',91)
y=heading('Look for improvement that carries forward',y+13)
y=para('A useful lesson preserves the reason an action was appropriate and the conditions under which that reason applies. Test it on fresh cases, including cases where applying it too broadly would cause harm. Explanations can help diagnose behavior; subsequent decisions show whether it improved.',y)
y=para('Evaluate complete work against outcomes that matter. Include consequential errors, rework, unnecessary intervention, recovery, operating cost, and the burden placed on people. Compare approaches with similar information, tools, and resources, and keep the evaluation fixed during each comparison.',y)
y=heading('Build understanding with the domain',y+13)
y=para('Work with people who understand the decisions and can observe their consequences. Preserve the distinctions between facts, interpretations, preferences, and commitments. Use precise calculations and enforceable controls where the meaning is exact, with informed judgment where context changes the answer.',y)
y=para('Methods for evaluation, recovery, and coordination can carry across domains. Domain assumptions and constraints need to be established again in each setting. Useful transfer should reduce the effort required to achieve dependable outcomes.',y)
y=heading('Start with useful work',y+13)
y=para('Choose a workflow with an accountable partner and observable results. Study a material correction, identify its cause, and test whether the resulting lesson improves fresh cases. Broaden the approach as repeatable value becomes visible.',y)
box(M,y+5,CW,74,fill='#EAF0EB',stroke='#EAF0EB')
para('Faithful delegation makes sound judgment more available. The agent carries purpose through changing conditions, corrects itself proportionately, and remains answerable to the people whose work it serves.',y+18,x=M+16,width=CW-32,sty=style)
y+=98
para('Source: <i>Agent Insights</i>, supplied by Owen Wassmer (agent_insights.md), and the accompanying discussion of trajectories, state space, and proportionate steering. Illustrations express a conceptual model. Prepared October 2026.',y,sty=small)
finish()
c.save()
(TMP/'report-text.txt').write_text('\n\n'.join(all_text))
print(OUT/'faithful-delegation.pdf')
