"""Create presentation sheets, a PDF dossier, and a verified portable ZIP.

Run with system Python after render_viajero.py and validate_viajero.py.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import hashlib
import json
import zipfile
import math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"entrega"
OUT.mkdir(exist_ok=True)
FONT="/usr/share/fonts/TTF/DejaVuSans.ttf"
if not Path(FONT).exists():
    FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD=FONT.replace("Sans.ttf","Sans-Bold.ttf")
pdfmetrics.registerFont(TTFont("Body",FONT))
pdfmetrics.registerFont(TTFont("Bold",BOLD))
INK="#15232f";PAPER="#f2ede3";GOLD="#b78b4c";MUTED="#53616b"
W,H=842,595


def sheet(paths,labels,path,cols=4,size=(450,600)):
    rows=math.ceil(len(paths)/cols);w,h=size
    im=Image.new("RGB",(cols*w,rows*(h+46)),PAPER)
    draw=ImageDraw.Draw(im);font=ImageFont.truetype(FONT,20)
    for i,(p,label) in enumerate(zip(paths,labels)):
        photo=Image.open(ROOT/p).convert("RGB");photo.thumbnail((w,h))
        x=(i%cols)*w;y=(i//cols)*(h+46)
        im.paste(photo,(x+(w-photo.width)//2,y))
        draw.text((x+16,y+h+10),label,fill=INK,font=font)
    im.save(ROOT/path)


def paragraph(c,text,x,y,width,size=11,color=INK,leading=17):
    c.setFont("Body",size);c.setFillColor(HexColor(color))
    words=text.split();line=""
    for word in words:
        candidate=(line+" "+word).strip()
        if pdfmetrics.stringWidth(candidate,"Body",size)>width and line:
            c.drawString(x,y,line);y-=leading;line=word
        else:line=candidate
    if line:c.drawString(x,y,line);y-=leading
    return y


def photo(c,path,x,y,w,h):
    p=ROOT/path
    assert p.is_file(),f"Falta render para dossier: {p}"
    im=Image.open(p)
    factor=min(w/im.width,h/im.height)
    iw=im.width*factor;ih=im.height*factor
    c.drawImage(ImageReader(im),x+(w-iw)/2,y+(h-ih)/2,iw,ih,mask="auto")


def heading(c,kicker,title,num):
    c.setFillColor(HexColor(PAPER));c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(HexColor(GOLD));c.setFont("Bold",10);c.drawString(38,H-35,kicker.upper())
    c.setFillColor(HexColor(INK));c.setFont("Bold",25);c.drawString(38,H-70,title)
    c.setStrokeColor(HexColor(GOLD));c.line(38,32,W-38,32)
    c.setFont("Body",8);c.drawString(38,18,"VIAJERO ENTRE ÉPOCAS  /  BLENDER  /  20 OCT 2026")
    c.drawRightString(W-38,18,f"{num:02d}")


def dossier(report,evidence):
    pdf_path=OUT/"Viajero_Entre_Epocas_Dossier.pdf"
    c=canvas.Canvas(str(pdf_path),pagesize=(W,H))
    c.setTitle("Viajero entre Épocas — dossier de modelado")
    c.setAuthor("Proyecto de Leonidas")
    heading(c,"Personaje 3D · dossier de trabajo","Viajero entre Épocas",1)
    photo(c,"renders/final/viajero_presentacion.png",400,42,405,465)
    y=450
    for text in [
        "Un joven que recorre tiempos y culturas para comprender a las personas, y cambia con cada encuentro.",
        "Personaje vestido, materiales nativos, accesorios independientes y rig FK. Escena editable para presentar y seguir trabajando.",
        f"Altura verificada: {report['height_m']:.3f} m. {report['meshes']} mallas y {report['bones']} huesos. Blender {report['blender']}.",
        "Versión de presentación: el parecido facial, la retopología y las deformaciones extremas requieren una revisión adicional."]:
        y=paragraph(c,text,40,y,325,12,leading=19)-22
    c.showPage()
    heading(c,"01 · Identidad y narrativa","La curiosidad como motor",2)
    photo(c,"referencias/personaje_aprobado/01_concepto_viajero_entre_epocas.png",360,85,445,345)
    y=460
    for text in [
        "22 años. Curioso, reflexivo, empático y vulnerable. No es un conquistador ni un soldado: busca conocer otros mundos.",
        "En su primer viaje encuentra una comunidad que conserva sus historias oralmente. Debe aprender a escuchar versiones distintas de un mismo conflicto antes de actuar.",
        "El abrigo mezcla épocas; el bolso reúne experiencias. La bufanda sugiere calidez humana y el talismán circular representa el tiempo compartido.",
        "La imagen de la derecha es una referencia proporcionada, no un render creado durante esta entrega."]:
        y=paragraph(c,text,40,y,285,11)-15
    paragraph(c,"La rúbrica pide el storytelling escrito a mano: adaptar y transcribir personalmente esta propuesta.",380,64,410,9)
    c.showPage()
    heading(c,"02 · Proceso real","De la base al personaje vestido",3)
    for x,path,label in [
        (40,"renders/cuerpo_base/blockout_front.png","01 / Blockout original"),
        (295,"renders/cuerpo_base/cuerpo_base_side.png","02 / Perfil elegido por el usuario"),
        (550,"renders/turnaround/frente.png","03 / Ensamblaje nuevo")]:
        photo(c,path,x,115,245,380)
        paragraph(c,label,x,94,245,10)
    paragraph(c,"Se conservaron 01–03. La nueva cabeza, manos, prendas y accesorios son editables por piezas. Las fotografías no son capturas métricas calibradas.",40,65,750,10)
    c.showPage()
    heading(c,"03 · Silueta","Turnaround ortográfico",4)
    names=["frente","perfil_izquierdo","espalda","tres_cuartos"]
    for i,name in enumerate(names):
        photo(c,f"renders/turnaround/{name}.png",35+i*194,105,190,390)
        paragraph(c,["Frente","Perfil izquierdo","Espalda","Tres cuartos"][i],40+i*194,84,185,10)
    paragraph(c,"Misma escala y pose A. La cámara de presentación de la portada es perspectiva.",40,58,730,10)
    c.showPage()
    heading(c,"04 · Construcción modular","Detalles que cuentan la historia",5)
    for i,(p,label) in enumerate([
        ("renders/accesorios/botas.png","Botas: suelas, caña, cordones y ojales"),
        ("renders/accesorios/bolso.png","Bolso: tapa, costuras y hebillas"),
        ("renders/accesorios/talisman.png","Talismán: latón, grabados y piedra azul"),
        ("renders/rostro/rostro_frente.png","Rostro y gafas: interpretación inicial")]):
        x=40+(i%2)*390;y=285-(i//2)*220
        photo(c,p,x,y,368,190)
        paragraph(c,label,x,y-15,368,10)
    c.showPage()
    heading(c,"05 · Shading e iluminación","Materiales nativos de Blender",6)
    palette=[("Abrigo","#465d78"),("Camisa","#d2bc99"),("Chaleco","#65492f"),
             ("Bufanda","#8e3932"),("Pantalón","#3b3d43"),("Latón","#b99453")]
    for i,(label,color) in enumerate(palette):
        x=40+i*127;c.setFillColor(HexColor(color));c.roundRect(x,422,112,62,5,fill=1,stroke=0)
        paragraph(c,label,x,408,115,10)
    paragraph(c,"Esquema de conexiones utilizado en tejidos",40,363,720,13)
    boxes=[(40,"Generated"),(185,"Noise"),(330,"Color Ramp"),(510,"Principled"),(685,"Output")]
    for x,label in boxes:
        c.setFillColor(HexColor(INK));c.roundRect(x,302,115,38,5,fill=1,stroke=0)
        paragraph(c,label,x+9,316,105,10,"#ffffff")
    c.setStrokeColor(HexColor(GOLD))
    for a,b in zip(boxes,boxes[1:]):c.line(a[0]+115,321,b[0],321)
    paragraph(c,"Otra rama Noise → Bump controla el microrelieve. Metales, piel, cuero, vidrio y piedra tienen parámetros distintos. Diagrama derivado de los nodos reales; no es una captura del editor.",40,276,755,10)
    y=214
    for light in evidence["lights"]:
        y=paragraph(c,f"{light['name']}: {light['power_w']:.0f} W · tamaño {light['size_m']:.1f} m · posición "+", ".join(f"{v:.1f}" for v in light["position"]),40,y,760,11)-6
    paragraph(c,"Cycles / OptiX, RTX 3070, AgX. UV automáticas; sin mapas PBR horneados. El .blend conserva el acabado completo. Exportaciones externas pueden verse diferentes.",40,103,755,11)
    c.showPage()
    heading(c,"06 · Movimiento","Rig FK y poses de comprobación",7)
    for i,(name,label) in enumerate([
        ("02_T_pose","T-pose"),("05_Codos_flexionados","Codos flexionados"),
        ("06_Paso_caminata","Paso de prueba"),("13_Presentacion","Presentación")]):
        photo(c,f"renders/poses/{name}.png",35+i*194,147,190,345)
        paragraph(c,label,40+i*194,128,185,10)
    paragraph(c,"Las 13 acciones son poses sostenidas, no ciclos animados. Huesos corporales, dedos, ojos, bolso y telas. Los pesos y el rig existen; sentarse/agacharse todavía exige correctivos de ropa.",40,97,755,11)
    paragraph(c,"Rostro con shape keys iniciales. Sin IK, mandíbula articulada ni sistema completo de diálogo.",40,60,755,10)
    c.showPage()
    heading(c,"07 · Entrega y próximos pasos","Archivos para continuar",8)
    y=465
    for text in [
        "Escena principal: blender/personaje_final.blend",
        "Etapas editables: blender/01_referencias.blend hasta 10_rigging.blend",
        "Guía: GUIA_BLENDER.md · Evidencias: docs/entrega_examen.md",
        "Biblioteca: assets/materiales/viajero_materiales.blend",
        "Intercambio: exports/glb/viajero.glb y exports/fbx/viajero.fbx",
        "Skills: viajero-modelado, viajero-materiales y viajero-rig",
        "Validación estructural: docs/validacion_viajero.json",
        "Pendientes: parecido facial, cabello, retopología, pesos, faldones y texturas horneadas."]:
        y=paragraph(c,text,40,y,750,12)-17
    paragraph(c,"Conservar una copia antes de editar. Reconstruir con scripts no incorpora automáticamente cambios manuales. Los originales y referencias permanecen disponibles.",40,104,750,11)
    c.showPage()
    c.save()
    return pdf_path


def main():
    report=json.loads((ROOT/"docs/validacion_viajero.json").read_text())
    evidence=json.loads((ROOT/"docs/evidencia_escena.json").read_text())
    sheet([f"renders/turnaround/{n}.png" for n in ["frente","perfil_izquierdo","espalda","tres_cuartos"]],
          ["FRENTE","PERFIL","ESPALDA","TRES CUARTOS"],"renders/final/lamina_turnaround.jpg")
    actions=report["actions"]
    sheet([f"renders/poses/{n}.png" for n in actions],actions,
          "renders/evidencias/lamina_poses.jpg",cols=5,size=(288,384))
    dossier(report,evidence)
    files=[]
    for folder in ["blender","referencias","renders","scripts","docs","assets/materiales","exports",".agents/skills"]:
        for p in (ROOT/folder).rglob("*"):
            if not p.is_file():continue
            rel=p.relative_to(ROOT)
            if any(part in {"respaldo","__pycache__","archive_robotics","blender-robotics"} for part in rel.parts):continue
            if p.name.endswith((".blend1",".pyc")) or p.name=="preview.png":continue
            if "anteriores" in p.stem or p.name=="README_pipeline_anterior.md":continue
            if p.name=="manifest_entrega.json":continue
            files.append(p)
    files += [ROOT/p for p in ["README.md","GUIA_BLENDER.md","ESTADO.md","PLAN_PROYECTO.md"]]
    files.append(OUT/"Viajero_Entre_Epocas_Dossier.pdf")
    files=sorted(set(files))
    manifest={"files":[{"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,
                 "sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
    m=ROOT/"docs/manifest_entrega.json";m.write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
    files.append(m)
    archive=OUT/"Viajero_Entre_Epocas.zip"
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for p in files:z.write(p,Path("Viajero_Entre_Epocas")/p.relative_to(ROOT))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None,"CRC incorrecto"
    print(f"PACKAGE_OK: {len(files)} archivos, ZIP {archive.stat().st_size/1024**2:.1f} MiB")


if __name__=="__main__":
    main()
