"""
scripts/robotics_anatomy/head_neck.py
Bloqueo anatómico geométrico de cabeza, rostro, mandíbula, cuello y trapecio (1.80m).
"""

import math
from .primitives import make_box, make_cylinder, make_sphere, make_wedge

def build_head_and_neck(col, mat, metrics):
    H_TOP = metrics["head_top"]       # 1.800
    H_CTR = metrics["head_center"]    # 1.710
    N_CTR = metrics["neck_center"]    # 1.585
    N_LEN = metrics["neck_length"]    # 0.080
    N_RAD = metrics["neck_radius"]    # 0.060

    parts = []

    # 1. Bóveda craneal (Neurocráneo ovoide)
    cranium = make_sphere(
        "Anat_Cranium",
        location=(0, 0.010, H_CTR),
        radius=0.092, segments=28, ring_count=20,
        scale=(0.92, 1.08, 1.02),
        col=col, mat=mat
    )
    parts.append(cranium)

    # 2. Cresta occipital posterior
    occiput = make_sphere(
        "Anat_Occiput",
        location=(0, 0.055, H_CTR - 0.025),
        radius=0.065, segments=20, ring_count=14,
        scale=(0.95, 0.85, 0.90),
        col=col, mat=mat
    )
    parts.append(occiput)

    # 3. Frente y arco superciliar (cejas)
    forehead = make_box(
        "Anat_Forehead",
        location=(0, -0.068, H_CTR + 0.030),
        scale=(0.105, 0.038, 0.048),
        rotation=(math.radians(8), 0, 0),
        col=col, mat=mat, bevel=0.008
    )
    parts.append(forehead)

    # 4. Pómulos (arcos cigomáticos)
    for side, sign in [("L", -1), ("R", 1)]:
        cheek = make_box(
            f"Anat_Zygomatic_{side}",
            location=(sign * 0.058, -0.052, H_CTR - 0.015),
            scale=(0.028, 0.048, 0.032),
            rotation=(0, sign * math.radians(-12), math.radians(6)),
            col=col, mat=mat, bevel=0.005
        )
        parts.append(cheek)

    # 5. Pirámide nasal
    nose = make_wedge(
        "Anat_Nose",
        location=(0, -0.092, H_CTR - 0.008),
        scale=(0.026, 0.032, 0.045),
        rotation=(math.radians(180), 0, 0),
        col=col, mat=mat, bevel=0.004
    )
    parts.append(nose)

    # 6. Maxilar y labio superior
    maxilla = make_box(
        "Anat_Maxilla",
        location=(0, -0.065, H_CTR - 0.045),
        scale=(0.072, 0.040, 0.028),
        col=col, mat=mat, bevel=0.006
    )
    parts.append(maxilla)

    # 7. Mandíbula anatómica con ramas goniacas y mentón
    # Ramas mandibulares laterales
    for side, sign in [("L", -1), ("R", 1)]:
        jaw_ramus = make_box(
            f"Anat_JawRamus_{side}",
            location=(sign * 0.052, -0.015, H_CTR - 0.055),
            scale=(0.024, 0.058, 0.052),
            rotation=(math.radians(-15), sign * math.radians(8), 0),
            col=col, mat=mat, bevel=0.006
        )
        parts.append(jaw_ramus)

    # Mentón (protuberancia mentoniana)
    chin = make_box(
        "Anat_Chin",
        location=(0, -0.065, H_CTR - 0.078),
        scale=(0.058, 0.048, 0.034),
        rotation=(math.radians(10), 0, 0),
        col=col, mat=mat, bevel=0.008
    )
    parts.append(chin)

    # 8. Orejas (pabellón auricular elíptico)
    for side, sign in [("L", -1), ("R", 1)]:
        ear = make_cylinder(
            f"Anat_Ear_{side}",
            location=(sign * 0.088, 0.012, H_CTR - 0.005),
            radius=0.020, depth=0.012, vertices=16,
            rotation=(0, math.radians(90), sign * math.radians(10)),
            scale=(1.4, 0.9, 1.0),
            col=col, mat=mat
        )
        parts.append(ear)

    # 9. Cuello central y columna cervical
    neck_core = make_cylinder(
        "Anat_NeckCore",
        location=(0, 0.005, N_CTR),
        radius=N_RAD * 0.88, depth=N_LEN, vertices=20,
        rotation=(math.radians(4), 0, 0),
        col=col, mat=mat
    )
    parts.append(neck_core)

    # Nuez de Adán (cartílago tiroides)
    thyroid = make_wedge(
        "Anat_ThyroidCartilage",
        location=(0, -0.056, N_CTR + 0.012),
        scale=(0.025, 0.022, 0.030),
        rotation=(math.radians(90), 0, 0),
        col=col, mat=mat, bevel=0.004
    )
    parts.append(thyroid)

    # Bandas musculares del esternocleidomastoideo (ECM)
    for side, sign in [("L", -1), ("R", 1)]:
        ecm = make_cylinder(
            f"Anat_ECM_{side}",
            location=(sign * 0.040, -0.018, N_CTR),
            radius=0.016, depth=N_LEN * 1.15, vertices=14,
            rotation=(math.radians(14), sign * math.radians(24), 0),
            scale=(0.9, 1.3, 1.0),
            col=col, mat=mat
        )
        parts.append(ecm)

    # Alas del músculo trapecio (cuello hacia hombros)
    for side, sign in [("L", -1), ("R", 1)]:
        trap = make_box(
            f"Anat_Trapezius_{side}",
            location=(sign * 0.105, 0.025, N_CTR - 0.020),
            scale=(0.095, 0.075, 0.065),
            rotation=(math.radians(6), sign * math.radians(-28), sign * math.radians(12)),
            col=col, mat=mat, bevel=0.012
        )
        parts.append(trap)

    return parts
