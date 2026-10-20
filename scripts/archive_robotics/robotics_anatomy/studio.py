"""
scripts/robotics_anatomy/studio.py
Entorno de estudio fotográfico: Ciclorama curvado, iluminación 3-puntos cinemática,
cámara con constraint Track-To y renderizador OptiX en Cycles.
"""

import bpy
import os
import math

def setup_studio_cyclorama(col):
    mesh = bpy.data.meshes.new("Cyclorama_Mesh")
    obj = bpy.data.objects.new("Studio_Cyclorama", mesh)
    col.objects.link(obj)

    verts = []
    faces = []
    profile_pts = [(-6.0, 0.0), (1.2, 0.0)]
    for i in range(1, 15):
        angle = (math.pi / 2.0) * (i / 15.0)
        py = 1.2 + 2.0 * (1.0 - math.cos(angle))
        pz = 2.0 * math.sin(angle)
        profile_pts.append((py, pz))
    profile_pts.append((3.2, 5.2))

    n_pts = len(profile_pts)
    for y, z in profile_pts:
        verts.append((-8.0, y, z))
        verts.append((8.0, y, z))

    for i in range(n_pts - 1):
        v0 = i * 2
        v1 = i * 2 + 1
        v2 = (i + 1) * 2 + 1
        v3 = (i + 1) * 2
        faces.append((v0, v1, v2, v3))

    mesh.from_pydata(verts, [], faces)
    mesh.update()

    mat_cyc = bpy.data.materials.new("Mat_Studio_Cyclorama")
    mat_cyc.use_nodes = True
    cbsdf = mat_cyc.node_tree.nodes.get("Principled BSDF")
    if cbsdf:
        cbsdf.inputs["Base Color"].default_value = (0.18, 0.20, 0.24, 1.0)
        cbsdf.inputs["Roughness"].default_value = 0.65
    obj.data.materials.append(mat_cyc)

    for p in mesh.polygons:
        p.use_smooth = True
    return obj

def setup_studio_lighting(col):
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World_Studio")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.07, 0.08, 0.10, 1.0)
        bg_node.inputs["Strength"].default_value = 0.55

    # 1. Key Light (Luz principal cálida a 45 grados)
    bpy.ops.object.light_add(type='SPOT', location=(2.6, -4.2, 3.4))
    key = bpy.context.active_object
    key.name = "Key_Light_Studio"
    key.data.energy = 1100
    key.data.spot_size = math.radians(72)
    key.data.spot_blend = 0.40
    key.data.color = (1.0, 0.97, 0.92)
    col.objects.link(key)

    # 2. Fill Light (Luz difusa de relleno suave contralateral)
    bpy.ops.object.light_add(type='AREA', location=(-3.4, -3.2, 1.8))
    fill = bpy.context.active_object
    fill.name = "Fill_Light_Studio"
    fill.data.energy = 450
    fill.data.size = 3.5
    fill.data.color = (0.78, 0.88, 1.0)
    col.objects.link(fill)

    # 3. Rim / Kicker Light (Luz trasera de silueta)
    bpy.ops.object.light_add(type='SPOT', location=(0.0, 3.4, 3.2))
    rim = bpy.context.active_object
    rim.name = "Rim_Light_Studio"
    rim.data.energy = 850
    rim.data.spot_size = math.radians(60)
    rim.data.color = (0.80, 0.94, 1.0)
    col.objects.link(rim)

def setup_studio_camera(col, target_z=0.90, view="front", lens=40):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, target_z))
    target_empty = bpy.context.active_object
    target_empty.name = "Cam_LookAt_Target"
    col.objects.link(target_empty)

    if view == "front":
        cam_loc = (0.0, -4.8, 0.92)
    elif view == "34":
        cam_loc = (2.4, -4.8, 1.35)
    else:
        cam_loc = (0.0, -4.8, 0.92)

    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.active_object
    cam.name = f"Cam_Studio_{view}"
    cam.data.lens = lens
    cam.data.clip_start = 0.1
    cam.data.clip_end = 100.0

    track = cam.constraints.new(type='TRACK_TO')
    track.target = target_empty
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    bpy.context.scene.camera = cam
    col.objects.link(cam)
    return cam

def render_and_save(output_image_path, blend_path=None, samples=128):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        for d in prefs.get_devices_for_type("OPTIX"):
            d.use = True
        print("[+] OptiX GPU activo para render.")
    except Exception as e:
        print(f"[*] GPU notice: {e}")

    scene.cycles.samples = samples
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = output_image_path

    bpy.ops.render.render(write_still=True)
    print(f"[✓] Render guardado exitosamente → {output_image_path}")

    if blend_path:
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[✓] Archivo .blend guardado → {blend_path}")
