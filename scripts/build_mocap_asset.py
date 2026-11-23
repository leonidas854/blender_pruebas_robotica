"""Crea copia del Viajero con cuerpo cerrado y textura de fotografía personal."""
from pathlib import Path
import sys,json,math
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from viajero_v2 import anatomy,common
import viajero_lib as g

def main():
    rig=bpy.data.objects['RIG_Viajero'];s=bpy.context.scene
    rig.animation_data_clear()
    for b in rig.pose.bones:b.rotation_mode='QUATERNION';b.rotation_quaternion=(1,0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
    # Conservar cuellos de ropa que el antiguo constructor borraría por prefijo.
    collars=[]
    for o in list(bpy.data.objects):
        if o.name.startswith('Cuello_'):
            collars.append((o,o.name));o.name='PRESERVAR_'+o.name
    original_fuse=anatomy.fuse
    def fuse(parts,name,voxel,iterations):
        for sign in (-1,1):
            for label,loc,size in [('cadera',(sign*.113,.008,.944),(.067,.078,.083)),
                                   ('hombro',(sign*.165,.004,1.443),(.065,.052,.053)),
                                   ('muneca',(sign*.461,-.003,1.124),(.024,.018,.029))]:
                o=g.sphere('Union_mocap_'+label,loc,size,bpy.data.materials['Piel'],segments=32,rings=16)
                if label=='muneca':o.rotation_euler[1]=-sign*.58
                parts.append(o)
        return original_fuse(parts,name,voxel=.0032,iterations=18)
    anatomy.fuse=fuse
    # Evitar un unwrap automático costoso; UV cilíndrica editable + proyección facial separada.
    original_bind=anatomy.bind
    def bind(obj,rig,**kw):
        if not obj.data.uv_layers:
            uv=obj.data.uv_layers.new(name='UV_Cilindrica')
            for poly in obj.data.polygons:
                for li in poly.loop_indices:
                    v=obj.data.vertices[obj.data.loops[li].vertex_index].co
                    uv.data[li].uv=((math.atan2(v.x,-v.y)+math.pi)/(2*math.pi),v.z/1.8)
        return original_bind(obj,rig,**kw)
    anatomy.bind=bind
    body=anatomy.build(rig);body.name='Mocap_Cuerpo_Cerrado'
    for obj,name in collars:obj.name=name
    print('BODY_CREATED',len(body.data.vertices),flush=True)
    # Color fotográfico en frente del rostro: imagen original, sin recorte destructivo.
    photo=bpy.data.images.load(str(ROOT/'referencias/fotografias_originales/foto_01_cuerpo_tpose.jpeg'),check_existing=True)
    photo.pack()
    material=bpy.data.materials['Piel'].copy();material.name='M_Piel_Fotografia_Personal'
    body.data.materials.clear();body.data.materials.append(material)
    uv=body.data.uv_layers.new(name='Foto_Frontal')
    mask=body.data.color_attributes.new(name='Mascara_Foto',type='FLOAT_COLOR',domain='POINT')
    for v in body.data.vertices:
        x,y,z=v.co/common.SCALE+Vector((0,0,common.LOW))
        front=max(0,min(1,(-y-.03)/.04))
        edge=max(0,min(1,(.09-abs(x))/.02))
        height=max(0,min(1,(z-1.57)/.025,(1.745-z)/.025))
        w=front*edge*height
        mask.data[v.index].color=(w,w,w,1)
    for poly in body.data.polygons:
        for li in poly.loop_indices:
            v=body.data.vertices[body.data.loops[li].vertex_index].co/common.SCALE+Vector((0,0,common.LOW))
            uv.data[li].uv=(.445+(v.x+.09)/.18*.100,1-(.402-(v.z-1.57)/.175*.086))
    nodes=material.node_tree.nodes;links=material.node_tree.links
    bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    original=bsdf.inputs['Base Color'].default_value[:]
    old=bsdf.inputs['Base Color'].links[0].from_socket if bsdf.inputs['Base Color'].is_linked else None
    tex=nodes.new('ShaderNodeTexImage');tex.image=photo;tex.label='Fotografía personal cuerpo completo'
    tex.extension='EXTEND'
    uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map=uv.name
    color=nodes.new('ShaderNodeVertexColor');color.layer_name=mask.name
    mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[1].default_value=original
    links.new(uvnode.outputs['UV'],tex.inputs['Vector']);links.new(color.outputs['Color'],mix.inputs[0])
    if old:links.new(old,mix.inputs[1])
    links.new(tex.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],bsdf.inputs['Base Color'])
    body['foto_origen']='referencias/fotografias_originales/foto_01_cuerpo_tpose.jpeg'
    body['limite_textura']='Proyección frontal localizada; laterales conservan material. No fotogrametría ni semejanza certificada.'
    s['mocap_status']='Preparado. Ejecutar blender_consumer_modal.py; prueba sintética separada.'
    s['alcance']='Mocap A, herramientas B, pruebas sintéticas; captura personal pendiente.'
    s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=720;s.render.resolution_y=960
    s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL'
    s.display.shading.show_shadows=True;s.display.shading.show_cavity=True
    s.display.shading.background_type='WORLD';s.world.color=(.12,.12,.12)
    s.view_settings.view_transform='Standard'
    # Reducir subdivisión de vista para receptor interactivo; geometría base conservada.
    for o in bpy.data.collections['PERSONAJE'].all_objects:
        for m in o.modifiers:
            if m.type=='SUBSURF':m.levels=min(m.levels,1);m.render_levels=min(m.render_levels,1)
    g.COL=bpy.data.collections['ESTUDIO']
    camera=g.camera('CAM_Mocap',(2.5,-6,1.8),(0,0,.95),2.12)
    s.camera=camera;s.render.fps=30;s.frame_start=1;s.frame_end=180
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_distance=2.8
                area.spaces.active.region_3d.view_location=(0,0,.95)
                area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
    # Text block portátil: encuentra raíz del proyecto relativa al .blend.
    text=bpy.data.texts.new('INICIAR_MOCAP.py')
    text.write("from pathlib import Path\nimport bpy, runpy\nroot=Path(bpy.data.filepath).resolve().parents[2]\nrunpy.run_path(str(root/'blender_consumer_modal.py'),run_name='__main__')\n")
    text=bpy.data.texts.new('LEEME_MOCAP')
    text.write('Ejecutar INICIAR_MOCAP.py en Scripting. Panel N > Mocap > Iniciar UDP.\nProductor externo: python mocap_producer.py\nESC detiene. Ver docs/mocap/GUIA_USO.md. La animación sintética no es captura humana.\n')
    for o in bpy.context.selected_objects:o.select_set(False)
    rig.select_set(True);bpy.context.view_layer.objects.active=rig
    s.frame_set(1);bpy.ops.file.pack_all()
    target=ROOT/'blender/mocap/robot_humanoide_mocap.blend';target.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(target))
    s.render.filepath=str(ROOT/'tmp/mocap/avatar_reposo.png');bpy.ops.render.render(write_still=True)
    # Revisión anatómica aislada, conserva las banderas al terminar.
    objects=list(bpy.data.collections['PERSONAJE'].all_objects);states={o:o.hide_render for o in objects}
    for o in objects:o.hide_render=o!=body
    s.render.filepath=str(ROOT/'tmp/mocap/anatomia_reposo.png');bpy.ops.render.render(write_still=True)
    for o,value in states.items():o.hide_render=value
    print('MOCAP_ASSET_SAVED',target,flush=True)

if __name__=='__main__':main()
