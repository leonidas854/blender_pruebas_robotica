#!/usr/bin/env bash
# characterize.sh
# Pipeline completo de caracterización de personaje robótico a partir de fotografía

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
    echo "[!] Entorno virtual no encontrado. Ejecuta primero ./install_blender_robotics.sh"
    exit 1
fi

echo "=========================================================="
echo "   Pipeline de Caracterización Robótica con IA y Blender  "
echo "=========================================================="

IMAGE_ARG=""
USE_WEBCAM=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --image|--photo|-i)
            IMAGE_ARG="$2"
            shift 2
            ;;
        --webcam|-w)
            USE_WEBCAM=true
            shift
            ;;
        *)
            echo "Uso: $0 [--image ruta/a/foto.jpg] [--webcam]"
            exit 1
            ;;
    esac
done

# Paso 1: Captura o selección de imagen
if [ -n "$IMAGE_ARG" ]; then
    echo -e "\n[Paso 1/3] Procesando imagen provista: $IMAGE_ARG..."
    "$PYTHON_BIN" "$SCRIPT_DIR/scripts/capture_photo.py" --image "$IMAGE_ARG"
elif [ "$USE_WEBCAM" = true ] || [ ! -f "$SCRIPT_DIR/character_data/photo.jpg" ]; then
    echo -e "\n[Paso 1/3] Abriendo cámara web para captura de foto..."
    "$PYTHON_BIN" "$SCRIPT_DIR/scripts/capture_photo.py"
else
    echo -e "\n[Paso 1/3] Utilizando foto existente en character_data/photo.jpg..."
fi

# Paso 2: Extracción de malla 3D y landmarks con MediaPipe
echo -e "\n[Paso 2/3] Extrayendo 468 landmarks faciales 3D y generando malla OBJ..."
"$PYTHON_BIN" "$SCRIPT_DIR/scripts/face_mesh_extractor.py" --image "$SCRIPT_DIR/character_data/photo.jpg"

# Paso 3: Construcción del personaje robótico en Blender
echo -e "\n[Paso 3/3] Construyendo personaje robótico articulado en Blender..."
/usr/local/bin/blender -b -P "$SCRIPT_DIR/scripts/build_robot_character.py"

echo -e "\n=========================================================="
echo "   [✓] Caracterización Completada Exitosamente!           "
echo "=========================================================="
echo "Archivos generados en character_data/:"
echo " - photo.jpg               : Foto original/capturada"
echo " - landmark_preview.jpg    : Foto con detección de landmarks"
echo " - face_mesh.obj           : Malla 3D facial generada"
echo " - character_profile.json  : Métricas antropométricas extraídas"
echo " - robot_character.blend   : Escena completa de Blender lista"
echo ""
echo "Para abrir el modelo en Blender:"
echo "    ./run_blender.sh character_data/robot_character.blend"
echo "=========================================================="
