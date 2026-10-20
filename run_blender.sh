#!/usr/bin/env bash
# run_blender.sh
# Lanza Blender con aceleración de GPU dedicada NVIDIA GeForce RTX 4070

set -e

BLENDER_BIN="/usr/local/bin/blender"

if [ ! -x "$BLENDER_BIN" ]; then
    BLENDER_BIN=$(which blender 2>/dev/null || true)
fi

if [ -z "$BLENDER_BIN" ]; then
    echo "[!] Error: No se encontró el ejecutable de Blender."
    exit 1
fi

echo "[*] Iniciando Blender con aceleración NVIDIA RTX 4070..."

# Forzar render offload en NVIDIA si prime-run está disponible o mediante variables de entorno NVIDIA
if command -v prime-run >/dev/null 2>&1; then
    exec prime-run "$BLENDER_BIN" "$@"
else
    export __NV_PRIME_RENDER_OFFLOAD=1
    export __GLX_VENDOR_LIBRARY_NAME=nvidia
    export __VK_LAYER_NV_optimus=NVIDIA_only
    exec "$BLENDER_BIN" "$@"
fi
