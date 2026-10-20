"""
scripts/robotics_anatomy/torso.py
Bloqueo anatómico geométrico de tórax, clavículas, esternón, pectorales,
dorsales, serratos, recto abdominal (6-pack) y oblicuos (1.80m).
"""

import math
from .primitives import make_box, make_cylinder, make_sphere, make_wedge

def build_torso(col, mat, metrics):
    CH_CTR = metrics["chest_center"]   # 1.370
    CH_W   = metrics["chest_width"]    # 0.390
    CH_D   = metrics["chest_depth"]    # 0.250
    CH_H   = metrics["chest_height"]   # 0.220
    W_CTR  = metrics["waist_center"]   # 1.160
    W_W    = metrics["waist_width"]    # 0.250
    W_D    = metrics["waist_depth"]    # 0.190
    W_H    = metrics["waist_height"]   # 0.180

    parts = []

    # 1. Caja torácica central (ovoide/barril torácico)
    ribcage = make_sphere(
        "Anat_Ribcage",
        location=(0, -0.015, CH_CTR),
        radius=0.175, segments=28, ring_count=20,
        scale=(CH_W / 0.35, CH_D / 0.35, CH_H / 0.35),
        col=col, mat=mat
    )
    parts.append(ribcage)

    # 2. Clavículas (barras claviculares con suave curva en S)
    for side, sign in [("L", -1), ("R", 1)]:
        clavicle = make_box(
            f"Anat_Clavicle_{side}",
            location=(sign * (CH_W * 0.28), -CH_D * 0.44, CH_CTR + CH_H * 0.54),
            scale=(CH_W * 0.46, 0.024, 0.020),
            rotation=(math.radians(-6), sign * math.radians(-10), sign * math.radians(4)),
            col=col, mat=mat, bevel=0.005
        )
        parts.append(clavicle)

    # 3. Esternón (Manubrio, Cuerpo y Apéndice xifoides)
    sternum = make_box(
        "Anat_Sternum",
        location=(0, -CH_D * 0.46, CH_CTR + 0.015),
        scale=(0.046, 0.022, CH_H * 0.85),
        col=col, mat=mat, bevel=0.006
    )
    parts.append(sternum)

    # 4. Músculos Pectorales Mayores (Pecs anatómicos divididos)
    for side, sign in [("L", -1), ("R", 1)]:
        # Pectoral superior (porción clavicular)
        pec_sup = make_box(
            f"Anat_PectoralSup_{side}",
            location=(sign * (CH_W * 0.24), -CH_D * 0.47, CH_CTR + 0.065),
            scale=(CH_W * 0.38, 0.034, 0.075),
            rotation=(math.radians(-6), sign * math.radians(-8), sign * math.radians(5)),
            col=col, mat=mat, bevel=0.010
        )
        parts.append(pec_sup)

        # Pectoral medio/inferior (porción esternocostal)
        pec_inf = make_box(
            f"Anat_PectoralInf_{side}",
            location=(sign * (CH_W * 0.23), -CH_D * 0.48, CH_CTR - 0.010),
            scale=(CH_W * 0.40, 0.038, 0.095),
            rotation=(math.radians(-4), sign * math.radians(-5), sign * math.radians(-3)),
            col=col, mat=mat, bevel=0.012
        )
        parts.append(pec_inf)

    # 5. Músculos Dorsales Anchos (Latissimus dorsi - Alas V-taper)
    for side, sign in [("L", -1), ("R", 1)]:
        lat = make_box(
            f"Anat_LatissimusDorsi_{side}",
            location=(sign * (CH_W * 0.44), 0.035, CH_CTR - 0.025),
            scale=(0.062, CH_D * 0.72, CH_H * 1.05),
            rotation=(math.radians(8), sign * math.radians(-16), sign * math.radians(10)),
            col=col, mat=mat, bevel=0.015
        )
        parts.append(lat)

    # 6. Serrato Anterior (dientes musculares costales)
    for side, sign in [("L", -1), ("R", 1)]:
        for s_idx, s_z in enumerate([-0.045, -0.010, 0.025]):
            serratus = make_box(
                f"Anat_Serratus_{side}_{s_idx}",
                location=(sign * (CH_W * 0.41), -CH_D * 0.15, CH_CTR + s_z),
                scale=(0.026, 0.070, 0.022),
                rotation=(math.radians(-8), sign * math.radians(-14), sign * math.radians(6)),
                col=col, mat=mat, bevel=0.005
            )
            parts.append(serratus)

    # 7. Recto Abdominal (Tabletas 6-pack anatómicas contorneadas)
    abs_segments = [
        ("Upper", W_CTR + 0.065, 0.088, 0.044),
        ("Mid",   W_CTR + 0.010, 0.082, 0.042),
        ("Lower", W_CTR - 0.048, 0.076, 0.045),
    ]
    for seg_name, seg_z, seg_w, seg_h in abs_segments:
        for side, sign in [("L", -1), ("R", 1)]:
            ab_pad = make_box(
                f"Anat_AbPad_{seg_name}_{side}",
                location=(sign * (seg_w * 0.52), -W_D * 0.46, seg_z),
                scale=(seg_w * 0.44, 0.028, seg_h * 0.88),
                rotation=(math.radians(2), sign * math.radians(-3), 0),
                col=col, mat=mat, bevel=0.008
            )
            parts.append(ab_pad)

    # Ombligo (depresión umbilical)
    navel = make_sphere(
        "Anat_Navel",
        location=(0, -W_D * 0.47, W_CTR - 0.025),
        radius=0.009, segments=12, ring_count=8,
        col=col, mat=mat
    )
    parts.append(navel)

    # 8. Oblicuos Externos (Flancos laterales sobre la cresta ilíaca)
    for side, sign in [("L", -1), ("R", 1)]:
        oblique = make_box(
            f"Anat_ExternalOblique_{side}",
            location=(sign * (W_W * 0.52), -0.015, W_CTR - 0.010),
            scale=(0.045, W_D * 0.75, W_H * 0.90),
            rotation=(math.radians(5), sign * math.radians(-12), sign * math.radians(8)),
            col=col, mat=mat, bevel=0.012
        )
        parts.append(oblique)

    # 9. Columna Lumbar y Erectores Espinales posteriores
    for l_idx, l_z in enumerate([-0.05, 0.0, 0.05]):
        for side, sign in [("L", -1), ("R", 1)]:
            erector = make_cylinder(
                f"Anat_ErectorSpinae_{side}_{l_idx}",
                location=(sign * 0.038, W_D * 0.42, W_CTR + l_z),
                radius=0.022, depth=0.055, vertices=16,
                rotation=(0, 0, 0),
                scale=(1.2, 0.8, 1.0),
                col=col, mat=mat
            )
            parts.append(erector)

    return parts
