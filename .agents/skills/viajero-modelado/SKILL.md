---
name: viajero-modelado
description: Continuar el personaje Viajero entre Épocas en este proyecto Blender, comparando sus fotografías y fichas con la geometría editable, vestuario y accesorios.
---

# Viajero: modelado y dirección artística

Trabaja desde la raíz que contiene `blender/personaje_final.blend` y `referencias/`.
Lee `ESTADO.md` y `GUIA_BLENDER.md` antes de cambiar el personaje.

El modelo preferido inicialmente por el usuario está en `blender/03_cuerpo_base.blend`;
su perfil es `renders/cuerpo_base/cuerpo_base_side.png`. Conserva estos originales.
El personaje es humano, joven y viajero histórico. No ejecutes el pipeline
`scripts/archive_robotics/` para continuar este diseño.

Orden de referencia: fotografías para identidad; concepto aprobado para silueta y
paleta; cuerpo base para proporciones; ocho fichas para construcción y detalles.
Revisa las imágenes pertinentes con una herramienta visual. Las fotografías
perspectivas no permiten afirmar medidas corporales exactas.

## Editar

- Archivo de trabajo: `blender/personaje_final.blend`; guarda una copia antes de
  cambios artísticos. Las etapas 04–10 son hitos, no enlaces vivos al archivo final.
- `scripts/build_viajero.py` contiene funciones `face`, `hair`, `clothing_base`,
  `clothing`, `accessories`; `scripts/viajero_lib.py` construye geometría y nodos.
- Regenerar produce nuevas etapas y respalda las anteriores en `blender/respaldo/`.
  No reconstruyas si hay trabajo manual sin guardar en una copia identificada.
- El frente es -Y, Z es vertical. La altura completa incluye cabello y botas:
  1.80 m. El factor real está en la propiedad de escena `factor_escala`.
- `Cuerpo` está oculto bajo el traje, pero sigue editable. Antes de desvestir,
  activa su visibilidad. No confundas esta ocultación con retopología o
  eliminación de colisiones.

```bash
blender -b --python-exit-code 1 -P scripts/build_viajero.py -- --preview
blender -b --python-exit-code 1 -P scripts/validate_viajero.py
```

Inspecciona frente, perfil, espalda, tres cuartos y detalle de cara. Comprueba
intersecciones en axilas, muñecas, cuello y cinturón. Los tests estructurales no
aprueban parecido facial ni calidad artística. Describe problemas visibles sin
declarar terminado un rig o una escultura que todavía necesitan trabajo.

Para materiales consulta `docs/materiales.md`; para poses `docs/rigging.md`.
