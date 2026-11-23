"""PDFs vectoriales con estética editorial de la referencia y evidencia medida."""
from pathlib import Path
import sys,json,csv,math,random
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,Color,white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mocap.core import OneEuro
OUT=ROOT/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
for name,file in [('Body','arial.ttf'),('Bold','arialbd.ttf'),('Title','ARIALNB.TTF'),('Mono','consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
W,H=595.276,841.89;M=42;CW=W-2*M
INK=HexColor('#16191D');RED=HexColor('#E73D46');PINK=HexColor('#F7DADD');BLUE=HexColor('#61759C');PALE=HexColor('#DDE3EE');PAPER=HexColor('#F5F4F1');GRAY=HexColor('#62666D')
validation=json.loads((ROOT/'docs/mocap/validation_blender.json').read_text())
bcheck=json.loads((ROOT/'docs/mocap/validation_B.json').read_text())
modal=json.loads((ROOT/'docs/mocap/validation_modal_integration.json').read_text())
qa=json.loads((ROOT/'docs/mocap/asset_qa.json').read_text())

class Doc:
    def __init__(self,name,label,accent=RED):
        self.path=OUT/name;self.c=canvas.Canvas(str(self.path),pagesize=(W,H));self.label=label;self.accent=accent;self.page=0
        self.c.setTitle(label);self.c.setAuthor('Proyecto Viajero - asistencia documentada en prompt_log.md')
    def new(self,kicker,title):
        if self.page:self.c.showPage()
        self.page+=1;c=self.c;c.setFillColor(PAPER);c.rect(0,0,W,H,fill=1,stroke=0)
        c.setFillColor(self.accent);c.rect(M,H-47,24,5,fill=1,stroke=0)
        c.setFont('Bold',8);c.drawString(M+33,H-47,kicker.upper())
        self.y=H-68;self.p(title,font='Title',size=27,leading=29,gap=13)
        c.setStrokeColor(INK);c.setLineWidth(.8);c.line(M,self.y,W-M,self.y);self.y-=17
        c.setFont('Body',7.4);c.setFillColor(GRAY);c.drawString(M,27,self.label+'  /  22 NOV 2026')
        c.drawRightString(W-M,27,f'{self.page:02d}')
    def p(self,text,font='Body',size=10.2,leading=14,gap=10,x=None,width=None,color=INK):
        x=M if x is None else x;width=CW if width is None else width
        style=ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,textColor=color)
        para=Paragraph(text,style);w,h=para.wrap(width,H)
        if self.y-h<52:raise ValueError(f'Overflow {self.label} page {self.page}: {text[:50]}')
        para.drawOn(self.c,x,self.y-h);self.y-=h+gap;return h+gap
    def head(self,text):self.p(text,font='Title',size=17,leading=19,gap=9)
    def box(self,title,text,tint=PINK):
        top=self.y;style=ParagraphStyle('box',fontName='Body',fontSize=10,leading=14)
        para=Paragraph(text,style);_,h=para.wrap(CW-28,H);height=h+46
        self.c.setFillColor(tint);self.c.rect(M,top-height,CW,height,fill=1,stroke=0)
        self.c.setFillColor(self.accent);self.c.rect(M,top-height,4,height,fill=1,stroke=0)
        self.y-=12;self.p(title,font='Bold',size=10,leading=13,gap=7,x=M+14,width=CW-28)
        self.p(text,x=M+14,width=CW-28,size=10,leading=14,gap=0)
        self.y=top-height-14
    def table(self,headers,rows,widths=None,size=9):
        widths=widths or [CW/len(headers)]*len(headers)
        st=ParagraphStyle('cell',fontName='Body',fontSize=size,leading=size+3,textColor=INK)
        hd=ParagraphStyle('hd',fontName='Bold',fontSize=size,leading=size+3,textColor=INK)
        values=[[Paragraph(escape(str(x)),hd) for x in headers]]+[[Paragraph(escape(str(x)),st) for x in r] for r in rows]
        t=Table(values,colWidths=widths,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PINK if self.accent==RED else PALE),
                              ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
                              ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
                              ('LINEBELOW',(0,0),(-1,0),1,INK),('LINEBELOW',(0,1),(-1,-1),.35,HexColor('#A0A3A7'))]))
        _,h=t.wrap(CW,H)
        if self.y-h<52:raise ValueError(f'Table overflow {self.label} {self.page}')
        t.drawOn(self.c,M,self.y-h);self.y-=h+15
    def pic(self,path,x,top,w,h):
        img=ImageReader(str(path));iw,ih=img.getSize();scale=min(w/iw,h/ih)
        self.c.drawImage(img,x+(w-iw*scale)/2,top-ih*scale,width=iw*scale,height=ih*scale,mask='auto')
    def code(self,text):
        self.p(escape(text).replace('\n','<br/>').replace(' ','&#160;'),font='Mono',size=8.2,leading=11,gap=14)
    def done(self):self.c.save();return self.path

def source(d,label,url):
    d.p(f'<b>{label}</b><br/><link href="{url}" color="#42597F">{url}</link>',size=8.3,leading=11,gap=8)

def chart(d,series,colors,height=130,yrange=None):
    x=M+30;y=d.y-height;w=CW-45;h=height-20;c=d.c
    values=[v for s in series for v in s];lo,hi=yrange or (min(values),max(values));span=hi-lo or 1
    c.setStrokeColor(HexColor('#D4D6DA'));c.setLineWidth(.4)
    for i in range(5):
        yy=y+i*h/4;c.line(x,yy,x+w,yy);c.setFont('Body',7);c.setFillColor(GRAY);c.drawRightString(x-6,yy-2,f'{lo+i*span/4:.2f}')
    for points,color in zip(series,colors):
        path=c.beginPath()
        for i,value in enumerate(points):
            xx=x+i/(len(points)-1)*w;yy=y+(value-lo)/span*h
            if i==0:path.moveTo(xx,yy)
            else:path.lineTo(xx,yy)
        c.setStrokeColor(color);c.setLineWidth(1.15);c.drawPath(path)
    d.y=y-18

def report_a():
    d=Doc('Informe_Camino_A.pdf','CAMINO A / INGENIERÍA LOCAL')
    d.new('Captura corporal y retargeting','DEL MOVIMIENTO HUMANO\nAL AVATAR Y ROS 2'.replace('\n','<br/>'))
    d.p('Viajero entre Épocas · implementación local, evidencia reproducible y límites de validación.',size=11,leading=15)
    top=d.y;d.pic(ROOT/'tmp/mocap/avatar_material.png',M,top,230,285)
    d.y=top-3
    d.p('UN AVATAR CON VOLUMEN',font='Title',size=18,leading=20,x=298,width=255)
    d.p('Se conserva la indumentaria del diseño existente. La copia de mocap incorpora una superficie anatómica cerrada, pesos normalizados y color facial proyectado desde la fotografía personal.',x=298,width=255)
    d.p('33 puntos estimados<br/>57 huesos del rig<br/>UDP local + TIMER<br/>Cuaterniones + telemetría',font='Bold',size=11,leading=18,x=298,width=255)
    d.y=top-300
    d.box('ESTADO REAL DE ESTA ENTREGA','Código, escenas y pruebas sintéticas disponibles. La captura personal, los videos de 1-2 minutos y la prueba visual en vivo siguen pendientes. No se presentan ensayos analíticos como captura del estudiante.')
    d.head('DOS CAMINOS, DOS CARPETAS')
    d.table(['Camino_A','Camino_B'],[['Productor MediaPipe + One Euro, UDP, receptor modal, avatar y muestra JointState.','Importación BVH/FBX, calibración corporal, retargeting y CSV. Informe comparativo independiente.']],size=10)
    d.p('Base documental: rúbrica técnica de mocap y guía de laboratorio entregadas en documentacion/. Uso de IA registrado en spec.md y prompt_log.md. No se crearon commits.',size=9,leading=12)

    d.new('01 / avatar obligatorio','ANATOMÍA, IDENTIDAD Y PESOS')
    top=d.y;d.pic(ROOT/'tmp/mocap/anatomia_reposo.png',M,top,245,230);d.pic(ROOT/'tmp/mocap/anatomia_flexion.png',M+265,top,245,230)
    d.y=top-242;d.p('Izquierda: reposo. Derecha: pose de ensayo. Son renders de la malla real; el cuerpo permanece cerrado bajo la deformación.',size=9,leading=12)
    d.table(['Comprobación','Resultado medido'],[['Cuerpo anatómico','227 722 vértices; 227 724 caras; una componente'],['Superficie','0 bordes abiertos; 0 aristas no manifold; 0 aristas inconsistentes'],['Rig y pesos','57 huesos; sin sumas de peso inválidas en la revisión'],['Escena de personaje','1 097 092 triángulos de malla base; incluye vestuario'],['Fotografía','Imagen personal de cuerpo completo empaquetada; proyección frontal localizada']],widths=[155,CW-155])
    d.box('ALCANCE DE LA REVISIÓN','El chequeo automático de asset pasa en perfil render. Conserva 19 advertencias: degeneraciones/UV heredadas de prendas, UV superpuestas de proyección y omisión del chequeo exhaustivo de colisiones por densidad. No se certifican todas las poses ni semejanza exacta.',tint=PALE)
    d.p('El original y la sesión previa se conservaron. No se reutilizan como evidencia los números del antiguo informe v2, cuyo archivo final no estaba disponible.',size=9,leading=12)

    d.new('02 / arquitectura','DATOS SEPARADOS DE LA INTERFAZ')
    d.table(['Etapa','Responsabilidad'],[['1. Productor externo','OpenCV convierte BGR a RGB; MediaPipe Tasks estima 33 world landmarks.'],['2. Procesamiento','Umbral de visibilidad 0,6; filtro One Euro por coordenada; vectores, ángulos y cuaterniones.'],['3. Transporte','JSON UTF-8 por UDP a 127.0.0.1:5005. Una copia va al puente ROS en 5006.'],['4. Blender','Socket no bloqueante y evento TIMER. El retargeter transforma orientación global a base local del hueso.'],['5. Salida','Pose del avatar; registro JSONL; estructura JointState opcional.']],widths=[135,CW-135])
    d.head('CONTRATO V1')
    d.code('{\n  "schema_version": 1, "session_id": "UUID",\n  "timestamp_ms": 1790000000000, "frame_id": 42,\n  "source": "webcam", "tracking": true,\n  "coordinate_space": "mediapipe_world_m",\n  "landmarks": {"0..32": {"name": "...",\n    "x": 0.1, "y": -0.4, "z": 0.02, "visibility": 0.98}},\n  "joint_rotations": {"left_elbow_flex_rad": 1.2}\n}')
    d.p('Esquema abreviado para lectura; no es un paquete completo. El código exige las 33 claves cuando tracking=true y rechaza NaN, valores fuera de rango y cuaterniones no unitarios.',size=9,leading=12)
    d.box('PÉRDIDA, REINICIO Y OCLUSIÓN','Se aplica el frame válido más reciente. Se rechazan duplicados y datos de más de 500 ms. Un UUID nuevo permite reiniciar frame_id. Un segmento ocluido conserva su pose; sin tracking por 500 ms el panel muestra STALE. Stop libera socket y temporizador.')

    d.new('03 / matemática','DIRECCIONES, BASES Y CUATERNIONES')
    d.head('DEL SENSOR AL CUERPO')
    d.code('MediaPipe -> Blender: (x, z, -y)\nBlender -> ROS cuerpo: (-y, x, z)\nUnidades: metros estimados / radianes / milisegundos\nCuaterniones JSON y Blender: [w, x, y, z]')
    d.p('Ambas transformaciones conservan orientación diestra. World landmarks tienen origen en caderas y no son posición absoluta calibrada en la habitación. El eje de cámara se verifica con entrada sin espejo y un gesto unilateral.')
    d.head('FLEXIÓN Y ARCO MÍNIMO')
    d.code('u = codo - hombro; v = muneca - codo\ntheta = acos(clamp(dot(u,v)/(norm(u)*norm(v)), -1, 1))\na,b unitarios: q = normalize([1 + dot(a,b), cross(a,b)])')
    d.p('La flexión vale 0 con el brazo extendido. Direcciones opuestas requieren elegir un eje perpendicular; vectores nulos se rechazan. Los cuaterniones evitan el bloqueo de Cardán de Euler, pero dos puntos no observan el twist axial del hueso.')
    d.head('EL PADRE TAMBIÉN GIRA')
    d.code('base = Qpadre * inverse(Rpadre_reposo) * Rhueso_reposo\nQlocal = inverse(base) * Qdeseada')
    d.p('Asignar Qdeseada directamente como rotación local duplicaría la influencia del padre. Se recorren los huesos en orden jerárquico, se conserva la escala y se mantiene la continuidad del signo q/-q. La orientación del hombro se resuelve desde su dirección, no desde el ángulo del codo.')
    d.box('LÍMITES CINEMÁTICOS','No hay IK de contacto ni traslación de raíz en el Camino A implementado. Los pies pueden deslizar. Los límites del puente son didácticos: no existe URDF de hardware en el proyecto. JointState comunica estado y no constituye una orden de actuación.')

    d.new('04 / señal y verificación','PRUEBAS QUE PUEDEN REPETIRSE')
    rng=random.Random(12);raw=[rng.gauss(0,.02) for _ in range(180)];f=OneEuro(beta=0);filtered=[f(x,i/30) for i,x in enumerate(raw)]
    d.p('Ensayo de señal estacionaria: ruido sintético de 2 cm de desviación estándar; min_cutoff=1 Hz, beta=0, 30 Hz. Gris: entrada. Rojo: salida. No son mediciones de una webcam.',size=9,leading=12)
    chart(d,[raw,filtered],[HexColor('#A8ADB5'),RED],height=140)
    d.code('fc = min_cutoff + beta * abs(derivada_filtrada)\nalpha = 1 / (1 + 1/(2*pi*fc*dt))')
    d.table(['Prueba','Resultado'],[['Núcleo Python','11 pruebas pasan: geometría, filtro, contrato, orden, sesiones, oclusión y UDP.'],['Retargeter A','180 frames; error direccional máximo '+f"{validation['max_direction_error_deg']:.7f}"+' grados.'],['Longitudes','Deriva máxima '+f"{validation['max_bone_length_drift_m']:.2e}"+' m.'],['Método modal','UDP real y eventos TIMER simulados: '+str(modal.get('applied',0))+' paquetes aplicados; prueba de STALE y liberación.'],['Retargeting B','180 frames; diferencia máxima frente a A < 0,000001 rad, excluyendo calibración.']],widths=[128,CW-128])
    d.p(f"Tiempo medio del adaptador con inserción de claves: {validation['mean_apply_and_keyframe_ms']:.2f} ms en este ensayo. Excluye inferencia, cámara, evaluación de escena y pantalla; no debe llamarse latencia extremo a extremo.",size=9,leading=12)
    d.box('VALIDACIÓN PENDIENTE EN VIVO','La ventana oculta no despachó TIMER de forma fiable en la automatización. La prueba de integración usa eventos simulados y está etiquetada. Falta comprobar respuesta visual con Blender visible, cámara personal y medición extremo a extremo.',tint=PALE)

    d.new('05 / evaluación','EVIDENCIA Y CIERRE DE LA ENTREGA')
    d.table(['Requisito','Evidencia / estado'],[['Humanoide completo','Cuerpo cerrado, foto proyectada, rig y pesos revisados; warnings de vestuario documentados.'],['Especificación y asistencia','spec.md previo al módulo y prompt_log.md real; conservar/exportar la conversación.'],['Camino A','Código y escenas verificadas con ensayo; inferencia y cámara requieren comprobar entorno y sesión personal.'],['Camino B','Importador y CSV verificados con fixture; falta archivo FreeMoCap real y proyecto de captura.'],['ROS 2','Muestra estructurada y puente opcional; publicación con rclpy no verificada.'],['Videos','Faltan demostraciones personales de 1-2 minutos para ambos caminos.'],['Git y defensa','Sin commits del asistente. Registrar revisiones reales del equipo y practicar cambios en 60 s.']],widths=[137,CW-137],size=9)
    d.head('FUENTES Y TRAZABILIDAD')
    d.p('Documentos locales: documentacion/rubrica-evaluacion-mocap-retargeting.pdf (2 páginas) y guía 5 practica-captura-movimiento-retargeting-ros2.pdf (4 páginas). Resultados actuales: docs/mocap/*.json. La guía exige ambas modalidades.',size=9,leading=12)
    source(d,'MediaPipe / salida Pose Landmarker','https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker/python')
    source(d,'One Euro / algoritmo y ajuste','https://gery.casiez.net/1euro/')
    source(d,'ROS / convenciones REP 103','https://github.com/ros-infrastructure/rep/blob/master/rep-0103.rst')
    source(d,'ROS 2 / definición JointState','https://github.com/ros2/common_interfaces/blob/rolling/sensor_msgs/msg/JointState.msg')
    return d.done()

def report_b():
    d=Doc('reporte_herramienta.pdf','CAMINO B / FLUJO INDUSTRIAL',BLUE)
    d.new('1 de 3 / elección y alcance','FREEMOCAP Y RETARGETING<br/>DEL VIAJERO')
    d.p('Herramienta seleccionada para completar la captura real: FreeMoCap. La implementación adjunta importa BVH/FBX y transfiere movimiento al rig propio; no automatiza una cuenta externa ni sube fotografías.')
    d.box('PROCEDENCIA DE LOS ARCHIVOS INCLUIDOS','El BVH, la animación y el CSV actuales son un fixture analítico generado localmente. Se usan para verificar importación y transformación. No proceden de FreeMoCap ni demuestran movimiento del estudiante.',tint=PALE)
    d.head('POR QUÉ ESTA OPCIÓN')
    d.p('La documentación oficial describe procesamiento local y exportación hacia Blender. Permite conservar datos y revisar el flujo. La guía consultada es de la línea 2.0 alpha: deben registrar la versión utilizada y verificar sus opciones durante la captura real. No se midió aquí una cuota comercial, costo ni latencia de un servicio en nube.')
    d.table(['Criterio','Camino A','Camino B elegido'],[['Captura','MediaPipe en proceso propio','Captura procesada en FreeMoCap'],['Retargeting','Vectores y base local por frame','Delta de fuente calibrada; horneado'],['Transporte','UDP local, sin retransmisión','Archivo BVH/FBX'],['Salida','Pose y JointState opcional','CSV y escena animada'],['Estado real','Ensayo sintético y pruebas','Fixture importado; captura real pendiente']],widths=[100,205,CW-305],size=9)
    d.head('FLUJO A COMPLETAR')
    d.p('Grabación personal → procesamiento en FreeMoCap → exportación BVH/FBX → mapa de huesos → pose A de calibración → retargeting → revisión visual → extracción CSV. Para triangulación multicámara se requiere calibración espacial; no debe confundirse con una estimación monocular.')
    source(d,'Exportación oficial de FreeMoCap (consulta 22-11-2026)','https://docs.freemocap.org/tutorials/blender/')
    source(d,'Arquitectura local y triangulación','https://docs.freemocap.org/build/backend/')

    d.new('2 de 3 / transferencia','CALIBRAR ANTES DE COPIAR')
    d.head('MAPA Y POSTURA')
    d.p('El JSON define destino → fuente. Se validan nombres y se exige mapear hombros y muslos para estimar el marco corporal. El frame de calibración debe mostrar la A-pose física del Viajero, aunque el rest pose de la fuente sea T. No se supone que el primer frame cumpla esa condición.')
    d.code('C = marco_destino * inverse(marco_fuente_calibracion)\ndelta = C * (Qfuente_actual * inverse(Qfuente_cal)) * inverse(C)\nQdestino = inverse(Qobj_destino) * delta * Qobj_destino * Rreposo')
    d.p('C alinea el marco corporal completo. La revisión detectó que el importador BVH podía orientar la fuente 180° respecto al destino; corregir sólo los rolls dejaba un error importante. La alineación corporal resuelve ese desfase antes de convertir al espacio local del padre.')
    d.table(['Aspecto','Decisión'],[['Longitud de eslabones','Se conserva la geometría de reposo del destino; no se animan escalas.'],['Root motion','Desactivado por defecto. Opción explícita con razón de altura de pelvis y marco corporal calibrados.'],['Ejes y unidades','Configurables al importar. Fixture nativo Z-up en metros; confirmar cada fuente real.'],['Keyframes','Cuaterniones, continuidad de signo y claves lineales; acción independiente de la fuente.'],['Validación','52 huesos mapeados y 180 frames. Error frente a A menor de 0,000001 rad fuera del frame de calibración.']],widths=[145,CW-145])
    d.box('QUÉ NO RESUELVE ESTE RETARGETER','No infiere una pose de calibración correcta, no ajusta automáticamente contactos ni elimina colisiones de ropa. Las diferencias de proporción pueden requerir IK y correcciones visuales. La correspondencia de nombres del fixture debe adaptarse al archivo real.',tint=PALE)
    d.p('Scripts: retarget_industrial.py y extract_joint_angles.py. El CSV y su archivo .meta.json conservan la procedencia para que la evidencia sea auditable.',size=9,leading=12)

    d.new('3 de 3 / telemetría y límites','DEL FRAME AL DATO ARTICULAR')
    rows=list(csv.DictReader((ROOT/'entrega/mocap/joint_telemetry_ros.csv').open()))
    d.p('Ángulos de codo del ensayo incluido. Azul: izquierdo. Rojo: derecho. Eje vertical: radianes; eje horizontal: 180 frames, aproximadamente 6 s. El primer frame es la calibración en reposo.',size=9,leading=12)
    chart(d,[[float(r['left_elbow_flex_rad']) for r in rows],[float(r['right_elbow_flex_rad']) for r in rows]],[BLUE,RED],height=160,yrange=(0,1.4))
    d.table(['Campo / salida','Definición'],[['frame, timestamp_s','Tiempo relativo: (frame-inicio) / FPS efectivo.'],['Codos y rodillas','Ángulo entre direcciones consecutivas; cero extendido.'],['Hombros','Pitch, roll y elevación de la dirección del brazo en marco del torso. Twist no observado.'],['CSV incluido','180 filas; diez ángulos finitos; unidades radianes. Procedencia sintética.'],['Enlace con ROS','Mapear nombres y ejes al URDF real. JointState es estado; un controlador de trayectoria necesita otra interfaz.']],widths=[145,CW-145])
    d.head('LATENCIA Y CAPA GRATUITA')
    d.p('No se dispone de una captura FreeMoCap real para medir tiempo de procesamiento, retraso o errores de oclusión. Esos resultados quedan pendientes. El flujo local evita depender de créditos de un servicio en nube, pero exige recursos de cómputo y calibración según el modo. No se asignan cifras estimadas como si fueran mediciones.')
    d.box('PARA CERRAR EL CAMINO B','Sustituir el fixture por la captura personal, guardar proyecto/versión, comprobar A/T y ejes, regenerar CSV, medir latencia o tiempo de procesamiento y grabar el video exigido de 1-2 minutos. Conservar también la fuente original.',tint=PALE)
    return d.done()

def defense():
    d=Doc('Guia_de_Defensa.pdf','DEFENSA / COMPRENSIÓN Y PRÁCTICA')
    d.new('1 de 4 / exposición','PREPARAR UNA DEFENSA<br/>DE SEIS MINUTOS')
    d.p('La rúbrica evalúa comprensión, especificación y modificación en vivo. Esta guía sirve para estudiar el código y comprobarlo personalmente. La asistencia está documentada; no se debe presentar el fixture como captura real.')
    d.table(['Tiempo','Mostrar','Explicar'],[['0:00-0:45','Avatar y foto','Volumen, pesos y proyección facial.'],['0:45-1:30','spec.md','Unidades, contrato y separación de procesos.'],['1:30-2:45','Camino A real','World landmarks, filtro, UDP y TIMER.'],['2:45-3:45','Cinemática','Vectores, cuaterniones y base del padre.'],['3:45-4:45','Camino B real','Mapa, calibración A/T y CSV.'],['4:45-5:30','Fallo + ROS','Retención, STALE, radianes y límites.'],['5:30-6:00','Evidencia','Resultados medidos, bitácora y pendientes.']],widths=[85,135,CW-220])
    d.head('ORDEN DE ESTUDIO')
    d.p('<b>1.</b> Vectores y radianes: resolver a mano extensión y flexión de 90°.<br/><b>2.</b> Cambios de base y cuaterniones: dibujar los ejes y derivar Qlocal.<br/><b>3.</b> Filtro y red: predecir efectos de parámetros y pérdida de paquetes.<br/><b>4.</b> Blender: localizar TIMER, PASS_THROUGH, limpieza y jerarquía.<br/><b>5.</b> Camino B y ROS: explicar calibración, CSV y límites.<br/><b>6.</b> Ensayar tres defensas y mutaciones cronometradas.',leading=17)
    d.box('ANTES DE PRESENTAR','Completar captura y videos personales, revisar el parecido y poses, comprobar Blender visible y conservar el proyecto industrial. Los commits deben corresponder a trabajo real del equipo; no se crearon commits ni una historia retrospectiva.')

    d.new('2 de 4 / fundamentos','LO QUE DEBES DERIVAR')
    topics=[('WORLD NO ES POSICIÓN ABSOLUTA','Los 33 world landmarks estiman metros relativos a caderas. Los puntos normalizados dependen del tamaño de imagen. Ninguno demuestra por sí solo calibración métrica de la habitación.'),
    ('PRODUCTO PUNTO Y PRODUCTO CRUZ','u=E-S y v=W-E. El producto punto da cos(theta); el cruz da la dirección del eje. Normalizar, limitar el coseno a [-1,1] y rechazar vectores nulos evita resultados inválidos.'),
    ('CUATERNIONES Y AMBIGÜEDAD','q=normalize([1+a·b,a×b]). Antiparalelos: escoger eje perpendicular. q y -q equivalen. Evitar gimbal lock no recupera el twist que dos puntos no observan.'),
    ('REPOSO, PADRE Y LOCAL','base=Qpadre*inverse(Rpadre)*Rhueso; Qlocal=inverse(base)*Qdeseada. Explica cada espacio. Una dirección global no se asigna sin conversión al canal local del antebrazo.'),
    ('A/T Y MARCO CORPORAL','La pose de calibración debe coincidir físicamente. Además hay que alinear los ejes corporales de fuente y destino; copiar deltas sin esa alineación puede invertir la dirección del movimiento.')]
    for title,text in topics:d.head(title);d.p(text)
    d.box('EJERCICIO SIN COMPUTADORA','Calcula theta para (1,0,0) y (0,1,0). Convierte (0,-1,0) de MediaPipe a Blender. Demuestra que R(ex)×R(ey)=R(ez). Explica por qué invertir sólo X es un espejo y no una rotación.')

    d.new('3 de 4 / código en vivo','MUTACIONES EN 60 SEGUNDOS')
    d.table(['Solicitud','Dónde actuar','Cómo comprobar'],[['Más suavizado','--min-cutoff y --beta','Reposo y gesto rápido; explicar retraso.'],['Cambiar puerto','Productor --port + panel','Coincidir ambos y liberar receptor anterior.'],['Campo extra JSON','PacketBuilder.build','Leer JSONL; conservar esquema y unidades.'],['Cambiar ejes','mp_to_blender','Verificar orientación diestra y gesto unilateral.'],['Oclusión','visibility del punto 13','Retener segmento izquierdo; otros siguen.'],['Límite de codo','joint_limits.json','Puente limita; CSV bruto conserva medición.'],['Mapa industrial','JSON destino->fuente','Nombres válidos y frame de calibración correcto.']],widths=[110,153,CW-263],size=9)
    d.head('UBICACIONES QUE DEBES CONOCER')
    d.p('<b>mocap/core.py:</b> OneEuro, between, validate, Receiver.poll y joint_state.<br/><b>mocap/blender_adapter.py:</b> Retargeter.apply y conversión padre/reposo.<br/><b>blender_consumer_modal.py:</b> execute, modal, stop y register.<br/><b>retarget_industrial.py:</b> body_frame, align y horneado.<br/><b>extract_joint_angles.py:</b> evaluación por frame y escritura CSV.',leading=17)
    d.box('RESPUESTA ESPERADA ANTE PÉRDIDAS','Cinco paquetes perdidos no congelan la GUI: se conserva pose, se acepta el siguiente frame vigente y se muestra STALE si transcurre el umbral. El filtro no rellena información inexistente. Explica por qué UDP prioriza actualidad sobre retransmisión.')

    d.new('4 de 4 / autoevaluación','PREGUNTAS SIN LEER EL GUION')
    questions=['¿Qué diferencia hay entre imagen normalizada y world landmarks?','¿Por qué el ángulo del codo no determina la orientación del hombro?','¿Cuál es el orden wxyz y qué pasa si una biblioteca espera xyzw?','¿Qué línea evita bloquear la interfaz y qué limita el trabajo por tick?','¿Qué sucede si se reinicia el productor o llega un frame atrasado?','¿Cómo cambian ruido y retraso al variar min_cutoff y beta?','¿Qué giro axial queda ambiguo y qué se conserva del reposo?','¿Cómo corrige el Camino B la postura A/T y el marco corporal?','¿Por qué un CSV de Euler X no basta para cualquier rig?','¿Qué se midió realmente y qué falta para la prueba personal?']
    for i,q in enumerate(questions,1):d.p(f'<b>{i:02d}.</b> {q}',size=11,leading=15,gap=12)
    d.box('CRITERIO PARA SABER SI ESTÁS LISTO','Puedes señalar la función pertinente, anticipar el efecto de una modificación y demostrarlo con una prueba. Si aún necesitas memorizar la respuesta, vuelve al ejemplo pequeño y ejecútalo antes de ensayar la exposición.')
    d.p('Estudio ampliado: docs/mocap/GUIA_DEFENSA.md. Ejecución: GUIA_USO.md. Fuentes oficiales y resultados: informes de cada camino. Conserva la conversación real junto con la bitácora de asistencia.',size=9,leading=12)
    return d.done()

if __name__=='__main__':
    for f in (report_a,report_b,defense):print(f())
