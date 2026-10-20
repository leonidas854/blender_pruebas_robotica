import bpy
import os
import math
import mathutils

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RENDERS_DIR = os.path.join(BASE_DIR, "renders", "cuerpo_base")

bpy.ops.wm.read_factory_settings(use_empty=True)
col = bpy.data.collections.new("FusedCol")
bpy.context.scene.collection.children.link(col)

# 1. Torso en Quads
torso_rings = [
    # Anillo 0: Base del cuello (Z = 1.505)
    [(0.000, -0.052, 1.505), (0.042, -0.040, 1.505), (0.060, 0.000, 1.505), (0.042, 0.042, 1.505), (0.000, 0.050, 1.505)],
    # Anillo 1: Clavícula y hombro alto (Z = 1.440)
    [(0.000, -0.098, 1.440), (0.095, -0.082, 1.440), (0.170, -0.010, 1.440), (0.115, 0.068, 1.440), (0.000, 0.078, 1.440)],
    # Anillo 2: Pecho / Pectorales (Z = 1.370)
    [(0.000, -0.128, 1.370), (0.118, -0.118, 1.370), (0.198, -0.015, 1.370), (0.132, 0.078, 1.370), (0.000, 0.088, 1.370)],
    # Anillo 3: Caja torácica baja (Z = 1.260)
    [(0.000, -0.108, 1.260), (0.098, -0.098, 1.260), (0.165, -0.010, 1.260), (0.108, 0.068, 1.260), (0.000, 0.078, 1.260)],
    # Anillo 4: Cintura estrecha (Z = 1.150)
    [(0.000, -0.088, 1.150), (0.078, -0.078, 1.150), (0.125, 0.000, 1.150), (0.082, 0.058, 1.150), (0.000, 0.068, 1.150)],
    # Anillo 5: Caderas / Ilion (Z = 1.020)
    [(0.000, -0.095, 1.020), (0.092, -0.085, 1.020), (0.148, 0.005, 1.020), (0.102, 0.072, 1.020), (0.000, 0.085, 1.020)],
    # Anillo 6: Pelvis y Glúteos (Z = 0.880)
    [(0.000, -0.098, 0.880), (0.108, -0.078, 0.880), (0.162, 0.010, 0.880), (0.118, 0.098, 0.880), (0.000, 0.112, 0.880)],
    # Anillo 7: Entrepierna / Base pélvica (Z = 0.820)
    [(0.000, -0.068, 0.820), (0.078, -0.048, 0.820), (0.118, 0.005, 0.820), (0.078, 0.068, 0.820), (0.000, 0.082, 0.820)],
]

verts_t = []
faces_t = []
n_pts = len(torso_rings[0])
for r in torso_rings:
    for pt in r:
        verts_t.append(pt)
for r_idx in range(len(torso_rings) - 1):
    base_curr = r_idx * n_pts
    base_next = (r_idx + 1) * n_pts
    for i in range(n_pts - 1):
        faces_t.append((base_curr + i, base_curr + i + 1, base_next + i + 1, base_next + i))

mesh_torso = bpy.data.meshes.new("Torso_Mesh")
mesh_torso.from_pydata(verts_t, [], faces_t)
mesh_torso.update()
obj_torso = bpy.data.objects.new("Torso", mesh_torso)
col.objects.link(obj_torso)
mod_m = obj_torso.modifiers.new("Mirror", "MIRROR")
mod_m.use_axis[0] = True
bpy.context.view_layer.objects.active = obj_torso
obj_torso.select_set(True)
bpy.ops.object.modifier_apply(modifier="Mirror")

parts = [obj_torso]

def _part(name, mtype, loc, scale=(1,1,1), rot=(0,0,0), radius=0.05, depth=0.1):
    if mtype == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=22, ring_count=16, location=loc, rotation=rot)
    elif mtype == "cube":
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    elif mtype == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=18, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    for c in list(o.users_collection):
        c.objects.unlink(o)
    col.objects.link(o)
    parts.append(o)
    return o

# 2. Cuello y Cabeza
_part("Neck", "cylinder", (0, 0.000, 1.530), radius=0.058, depth=0.110, rot=(math.radians(6), 0, 0))
_part("Cranium", "sphere", (0, 0.010, 1.695), scale=(0.095, 0.110, 0.105), radius=1.0)
_part("Forehead", "cube", (0, -0.075, 1.710), scale=(0.105, 0.038, 0.052), rot=(math.radians(8), 0, 0))
_part("JawChin", "cube", (0, -0.055, 1.605), scale=(0.068, 0.078, 0.055), rot=(math.radians(-14), 0, 0))
_part("Nose", "cube", (0, -0.096, 1.670), scale=(0.020, 0.028, 0.040), rot=(math.radians(-18), 0, 0))

for side, sign in [("L", -1), ("R", 1)]:
    _part(f"Cheek_{side}", "sphere", (sign * 0.055, -0.055, 1.670), scale=(0.026, 0.032, 0.026), radius=1.0)
    _part(f"Ear_{side}", "cylinder", (sign * 0.090, 0.012, 1.675), radius=0.022, depth=0.012, rot=(0, math.radians(90), sign * math.radians(10)), scale=(1.3, 0.9, 1.0))

# 3. Hombros y Deltoides que unen el Torso con los Brazos
ang_rad = math.radians(26.0)
sin_a = math.sin(ang_rad)
cos_a = math.cos(ang_rad)

x_sh = 0.2215
z_sh = 1.485
l_ua = 0.298
l_fa = 0.299

x_elb = x_sh + l_ua * sin_a
z_elb = z_sh - l_ua * cos_a
x_wri = x_elb + l_fa * sin_a
z_wri = z_elb - l_fa * cos_a

for side, sign in [("L", -1), ("R", 1)]:
    # Deltoides sólido envolvente (conecta torso y brazo sin fisuras)
    _part(f"Deltoid_{side}", "sphere", (sign * (x_sh - 0.02), -0.005, z_sh), scale=(0.075, 0.075, 0.088), radius=1.0)
    # Brazo superior
    _part(f"UpperArm_{side}", "cylinder", (sign * (x_sh + l_ua*0.5*sin_a), -0.005, z_sh - l_ua*0.5*cos_a),
          radius=0.054, depth=l_ua * 1.08, rot=(0, sign * ang_rad, 0), scale=(1.05, 0.95, 1.0))
    # Codo
    _part(f"Elbow_{side}", "sphere", (sign * x_elb, -0.006, z_elb), scale=(0.048, 0.046, 0.052), radius=1.0)
    # Antebrazo
    _part(f"Forearm_{side}", "cylinder", (sign * (x_elb + l_fa*0.5*sin_a), -0.005, z_elb - l_fa*0.5*cos_a),
          radius=0.042, depth=l_fa * 1.08, rot=(0, sign * ang_rad, 0), scale=(1.08, 0.92, 1.0))
    # Muñeca y Palma
    _part(f"Palm_{side}", "cube", (sign * (x_wri + 0.025 * sin_a), -0.005, z_wri - 0.035 * cos_a),
          scale=(0.042, 0.020, 0.058), rot=(math.radians(8), sign * ang_rad, 0))

    # 5 dedos
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
        _part(f"Finger_{f_name}_{side}", "cylinder", f_loc, radius=f_rad, depth=f_len, rot=(f_rotx, sign * (ang_rad + f_rotz), 0))

# 4. Caderas y Piernas (conecta pelvis y muslo sin fisuras)
x_hip = 0.108
z_hip = 0.880
z_kne = 0.490
z_ank = 0.080
l_th = z_hip - z_kne
l_sh = z_kne - z_ank

for side, sign in [("L", -1), ("R", 1)]:
    # Articulación de cadera / glúteo
    _part(f"HipJoint_{side}", "sphere", (sign * x_hip, 0.015, z_hip), scale=(0.092, 0.095, 0.095), radius=1.0)
    # Muslo
    _part(f"Thigh_{side}", "cylinder", (sign * x_hip, -0.005, (z_hip + z_kne) / 2),
          radius=0.082, depth=l_th * 1.08, scale=(1.05, 1.08, 1.0))
    # Rodilla
    _part(f"Knee_{side}", "sphere", (sign * x_hip, -0.020, z_kne), scale=(0.058, 0.054, 0.062), radius=1.0)
    # Pantorrilla con curva de gemelos
    _part(f"Calf_{side}", "cylinder", (sign * x_hip, 0.008, (z_kne + z_ank) / 2),
          radius=0.062, depth=l_sh * 1.08, scale=(1.02, 1.15, 1.0))
    # Tobillo
    _part(f"Ankle_{side}", "sphere", (sign * x_hip, 0.005, z_ank), scale=(0.044, 0.044, 0.048), radius=1.0)
    # Pie
    _part(f"FootSole_{side}", "cube", (sign * x_hip, -0.045, z_ank * 0.38), scale=(0.046, 0.115, 0.030))
    _part(f"FootInstep_{side}", "cube", (sign * x_hip, -0.020, z_ank * 0.60), scale=(0.042, 0.080, 0.035), rot=(math.radians(-25), 0, 0))

# 5. Fusión Manifold de TODOS los volúmenes anatómicos
print(f"[*] Fusionando {len(parts)} volúmenes anatómicos continuos...")
bpy.ops.object.select_all(action='DESELECT')
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = obj_torso
bpy.ops.object.join()

body = bpy.context.active_object
body.name = "Leonidas_Cuerpo_Base_Stylized"

# 6. Voxel remesh a 6.5 mm
body.data.remesh_voxel_size = 0.0065
bpy.ops.object.voxel_remesh()
print("[✓] Voxel remesh completado. Verts:", len(body.data.vertices))

# 7. Suavizado orgánico
mod_smooth = body.modifiers.new("Smooth_Organic", "SMOOTH")
mod_smooth.factor = 0.52
mod_smooth.iterations = 4
bpy.ops.object.modifier_apply(modifier="Smooth_Organic")

# 8. QuadriFlow simétrico
bpy.ops.object.quadriflow_remesh(use_mesh_symmetry=True, target_faces=9500)
print("[✓] QuadriFlow completado. Polys:", len(body.data.polygons))

# 9. Subsurf nivel 1
mod_sub = body.modifiers.new("Subsurf", "SUBSURF")
mod_sub.levels = 1
mod_sub.render_levels = 2

# 10. Calibración métrica (1.800 m) y apoyo en suelo Z = 0.000 m
bpy.context.view_layer.update()
bbox = [mathutils.Vector(corner) for corner in body.bound_box]
min_z = min(b.z for b in bbox)
max_z = max(b.z for b in bbox)
cur_h = max_z - min_z
if cur_h > 0:
    scale_f = 1.80 / cur_h
    body.scale = (scale_f, scale_f, scale_f)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

bbox_new = [mathutils.Vector(corner) for corner in body.bound_box]
min_z_new = min(b.z for b in bbox_new)
body.location.z = -min_z_new
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

mat_clay = bpy.data.materials.new("Mat_Clay_Stylized")
mat_clay.use_nodes = True
bsdf = mat_clay.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.72, 0.74, 0.77, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.40
    bsdf.inputs["Metallic"].default_value = 0.02
body.data.materials.append(mat_clay)

for p in body.data.polygons:
    p.use_smooth = True

# Estudio y Luces
bpy.ops.mesh.primitive_plane_add(size=14.0, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Studio_Backdrop"
mat_f = bpy.data.materials.new("Mat_Studio_Floor")
mat_f.use_nodes = True
bf = mat_f.node_tree.nodes.get("Principled BSDF")
if bf:
    bf.inputs["Base Color"].default_value = (0.07, 0.08, 0.10, 1.0)
    bf.inputs["Roughness"].default_value = 0.85
floor.data.materials.append(mat_f)

lights = [
    ("Light_Key",  'AREA', (2.6, -3.2, 2.8), (0.98, 0.96, 0.92), 380.0, 1.6),
    ("Light_Fill", 'AREA', (-3.2, -2.6, 2.0), (0.75, 0.85, 1.0), 180.0, 2.2),
    ("Light_Rim",  'AREA', (0.0, 3.2, 3.1), (1.0, 0.98, 0.95), 480.0, 1.4),
]
for l_name, l_type, l_loc, l_col, l_energy, l_size in lights:
    l_data = bpy.data.lights.new(l_name, l_type)
    l_data.color = l_col
    l_data.energy = l_energy
    l_data.size = l_size
    l_obj = bpy.data.objects.new(l_name, l_data)
    l_obj.location = l_loc
    col.objects.link(l_obj)

def render_view(cam_name, loc, rot, out_file):
    cam_data = bpy.data.cameras.new(cam_name)
    cam_data.lens = 45.0
    cam_obj = bpy.data.objects.new(cam_name, cam_data)
    cam_obj.location = loc
    cam_obj.rotation_euler = rot
    col.objects.link(cam_obj)
    scene = bpy.context.scene
    scene.camera = cam_obj
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 1280
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
    scene.render.filepath = out_file
    bpy.ops.render.render(write_still=True)
    print(f"[✓] Render guardado: {out_file}")

dist = 4.2
tz = 0.90
render_view("Cam_Fused_Front", (0, -dist, tz), (math.radians(90), 0, 0), os.path.join(RENDERS_DIR, "cuerpo_base_front.png"))
render_view("Cam_Fused_34", (-dist * 0.75, -dist * 0.75, tz + 0.20), (math.radians(85), 0, math.radians(-45)), os.path.join(RENDERS_DIR, "cuerpo_base_34view.png"))

print(f"[✓] Personaje anatómico estilizado completo: {len(body.data.vertices)} vértices, {len(body.data.polygons)} quads.")
