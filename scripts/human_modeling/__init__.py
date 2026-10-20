"""
scripts/human_modeling package
Módulos especializados para la generación y modelado poligonal continuo
del cuerpo humano masculino a escala real 1.80m (Leonidas).
"""

from .metrics import get_user_biometrics
from .skeleton_core import create_continuous_apose_core
from .musculature import create_male_musculature
from .face_head import create_male_head_and_face
from .hands_feet import create_detailed_hands_and_feet
from .mesh_builder import build_complete_human_mesh
from .studio_render import setup_human_studio, render_human_views

__all__ = [
    "get_user_biometrics",
    "create_continuous_apose_core",
    "create_male_musculature",
    "create_male_head_and_face",
    "create_detailed_hands_and_feet",
    "build_complete_human_mesh",
    "setup_human_studio",
    "render_human_views",
]
