# Preparación de la defensa (5-7 minutos)

La meta es explicar y modificar el sistema, no memorizar un discurso. La rúbrica permite asistencia de IA bajo ingeniería de contexto y evalúa comprensión, especificación y trazabilidad. Reconoce la asistencia y explica las decisiones que hayas comprobado personalmente.

## Guion de seis minutos

| Tiempo | Demostración | Qué debes poder justificar |
|---|---|---|
| 0:00-0:45 | Avatar, foto fuente, cuerpo aislado y pesos | Volumen cerrado, anatomía, identidad, relación malla/armature |
| 0:45-1:30 | `spec.md` y diagrama | Procesos separados, unidades, contrato y tolerancia a fallos |
| 1:30-2:45 | Camino A y movimiento bilateral real | World landmarks, filtro, UDP y operador modal |
| 2:45-3:45 | Vectores y cuaterniones | Dirección global, reposo, padre y rotación local |
| 3:45-4:45 | Camino B real y CSV | Mapa, postura A/T, longitudes y telemetría |
| 4:45-5:30 | Fallo de red/oclusión y salida ROS | Retención, STALE, radianes y límites didácticos |
| 5:30-6:00 | Evidencia y límites | Pruebas, bitácora, commits propios y pendientes reconocidos |

No mostrar un camino como validado con captura personal mientras sólo exista su fixture.

## 1. Landmarks y cambio de ejes

MediaPipe entrega 33 puntos. Los de imagen tienen x/y normalizados y una profundidad relativa; los world landmarks estiman coordenadas en metros centradas en caderas. El tamaño normalizado cambia al acercarse a la cámara y no se puede tratar como una medida corporal. La estimación monocular world tampoco equivale a una medición métrica calibrada.

En `mocap/core.py`, `mp_to_blender` implementa `(x,z,-y)`: el eje vertical negativo de cámara se vuelve +Z, y se conserva orientación diestra. Su determinante es +1. Reflejar sólo x produciría determinante -1; eso es un espejo, no una rotación. Para un cuerpo mirando -Y en Blender, ROS recibe `(-y,x,z)`. REP 103 define X delante, Y izquierda, Z arriba; un marco óptico usa otra convención.

Ejercicio: escribe las imágenes de los tres vectores base y verifica `R(ex) × R(ey) = R(ez)`. Después levanta tu brazo izquierdo y verifica el lado del avatar con cámara sin espejo. No sustituyas esta prueba física por una suposición.

## 2. Cinemática que debes derivar en papel

Con hombro S, codo E y muñeca W: `u=E-S`, `v=W-E`. Flexión `theta=acos(clamp((u·v)/(|u||v|),-1,1))`. Si u=v, la flexión es 0; si son perpendiculares es pi/2. Usar el ángulo interior con vector S-E cambia la convención a pi-theta: explica cuál elegiste.

El producto cruz da un eje perpendicular. Para alinear dos direcciones unitarias a,b, el cuaternión de arco mínimo es `normalize([1+a·b, a×b])`, en orden wxyz. Si a=-b hay infinitos ejes válidos: elegimos uno perpendicular de forma determinista. Si el vector es cero, no hay orientación válida y retenemos pose. En `mocap/core.py`, localiza `between`, `angle` y `unit`.

Los cuaterniones evitan la singularidad de parametrizar la orientación con tres ángulos de Euler. No eliminan la ambigüedad de un brazo recto ni recuperan información no observada. Dos puntos definen dirección pero no giro alrededor del propio hueso: el twist axial queda restringido por el reposo. q y -q representan la misma orientación; se mantiene el signo cercano al frame anterior para evitar saltos de interpolación.

## 3. Por qué no asignar una rotación global directamente al hueso

El hueso tiene orientación de reposo y hereda la del padre. Con reposos globales Rp y Rb, la base actual es `Qpadre * inverse(Rp) * Rb`. La rotación que se guarda en `rotation_quaternion` es `inverse(base_actual) * Qdeseada`. Así un antebrazo no recibe dos veces la rotación del brazo. Revisa el bucle de `Retargeter.apply` y explica cada multiplicación en ese orden.

No se anima escala. La longitud del hueso depende de su geometría de reposo; cambiar longitudes para igualar otra persona deformaría el avatar. La traslación de raíz está fuera del Camino A implementado; los pies pueden deslizar y no existe un solver IK de contacto.

## 4. Filtro One Euro

`alpha = 1 / (1 + 1/(2*pi*fc*dt))`. Primero se estima y filtra la derivada. Luego `fc = min_cutoff + beta*abs(derivada_filtrada)` y se filtra la posición. Reducir min_cutoff suaviza reposo pero añade retraso; aumentar beta permite responder más rápido cuando sube la velocidad. dt se mide, no se supone que la cámara siempre produzca 30 FPS. Un hueco mayor de 0,5 s reinicia el filtro para no arrastrar una posición vieja.

Práctica: ejecuta con `--beta 0`, después `--beta 0.2`, manteniendo la misma cámara y gesto. Compara ruido en reposo y respuesta, registra observaciones reales. No digas que el filtro elimina toda latencia.

## 5. UDP, pérdida y GUI

UDP evita esperar retransmisiones de frames que ya caducaron; puede perder, duplicar y reordenar paquetes. El contrato incluye frame_id, timestamp y session_id. Se descartan paquetes viejos/duplicados; un reinicio usa sesión nueva. Tras una pérdida corta se conserva la última pose; a 500 ms se muestra STALE. No se interpolan paquetes inexistentes ni se finge recibir datos.

La línea decisiva está en `Receiver.__init__`: `self.sock.setblocking(False)`. Eso por sí solo no limita el trabajo: `poll` además drena como máximo 32 datagramas y 4 ms por tick. La inferencia está en otro proceso. El modal atiende TIMER y devuelve PASS_THROUGH para otros eventos. `cancel` cierra socket y quita timer. Explica qué ocurriría con recvfrom bloqueante o un bucle infinito dentro del modal.

## 6. Camino B y visión

Explica lo que realmente usaste. FreeMoCap es un pipeline local; una ruta multicámara añade calibración, correspondencias temporales y triangulación. Una red de pose estima landmarks, pero no se debe atribuir a un producto una arquitectura Transformer específica sin fuente. CNN explota patrones espaciales; modelos temporales usan contexto entre frames; las oclusiones siguen introduciendo incertidumbre. La documentación de la versión elegida debe respaldar las afirmaciones sobre su modelo concreto.

El retargeter guarda la orientación de la fuente en el frame de calibración. Cada frame calcula `delta = Qfuente_actual * inverse(Qfuente_calibracion)` y la aplica al reposo del destino, convirtiendo antes los marcos de objeto. Si calibras una fuente T mientras el destino está en A sin compensación, el desplazamiento de hombros persistirá. El primer frame no es automáticamente una calibración válida.

El CSV usa puntos articulares evaluados para obtener codos y hombros, en radianes. No copia Euler X de todos los huesos: el roll de cada hueso hace que eso sea ambiguo. Un JointState comunica estados articulares, no es por sí mismo una orden de movimiento a un controlador. Para hardware hacen falta nombres, ejes y límites del URDF real.

## Mutaciones de 60 segundos

| Cambio solicitado | Lugar | Verificación |
|---|---|---|
| Cambiar suavizado | `mocap_producer.py --min-cutoff/--beta` | Reposo y gesto rápido; explicar dt |
| Cambiar puerto | Productor `--port` y panel Blender | Mismo puerto; detener/liberar el anterior |
| Añadir campo JSON | Diccionario en `PacketBuilder.build` | Captura JSONL; decoder acepta metadatos extra |
| Alterar un eje | `mp_to_blender` | Primero pruebas de orientación diestra; explicar reflexión vs giro |
| Simular oclusión | visibility de landmark 13 < 0.6 | Codo izquierdo no se actualiza, otros sí |
| Reducir límite de codo | `mocap/joint_limits.json` | JSON del puente limitado; raw CSV conserva medición |
| Cambiar mapa B | JSON destino->fuente | Hueso existe y calibración coincide |

Haz cada ensayo en copia y vuelve a ejecutar las pruebas. Si sólo cambias un signo, reconoce que puedes introducir un espejo; una rotación de 180 grados invierte dos ejes. No desactives validaciones para hacer pasar una demostración.

## Preguntas que debes responder sin leer

1. ¿Por qué world landmarks no equivale a posición absoluta del usuario en la habitación?
2. ¿Por qué un hombro no se orienta usando únicamente el ángulo de flexión del codo?
3. ¿Qué significa el orden wxyz y cómo difiere de xyzw en otras bibliotecas?
4. ¿Qué ocurre si se pierden cinco paquetes? ¿Y si reinicio el productor?
5. ¿Dónde se impide bloquear la GUI y dónde se limita el trabajo por tick?
6. ¿Qué compromisos cambian al bajar min_cutoff o subir beta?
7. ¿Qué información de twist no puede determinarse con dos puntos?
8. ¿Por qué hay que calibrar A/T pose antes de transferir?
9. ¿Qué parte de la latencia se midió y qué parte falta medir?
10. ¿Qué evidencia es sintética y qué evidencia personal debes aportar?

## Orden de estudio

Primero vectores, producto punto/cruz y radianes; después cambios de base, cuaterniones y jerarquía de huesos; después filtro, UDP y eventos Blender; finalmente calibración B, CSV y JointState. Termina con tres ensayos completos de seis minutos y mutaciones cronometradas. Tu defensa estará lista cuando puedas predecir el resultado de un cambio antes de ejecutarlo.
