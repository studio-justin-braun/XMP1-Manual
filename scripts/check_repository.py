"""Validate the checked-in manual, original source and repository links."""
from pathlib import Path
import base64
import hashlib
import io
import json
import re
import sys
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup
from PIL import Image
import pymupdf
import build_manual as source

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA = '487089c8f0aab8dafafb1712b284400b90cec0411c963d2c4fbcf455cb6849f6'


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def local_links(document, path):
    ids = {e['id'] for e in document.select('[id]')}
    for a in document.select('a[href]'):
        link = urlsplit(a['href'])
        if link.scheme or link.netloc:
            continue
        if not link.path:
            check(not link.fragment or unquote(link.fragment) in ids, f'Fehlender Anker: {path}: {a["href"]}')
        else:
            target = (path.parent / unquote(link.path)).resolve()
            check(target.is_relative_to(ROOT) and target.exists(), f'Fehlende lokale Datei: {a["href"]}')


def main():
    check(hashlib.sha256((ROOT / 'Quellen/XMP1.HLP').read_bytes()).hexdigest() == EXPECTED_SHA, 'Original-HLP wurde verändert.')
    check(not source.diffs, 'Unterschiede zwischen RTF und unabhängigem Textinventar.')
    check(len(source.TOPICS) == 244 and len(source.P.links) == 243, 'Unvollständige Themen oder Verweise.')
    path = ROOT / 'Handbuch/index.html'
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    sections = soup.select('section.topic')
    check([s['id'] for s in sections] == [f'topic-{i}' for i in range(244)], 'Themen fehlen oder Reihenfolge abweichend.')
    local_links(soup, path)
    local_links(BeautifulSoup((ROOT / 'index.html').read_text(encoding='utf-8'), 'html.parser'), ROOT / 'index.html')
    for i, section in enumerate(sections):
        actual = source.norm(section.get_text(' ')).replace('·', '•')
        for p in source.paragraphs(source.TOPICS[i]):
            text = re.sub(r'\{bm[clr] bm\d+\.(?:BMP|WMF)\}', '', ''.join(r['text'] for r in p['runs']))
            check(source.norm(text).replace('·', '•') in actual, f'Text fehlt in HTML-Thema {i}: {text[:70]}')
    images = soup.select('section.topic img')
    check(len(images) == 125, 'HTML-Bildanzahl abweichend.')
    for img in images:
        check(img['src'].startswith('data:image/png;base64,'), 'Bild ist nicht offline eingebettet.')
        data = base64.b64decode(img['src'].split(',', 1)[1], validate=True)
        with Image.open(io.BytesIO(data)) as picture:
            picture.verify()
        check(data == (ROOT / 'Handbuch/medien' / (img['data-image'] + '.png')).read_bytes(), 'Eingebettetes Bild weicht von PNG ab.')
    search = json.loads(soup.select_one('#search-data').string)
    check([d['id'] for d in search] == list(range(244)), 'Suchindex unvollständig.')
    check(len(soup.select('#index-panel li')) == 276, 'Stichwortregister unvollständig.')
    check(len(soup.select('section.topic td')) == 1106, 'Tabellenzellen fehlen.')
    for md in [*ROOT.glob('*.md'), *ROOT.glob('docs/*.md')]:
        for href in re.findall(r'\]\(([^)]+)\)', md.read_text(encoding='utf-8')):
            ref = urlsplit(href)
            if ref.scheme or ref.netloc or not ref.path:
                continue
            check((md.parent / unquote(ref.path)).exists(), f'Dokumentationslink fehlt: {md.name}: {href}')
    with pymupdf.open(ROOT / 'pdf/XMP1_Handbuch.pdf') as pdf:
        check(len(pdf) == 132, 'PDF-Seitenanzahl abweichend; bei neuer Ausgabe Sollwerte aktualisieren.')
        check(sum(len(p.get_image_info()) for p in pdf) == 125, 'PDF-Bilder fehlen.')
        for page in pdf:
            for link in page.get_links():
                if link['kind'] == pymupdf.LINK_GOTO:
                    check(0 <= link.get('page', -1) < len(pdf), 'Ungültiger PDF-Verweis.')
    print('OK: Original-SHA, 244 Themen, 243 Verweise, 125 Bilder, 1.106 Tabellenzellen, Suchindex, 276 Registereinträge, PDF und lokale Links.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, KeyError, ValueError) as error:
        print(f'FEHLER: {error}', file=sys.stderr)
        raise SystemExit(1)
