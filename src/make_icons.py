import asyncio, re
from playwright.async_api import async_playwright
from PIL import Image
icon_src = open('icon.svg', encoding='utf-8').read()
VB = re.search(r'viewBox="([^"]+)"', icon_src).group(1); ICON = re.sub(r'<svg [^>]*>', '', icon_src, count=1).replace('</svg>', '')
word_src = open('wordmark.svg', encoding='utf-8').read()
WVB = re.search(r'viewBox="([^"]+)"', word_src).group(1); WORD = re.sub(r'<svg [^>]*>', '', word_src, count=1).replace('</svg>', '')
def page(body, extra=''):
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    body{{margin:0;width:1024px;height:1024px;background:linear-gradient(160deg,#17483B,#0B2D26 70%);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:100px}}
    {extra}</style></head><body>{body}</body></html>'''
BIG = page(f'<svg viewBox="{VB}" style="width:450px;height:auto">{ICON}</svg><svg viewBox="{WVB}" style="width:676px;height:auto">{WORD}</svg>')
FAV = page(f'<svg viewBox="{VB}" style="width:640px;height:auto">{ICON}</svg>', 'body{background:#0B2D26}')
async def main():
    open('icon_big.html','w',encoding='utf-8').write(BIG); open('icon_fav.html','w',encoding='utf-8').write(FAV)
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1024,'height':1024})
        await pg.goto('file:///home/claude/sirius-card/icon_big.html', wait_until='networkidle'); await pg.screenshot(path='icon_1024.png')
        await pg.goto('file:///home/claude/sirius-card/icon_fav.html', wait_until='networkidle'); await pg.screenshot(path='fav_1024.png')
        await b.close()
    big=Image.open('icon_1024.png').convert('RGB'); fav=Image.open('fav_1024.png').convert('RGB')
    big.resize((180,180),Image.LANCZOS).save('apple-touch-icon.png',optimize=True)
    big.resize((192,192),Image.LANCZOS).save('icon-192.png',optimize=True)
    big.resize((512,512),Image.LANCZOS).save('icon-512.png',optimize=True)
    fav.resize((32,32),Image.LANCZOS).save('favicon-32.png',optimize=True)
    fav.resize((64,64),Image.LANCZOS).save('favicon-64.png',optimize=True)
    print('ok')
asyncio.run(main())
