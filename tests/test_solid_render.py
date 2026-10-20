import bpy
import os
import sys
import math
import mathutils

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RENDERS_DIR = os.path.join(BASE_DIR, "renders", "cuerpo_base")
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))

from human_modeling.metrics import get_user_biometrics
from human_modeling.skeleton_core import create_continuous_apose_core
from human_modeling.hands_feet import create_detailed_hands_and_feet
from human_modeling.face_head import create_male_head_and_face

bpy.ops.wm.read_factory_settings(use_empty=True)
col = bpy.data.collections.new("SolidCol")
bpy.context.scene.collection.children.link(col)

metrics = get_user_biometrics(BASE_DIR)

# 1. Crear el núcleo sólido continuo
core = create_continuous_apose_core(col, None, metrics)

# 2. Agregar cabeza sólida y manos/pies sólidos
head_parts = [p for p in create_male_head_and_face(col, None, metrics, base_dir=None)]
digit_parts = create_detailed_hands_and_feet(col, None, metrics)

# 3. Agregar pectorales y deltoides redondeados suaves (esferas sólidas, nunca cubos)
for side, sign in [("L", -1), ("R", 1)]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=20, ring_count=14, location=(sign * 0.088, -0.090, 1.370))
    pec = bpy.context.active_object
    pec.name = f"Pec_Soft_{side}"
    pec.scale = (0.075, 0.040, 0.055)
    pec.rotation_euler = (math.radians(-6), sign * math.radians(-8), 0)
    for c in list(pec.users_collection):
        c.objects.unlink(pec)
    col.objects.link(pec)
    head_parts.append(pec)

all_parts = [core] + head_parts + digit_parts
for p in all_parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = core
bpy.ops.object.join()

base = bpy.context.active_object
base.data.remesh_voxel_size = 0.0080
bpy.ops.object.voxel_remesh()

mod_smooth = base.modifiers.new("Smooth", "SMOOTH")
mod_smooth.factor = 0.50
mod_smooth.iterations = 3
bpy.ops.object.modifier_apply(modifier="Smooth")

bpy.ops.object.quadriflow_remesh(use_mesh_symmetry=True, target_faces=8500)

mod_sub = base.modifiers.new("Subsurf", "SUBSURF")
mod_sub.levels = 1

# Calibración a 1.80m y suelo Z=0
bpy.context.view_layer.update()
bbox = [mathutils.Vector(corner) for corner in base.bound_box]
min_z = min(b.z for b in bbox)
max_z = max(b.z for b in bbox)
cur_h = max_z - min_z
if cur_h > 0:
    scale_f = 1.80 / cur_h
    base.scale = (scale_f, scale_f, scale_f)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

bbox_new = [mathutils.Vector(corner) for corner in base.bound_box]
min_z_new = min(b.z for b in bbox_new)
base.location.z = -min_z_new
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

mat = bpy.data.materials.new("Mat_Clay")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.72, 0.74, 0.77, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.40
base.data.materials.append(mat)

for p in base.data.polygons:
    p.use_smooth = True

# Luces y render
bpy.ops.mesh.primitive_plane_add(size=14.0, location=(0, 0, 0))
floor = bpy.context.active_object
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

cam_data = bpy.data.cameras.new("Cam_Solid")
cam_data.lens = 45.0
cam_obj = bpy.data.objects.new("Cam_Solid", cam_data)
cam_obj.location = (0, -4.2, 0.90)
cam_obj.rotation_euler = (math.radians(90), 0, 0)
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
scene.render.filepath = os.path.join(RENDERS_DIR, "cuerpo_base_front.png")
bpy.ops.render.render(write_still=True)
print("[✓] Render sólido frontal guardado exitosamente!")
