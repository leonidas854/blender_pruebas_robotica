"""
scripts/robotics_anatomy/pelvis.py
Bloqueo anatómico geométrico de pelvis, cresta ilíaca, sacro y glúteos (1.80m).
"""

import math
from .primitives import make_box, make_cylinder, make_sphere, make_wedge

def build_pelvis(col, mat, metrics):
    P_CTR  = metrics["pelvis_center"]   # 0.950
    P_W    = metrics["pelvis_width"]    # 0.270
    P_D    = metrics["pelvis_depth"]    # 0.200
    P_H    = metrics["pelvis_height"]   # 0.180
    HIP_Z  = metrics["hip_joint_z"]     # 0.880
    HIP_X  = metrics["hip_x"]           # 0.110

    parts = []

    # 1. Cuerpo pélvico central (bloque cónico invertido)
    pelvic_core = make_box(
        "Anat_PelvicCore",
        location=(0, 0, P_CTR),
        scale=(P_W * 0.92, P_D * 0.88, P_H * 0.85),
        col=col, mat=mat, bevel=0.018
    )
    parts.append(pelvic_core)

    # 2. Crestas Ilíacas (reborde superior curvado de los huesos ilíacos)
    for side, sign in [("L", -1), ("R", 1)]:
        crest = make_box(
            f"Anat_IliacCrest_{side}",
            location=(sign * (P_W * 0.48), -0.010, P_CTR + 0.055),
            scale=(0.040, P_D * 0.82, 0.035),
            rotation=(math.radians(4), sign * math.radians(-16), sign * math.radians(10)),
            col=col, mat=mat, bevel=0.010
        )
        parts.append(crest)

        # Espina Ilíaca Anteroposterior (ASIS - punto óseo frontal visible)
        asis = make_sphere(
            f"Anat_ASIS_{side}",
            location=(sign * (P_W * 0.38), -P_D * 0.44, P_CTR + 0.035),
            radius=0.018, segments=14, ring_count=10,
            scale=(1.0, 1.2, 0.9),
            col=col, mat=mat
        )
        parts.append(asis)

    # 3. Sacro posterior (cuña ósea triangular)
    sacrum = make_wedge(
        "Anat_Sacrum",
        location=(0, P_D * 0.42, P_CTR + 0.025),
        scale=(0.082, 0.038, 0.095),
        rotation=(math.radians(180), 0, 0),
        col=col, mat=mat, bevel=0.008
    )
    parts.append(sacrum)

    # 4. Músculos Glúteos (Gluteus Maximus y Medius anatómicos)
    for side, sign in [("L", -1), ("R", 1)]:
        # Glúteo medio (lateral superior)
        glut_med = make_sphere(
            f"Anat_GluteusMedius_{side}",
            location=(sign * (P_W * 0.44), P_D * 0.22, P_CTR + 0.010),
            radius=0.055, segments=18, ring_count=12,
            scale=(0.95, 1.15, 0.90),
            col=col, mat=mat
        )
        parts.append(glut_med)

        # Glúteo mayor (volumen principal de las nalgas)
        glut_max = make_sphere(
            f"Anat_GluteusMaximus_{side}",
            location=(sign * (P_W * 0.28), P_D * 0.42, P_CTR - 0.045),
            radius=0.078, segments=22, ring_count=16,
            scale=(1.05, 1.20, 1.00),
            rotation=(math.radians(-12), sign * math.radians(10), sign * math.radians(-5)),
            col=col, mat=mat
        )
        parts.append(glut_max)

    # 5. Región Púbica y arco inguinal frontal
    pubis = make_box(
        "Anat_Pubis",
        location=(0, -P_D * 0.44, P_CTR - 0.055),
        scale=(0.088, 0.035, 0.065),
        rotation=(math.radians(12), 0, 0),
        col=col, mat=mat, bevel=0.010
    )
    parts.append(pubis)

    # 6. Acetábulos / Cavidades articulares coxofemorales (cabezas de fémur)
    for side, sign in [("L", -1), ("R", 1)]:
        acetabulum = make_sphere(
            f"Anat_HipJoint_{side}",
            location=(sign * HIP_X, 0, HIP_Z),
            radius=0.068, segments=18, ring_count=12,
            col=col, mat=mat
        )
        parts.append(acetabulum)

    return parts
