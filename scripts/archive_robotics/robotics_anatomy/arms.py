"""
scripts/robotics_anatomy/arms.py
Bloqueo anatómico geométrico de brazos, deltoides (3 cabezas), bíceps, tríceps,
braquiorradial, antebrazo y manos con palma y 5 dedos articulados (1.80m).
"""

import math
from .primitives import make_box, make_cylinder, make_sphere, make_wedge

def build_arms_and_hands(col, mat, metrics):
    SH_Z = metrics["shoulder_height"]  # 1.505
    SH_W = metrics["shoulder_width"]   # 0.443
    ELB_Z= metrics["elbow_z"]          # 1.205
    WRI_Z= metrics["wrist_z"]          # 0.910
    FIN_Z= metrics["fingertip_z"]      # 0.790

    X_SH = SH_W / 2.0  # 0.2215
    L_ARM = SH_Z - ELB_Z   # ~0.300
    L_FORE= ELB_Z - WRI_Z  # ~0.295
    L_HAND= WRI_Z - FIN_Z  # ~0.120

    parts = []

    for side, sign in [("L", -1), ("R", 1)]:
        # ── 1. DELTOIDES ANATÓMICO (3 CABEZAS MUSCULARES) ─────────────────────
        # Cabeza Lateral / Media (hombrera principal)
        delt_lat = make_sphere(
            f"Anat_Deltoid_Lateral_{side}",
            location=(sign * (X_SH + 0.038), 0, SH_Z - 0.010),
            radius=0.072, segments=20, ring_count=14,
            scale=(0.85, 1.05, 1.25),
            rotation=(0, sign * math.radians(-8), 0),
            col=col, mat=mat
        )
        parts.append(delt_lat)

        # Cabeza Anterior (frontal, inserta desde la clavícula)
        delt_ant = make_sphere(
            f"Anat_Deltoid_Anterior_{side}",
            location=(sign * (X_SH + 0.015), -0.052, SH_Z - 0.020),
            radius=0.052, segments=16, ring_count=12,
            scale=(0.95, 0.90, 1.20),
            rotation=(math.radians(15), sign * math.radians(10), 0),
            col=col, mat=mat
        )
        parts.append(delt_ant)

        # Cabeza Posterior (dorsal, inserta desde la escápula)
        delt_post = make_sphere(
            f"Anat_Deltoid_Posterior_{side}",
            location=(sign * (X_SH + 0.015), 0.052, SH_Z - 0.020),
            radius=0.054, segments=16, ring_count=12,
            scale=(0.95, 0.90, 1.20),
            rotation=(math.radians(-15), sign * math.radians(10), 0),
            col=col, mat=mat
        )
        parts.append(delt_post)

        # ── 2. BRAZO SUPERIOR: BÍCEPS Y TRÍCEPS ───────────────────────────────
        arm_mid_z = (SH_Z + ELB_Z) / 2.0

        # Bíceps Braquial (músculo anterior fusiforme)
        biceps = make_cylinder(
            f"Anat_Biceps_{side}",
            location=(sign * X_SH, -0.022, arm_mid_z - 0.010),
            radius=0.046, depth=L_ARM * 0.70, vertices=18,
            scale=(1.10, 0.95, 1.0),
            col=col, mat=mat
        )
        parts.append(biceps)

        # Tríceps Braquial (músculo posterior en herradura con 3 cabezas)
        triceps = make_box(
            f"Anat_Triceps_{side}",
            location=(sign * X_SH, 0.028, arm_mid_z + 0.010),
            scale=(0.078, 0.065, L_ARM * 0.75),
            col=col, mat=mat, bevel=0.015
        )
        parts.append(triceps)

        # Braquial anterior (músculo lateral intermedio)
        brachialis = make_cylinder(
            f"Anat_Brachialis_{side}",
            location=(sign * (X_SH + 0.026), 0.002, ELB_Z + 0.045),
            radius=0.030, depth=0.090, vertices=14,
            col=col, mat=mat
        )
        parts.append(brachialis)

        # ── 3. ARTICULACIÓN DEL CODO ──────────────────────────────────────────
        # Olécranon (punta posterior ósea del codo)
        olecranon = make_box(
            f"Anat_Olecranon_{side}",
            location=(sign * X_SH, 0.048, ELB_Z),
            scale=(0.042, 0.034, 0.042),
            rotation=(math.radians(18), 0, 0),
            col=col, mat=mat, bevel=0.006
        )
        parts.append(olecranon)

        # Epicóndilos del codo
        elbow_joint = make_cylinder(
            f"Anat_ElbowJoint_{side}",
            location=(sign * X_SH, 0, ELB_Z),
            radius=0.046, depth=0.065, vertices=18,
            rotation=(0, math.radians(90), 0),
            col=col, mat=mat
        )
        parts.append(elbow_joint)

        # ── 4. ANTEBRAZO: BRAQUIORRADIAL, FLEXORES Y EXTENSORES ──────────────
        fore_mid_z = (ELB_Z + WRI_Z) / 2.0

        # Músculo Braquiorradial (cresta prominente externa hacia el pulgar)
        brachiorad = make_cylinder(
            f"Anat_Brachioradialis_{side}",
            location=(sign * (X_SH + 0.034), -0.016, ELB_Z - 0.055),
            radius=0.032, depth=0.130, vertices=16,
            rotation=(math.radians(-6), sign * math.radians(-14), 0),
            scale=(1.2, 0.85, 1.0),
            col=col, mat=mat
        )
        parts.append(brachiorad)

        # Grupo Flexor (vientre muscular anterior)
        flexors = make_cylinder(
            f"Anat_FlexorGroup_{side}",
            location=(sign * X_SH, -0.016, fore_mid_z),
            radius=0.038, depth=L_FORE * 0.72, vertices=18,
            scale=(1.05, 0.88, 1.0),
            col=col, mat=mat
        )
        parts.append(flexors)

        # Grupo Extensor (vientre muscular posterior)
        extensors = make_cylinder(
            f"Anat_ExtensorGroup_{side}",
            location=(sign * X_SH, 0.018, fore_mid_z),
            radius=0.036, depth=L_FORE * 0.72, vertices=18,
            scale=(1.05, 0.88, 1.0),
            col=col, mat=mat
        )
        parts.append(extensors)

        # Muñeca y cabeza del cúbito (hueso de muñeca)
        wrist = make_box(
            f"Anat_Wrist_{side}",
            location=(sign * X_SH, 0, WRI_Z),
            scale=(0.048, 0.065, 0.032),
            col=col, mat=mat, bevel=0.006
        )
        parts.append(wrist)

        # ── 5. MANO Y 5 DEDOS ARTICULADOS ────────────────────────────────────
        palm_z = WRI_Z - 0.045

        # Palma (placa metacarpiana)
        palm = make_box(
            f"Anat_Palm_{side}",
            location=(sign * X_SH, 0, palm_z),
            scale=(0.032, 0.076, 0.065),
            col=col, mat=mat, bevel=0.008
        )
        parts.append(palm)

        # Eminencia tenar (cojín carnoso en la base del pulgar)
        thenar = make_sphere(
            f"Anat_Thenar_{side}",
            location=(sign * (X_SH - 0.012), -0.024, palm_z + 0.010),
            radius=0.016, segments=12, ring_count=8,
            scale=(1.0, 1.3, 0.9),
            col=col, mat=mat
        )
        parts.append(thenar)

        # Dedo 1: Pulgar (opuesto y en ángulo hacia el frente)
        thumb = make_cylinder(
            f"Anat_Thumb_{side}",
            location=(sign * (X_SH - 0.018), -0.038, palm_z - 0.015),
            radius=0.009, depth=0.045, vertices=12,
            rotation=(math.radians(35), sign * math.radians(-25), 0),
            col=col, mat=mat
        )
        parts.append(thumb)

        # Dedos 2 a 5: Índice, Medio, Anular, Meñique (con falanges segmentadas)
        finger_offsets = [
            ("Index",  -0.024, 0.058),
            ("Middle", -0.008, 0.065),
            ("Ring",    0.008, 0.060),
            ("Pinky",   0.024, 0.048),
        ]
        for f_name, f_y, f_len in finger_offsets:
            finger = make_cylinder(
                f"Anat_Finger_{f_name}_{side}",
                location=(sign * X_SH, f_y, palm_z - 0.032 - f_len * 0.45),
                radius=0.008, depth=f_len, vertices=10,
                col=col, mat=mat
            )
            parts.append(finger)

    return parts
