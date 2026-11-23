"""Prueba Blender reproducible: direcciones, longitudes, poses y fixture BVH."""
from pathlib import Path
import sys,json,time,math,bmesh
import bpy
from mathutils import Vector,Quaternion
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from mocap.core import PacketBuilder,points_blender,SEGMENTS,joint_state,encode,angle
from mocap.synthetic import pose
from mocap.blender_adapter import Retargeter
from extract_joint_angles import extract

def topology(obj):
    bm=bmesh.new();bm.from_mesh(obj.data)
    pending=set(bm.verts);sizes=[]
    while pending:
        seed=pending.pop();stack=[seed];n=0
        while stack:
            v=stack.pop();n+=1
            for e in v.link_edges:
                other=e.other_vert(v)
                if other in pending:pending.remove(other);stack.append(other)
        sizes.append(n)
    report=dict(vertices=len(bm.verts),faces=len(bm.faces),components=len(sizes),
                boundary_edges=sum(e.is_boundary for e in bm.edges),
                nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),
                inconsistent_edges=sum(e.is_manifold and not e.is_contiguous for e in bm.edges))
    bm.free();return report

def main():
    s=bpy.context.scene;rig=bpy.data.objects['RIG_Viajero'];body=bpy.data.objects['Mocap_Cuerpo_Cerrado']
    rig.animation_data_clear();adapter=Retargeter(rig);builder=PacketBuilder('synthetic_fixture')
    lengths={b.name:b.length for b in rig.data.bones};errors=[];times=[];max_error=0;max_length=0
    out=ROOT/'entrega/mocap';out.mkdir(exist_ok=True,parents=True)
    packets=[]
    for f in range(1,181):
        s.frame_set(f);packet=builder.build(pose((f-1)/30),t=(f-1)/30)
        start=time.perf_counter();adapter.apply(packet,keyframe=f);times.append((time.perf_counter()-start)*1000)
        bpy.context.view_layer.update()
        p=points_blender(packet)
        for n,(a,b) in SEGMENTS.items():
            pb=rig.pose.bones[n]
            error=angle(tuple(pb.tail-pb.head),tuple(Vector(p[b])-Vector(p[a])))
            max_error=max(max_error,error)
            max_length=max(max_length,abs(pb.length-lengths[n]))
        packets.append(packet)
    if max_error>1e-3:errors.append(f'Direction error {max_error}')
    if max_length>1e-5:errors.append(f'Length drift {max_length}')
    action=rig.animation_data.action;action.name='A_SYNTHETIC_TEST_NO_HUMAN_CAPTURE';action.use_fake_user=True
    rig['mocap_provenance']='synthetic_fixture; analytical coordinates; NOT human or FreeMoCap capture'
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='LINEAR'
    s.frame_start=1;s.frame_end=180;s.render.fps=30
    (out/'synthetic_landmarks.jsonl').write_text('\n'.join(encode(p).decode() for p in packets)+'\n',encoding='utf8')
    (out/'ros2_joint_states_sample.json').write_text(json.dumps(joint_state(packets[90]),indent=2),encoding='utf8')
    extract(rig,out/'joint_telemetry_A_synthetic.csv')
    top=topology(body)
    if top['components']!=1 or top['nonmanifold_edges']:errors.append('Body topology')
    weights={};total_tris=0
    for obj in bpy.data.collections['PERSONAJE'].all_objects:
        if obj.type!='MESH':continue
        obj.data.calc_loop_triangles();total_tris+=len(obj.data.loop_triangles)
        invalid=sum(not v.groups or abs(sum(g.weight for g in v.groups)-1)>.005 for v in obj.data.vertices)
        if invalid:weights[obj.name]=invalid
    if weights:errors.append('Invalid weight sums')
    # Finitud de la superficie deformada en varios frames, sin afirmar ausencia de colisiones.
    pose_checks={}
    for frame in (1,45,90,135,180):
        s.frame_set(frame);bpy.context.view_layer.update()
        evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        finite=all(math.isfinite(c) for v in mesh.vertices for c in v.co)
        pose_checks[str(frame)]=finite;evaluated.to_mesh_clear()
        if not finite:errors.append(f'Nonfinite mesh frame {frame}')
    s.frame_set(45);s.render.filepath=str(ROOT/'tmp/mocap/avatar_flexion.png');bpy.ops.render.render(write_still=True)
    objects=list(bpy.data.collections['PERSONAJE'].all_objects);states={o:o.hide_render for o in objects}
    for o in objects:o.hide_render=o!=body
    s.render.filepath=str(ROOT/'tmp/mocap/anatomia_flexion.png');bpy.ops.render.render(write_still=True)
    s.display.shading.type='SOLID';s.display.shading.color_type='MATERIAL'
    for o,value in states.items():o.hide_render=value
    # Copia A con acción de ensayo. El archivo principal se mantiene en reposo.
    s.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/mocap/prueba_A_sintetica.blend'))
    # Fuente de integración B: exportación nativa Z-up, frame 1 de calibración A.
    source=rig.copy();source.data=rig.data.copy();s.collection.objects.link(source);source.name='SOURCE_SYNTHETIC'
    source.animation_data_create();source.animation_data.action=action.copy()
    for pb in source.pose.bones:
        pb.rotation_quaternion=(1,0,0,0);pb.keyframe_insert('rotation_quaternion',frame=1)
    for o in bpy.context.selected_objects:o.select_set(False)
    source.select_set(True);bpy.context.view_layer.objects.active=source
    bvh=out/'source_SYNTHETIC_NOT_FREEMOCAP.bvh'
    bpy.ops.export_anim.bvh(filepath=str(bvh),frame_start=1,frame_end=180,root_transform_only=True)
    mapping={n:n for n in rig.data.bones.keys() if not n.startswith(('eye.','cloth.','bag'))}
    (ROOT/'mocap/bone_map_viajero.json').write_text(json.dumps(mapping,indent=2),encoding='utf8')
    report=dict(blender=bpy.app.version_string,source='synthetic_fixture',frames=180,
                max_direction_error_deg=math.degrees(max_error),max_bone_length_drift_m=max_length,
                mean_apply_and_keyframe_ms=sum(times)/len(times),max_apply_and_keyframe_ms=max(times),
                timing_scope='Python adapter and keyframe insertion; excludes depsgraph and camera/inference',
                body=top,weights_invalid=weights,pose_finite_checks=pose_checks,base_mesh_triangles=total_tris,
                bones=len(rig.data.bones),errors=errors,
                pending=['live personal capture','real FreeMoCap source','ROS 2 runtime publication','visual collision approval','student Git history'])
    (ROOT/'docs/mocap/validation_blender.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report),flush=True)
    if errors:raise RuntimeError(errors)

if __name__=='__main__':main()
