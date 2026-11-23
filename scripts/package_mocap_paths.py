"""Dos entregas independientes de ejecución. No opera sobre Git."""
from pathlib import Path
import shutil,json,hashlib
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'entrega/mocap'
A=DEST/'Camino_A';B=DEST/'Camino_B'

def copy(src,dst):
    src=ROOT/src if not isinstance(src,Path) else src
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)

def common(folder):
    folder.mkdir(parents=True,exist_ok=True)
    copy('spec.md',folder/'spec.md');copy('docs/mocap/prompt_log.md',folder/'prompt_log.md')
    for name in ['ESTADO_ENTREGA.md','GUIA_DEFENSA.md']:
        copy('docs/mocap/'+name,folder/name)
    copy('output/pdf/Guia_de_Defensa.pdf',folder/'Guia_de_Defensa.pdf')
    copy('mocap/__init__.py',folder/'mocap/__init__.py');copy('mocap/core.py',folder/'mocap/core.py')
    for name in ['asset_qa.json','validation_blender.json','validation_B.json','validation_modal_integration.json','validation_modal_live.json','test_results.txt']:
        copy('docs/mocap/'+name,folder/'evidencias'/name)
    for name in ['avatar_material.png','rostro_fotografico.png','anatomia_reposo.png','anatomia_flexion.png','anatomia_wire.png']:
        copy('tmp/mocap/'+name,folder/'evidencias'/name)
    copy('documentacion/rubrica-evaluacion-mocap-retargeting.pdf',folder/'documentacion/rubrica-evaluacion-mocap-retargeting.pdf')
    copy('documentacion/5 practica-captura-movimiento-retargeting-ros2.pdf',folder/'documentacion/guia_practica.pdf')

def main():
    common(A);common(B)
    for name in ['mocap_producer.py','blender_consumer_modal.py','ros2_bridge.py','requirements-mocap.txt','run_mocap.ps1']:
        copy(name,A/name)
    for name in ['blender_adapter.py','synthetic.py','joint_limits.json']:
        copy('mocap/'+name,A/'mocap'/name)
    copy('models/pose_landmarker_full.task',A/'models/pose_landmarker_full.task')
    copy('tests/test_mocap.py',A/'tests/test_mocap.py')
    for name in ['robot_humanoide_mocap.blend','prueba_A_sintetica.blend']:
        copy('blender/mocap/'+name,A/name)
    for name in ['synthetic_landmarks.jsonl','ros2_joint_states_sample.json','joint_telemetry_A_synthetic.csv','joint_telemetry_A_synthetic.meta.json']:
        copy(DEST/name,A/'datos'/name)
    copy('output/pdf/Informe_Camino_A.pdf',A/'Informe_Camino_A.pdf')
    copy('docs/mocap/GUIA_USO.md',A/'GUIA_USO_REPOSITORIO.md')
    if (DEST/'ensayo_sintetico_A.mp4').is_file():copy(DEST/'ensayo_sintetico_A.mp4',A/'ensayo_sintetico_A.mp4')
    for name in ['retarget_industrial.py','extract_joint_angles.py']:
        copy(name,B/name)
    copy('mocap/bone_map_viajero.json',B/'bone_map_viajero.json')
    copy('blender/mocap/robot_humanoide_retargeting.blend',B/'robot_humanoide_retargeting.blend')
    copy('blender/mocap/robot_humanoide_mocap.blend',B/'robot_humanoide_base.blend')
    for name in ['source_SYNTHETIC_NOT_FREEMOCAP.bvh','joint_telemetry_ros.csv','joint_telemetry_ros.meta.json']:
        copy(DEST/name,B/'datos'/name)
    copy('output/pdf/reporte_herramienta.pdf',B/'reporte_herramienta.pdf')
    if (DEST/'ensayo_sintetico_B.mp4').is_file():copy(DEST/'ensayo_sintetico_B.mp4',B/'ensayo_sintetico_B.mp4')
    capture=ROOT/'docs/mocap/validation_mediapipe.json'
    if capture.exists():copy(capture,A/'evidencias'/capture.name)
    frozen=ROOT/'docs/mocap/requirements-tested.txt'
    if frozen.exists():copy(frozen,A/'requirements-tested.txt')
    (A/'README.md').write_text('''# Camino A - ingeniería local

Lee primero `Informe_Camino_A.pdf`, `ESTADO_ENTREGA.md` y `Guia_de_Defensa.pdf`.
Esta carpeta funciona como raíz de ejecución; no necesita los scripts del Camino B.

## Preparar

Desde esta carpeta:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements-mocap.txt
python -m unittest discover -s tests -p test_mocap.py -v
```

## Capturar

1. Abrir `robot_humanoide_mocap.blend`.
2. En Scripting ejecutar el texto interno `INICIAR_MOCAP.py`.
3. Vista 3D > N > Mocap > Iniciar UDP; puerto 5005.
4. Ejecutar:

```powershell
.\\.venv\\Scripts\\python.exe mocap_producer.py --camera 0 --seconds 90 --record datos/captura_personal.jsonl --sample datos/ros2_joint_states_personal.json
```

Q detiene cámara; botón Detener UDP o ESC detiene Blender. No reproducir simultáneamente una acción en la línea de tiempo.
Para ensayo sin cámara: `python mocap_producer.py --synthetic --seconds 10`.
Para video propio: `--video ruta.mp4`. Un video pregrabado no prueba réplica en vivo.

`prueba_A_sintetica.blend`, el MP4 breve y los archivos de datos con synthetic son ensayos, no captura personal. El MP4 está rotulado y no sustituye el video de 1-2 minutos exigido.

## Salida ROS

Abrir `python ros2_bridge.py --output datos/joint_states_personal.jsonl` antes del productor. En entorno ROS 2 cargado usar `--ros`; no se verificó rclpy aquí. Los límites son didácticos y faltan URDF/ejes de un robot físico.

La guía larga `GUIA_USO_REPOSITORIO.md` describe rutas del repositorio principal; en esta carpeta usa las rutas cortas anteriores. El material fotográfico está empaquetado en Blender. Las comprobaciones y límites están en `evidencias/`.
''',encoding='utf8')
    (B/'README.md').write_text('''# Camino B - flujo industrial

Lee `reporte_herramienta.pdf` (3 páginas), `ESTADO_ENTREGA.md` y `Guia_de_Defensa.pdf`.
Esta carpeta tiene sus scripts y una copia base del avatar. Requiere Blender 5.2; sus scripts se ejecutan con el Python de Blender.

## Revisar el ensayo incluido

Abre `robot_humanoide_retargeting.blend` y reproduce 1-180. Fuente y telemetría en `datos/` son SINTÉTICAS; no provienen de FreeMoCap. El frame 1 es la calibración A y puede producir un salto al comenzar el movimiento de prueba. El MP4 de ensayo tampoco sustituye el video personal exigido.

## Completar la captura industrial

1. Grabar y procesar al estudiante en FreeMoCap; conservar proyecto, videos y versión.
2. Exportar BVH o FBX; preparar una pose A de calibración equivalente al reposo del avatar.
3. Adaptar `bone_map_viajero.json` a los nombres reales (destino -> fuente). Los nombres incluidos son del fixture.
4. Desde esta carpeta, ejecutar (reemplazar rutas y frame por los datos reales):

```powershell
& 'C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe' -b robot_humanoide_base.blend --python-exit-code 1 -P retarget_industrial.py -- --source CAPTURA_REAL.bvh --map MAPA_REAL.json --calibration-frame 1 --axis-forward Y --axis-up Z --scale 1 --provenance FreeMoCap_VERSION_FECHA --output captura_personal_retargeting.blend
```

Los ejes/unidades deben corresponder a la fuente. Y/Z y escala 1 describen el BVH nativo de ensayo, no toda exportación. El algoritmo alinea además el marco corporal de calibración. Root motion queda desactivado salvo `--root-motion`.

```powershell
& 'C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe' -b captura_personal_retargeting.blend --python-exit-code 1 -P extract_joint_angles.py -- --output datos/joint_telemetry_personal.csv
```

## Repetir exactamente la prueba incluida

Usar `--source datos/source_SYNTHETIC_NOT_FREEMOCAP.bvh --map bone_map_viajero.json --calibration-frame 1 --provenance synthetic_fixture_NOT_FreeMoCap` y una salida nueva. El exportador de CSV exige hombros, codos, muslos y piernas del rig Viajero.

El texto INICIAR_MOCAP que puede aparecer en la copia base pertenece al flujo A y no se usa aquí. Trabajar con el importador B desde terminal. No se requiere instalar sockets ni MediaPipe dentro de Blender.
''',encoding='utf8')
    (DEST/'LEEME.md').write_text('''# Entrega separada

- `Camino_A/`: productor, receptor modal, escenas, modelo MediaPipe, pruebas e informe.
- `Camino_B/`: importador/retargeter, escena base y animada, BVH de ensayo, CSV e informe de 3 páginas.

Cada carpeta incluye la guía de defensa, la rúbrica y un estado de cumplimiento. Las capturas y videos personales aún deben aportarse; las pruebas incluidas están identificadas como sintéticas. No se realizaron commits.

Los archivos sueltos de esta carpeta son resultados reproducibles de los scripts del repositorio; las entregas organizadas para revisar están en las dos subcarpetas anteriores.
''',encoding='utf8')
    for folder in [A,B]:
        entries=[]
        for p in sorted(folder.rglob('*')):
            if not p.is_file() or p.name=='manifest.json':continue
            entries.append(dict(path=str(p.relative_to(folder)).replace('\\','/'),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        (folder/'manifest.json').write_text(json.dumps(entries,indent=2),encoding='utf8')
        print(folder.name,len(entries),'files',sum(e['bytes'] for e in entries),'bytes')

if __name__=='__main__':main()
