"""
scripts/human_modeling/hands_feet.py
Modelado anatómico de manos con 5 dedos en Pose A y pies con arco plantar y 5 dedos (1.80m).
"""

import bpy
import math

def create_detailed_hands_and_feet(col, mat, metrics):
    a = metrics["arms"]
    l = metrics["legs"]

    ang_rad = math.radians(a["apose_angle_deg"])
    sin_a = math.sin(ang_rad)
    cos_a = math.cos(ang_rad)

    x_sh = a["shoulder_x"]
    z_sh = metrics["torso"]["shoulder_z"]
    l_ua = a["upper_arm_len"]
    l_fa = a["forearm_len"]

    # Posición de la muñeca en Pose A
    x_wri = x_sh + (l_ua + l_fa) * sin_a
    z_wri = z_sh - (l_ua + l_fa) * cos_a

    parts = []

    def _obj(name, mtype, loc, scale=(1,1,1), rot=(0,0,0), radius=0.01, depth=0.05):
        if mtype == "cube":
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
        elif mtype == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=16, ring_count=12, location=loc, rotation=rot)
        elif mtype == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=14, location=loc, rotation=rot)
        o = bpy.context.active_object
        o.name = name
        o.scale = scale
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)
        if mat:
            o.data.materials.append(mat)
        for p in o.data.polygons:
            p.use_smooth = True
        return o

    # ── 1. MANOS Y 5 DEDOS EN POSE A ──────────────────────────────────────────
    palm_len = 0.065
    palm_dist = palm_len * 0.5

    for side, sign in [("L", -1), ("R", 1)]:
        palm_x = sign * (x_wri + palm_dist * sin_a)
        palm_z = z_wri - palm_dist * cos_a
        rot_arm = (0, sign * ang_rad, 0)

        # Palma de la mano
        palm = _obj(f"Hand_Palm_{side}", "cube", (palm_x, 0, palm_z),
                    scale=(0.026, 0.074, palm_len), rot=rot_arm)
        parts.append(palm)

        # Eminencia tenar (base carnosa del pulgar)
        thenar = _obj(f"Hand_Thenar_{side}", "sphere",
                      (palm_x - sign * 0.010, -0.022, palm_z + 0.010),
                      radius=0.016, scale=(1.0, 1.25, 0.9))
        parts.append(thenar)

        # Pulgar (en ángulo hacia adelante y medial)
        thumb = _obj(f"Hand_Thumb_{side}", "cylinder",
                     (palm_x - sign * 0.016, -0.034, palm_z - 0.010),
                     radius=0.009, depth=0.045, rot=(math.radians(35), sign * (ang_rad - math.radians(20)), 0))
        parts.append(thumb)

        # Dedos 2 a 5 (Índice, Medio, Anular, Meñique)
        fingers = [
            ("Index",  -0.022, 0.054),
            ("Middle", -0.007, 0.062),
            ("Ring",    0.008, 0.056),
            ("Pinky",   0.022, 0.046),
        ]
        for f_name, f_y, f_len in fingers:
            f_dist = palm_len + f_len * 0.45
            f_x = sign * (x_wri + f_dist * sin_a)
            f_z = z_wri - f_dist * cos_a
            finger = _obj(f"Hand_Finger_{f_name}_{side}", "cylinder",
                          (f_x, f_y, f_z), radius=0.0075, depth=f_len, rot=rot_arm)
            parts.append(finger)

    # ── 2. PIES ANATÓMICOS CON ARCO Y 5 DEDOS ─────────────────────────────────
    x_hip = l["hip_x"]
    z_ank = l["ankle_z"]

    for side, sign in [("L", -1), ("R", 1)]:
        # Maléolos de tobillo (medial más alto que lateral)
        mal_med = _obj(f"Foot_MalleolusMedial_{side}", "sphere",
                       (sign * (x_hip - 0.034), 0, z_ank + 0.014), radius=0.018)
        parts.append(mal_med)
        mal_lat = _obj(f"Foot_MalleolusLateral_{side}", "sphere",
                       (sign * (x_hip + 0.034), 0, z_ank - 0.004), radius=0.018)
        parts.append(mal_lat)

        # Talón / Calcáneo
        heel = _obj(f"Foot_Heel_{side}", "sphere",
                    (sign * x_hip, 0.045, z_ank * 0.45), radius=0.032, scale=(0.95, 1.25, 0.85))
        parts.append(heel)

        # Empeine y arco longitudinal
        instep = _obj(f"Foot_Instep_{side}", "cube",
                      (sign * x_hip, -0.048, z_ank * 0.45),
                      scale=(0.082, 0.125, z_ank * 0.70), rot=(math.radians(10), 0, 0))
        parts.append(instep)

        # Almohadilla plantar metatarsiana
        ball = _obj(f"Foot_Ball_{side}", "cube",
                    (sign * x_hip, -0.115, z_ank * 0.30),
                    scale=(0.086, 0.045, z_ank * 0.45))
        parts.append(ball)

        # 5 Dedos del pie
        toes = [
            ("BigToe", sign * -0.024, -0.155, 0.013, 0.036),
            ("Toe2",   sign * -0.008, -0.152, 0.010, 0.032),
            ("Toe3",   sign *  0.006, -0.148, 0.009, 0.028),
            ("Toe4",   sign *  0.018, -0.142, 0.0085, 0.025),
            ("Toe5",   sign *  0.028, -0.134, 0.008, 0.022),
        ]
        for t_name, t_x, t_y, t_rad, t_len in toes:
            toe = _obj(f"Foot_{t_name}_{side}", "cylinder",
                       (sign * x_hip + t_x, t_y, z_ank * 0.22),
                       radius=t_rad, depth=t_len, rot=(math.radians(90), 0, 0))
            parts.append(toe)

    return parts
