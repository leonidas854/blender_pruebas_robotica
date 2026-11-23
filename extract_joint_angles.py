"""Blender: exporta ángulos geométricos de la animación evaluada a CSV."""
import argparse
import csv
import json
import sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from mocap.core import joint_angles

def extract(rig,path,start=None,end=None):
    s=bpy.context.scene;old=s.frame_current
    names=['left_shoulder_pitch','left_shoulder_roll','left_elbow_flex',
           'right_shoulder_pitch','right_shoulder_roll','right_elbow_flex',
           'left_shoulder_elevation','right_shoulder_elevation','left_knee_flex','right_knee_flex']
    rows=[];fps=s.render.fps/s.render.fps_base
    start=s.frame_start if start is None else start;end=s.frame_end if end is None else end
    try:
        for frame in range(start,end+1):
            s.frame_set(frame);bpy.context.view_layer.update()
            r=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
            def point(bone,tail=False):
                pb=r.pose.bones[bone]
                return tuple(r.matrix_world@(pb.tail if tail else pb.head))
            p={}
            for side,ids in [('L',(11,13,15,23,25,27)),('R',(12,14,16,24,26,28))]:
                for i,bone,tail in zip(ids,['upper_arm.','forearm.','forearm.','thigh.','shin.','shin.'],[False,False,True,False,False,True]):
                    p[i]=point(bone+side,tail)
            values=joint_angles(p)
            if any(n not in values for n in names):raise ValueError(f'Geometría degenerada en frame {frame}')
            rows.append([frame,(frame-start)/fps]+[values[n] for n in names])
    finally:s.frame_set(old)
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf8') as f:
        w=csv.writer(f);w.writerow(['frame','timestamp_s']+[n+'_rad' for n in names]);w.writerows(rows)
    meta=dict(source_blend=bpy.data.filepath,action=rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None,
              provenance=rig.get('mocap_provenance','UNSPECIFIED'),frames=len(rows),fps=fps,units='radians',
              definition='Geometric angles from evaluated joint positions. No arbitrary local Euler components.',
              hardware_limits='Not certified; no URDF supplied')
    path.with_suffix('.meta.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
    return meta

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rig',default='RIG_Viajero');p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    print(json.dumps(extract(bpy.data.objects[a.rig],a.output),indent=2))
