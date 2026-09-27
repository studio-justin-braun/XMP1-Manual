"""Rebuild the decompiled WinHelp source as offline HTML and a print manual.

The RTF source preserves links and table geometry that winhlp 0.4.1 loses.
The independent winhlp inventory is retained for text and order verification.
"""
from pathlib import Path
import sys, re, json, html, base64, hashlib, copy, difflib, collections, shutil, argparse
ROOT = Path(__file__).resolve().parents[1]
from PIL import Image as PILImage

OUT = ROOT / 'build/Handbuch'
QA = ROOT / 'build/qa'
QA.mkdir(parents=True, exist_ok=True)
INV = json.loads((ROOT / 'Quellen/inventory.json').read_text(encoding='utf8'))
RTF = (ROOT / 'Quellen/dekompiliert/XMP1.RTF').read_text(encoding='cp1252')
TOKEN = re.compile(r"(\{)|(\})|\\'([0-9a-fA-F]{2})|\\([a-zA-Z]+)(-?\d+)? ?|\\([^a-zA-Z])|([^{}\\\r\n]+)")
DEFAULT = dict(b=False, i=False, ul=False, fs=20, f=2, cf=0, skip=False, hidden=False)
PDEFAULT = dict(align='left', li=0, fi=0, sb=0, sa=0, sl=275)

class Parser:
    def __init__(self):
        self.state = DEFAULT.copy(); self.stack=[]; self.para=PDEFAULT.copy()
        self.topics=[[]]; self.runs=[]; self.cells=None; self.cellparas=[]; self.widths=[]
        self.hidden=''; self.links=[]; self.linkruns=[]

    def text(self, text):
        if self.state['skip']: return
        if self.state['hidden']:
            self.hidden += text
            return
        if not text: return
        st={k:self.state[k] for k in ('b','i','ul','fs','f','cf')}
        if self.runs and self.runs[-1]['style']==st and not self.runs[-1].get('link'):
            self.runs[-1]['text']+=text
        else:
            self.runs.append(dict(text=text,style=st))
        if self.state['ul'] and all(self.runs[-1] is not r for r in self.linkruns):
            self.linkruns.append(self.runs[-1])

    def flush(self):
        if any(r['text'].strip() for r in self.runs):
            p=dict(kind='p',runs=self.runs,style=self.para.copy())
            (self.cellparas if self.cells is not None else self.topics[-1]).append(p)
        self.runs=[]

    def parse(self, source):
        for m in TOKEN.finditer(source):
            op,cl,hx,word,num,sym,txt=m.groups()
            if op: self.stack.append(self.state.copy())
            elif cl:
                old=self.state; self.state=self.stack.pop()
                if old['hidden'] and not self.state['hidden'] and self.hidden:
                    target=self.hidden.strip(); self.hidden=''
                    label=''.join(r['text'] for r in self.linkruns).strip()
                    assert label, ('link without label',target)
                    for r in self.linkruns: r['link']=target
                    self.links.append(dict(source=len(self.topics)-1,label=label,target=target))
                    self.linkruns=[]
            elif hx: self.text(bytes.fromhex(hx).decode('cp1252'))
            elif txt: self.text(txt)
            elif sym:
                if sym in '{}\\': self.text(sym)
                elif sym=='~': self.text('\u00a0')
            elif word:
                n=int(num) if num else 1
                if word in ('fonttbl','colortbl','stylesheet','footnote','up'):
                    self.state['skip']=True
                elif self.state['skip']: continue
                elif word=='v': self.state['hidden']=bool(n)
                elif word=='plain':
                    self.state.update({k:v for k,v in DEFAULT.items() if k not in ('skip','hidden')})
                elif word in ('b','i'): self.state[word]=bool(n)
                elif word in ('ul','uldb'): self.state['ul']=bool(n)
                elif word in ('fs','f','cf'): self.state[word]=n
                elif word=='par': self.flush()
                elif word=='line': self.text('\n')
                elif word=='tab': self.text('\t')
                elif word=='pard': self.para=PDEFAULT.copy()
                elif word=='qc': self.para['align']='center'
                elif word in ('li','fi','sb','sa','sl'): self.para[word]=n
                elif word=='page':
                    self.flush(); self.topics.append([])
                elif word=='trowd':
                    self.flush(); self.cells=[]; self.cellparas=[]; self.widths=[]
                elif word=='cellx': self.widths.append(n)
                elif word=='cell':
                    self.flush(); self.cells.append(self.cellparas); self.cellparas=[]
                elif word=='row':
                    assert len(self.cells)==len(self.widths)
                    row=dict(cells=self.cells,widths=self.widths)
                    if self.topics[-1] and self.topics[-1][-1]['kind']=='table':
                        self.topics[-1][-1]['rows'].append(row)
                    else: self.topics[-1].append(dict(kind='table',rows=[row]))
                    self.cells=None; self.cellparas=[]; self.widths=[]
        self.flush()
        return self.topics

def paragraphs(blocks):
    for b in blocks:
        if b['kind']=='p': yield b
        else:
            for row in b['rows']:
                for cell in row['cells']: yield from paragraphs(cell)

def plain(blocks):
    return '\n'.join(''.join(r['text'] for r in p['runs']) for p in paragraphs(blocks))

def norm(s):
    return re.sub(r'\s+', '', s).replace('\u00ad','')

P = Parser()
TOPICS=P.parse(RTF)
assert len(TOPICS)==len(INV['topics'])==244
CONTEXT={c:i for i,t in enumerate(INV['topics']) for c in t['contexts']}
RTF_CONTEXTS = re.findall(r'\{\\footnote\\pard\\plain\{\\up #\} ([^}]+)\}',RTF)
assert len(RTF_CONTEXTS)==244
CONTEXT.update({c:i for i,c in enumerate(RTF_CONTEXTS)})
for l in P.links:
    l['destination']=CONTEXT.get(l['target'].split('>')[0])
assert all(l['destination'] is not None for l in P.links)
CHILDREN=collections.defaultdict(list)
PARENTS={}
for l in P.links:
    CHILDREN[l['source']].append(l['destination'])
    assert l['destination'] not in PARENTS
    PARENTS[l['destination']]=l['source']
assert set(PARENTS)==set(range(1,244))

# Root chapter labels are explicitly present in the original contents page.
CHAPTERS=[]
chapter=None
for p in paragraphs(TOPICS[0]):
    text=''.join(r['text'] for r in p['runs']).strip()
    if any(r.get('link') for r in p['runs']):
        dest=CONTEXT[next(r['link'] for r in p['runs'] if r.get('link')).split('>')[0]]
        chapter['children'].append(dest)
    elif text and text!='Inhaltsverzeichnis':
        chapter=dict(title=text,children=[]); CHAPTERS.append(chapter)

ORDER=[]; META={0:dict(number='0',chapter='Original-Inhaltsverzeichnis',level=0,title='Inhaltsverzeichnis')}
def walk(i,number,chapter,level):
    ORDER.append(i)
    META[i]=dict(number=number,chapter=chapter,level=level,title=plain(TOPICS[i][:1]).strip())
    for n,c in enumerate(CHILDREN[i],1): walk(c,f'{number}.{n}',chapter,level+1)
for n,ch in enumerate(CHAPTERS,1):
    ch['number']=n
    for k,i in enumerate(ch['children'],1): walk(i,f'{n}.{k}',ch['title'],1)
assert ORDER==list(range(1,244)), 'Authored contents order differs from file order'

# Verify every visible character against the independent binary parser.
diffs=[]
for i,blocks in enumerate(TOPICS):
    a=re.sub(r'\{bm[clr] bm\d+\.(?:BMP|WMF)\}','',plain(blocks))
    b=INV['topics'][i]['text']
    if norm(a)!=norm(b):
        diffs.append(dict(topic=i,ratio=difflib.SequenceMatcher(None,norm(a),norm(b),autojunk=False).ratio(),
          difference=list(difflib.unified_diff(a.splitlines(),b.splitlines()))[:35]))

def table_grid(block):
    # Recover merged cells from their absolute RTF right boundaries.
    bounds=sorted(set(x for row in block['rows'] for x in row['widths']))
    # Small right-edge rounding differences represent the same physical column.
    merged=[]
    for x in bounds:
        if not merged or x-merged[-1]>60: merged.append(x)
    def nearest(x): return min(range(len(merged)), key=lambda k:abs(merged[k]-x))
    grid=[]
    for row in block['rows']:
        cells=[]; start=0
        for cell,right in zip(row['cells'],row['widths']):
            end=nearest(right)+1
            cells.append(dict(blocks=cell,col=start,span=end-start))
            start=end
        grid.append(cells)
    widths=[merged[0]]+[b-a for a,b in zip(merged,merged[1:])]
    return widths,grid

def run_html(r):
    st=r['style']; s=html.escape(r['text'])
    s=re.sub(r'\{bm[clr] (bm\d+)\.(?:BMP|WMF)\}',lambda m: f'<img src="medien/{m[1]}.png" data-image="{m[1]}" alt="Originalabbildung {m[1]}" loading="lazy">',s)
    s=s.replace('\n','<br>').replace('\t','<span class="tab">\t</span>')
    if st['f']==4: s=s.replace('·','•')
    if st['b']: s=f'<strong>{s}</strong>'
    if st['i']: s=f'<em>{s}</em>'
    if st['ul'] and not r.get('link'): s=f'<u>{s}</u>'
    if r.get('link'):
        i=CONTEXT[r['link'].split('>')[0]]
        s=f'<a href="#topic-{i}">{s}</a>'
    return s

def blocks_html(blocks):
    parts=[]
    for b in blocks:
        if b['kind']=='p':
            s=''.join(run_html(r) for r in b['runs'])
            size=max(r['style']['fs'] for r in b['runs'])
            cls='subheading' if size>=22 and not all(r.get('link') or not r['text'].strip() for r in b['runs']) else ''
            if b['style']['li']>0: cls+=' indented'
            if b['style']['align']=='center': cls+=' centered'
            parts.append(f'<p class="{cls.strip()}">{s}</p>')
        else:
            widths,grid=table_grid(b)
            rows=[]
            for cells in grid:
                rows.append('<tr>'+''.join(f'<td colspan="{c["span"]}">{blocks_html(c["blocks"])}</td>' for c in cells)+'</tr>')
            cols=''.join(f'<col style="width:{w/sum(widths)*100:.3f}%">' for w in widths)
            parts.append(f'<div class="table-scroll"><table><colgroup>{cols}</colgroup>'+''.join(rows)+'</table></div>')
    return '\n'.join(parts)

def data_model():
    return dict(source='XMP1.HLP',sha256=hashlib.sha256((ROOT/'Quellen/XMP1.HLP').read_bytes()).hexdigest(),
                chapters=CHAPTERS,topics=[dict(index=i,**META[i],blocks=TOPICS[i],keywords=INV['topics'][i]['keywords']) for i in [0]+ORDER],
                links=P.links,text_comparison_differences=diffs)

def make_html():
    OUT.mkdir(parents=True,exist_ok=True)
    shutil.copytree(ROOT/'Handbuch/medien',OUT/'medien',dirs_exist_ok=True)
    css=(ROOT/'scripts/manual.css').read_text(encoding='utf8')
    js=(ROOT/'scripts/manual.js').read_text(encoding='utf8')
    def nav_item(i):
        m=META[i]
        return f'<li><a href="#topic-{i}" data-topic="{i}"><span>{m["number"]}</span> {html.escape(m["title"])}</a>'+(
            '<ul>'+''.join(nav_item(c) for c in CHILDREN[i])+'</ul>' if CHILDREN[i] else '')+'</li>'
    nav=''.join(f'<details open><summary>{ch["number"]:02d} · {html.escape(ch["title"])}</summary><ul>'+''.join(nav_item(i) for i in ch['children'])+'</ul></details>' for ch in CHAPTERS)
    sections=[]; search=[]
    for i in [0]+ORDER:
        m=META[i]
        content=blocks_html(TOPICS[i][1:])
        sections.append(f'<section id="topic-{i}" class="topic" data-topic="{i}" aria-labelledby="heading-{i}"><div class="eyebrow">{html.escape(m["chapter"])}</div><h2 id="heading-{i}"><span>{m["number"] if i else ""}</span> {html.escape(m["title"])}</h2>{content}</section>')
        search.append(dict(id=i,number=m['number'],title=m['title'],chapter=m['chapter'],text=re.sub(r'\{bm[clr] bm\d+\.(BMP|WMF)\}','',plain(TOPICS[i])),keywords='; '.join(INV['topics'][i]['keywords'])))
    index=[]
    for e in INV['index']:
        targets=e['topics'] or ([e['topic']] if e['topic'] is not None else [])
        index.append(f'<li><strong>{html.escape(e["label"])}</strong><div>'+ ' · '.join(f'<a href="#topic-{i}">{html.escape(META[i]["number"]+" "+META[i]["title"])}</a>' for i in targets)+'</div></li>')
    chaptercards=''.join(f'<a href="#topic-{ch["children"][0]}"><span>{ch["number"]:02d}</span><strong>{html.escape(ch["title"])}</strong></a>' for ch in CHAPTERS)
    document=f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>MSP XMP1 · Bedienhandbuch</title><style>{css}</style></head>
<body><a class="skip" href="#main">Zum Inhalt</a>
<header class="topbar"><a class="brand" href="#start"><span class="brandmark">X</span>MSP <b>XMP1</b><small>BEDIENHANDBUCH</small></a><div><button id="menu" aria-expanded="false" aria-controls="sidebar">Inhalt</button><a href="../pdf/XMP1_Handbuch.pdf">PDF herunterladen ↗</a></div></header>
<aside id="sidebar"><div class="searchbox"><label for="search">Im gesamten Handbuch suchen</label><div><input id="search" type="search" placeholder="Begriff, Funktion oder Befehl …" autocomplete="off"><button id="clear" aria-label="Suche löschen">×</button></div><small>Mehrere Wörter eingeben · Strg + K</small></div>
<nav class="tabs" aria-label="Ansichten"><button id="contents-tab" class="active">Inhalt</button><button id="index-tab">Stichwörter</button></nav><div id="outline" aria-label="Inhaltsverzeichnis"><a class="original-link" href="#topic-0">Original-Inhaltsverzeichnis</a>{nav}</div><div id="index-panel" hidden><ul>{''.join(index)}</ul></div><div class="sidebar-foot">244 Themen · 125 Abbildungen<br>Offline verfügbar · Quelle: XMP1.HLP</div></aside>
<main id="main"><div id="results" hidden><div class="eyebrow">VOLLTEXTSUCHE</div><h1 id="result-count" aria-live="polite"></h1><p>Treffer in Überschriften, Texten und originalen Stichwörtern.</p><ol id="result-list"></ol></div>
<div id="reading"><section id="start" class="intro"><div class="eyebrow">TECHNISCHE DOKUMENTATION</div><h1>MSP XMP1<span>Bedienhandbuch</span></h1><p class="lead">Konfiguration, Bedienung und Diagnose der XMP1-Applikation auf dem Modularen Service-PC.</p><div class="stats"><div><b>07</b>Hauptkapitel</div><div><b>244</b>Hilfethemen</div><div><b>125</b>Abbildungen</div></div><div class="chaptercards">{chaptercards}</div><div class="edition"><strong>Zur digitalen Ausgabe</strong><p>Vollständige Übertragung der bereitgestellten XMP1.HLP. Gliederung und Reihenfolge folgen dem Original; Nummerierung, Suche und Navigation wurden ergänzt. Historische Systemanforderungen und Bedienhinweise entsprechen dem Stand der Quelldatei.</p><p>Verweise führen direkt zum jeweiligen Thema. Abbildungen lassen sich per Klick vergrößern. Das Stichwortregister enthält die Originaleinträge.</p></div></section>
{''.join(sections)}<section id="edition" class="edition"><h2>Über diese Ausgabe</h2><p>244 von 244 Themen, 243 von 243 Querverweisen und 125 von 125 Bildressourcen übernommen. Alle Texte wurden mit zwei unabhängigen Ausleseverfahren abgeglichen. Die Datei enthält 106 Bitmap- und 19 Vektorgrafiken; keine separaten Audio- oder Videodateien. Die Vektorgrafiken wurden für die Darstellung mit 300 dpi gerendert.</p><p>Originalquelle: XMP1.HLP · Quellvermerk: ® PET2BK. Die Texte wurden nicht fachlich aktualisiert. Details zur Konvertierung stehen im beigefügten Prüfbericht.</p></section></div>
<nav class="pager" aria-label="Themennavigation"><a id="prev-topic" href="#start">← Übersicht</a><span id="position"></span><a id="next-topic" href="#topic-0">Nächstes Thema →</a></nav></main>
<button id="top" aria-label="Zur Seitenübersicht">↑</button><dialog id="lightbox"><div><span id="image-caption"></span><button id="close-image" autofocus aria-label="Bildansicht schließen">Schließen ×</button></div><img id="large-image" alt=""></dialog>
<script id="search-data" type="application/json">{json.dumps(search,ensure_ascii=False).replace('</','<\\/')}</script><script>{js}</script></body></html>'''
    # The HTML is independently portable: fonts, CSS, JS and all 125 pictures work offline.
    def embed(m):
        path=OUT/'medien'/m[1]
        return 'src="data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()+'"'
    document=re.sub(r'src="medien/([^"/]+\.png)"',embed,document)
    (OUT/'index.html').write_text(document,encoding='utf8')

def make_pdf():
    from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Image, LongTable, TableStyle, Flowable, KeepTogether
    from reportlab.platypus.tableofcontents import TableOfContents
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for name,file in [('Manual','arial.ttf'),('Manual-Bold','arialbd.ttf'),('Manual-Italic','ariali.ttf'),('Manual-BoldItalic','arialbi.ttf')]:
        pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
    pdfmetrics.registerFontFamily('Manual',normal='Manual',bold='Manual-Bold',italic='Manual-Italic',boldItalic='Manual-BoldItalic')
    navy=colors.HexColor('#142b42'); teal=colors.HexColor('#087c86'); ink=colors.HexColor('#263746'); muted=colors.HexColor('#627484')
    W,H=A4; M=46; CW=W-2*M
    body=ParagraphStyle('body',fontName='Manual',fontSize=9.6,leading=14.1,textColor=ink,spaceAfter=7,allowWidows=0,allowOrphans=0)
    styles={
        'body':body,
        'small':ParagraphStyle('small',parent=body,fontSize=8,leading=11,textColor=muted),
        'chapter':ParagraphStyle('chapter',parent=body,fontName='Manual-Bold',fontSize=24,leading=29,textColor=navy,spaceAfter=20,keepWithNext=True),
        'h1':ParagraphStyle('h1',parent=body,fontName='Manual-Bold',fontSize=17,leading=21,textColor=navy,spaceBefore=17,spaceAfter=10,keepWithNext=True),
        'h2':ParagraphStyle('h2',parent=body,fontName='Manual-Bold',fontSize=12.5,leading=17,textColor=navy,spaceBefore=13,spaceAfter=8,keepWithNext=True),
        'h3':ParagraphStyle('h3',parent=body,fontName='Manual-Bold',fontSize=10.5,leading=14.5,textColor=teal,spaceBefore=10,spaceAfter=6,keepWithNext=True),
    }
    class ManualDoc(BaseDocTemplate):
        def __init__(self,path):
            super().__init__(str(path),pagesize=A4,leftMargin=M,rightMargin=M,topMargin=48,bottomMargin=46,
                title='MSP XMP1 - Bedienhandbuch',author='Originalquelle: XMP1.HLP',subject='Konfiguration, Bedienung und Diagnose - vollständige digitale Ausgabe')
            self.addPageTemplates(PageTemplate(id='normal',frames=[Frame(M,46,CW,H-94,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPageEnd=self.decorate))
            self.current_chapter='MSP XMP1'; self.topic_pages={}
        def beforeDocument(self):
            self.current_chapter='MSP XMP1'
        def decorate(self,c,doc):
            if doc.page==1: return
            c.saveState(); c.setStrokeColor(colors.HexColor('#c9d7de')); c.setLineWidth(.5); c.line(M,H-31,W-M,H-31)
            c.setFont('Manual-Bold',8); c.setFillColor(navy); c.drawString(M,H-23,'MSP XMP1')
            c.setFont('Manual',7.5); c.setFillColor(muted); c.drawRightString(W-M,H-23,'BEDIENHANDBUCH')
            c.line(M,32,W-M,32); c.drawString(M,20,self.current_chapter[:95]); c.drawRightString(W-M,20,str(doc.page)); c.restoreState()
        def afterFlowable(self,f):
            if hasattr(f,'bookmark'):
                self.canv.bookmarkPage(f.bookmark,fit='FitH',top=self.frame._y+f.height+f.getSpaceAfter())
                self.canv.addOutlineEntry(f.outline,f.bookmark,level=f.outline_level,closed=f.outline_level>0)
                if f.bookmark.startswith('topic-'): self.topic_pages[int(f.bookmark[6:])]=self.page
                if getattr(f,'toc',False): self.notify('TOCEntry',(f.toc_level,f.outline,self.page,f.bookmark))
            if hasattr(f,'chapter_title'): self.current_chapter=f.chapter_title
    class Cover(Flowable):
        def __init__(self):
            Flowable.__init__(self)
            self.width=CW; self.height=H-100
        def draw(self):
            c=self.canv; hh=self.height
            c.setFillColor(navy); c.rect(-M,hh-370,W,430,fill=1,stroke=0)
            c.setFillColor(colors.HexColor('#4bd4c3')); c.setFont('Manual-Bold',9); c.drawString(0,hh-44,'TECHNISCHE DOKUMENTATION')
            c.setFillColor(colors.white); c.setFont('Manual-Bold',53); c.drawString(-2,hh-128,'MSP XMP1')
            c.setFont('Manual',28); c.drawString(0,hh-171,'Bedienhandbuch')
            c.setFont('Manual',11); c.setFillColor(colors.HexColor('#d7e7ee'))
            c.drawString(0,hh-216,'Konfiguration, Bedienung und Diagnose')
            c.drawString(0,hh-234,'der XMP1-Applikation')
            for k,label in enumerate(['07  HAUPTKAPITEL','244  HILFETHEMEN','125  ABBILDUNGEN']):
                c.setFont('Manual-Bold',9); c.drawString(k*170,hh-321,label)
            c.setFillColor(teal); c.rect(0,hh-411,40,4,fill=1,stroke=0)
            c.setFillColor(navy); c.setFont('Manual-Bold',15); c.drawString(0,hh-447,'Vollständige digitale Ausgabe')
            c.setFont('Manual',10); c.setFillColor(ink)
            for k,line in enumerate(['Aus der originalen Windows-Hilfedatei XMP1.HLP.', 'Mit Inhaltsverzeichnis, Querverweisen und Stichwortregister.', 'Originaltexte, Bildschirmabbildungen und technische Zeichnungen.']): c.drawString(0,hh-477-k*18,line)
            c.setFont('Manual',8); c.setFillColor(muted); c.drawString(0,30,'QUELLE  XMP1.HLP     |     Originalvermerk: ® PET2BK')
            c.drawString(0,15,'Neu gesetzte Ausgabe · 27. September 2026')
    story=[Cover(),PageBreak()]
    def heading(text,key,level,toclevel=None):
        p=Paragraph(html.escape(text),styles['chapter' if level==0 else 'h'+str(min(level,3))])
        p.bookmark=key; p.outline=text; p.outline_level=level; p.toc=toclevel is not None; p.toc_level=toclevel
        return p
    story.append(heading('Hinweise zur Ausgabe','hinweise',0))
    notes=[
        'Dieses Handbuch enthält den vollständigen Inhalt der bereitgestellten WinHelp-Datei XMP1.HLP. Die sieben Hauptkapitel und die Reihenfolge aller Themen stammen aus dem Original-Inhaltsverzeichnis. Die ergänzte Abschnittsnummerierung macht die Hierarchie in der digitalen und gedruckten Fassung sichtbar.',
        'Texte und technische Angaben wurden unverändert übernommen. Die beschriebenen Systemanforderungen, Betriebssysteme und Bedienabläufe entsprechen dem historischen Stand der Quelldatei; sie wurden nicht auf heutige Systeme umgeschrieben.',
        'Das Inhaltsverzeichnis, die blauen Querverweise und das Stichwortregister sind anklickbar. Die seitliche Lesezeichenansicht Ihres PDF-Programms bildet alle Themen ab. Mit Strg + F durchsuchen Sie den Text. Eine komfortable Volltextsuche und vergrößerbare Abbildungen bietet zusätzlich das HTML-Handbuch.',
        '125 Originalabbildungen sind an den vorgesehenen Stellen enthalten: 106 Bitmap-Grafiken und 19 Vektorgrafiken. Letztere wurden mit 300 dpi für die Darstellung aufbereitet. Separate Audio- oder Videoressourcen sind in der HLP-Datei nicht enthalten.',
        'Zur Prüfung wurden zwei unabhängige Verfahren verwendet. Sämtliche sichtbaren Texte stimmen nach Vereinheitlichung der Leerzeichen überein. Alle 243 internen Querverweise führen zu vorhandenen Themen. Die Originaldatei und die dekompilierten Quellen liegen dem Gesamtpaket bei.',
    ]
    story.extend(Paragraph(html.escape(s),body) for s in notes)
    story.append(Spacer(1,14)); story.append(Paragraph('Originalquelle: XMP1.HLP · Quellvermerk: ® PET2BK',styles['small']))
    story.append(PageBreak()); story.append(heading('Inhaltsverzeichnis','inhalt',0))
    toc=TableOfContents(); toc.levelStyles=[ParagraphStyle('toc'+str(i),fontName='Manual-Bold' if i<2 else 'Manual',fontSize=10 if i==0 else 8.6,
        leading=15 if i==0 else 12,leftIndent=i*13,firstLineIndent=0,spaceBefore=7 if i==0 else 2,textColor=navy if i<2 else ink,rightIndent=25) for i in range(6)]
    toc.dotsMinLevel=0; story.append(toc); story.append(PageBreak())

    def inline(r):
        s=html.escape(r['text']).replace('\n','<br/>').replace('\t','&#160;&#160;&#160;')
        if r['style']['f']==4: s=s.replace('·','•')
        if r['style']['b']: s=f'<b>{s}</b>'
        if r['style']['i']: s=f'<i>{s}</i>'
        if r.get('link'):
            i=CONTEXT[r['link'].split('>')[0]]
            s=f'<link href="#topic-{i}" color="#087c86"><u>{s}</u></link>'
        elif r['style']['ul']: s=f'<u>{s}</u>'
        return s
    def flows(blocks,width=CW,cell=False):
        result=[]
        for b in blocks:
            if b['kind']=='p':
                txt=''.join(r['text'] for r in b['runs'])
                imgs=list(re.finditer(r'\{bm[clr] (bm\d+)\.(?:BMP|WMF)\}',txt))
                if imgs:
                    buffered=[]
                    for r in b['runs']:
                        for part in re.split(r'(\{bm[clr] bm\d+\.(?:BMP|WMF)\})',r['text']):
                            marker=re.fullmatch(r'\{bm[clr] (bm\d+)\.(?:BMP|WMF)\}',part)
                            if not marker:
                                if part: buffered.append(dict(r,text=part))
                                continue
                            if any(x['text'].strip() for x in buffered): result.extend(flows([dict(b,runs=buffered)],width,cell))
                            buffered=[]
                            path=OUT/'medien'/f'{marker[1]}.png'
                            with PILImage.open(path) as im: iw,ih=im.size
                            scale=min(width/iw,530/ih,.75 if iw<1000 else .48)
                            pic=Image(str(path),width=iw*scale,height=ih*scale)
                            pic.hAlign='LEFT'; pic.spaceBefore=6; pic.spaceAfter=10
                            result.append(pic)
                    if any(x['text'].strip() for x in buffered): result.extend(flows([dict(b,runs=buffered)],width,cell))
                    continue
                text=''.join(inline(r) for r in b['runs'])
                ps=copy.copy(body)
                if cell:
                    ps.fontSize=8.3 if width>37 else 7.5; ps.leading=ps.fontSize+3; ps.spaceAfter=2
                else:
                    size=max(r['style']['fs'] for r in b['runs'])
                    if size>=22 and not any(r.get('link') for r in b['runs']):
                        ps.fontSize=10.5; ps.leading=14.5; ps.spaceBefore=6; ps.keepWithNext=True
                    ps.leftIndent=min(28,b['style']['li']/20)
                if b['style']['align']=='center': ps.alignment=1
                result.append(Paragraph(text,ps))
            else:
                widths,grid=table_grid(b); ws=[w/sum(widths)*width for w in widths]
                data=[]; commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,-1),.35,colors.HexColor('#d4dfe5'))]
                for rownum,cells in enumerate(grid):
                    row=['']*len(widths)
                    for c in cells:
                        row[c['col']]=flows(c['blocks'],sum(ws[c['col']:c['col']+c['span']])-10,True) or ''
                        if c['span']>1: commands.append(('SPAN',(c['col'],rownum),(c['col']+c['span']-1,rownum)))
                    data.append(row)
                    if len(cells)==1 and len(widths)>1:
                        commands.append(('BACKGROUND',(0,rownum),(-1,rownum),colors.HexColor('#e4f0f1')))
                    elif rownum%2: commands.append(('BACKGROUND',(0,rownum),(-1,rownum),colors.HexColor('#f4f7f9')))
                repeat=2 if len(widths)==9 else 1 if len(grid)>3 else 0
                if repeat: commands.append(('BACKGROUND',(0,0),(-1,repeat-1),colors.HexColor('#e6edf2')))
                table=LongTable(data,colWidths=ws,repeatRows=repeat,hAlign='LEFT',spaceBefore=7,spaceAfter=12)
                table.setStyle(TableStyle(commands)); result.append(table)
        return result

    story.append(heading('Original-Inhaltsverzeichnis','topic-0',0))
    story.extend(flows(TOPICS[0][1:])); story.append(PageBreak())
    for ch in CHAPTERS:
        hp=heading(f'{ch["number"]:02d}  {ch["title"]}',f'chapter-{ch["number"]}',0,0)
        hp.chapter_title=ch['title']; story.append(hp)
        for i in ORDER:
            m=META[i]
            if m['chapter']!=ch['title']: continue
            story.append(heading(m['number']+'  '+m['title'],f'topic-{i}',m['level'],m['level']))
            story.extend(flows(TOPICS[i][1:]))
        story.append(PageBreak())
    ip=heading('Stichwortregister','stichwoerter',0,0); ip.chapter_title='Stichwortregister'; story.append(ip)
    story.append(Paragraph('Originale Suchbegriffe der Hilfedatei mit anklickbaren Abschnittsnummern.',body))
    for e in INV['index']:
        targets=e['topics'] or ([e['topic']] if e['topic'] is not None else [])
        refs=' · '.join(f'<link href="#topic-{i}" color="#087c86">{META[i]["number"]}</link>' for i in targets)
        story.append(Paragraph(f'<b>{html.escape(e["label"])}</b> &#160; {refs}',body))
    PDF=ROOT/'build/pdf/XMP1_Handbuch.pdf'; PDF.parent.mkdir(parents=True,exist_ok=True)
    doc=ManualDoc(PDF); doc.multiBuild(story)
    (QA/'pdf_topic_pages.json').write_text(json.dumps(doc.topic_pages),encoding='utf8')
    print('PDF:',doc.page,'pages')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Handbuch aus den archivierten Quellen nach build/ erzeugen.')
    parser.add_argument('--html-only',action='store_true',help='Nur HTML erzeugen; benötigt keine Windows-Schriften.')
    args=parser.parse_args()
    if diffs: raise SystemExit('Textvergleich fehlgeschlagen; siehe Modellprüfung.')
    model=data_model()
    (QA/'model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf8')
    make_html()
    if not args.html_only: make_pdf()
    print('Topics:',len(TOPICS),'Links:',len(P.links),'Text differences:',len(diffs))
