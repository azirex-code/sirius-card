"""Обложка Reels/поста в стиле Sirius по формуле RMG: кадр из видео + заголовок сверху + логотип снизу.
Запуск:  python3 make_cover.py кадр.jpg "ЗАГОЛОВОК|второе слово золотом" "подзаголовок" [1920|1350]
Пример:  python3 make_cover.py frame.jpg "FINOBOD|2026" "Технический партнёр форума · Hyatt Regency" 1920
Выход:   cover_<имя кадра>_1080x<H>.png
"""
import asyncio, re, sys, os
from playwright.async_api import async_playwright
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
def svg_body(path):
    s = open(path, encoding='utf-8').read()
    return re.search(r'viewBox="([^"]+)"', s).group(1), re.sub(r'<svg [^>]*>', '', s, count=1).replace('</svg>', '')
VB, ICON = svg_body(os.path.join(ROOT, 'icon.svg'))
WVB, WORD = svg_body(os.path.join(ROOT, 'wordmark.svg'))

def face_top(im):
    """Верх лица по цвету кожи (доля высоты); None если не найдено."""
    import numpy as np
    a = np.asarray(im.convert('RGB').resize((im.width // 4, im.height // 4))).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    skin = (r > 140) & (g > 90) & (b > 70) & (r > g) & (g > b) & ((r - b) > 25)
    rows = skin.sum(axis=1); ys = [i for i, v in enumerate(rows) if v > a.shape[1] * 0.06]
    return (ys[0] / a.shape[0]) if ys else None

def prep_frame(src, W, H, head_zone):
    """Кадр под обложку. head_zone — нижняя граница зоны заголовка (px): лицо не должно заходить выше неё."""
    im = Image.open(src).convert('RGB')
    im = ImageOps.exif_transpose(im)
    ratio = im.width / im.height
    ft = face_top(im)
    if ratio > (W / H) * 1.15:
        # кадр шире холста: целиком, на размытом фоне, сдвигаем вниз так, чтобы лицо было под заголовком
        bg = ImageOps.fit(im, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
        fg = im.resize((W, int(W / ratio)), Image.LANCZOS)
        y = int(H * 0.5 - fg.height / 2)
        if ft is not None:
            y = max(y, head_zone - int(ft * fg.height) + 10)
        y = min(y, H - fg.height - 60)
        bg.paste(fg, (0, y)); im = bg
    else:
        # кадр вертикальный: кропим так, чтобы верх лица оказался не выше head_zone
        scale = max(W / im.width, H / im.height)
        im2 = im.resize((int(im.width * scale) + 1, int(im.height * scale) + 1), Image.LANCZOS)
        face_px = int(ft * im2.height) if ft is not None else int(im2.height * 0.3)
        top = max(0, min(face_px - head_zone - 20, im2.height - H))
        left = (im2.width - W) // 2
        im = im2.crop((left, top, left + W, top + H))
    im = ImageEnhance.Color(im).enhance(0.75)
    tint = Image.new('RGB', (W, H), (11, 45, 38))
    im = Image.blend(im, tint, 0.22)
    out = os.path.join(HERE, '_frame.jpg'); im.save(out, quality=94); return out

CSS = '''@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;800&family=Golos+Text:wght@400;500&display=swap');
body{margin:0;width:%dpx;height:%dpx;overflow:hidden;position:relative;background:#0B2D26;color:#F3EFE6;font-family:Montserrat,sans-serif}
.ph{position:absolute;inset:0;background:url(_frame.jpg) center/cover}
.ov{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,45,38,.95) 0%%,rgba(11,45,38,.8) 20%%,rgba(11,45,38,.1) 34%%,rgba(11,45,38,0) 55%%,rgba(11,45,38,.35) 78%%,rgba(11,45,38,.92) 100%%)}
.head{position:absolute;left:64px;right:64px;top:%dpx;text-align:center}
.h1{font:800 %dpx/0.98 Montserrat;letter-spacing:-.02em;text-transform:uppercase;color:#F3EFE6;text-shadow:0 6px 30px rgba(0,0,0,.45)}
.h1 em{font-style:normal;color:#E8CC8C}
.h2{margin-top:22px;font:500 %dpx/1.3 "Golos Text",sans-serif;color:rgba(243,239,230,.92);text-shadow:0 2px 12px rgba(0,0,0,.5)}
.logo{position:absolute;left:0;right:0;bottom:%dpx;text-align:center}
.logo .mark{width:%dpx;height:auto;display:block;margin:0 auto 22px;filter:drop-shadow(0 6px 24px rgba(0,0,0,.6))} .logo .word{width:%dpx;height:auto;display:block;margin:0 auto 10px;filter:drop-shadow(0 4px 16px rgba(0,0,0,.6))} .logo .s{font:600 %dpx Montserrat;letter-spacing:.42em;text-indent:.42em;color:#E8CC8C}
'''
def page(W, H, h1, h2):
    tall = H > 1500
    css = CSS % (W, H, 220 if tall else 100, 116 if tall else 92, 36 if tall else 32, 440 if tall else 110, 120 if tall else 100, 320 if tall else 270, 19 if tall else 17)
    parts = h1.split('|'); title = parts[0]
    if len(parts) > 1: title += '<br><em>' + parts[1] + '</em>'
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
<div class="ph"></div><div class="ov"></div>
<div class="head"><div class="h1">{title}</div>{f'<div class="h2">{h2}</div>' if h2 else ''}</div>
<div class="logo"><svg class="mark" viewBox="{VB}">{ICON}</svg><svg class="word" viewBox="{WVB}">{WORD}</svg><div class="s">EVENT SYSTEMS</div></div>
</body></html>'''

async def main():
    if len(sys.argv) < 3:
        print(__doc__); return
    src, h1 = sys.argv[1], sys.argv[2]
    h2 = sys.argv[3] if len(sys.argv) > 3 else ''
    H = int(sys.argv[4]) if len(sys.argv) > 4 else 1920
    W = 1080
    tall = H > 1500
    prep_frame(src, W, H, head_zone=560 if tall else 440)
    html = os.path.join(HERE, '_cover.html'); open(html, 'w', encoding='utf-8').write(page(W, H, h1, h2))
    out = os.path.join(HERE, f"cover_{os.path.splitext(os.path.basename(src))[0]}_{W}x{H}.png")
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': W, 'height': H})
        await pg.goto('file://' + html, wait_until='networkidle'); await pg.wait_for_timeout(700)
        await pg.screenshot(path=out); await b.close()
    print(out)
asyncio.run(main())
