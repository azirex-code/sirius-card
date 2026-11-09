import base64, subprocess, re
TELEGRAM = "Denis_SES"
INSTAGRAM_URL = "https://www.instagram.com/"   # ник компании не известен — заглушка
icon = open('icon.svg',encoding='utf-8').read().replace('<svg ','<svg class="mark" ',1)
word = open('wordmark.svg',encoding='utf-8').read().replace('<svg ','<svg class="wordmark" ',1).replace('aria-label="Sirius"','aria-label="SIRIUS"')
html = open('index.template.html',encoding='utf-8').read()
COPY_ICON='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2.5"/><path d="M15 9V6.5A2.5 2.5 0 0 0 12.5 4h-6A2.5 2.5 0 0 0 4 6.5v6A2.5 2.5 0 0 0 6.5 15H9"/></svg>'
html = html.replace('{{COPY_ICON}}',COPY_ICON).replace('{{ICON}}',icon).replace('{{WORDMARK}}',word).replace('{{TELEGRAM}}',TELEGRAM).replace('{{INSTAGRAM_URL}}',INSTAGRAM_URL)
open('index.html','w',encoding='utf-8').write(html)
print('index.html bytes', len(html.encode()))
# --- версия для своего хостинга: кнопка ведёт прямо на файл контакта, шторка не нужна ---
hosted = re.sub(r'<!-- sheet:start -->.*?<!-- sheet:end -->', '', html, flags=re.S)
btn_start = hosted.index('<button class="btn btn-primary"'); btn_end = hosted.index('</button>', btn_start)+len('</button>')
btn = hosted[btn_start:btn_end]
inner = btn[btn.index('>')+1:btn.rindex('</button>')]
hosted = hosted[:btn_start] + '<a class="btn btn-primary" id="save-contact" href="sirius.vcard">' + inner + '</a>' + hosted[btn_end:]
# iOS: встроенные браузеры (Telegram, Instagram и т.п.) не открывают карточку контакта — отправляем файл в настоящий Safari
ios_fix = r'''<script>
(function(){
  var a=document.getElementById('save-contact');if(!a)return;
  var ua=navigator.userAgent||'';
  var ios=/iPhone|iPad|iPod/.test(ua)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
  if(!ios)return;
  var safariUA=/Safari\//.test(ua)&&/Version\//.test(ua);
  var inApp=!safariUA||!!(window.webkit&&window.webkit.messageHandlers)||/Telegram|FBAN|FBAV|Instagram|Line\/|VK/i.test(ua);
  if(!inApp)return;
  var target=location.protocol.replace(':','')+'://'+location.host+location.pathname.replace(/[^\/]*$/,'')+'sirius.vcard';
  a.addEventListener('click',function(e){
    e.preventDefault();
    var left=false,onHide=function(){left=true};
    window.addEventListener('pagehide',onHide);document.addEventListener('visibilitychange',onHide);
    location.href='x-safari-'+target;
    setTimeout(function(){if(!left&&!document.hidden){location.href=target;}},1500);
  });
})();
</script>
</body>'''
hosted = hosted.replace('</body>', ios_fix, 1)
import os; os.makedirs('hosted', exist_ok=True)
open('hosted/index.html','w',encoding='utf-8').write(hosted)
print('hosted/index.html bytes', len(hosted.encode()))

# --- фото для карточки контакта: знак S на тёмно-зелёном ---
inner = open('icon.svg',encoding='utf-8').read()
vb = re.search(r'viewBox="([^"]+)"', inner).group(1)
inner = re.sub(r'<svg [^>]*>', '', inner, count=1).replace('</svg>','')
wsrc = open('wordmark.svg',encoding='utf-8').read()
wvb = re.search(r'viewBox="([^"]+)"', wsrc).group(1)
winner = re.sub(r'<svg [^>]*>', '', wsrc, count=1).replace('</svg>','')
wrap = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><rect width="1000" height="1000" fill="#0B2D26"/><svg x="200" y="225" width="600" height="550" viewBox="{vb}" preserveAspectRatio="xMidYMid meet">{inner}</svg></svg>'''
open('/tmp/photo.svg','w').write(wrap)
png = subprocess.run(['rsvg-convert','-w','512','-h','512','/tmp/photo.svg'],capture_output=True,check=True).stdout
open('photo.png','wb').write(png)
from PIL import Image
import io
im = Image.open(io.BytesIO(png)).convert('RGB'); buf = io.BytesIO(); im.save(buf,'JPEG',quality=85,optimize=True); jpg = buf.getvalue(); open('photo.jpg','wb').write(jpg)
b64 = base64.b64encode(jpg).decode()

def fold(line):
    # перенос строк vCard по 75 байт, не разрывая многобайтовые символы
    out=[]; cur=''; limit=75
    for ch in line:
        if len((cur+ch).encode('utf-8')) > limit:
            out.append(cur); cur=ch; limit=74
        else:
            cur+=ch
    out.append(cur)
    return '\r\n '.join(out)

lines = [
 'BEGIN:VCARD','VERSION:3.0',
 'N:;Farhod;;;','FN:Farhod','ORG:Sirius Event Systems',
 'X-PHONETIC-FIRST-NAME:Переводчик синхронист синхронный перевод наушник наушники кабина кабинка будка',
 'X-PHONETIC-LAST-NAME:Звук свет LED экран сцена подиум суфлёр телевизор интерактивная панель видеосвязь Zoom конференция форум','TITLE:Синхронный перевод и звук',
 'NOTE:Техническое сопровождение конференций и форумов: синхронный перевод, переводчики-синхронисты, звук, свет, LED-экраны, телевизоры-суфлёры, интерактивные панели, сцены и подиумы, видеосвязь Zoom. Ташкент и весь Узбекистан.',
 'TEL;TYPE=CELL,VOICE:+998998110745',
 'END:VCARD']
vcf = '\r\n'.join(fold(l) for l in lines)+'\r\n'
open('sirius.vcf','w',encoding='utf-8',newline='').write(vcf)
print('sirius.vcf bytes', len(vcf.encode()), 'photo bytes', len(png))
