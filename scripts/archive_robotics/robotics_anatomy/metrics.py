"""
scripts/robotics_anatomy/metrics.py
Carga y cálculo de métricas antropométricas reales escaladas a 1.80m.
"""

import os
import json

DEFAULT_METRICS = {
    "height_m": 1.800,
    "head_top": 1.800,
    "head_center": 1.710,
    "head_radius": 0.095,
    "neck_center": 1.585,
    "neck_length": 0.080,
    "neck_radius": 0.060,
    "shoulder_height": 1.505,
    "shoulder_width": 0.443,
    "chest_center": 1.370,
    "chest_width": 0.390,
    "chest_depth": 0.250,
    "chest_height": 0.220,
    "waist_center": 1.160,
    "waist_width": 0.250,
    "waist_depth": 0.190,
    "waist_height": 0.180,
    "pelvis_center": 0.950,
    "pelvis_width": 0.270,
    "pelvis_depth": 0.200,
    "pelvis_height": 0.180,
    "hip_joint_z": 0.880,
    "hip_x": 0.110,
    "knee_z": 0.490,
    "ankle_z": 0.085,
    "ground_z": 0.000,
    "elbow_z": 1.205,
    "wrist_z": 0.910,
    "fingertip_z": 0.790,
}

def get_body_metrics(base_dir=None):
    if base_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    json_path = os.path.join(base_dir, "character_data", "body_metrics_real.json")
    metrics = dict(DEFAULT_METRICS)

    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                props = data.get("proportions", {})
                t = props.get("torso", {})
                a = props.get("arms", {})
                l = props.get("legs", {})
                h = props.get("head", {})

                if "shoulder_width" in t:
                    metrics["shoulder_width"] = float(t["shoulder_width"])
                if "chest_width" in t:
                    metrics["chest_width"] = float(t["chest_width"])
                if "chest_depth" in t:
                    metrics["chest_depth"] = float(t["chest_depth"])
                if "waist_width" in t:
                    metrics["waist_width"] = float(t["waist_width"])
                if "waist_depth" in t:
                    metrics["waist_depth"] = float(t["waist_depth"])
                if "hip_width" in t:
                    metrics["pelvis_width"] = float(t["hip_width"])

                print(f"[+] Métricas antropométricas cargadas desde {json_path}")
        except Exception as e:
            print(f"[!] Aviso al leer body_metrics_real.json ({e}), usando valores anatómicos 1.80m.")
    else:
        print("[*] Usando métricas estándar de complexión atlética masculina 1.80m.")

    return metrics
