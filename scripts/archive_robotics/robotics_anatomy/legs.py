"""
scripts/robotics_anatomy/legs.py
Bloqueo anatómico geométrico de muslos, cuádriceps (vasto medial en lágrima, vasto lateral),
rótula, gemelos asimétricos, tendón de Aquiles, maléolos de tobillo y pies con arco y 5 dedos (1.80m).
"""

import math
from .primitives import make_box, make_cylinder, make_sphere, make_wedge

def build_legs_and_feet(col, mat, metrics):
    HIP_Z = metrics["hip_joint_z"]   # 0.880
    HIP_X = metrics["hip_x"]         # 0.110
    KNEE_Z= metrics["knee_z"]        # 0.490
    ANK_Z = metrics["ankle_z"]       # 0.085

    L_THIGH = HIP_Z - KNEE_Z  # ~0.390
    L_SHIN  = KNEE_Z - ANK_Z  # ~0.405

    parts = []

    for side, sign in [("L", -1), ("R", 1)]:
        # ── 1. TROCÁNTER MAYOR (PUNTO ÓSEO LATERAL DE LA CADERA) ─────────────
        trochanter = make_sphere(
            f"Anat_Trochanter_{side}",
            location=(sign * (HIP_X + 0.072), 0, HIP_Z - 0.015),
            radius=0.032, segments=14, ring_count=10,
            scale=(0.9, 1.2, 1.0),
            col=col, mat=mat
        )
        parts.append(trochanter)

        # ── 2. MUSLO: CUÁDRICEPS ANATÓMICOS (4 GRUPOS MUSCULARES) ────────────
        thigh_mid_z = (HIP_Z + KNEE_Z) / 2.0

        # Recto femoral (vientre central anterior)
        rectus_fem = make_cylinder(
            f"Anat_RectusFemoris_{side}",
            location=(sign * HIP_X, -0.038, thigh_mid_z + 0.010),
            radius=0.046, depth=L_THIGH * 0.72, vertices=18,
            col=col, mat=mat
        )
        parts.append(rectus_fem)

        # Vasto lateral (gran abultamiento muscular exterior del muslo)
        vastus_lat = make_cylinder(
            f"Anat_VastusLateralis_{side}",
            location=(sign * (HIP_X + 0.042), -0.012, thigh_mid_z + 0.020),
            radius=0.048, depth=L_THIGH * 0.76, vertices=18,
            rotation=(0, sign * math.radians(-5), 0),
            scale=(1.15, 0.90, 1.0),
            col=col, mat=mat
        )
        parts.append(vastus_lat)

        # Vasto medial ("músculo en lágrima" sobre la cara interna de la rodilla)
        vastus_med = make_sphere(
            f"Anat_VastusMedialis_{side}",
            location=(sign * (HIP_X - 0.032), -0.038, KNEE_Z + 0.065),
            radius=0.042, segments=18, ring_count=12,
            scale=(1.10, 0.95, 1.40),
            rotation=(math.radians(10), sign * math.radians(15), 0),
            col=col, mat=mat
        )
        parts.append(vastus_med)

        # Isquiotibiales posteriores (bíceps femoral y semitendinoso)
        hamstrings = make_cylinder(
            f"Anat_Hamstrings_{side}",
            location=(sign * HIP_X, 0.036, thigh_mid_z),
            radius=0.052, depth=L_THIGH * 0.75, vertices=18,
            scale=(1.05, 0.95, 1.0),
            col=col, mat=mat
        )
        parts.append(hamstrings)

        # Aductores (cara interna superior del muslo)
        adductors = make_cylinder(
            f"Anat_Adductors_{side}",
            location=(sign * (HIP_X - 0.030), 0.005, HIP_Z - 0.085),
            radius=0.038, depth=0.140, vertices=16,
            col=col, mat=mat
        )
        parts.append(adductors)

        # ── 3. COMPLEJO DE LA RODILLA ─────────────────────────────────────────
        # Rótula (patella flotante anatómica)
        patella = make_box(
            f"Anat_Patella_{side}",
            location=(sign * HIP_X, -0.062, KNEE_Z),
            scale=(0.048, 0.026, 0.056),
            rotation=(math.radians(-8), 0, 0),
            col=col, mat=mat, bevel=0.008
        )
        parts.append(patella)

        # Tendón rotuliano hacia la tuberosidad tibial
        pat_tendon = make_box(
            f"Anat_PatellarTendon_{side}",
            location=(sign * HIP_X, -0.055, KNEE_Z - 0.042),
            scale=(0.024, 0.018, 0.042),
            col=col, mat=mat, bevel=0.004
        )
        parts.append(pat_tendon)

        # Cóndilos femorales (rodete articular posterior)
        condyles = make_cylinder(
            f"Anat_FemoralCondyles_{side}",
            location=(sign * HIP_X, 0.005, KNEE_Z),
            radius=0.055, depth=0.075, vertices=20,
            rotation=(0, math.radians(90), 0),
            col=col, mat=mat
        )
        parts.append(condyles)

        # ── 4. PIERNA INFERIOR: ESPINILLA, GEMELOS Y TENDÓN DE AQUILES ───────
        shin_mid_z = (KNEE_Z + ANK_Z) / 2.0

        # Cresta tibial (espinilla ósea anterior curvada)
        shin_crest = make_wedge(
            f"Anat_TibiaCrest_{side}",
            location=(sign * HIP_X, -0.045, shin_mid_z),
            scale=(0.032, 0.038, L_SHIN * 0.85),
            rotation=(math.radians(90), 0, 0),
            col=col, mat=mat, bevel=0.005
        )
        parts.append(shin_crest)

        # Gemelos / Gastrocnemio: cabeza medial (interna, más baja y voluminosa)
        calf_med = make_sphere(
            f"Anat_GastrocnemiusMedial_{side}",
            location=(sign * (HIP_X - 0.022), 0.042, KNEE_Z - 0.095),
            radius=0.044, segments=18, ring_count=14,
            scale=(0.95, 1.10, 1.65),
            col=col, mat=mat
        )
        parts.append(calf_med)

        # Gemelos / Gastrocnemio: cabeza lateral (externa, situada más alta)
        calf_lat = make_sphere(
            f"Anat_GastrocnemiusLateral_{side}",
            location=(sign * (HIP_X + 0.026), 0.040, KNEE_Z - 0.075),
            radius=0.042, segments=18, ring_count=14,
            scale=(0.95, 1.10, 1.55),
            col=col, mat=mat
        )
        parts.append(calf_lat)

        # Músculo Sóleo (capa muscular inferior plana)
        soleus = make_cylinder(
            f"Anat_Soleus_{side}",
            location=(sign * HIP_X, 0.025, shin_mid_z - 0.040),
            radius=0.036, depth=L_SHIN * 0.45, vertices=16,
            col=col, mat=mat
        )
        parts.append(soleus)

        # Tendón de Aquiles (cordón tendinoso posterior hacia el talón)
        achilles = make_cylinder(
            f"Anat_AchillesTendon_{side}",
            location=(sign * HIP_X, 0.035, ANK_Z + 0.045),
            radius=0.016, depth=0.100, vertices=14,
            col=col, mat=mat
        )
        parts.append(achilles)

        # ── 5. TOBILLO ANATÓMICO (MALÉOLOS ASIMÉTRICOS) ──────────────────────
        # Maléolo medial (interno - más alto)
        mal_med = make_sphere(
            f"Anat_MalleolusMedial_{side}",
            location=(sign * (HIP_X - 0.036), 0, ANK_Z + 0.014),
            radius=0.018, segments=14, ring_count=10,
            col=col, mat=mat
        )
        parts.append(mal_med)

        # Maléolo lateral (externo - más bajo)
        mal_lat = make_sphere(
            f"Anat_MalleolusLateral_{side}",
            location=(sign * (HIP_X + 0.036), 0, ANK_Z - 0.005),
            radius=0.018, segments=14, ring_count=10,
            col=col, mat=mat
        )
        parts.append(mal_lat)

        # ── 6. PIE ANATÓMICO CON ARCO Y 5 DEDOS ──────────────────────────────
        # Talón (Calcáneo que proyecta hacia atrás)
        heel = make_sphere(
            f"Anat_Calcaneus_{side}",
            location=(sign * HIP_X, 0.045, ANK_Z * 0.48),
            radius=0.032, segments=16, ring_count=12,
            scale=(0.95, 1.25, 0.85),
            col=col, mat=mat
        )
        parts.append(heel)

        # Puente y empeine del pie (arco plantar)
        instep = make_box(
            f"Anat_FootInstep_{side}",
            location=(sign * HIP_X, -0.048, ANK_Z * 0.45),
            scale=(0.082, 0.125, ANK_Z * 0.70),
            rotation=(math.radians(10), 0, 0),
            col=col, mat=mat, bevel=0.008
        )
        parts.append(instep)

        # Almohadilla metatarsiana (base de los dedos)
        ball = make_box(
            f"Anat_FootBall_{side}",
            location=(sign * HIP_X, -0.115, ANK_Z * 0.30),
            scale=(0.086, 0.045, ANK_Z * 0.45),
            col=col, mat=mat, bevel=0.006
        )
        parts.append(ball)

        # 5 Dedos del pie (Hallux gordo + 4 menores)
        toe_offsets = [
            ("BigToe", sign * -0.024, -0.155, 0.014, 0.036),
            ("Toe2",   sign * -0.008, -0.152, 0.011, 0.032),
            ("Toe3",   sign *  0.006, -0.148, 0.010, 0.028),
            ("Toe4",   sign *  0.018, -0.142, 0.009, 0.025),
            ("Toe5",   sign *  0.030, -0.134, 0.008, 0.022),
        ]
        for t_name, t_x, t_y, t_rad, t_len in toe_offsets:
            toe = make_cylinder(
                f"Anat_{t_name}_{side}",
                location=(sign * HIP_X + t_x, t_y, ANK_Z * 0.22),
                radius=t_rad, depth=t_len, vertices=10,
                rotation=(math.radians(90), 0, 0),
                col=col, mat=mat
            )
            parts.append(toe)

    return parts
