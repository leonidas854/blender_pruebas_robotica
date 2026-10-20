"""Build an editable Viajero character from the approved base.

blender -b --python-exit-code 1 -P scripts/build_viajero.py -- --preview
blender -b --python-exit-code 1 -P scripts/build_viajero.py -- --render
Existing stages 01–03 are read only. Generated stages are backed up on rebuild.
"""
import bpy
import bmesh
import sys
import math
import random
import shutil
import json
from pathlib import Path
from datetime import datetime
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import viajero_lib as g

random.seed(28)
M={}
FINGERS={}
SCALE=1.0


def save(name):
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"blender"/name))


def setup():
    for path in ["renders/final","renders/turnaround","renders/rostro","renders/poses",
                 "renders/accesorios","renders/evidencias","exports/glb","exports/fbx",
                 "assets/materiales","docs"]:
        (ROOT/path).mkdir(parents=True,exist_ok=True)
    generated=[ROOT/"blender"/n for n in [
        "04_cabeza_rostro.blend","05_cabello.blend","06_ropa_base.blend",
        "07_ropa_detallada.blend","08_accesorios.blend","09_materiales.blend",
        "10_rigging.blend","personaje_final.blend"]]
    existing=[p for p in generated if p.exists()]
    if existing:
        backup=ROOT/"blender/respaldo"/datetime.now().strftime("%Y%m%d_%H%M%S")
        backup.mkdir(parents=True)
        for p in existing:shutil.copy2(p,backup/p.name)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    s=bpy.context.scene
    s.unit_settings.system="METRIC";s.unit_settings.length_unit="METERS"
    g.CHAR=g.collection("PERSONAJE")
    g.COL=g.collection("01_Anatomia",g.CHAR)
    s["proyecto"]="Viajero entre épocas"
    s["orientacion"]="Z arriba; frente -Y; escala total con cabello 1.80 m"
    s["estado"]="Versión de presentación editable; revisar parecido y deformaciones extremas."
    colors={
        "Piel":((.43,.235,.14),.5,0,"skin"),
        "Labios":((.26,.09,.065),.55,0,None),
        "Cabello":((.009,.006,.005),.66,0,"hair"),
        "Mechon_luz":((.018,.012,.009),.61,0,None),
        "Camisa":((.64,.53,.37),.83,0,"fabric"),
        "Abrigo":((.065,.105,.16),.77,0,"fabric"),
        "Forro":((.12,.045,.036),.8,0,"fabric"),
        "Chaleco":((.12,.065,.035),.7,0,"leather"),
        "Pantalon":((.039,.043,.05),.87,0,"fabric"),
        "Bufanda":((.24,.044,.035),.85,0,"fabric"),
        "Bordado":((.46,.25,.095),.65,0,None),
        "Cuero":((.11,.048,.023),.5,0,"leather"),
        "Cuero_borde":((.22,.115,.05),.55,0,"leather"),
        "Guantes":((.039,.026,.019),.65,0,"leather"),
        "Suela":((.022,.017,.014),.89,0,None),
        "Laton":((.42,.25,.085),.34,.78,"metal"),
        "Bronce":((.13,.078,.025),.48,.75,"metal"),
        "Piedra":((.025,.115,.18),.19,.28,None),
        "Ojo":((.72,.70,.61),.27,0,None),
        "Iris":((.068,.033,.015),.3,0,None),
        "Pupila":((.003,.002,.002),.2,0,None),
    }
    for n,args in colors.items():M[n]=g.material(n,*args)
    M["Vidrio"]=g.material("Vidrio",(.89,.94,.96),.07)
    bs=M["Vidrio"].node_tree.nodes.get("Principled BSDF")
    bs.inputs["Transmission Weight"].default_value=1
    bs.inputs["IOR"].default_value=1.45
    # A separate, untouched base is preserved in the original .blend.
    with bpy.data.libraries.load(str(ROOT/"blender/03_cuerpo_base.blend"),link=False) as (src,dst):
        dst.objects=["Leonidas_Cuerpo_Base_180"]
    body=dst.objects[0];g.COL.objects.link(body);body.name="Cuerpo"
    body.data=body.data.copy()
    bm=bmesh.new();bm.from_mesh(body.data)
    # Remove the provisional head and hand ends. Clothing masks torso transitions.
    remove=[v for v in bm.verts if v.co.z>1.555 or (abs(v.co.x)>.477 and v.co.z<1.16)]
    bmesh.ops.delete(bm,geom=remove,context="VERTS")
    bm.to_mesh(body.data);bm.free()
    body.data.materials.clear();body.data.materials.append(M["Piel"])
    body.modifiers.clear()
    smooth=body.modifiers.new("Relajar base heredada","SMOOTH");smooth.factor=.6;smooth.iterations=8
    sub=body.modifiers.new("Superficie corporal","SUBSURF");sub.levels=1;sub.render_levels=1
    body["nota"]="Base conservada para edición; oculta bajo prendas para evitar penetraciones."
    g.tube("Cuello",[(0,.015,1.48),(0,.012,1.53),(0,.012,1.59)],
           [.054,.053,.05],M["Piel"],"neck",n=32)
    # Import every reference as packed image empties in a disabled viewport collection.
    refs=g.collection("REFERENCIAS — activar para consultar")
    for i,p in enumerate(sorted((ROOT/"referencias").rglob("*"))):
        if p.suffix.lower() not in {".png",".jpg",".jpeg"}:continue
        img=bpy.data.images.load(str(p),check_existing=True);img.pack()
        o=bpy.data.objects.new(p.stem,None);refs.objects.link(o)
        o.empty_display_type="IMAGE";o.data=img;o.empty_display_size=1.8
        o.location=(3+(i%4)*2.1,2,1+(i//4)*1.7)
        o.rotation_euler=(math.pi/2,0,0);o.hide_render=True
    refs.hide_viewport=True;refs.hide_render=True


def face():
    g.COL=g.collection("02_Rostro",g.CHAR)
    rings=[
        (1.559,.016,.025,-.007,0),(1.568,.037,.043,-.012,0),
        (1.582,.057,.058,-.008,0),(1.607,.074,.074,.002,0),
        (1.635,.086,.083,.005,0),(1.665,.089,.088,.008,0),
        (1.693,.087,.088,.01,0),(1.722,.087,.085,.013,0),
        (1.749,.08,.077,.016,0),(1.773,.062,.06,.018,0),
        (1.787,.033,.032,.018,0),(1.792,.002,.002,.018,0)]
    head=g.loft("Rostro",rings,M["Piel"],n=64,sub=2,bone="head")
    # Sculpt planar cheeks, nasal bridge, chin and brow into the continuous head.
    for v in head.data.vertices:
        x,y,z=v.co
        frontal=max(0, min(1,(-y+.01)/.07))
        nose=.049*math.exp(-(x/.016)**2-((z-1.654)/.023)**2)
        bridge=.018*math.exp(-(x/.012)**2-((z-1.685)/.031)**2)
        muzzle=.022*math.exp(-(x/.034)**2-((z-1.612)/.018)**2)
        cheek=.012*math.exp(-((abs(x)-.052)/.023)**2-((z-1.65)/.026)**2)
        chin=.014*math.exp(-(x/.035)**2-((z-1.585)/.015)**2)
        v.co.y-=frontal*(nose+bridge+muzzle+cheek+chin)
    head.shape_key_add(name="Basis")
    for name in ["Sonrisa","Sorpresa","Reflexion"]:
        key=head.shape_key_add(name=name)
        key.value=0
        for v in key.data:
            x,y,z=v.co
            front=max(0,min(1,(-y-.02)/.06))
            mouth=math.exp(-((z-1.611)/.025)**2)*front
            if name=="Sonrisa":
                v.co.z+=.007*math.exp(-((abs(x)-.029)/.019)**2)*mouth
            elif name=="Sorpresa":
                v.co.z-=.011*math.exp(-(x/.032)**2)*mouth
            else:
                v.co.y-=.003*math.exp(-(x/.06)**2-((z-1.704)/.025)**2)*front
    for sign,side in [(1,"L"),(-1,"R")]:
        x=sign*.039
        g.sphere("Ojo."+side,(x,-.090,1.685),(.020,.018,.0085),M["Ojo"],"eye."+side)
        g.sphere("Iris."+side,(x,-.107,1.685),(.0063,.002,.0063),M["Iris"],"eye."+side)
        g.sphere("Pupila."+side,(x,-.109,1.685),(.0027,.001,.0033),M["Pupila"],"eye."+side)
        for upper in [True,False]:
            pts=[]
            for i in range(13):
                a=math.pi*i/12
                pts.append((x+.020*math.cos(a),-.101-.004*math.sin(a),
                            1.685+(.0075 if upper else -.006)*math.sin(a)))
            lid=g.curve(("Parpado_sup." if upper else "Parpado_inf.")+side,pts,.0035,M["Piel"],"head")
        vs=[];fs=[]
        for j in range(4):
            t=j/3
            for i in range(25):
                a=math.pi*i/24
                vs.append((x+.020*math.cos(a),-.108-.003*math.sin(a),
                           1.685+(.0075+.008*t)*math.sin(a)))
        for j in range(3):
            for i in range(24):
                a=j*25+i;fs.append((a,a+1,a+26,a+25))
        g.mesh("Parpado_piel."+side,vs,fs,M["Piel"],"head")
        g.curve("Ceja."+side,[(x-sign*.024,-.090,1.710),(x,-.099,1.715),(x+sign*.025,-.084,1.708)],
                .003,M["Cabello"],"head")
        ear=g.sphere("Oreja."+side,(sign*.089,.006,1.657),(.014,.022,.030),M["Piel"],"head")
        g.curve("Oreja_helix."+side,[(sign*.094,-.012,1.641),(sign*.101,-.014,1.660),
                    (sign*.095,-.008,1.679),(sign*.087,-.008,1.670)],.003,M["Piel"],"head")
        g.sphere("Fosa_nasal."+side,(sign*.012,-.120,1.649),(.004,.0015,.0024),M["Labios"],"head")
    g.curve("Boca_linea",[(-.031,-.093,1.613),(-.016,-.102,1.611),(0,-.106,1.610),
                         (.016,-.102,1.611),(.031,-.093,1.613)],.0015,M["Labios"],"head")
    g.curve("Labio_inferior",[(-.028,-.093,1.609),(0,-.105,1.606),(.028,-.093,1.609)],
            .0032,M["Labios"],"head")
    save("04_cabeza_rostro.blend")


def hair():
    g.COL=g.collection("03_Cabello",g.CHAR)
    # Scalp shell with a variable hairline, then hand-directed tapered tufts.
    vs=[];fs=[];n=64;rows=14
    for j in range(rows):
        for i in range(n):
            a=math.tau*i/n
            edge=1.28+.48*(1-math.cos(a))/2+.06*math.sin(9*a)
            theta=.025+(edge-.025)*j/(rows-1)
            vs.append((.093*math.sin(theta)*math.sin(a),
                       .013-.093*math.sin(theta)*math.cos(a),
                       1.718+.082*math.cos(theta)))
    for j in range(rows-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
    g.mesh("Cabello_base",vs,fs,M["Cabello"],"head",sub=1,thick=.003)
    for i in range(30):
        a=i*2.39996
        r=.073*math.sqrt((i+.5)/30)
        x=r*math.cos(a);y=.012+r*math.sin(a)
        z=1.775+.023*(1-r/.08)
        # Strong lateral sweep, irregular silhouette rather than a round cap.
        direction=Vector((-.038-.018*random.random(),-.016+.025*random.random(),.023))
        root=Vector((x,y,z-.018))
        points=[root,root+direction*.35+Vector((0,0,.021)),
                root+direction*.85+Vector((0,0,.020)),root+direction*1.5]
        g.tube("Mechon_%02d"%i,points,[.018,.019,.012,.001],
               M["Cabello"] if i%4 else M["Mechon_luz"],"head",n=10,sub=1)
    for i in range(12):
        x=-.071+i*.012
        z=1.769+.008*math.sin(i)
        g.tube("Mechon_flequillo",[(x,-.047,z),(x-.012,-.078,z+.005),
            (x-.026,-.087,z-.009),(x-.034,-.082,z-.035-(i%3)*.006)],
            [.013,.015,.009,.0007],M["Cabello"],"head",n=10)
    for sign in [-1,1]:
        for j in range(7):
            g.tube("Mechon_lateral",[(sign*.077,-.006+j*.011,1.755),
                (sign*.094,-.008+j*.011,1.732),(sign*.089,.012+j*.011,1.689+(j%2)*.006)],
                [.013,.012,.001],M["Cabello"],"head",n=8)
    save("05_cabello.blend")


def clothing_base():
    g.COL=g.collection("04_Camisa_chaleco",g.CHAR)
    g.loft("Camisa",[(1.00,.151,.115,0,0),(1.01,.153,.116,0,0),
        (1.08,.15,.117,0,0),(1.17,.145,.114,0,0),(1.29,.175,.129,0,0),
        (1.39,.195,.137,0,0),(1.46,.188,.118,0,0),(1.495,.10,.081,.006,0),
        (1.51,.065,.063,.008,0)],M["Camisa"],thick=.003,folds=.003)
    for sign,side in [(1,"L"),(-1,"R")]:
        shoulder=(sign*.19,0,1.465);elbow=(sign*.35,0,1.275);cuff=(sign*.40,0,1.21)
        g.tube("Camisa_manga."+side,[shoulder,(sign*.235,0,1.43),elbow,cuff],
               [.075,.073,.061,.056],M["Camisa"])
        g.panel("Cuello_camisa."+side,[(sign*.008,-.079,1.49),(sign*.052,-.066,1.53),
                (sign*.088,-.099,1.46),(sign*.050,-.126,1.403)],
                M["Camisa"],"chest")
    # Open V is encoded per row, preserving a visibly separate shirt underneath.
    rings=[(1.045,.159,.125,0,0),(1.055,.160,.125,0,0),
           (1.18,.153,.126,0,0),(1.30,.180,.140,0,0),
           (1.40,.199,.146,0,0),(1.46,.182,.126,0,0),(1.48,.125,.092,0,0)]
    vest=g.loft("Chaleco",rings,M["Chaleco"],n=48,start=.08,end=math.tau-.08,thick=.006)
    cols=49
    for j,ring in enumerate(rings):
        gap=[.06,.06,.06,.10,.32,.54,.67][j]
        z,rx,ry,cy,cx=ring
        for i in range(cols):
            a=gap+(math.tau-2*gap)*i/(cols-1)
            vest.data.vertices[j*cols+i].co=(rx*math.sin(a),-ry*math.cos(a),z)
    for sign in [-1,1]:
        g.curve("Costura_chaleco",[(sign*.01,-.128,1.06),(sign*.016,-.13,1.25),
             (sign*.064,-.14,1.40),(sign*.09,-.08,1.48)],.0016,M["Cuero_borde"])
        g.box("Bolsillo_chaleco",(sign*.096,-.118,1.14),(.063,.009,.014),M["Cuero"],.003)
    for z in [1.10,1.16,1.22,1.28,1.34]:
        g.sphere("Boton_chaleco",(.020,-.145 if z>1.25 else -.133,z),(.005,.003,.005),M["Laton"],"spine")
    save("06_ropa_base.blend")


def clothing():
    g.COL=g.collection("05_Abrigo",g.CHAR)
    rings=[(.755,.244,.157,.015,0),(.77,.242,.158,.015,0),
           (.91,.208,.154,.01,0),(1.045,.177,.140,.005,0),
           (1.17,.171,.137,.003,0),(1.30,.196,.155,.003,0),
           (1.40,.218,.16,.004,0),(1.46,.216,.14,.007,0),
           (1.49,.172,.105,.01,0),(1.515,.075,.075,.014,0)]
    coat=g.loft("Abrigo",rings,M["Abrigo"],n=64,start=.42,end=math.tau-.42,thick=.006,folds=.002)
    coat.data.materials.append(M["Forro"])
    coat.modifiers.get("Grosor de tejido").material_offset=1
    for sign,side in [(1,"L"),(-1,"R")]:
        edge=[(sign*rx*math.sin(.42),cy-ry*math.cos(.42)-.002,z) for z,rx,ry,cy,cx in rings]
        g.curve("Ribete_abrigo."+side,edge,.0023,M["Cuero_borde"])
        g.panel("Solapa."+side,[(sign*.048,-.080,1.514),(sign*.116,-.103,1.473),
             (sign*.143,-.142,1.405),(sign*.093,-.168,1.345),
             (sign*.077,-.145,1.255),(sign*.055,-.159,1.37)],M["Abrigo"],"chest")
        g.curve("Solapa_ribete."+side,[(sign*.05,-.085,1.514),(sign*.12,-.108,1.473),
             (sign*.145,-.148,1.405),(sign*.095,-.173,1.345),(sign*.079,-.15,1.265)],
             .0017,M["Bordado"],"chest")
        g.tube("Abrigo_manga."+side,[(sign*.18,.01,1.465),(sign*.214,.006,1.452),
            (sign*.26,.002,1.40),(sign*.302,0,1.345),(sign*.338,0,1.295),
            (sign*.361,0,1.267),(sign*.38,0,1.245)],
            [.065,.080,.078,.071,.075,.064,.063],M["Abrigo"],n=24,sub=2)
        g.tube("Puno_arremangado."+side,[(sign*.378,0,1.25),(sign*.383,0,1.244),
            (sign*.397,0,1.223),(sign*.406,0,1.212)],
            [.067,.070,.067,.058],M["Camisa"],n=24)
        g.ribbon("Hombrera_cuero."+side,[(sign*.095,-.044,1.50),(sign*.15,-.043,1.49),
            (sign*.211,-.035,1.468)],.026,M["Cuero"],"clavicle."+side)
        g.sphere("Remache_hombro."+side,(sign*.202,-.054,1.48),(.006,.003,.006),M["Laton"],"clavicle."+side)
        for z in [1.12,1.22,1.32]:
            x=sign*(.11 if z<1.25 else .125)
            g.sphere("Boton_abrigo."+side,(x,-.125 if z<1.25 else -.144,z),(.0065,.004,.0065),M["Laton"])
        # Curved welt pockets, rear tailoring lines.
        g.curve("Bolsillo_abrigo."+side,[(sign*.16,-.108,.94),(sign*.173,-.096,1.00),
             (sign*.174,-.09,1.04)],.005,M["Cuero_borde"])
        g.curve("Costura_espalda."+side,[(sign*.08,.10,1.47),(sign*.105,.14,1.3),
             (sign*.07,.135,1.05),(sign*.15,.145,.77)],.0015,M["Cuero_borde"])
    g.loft("Cuello_abrigo",[(1.477,.083,.081,.014,0),(1.488,.090,.083,.014,0),
        (1.546,.096,.086,.019,0),(1.551,.095,.085,.019,0)],M["Abrigo"],
        start=.66,end=math.tau-.66,thick=.005,bone="chest")
    g.COL=g.collection("06_Pantalon_telas",g.CHAR)
    # A closed hip yoke and two roomy, shaped trouser legs.
    g.loft("Pantalon_cintura",[(.905,.153,.11,.015,0),(.96,.165,.127,.008,0),
         (1.065,.158,.127,0,0),(1.075,.156,.125,0,0)],M["Pantalon"],thick=.004,bone="pelvis")
    for sign,side in [(1,"L"),(-1,"R")]:
        x=sign*.105
        rings=[(.21,.051,.056,.004,x),(.225,.052,.059,.004,x),
               (.26,.063,.064,.006,x),(.30,.066,.066,.006,x),
               (.36,.067,.069,.012,x),(.43,.065,.067,.006,x),
               (.49,.061,.061,-.01,x),(.54,.073,.078,0,x),
               (.65,.084,.09,.01,x),(.77,.092,.103,.012,x),
               (.88,.094,.108,.008,x),(.925,.087,.102,.005,x)]
        g.loft("Pantalon."+side,rings,M["Pantalon"],n=40,folds=.006,thick=.003)
        g.box("Bolsillo_cargo."+side,(sign*.184,-.06,.777),(.056,.032,.121),M["Pantalon"],.011,
              "thigh."+side)
        g.box("Tapeta_cargo."+side,(sign*.184,-.079,.824),(.063,.012,.039),M["Pantalon"],.006,
              "thigh."+side)
        g.sphere("Boton_cargo."+side,(sign*.184,-.087,.82),(.004,.002,.004),M["Laton"],"thigh."+side)
        g.curve("Costura_pantalon."+side,[(x+sign*.055,.018,.26),(x+sign*.067,.026,.38),
             (x+sign*.063,.008,.49),(x+sign*.084,.025,.67),(x+sign*.09,.036,.86)],
             .0013,M["Cuero_borde"])
    # Draped woven strips: grid, large folds, geometric embroidery and fringe.
    for name,x0,width,length,mat in [
        ("Fajin_rojo",-.165,.10,.39,M["Bufanda"]),
        ("Tela_clara",.156,.075,.34,M["Camisa"])]:
        vs=[];fs=[];rows=20;cols=8
        for j in range(rows):
            t=j/(rows-1)
            for i in range(cols):
                u=i/(cols-1)
                vs.append((x0+(u-.5)*width+math.sin(t*2)*.025,
                           -.14-.018*math.sin(u*math.tau*2+t*2)-.012*t,
                           1.045-length*t+.018*math.sin(u*math.pi)*t))
        for j in range(rows-1):
            for i in range(cols-1):
                a=j*cols+i;fs.append((a,a+1,a+1+cols,a+cols))
        g.mesh(name,vs,fs,mat,"cloth."+("L" if x0>0 else "R"),1,.002)
        for sideu in [.12,.88]:
            pts=[]
            for j in range(rows):
                t=j/(rows-1);u=sideu
                pts.append((x0+(u-.5)*width+math.sin(t*2)*.025,
                            -.143-.018*math.sin(u*math.tau*2+t*2)-.012*t,
                            1.045-length*t+.018*math.sin(u*math.pi)*t))
            g.curve(name+"_borde",pts,.0015,M["Bordado"],"cloth."+("L" if x0>0 else "R"))
        for j in range(7):
            t=.16+j*.115
            xc=x0+math.sin(t*2)*.025;zc=1.045-length*t
            g.curve(name+"_rombo",[(xc-.018,-.177,zc),(xc,-.181,zc+.015),
                  (xc+.018,-.177,zc),(xc,-.181,zc-.015)],.001,M["Bordado"],
                  "cloth."+("L" if x0>0 else "R"),True)
        for i in range(10):
            x=x0+(i/9-.5)*width+math.sin(2)*.025
            g.curve(name+"_fleco",[(x,-.153,1.05-length),(x+.003,-.158,1.024-length)],
                    .0012,mat,"cloth."+("L" if x0>0 else "R"))
    scarf()
    hands()
    boots()
    bpy.data.objects["Cuerpo"].hide_render=True
    bpy.data.objects["Cuerpo"].hide_set(True)
    save("07_ropa_detallada.blend")


def scarf():
    g.COL=g.collection("07_Bufanda",g.CHAR)
    # An actual draped fabric surface, not stacked torus primitives.
    vs=[];fs=[];n=72;rows=12
    for j in range(rows):
        t=j/(rows-1)
        for i in range(n):
            a=math.tau*i/n
            r=.079+.018*math.sin(math.pi*t)+.004*math.sin(5*math.pi*t+2*a)
            ry=r+.082*t*max(0,math.cos(a))
            z=1.552-.077*t-.041*t*max(0,math.cos(a))+.005*math.sin(2*a+6*t)
            vs.append((r*math.sin(a),.005-ry*math.cos(a),z))
    for j in range(rows-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
    g.mesh("Bufanda",vs,fs,M["Bufanda"],"neck",1,.003)
    for t in [.18,.45,.72,.94]:
        pts=[]
        for i in range(60):
            a=math.tau*i/60;r=.081+.018*math.sin(math.pi*t)+.004*math.sin(5*math.pi*t+2*a)
            ry=r+.082*t*max(0,math.cos(a))
            pts.append((r*math.sin(a),.005-ry*math.cos(a),
                        1.552-.077*t-.041*t*max(0,math.cos(a))+.005*math.sin(2*a+6*t)))
        g.curve("Pliegue_bufanda",pts,.0018,M["Bufanda"],"neck",True)
    g.ribbon("Bufanda_cola",[(-.075,.037,1.49),(-.115,.11,1.40),
          (-.116,.16,1.26),(-.15,.171,1.12)],.060,M["Bufanda"],"chest",.0025)


def hands():
    g.COL=g.collection("08_Manos_guantes",g.CHAR)
    for sign,side in [(1,"L"),(-1,"R")]:
        wrist=Vector((sign*.461,-.003,1.124))
        down=Vector((sign*.55,0,-.835));across=Vector((sign*.835,0,.55))
        g.tube("Antebrazo_visible."+side,[(sign*.395,0,1.23),(sign*.414,0,1.202),
                  (sign*.442,-.002,1.16),wrist],
               [.044,.039,.030,.023],M["Piel"],"forearm."+side,n=24)
        palm=wrist+down*.041
        o=g.sphere("Mano."+side,palm,(.031,.017,.047),M["Piel"],"hand."+side)
        o.rotation_euler[1]=-sign*.58
        glove=g.sphere("Guante."+side,palm+Vector((0,.001,.004)),
                       (.032,.0185,.038),M["Guantes"],"hand."+side)
        glove.rotation_euler[1]=-sign*.58
        g.tube("Muneca."+side,[wrist-down*.035,wrist,wrist+down*.018],
               [.028,.023,.025],M["Piel"],"forearm."+side)
        g.tube("Correa_guante."+side,[wrist-down*.005,wrist+down*.006],
               [.026,.026],M["Cuero"],"hand."+side,n=24)
        g.buckle("Hebilla_guante."+side,tuple(wrist+Vector((0,-.029,0))),.022,.015,M["Laton"],"hand."+side)
        for i,(name,length) in enumerate([("index",.060),("middle",.068),("ring",.060),("pinky",.046)]):
            root=palm+down*.027+across*((i-1.5)*.015)
            end=root+down*length+Vector((0,-.011,0))
            mid=root.lerp(end,.52)
            points=[root-down*.009,root,mid,end-down*.003,end]
            bone=f"{name}.01.{side}"
            g.tube("Dedo_"+name+"."+side,points,[.0085,.008,.0077,.006,.002],M["Piel"],bone,n=12,sub=1)
            g.tube("Guante_"+name+"."+side,[root-down*.009,root,root+down*.016],
                   [.0092,.0093,.009],M["Guantes"],bone,n=12,sub=1)
            FINGERS[(name,side)]=(root,mid,end)
        root=palm-across*.027-down*.013
        end=root-across*.032+down*.036
        mid=root.lerp(end,.5)
        g.tube("Dedo_thumb."+side,[root,mid,end],[.011,.009,.004],M["Piel"],"thumb.01."+side,n=12)
        FINGERS[("thumb",side)]=(root,mid,end)


def boots():
    g.COL=g.collection("09_Botas",g.CHAR)
    for sign,side in [(1,"L"),(-1,"R")]:
        x=sign*.105;foot="foot."+side;shin="shin."+side
        # Planform outline of boot, lofted through welt, upper and toe box.
        outline=[(-.046,.072),(.046,.072),(.052,.01),(.057,-.11),
                 (.051,-.170),(.026,-.185),(-.027,-.185),(-.051,-.168),(-.055,-.09)]
        vs=[];fs=[];n=len(outline)
        for j,(z,f) in enumerate([(.012,.92),(.019,1),(.039,1),(.045,.94)]):
            for xx,yy in outline:vs.append((x+xx*f,yy,z))
        for j in range(3):
            for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        fs.extend([tuple(reversed(range(n))),tuple(3*n+i for i in range(n))])
        sole=g.mesh("Suela."+side,vs,fs,M["Suela"],foot)
        mod=sole.modifiers.new("Canto suela","BEVEL");mod.width=.005;mod.segments=3
        g.curve("Cerco_bota."+side,[(x+xx,yy,.042) for xx,yy in outline],.0035,M["Cuero_borde"],foot,True)
        g.sphere("Bota."+side,(x,-.056,.075),(.052,.122,.045),M["Cuero"],foot)
        g.sphere("Puntera."+side,(x,-.126,.066),(.053,.060,.028),M["Cuero"],foot)
        g.loft("Cana_bota."+side,[(.056,.047,.065,-.014,x),(.09,.048,.058,-.002,x),
                (.125,.045,.048,.007,x),(.18,.049,.051,.007,x),
                (.235,.054,.055,.004,x),(.243,.054,.055,.004,x)],
               M["Cuero"],n=32,thick=.005,bone=shin,folds=.002)
        g.ribbon("Lengueta."+side,[(x,-.095,.09),(x,-.052,.14),(x,-.055,.239)],
                 .050,M["Cuero_borde"],shin)
        g.loft("Correa_bota."+side,[(.217,.057,.059,.004,x),(.238,.057,.059,.004,x)],
               M["Cuero_borde"],n=40,thick=.003,bone=shin)
        g.buckle("Hebilla_bota."+side,(x+sign*.038,-.040,.228),.027,.022,M["Laton"],shin)
        for j in range(7):
            z=.10+j*.017;y=-.057 if j>1 else -.085+j*.014
            for s in [-1,1]:
                g.ellipse("Ojal."+side,(x+s*.023,y,z),.0032,.0032,.001,M["Laton"],shin)
            if j<6:
                yn=-.057 if j>=1 else -.071
                for s in [-1,1]:
                    g.curve("Cordon."+side,[(x+s*.023,y-.004,z),
                       (x, min(y,yn)-.008,z+.009),(x-s*.023,yn-.004,z+.017)],
                       .0017,M["Bordado"],shin)
        for j in range(6):
            g.box("Taco_suela."+side,(x,-.14+j*.035,.01),(.079,.016,.017),
                  M["Suela"],.002,foot)


def accessories():
    g.COL=g.collection("10_Cinturones_bolso",g.CHAR)
    g.loft("Cinturon",[(1.035,.179,.148,.003,0),(1.041,.18,.149,.003,0),
         (1.077,.18,.149,.003,0),(1.081,.179,.148,.003,0)],M["Cuero"],n=64,thick=.005,bone="pelvis")
    g.buckle("Hebilla_cinturon",(0,-.153,1.059),.052,.036,M["Laton"],"pelvis")
    for sign in [-1,1]:
        for i in range(3):
            g.sphere("Remache_cinturon",(sign*(.044+i*.019),-.148+i*.003,1.06),
                      (.0025,.002,.0025),M["Laton"],"pelvis")
    for a in [.5,1.2,2.3,3.3,4.3,5.5]:
        x=.183*math.sin(a);y=.003-.151*math.cos(a)
        loop=g.box("Pasador_cinturon",(x,y,1.057),(.013,.009,.053),M["Cuero_borde"],.002,"pelvis")
        loop.rotation_euler[2]=-a
    # Shoulder strap wraps over the shoulder and returns down the back.
    strap=[(-.15,-.073,1.49),(-.123,-.144,1.417),(-.066,-.168,1.32),
           (.005,-.17,1.22),(.087,-.163,1.12),(.19,-.132,1.01),(.252,-.03,.96)]
    g.ribbon("Bandolera_frente",strap,.030,M["Cuero"])
    for offset in [-.012,.012]:
        g.curve("Costura_bandolera",[(x+offset,y-.003,z) for x,y,z in strap],.0008,M["Bordado"])
    g.ribbon("Bandolera_espalda",[(-.15,-.073,1.49),(-.16,.01,1.51),
        (-.145,.11,1.46),(-.05,.17,1.30),(.08,.17,1.15),(.23,.105,.97)],.030,M["Cuero"])
    g.buckle("Hebilla_bandolera",(-.067,-.18,1.32),.033,.040,M["Laton"],"chest")
    g.box("Bolso",(.254,.017,.914),(.185,.102,.195),M["Cuero"],.019,"bag")
    g.box("Bolso_tapa",(.254,-.039,.977),(.190,.017,.092),M["Cuero"],.012,"bag")
    g.curve("Costura_bolso",[(.17,-.052,1.005),(.17,-.052,.945),(.20,-.052,.935),
        (.31,-.052,.935),(.34,-.052,.945),(.34,-.052,1.005)],.0013,M["Bordado"],"bag")
    for x in [.205,.30]:
        g.ribbon("Bolso_correa",[(x,-.055,1.005),(x,-.059,.945),(x,-.052,.865)],
                 .016,M["Cuero_borde"],"bag")
        g.buckle("Bolso_hebilla",(x,-.065,.922),.023,.025,M["Laton"],"bag")
        g.sphere("Bolso_remache",(x,-.062,.986),(.003,.002,.003),M["Laton"],"bag")
    g.box("Bolsa_auxiliar",(-.181,-.055,1.00),(.07,.055,.095),M["Cuero"],.009,"pelvis")
    g.box("Bolsa_aux_tapa",(-.181,-.085,1.024),(.076,.009,.04),M["Cuero_borde"],.005,"pelvis")
    g.sphere("Bolsa_aux_boton",(-.181,-.093,1.018),(.004,.002,.004),M["Laton"],"pelvis")
    g.COL=g.collection("11_Talisman",g.CHAR)
    c=(-.059,-.164,.975)
    g.sphere("Talisman_Disco",c,(.026,.005,.026),M["Bronce"],"pelvis",48,24)
    for r in [.025,.022,.017,.008]:
        g.ellipse("Talisman_aro",(c[0],c[1]-.005,c[2]),r,r,.0012,M["Laton"],"pelvis")
    for i in range(24):
        a=math.tau*i/24
        pts=[(c[0]+r*math.sin(a),c[1]-.006,c[2]+r*math.cos(a)) for r in [.0185,.021]]
        g.curve("Talisman_grabado",pts,.00055,M["Laton"],"pelvis")
    for i in range(8):
        a=math.tau*i/8
        g.curve("Talisman_radio",[(c[0]+r*math.sin(a+.25*r/.016),c[1]-.007,
                   c[2]+r*math.cos(a+.25*r/.016)) for r in [.008,.013,.016]],
                   .0007,M["Laton"],"pelvis")
    g.sphere("Talisman_piedra",(c[0],c[1]-.009,c[2]),(.006,.003,.006),M["Piedra"],"pelvis")
    g.ellipse("Talisman_anilla",(c[0],c[1],1.005),.005,.006,.0014,M["Laton"],"pelvis")
    g.curve("Talisman_cordon",[(-.09,-.15,1.06),(-.075,-.16,1.025),
            (c[0],c[1],1.009),(-.038,-.157,1.053)],.0017,M["Cuero"],"pelvis")
    g.COL=g.collection("12_Gafas",g.CHAR)
    for sign,side in [(1,"L"),(-1,"R")]:
        x=sign*.039
        g.ellipse("Gafas_Aro."+side,(x,-.121,1.684),.030,.023,.0015,M["Laton"],"head")
        # Thin closed lenses with real transmission.
        g.sphere("Gafas_Lente."+side,(x,-.121,1.684),(.0285,.001,.0215),M["Vidrio"],"head",48,24)
        g.curve("Gafas_varilla."+side,[(sign*.069,-.119,1.69),(sign*.088,-.075,1.692),
                 (sign*.098,.001,1.683),(sign*.092,.024,1.668)],.0015,M["Laton"],"head")
        g.sphere("Gafas_plaqueta."+side,(sign*.014,-.116,1.675),(.003,.002,.005),M["Vidrio"],"head")
        g.box("Gafas_bisagra."+side,(sign*.07,-.118,1.689),(.004,.003,.006),M["Laton"],.001,"head")
    g.curve("Gafas_puente",[(-.009,-.123,1.688),(0,-.128,1.694),(.009,-.123,1.688)],
             .0015,M["Laton"],"head")
    save("08_accesorios.blend")


def prepare_meshes():
    """Convert curves, apply construction modifiers, unwrap; preserve head shape keys."""
    global SCALE
    objects=list(g.CHAR.all_objects)
    for o in objects:
        if o.type not in {"MESH","CURVE"}:continue
        was_hidden=o.hide_get()
        o.hide_set(False)
        g.activate(o)
        if o.type=="CURVE":
            bpy.ops.object.convert(target="MESH")
        for mod in list(o.modifiers):
            # Keep the animated facial topology and light-weight body subdivision editable.
            if o.name in {"Rostro","Cuerpo"} and mod.type=="SUBSURF":continue
            bpy.ops.object.modifier_apply(modifier=mod.name)
        # Recalculate consistent normals on open cloth and enclosed accessories.
        bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(o.data);bm.free()
        if not o.data.uv_layers:
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.015)
            bpy.ops.object.mode_set(mode="OBJECT")
        o.hide_set(was_hidden)
    bpy.context.view_layer.update()
    coords=[o.matrix_world@Vector(c) for o in g.CHAR.all_objects if o.type=="MESH" for c in o.bound_box]
    low=min(v.z for v in coords);high=max(v.z for v in coords)
    SCALE=1.8/(high-low)
    for o in list(g.CHAR.all_objects):
        if o.type!="MESH":continue
        # Bake world-space geometry to make skinning reproducible.
        mat=o.matrix_world.copy()
        for v in o.data.vertices:
            co=mat@v.co;co.z-=low;v.co=co*SCALE
        if o.data.shape_keys:
            for key in o.data.shape_keys.key_blocks:
                for v in key.data:
                    co=mat@v.co;co.z-=low;v.co=co*SCALE
        o.matrix_world.identity()
        o["component"]="Viajero editable"
    bpy.context.scene["factor_escala"]=SCALE
    bpy.context.scene["suelo_origen"]=low
    # Native library: shader nodes preserved, with no external texture dependency.
    bpy.data.libraries.write(str(ROOT/"assets/materiales/viajero_materiales.blend"),set(M.values()),fake_user=True)
    save("09_materiales.blend")
    return low


def rigging(low):
    g.COL=g.collection("13_Rig")
    data=bpy.data.armatures.new("Esqueleto_Viajero")
    rig=bpy.data.objects.new("RIG_Viajero",data);g.COL.objects.link(rig)
    rig.show_in_front=True;data.display_type="OCTAHEDRAL"
    g.activate(rig);bpy.ops.object.mode_set(mode="EDIT")
    def pos(p):return Vector((p[0],p[1],p[2]-low))*SCALE
    def bone(name,a,b,parent=None):
        eb=data.edit_bones.new(name);eb.head=pos(a);eb.tail=pos(b)
        eb.align_roll(Vector((0,0,1)) if name.startswith("eye.") else Vector((0,1,0)))
        if parent:eb.parent=data.edit_bones[parent]
        return eb
    bone("root",(0,0,0),(0,0,.18))
    bone("pelvis",(0,0,.88),(0,0,1.06),"root")
    bone("spine",(0,0,1.06),(0,0,1.29),"pelvis")
    bone("chest",(0,0,1.29),(0,0,1.48),"spine")
    bone("neck",(0,0,1.48),(0,.008,1.59),"chest")
    bone("head",(0,.008,1.59),(0,.013,1.78),"neck")
    bone("bag",(.254,.017,1.01),(.254,.017,.84),"pelvis")
    for sign,side in [(1,"L"),(-1,"R")]:
        bone("clavicle."+side,(sign*.035,0,1.46),(sign*.205,0,1.465),"chest")
        bone("upper_arm."+side,(sign*.205,0,1.465),(sign*.352,0,1.27),"clavicle."+side)
        bone("forearm."+side,(sign*.352,0,1.27),(sign*.461,-.003,1.124),"upper_arm."+side)
        bone("hand."+side,(sign*.461,-.003,1.124),(sign*.50,-.003,1.06),"forearm."+side)
        bone("eye."+side,(sign*.039,-.08,1.685),(sign*.039,-.15,1.685),"head")
        bone("thigh."+side,(sign*.105,0,.90),(sign*.105,-.01,.49),"pelvis")
        bone("shin."+side,(sign*.105,-.01,.49),(sign*.105,.005,.10),"thigh."+side)
        bone("foot."+side,(sign*.105,.005,.10),(sign*.105,-.145,.045),"shin."+side)
        bone("toe."+side,(sign*.105,-.145,.045),(sign*.105,-.18,.045),"foot."+side)
        bone("cloth."+side,(sign*.16,-.14,1.04),(sign*.18,-.15,.67),"pelvis")
        for finger in ["thumb","index","middle","ring","pinky"]:
            a,b,c=FINGERS[(finger,side)]
            bone(finger+".01."+side,a,b,"hand."+side)
            bone(finger+".02."+side,b,b.lerp(c,.6),finger+".01."+side)
            bone(finger+".03."+side,b.lerp(c,.6),c,finger+".02."+side)
    bpy.ops.object.mode_set(mode="OBJECT")
    # Controls are native FK bones, clearly grouped by function.
    for name in ["Cuerpo FK","Manos","Rostro","Telas y bolso"]:
        data.collections.new(name)
    for b in data.bones:
        group="Manos" if any(f in b.name for f in ["thumb","index","middle","ring","pinky"]) else (
            "Rostro" if b.name.startswith("eye") else
            "Telas y bolso" if b.name.startswith(("cloth","bag")) else "Cuerpo FK")
        data.collections[group].assign(b)
    def distance(p,b):
        a=b.head_local;t=b.tail_local;v=t-a
        fac=max(0,min(1,(p-a).dot(v)/v.length_squared))
        return (p-(a+fac*v)).length
    def candidates(p,o):
        x,y,z=p/SCALE+Vector((0,0,low));side="L" if x>0 else "R"
        if o.name.startswith(("Pantalon.","Costura_pantalon.")):
            return ["pelvis","thigh."+side,"shin."+side]
        if o.name.startswith(("Abrigo_manga","Camisa_manga","Puno_arremangado")):
            return ["clavicle."+side,"upper_arm."+side,"forearm."+side]
        if o.name != "Cuerpo":
            return ["pelvis","spine","chest","neck"]
        if z<.95:
            return ["pelvis","thigh."+side,"shin."+side,"foot."+side]
        if abs(x)>.19 and z>1.02:
            return ["chest","clavicle."+side,"upper_arm."+side,"forearm."+side,"hand."+side]
        return ["pelvis","spine","chest","neck"]
    for o in list(g.CHAR.all_objects):
        if o.type!="MESH":continue
        bind=o.get("bind")
        groups={}
        def assign(i,name,weight):
            if name not in groups:groups[name]=o.vertex_groups.new(name=name)
            groups[name].add([i],weight,"REPLACE")
        for v in o.data.vertices:
            if bind and ".01." in bind and o.name.startswith("Dedo_"):
                choices=[bind,bind.replace(".01.",".02."),bind.replace(".01.",".03.")]
            elif bind:
                assign(v.index,bind,1);continue
            elif o.name.startswith(("Abrigo","Ribete_abrigo","Costura_espalda","Bolsillo_abrigo")) and v.co.z/SCALE+low<1.10:
                assign(v.index,"pelvis",1);continue
            else:
                choices=candidates(v.co,o)
            near=sorted([(distance(v.co,data.bones[n]),n) for n in choices])[:2]
            weights=[1/(d+.012)**5 for d,n in near];total=sum(weights)
            for (d,n),w in zip(near,weights):assign(v.index,n,w/total)
        mod=o.modifiers.new("Deformacion Viajero","ARMATURE");mod.object=rig
        # Deform coarse topology before subdividing.
        was_hidden=o.hide_get();o.hide_set(False)
        g.activate(o)
        if list(o.modifiers).index(mod)>0:
            bpy.ops.object.modifier_move_up(modifier=mod.name)
        o.hide_set(was_hidden)
        o.parent=rig
    rig["uso"]="Modo Pose: rotar huesos FK. Acciones en Dope Sheet / Action Editor."
    rig["limitacion"]="Sin IK ni simulación de tela; revisar colisiones al cambiar poses."
    expressions()
    actions(rig)
    save("10_rigging.blend")
    return rig


def expressions():
    # Eyelid meshes have a genuine blink target. Eyes remain independent rig objects.
    for side in ["L","R"]:
        skin=bpy.data.objects["Parpado_piel."+side]
        skin.shape_key_add(name="Basis");closed=skin.shape_key_add(name="Parpadeo")
        closed.value=0
        for i,v in enumerate(closed.data):
            t=(i//25)/3;a=math.pi*(i%25)/24
            v.co.z-=.016*SCALE*(1-t)*math.sin(a)
        o=bpy.data.objects["Parpado_sup."+side]
        o.shape_key_add(name="Basis");k=o.shape_key_add(name="Parpadeo")
        k.value=0
        for v in k.data:
            x0=(.039 if side=="L" else -.039)*SCALE
            rel=min(1,abs((v.co.x-x0)/(.02*SCALE)))
            v.co.z-=.016*SCALE*math.sqrt(max(0,1-rel*rel))
        brow=bpy.data.objects["Ceja."+side]
        brow.shape_key_add(name="Basis")
        for name,dz in [("Sorpresa",.009),("Reflexion",-.004)]:
            k=brow.shape_key_add(name=name)
            k.value=0
            for v in k.data:v.co.z+=dz*SCALE


def actions(rig):
    # Every action is one held pose at frames 1–24; explicitly not a walk cycle.
    recipes={
        "01_A_pose":{},
        "02_T_pose":{"upper_arm.L":(0,0,-52),"upper_arm.R":(0,0,52)},
        "03_Brazos_elevados":{"upper_arm.L":(0,0,-120),"upper_arm.R":(0,0,120)},
        "04_Brazos_delante":{"upper_arm.L":(-65,0,-25),"upper_arm.R":(-65,0,25)},
        "05_Codos_flexionados":{"forearm.L":(-75,0,0),"forearm.R":(-75,0,0)},
        "06_Paso_caminata":{"thigh.L":(-20,0,0),"thigh.R":(18,0,0),"shin.R":(25,0,0),
                            "upper_arm.L":(12,0,20),"upper_arm.R":(-12,0,-20)},
        "07_Sentado_prueba":{"thigh.L":(-80,0,0),"thigh.R":(-80,0,0),
                             "shin.L":(85,0,0),"shin.R":(85,0,0)},
        "08_Agachado_prueba":{"thigh.L":(-48,0,0),"thigh.R":(-48,0,0),
                              "shin.L":(70,0,0),"shin.R":(70,0,0),"spine":(20,0,0)},
        "09_Giro_torso":{"spine":(0,25,0),"chest":(0,12,0)},
        "10_Giro_cabeza":{"head":(0,25,0)},
        "11_Sorpresa":{"head":(-8,0,0),"forearm.L":(-30,0,0)},
        "12_Reflexion":{"head":(10,10,0),"forearm.R":(-65,0,0)},
        "13_Presentacion":{"upper_arm.L":(0,0,25),"upper_arm.R":(0,0,-25),
                           "forearm.L":(-5,0,0),"forearm.R":(-9,0,0),"head":(0,0,-3)},
    }
    rig.animation_data_create()
    for name,recipe in recipes.items():
        rig.animation_data.action=None
        for b in rig.pose.bones:
            b.rotation_mode="XYZ";b.rotation_euler=(0,0,0);b.location=(0,0,0)
        for nameb,angles in recipe.items():
            rig.pose.bones[nameb].rotation_euler=tuple(math.radians(v) for v in angles)
        for b in rig.pose.bones:
            b.keyframe_insert("rotation_euler",frame=1,group=b.name)
            b.keyframe_insert("rotation_euler",frame=24,group=b.name)
        act=rig.animation_data.action;act.name=name;act.use_fake_user=True
    rig.animation_data.action=bpy.data.actions["01_A_pose"]
    bpy.context.scene.frame_set(1)


def setup_world():
    s=bpy.context.scene
    if not s.world:s.world=bpy.data.worlds.new("Ambiente_estudio")
    s.world.use_nodes=True
    nodes=s.world.node_tree.nodes;links=s.world.node_tree.links
    nodes.clear()
    illumination=nodes.new("ShaderNodeBackground")
    illumination.inputs[0].default_value=(.20,.25,.33,1)
    illumination.inputs[1].default_value=.3
    backdrop=nodes.new("ShaderNodeBackground")
    backdrop.inputs[0].default_value=(.004,.006,.009,1)
    rays=nodes.new("ShaderNodeLightPath")
    mix=nodes.new("ShaderNodeMixShader")
    output=nodes.new("ShaderNodeOutputWorld")
    links.new(rays.outputs["Is Camera Ray"],mix.inputs[0])
    links.new(illumination.outputs[0],mix.inputs[1])
    links.new(backdrop.outputs[0],mix.inputs[2])
    links.new(mix.outputs[0],output.inputs["Surface"])


def studio(rig):
    g.COL=g.collection("ESTUDIO")
    floor=g.material("Estudio_tinta",(.026,.034,.046),.8)
    g.mesh("Suelo",[(-100,-100,-.002),(100,-100,-.002),(100,100,-.002),(-100,100,-.002)],
           [(0,1,2,3)],floor)
    s=bpy.context.scene
    setup_world()
    for name,loc,power,size,color in [
        ("Key — calida",(-2.3,-3.2,3.6),450,2.5,(1,.80,.64)),
        ("Fill — fria",(2.5,-1.8,2.2),240,2.2,(.63,.77,1)),
        ("Rim — contorno",(.6,1.6,2.8),600,1.6,(1,.78,.51))]:
        d=bpy.data.lights.new(name,"AREA");d.energy=power;d.shape="DISK";d.size=size;d.color=color
        o=bpy.data.objects.new(name,d);g.COL.objects.link(o);o.location=loc
        o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat("-Z","Y").to_euler()
    g.camera("CAM_Frente",(0,-5,.92),(0,0,.92),2.12)
    g.camera("CAM_Perfil",(-5,0,.92),(0,0,.92),2.12)
    g.camera("CAM_Espalda",(0,5,.92),(0,0,.92),2.12)
    g.camera("CAM_Tres_cuartos",(2.8,-5,2.0),(0,0,.91),2.18)
    g.camera("CAM_Rostro",(.45,-2.5,1.82),(0,-.02,1.65),.46)
    g.camera("CAM_Talisman",(-.10,-2,1.05),(-.06,-.16,.975*SCALE),.19)
    g.camera("CAM_Estudio",(4,-6,4),(0,0,1),5.4)
    s.camera=bpy.data.objects["CAM_Tres_cuartos"]
    s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=True
    prefs=bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type="OPTIX";prefs.get_devices()
        gpu=[d for d in prefs.devices if d.type=="OPTIX"]
        for d in prefs.devices:d.use=d in gpu
        s.cycles.device="GPU" if gpu else "CPU"
        print("RENDER_DEVICE",[(d.name,d.type,d.use) for d in prefs.devices],flush=True)
    except Exception as e:
        print("GPU fallback",repr(e),flush=True);s.cycles.device="CPU"
    s.render.resolution_x=1600;s.render.resolution_y=2000;s.render.resolution_percentage=100
    s.render.image_settings.file_format="PNG"
    s.view_settings.view_transform="AgX"
    s.render.film_transparent=False
    s.render.image_settings.color_mode="RGBA"
    # The saved file opens framed on the character.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=="VIEW_3D":
                area.spaces.active.region_3d.view_distance=2.8
                area.spaces.active.region_3d.view_location=(0,0,.95)
                area.spaces.active.shading.type="MATERIAL"
    g.activate(rig)
    s.camera=bpy.data.objects["CAM_Tres_cuartos"]
    bpy.ops.file.pack_all()
    save("personaje_final.blend")


def render_view(camera,path,size=(1200,1600),action="01_A_pose",samples=48):
    s=bpy.context.scene;rig=bpy.data.objects["RIG_Viajero"]
    rig.animation_data.action=bpy.data.actions[action];s.frame_set(1)
    s.camera=bpy.data.objects[camera]
    s.render.resolution_x,s.render.resolution_y=size;s.cycles.samples=samples
    s.render.filepath=str(ROOT/path)
    bpy.ops.render.render(write_still=True)


def main():
    setup();face();hair();clothing_base();clothing();accessories()
    low=prepare_meshes();rig=rigging(low);studio(rig)
    args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    if "--preview" in args:
        render_view("CAM_Tres_cuartos","renders/final/preview.png",(850,1100),samples=24)
        render_view("CAM_Rostro","renders/rostro/preview.png",(850,850),samples=24)
    if "--render" in args:
        sys.path.insert(0,str(ROOT/"scripts"))
        from render_viajero import render_all
        render_all()
    print("VIAJERO_BUILD_OK",flush=True)


if __name__=="__main__":
    main()
