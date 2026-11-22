# Viajero entre Épocas — revisión escultórica v2

22 de noviembre de 2026. Alcance elegido: personaje, rig y renders.

## Abrir y revisar

Archivo maestro: `blender/v2/viajero_esculpido.blend`.
Usar Blender 5.2.4 LTS; el comando `blender` de esta máquina apunta a 3.6.15.

```bash
/opt/blender-lts/blender blender/v2/viajero_esculpido.blend
```

El original `blender/personaje_final.blend` y las etapas 01–03 están conservados.
Los accesorios, buena parte del abrigo y el esqueleto proceden de v1. La anatomía,
el rostro continuo, pantalón, bufanda y cabello se reconstruyeron para esta revisión;
las botas se unificaron y las mangas recibieron pliegues de compresión.

## Esculpir

1. Seleccionar `RIG_Viajero` y la acción `01_A_pose`, fotograma 1.
2. Ocultar las colecciones de prendas y accesorios en el Outliner. La anatomía
   nueva se llama `Anatomia_Esculpida`, dentro de `V2_Anatomia_continua`.
3. Seleccionar la anatomía y entrar en **Sculpt Mode**. Ya tiene densidad de
   escultura. Grab sirve para silueta, Clay Strips para volúmenes y Smooth para
   transiciones; trabajar a escala pequeña y comparar frente/perfil.
4. Conservar una copia antes de remallar: remesh altera topología y requiere
   reconstruir pesos, UV y shape keys. No volver a remallar el maestro riggeado
   sin guardar una copia y rehacer esos datos.
5. Para seguir el flujo automatizado, editar los módulos en `scripts/viajero_v2/`.
   Regenerar parte de v1 y no incorpora cambios manuales realizados sobre v2.

El aspecto escultórico se obtuvo con generación de superficies, unión volumétrica,
relajación y desplazamiento de vértices. No se presenta como una sesión manual de
pincel ni como escaneo fotogramétrico. La malla densa es editable, pero requiere
retopología específica si el objetivo pasa a ser animación facial de producción.

## Poses

`RIG_Viajero` → Pose Mode. Acciones en Dope Sheet / Action Editor:
`01_A_pose`, `02_T_pose`, `05_Codos_flexionados`, `13_Presentacion` y
`14_Prueba_codos_rodilla`. Las acciones son poses sostenidas de 24 fotogramas,
no ciclos de locomoción ni captura de movimiento. Para editar una pose, desvincular
la acción temporalmente. Alt+R/Alt+G restablecen el hueso seleccionado.

Las gafas y cabello siguen la cabeza; el bolso sigue `bag`; las telas colgantes
usan `cloth.L/R`. No hay IK ni simulación de telas. Sentado/agachado heredados
siguen siendo pruebas extremas que necesitan correctivos de prendas.

## Render y materiales

F12 usa la cámara guardada. `V2_Hero` es perspectiva; frente, perfil, espalda,
tres cuartos y detalles del rostro son ortográficos. Materiales Principled nativos,
AgX, Cycles y OptiX en la RTX 4070 Laptop comprobada. Los detalles exactos están
en `docs/v2/escena.json`.

La referencia de apariencia es el `.blend`. Las UV son automáticas y no se
entregan texturas PBR horneadas. No trasladar conclusiones de apariencia a otros
motores sin hornear y comprobar la exportación.

## Reproducir y comprobar

Desde la raíz del proyecto:

```bash
# Reconstruir desde los accesorios y el rig preservados de v1.
/opt/blender-lts/blender -b blender/personaje_final.blend --python-exit-code 1 -P scripts/build_viajero_v2.py
# Renderizar la revisión ya guardada.
/opt/blender-lts/blender -b blender/v2/viajero_esculpido.blend --python-exit-code 1 -P scripts/render_viajero_v2.py -- --final
# Reabrir y comprobar malla, pesos, escala y poses.
/opt/blender-lts/blender -b --python-exit-code 1 -P scripts/validate_viajero_v2.py
```

Para MCP: abrir Blender con `--python scripts/start_blender_mcp.py` y usar
`python scripts/blender_mcp_client.py`. El puente instalado escucha en localhost:9876.
Abrir otro `.blend` y editarlo deben ser llamadas separadas para que el contexto
interactivo de Blender se actualice. El puente no está registrado como herramienta
nativa de esta sesión de Codex; el cliente local usa el protocolo del add-on instalado.

## Documentación nueva y siguiente entrega

La rúbrica pide geometría completa, identidad basada en fotos y pesos funcionales.
Los controles estructurales se registran en `validacion.json`; el parecido sigue
siendo una evaluación artística y requiere revisión del usuario.

Por decisión expresa del usuario quedan fuera de esta entrega: productor de mocap,
operador UDP, captura freemium, fuente BVH/FBX de movimiento, telemetría ROS 2 y
videos de una persona real. No se presentan poses sintéticas como captura real.
Consultar `spec.md`, `bitacora.md` y `mejora_continua.md`.
