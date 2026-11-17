from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs'
W,H=1800,1120
can=Image.new('RGB',(W,H),'white');D=ImageDraw.Draw(can)
try:
 title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',32)
 normal=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
 small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
except: title=normal=small=ImageFont.load_default()
D.text((32,10),'S1–S6: alternate layouts in the same 6 × 6 m Window C',font=title,fill='#244e45')
D.text((32,59),'Each panel shows one separate 2 × 1 m seat. OSM east boundary = location anchor; pedestrian flow remains unverified.',font=normal,fill='#825f3e')
colors={'corridor':'#b7cec6','comfort':'#e2d2a1','seat':'#236456','edge':'#ae6953'}
marginX=40; top=116; panelW=565; panelH=470; padX=50;padY=44
for i,(name,dist,parallel) in enumerate([('S1',2.2,True),('S2',2.2,False),('S3',3.2,True),('S4',3.2,False),('S5',4.3,True),('S6',4.3,False)]):
 col=i%3;row=i//3;x0=marginX+col*590;y0=top+row*480
 D.rounded_rectangle((x0,y0,x0+panelW,y0+panelH),radius=14,fill='#f6f9f7',outline='#bbcbc3',width=2)
 D.text((x0+22,y0+12),f'{name}  ·  '+['Near','Near','Centre','Centre','Far','Far'][i]+'  ·  '+('parallel' if parallel else 'perpendicular'),font=normal,fill='#244e45')
 edgeX=x0+72; edgeY=y0+76;sz=51
 # C at map coordinate u 0..6, v 0..6, u to right (inward), v down
 D.rectangle((edgeX,edgeY,edgeX+6*sz,edgeY+6*sz),fill='#eff5ef',outline='#236456',width=3)
 D.rectangle((edgeX,edgeY,edgeX+1*sz,edgeY+6*sz),fill=colors['corridor'])
 D.rectangle((edgeX+1.3*sz,edgeY,edgeX+2.5*sz,edgeY+6*sz),fill=colors['comfort'])
 for u in [1,1.3,2.5]:
  xx=round(edgeX+u*sz)
  D.line((xx,edgeY,xx,edgeY+6*sz),fill='#ae6953' if u!=1 else '#266454',width=2)
 uc=dist; vc=3.0
 if parallel: u_rad=.5;v_rad=1.0
 else: u_rad=1.0;v_rad=.5
 rect=(round(edgeX+(uc-u_rad)*sz),round(edgeY+(vc-v_rad)*sz),round(edgeX+(uc+u_rad)*sz),round(edgeY+(vc+v_rad)*sz))
 D.rectangle(rect,fill=colors['seat'] if i==0 else '#fffefa',outline='#236456',width=3)
 labelB=D.textbbox((0,0),name,font=normal)
 D.text(((rect[0]+rect[2]-(labelB[2]-labelB[0]))/2,(rect[1]+rect[3]-(labelB[3]-labelB[1]))/2),name,font=normal,fill='white' if i==0 else '#26493f')
 D.text((edgeX,edgeY+6*sz+7),'0 m',font=small,fill='#5a706a')
 D.text((edgeX+6*sz-40,edgeY+6*sz+7),'6 m',font=small,fill='#5a706a')
 D.text((x0+22,y0+panelH-31),'Sourced boundary geometry · assumed seats and bands',font=small,fill='#a26443')
D.text((36,H-32),'EXPLORATORY GEOMETRIC PROXY · NOT OBSERVED PEDESTRIAN FLOW · NOT VALIDATED COMFORT',font=small,fill='#a26443')
can.save(OUT/'a3_six_variant_plans.png')
print(OUT/'a3_six_variant_plans.png')
