import bpy
import os
import sys
import math
import mathutils

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RENDERS_DIR = os.path.join(BASE_DIR, "renders", "cuerpo_base")
os.makedirs(RENDERS_DIR, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)

col = bpy.data.collections.new("StylizedBaseCol")
bpy.context.scene.collection.children.link(col)

# 1. Torso en Quads con Mirror
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
obj_torso = bpy.data.objects.new("Character_Torso", mesh_torso)
col.objects.link(obj_torso)

mod_m = obj_torso.modifiers.new("Mirror", "MIRROR")
mod_m.use_axis[0] = True
mod_m.use_clip = True

mod_s = obj_torso.modifiers.new("Subsurf", "SUBSURF")
mod_s.levels = 1
mod_s.render_levels = 2

# 2. Extremidades superiores en Pose A (~26°)
ang_rad = math.radians(26.0)
sin_a = math.sin(ang_rad)
cos_a = math.cos(ang_rad)

# Hombro / Brazo / Antebrazo / Mano
def build_limb_tube(name, segments, col, mirror=True):
    # segments: lista de tuplas (centro, radius_x, radius_y)
    v_list = []
    f_list = []
    n_circ = 8
    for c_idx, (center, rx, ry) in enumerate(segments):
        cx, cy, cz = center
        for i in range(n_circ):
            th = 2.0 * math.pi * i / n_circ
            vx = cx + rx * math.cos(th)
            vy = cy + ry * math.sin(th)
            vz = cz
            v_list.append((vx, vy, vz))
        if c_idx > 0:
            b_prev = (c_idx - 1) * n_circ
            b_curr = c_idx * n_circ
            for i in range(n_circ):
                i_next = (i + 1) % n_circ
                f_list.append((b_prev + i, b_prev + i_next, b_curr + i_next, b_curr + i))
    m = bpy.data.meshes.new(f"{name}_Mesh")
    m.from_pydata(v_list, [], f_list)
    m.update()
    o = bpy.data.objects.new(name, m)
    col.objects.link(o)
    if mirror:
        mm = o.modifiers.new("Mirror", "MIRROR")
        mm.use_axis[0] = True
    ms = o.modifiers.new("Subsurf", "SUBSURF")
    ms.levels = 1
    ms.render_levels = 2
    for p in m.polygons:
        p.use_smooth = True
    return o

# Brazo Derecho en Pose A
x_sh = 0.2215
z_sh = 1.485
l_ua = 0.298
l_fa = 0.299

x_elb = x_sh + l_ua * sin_a
z_elb = z_sh - l_ua * cos_a
x_wri = x_elb + l_fa * sin_a
z_wri = z_elb - l_fa * cos_a

arm_segs = [
    ((x_sh - 0.02, 0.0, z_sh + 0.02), 0.068, 0.065), # Deltoides superior
    ((x_sh + 0.05 * sin_a, -0.005, z_sh - 0.05 * cos_a), 0.062, 0.058), # Bíceps alto
    (((x_sh + x_elb)/2, -0.008, (z_sh + z_elb)/2), 0.054, 0.050), # Bíceps medio
    ((x_elb, -0.005, z_elb), 0.046, 0.044), # Codo
    (((x_elb + x_wri)/2, -0.006, (z_elb + z_wri)/2), 0.044, 0.040), # Antebrazo
    ((x_wri, -0.004, z_wri), 0.035, 0.030), # Muñeca
]
obj_arm = build_limb_tube("Character_Arm", arm_segs, col)

# Pierna Derecha
x_hip = 0.108
z_hip = 0.880
z_kne = 0.490
z_ank = 0.080

leg_segs = [
    ((x_hip, -0.005, z_hip), 0.092, 0.092), # Ingle / Cadera
    ((x_hip, -0.008, (z_hip*2 + z_kne)/3), 0.082, 0.085), # Muslo alto
    ((x_hip, -0.010, (z_hip + z_kne*2)/3), 0.072, 0.075), # Muslo bajo
    ((x_hip, -0.015, z_kne), 0.058, 0.056), # Rodilla
    ((x_hip, 0.015, (z_kne*2 + z_ank)/3), 0.068, 0.072), # Gemelos (pantorrilla curva)
    ((x_hip, 0.008, (z_kne + z_ank*2)/3), 0.052, 0.054), # Pantorrilla baja
    ((x_hip, 0.002, z_ank), 0.042, 0.042), # Tobillo
    ((x_hip, 0.010, z_ank * 0.45), 0.045, 0.045), # Talón
]
obj_leg = build_limb_tube("Character_Leg", leg_segs, col)

# 3. Cabeza y Cuello anatómicos estilizados
# Cuello
neck_segs = [
    ((0, 0.002, 1.485), 0.062, 0.062),
    ((0, -0.002, 1.525), 0.056, 0.056),
    ((0, -0.005, 1.565), 0.054, 0.054),
]
obj_neck = build_limb_tube("Character_Neck", neck_segs, col, mirror=False)

# Cráneo y Facciones
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=24, ring_count=18, location=(0, 0.008, 1.690))
cranium = bpy.context.active_object
cranium.name = "Character_Cranium"
cranium.scale = (0.094, 0.108, 0.102)
for c in list(cranium.users_collection):
    c.objects.unlink(cranium)
col.objects.link(cranium)

# Mandíbula y barbilla
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.055, 1.605), rotation=(math.radians(-14), 0, 0))
jaw = bpy.context.active_object
jaw.name = "Character_Jaw"
jaw.scale = (0.065, 0.075, 0.052)
for c in list(jaw.users_collection):
    c.objects.unlink(jaw)
col.objects.link(jaw)
mod_j_s = jaw.modifiers.new("Subsurf", "SUBSURF")
mod_j_s.levels = 1

# Nariz estilizada
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.094, 1.670), rotation=(math.radians(-18), 0, 0))
nose = bpy.context.active_object
nose.name = "Character_Nose"
nose.scale = (0.018, 0.026, 0.038)
for c in list(nose.users_collection):
    c.objects.unlink(nose)
col.objects.link(nose)
mod_n_s = nose.modifiers.new("Subsurf", "SUBSURF")
mod_n_s.levels = 1

# Orejas
for side, sign in [("L", -1), ("R", 1)]:
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.024, depth=0.012, vertices=16,
        location=(sign * 0.090, 0.012, 1.675),
        rotation=(0, math.radians(90), sign * math.radians(10))
    )
    ear = bpy.context.active_object
    ear.name = f"Character_Ear_{side}"
    ear.scale = (1.3, 0.9, 1.0)
    for c in list(ear.users_collection):
        c.objects.unlink(ear)
    col.objects.link(ear)

# 4. Manos y Pies estilizados
# Manos con 5 dedos
for side, sign in [("L", -1), ("R", 1)]:
    # Palma
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(sign * (x_wri + 0.022 * sin_a), -0.005, z_wri - 0.035 * cos_a),
        rotation=(math.radians(8), sign * ang_rad, 0)
    )
    palm = bpy.context.active_object
    palm.name = f"Character_Palm_{side}"
    palm.scale = (0.042, 0.018, 0.054)
    for c in list(palm.users_collection):
        c.objects.unlink(palm)
    col.objects.link(palm)
    mod_p_s = palm.modifiers.new("Subsurf", "SUBSURF")
    mod_p_s.levels = 1

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
        bpy.ops.mesh.primitive_cylinder_add(
            radius=f_rad, depth=f_len, vertices=14,
            location=f_loc,
            rotation=(f_rotx, sign * (ang_rad + f_rotz), 0)
        )
        fin = bpy.context.active_object
        fin.name = f"Character_Finger_{f_name}_{side}"
        for c in list(fin.users_collection):
            c.objects.unlink(fin)
        col.objects.link(fin)

    # Pie (Planta y empeine)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(sign * x_hip, -0.045, z_ank * 0.40)
    )
    foot = bpy.context.active_object
    foot.name = f"Character_Foot_{side}"
    foot.scale = (0.046, 0.115, 0.030)
    for c in list(foot.users_collection):
        c.objects.unlink(foot)
    col.objects.link(foot)
    mod_f_s = foot.modifiers.new("Subsurf", "SUBSURF")
    mod_f_s.levels = 1

# Material clay para todos los objetos del cuerpo
mat_clay = bpy.data.materials.new("Mat_Clay_Character")
mat_clay.use_nodes = True
bsdf = mat_clay.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.72, 0.74, 0.77, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.40
    bsdf.inputs["Metallic"].default_value = 0.02

for o in col.objects:
    if o.type == 'MESH':
        o.data.materials.append(mat_clay)
        for p in o.data.polygons:
            p.use_smooth = True

# 5. Estudio neutro y luces
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

# 6. Renderizar vista frontal y 3/4
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
render_view("Cam_Test_Front", (0, -dist, tz), (math.radians(90), 0, 0), os.path.join(RENDERS_DIR, "cuerpo_base_front.png"))
render_view("Cam_Test_34", (-dist * 0.75, -dist * 0.75, tz + 0.20), (math.radians(85), 0, math.radians(-45)), os.path.join(RENDERS_DIR, "cuerpo_base_34view.png"))

print("Prueba completada con éxito!")
