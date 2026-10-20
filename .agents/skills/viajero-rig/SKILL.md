---
name: viajero-rig
description: Revisar pesos, poses, dedos y expresiones del rig FK nativo del Viajero entre Épocas y preparar su exportación desde Blender.
---

# Rig del Viajero

Lee `docs/rigging.md` y abre una copia de `blender/personaje_final.blend`.
El armature se llama `RIG_Viajero`. No necesita Rigify ni servicios externos.

- Es un rig FK: no promete controles IK, cambio IK/FK ni simulación de telas.
- Cada acción 01–13 es una pose sostenida, no un ciclo de caminata.
- Las prendas se deforman con pesos; los faldones usan pelvis y las telas
  colgantes tienen huesos `cloth.L/R`. Verifica colisiones al sentarse/agacharse.
- Hay tres segmentos por dedo. Las gafas/cabello siguen `head`, los ojos tienen
  `eye.L/R`; el bolso usa `bag`.
- Los ejes de huesos se orientan explícitamente al construir el rig. No
  presupongas que una rotación Euler local equivale a un eje global.
- El rostro y los párpados tienen shape keys iniciales. Inspecciona cada una:
  su existencia no demuestra una actuación facial final ni una boca articulada.

Para verificar en un proceso nuevo:

```bash
blender -b --python-exit-code 1 -P scripts/validate_viajero.py
```

Evalúa las mallas con el depsgraph en A, T, codos flexionados y la pose nueva;
inspecciona además sus renders. Los pesos deben sumar 1 por vértice y referenciar
huesos existentes. La validación numérica no mide automáticamente colisiones.

Al cambiar la topología, conserva UV y shape keys o reconstruye explícitamente
las afectadas. No apliques a ciegas remesh a una cara con expresiones.
En GLB verifica escala, skeleton, morph targets y acciones reimportando. FBX de
esta entrega contiene rig y geometría sin animaciones horneadas.
