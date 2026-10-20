"""
scripts/human_modeling/face_head.py
Modelado de cabeza, cuello y facciones faciales masculinas de Leonidas (1.80m).
"""

import bpy
import os
import math

def create_male_head_and_face(col, mat, metrics, base_dir=None):
    h = metrics["head"]
    h_top = h["top_z"]       # 1.800
    h_ctr = h["center_z"]    # 1.710
    n_top = h["neck_top_z"]  # 1.625
    n_bas = h["neck_base_z"] # 1.520
    n_rad = h["neck_radius"] # 0.062

    parts = []

    def _part(name, mtype, loc, scale=(1,1,1), rot=(0,0,0), radius=0.05, depth=0.1):
        if mtype == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=24, ring_count=18, location=loc, rotation=rot)
        elif mtype == "cube":
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
        elif mtype == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=20, location=loc, rotation=rot)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = scale
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        col.objects.link(obj)
        if mat:
            obj.data.materials.append(mat)
        for p in obj.data.polygons:
            p.use_smooth = True
        return obj

    # 1. Bóveda craneal masculina
    cranium = _part("Head_Cranium", "sphere", (0, 0.010, h_ctr), scale=(0.94, 1.08, 1.02), radius=0.094)
    parts.append(cranium)

    # 2. Frente y reborde supraciliar masculino (cejas marcadas)
    forehead = _part("Head_Forehead", "cube", (0, -0.072, h_ctr + 0.028), scale=(0.108, 0.038, 0.052), rot=(math.radians(8), 0, 0))
    parts.append(forehead)

    # 3. Pómulos (arcos cigomáticos)
    for side, sign in [("L", -1), ("R", 1)]:
        cheek = _part(f"Head_Zygomatic_{side}", "cube", (sign * 0.060, -0.055, h_ctr - 0.015),
                      scale=(0.028, 0.048, 0.035), rot=(0, sign * math.radians(-12), math.radians(6)))
        parts.append(cheek)

    # 4. Nariz masculina (puente y punta recta)
    nose = _part("Head_Nose", "cube", (0, -0.092, h_ctr - 0.005), scale=(0.026, 0.034, 0.048), rot=(math.radians(-12), 0, 0))
    parts.append(nose)

    # 5. Mandíbula y mentón masculino angular (facciones de Leonidas)
    for side, sign in [("L", -1), ("R", 1)]:
        jaw = _part(f"Head_Jaw_{side}", "cube", (sign * 0.056, -0.018, h_ctr - 0.055),
                    scale=(0.026, 0.060, 0.052), rot=(math.radians(-14), sign * math.radians(8), 0))
        parts.append(jaw)

    chin = _part("Head_Chin", "cube", (0, -0.068, h_ctr - 0.076), scale=(0.062, 0.048, 0.036), rot=(math.radians(10), 0, 0))
    parts.append(chin)

    # 6. Orejas anatómicas
    for side, sign in [("L", -1), ("R", 1)]:
        ear = _part(f"Head_Ear_{side}", "cylinder", (sign * 0.088, 0.012, h_ctr - 0.005),
                    radius=0.022, depth=0.012, rot=(0, math.radians(90), sign * math.radians(10)),
                    scale=(1.4, 0.9, 1.0))
        parts.append(ear)

    # 7. Cuello masculino, nuez de Adán y esternocleidomastoideo
    n_mid_z = (n_top + n_bas) / 2.0
    neck = _part("Neck_Column", "cylinder", (0, 0.005, n_mid_z), radius=n_rad * 0.90, depth=(n_top - n_bas) * 1.15,
                 rot=(math.radians(4), 0, 0))
    parts.append(neck)

    thyroid = _part("Neck_AdamApple", "cube", (0, -0.060, n_mid_z + 0.015), scale=(0.024, 0.020, 0.028),
                    rot=(math.radians(45), 0, 0))
    parts.append(thyroid)

    for side, sign in [("L", -1), ("R", 1)]:
        ecm = _part(f"Neck_ECM_{side}", "cylinder", (sign * 0.042, -0.018, n_mid_z),
                    radius=0.018, depth=(n_top - n_bas) * 1.20,
                    rot=(math.radians(14), sign * math.radians(24), 0), scale=(0.9, 1.3, 1.0))
        parts.append(ecm)

        trap = _part(f"Neck_Trapezius_{side}", "cube", (sign * 0.110, 0.028, n_bas + 0.010),
                     scale=(0.098, 0.080, 0.070),
                     rot=(math.radians(6), sign * math.radians(-28), sign * math.radians(12)))
        parts.append(trap)

    # 8. Malla facial real importada de face_mesh.obj si está disponible
    if base_dir:
        face_obj_path = os.path.join(base_dir, "character_data", "meshes", "face_mesh.obj")
        if not os.path.exists(face_obj_path):
            face_obj_path = os.path.join(base_dir, "character_data", "face_mesh.obj")
        if os.path.exists(face_obj_path):
            try:
                bpy.ops.wm.obj_import(filepath=face_obj_path)
                f_mesh = bpy.context.selected_objects[0]
                f_mesh.name = "Head_Leonidas_FacePlate"
                f_mesh.scale = (0.95, 0.95, 0.95)
                f_mesh.location = (0.0, -0.058, h_ctr - 0.010)
                for c in list(f_mesh.users_collection):
                    c.objects.unlink(f_mesh)
                col.objects.link(f_mesh)
                if mat:
                    f_mesh.data.materials.append(mat)
                for p in f_mesh.data.polygons:
                    p.use_smooth = True
                parts.append(f_mesh)
            except Exception as e:
                print(f"[*] Aviso al importar face_mesh.obj: {e}")

    return parts
