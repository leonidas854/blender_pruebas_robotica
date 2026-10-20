# Trabajar con el Viajero entre Épocas

## Abrir

Desde esta carpeta:

```bash
blender blender/personaje_final.blend
```

El personaje completo está en `PERSONAJE`, dividido en anatomía, cara, cabello,
camisa/chaleco, abrigo, pantalón/telas, bufanda, manos, botas y accesorios.
`ESTUDIO` contiene cámaras, suelo y tres luces. Las referencias están empaquetadas
en una colección desactivada para que no estorben al editar.

Selecciona una pieza en el Outliner. `Tab` entra en modo Edición; en Material
Properties puedes cambiar sus materiales y en Shading editar los nodos.
Guarda con **Save As** una copia, por ejemplo `blender/viajero_edicion_01.blend`.

La anatomía heredada `Cuerpo` está oculta bajo la ropa. Para trabajar el cuerpo
sin vestuario, abre el original `03_cuerpo_base.blend`, o activa `Cuerpo` y
desactiva las colecciones de ropa. El original y sus renders no se sustituyeron.
La nueva cabeza, manos y antebrazos son piezas independientes.

## Poses y expresiones

Selecciona `RIG_Viajero`, cambia a **Pose Mode**, selecciona un hueso y rota.
Usa **Dope Sheet → Action Editor** para elegir las acciones `01_A_pose`,
`02_T_pose`, `05_Codos_flexionados` o `13_Presentacion`.
Son poses de prueba sostenidas durante 24 fotogramas; `06_Paso_caminata`
no es una animación de andar.

Para posar manualmente sin que una acción restaure sus valores, desvincula
temporalmente la acción con la X del Action Editor; tiene Fake User y se conserva.
`Alt+R` y `Alt+G` restablecen rotación y posición de los huesos seleccionados.
El control es FK. No hay controles IK ni simulación de ropa.

Selecciona `Rostro` → Object Data Properties → Shape Keys para explorar
`Sonrisa`, `Sorpresa`, `Reflexion`. Los párpados y cejas tienen sus propias keys.
Son controles iniciales para seguir desarrollando expresión, no un sistema
facial terminado para diálogo.

## Renderizar

El archivo abre con una cámara de tres cuartos. `Numpad 0` muestra la cámara;
`F12` renderiza. Para cambiar cámara, selecciónala y usa `Ctrl+Numpad 0`.
Las cámaras de turnaround son ortográficas; `CAM_Hero` es perspectiva.

```bash
# Reconstrucción desde scripts: respalda etapas generadas, conserva 01–03.
blender -b --python-exit-code 1 -P scripts/build_viajero.py -- --preview
# Renders completos y exportaciones desde el archivo ya editado.
blender -b --python-exit-code 1 -P scripts/render_viajero.py
# Comprobación en proceso nuevo.
blender -b --python-exit-code 1 -P scripts/validate_viajero.py
```

Reconstruir no incorpora automáticamente tus ediciones manuales. Conserva una
copia y modifica el generador sólo si quieres mantener el resultado procedural.
Los scripts usan el `bpy` incluido en Blender; no requieren instalar `bpy` con pip.

## Continuar con el asistente

Skills del proyecto en `.agents/skills/`:

- `$viajero-modelado`: anatomía, parecido, prendas y accesorios.
- `$viajero-materiales`: shaders, iluminación, renders y evidencias.
- `$viajero-rig`: pesos, poses, dedos, expresiones y exportación.

Ejemplo: «Usa $viajero-modelado, abre mi copia de edición y ajusta el perfil de
la nariz comparando la fotografía lateral; conserva el vestuario y renderiza
frente y perfil».

Consulta `docs/pendientes.md` antes de presentar el modelo como personaje
definitivo para animación. La escena completa es editable y renderizable;
su parecido y deformaciones requieren revisión artística adicional.
