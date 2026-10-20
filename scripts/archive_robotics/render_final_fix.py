#!/usr/bin/env python3
"""
scripts/render_final_fix.py
RENDER DEFINITIVO — Cámara correctamente orientada con Track-To
encuadrando completamente al personaje robótico.
"""
import bpy
import os
import math
import mathutils

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "character_data")


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, color, metallic=0.0, roughness=0.5, emission=None, em_str=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = m.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        out = m.node_tree.nodes.new("ShaderNodeOutputMaterial")
        m.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
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
    return m


def ac(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)


def P(obj, m, col):
    ac(obj, col)
    if obj.data and hasattr(obj.data, "materials"):
        if obj.data.materials:
            obj.data.materials[0] = m
        else:
            obj.data.materials.append(m)
    return obj


def ss(obj, lv=1):
    mod = obj.modifiers.new("S", "SUBSURF")
    mod.levels = lv
    mod.render_levels = lv + 1


def look_at(obj, target_location):
    """Orientar objeto a un punto objetivo."""
    direction = mathutils.Vector(target_location) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def build():
    clear_scene()
    col = bpy.data.collections.new("Robot")
    bpy.context.scene.collection.children.link(col)

    mb    = mat("Body",   (0.09,0.10,0.14), 0.86, 0.24)
    marm  = mat("Armor",  (0.74,0.78,0.84), 0.82, 0.36)
    mcarb = mat("Carbon", (0.07,0.07,0.08), 0.46, 0.54)
    mcyan = mat("Cyan",   (0.0,0.88,1.0),   0.05, 0.04,
                emission=(0.0,0.88,1.0), em_str=10.0)
    mamb  = mat("Amber",  (1.0,0.46,0.06),  0.05, 0.04,
                emission=(1.0,0.46,0.06), em_str=8.0)
    mface = mat("Face",   (0.64,0.70,0.76), 0.70, 0.26)
    mhair = mat("Hair",   (0.24,0.15,0.08), 0.16, 0.68)
    mjt   = mat("Joint",  (0.07,0.07,0.08), 0.62, 0.46)
    mwire = mat("Wire",   (0.88,0.35,0.04), 0.08, 0.80)
    msole = mat("Sole",   (0.08,0.08,0.09), 0.20, 0.72)

    # ── CABEZA ────────────────────────────────────────────────────────────
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.46,segments=32,ring_count=24,location=(0,0,1.72))
    hd=bpy.context.active_object; hd.name="Head"; hd.scale=(0.87,0.80,0.95); ss(hd,2); P(hd,mb,col)

    bpy.ops.mesh.primitive_cube_add(size=1.0,location=(0,-0.347,1.68))
    P(bpy.context.active_object,mface,col).name="FacePlate"
    bpy.context.active_object.scale=(0.43,0.055,0.50); ss(bpy.context.active_object,1)

    bpy.ops.mesh.primitive_cube_add(size=1.0,location=(0,-0.372,1.40))
    P(bpy.context.active_object,marm,col).name="Jaw"; bpy.context.active_object.scale=(0.30,0.022,0.135)

    for ex,nm in[(-0.155,"L"),(0.155,"R")]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.058,depth=0.046,vertices=24,location=(ex,-0.377,1.73),rotation=(math.radians(90),0,0))
        P(bpy.context.active_object,mcyan,col).name=f"Eye_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(radius=0.030,depth=0.052,vertices=16,location=(ex,-0.392,1.73),rotation=(math.radians(90),0,0))
        P(bpy.context.active_object,mcyan,col).name=f"EyeIris_{nm}"
        bpy.ops.mesh.primitive_torus_add(major_radius=0.068,minor_radius=0.010,location=(ex,-0.375,1.73),rotation=(math.radians(90),0,0))
        P(bpy.context.active_object,marm,col).name=f"EyeRing_{nm}"

    bpy.ops.mesh.primitive_cube_add(size=1.0,location=(0,-0.382,1.73))
    P(bpy.context.active_object,mamb,col).name="Visor"; bpy.context.active_object.scale=(0.20,0.020,0.033)

    for ex,nm in[(-0.465,"L"),(0.465,"R")]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.062,depth=0.065,vertices=18,location=(ex,0,1.72),rotation=(0,math.radians(90),0))
        P(bpy.context.active_object,marm,col).name=f"Ear_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(radius=0.020,depth=0.010,vertices=12,location=(ex*1.065,0,1.72),rotation=(0,math.radians(90),0))
        P(bpy.context.active_object,mcyan,col).name=f"EarLED_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(radius=0.012,depth=0.28,vertices=8,location=(ex*0.90,0,2.06))
        P(bpy.context.active_object,mcarb,col).name=f"Ant_{nm}"
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.024,segments=8,ring_count=6,location=(ex*0.90,0,2.22))
        P(bpy.context.active_object,mcyan,col).name=f"AntTip_{nm}"

    # Cabello
    hair_pts=[(-0.24,0.27,1.97,0.0),(-0.16,0.29,1.94,0.0),(0.0,0.31,1.96,0.0),(0.16,0.29,1.94,0.0),(0.24,0.27,1.97,0.0),(-0.38,0.17,1.80,-0.1),(-0.42,0.09,1.65,-0.15),(-0.40,0.04,1.50,-0.18),(0.38,0.17,1.80,0.1),(0.42,0.09,1.65,0.15),(0.40,0.04,1.50,0.18),(-0.28,0.24,1.50,0.0),(0.28,0.24,1.50,0.0),(0.0,0.30,1.55,0.0),(-0.15,0.28,1.62,0.0),(0.15,0.28,1.62,0.0)]
    for i,(hx,hy,hz,rx) in enumerate(hair_pts):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.033,depth=0.17,vertices=8,location=(hx,hy,hz),rotation=(0.12+abs(rx),0,hx*0.4))
        P(bpy.context.active_object,mhair,col).name=f"Hair_{i}"

    # ── CUELLO ────────────────────────────────────────────────────────────
    bpy.ops.mesh.primitive_cylinder_add(radius=0.108,depth=0.28,vertices=20,location=(0,0,1.22))
    P(bpy.context.active_object,mcarb,col).name="Neck"
    for z in(1.09,1.20,1.31):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.122,minor_radius=0.016,location=(0,0,z))
        P(bpy.context.active_object,marm,col).name="NeckRing"
    for ox in[-0.06,0.06]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.014,depth=0.20,vertices=8,location=(ox,-0.085,1.22))
        P(bpy.context.active_object,mcarb,col).name="NeckHydro"

    # ── TORSO ─────────────────────────────────────────────────────────────
    bpy.ops.mesh.primitive_cube_add(size=1.0,location=(0,0,0.76))
    ch=bpy.context.active_object; ch.name="Chest"; ch.scale=(0.57,0.27,0.29); ss(ch,1); P(ch,mb,col)
    for ex in[-0.285,0.285]:
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,-0.263,0.90))
        P(bpy.context.active_object,marm,col).name="ChestPanel"; bpy.context.active_object.scale=(0.175,0.028,0.115)
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,-0.271,0.90))
        P(bpy.context.active_object,mcyan,col).name="ChestLED"; bpy.context.active_object.scale=(0.165,0.005,0.008)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.098,depth=0.058,vertices=32,location=(0,-0.265,0.78),rotation=(math.radians(90),0,0))
    P(bpy.context.active_object,mcyan,col).name="PowerCore"
    bpy.ops.mesh.primitive_torus_add(major_radius=0.112,minor_radius=0.014,location=(0,-0.265,0.78),rotation=(math.radians(90),0,0))
    P(bpy.context.active_object,marm,col).name="CoreRing"
    bpy.ops.mesh.primitive_cube_add(size=1.0,location=(0,0,0.43))
    wa=bpy.context.active_object; wa.name="Waist"; wa.scale=(0.45,0.23,0.19); ss(wa,1); P(wa,mb,col)
    bpy.ops.mesh.primitive_cube_add(size=1.0,location=(0,-0.241,0.50))
    P(bpy.context.active_object,marm,col).name="AbPlate"; bpy.context.active_object.scale=(0.28,0.024,0.21)
    for dz in[-0.06,0.0,0.06]:
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(0,-0.248,0.50+dz))
        P(bpy.context.active_object,mcarb,col).name="AbGrill"; bpy.context.active_object.scale=(0.25,0.008,0.014)
    bpy.ops.mesh.primitive_cube_add(size=1.0,location=(0,0,0.07))
    hp=bpy.context.active_object; hp.name="Hips"; hp.scale=(0.54,0.25,0.20); ss(hp,1); P(hp,mb,col)
    for ex in[-0.25,0.25]:
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,-0.243,0.07))
        P(bpy.context.active_object,marm,col).name="HipPanel"; bpy.context.active_object.scale=(0.155,0.025,0.145)

    # ── HOMBROS ───────────────────────────────────────────────────────────
    for ex,nm in[(-0.70,"L"),(0.70,"R")]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.172,segments=22,ring_count=16,location=(ex,0,0.88))
        sh=bpy.context.active_object; sh.name=f"Sh_{nm}"; sh.scale=(1.0,0.76,0.76); ss(sh,1); P(sh,marm,col)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.055,depth=0.038,vertices=16,location=(ex*1.155,0,0.88),rotation=(0,math.radians(90),0))
        P(bpy.context.active_object,mcyan,col).name=f"ShLED_{nm}"

    # ── BRAZOS ────────────────────────────────────────────────────────────
    for ex,nm in[(-0.82,"L"),(0.82,"R")]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.083,depth=0.46,vertices=18,location=(ex,0,0.60))
        ua=bpy.context.active_object; ua.name=f"UA_{nm}"; ss(ua,1); P(ua,mb,col)
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,-0.062,0.68))
        P(bpy.context.active_object,marm,col).name=f"ArmPanel_{nm}"; bpy.context.active_object.scale=(0.055,0.010,0.16)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.090,segments=18,ring_count=12,location=(ex,0,0.32))
        P(bpy.context.active_object,mjt,col).name=f"Elbow_{nm}"
        bpy.ops.mesh.primitive_torus_add(major_radius=0.100,minor_radius=0.017,location=(ex,0,0.32))
        P(bpy.context.active_object,marm,col).name=f"ElbowRing_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(radius=0.070,depth=0.42,vertices=16,location=(ex,0,0.07))
        fa=bpy.context.active_object; fa.name=f"FA_{nm}"; ss(fa,1); P(fa,mb,col)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.078,minor_radius=0.015,location=(ex,0,-0.15))
        P(bpy.context.active_object,marm,col).name=f"Wrist_{nm}"
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,0,-0.27))
        ha=bpy.context.active_object; ha.name=f"Hand_{nm}"; ha.scale=(0.108,0.062,0.135); ss(ha,1); P(ha,marm,col)
        for fi in range(3):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.016,depth=0.046,vertices=8,location=(ex+(fi-1)*0.030,-0.052,-0.335-fi*0.012))
            P(bpy.context.active_object,mcarb,col).name=f"Finger_{nm}_{fi}"

    # ── PIERNAS ───────────────────────────────────────────────────────────
    for ex,nm in[(-0.21,"L"),(0.21,"R")]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.122,depth=0.52,vertices=20,location=(ex,0,-0.52))
        th=bpy.context.active_object; th.name=f"Th_{nm}"; ss(th,1); P(th,mb,col)
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,-0.100,-0.46))
        P(bpy.context.active_object,marm,col).name=f"ThPanel_{nm}"; bpy.context.active_object.scale=(0.07,0.012,0.18)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.112,segments=18,ring_count=12,location=(ex,0.005,-0.83))
        P(bpy.context.active_object,mjt,col).name=f"Knee_{nm}"
        bpy.ops.mesh.primitive_torus_add(major_radius=0.126,minor_radius=0.017,location=(ex,0,-0.83))
        P(bpy.context.active_object,marm,col).name=f"KneeRing_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(radius=0.022,depth=0.020,vertices=12,location=(ex,-0.112,-0.83),rotation=(math.radians(90),0,0))
        P(bpy.context.active_object,mcyan,col).name=f"KneeLED_{nm}"
        bpy.ops.mesh.primitive_cylinder_add(radius=0.096,depth=0.49,vertices=18,location=(ex,0,-1.12))
        sh=bpy.context.active_object; sh.name=f"Shin_{nm}"; ss(sh,1); P(sh,mb,col)
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,-0.086,-1.04))
        P(bpy.context.active_object,marm,col).name=f"ShinPanel_{nm}"; bpy.context.active_object.scale=(0.065,0.010,0.15)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.103,minor_radius=0.015,location=(ex,0,-1.40))
        P(bpy.context.active_object,marm,col).name=f"Ankle_{nm}"
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,0.09,-1.56))
        ft=bpy.context.active_object; ft.name=f"Foot_{nm}"; ft.scale=(0.122,0.210,0.070); ss(ft,1); P(ft,mb,col)
        bpy.ops.mesh.primitive_cube_add(size=1.0,location=(ex,0.09,-1.632))
        P(bpy.context.active_object,msole,col).name=f"Sole_{nm}"; bpy.context.active_object.scale=(0.124,0.215,0.018)

    # Cables
    for cx,cy,cz,rx in[(-0.35,-0.08,0.55,0.18),(0.35,-0.08,0.55,0.18)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.010,depth=0.18,vertices=6,location=(cx,cy,cz),rotation=(rx,0,0))
        P(bpy.context.active_object,mwire,col).name="Cable"

    # ── PLATAFORMA / BASE ─────────────────────────────────────────────────
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=0.06, vertices=48, location=(0,0,-1.70))
    base = bpy.context.active_object
    base.name = "Base_Platform"
    P(base, mat("Base_Mat", (0.06,0.07,0.09), 0.70, 0.40), col)
    # Anillo luminoso de base
    bpy.ops.mesh.primitive_torus_add(major_radius=0.88, minor_radius=0.022, location=(0,0,-1.67))
    P(bpy.context.active_object, mcyan, col).name = "Base_LED_Ring"

    # ── ILUMINACIÓN ───────────────────────────────────────────────────────
    # KEY LIGHT - Principal frontal-izquierda
    bpy.ops.object.light_add(type="SPOT", location=(2.5, -4.0, 2.8))
    key = bpy.context.active_object
    key.name = "Key_Light"
    key.data.energy = 1500.0
    key.data.color = (1.0, 0.94, 0.86)
    key.data.spot_size = math.radians(55)
    key.data.spot_blend = 0.30
    look_at(key, (0, 0, 0.5))
    ac(key, col)

    # FILL LIGHT - Area difusa izquierda
    bpy.ops.object.light_add(type="AREA", location=(-3.5, -2.5, 0.5))
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = 700.0
    fill.data.color = (0.48, 0.70, 1.0)
    fill.data.size = 2.5
    fill.rotation_euler = mathutils.Euler((math.radians(10), 0, math.radians(-20)), 'XYZ')
    ac(fill, col)

    # RIM LIGHT - Cyan desde atrás-arriba
    bpy.ops.object.light_add(type="SPOT", location=(0.0, 5.0, 3.5))
    rim = bpy.context.active_object
    rim.name = "Rim_Light"
    rim.data.energy = 2200.0
    rim.data.color = (0.0, 0.88, 1.0)
    rim.data.spot_size = math.radians(35)
    rim.data.spot_blend = 0.18
    look_at(rim, (0, 0, 0.5))
    ac(rim, col)

    # BOUNCE GROUND - Suelo
    bpy.ops.object.light_add(type="AREA", location=(0.0, -1.0, -2.5))
    bounce = bpy.context.active_object
    bounce.name = "Bounce_Ground"
    bounce.data.energy = 300.0
    bounce.data.color = (0.5, 0.7, 1.0)
    bounce.data.size = 3.0
    bounce.rotation_euler = mathutils.Euler((math.radians(180), 0, 0), 'XYZ')
    ac(bounce, col)

    # ── MUNDO ─────────────────────────────────────────────────────────────
    world = bpy.data.worlds.new("W")
    bpy.context.scene.world = world
    world.use_nodes = True
    wn = world.node_tree.nodes
    wn.clear()
    bg = wn.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.012, 0.014, 0.025, 1.0)
    bg.inputs["Strength"].default_value = 0.8
    wo = wn.new("ShaderNodeOutputWorld")
    world.node_tree.links.new(bg.outputs["Background"], wo.inputs["Surface"])

    # ── CÁMARA CON TRACK-TO ───────────────────────────────────────────────
    # Modelo va de Z=-1.70 (base) a Z=2.22 (punta antena) → centro ≈ Z=0.26
    # Total height ≈ 3.92 unidades. Con lens=45 y dist=6 debería encuadrar todo.

    target_center = (0, 0, 0.26)   # Centro vertical del modelo

    # Cámara FRONTAL
    cam_f_loc = (0, -6.5, 0.26)
    bpy.ops.object.camera_add(location=cam_f_loc)
    cam_f = bpy.context.active_object
    cam_f.name = "Cam_Front"
    cam_f.data.lens = 45
    look_at(cam_f, target_center)
    bpy.context.scene.camera = cam_f
    ac(cam_f, col)

    # Cámara 3/4
    cam_34_loc = (3.8, -5.0, 0.26)
    bpy.ops.object.camera_add(location=cam_34_loc)
    cam_34 = bpy.context.active_object
    cam_34.name = "Cam_34"
    cam_34.data.lens = 45
    look_at(cam_34, target_center)
    ac(cam_34, col)

    # ── RENDER CONFIG ─────────────────────────────────────────────────────
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        for d in prefs.get_devices_for_type("OPTIX"):
            d.use = True
        print("[+] RTX 4070 OptiX ACTIVADO")
    except Exception as e:
        scene.cycles.device = "CPU"
        print(f"[!] CPU fallback: {e}")

    scene.view_settings.exposure = 0.8
    scene.view_settings.gamma = 1.05
    scene.view_settings.look = "Medium High Contrast"

    scene.cycles.samples = 256
    scene.cycles.use_denoising = True
    try: scene.cycles.denoiser = 'OPTIX'
    except Exception: pass
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"

    # ── RENDER FRONTAL 1920×1080 ──────────────────────────────────────────
    bpy.context.scene.camera = cam_f
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.cycles.samples = 256
    out1 = os.path.join(OUTPUT_DIR, "FINAL_render_front_1920x1080.png")
    scene.render.filepath = out1
    bpy.ops.render.render(write_still=True)
    print(f"[✓] RENDER FRONTAL 1920×1080 → {out1}")

    # ── RENDER 3/4 1920×1080 ─────────────────────────────────────────────
    bpy.context.scene.camera = cam_34
    scene.cycles.samples = 256
    out2 = os.path.join(OUTPUT_DIR, "FINAL_render_34view_1920x1080.png")
    scene.render.filepath = out2
    bpy.ops.render.render(write_still=True)
    print(f"[✓] RENDER 3/4 1920×1080 → {out2}")

    # ── RENDER ESQUEMA LUCES (Preview rápido) ────────────────────────────
    bpy.context.scene.camera = cam_f
    scene.cycles.samples = 96
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    out3 = os.path.join(OUTPUT_DIR, "FINAL_lighting_scheme.png")
    scene.render.filepath = out3
    bpy.ops.render.render(write_still=True)
    print(f"[✓] ESQUEMA LUCES → {out3}")

    # ── GUARDAR .BLEND ────────────────────────────────────────────────────
    bpy.context.scene.camera = cam_34
    bp = os.path.join(OUTPUT_DIR, "robot_FINAL.blend")
    bpy.ops.wm.save_as_mainfile(filepath=bp)
    print(f"[✓] .blend FINAL → {bp}")
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║   PERSONAJE ROBÓTICO — FASE 4 + 5 COMPLETADAS       ║")
    print("╚══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    build()
