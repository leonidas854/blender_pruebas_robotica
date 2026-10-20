"""
robotics_anatomy package
Módulos especializados para modelado anatómico humanoide y robótico en Blender.
Escala 1.80m calibrada a partir de fotos y métricas antropométricas reales.
"""

from .metrics import get_body_metrics
from .materials import create_clay_material, create_pbr_material
from .primitives import add_to_collection, apply_material, make_box, make_cylinder, make_sphere, make_capsule
from .head_neck import build_head_and_neck
from .torso import build_torso
from .pelvis import build_pelvis
from .arms import build_arms_and_hands
from .legs import build_legs_and_feet
from .studio import setup_studio_cyclorama, setup_studio_lighting, setup_studio_camera, render_and_save

__all__ = [
    "get_body_metrics",
    "create_clay_material",
    "create_pbr_material",
    "add_to_collection",
    "apply_material",
    "make_box",
    "make_cylinder",
    "make_sphere",
    "make_capsule",
    "build_head_and_neck",
    "build_torso",
    "build_pelvis",
    "build_arms_and_hands",
    "build_legs_and_feet",
    "setup_studio_cyclorama",
    "setup_studio_lighting",
    "setup_studio_camera",
    "render_and_save",
]
