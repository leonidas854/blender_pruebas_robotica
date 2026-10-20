#!/usr/bin/env python3
"""
scripts/phase5_materials_lighting.py
FASE 5 - TEXTURIZADO, SHADING E ILUMINACIÓN CINEMÁTICA
Aplica materiales PBR completos (metálico, rugosidad, emisión),
esquema de iluminación cinemático de 3 puntos, y render final 1920x1080.
Ejecutar: /usr/local/bin/blender -b -P scripts/phase5_materials_lighting.py
"""

import bpy
import os
import math
import mathutils

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "character_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


# ─── MATERIALES PBR ──────────────────────────────────────────────────────────

def create_pbr_material(name, base_color, metallic=0.0, roughness=0.5,
                        specular=0.5, emission_color=None, emission_strength=0.0,
                        alpha=1.0):
    """Crea un material Principled BSDF con configuración PBR completa."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Nodo Output
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)

    # Principled BSDF principal
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if "Specular" in bsdf.inputs:
        bsdf.inputs["Specular"].default_value = specular
    elif "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = specular

    if emission_color and emission_strength > 0:
        for nm in ["Emission", "Emission Color"]:
            if nm in bsdf.inputs:
                bsdf.inputs[nm].default_value = (*emission_color, 1.0)
                break
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength

    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = 'BLEND'

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def create_noise_metallic_material(name, base_color, metallic=0.9, roughness=0.25):
    """Material metálico con variación de ruido para profundidad."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (900, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (500, 0)
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness

    # Nodo de textura de ruido para variación de roughness
    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-200, -200)
    noise.inputs["Scale"].default_value = 8.0
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.65
    if "Distortion" in noise.inputs:
        noise.inputs["Distortion"].default_value = 0.2

    # Mix para modular el roughness
    mix_rough = nodes.new("ShaderNodeMath")
    mix_rough.location = (100, -200)
    mix_rough.operation = 'MULTIPLY_ADD'
    if len(mix_rough.inputs) >= 3:
        mix_rough.inputs[1].default_value = 0.08
        mix_rough.inputs[2].default_value = roughness - 0.04

    links.new(noise.outputs["Fac"], mix_rough.inputs[0])
    links.new(mix_rough.outputs["Value"], bsdf.inputs["Roughness"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def add_to_col(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)


def P(obj, mat, col):
    add_to_col(obj, col)
    if obj.data and hasattr(obj.data, "materials"):
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    return obj


def subsurf(obj, lv=2):
    mod = obj.modifiers.new("Sub", "SUBSURF")
    mod.levels = lv
    mod.render_levels = lv


def build_phase5():
    clear_scene()

    col = bpy.data.collections.new("Robot_Phase5_Final")
    bpy.context.scene.collection.children.link(col)

    # ════════════════════════════════════════════════════════════════════════
    # PALETA DE MATERIALES PBR
    # ════════════════════════════════════════════════════════════════════════

    # Titanio oscuro – Chasis principal del cuerpo
    M_body = create_noise_metallic_material(
        "PBR_DarkTitanium", (0.055, 0.065, 0.08), metallic=0.92, roughness=0.20)

    # Aleación plateada – Paneles de armadura
    M_armor = create_pbr_material(
        "PBR_ArmorAlloy", (0.72, 0.76, 0.80), metallic=0.84, roughness=0.36, specular=0.7)

    # Fibra de carbono – Articulaciones y cuello
    M_carbon = create_pbr_material(
        "PBR_CarbonFiber", (0.028, 0.028, 0.032), metallic=0.40, roughness=0.58)

    # LED Cyan / Cian – Ojos, core de poder, puntos de emisión
    M_cyan = create_pbr_material(
        "PBR_CyanLED", (0.0, 0.88, 1.0), metallic=0.05, roughness=0.04,
        emission_color=(0.0, 0.88, 1.0), emission_strength=8.5)

    # LED Ámbar – Visor HUD, detalles de alerta
    M_amber = create_pbr_material(
        "PBR_AmberLED", (1.0, 0.44, 0.04), metallic=0.05, roughness=0.04,
        emission_color=(1.0, 0.44, 0.04), emission_strength=6.0)

    # Placa facial – Aleación de cara (más pulida)
    M_face = create_pbr_material(
        "PBR_FacePlate", (0.60, 0.66, 0.72), metallic=0.70, roughness=0.28, specular=0.8)

    # Cabello – Material orgánico-metálico estilizado
    M_hair = create_pbr_material(
        "PBR_HairStrands", (0.22, 0.14, 0.07), metallic=0.15, roughness=0.68)

    # Articulaciones oscuras
    M_joint = create_pbr_material(
        "PBR_JointDark", (0.045, 0.048, 0.055), metallic=0.58, roughness=0.48)

    # Cables naranja/rojo
    M_wire = create_pbr_material(
        "PBR_Cables", (0.88, 0.36, 0.04), metallic=0.08, roughness=0.82)

    # Suela de pie (plástico industrial)
    M_sole = create_pbr_material(
        "PBR_Sole", (0.06, 0.06, 0.07), metallic=0.20, roughness=0.72)

    # ════════════════════════════════════════════════════════════════════════
    # CONSTRUCCIÓN DEL MODELO COMPLETO (FASE 5 FINAL)
    # ════════════════════════════════════════════════════════════════════════

    # ── CABEZA ───────────────────────────────────────────────────────────────
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.46, segments=32, ring_count=24, location=(0, 0, 1.72))
    head = bpy.context.active_object
    head.name = "Head_Cranium"
    head.scale = (0.87, 0.80, 0.95)
    subsurf(head, 2)
    P(head, M_body, col)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.348, 1.68))
    fp = bpy.context.active_object
    fp.name = "Head_FacePlate"
    fp.scale = (0.43, 0.055, 0.50)
    subsurf(fp, 1)
    P(fp, M_face, col)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.372, 1.40))
    jaw = bpy.context.active_object
    jaw.name = "Head_Jaw"
    jaw.scale = (0.30, 0.022, 0.135)
    P(jaw, M_armor, col)

    # Ojos LED (con iris)
    for ex, nm in [(-0.155, "L"), (0.155, "R")]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.058, depth=0.046, vertices=24,
            location=(ex, -0.377, 1.73), rotation=(math.radians(90), 0, 0))
        P(bpy.context.active_object, M_cyan, col).name = f"Eye_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.030, depth=0.052, vertices=16,
            location=(ex, -0.388, 1.73), rotation=(math.radians(90), 0, 0))
        P(bpy.context.active_object, M_cyan, col).name = f"Eye_Iris_{nm}"
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.068, minor_radius=0.010,
            location=(ex, -0.375, 1.73), rotation=(math.radians(90), 0, 0))
        P(bpy.context.active_object, M_armor, col).name = f"Eye_Ring_{nm}"

    # Visor HUD (ámbar)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.382, 1.73))
    v = bpy.context.active_object
    v.name = "Visor_HUD"
    v.scale = (0.20, 0.020, 0.033)
    P(v, M_amber, col)

    # Panel de boca / ventilación
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.374, 1.455))
    P(bpy.context.active_object, M_carbon, col).name = "Mouth_Panel"
    bpy.context.active_object.scale = (0.22, 0.021, 0.020)

    # Sensores laterales + antenas
    for ex, nm in [(-0.465, "L"), (0.465, "R")]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.062, depth=0.065, vertices=18,
            location=(ex, 0.0, 1.72), rotation=(0, math.radians(90), 0))
        P(bpy.context.active_object, M_armor, col).name = f"Ear_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.020, depth=0.010, vertices=12,
            location=(ex * 1.065, 0.0, 1.72), rotation=(0, math.radians(90), 0))
        P(bpy.context.active_object, M_cyan, col).name = f"Ear_LED_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.012, depth=0.28, vertices=8,
            location=(ex * 0.90, 0.0, 2.06))
        P(bpy.context.active_object, M_carbon, col).name = f"Antenna_{nm}"
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.024, segments=8, ring_count=6,
            location=(ex * 0.90, 0.0, 2.21))
        P(bpy.context.active_object, M_cyan, col).name = f"Antenna_Tip_{nm}"

    # Cabello estilizado
    hair_pts = [
        (-0.24, 0.27, 1.97, 0.0), (-0.16, 0.29, 1.94, 0.0),
        (0.0, 0.31, 1.96, 0.0),   (0.16, 0.29, 1.94, 0.0),
        (0.24, 0.27, 1.97, 0.0),  (-0.38, 0.17, 1.80, -0.1),
        (-0.42, 0.09, 1.65, -0.15), (-0.40, 0.04, 1.50, -0.18),
        (0.38, 0.17, 1.80, 0.1),  (0.42, 0.09, 1.65, 0.15),
        (0.40, 0.04, 1.50, 0.18), (-0.28, 0.24, 1.50, 0.0),
        (0.28, 0.24, 1.50, 0.0),  (0.0, 0.30, 1.55, 0.0),
        (-0.15, 0.28, 1.62, 0.0), (0.15, 0.28, 1.62, 0.0),
    ]
    for i, (hx, hy, hz, rot) in enumerate(hair_pts):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.033, depth=0.17, vertices=8,
            location=(hx, hy, hz),
            rotation=(0.12 + abs(rot), 0, hx * 0.4))
        P(bpy.context.active_object, M_hair, col).name = f"Hair_{i}"

    # ── CUELLO ───────────────────────────────────────────────────────────────
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.108, depth=0.28, vertices=20, location=(0, 0, 1.22))
    P(bpy.context.active_object, M_carbon, col).name = "Neck_Core"
    for z in (1.09, 1.20, 1.31):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.122, minor_radius=0.016, location=(0, 0, z))
        P(bpy.context.active_object, M_armor, col).name = "Neck_Ring"
    for ox in [-0.06, 0.06]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.014, depth=0.20, vertices=8, location=(ox, -0.085, 1.22))
        P(bpy.context.active_object, M_carbon, col).name = "Neck_Hydraulic"

    # ── TORSO ────────────────────────────────────────────────────────────────
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.76))
    chest = bpy.context.active_object
    chest.name = "Chest"
    chest.scale = (0.57, 0.27, 0.29)
    subsurf(chest, 1)
    P(chest, M_body, col)

    for ex in [-0.285, 0.285]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, -0.262, 0.90))
        cp = bpy.context.active_object
        cp.name = "Chest_Panel"
        cp.scale = (0.175, 0.028, 0.115)
        P(cp, M_armor, col)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, -0.270, 0.90))
        P(bpy.context.active_object, M_cyan, col).name = "Chest_Panel_LED"
        bpy.context.active_object.scale = (0.165, 0.005, 0.008)

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.098, depth=0.058, vertices=32,
        location=(0, -0.264, 0.78), rotation=(math.radians(90), 0, 0))
    P(bpy.context.active_object, M_cyan, col).name = "Power_Core"
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.112, minor_radius=0.014,
        location=(0, -0.264, 0.78), rotation=(math.radians(90), 0, 0))
    P(bpy.context.active_object, M_armor, col).name = "Core_Ring"

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.43))
    waist = bpy.context.active_object
    waist.name = "Waist"
    waist.scale = (0.45, 0.23, 0.19)
    subsurf(waist, 1)
    P(waist, M_body, col)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.240, 0.50))
    P(bpy.context.active_object, M_armor, col).name = "Abdominal_Plate"
    bpy.context.active_object.scale = (0.28, 0.024, 0.21)
    for dz in [-0.06, 0.0, 0.06]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.247, 0.50 + dz))
        P(bpy.context.active_object, M_carbon, col).name = "Ab_Grill"
        bpy.context.active_object.scale = (0.25, 0.008, 0.014)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.07))
    hips = bpy.context.active_object
    hips.name = "Hips"
    hips.scale = (0.54, 0.25, 0.20)
    subsurf(hips, 1)
    P(hips, M_body, col)
    for ex in [-0.25, 0.25]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, -0.242, 0.07))
        P(bpy.context.active_object, M_armor, col).name = "Hip_Panel"
        bpy.context.active_object.scale = (0.155, 0.025, 0.145)

    # ── HOMBROS ──────────────────────────────────────────────────────────────
    for ex, nm in [(-0.70, "L"), (0.70, "R")]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.172, segments=22, ring_count=16, location=(ex, 0, 0.88))
        sh = bpy.context.active_object
        sh.name = f"Shoulder_{nm}"
        sh.scale = (1.0, 0.76, 0.76)
        subsurf(sh, 1)
        P(sh, M_armor, col)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.055, depth=0.038, vertices=16,
            location=(ex * 1.155, 0, 0.88), rotation=(0, math.radians(90), 0))
        P(bpy.context.active_object, M_cyan, col).name = f"Shoulder_LED_{nm}"

    # ── BRAZOS ───────────────────────────────────────────────────────────────
    for ex, nm in [(-0.82, "L"), (0.82, "R")]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.083, depth=0.46, vertices=18, location=(ex, 0, 0.60))
        ua = bpy.context.active_object
        ua.name = f"UpperArm_{nm}"
        subsurf(ua, 1)
        P(ua, M_body, col)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, -0.062, 0.68))
        P(bpy.context.active_object, M_armor, col).name = f"Arm_Panel_{nm}"
        bpy.context.active_object.scale = (0.055, 0.010, 0.16)

        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.090, segments=18, ring_count=12, location=(ex, 0, 0.32))
        P(bpy.context.active_object, M_joint, col).name = f"Elbow_{nm}"
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.100, minor_radius=0.017, location=(ex, 0, 0.32))
        P(bpy.context.active_object, M_armor, col).name = f"Elbow_Ring_{nm}"

        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.070, depth=0.42, vertices=16, location=(ex, 0, 0.07))
        fa = bpy.context.active_object
        fa.name = f"ForeArm_{nm}"
        subsurf(fa, 1)
        P(fa, M_body, col)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.078, minor_radius=0.015, location=(ex, 0, -0.15))
        P(bpy.context.active_object, M_armor, col).name = f"Wrist_{nm}"
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, 0, -0.27))
        hand = bpy.context.active_object
        hand.name = f"Hand_{nm}"
        hand.scale = (0.108, 0.062, 0.135)
        subsurf(hand, 1)
        P(hand, M_armor, col)
        for fi in range(3):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.016, depth=0.046, vertices=8,
                location=(ex + (fi - 1) * 0.030, -0.052, -0.335 - fi * 0.012))
            P(bpy.context.active_object, M_carbon, col).name = f"Finger_{nm}_{fi}"

    # ── PIERNAS ──────────────────────────────────────────────────────────────
    for ex, nm in [(-0.21, "L"), (0.21, "R")]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.122, depth=0.52, vertices=20, location=(ex, 0, -0.52))
        th = bpy.context.active_object
        th.name = f"Thigh_{nm}"
        subsurf(th, 1)
        P(th, M_body, col)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, -0.100, -0.46))
        P(bpy.context.active_object, M_armor, col).name = f"Thigh_Panel_{nm}"
        bpy.context.active_object.scale = (0.07, 0.012, 0.18)

        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.112, segments=18, ring_count=12, location=(ex, 0.005, -0.83))
        P(bpy.context.active_object, M_joint, col).name = f"Knee_{nm}"
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.126, minor_radius=0.017, location=(ex, 0, -0.83))
        P(bpy.context.active_object, M_armor, col).name = f"Knee_Ring_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.022, depth=0.020, vertices=12,
            location=(ex, -0.112, -0.83), rotation=(math.radians(90), 0, 0))
        P(bpy.context.active_object, M_cyan, col).name = f"Knee_LED_{nm}"

        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.096, depth=0.49, vertices=18, location=(ex, 0, -1.12))
        sh = bpy.context.active_object
        sh.name = f"Shin_{nm}"
        subsurf(sh, 1)
        P(sh, M_body, col)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, -0.086, -1.04))
        P(bpy.context.active_object, M_armor, col).name = f"Shin_Panel_{nm}"
        bpy.context.active_object.scale = (0.065, 0.010, 0.15)

        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.103, minor_radius=0.015, location=(ex, 0, -1.40))
        P(bpy.context.active_object, M_armor, col).name = f"Ankle_{nm}"
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, 0.09, -1.56))
        foot = bpy.context.active_object
        foot.name = f"Foot_{nm}"
        foot.scale = (0.122, 0.210, 0.070)
        subsurf(foot, 1)
        P(foot, M_body, col)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, 0.09, -1.632))
        sole = bpy.context.active_object
        sole.name = f"Sole_{nm}"
        sole.scale = (0.124, 0.215, 0.018)
        P(sole, M_sole, col)

    # Cables decorativos
    for cx, cy, cz, rx in [(-0.35,-0.08,0.55,0.18), (0.35,-0.08,0.55,0.18),
                             (-0.55,0.0,0.12,0.0),  (0.55,0.0,0.12,0.0)]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.010, depth=0.18, vertices=6,
            location=(cx, cy, cz), rotation=(rx, 0, 0))
        P(bpy.context.active_object, M_wire, col).name = "Cable"

    # ════════════════════════════════════════════════════════════════════════
    # ILUMINACIÓN CINEMÁTICA DE 3 PUNTOS (PBR)
    # ════════════════════════════════════════════════════════════════════════

    # Key Light (principal - luz caliente desde frente-izquierda)
    bpy.ops.object.light_add(type="SPOT", location=(1.9, -3.0, 2.4))
    key = bpy.context.active_object
    key.name = "Key_Light_Spot"
    key.data.energy = 380.0
    key.data.color = (1.0, 0.94, 0.86)           # Luz cálida dorada
    key.data.spot_size = math.radians(44)
    key.data.spot_blend = 0.35
    key.data.shadow_soft_size = 0.15
    key.rotation_euler = mathutils.Euler(
        (math.radians(60), 0, math.radians(34)), 'XYZ')
    add_to_col(key, col)

    # Fill Light (relleno suave - luz fría desde derecha)
    bpy.ops.object.light_add(type="AREA", location=(-2.8, -1.8, 0.8))
    fill = bpy.context.active_object
    fill.name = "Fill_Light_Area"
    fill.data.energy = 130.0
    fill.data.color = (0.50, 0.72, 1.0)           # Luz fría azul-cyan
    fill.data.size = 1.5
    fill.rotation_euler = mathutils.Euler(
        (math.radians(18), 0, math.radians(-30)), 'XYZ')
    add_to_col(fill, col)

    # Rim / Back Light (ciberpunk cyan desde atrás-arriba)
    bpy.ops.object.light_add(type="SPOT", location=(0.0, 3.4, 2.8))
    rim = bpy.context.active_object
    rim.name = "Rim_Back_Light"
    rim.data.energy = 520.0
    rim.data.color = (0.0, 0.88, 1.0)             # Cyan puro ciberpunk
    rim.data.spot_size = math.radians(28)
    rim.data.spot_blend = 0.20
    rim.rotation_euler = mathutils.Euler(
        (math.radians(-55), 0, 0), 'XYZ')
    add_to_col(rim, col)

    # Luz ambiente (bajo ambiente sci-fi)
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new("World_SciFi")
    scene.world.use_nodes = True
    wn = scene.world.node_tree.nodes
    wn.clear()
    bg = wn.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.008, 0.010, 0.020, 1.0)   # Oscuro azulado
    bg.inputs["Strength"].default_value = 0.5
    out_w = wn.new("ShaderNodeOutputWorld")
    scene.world.node_tree.links.new(bg.outputs["Background"], out_w.inputs["Surface"])

    # ── CÁMARA DE PRESENTACIÓN ────────────────────────────────────────────────
    bpy.ops.object.camera_add(
        location=(2.5, -4.4, 0.55),
        rotation=(math.radians(83), 0, math.radians(30)))
    cam = bpy.context.active_object
    cam.name = "Cam_Presentation"
    cam.data.lens = 54
    cam.data.clip_start = 0.1
    cam.data.clip_end = 100.0
    bpy.context.scene.camera = cam
    add_to_col(cam, col)

    # ════════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN RENDER CYCLES + OPTIX RTX 4070
    # ════════════════════════════════════════════════════════════════════════

    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        for d in prefs.get_devices_for_type("OPTIX"):
            d.use = True
        print("[+] RTX 4070 OptiX activado para render final.")
    except Exception as e:
        scene.cycles.device = "CPU"
        print(f"[*] Usando CPU: {e}")

    scene.cycles.samples = 256
    scene.cycles.use_denoising = True
    try:
        scene.cycles.denoiser = 'OPTIX'
    except Exception:
        pass
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"

    # ── RENDER FINAL 1920x1080 ───────────────────────────────────────────────
    out_final = os.path.join(OUTPUT_DIR, "phase5_render_final.png")
    scene.render.filepath = out_final
    bpy.ops.render.render(write_still=True)
    print(f"[✓] RENDER FINAL (1920×1080) guardado → {out_final}")

    # ── RENDER VISTA ILUMINACIÓN (desde arriba) ───────────────────────────────
    bpy.ops.object.camera_add(
        location=(0, 0, 6.5),
        rotation=(0, 0, 0))
    cam_top = bpy.context.active_object
    cam_top.name = "Cam_Top_LightScheme"
    add_to_col(cam_top, col)
    bpy.context.scene.camera = cam_top
    scene.cycles.samples = 64
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720

    out_lights = os.path.join(OUTPUT_DIR, "phase5_lighting_scheme.png")
    scene.render.filepath = out_lights
    bpy.ops.render.render(write_still=True)
    print(f"[✓] ESQUEMA DE ILUMINACIÓN guardado → {out_lights}")

    # Restaurar cámara de presentación para el .blend
    bpy.context.scene.camera = cam

    # ── GUARDAR ARCHIVO BLEND FINAL ───────────────────────────────────────────
    blend_final = os.path.join(OUTPUT_DIR, "robot_final_phase5.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_final)
    print(f"[✓] .blend FINAL guardado → {blend_final}")
    print("\n═══════════════════════════════════════════════")
    print("  FASE 5 COMPLETADA — Personaje Robótico Listo")
    print("═══════════════════════════════════════════════")


if __name__ == "__main__":
    build_phase5()
