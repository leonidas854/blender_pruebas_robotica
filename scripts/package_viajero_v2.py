"""Create an evidence-based PDF and reproducible ZIP of the reviewed v2 delivery."""
import hashlib
import json
import zipfile
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'entrega/v2';OUT.mkdir(parents=True,exist_ok=True)
W,H=A4


def draw_image(c,path,x,y,w,h):
    image=ImageReader(str(ROOT/path));iw,ih=image.getSize();scale=min(w/iw,h/ih)
    c.drawImage(image,x+(w-iw*scale)/2,y+(h-ih*scale)/2,iw*scale,ih*scale,mask='auto')


def paragraph(c,text,x,y,w,size=10):
    style=ParagraphStyle('body',fontName='Helvetica',fontSize=size,leading=size*1.45,textColor=colors.black)
    p=Paragraph(text,style);_,height=p.wrap(w,H);p.drawOn(c,x,y-height);return y-height-12


def header(c,title,number):
    c.setFillColor(colors.black);c.setFont('Helvetica-Bold',20);c.drawString(36,H-50,title)
    c.setFont('Helvetica',9);c.drawString(36,H-69,'Viajero entre Epocas | Revision escultorica v2 | 22 noviembre 2026')
    c.line(36,36,W-36,36);c.setFont('Helvetica',8)
    c.drawString(36,23,'Personaje, rig FK y renders. No incluye captura de movimiento.');c.drawRightString(W-36,23,str(number))


def report():
    validation=json.loads((ROOT/'docs/v2/validacion.json').read_text())
    path=OUT/'Viajero_v2_Informe_y_Evidencias.pdf';c=canvas.Canvas(str(path),pagesize=A4)
    c.setTitle('Viajero entre Epocas — Entrega escultorica v2')
    c.setAuthor('Revision asistida en Blender; evidencia de la sesion del proyecto')
    header(c,'El Viajero: nueva superficie',1)
    draw_image(c,'renders/v2/presentacion.png',36,114,W-72,H-204)
    paragraph(c,'Anatomía nueva y continua; rostro interpretado a partir de fotografías; prendas, cabello y materiales revisados. Archivo maestro editable: <b>blender/v2/viajero_esculpido.blend</b>.',36,105,W-72)
    c.showPage();header(c,'Comparación de revisiones',2)
    draw_image(c,'renders/final/viajero_presentacion.png',36,175,(W-84)/2,540)
    draw_image(c,'renders/v2/presentacion.png',W/2+6,175,(W-84)/2,540)
    c.setFont('Helvetica-Bold',11);c.drawString(56,158,'v1 conservada');c.drawString(W/2+24,158,'v2 revisada')
    paragraph(c,'Cambios: unión de la anatomía, reconstrucción del pantalón y bufanda, integración de botas, cabello remallado, pliegues localizados y paleta menos lavada. Cámaras e iluminación difieren: esta comparación es visual y no una medición de semejanza.',36,135,W-72)
    c.showPage();header(c,'Silueta desde cuatro vistas',3)
    for name,x,y in [('frente',36,410),('perfil',W/2+5,410),('espalda',36,80),('tres_cuartos',W/2+5,80)]:
        draw_image(c,'renders/v2/'+name+'.png',x,y,(W-84)/2,315)
        c.setFont('Helvetica',10);c.drawString(x+12,y-12,name.replace('_',' ').capitalize())
    c.showPage();header(c,'Rostro y referencia de diseño',4)
    draw_image(c,'renders/v2/rostro_frente.png',36,405,255,285)
    draw_image(c,'renders/v2/rostro_perfil.png',304,405,255,285)
    draw_image(c,'referencias/personaje_aprobado/01_concepto_viajero_entre_epocas.png',36,115,W-72,270)
    paragraph(c,'El rostro sigue siendo una interpretación estilizada, no fotogrametría ni una coincidencia facial certificada. Se consultaron las cinco fotografías personales y el concepto aprobado; la mandíbula, ojos y peinado admiten más refinamiento.',36,105,W-72,9)
    c.showPage();header(c,'Anatomía y prueba de deformación',5)
    draw_image(c,'renders/v2/anatomia_continua.png',36,235,(W-84)/2,470)
    draw_image(c,'renders/v2/anatomia_flexion.png',W/2+6,235,(W-84)/2,470)
    a=validation['anatomy']
    paragraph(c,f"La anatomía contiene <b>{a['vertices']:,} vértices</b>, <b>{a['components']} componente conexo</b>, {a['boundary_edges']} bordes abiertos y {a['nonmanifold_edges']} aristas no manifold. La superficie se creó por unión voxel a 1,8 mm y relajación. La densidad favorece escultura; no reemplaza una retopología para animación facial.",36,218,W-72)
    paragraph(c,'Los pesos normalizados vinculan la malla al rig FK de 57 huesos. La pose mostrada combina flexión de codos y una rodilla. Son poses sintéticas sostenidas, no captura de movimiento. La conectividad preservada no certifica por sí sola que todas las deformaciones extremas sean correctas.',36,130,W-72)
    c.showPage();header(c,'Prueba vestida y controles',6)
    draw_image(c,'renders/v2/prueba_codos_rodilla.png',36,165,W-72,550)
    paragraph(c,'Se revisaron frente, perfil, espalda y flexión. Se corrigieron penetraciones visibles de la camisa, pantorrillas, bufanda y bandolera. Las poses de sentado/agachado heredadas siguen necesitando correctivos de faldones y bolso. Rig FK sin IK ni simulación de tela.',36,140,W-72)
    c.showPage();header(c,'Validación y alcance de entrega',7)
    y=H-100
    for text in [
        f"<b>Resultado estructural: {validation['status']}.</b> Altura medida: {validation['height_m']:.6f} m. {validation['meshes']} mallas y {validation['bones']} huesos. Pesos normalizados, materiales y UV presentes. Escena reabierta en Blender {validation['blender']}.",
        '<b>Render:</b> Cycles, OptiX en NVIDIA GeForce RTX 4070 Laptop GPU, AgX, tres luces de área. Presentación 1800 × 2400 a 96 muestras; vistas 1200 × 1600 y rostro 1200 × 1200. Configuración registrada en docs/v2/escena.json.',
        '<b>Edición:</b> seleccionar Anatomia_Esculpida, mantener la acción 01_A_pose, ocultar prendas y entrar en Sculpt Mode. Guardar una copia antes de remallar: cambiar topología exige reconstruir pesos, UV y shape keys. Guía detallada en docs/v2/GUIA_ENTREGA.md.',
        '<b>Conservación:</b> la v1, el cuerpo base 03 y las referencias originales se mantienen. Los accesorios y el esqueleto se reutilizan; no se afirma haber rehecho desde cero cada pieza del personaje.',
        '<b>Límites:</b> parecido interpretado; malla densa sin retopología facial de producción; UV automáticas; materiales procedurales sin horneado PBR; no hay captura real, videos de persona, telemetría ni integración ROS 2 en esta entrega.',
        '<b>Rúbrica:</b> se prioriza volumen anatómico, identidad y deformación. La práctica completa solicita también dos modalidades de captura; el usuario eligió expresamente dejar esa fase para después. Este paquete no se presenta como cumplimiento total del laboratorio.',
        '<b>Mejora continua:</b> revisar parecido con el usuario, refinar manos/rostro/peinado, preparar retopología y correctivos de ropa, y después desarrollar la captura con evidencia real. Bitácora auténtica y especificación incluidas.',
        '<b>Integridad:</b> manifiesto SHA-256 del contenido en docs/v2/manifest_entrega.json. No se fabricaron commits de estudiantes, sesiones de captura ni aprobación artística.'
    ]: y=paragraph(c,text,36,y,W-72,10)
    c.save();return path


def package():
    validation=json.loads((ROOT/'docs/v2/validacion.json').read_text())
    if validation['status']!='PASS':raise RuntimeError('No empaquetar una validacion fallida')
    pdf=report()
    fixed=['blender/v2/viajero_esculpido.blend','blender/personaje_final.blend',
        'scripts/viajero_lib.py','scripts/build_viajero_v2.py','scripts/render_viajero_v2.py',
        'scripts/refine_viajero_v2.py','scripts/relax_viajero_v2_anatomy.py','scripts/blend_viajero_v2_anatomy.py','scripts/restore_viajero_v2_hands.py','scripts/fix_viajero_v2_layers.py','scripts/validate_viajero_v2.py',
        'scripts/start_blender_mcp.py','scripts/blender_mcp_client.py','scripts/package_viajero_v2.py',
        'renders/final/viajero_presentacion.png',str(pdf.relative_to(ROOT))]
    files=[ROOT/p for p in fixed]
    files+=list((ROOT/'scripts/viajero_v2').glob('*.py'))
    files+=list((ROOT/'docs/v2').glob('*.md'))
    files+=[ROOT/'docs/v2/validacion.json',ROOT/'docs/v2/escena.json']
    files+=list((ROOT/'renders/v2').glob('*.png'))
    files += [p for p in (ROOT/'referencias').rglob('*') if p.suffix.lower() in {'.png','.jpg','.jpeg'}]
    files+=list((ROOT/'documentacion').glob('*.pdf'))
    manifest=[]
    for path in sorted(set(files)):
        data=path.read_bytes();manifest.append({'path':str(path.relative_to(ROOT)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    manifest_path=ROOT/'docs/v2/manifest_entrega.json'
    manifest_path.write_text(json.dumps({'date':'2026-11-22','scope':'personaje, rig FK, renders','files':manifest},indent=2,ensure_ascii=False))
    zip_path=OUT/'Viajero_v2_Personaje_Rig_Renders.zip'
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as archive:
        for path in sorted(set(files+[manifest_path])):archive.write(path,path.relative_to(ROOT))
        archive.writestr('LEEME.txt','Abrir blender/v2/viajero_esculpido.blend con Blender 5.2.4.\nInforme: entrega/v2/Viajero_v2_Informe_y_Evidencias.pdf\nGuia: docs/v2/GUIA_ENTREGA.md\nV1 preservada solo como entrada reproducible. La nueva entrega es V2.\n')
    with zipfile.ZipFile(zip_path) as archive:
        assert archive.testzip() is None
        for item in manifest:
            assert hashlib.sha256(archive.read(item['path'])).hexdigest()==item['sha256']
    print(json.dumps({'pdf':str(pdf),'zip':str(zip_path),'files':len(manifest),'zip_bytes':zip_path.stat().st_size,'integrity':'PASS'},indent=2))


if __name__=='__main__':package()
