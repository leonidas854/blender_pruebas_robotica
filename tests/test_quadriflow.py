import bpy

bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.4, location=(0,0,0))
c1 = bpy.context.active_object
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0,0,0.2))
s1 = bpy.context.active_object

c1.select_set(True)
s1.select_set(True)
bpy.context.view_layer.objects.active = c1
bpy.ops.object.join()

obj = bpy.context.active_object
obj.data.remesh_voxel_size = 0.015
bpy.ops.object.voxel_remesh()
print("Voxel remesh done. Verts:", len(obj.data.vertices))

try:
    bpy.ops.object.quadriflow_remesh(use_mesh_symmetry=True, target_faces=2000)
    print("Quadriflow done. Polys:", len(obj.data.polygons))
except Exception as e:
    print("Quadriflow failed or skipped:", e)
