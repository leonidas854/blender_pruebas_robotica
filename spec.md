# Especificación de mocap y retargeting del Viajero

Fecha de trabajo: 22-11-2026 (Bolivia). Especificación preparada con asistencia de IA antes de implementar el módulo mocap. No representa una especificación previa escrita por el estudiante.

## Alcance y evidencia

Implementar Camino A local (MediaPipe Tasks + One Euro + UDP + Blender modal) y herramientas de Camino B (importación BVH/FBX, mapeo, calibración, horneado y telemetría). Conservar los originales. Generar copias en `blender/mocap/`. No crear commits. No inventar capturas, latencias humanas, uso de FreeMoCap ni historial de autoría. Las pruebas sintéticas deben llevar esa etiqueta; no sustituyen los videos personales requeridos por la práctica.

La rúbrica exige volumen cerrado, anatomía completa, identidad fotográfica y pesos funcionales. La imagen añade texturado por fotografía. Se conservará la indumentaria del Viajero y se verificará/proyectará su referencia fotográfica en la copia de entrega. El archivo v2 final anunciado por ESTADO.md no está en disco; existe `blender/v2/sesion_antes_de_v2.blend`. No se asume vigente la validación histórica.

## Flujo

```text
Cámara/video -> OpenCV RGB -> MediaPipe Tasks (33 world landmarks)
 -> confianza -> One Euro por coordenada -> vectores/ángulos/cuaterniones
 -> JSON UDP localhost:5005 -> socket no bloqueante -> TIMER Blender
 -> rotaciones en espacio de armature -> matrix_basis -> malla con pesos
                         +-> muestra JointState / puente ROS 2 opcional

FreeMoCap -> BVH/FBX real -> mapa explícito -> calibración de postura
 -> horneado sobre Viajero -> CSV en radianes -> adaptación ROS 2
```

## Unidades y sistemas

Coordenadas de `pose_world_landmarks`: metros estimados, origen en mitad de caderas (no coordenadas de imagen ni medición métrica calibrada). Tiempos de filtro: segundos monotónicos; timestamp de paquete: milisegundos Unix; rotaciones: radianes; cuaterniones serializados `[w,x,y,z]`. Blender: +Z arriba, personaje hacia -Y, izquierda anatómica +X. Cámara MediaPipe: x derecha de imagen, y abajo, z alejándose; para persona frontal sin espejo: Blender `(x,z,-y)`. Esta matriz tiene determinante +1. ROS cuerpo: `(x_ros,y_ros,z_ros)=(-y_bl,x_bl,z_bl)`, +X hacia delante, +Y izquierda, +Z arriba. No confundir marco óptico con marco corporal ni girar ángulos escalares como si fueran puntos.

## Contrato UDP v1

Objeto JSON UTF-8 <= 60 000 bytes. Campos obligatorios: `schema_version:1`, `session_id` UUID, `timestamp_ms` Unix no negativo, `frame_id` entero creciente, `source` identificable, `coordinate_space:"mediapipe_world_m"`, `landmarks` con claves 0..32, cada una con `name,x,y,z,visibility`, y `joint_rotations` con ángulos de codo/rodilla y cuaterniones de hombro en convención Blender. `tracking:false` y landmarks vacíos cuando no existe pose. Campos adicionales permitidos; valores no finitos, vectores nulos y confianza baja se rechazan antes de aplicar rotaciones. `joint_rotations` es telemetría; Blender resuelve la orientación usando landmarks y su rest pose, nunca confunde el ángulo entre brazo/antebrazo con la orientación del hombro.

## Matemática

`v1=codo-hombro`, `v2=muñeca-codo`; flexión `acos(clamp(dot(v1,v2)/(norm(v1)*norm(v2)),-1,1))`, cero con extremidad extendida. Cuaternión de arco mínimo entre direcciones unitarias a,b: normalizar `[1+dot(a,b), cross(a,b)]`. Paralelos: identidad; antiparalelos: eje perpendicular determinista y giro pi. Esto no recupera el twist axial de un hueso con dos puntos: se conserva el roll de referencia; torso usa hombros/caderas para orientación. Hombros y caderas se orientan por dirección global, articulaciones hijas se convierten al espacio local con matrices de reposo y padre, evitando rotación doble. Escalas y longitudes no se animan.

## Concurrencia y fallos

Productor externo; ninguna inferencia dentro de Blender. Filtro One Euro: min_cutoff=1 Hz, beta=0.03, d_cutoff=1 Hz, dt medido. Reset tras hueco >0.5 s para evitar arrastre. Visibilidad mínima 0.6; hueso ocluido conserva su última pose. UDP solo 127.0.0.1, puerto configurable. TIMER a 30 Hz, `setblocking(False)`, máximo 32 datagramas y presupuesto de drenaje de 4 ms por tick. Se aplica el frame más reciente válido de una sesión, se descartan duplicados, retrasados y paquetes mayores de 500 ms. Reinicio de productor cambia session_id y permite frame 0. A 500 ms sin dato válido: estado STALE, conserva pose, nunca finge continuidad. Stop libera socket y timer; ESC cancela. No `while True` dentro del operador modal.

## ROS 2 y límites

Preparar JointState con header, name, position, velocity y effort vacíos; name/position de igual longitud. Mínimo hombros y codos bilaterales. No existe URDF en el proyecto: límites configurados son didácticos, no límites certificados de hardware. Hombros pitch/roll usan una descomposición explícita de la dirección en marco de torso; no se afirma una solución completa de orientación de 3 GDL. Publicación real requiere rclpy y sensor_msgs en un entorno ROS 2; modo JSON funciona sin ROS. No se envían comandos a hardware.

## Camino B

Elegir FreeMoCap por procesamiento local y disponibilidad del código; comprobar su exportación documentada BVH/FBX. No crear cuenta ni subir fotos. Si falta grabación procesada, entregar importador probado con fixture sintético claramente identificado y registrar pendiente la validación con captura FreeMoCap real. Mapa destino->fuente obligatorio; calibrar frame de referencia con postura física coincidente para corregir A/T pose. Aplicar delta de orientación de fuente respecto a calibración al reposo del destino. Exportar flexión de codos y elevación de hombros desde vectores evaluados, no componentes arbitrarias de Euler.

## Aceptación

Pruebas unitarias: ángulos conocidos, antiparalelos, cambio de ejes, respuesta del filtro, contrato JSON malformado/NaN, orden, sesiones, tiempo obsoleto, oclusión. Integración: UDP real localhost, aplicación y horneado en Blender, reapertura del blend, telemetría finita, cuatro articulaciones, dimensiones constantes. Inspección visual de reposo y flexión, material fotográfico empaquetado, revisión de pesos y topología. PDF renderizado y revisado. Registrar métricas medidas separadas de metas. Entrega no se declara íntegramente aprobada sin captura personal, demostración en vivo y trazabilidad Git del estudiante.

