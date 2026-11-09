import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for (w,h,pad,tag) in [(390,761,69,'safari_bars'),(390,700,69,'small'),(390,844,59,'standalone'),(375,667,20,'se'),(430,932,59,'promax')]:
            pg = await b.new_page(viewport={'width':w,'height':h}, device_scale_factor=3, is_mobile=True, has_touch=True)
            await pg.goto('file:///home/claude/sirius-card/hosted/index.html', wait_until='networkidle')
            await pg.add_style_tag(content=f'body{{padding-top:{8+pad}px !important}}')
            await pg.wait_for_timeout(500)
            r = await pg.evaluate('''() => {
              const bs=[...document.querySelectorAll('.g b')];
              const bad=bs.filter(e=>e.scrollWidth>e.clientWidth+0.5).map(e=>e.textContent);
              const lines=bs.map(e=>{const r=document.createRange();r.selectNodeContents(e);return Math.round(r.getBoundingClientRect().height/(parseFloat(getComputedStyle(e).fontSize)*1.2))});
              const sm=[...document.querySelectorAll('.g small, .hero .tag, .hero .geo')].filter(e=>e.scrollWidth>e.clientWidth+0.5).map(e=>e.textContent);
              return {scroll:document.documentElement.scrollHeight, inner:innerHeight, bad, sm, maxLines:Math.max(...lines)};
            }''')
            print(tag, w, h, r)
            await pg.screenshot(path=f'shot_{tag}.png')
            await pg.close()
        await b.close()
asyncio.run(main())
