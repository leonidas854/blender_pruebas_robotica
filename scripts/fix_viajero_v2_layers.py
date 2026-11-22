"""Resolve intersections revealed by rear, profile and flexion review renders."""
import bpy
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import viajero_lib as g
from viajero_v2.common import SCALE,LOW,remove_prefixes,bake,to_scene,bind,activate
from viajero_v2 import scene


def main():
    rig=bpy.data.objects['RIG_Viajero'];rig.animation_data.action=bpy.data.actions['01_A_pose'];bpy.context.scene.frame_set(1)
    remove_prefixes(['Camisa_manga.'])
    body=bpy.data.objects['Anatomia_Esculpida']
    # Apply fitting correction consistently to Basis and both expression keys.
    for key in body.data.shape_keys.key_blocks:
        for v in key.data:
            x,y,z=v.co/SCALE+Vector((0,0,LOW))
            if .18<z<.47:
                w=math.sin(math.pi*(z-.18)/.29)**2
                v.co.y-=.017*w*SCALE
                cx=.105 if x>0 else -.105
                v.co.x-=.06*(x-cx)*w*SCALE
            frontal=max(0,min(1,(-y-.07)/.04))
            v.co.y+=.009*math.exp(-(x/.021)**2-((z-1.655)/.023)**2)*frontal*SCALE
    # Synchronise the mesh with its Basis before saving and structural validation.
    for v,k in zip(body.data.vertices,body.data.shape_keys.key_blocks['Basis'].data):v.co=k.co
    for o in bpy.data.objects:
        if o.name.startswith('Fosa_nasal.'):
            for v in o.data.vertices:v.co.y+=.009*SCALE
    coat=bpy.data.objects['Abrigo'];tree=BVHTree.FromPolygons([v.co for v in coat.data.vertices],[list(p.vertices) for p in coat.data.polygons])
    def rear(x,z,offset=.004):
        hit=tree.ray_cast(Vector((x,1,z)),Vector((0,-1,0)))[0]
        return hit.y+offset if hit else .065*SCALE
    # Project back stitches onto the actual modified coat surface.
    for obj in bpy.data.objects:
        if obj.name.startswith('Costura_espalda.'):
            for v in obj.data.vertices:v.co.y=rear(v.co.x,v.co.z,.0018)
    remove_prefixes(['Bandolera_espalda','Bufanda_cola'])
    g.COL=g.collection('V2_Correas_ajustadas',bpy.data.collections['PERSONAJE']);before=set(bpy.data.objects)
    pts=[]
    for i in range(35):
        t=i/34;x=(-.135+.375*t)*SCALE;z=(1.477-.489*t-LOW)*SCALE
        pts.append((x,rear(x,z,.006),z))
    # Geometry is already in scene coordinates, so no second scale conversion.
    g.ribbon('Bandolera_espalda',pts,.026*SCALE,bpy.data.materials['Cuero'],thickness=.003)
    tail=[]
    for i in range(22):
        t=i/21;x=(-.085-.055*t)*SCALE;z=(1.488-.365*t-LOW)*SCALE
        tail.append((x,rear(x,z,.011)+.004*math.sin(t*7),z))
    g.ribbon('Bufanda_cola',tail,.054*SCALE,bpy.data.materials['Bufanda'],'chest',.0025)
    for obj in set(bpy.data.objects)-before:
        bone=obj.get('bind');bake(obj);bind(obj,rig,bone=bone)
    belt=bpy.data.objects['Cinturon']
    for v in belt.data.vertices:
        v.co.x*=1.045;v.co.y*=1.045
    for obj in bpy.data.objects:
        if obj.name.startswith('Hebilla_cinturon'):
            for v in obj.data.vertices:v.co.y-=.006*SCALE
    # Foot-only boots do not expose skin at the upper rear after calf correction.
    activate(body);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/v2/viajero_esculpido.blend'))
    scene.render(ROOT,'revision_04_espalda','V2_Espalda',(750,1000),24)
    scene.render(ROOT,'revision_04_flexion','V2_TresCuartos',(750,1000),24,'14_Prueba_codos_rodilla')
    scene.render(ROOT,'revision_04_perfil','V2_Perfil',(750,1000),24)


if __name__=='__main__':main()
