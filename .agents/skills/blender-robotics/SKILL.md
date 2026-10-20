---
name: blender-robotics
description: >-
  Use this skill to control Blender via MCP, run robotics 3D characterization pipelines from photos, generate 3D facial meshes with MediaPipe, and create rigged humanoid robotics models in Blender.
---

# Blender Robotics & AI Characterization Skill

This skill provides step-by-step procedures and runbooks for automating Blender 3D modeling, integrating with LLM agents via Model Context Protocol (MCP), and creating humanoid robot characterizations from portrait photos for robotics engineering.

## System & Architecture

- **Operating System:** Arch Linux
- **GPU:** NVIDIA GeForce RTX 4070 Laptop GPU (OptiX & CUDA acceleration)
- **Blender Version:** Blender 5.2 LTS (en `/opt/blender-lts/blender` y `~/.local/bin/blender`)
- **Python Runtime:** Python 3.11 con OpenCV y MediaPipe Tasks API
- **Modelos Neuronales:** `models/pose_landmarker_full.task` y `models/face_landmarker.task`
- **Fotos de Referencia:** `fotos_mias/` (calibrado a 1.80m de altura)

---

## Workflows & Runbooks

### 1. Extracción de Métricas Biométricas de la Persona (1.80m)

Procesa las fotografías del usuario ubicadas en `fotos_mias/` para extraer proporciones antropométricas exactas y la placa facial 3D:

```bash
python3 scripts/extract_body_metrics.py
```
Salidas generadas:
- `character_data/metrics/body_metrics_real.json` (Hombros 44.3cm, pecho 39cm, envergadura 1.77m, altura 1.80m)
- `character_data/renders/biometrics/body_analysis_debug.png` (Verificación visual del esqueleto y mediciones)
- `character_data/meshes/face_mesh.obj` (Malla 3D facial personalizada de Leonidas)
- `character_data/renders/biometrics/landmark_preview.jpg` (Puntos clave faciales y distancia interpupilar)

---

### 2. Modelado Poligonal Continuo de la Persona (Pose A)

Construye la figura humana masculina en Pose A (~42° brazos) con código modular estructurado en `scripts/human_modeling/`:

```bash
blender -b -P scripts/build_human_model.py
```
Genera:
- **Molde 1 (Basemesh Orgánico):** Malla poligonal continua, limpia y proporcional.
- **Molde 2 (Escultura Anatómica Muscular):** Definición atlética completa (pectorales, 6-pack abdominal, dorsales, deltoides, cuádriceps, gemelos).
- **Renders de Estudio:**
  - `character_data/renders/human/human_model_comparison.png` (Comparación lado a lado: Basemesh vs Anatómico)
  - `character_data/renders/human/human_model_front.png` (Vista frontal completa en ciclorama)
  - `character_data/renders/human/human_model_34view.png` (Vista 3/4 dinámica de escultura)
- **Archivo Maestro:** `character_data/blends/human/leonidas_human_180.blend`

---

### 3. Lanzar Blender con Aceleración NVIDIA RTX 4070

Para inspeccionar o esculpir el modelo en la interfaz interactiva con OptiX:

```bash
./run_blender.sh character_data/blends/human/leonidas_human_180.blend
```

---

## Troubleshooting & Tips

- **Binario de Blender:** Enlazar a `/opt/blender-lts/blender`:
  ```bash
  ln -sf /opt/blender-lts/blender ~/.local/bin/blender
  ```
- **Aceleración OptiX en Cycles:** La RTX 4070 Laptop GPU renderiza escenas completas en ~12-15 segundos.
