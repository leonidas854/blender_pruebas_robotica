---
name: viajero-materiales
description: Ajustar materiales, iluminación, renders y evidencias del personaje Viajero entre Épocas, conservando su paleta histórica aprobada.
---

# Materiales y presentación del Viajero

Localiza la raíz del proyecto y lee `docs/materiales.md`.
Usa `blender/personaje_final.blend`, no los modelos del archivo robótico.
Biblioteca reutilizable: `assets/materiales/viajero_materiales.blend`.

La paleta viene de `referencias/personaje_aprobado/`: abrigo azul grisáceo,
camisa cruda, chaleco marrón, pantalón carbón, bufanda burdeos, cuero marrón,
latón envejecido, cabello oscuro y piedra azul sin emisión de neón.

Los shaders nativos usan Principled, ruido, rampas y bump. Los colores de
`viajero_lib.material` son lineales; compara renders, no sólo valores numéricos.
Evita poros excesivos, reflejos plásticos en telas y pelo plateado por contraluz.
Para cambiar de material, inspecciona los slots por objeto y sus conexiones.

```bash
blender -b --python-exit-code 1 -P scripts/render_viajero.py
```

Este comando vuelve a renderizar, exporta y guarda cámaras en el archivo final;
trabaja sobre copia si hay una toma manual que deba conservarse.
`CAM_Frente`, `CAM_Perfil` y `CAM_Espalda` son ortográficas; `CAM_Hero` es
perspectiva. No presentes unas como otras. `docs/evidencia_escena.json` registra
luces y nodos realmente usados.

Verifica primero un render pequeño. El entorno comprobado tiene Blender 5.2.2
y RTX 3070 con OptiX; detecta los dispositivos de nuevo si cambia la máquina.
El nombre del hardware en scripts antiguos no constituye una comprobación.

GLB/FBX no conservan los grafos procedurales completos. Para equivalencia visual
en motores externos, hornea mapas PBR y verifica la reimportación; no declares
texturas horneadas por el mero hecho de tener UV. Para esta entrega, `.blend`
es la referencia visual.
