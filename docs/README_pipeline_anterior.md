# Blender & Robotics: Pipeline de Caracterización 3D con IA

Pipeline integral para captura fotográfica/webcam, extracción de malla facial 3D antropométrica con MediaPipe (468 landmarks), generación de modelos robóticos humanoides articulados en Blender 3.6 LTS y control bidireccional mediante Model Context Protocol (MCP). Optimizado para aceleración por GPU NVIDIA (Cycles con OptiX).

## 🚀 Características

- **Captura Flexible:** Obtención de fotos desde cámara web en tiempo real con guías biométricas o procesamiento de archivos JPG/PNG existentes (`scripts/capture_photo.py`).
- **Extracción de Malla Facial 3D e IA:** Estimación de 468 landmarks 3D con MediaPipe FaceLandmarker, métricas antropométricas (anchos de mandíbula, pómulos, ojos, altura de frente) y generación de archivo OBJ texturizable (`scripts/face_mesh_extractor.py`).
- **Generación Procedural en Blender:** Creación automatizada del chasis robótico, articulaciones metálicas, torso estilizado, montaje de la máscara facial y materiales PBR (plásticos duros, metales y emisores LED) (`scripts/build_robot_character.py`).
- **Integración MCP (Model Context Protocol):** Conexión con agentes de IA (Antigravity) para inspección de escena, renderizado y manipulación en tiempo real (`scripts/test_blender_mcp.py`).
- **Aceleración Hardware:** Script lanzador configurado para GPU NVIDIA GeForce RTX con backend OptiX en Arch Linux (`run_blender.sh`).

## 📁 Estructura del Proyecto

```text
├── .agents/
│   └── skills/blender-robotics/ # Skill de Antigravity para automatizar el pipeline
├── character_data/              # Datos generados, métricas y renders
│   ├── blends/
│   │   ├── human/               # Modelo activo: leonidas_human_180.blend
│   │   └── robot_archive/       # Modelos robóticos anteriores archivados
│   ├── meshes/
│   │   └── face_mesh.obj        # Malla 3D facial generada con MediaPipe
│   ├── metrics/
│   │   ├── body_metrics_real.json   # Biometría corporal completa (altura 1.80m)
│   │   └── character_profile.json   # Perfil antropométrico
│   └── renders/
│       ├── human/               # Renders del modelo humano (frontal, 3/4, comparativo)
│       ├── biometrics/          # Fotos y esquemas debug de MediaPipe
│       └── robot_archive/       # Renders de fases robóticas anteriores
├── fotos_mias/                  # Fotografías de referencia del usuario (Leonidas)
├── models/                      # Modelos neuronales (pose_landmarker, face_landmarker)
├── pdfs/                        # Documentación narrativa y de personajes en PDF
├── references/                  # Imágenes de referencia anatómica y modelado 3D
├── scripts/
│   ├── build_human_model.py     # Script maestro generador del modelo humano
│   ├── extract_body_metrics.py  # Extracción biométrica con MediaPipe & OpenCV
│   ├── human_modeling/          # Paquete modular de modelado poligonal continuo
│   │   ├── face_head.py         # Cabeza, mandíbula, rasgos faciales y cuello
│   │   ├── hands_feet.py        # Manos y pies con 5 dedos articulados
│   │   ├── mesh_builder.py      # Fusión orgánica y remallado poligonal
│   │   ├── metrics.py           # Calibración biométrica a 1.80m
│   │   ├── musculature.py       # Pectorales, abdomen, dorsales, deltoides y piernas
│   │   ├── skeleton_core.py     # Núcleo continuo estanco en Pose A
│   │   └── studio_render.py     # Ciclorama, iluminación de 3 puntos y cámaras
│   └── archive_robotics/        # Scripts históricos de la fase robótica previa
├── characterize.sh              # Script histórico de pipeline robótico
├── install_blender_robotics.sh  # Instalador de dependencias y modelos
└── run_blender.sh               # Lanzador de Blender con GPU NVIDIA RTX 4070 (OptiX)
```

## 🛠️ Instalación y Requisitos

1. **Requisitos del sistema:**
   - Linux (Arch Linux probado con NVIDIA GeForce RTX 4070)
   - Blender 5.2 LTS (en `/opt/blender-lts/blender`)
   - Python 3.11 con OpenCV y MediaPipe

2. **Instalación:**
   ```bash
   chmod +x install_blender_robotics.sh characterize.sh run_blender.sh
   ./install_blender_robotics.sh
   ```

## 🎯 Uso del Pipeline

### 1. Extracción de Biometría Real (1.80m)
```bash
python3 scripts/extract_body_metrics.py
```

### 2. Generar el Modelo Poligonal Humano y Renders
```bash
blender -b -P scripts/build_human_model.py
```

### 3. Abrir la escena en Blender interactivo con GPU OptiX
```bash
./run_blender.sh character_data/blends/human/leonidas_human_180.blend
```
