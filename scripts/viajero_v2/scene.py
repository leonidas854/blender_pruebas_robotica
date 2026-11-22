"""Native material tuning and consistent photographic studio views."""
import bpy
from mathutils import Vector
import viajero_lib as g


def setup():
    factors={'Abrigo':.47,'Pantalon':.34,'Bufanda':.34,'Cuero':.48,'Cuero_borde':.52,
        'Chaleco':.45,'Camisa':.78,'Cabello':.24,'Mechon_luz':.22,'Piel':.72,'Labios':.65}
    for name,factor in factors.items():
        mat=bpy.data.materials.get(name)
        if not mat:continue
        mat.diffuse_color=tuple(c*factor for c in mat.diffuse_color[:3])+(1,)
        for node in mat.node_tree.nodes:
            if node.type=='BSDF_PRINCIPLED':
                color=node.inputs['Base Color'].default_value
                node.inputs['Base Color'].default_value=tuple(c*factor for c in color[:3])+(1,)
                if name in ['Cabello','Mechon_luz']:
                    node.inputs['Roughness'].default_value=.78
                    node.inputs['Specular IOR Level'].default_value=.20
                if name in ['Cuero','Cuero_borde','Chaleco']:node.inputs['Roughness'].default_value=.67
                if name=='Piel':
                    node.inputs['Roughness'].default_value=.53
                    node.inputs['Subsurface Weight'].default_value=.045
            elif node.type=='VALTORGB':
                for el in node.color_ramp.elements:el.color=tuple(c*factor for c in el.color[:3])+(1,)
            elif node.type=='BUMP':node.inputs['Strength'].default_value=.10
    # Black pupils and dark irises remain readable beneath round brass spectacles.
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    gpu=[d for d in prefs.devices if d.type=='OPTIX']
    for d in prefs.devices:d.use=d in gpu
    s.cycles.device='GPU' if gpu else 'CPU'
    s['render_devices']=str([(d.name,d.type) for d in gpu])
    s.view_settings.view_transform='AgX';s.view_settings.exposure=0
    world=bpy.data.worlds.new('V2_Ambiente');world.use_nodes=True;s.world=world
    world.node_tree.nodes.get('Background').inputs[0].default_value=(.28,.32,.38,1)
    world.node_tree.nodes.get('Background').inputs[1].default_value=.22
    for obj in list(bpy.data.objects):
        if obj.type=='LIGHT':bpy.data.objects.remove(obj,do_unlink=True)
    g.COL=bpy.data.collections['ESTUDIO']
    for name,loc,power,size,color in [
        ('V2_Key',(-2.4,-3.2,3.7),340,2.5,(1,.89,.78)),
        ('V2_Fill',(2.8,-2,2.1),150,3,(.80,.88,1)),
        ('V2_Rim',(.6,1.8,2.7),230,2,(1,.87,.72))]:
        d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
        o=bpy.data.objects.new(name,d);g.COL.objects.link(o);o.location=loc
        o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
    floor=bpy.data.objects.get('Suelo')
    if floor:
        mat=g.material('V2_Fondo_piedra',(.12,.105,.085),.91);floor.data.materials.clear();floor.data.materials.append(mat)
    for name,loc,target,scale in [
        ('V2_Frente',(0,-6,.95),(0,0,.95),2.06),
        ('V2_Perfil',(-6,0,.95),(0,0,.95),2.06),
        ('V2_Espalda',(0,6,.95),(0,0,.95),2.06),
        ('V2_TresCuartos',(2.7,-5.5,2.15),(0,0,.93),2.1),
        ('V2_Rostro',(.35,-3,1.75),(0,-.02,1.652),.40),
        ('V2_RostroFrente',(0,-3,1.65),(0,-.02,1.65),.37),
        ('V2_RostroPerfil',(-3,0,1.65),(0,-.02,1.65),.37)]:
        g.camera(name,loc,target,scale)
    hero=g.camera('V2_Hero',(2.5,-5.7,2.15),(0,0,.93),2.1)
    hero.data.type='PERSP';hero.data.lens=104
    s.camera=hero;s.render.resolution_x=1440;s.render.resolution_y=1920
    s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    s.render.image_settings.color_mode='RGB';s.render.film_transparent=False
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_distance=2.8
                area.spaces.active.region_3d.view_location=(0,0,.94)
                area.spaces.active.shading.type='SOLID'
                area.spaces.active.shading.color_type='MATERIAL'


def render(root,name,camera,size=(900,1200),samples=32,action='01_A_pose'):
    s=bpy.context.scene;rig=bpy.data.objects['RIG_Viajero']
    rig.animation_data.action=bpy.data.actions[action];s.frame_set(1)
    s.camera=bpy.data.objects[camera];s.render.resolution_x,s.render.resolution_y=size
    s.cycles.samples=samples;s.render.filepath=str(root/'renders/v2'/f'{name}.png')
    bpy.ops.render.render(write_still=True)
