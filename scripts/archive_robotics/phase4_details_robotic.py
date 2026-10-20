#!/usr/bin/env python3
"""
scripts/phase4_details_robotic.py
FASE 4 - DETALLES FINALES ROBÓTICOS
Agrega paneles de acceso, cables, articulaciones detalladas, cabello estilizado.
Vista completa para captura final de Fase 4.
Ejecutar: /usr/local/bin/blender -b -P scripts/phase4_details_robotic.py
"""

import bpy
import os
import math

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "character_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_mat(name, color, metallic=0.0, roughness=0.7, emission=None, em_str=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        for n in ["Emission", "Emission Color"]:
            if n in bsdf.inputs:
                bsdf.inputs[n].default_value = (*emission, 1.0)
                break
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = em_str
    return mat


def add_to_col(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)


def P(obj, mat, col):
    add_to_col(obj, col)
    if obj.data and hasattr(obj.data, "materials"):
        obj.data.materials.append(mat)
    return obj


def subsurf(obj, lv=2):
    mod = obj.modifiers.new("Sub", "SUBSURF")
    mod.levels = lv
    mod.render_levels = lv


def build_details():
    clear_scene()

    col = bpy.data.collections.new("Robot_Phase4_Final")
    bpy.context.scene.collection.children.link(col)

    # ── MATERIALES ──────────────────────────────────────────────────────────
    mb    = make_mat("M_Body",    (0.06, 0.07, 0.09), 0.90, 0.22)
    marm  = make_mat("M_Armor",   (0.70, 0.74, 0.78), 0.82, 0.38)
    mcarb = make_mat("M_Carbon",  (0.03, 0.03, 0.04), 0.42, 0.56)
    mcyan = make_mat("M_Cyan",    (0.00, 0.85, 1.00), 0.10, 0.05,
                     emission=(0.0, 0.85, 1.0), em_str=7.0)
    mamb  = make_mat("M_Amber",   (1.00, 0.45, 0.05), 0.10, 0.05,
                     emission=(1.0, 0.45, 0.05), em_str=5.0)
    mface = make_mat("M_Face",    (0.60, 0.66, 0.72), 0.68, 0.32)
    mhair = make_mat("M_Hair",    (0.20, 0.13, 0.07), 0.18, 0.65)
    mjoint= make_mat("M_Joint",   (0.05, 0.05, 0.06), 0.55, 0.50)
    mwire = make_mat("M_Wire",    (0.90, 0.40, 0.05), 0.10, 0.80)

    # ── CABEZA ───────────────────────────────────────────────────────────────
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.46, segments=32, ring_count=24, location=(0, 0, 1.72))
    head = bpy.context.active_object
    head.name = "Head_Cranium"
    head.scale = (0.87, 0.80, 0.95)
    subsurf(head, 2)
    P(head, mb, col)

    # Placa facial
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.348, 1.68))
    fp = bpy.context.active_object
    fp.name = "Head_FacePlate"
    fp.scale = (0.43, 0.055, 0.50)
    subsurf(fp, 1)
    P(fp, mface, col)

    # Ojos LED
    for sx, nm in [(-0.155, "Eye_L"), (0.155, "Eye_R")]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.056, depth=0.045, vertices=24,
            location=(sx, -0.375, 1.73), rotation=(math.radians(90), 0, 0))
        e = bpy.context.active_object
        e.name = nm
        P(e, mcyan, col)
        # Iris interior (brillo)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.028, depth=0.05, vertices=16,
            location=(sx, -0.385, 1.73), rotation=(math.radians(90), 0, 0))
        iris = bpy.context.active_object
        iris.name = nm + "_Iris"
        P(iris, mcyan, col)
        # Marco del ojo
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.066, minor_radius=0.010,
            location=(sx, -0.375, 1.73), rotation=(math.radians(90), 0, 0))
        ring = bpy.context.active_object
        ring.name = nm + "_Ring"
        P(ring, marm, col)

    # Visor HUD (barra nariz)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.381, 1.73))
    visor = bpy.context.active_object
    visor.name = "Head_Visor_HUD"
    visor.scale = (0.20, 0.020, 0.033)
    P(visor, mamb, col)

    # Panel de boca / ventilación
    for zy, z in [(1.455, "Mouth"), (1.495, "Chin_Vent")]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.375, zy))
        panel = bpy.context.active_object
        panel.name = f"Head_{z}"
        panel.scale = (0.28 if zy > 1.47 else 0.22, 0.022, 0.020)
        P(panel, mcarb, col)

    # Sensores laterales (oído)
    for sx, nm in [(-0.465, "Ear_L"), (0.465, "Ear_R")]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.062, depth=0.065, vertices=18,
            location=(sx, 0.0, 1.72), rotation=(0, math.radians(90), 0))
        ear = bpy.context.active_object
        ear.name = nm
        P(ear, marm, col)
        # LED del sensor
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.020, depth=0.01, vertices=12,
            location=(sx * 1.065, 0.0, 1.72), rotation=(0, math.radians(90), 0))
        led = bpy.context.active_object
        led.name = nm + "_LED"
        P(led, mcyan, col)

    # Antenas
    for sx in [-0.42, 0.42]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.012, depth=0.28, vertices=8,
            location=(sx, 0.0, 2.06))
        ant = bpy.context.active_object
        ant.name = "Antenna"
        P(ant, mcarb, col)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.024, segments=8, ring_count=6,
            location=(sx, 0.0, 2.21))
        tip = bpy.context.active_object
        tip.name = "Antenna_Tip"
        P(tip, mcyan, col)

    # ── CABELLO ESTILIZADO (curvas convertidas) ──────────────────────────────
    # Representado con cilindros curvos en la parte trasera/lateral de la cabeza
    hair_positions = [
        (-0.24, 0.28, 1.98), (-0.16, 0.30, 1.94), (0.0, 0.32, 1.96),
        (0.16, 0.30, 1.94), (0.24, 0.28, 1.98),
        (-0.38, 0.18, 1.80), (-0.42, 0.10, 1.65), (-0.40, 0.05, 1.50),
        (0.38, 0.18, 1.80), (0.42, 0.10, 1.65), (0.40, 0.05, 1.50),
        (-0.28, 0.25, 1.50), (0.28, 0.25, 1.50),
    ]
    for i, (hx, hy, hz) in enumerate(hair_positions):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.035, depth=0.18, vertices=8,
            location=(hx, hy, hz),
            rotation=(0.15, 0, hx * 0.5))
        h = bpy.context.active_object
        h.name = f"Hair_Strand_{i}"
        P(h, mhair, col)

    # ── CUELLO ───────────────────────────────────────────────────────────────
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.108, depth=0.28, vertices=20, location=(0, 0, 1.22))
    neck = bpy.context.active_object
    neck.name = "Neck_Core"
    P(neck, mcarb, col)
    for z in (1.09, 1.20, 1.31):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.122, minor_radius=0.016, location=(0, 0, z))
        P(bpy.context.active_object, marm, col).name = "Neck_Ring"

    # Hidráulicos del cuello
    for offset_x in [-0.06, 0.06]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.016, depth=0.22, vertices=8,
            location=(offset_x, -0.085, 1.20))
        P(bpy.context.active_object, mcarb, col).name = "Neck_Hydraulic"

    # ── TORSO ────────────────────────────────────────────────────────────────
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.76))
    chest = bpy.context.active_object
    chest.name = "Torso_Chest"
    chest.scale = (0.57, 0.27, 0.29)
    subsurf(chest, 1)
    P(chest, mb, col)

    # Paneles del pecho
    for sx in [-0.285, 0.285]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, -0.26, 0.90))
        cp = bpy.context.active_object
        cp.name = "Chest_Panel"
        cp.scale = (0.175, 0.028, 0.115)
        P(cp, marm, col)
        # Detalle línea en panel
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, -0.268, 0.90))
        line = bpy.context.active_object
        line.name = "Chest_Panel_Line"
        line.scale = (0.165, 0.005, 0.008)
        P(line, mcyan, col)

    # Power Core
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.098, depth=0.058, vertices=32,
        location=(0, -0.262, 0.78), rotation=(math.radians(90), 0, 0))
    core = bpy.context.active_object
    core.name = "Power_Core"
    P(core, mcyan, col)
    # Anillo del core
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.112, minor_radius=0.014,
        location=(0, -0.262, 0.78), rotation=(math.radians(90), 0, 0))
    P(bpy.context.active_object, marm, col).name = "Core_Ring"

    # Placa abdominal
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.238, 0.50))
    ab = bpy.context.active_object
    ab.name = "Abdominal_Plate"
    ab.scale = (0.28, 0.025, 0.21)
    P(ab, marm, col)
    # Rejillas abdomen
    for dz in [-0.06, 0.0, 0.06]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.245, 0.50 + dz))
        gr = bpy.context.active_object
        gr.name = "Abdominal_Grill"
        gr.scale = (0.25, 0.008, 0.014)
        P(gr, mcarb, col)

    # Cintura
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.43))
    waist = bpy.context.active_object
    waist.name = "Torso_Waist"
    waist.scale = (0.45, 0.23, 0.19)
    subsurf(waist, 1)
    P(waist, mb, col)

    # Cadera
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.07))
    hips = bpy.context.active_object
    hips.name = "Torso_Hips"
    hips.scale = (0.54, 0.25, 0.20)
    subsurf(hips, 1)
    P(hips, mb, col)
    # Paneles de cadera
    for sx in [-0.25, 0.25]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, -0.24, 0.07))
        hp = bpy.context.active_object
        hp.name = "Hip_Panel"
        hp.scale = (0.155, 0.025, 0.145)
        P(hp, marm, col)

    # ── HOMBROS ──────────────────────────────────────────────────────────────
    for sx, nm in [(-0.70, "L"), (0.70, "R")]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.172, segments=22, ring_count=16, location=(sx, 0, 0.88))
        sh = bpy.context.active_object
        sh.name = f"Shoulder_{nm}"
        sh.scale = (1.0, 0.76, 0.76)
        subsurf(sh, 1)
        P(sh, marm, col)
        # Detalle de hombro
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.06, depth=0.04, vertices=16,
            location=(sx * 1.15, 0, 0.88), rotation=(0, math.radians(90), 0))
        P(bpy.context.active_object, mcyan, col).name = f"Shoulder_LED_{nm}"

    # ── BRAZOS ───────────────────────────────────────────────────────────────
    for sx, nm in [(-0.82, "L"), (0.82, "R")]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.083, depth=0.46, vertices=18, location=(sx, 0, 0.60))
        ua = bpy.context.active_object
        ua.name = f"UpperArm_{nm}"
        subsurf(ua, 1)
        P(ua, mb, col)
        # Panel del brazo
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, -0.06, 0.68))
        P(bpy.context.active_object, marm, col).name = f"Arm_Panel_{nm}"
        bpy.context.active_object.scale = (0.055, 0.010, 0.16)

        # Codo
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.090, segments=18, ring_count=12, location=(sx, 0, 0.32))
        P(bpy.context.active_object, mjoint, col).name = f"Elbow_{nm}"
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.100, minor_radius=0.017,
            location=(sx, 0, 0.32))
        P(bpy.context.active_object, marm, col).name = f"Elbow_Ring_{nm}"

        # Antebrazo
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.070, depth=0.42, vertices=16, location=(sx, 0, 0.07))
        fa = bpy.context.active_object
        fa.name = f"ForeArm_{nm}"
        subsurf(fa, 1)
        P(fa, mb, col)

        # Muñeca
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.078, minor_radius=0.015, location=(sx, 0, -0.15))
        P(bpy.context.active_object, marm, col).name = f"Wrist_{nm}"

        # Mano
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0, -0.27))
        hand = bpy.context.active_object
        hand.name = f"Hand_{nm}"
        hand.scale = (0.108, 0.062, 0.135)
        subsurf(hand, 1)
        P(hand, marm, col)

        # Dedos (3 cilindros)
        for fi, fz in enumerate([-0.335, -0.355, -0.375]):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.016, depth=0.045, vertices=8,
                location=(sx + (fi - 1) * 0.028, -0.05, fz))
            P(bpy.context.active_object, mcarb, col).name = f"Finger_{nm}_{fi}"

    # ── PIERNAS ──────────────────────────────────────────────────────────────
    for sx, nm in [(-0.21, "L"), (0.21, "R")]:
        # Muslo
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.122, depth=0.52, vertices=20, location=(sx, 0, -0.52))
        th = bpy.context.active_object
        th.name = f"Thigh_{nm}"
        subsurf(th, 1)
        P(th, mb, col)
        # Panel del muslo
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, -0.1, -0.46))
        P(bpy.context.active_object, marm, col).name = f"Thigh_Panel_{nm}"
        bpy.context.active_object.scale = (0.07, 0.012, 0.18)

        # Rodilla
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.112, segments=18, ring_count=12, location=(sx, 0.005, -0.83))
        P(bpy.context.active_object, mjoint, col).name = f"Knee_{nm}"
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.126, minor_radius=0.017, location=(sx, 0, -0.83))
        P(bpy.context.active_object, marm, col).name = f"Knee_Ring_{nm}"
        # Detalle LED rodilla
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.022, depth=0.02, vertices=12,
            location=(sx, -0.112, -0.83), rotation=(math.radians(90), 0, 0))
        P(bpy.context.active_object, mcyan, col).name = f"Knee_LED_{nm}"

        # Espinilla
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.096, depth=0.49, vertices=18, location=(sx, 0, -1.12))
        sh = bpy.context.active_object
        sh.name = f"Shin_{nm}"
        subsurf(sh, 1)
        P(sh, mb, col)
        # Panel espinilla
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, -0.084, -1.04))
        P(bpy.context.active_object, marm, col).name = f"Shin_Panel_{nm}"
        bpy.context.active_object.scale = (0.065, 0.010, 0.15)

        # Tobillo
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.103, minor_radius=0.015, location=(sx, 0, -1.40))
        P(bpy.context.active_object, marm, col).name = f"Ankle_{nm}"

        # Pie
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0.09, -1.56))
        foot = bpy.context.active_object
        foot.name = f"Foot_{nm}"
        foot.scale = (0.122, 0.210, 0.070)
        subsurf(foot, 1)
        P(foot, mb, col)
        # Suela
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0.09, -1.63))
        sole = bpy.context.active_object
        sole.name = f"Sole_{nm}"
        sole.scale = (0.124, 0.215, 0.018)
        P(sole, mcarb, col)

    # ── CABLES DECORATIVOS ────────────────────────────────────────────────────
    for cx, cy, cz in [(-0.35, -0.08, 0.55), (0.35, -0.08, 0.55),
                        (-0.55, 0.0, 0.12),  (0.55, 0.0, 0.12)]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.010, depth=0.18, vertices=6,
            location=(cx, cy, cz),
            rotation=(0.2, 0, 0))
        P(bpy.context.active_object, mwire, col).name = "Cable"

    # ── ARMATURE (ESQUELETO) ──────────────────────────────────────────────────
    bpy.ops.object.armature_add(location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "Robot_Rig"
    arm_data = arm_obj.data
    arm_data.name = "Robot_Rig_Data"
    add_to_col(arm_obj, col)

    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones

    root = eb[0]
    root.name = "Root"
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.5)

    torso_b = eb.new("Torso")
    torso_b.head = (0, 0, 0.5)
    torso_b.tail = (0, 0, 1.05)
    torso_b.parent = root

    neck_b = eb.new("Neck")
    neck_b.head = (0, 0, 1.05)
    neck_b.tail = (0, 0, 1.36)
    neck_b.parent = torso_b

    head_b = eb.new("Head")
    head_b.head = (0, 0, 1.36)
    head_b.tail = (0, 0, 2.10)
    head_b.parent = neck_b

    for nm, xh, xt in [("ShoulderL", (-0.35, 0, 0.98), (-0.68, 0, 0.88)),
                         ("ShoulderR", (0.35, 0, 0.98), (0.68, 0, 0.88))]:
        b = eb.new(nm)
        b.head = xh
        b.tail = xt
        b.parent = torso_b

    for nm, hd, tl, par in [
        ("UpperArm_L", (-0.70, 0, 0.88), (-0.82, 0, 0.38), "ShoulderL"),
        ("ForeArm_L",  (-0.82, 0, 0.38), (-0.82, 0, -0.10), "UpperArm_L"),
        ("Hand_L",     (-0.82, 0, -0.10), (-0.82, 0, -0.38), "ForeArm_L"),
        ("UpperArm_R", (0.70, 0, 0.88), (0.82, 0, 0.38), "ShoulderR"),
        ("ForeArm_R",  (0.82, 0, 0.38), (0.82, 0, -0.10), "UpperArm_R"),
        ("Hand_R",     (0.82, 0, -0.10), (0.82, 0, -0.38), "ForeArm_R"),
        ("Thigh_L",    (-0.21, 0, -0.05), (-0.21, 0, -0.62), "Root"),
        ("Shin_L",     (-0.21, 0, -0.62), (-0.21, 0, -1.25), "Thigh_L"),
        ("Foot_L",     (-0.21, 0, -1.25), (-0.21, 0.16, -1.60), "Shin_L"),
        ("Thigh_R",    (0.21, 0, -0.05), (0.21, 0, -0.62), "Root"),
        ("Shin_R",     (0.21, 0, -0.62), (0.21, 0, -1.25), "Thigh_R"),
        ("Foot_R",     (0.21, 0, -1.25), (0.21, 0.16, -1.60), "Shin_R"),
    ]:
        b = eb.new(nm)
        b.head = hd
        b.tail = tl
        b.parent = eb[par]

    bpy.ops.object.mode_set(mode="OBJECT")

    # ── ILUMINACIÓN 3 PUNTOS ──────────────────────────────────────────────────
    bpy.ops.object.light_add(type="SPOT", location=(1.8, -2.8, 2.2))
    key = bpy.context.active_object
    key.name = "Key_Light"
    key.data.energy = 350.0
    key.data.color = (1.0, 0.94, 0.88)
    key.data.spot_size = math.radians(42)
    import mathutils
    key.rotation_euler = mathutils.Euler(
        (math.radians(62), 0, math.radians(32)), 'XYZ')
    add_to_col(key, col)

    bpy.ops.object.light_add(type="POINT", location=(-2.6, -1.5, 0.9))
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = 110.0
    fill.data.color = (0.52, 0.76, 1.0)
    add_to_col(fill, col)

    bpy.ops.object.light_add(type="SPOT", location=(0.0, 3.2, 2.5))
    rim = bpy.context.active_object
    rim.name = "Rim_Light"
    rim.data.energy = 480.0
    rim.data.color = (0.0, 0.88, 1.0)
    rim.data.spot_size = math.radians(30)
    rim.rotation_euler = mathutils.Euler(
        (math.radians(-52), 0, 0), 'XYZ')
    add_to_col(rim, col)

    # ── CÁMARA 3/4 COMPLETA ───────────────────────────────────────────────────
    bpy.ops.object.camera_add(
        location=(2.4, -4.2, 0.50),
        rotation=(math.radians(82), 0, math.radians(30)))
    cam = bpy.context.active_object
    cam.name = "Cam_Final_34"
    cam.data.lens = 52
    bpy.context.scene.camera = cam
    add_to_col(cam, col)

    # ── RENDER CAPTURA 3 ─────────────────────────────────────────────────────
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        for d in prefs.get_devices_for_type("OPTIX"):
            d.use = True
        print("[+] RTX 4070 OptiX OK")
    except Exception as e:
        scene.cycles.device = "CPU"
        print(f"[*] CPU mode: {e}")

    scene.cycles.samples = 160
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.image_settings.file_format = "PNG"

    out3 = os.path.join(OUTPUT_DIR, "phase4_capture3_details.png")
    scene.render.filepath = out3
    bpy.ops.render.render(write_still=True)
    print(f"[✓] CAPTURA 3 (Detalles Finales) guardada → {out3}")

    # ── GUARDAR BLEND ─────────────────────────────────────────────────────────
    blend_v3 = os.path.join(OUTPUT_DIR, "robot_v3_details.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_v3)
    print(f"[✓] .blend v3 guardado → {blend_v3}")


if __name__ == "__main__":
    build_details()
