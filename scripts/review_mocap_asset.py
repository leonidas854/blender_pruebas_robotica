"""QA y vistas reproducibles de la copia de entrega, sin modificar el original."""
from pathlib import Path
import sys,json
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.agents/skills/blender-asset-qa/scripts')]
import qa_check

s=bpy.context.scene;body=bpy.data.objects['Mocap_Cuerpo_Cerrado']
objects=[o for o in bpy.data.collections['PERSONAJE'].all_objects if o.type=='MESH']
report=qa_check.run(objects=[o.name for o in objects],profile='render',max_tris=300000,no_modifiers=True)
(ROOT/'docs/mocap/asset_qa.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('QA',report['pass'],report['errors'],flush=True)
# Material lighting. Workbench cannot show masked node textures.
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32
s.view_settings.view_transform='AgX';s.render.resolution_x=600;s.render.resolution_y=750
s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for o in bpy.data.objects:
    if o.type=='LIGHT':o.hide_render=True
world=bpy.data.worlds.new('Mocap_Revision_World');world.use_nodes=True;s.world=world
world.node_tree.nodes.get('Background').inputs[0].default_value=(.22,.24,.28,1)
world.node_tree.nodes.get('Background').inputs[1].default_value=.5
for name,loc,power,size in [('Mocap_Key',(-2,-4,4),450,3),('Mocap_Fill',(3,-2,3),230,3)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(name,data);s.collection.objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector((0,0,1.5))-ob.location).to_track_quat('-Z','Y').to_euler()
s.camera=bpy.data.objects['CAM_Mocap']
s.render.filepath=str(ROOT/'tmp/mocap/avatar_material.png');bpy.ops.render.render(write_still=True)
cam=s.camera;cam.location=(0,-3,1.65);cam.rotation_euler=(Vector((0,0,1.65))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.ortho_scale=.4
s.render.resolution_x=650;s.render.resolution_y=650
s.render.filepath=str(ROOT/'tmp/mocap/rostro_fotografico.png');bpy.ops.render.render(write_still=True)
# Wire overlay over anatomical surface for actual topology inspection.
states={o:o.hide_render for o in objects}
for o in objects:o.hide_render=o!=body
s.render.engine='BLENDER_WORKBENCH';s.display.shading.show_shadows=False
s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.52,.59,.65)
cam.location=(2.5,-6,1.8);cam.rotation_euler=(Vector((0,0,.95))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.12
s.render.resolution_x=720;s.render.resolution_y=960
# Wireframe modifier on a temporary copy; original mesh remains closed.
wire=body.copy();wire.data=body.data.copy();s.collection.objects.link(wire);wire.name='QA_Wire_Only'
wire.modifiers.clear();wire.shape_key_clear();wire.hide_render=False
mod=wire.modifiers.new('QA topology','WIREFRAME');mod.thickness=.0001;mod.use_replace=True
body.hide_render=True
s.render.filepath=str(ROOT/'tmp/mocap/anatomia_wire.png');bpy.ops.render.render(write_still=True)
print('REVIEW_RENDERED',flush=True)
