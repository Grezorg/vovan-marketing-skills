"""Create original procedural motion and portrait NASA footage; no video API."""
from pathlib import Path
import math, subprocess, json, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets'
W,H,FPS=1080,1920,30

def run(args):
    subprocess.run(args,check=True)

def earth():
    # Keep the whole central planet visible instead of cropping most of it away.
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(ASSETS/'earth.mp4'),
         '-filter_complex',
         '[0:v]fps=30,split=2[b][f];[b]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=45:3,eq=brightness=-0.35:saturation=0.8[b];[f]scale=1540:-2[f];[b][f]overlay=(W-w)/2:(H-h)/2,setsar=1[v]',
         '-map','[v]','-t','17','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-threads','3',str(ASSETS/'earth-portrait.mp4')])

def project(p,scale=570,center=(540,810)):
    p=np.asarray(p);z=p[...,2]+5
    return np.stack([center[0]+scale*p[...,0]/z,center[1]-scale*p[...,1]/z],axis=-1)

def rotate(p,a,b):
    p=np.asarray(p)
    ry=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
    rx=np.array([[1,0,0],[0,math.cos(b),-math.sin(b)],[0,math.sin(b),math.cos(b)]])
    return p@ry.T@rx.T

def base_background():
    y,x=np.mgrid[0:960,0:540]
    light=np.exp(-(((x-270)/220)**2+((y-405)/250)**2))
    a=np.stack([5+6*light,9+24*light,21+38*light],axis=-1).astype('uint8')
    return Image.fromarray(a).resize((W,H),Image.Resampling.BICUBIC)

BG=base_background()
rng=np.random.default_rng(48)
stars=np.stack([rng.uniform(40,1040,100),rng.uniform(150,1500,100),rng.uniform(.1,1,100)],axis=1)
theta=np.linspace(0,math.pi,24)
phi=np.linspace(0,2*math.pi,37)
sphere=np.array([[[math.sin(t)*math.cos(p),math.cos(t),math.sin(t)*math.sin(p)] for p in phi] for t in theta])*2.25

def frame(t):
    im=BG.copy();draw=ImageDraw.Draw(im)
    glow=Image.new('RGB',(W,H));g=ImageDraw.Draw(glow)
    for x,y,b in stars:
        yy=150+(y-150+t*8*b)%1350
        v=int(65+90*b*(.7+.3*math.sin(t*2+x)))
        draw.ellipse((x,yy,x+2,yy+2),fill=(v//2,v,v))
    shot=int(t/4.8)
    if shot==0:
        # An actual shaded 3D mesh with rotating orbital paths and satellites.
        pts=rotate(sphere.reshape(-1,3),t*.42,.22+math.sin(t*.4)*.15).reshape(sphere.shape)
        xy=project(pts,scale=650)
        faces=[]
        for i in range(23):
            for j in range(36):
                q=np.array([pts[i,j],pts[i+1,j],pts[i+1,j+1],pts[i,j+1]])
                poly=[tuple(xy[a,b]) for a,b in [(i,j),(i+1,j),(i+1,j+1),(i,j+1)]]
                normal=q.mean(axis=0);lit=max(.06,float(np.dot(normal/2.25,np.array([-.4,.5,-.76]))))
                faces.append((q[:,2].mean(),poly,(int(9+14*lit),int(25+115*lit),int(43+155*lit))))
        for _,poly,col in sorted(faces,reverse=True):
            draw.polygon(poly,fill=col)
            draw.line(poly+[poly[0]],fill=(14,69,91),width=1)
        for k in range(3):
            a=np.linspace(0,2*math.pi,150)
            ring=np.stack([2.8*np.cos(a),np.zeros_like(a),2.8*np.sin(a)],axis=-1)
            ring=rotate(ring,t*.13+k*1.5,.5+k*.72)
            path=[tuple(p) for p in project(ring,scale=650)]
            col=(45,170,205) if k!=1 else (255,161,83)
            g.line(path,fill=col,width=7);draw.line(path,fill=col,width=2)
            s=path[int((t*.16+k*.27)%1*149)]
            draw.ellipse((s[0]-6,s[1]-6,s[0]+6,s[1]+6),fill=(215,250,255))
    elif shot==1:
        # Camera flight down a luminous geometric tunnel.
        local=t-4.8
        for j in range(22,-1,-1):
            z=(j*.65-local*2.1)%14+.35
            radius=410/z
            ang=local*.16+j*.045
            path=[]
            for k in range(7):
                a=k*math.pi/3+ang
                path.append((540+radius*math.cos(a),810+radius*math.sin(a)))
            v=max(.08,1-z/16)
            col=(int(30*v),int(180*v),int(235*v)) if j%3 else (int(250*v),int(140*v),int(70*v))
            g.line(path,fill=col,width=max(2,int(8/z)))
            draw.line(path,fill=col,width=max(1,int(3/z)))
        for k in range(6):
            a=k*math.pi/3+local*.16
            draw.line((540,810,540+1700*math.cos(a),810+1700*math.sin(a)),fill=(18,57,81),width=2)
    else:
        # A travelling camera over a breathing digital landscape and energy sun.
        local=t-9.6
        for j in range(26,0,-1):
            z=.4+j*.28
            path=[]
            for k in range(-16,17):
                x=k*.22
                y=-1.4+.28*math.sin(x*1.8+z*2-local*1.8)+.18*math.cos(x*3-local)
                path.append((540+520*x/z,820-520*y/z))
            col=(18,int(80+95*(1-j/27)),int(125+110*(1-j/27)))
            draw.line(path,fill=col,width=2)
            if j%3==0:g.line(path,fill=col,width=3)
        a=np.linspace(0,2*math.pi,160)
        for r in [135,145,175]:
            path=[(540+(r+8*math.sin(v*8+local*2))*math.cos(v),660+(r+8*math.sin(v*8+local*2))*math.sin(v)) for v in a]
            g.line(path,fill=(255,120,40),width=9);draw.line(path,fill=(255,178,90),width=2)
    im=Image.blend(im,Image.blend(im,glow.filter(ImageFilter.GaussianBlur(18)),.55),.48)
    # Faint original film grain; keep the frame clean for subtitles.
    fade=min(1,t/.35,(14.8-t)/.5)
    if fade<1:im=Image.blend(Image.new('RGB',(W,H),(3,6,15)),im,max(0,fade))
    return im

def motion():
    command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-threads','3',str(ASSETS/'digital-motion.mp4')]
    p=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for i in range(444):
            p.stdin.write(frame(i/FPS).tobytes())
            if i%90==0:print('animation',i,'/ 444',flush=True)
    finally:p.stdin.close()
    if p.wait():raise RuntimeError('animation encode failed')

def music():
    sr=44100;duration=18;t=np.arange(int(sr*duration))/sr
    a=np.zeros_like(t)
    for k,f in enumerate([130.8128,164.8138,195.9977,261.6256]):
        a+=.027*np.sin(2*np.pi*f*t+0.18*np.sin(t*.6+k))
    for b in np.arange(0,duration,.625):
        u=t-b;sel=(u>=0)&(u<.28)
        a[sel]+=.17*np.sin(2*np.pi*(53*u[sel]+2.5*(1-np.exp(-u[sel]*18))))*np.exp(-u[sel]*17)
    a*=np.minimum(1,t/.7)*np.minimum(1,(duration-t)/1.5)
    stereo=np.stack([a,a*.95],axis=1)
    with wave.open(str(ASSETS/'original-music.wav'),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((stereo*32767).astype('<i2').tobytes())

if __name__=='__main__':
    earth();motion();music()
