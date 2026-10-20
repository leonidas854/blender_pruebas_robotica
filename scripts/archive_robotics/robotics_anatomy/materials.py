"""
scripts/robotics_anatomy/materials.py
Creación de materiales para el modelado anatómico y robótico.
"""

import bpy

def create_clay_material(name="Mat_Clay_Anatomy"):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.56, 0.58, 0.62, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.52
        bsdf.inputs["Metallic"].default_value = 0.08
    return mat

def create_pbr_material(name, base_color=(0.5, 0.5, 0.5), metallic=0.0, roughness=0.5,
                        emission=None, em_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission:
            for inp_name in ["Emission", "Emission Color"]:
                if inp_name in bsdf.inputs:
                    bsdf.inputs[inp_name].default_value = (*emission, 1.0)
                    break
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = em_strength
    return mat
