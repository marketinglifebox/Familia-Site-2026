# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np
from scipy import ndimage

SP='/tmp/claude-0/-home-user-Familia-Site-2026/f5a484da-fb78-5b61-8d16-a736d78a1c8f/scratchpad/'
Y0,Y1=3444,4449
a=np.asarray(Image.open(SP+'page.png').convert('RGB')).astype(int)[Y0:Y1]
H,W=a.shape[:2]
m=(np.abs(a-np.array([100,165,104])).sum(2)<90)
lab,n=ndimage.label(m,structure=np.ones((3,3)))
tam=np.array(ndimage.sum(m,lab,range(1,n+1)))
caixas=ndimage.find_objects(lab)
def bbox(k):
    s=caixas[k-1]; return s[1].start,s[1].stop,s[0].start,s[0].stop

# As fotos do documento ocupam estas faixas horizontais na altura dos cartoes;
# tudo que e "verde" dentro delas e folhagem das fotos, nao curva.
FOTOS=[(0,130),(225,575),(600,950),(1013,1320),(1410,1512)]
def dentro_de_foto(k):
    x0,x1,y0,y1=bbox(k)
    if y0<458 or y1>690: return False
    return any(x0>=f0-6 and x1<=f1+6 for f0,f1 in FOTOS)

grupos={'A':[], 'B':[], 'C':[]}
for k in range(1,n+1):
    if tam[k-1]<300 or dentro_de_foto(k): continue
    x0,x1,y0,y1=bbox(k); cx=(x0+x1)/2
    if   x1<110:        grupos['C'].append(k)   # arco da esquerda
    elif 1000<cx<1250:  grupos['A'].append(k)   # arco da direita
    elif 190<cx<800:    grupos['B'].append(k)   # diagonal longa
for g in grupos: print(g, [bbox(k) for k in grupos[g]])

def modelo(ks):
    sel=np.isin(lab,ks)
    d=[]
    for y in range(H):
        xs=np.where(sel[y])[0]
        if len(xs): d.append((y,(xs.min()+xs.max())/2.0,xs.max()-xs.min()+1))
    d=np.array(d); lg=np.percentile(d[:,2],75)
    b=d[(d[:,2]>=0.8*lg)&(d[:,2]<=1.25*lg)]
    b=b[b[:,1]>lg/2-1]                       # descarta linhas cortadas pela borda
    p=np.polyfit(b[:,0],b[:,1],2)
    for _ in range(4):
        r=np.abs(np.polyval(p,b[:,0])-b[:,1]); ok=r<max(10,2.5*np.median(r))
        if ok.all(): break
        b=b[ok]; p=np.polyfit(b[:,0],b[:,1],2)
    return p,lg,int(b[:,0].min()),int(b[:,0].max()),np.abs(np.polyval(p,b[:,0])-b[:,1])

novo=np.zeros_like(m)
for g,ks in grupos.items():
    p,lg,ya,yb,r=modelo(ks)
    # estende ate onde a curva ainda toca a tela
    while ya>0 and np.polyval(p,ya-1)+lg/2 > 0 and np.polyval(p,ya-1)-lg/2 < W: ya-=1
    while yb<H-1 and np.polyval(p,yb+1)+lg/2 > 0 and np.polyval(p,yb+1)-lg/2 < W: yb+=1
    print('%s  y %d..%d  largura %.0f  erro medio %.2f max %.2f'%(g,ya,yb,lg,r.mean(),r.max()))
    for y in range(ya,yb+1):
        c=np.polyval(p,y); xa=int(round(c-lg/2)); xb=int(round(c+lg/2))
        if xb<0 or xa>=W: continue
        novo[y,max(0,xa):min(W,xb+1)]=True

print('pixels %d -> %d'%(m.sum(),novo.sum()))
np.save('/tmp/curvas_novo.npy',novo)
Image.fromarray(np.where(novo,255,0).astype('uint8')).save('/tmp/curvas_novo.png')

# ---- gera o SVG: cada curva e uma parabola exata, sem rasterizacao ----------
def bezier(p, lg, ya, yb, desloc):
    def x(y): return np.polyval(p, y) + desloc
    def dx(y): return 2*p[0]*y + p[1]
    return (x(ya), ya), (x(ya) + dx(ya)*(yb-ya)/2.0, (ya+yb)/2.0), (x(yb), yb)

def f(v): return ('%.2f'%v).rstrip('0').rstrip('.')

caminhos=[]
for g in ('A','B','C'):
    p,lg,ya,yb,r=modelo(grupos[g])
    while ya>0 and np.polyval(p,ya-1)+lg/2 > 0 and np.polyval(p,ya-1)-lg/2 < W: ya-=1
    while yb<H-1 and np.polyval(p,yb+1)+lg/2 > 0 and np.polyval(p,yb+1)-lg/2 < W: yb+=1
    (ex0,ey0),(ec,ecy),(ex1,ey1)=bezier(p,lg,ya,yb,-lg/2.0)
    (dx0,dy0),(dc,dcy),(dx1,dy1)=bezier(p,lg,ya,yb,+lg/2.0)
    d=('M%s %s Q%s %s %s %s L%s %s Q%s %s %s %sZ'%(
        f(ex0),f(ey0), f(ec),f(ecy), f(ex1),f(ey1),
        f(dx1),f(dy1), f(dc),f(dcy), f(dx0),f(dy0)))
    caminhos.append(d)

svg=('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" fill="#64A568" '
     'shape-rendering="geometricPrecision">\n'
     '  <!-- curvas da faixa de beneficios, reconstruidas como parabolas\n'
     '       continuas: no PDF achatado elas apareciam cortadas onde as fotos\n'
     '       e os titulos passavam por cima -->\n%s\n</svg>\n')%(
     W,H,'\n'.join('  <path d="%s"/>'%d for d in caminhos))
open('/home/user/Familia-Site-2026/assets/svg/curves-benef.svg','w').write(svg)
print('svg %d bytes, %d caminhos'%(len(svg),len(caminhos)))
