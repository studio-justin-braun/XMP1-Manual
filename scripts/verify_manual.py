from pathlib import Path
import sys, json, re, argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import pymupdf
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
import build_manual as b

parser=argparse.ArgumentParser(description='Texte, Links, Bilder und PDF-Seiten prüfen und rendern.')
parser.add_argument('--artifact-root',type=Path,default=ROOT,help='Ordner mit Handbuch/ und pdf/ (Standard: Repository).')
args=parser.parse_args()
QA=ROOT/'build/qa'; QA.mkdir(parents=True,exist_ok=True)
pdf=pymupdf.open(args.artifact_root/'pdf/XMP1_Handbuch.pdf')
alltext='\n'.join(p.get_text(clip=pymupdf.Rect(40,40,p.rect.width-40,p.rect.height-40),sort=False) for p in pdf)
normalize=lambda s:re.sub(r'\s+','',s).replace('\u00ad','').replace('·','•')
normtext=normalize(alltext)
missing=[]
for i,t in enumerate(b.TOPICS):
    for p in b.paragraphs(t):
        text=re.sub(r'\{bm[clr] bm\d+\.(?:BMP|WMF)\}','',''.join(r['text'] for r in p['runs'])).strip()
        if text and normalize(text) not in normtext: missing.append({'topic':i,'text':text})
links=[(n+1,l) for n,p in enumerate(pdf) for l in p.get_links()]
invalid=[(n,l) for n,l in links if l['kind']==1 and not 0<=l.get('page',-1)<len(pdf)]
outbounds=[]
for n,p in enumerate(pdf):
    for block in p.get_text('dict')['blocks']:
        if block['type']!=0:continue
        for line in block['lines']:
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                if x0<-1 or x1>p.rect.width+1 or y0<-1 or y1>p.rect.height+1:
                    outbounds.append({'page':n+1,'text':span['text'],'bbox':span['bbox']})
soup=BeautifulSoup((args.artifact_root/'Handbuch/index.html').read_text(encoding='utf8'),'html.parser')
ids={e['id'] for e in soup.select('[id]')}
badlinks=[a['href'] for a in soup.select('a[href^="#"]') if a['href'][1:] not in ids]
outline_pages={re.sub(r'\s+',' ',title):page for _,title,page in pdf.get_toc()}
topic_pages={str(i):outline_pages[re.sub(r'\s+',' ','Original-Inhaltsverzeichnis' if i==0 else m['number']+' '+m['title'])] for i,m in b.META.items()}
report=dict(pdf_pages=len(pdf),pdf_images=sum(len(p.get_image_info()) for p in pdf),pdf_links=len(links),pdf_bookmarks=len(pdf.get_toc()),
    missing_pdf_paragraphs=missing,invalid_pdf_links=invalid,out_of_bounds_text=outbounds,
    html_topics=len(soup.select('section.topic')),html_images=len(soup.select('section.topic img')),html_bad_links=badlinks,
    original_links=len(b.P.links),source_text_differences=b.diffs,original_tables=sum(x['kind']=='table' for t in b.TOPICS for x in t),
    original_table_rows=sum(len(x['rows']) for t in b.TOPICS for x in t if x['kind']=='table'),
    original_table_cells=sum(len(r['cells']) for t in b.TOPICS for x in t if x['kind']=='table' for r in x['rows']))
(QA/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
assert not (missing or invalid or outbounds or badlinks or b.diffs), 'Inhalt oder Layout fehlerhaft; siehe build/qa/validation.json'
assert report['html_topics']==244 and report['html_images']==report['pdf_images']==125
# Render every PDF page; contact sheets allow inspection of all page transitions.
thumbs=[]
for i,page in enumerate(pdf):
    pix=page.get_pixmap(matrix=pymupdf.Matrix(.5,.5),alpha=False)
    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    thumbs.append(im)
for start in range(0,len(thumbs),20):
    canvas=Image.new('RGB',(5*318,4*450),'#dce5eb'); draw=ImageDraw.Draw(canvas)
    for offset,im in enumerate(thumbs[start:start+20]):
        x=(offset%5)*318+10;y=(offset//5)*450+20
        canvas.paste(im,(x,y));draw.text((x,y-15),str(start+offset+1),fill='black')
    canvas.save(QA/f'contact-{start+1:03d}.jpg',quality=88)
samples={0,1,2,10,len(pdf)-1}
for i in [19,35,92,117,128,233,238,243]:
    p=topic_pages[str(i)]-1;samples.add(p);samples.add(min(len(pdf)-1,p+1))
for i in sorted(samples):
    pdf[i].get_pixmap(matrix=pymupdf.Matrix(1.3,1.3),alpha=False).save(QA/f'page-{i+1:03d}.png')
