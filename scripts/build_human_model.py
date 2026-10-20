#!/usr/bin/env python3
"""
scripts/build_human_model.py
=====================================================
GENERADOR DEL MOLDE DE LA PERSONA (LEONIDAS 1.80m)
Genera el modelo poligonal humano masculino completo a escala real basado en sus fotos:
  1. Basemesh orgánico continuo en Pose A (izq).
  2. Molde anatómico muscular masculino esculpido (der).
  3. Render de comparación lado a lado (formato de referencia del usuario).
  4. Renders frontal y tres cuartos en alta resolución.
  5. Archivo maestro Blender: character_data/blends/leonidas_human_180.blend.
"""

import bpy
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from human_modeling import (
    get_user_biometrics,
    build_complete_human_mesh,
    setup_human_studio,
    render_human_views,
)
from human_modeling.studio_render import setup_camera

OUTPUT_DIR  = os.path.join(BASE_DIR, "character_data")
RENDERS_DIR = os.path.join(OUTPUT_DIR, "renders", "human")
BLENDS_DIR  = os.path.join(OUTPUT_DIR, "blends", "human")
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(BLENDS_DIR, exist_ok=True)

def create_sculpt_material(name="Mat_Human_Sculpt"):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.64, 0.66, 0.70, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.44
        bsdf.inputs["Metallic"].default_value = 0.04
    return mat

def main():
    print("=================================================================")
    print("  MODELADO POLIGONAL DE LA PERSONA (LEONIDAS 1.80m)             ")
    print("=================================================================")

    # 1. Reiniciar escena limpia
    bpy.ops.wm.read_factory_settings(use_empty=True)

    col = bpy.data.collections.new("Leonidas_Human_Model_180cm")
    bpy.context.scene.collection.children.link(col)

    metrics = get_user_biometrics(BASE_DIR)
    mat_clay = create_sculpt_material()

    # 2. Configurar ciclorama e iluminación
    setup_human_studio(col)

    # 3. Construir Molde 1: Basemesh Orgánico (lado izquierdo X = -0.85)
    print("\n[*] Construyendo Molde 1: Basemesh Orgánico continuo...")
    mesh_base = build_complete_human_mesh(col, mat_clay, metrics, mode="basemesh", base_dir=BASE_DIR)
    mesh_base.location.x = -0.85

    # 4. Construir Molde 2: Molde Anatómico Muscular (lado derecho X = +0.85)
    print("\n[*] Construyendo Molde 2: Molde Anatómico Muscular completo...")
    mesh_anat = build_complete_human_mesh(col, mat_clay, metrics, mode="anatomical", base_dir=BASE_DIR)
    mesh_anat.location.x = 0.85

    # 5. Render de Comparación Lado a Lado (idéntico a la referencia)
    print("\n[*] Renderizando Comparación Lado a Lado (Basemesh vs Anatómico)...")
    setup_camera(col, target_z=0.90, view="comparison", lens=40, dist=5.2)
    cmp_img = os.path.join(RENDERS_DIR, "human_model_comparison.png")
    master_blend = os.path.join(BLENDS_DIR, "leonidas_human_180.blend")
    render_human_views(cmp_img, blend_path=master_blend, samples=128)

    # 6. Render individual frontal del modelo anatómico centrado
    print("\n[*] Renderizando vista frontal del modelo anatómico...")
    mesh_base.hide_render = True
    mesh_anat.location.x = 0.0
    setup_camera(col, target_z=0.90, view="front", lens=40, dist=4.8)
    front_img = os.path.join(RENDERS_DIR, "human_model_front.png")
    render_human_views(front_img, samples=128)

    # 7. Render individual 3/4 dinámico
    print("\n[*] Renderizando vista 3/4 del modelo anatómico...")
    setup_camera(col, target_z=0.90, view="34", lens=42, dist=4.6)
    view34_img = os.path.join(RENDERS_DIR, "human_model_34view.png")
    render_human_views(view34_img, samples=128)

    # Restaurar visibilidad para el .blend final
    mesh_base.hide_render = False
    mesh_anat.location.x = 0.85
    bpy.ops.wm.save_as_mainfile(filepath=master_blend)

    print("\n=================================================================")
    print("[✓] MODELADO POLIGONAL DE LA PERSONA FINALIZADO CON ÉXITO")
    print(f"    - Blend Maestro:   {master_blend}")
    print(f"    - Comparación:     {cmp_img}")
    print(f"    - Frontal:         {front_img}")
    print(f"    - Vista 3/4:       {view34_img}")
    print("=================================================================")

if __name__ == "__main__":
    main()
