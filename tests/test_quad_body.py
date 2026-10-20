import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
col = bpy.data.collections.new("TestQuad")
bpy.context.scene.collection.children.link(col)

# Construir el torso en quads puros mediante anillos de 8 vértices
# Cada anillo define (X, Y, Z) para el lado derecho (X >= 0)
# Vértices del centro en X = 0 (frontal y posterior) para el Mirror modifier

rings = [
    # Anillo 0: Base del cuello (Z = 1.505)
    [(0.000, -0.050, 1.505), (0.040, -0.038, 1.505), (0.058, 0.000, 1.505), (0.040, 0.040, 1.505), (0.000, 0.048, 1.505)],
    # Anillo 1: Clavícula y hombro alto (Z = 1.440)
    [(0.000, -0.095, 1.440), (0.090, -0.080, 1.440), (0.165, -0.010, 1.440), (0.110, 0.065, 1.440), (0.000, 0.075, 1.440)],
    # Anillo 2: Pecho / Pectorales (Z = 1.370)
    [(0.000, -0.125, 1.370), (0.115, -0.115, 1.370), (0.195, -0.015, 1.370), (0.130, 0.075, 1.370), (0.000, 0.085, 1.370)],
    # Anillo 3: Caja torácica baja (Z = 1.260)
    [(0.000, -0.105, 1.260), (0.095, -0.095, 1.260), (0.160, -0.010, 1.260), (0.105, 0.065, 1.260), (0.000, 0.075, 1.260)],
    # Anillo 4: Cintura estrecha (Z = 1.150)
    [(0.000, -0.085, 1.150), (0.075, -0.075, 1.150), (0.122, 0.000, 1.150), (0.080, 0.055, 1.150), (0.000, 0.065, 1.150)],
    # Anillo 5: Caderas / Ilion (Z = 1.020)
    [(0.000, -0.092, 1.020), (0.090, -0.082, 1.020), (0.145, 0.005, 1.020), (0.100, 0.070, 1.020), (0.000, 0.082, 1.020)],
    # Anillo 6: Pelvis y Glúteos (Z = 0.880)
    [(0.000, -0.095, 0.880), (0.105, -0.075, 0.880), (0.160, 0.010, 0.880), (0.115, 0.095, 0.880), (0.000, 0.110, 0.880)],
    # Anillo 7: Entrepierna / Base pélvica (Z = 0.820)
    [(0.000, -0.065, 0.820), (0.075, -0.045, 0.820), (0.115, 0.005, 0.820), (0.075, 0.065, 0.820), (0.000, 0.080, 0.820)],
]

verts = []
faces = []
n_pts = len(rings[0]) # 5 puntos por anillo

for r in rings:
    for pt in r:
        verts.append(pt)

for r_idx in range(len(rings) - 1):
    base_curr = r_idx * n_pts
    base_next = (r_idx + 1) * n_pts
    for i in range(n_pts - 1):
        v1 = base_curr + i
        v2 = base_curr + i + 1
        v3 = base_next + i + 1
        v4 = base_next + i
        faces.append((v1, v2, v3, v4))

mesh = bpy.data.meshes.new("Torso_Half_Mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

obj = bpy.data.objects.new("Torso_Base", mesh)
col.objects.link(obj)

mod_m = obj.modifiers.new("Mirror", "MIRROR")
mod_m.use_axis[0] = True
mod_m.use_clip = True

mod_s = obj.modifiers.new("Subsurf", "SUBSURF")
mod_s.levels = 1

for p in mesh.polygons:
    p.use_smooth = True

print("Torso base generado con quads puros. Caras:", len(faces), "x 2 (Mirror) =", len(faces)*2)
