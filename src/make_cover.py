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

def prep_frame(src, W, H):
    """Кадр под обложку: кроп по центру, лёгкий зелёный тон и затемнение, чтобы текст читался."""
    im = Image.open(src).convert('RGB')
    im = ImageOps.exif_transpose(im)
    im = ImageOps.fit(im, (W, H), Image.LANCZOS, centering=(0.5, 0.45))
    im = ImageEnhance.Color(im).enhance(0.75)            # чуть приглушить цвет
    tint = Image.new('RGB', (W, H), (11, 45, 38))
    im = Image.blend(im, tint, 0.28)                     # фирменный тон
    out = os.path.join(HERE, '_frame.jpg'); im.save(out, quality=94); return out

CSS = '''@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;800&family=Golos+Text:wght@400;500&display=swap');
body{margin:0;width:%dpx;height:%dpx;overflow:hidden;position:relative;background:#0B2D26;color:#F3EFE6;font-family:Montserrat,sans-serif}
.ph{position:absolute;inset:0;background:url(_frame.jpg) center/cover}
.ov{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,45,38,.9) 0%%,rgba(11,45,38,.45) 30%%,rgba(11,45,38,0) 50%%,rgba(11,45,38,.2) 72%%,rgba(11,45,38,.88) 100%%)}
.head{position:absolute;left:64px;right:64px;top:%dpx;text-align:center}
.h1{font:800 %dpx/0.98 Montserrat;letter-spacing:-.02em;text-transform:uppercase;color:#F3EFE6;text-shadow:0 6px 30px rgba(0,0,0,.45)}
.h1 em{font-style:normal;color:#E8CC8C}
.h2{margin-top:22px;font:500 %dpx/1.3 "Golos Text",sans-serif;color:rgba(243,239,230,.92);text-shadow:0 2px 12px rgba(0,0,0,.5)}
.logo{position:absolute;left:0;right:0;bottom:%dpx;text-align:center}
.logo .mark{width:%dpx;height:auto;display:block;margin:0 auto 22px;filter:drop-shadow(0 6px 24px rgba(0,0,0,.6))} .logo .word{width:%dpx;height:auto;display:block;margin:0 auto 10px;filter:drop-shadow(0 4px 16px rgba(0,0,0,.6))} .logo .s{font:600 %dpx Montserrat;letter-spacing:.42em;text-indent:.42em;color:#E8CC8C}
'''
def page(W, H, h1, h2):
    tall = H > 1500
    css = CSS % (W, H, 260 if tall else 120, 128 if tall else 100, 38 if tall else 34, 440 if tall else 110, 120 if tall else 100, 320 if tall else 270, 19 if tall else 17)
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
    prep_frame(src, W, H)
    html = os.path.join(HERE, '_cover.html'); open(html, 'w', encoding='utf-8').write(page(W, H, h1, h2))
    out = os.path.join(HERE, f"cover_{os.path.splitext(os.path.basename(src))[0]}_{W}x{H}.png")
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': W, 'height': H})
        await pg.goto('file://' + html, wait_until='networkidle'); await pg.wait_for_timeout(700)
        await pg.screenshot(path=out); await b.close()
    print(out)
asyncio.run(main())
