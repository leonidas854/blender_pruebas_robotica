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
- **Blender Version:** Blender 3.6 LTS (in `/usr/local/bin/blender`)
- **Python Runtime:** Python 3.11 managed via `uv` in `.venv/`
- **MCP Bridge:** `mcp-for-blender` communicating over localhost TCP port 9876
- **Vision & 3D Stack:** MediaPipe FaceLandmarker (468/478 3D landmarks), OpenCV, Trimesh, SciPy

---

## Workflows & Runbooks

### 1. Launching Blender with Dedicated GPU

Always run Blender using the GPU offload wrapper to ensure the RTX 4070 renders Cycles scenes:

```bash
./run_blender.sh
```

Or open an existing robotics model directly:
```bash
./run_blender.sh character_data/robot_character.blend
```

---

### 2. Live MCP Control with Blender

To allow AI agents (Antigravity, Claude, Cursor) to inspect the 3D viewport, create objects, adjust bones, and run `bpy` code in real-time:

1. Open Blender:
   ```bash
   ./run_blender.sh
   ```
2. In the 3D Viewport, press **`N`** to open the right sidebar.
3. Select the **`MCP for Blender`** tab.
4. Click **`Start MCP Server`** (the socket server will start listening on port `9876`).
5. Verify the connection from the terminal:
   ```bash
   .venv/bin/python scripts/test_blender_mcp.py
   ```

---

### 3. Characterization Pipeline from Photo to 3D Robot

This workflow characterizes a humanoid robot based on the student's portrait photo for robotics examinations:

#### Option A: One-Command Pipeline
```bash
# Using Webcam:
./characterize.sh --webcam

# Or using an existing photo:
./characterize.sh --image ruta/a/tu_foto.jpg
```

#### Option B: Step-by-Step Execution

1. **Capture Photo:**
   ```bash
   .venv/bin/python scripts/capture_photo.py --output character_data/photo.jpg
   ```
   *(Or pass `--image path/to/selfie.jpg`)*

2. **Extract 3D Facial Landmarks & Anthropometric Metrics:**
   ```bash
   .venv/bin/python scripts/face_mesh_extractor.py --image character_data/photo.jpg
   ```
   Generates:
   - `character_data/character_profile.json` (Interpupillary distance, jaw width, nose projection)
   - `character_data/face_mesh.obj` (3D surface mesh of the face)
   - `character_data/landmark_preview.jpg` (Visual verification)

3. **Build Rigged Robotic Character in Blender:**
   ```bash
   /usr/local/bin/blender -b -P scripts/build_robot_character.py
   ```
   Constructs:
   - Robotic head and custom face plate
   - LED optical sensor visors aligned with pupil distance
   - Articulated neck with hydraulic servos
   - Power core and titanium chassis
   - Armature with `Torso_Root`, `Neck_PitchYaw`, and `Head_RollTilt` bones
   - Studio 3-point lighting and Cycles OptiX setup

---

## Troubleshooting & Tips

- **Blender Python Library Conflict:** If running external python with Blender's bundled binary throws `libcrypt.so.1`, ensure `libxcrypt-compat` is installed:
  ```bash
  sudo pacman -S --needed libxcrypt-compat
  ```
- **Port 9876 Already in Use:** Check for running Blender instances:
  ```bash
  ss -tulpn | grep 9876
  ```
- **Rebuilding Virtual Environment:**
  ```bash
  ./install_blender_robotics.sh
  ```
