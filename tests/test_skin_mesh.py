import bpy
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))

from human_modeling.metrics import get_user_biometrics
from human_modeling.skeleton_core import create_continuous_apose_core
from human_modeling.hands_feet import create_detailed_hands_and_feet
from human_modeling.face_head import create_male_head_and_face

bpy.ops.wm.read_factory_settings(use_empty=True)
col = bpy.data.collections.new("TestCol")
bpy.context.scene.collection.children.link(col)

metrics = get_user_biometrics(BASE_DIR)
core = create_continuous_apose_core(col, None, metrics)

# Don't import the open 2D OBJ sheet into the solid join
head_parts = [p for p in create_male_head_and_face(col, None, metrics, base_dir=None)]
digit_parts = create_detailed_hands_and_feet(col, None, metrics)

all_parts = [core] + head_parts + digit_parts
for p in all_parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = core
bpy.ops.object.join()

base = bpy.context.active_object
base.data.remesh_voxel_size = 0.0085
bpy.ops.object.voxel_remesh()
print("After voxel remesh: Verts:", len(base.data.vertices))

mod_smooth = base.modifiers.new("Smooth", "SMOOTH")
mod_smooth.factor = 0.5
mod_smooth.iterations = 3
bpy.ops.object.modifier_apply(modifier="Smooth")

try:
    bpy.ops.object.quadriflow_remesh(use_mesh_symmetry=True, target_faces=9500)
    print("Quadriflow Success! Polys:", len(base.data.polygons))
except Exception as e:
    print("Quadriflow error:", e)
