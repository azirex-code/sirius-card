import re, subprocess, sys, io
from PIL import Image
def crop(src, dst, pad=0.0):
    s = open(src, encoding='utf-8').read()
    fills = dict(re.findall(r'\.(st\d)\{fill:(#[0-9A-Fa-f]{6});\}', s))
    body = s[s.index('<rect'):]            # after style block
    body = re.sub(r'<rect[^>]*/>\s*', '', body, count=1)   # drop background rect
    body = body[:body.rindex('</svg>')]
    # inline fills
    body = re.sub(r'class="(st\d)"', lambda m: f'fill="{fills[m.group(1)]}"', body)
    body = re.sub(r'\s+', ' ', body).strip()
    tmp = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">{body}</svg>'
    open('/tmp/_t.svg','w').write(tmp)
    png = subprocess.run(['rsvg-convert','-w','4000','-h','4000','/tmp/_t.svg'], capture_output=True, check=True).stdout
    im = Image.open(io.BytesIO(png)); bb = im.getbbox()  # non-transparent bbox
    sc = 1000/4000
    x0,y0,x1,y1 = [v*sc for v in bb]
    w,h = x1-x0, y1-y0
    x0-=w*pad; y0-=h*pad; w*=1+2*pad; h*=1+2*pad
    vb = f'{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}'
    out = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="Sirius">{body}</svg>'
    open(dst,'w',encoding='utf-8').write(out)
    print(dst, 'viewBox', vb, 'bytes', len(out))
crop('Vector_Sirius/Sirius_icon_only/Sirius_icon_only_dark_background.svg','/home/claude/sirius-card/icon.svg')
crop('Vector_Sirius/Sirius_font_only/Sirius_font_only_dark_background.svg','/home/claude/sirius-card/wordmark.svg')
crop('Vector_Sirius/Sirius_horizontal_logo/Sirius_horizontal_dark_background.svg','/home/claude/sirius-card/horizontal.svg')
