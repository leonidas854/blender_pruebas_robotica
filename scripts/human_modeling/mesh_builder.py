"""
scripts/human_modeling/mesh_builder.py
Constructor y fusionador poligonal de la persona (Leonidas 1.80m).
Permite generar el Basemesh Orgánico (Molde Base) y la Escultura Anatómica Muscular.
"""

import bpy
import mathutils
from .skeleton_core import create_continuous_apose_core
from .musculature import create_male_musculature
from .face_head import create_male_head_and_face
from .hands_feet import create_detailed_hands_and_feet

def build_complete_human_mesh(col, mat, metrics, mode="anatomical", base_dir=None):
    """
    Construye la malla poligonal humana continua:
      - mode='basemesh': Silueta orgánica limpia y suave.
      - mode='anatomical': Molde con definición muscular masculina completa.
    """
    # 1. Crear el núcleo continuo en Pose A
    core_obj = create_continuous_apose_core(col, mat, metrics)
    parts_to_join = [core_obj]

    # 2. Agregar cabeza y rostro
    head_parts = create_male_head_and_face(col, mat, metrics, base_dir=base_dir)
    parts_to_join.extend(head_parts)

    # 3. Agregar manos y pies detallados
    digit_parts = create_detailed_hands_and_feet(col, mat, metrics)
    parts_to_join.extend(digit_parts)

    # 4. Si el modo es anatómico, agregar las capas musculares
    if mode == "anatomical":
        musc_parts = create_male_musculature(col, mat, metrics)
        parts_to_join.extend(musc_parts)

    # 5. Unificar todos los volúmenes en una sola malla continua
    for p in parts_to_join:
        p.select_set(True)
    bpy.context.view_layer.objects.active = core_obj
    bpy.ops.object.join()

    human_mesh = bpy.context.active_object
    human_mesh.name = f"Leonidas_Human_{mode.capitalize()}_180"

    # 6. Remallado poligonal voxel para sellar uniones en una superficie manifold
    voxel_sz = 0.0085 if mode == "anatomical" else 0.0105
    human_mesh.data.remesh_voxel_size = voxel_sz
    bpy.ops.object.voxel_remesh()

    # 7. Suavizado y relajación orgánica
    mod_smooth = human_mesh.modifiers.new("Smooth_Relax", "SMOOTH")
    mod_smooth.factor = 0.45 if mode == "anatomical" else 0.65
    mod_smooth.iterations = 2 if mode == "anatomical" else 4

    # 8. Modificador de subdivisión para acabado cinematográfico
    mod_sub = human_mesh.modifiers.new("Subsurf", "SUBSURF")
    mod_sub.levels = 1
    mod_sub.render_levels = 2

    # 9. Calibración exacta de altura (1.800m) y apoyo en suelo (Z=0.000)
    bpy.context.view_layer.update()
    bbox = [mathutils.Vector(corner) for corner in human_mesh.bound_box]
    min_z = min(b.z for b in bbox)
    max_z = max(b.z for b in bbox)
    cur_h = max_z - min_z

    if cur_h > 0:
        scale_factor = metrics["total_height"] / cur_h
        human_mesh.scale = (scale_factor, scale_factor, scale_factor)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bbox_new = [mathutils.Vector(corner) for corner in human_mesh.bound_box]
    min_z_new = min(b.z for b in bbox_new)
    human_mesh.location.z = -min_z_new
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    if mat:
        human_mesh.data.materials.clear()
        human_mesh.data.materials.append(mat)
    for p in human_mesh.data.polygons:
        p.use_smooth = True

    print(f"[✓] Malla humana ({mode}) generada: {len(human_mesh.data.vertices)} vértices, {len(human_mesh.data.polygons)} polígonos.")
    return human_mesh
