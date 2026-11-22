"""Geometry utilities for the sculpt revision; design coordinates are metres."""
import bpy
import bmesh
import math
from mathutils import Vector

SCALE = .9877763687978055
LOW = .001499999314546585


def activate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def remove_prefixes(prefixes):
    for obj in list(bpy.data.objects):
        if obj.name.startswith(tuple(prefixes)):
            bpy.data.objects.remove(obj, do_unlink=True)


def bake(obj):
    activate(obj)
    if obj.type == 'CURVE':
        bpy.ops.object.convert(target='MESH')
    for mod in list(obj.modifiers):
        if mod.type != 'ARMATURE':
            bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def close_mesh(obj):
    bake(obj)
    bm = bmesh.new(); bm.from_mesh(obj.data)
    boundary = [e for e in bm.edges if e.is_boundary]
    if boundary:
        bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data); bm.free()


def fuse(parts, name, voxel=.0025, iterations=5):
    for obj in parts:
        close_mesh(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts: obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active; obj.name = name
    obj.vertex_groups.clear()
    obj.modifiers.clear()
    remesh = obj.modifiers.new('Union volumetrica para esculpir', 'REMESH')
    remesh.mode = 'VOXEL'; remesh.voxel_size = voxel
    remesh.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    smooth = obj.modifiers.new('Relajacion de superficie', 'SMOOTH')
    smooth.factor = .65; smooth.iterations = iterations
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    # Remove only tiny isolated voxel debris, never anatomical components.
    bm=bmesh.new(); bm.from_mesh(obj.data); pending=set(bm.verts); debris=[]
    while pending:
        seed=pending.pop(); stack=[seed]; component=[]
        while stack:
            v=stack.pop(); component.append(v)
            for edge in v.link_edges:
                other=edge.other_vert(v)
                if other in pending:pending.remove(other);stack.append(other)
        if len(component)<100:debris.extend(component)
    if debris:bmesh.ops.delete(bm,geom=debris,context='VERTS')
    bm.to_mesh(obj.data);bm.free()
    for face in obj.data.polygons: face.use_smooth = True
    return obj


def to_scene(obj):
    matrix = obj.matrix_world.copy()
    for v in obj.data.vertices:
        p = matrix @ v.co
        v.co = Vector((p.x, p.y, p.z - LOW)) * SCALE
    obj.matrix_world.identity()


def distance(point, bone):
    a, b = bone.head_local, bone.tail_local
    d = b-a
    t = max(0, min(1, (point-a).dot(d)/d.length_squared))
    return (point-(a+t*d)).length


def bind(obj, rig, mode='body', bone=None):
    obj.vertex_groups.clear()
    groups = {}
    for v in obj.data.vertices:
        x, y, z = v.co/SCALE + Vector((0,0,LOW))
        side = 'L' if x>0 else 'R'
        if bone: choices = [bone]
        elif mode == 'pants': choices = ['pelvis','thigh.'+side,'shin.'+side]
        elif z > 1.555: choices = ['head','neck']
        elif abs(x) > .445 and z < 1.16:
            choices = ['hand.'+side,'forearm.'+side] + [n for n in rig.data.bones.keys() if n.endswith('.'+side) and n.startswith(('index.','middle.','ring.','pinky.','thumb.'))]
        elif abs(x) > .19 and z > 1.01:
            choices = ['chest','clavicle.'+side,'upper_arm.'+side,'forearm.'+side,'hand.'+side]
        elif z < .94: choices = ['pelvis','thigh.'+side,'shin.'+side,'foot.'+side,'toe.'+side]
        else: choices = ['pelvis','spine','chest','neck']
        near = sorted((distance(v.co,rig.data.bones[n]),n) for n in choices)[:3]
        weights = [1/(d+.014)**6 for d,n in near]
        total = sum(weights)
        for (_,name),w in zip(near,weights):
            if name not in groups: groups[name] = obj.vertex_groups.new(name=name)
            groups[name].add([v.index],w/total,'REPLACE')
    mod = obj.modifiers.new('Deformacion con volumen', 'ARMATURE')
    mod.object = rig; mod.use_deform_preserve_volume = True
    obj.parent = rig
    if not obj.data.uv_layers:
        activate(obj)
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.008)
        bpy.ops.object.mode_set(mode='OBJECT')
    obj['revision'] = 'v2 - superficie moldeada, 22 noviembre 2026'
