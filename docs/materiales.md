# Materiales, iluminación y exportación

La escena usa materiales nativos Principled BSDF. El abrigo, camisa, pantalón y
bufanda tienen variación de color mediante Noise → Color Ramp y microrelieve
Noise → Bump → Normal. Cuero y latón tienen rugosidades diferentes. La piel
usa subsurface ligero sin poros fotográficos; los lentes usan transmisión e IOR
1.45; la piedra azul no tiene emisión.

| Familias | Materiales |
|---|---|
| Anatomía | Piel, Labios, Ojo, Iris, Pupila |
| Cabello | Cabello, Mechon_luz |
| Tejidos | Camisa, Abrigo, Forro, Pantalon, Bufanda, Bordado |
| Cuero | Chaleco, Cuero, Cuero_borde, Guantes |
| Herrajes | Laton, Bronce |
| Otros | Suela, Piedra, Vidrio |

La biblioteca `assets/materiales/viajero_materiales.blend` permite usar
**File → Append → Material** en otros archivos. Las referencias están empaquetadas.
Las superficies tienen UV automáticas; los shaders usan coordenadas Generated.
No se han pintado ni horneado mapas PBR externos y las UV necesitan revisión si
se emplearán para pintura o texturas de alta calidad.

Iluminación: Key cálida 450 W, Fill fría 240 W, Rim cálida 600 W. Cycles con
OptiX en la RTX 3070 comprobada. AgX y denoising activados. Las posiciones,
colores y nodos exactos se guardan en `evidencia_escena.json`.

El `.blend` es la referencia de apariencia. GLB y FBX transfieren geometría y
rig; los nodos procedurales se simplifican o no se transfieren. Hace falta
hornear Base Color, Roughness, Metallic y Normal para conservar el mismo
acabado fuera de Blender. Las exportaciones no equivalen a ese horneado.
