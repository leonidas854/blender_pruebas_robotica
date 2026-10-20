"""
scripts/human_modeling/skeleton_core.py
Generador de la estructura anatómica continua en Pose A (1.80m) mediante Skin modifier.
Garantiza un volumen poligonal unificado sin huecos ni partes desconectadas.
"""

import bpy
import math

def create_continuous_apose_core(col, mat, metrics):
    t = metrics["torso"]
    a = metrics["arms"]
    l = metrics["legs"]
    h = metrics["head"]

    # Ángulo Pose A: ~42 grados hacia afuera y abajo
    ang_rad = math.radians(a["apose_angle_deg"])
    sin_a = math.sin(ang_rad)
    cos_a = math.cos(ang_rad)

    # Coordenadas de articulaciones de brazos en Pose A
    x_sh = a["shoulder_x"]      # 0.2215
    z_sh = t["shoulder_z"]      # 1.505
    l_ua = a["upper_arm_len"]   # 0.298
    l_fa = a["forearm_len"]     # 0.299
    l_hd = a["hand_len"]        # 0.115

    x_elb = x_sh + l_ua * sin_a
    z_elb = z_sh - l_ua * cos_a

    x_wri = x_elb + l_fa * sin_a
    z_wri = z_elb - l_fa * cos_a

    x_hnd = x_wri + l_hd * sin_a
    z_hnd = z_wri - l_hd * cos_a

    # Coordenadas de articulaciones de piernas
    x_hip = l["hip_x"]          # 0.108
    z_hip = l["hip_z"]          # 0.880
    z_kne = l["knee_z"]         # 0.490
    z_ank = l["ankle_z"]        # 0.080

    mesh = bpy.data.meshes.new("Human_Core_Skeleton_Mesh")
    obj = bpy.data.objects.new("Human_Core_Skeleton", mesh)
    col.objects.link(obj)

    verts = [
        # Columna y Cabeza (0 a 6)
        (0, 0, t["pelvis_z"]),                  # 0: Pelvis
        (0, 0.012, (t["pelvis_z"]+t["waist_z"])/2), # 1: Lumbar bajo
        (0, 0.015, t["waist_z"]),               # 2: Cintura
        (0, 0.010, t["chest_z"]),               # 3: Tórax / Pecho
        (0, 0.005, h["neck_base_z"]),           # 4: Base del cuello
        (0, 0.000, h["neck_top_z"]),            # 5: Cuello superior
        (0, 0.010, h["center_z"]),              # 6: Centro del cráneo
        (0, 0.000, h["top_z"]),                 # 7: Corona de la cabeza
        # Clavícula y Brazo Derecho (8 a 12)
        (x_sh * 0.5, -0.015, z_sh - 0.01),      # 8: Clavícula Der
        (x_sh, 0, z_sh),                        # 9: Hombro Der
        (x_elb, 0, z_elb),                      # 10: Codo Der
        (x_wri, 0, z_wri),                      # 11: Muñeca Der
        (x_hnd, 0, z_hnd),                      # 12: Mano Der
        # Clavícula y Brazo Izquierdo (13 a 17)
        (-x_sh * 0.5, -0.015, z_sh - 0.01),     # 13: Clavícula Izq
        (-x_sh, 0, z_sh),                       # 14: Hombro Izq
        (-x_elb, 0, z_elb),                     # 15: Codo Izq
        (-x_wri, 0, z_wri),                     # 16: Muñeca Izq
        (-x_hnd, 0, z_hnd),                     # 17: Mano Izq
        # Pierna Derecha (18 a 22)
        (x_hip, 0, z_hip),                      # 18: Cadera Der
        (x_hip, -0.010, z_kne),                 # 19: Rodilla Der
        (x_hip, 0, z_ank),                      # 20: Tobillo Der
        (x_hip, 0.045, z_ank * 0.45),           # 21: Talón Der
        (x_hip, -0.115, z_ank * 0.25),          # 22: Punta del pie Der
        # Pierna Izquierda (23 a 27)
        (-x_hip, 0, z_hip),                     # 23: Cadera Izq
        (-x_hip, -0.010, z_kne),                # 24: Rodilla Izq
        (-x_hip, 0, z_ank),                     # 25: Tobillo Izq
        (-x_hip, 0.045, z_ank * 0.45),          # 26: Talón Izq
        (-x_hip, -0.115, z_ank * 0.25),         # 27: Punta del pie Izq
    ]

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), # Columna
        (4, 8), (8, 9), (9, 10), (10, 11), (11, 12),             # Brazo Der
        (4, 13), (13, 14), (14, 15), (15, 16), (16, 17),         # Brazo Izq
        (0, 18), (18, 19), (19, 20), (20, 21), (20, 22),         # Pierna Der
        (0, 23), (23, 24), (24, 25), (25, 26), (25, 27),         # Pierna Izq
    ]

    mesh.from_pydata(verts, edges, [])
    mesh.update()

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    mod_skin = obj.modifiers.new("Skin", "SKIN")

    # Radios anatómicos por vértice (X: ancho, Y: profundidad)
    radii = {
        0: (t["pelvis_width"] * 0.46, t["pelvis_depth"] * 0.45),
        1: (t["waist_width"] * 0.48, t["waist_depth"] * 0.46),
        2: (t["waist_width"] * 0.46, t["waist_depth"] * 0.44),
        3: (t["chest_width"] * 0.44, t["chest_depth"] * 0.42),
        4: (h["neck_radius"] * 1.05, h["neck_radius"] * 1.05),
        5: (h["neck_radius"] * 0.95, h["neck_radius"] * 0.95),
        6: (h["width"] * 0.50, h["depth"] * 0.50),
        7: (0.040, 0.050),
        # Brazo Der
        8: (0.045, 0.040), 9: (0.058, 0.056), 10: (a["forearm_radius"] * 1.05, a["forearm_radius"] * 1.05),
        11: (a["wrist_radius"], a["wrist_radius"] * 0.9), 12: (0.035, 0.022),
        # Brazo Izq
        13: (0.045, 0.040), 14: (0.058, 0.056), 15: (a["forearm_radius"] * 1.05, a["forearm_radius"] * 1.05),
        16: (a["wrist_radius"], a["wrist_radius"] * 0.9), 17: (0.035, 0.022),
        # Pierna Der
        18: (l["thigh_radius"] * 1.02, l["thigh_radius"] * 1.02),
        19: (l["knee_radius"], l["knee_radius"]),
        20: (l["ankle_radius"], l["ankle_radius"]),
        21: (0.042, 0.045), 22: (l["foot_width"] * 0.46, 0.028),
        # Pierna Izq
        23: (l["thigh_radius"] * 1.02, l["thigh_radius"] * 1.02),
        24: (l["knee_radius"], l["knee_radius"]),
        25: (l["ankle_radius"], l["ankle_radius"]),
        26: (0.042, 0.045), 27: (l["foot_width"] * 0.46, 0.028),
    }

    skin_data = mesh.skin_vertices[0].data
    for idx, (rx, ry) in radii.items():
        if idx < len(skin_data):
            skin_data[idx].radius = (rx, ry)

    bpy.ops.object.modifier_apply(modifier="Skin")

    if mat:
        obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = True

    return obj
