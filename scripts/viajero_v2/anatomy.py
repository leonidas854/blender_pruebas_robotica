"""Continuous anatomical surface with modelled facial planes and separated digits."""
import bpy
import math
from mathutils import Vector
import viajero_lib as g
from .common import fuse, remove_prefixes, to_scene, bind


def gauss(x,z,cx,cz,wx,wz):
    return math.exp(-((x-cx)/wx)**2-((z-cz)/wz)**2)


def face_surface(mat):
    profile = [(1.557,.014,.027,-.010),(1.565,.035,.042,-.010),
        (1.581,.057,.057,-.004),(1.602,.075,.069,.003),
        (1.626,.087,.079,.008),(1.650,.091,.084,.010),
        (1.676,.090,.086,.012),(1.702,.087,.085,.014),
        (1.730,.085,.081,.017),(1.757,.076,.070,.020),
        (1.779,.051,.047,.020),(1.793,.002,.002,.020)]
    # Dense interpolated rings support actual surface displacement, not loose facial pieces.
    rings=[]
    for k,(a,b) in enumerate(zip(profile,profile[1:])):
        p0=profile[max(0,k-1)];p3=profile[min(len(profile)-1,k+2)]
        for j in range(6):
            t=j/6
            rings.append(tuple(.5*((2*q1)+(-q0+q2)*t+(2*q0-5*q1+4*q2-q3)*t*t+(-q0+3*q1-3*q2+q3)*t*t*t) for q0,q1,q2,q3 in zip(p0,a,b,p3)))
    rings.append(profile[-1])
    vs=[]; fs=[]; n=160
    for z,rx,ry,cy in rings:
        for i in range(n):
            a=math.tau*i/n; x=rx*math.sin(a); y=cy-ry*math.cos(a)
            f=max(0,math.cos(a))**4
            # Photos: broad cheeks, soft squared jaw, rounded tip, full lower lip.
            projection=(.026*gauss(x,z,0,1.675,.014,.040)
                +.044*gauss(x,z,0,1.654,.018,.015)
                +.013*gauss(abs(x),z,.016,1.650,.009,.009)
                +.014*gauss(abs(x),z,.051,1.642,.027,.024)
                +.021*gauss(x,z,0,1.610,.038,.022)
                +.017*gauss(x,z,0,1.584,.038,.015)
                +.007*gauss(abs(x),z,.040,1.707,.031,.011)
                -.009*gauss(abs(x),z,.038,1.684,.023,.010))
            y-=projection*f
            # Integrated philtrum and lips with a shallow mouth crease.
            y-=f*(.004*gauss(x,z,0,1.620,.009,.009)
                +.006*gauss(x,z,0,1.607,.025,.004)
                -.0028*gauss(x,z,0,1.612,.030,.0018))
            vs.append((x,y,z))
    for j in range(len(rings)-1):
        for i in range(n):
            a=j*n+i; b=j*n+(i+1)%n; fs.append((a,b,b+n,a+n))
    fs.extend([tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))])
    return g.mesh('Volumen_rostro_fotografias',vs,fs,mat)


def build(rig):
    remove_prefixes(['Cuerpo','Rostro','Cuello','Oreja','Antebrazo_visible','Muneca.',
        'Mano.','Dedo_','Ojo.','Iris.','Pupila.','Parpado','Ceja.','Fosa_nasal.','Boca_linea','Labio_inferior'])
    # Shirt/coat collars also share Cuello prefix; rebuilt separately by wardrobe.
    g.CHAR=bpy.data.collections['PERSONAJE']
    g.COL=g.collection('V2_Anatomia_continua',g.CHAR)
    mat=bpy.data.materials['Piel']; parts=[]
    parts.append(g.loft('Volumen_torso',[(.85,.105,.085,.025,0),(.92,.140,.100,.015,0),
        (1.01,.140,.102,.010,0),(1.12,.125,.094,.005,0),(1.25,.150,.106,.005,0),
        (1.36,.177,.115,.010,0),(1.43,.180,.108,.012,0),(1.48,.144,.085,.012,0),
        (1.51,.065,.055,.012,0)],mat,n=64,sub=2))
    parts.append(g.tube('Volumen_cuello',[(0,.014,1.46),(0,.014,1.52),(0,.015,1.59)],
        [.057,.048,.049],mat,n=48,sub=2))
    parts.append(face_surface(mat))
    for sign,side in [(1,'L'),(-1,'R')]:
        parts.append(g.sphere('Volumen_oreja',(sign*.089,.008,1.655),(.013,.019,.030),mat))
        parts.append(g.tube('Volumen_brazo',[(sign*.155,.005,1.455),(sign*.205,0,1.465),
            (sign*.252,0,1.405),(sign*.300,0,1.335),(sign*.352,0,1.270),
            (sign*.395,0,1.219),(sign*.429,-.002,1.173),(sign*.461,-.003,1.124)],
            [.056,.060,.057,.048,.037,.039,.029,.022],mat,n=32,sub=2))
        parts.append(g.loft('Volumen_pierna',[(.075,.030,.036,.006,sign*.105),
            (.15,.032,.037,.008,sign*.105),(.26,.046,.052,.023,sign*.105),
            (.36,.055,.060,.027,sign*.105),(.46,.046,.046,-.002,sign*.105),
            (.50,.048,.050,-.012,sign*.105),(.61,.064,.071,.008,sign*.105),
            (.75,.079,.085,.013,sign*.105),(.87,.083,.086,.011,sign*.105),
            (.95,.073,.080,.010,sign*.105)],mat,n=40,sub=2))
        parts.append(g.sphere('Volumen_pie',(sign*.105,-.055,.055),(.044,.115,.040),mat))
        wrist=Vector((sign*.461,-.003,1.124)); down=Vector((sign*.55,0,-.835)); across=Vector((sign*.835,0,.55))
        palm=wrist+down*.041
        o=g.sphere('Volumen_palma',palm,(.031,.017,.047),mat); o.rotation_euler[1]=-sign*.58; parts.append(o)
        for i,(finger,length) in enumerate([('index',.060),('middle',.068),('ring',.060),('pinky',.046)]):
            root=palm+down*.027+across*((i-1.5)*.015); end=root+down*length+Vector((0,-.011,0))
            parts.append(g.tube('Volumen_dedo',[root-down*.015,root,root.lerp(end,.5),end-down*.004,end],
                [.0077,.0074,.0065,.0054,.002],mat,n=16,sub=2))
        root=palm-across*.027-down*.013; end=root-across*.032+down*.036
        parts.append(g.tube('Volumen_pulgar',[root+across*.01,root,root.lerp(end,.5),end],
            [.012,.010,.008,.003],mat,n=16,sub=2))
    body=fuse(parts,'Anatomia_Esculpida',voxel=.0018,iterations=5)
    # Fit the hidden anatomical shoulders inside the tailored shoulder seam.
    for v in body.data.vertices:
        x,y,z=v.co
        shoulder=math.exp(-((abs(x)-.188)/.070)**2-((z-1.475)/.060)**2)
        v.co.z-=.028*shoulder
        v.co.y*=1-.10*shoulder
        if .84<z<1.08:
            t=math.sin(math.pi*(z-.84)/.24)**2
            v.co.x*=1-.04*t;v.co.y*=1-.08*t
    body.data.materials.clear(); body.data.materials.append(mat)
    to_scene(body); bind(body,rig)
    body['metodo']='Volumen nuevo; union voxel 1.8 mm; relajacion; planos faciales desplazados sobre malla.'
    body['identidad']='Interpretacion de las cinco fotos personales y concepto aprobado; no fotogrametria.'
    body.shape_key_add(name='Basis')
    from .common import SCALE,LOW
    for name in ['Sonrisa_sutil','Reflexion_sutil']:
        key=body.shape_key_add(name=name)
        for v in key.data:
            x,y,z=v.co/SCALE+Vector((0,0,LOW))
            front=max(0,min(1,(-y-.025)/.055))
            if name=='Sonrisa_sutil':v.co.z+=SCALE*.0035*gauss(abs(x),z,.027,1.612,.014,.018)*front
            else:v.co.z-=SCALE*.002*gauss(abs(x),z,.035,1.709,.025,.012)*front
    # Eye inserts and edge details are kept separate and can be edited independently.
    before=set(bpy.data.objects)
    for sign,side in [(1,'L'),(-1,'R')]:
        x=sign*.039
        g.sphere('Ojo.'+side,(x,-.084,1.684),(.019,.012,.0065),bpy.data.materials['Ojo'],'eye.'+side,48,24)
        g.sphere('Iris.'+side,(x,-.0955,1.684),(.0052,.0018,.0052),bpy.data.materials['Iris'],'eye.'+side)
        g.sphere('Pupila.'+side,(x,-.0971,1.684),(.0024,.0008,.0028),bpy.data.materials['Pupila'],'eye.'+side)
        for upper in [True,False]:
            pts=[]
            for i in range(25):
                a=math.pi*i/24
                pts.append((x+.019*math.cos(a),-.088-.009*math.sin(a),1.684+(.0065 if upper else -.0055)*math.sin(a)))
            g.curve(('Parpado_sup.' if upper else 'Parpado_inf.')+side,pts,.002,mat,'head')
        g.curve('Ceja.'+side,[(x-sign*.022,-.082,1.708),(x,-.089,1.714),(x+sign*.024,-.074,1.707)],.0028,bpy.data.materials['Cabello'],'head')
        g.curve('Helix.'+side,[(sign*.093,-.007,1.635),(sign*.100,-.009,1.654),
            (sign*.095,-.004,1.677),(sign*.088,-.007,1.668)],.0024,mat,'head')
        g.sphere('Fosa_nasal.'+side,(sign*.012,-.1245,1.648),(.0033,.001,.0018),bpy.data.materials['Labios'],'head')
    g.curve('Boca_hendidura',[(-.027,-.089,1.613),(-.014,-.098,1.612),(0,-.101,1.611),(.014,-.098,1.612),(.027,-.089,1.613)],.0008,bpy.data.materials['Labios'],'head')
    from .common import bake
    for obj in set(bpy.data.objects)-before:
        bone=obj.get('bind','head'); bake(obj); to_scene(obj); bind(obj,rig,bone=bone)
    return body
