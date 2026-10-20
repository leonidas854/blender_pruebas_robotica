# DECISIONES DE DISEÑO: VIAJERO ENTRE ÉPOCAS

### 1. Filosofía de Modelado
- **Modularidad Radical:** Cada elemento de vestuario y accesorio es una pieza separada del cuerpo.
- **Topología Orgánica de Deformación:** Se utilizan loops limpios en hombros, codos, rodillas y pelvis con topología predominantemente quads, facilitando el rigging y deformaciones naturales sin pliegues extraños.
- **Identidad Facial:** Se combina la captura fotogramétrica/biométrica de MediaPipe (`character_data/meshes/face_mesh.obj`) con una reconstrucción anatómica del cráneo y mandíbula para lograr el parecido con Leonidas sin perder la limpieza poligonal.

### 2. Tratamiento de Vestuario y Accesorios
- **Capas Reales:**
  1. Cuerpo base (malla cerrada en A-pose).
  2. Camisa interior de manga recogida.
  3. Chaleco marrón con botones.
  4. Abrigo exterior asimétrico con solapas altas y faldones.
  5. Pantalón holgado con bolsillos cargo y ajustes en tobillos.
  6. Bufanda y telas colgantes modeladas con caída natural.
  7. Botas de cuero con cordones y hebillas independientes.
  8. Accesorios: Cinturón multi-correas, bolso satchel, talismán artesanal y gafas redondeadas.
- **Estilo de Materiales:** Shaders PBR Principled BSDF estilizados con tonos pictóricos mates y rugosidades calibradas para evitar el aspecto de plástico liso o hiperrealismo fotográfico.
