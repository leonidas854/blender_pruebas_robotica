# Plan del Viajero entre Épocas

## Entrega actual

1. Conservar escenas 01–03 y revisar referencias.
2. Crear cabeza, cabello, ropa por capas y accesorios.
3. Asignar materiales y UV; guardar biblioteca nativa.
4. Crear rig FK, pesos y poses de comprobación.
5. Renderizar turnaround, detalles y presentación.
6. Reabrir y validar; exportar y comprobar intercambio.
7. Preparar guía, skills, dossier y ZIP.

| Trabajo | Código |
|---|---|
| Preparación, cara, cabello, prendas y accesorios | Funciones en `scripts/build_viajero.py` |
| Geometría y nodos | `scripts/viajero_lib.py` |
| Rig y poses | `rigging`, `expressions`, `actions` del generador |
| Cámaras, renders y exportación | `scripts/render_viajero.py` |
| Validación | `scripts/validate_viajero.py` |
| PDF y paquete | `scripts/package_viajero.py` |

Se agrupan funciones en módulos reales, evitando scripts vacíos que simulen fases.

## Siguiente ciclo artístico

Revisar parecido con el usuario; refinar cabello, retopología facial, pesos/correctivos y faldones. Después: IK, diálogo, caminata y texturas horneadas si se necesita otro motor. Las escenas y renders permiten revisar estas decisiones concretamente.
