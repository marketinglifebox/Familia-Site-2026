from PIL import Image
import numpy as np, glob, sys

# --- duotone medido na foto que ja esta no circulo -------------------------
L  = np.array([  0,  60,  84, 108, 132, 156, 180, 204, 255])
R  = np.array([ 52, 114, 139, 168, 190, 209, 223, 240, 255])
G  = np.array([  1,  46,  64,  89, 113, 139, 165, 188, 237])
B  = np.array([  0,  19,  31,  52,  74, 101, 132, 165, 235])
eixo = np.arange(256)
LUT = np.stack([np.interp(eixo,L,R), np.interp(eixo,L,G), np.interp(eixo,L,B)],1)

lum_ref = np.load('/tmp/lum_ref.npy')
ref_hist,_ = np.histogram(lum_ref, bins=256, range=(0,256))
ref_cdf = np.cumsum(ref_hist)/ref_hist.sum()

def trata(img):
    a = np.asarray(img.convert('RGB')).astype(float)
    lum = 0.299*a[:,:,0]+0.587*a[:,:,1]+0.114*a[:,:,2]
    # 1) estica a faixa tonal ate a da foto de referencia, sem achatar o contraste
    lo, hi = np.percentile(lum, 2), np.percentile(lum, 98)
    t = np.clip((lum - lo) / max(hi - lo, 1e-6), 0, 1)
    t = t ** 1.15                       # segura um pouco os meios-tons
    lum2 = 46 + t * (198 - 46)          # p2..p98 da referencia
    # 1b) iguala o brilho medio ao da referencia, sem mexer no contraste
    alvo = 116.0
    g = 1.0
    for _ in range(40):
        atual = (((lum2/255.0)**g)*255).mean()
        if abs(atual-alvo) < 0.5: break
        g *= (np.log(alvo/255.0) / np.log(max(atual,1)/255.0))
        g = float(np.clip(g, 0.35, 2.5))
    lum2 = ((lum2/255.0)**g)*255
    # 2) aplica o duotone
    out = LUT[np.clip(lum2,0,255).astype(int)]
    return Image.fromarray(out.round().astype('uint8'))

def quadrado(img, fx=0.5, fy=0.5):
    w,h = img.size; s = min(w,h)
    x = int((w-s)*fx); y = int((h-s)*fy)
    return img.crop((x,y,x+s,y+s))

alvos = [
    (sorted(glob.glob('Captura*.png'))[0], 'pilar-agilidade.jpg',   0.5, 0.42),
    (sorted(glob.glob('Captura*.png'))[1], 'pilar-produto.jpg',     0.5, 0.62),
    ('atendimento.jpg',                    'pilar-atendimento.jpg', 0.5, 0.45),
]
for src, dst, fx, fy in alvos:
    im = Image.open(src)
    q  = quadrado(im, fx, fy)
    lado = max(620, min(1240, q.size[0]))
    q  = q.resize((lado,lado), Image.LANCZOS)
    trata(q).save(dst, quality=92, subsampling=0)
    print('%-24s <- %-42s  %dx%d'%(dst, src[:42], lado, lado))
