"""Blend hip, shoulder and wrist volumes into the existing sculpt; transfer facial data."""
import bpy
import sys
import math
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import viajero_lib as g
from viajero_v2.common import SCALE,LOW,fuse,bind,to_scene,activate
from viajero_v2 import scene


def main(preview=True):
    rig=bpy.data.objects['RIG_Viajero'];rig.animation_data.action=bpy.data.actions['01_A_pose'];bpy.context.scene.frame_set(1)
    body=bpy.data.objects['Anatomia_Esculpida'];n=len(body.data.vertices)
    coords=np.empty(n*3,dtype=np.float32);body.data.shape_keys.key_blocks['Basis'].data.foreach_get('co',coords)
    deltas={}
    for key in list(body.data.shape_keys.key_blocks)[1:]:
        a=np.empty(n*3,dtype=np.float32);key.data.foreach_get('co',a);deltas[key.name]=(a-coords).reshape((-1,3))
    colors=np.empty(n*4,dtype=np.float32);body.data.color_attributes['Color_rostro'].data.foreach_get('color',colors);colors=colors.reshape((-1,4))
    tree=KDTree(n)
    for i,p in enumerate(coords.reshape((-1,3))):tree.insert(p,i)
    tree.balance()
    body.shape_key_clear();body.parent=None
    for mod in list(body.modifiers):body.modifiers.remove(mod)
    g.COL=bpy.data.collections['V2_Anatomia_continua'];mat=body.data.materials[0];parts=[body]
    for sign in [-1,1]:
        for name,loc,scale in [
            ('Union_cadera',(sign*.113,.008,.944),(.067,.078,.083)),
            ('Union_hombro',(sign*.165,.004,1.443),(.065,.052,.053)),
            ('Union_muneca',(sign*.461,-.003,1.124),(.024,.018,.029))]:
            obj=g.sphere(name,loc,scale,mat,segments=40,rings=24)
            if 'muneca' in name:obj.rotation_euler[1]=-sign*.58
            to_scene(obj);parts.append(obj)
    body=fuse(parts,'Anatomia_Esculpida',.0018,18)
    body.data.materials.clear();body.data.materials.append(mat)
    for v in body.data.vertices:
        x,y,z=v.co/SCALE+Vector((0,0,LOW))
        v.co.z+=.010*min(1,(x/.09)**2)*math.exp(-((z-.855)/.025)**2)*SCALE
    mapping=np.empty(len(body.data.vertices),dtype=np.int32)
    for v in body.data.vertices:mapping[v.index]=tree.find(v.co)[1]
    for attr in list(body.data.color_attributes):body.data.color_attributes.remove(attr)
    attr=body.data.color_attributes.new(name='Color_rostro',type='FLOAT_COLOR',domain='POINT')
    attr.data.foreach_set('color',colors[mapping].ravel())
    bind(body,rig)
    new=np.empty(len(body.data.vertices)*3,dtype=np.float32);body.data.vertices.foreach_get('co',new)
    body.shape_key_add(name='Basis')
    for name,delta in deltas.items():body.shape_key_add(name=name).data.foreach_set('co',new+delta[mapping].ravel())
    body['metodo']='Union volumetrica; puentes anatomicos en cadera, hombro y muneca; relajacion; color y deltas faciales transferidos por proximidad.'
    activate(body);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/v2/viajero_esculpido.blend'))
    if preview:
        objs=list(bpy.data.collections['PERSONAJE'].all_objects);states={o:o.hide_render for o in objs}
        for o in objs:o.hide_render=o!=body
        scene.render(ROOT,'revision_06_anatomia','V2_TresCuartos',(750,1000),24)
        for o,state in states.items():o.hide_render=state
        scene.render(ROOT,'revision_06_vestido','V2_TresCuartos',(750,1000),24,'14_Prueba_codos_rodilla')


if __name__=='__main__':main()
