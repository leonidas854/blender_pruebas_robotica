"""Validate the v2 asset without treating structural checks as artistic approval."""
import bpy
import bmesh
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]


def topology(obj):
    bm=bmesh.new();bm.from_mesh(obj.data)
    pending=set(bm.verts);sizes=[]
    while pending:
        seed=pending.pop();stack=[seed];size=0
        while stack:
            v=stack.pop();size+=1
            for edge in v.link_edges:
                other=edge.other_vert(v)
                if other in pending:pending.remove(other);stack.append(other)
        sizes.append(size)
    out={'vertices':len(bm.verts),'faces':len(bm.faces),'components':len(sizes),
         'component_sizes':sorted(sizes,reverse=True),'boundary_edges':sum(e.is_boundary for e in bm.edges),
         'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)}
    bm.free();return out


def validate():
    rig=bpy.data.objects['RIG_Viajero'];s=bpy.context.scene
    rig.animation_data.action=bpy.data.actions['01_A_pose'];s.frame_set(1)
    meshes=[o for o in bpy.data.collections['PERSONAJE'].all_objects if o.type=='MESH']
    errors=[];warn=[]
    for obj in meshes:
        if not obj.data.materials:errors.append(obj.name+': sin material')
        if not obj.data.uv_layers:errors.append(obj.name+': sin UV')
        mods=[m for m in obj.modifiers if m.type=='ARMATURE' and m.object==rig]
        if not mods:errors.append(obj.name+': sin rig')
        invalid=0
        groups={g.index:g.name for g in obj.vertex_groups}
        for v in obj.data.vertices:
            if not v.groups or abs(sum(g.weight for g in v.groups)-1)>.002:invalid+=1
            if any(groups[g.group] not in rig.data.bones for g in v.groups):invalid+=1
        if invalid:errors.append(f'{obj.name}: {invalid} pesos invalidos')
    body=bpy.data.objects['Anatomia_Esculpida'];topo=topology(body)
    if topo['components']!=1:errors.append('Anatomia desconectada')
    if topo['nonmanifold_edges']:errors.append('Anatomia no manifold')
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    points=[o.evaluated_get(dg).matrix_world@Vector(c) for o in meshes if not o.hide_render for c in o.evaluated_get(dg).bound_box]
    height=max(p.z for p in points)-min(p.z for p in points)
    if abs(height-1.8)>.012:errors.append('Altura fuera de tolerancia 12 mm')
    # Same topology remains under deformation; sample several real poses for finite coordinates.
    poses={}
    for action in ['01_A_pose','02_T_pose','05_Codos_flexionados','06_Paso_caminata','13_Presentacion','14_Prueba_codos_rodilla']:
        rig.animation_data.action=bpy.data.actions[action];s.frame_set(1);bpy.context.view_layer.update()
        dg=bpy.context.evaluated_depsgraph_get();evaluated=body.evaluated_get(dg);mesh=evaluated.to_mesh()
        finite=all(math.isfinite(c) for v in mesh.vertices for c in v.co)
        poses[action]={'finite_vertices':finite,'vertices':len(mesh.vertices)}
        if not finite:errors.append(action+': coordenadas no finitas')
        evaluated.to_mesh_clear()
    rig.animation_data.action=bpy.data.actions['01_A_pose'];s.frame_set(1)
    report={'blender':bpy.app.version_string,'height_m':height,'meshes':len(meshes),
        'vertices_total':sum(len(o.data.vertices) for o in meshes),'bones':len(rig.data.bones),
        'anatomy':topo,'pants':topology(bpy.data.objects['Pantalon_Esculpido']),
        'poses':poses,'errors':errors,'warnings':warn,'status':'PASS' if not errors else 'FAIL',
        'limits':'No certifica parecido fotografico, retopologia de produccion ni ausencia de colisiones en todas las poses. UV automaticas; sin mapas PBR horneados.',
        'render_devices':s.get('render_devices')}
    (ROOT/'docs/v2/validacion.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print(json.dumps(report,indent=2,ensure_ascii=False))
    if errors:raise RuntimeError(errors)


if __name__=='__main__':
    if bpy.app.background:bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/v2/viajero_esculpido.blend'))
    validate()
