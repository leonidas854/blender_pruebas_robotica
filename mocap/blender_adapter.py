"""Resuelve direcciones en espacio armature y conserva longitudes de reposo."""
from mathutils import Vector, Matrix, Quaternion
from mocap.core import points_blender, SEGMENTS, torso_axes, between

class Retargeter:
    def __init__(self,rig):
        self.rig=rig
        if max(abs(x-1) for x in rig.scale)>1e-5 or abs(rig.matrix_world.to_quaternion().angle)>1e-5:
            raise ValueError('El rig debe tener escala 1 y rotación de objeto aplicada')
        self.rest={b.name:b.matrix_local.to_quaternion() for b in rig.data.bones}
        self.ordered=sorted(rig.pose.bones,key=lambda b:len(b.parent_recursive))
        self.torso=Quaternion()

    def apply(self,packet,keyframe=None):
        p=points_blender(packet);target={}
        try:
            left,back,up=torso_axes(p)
            self.torso=Matrix((left,back,up)).transposed().to_quaternion()
            for n in ('pelvis','spine','chest','neck'):
                if n in self.rest:target[n]=self.torso@self.rest[n]
        except (KeyError,ValueError):pass
        for n,(a,b) in SEGMENTS.items():
            if n not in self.rest or a not in p or b not in p:continue
            d=Vector(p[b])-Vector(p[a])
            if d.length<1e-5:continue
            base=self.torso@self.rest[n]
            target[n]=Quaternion(between(base@Vector((0,1,0)),d))@base
        # Cabeza: línea entre orejas y nariz; fallback conserva orientación anterior.
        if all(i in p for i in (0,7,8)) and 'head' in self.rest:
            try:
                left=(Vector(p[7])-Vector(p[8])).normalized()
                front=Vector(p[0])-(Vector(p[7])+Vector(p[8]))*.5
                up=left.cross(-front).normalized();back=up.cross(left).normalized()
                if min(up.length,back.length)>.5:
                    target['head']=Matrix((left,back,up)).transposed().to_quaternion()@self.rest['head']
            except ValueError:pass
        current={};changed=0
        for pb in self.ordered:
            rest=self.rest[pb.name]
            basis=(current[pb.parent.name]@self.rest[pb.parent.name].inverted()@rest) if pb.parent else rest
            pb.rotation_mode='QUATERNION'
            if pb.name in target:
                q=basis.inverted()@target[pb.name]
                q.normalize()
                if q.dot(pb.rotation_quaternion)<0:q.negate()
                pb.rotation_quaternion=q;changed+=1
                if keyframe is not None:pb.keyframe_insert('rotation_quaternion',frame=keyframe,group=pb.name)
            current[pb.name]=basis@pb.rotation_quaternion
        return changed
