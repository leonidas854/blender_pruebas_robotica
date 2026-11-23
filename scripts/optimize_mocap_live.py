"""Copia ligera con pesos y fotografía; conserva la escena detallada."""
from pathlib import Path
import sys,json
import bpy,bmesh
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.agents/skills/blender-asset-qa/scripts'),str(ROOT/'scripts')]
from verify_mocap_blender import topology
import qa_check
objects=[o for o in bpy.data.collections['PERSONAJE'].all_objects if o.type=='MESH']
before=after=0
for obj in objects:
    obj.data.calc_loop_triangles();n=len(obj.data.loop_triangles);before+=n
    for mod in obj.modifiers:
        if mod.type=='SUBSURF':mod.show_viewport=False;mod.show_render=False
    if n>1000:
        if obj.data.shape_keys:obj.shape_key_clear()
        bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj
        mod=obj.modifiers.new('Reduccion para captura','DECIMATE');mod.ratio=.2 if obj.name=='Mocap_Cuerpo_Cerrado' else .35
        bpy.ops.object.modifier_move_to_index(modifier=mod.name,index=0)
        bpy.ops.object.modifier_apply(modifier=mod.name)
        # Decimation interpola grupos: normalizar pesos por vértice tras reducción.
        for v in obj.data.vertices:
            total=sum(g.weight for g in v.groups)
            if total>0 and abs(total-1)>1e-6:
                for g in list(v.groups):obj.vertex_groups[g.group].add([v.index],g.weight/total,'REPLACE')
    obj.data.calc_loop_triangles();after+=len(obj.data.loop_triangles)
body=bpy.data.objects['Mocap_Cuerpo_Cerrado'];top=topology(body)
report=dict(before_triangles=before,after_triangles=after,body=top,
            changes='Decimación aplicada antes de Armature; Subsurf desactivado; shape keys sólo conservadas en versión detallada',
            errors=[])
if top['nonmanifold_edges'] or top['components']!=1:report['errors'].append('Topología del cuerpo')
rig=bpy.data.objects['RIG_Viajero'];rig.select_set(True);bpy.context.view_layer.objects.active=rig
scene=bpy.context.scene;scene['variant']='LIGERO para captura; detallado conservado en archivo separado'
scene.display.shading.show_shadows=False
scene.render.filepath=str(ROOT/'tmp/mocap/avatar_ligero.png');bpy.ops.render.render(write_still=True)
bpy.context.preferences.filepaths.save_version=0
path=ROOT/'blender/mocap/robot_humanoide_mocap_ligero.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(path))
(ROOT/'docs/mocap/validation_lite.json').write_text(json.dumps(report,indent=2),encoding='utf8')
# Topología/pesos/materiales en perfil render; comparar imagen antes de entregar.
qa=qa_check.run(objects=[o.name for o in objects],profile='render',max_tris=300000,no_modifiers=True)
(ROOT/'docs/mocap/asset_qa_lite.json').write_text(json.dumps(qa,indent=2),encoding='utf8')
print(json.dumps(report),qa['pass'],qa['errors'])
if report['errors'] or qa['errors']:raise RuntimeError('Revisar variante ligera')
