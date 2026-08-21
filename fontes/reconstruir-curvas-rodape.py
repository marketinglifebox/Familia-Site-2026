# -*- coding: utf-8 -*-
"""Reconstroi as curvas verdes do rodape.

Mesmo problema da faixa de beneficios: o SVG foi tracado sobre o PDF ja
achatado, entao o logo, o botao "TRABALHE CONOSCO" e a linha de credito
deixaram buracos gravados dentro do desenho. Aqui as curvas sao remontadas
como conicas continuas.

As curvas do rodape descrevem um "U" deitado, entao nao dao para escrever
como x(y): a linha de centro e ajustada por uma conica geral e depois
percorrida passo a passo (marcha com correcao de Newton), o que funciona em
qualquer inclinacao.
"""
from PIL import Image
import numpy as np
from scipy import ndimage

SP='/tmp/claude-0/-home-user-Familia-Site-2026/f5a484da-fb78-5b61-8d16-a736d78a1c8f/scratchpad/'
Y0,Y1=5008,5577
DEST='/home/user/Familia-Site-2026/assets/svg/curves-footer.svg'

a=np.asarray(Image.open(SP+'page.png').convert('RGB')).astype(int)[Y0:Y1]
H,W=a.shape[:2]
m=(np.abs(a-np.array([100,165,104])).sum(2)<90)
lab,n=ndimage.label(m,structure=np.ones((3,3)))
tam=np.array(ndimage.sum(m,lab,range(1,n+1)))
caixas=ndimage.find_objects(lab)
def bbox(k):
    s=caixas[k-1]; return s[1].start,s[1].stop,s[0].start,s[0].stop

# --- agrupamento -------------------------------------------------------------
# U: desce pela esquerda, varre o fundo e sobe ate a direita
# R: risco longo que desce do alto da direita ate o pe da pagina
GRUPOS={'U':[], 'R':[]}
sobra=[]
for k in range(1,n+1):
    if tam[k-1]<300: continue
    x0,x1,y0,y1=bbox(k); cx=(x0+x1)/2; cy=(y0+y1)/2
    if   x1<420 or (x0>360 and x1<1010 and cy<260): GRUPOS['U'].append(k)
    elif x0>800 and x1<1110:                        GRUPOS['R'].append(k)
    else:                                           sobra.append(k)
for g in GRUPOS: print(g,[bbox(k) for k in GRUPOS[g]])
print('fora dos grupos:',[bbox(k) for k in sobra])

def espinha(ks):
    """linha de centro pela transformada de distancia: vale para qualquer
       inclinacao, ao contrario do ponto medio linha a linha"""
    sel=np.isin(lab,ks)
    dt=ndimage.distance_transform_edt(sel)
    meia=np.percentile(dt[sel],99.0)
    pontos=np.argwhere(dt>=meia-1.2)
    return pontos[:,::-1].astype(float), 2*meia    # (x,y), largura

# --- conica geral ------------------------------------------------------------
def conica(P):
    mu=P.mean(0); sd=P.std(0).mean()
    q=(P-mu)/sd
    x,y=q[:,0],q[:,1]
    D=np.stack([x*x,x*y,y*y,x,y,np.ones_like(x)],1)
    p=np.linalg.svd(D,full_matrices=False)[2][-1]
    return p,mu,sd

def marcha(p,mu,sd,semente,passo=1.0,limite=12000):
    """percorre a conica a partir da semente, nos dois sentidos"""
    A,B,C,Dd,E,F=p
    def f(q):   return A*q[0]**2+B*q[0]*q[1]+C*q[1]**2+Dd*q[0]+E*q[1]+F
    def g(q):   return np.array([2*A*q[0]+B*q[1]+Dd, B*q[0]+2*C*q[1]+E])
    def corrige(q):
        for _ in range(4):
            gr=g(q); n2=gr@gr
            if n2<1e-12: break
            q=q-f(q)/n2*gr
        return q
    def ramo(sentido):
        q=corrige(((semente-mu)/sd).copy()); pts=[]
        h=passo/sd
        for _ in range(limite):
            gr=g(q); nm=np.hypot(*gr)
            if nm<1e-9: break
            t=np.array([-gr[1],gr[0]])/nm
            q=corrige(q+sentido*h*t)
            real=q*sd+mu
            if not(-60<real[0]<W+60 and -60<real[1]<H+60): break
            pts.append(real.copy())
        return pts
    tras=ramo(-1)[::-1]
    return np.array(tras+[semente]+ramo(+1))

def largura(P,p,mu,sd):
    A,B,C,Dd,E,F=p
    q=(P-mu)/sd; x,y=q[:,0],q[:,1]
    val=A*x*x+B*x*y+C*y*y+Dd*x+E*y+F
    gx=2*A*x+B*y+Dd; gy=B*x+2*C*y+E
    d=np.abs(val)/np.hypot(gx,gy)*sd
    return 4*d.mean()

def vertical(ks, grau=4):
    """riscos quase verticais: x(y) medido linha a linha (o ponto medio da
       mancha vale ate a ultima linha, ao contrario da espinha, que encolhe
       meia largura em cada ponta)"""
    sel=np.isin(lab,ks); d=[]
    for y in range(H):
        xs=np.where(sel[y])[0]
        if len(xs): d.append((y,(xs.min()+xs.max())/2.0,xs.max()-xs.min()+1))
    d=np.array(d); lg=np.percentile(d[:,2],75)
    b=d[(d[:,2]>=0.8*lg)&(d[:,2]<=1.25*lg)]
    p=np.polyfit(b[:,0],b[:,1],grau)
    r=np.abs(np.polyval(p,b[:,0])-b[:,1])
    ya,yb=int(b[:,0].min()),int(b[:,0].max())
    ys=np.arange(ya-FOLGA,yb+FOLGA+1,dtype=float)
    print('  x(y) grau %d: erro medio %.2f px, maximo %.2f'%(grau,r.mean(),r.max()))
    return np.stack([np.polyval(p,ys),ys],1), lg

def parabola(ks, C, lg):
    """para os riscos quase verticais, x(y) e uma parabola - mais estavel
       que a conica geral, que degenera quando a curva e quase reta"""
    b=np.stack([C[:,1],C[:,0]],1)          # (y, x)
    p=np.polyfit(b[:,0],b[:,1],2)
    for _ in range(4):
        r=np.abs(np.polyval(p,b[:,0])-b[:,1]); ok=r<max(10,2.5*np.median(r))
        if ok.all(): break
        b=b[ok]; p=np.polyfit(b[:,0],b[:,1],2)
    ya,yb=int(b[:,0].min()),int(b[:,0].max())
    ys=np.arange(ya,yb+1,dtype=float)
    linha=np.stack([np.polyval(p,ys),ys],1)
    print('  ajuste x(y): erro medio %.2f px, maximo %.2f'%(
        np.abs(np.polyval(p,b[:,0])-b[:,1]).mean(),
        np.abs(np.polyval(p,b[:,0])-b[:,1]).max()))
    return linha,lg

FOLGA=12        # px de folga alem da ponta, para a moldura cortar
VERTICAIS={'R'}   # riscos quase verticais: x(y) e mais estavel que a conica

caminhos=[]
for g,ks in GRUPOS.items():
    print(g)
    if g in VERTICAIS:
        linha,lg=vertical(ks)
    else:
        C,lg=espinha(ks)
        p,mu,sd=conica(C)
        linha=marcha(p,mu,sd,C.mean(0))
        # recorta ao trecho que o documento mostra - os vaos internos ficam.
        # O corte usa a mancha inteira, nao a espinha: a espinha encolhe meia
        # largura em cada ponta, e era isso que abria a fresta sob a faixa
        # laranja. Depois sobra uma folga, para a moldura fazer o corte.
        from scipy.spatial import cKDTree
        arv=cKDTree(linha)
        ys,xs=np.where(np.isin(lab,ks))
        _,imk=arv.query(np.stack([xs,ys],1).astype(float))
        ia=max(0,imk.min()-FOLGA); ib=min(len(linha)-1,imk.max()+FOLGA)
        linha=linha[ia:ib+1]
        dist,_=arv.query(C)
        print('  conica: largura %.1f, ajuste a espinha: medio %.2f px, p99 %.2f'%(
            lg,dist.mean(),np.percentile(dist,99)))
    passo=max(1,len(linha)//130)
    c=linha[::passo]
    if not np.allclose(c[-1],linha[-1]): c=np.vstack([c,linha[-1]])
    tg=np.gradient(c,axis=0); tg/=np.linalg.norm(tg,axis=1,keepdims=True)
    nrm=np.stack([-tg[:,1],tg[:,0]],1)
    esq=c+nrm*lg/2; dir=c-nrm*lg/2
    def pt(q): return '%.1f %.1f'%(q[0],q[1])
    d=('M'+pt(esq[0])+' '+' '.join('L'+pt(q) for q in esq[1:])+
       ' L'+pt(dir[-1])+' '+' '.join('L'+pt(q) for q in dir[-2::-1])+'Z')
    caminhos.append(d)

# --- os fragmentos que nao formam curva continuam como estao -----------------
if sobra:
    import subprocess,re
    from PIL import ImageFilter
    mk=np.isin(lab,sobra)
    im=Image.fromarray(np.where(mk,0,255).astype('uint8')).convert('1')
    up=6
    big=im.resize((W*up,H*up),Image.BICUBIC).point(lambda v:0 if v<128 else 255).convert('1')
    big.save('/tmp/_f.pbm')
    subprocess.run(['potrace','/tmp/_f.pbm','-s','-o','/tmp/_f.svg','-t','3','-a','1.34'],check=True)
    svg=open('/tmp/_f.svg').read()
    gt=re.search(r'<g transform="([^"]+)"',svg).group(1)
    vw,vh=[float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"',svg).groups()]
    ds=re.findall(r'\sd="([^"]+)"',svg)
    # o potrace traz o proprio viewBox; um envoltorio leva do sistema dele
    # para o desta figura
    extra=('<g transform="scale(%.6f,%.6f)"><g transform="%s">%s</g></g>'
           %(W/vw,H/vh,gt,''.join('<path d="%s"/>'%d for d in ds)))
else:
    extra=''

svg=('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" fill="#64A568" '
     'shape-rendering="geometricPrecision">\n'
     '  <!-- curvas do rodape, reconstruidas como conicas continuas: no PDF\n'
     '       achatado elas apareciam cortadas onde o logo, o botao e a linha\n'
     '       de credito passavam por cima -->\n%s\n%s</svg>\n')%(
     W,H,'\n'.join('  <path d="%s"/>'%d for d in caminhos),
     ('  '+extra+'\n') if extra else '')
open(DEST,'w').write(svg)
print('svg %.1f kB, %d curvas'%(len(svg)/1024,len(caminhos)))
