#!/usr/bin/env python3
"""
scripts/create_body_blockout.py
=====================================================
ETAPA 02: Blockout Anatómico Humano (1.80 m, Pose A)
Genera el bloqueo anatómico editable del cuerpo masculino estilizado (7.7 cabezas).
Volúmenes orgánicos con modificador Mirror y Subsurf para siluetas limpias.
Genera renders en 4 vistas: Frente, Lateral, Espalda y 3/4.
Guarda en: blender/02_blockout.blend
"""

import bpy
import os
import math

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BLEND_DIR = os.path.join(BASE_DIR, "blender")
RENDERS_DIR = os.path.join(BASE_DIR, "renders", "cuerpo_base")
os.makedirs(RENDERS_DIR, exist_ok=True)

# Métricas canónicas calibradas (Leonidas 1.80m, 7.7 cabezas)
METRICS = {
    "total_height": 1.80,
    "head": {
        "top_z": 1.800,
        "center_z": 1.685,
        "chin_z": 1.566,
        "width": 0.165,
        "depth": 0.205,
        "neck_top_z": 1.560,
        "neck_base_z": 1.485,
        "neck_radius": 0.058,
    },
    "torso": {
        "shoulder_z": 1.505,
        "chest_z": 1.370,
        "waist_z": 1.150,
        "pelvis_z": 0.880,
        "shoulder_width": 0.443,
        "chest_width": 0.390,
        "chest_depth": 0.250,
        "waist_width": 0.245,
        "waist_depth": 0.180,
        "pelvis_width": 0.320,
        "pelvis_depth": 0.220,
    },
    "arms": {
        "shoulder_x": 0.2215,
        "apose_angle_deg": 28.0,
        "upper_arm_len": 0.300,
        "forearm_len": 0.290,
        "bicep_radius": 0.052,
        "wrist_radius": 0.035,
    },
    "legs": {
        "hip_x": 0.108,
        "hip_z": 0.880,
        "knee_z": 0.490,
        "ankle_z": 0.080,
        "thigh_radius": 0.082,
        "knee_radius": 0.058,
        "calf_radius": 0.065,
        "ankle_radius": 0.042,
        "foot_len": 0.250,
        "foot_width": 0.095,
        "foot_height": 0.075,
    }
}

def create_clay_material(name="Mat_Clay_Blockout"):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.68, 0.69, 0.72, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.40
        bsdf.inputs["Metallic"].default_value = 0.02
    return mat

def create_subdivided_primitive(name, mesh_type, location, scale=(1,1,1), rotation=(0,0,0), radius=0.05, depth=0.1, col=None, mat=None, mirror=False):
    if mesh_type == "cube":
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    elif mesh_type == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=24, ring_count=16, location=location, rotation=rotation)
    elif mesh_type == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=20, location=location, rotation=rotation)

    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale

    if mirror:
        mod_m = obj.modifiers.new("Mirror", "MIRROR")
        mod_m.use_axis[0] = True

    mod_s = obj.modifiers.new("Subsurf", "SUBSURF")
    mod_s.levels = 1
    mod_s.render_levels = 2

    if col:
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        col.objects.link(obj)

    if mat:
        obj.data.materials.append(mat)

    for p in obj.data.polygons:
        p.use_smooth = True

    return obj

def build_torso_and_spine(col, mat):
    t = METRICS["torso"]
    parts = []

    # 1. Caja Torácica / Pecho
    ribcage = create_subdivided_primitive(
        "Blockout_Ribcage", "cube",
        location=(0, -0.010, t["chest_z"]),
        scale=(t["chest_width"] * 0.48, t["chest_depth"] * 0.46, 0.165),
        col=col, mat=mat
    )
    parts.append(ribcage)

    # 2. Pectorales (contorno estilizado)
    for side, sign in [("R", 1), ("L", -1)]:
        pec = create_subdivided_primitive(
            f"Blockout_Pectoral_{side}", "sphere",
            location=(sign * (t["chest_width"] * 0.22), -t["chest_depth"] * 0.42, t["chest_z"] + 0.02),
            radius=0.065, scale=(1.25, 0.70, 0.95),
            rotation=(math.radians(-8), sign * math.radians(-5), 0),
            col=col, mat=mat
        )
        parts.append(pec)

    # 3. Abdomen y Cintura (estrechamiento atlético)
    abs_core = create_subdivided_primitive(
        "Blockout_Abdomen", "cube",
        location=(0, 0.005, t["waist_z"]),
        scale=(t["waist_width"] * 0.46, t["waist_depth"] * 0.44, 0.110),
        col=col, mat=mat
    )
    parts.append(abs_core)

    # 4. Pelvis y Glúteos (con curvatura posterior natural)
    pelvis = create_subdivided_primitive(
        "Blockout_Pelvis", "cube",
        location=(0, 0.015, t["pelvis_z"] + 0.04),
        scale=(t["pelvis_width"] * 0.47, t["pelvis_depth"] * 0.46, 0.115),
        col=col, mat=mat
    )
    parts.append(pelvis)

    for side, sign in [("R", 1), ("L", -1)]:
        glute = create_subdivided_primitive(
            f"Blockout_Gluteus_{side}", "sphere",
            location=(sign * (t["pelvis_width"] * 0.22), 0.055, t["pelvis_z"] + 0.03),
            radius=0.075, scale=(1.10, 1.25, 1.15),
            col=col, mat=mat
        )
        parts.append(glute)

    return parts

def build_head_neck(col, mat):
    h = METRICS["head"]
    parts = []

    # Cuello estilizado inclinado 7 grados
    neck = create_subdivided_primitive(
        "Blockout_Neck", "cylinder",
        location=(0, -0.005, (h["neck_base_z"] + h["neck_top_z"]) / 2.0),
        radius=h["neck_radius"], depth=h["neck_top_z"] - h["neck_base_z"] + 0.02,
        rotation=(math.radians(7), 0, 0),
        scale=(0.95, 1.05, 1.0),
        col=col, mat=mat
    )
    parts.append(neck)

    # Bóveda craneal
    cranium = create_subdivided_primitive(
        "Blockout_Cranium", "sphere",
        location=(0, 0.015, h["center_z"] + 0.02),
        radius=0.092, scale=(h["width"] / 0.18, h["depth"] / 0.18, 1.15),
        col=col, mat=mat
    )
    parts.append(cranium)

    # Mandíbula y barbilla
    jaw = create_subdivided_primitive(
        "Blockout_JawChin", "cube",
        location=(0, -0.045, h["chin_z"] + 0.035),
        scale=(0.065, 0.075, 0.055),
        rotation=(math.radians(-14), 0, 0),
        col=col, mat=mat
    )
    parts.append(jaw)

    # Nariz estilizada
    nose = create_subdivided_primitive(
        "Blockout_Nose", "cube",
        location=(0, -0.098, h["chin_z"] + 0.078),
        scale=(0.016, 0.024, 0.034),
        rotation=(math.radians(-18), 0, 0),
        col=col, mat=mat
    )
    parts.append(nose)

    return parts

def build_arms_pose_a(col, mat):
    a = METRICS["arms"]
    t = METRICS["torso"]
    parts = []

    ang_rad = math.radians(a["apose_angle_deg"])
    sin_a = math.sin(ang_rad)
    cos_a = math.cos(ang_rad)

    x_sh = a["shoulder_x"]
    z_sh = t["shoulder_z"]

    for side, sign in [("R", 1), ("L", -1)]:
        # 1. Deltoides (hombro)
        delt = create_subdivided_primitive(
            f"Blockout_Deltoid_{side}", "sphere",
            location=(sign * (x_sh + 0.015), 0, z_sh - 0.015),
            radius=0.072, scale=(1.05, 1.15, 1.20),
            col=col, mat=mat
        )
        parts.append(delt)

        # 2. Brazo superior (Bíceps/Tríceps) orientado en Pose A
        ua_mid = a["upper_arm_len"] * 0.50
        ua_x = sign * (x_sh + ua_mid * sin_a)
        ua_z = z_sh - ua_mid * cos_a
        upper_arm = create_subdivided_primitive(
            f"Blockout_UpperArm_{side}", "cylinder",
            location=(ua_x, -0.005, ua_z),
            radius=a["bicep_radius"], depth=a["upper_arm_len"] * 0.90,
            rotation=(0, sign * ang_rad, 0),
            scale=(1.10, 0.95, 1.0),
            col=col, mat=mat
        )
        parts.append(upper_arm)

        # 3. Antebrazo
        elb_x = sign * (x_sh + a["upper_arm_len"] * sin_a)
        elb_z = z_sh - a["upper_arm_len"] * cos_a
        fa_mid = a["forearm_len"] * 0.50
        fa_x = elb_x + sign * (fa_mid * sin_a)
        fa_z = elb_z - fa_mid * cos_a
        forearm = create_subdivided_primitive(
            f"Blockout_Forearm_{side}", "cylinder",
            location=(fa_x, -0.005, fa_z),
            radius=a["wrist_radius"] * 1.18, depth=a["forearm_len"] * 0.90,
            rotation=(0, sign * ang_rad, 0),
            scale=(1.12, 0.92, 1.0),
            col=col, mat=mat
        )
        parts.append(forearm)

        # 4. Mano en reposo (curvada hacia adentro/atrás)
        hnd_x = elb_x + sign * (a["forearm_len"] * sin_a)
        hnd_z = elb_z - a["forearm_len"] * cos_a
        hand = create_subdivided_primitive(
            f"Blockout_Hand_{side}", "cube",
            location=(hnd_x + sign * 0.035 * sin_a, -0.008, hnd_z - 0.035 * cos_a),
            scale=(0.045, 0.022, 0.075),
            rotation=(math.radians(10), sign * (ang_rad + math.radians(5)), sign * math.radians(-10)),
            col=col, mat=mat
        )
        parts.append(hand)

    return parts

def build_legs_and_feet(col, mat):
    l = METRICS["legs"]
    parts = []

    x_hip = l["hip_x"]
    z_hip = l["hip_z"]
    z_kne = l["knee_z"]
    z_ank = l["ankle_z"]

    thigh_len = z_hip - z_kne
    thigh_mid_z = (z_hip + z_kne) / 2.0
    calf_len = z_kne - z_ank
    calf_mid_z = (z_kne + z_ank) / 2.0

    for side, sign in [("R", 1), ("L", -1)]:
        # 1. Muslo (Cuádriceps)
        thigh = create_subdivided_primitive(
            f"Blockout_Thigh_{side}", "cylinder",
            location=(sign * x_hip, -0.008, thigh_mid_z),
            radius=l["thigh_radius"], depth=thigh_len * 0.92,
            scale=(1.05, 1.08, 1.0),
            col=col, mat=mat
        )
        parts.append(thigh)

        # 2. Rodilla (Rótula)
        knee = create_subdivided_primitive(
            f"Blockout_Knee_{side}", "sphere",
            location=(sign * x_hip, -0.038, z_kne),
            radius=l["knee_radius"] * 0.75, scale=(1.0, 0.9, 1.2),
            col=col, mat=mat
        )
        parts.append(knee)

        # 3. Pantorrilla (Gemelos)
        calf = create_subdivided_primitive(
            f"Blockout_Calf_{side}", "cylinder",
            location=(sign * x_hip, 0.010, calf_mid_z),
            radius=l["calf_radius"], depth=calf_len * 0.92,
            scale=(1.02, 1.15, 1.0),
            col=col, mat=mat
        )
        parts.append(calf)

        # 4. Pie (Talón a puntera en Z=0)
        foot = create_subdivided_primitive(
            f"Blockout_Foot_{side}", "cube",
            location=(sign * x_hip, -0.045, z_ank * 0.45),
            scale=(l["foot_width"] * 0.46, l["foot_len"] * 0.46, l["foot_height"] * 0.45),
            col=col, mat=mat
        )
        parts.append(foot)

    return parts

def setup_blockout_studio(col):
    # Ciclorama de estudio neutro
    bpy.ops.mesh.primitive_plane_add(size=14.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Studio_Backdrop"
    for c in list(floor.users_collection):
        c.objects.unlink(floor)
    col.objects.link(floor)

    mat_floor = bpy.data.materials.new("Mat_Studio_Backdrop")
    mat_floor.use_nodes = True
    bsdf = mat_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.08, 0.09, 0.11, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.85
    floor.data.materials.append(mat_floor)

    # Luces de 3 puntos
    lights = [
        ("Light_Key", 'AREA', (2.5, -3.2, 2.8), (0.98, 0.96, 0.92), 350.0, 1.5),
        ("Light_Fill", 'AREA', (-3.0, -2.8, 2.0), (0.75, 0.85, 1.0), 160.0, 2.0),
        ("Light_Rim", 'AREA', (0.0, 3.2, 3.0), (1.0, 0.98, 0.95), 450.0, 1.2),
    ]
    for l_name, l_type, l_loc, l_col, l_energy, l_size in lights:
        l_data = bpy.data.lights.new(l_name, l_type)
        l_data.color = l_col
        l_data.energy = l_energy
        l_data.size = l_size
        l_obj = bpy.data.objects.new(l_name, l_data)
        l_obj.location = l_loc
        col.objects.link(l_obj)

def render_camera_view(name, location, rotation, output_file, col):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = 45.0
    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = location
    cam_obj.rotation_euler = rotation
    col.objects.link(cam_obj)

    scene = bpy.context.scene
    scene.camera = cam_obj
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 1280
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = output_file

    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.device = 'GPU'
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'OPTIX'
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
    except Exception:
        pass
    scene.cycles.samples = 64

    bpy.ops.render.render(write_still=True)
    print(f"[✓] Render guardado: {output_file}")

def main():
    print("=================================================================")
    print("  ETAPA 02: GENERACIÓN DEL BLOCKOUT ANATÓMICO (1.80m, POSE A)   ")
    print("=================================================================")

    # Cargar 01_referencias.blend
    blend_ref_path = os.path.join(BLEND_DIR, "01_referencias.blend")
    if os.path.exists(blend_ref_path):
        bpy.ops.wm.open_mainfile(filepath=blend_ref_path)
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)

    master_col = bpy.data.collections.get("CH_VIAJERO")
    if not master_col:
        master_col = bpy.data.collections.new("CH_VIAJERO")
        bpy.context.scene.collection.children.link(master_col)

    body_col = bpy.data.collections.get("01_BODY")
    if not body_col:
        body_col = bpy.data.collections.new("01_BODY")
        master_col.children.link(body_col)

    mat_clay = create_clay_material()

    # Construir volúmenes
    print("\n[*] Construyendo volúmenes del torso y pelvis...")
    build_torso_and_spine(body_col, mat_clay)

    print("[*] Construyendo cabeza y cuello...")
    build_head_neck(body_col, mat_clay)

    print("[*] Construyendo extremidades superiores en Pose A (~28°)...")
    build_arms_pose_a(body_col, mat_clay)

    print("[*] Construyendo extremidades inferiores y pies...")
    build_legs_and_feet(body_col, mat_clay)

    # Configuración de estudio para renders
    pres_col = bpy.data.collections.get("08_PRESENTATION")
    if not pres_col:
        pres_col = bpy.data.collections.new("08_PRESENTATION")
        master_col.children.link(pres_col)

    setup_blockout_studio(pres_col)

    # Renders de 4 vistas (frente, lateral, espalda, 3/4)
    cam_col = bpy.data.collections.get("06_CAMERAS")
    if not cam_col:
        cam_col = bpy.data.collections.new("06_CAMERAS")
        master_col.children.link(cam_col)

    # Asegurar que las referencias no se rendericen en las vistas de inspección
    ref_col = bpy.data.collections.get("00_REFERENCES")
    if ref_col:
        for obj in ref_col.all_objects:
            obj.hide_render = True

    print("\n[*] Generando renders en 4 vistas...")
    dist = 4.2
    tz = 0.90
    render_camera_view("Cam_Blockout_Front", (0, -dist, tz), (math.radians(90), 0, 0),
                       os.path.join(RENDERS_DIR, "blockout_front.png"), cam_col)
    render_camera_view("Cam_Blockout_Side", (-dist, 0, tz), (math.radians(90), 0, math.radians(-90)),
                       os.path.join(RENDERS_DIR, "blockout_side.png"), cam_col)
    render_camera_view("Cam_Blockout_Back", (0, dist, tz), (math.radians(90), 0, math.radians(180)),
                       os.path.join(RENDERS_DIR, "blockout_back.png"), cam_col)
    render_camera_view("Cam_Blockout_34", (-dist * 0.75, -dist * 0.75, tz + 0.20),
                       (math.radians(85), 0, math.radians(-45)),
                       os.path.join(RENDERS_DIR, "blockout_34view.png"), cam_col)

    # Guardar 02_blockout.blend
    out_blend = os.path.join(BLEND_DIR, "02_blockout.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)

    print(f"\n[✓] Escena 02_blockout.blend guardada con éxito en: {out_blend}")
    print("=================================================================")

if __name__ == "__main__":
    main()
