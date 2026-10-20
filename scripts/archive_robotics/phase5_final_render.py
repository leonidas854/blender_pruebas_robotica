#!/usr/bin/env python3
"""
scripts/phase5_final_render.py
RENDER FINAL CORREGIDO - Cámara correcta + iluminación intensa + exposición
Carga robot_final_phase5.blend y genera renders corregidos.
"""
import bpy
import os
import math
import mathutils

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "character_data")


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_mat(name, color, metallic=0.0, roughness=0.5,
             emission=None, em_str=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        out = nodes.get("Material Output") or nodes.new("ShaderNodeOutputMaterial")
        mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        for n in ["Emission", "Emission Color"]:
            if n in bsdf.inputs:
                bsdf.inputs[n].default_value = (*emission, 1.0)
                break
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = em_str
    return mat


def add_col(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)


def A(obj, mat, col):
    add_col(obj, col)
    if obj.data and hasattr(obj.data, "materials"):
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat
    return obj


def ss(obj, lv=2):
    mod = obj.modifiers.new("S", "SUBSURF")
    mod.levels = lv
    mod.render_levels = lv


def build():
    clear_scene()
    col = bpy.data.collections.new("Robot_Final")
    bpy.context.scene.collection.children.link(col)

    mb    = make_mat("M_Body",   (0.08, 0.09, 0.12), 0.85, 0.25)
    marm  = make_mat("M_Armor",  (0.72, 0.76, 0.82), 0.80, 0.38)
    mcarb = make_mat("M_Carb",   (0.06, 0.06, 0.07), 0.45, 0.55)
    mcyan = make_mat("M_Cyan",   (0.0, 0.88, 1.0),   0.05, 0.04,
                     emission=(0.0, 0.88, 1.0), em_str=9.0)
    mamb  = make_mat("M_Amber",  (1.0, 0.45, 0.05),  0.05, 0.04,
                     emission=(1.0, 0.45, 0.05), em_str=7.0)
    mface = make_mat("M_Face",   (0.62, 0.68, 0.75), 0.68, 0.28)
    mhair = make_mat("M_Hair",   (0.22, 0.14, 0.07), 0.15, 0.70)
    mjt   = make_mat("M_Joint",  (0.06, 0.06, 0.07), 0.60, 0.48)
    mwire = make_mat("M_Wire",   (0.85, 0.32, 0.04), 0.08, 0.80)
    msole = make_mat("M_Sole",   (0.07, 0.07, 0.08), 0.22, 0.70)

    # ─── CABEZA ──────────────────────────────────────────────────────────────
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.46, segments=32, ring_count=24, location=(0,0,1.72))
    hd = bpy.context.active_object; hd.name="Head"; hd.scale=(0.87,0.80,0.95); ss(hd,2); A(hd,mb,col)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,-0.347,1.68))
    fp = bpy.context.active_object; fp.name="FacePlate"; fp.scale=(0.43,0.055,0.50); ss(fp,1); A(fp,mface,col)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,-0.372,1.40))
    jw = bpy.context.active_object; jw.name="Jaw"; jw.scale=(0.30,0.022,0.135); A(jw,marm,col)

    for ex, nm in [(-0.155,"L"),(0.155,"R")]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.058,depth=0.046,vertices=24,location=(ex,-0.377,1.73),rotation=(math.radians(90),0,0))
        A(bpy.context.active_object,mcyan,col).name=f"Eye_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(radius=0.030,depth=0.052,vertices=16,location=(ex,-0.390,1.73),rotation=(math.radians(90),0,0))
        A(bpy.context.active_object,mcyan,col).name=f"EyeIris_{nm}"
        bpy.ops.mesh.primitive_torus_add(major_radius=0.068,minor_radius=0.010,location=(ex,-0.375,1.73),rotation=(math.radians(90),0,0))
        A(bpy.context.active_object,marm,col).name=f"EyeRing_{nm}"

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,-0.382,1.73))
    v = bpy.context.active_object; v.name="Visor"; v.scale=(0.20,0.020,0.033); A(v,mamb,col)

    for ex,nm in [(-0.465,"L"),(0.465,"R")]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.062,depth=0.065,vertices=18,location=(ex,0,1.72),rotation=(0,math.radians(90),0))
        A(bpy.context.active_object,marm,col).name=f"Ear_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(radius=0.020,depth=0.010,vertices=12,location=(ex*1.065,0,1.72),rotation=(0,math.radians(90),0))
        A(bpy.context.active_object,mcyan,col).name=f"EarLED_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(radius=0.012,depth=0.28,vertices=8,location=(ex*0.90,0,2.06))
        A(bpy.context.active_object,mcarb,col).name=f"Ant_{nm}"
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.024,segments=8,ring_count=6,location=(ex*0.90,0,2.21))
        A(bpy.context.active_object,mcyan,col).name=f"AntTip_{nm}"

    # Cabello
    for i,(hx,hy,hz,rx) in enumerate([
        (-0.24,0.27,1.97,0.0),(-0.16,0.29,1.94,0.0),(0.0,0.31,1.96,0.0),(0.16,0.29,1.94,0.0),(0.24,0.27,1.97,0.0),
        (-0.38,0.17,1.80,-0.1),(-0.42,0.09,1.65,-0.15),(-0.40,0.04,1.50,-0.18),
        (0.38,0.17,1.80,0.1),(0.42,0.09,1.65,0.15),(0.40,0.04,1.50,0.18),
        (-0.28,0.24,1.50,0.0),(0.28,0.24,1.50,0.0),(0.0,0.30,1.55,0.0),
        (-0.15,0.28,1.62,0.0),(0.15,0.28,1.62,0.0)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.033,depth=0.17,vertices=8,location=(hx,hy,hz),rotation=(0.12+abs(rx),0,hx*0.4))
        A(bpy.context.active_object,mhair,col).name=f"Hair_{i}"

    # ─── CUELLO ──────────────────────────────────────────────────────────────
    bpy.ops.mesh.primitive_cylinder_add(radius=0.108,depth=0.28,vertices=20,location=(0,0,1.22))
    A(bpy.context.active_object,mcarb,col).name="Neck"
    for z in(1.09,1.20,1.31):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.122,minor_radius=0.016,location=(0,0,z))
        A(bpy.context.active_object,marm,col).name="NeckRing"
    for ox in[-0.06,0.06]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.014,depth=0.20,vertices=8,location=(ox,-0.085,1.22))
        A(bpy.context.active_object,mcarb,col).name="NeckHydro"

    # ─── TORSO ───────────────────────────────────────────────────────────────
    bpy.ops.mesh.primitive_cube_add(size=1.0,location=(0,0,0.76))
    ch=bpy.context.active_object;ch.name="Chest";ch.scale=(0.57,0.27,0.29);ss(ch,1);A(ch,mb,col)
    for ex in[-0.285,0.285]:
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,-0.263,0.90))
        cp=bpy.context.active_object;cp.name="ChestPanel";cp.scale=(0.175,0.028,0.115);A(cp,marm,col)
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,-0.271,0.90))
        A(bpy.context.active_object,mcyan,col).name="ChestLED";bpy.context.active_object.scale=(0.165,0.005,0.008)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.098,depth=0.058,vertices=32,location=(0,-0.265,0.78),rotation=(math.radians(90),0,0))
    A(bpy.context.active_object,mcyan,col).name="PowerCore"
    bpy.ops.mesh.primitive_torus_add(major_radius=0.112,minor_radius=0.014,location=(0,-0.265,0.78),rotation=(math.radians(90),0,0))
    A(bpy.context.active_object,marm,col).name="CoreRing"
    bpy.ops.mesh.primitive_cube_add(size=1.0,location=(0,0,0.43))
    wa=bpy.context.active_object;wa.name="Waist";wa.scale=(0.45,0.23,0.19);ss(wa,1);A(wa,mb,col)
    bpy.ops.mesh.primitive_cube_add(size=1.0,location=(0,-0.241,0.50))
    A(bpy.context.active_object,marm,col).name="AbPlate";bpy.context.active_object.scale=(0.28,0.024,0.21)
    for dz in[-0.06,0.0,0.06]:
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(0,-0.248,0.50+dz))
        A(bpy.context.active_object,mcarb,col).name="AbGrill";bpy.context.active_object.scale=(0.25,0.008,0.014)
    bpy.ops.mesh.primitive_cube_add(size=1.0,location=(0,0,0.07))
    hp=bpy.context.active_object;hp.name="Hips";hp.scale=(0.54,0.25,0.20);ss(hp,1);A(hp,mb,col)
    for ex in[-0.25,0.25]:
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,-0.243,0.07))
        A(bpy.context.active_object,marm,col).name="HipPanel";bpy.context.active_object.scale=(0.155,0.025,0.145)

    # ─── HOMBROS ─────────────────────────────────────────────────────────────
    for ex,nm in[(-0.70,"L"),(0.70,"R")]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.172,segments=22,ring_count=16,location=(ex,0,0.88))
        sh=bpy.context.active_object;sh.name=f"Sh_{nm}";sh.scale=(1.0,0.76,0.76);ss(sh,1);A(sh,marm,col)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.055,depth=0.038,vertices=16,location=(ex*1.155,0,0.88),rotation=(0,math.radians(90),0))
        A(bpy.context.active_object,mcyan,col).name=f"ShLED_{nm}"

    # ─── BRAZOS ──────────────────────────────────────────────────────────────
    for ex,nm in[(-0.82,"L"),(0.82,"R")]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.083,depth=0.46,vertices=18,location=(ex,0,0.60))
        ua=bpy.context.active_object;ua.name=f"UA_{nm}";ss(ua,1);A(ua,mb,col)
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,-0.062,0.68))
        A(bpy.context.active_object,marm,col).name=f"ArmPanel_{nm}";bpy.context.active_object.scale=(0.055,0.010,0.16)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.090,segments=18,ring_count=12,location=(ex,0,0.32))
        A(bpy.context.active_object,mjt,col).name=f"Elbow_{nm}"
        bpy.ops.mesh.primitive_torus_add(major_radius=0.100,minor_radius=0.017,location=(ex,0,0.32))
        A(bpy.context.active_object,marm,col).name=f"ElbowRing_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(radius=0.070,depth=0.42,vertices=16,location=(ex,0,0.07))
        fa=bpy.context.active_object;fa.name=f"FA_{nm}";ss(fa,1);A(fa,mb,col)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.078,minor_radius=0.015,location=(ex,0,-0.15))
        A(bpy.context.active_object,marm,col).name=f"Wrist_{nm}"
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,0,-0.27))
        ha=bpy.context.active_object;ha.name=f"Hand_{nm}";ha.scale=(0.108,0.062,0.135);ss(ha,1);A(ha,marm,col)
        for fi in range(3):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.016,depth=0.046,vertices=8,location=(ex+(fi-1)*0.030,-0.052,-0.335-fi*0.012))
            A(bpy.context.active_object,mcarb,col).name=f"Fing_{nm}_{fi}"

    # ─── PIERNAS ─────────────────────────────────────────────────────────────
    for ex,nm in[(-0.21,"L"),(0.21,"R")]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.122,depth=0.52,vertices=20,location=(ex,0,-0.52))
        th=bpy.context.active_object;th.name=f"Th_{nm}";ss(th,1);A(th,mb,col)
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,-0.100,-0.46))
        A(bpy.context.active_object,marm,col).name=f"ThPanel_{nm}";bpy.context.active_object.scale=(0.07,0.012,0.18)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.112,segments=18,ring_count=12,location=(ex,0.005,-0.83))
        A(bpy.context.active_object,mjt,col).name=f"Knee_{nm}"
        bpy.ops.mesh.primitive_torus_add(major_radius=0.126,minor_radius=0.017,location=(ex,0,-0.83))
        A(bpy.context.active_object,marm,col).name=f"KneeRing_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(radius=0.022,depth=0.020,vertices=12,location=(ex,-0.112,-0.83),rotation=(math.radians(90),0,0))
        A(bpy.context.active_object,mcyan,col).name=f"KneeLED_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(radius=0.096,depth=0.49,vertices=18,location=(ex,0,-1.12))
        sh=bpy.context.active_object;sh.name=f"Sh_{nm}";ss(sh,1);A(sh,mb,col)
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,-0.086,-1.04))
        A(bpy.context.active_object,marm,col).name=f"ShinPanel_{nm}";bpy.context.active_object.scale=(0.065,0.010,0.15)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.103,minor_radius=0.015,location=(ex,0,-1.40))
        A(bpy.context.active_object,marm,col).name=f"Ankle_{nm}"
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,0.09,-1.56))
        ft=bpy.context.active_object;ft.name=f"Foot_{nm}";ft.scale=(0.122,0.210,0.070);ss(ft,1);A(ft,mb,col)
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,0.09,-1.632))
        A(bpy.context.active_object,msole,col).name=f"Sole_{nm}";bpy.context.active_object.scale=(0.124,0.215,0.018)

    # Cables decorativos
    for cx,cy,cz,rx in[(-0.35,-0.08,0.55,0.18),(0.35,-0.08,0.55,0.18),(-0.55,0.0,0.12,0.0),(0.55,0.0,0.12,0.0)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.010,depth=0.18,vertices=6,location=(cx,cy,cz),rotation=(rx,0,0))
        A(bpy.context.active_object,mwire,col).name="Cable"

    # ─── ILUMINACIÓN 3 PUNTOS INTENSA ────────────────────────────────────────
    # Key light - frontal derecha, muy intensa
    bpy.ops.object.light_add(type="SPOT", location=(2.2, -3.5, 2.0))
    key = bpy.context.active_object
    key.name = "Key_Light"
    key.data.energy = 1200.0
    key.data.color = (1.0, 0.94, 0.86)
    key.data.spot_size = math.radians(50)
    key.data.spot_blend = 0.30
    key.rotation_euler = mathutils.Euler((math.radians(55), 0, math.radians(32)), 'XYZ')
    add_col(key, col)

    # Fill light - izquierda, luz fría difusa
    bpy.ops.object.light_add(type="AREA", location=(-3.0, -2.0, 0.5))
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = 600.0
    fill.data.color = (0.50, 0.72, 1.0)
    fill.data.size = 2.0
    fill.rotation_euler = mathutils.Euler((math.radians(15), 0, math.radians(-25)), 'XYZ')
    add_col(fill, col)

    # Rim light - cyan desde atrás
    bpy.ops.object.light_add(type="SPOT", location=(0.0, 4.0, 3.0))
    rim = bpy.context.active_object
    rim.name = "Rim_Light"
    rim.data.energy = 1800.0
    rim.data.color = (0.0, 0.88, 1.0)
    rim.data.spot_size = math.radians(32)
    rim.data.spot_blend = 0.20
    rim.rotation_euler = mathutils.Euler((math.radians(-50), 0, 0), 'XYZ')
    add_col(rim, col)

    # Luz de suelo suave
    bpy.ops.object.light_add(type="POINT", location=(0.0, 0.0, -2.5))
    ground = bpy.context.active_object
    ground.name = "Ground_Bounce"
    ground.data.energy = 200.0
    ground.data.color = (0.3, 0.5, 1.0)
    add_col(ground, col)

    # ─── MUNDO / FONDO ───────────────────────────────────────────────────────
    world = bpy.data.worlds.new("World_SciFi")
    bpy.context.scene.world = world
    world.use_nodes = True
    wn = world.node_tree.nodes
    wn.clear()
    bg = wn.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.010, 0.012, 0.022, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    wo = wn.new("ShaderNodeOutputWorld")
    world.node_tree.links.new(bg.outputs["Background"], wo.inputs["Surface"])

    # ─── CÁMARA FRONTAL (framing completo del personaje) ─────────────────────
    bpy.ops.object.camera_add(location=(0, -5.8, 0.10), rotation=(math.radians(90), 0, 0))
    cam_front = bpy.context.active_object
    cam_front.name = "Cam_Front_Full"
    cam_front.data.lens = 42           # Lente un poco más ancho para encuadrar todo
    bpy.context.scene.camera = cam_front
    add_col(cam_front, col)

    # ─── RENDER CONFIG ───────────────────────────────────────────────────────
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        for d in prefs.get_devices_for_type("OPTIX"):
            d.use = True
        print("[+] RTX 4070 OptiX OK")
    except Exception as e:
        scene.cycles.device = "CPU"
        print(f"[*] CPU: {e}")

    # Exposure correction
    scene.view_settings.exposure = 1.5          # Brighter
    scene.view_settings.gamma = 1.1

    scene.cycles.samples = 256
    scene.cycles.use_denoising = True
    try:
        scene.cycles.denoiser = 'OPTIX'
    except Exception:
        pass
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = "PNG"

    # ── RENDER FRONTAL 1920×1080 ─────────────────────────────────────────────
    out_front = os.path.join(OUTPUT_DIR, "phase5_render_front.png")
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)
    print(f"[✓] RENDER FRONTAL guardado → {out_front}")

    # ── CÁMARA 3/4 PARA RENDER LATERAL ──────────────────────────────────────
    bpy.ops.object.camera_add(
        location=(3.2, -4.0, 0.20),
        rotation=(math.radians(84), 0, math.radians(38)))
    cam_34 = bpy.context.active_object
    cam_34.name = "Cam_34_Final"
    cam_34.data.lens = 44
    bpy.context.scene.camera = cam_34
    add_col(cam_34, col)

    scene.cycles.samples = 256
    out_34 = os.path.join(OUTPUT_DIR, "phase5_render_34view.png")
    scene.render.filepath = out_34
    bpy.ops.render.render(write_still=True)
    print(f"[✓] RENDER 3/4 guardado → {out_34}")

    # ── CAPTURA ESQUEMA LUCES (vista lateral) ────────────────────────────────
    bpy.ops.object.camera_add(location=(8.0, 0, 0), rotation=(math.radians(90), 0, math.radians(90)))
    cam_side = bpy.context.active_object
    cam_side.name = "Cam_Side_Lights"
    cam_side.data.lens = 36
    bpy.context.scene.camera = cam_side
    add_col(cam_side, col)
    scene.cycles.samples = 64
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    out_lights = os.path.join(OUTPUT_DIR, "phase5_lighting_positions.png")
    scene.render.filepath = out_lights
    bpy.ops.render.render(write_still=True)
    print(f"[✓] POSICIÓN DE LUCES guardada → {out_lights}")

    # ── GUARDAR .BLEND ───────────────────────────────────────────────────────
    bpy.context.scene.camera = cam_34
    blend_out = os.path.join(OUTPUT_DIR, "robot_final_phase5.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"[✓] .blend guardado → {blend_out}")
    print("\n═══════════════════════════════════════════════════════")
    print("  FASE 5 COMPLETA — 3 renders + .blend listo")
    print("═══════════════════════════════════════════════════════")


if __name__ == "__main__":
    build()
