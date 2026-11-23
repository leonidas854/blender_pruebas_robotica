"""Camino B: importar BVH/FBX y transferir una captura con mapa explícito."""
import argparse
import json
import sys
from pathlib import Path
import bpy
from mathutils import Quaternion,Matrix

def retarget(source,target,mapping,start,end,calibration_frame=1,root_motion=False):
    """El frame de calibración debe representar la A-pose física del destino.

    Permite rest pose T distinta si la fuente se posa en A en ese frame.
    No inferimos automáticamente que el primer frame sea una pose válida.
    """
    for dst,src in mapping.items():
        if dst not in target.pose.bones or src not in source.pose.bones:raise ValueError(f'Mapa inválido: {dst} <- {src}')
    if any(abs(x-1)>1e-5 for x in target.scale):raise ValueError('Aplicar escala del destino')
    s=bpy.context.scene;s.frame_set(calibration_frame);bpy.context.view_layer.update()
    src_world=source.matrix_world.to_quaternion();dst_world=target.matrix_world.to_quaternion()
    base={n:src_world@source.pose.bones[n].matrix.to_quaternion() for n in mapping.values()}
    rest={b.name:b.matrix_local.to_quaternion() for b in target.data.bones}
    # Alinear también el marco corporal de calibración, no sólo los rolls.
    # El importador BVH puede girar 180 grados el conjunto al convertir forward.
    def body_frame(obj,names,posed):
        bones=obj.pose.bones if posed else obj.data.bones
        def head(n):
            b=bones[names[n]]
            return obj.matrix_world@(b.head if posed else b.head_local)
        l,r,hl,hr=[head(n) for n in ('upper_arm.L','upper_arm.R','thigh.L','thigh.R')]
        left=(l-r).normalized();up_hint=(l+r-hl-hr)*.5
        back=up_hint.cross(left).normalized();up=left.cross(back).normalized()
        if min(left.length,back.length,up.length)<.9:raise ValueError('Marco corporal degenerado')
        return Matrix((left,back,up)).transposed().to_quaternion()
    required=('upper_arm.L','upper_arm.R','thigh.L','thigh.R')
    if not all(n in mapping for n in required):raise ValueError('Mapa debe incluir hombros y muslos para calibrar marco corporal')
    align=body_frame(target,{n:n for n in required},False)@body_frame(source,mapping,True).inverted()
    target.animation_data_create();target.animation_data.action=bpy.data.actions.new('B_Retarget_'+source.name)
    ordered=sorted(target.pose.bones,key=lambda b:len(b.parent_recursive))
    root_name=mapping.get('pelvis');origin=source.matrix_world@source.pose.bones[root_name].head if root_name else None
    ratio=1.
    if root_motion:
        if not root_name:raise ValueError('Root motion requiere pelvis en mapa')
        src_height=abs((source.matrix_world@source.pose.bones[root_name].head).z)
        dst_height=abs((target.matrix_world@target.data.bones['pelvis'].head_local).z)
        if src_height<1e-5:raise ValueError('Calibrar altura/origen antes de root motion')
        ratio=dst_height/src_height
    for frame in range(start,end+1):
        s.frame_set(frame);bpy.context.view_layer.update();desired={};current={}
        for dst,src in mapping.items():
            q=src_world@source.pose.bones[src].matrix.to_quaternion()
            delta=align@(q@base[src].inverted())@align.inverted()
            desired[dst]=dst_world.inverted()@delta@dst_world@rest[dst]
        for pb in ordered:
            basis=current[pb.parent.name]@rest[pb.parent.name].inverted()@rest[pb.name] if pb.parent else rest[pb.name]
            pb.rotation_mode='QUATERNION'
            q=basis.inverted()@desired[pb.name] if pb.name in desired else Quaternion()
            if q.dot(pb.rotation_quaternion)<0:q.negate()
            pb.rotation_quaternion=q;pb.scale=(1,1,1);pb.location=(0,0,0)
            current[pb.name]=basis@q
            pb.keyframe_insert('rotation_quaternion',frame=frame,group=pb.name)
        if root_motion:
            displacement=align@(source.matrix_world@source.pose.bones[root_name].head-origin)*ratio
            root=target.pose.bones['root']
            root.location=target.data.bones['root'].matrix_local.to_3x3().inverted()@(target.matrix_world.to_3x3().inverted()@displacement)
            root.keyframe_insert('location',frame=frame)
    action=target.animation_data.action;action.use_fake_user=True
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='LINEAR'
    s.frame_start=start;s.frame_end=end;s.frame_set(start)
    return dict(mapped=len(mapping),frames=end-start+1,calibration_frame=calibration_frame,root_motion=root_motion)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--map',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--rig',default='RIG_Viajero')
    p.add_argument('--scale',type=float,default=1.);p.add_argument('--calibration-frame',type=int,required=True)
    p.add_argument('--axis-forward',default='Y');p.add_argument('--axis-up',default='Z')
    p.add_argument('--root-motion',action='store_true');p.add_argument('--provenance',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);before=set(bpy.data.objects)
    if a.source.suffix.lower()=='.bvh':
        bpy.ops.import_anim.bvh(filepath=str(a.source.resolve()),global_scale=a.scale,axis_forward=a.axis_forward,axis_up=a.axis_up,update_scene_fps=True,update_scene_duration=True)
    elif a.source.suffix.lower()=='.fbx':bpy.ops.import_scene.fbx(filepath=str(a.source.resolve()),global_scale=a.scale)
    else:raise ValueError('Usar BVH o FBX')
    rigs=[o for o in set(bpy.data.objects)-before if o.type=='ARMATURE']
    if len(rigs)!=1:raise ValueError('Se requiere exactamente un esqueleto fuente')
    source=rigs[0];target=bpy.data.objects[a.rig]
    action=source.animation_data.action
    start,end=map(int,action.frame_range)
    result=retarget(source,target,json.loads(a.map.read_text(encoding='utf8')),start,end,a.calibration_frame,a.root_motion)
    target['mocap_provenance']=a.provenance
    source.hide_render=True;source.hide_set(True)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(a.output.resolve()))
    print(json.dumps(result))

if __name__=='__main__':main()
