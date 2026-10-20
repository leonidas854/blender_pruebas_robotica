"""Native Blender geometry and shading tools for the Viajero asset."""
import bpy
import math
from mathutils import Vector

TAU = math.tau
CHAR = None
COL = None


def collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c


def register(o, name, material=None, bone=None):
    o.name = name
    for c in list(o.users_collection):
        c.objects.unlink(o)
    COL.objects.link(o)
    if material:
        o.data.materials.clear()
        o.data.materials.append(material)
    if bone:
        o["bind"] = bone
    if o.type == "MESH":
        for p in o.data.polygons:
            p.use_smooth = True
    return o


def mesh(name, verts, faces, mat, bone=None, sub=0, thick=0):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    o = bpy.data.objects.new(name, data)
    COL.objects.link(o)
    if mat:
        data.materials.append(mat)
    if bone:
        o["bind"] = bone
    for p in data.polygons:
        p.use_smooth = True
    if sub:
        m = o.modifiers.new("Suavizado editable", "SUBSURF")
        m.levels = sub
        m.render_levels = sub
    if thick:
        m = o.modifiers.new("Grosor de tejido", "SOLIDIFY")
        m.thickness = thick
        m.offset = 0
    return o


def loft(name, rings, mat, n=48, start=0, end=TAU, sub=1, thick=0, bone=None, folds=0):
    """Rings: (z, rx, ry, cy, cx), theta=0 at front, open when end-start<2pi."""
    closed = abs(end - start - TAU) < .001
    cols = n if closed else n + 1
    vs = []
    for j, (z, rx, ry, cy, cx) in enumerate(rings):
        for i in range(cols):
            a = start + (end-start)*i/n
            f = folds * (math.sin(7*a+j*1.8)+.45*math.sin(13*a-j)) * math.sin(math.pi*j/(len(rings)-1))
            vs.append((cx+(rx+f)*math.sin(a), cy-(ry+f)*math.cos(a), z+.4*f))
    fs = []
    for j in range(len(rings)-1):
        for i in range(n if closed else cols-1):
            a=j*cols+i; b=j*cols+(i+1)%cols
            fs.append((a,b,b+cols,a+cols))
    return mesh(name, vs, fs, mat, bone, sub, thick)


def tube(name, points, radii, mat, bone=None, n=16, sub=1):
    vs = []
    pts = [Vector(p) for p in points]
    for j,p in enumerate(pts):
        tangent=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized()
        u=tangent.cross(Vector((0,1,0))).normalized()
        if u.length < .1:
            u=tangent.cross(Vector((1,0,0))).normalized()
        v=tangent.cross(u).normalized()
        r=radii[j]
        r1,r2=(r,r) if isinstance(r,(float,int)) else r
        for i in range(n):
            a=TAU*i/n
            vs.append(p+u*(r1*math.cos(a))+v*(r2*math.sin(a)))
    fs=[]
    for j in range(len(pts)-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n
            fs.append((a,b,b+n,a+n))
    fs.extend([tuple(reversed(range(n))), tuple((len(pts)-1)*n+i for i in range(n))])
    return mesh(name,vs,fs,mat,bone,sub)


def curve(name, points, radius, mat, bone=None, cyclic=False):
    data=bpy.data.curves.new(name, "CURVE")
    data.dimensions="3D"
    data.resolution_u=12
    data.bevel_depth=radius
    data.bevel_resolution=2
    spline=data.splines.new("BEZIER")
    spline.bezier_points.add(len(points)-1)
    for p,co in zip(spline.bezier_points,points):
        p.co=co
        p.handle_left_type="AUTO"
        p.handle_right_type="AUTO"
    spline.use_cyclic_u=cyclic
    o=bpy.data.objects.new(name,data)
    COL.objects.link(o)
    data.materials.append(mat)
    if bone:o["bind"]=bone
    return o


def ellipse(name, center, rx, rz, radius, mat, bone=None):
    x,y,z=center
    return curve(name,[(x+rx*math.cos(TAU*i/48),y,z+rz*math.sin(TAU*i/48)) for i in range(48)],
                 radius,mat,bone,True)


def sphere(name, loc, scale, mat, bone=None, segments=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc)
    o=register(bpy.context.object,name,mat,bone)
    o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return o


def box(name,loc,dims,mat,bevel=.008,bone=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=register(bpy.context.object,name,mat,bone)
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    m=o.modifiers.new("Bordes redondeados","BEVEL");m.width=bevel;m.segments=3
    o.modifiers.new("Normales","WEIGHTED_NORMAL")
    return o


def panel(name, outline, mat, bone=None, thick=.004, bevel=.003):
    o=mesh(name,outline,[tuple(range(len(outline)))],mat,bone,thick=thick)
    if bevel:
        m=o.modifiers.new("Borde de prenda","BEVEL");m.width=bevel;m.segments=3
    return o


def ribbon(name, points, width, mat, bone=None, thickness=.004):
    pts=[Vector(p) for p in points];vs=[]
    for j,p in enumerate(pts):
        t=pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]
        across=t.cross(Vector((0,1,0))).normalized()*width/2
        vs.extend([p-across,p+across])
    fs=[(2*j,2*j+1,2*j+3,2*j+2) for j in range(len(pts)-1)]
    return mesh(name,vs,fs,mat,bone,sub=1,thick=thickness)


def buckle(name,center,w,h,mat,bone=None):
    x,y,z=center
    pts=[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)]
    o=curve(name,pts,.0025,mat,bone,True)
    curve(name+"_aguja",[(x,y-.001,z-h/2),(x,y-.001,z+h*.3)],.0014,mat,bone)
    return o


def material(name,color,rough=.6,metal=0,kind=None):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    ns=m.node_tree.nodes;ls=m.node_tree.links
    bs=ns.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    bs.location=(440,100)
    ns.get("Material Output").location=(740,100)
    if kind and kind != "skin":
        tex=ns.new("ShaderNodeTexCoord");tex.location=(-800,0)
        noise=ns.new("ShaderNodeTexNoise");noise.location=(-580,180)
        noise.inputs["Scale"].default_value=90 if kind=="leather" else 35
        noise.inputs["Detail"].default_value=3
        ls.new(tex.outputs["Generated"],noise.inputs["Vector"])
        ramp=ns.new("ShaderNodeValToRGB");ramp.location=(-280,200)
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(*(c*.68 for c in color),1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(*(min(c*1.18+.006,1) for c in color),1)
        ls.new(noise.outputs["Fac"],ramp.inputs[0]);ls.new(ramp.outputs["Color"],bs.inputs["Base Color"])
        fine=ns.new("ShaderNodeTexNoise");fine.location=(-570,-150)
        fine.inputs["Scale"].default_value=420 if kind=="fabric" else 220
        fine.inputs["Detail"].default_value=2
        ls.new(tex.outputs["Generated"],fine.inputs["Vector"])
        bump=ns.new("ShaderNodeBump");bump.location=(170,-100)
        bump.inputs["Strength"].default_value=.16
        bump.inputs["Distance"].default_value=.0005 if kind=="fabric" else .00025
        ls.new(fine.outputs["Fac"],bump.inputs["Height"]);ls.new(bump.outputs["Normal"],bs.inputs["Normal"])
    if kind=="fabric":
        bs.inputs["Sheen Weight"].default_value=.18
    if kind=="skin":
        bs.inputs["Subsurface Weight"].default_value=.065
        bs.inputs["Subsurface Radius"].default_value=(1,.4,.2)
    return m


def activate(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active=o


def camera(name,loc,target,ortho=2.2):
    d=bpy.data.cameras.new(name);d.type="ORTHO";d.ortho_scale=ortho
    o=bpy.data.objects.new(name,d);COL.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
    return o
