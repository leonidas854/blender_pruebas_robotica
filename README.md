# Viajero entre Épocas

Personaje humano estilizado, vestido por capas y editable en Blender. Versión de presentación y base para seguir refinando parecido y animación.

**Abrir:** `blender blender/personaje_final.blend`

- `GUIA_BLENDER.md`: edición, poses, materiales y comandos.
- `ESTADO.md`: resultados y límites reales.
- `renders/final/`: imágenes de presentación.
- `renders/turnaround/`: vistas ortográficas.
- `renders/poses/`: pruebas del rig.
- `assets/materiales/viajero_materiales.blend`: biblioteca nativa.
- `exports/glb/viajero.glb` y `exports/fbx/viajero.fbx`: intercambio.
- `docs/entrega_examen.md`: relación con la rúbrica y storytelling.
- `docs/pendientes.md`: refinamientos pendientes.
- `.agents/skills/`: skills para continuar.

## Reproducir

Entorno comprobado: Blender 5.2.2 LTS, Linux, NVIDIA RTX 3070, Cycles/OptiX. Los scripts de modelado usan el Python incluido en Blender.

```bash
blender -b --python-exit-code 1 -P scripts/build_viajero.py -- --preview
blender -b --python-exit-code 1 -P scripts/render_viajero.py
blender -b --python-exit-code 1 -P scripts/validate_viajero.py
python scripts/package_viajero.py
```

Los generadores conservan 01–03 y respaldan etapas generadas antes de reconstruir. Guarda las ediciones manuales en otro `.blend`. El empaquetador requiere Pillow y ReportLab, disponibles en este entorno.

Los materiales procedurales completos se conservan en Blender. GLB/FBX no garantizan el mismo aspecto sin hornear texturas. El rig es FK y las acciones son poses de prueba, no ciclos animados terminados.

El trabajo robótico anterior sigue en `scripts/archive_robotics/` y `character_data/blends/robot_archive/`. Su documentación original se conserva en `docs/README_pipeline_anterior.md`; no es el flujo de este personaje.
