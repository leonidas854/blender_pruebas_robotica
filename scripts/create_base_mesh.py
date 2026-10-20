#!/usr/bin/env python3
"""
scripts/create_base_mesh.py
=====================================================
ETAPA 03: Cuerpo Base Poligonal Definitivo (1.80 m, Pose A)
Genera la malla anatómica continua, estilizada y orgánica del protagonista:
  - Estructura continua en Pose A mediante Skin core y radios anatómicos calibrados.
  - Musculatura orgánica estilizada (sin placas ni formas robóticas).
  - Manos anatómicas con 5 dedos articulados en arco de reposo.
  - Pies con arco plantar, talón y dedos definidos en el suelo (Z = 0.000 m).
  - Cabeza estilizada con cráneo, mandíbula, mentón, orejas y facciones de Leonidas.
  - Fusión manifold perfecta mediante Voxel Remesh + Smooth Relaxation.
  - Retopología simétrica en quads limpios mediante QuadriFlow (~8,500 quads).
  - Modificador Subdivision Surface para acabado de animación estilizada.
  - Renders de inspección en 4 vistas (frente, lateral, espalda, 3/4).
  - Guarda en: blender/03_cuerpo_base.blend
"""

import bpy
import os
import sys
import math
import mathutils

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from human_modeling.metrics import get_user_biometrics

BLEND_DIR = os.path.join(BASE_DIR, "blender")
RENDERS_DIR = os.path.join(BASE_DIR, "renders", "cuerpo_base")
os.makedirs(RENDERS_DIR, exist_ok=True)

def create_clay_material(name="Mat_Clay_CuerpoBase"):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.72, 0.73, 0.76, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.42
        bsdf.inputs["Metallic"].default_value = 0.02
    return mat

def setup_studio_scene(master_col):
    # Ciclorama neutro
    bpy.ops.mesh.primitive_plane_add(size=14.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Studio_Backdrop"
    pres_col = bpy.data.collections.get("08_PRESENTATION")
    if not pres_col:
        pres_col = bpy.data.collections.new("08_PRESENTATION")
        master_col.children.link(pres_col)

    for c in list(floor.users_collection):
        c.objects.unlink(floor)
    pres_col.objects.link(floor)

    mat_floor = bpy.data.materials.new("Mat_Studio_Backdrop_Base")
    mat_floor.use_nodes = True
    bsdf = mat_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.07, 0.08, 0.10, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.85
    floor.data.materials.append(mat_floor)

    # Esquema de iluminación cinematográfica de 3 puntos
    lights = [
        ("Light_Key",  'AREA', (2.6, -3.2, 2.8), (0.98, 0.96, 0.92), 380.0, 1.6),
        ("Light_Fill", 'AREA', (-3.2, -2.6, 2.0), (0.75, 0.85, 1.0), 180.0, 2.2),
        ("Light_Rim",  'AREA', (0.0, 3.2, 3.1), (1.0, 0.98, 0.95), 480.0, 1.4),
    ]
    for l_name, l_type, l_loc, l_col, l_energy, l_size in lights:
        if bpy.data.objects.get(l_name):
            continue
        l_data = bpy.data.lights.new(l_name, l_type)
        l_data.color = l_col
        l_data.energy = l_energy
        l_data.size = l_size
        l_obj = bpy.data.objects.new(l_name, l_data)
        l_obj.location = l_loc
        pres_col.objects.link(l_obj)

def render_camera_view(name, location, rotation, output_file, cam_col):
    cam_obj = bpy.data.objects.get(name)
    if not cam_obj:
        cam_data = bpy.data.cameras.new(name)
        cam_data.lens = 45.0
        cam_obj = bpy.data.objects.new(name, cam_data)
        cam_col.objects.link(cam_obj)

    cam_obj.location = location
    cam_obj.rotation_euler = rotation

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
    print("  ETAPA 03: CONSTRUCCIÓN DEL CUERPO BASE DEFINITIVO (1.80m)      ")
    print("=================================================================")

    in_blend = os.path.join(BLEND_DIR, "01_referencias.blend")
    if os.path.exists(in_blend):
        bpy.ops.wm.open_mainfile(filepath=in_blend)
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

    # Limpiar cualquier objeto residual en 01_BODY
    for obj in list(body_col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # Ocultar planos de referencia en render
    ref_col = bpy.data.collections.get("00_REFERENCES")
    if ref_col:
        for obj in ref_col.all_objects:
            obj.hide_render = True

    metrics = get_user_biometrics(BASE_DIR)
    mat_clay = create_clay_material()

    t = metrics["torso"]
    a = metrics["arms"]
    l = metrics["legs"]
    h = metrics["head"]

    # 1. Crear el esqueleto continuo conectado para el Skin modifier en Pose A
    ang_rad = math.radians(26.0) # Pose A relajada
    sin_a = math.sin(ang_rad)
    cos_a = math.cos(ang_rad)

    x_sh = a["shoulder_x"]      # 0.2215
    z_sh = t["shoulder_z"]      # 1.505
    l_ua = a["upper_arm_len"]   # 0.298
    l_fa = a["forearm_len"]     # 0.299
    l_hd = a["hand_len"]        # 0.115

    x_elb = x_sh + l_ua * sin_a
    z_elb = z_sh - l_ua * cos_a
    x_wri = x_elb + l_fa * sin_a
    z_wri = z_elb - l_fa * cos_a
    x_hnd = x_wri + l_hd * sin_a
    z_hnd = z_wri - l_hd * cos_a

    x_hip = l["hip_x"]          # 0.108
    z_hip = l["hip_z"]          # 0.880
    z_kne = l["knee_z"]         # 0.490
    z_ank = l["ankle_z"]        # 0.080

    mesh = bpy.data.meshes.new("Organic_Core_Mesh")
    core_obj = bpy.data.objects.new("Organic_Core", mesh)
    body_col.objects.link(core_obj)

    verts = [
        # Columna y Cabeza (0 a 7)
        (0, 0, t["pelvis_z"]),                          # 0: Pelvis
        (0, 0.008, (t["pelvis_z"] + t["waist_z"]) / 2), # 1: Lumbar
        (0, 0.010, t["waist_z"]),                       # 2: Cintura
        (0, -0.005, (t["waist_z"] + t["chest_z"]) / 2), # 3: Tórax medio
        (0, -0.010, t["chest_z"]),                      # 4: Tórax alto / Pecho
        (0, 0.002, h["neck_base_z"]),                   # 5: Base cuello
        (0, -0.002, h["neck_top_z"]),                   # 6: Cuello alto
        (0, 0.005, h["center_z"]),                      # 7: Cráneo centro
        # Brazo Der (8 a 12)
        (x_sh * 0.45, -0.010, z_sh - 0.01),             # 8: Clavícula Der
        (x_sh, 0, z_sh),                                # 9: Hombro Der
        (x_elb, 0, z_elb),                              # 10: Codo Der
        (x_wri, 0, z_wri),                              # 11: Muñeca Der
        (x_hnd, 0, z_hnd),                              # 12: Palma Der
        # Brazo Izq (13 a 17)
        (-x_sh * 0.45, -0.010, z_sh - 0.01),            # 13: Clavícula Izq
        (-x_sh, 0, z_sh),                               # 14: Hombro Izq
        (-x_elb, 0, z_elb),                             # 15: Codo Izq
        (-x_wri, 0, z_wri),                             # 16: Muñeca Izq
        (-x_hnd, 0, z_hnd),                             # 17: Palma Izq
        # Pierna Der (18 a 22)
        (x_hip, 0, z_hip),                              # 18: Cadera Der
        (x_hip, -0.008, z_kne),                         # 19: Rodilla Der
        (x_hip, 0, z_ank),                              # 20: Tobillo Der
        (x_hip, 0.045, z_ank * 0.40),                   # 21: Talón Der
        (x_hip, -0.110, z_ank * 0.20),                  # 22: Punta pie Der
        # Pierna Izq (23 a 27)
        (-x_hip, 0, z_hip),                             # 23: Cadera Izq
        (-x_hip, -0.008, z_kne),                        # 24: Rodilla Izq
        (-x_hip, 0, z_ank),                             # 25: Tobillo Izq
        (-x_hip, 0.045, z_ank * 0.40),                  # 26: Talón Izq
        (-x_hip, -0.110, z_ank * 0.20),                 # 27: Punta pie Izq
    ]

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7),
        (5, 8), (8, 9), (9, 10), (10, 11), (11, 12),
        (5, 13), (13, 14), (14, 15), (15, 16), (16, 17),
        (0, 18), (18, 19), (19, 20), (20, 21), (20, 22),
        (0, 23), (23, 24), (24, 25), (25, 26), (25, 27),
    ]

    mesh.from_pydata(verts, edges, [])
    mesh.update()

    bpy.context.view_layer.objects.active = core_obj
    core_obj.select_set(True)
    mod_skin = core_obj.modifiers.new("Skin", "SKIN")

    # Radios anatómicos calibrados
    radii = {
        0: (0.155, 0.110),   # Pelvis
        1: (0.135, 0.098),   # Lumbar
        2: (0.125, 0.092),   # Cintura
        3: (0.165, 0.115),   # Tórax medio
        4: (0.185, 0.125),   # Tórax superior / Pectoral
        5: (0.065, 0.065),   # Base cuello
        6: (0.058, 0.058),   # Cuello alto
        7: (0.092, 0.108),   # Cráneo
        # Brazos
        8: (0.045, 0.042),   9: (0.068, 0.068),   10: (0.052, 0.050),
        11: (0.038, 0.034), 12: (0.044, 0.022),
        13: (0.045, 0.042), 14: (0.068, 0.068),  15: (0.052, 0.050),
        16: (0.038, 0.034), 17: (0.044, 0.022),
        # Piernas
        18: (0.088, 0.088), 19: (0.062, 0.062),  20: (0.045, 0.045),
        21: (0.045, 0.045), 22: (0.050, 0.028),
        23: (0.088, 0.088), 24: (0.062, 0.062),  25: (0.045, 0.045),
        26: (0.045, 0.045), 27: (0.050, 0.028),
    }

    skin_data = mesh.skin_vertices[0].data
    for idx, (rx, ry) in radii.items():
        if idx < len(skin_data):
            skin_data[idx].radius = (rx, ry)

    bpy.ops.object.modifier_apply(modifier="Skin")
    print("[✓] Núcleo continuo generado. Verts:", len(core_obj.data.vertices))

    # 2. Agregar volúmenes anatómicos orgánicos redondeados
    parts = [core_obj]

    def _add_organic_volume(name, loc, scale, rot=(0,0,0)):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=20, ring_count=14, location=loc, rotation=rot)
        o = bpy.context.active_object
        o.name = name
        o.scale = scale
        for c in list(o.users_collection):
            c.objects.unlink(o)
        body_col.objects.link(o)
        parts.append(o)
        return o

    # Pectorales suaves estilizados (esferas aplanadas, no cubos)
    for side, sign in [("L", -1), ("R", 1)]:
        _add_organic_volume(f"Pec_{side}", (sign * 0.088, -0.095, 1.370), (0.075, 0.042, 0.058), (math.radians(-6), sign * math.radians(-8), 0))
        _add_organic_volume(f"Glute_{side}", (sign * 0.085, 0.080, 0.880), (0.082, 0.078, 0.088))
        _add_organic_volume(f"Delt_{side}", (sign * (x_sh + 0.01), 0, z_sh - 0.01), (0.068, 0.068, 0.082))
        _add_organic_volume(f"Patella_{side}", (sign * x_hip, -0.048, z_kne), (0.038, 0.026, 0.042))
        _add_organic_volume(f"Calf_Gastro_{side}", (sign * x_hip, 0.025, (z_kne + z_ank) * 0.58), (0.055, 0.058, 0.095))

    # Rostro orgánico suave (frente, pómulos, mandíbula, mentón, nariz, orejas)
    _add_organic_volume("Head_Cranium_Top", (0, 0.010, h["center_z"] + 0.02), (0.092, 0.105, 0.098))
    _add_organic_volume("Head_Jaw_Chin", (0, -0.058, h["center_z"] - 0.072), (0.055, 0.058, 0.042), (math.radians(-12), 0, 0))
    _add_organic_volume("Head_Nose_Soft", (0, -0.092, h["center_z"] - 0.010), (0.016, 0.022, 0.035), (math.radians(-15), 0, 0))

    for side, sign in [("L", -1), ("R", 1)]:
        _add_organic_volume(f"Cheek_{side}", (sign * 0.054, -0.055, h["center_z"] - 0.018), (0.028, 0.034, 0.028))
        _add_organic_volume(f"Ear_Soft_{side}", (sign * 0.088, 0.012, h["center_z"] - 0.010), (0.012, 0.022, 0.032))

    # 3. Manos anatómicas con 5 dedos y pies
    for side, sign in [("L", -1), ("R", 1)]:
        _add_organic_volume(f"Palm_{side}", (sign * (x_wri + 0.025 * sin_a), -0.005, z_wri - 0.035 * cos_a),
                            (0.038, 0.018, 0.048), (math.radians(8), sign * ang_rad, 0))
        finger_specs = [
            ("Thumb",  0.018, -0.014, 0.046, 0.010, math.radians(35), math.radians(-25)),
            ("Index",  0.022, -0.004, 0.070, 0.009, math.radians(10), math.radians(5)),
            ("Middle", 0.008, -0.003, 0.078, 0.0095, math.radians(8), 0),
            ("Ring",  -0.006, -0.004, 0.070, 0.009, math.radians(9), math.radians(-4)),
            ("Pinky", -0.018, -0.005, 0.055, 0.008, math.radians(12), math.radians(-8)),
        ]
        for f_name, f_ox, f_oy, f_len, f_rad, f_rotx, f_rotz in finger_specs:
            f_loc = (
                sign * (x_wri + f_ox * cos_a + 0.045 * sin_a),
                -0.006 + f_oy,
                z_wri - 0.062 - f_len * 0.45
            )
            bpy.ops.mesh.primitive_cylinder_add(
                radius=f_rad, depth=f_len, vertices=14,
                location=f_loc,
                rotation=(f_rotx, sign * (ang_rad + f_rotz), 0)
            )
            fin = bpy.context.active_object
            fin.name = f"Finger_{f_name}_{side}"
            for c in list(fin.users_collection):
                c.objects.unlink(fin)
            body_col.objects.link(fin)
            parts.append(fin)

        _add_organic_volume(f"Foot_Heel_{side}", (sign * x_hip, 0.035, 0.035), (0.042, 0.055, 0.035))
        _add_organic_volume(f"Foot_Instep_{side}", (sign * x_hip, -0.045, 0.028), (0.046, 0.075, 0.026))

    # 4. Fusión de todos los volúmenes anatómicos
    print(f"[*] Fusionando {len(parts)} volúmenes anatómicos orgánicos...")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = core_obj
    bpy.ops.object.join()

    cuerpo_base = bpy.context.active_object
    cuerpo_base.name = "Leonidas_Cuerpo_Base_180"

    # 5. Remallado Voxel suave a 7.0 mm
    print("[*] Aplicando remallado voxel manifold (7.0 mm)...")
    cuerpo_base.data.remesh_voxel_size = 0.0070
    bpy.ops.object.voxel_remesh()
    print(f"    Vértices tras voxel remesh: {len(cuerpo_base.data.vertices)}")

    # 6. Suavizado y relajación orgánica
    print("[*] Aplicando relajación y suavizado anatómico...")
    mod_smooth = cuerpo_base.modifiers.new("Smooth_Organic", "SMOOTH")
    mod_smooth.factor = 0.55
    mod_smooth.iterations = 4
    bpy.ops.object.modifier_apply(modifier="Smooth_Organic")

    # 7. Retopología en Quads con QuadriFlow simétrico
    print("[*] Aplicando retopología QuadriFlow simétrica (target ~9,500 quads)...")
    try:
        bpy.ops.object.quadriflow_remesh(use_mesh_symmetry=True, target_faces=9500)
        print(f"[✓] QuadriFlow completado: {len(cuerpo_base.data.polygons)} polígonos (quads).")
    except Exception as e:
        print(f"[!] Aviso en Quadriflow ({e}), manteniendo malla suavizada manifold.")

    # 8. Modificador de subdivisión para acabado cinematográfico
    mod_sub = cuerpo_base.modifiers.new("Subsurf", "SUBSURF")
    mod_sub.levels = 1
    mod_sub.render_levels = 2

    # 9. Calibración métrica exacta (1.800 m) y apoyo en suelo (Z = 0.000 m)
    bpy.context.view_layer.update()
    bbox = [mathutils.Vector(corner) for corner in cuerpo_base.bound_box]
    min_z = min(b.z for b in bbox)
    max_z = max(b.z for b in bbox)
    cur_h = max_z - min_z
    if cur_h > 0:
        scale_f = 1.80 / cur_h
        cuerpo_base.scale = (scale_f, scale_f, scale_f)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bbox_new = [mathutils.Vector(corner) for corner in cuerpo_base.bound_box]
    min_z_new = min(b.z for b in bbox_new)
    cuerpo_base.location.z = -min_z_new
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    if mat_clay:
        cuerpo_base.data.materials.clear()
        cuerpo_base.data.materials.append(mat_clay)

    for p in cuerpo_base.data.polygons:
        p.use_smooth = True

    print(f"[✓] Malla final del cuerpo base: {len(cuerpo_base.data.vertices)} vértices, {len(cuerpo_base.data.polygons)} caras.")

    # 10. Configuración de estudio y cámaras
    setup_studio_scene(master_col)

    cam_col = bpy.data.collections.get("06_CAMERAS")
    if not cam_col:
        cam_col = bpy.data.collections.new("06_CAMERAS")
        master_col.children.link(cam_col)

    print("\n[*] Renderizando 4 vistas del cuerpo base continuo...")
    dist = 4.2
    tz = 0.90
    render_camera_view("Cam_Blockout_Front", (0, -dist, tz), (math.radians(90), 0, 0),
                       os.path.join(RENDERS_DIR, "cuerpo_base_front.png"), cam_col)
    render_camera_view("Cam_Blockout_Side", (-dist, 0, tz), (math.radians(90), 0, math.radians(-90)),
                       os.path.join(RENDERS_DIR, "cuerpo_base_side.png"), cam_col)
    render_camera_view("Cam_Blockout_Back", (0, dist, tz), (math.radians(90), 0, math.radians(180)),
                       os.path.join(RENDERS_DIR, "cuerpo_base_back.png"), cam_col)
    render_camera_view("Cam_Blockout_34", (-dist * 0.75, -dist * 0.75, tz + 0.20),
                       (math.radians(85), 0, math.radians(-45)),
                       os.path.join(RENDERS_DIR, "cuerpo_base_34view.png"), cam_col)

    # 11. Guardar escena 03_cuerpo_base.blend
    out_blend = os.path.join(BLEND_DIR, "03_cuerpo_base.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)

    print(f"\n[✓] Escena 03_cuerpo_base.blend guardada con éxito en: {out_blend}")
    print("=================================================================")

if __name__ == "__main__":
    main()
