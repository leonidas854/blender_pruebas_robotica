#!/usr/bin/env bash
# ==============================================================================
# install_blender_robotics.sh
# Script de instalación y configuración integral para Blender, MCP,
# aceleración NVIDIA OptiX y pipeline de caracterización robótica con IA.
# Sistema objetivo: Arch Linux + NVIDIA RTX 4070 Laptop GPU + Blender 3.6 LTS
# ==============================================================================

set -e

# Colores para salida de terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${BLUE}===================================================================${NC}"
echo -e "${BLUE}       Instalador: Blender 3D + MCP + Robótica e IA               ${NC}"
echo -e "${BLUE}===================================================================${NC}"

# 1. Verificar Blender
echo -e "\n${YELLOW}[1/7] Verificando instalación de Blender...${NC}"
BLENDER_PATH="/usr/local/bin/blender"
if [ ! -x "$BLENDER_PATH" ]; then
    BLENDER_PATH=$(which blender 2>/dev/null || true)
fi

if [ -z "$BLENDER_PATH" ]; then
    echo -e "${RED}[!] Blender no encontrado en /usr/local/bin/blender ni en el PATH.${NC}"
    echo -e "[*] Asegúrate de tener Blender instalado en tu sistema."
    exit 1
fi

BLENDER_VER=$("$BLENDER_PATH" --version | head -n 1)
echo -e "${GREEN}[+] Detectado: $BLENDER_VER${NC}"

# 2. Verificar libxcrypt-compat (para el Python interno de Blender en Arch Linux)
echo -e "\n${YELLOW}[2/7] Verificando compatibilidad de librerías del sistema...${NC}"
if ! pacman -Qs libxcrypt-compat >/dev/null 2>&1; then
    echo -e "${YELLOW}[*] 'libxcrypt-compat' no está instalado. En Arch Linux es necesario para evitar el error 'libcrypt.so.1'.${NC}"
    if sudo -n true 2>/dev/null; then
        echo -e "${BLUE}[*] Instalando libxcrypt-compat automáticamente...${NC}"
        sudo pacman -S --needed --noconfirm libxcrypt-compat
    else
        echo -e "${YELLOW}[!] Recomendación: Ejecuta en otra terminal: 'sudo pacman -S --needed libxcrypt-compat'${NC}"
    fi
else
    echo -e "${GREEN}[+] libxcrypt-compat ya está presente en el sistema.${NC}"
fi

# 3. Instalar o verificar herramienta 'uv'
echo -e "\n${YELLOW}[3/7] Verificando gestor ultra-rápido de Python (uv)...${NC}"
UV_BIN="$HOME/.local/bin/uv"
if command -v uv >/dev/null 2>&1; then
    UV_BIN=$(command -v uv)
elif [ ! -x "$UV_BIN" ]; then
    echo -e "[*] Instalando uv en espacio de usuario..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    UV_BIN="$HOME/.local/bin/uv"
fi
echo -e "${GREEN}[+] uv disponible en: $UV_BIN ($("$UV_BIN" --version))${NC}"

# 4. Crear entorno virtual con Python 3.11 e instalar dependencias de IA
echo -e "\n${YELLOW}[4/7] Configurando entorno virtual (.venv) con dependencias de IA y robótica...${NC}"
if [ ! -d ".venv" ]; then
    "$UV_BIN" venv .venv --python 3.11
fi

echo -e "[*] Instalando librerías científicas y de visión por computador..."
"$UV_BIN" pip install --python .venv/bin/python \
    opencv-python \
    mediapipe \
    numpy \
    scipy \
    trimesh \
    pillow \
    requests \
    fastmcp \
    mcp \
    mcp-for-blender

# 5. Descargar modelo de MediaPipe FaceLandmarker si no existe
echo -e "\n${YELLOW}[5/7] Verificando modelo de red neuronal de MediaPipe...${NC}"
mkdir -p models
if [ ! -f "models/face_landmarker.task" ]; then
    echo -e "[*] Descargando face_landmarker.task..."
    curl -L -o models/face_landmarker.task \
        https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
fi
echo -e "${GREEN}[+] Modelo neuronal listo: models/face_landmarker.task${NC}"

# 6. Instalar y configurar Add-on MCP en Blender y aceleración OptiX
echo -e "\n${YELLOW}[6/7] Configurando Blender (Add-on MCP, Rigify, MeasureIt y GPU OptiX)...${NC}"
ADDON_DIR="$HOME/.config/blender/3.6/scripts/addons"
mkdir -p "$ADDON_DIR"

# Instalar addon mcp-for-blender
.venv/bin/mcp-for-blender install-addon >/dev/null 2>&1 || true
if [ -f "$HOME/.config/blender/5.2/scripts/addons/blender_mcp.py" ] && [ ! -f "$ADDON_DIR/blender_mcp.py" ]; then
    cp -f "$HOME/.config/blender/5.2/scripts/addons/blender_mcp.py" "$ADDON_DIR/blender_mcp.py"
fi

# Guardar configuración en Blender
"$BLENDER_PATH" -b --python-expr "
import bpy

addons = [
    'blender_mcp',
    'rigify',
    'io_import_images_as_planes',
    'add_mesh_extra_objects',
    'add_curve_extra_objects',
    'measureit',
    'cycles',
]

for a in addons:
    try:
        bpy.ops.preferences.addon_enable(module=a)
    except Exception as e:
        print(f'Addon {a}: {e}')

try:
    c = bpy.context.preferences.addons['cycles'].preferences
    c.compute_device_type = 'OPTIX'
    for d in c.get_devices_for_type('OPTIX'):
        if 'RTX' in d.name or 'GeForce' in d.name:
            d.use = True
except Exception as e:
    pass

bpy.ops.wm.save_userpref()
" >/dev/null 2>&1

echo -e "${GREEN}[+] Blender 3.6 configurado con Addons y NVIDIA GeForce RTX 4070 (OptiX).${NC}"

# 7. Registrar servidor MCP en Antigravity
echo -e "\n${YELLOW}[7/7] Registrando servidor MCP en Antigravity (~/.gemini/config/mcp_config.json)...${NC}"
mkdir -p "$HOME/.gemini/config"
cat <<EOF > "$HOME/.gemini/config/mcp_config.json"
{
  "mcpServers": {
    "blender": {
      "command": "$PROJECT_DIR/.venv/bin/mcp-for-blender",
      "args": []
    }
  }
}
EOF

# Otorgar permisos de ejecución a los scripts
chmod +x run_blender.sh characterize.sh scripts/*.py

echo -e "\n${GREEN}===================================================================${NC}"
echo -e "${GREEN}   ¡INSTALACIÓN Y CONFIGURACIÓN COMPLETADA CON ÉXITO!              ${NC}"
echo -e "${GREEN}===================================================================${NC}"
echo -e "Instrucciones de uso:"
echo -e "  1. Para iniciar Blender con aceleración de GPU dedicada:"
echo -e "     ${BLUE}./run_blender.sh${NC}"
echo -e "  2. Para iniciar el servidor MCP dentro de Blender:"
echo -e "     Abre Blender -> En el 3D Viewport presiona '${YELLOW}N${NC}' -> pestaña '${YELLOW}MCP for Blender${NC}' -> clic en '${GREEN}Start MCP Server${NC}'"
echo -e "  3. Para probar la conexión MCP:"
echo -e "     ${BLUE}.venv/bin/python scripts/test_blender_mcp.py${NC}"
echo -e "  4. Para caracterizar tu personaje robótico a partir de tu foto:"
echo -e "     - Usando webcam:      ${BLUE}./characterize.sh --webcam${NC}"
echo -e "     - Usando foto JPG/PNG: ${BLUE}./characterize.sh --image ruta/a/tu_foto.jpg${NC}"
echo -e "${GREEN}===================================================================${NC}"
