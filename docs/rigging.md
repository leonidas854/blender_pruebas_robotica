# Rig y alcance de las pruebas

`RIG_Viajero` es un esqueleto FK nativo, con root, pelvis, columna, pecho, cuello,
cabeza, clavículas, brazos, antebrazos, manos, tres segmentos por dedo, muslos,
espinillas, pies, dedos de pies, ojos, telas y bolso.

Las piezas rígidas tienen un hueso dominante. La ropa y el cuerpo usan pesos
normalizados calculados por proximidad a segmentos de huesos; los dedos
distribuyen pesos entre tres articulaciones. Esto es un punto de partida,
no una sustitución del pintado artístico de pesos.

Acciones guardadas:

1. A-pose.
2. T-pose.
3. Brazos elevados.
4. Brazos delante.
5. Codos flexionados.
6. Paso de caminata.
7. Sentado de prueba.
8. Agachado de prueba.
9. Giro de torso.
10. Giro de cabeza.
11. Pose corporal de sorpresa.
12. Pose corporal reflexiva.
13. Pose de presentación.

Cada acción contiene una pose sostenida en fotogramas 1–24. Las acciones 11/12
son corporales y no activan automáticamente las shape keys faciales. El usuario
puede ajustar esas keys por separado. No se entrega un ciclo de caminar.

No hay IK, cambio IK/FK, rig de mandíbula, visemas ni colisión/simulación de tela.
Los faldones del abrigo siguen pelvis: al sentarse o agacharse requieren
controles adicionales y correcciones de penetración. Las poses extremas son
pruebas para localizar problemas, no poses aprobadas para producción.

`validate_viajero.py` comprueba que cada malla tenga UV, material, modificador de
armature y pesos normalizados. No certifica automáticamente ausencia de
colisiones o conservación de volumen.
