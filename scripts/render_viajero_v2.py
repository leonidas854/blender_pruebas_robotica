"""Review views and final stills for the sculpted Viajero. Run on the v2 scene."""
import bpy
import sys
import math
import json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from viajero_v2 import scene
from viajero_v2.common import activate


def normalize_height():
    rig=bpy.data.objects['RIG_Viajero'];s=bpy.context.scene
    rig.animation_data.action=bpy.data.actions['01_A_pose'];s.frame_set(1)
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    points=[o.evaluated_get(dg).matrix_world@Vector(c) for o in bpy.data.collections['PERSONAJE'].all_objects
            if o.type=='MESH' and not o.hide_render for c in o.evaluated_get(dg).bound_box]
    low=min(p.z for p in points);height=max(p.z for p in points)-low;factor=1.8/height
    rig.scale*=factor;rig.location.z-=low*factor
    s['altura_entrega_m']=1.8


def test_pose():
    if '14_Prueba_codos_rodilla' in bpy.data.actions:return
    rig=bpy.data.objects['RIG_Viajero'];rig.animation_data.action=None
    for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0)
    for name,angle in [('forearm.L',-65),('forearm.R',-55),('thigh.L',-25),('shin.L',45)]:
        rig.pose.bones[name].rotation_euler.x=math.radians(angle)
    for b in rig.pose.bones:
        b.keyframe_insert('rotation_euler',frame=1,group=b.name)
        b.keyframe_insert('rotation_euler',frame=24,group=b.name)
    rig.animation_data.action.name='14_Prueba_codos_rodilla';rig.animation_data.action.use_fake_user=True


def main(final=False):
    normalize_height();test_pose()
    bpy.data.objects['V2_Hero'].data.lens=104
    if not final:
        for name,camera in [('revision_frente','V2_Frente'),('revision_perfil','V2_Perfil'),('revision_espalda','V2_Espalda')]:
            scene.render(ROOT,name,camera,(750,1000),24)
        scene.render(ROOT,'revision_flexion','V2_TresCuartos',(750,1000),24,'14_Prueba_codos_rodilla')
        scene.render(ROOT,'revision_rostro_perfil','V2_RostroPerfil',(700,700),32)
    else:
        for name,camera in [('frente','V2_Frente'),('perfil','V2_Perfil'),('espalda','V2_Espalda'),('tres_cuartos','V2_TresCuartos')]:
            scene.render(ROOT,name,camera,(1200,1600),64)
        scene.render(ROOT,'presentacion','V2_Hero',(1800,2400),96,'13_Presentacion')
        scene.render(ROOT,'rostro_frente','V2_RostroFrente',(1200,1200),96)
        scene.render(ROOT,'rostro_perfil','V2_RostroPerfil',(1200,1200),96)
        scene.render(ROOT,'prueba_codos_rodilla','V2_TresCuartos',(1200,1600),64,'14_Prueba_codos_rodilla')
        anatomy_evidence()
    s=bpy.context.scene;rig=bpy.data.objects['RIG_Viajero']
    rig.animation_data.action=bpy.data.actions['01_A_pose'];s.frame_set(1)
    s.camera=bpy.data.objects['V2_Hero'];s.render.resolution_x=1800;s.render.resolution_y=2400;s.cycles.samples=96
    s.render.filepath='//../../renders/v2/nuevo_render.png'
    activate(bpy.data.objects['Anatomia_Esculpida'])
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/v2/viajero_esculpido.blend'))
    evidence={'lights':[{'name':o.name,'watts':o.data.energy,'size_m':o.data.size,'position':list(o.location)} for o in bpy.data.objects if o.type=='LIGHT'],
        'cameras':{o.name:o.data.type for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('V2_')},
        'color_management':s.view_settings.view_transform,'device':s.get('render_devices'),'samples_final':96}
    (ROOT/'docs/v2/escena.json').write_text(json.dumps(evidence,indent=2))


def anatomy_evidence():
    body=bpy.data.objects['Anatomia_Esculpida'];rig=bpy.data.objects['RIG_Viajero']
    objects=[o for o in bpy.data.collections['PERSONAJE'].all_objects if o.type=='MESH']
    states={o:o.hide_render for o in objects}
    for o in objects:o.hide_render=o!=body
    clay=bpy.data.materials.new('V2_Arcilla_estudio');clay.use_nodes=True
    bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.28,.25,.20,1);bs.inputs['Roughness'].default_value=.88
    previous=body.data.materials[0];body.data.materials[0]=clay
    scene.render(ROOT,'anatomia_continua','V2_TresCuartos',(1200,1600),48)
    scene.render(ROOT,'anatomia_flexion','V2_TresCuartos',(1200,1600),48,'14_Prueba_codos_rodilla')
    body.data.materials[0]=previous
    for o,value in states.items():o.hide_render=value


if __name__=='__main__':main('--final' in sys.argv)
