#!/usr/bin/env python3
"""Miniature v3 1080x1920. Usage : thumb.py <clip.mp4> <t_sec> <ligne_rose> <ligne2> <ligne3> <out.jpg>"""
import sys,subprocess
from PIL import Image,ImageDraw,ImageFont,ImageFilter
clip,t,l1,l2,l3,out=sys.argv[1:7]
subprocess.run(["ffmpeg","-y","-v","error","-ss",t,"-i",clip,"-frames:v","1","/tmp/_f.png"],check=True)
im=Image.open("/tmp/_f.png").convert("RGB"); W,H=1080,1920
s=max(W/im.width,H/im.height); im=im.resize((int(im.width*s),int(im.height*s)))
im=im.crop(((im.width-W)//2,(im.height-H)//2,(im.width-W)//2+W,(im.height-H)//2+H))
g=Image.new("L",(1,H)); [g.putpixel((0,y),int(200*max(0,(y-H*0.45)/(H*0.55)))) for y in range(H)]
im.paste(Image.new("RGB",(W,H),(0,0,0)),(0,0),g.resize((W,H)))
import os; F=os.path.expanduser("~/gta/fonts/Montserrat-Black.ttf")
def fit(txt,maxs):
    s=maxs
    while ImageFont.truetype(F,s).getlength(txt)>W-100: s-=4
    return ImageFont.truetype(F,s)
y=1180
f1=fit(l1.upper(),150); glow=Image.new("RGBA",(W,H)); gd=ImageDraw.Draw(glow)
w=f1.getlength(l1.upper()); gd.text(((W-w)/2,y),l1.upper(),font=f1,fill=(255,79,163,255))
im=im.convert("RGBA"); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(22))); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8)))
d=ImageDraw.Draw(im); d.text(((W-w)/2,y),l1.upper(),font=f1,fill=(255,79,163),stroke_width=4,stroke_fill=(60,0,30))
y+=f1.size+40
for l in (l2,l3):
    f=fit(l.upper(),110); w=f.getlength(l.upper()); d.text(((W-w)/2,y),l.upper(),font=f,fill="white",stroke_width=8,stroke_fill="black"); y+=f.size+25
im.convert("RGB").save(out,quality=92); print("miniature",out)
