"""Broad sculpt relaxation of anatomical unions, preserving topology and facial deltas."""
import bpy
import sys
import math
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from viajero_v2.common import SCALE,LOW,activate
from viajero_v2 import scene


def main(preview=True, iterations=500):
    rig=bpy.data.objects['RIG_Viajero'];rig.animation_data.action=bpy.data.actions['01_A_pose'];bpy.context.scene.frame_set(1)
    body=bpy.data.objects['Anatomia_Esculpida'];activate(body)
    n=len(body.data.vertices);keys={}
    basis=np.empty(n*3,dtype=np.float32);body.data.shape_keys.key_blocks['Basis'].data.foreach_get('co',basis)
    for key in list(body.data.shape_keys.key_blocks)[1:]:
        arr=np.empty(n*3,dtype=np.float32);key.data.foreach_get('co',arr);keys[key.name]=arr-basis
    body.shape_key_clear()
    group=body.vertex_groups.new(name='TEMP_Relajacion')
    for v in body.data.vertices:
        x,y,z=v.co/SCALE;x=abs(x);z+=LOW
        shoulder=math.exp(-((x-.167)/.085)**2-((z-1.455)/.085)**2)
        hip=math.exp(-((z-.91)/.10)**2)
        neck=math.exp(-((z-1.515)/.045)**2)*math.exp(-(x/.065)**2)
        wrist=math.exp(-((x-.462)/.040)**2-((z-1.122)/.045)**2)
        weight=max(shoulder,hip,neck if z<1.555 else 0,wrist*.55)
        if weight>.005:group.add([v.index],weight,'REPLACE')
    smooth=body.modifiers.new('Moldear transiciones anatomicas','SMOOTH')
    smooth.factor=.8;smooth.iterations=iterations;smooth.vertex_group=group.name
    bpy.ops.object.modifier_move_to_index(modifier=smooth.name,index=0)
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    body.vertex_groups.remove(body.vertex_groups['TEMP_Relajacion'])
    new=np.empty(n*3,dtype=np.float32);body.data.vertices.foreach_get('co',new)
    body.shape_key_add(name='Basis')
    for name,delta in keys.items():body.shape_key_add(name=name).data.foreach_set('co',new+delta)
    body['union_suavizada']=f'Relax localizado {iterations} iteraciones; hombros, pelvis, cuello y munecas; topologia conservada.'
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/v2/viajero_esculpido.blend'))
    if preview:
        objects=list(bpy.data.collections['PERSONAJE'].all_objects);states={o:o.hide_render for o in objects}
        for o in objects:o.hide_render=o!=body
        scene.render(ROOT,'revision_05_anatomia','V2_TresCuartos',(750,1000),24)
        for o,state in states.items():o.hide_render=state


if __name__=='__main__':main()
