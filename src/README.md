# Sirius Event Systems — NFC-визитка (исходники)

Страницы: https://azirex-code.github.io/sirius-card/farhod/ (Фарход); корень `/sirius-card/` перенаправляет на неё. Для новой персоны: добавить запись в PEOPLE в build4.py, собрать `python3 build4.py <имя>`, положить `<имя>/index.html` и `<имя>/sirius.vcard`.

## Как собрать
```bash
cd src
python3 build.py        # собирает sirius.vcf (карточка контакта Фархода)
python3 build4.py farhod   # собирает hosted/farhod/index.html
cp hosted/farhod/index.html ../farhod/index.html
cp sirius.vcf ../farhod/sirius.vcard   # на Pages файл отдаётся как .vcard (text/vcard), иначе Safari предлагает скачать
python3 make_icons.py   # иконки для домашнего экрана (apple-touch-icon.png, icon-192/512.png, favicon-*.png)
python3 check_fit.py    # проверка: один экран без прокрутки на iPhone (390×761, 844, SE, Pro Max)
```
Для check_fit.py и test_sheet.py нужен Playwright (`pip install playwright && playwright install chromium`).

## Что где
- `build4.py` — генератор страницы: тексты услуг, описания карточек, ссылки (Telegram `faribabu`, Instagram — заглушка), вёрстка, карточка по нажатию, Open Graph.
- `index.template.html` — источник значков услуг (стиль линий 1.6).
- `icon.svg`, `wordmark.svg`, `horizontal.svg` — обрезанные логотипы из брендбука (Vector_Sirius).
- `og_src.html` — макет картинки превью ссылки (og.png 1200×630).
- Цвета: фон #0B2D26, золото #CC9F52 / #E8CC8C, текст #F3EFE6. Шрифты: Montserrat, Golos Text, Rajdhani.

## Особенности
- Ссылка на контакт версионируется: `sirius.vcard?v=<sha1[:8]>` — обходит кэш GitHub Pages (10 мин).
- Во встроенном браузере Telegram на iOS vCard не открывается — скрипт перекидывает в Safari через `x-safari-https://`.
- Safari (iOS 26) красит панели по фону страницы и закреплённым элементам: затемнения нет, карточка и её подложка в закрытом состоянии `hidden`.
- Ключевые слова для поиска контакта в телефоне лежат в X-PHONETIC-полях имени (iPhone ищет по ним, но не показывает).

## Обложки для Reels и постов (формула: кадр + заголовок + логотип)
```bash
cd src && python3 make_cover.py кадр.jpg "ЗАГОЛОВОК|слово золотом" "подзаголовок" 1920   # Reels 9:16
cd src && python3 make_cover.py кадр.jpg "ЗАГОЛОВОК|слово золотом" "подзаголовок" 1350   # пост 4:5
```
Кадр — любой стоп-кадр из видео или фото; скрипт сам кадрирует, приглушает цвет и кладёт фирменный тон.
Обложка ставится на Reels: «… → Редактировать → Обложка → Из галереи».
