"""
scripts/robotics_anatomy/primitives.py
Funciones utilitarias para generación y transformación de primitivos anatómicos.
"""

import bpy
import math

def add_to_collection(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

def apply_material(obj, mat):
    if obj.data and hasattr(obj.data, "materials") and mat:
        obj.data.materials.append(mat)

def shade_smooth(obj):
    if obj.type == 'MESH' and obj.data:
        for p in obj.data.polygons:
            p.use_smooth = True

def add_bevel(obj, width=0.006, segments=2):
    mod = obj.modifiers.new("Bevel", "BEVEL")
    mod.width = width
    mod.segments = segments

def make_box(name, location, scale, rotation=(0,0,0), col=None, mat=None, bevel=0.0, smooth=True):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if col:
        add_to_collection(obj, col)
    if mat:
        apply_material(obj, mat)
    if bevel > 0:
        add_bevel(obj, bevel, 2)
    if smooth:
        shade_smooth(obj)
    return obj

def make_cylinder(name, location, radius, depth, vertices=18, rotation=(0,0,0), scale=(1,1,1),
                  col=None, mat=None, smooth=True):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, vertices=vertices,
        location=location, rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if col:
        add_to_collection(obj, col)
    if mat:
        apply_material(obj, mat)
    if smooth:
        shade_smooth(obj)
    return obj

def make_sphere(name, location, radius, segments=20, ring_count=14, scale=(1,1,1),
                rotation=(0,0,0), col=None, mat=None, smooth=True):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius, segments=segments, ring_count=ring_count,
        location=location, rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if col:
        add_to_collection(obj, col)
    if mat:
        apply_material(obj, mat)
    if smooth:
        shade_smooth(obj)
    return obj

def make_wedge(name, location, scale, rotation=(0,0,0), col=None, mat=None, bevel=0.0):
    """Crea un prisma triangular / cuña anatómica."""
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    if col:
        col.objects.link(obj)

    # Vértices de una cuña triangular centrada
    # Base en Y- inferior, inclinada hacia Y+
    verts = [
        (-0.5, -0.5, -0.5), ( 0.5, -0.5, -0.5),
        ( 0.5,  0.5, -0.5), (-0.5,  0.5, -0.5),
        (-0.5, -0.5,  0.5), ( 0.5, -0.5,  0.5),
    ]
    faces = [
        (0, 1, 2, 3), # base inferior
        (0, 4, 5, 1), # cara frontal
        (1, 5, 2),    # lateral derecho
        (3, 2, 5, 4), # rampa inclinada
        (0, 3, 4),    # lateral izquierdo
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj.location = location
    obj.rotation_euler = rotation
    obj.scale = scale

    if mat:
        apply_material(obj, mat)
    if bevel > 0:
        add_bevel(obj, bevel, 2)
    shade_smooth(obj)
    return obj

def make_torus(name, location, major_radius, minor_radius, rotation=(0,0,0), col=None, mat=None):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius, minor_radius=minor_radius,
        major_segments=24, minor_segments=8,
        location=location, rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    if col:
        add_to_collection(obj, col)
    if mat:
        apply_material(obj, mat)
    shade_smooth(obj)
    return obj

def make_capsule(name, location, radius, length, vertices=16, rotation=(0,0,0), col=None, mat=None):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=length, vertices=vertices,
        location=location, rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    add_bevel(obj, width=radius * 0.45, segments=3)
    if col:
        add_to_collection(obj, col)
    if mat:
        apply_material(obj, mat)
    shade_smooth(obj)
    return obj
