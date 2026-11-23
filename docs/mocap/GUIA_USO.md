# Ejecutar y revisar mocap

Esta entrega contiene implementación y pruebas de ingeniería. Las animaciones incluidas son **sintéticas**: no sustituyen una captura personal ni prueban que se haya utilizado FreeMoCap. Consultar `ESTADO_ENTREGA.md` antes de presentar.

## Archivos principales

- `blender/mocap/robot_humanoide_mocap.blend`: copia del Viajero preparada para UDP, cuerpo volumétrico cerrado y material con fotografía personal empaquetada.
- `blender/mocap/prueba_A_sintetica.blend`: 180 frames de ensayo analítico del Camino A.
- `blender/mocap/robot_humanoide_retargeting.blend`: transferencia del BVH de ensayo; todavía necesita una fuente industrial real.
- `mocap_producer.py`: webcam/video, MediaPipe Tasks, filtro, UDP y registro JSONL.
- `blender_consumer_modal.py`: receptor y panel de Blender; `mocap/blender_adapter.py`: conversión al espacio de los huesos.
- `retarget_industrial.py`: importador BVH/FBX, calibración y horneado.
- `extract_joint_angles.py`: CSV de diez ángulos geométricos.
- `ros2_bridge.py`: JSONL o publicación ROS 2 opcional.
- `spec.md`: contrato previo a la implementación de este módulo. `prompt_log.md`: bitácora de asistencia.

## Preparación en Windows

Trabajar desde la raíz del repositorio. Se creó `.venv` aislado. Blender detectado: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-mocap.txt
python -m unittest discover -s tests -p test_mocap.py -v
```

Si existe una variable `SSLKEYLOGFILE` que apunta a una ruta inexistente, desactivarla solamente en la terminal de ejecución con `$env:SSLKEYLOGFILE=''`. No se modifica la configuración global.

## Camino A: sesión real

1. Abrir `blender/mocap/robot_humanoide_mocap.blend`. En Scripting seleccionar el texto `INICIAR_MOCAP.py` y ejecutarlo. No habilitar ejecución automática de archivos desconocidos.
2. En la vista 3D, panel N > Mocap: rig `RIG_Viajero`, puerto 5005, **Iniciar UDP**. Detener reproducción de la línea de tiempo durante captura. La acción anterior se restaura al detener.
3. En otra terminal:

```powershell
.\.venv\Scripts\python.exe mocap_producer.py --camera 0 --seconds 90 --record entrega/mocap/captura_personal.jsonl --sample entrega/mocap/ros2_joint_states_personal.json
```

4. Mantener cuerpo completo dentro del encuadre. La entrada no se espeja. Probar primero elevar el brazo izquierdo, después el derecho; comprobar correspondencia antes de grabar evidencia. `Q` cierra la captura; **Detener UDP** o ESC libera el receptor.
5. Hacer flexiones moderadas de codos, movimiento de hombros y paso lento. El método no incluye IK de contacto de pies, recuperación de twist axial completo ni correctivos de ropa para todas las poses. Las oclusiones retienen el último valor; a 500 ms sin pose el panel avisa STALE.

Modo de ensayo sin cámara, para revisar instalación:

```powershell
python mocap_producer.py --synthetic --seconds 10
```

Para un video propio ya grabado: `--video ruta/al/video.mp4`. Es una reproducción a ritmo del archivo, no evidencia de sincronización con una persona en vivo. El registro JSONL contiene coordenadas corporales y debe tratarse como dato personal.

## ROS 2

El productor duplica datagramas al puerto 5006. Primero abrir el puente y después el productor:

```powershell
python ros2_bridge.py --output entrega/mocap/joint_states_personal.jsonl
```

En un entorno con ROS 2 y sus paquetes cargados:

```text
python ros2_bridge.py --ros
ros2 topic echo /joint_states
```

No se instaló ni verificó ROS 2 en este equipo. La muestra JSON sí respeta la estructura JointState. La práctica permite exportar o simular esta salida. `mocap/joint_limits.json` contiene límites didácticos; faltan un URDF y una calibración de actuadores para afirmar compatibilidad con un robot físico. El puente omite articulaciones sin observación válida, mantiene arrays coherentes y no publica poses obsoletas.

## Camino B: completar con FreeMoCap real

1. Grabar y procesar al estudiante en FreeMoCap. Conservar el proyecto y la versión. La documentación consultada corresponde a 2.0 alpha; sus pantallas pueden cambiar y su guía advierte que no todas las rutas fueron verificadas mediante exportación real.
2. Seleccionar MediaPipe como tracker y exportar BVH o FBX. Conservar también los videos originales. Para reconstrucción multicámara, calibrar intrínsecos/extrínsecos; una estimación monocular no es triangulación métrica.
3. Identificar los nombres de los huesos fuente. Crear un JSON destino->fuente a partir de `mocap/bone_map_viajero.json`; ese archivo contiene nombres del fixture, no promete coincidir con toda versión de FreeMoCap.
4. Elegir un frame donde la fuente esté físicamente en la misma A-pose que el reposo del Viajero. Si la fuente tiene reposo T, crear una pose A de calibración en la fuente. No aplicar cambios de reposo a una malla ya pesada sin entender sus consecuencias.
5. Importar/hornear desde una copia base:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b blender/mocap/robot_humanoide_mocap.blend --python-exit-code 1 -P retarget_industrial.py -- --source RUTA_REAL.bvh --map MAPA_REAL.json --calibration-frame 1 --axis-forward=-Y --axis-up Z --scale 1 --provenance FreeMoCap_VERSION_CAPTURA_FECHA --output blender/mocap/retargeting_personal.blend
```

Los valores `axis-up`, `axis-forward` y `scale` deben corresponder al archivo real. El fixture incluido es Z-up, metros. Si el archivo usa centímetros, `--scale 0.01`; si es Y-up, elegir conversión apropiada y verificar una pose. `--root-motion` es opcional y exige origen/pelvis calibrados; por defecto el personaje queda en el sitio.

6. Exportar telemetría de la captura real:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b blender/mocap/retargeting_personal.blend --python-exit-code 1 -P extract_joint_angles.py -- --output entrega/mocap/joint_telemetry_personal.csv
```

El CSV incluido `joint_telemetry_ros.csv` tiene metadatos que identifican explícitamente su fuente sintética. No renombrarlo ni eliminar esa procedencia para presentarlo como captura real.

## Demostraciones exigidas

Camino A: video personal de 1-2 minutos mostrando simultáneamente cámara y Blender, inicio del receptor, movimiento bilateral, oclusión corta y recuperación. Mostrar el estado y medir latencia con marcas de tiempo o un gesto visible en ambas vistas; el tiempo del adaptador Python no es latencia extremo a extremo.

Camino B: video de 1-2 minutos con fuente real, mapeo, calibración A/T, reproducción y CSV. Mostrar límites articulares como límites del modelo utilizado; no atribuirlos a un URDF inexistente.

Guardar antes de la defensa. No grabar una reproducción de la acción sintética como si fuera mocap en vivo.

## Reconstrucción y pruebas

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup blender/v2/sesion_antes_de_v2.blend --python-exit-code 1 -P scripts/build_mocap_asset.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b blender/mocap/robot_humanoide_mocap.blend --python-exit-code 1 -P scripts/verify_mocap_blender.py
```

La construcción usa módulos locales existentes de anatomía y conserva las escenas originales. Los números históricos de `docs/v2/` no describen la nueva copia. Los resultados actuales se encuentran en `docs/mocap/`.

## Git

No se ejecutaron add, reset, commit ni push. El índice ya mostraba numerosos borrados preparados y archivos presentes como no rastreados antes de este trabajo; revisarlo cuidadosamente. La rúbrica exige 4-6 commits progresivos y participación real de ambos integrantes cuando hay pareja. No fabricar fechas, autores ni una secuencia retrospectiva para simular desarrollo. Registrar tus revisiones, correcciones y pruebas reales a partir de ahora.
