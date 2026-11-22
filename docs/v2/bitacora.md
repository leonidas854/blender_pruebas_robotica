# Bitácora auténtica — 22 de noviembre de 2026

## Instrucciones recibidas
El usuario solicita revisar la documentación recién subida, iniciar MCP, realizar
una nueva entrega y favorecer modelado/esculpido orgánico frente a piezas geométricas
visibles, buscando semejanza con sus bocetos.

Aclaración planteada: incluir ambas modalidades de captura o priorizar el personaje.
Respuesta textual del usuario: «Primero personaje, rig y renders».

## Trabajo y revisión
- Lectura de ESTADO, GUIA, materiales, pendientes, rig y habilidades del proyecto.
- Lectura de la guía de práctica y rúbrica nuevas; inspección de la lámina de
  requisitos, primeras diapositivas, fotos, concepto aprobado y ficha de abrigo.
- Arranque del add-on MCP instalado con Blender 5.2.4. Comunicación local verificada.
  El arranque de terminal inicial terminó al llegar nueva entrada del usuario; se
  relanzó Blender en sesión independiente. No se cambiaron preferencias globales.
- La primera llamada que cargaba archivo y modelaba en el mismo contexto falló.
  Se separó la carga de archivo de las operaciones para evitar contexto obsoleto.
- Nueva anatomía por unión de volúmenes, remallado voxel 1.8 mm y relajación.
  Rostro con desplazamientos continuos; nuevas masas de cabello y pliegues.
- Primera revisión visual: piel atravesaba hombros/entrepierna, bufanda penetraba
  el cuello de camisa y los pliegues de pantalón eran demasiado periódicos.
- Primera validación: anatomía cerrada, pero dos islotes de ocho vértices del voxel.
- Segunda revisión: ajuste anatómico bajo ropa, extensión de la pelvis del pantalón,
  bufanda más adelantada, pliegues localizados y eliminación de restos diminutos.

El registro numérico definitivo y las imágenes están junto a esta bitácora.
Esta bitácora resume esta sesión real; no inventa autoría estudiantil, commits
progresivos de dos integrantes ni una grabación de captura que no se realizó.
- Tercera revisión: unión del cabello en una masa editable, coloración suave de
  labios y mejillas, afinado de cejas. No se añadieron texturas fotográficas falsas.
- Revisión multivista: se eliminaron mangas interiores que atravesaban el abrigo;
  ajuste de pantorrillas bajo el pantalón, reducción de proyección nasal,
  reproyección de bandolera/costuras traseras y ajuste del cinturón.
- La escena conserva las tomas de iteración para contrastar decisiones. El resultado
  sigue siendo estilizado y requiere revisión de parecido; no se declara equivalencia
  visual exacta con la ilustración de referencia.
- La evidencia sin ropa mostró transiciones demasiado duras en hombros y pelvis.
  Se añadió relajación localizada de la malla, conservando topología, pesos y deltas
  de expresiones. Se corrigió una referencia temporal de vertex group invalidada
  por Blender al aplicar el modificador, recuperando la copia previa guardada.
- Se cerró el encuadre de la cámara de presentación para reducir espacio vacío.
- El suavizado aislado redondeaba bordes pero no aportaba suficiente volumen en
  las uniones. Se añadieron puentes anatómicos de cadera, hombro y muñeca, se
  fundieron con la superficie y se transfirieron color y deltas faciales por
  proximidad. Los pesos se reconstruyeron después del cambio de topología.
- La revisión de la portada detectó erosión excesiva de dedos tras la relajación.
  Se recuperan palma, muñeca y dedos del original preservado, fundiéndolos con
  la nueva anatomía y reconstruyendo los pesos antes de actualizar la entrega.
