"""Сборка визитки Sirius — композиция D: логотип, услуги открытой сеткой (крупные значки и названия), золотая кнопка."""
import re, math, hashlib, os

import sys
PERSON = sys.argv[1] if len(sys.argv) > 1 else "farhod"   # farhod | aziz
PEOPLE = {
    "farhod": {"telegram": "faribabu", "vcf": "sirius.vcf"},
}
P = PEOPLE[PERSON]
TELEGRAM = P["telegram"]
SITE = "https://azirex-code.github.io/sirius-card/"
PAGE_URL = SITE + PERSON + "/"
A = "../"   # общие ресурсы (иконки, манифест, og.png) лежат в корне
INSTAGRAM_URL = "https://www.instagram.com/"   # ник компании ещё не получен

icon_src = open('icon.svg', encoding='utf-8').read()
VB = re.search(r'viewBox="([^"]+)"', icon_src).group(1)
ICON = re.sub(r'<svg [^>]*>', '', icon_src, count=1).replace('</svg>', '')
word_src = open('wordmark.svg', encoding='utf-8').read()
WVB = re.search(r'viewBox="([^"]+)"', word_src).group(1)
WORD = re.sub(r'<svg [^>]*>', '', word_src, count=1).replace('</svg>', '')

old = open('index.template.html', encoding='utf-8').read()
icons = {t: svg for svg, t in re.findall(r'<li>\s*(<svg.*?</svg>)\s*<div><h3>(.*?)</h3>', old, flags=re.S)}
descs = {t: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', d)).strip() for t, d in re.findall(r'<h3>(.*?)</h3>\s*(.*?)</div>', old, flags=re.S)}
import json
A_ = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
icons['Телевизоры-суфлёры'] = A_ + '<path d="M5 6.5 19 4.5v9L5 15.5z"/><path d="M8.5 9.2l7-1M8.5 12l4.5-.65"/><path d="M12 15.5v3.5M8.5 19h7"/></svg>'   # наклонный напольный монитор
icons['Сцены и подиумы'] = A_ + '<rect x="3" y="14" width="18" height="4" rx="1"/><path d="M12 14V8"/><rect x="10.4" y="3" width="3.2" height="5" rx="1.6"/><path d="M9 7.5a3 3 0 0 0 6 0"/></svg>'   # настил сцены и микрофон

services = [
 ('Синхронный перевод', 'Синхронный перевод', 'Bosch Integrus', False),
 ('Переводчики-синхронисты', 'Переводчики-синхронисты', 'UZ · RU · EN · TR · ZH', False),
 ('Звуковое оборудование', 'Звуковое оборудование', 'Yamaha', False),
 ('Световое оборудование', 'Световое оборудование', 'Anzhee', False),
 ('LED-экраны', 'Светодиодные экраны', 'Unilumin', False),
 ('Телевизоры-суфлёры', 'Мониторы для спикеров', 'Экран спикера', True),
 ('Интерактивные панели', 'Интерактивные панели', 'Сенсорный экран', True),
 ('Видеоконференцсвязь', 'Zoom-конференции', 'Видеоконференцсвязь', False),
 ('Сцены и подиумы', 'Сцены и подиумы', 'Модульные', True),
]
grid = '\n'.join(
    '    <button class="g" type="button">' + icons[k].replace('<svg ', '<svg aria-hidden="true" ', 1) +
    f'<b>{t}</b></button>'
    for k, t, c, cyr in services)
SHEET_DATA = json.dumps([{'t': t.replace('\u00ad', ''), 'b': c, 'cyr': cyr, 'd': descs[k]} for k, t, c, cyr in services], ensure_ascii=False)

# золотая волна: огибающая Гаусса, затухание к краям
pts = []
for x in range(0, 391, 5):
    env = math.exp(-((x - 195) / 110) ** 2)
    y = 110 + (math.sin(x / 9) * 26 + math.sin(x / 4.3) * 12) * env
    pts.append(f'{x},{y:.1f}')
WAVE = ' '.join(pts)

save_ic = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="10" cy="8" r="3.5"/><path d="M3.5 20c.5-3.6 3-5.6 6.5-5.6 1.2 0 2.3.2 3.2.7"/><path d="M18.5 14v6M15.5 17h6"/></svg>'
tg_ic = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 4.5 3.6 11.2c-.9.4-.9 1.1 0 1.4l4.4 1.4 1.7 5.2c.2.6.8.7 1.2.3l2.4-2.3 4.6 3.4c.7.4 1.3.1 1.5-.8L21 4.5z"/><path d="M8 14l9.5-7.5"/></svg>'
ig_ic = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r=".9" fill="currentColor" stroke="none"/></svg>'

VCARD_V = hashlib.sha1(open(P['vcf'], 'rb').read()).hexdigest()[:8]
OG_V = hashlib.sha1(open('og.png', 'rb').read()).hexdigest()[:8]
ICON_V = hashlib.sha1(open('apple-touch-icon.png', 'rb').read()).hexdigest()[:8]
vcard_href = f'sirius.vcard?v={VCARD_V}'

sheet_js = """<script>
(function(){
  var D=""" + SHEET_DATA + r""";
  var cells=document.querySelectorAll('.g'),sheet=document.getElementById('sheet'),dim=document.getElementById('dim');
  var t=document.getElementById('sh-t'),b=document.getElementById('sh-b'),d=document.getElementById('sh-d'),ic=document.getElementById('sh-i');
  var tm=null;
  function open(i){var x=D[i];ic.innerHTML=cells[i].querySelector('svg').outerHTML;t.textContent=x.t;b.textContent=x.b;b.className='br'+(x.cyr?' cyr':'');d.textContent=x.d;
    clearTimeout(tm);dim.hidden=false;sheet.hidden=false;sheet.style.transform='';void sheet.offsetHeight;
    sheet.setAttribute('aria-hidden','false');document.body.classList.add('open');}
  function close(){document.body.classList.remove('open');sheet.setAttribute('aria-hidden','true');
    clearTimeout(tm);tm=setTimeout(function(){if(!document.body.classList.contains('open')){dim.hidden=true;sheet.hidden=true;}},360);}
  cells.forEach(function(c,i){c.addEventListener('click',function(){open(i)})});
  dim.addEventListener('click',close);
  document.addEventListener('keydown',function(e){if(e.key==='Escape')close()});
  var y0=null;
  sheet.addEventListener('touchstart',function(e){y0=e.touches[0].clientY;sheet.style.transition='none'},{passive:true});
  sheet.addEventListener('touchmove',function(e){if(y0===null)return;var dy=e.touches[0].clientY-y0;if(dy>0)sheet.style.transform='translateY('+dy+'px)'},{passive:true});
  sheet.addEventListener('touchend',function(e){sheet.style.transition='';var dy=e.changedTouches[0].clientY-(y0||0);y0=null;if(dy>70)close();else sheet.style.transform=''});
})();
</script>"""

ios_fix = r'''<script>
(function(){
  var a=document.getElementById('save-contact');if(!a)return;
  var ua=navigator.userAgent||'';
  var ios=/iPhone|iPad|iPod/.test(ua)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
  if(!ios)return;
  var safariUA=/Safari\//.test(ua)&&/Version\//.test(ua);
  var inApp=!safariUA||!!(window.webkit&&window.webkit.messageHandlers)||/Telegram|FBAN|FBAV|Instagram|Line\/|VK/i.test(ua);
  if(!inApp)return;
  var target=location.protocol.replace(':','')+'://'+location.host+location.pathname.replace(/[^\/]*$/,'')+a.getAttribute('href');
  a.addEventListener('click',function(e){
    e.preventDefault();
    var left=false,onHide=function(){left=true};
    window.addEventListener('pagehide',onHide);document.addEventListener('visibilitychange',onHide);
    location.href='x-safari-'+target;
    setTimeout(function(){if(!left&&!document.hidden){location.href=target;}},1500);
  });
})();
</script>'''

html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0B2D26">
<meta name="description" content="Технический партнёр мероприятий: синхронный перевод, звук, свет, экраны, сцены, Zoom. Ташкент — Узбекистан.">
<title>Sirius Event Systems</title>
<link rel="apple-touch-icon" sizes="180x180" href="{A}apple-touch-icon.png?v={ICON_V}">
<meta name="apple-mobile-web-app-title" content="Sirius">
<link rel="icon" type="image/png" sizes="32x32" href="{A}favicon-32.png?v={ICON_V}">
<link rel="icon" type="image/png" sizes="64x64" href="{A}favicon-64.png?v={ICON_V}">
<link rel="manifest" href="{A}site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Sirius Event Systems">
<meta property="og:title" content="Технический партнёр мероприятий">
<meta property="og:description" content="Синхронный перевод, звук, свет, экран, сцена, Zoom">
<meta property="og:url" content="{PAGE_URL}">
<meta property="og:image" content="https://azirex-code.github.io/sirius-card/og.png?v={OG_V}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Sirius Event Systems">
<meta property="og:locale" content="ru_RU">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Технический партнёр мероприятий">
<meta name="twitter:description" content="Синхронный перевод, звук, свет, экран, сцена, Zoom">
<meta name="twitter:image" content="https://azirex-code.github.io/sirius-card/og.png?v={OG_V}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600&family=Montserrat:wght@500;600;700&family=Rajdhani:wght@600;700&family=Play:wght@700&display=swap" rel="stylesheet">
<style>
:root{{
  /* Композиция D: логотип в золотой звуковой волне, услуги открытой сеткой без плиток, золотая кнопка внизу */
  --bg:#0B2D26;--ink:#F3EFE6;--muted:rgba(243,239,230,.62);
  --gold:#CC9F52;--gold-hi:#E8CC8C;
  --glass:rgba(243,239,230,.06);--glass-line:rgba(243,239,230,.14);
  --fd:"Montserrat",-apple-system,"SF Pro Display","Segoe UI",sans-serif;
  --fb:"Golos Text",-apple-system,"SF Pro Text","Segoe UI",sans-serif;
  color-scheme:dark;
}}
*{{box-sizing:border-box}}
html{{height:100%;background:var(--bg)}}
body{{margin:0;min-height:100%;min-height:100dvh;background:var(--bg);color:var(--ink);font-family:var(--fb);-webkit-font-smoothing:antialiased;-webkit-tap-highlight-color:transparent;display:flex;flex-direction:column;padding:calc(8px + env(safe-area-inset-top)) 16px calc(11px + env(safe-area-inset-bottom))}}
a{{color:inherit;text-decoration:none}}
.wrap{{width:100%;max-width:440px;margin:0 auto;display:flex;flex-direction:column;flex:1}}
.hero{{position:relative;height:224px;flex:none}}
.hero .wave{{position:absolute;left:-16px;right:-16px;top:0;width:calc(100% + 32px);height:220px}}
.hero .mark{{position:absolute;left:50%;top:28px;width:77px;height:auto;transform:translateX(-50%)}}
.hero .word{{position:absolute;left:50%;top:114px;width:136px;height:auto;transform:translateX(-50%)}}
.hero .sub{{position:absolute;left:0;right:0;top:146px;text-align:center;font:600 9.5px var(--fd);letter-spacing:.42em;text-indent:.42em;color:var(--gold)}}
.hero .geo{{margin:0;position:absolute;left:0;right:0;top:203px;text-align:center;font:600 10px/1.3 "Rajdhani",var(--fd);letter-spacing:.13em;text-indent:.13em;text-transform:uppercase;color:var(--gold);white-space:nowrap}}
.hero .tag{{margin:0;position:absolute;left:0;right:0;top:178px;display:flex;align-items:center;gap:12px;font:500 13.5px/1.2 var(--fb);color:rgba(243,239,230,.9);letter-spacing:0;white-space:nowrap}}
.hero .tag:before,.hero .tag:after{{content:"";flex:1;height:1px;background:rgba(204,159,82,.55)}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;margin:auto 0;padding:0;--line:rgba(243,239,230,.12)}}
.g:nth-child(3n+2),.g:nth-child(3n+3){{border-left:1px solid var(--line)}}
.g:nth-child(n+4){{border-top:1px solid var(--line)}}
.g{{appearance:none;-webkit-appearance:none;background:none;border:0;color:inherit;font:inherit;cursor:pointer;display:flex;flex-direction:column;align-items:center;text-align:center;gap:6px;min-width:0;padding:6px 4px 4px;transition:background .15s}}
.g:active{{background:rgba(243,239,230,.06)}}
.g:focus-visible{{outline:2px solid var(--gold-hi);outline-offset:-2px}}
.g svg{{width:38px;height:38px;color:var(--gold)}}
.g b{{font:600 14px/1.2 var(--fd);min-height:34px;display:flex;align-items:flex-start;justify-content:center;letter-spacing:-.01em;hyphens:manual}}
.g small{{font:600 11px "Rajdhani",var(--fd);letter-spacing:.06em;text-transform:uppercase;color:var(--gold);white-space:nowrap}}
.g small.cyr{{font-family:"Play",var(--fd);font-size:10px;font-weight:700}}
.dock{{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding-top:7px}}
.foot{{margin:10px 0 0;text-align:center;font:500 10.5px var(--fd);letter-spacing:.12em;text-transform:uppercase;color:rgba(243,239,230,.42)}}
.btn{{display:flex;align-items:center;justify-content:center;gap:9px;height:46px;border-radius:14px;border:1px solid var(--glass-line);background:var(--glass);font:600 13.5px var(--fd);color:var(--ink);transition:transform .12s ease}}
.btn svg{{width:18px;height:18px;color:var(--gold);flex:none}}
.btn:active{{transform:scale(.98)}}
.btn:focus-visible{{outline:2px solid var(--gold-hi);outline-offset:3px}}
.btn-primary{{grid-column:1/-1;height:50px;border:0;background:linear-gradient(135deg,var(--gold-hi),var(--gold) 55%,#B98E45);color:#14261F;font-size:15px;box-shadow:0 10px 24px rgba(204,159,82,.25)}}
.btn-primary svg{{color:#14261F}}
.dim{{position:fixed;inset:0;z-index:5;background:transparent;pointer-events:none}}
.sheet{{position:fixed;left:0;right:0;bottom:0;z-index:6;max-width:440px;margin:0 auto;background:#0F3A31;border-radius:22px 22px 0 0;padding:12px 20px calc(20px + env(safe-area-inset-bottom));box-shadow:0 -24px 70px rgba(0,0,0,.6),0 -1px 0 rgba(243,239,230,.08);transform:translateY(105%);transition:transform .32s cubic-bezier(.2,.8,.2,1);touch-action:none}}
.sheet .hd{{width:38px;height:4px;border-radius:2px;background:rgba(243,239,230,.25);margin:0 auto 16px}}
.sheet .ic svg{{width:40px;height:40px;color:var(--gold);display:block;margin-bottom:10px}}
.sheet h2{{margin:0 0 4px;font:600 20px/1.2 var(--fd)}}
.sheet .br{{margin:0 0 12px;font:600 10.5px var(--fd);letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}}
.sheet p.tx{{margin:0 0 16px;font:400 15px/1.45 var(--fb);color:rgba(243,239,230,.86)}}
body.open .dim{{pointer-events:auto}}
body.open .sheet{{transform:none}}
@media (prefers-reduced-motion:reduce){{.dim,.sheet{{transition:none}}}}
@media (prefers-reduced-motion:reduce){{.btn{{transition:none}}}}
@media (max-height:720px){{.hero{{height:196px}}.hero .mark{{top:20px;width:67px}}.hero .word{{top:96px;width:125px}}.hero .sub{{top:126px}}.hero .tag{{top:152px;font-size:12.5px}}.hero .geo{{top:173px;font-size:9px}}.g{{padding:5px 4px 3px}}.g svg{{width:32px;height:32px}}.g b{{font-size:13px;min-height:31px}}.g small{{font-size:10px}}.g small.cyr{{font-size:9px}}.dock{{padding-top:8px}}}}
@media (min-height:800px){{.hero{{height:256px}}.hero .mark{{top:44px;width:83px}}.hero .word{{top:138px;width:147px}}.hero .sub{{top:172px}}.hero .tag{{top:204px;font-size:14.5px}}.hero .geo{{top:227px}}.g{{padding:14px 4px 12px}}.g svg{{width:44px;height:44px}}.g b{{font-size:14.5px;min-height:36px}}.g small{{font-size:11.5px}}.g small.cyr{{font-size:10.5px}}.dock{{padding-top:14px}}}}
@media (min-width:420px) and (min-height:800px){{.g{{padding:9px 4px 7px}}.g svg{{width:46px;height:46px}}.g b{{font-size:15px;min-height:36px}}.g small{{font-size:12px}}.g small.cyr{{font-size:11px}}.hero .tag{{font-size:15px}}.hero .geo{{font-size:11px}}}}
</style>
</head>
<body>
<main class="wrap">
  <header class="hero">
    <svg class="mark" viewBox="{VB}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sirius">{ICON}</svg>
    <svg class="word" viewBox="{WVB}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="SIRIUS">{WORD}</svg>
    <div class="sub">EVENT SYSTEMS</div>
    <p class="tag">Ваш технический партнёр мероприятий</p>
    <p class="geo">Ташкент — Узбекистан</p>
  </header>
  <section class="grid" aria-label="Услуги">
{grid}
  </section>
  <nav class="dock" aria-label="Связаться">
    <a class="btn btn-primary" id="save-contact" href="{vcard_href}">{save_ic}Сохранить контакт</a>
    <a class="btn" href="https://t.me/{TELEGRAM}" target="_blank" rel="noopener">{tg_ic}Telegram</a>
    <a class="btn" href="{INSTAGRAM_URL}" target="_blank" rel="noopener">{ig_ic}Instagram</a>
  </nav>
  <p class="foot">© 2019 Sirius Event Systems</p>
</main>
<div class="dim" id="dim" hidden></div>
<div class="sheet" id="sheet" role="dialog" aria-modal="true" aria-labelledby="sh-t" aria-hidden="true" hidden>
  <div class="hd"></div>
  <div class="ic" id="sh-i"></div>
  <h2 id="sh-t"></h2>
  <p class="br" id="sh-b"></p>
  <p class="tx" id="sh-d"></p>
  <a class="btn" href="https://t.me/{TELEGRAM}" target="_blank" rel="noopener">{tg_ic}Уточнить в Telegram</a>
</div>
{sheet_js}
{ios_fix}
</body>
</html>
'''
os.makedirs(f'hosted/{PERSON}', exist_ok=True)
open(f'hosted/{PERSON}/index.html', 'w', encoding='utf-8').write(html)
print(f'hosted/{PERSON}/index.html bytes', len(html.encode()), 'vcard', vcard_href)
