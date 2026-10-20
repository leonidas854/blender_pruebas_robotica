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
│   └── skills/blender-robotics/ # Habilidad de Antigravity para automatizar el pipeline
├── character_data/              # Datos generados (malla, perfiles, escena .blend)
├── models/                      # Modelos de redes neuronales (face_landmarker.task)
├── scripts/
│   ├── capture_photo.py         # Captura desde webcam o procesador de foto
│   ├── face_mesh_extractor.py   # Extractor de landmarks 3D y generador OBJ
│   ├── build_robot_character.py # Generador procedural en Blender
│   └── test_blender_mcp.py      # Verificador de conexión MCP con Blender
├── characterize.sh              # Script maestro del pipeline completo
├── install_blender_robotics.sh  # Instalador de dependencias, uv, venv y addons
└── run_blender.sh               # Lanzador de Blender con aceleración GPU NVIDIA
```

## 🛠️ Instalación y Requisitos

1. **Requisitos del sistema:**
   - Linux (Arch Linux probado con NVIDIA GeForce RTX 4070)
   - Blender 3.6 LTS
   - Python 3.11

2. **Instalación automática:**
   ```bash
   chmod +x install_blender_robotics.sh characterize.sh run_blender.sh
   ./install_blender_robotics.sh
   ```

## 🎯 Uso del Pipeline

### 1. Ejecutar pipeline completo desde la webcam
```bash
./characterize.sh --webcam
```

### 2. Ejecutar pipeline usando una fotografía existente
```bash
./characterize.sh --image ruta/a/mi_foto.jpg
```

### 3. Abrir la escena generada en Blender con GPU OptiX
```bash
./run_blender.sh character_data/robot_character.blend
```

### 4. Probar la conexión MCP con Blender
```bash
.venv/bin/python scripts/test_blender_mcp.py
```
