from pathlib import Path
import fitz
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'tmp/pdfs';out.mkdir(parents=True,exist_ok=True)
files=list((ROOT/'output/pdf').glob('*.pdf'))+[ROOT/'documentacion/rubrica-evaluacion-mocap-retargeting.pdf']
for f in files:
    doc=fitz.open(f);thumbs=[]
    for i,p in enumerate(doc):
        pix=p.get_pixmap(matrix=fitz.Matrix(1.3,1.3))
        path=out/f'{f.stem}_{i+1}.png';pix.save(path)
        im=Image.open(path).convert('RGB');im.thumbnail((600,850));thumbs.append(im)
    for j in range(0,len(thumbs),2):
        sheet=Image.new('RGB',(1220,870),(220,220,220))
        for k,im in enumerate(thumbs[j:j+2]):sheet.paste(im,(10+610*k,10))
        sheet.save(out/f'{f.stem}_sheet_{j//2}.png')
    print(f.name,len(doc),'pages')
