"""
scripts/human_modeling/musculature.py
Volúmenes musculares masculinos anatómicos para el molde humano de Leonidas (1.80m).
Diseñado para coincidir con la figura de referencia muscular (pectorales, 6-pack, deltoides, cuádriceps, gemelos).
"""

import bpy
import math

def _make_part(name, mesh_type, location, scale=(1,1,1), rotation=(0,0,0), radius=0.05, depth=0.1, col=None, mat=None):
    if mesh_type == "cube":
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    elif mesh_type == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=22, ring_count=16, location=location, rotation=rotation)
    elif mesh_type == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=20, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if col:
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        col.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj

def create_male_musculature(col, mat, metrics):
    t = metrics["torso"]
    a = metrics["arms"]
    l = metrics["legs"]

    parts = []

    # ── 1. PECTORALES MASCULINOS ATLETICOS ───────────────────────────────────
    ch_w = t["chest_width"]    # 0.390
    ch_d = t["chest_depth"]    # 0.250
    ch_z = t["chest_z"]        # 1.370

    for side, sign in [("L", -1), ("R", 1)]:
        # Pectoral principal masculino (placa muscular biselada y contorneada)
        pec = _make_part(
            f"Musc_Pectoral_{side}", "cube",
            location=(sign * (ch_w * 0.24), -ch_d * 0.44, ch_z + 0.015),
            scale=(ch_w * 0.42, 0.055, 0.145),
            rotation=(math.radians(-6), sign * math.radians(-7), sign * math.radians(4)),
            col=col, mat=mat
        )
        parts.append(pec)

        # Clavícula superior
        clav = _make_part(
            f"Musc_Clavicle_{side}", "cube",
            location=(sign * (ch_w * 0.26), -ch_d * 0.40, ch_z + 0.115),
            scale=(ch_w * 0.44, 0.030, 0.024),
            rotation=(math.radians(-4), sign * math.radians(-10), sign * math.radians(5)),
            col=col, mat=mat
        )
        parts.append(clav)

    # ── 2. DORSALES ANCHOS (V-TAPER) Y SERRATOS ──────────────────────────────
    for side, sign in [("L", -1), ("R", 1)]:
        lat = _make_part(
            f"Musc_Latissimus_{side}", "cube",
            location=(sign * (ch_w * 0.44), 0.020, ch_z - 0.040),
            scale=(0.065, ch_d * 0.75, 0.240),
            rotation=(math.radians(8), sign * math.radians(-15), sign * math.radians(10)),
            col=col, mat=mat
        )
        parts.append(lat)

        for s_idx, s_z in enumerate([-0.05, -0.015, 0.020]):
            ser = _make_part(
                f"Musc_Serratus_{side}_{s_idx}", "cube",
                location=(sign * (ch_w * 0.40), -ch_d * 0.18, ch_z + s_z),
                scale=(0.028, 0.075, 0.024),
                rotation=(math.radians(-8), sign * math.radians(-12), sign * math.radians(6)),
                col=col, mat=mat
            )
            parts.append(ser)

    # ── 3. RECTO ABDOMINAL (6-PACK) Y OBLICUOS EXTERNOS ───────────────────────
    w_w = t["waist_width"]     # 0.245
    w_d = t["waist_depth"]     # 0.180
    w_z = t["waist_z"]         # 1.150

    abs_levels = [
        ("Upper", w_z + 0.070, 0.088, 0.048),
        ("Mid",   w_z + 0.015, 0.082, 0.046),
        ("Lower", w_z - 0.045, 0.076, 0.050),
    ]
    for name, sz, sw, sh in abs_levels:
        for side, sign in [("L", -1), ("R", 1)]:
            ab_block = _make_part(
                f"Musc_AbPad_{name}_{side}", "cube",
                location=(sign * (sw * 0.52), -w_d * 0.45, sz),
                scale=(sw * 0.44, 0.035, sh * 0.88),
                rotation=(math.radians(2), sign * math.radians(-3), 0),
                col=col, mat=mat
            )
            parts.append(ab_block)

    for side, sign in [("L", -1), ("R", 1)]:
        obl = _make_part(
            f"Musc_Oblique_{side}", "cube",
            location=(sign * (w_w * 0.52), -0.015, w_z - 0.010),
            scale=(0.052, w_d * 0.78, 0.170),
            rotation=(math.radians(5), sign * math.radians(-14), sign * math.radians(8)),
            col=col, mat=mat
        )
        parts.append(obl)

    # ── 4. DELTOIDES Y BRAZOS EN POSE A (42°) ────────────────────────────────
    ang_rad = math.radians(a["apose_angle_deg"])
    sin_a = math.sin(ang_rad)
    cos_a = math.cos(ang_rad)
    x_sh = a["shoulder_x"]
    z_sh = t["shoulder_z"]

    for side, sign in [("L", -1), ("R", 1)]:
        # Deltoides cabeza lateral
        delt = _make_part(
            f"Musc_Deltoid_{side}", "sphere",
            location=(sign * (x_sh + 0.038), 0, z_sh - 0.010),
            radius=0.075,
            scale=(0.95, 1.10, 1.25),
            rotation=(0, sign * math.radians(-15), 0),
            col=col, mat=mat
        )
        parts.append(delt)

        # Bíceps Braquial orientado en el eje del brazo en Pose A
        arm_mid_dist = a["upper_arm_len"] * 0.50
        bicep_x = sign * (x_sh + arm_mid_dist * sin_a)
        bicep_z = z_sh - arm_mid_dist * cos_a
        bicep = _make_part(
            f"Musc_Biceps_{side}", "cylinder",
            location=(bicep_x, -0.024, bicep_z),
            radius=a["bicep_radius"], depth=a["upper_arm_len"] * 0.75,
            rotation=(0, sign * ang_rad, 0),
            scale=(1.10, 0.95, 1.0),
            col=col, mat=mat
        )
        parts.append(bicep)

        # Tríceps posterior
        tricep = _make_part(
            f"Musc_Triceps_{side}", "cylinder",
            location=(bicep_x, 0.026, bicep_z),
            radius=a["bicep_radius"] * 1.05, depth=a["upper_arm_len"] * 0.80,
            rotation=(0, sign * ang_rad, 0),
            scale=(1.15, 0.95, 1.0),
            col=col, mat=mat
        )
        parts.append(tricep)

    # ── 5. PIERNAS: CUÁDRICEPS, RÓTULA Y GEMELOS ──────────────────────────────
    x_hip = l["hip_x"]
    z_hip = l["hip_z"]
    z_kne = l["knee_z"]
    thigh_mid_z = (z_hip + z_kne) / 2.0
    l_thigh = z_hip - z_kne

    for side, sign in [("L", -1), ("R", 1)]:
        # Vasto lateral (curvatura externa del muslo)
        vast_lat = _make_part(
            f"Musc_VastusLateralis_{side}", "cylinder",
            location=(sign * (x_hip + 0.045), -0.010, thigh_mid_z + 0.020),
            radius=0.052, depth=l_thigh * 0.78,
            rotation=(0, sign * math.radians(-5), 0),
            scale=(1.15, 0.90, 1.0),
            col=col, mat=mat
        )
        parts.append(vast_lat)

        # Vasto medial ("teardrop" encima de la rodilla interna)
        vast_med = _make_part(
            f"Musc_VastusMedialis_{side}", "sphere",
            location=(sign * (x_hip - 0.034), -0.042, z_kne + 0.068),
            radius=0.046,
            scale=(1.12, 0.95, 1.35),
            rotation=(math.radians(10), sign * math.radians(14), 0),
            col=col, mat=mat
        )
        parts.append(vast_med)

        # Rótula / Patella
        patella = _make_part(
            f"Musc_Patella_{side}", "cube",
            location=(sign * x_hip, -0.065, z_kne),
            scale=(0.052, 0.028, 0.058),
            rotation=(math.radians(-8), 0, 0),
            col=col, mat=mat
        )
        parts.append(patella)

        # Gemelos / Gastrocnemio: cabeza medial (más baja y carnosa)
        calf_med = _make_part(
            f"Musc_CalfMedial_{side}", "sphere",
            location=(sign * (x_hip - 0.024), 0.044, z_kne - 0.100),
            radius=0.046,
            scale=(0.95, 1.10, 1.65),
            col=col, mat=mat
        )
        parts.append(calf_med)

        # Gemelos / Gastrocnemio: cabeza lateral (más alta)
        calf_lat = _make_part(
            f"Musc_CalfLateral_{side}", "sphere",
            location=(sign * (x_hip + 0.028), 0.042, z_kne - 0.080),
            radius=0.044,
            scale=(0.95, 1.10, 1.55),
            col=col, mat=mat
        )
        parts.append(calf_lat)

    return parts
