"""Обложка «как у RMG»: человек вырезается и ставится ПОВЕРХ заголовка; фон — кадр с фирменным тоном.
python3 rmg_cover.py кадр.jpg "ЗАГОЛОВОК|второе слово золотом" "подзаголовок" [1920|1350]
"""
import asyncio, re, sys, os
import numpy as np, cv2
import mediapipe as mp
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision
from playwright.async_api import async_playwright
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
MODEL=os.path.join(HERE,'selfie_segmenter.tflite')
def svg_body(p):
    s=open(p,encoding='utf-8').read(); return re.search(r'viewBox="([^"]+)"',s).group(1), re.sub(r'<svg [^>]*>','',s,count=1).replace('</svg>','')
VB,ICON=svg_body(os.path.join(ROOT,'icon.svg')); WVB,WORD=svg_body(os.path.join(ROOT,'wordmark.svg'))

def person_mask(im):
    arr=np.asarray(im.convert('RGB'))
    opts=vision.ImageSegmenterOptions(base_options=mpp.BaseOptions(model_asset_path=MODEL), output_confidence_masks=True)
    with vision.ImageSegmenter.create_from_options(opts) as seg:
        m=seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=arr)).confidence_masks[0].numpy_view()
    m=np.clip((m-0.35)/0.4,0,1)
    m=cv2.GaussianBlur((m*255).astype('uint8'),(0,0),2)
    return Image.fromarray(m,'L')

def fit_frame(im, W, H, anchor=0.5):
    """Кроп/вписывание кадра в холст; возвращает (картинка WxH, смещение по y для совпадения маски)."""
    ratio=im.width/im.height
    if ratio>(W/H)*1.15:
        target_h=int(H*0.66)
        fg=im.resize((int(target_h*ratio),target_h),Image.LANCZOS)
        x=(W-fg.width)//2; y=H-fg.height
        canvas=ImageOps.fit(im,(W,H),Image.LANCZOS).filter(ImageFilter.GaussianBlur(50))
        canvas.paste(fg,(x,y)); return canvas, ('paste',fg.size,(x,y))
    scale=max(W/im.width,H/im.height)
    im2=im.resize((int(im.width*scale)+1,int(im.height*scale)+1),Image.LANCZOS)
    left=(im2.width-W)//2; top=min(max(0,int(im2.height*anchor)-H//2), im2.height-H)
    return im2.crop((left,top,left+W,top+H)), ('crop',im2.size,(left,top))

def apply_same(mask, how, W, H):
    kind,size,off=how
    if kind=='paste':
        m=mask.resize(size,Image.LANCZOS); c=Image.new('L',(W,H),0); c.paste(m,off); return c
    m=mask.resize(size,Image.LANCZOS); return m.crop((off[0],off[1],off[0]+W,off[1]+H))

CSS='''@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;800&family=Golos+Text:wght@400;500&display=swap');
body{margin:0;width:%dpx;height:%dpx;overflow:hidden;position:relative;background:#0B2D26;color:#F3EFE6;font-family:Montserrat,sans-serif}
.bg{position:absolute;inset:0;background:url(_bg.jpg) center/cover}
.ov{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,45,38,.7) 0%%,rgba(11,45,38,.3) 45%%,rgba(11,45,38,.65) 100%%)}
.head{position:absolute;left:56px;right:56px;top:%dpx;text-align:center}
.h1{font:800 %dpx/0.95 Montserrat;letter-spacing:-.02em;text-transform:uppercase;color:#F3EFE6;text-shadow:0 8px 34px rgba(0,0,0,.45)}
.h1 em{font-style:normal;color:#E8CC8C}
.h2{margin-top:20px;font:500 %dpx/1.3 "Golos Text",sans-serif;color:rgba(243,239,230,.95);text-shadow:0 2px 12px rgba(0,0,0,.5)}
.person{position:absolute;inset:0;background:url(_person.png) center/cover}
.logo{position:absolute;left:0;right:0;bottom:%dpx;text-align:center}
.logo .mark{width:%dpx;height:auto;display:block;margin:0 auto 20px;filter:drop-shadow(0 6px 24px rgba(0,0,0,.7))} .logo .word{width:%dpx;height:auto;display:block;margin:0 auto 10px;filter:drop-shadow(0 4px 16px rgba(0,0,0,.7))} .logo .s{font:600 %dpx Montserrat;letter-spacing:.42em;text-indent:.42em;color:#E8CC8C;text-shadow:0 2px 10px rgba(0,0,0,.7)}
'''
def page(W,H,h1,h2):
    tall=H>1500
    css=CSS%(W,H, 250 if tall else 110, 140 if tall else 112, 38 if tall else 34, 430 if tall else 120, 120 if tall else 104, 320 if tall else 280, 19 if tall else 17)
    parts=h1.split('|'); title=parts[0]+('<br><em>'+parts[1]+'</em>' if len(parts)>1 else '')
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
<div class="bg"></div><div class="ov"></div>
<div class="head"><div class="h1">{title}</div>{f'<div class="h2">{h2}</div>' if h2 else ''}</div>
<div class="person"></div>
<div class="logo"><svg class="mark" viewBox="{VB}">{ICON}</svg><svg class="word" viewBox="{WVB}">{WORD}</svg><div class="s">EVENT SYSTEMS</div></div>
</body></html>'''

async def main():
    if len(sys.argv)<3: print(__doc__); return
    src,h1=sys.argv[1],sys.argv[2]; h2=sys.argv[3] if len(sys.argv)>3 else ''; H=int(sys.argv[4]) if len(sys.argv)>4 else 1920; W=1080
    im=ImageOps.exif_transpose(Image.open(src).convert('RGB'))
    mask=person_mask(im)
    bg,how=fit_frame(im,W,H)
    m=apply_same(mask,how,W,H)
    # фон: приглушить и тонировать
    bgc=ImageEnhance.Color(bg).enhance(0.5); bgc=Image.blend(bgc,Image.new('RGB',(W,H),(11,45,38)),0.5)
    bgc.save(os.path.join(HERE,'_bg.jpg'),quality=94)
    # человек: лёгкая тонировка, без размытия
    pc=ImageEnhance.Color(bg).enhance(0.85); pc=Image.blend(pc,Image.new('RGB',(W,H),(11,45,38)),0.08)
    person=pc.convert('RGBA'); person.putalpha(m); person.save(os.path.join(HERE,'_person.png'))
    html=os.path.join(HERE,'_rmg.html'); open(html,'w',encoding='utf-8').write(page(W,H,h1,h2))
    out=os.path.join(HERE,f"rmg_{os.path.splitext(os.path.basename(src))[0]}_{W}x{H}.png")
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':W,'height':H})
        await pg.goto('file://'+html,wait_until='networkidle'); await pg.wait_for_timeout(700); await pg.screenshot(path=out); await b.close()
    print(out)
asyncio.run(main())
