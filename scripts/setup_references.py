#!/usr/bin/env python3
"""
scripts/setup_references.py
=====================================================
Configura la escena inicial de Blender (01_referencias.blend):
  - Sistema métrico con altura calibrada a 1.80 m.
  - Colecciones estructuradas del proyecto (CH_VIAJERO).
  - Planos de referencia visuales ortográficos en la vista Frontal y Lateral.
"""

import bpy
import os
import math

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REF_DIR  = os.path.join(BASE_DIR, "referencias")
BLEND_DIR = os.path.join(BASE_DIR, "blender")
os.makedirs(BLEND_DIR, exist_ok=True)

COLLECTION_NAMES = [
    "00_REFERENCES",
    "01_BODY",
    "02_HAIR",
    "03_CLOTHING",
    "04_ACCESSORIES",
    "05_RIG",
    "06_CAMERAS",
    "07_LIGHTS",
    "08_PRESENTATION",
]

def create_reference_plane(name, img_path, location, rotation, height_m=1.80, col=None):
    if not os.path.exists(img_path):
        print(f"[!] Aviso: Imagen de referencia no encontrada: {img_path}")
        return None

    img = bpy.data.images.load(img_path)
    aspect = img.size[0] / img.size[1] if img.size[1] > 0 else 1.0
    width_m = height_m * aspect

    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0))
    plane = bpy.context.active_object
    plane.name = name
    plane.scale = (width_m, height_m, 1.0)
    plane.location = location
    plane.rotation_euler = rotation
    # Ocultar en renders para no obstruir las cámaras de inspección 3D
    plane.hide_render = True

    # Crear material no iluminado (Emissive) para visualización clara
    mat = bpy.data.materials.new(f"Mat_{name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    node_tex = nodes.new("ShaderNodeTexImage")
    node_tex.image = img
    node_emit = nodes.new("ShaderNodeEmission")
    node_emit.inputs["Strength"].default_value = 1.0
    node_out = nodes.new("ShaderNodeOutputMaterial")

    mat.node_tree.links.new(node_tex.outputs["Color"], node_emit.inputs["Color"])
    mat.node_tree.links.new(node_emit.outputs["Emission"], node_out.inputs["Surface"])

    plane.data.materials.append(mat)

    if col:
        for c in list(plane.users_collection):
            c.objects.unlink(plane)
        col.objects.link(plane)

    return plane

def main():
    print("=================================================================")
    print("  CONFIGURACIÓN DE ESCENA Y REFERENCIAS (VIAJERO ENTRE ÉPOCAS)  ")
    print("=================================================================")

    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Configurar sistema métrico
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'

    # Colección raíz
    master_col = bpy.data.collections.new("CH_VIAJERO")
    scene.collection.children.link(master_col)

    cols = {}
    for c_name in COLLECTION_NAMES:
        col = bpy.data.collections.new(c_name)
        master_col.children.link(col)
        cols[c_name] = col

    # Planos de referencia en 00_REFERENCES
    ref_col = cols["00_REFERENCES"]

    # 1. Referencia Frontal del Cuerpo Base (desplazada en Y=+0.6 para no estorbar el modelado)
    ref_front_path = os.path.join(REF_DIR, "cuerpo_base", "02_cuerpo_base_referencia.png")
    create_reference_plane(
        "Ref_Frontal_CuerpoBase",
        ref_front_path,
        location=(0.0, 0.60, 0.90),
        rotation=(math.radians(90), 0, 0),
        height_m=1.80,
        col=ref_col
    )

    # 2. Referencia Lateral de Perfil (desplazada en X=-0.80)
    ref_lat_path = os.path.join(REF_DIR, "fotografias_originales", "foto_03_lateral_perfil.jpeg")
    create_reference_plane(
        "Ref_Lateral_PerfilLeonidas",
        ref_lat_path,
        location=(-0.80, 0.0, 0.90),
        rotation=(math.radians(90), 0, math.radians(90)),
        height_m=1.80,
        col=ref_col
    )

    # Guardar 01_referencias.blend
    blend_path = os.path.join(BLEND_DIR, "01_referencias.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"\n[✓] Escena de referencias guardada en: {blend_path}")
    print("=================================================================")

if __name__ == "__main__":
    main()
