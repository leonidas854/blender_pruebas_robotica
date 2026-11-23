# Estado honesto de la entrega

Trabajo del 22 de noviembre de 2026. La entrega se separa en `entrega/mocap/Camino_A/` y `entrega/mocap/Camino_B/`. Los originales del personaje se conservaron. No se hicieron commits, staging ni cambios de autoría.

## Implementado y probado

- Especificación previa del módulo mocap, bitácora real y guía de estudio.
- Núcleo matemático, filtro One Euro, contrato UDP, orden de frames, reinicio de sesión y timeout. Once pruebas unitarias/integración de localhost pasan.
- Copia del avatar con una superficie anatómica cerrada de 227 722 vértices, 57 huesos, fotografía facial proyectada y empaquetada, y pesos normalizados.
- Camino A: productor de cámara/video, receptor modal y retargeter. Prueba analítica de 180 frames: error máximo de dirección de aproximadamente 0,000064 grados; longitudes constantes dentro de 0,00000015 m.
- Integración del método modal con UDP real, pose, STALE, PASS_THROUGH y liberación del socket/temporizador. El detalle del tipo de eventos está en `validation_modal_integration.json`; la prueba de ventana dedicada se registra aparte en `validation_modal_live.json`.
- Camino B: BVH analítico exportado/importado, 52 huesos mapeados, calibración de postura y marco corporal, 180 frames horneados. Diez ángulos exportados; diferencia máxima A/B menor de 0,000001 rad fuera del frame de calibración.
- Muestra JointState y puente opcional a ROS 2. No se ejecutó rclpy.
- Informes PDF y guía de defensa, renderizados para revisión visual.

## Lo que impide declarar cumplimiento total de la práctica

1. Falta una captura personal en vivo con cámara y validación visual de la respuesta completa en Blender.
2. Faltan los dos videos personales de 1-2 minutos exigidos por la guía. Los ensayos sintéticos no los sustituyen.
3. Falta un proyecto/archivo fuente real procesado en FreeMoCap. El BVH incluido lleva `SYNTHETIC_NOT_FREEMOCAP` en el nombre y procedencia explícita en metadatos.
4. Falta medir latencia extremo a extremo y desempeño con oclusión real. El tiempo del adaptador excluye inferencia, captura, evaluación y pantalla.
5. Falta practicar la defensa y la modificación en 60 segundos. Los commits progresivos deben corresponder a revisiones y trabajo real del estudiante/equipo.
6. Para un robot físico falta URDF, definición/calibración de ejes y límites reales. La preparación JSON cubre la salida simulada que permite la guía; no equivale a integración de hardware verificada.

## Advertencias aceptadas, sin ocultarlas

El QA de asset pasa en perfil render, con 19 advertencias. Se conservan degeneraciones y vértices duplicados heredados en cuellos y tapas de prendas porque no se reconstruyó su topología de diseño; requieren limpieza antes de una entrega de producción. Las UV cilíndricas y la proyección facial tienen superposición y algunas caras de área UV nula: son aceptadas para este material localizado, no para horneado de texturas. El detector exhaustivo de z-fighting y partes flotantes se omite sobre el conjunto de 1 097 092 triángulos por su límite de 300 000; las vistas se revisaron, pero no certifican todas las colisiones.

El parecido sigue siendo estilizado. La fotografía cubre la zona frontal de la cara, no toda la cabeza ni la ropa. El rig no incorpora IK de contacto, corrección completa de telas ni recuperación de twist axial. Se deben usar movimientos moderados durante la prueba y documentar las limitaciones observadas.

## Revisión de código detectada y corregida

- La conversión de ejes se verifica por orientación diestra; invertir un único eje sería reflexión.
- El retargeter B alinea marcos corporales de calibración; corregir sólo rest pose/roll producía direcciones erróneas al importar BVH con otro forward.
- Blender 5.2 no expone `Event.timer`. El receptor usa `event.type == 'TIMER'` con control de frecuencia monotónico; no consulta esa propiedad inexistente.
- El estado del operador se guarda en un objeto Python independiente, evitando depender de identidad de wrappers RNA entre callbacks.

## Fuentes

Rúbrica y guía local en documentacion/. Documentación oficial de MediaPipe, One Euro, ROS REP 103, JointState y FreeMoCap enlazada en los PDFs. No se afirma ninguna arquitectura propietaria concreta sin fuente.
