import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':390,'height':761}, device_scale_factor=3, is_mobile=True, has_touch=True)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto('file:///home/claude/sirius-card/hosted/index.html', wait_until='networkidle')
        await pg.add_style_tag(content='body{padding-top:67px !important}')
        geo = await pg.evaluate("(e=>({w:e.scrollWidth,c:e.clientWidth}))(document.querySelector('.hero .geo'))")
        await pg.screenshot(path='shot_geo.png')
        await pg.tap('.g:nth-child(4)'); await pg.wait_for_timeout(500)
        st = await pg.evaluate("({open:document.body.classList.contains('open'),t:document.getElementById('sh-t').textContent,d:document.getElementById('sh-d').textContent,h:document.getElementById('sheet').getBoundingClientRect().height})")
        await pg.screenshot(path='shot_sheet.png')
        await pg.tap('#dim'); await pg.wait_for_timeout(400)
        closed = await pg.evaluate("!document.body.classList.contains('open')")
        await pg.tap('.g:nth-child(9)'); await pg.wait_for_timeout(400)
        st2 = await pg.evaluate("({t:document.getElementById('sh-t').textContent,b:document.getElementById('sh-b').className})")
        print('geo',geo); print('open',st); print('closed',closed); print('second',st2); print('errors',errs)
        await b.close()
asyncio.run(main())
