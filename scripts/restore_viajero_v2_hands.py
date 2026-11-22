"""Restore finger detail lost during broad smoothing, preserving the continuous body."""
import bpy
import bmesh
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
    # Trim only the hands; retain an overlapping forearm section for closed union.
    bm=bmesh.new();bm.from_mesh(body.data)
    doomed=[v for v in bm.verts if v.co.z < (1.108-LOW)*SCALE and abs(v.co.x)>.43*SCALE]
    bmesh.ops.delete(bm,geom=doomed,context='VERTS');bm.to_mesh(body.data);bm.free()
    with bpy.data.libraries.load(str(ROOT/'blender/personaje_final.blend'),link=False) as (src,dst):
        dst.objects=[name for name in src.objects if name.startswith(('Mano.','Muneca.','Dedo_'))]
    for old in dst.objects:
        g.COL.objects.link(old);old.parent=None;old.modifiers.clear()
        if old.data.shape_keys:old.shape_key_clear()
        parts.append(old)
    body=fuse(parts,'Anatomia_Esculpida',.0018,3)
    body.data.materials.clear();body.data.materials.append(mat)
    mapping=np.empty(len(body.data.vertices),dtype=np.int32)
    for v in body.data.vertices:mapping[v.index]=tree.find(v.co)[1]
    for attr in list(body.data.color_attributes):body.data.color_attributes.remove(attr)
    attr=body.data.color_attributes.new(name='Color_rostro',type='FLOAT_COLOR',domain='POINT')
    attr.data.foreach_set('color',colors[mapping].ravel())
    bind(body,rig)
    new=np.empty(len(body.data.vertices)*3,dtype=np.float32);body.data.vertices.foreach_get('co',new)
    body.shape_key_add(name='Basis')
    for name,delta in deltas.items():body.shape_key_add(name=name).data.foreach_set('co',new+delta[mapping].ravel())
    body['metodo']='Superficie continua; restauracion de dedos desde copia anterior al suavizado; color y deltas faciales conservados.'
    activate(body);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/v2/viajero_esculpido.blend'))
    if preview:
        objs=list(bpy.data.collections['PERSONAJE'].all_objects);states={o:o.hide_render for o in objs}
        for o in objs:o.hide_render=o!=body
        scene.render(ROOT,'revision_07_anatomia','V2_TresCuartos',(750,1000),24)
        for o,state in states.items():o.hide_render=state
        scene.render(ROOT,'revision_07_vestido','V2_TresCuartos',(750,1000),24,'14_Prueba_codos_rodilla')


if __name__=='__main__':main()
