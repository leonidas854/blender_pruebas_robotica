#!/usr/bin/env python3
"""
scripts/build_robot_character.py
Script de Blender para generar el modelo 3D del personaje robótico personalizado
utilizando la malla facial y las métricas calculadas por la IA a partir de tu foto.
Puede ejecutarse interactivamente o en modo headless:
    blender -b -P scripts/build_robot_character.py
"""

import bpy
import mathutils
import json
import os
import sys

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_material(name, base_color=(0.1, 0.1, 0.1, 1.0), metallic=0.9, roughness=0.25, emission_color=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission_color:
            # En Blender 3.6 / 4.x
            if "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission_color
            elif "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission_color
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

def build_robot():
    base_dir = os.path.abspath(os.path.dirname(__file__) + "/..")
    data_dir = os.path.join(base_dir, "character_data")
    os.makedirs(data_dir, exist_ok=True)
    profile_path = os.path.join(data_dir, "character_profile.json")
    obj_path = os.path.join(data_dir, "face_mesh.obj")
    photo_path = os.path.join(data_dir, "photo.jpg")

    # Valores por defecto en caso de no haber procesado aún una foto
    metrics = {
        "interpupillary_distance": 0.28,
        "face_width": 0.65,
        "face_height": 1.0,
        "nose_projection": 0.15,
        "left_eye_pos": [-0.14, 0.05, 0.02],
        "right_eye_pos": [0.14, 0.05, 0.02],
    }

    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        print(f"[+] Cargadas métricas faciales personalizadas desde {profile_path}")
    else:
        print("[*] No se encontró character_profile.json; utilizando proporciones humanas canónicas.")

    clear_scene()

    # Colección principal
    col = bpy.data.collections.new("Robot_Character")
    bpy.context.scene.collection.children.link(col)

    # 1. Materiales PBR
    mat_chassis_dark = create_material("Mat_Dark_Titanium", (0.05, 0.06, 0.07, 1.0), metallic=0.95, roughness=0.2)
    mat_armor_silver = create_material("Mat_Armor_Alloy", (0.8, 0.82, 0.85, 1.0), metallic=0.85, roughness=0.35)
    mat_cyan_led = create_material("Mat_Cyan_LED", (0.0, 0.9, 1.0, 1.0), metallic=0.1, roughness=0.1,
                                   emission_color=(0.0, 0.9, 1.0, 1.0), emission_strength=8.0)
    mat_orange_led = create_material("Mat_Amber_LED", (1.0, 0.45, 0.0, 1.0), metallic=0.1, roughness=0.1,
                                    emission_color=(1.0, 0.45, 0.0, 1.0), emission_strength=6.0)
    mat_carbon = create_material("Mat_Carbon_Fiber", (0.02, 0.02, 0.02, 1.0), metallic=0.4, roughness=0.5)

    # 2. Torso / Chasis Base
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -1.2))
    torso = bpy.context.active_object
    torso.name = "Robot_Torso"
    torso.scale = (0.75, 0.45, 0.7)
    torso.data.materials.append(mat_chassis_dark)

    # Núcleo de energía en el pecho (Arc Reactor / Power Core)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.1, location=(0, -0.23, -1.05), rotation=(1.5708, 0, 0))
    core = bpy.context.active_object
    core.name = "Robot_Power_Core"
    core.data.materials.append(mat_cyan_led)

    # Hombreras Robóticas
    for side, sign in [("Left", -1), ("Right", 1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(sign * 0.55, 0, -0.9))
        shoulder = bpy.context.active_object
        shoulder.name = f"Robot_Shoulder_{side}"
        shoulder.scale = (1.0, 0.8, 0.8)
        shoulder.data.materials.append(mat_armor_silver)

    # 3. Cuello Robótico Articulado
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.35, location=(0, 0, -0.65))
    neck = bpy.context.active_object
    neck.name = "Robot_Neck_Piston"
    neck.data.materials.append(mat_carbon)

    # Anillos servomotores del cuello
    for z_offset in (-0.72, -0.58):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.025, location=(0, 0, z_offset))
        ring = bpy.context.active_object
        ring.name = "Robot_Neck_ServoRing"
        ring.data.materials.append(mat_armor_silver)

    # 4. Cabeza Robótica (Cráneo / Casco protector)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.52, location=(0, 0.08, 0.0))
    head_chassis = bpy.context.active_object
    head_chassis.name = "Robot_Head_Cranium"
    head_chassis.scale = (metrics.get("face_width", 0.65) * 0.95, 1.0, 1.1)
    head_chassis.data.materials.append(mat_chassis_dark)

    # Antenas / Receptores laterales
    for side, sign in [("Left", -1), ("Right", 1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.08, location=(sign * 0.45, 0.05, 0.0), rotation=(0, 1.5708, 0))
        ear = bpy.context.active_object
        ear.name = f"Robot_Ear_Sensor_{side}"
        ear.data.materials.append(mat_armor_silver)

    # 5. Importar / Integrar Placa Facial Personalizada
    face_obj = None
    if os.path.exists(obj_path):
        try:
            bpy.ops.wm.obj_import(filepath=obj_path)
            face_obj = bpy.context.selected_objects[0]
            face_obj.name = "Robot_Custom_FacePlate"
            face_obj.location = (0, -0.38, 0.0)
            face_obj.scale = (0.75, 0.75, 0.75)
            # Material cibernético para la placa del rostro
            mat_face = create_material("Mat_FacePlate_Alloy", (0.7, 0.73, 0.78, 1.0), metallic=0.7, roughness=0.3)
            face_obj.data.materials.append(mat_face)
            print(f"[+] Malla facial {obj_path} importada y montada exitosamente!")
        except Exception as e:
            print(f"[!] Error importando OBJ con nuevo operador: {e}")
            try:
                bpy.ops.import_scene.obj(filepath=obj_path)
                face_obj = bpy.context.selected_objects[0]
                face_obj.name = "Robot_Custom_FacePlate"
                face_obj.location = (0, -0.38, 0.0)
                face_obj.scale = (0.75, 0.75, 0.75)
            except Exception as e2:
                print(f"[!] Fallo alternativo de importación OBJ: {e2}")

    # Si no se pudo importar el OBJ o para complementar: crear Visores Oculares Robóticos
    # alineados con la distancia interpupilar exacta del estudiante
    eye_l_pos = metrics.get("left_eye_pos", [-0.14, 0.05, 0.02])
    eye_r_pos = metrics.get("right_eye_pos", [0.14, 0.05, 0.02])

    for side, pos, name in [("Left", eye_l_pos, "Robot_Eye_Sensor_L"), ("Right", eye_r_pos, "Robot_Eye_Sensor_R")]:
        # Sensor ocular cilíndrico
        target_x = pos[0] * 0.9
        target_z = pos[1] * 0.9
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.065, depth=0.06,
            location=(target_x, -0.44, target_z),
            rotation=(1.5708, 0, 0)
        )
        eye_sensor = bpy.context.active_object
        eye_sensor.name = name
        eye_sensor.data.materials.append(mat_cyan_led)

    # Visor HUD cibernético frontal
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.42, eye_l_pos[1] * 0.9))
    visor = bpy.context.active_object
    visor.name = "Robot_Visor_HUD"
    visor.scale = (abs(eye_l_pos[0]) * 2.6, 0.04, 0.08)
    visor.data.materials.append(mat_orange_led)

    # 6. Crear Armature (Esqueleto cinemático de robótica)
    bpy.ops.object.armature_add(location=(0, 0, -1.2))
    armature_obj = bpy.context.active_object
    armature_obj.name = "Robot_Kinematic_Rig"
    armature_data = armature_obj.data
    armature_data.name = "Robot_Rig_Data"

    bpy.ops.object.mode_set(mode='EDIT')
    root_bone = armature_data.edit_bones[0]
    root_bone.name = "Torso_Root"
    root_bone.head = (0, 0, -1.2)
    root_bone.tail = (0, 0, -0.65)

    neck_bone = armature_data.edit_bones.new("Neck_PitchYaw")
    neck_bone.head = (0, 0, -0.65)
    neck_bone.tail = (0, 0, -0.45)
    neck_bone.parent = root_bone

    head_bone = armature_data.edit_bones.new("Head_RollTilt")
    head_bone.head = (0, 0, -0.45)
    head_bone.tail = (0, 0, 0.45)
    head_bone.parent = neck_bone

    bpy.ops.object.mode_set(mode='OBJECT')

    # 7. Configuración de Iluminación de Estudio (3-Point Lighting)
    # Key Light
    bpy.ops.object.light_add(type='SPOT', radius=0.2, location=(1.5, -2.0, 1.2))
    key_light = bpy.context.active_object
    key_light.name = "Key_Light"
    key_light.data.energy = 280.0
    key_light.data.color = (1.0, 0.95, 0.9)

    # Fill Light
    bpy.ops.object.light_add(type='POINT', radius=0.5, location=(-2.0, -1.2, 0.5))
    fill_light = bpy.context.active_object
    fill_light.name = "Fill_Light"
    fill_light.data.energy = 90.0
    fill_light.data.color = (0.6, 0.8, 1.0)

    # Rim / Back Light (Ciberpunk Cyan Rim)
    bpy.ops.object.light_add(type='SPOT', radius=0.2, location=(0, 2.2, 1.5))
    rim_light = bpy.context.active_object
    rim_light.name = "Rim_Back_Light"
    rim_light.data.energy = 350.0
    rim_light.data.color = (0.0, 0.9, 1.0)

    # 8. Cámara de Presentación
    bpy.ops.object.camera_add(location=(0, -2.6, -0.1), rotation=(1.5708, 0, 0))
    cam = bpy.context.active_object
    cam.name = "Presentation_Camera"
    bpy.context.scene.camera = cam

    # 9. Configuración del Motor de Render (Cycles OptiX con RTX 4070)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'OPTIX'
        for d in prefs.get_devices_for_type('OPTIX'):
            d.use = True
    except Exception as e:
        print(f"[*] Render pref notice: {e}")

    scene.cycles.samples = 128
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    # Guardar archivo .blend
    save_path = os.path.join(data_dir, "robot_character.blend")
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    print(f"\n[+] Personaje robótico construido exitosamente!")
    print(f"[+] Archivo Blender guardado en: {save_path}")

    return save_path

if __name__ == "__main__":
    build_robot()
