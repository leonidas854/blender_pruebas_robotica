"""Final local sculpt refinement: coherent hair volume and natural lip coloration."""
import bpy
import sys
import math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from viajero_v2.common import SCALE,LOW,fuse,bind,activate
from viajero_v2 import scene


def refine():
    rig=bpy.data.objects['RIG_Viajero'];rig.animation_data.action=bpy.data.actions['01_A_pose'];bpy.context.scene.frame_set(1)
    parts=list(bpy.data.collections['V2_Cabello_moldeado'].objects)
    for o in parts:
        o.parent=None
        for m in list(o.modifiers):
            if m.type=='ARMATURE':o.modifiers.remove(m)
    hair=fuse(parts,'Cabello_Esculpido',.0010,5)
    hair.data.materials.clear();hair.data.materials.append(bpy.data.materials['Cabello'])
    bind(hair,rig,bone='head')
    # Skin shader uses a smooth colour field, not a separate floating lip strip.
    body=bpy.data.objects['Anatomia_Esculpida']
    mat=body.data.materials[0].copy();mat.name='Piel_rostro_v2';body.data.materials[0]=mat
    bs=mat.node_tree.nodes.get('Principled BSDF');base=tuple(bs.inputs['Base Color'].default_value[:3])
    attr=body.data.color_attributes.new(name='Color_rostro',type='FLOAT_COLOR',domain='POINT')
    for v,c in zip(body.data.vertices,attr.data):
        x,y,z=v.co/SCALE+Vector((0,0,LOW));front=max(0,min(1,(-y-.05)/.035))
        upper=1.615+.0015*math.exp(-((abs(x)-.008)/.005)**2)
        lower=1.608-.0012*math.exp(-(x/.020)**2)
        lip=math.exp(-(x/.025)**6)*max(math.exp(-((z-upper)/.0025)**2),math.exp(-((z-lower)/.0033)**2))*front
        blush=.12*math.exp(-((abs(x)-.056)/.025)**2-((z-1.643)/.022)**2)*front
        w=min(.8,.65*lip+blush);target=(.285,.105,.075)
        c.color=tuple(b*(1-w)+t*w for b,t in zip(base,target))+(1,)
    node=mat.node_tree.nodes.new('ShaderNodeVertexColor');node.layer_name='Color_rostro'
    mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
    # Eyebrows are tapered rather than uniformly thick drawing strokes.
    for side in ['L','R']:
        obj=bpy.data.objects['Ceja.'+side]
        xs=[v.co.x for v in obj.data.vertices];lo=min(xs);hi=max(xs)
        for v in obj.data.vertices:
            t=(v.co.x-lo)/(hi-lo)
            strength=.50+.50*math.sin(math.pi*t)**.5
            center=1.710*SCALE-LOW*SCALE
            v.co.z=center+(v.co.z-center)*strength
    activate(body)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/v2/viajero_esculpido.blend'))
    scene.render(ROOT,'iteracion_03_rostro','V2_RostroFrente',(800,800),48)
    scene.render(ROOT,'iteracion_03_cuerpo','V2_TresCuartos',(750,1000),32,'13_Presentacion')


if __name__=='__main__':refine()
