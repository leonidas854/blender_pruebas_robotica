#!/usr/bin/env python3
"""
scripts/phase4_block_out.py
=====================================================
FASE 4 - PASO 1: BLOQUEO ANATÓMICO MODULAR HUMANOIDE (1.80m)
Orquestador principal modular que ensambla todos los subsistemas anatómicos:
  - Cabeza, rostro, mandíbula, esternocleidomastoideo y trapecio.
  - Clavículas, esternón, pectorales, dorsales, serratos y 6-pack abdominal.
  - Pelvis, crestas ilíacas, sacro y glúteos.
  - Deltoides de 3 cabezas, bíceps, tríceps, antebrazos y manos con 5 dedos.
  - Cuádriceps cuádruples, rótula, gemelos asimétricos, tendón de Aquiles y pies con arco.

Salidas:
  - character_data/robot_v1_blockout.blend
  - character_data/phase4_capture1_blockout.png
"""

import bpy
import os
import sys

# Asegurar importación del paquete modular robotics_anatomy
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from robotics_anatomy import (
    get_body_metrics,
    create_clay_material,
    build_head_and_neck,
    build_torso,
    build_pelvis,
    build_arms_and_hands,
    build_legs_and_feet,
    setup_studio_cyclorama,
    setup_studio_lighting,
    setup_studio_camera,
    render_and_save,
)

OUTPUT_DIR = os.path.join(BASE_DIR, "character_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    print("=================================================================")
    print("  FASE 4: BLOQUEO ANATÓMICO MODULAR HUMANOIDE COMPLETO (1.80m)    ")
    print("=================================================================")

    # 1. Reiniciar escena limpia
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Crear colección principal del personaje
    col = bpy.data.collections.new("Robot_Anatomy_Blockout_180cm")
    bpy.context.scene.collection.children.link(col)

    # 3. Cargar métricas antropométricas reales de 1.80m
    metrics = get_body_metrics(BASE_DIR)

    # 4. Crear material clay neutro para el bloqueo
    mat_clay = create_clay_material("Mat_Clay_Anatomy")

    # 5. Ensamblar todos los sistemas anatómicos modulares
    print("[*] Construyendo cabeza, rostro, cuello y trapecio...")
    build_head_and_neck(col, mat_clay, metrics)

    print("[*] Construyendo caja torácica, clavículas, pectorales, dorsales y 6-pack...")
    build_torso(col, mat_clay, metrics)

    print("[*] Construyendo pelvis, sacro y glúteos...")
    build_pelvis(col, mat_clay, metrics)

    print("[*] Construyendo brazos, deltoides (3 cabezas), bíceps, tríceps y manos con 5 dedos...")
    build_arms_and_hands(col, mat_clay, metrics)

    print("[*] Construyendo piernas, cuádriceps, rótula, gemelos asimétricos y pies con 5 dedos...")
    build_legs_and_feet(col, mat_clay, metrics)

    # 6. Configurar entorno de estudio fotográfico
    print("[*] Configurando ciclorama, iluminación 3-puntos y cámara Track-To...")
    setup_studio_cyclorama(col)
    setup_studio_lighting(col)
    setup_studio_camera(col, target_z=0.90, view="front", lens=40)

    # 7. Renderizar captura 1 y guardar archivo .blend
    out_img = os.path.join(OUTPUT_DIR, "phase4_capture1_blockout.png")
    out_blend = os.path.join(OUTPUT_DIR, "robot_v1_blockout.blend")

    render_and_save(out_img, out_blend, samples=128)
    print(f"\n[✓] FASE 4 PASO 1 (BLOQUEO ANATÓMICO MODULAR) COMPLETADO EXITOSAMENTE.")

if __name__ == "__main__":
    main()
