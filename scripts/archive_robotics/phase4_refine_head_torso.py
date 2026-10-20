#!/usr/bin/env python3
"""
scripts/phase4_refine_head_torso.py
=====================================================
FASE 4 - PASO 2: REFINAMIENTO DE CABEZA Y TORSO (1.80m)
Refina la anatomía del humanoide robótico aplicando modificadores Subdivision Surface,
Bevels, placas pectorales divididas, abdomen segmentado atlético, columna cervical,
e integración de la placa facial real 3D (face_mesh.obj).

Salidas:
  - character_data/robot_v2_refined.blend
  - character_data/phase4_capture2_refined.png
"""

import bpy
import os
import sys
import json
import math

BASE_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "character_data")
METRICS_PATH = os.path.join(OUTPUT_DIR, "body_metrics_real.json")
FACE_OBJ_PATH = os.path.join(OUTPUT_DIR, "face_mesh.obj")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def load_metrics():
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data["proportions"]
    return None

def make_pbr_material(name, base_color, metallic=0.0, roughness=0.5, emission=None, em_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        for inp_name in ["Emission", "Emission Color"]:
            if inp_name in bsdf.inputs:
                bsdf.inputs[inp_name].default_value = (*emission, 1.0)
                break
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = em_strength
    return mat

def add_subsurf(obj, levels=2):
    mod = obj.modifiers.new("Subsurf", "SUBSURF")
    mod.levels = levels
    mod.render_levels = levels

def add_bevel(obj, width=0.008, segments=3):
    mod = obj.modifiers.new("Bevel", "BEVEL")
    mod.width = width
    mod.segments = segments

def shade_smooth(obj):
    if obj.type == 'MESH' and obj.data:
        for p in obj.data.polygons:
            p.use_smooth = True

def create_cyclorama(col):
    mesh = bpy.data.meshes.new("Cyclorama_Mesh")
    obj = bpy.data.objects.new("Studio_Cyclorama", mesh)
    col.objects.link(obj)

    verts = []
    faces = []
    profile_pts = [(-5.0, 0.0), (1.0, 0.0)]
    for i in range(1, 14):
        angle = (math.pi / 2.0) * (i / 14.0)
        py = 1.0 + 1.8 * (1.0 - math.cos(angle))
        pz = 1.8 * math.sin(angle)
        profile_pts.append((py, pz))
    profile_pts.append((2.8, 5.0))

    n_pts = len(profile_pts)
    for y, z in profile_pts:
        verts.append((-8.0, y, z))
        verts.append((8.0, y, z))

    for i in range(n_pts - 1):
        v0 = i * 2
        v1 = i * 2 + 1
        v2 = (i + 1) * 2 + 1
        v3 = (i + 1) * 2
        faces.append((v0, v1, v2, v3))

    mesh.from_pydata(verts, [], faces)
    mesh.update()

    mat_cyc = bpy.data.materials.new("Mat_Studio_Cyclorama")
    mat_cyc.use_nodes = True
    cbsdf = mat_cyc.node_tree.nodes.get("Principled BSDF")
    cbsdf.inputs["Base Color"].default_value = (0.16, 0.18, 0.22, 1.0)
    cbsdf.inputs["Roughness"].default_value = 0.60
    obj.data.materials.append(mat_cyc)
    shade_smooth(obj)
    return obj

def build_refined():
    clear_scene()
    col = bpy.data.collections.new("Robot_Refined_180cm")
    bpy.context.scene.collection.children.link(col)

    # ── MATERIALES ────────────────────────────────────────────────────────────
    mat_chassis = make_pbr_material("Mat_Chassis_Gunmetal", (0.08, 0.09, 0.11), metallic=0.88, roughness=0.28)
    mat_armor   = make_pbr_material("Mat_Armor_Silver",     (0.68, 0.72, 0.76), metallic=0.75, roughness=0.35)
    mat_face    = make_pbr_material("Mat_FacePlate_Custom", (0.78, 0.80, 0.84), metallic=0.70, roughness=0.24)
    mat_joint   = make_pbr_material("Mat_Joint_Carbon",     (0.04, 0.04, 0.05), metallic=0.50, roughness=0.45)
    mat_gold    = make_pbr_material("Mat_Actuator_Gold",    (0.85, 0.65, 0.25), metallic=0.92, roughness=0.20)
    mat_cyan    = make_pbr_material("Mat_Cyan_Sensor",      (0.00, 0.85, 1.00), metallic=0.10, roughness=0.10,
                                    emission=(0.0, 0.85, 1.0), em_strength=8.0)

    def link_obj(obj, mat):
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)
        if obj.data and hasattr(obj.data, "materials"):
            obj.data.materials.append(mat)
        shade_smooth(obj)
        return obj

    # ──────────────────────────────────────────────────────────────────────────
    # MEDIDAS PROPORCIONALES (ALTURA TOTAL = 1.80m, SUELO = Z 0.0)
    # ──────────────────────────────────────────────────────────────────────────
    H_HEAD_TOP  = 1.800
    H_HEAD_CTR  = 1.710
    R_HEAD      = 0.095
    H_NECK_CTR  = 1.585
    L_NECK      = 0.080

    H_SHOULDER  = 1.505
    W_SHOULDER  = 0.443  # Biacromial real Leonidas
    H_CHEST_CTR = 1.370
    W_CHEST     = 0.390
    D_CHEST     = 0.250
    H_CHEST     = 0.220

    H_WAIST_CTR = 1.160
    W_WAIST     = 0.250
    D_WAIST     = 0.190

    H_PELVIS_CTR= 0.950
    W_PELVIS    = 0.270
    D_PELVIS    = 0.200

    Z_HIP_JOINT = 0.880
    X_HIP       = 0.110
    Z_KNEE      = 0.490
    Z_ANKLE     = 0.085

    X_SHOULDER  = W_SHOULDER / 2.0  # 0.2215
    Z_ELBOW     = 1.205
    Z_WRIST     = 0.910
    Z_FINGERTIP = 0.790

    # ── 1. CABEZA REFINADA ───────────────────────────────────────────────────
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=R_HEAD, segments=32, ring_count=24,
        location=(0, 0, H_HEAD_CTR)
    )
    cranium = bpy.context.active_object
    cranium.name = "Refined_Cranium"
    cranium.scale = (0.92, 1.06, 1.02)
    add_subsurf(cranium, 2)
    link_obj(cranium, mat_chassis)

    # Mandíbula robótica biselada
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0, -0.035, H_HEAD_CTR - 0.072)
    )
    jaw = bpy.context.active_object
    jaw.name = "Refined_Jaw"
    jaw.scale = (0.105, 0.110, 0.065)
    add_bevel(jaw, 0.015, 3)
    add_subsurf(jaw, 1)
    link_obj(jaw, mat_armor)

    # Sensores laterales / audífonos robóticos
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.024, depth=0.025, vertices=24,
            location=(sign * 0.096, 0.005, H_HEAD_CTR),
            rotation=(0, math.radians(90), 0)
        )
        ear_pod = bpy.context.active_object
        ear_pod.name = f"Refined_EarPod_{side}"
        add_bevel(ear_pod, 0.004, 2)
        link_obj(ear_pod, mat_gold)

        # Anillo LED en el sensor lateral
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.020, minor_radius=0.003, major_segments=24, minor_segments=8,
            location=(sign * 0.108, 0.005, H_HEAD_CTR),
            rotation=(0, math.radians(90), 0)
        )
        ear_led = bpy.context.active_object
        ear_led.name = f"Refined_EarLED_{side}"
        link_obj(ear_led, mat_cyan)

    # Placa facial real 3D importada de face_mesh.obj
    if os.path.exists(FACE_OBJ_PATH):
        try:
            bpy.ops.wm.obj_import(filepath=FACE_OBJ_PATH)
            face_imported = bpy.context.selected_objects[0]
            face_imported.name = "Refined_UserFacePlate_3D"
            face_imported.scale = (0.95, 0.95, 0.95)
            face_imported.location = (0.0, -0.060, H_HEAD_CTR - 0.010)
            add_bevel(face_imported, 0.002, 2)
            add_subsurf(face_imported, 1)
            link_obj(face_imported, mat_face)
            print("[✓] Placa facial 3D de Leonidas importada y posicionada exitosamente.")
        except Exception as e:
            print(f"[*] OBJ import aviso: {e}")

    # Visor estereoscópico LED (IPD = 7.5 cm)
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.012, segments=18, ring_count=12,
            location=(sign * (0.075 / 2.0), -0.088, H_HEAD_CTR + 0.012)
        )
        eye_led = bpy.context.active_object
        eye_led.name = f"Refined_EyeLED_{side}"
        link_obj(eye_led, mat_cyan)

    # ── 2. CUELLO ARTICULADO (VÉRTEBRAS MECÁNICAS) ───────────────────────────
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.045, depth=L_NECK, vertices=24,
        location=(0, 0, H_NECK_CTR)
    )
    neck_core = bpy.context.active_object
    neck_core.name = "Refined_Neck_Piston"
    link_obj(neck_core, mat_gold)

    for i in [-0.025, 0.0, 0.025]:
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.058, minor_radius=0.009, major_segments=24, minor_segments=8,
            location=(0, 0, H_NECK_CTR + i)
        )
        ring = bpy.context.active_object
        ring.name = f"Refined_Neck_Ring_{i}"
        link_obj(ring, mat_armor)

    # ── 3. TÓRAX Y PECHO REFINADO ─────────────────────────────────────────────
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, H_CHEST_CTR))
    chest_core = bpy.context.active_object
    chest_core.name = "Refined_Chest_Chassis"
    chest_core.scale = (W_CHEST * 0.90, D_CHEST * 0.85, H_CHEST)
    add_bevel(chest_core, 0.02, 3)
    add_subsurf(chest_core, 1)
    link_obj(chest_core, mat_chassis)

    # Placas pectorales anatómicas divididas
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sign * (W_CHEST * 0.24), -D_CHEST * 0.44, H_CHEST_CTR + 0.025)
        )
        pec_plate = bpy.context.active_object
        pec_plate.name = f"Refined_PectoralPlate_{side}"
        pec_plate.scale = (W_CHEST * 0.40, 0.038, H_CHEST * 0.60)
        pec_plate.rotation_euler = (math.radians(-4), sign * math.radians(-5), sign * math.radians(3))
        add_bevel(pec_plate, 0.012, 3)
        add_subsurf(pec_plate, 1)
        link_obj(pec_plate, mat_armor)

    # Placas laterales de costillas
    for side, sign in [("L", -1), ("R", 1)]:
        for r_idx, r_z in enumerate([-0.05, -0.01, 0.03]):
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(sign * (W_CHEST * 0.46), -0.02, H_CHEST_CTR + r_z)
            )
            rib = bpy.context.active_object
            rib.name = f"Refined_RibPlate_{side}_{r_idx}"
            rib.scale = (0.025, D_CHEST * 0.60, 0.028)
            add_bevel(rib, 0.006, 2)
            link_obj(rib, mat_armor)

    # ── 4. ABDOMEN ATLETA SEGMENTADO ──────────────────────────────────────────
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.065, depth=0.170, vertices=20,
        location=(0, 0.01, H_WAIST_CTR)
    )
    spine_core = bpy.context.active_object
    spine_core.name = "Refined_Abdominal_Spine"
    link_obj(spine_core, mat_joint)

    abs_levels = [
        (H_WAIST_CTR + 0.055, 0.088, 0.038),
        (H_WAIST_CTR,         0.082, 0.035),
        (H_WAIST_CTR - 0.055, 0.076, 0.032),
    ]
    for lvl_idx, (abs_z, abs_w, abs_h) in enumerate(abs_levels):
        for side, sign in [("L", -1), ("R", 1)]:
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(sign * (abs_w * 0.55), -D_WAIST * 0.44, abs_z)
            )
            ab_plate = bpy.context.active_object
            ab_plate.name = f"Refined_AbPlate_{side}_{lvl_idx}"
            ab_plate.scale = (abs_w * 0.46, 0.024, abs_h * 0.44)
            add_bevel(ab_plate, 0.008, 2)
            add_subsurf(ab_plate, 1)
            link_obj(ab_plate, mat_armor)

    # ── 5. PELVIS Y ARTICULACIÓN DE CADERA ───────────────────────────────────
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, H_PELVIS_CTR))
    pelvis = bpy.context.active_object
    pelvis.name = "Refined_Pelvis"
    pelvis.scale = (W_PELVIS, D_PELVIS, 0.160)
    add_bevel(pelvis, 0.025, 3)
    add_subsurf(pelvis, 1)
    link_obj(pelvis, mat_chassis)

    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0, -D_PELVIS * 0.48, H_PELVIS_CTR - 0.02)
    )
    pelvis_guard = bpy.context.active_object
    pelvis_guard.name = "Refined_Pelvis_Guard"
    pelvis_guard.scale = (0.120, 0.035, 0.120)
    add_bevel(pelvis_guard, 0.015, 2)
    link_obj(pelvis_guard, mat_armor)

    # ── 6. HOMBROS Y BRAZOS REFINADOS ─────────────────────────────────────────
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.088, segments=24, ring_count=16,
            location=(sign * (X_SHOULDER + 0.015), 0, H_SHOULDER + 0.015)
        )
        pauldron = bpy.context.active_object
        pauldron.name = f"Refined_Pauldron_{side}"
        pauldron.scale = (1.05, 0.90, 0.85)
        add_bevel(pauldron, 0.012, 2)
        add_subsurf(pauldron, 1)
        link_obj(pauldron, mat_armor)

        l_arm = H_SHOULDER - Z_ELBOW
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.052, depth=l_arm * 0.88, vertices=20,
            location=(sign * X_SHOULDER, 0, (H_SHOULDER + Z_ELBOW) / 2.0)
        )
        bicep = bpy.context.active_object
        bicep.name = f"Refined_Bicep_{side}"
        add_subsurf(bicep, 1)
        link_obj(bicep, mat_chassis)

        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sign * (X_SHOULDER + 0.045), 0, (H_SHOULDER + Z_ELBOW) / 2.0)
        )
        arm_guard = bpy.context.active_object
        arm_guard.name = f"Refined_ArmGuard_{side}"
        arm_guard.scale = (0.022, 0.075, l_arm * 0.70)
        add_bevel(arm_guard, 0.008, 2)
        link_obj(arm_guard, mat_armor)

        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.054, depth=0.035, vertices=24,
            location=(sign * X_SHOULDER, 0, Z_ELBOW),
            rotation=(0, math.radians(90), 0)
        )
        elbow_joint = bpy.context.active_object
        elbow_joint.name = f"Refined_Elbow_Disc_{side}"
        add_bevel(elbow_joint, 0.005, 2)
        link_obj(elbow_joint, mat_gold)

        l_fore = Z_ELBOW - Z_WRIST
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.044, depth=l_fore * 0.88, vertices=20,
            location=(sign * X_SHOULDER, 0, (Z_ELBOW + Z_WRIST) / 2.0)
        )
        forearm = bpy.context.active_object
        forearm.name = f"Refined_Forearm_{side}"
        add_subsurf(forearm, 1)
        link_obj(forearm, mat_chassis)

        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.040, minor_radius=0.008, major_segments=20, minor_segments=8,
            location=(sign * X_SHOULDER, 0, Z_WRIST)
        )
        wrist_ring = bpy.context.active_object
        wrist_ring.name = f"Refined_Wrist_Ring_{side}"
        link_obj(wrist_ring, mat_armor)

        l_hand = Z_WRIST - Z_FINGERTIP
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sign * X_SHOULDER, 0, (Z_WRIST + Z_FINGERTIP) / 2.0)
        )
        hand = bpy.context.active_object
        hand.name = f"Refined_Hand_{side}"
        hand.scale = (0.036, 0.082, l_hand)
        add_bevel(hand, 0.008, 2)
        link_obj(hand, mat_armor)

    # ── 7. PIERNAS Y RODILLAS REFINADAS ───────────────────────────────────────
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.076, segments=24, ring_count=16,
            location=(sign * X_HIP, 0, Z_HIP_JOINT)
        )
        hip_sph = bpy.context.active_object
        hip_sph.name = f"Refined_HipSphere_{side}"
        link_obj(hip_sph, mat_joint)

        l_thigh = Z_HIP_JOINT - Z_KNEE
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.074, depth=l_thigh * 0.88, vertices=22,
            location=(sign * X_HIP, 0, (Z_HIP_JOINT + Z_KNEE) / 2.0)
        )
        thigh_core = bpy.context.active_object
        thigh_core.name = f"Refined_Thigh_{side}"
        add_subsurf(thigh_core, 1)
        link_obj(thigh_core, mat_chassis)

        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sign * X_HIP, -0.065, (Z_HIP_JOINT + Z_KNEE) / 2.0)
        )
        quad_guard = bpy.context.active_object
        quad_guard.name = f"Refined_QuadGuard_{side}"
        quad_guard.scale = (0.095, 0.026, l_thigh * 0.75)
        add_bevel(quad_guard, 0.012, 2)
        link_obj(quad_guard, mat_armor)

        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.068, depth=0.045, vertices=24,
            location=(sign * X_HIP, 0, Z_KNEE),
            rotation=(0, math.radians(90), 0)
        )
        knee_disc = bpy.context.active_object
        knee_disc.name = f"Refined_KneeDisc_{side}"
        add_bevel(knee_disc, 0.006, 2)
        link_obj(knee_disc, mat_gold)

        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sign * X_HIP, -0.065, Z_KNEE)
        )
        patella = bpy.context.active_object
        patella.name = f"Refined_Patella_{side}"
        patella.scale = (0.082, 0.028, 0.082)
        add_bevel(patella, 0.010, 2)
        link_obj(patella, mat_armor)

        l_shin = Z_KNEE - Z_ANKLE
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.060, depth=l_shin * 0.88, vertices=22,
            location=(sign * X_HIP, 0, (Z_KNEE + Z_ANKLE) / 2.0)
        )
        shin_core = bpy.context.active_object
        shin_core.name = f"Refined_ShinCore_{side}"
        add_subsurf(shin_core, 1)
        link_obj(shin_core, mat_chassis)

        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sign * X_HIP, -0.054, (Z_KNEE + Z_ANKLE) / 2.0)
        )
        shin_plate = bpy.context.active_object
        shin_plate.name = f"Refined_ShinPlate_{side}"
        shin_plate.scale = (0.076, 0.024, l_shin * 0.72)
        add_bevel(shin_plate, 0.010, 2)
        link_obj(shin_plate, mat_armor)

        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sign * X_HIP, -0.065, Z_ANKLE / 2.0)
        )
        foot = bpy.context.active_object
        foot.name = f"Refined_Foot_{side}"
        foot.scale = (0.096, 0.220, Z_ANKLE)
        add_bevel(foot, 0.012, 2)
        link_obj(foot, mat_armor)

    # ── 8. CICLORAMA DE ESTUDIO ───────────────────────────────────────────────
    create_cyclorama(col)

    # ── 9. ILUMINACIÓN CINEMÁTICA ─────────────────────────────────────────────
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World_Refined")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.06, 0.07, 0.09, 1.0)
        bg_node.inputs["Strength"].default_value = 0.5

    # Key Light (Foco principal 45 grados)
    bpy.ops.object.light_add(type='SPOT', location=(3.2, -3.4, 3.0))
    key = bpy.context.active_object
    key.name = "Key_Light_Refined"
    key.data.energy = 1100
    key.data.spot_size = math.radians(70)
    key.data.spot_blend = 0.4
    key.data.color = (1.0, 0.96, 0.90)
    col.objects.link(key)

    # Fill Light difuso (contralateral)
    bpy.ops.object.light_add(type='AREA', location=(-3.2, -2.6, 1.8))
    fill = bpy.context.active_object
    fill.name = "Fill_Light_Refined"
    fill.data.energy = 420
    fill.data.size = 3.5
    fill.data.color = (0.75, 0.88, 1.0)
    col.objects.link(fill)

    # Rim / Kicker Light (borde azul cian para silueta)
    bpy.ops.object.light_add(type='SPOT', location=(-1.5, 3.4, 2.8))
    rim = bpy.context.active_object
    rim.name = "Rim_Light_Refined"
    rim.data.energy = 850
    rim.data.spot_size = math.radians(60)
    rim.data.color = (0.0, 0.85, 1.0)
    col.objects.link(rim)

    # ── 10. TARGET EMPTY Y CÁMARA 3/4 PERFECTAMENTE ENCUADRADA ───────────────
    # Empty centrado en el medio geométrico del humanoide (Z = 0.90)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 0.90))
    target_empty = bpy.context.active_object
    target_empty.name = "Cam_LookAt_Target"
    col.objects.link(target_empty)

    # Cámara 3/4 a distancia óptima con lente de 38mm para encuadre completo de 1.80m
    bpy.ops.object.camera_add(location=(2.4, -4.8, 1.35))
    cam = bpy.context.active_object
    cam.name = "Cam_Refined_34"
    cam.data.lens = 38
    cam.data.clip_start = 0.1
    cam.data.clip_end = 100.0

    # Constraint Track To al centro exacto del robot
    track = cam.constraints.new(type='TRACK_TO')
    track.target = target_empty
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    bpy.context.scene.camera = cam
    col.objects.link(cam)

    # ── 11. RENDERIZADO CYCLES OPTIX ─────────────────────────────────────────
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        for d in prefs.get_devices_for_type("OPTIX"):
            d.use = True
        print("[+] OptiX GPU activo para refinamiento.")
    except Exception as e:
        print(f"[*] GPU notice: {e}")

    scene.cycles.samples = 128
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = "PNG"

    out_img = os.path.join(OUTPUT_DIR, "phase4_capture2_refined.png")
    scene.render.filepath = out_img
    bpy.ops.render.render(write_still=True)
    print(f"[✓] CAPTURA 2 (Refinamiento 3/4) guardada → {out_img}")

    # Guardar archivo .blend de la fase
    blend_path = os.path.join(OUTPUT_DIR, "robot_v2_refined.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[✓] Guardado archivo maestro: {blend_path}")

if __name__ == "__main__":
    build_refined()
