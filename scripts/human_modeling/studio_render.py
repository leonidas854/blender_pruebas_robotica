"""
scripts/human_modeling/studio_render.py
Estudio fotográfico y renderizado cinemático OptiX para el molde humano de Leonidas.
"""

import bpy
import os
import math

def setup_human_studio(col):
    # 1. Ciclorama de estudio curvado oscuro (estilo fondo de referencia)
    mesh = bpy.data.meshes.new("Studio_Cyc_Mesh")
    obj = bpy.data.objects.new("Studio_Cyclorama", mesh)
    col.objects.link(obj)

    verts = []
    faces = []
    profile_pts = [(-6.0, 0.0), (1.5, 0.0)]
    for i in range(1, 15):
        angle = (math.pi / 2.0) * (i / 15.0)
        py = 1.5 + 2.0 * (1.0 - math.cos(angle))
        pz = 2.0 * math.sin(angle)
        profile_pts.append((py, pz))
    profile_pts.append((3.5, 5.5))

    n_pts = len(profile_pts)
    for y, z in profile_pts:
        verts.append((-10.0, y, z))
        verts.append((10.0, y, z))

    for i in range(n_pts - 1):
        v0 = i * 2
        v1 = i * 2 + 1
        v2 = (i + 1) * 2 + 1
        v3 = (i + 1) * 2
        faces.append((v0, v1, v2, v3))

    mesh.from_pydata(verts, [], faces)
    mesh.update()

    mat_cyc = bpy.data.materials.new("Mat_Studio_DarkCyc")
    mat_cyc.use_nodes = True
    cbsdf = mat_cyc.node_tree.nodes.get("Principled BSDF")
    if cbsdf:
        cbsdf.inputs["Base Color"].default_value = (0.05, 0.06, 0.07, 1.0)
        cbsdf.inputs["Roughness"].default_value = 0.70
    obj.data.materials.append(mat_cyc)
    for p in mesh.polygons:
        p.use_smooth = True

    # 2. Entorno mundial suave
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World_Studio")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.03, 0.035, 0.045, 1.0)
        bg.inputs["Strength"].default_value = 0.40

    # 3. Esquema de Iluminación 3-Puntos de Escultura
    bpy.ops.object.light_add(type='SPOT', location=(2.8, -4.2, 3.4))
    key = bpy.context.active_object
    key.name = "Key_Light"
    key.data.energy = 1150
    key.data.spot_size = math.radians(72)
    key.data.spot_blend = 0.45
    key.data.color = (1.0, 0.98, 0.94)
    col.objects.link(key)

    bpy.ops.object.light_add(type='AREA', location=(-3.2, -3.2, 1.8))
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = 420
    fill.data.size = 3.5
    fill.data.color = (0.80, 0.88, 1.0)
    col.objects.link(fill)

    bpy.ops.object.light_add(type='SPOT', location=(0.0, 3.6, 3.2))
    rim = bpy.context.active_object
    rim.name = "Rim_Light"
    rim.data.energy = 880
    rim.data.spot_size = math.radians(60)
    rim.data.color = (0.82, 0.92, 1.0)
    col.objects.link(rim)

def setup_camera(col, target_z=0.90, view="front", lens=40, dist=4.8):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, target_z))
    target = bpy.context.active_object
    target.name = f"Cam_Target_{view}"
    col.objects.link(target)

    if view == "front":
        cam_loc = (0.0, -dist, 0.92)
    elif view == "34":
        cam_loc = (2.4, -dist, 1.25)
    elif view == "comparison":
        cam_loc = (0.0, -dist * 1.25, 0.92)
    else:
        cam_loc = (0.0, -dist, 0.92)

    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.active_object
    cam.name = f"Cam_{view}"
    cam.data.lens = lens

    track = cam.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    bpy.context.scene.camera = cam
    col.objects.link(cam)
    return cam

def render_human_views(output_path, blend_path=None, samples=128):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        for d in prefs.get_devices_for_type("OPTIX"):
            d.use = True
        print("[+] OptiX GPU activo.")
    except Exception as e:
        print(f"[*] GPU notice: {e}")

    scene.cycles.samples = samples
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = output_path

    bpy.ops.render.render(write_still=True)
    print(f"[✓] Render guardado en: {output_path}")

    if blend_path:
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[✓] Archivo .blend guardado en: {blend_path}")
