# Estado del proyecto — 20 de octubre de 2026

**Entrega ensamblada v1:** personaje vestido y editable, materiales, accesorios, rig FK y renders. No se certifica como personaje final de producción: el parecido facial y las deformaciones exigentes requieren refinamiento.

| Etapa | Resultado real |
|---|---|
| 01 Referencias | 18 imágenes revisadas y empaquetadas en el archivo; colección desactivada |
| 02 Blockout | Original conservado con cuatro vistas |
| 03 Cuerpo base | Original preferido por el usuario conservado; copia editable oculta bajo ropa |
| 04 Rostro | Cabeza, ojos, párpados, cejas, nariz y boca; parecido pendiente de revisión artística |
| 05 Cabello | Casquete y mechones independientes; silueta a seguir refinando |
| 06 Ropa base | Camisa y chaleco por piezas |
| 07 Ropa exterior | Abrigo, pantalón, bufanda, telas, guantes y botas |
| 08 Accesorios | Cinturón, bandolera, bolso, bolsa auxiliar, talismán y gafas |
| 09 Materiales | 23 materiales de personaje; UV automáticas; biblioteca .blend |
| 10 Rig | 57 huesos FK, pesos normalizados, dedos y 13 poses; sin IK ni simulación de telas |
| 11 Renders | Cinco vistas, ocho detalles, trece poses y dos renders finales |
| 12 Entrega | Guía, tres skills, dossier PDF, GLB, FBX y ZIP; informes de verificación en docs/ |

## Comprobaciones

La escena se reabre con Blender 5.2.2 LTS. El validador comprueba altura de 1.80 m, materiales, UV, pesos normalizados, armature, acciones y estado neutral de expresiones. También evalúa que la T-pose no estire los paneles del torso del abrigo.

`docs/validacion_viajero.json` registra los números medidos; `docs/validacion_exportaciones.json` registra la reimportación de GLB y FBX. `docs/manifest_entrega.json` lista archivos, tamaños y SHA-256 del paquete.

## Límites observados

El rostro es una interpretación procedural; no se afirma semejanza exacta ni fotogrametría. La topología facial no está preparada para diálogo. Las poses de sentado/agachado son pruebas, no deformaciones aprobadas: faltan controles/correctivos de faldones. No hay ciclo de caminata ni texturas PBR horneadas. GLB/FBX simplifican los shaders procedurales.

Los originales 01–03 y referencias se conservaron. Las versiones generadas durante la revisión están en `blender/respaldo/`, fuera del ZIP para evitar duplicados. Se preservó la documentación histórica por separado.

## Continuar

Abrir `GUIA_BLENDER.md`. Skills instaladas: `viajero-modelado`, `viajero-materiales`, `viajero-rig`. Próximas prioridades concretas en `docs/pendientes.md`.
