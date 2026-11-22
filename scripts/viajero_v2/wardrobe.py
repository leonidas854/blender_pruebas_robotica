"""Clothing reconstruction and local surface sculpting of compression folds."""
import bpy
import math
from mathutils import Vector
import viajero_lib as g
from .common import SCALE,LOW,activate,remove_prefixes,fuse,to_scene,bind,bake


def pants(rig):
    remove_prefixes(['Pantalon.','Pantalon_cintura','Costura_pantalon.'])
    g.COL=g.collection('V2_Pantalon_continuo',bpy.data.collections['PERSONAJE'])
    mat=bpy.data.materials['Pantalon']; parts=[]
    parts.append(g.loft('Cadera_pantalon',[(.832,.105,.098,.015,0),(.94,.158,.119,.008,0),
        (1.025,.158,.125,.003,0),(1.070,.155,.124,0,0)],mat,n=64,sub=2))
    for sign in [-1,1]:
        rings=[(.217,.050,.053,.005,sign*.105),(.24,.057,.059,.005,sign*.105),
            (.28,.061,.064,.008,sign*.105),(.34,.065,.067,.018,sign*.105),
            (.41,.065,.068,.015,sign*.105),(.48,.059,.064,-.008,sign*.105),
            (.54,.066,.071,-.002,sign*.105),(.64,.081,.087,.010,sign*.105),
            (.76,.089,.101,.015,sign*.105),(.87,.092,.105,.010,sign*.105),
            (.95,.086,.103,.006,sign*.105),(1.02,.070,.090,.003,sign*.105)]
        parts.append(g.loft('Pierna_pantalon',rings,mat,n=64,sub=2))
    obj=fuse(parts,'Pantalon_Esculpido',.0025,5)
    for v in obj.data.vertices:
        x,y,z=v.co;cx=.105 if x>0 else -.105
        a=math.atan2(x-cx,-y);r=math.hypot(x-cx,y)
        if z>.90:continue
        # Localised asymmetric compression creases rather than periodic spirals.
        front=max(0,math.cos(a)); side=1 if x>0 else -1
        d=.002*math.sin(6*a+z*4)*math.exp(-((z-.68)/.20)**2)
        for center,amp,width,slant in [(.245,.007,.010,.010),(.278,-.005,.012,-.016),
            (.315,.004,.016,.020),(.455,.006,.018,-.022),(.495,-.005,.014,.015),
            (.540,.004,.020,-.010),(.77,.003,.027,.025)]:
            ridge=center+slant*math.sin(a+side*.8)
            d+=amp*math.exp(-((z-ridge)/width)**2)*(.3+.7*front)
        if r>.001:v.co.x+=(x-cx)/r*d;v.co.y+=y/r*d
    to_scene(obj);bind(obj,rig,mode='pants')


def sculpt_existing():
    # Subdivide before displacement; existing vertex groups are interpolated by Blender.
    for name in ['Abrigo','Abrigo_manga.L','Abrigo_manga.R','Puno_arremangado.L','Puno_arremangado.R','Camisa','Chaleco']:
        obj=bpy.data.objects.get(name)
        if not obj:continue
        activate(obj)
        sub=obj.modifiers.new('Densidad para pliegues','SUBSURF');sub.levels=1
        # Apply to rest mesh; the armature is neutral at this point.
        bpy.ops.object.modifier_apply(modifier=sub.name)
        for v in obj.data.vertices:
            x,y,z=v.co/SCALE+Vector((0,0,LOW));sign=1 if x>0 else -1
            if 'manga' in name or 'Puno' in name:
                a=Vector((sign*.205,0,1.465));b=Vector((sign*.385,0,1.235));d=b-a
                t=max(0,min(1,(Vector((x,y,z))-a).dot(d)/d.length_squared));c=a+t*d
                offset=Vector((x,y,z))-c;ax=math.atan2(offset.y,offset.x*sign)
                envelope=math.exp(-((t-.76)/.32)**2)
                amount=.007*envelope*math.sin(t*31+2.5*ax)+.003*envelope*math.sin(t*57-ax)
                if 'Puno' in name:amount*=.4
                if offset.length>0:v.co+=offset.normalized()*amount*SCALE
            elif name=='Abrigo':
                a=math.atan2(x,-y);lower=math.exp(-((z-.85)/.16)**2)
                amp=.008*lower*math.sin(8*a+z*5)+.003*math.exp(-((z-1.18)/.20)**2)*math.sin(12*a+z*12)
                r=math.hypot(x,y)
                if r>.01:v.co.x+=x/r*amp*SCALE;v.co.y+=y/r*amp*SCALE
            elif name=='Camisa':
                front=max(0,min(1,-y/.08));v.co.y+=.0035*math.sin(x*95+z*32)*math.exp(-((z-1.21)/.20)**2)*front*SCALE
        for mod in obj.modifiers:
            if mod.type=='ARMATURE':mod.use_deform_preserve_volume=True


def scarf_and_collars(rig):
    remove_prefixes(['Bufanda','Pliegue_bufanda','Solapa.','Solapa_ribete.'])
    g.COL=g.collection('V2_Cuello_y_bufanda',bpy.data.collections['PERSONAJE'])
    before=set(bpy.data.objects);n=120;rows=36;vs=[];fs=[]
    mat=bpy.data.materials['Bufanda']
    for j in range(rows):
        t=j/(rows-1)
        for i in range(n):
            a=math.tau*i/n;front=max(0,math.cos(a))
            fold=.004*math.sin(5*math.pi*t+1.4*math.sin(a))+.0015*math.sin(13*math.pi*t+3*a)
            rx=.069+.030*math.sin(t*math.pi*.8)+fold
            ry=.075+.025*front+.060*t*front+.019*math.sin(math.pi*t)+fold
            z=1.538-.048*t-.061*t*front+.008*math.sin(a*2+t*4)
            vs.append((rx*math.sin(a),.007-ry*math.cos(a),z))
    for j in range(rows-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
    g.mesh('Bufanda_Esculpida',vs,fs,mat,'neck',1,.003)
    g.ribbon('Bufanda_cola',[(-.073,.035,1.49),(-.103,.10,1.41),(-.116,.165,1.25),(-.15,.18,1.13)],.061,mat,'chest',.003)
    g.loft('Cuello_abrigo',[(1.478,.084,.082,.016,0),(1.49,.092,.086,.016,0),
        (1.545,.105,.091,.018,0),(1.55,.104,.090,.018,0)],bpy.data.materials['Abrigo'],
        start=.8,end=math.tau-.8,thick=.005,bone='chest')
    for sign,side in [(1,'L'),(-1,'R')]:
        g.panel('Cuello_camisa.'+side,[(sign*.008,-.080,1.489),(sign*.05,-.067,1.52),
            (sign*.086,-.10,1.452),(sign*.042,-.130,1.407)],bpy.data.materials['Camisa'],'chest')
        g.panel('Solapa.'+side,[(sign*.06,-.082,1.507),(sign*.112,-.106,1.47),
            (sign*.143,-.143,1.412),(sign*.102,-.169,1.36),
            (sign*.075,-.153,1.28),(sign*.064,-.162,1.38)],bpy.data.materials['Abrigo'],'chest')
        g.curve('Solapa_ribete.'+side,[(sign*.06,-.087,1.507),(sign*.112,-.111,1.47),
            (sign*.143,-.148,1.412),(sign*.102,-.174,1.36),(sign*.075,-.158,1.28)],.0013,bpy.data.materials['Cuero_borde'],'chest')
    for obj in set(bpy.data.objects)-before:
        bone=obj.get('bind','chest');bake(obj);to_scene(obj);bind(obj,rig,bone=bone)


def boots(rig):
    for side in ['L','R']:
        parts=[bpy.data.objects[n+'.'+side] for n in ['Bota','Puntera','Cana_bota']]
        for obj in parts:
            obj.parent=None
            for mod in list(obj.modifiers):
                if mod.type=='ARMATURE':obj.modifiers.remove(mod)
        obj=fuse(parts,'Bota_Esculpida.'+side,.0016,7)
        bind(obj,rig,bone='foot.'+side)
        # Ankle section follows shin; continuous blend into the vamp.
        foot=obj.vertex_groups['foot.'+side];shin=obj.vertex_groups.new(name='shin.'+side)
        for v in obj.data.vertices:
            t=max(0,min(1,(v.co.z/SCALE+LOW-.08)/.065));t=t*t*(3-2*t)
            foot.add([v.index],1-t,'REPLACE');shin.add([v.index],t,'REPLACE')
