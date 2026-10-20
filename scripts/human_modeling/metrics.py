"""
scripts/human_modeling/metrics.py
Métricas biométricas de Leonidas (1.80m) cargadas desde body_metrics_real.json.
"""

import os
import json

DEFAULT_LEONIDAS_METRICS = {
    "total_height": 1.800,
    "head": {
        "top_z": 1.800,
        "center_z": 1.710,
        "height": 0.188,
        "width": 0.168,
        "depth": 0.195,
        "chin_z": 1.625,
        "neck_top_z": 1.625,
        "neck_base_z": 1.520,
        "neck_radius": 0.062,
    },
    "torso": {
        "shoulder_z": 1.505,
        "shoulder_width": 0.443,  # Biacromial real 44.3cm
        "chest_z": 1.370,
        "chest_width": 0.390,     # Pecho masculino atlético 39cm
        "chest_depth": 0.250,
        "waist_z": 1.150,
        "waist_width": 0.245,     # Cintura estrecha en V-taper
        "waist_depth": 0.180,
        "pelvis_z": 0.940,
        "pelvis_width": 0.265,
        "pelvis_depth": 0.195,
        "spine_curve_y": 0.015,
    },
    "arms": {
        "apose_angle_deg": 42.0,   # Pose A relajada como en la imagen de referencia
        "shoulder_x": 0.2215,      # 44.3cm / 2
        "upper_arm_len": 0.298,
        "forearm_len": 0.299,
        "hand_len": 0.115,
        "bicep_radius": 0.054,
        "forearm_radius": 0.046,
        "wrist_radius": 0.034,
    },
    "legs": {
        "hip_z": 0.880,
        "hip_x": 0.108,
        "knee_z": 0.490,
        "ankle_z": 0.080,
        "thigh_radius": 0.082,
        "knee_radius": 0.060,
        "calf_radius": 0.064,
        "ankle_radius": 0.045,
        "foot_len": 0.240,
        "foot_width": 0.098,
        "foot_height": 0.080,
    }
}

def get_user_biometrics(base_dir=None):
    if base_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    json_path = os.path.join(base_dir, "character_data", "metrics", "body_metrics_real.json")
    if not os.path.exists(json_path):
        json_path = os.path.join(base_dir, "character_data", "body_metrics_real.json")
    metrics = dict(DEFAULT_LEONIDAS_METRICS)

    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                props = data.get("proportions", {})
                if "torso" in props and "shoulder_width" in props["torso"]:
                    metrics["torso"]["shoulder_width"] = float(props["torso"]["shoulder_width"])
                    metrics["arms"]["shoulder_x"] = metrics["torso"]["shoulder_width"] / 2.0
                if "torso" in props and "chest_width" in props["torso"]:
                    metrics["torso"]["chest_width"] = float(props["torso"]["chest_width"])
                print(f"[✓] Métricas biométricas de Leonidas cargadas desde {json_path}")
        except Exception as e:
            print(f"[*] Aviso al leer json ({e}), usando valores calibrados a 1.80m.")
    return metrics
