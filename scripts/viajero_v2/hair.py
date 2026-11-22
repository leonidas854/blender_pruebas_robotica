"""Swept, flattened and grooved locks over a scalp shell."""
import bpy
import math
import random
from mathutils import Vector
import viajero_lib as g
from .common import remove_prefixes,bake,to_scene,bind


def lock(name,points,width,mat):
    p=[Vector(v) for v in points]; vs=[]; fs=[]; rows=22; cols=9
    for j in range(rows):
        t=j/(rows-1)
        center=(1-t)**3*p[0]+3*t*(1-t)**2*p[1]+3*t*t*(1-t)*p[2]+t**3*p[3]
        tangent=3*(1-t)**2*(p[1]-p[0])+6*t*(1-t)*(p[2]-p[1])+3*t*t*(p[3]-p[2])
        normal=Vector((center.x/.096,(center.y-.012)/.096,(center.z-1.71)/.092)).normalized()
        across=tangent.cross(normal).normalized(); normal=across.cross(tangent).normalized()
        w=width*(.65+.65*math.sin(math.pi*t))*(1-t**2.3)+.00025
        for i in range(cols):
            u=2*i/(cols-1)-1
            crest=.0025*(1-u*u)*(1-t)+.0007*math.cos(u*math.pi*4)*(1-u*u)*(1-t)
            vs.append(center+across*u*w+normal*crest)
    for j in range(rows-1):
        for i in range(cols-1):
            a=j*cols+i;fs.append((a,a+1,a+1+cols,a+cols))
    obj=g.mesh(name,vs,fs,mat,'head',sub=1,thick=.0015)
    # Thin curved grooves catch highlights without making the mass look cylindrical.
    for col in [2,4,6]:
        pts=[Vector(vs[j*cols+col])+Vector((0,-.0003,.0004)) for j in range(2,rows-2)]
        g.curve(name+'_fibra',pts,.00022,mat,'head')
    return obj


def build(rig):
    remove_prefixes(['Cabello','Mechon'])
    g.COL=g.collection('V2_Cabello_moldeado',bpy.data.collections['PERSONAJE'])
    dark=bpy.data.materials['Cabello']; light=bpy.data.materials['Mechon_luz']
    before=set(bpy.data.objects); rng=random.Random(1122)
    vs=[];fs=[];n=100;rows=24
    for j in range(rows):
        for i in range(n):
            a=math.tau*i/n
            edge=1.33+.51*(1-math.cos(a))/2+.045*math.sin(a*7)
            theta=.012+(edge-.012)*j/(rows-1)
            vs.append((.094*math.sin(theta)*math.sin(a),.015-.094*math.sin(theta)*math.cos(a),1.714+.087*math.cos(theta)))
    for j in range(rows-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
    g.mesh('Cabello_casquete',vs,fs,dark,'head',1,.002)
    for i in range(45):
        a=i*2.39996;r=.075*math.sqrt((i+.5)/45)
        x=r*math.cos(a);y=.015+r*math.sin(a);z=1.714+.089*math.sqrt(max(0,1-(r/.096)**2))
        lift=rng.uniform(.010,.020); shift=rng.uniform(-.045,-.028)
        lock('Cabello_mechon_%02d'%i,[(x,y,z-.008),(x+.010,y-.006,z+lift),
            (x+shift*.7,y-.014,z+lift*.7),(x+shift,y-.020,z+.002)],rng.uniform(.008,.014),light if i%9==0 else dark)
    # Irregular front locks, separated into large flowing masses.
    for i in range(12):
        x=-.069+i*.0125;z=1.770+.013*math.sin(i*.7)
        lock('Cabello_flequillo_%02d'%i,[(x+.02,-.040,z+.015),(x+.019,-.074,z+.018),
            (x-.005,-.092,z-.002),(x-.020,-.085,z-.032-rng.random()*.014)],rng.uniform(.009,.013),dark)
    # Close-cut side and rear locks follow the head instead of floating capsules.
    for side in [-1,1]:
        for i in range(15):
            a=side*(.9+i*.14); x=.092*math.sin(a);y=.015-.092*math.cos(a)
            lock('Cabello_lateral',[(x*.9,y,1.761),(x*1.05,y+.006,1.748),
                (x*1.05,y+.018,1.719),(x*.97,y+.024,1.693+.008*math.sin(i))],.009,dark)
    for obj in set(bpy.data.objects)-before:
        bake(obj);to_scene(obj);bind(obj,rig,bone='head')
