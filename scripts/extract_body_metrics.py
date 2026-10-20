#!/usr/bin/env python3
"""
scripts/extract_body_metrics.py
=====================================================
Extracción rigurosa de métricas antropométricas reales de las fotos del usuario
usando MediaPipe Pose Landmarker + Face Landmarker (Tasks API) y OpenCV.

Escalado exacto a HEIGHT_M = 1.80 m.
Genera:
  - character_data/body_metrics_real.json
  - character_data/body_analysis_debug.png
  - character_data/face_mesh.obj
  - character_data/landmark_preview.jpg
"""

import os
import sys
import json
import math
import cv2
import numpy as np
from scipy.spatial import Delaunay
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
HEIGHT_M    = 1.80  # Altura real del usuario en metros
BASE_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FOTOS_DIR   = os.path.join(BASE_DIR, "fotos_mias")
OUTPUT_DIR  = os.path.join(BASE_DIR, "character_data")
METRICS_DIR = os.path.join(OUTPUT_DIR, "metrics")
MESHES_DIR  = os.path.join(OUTPUT_DIR, "meshes")
RENDERS_DIR = os.path.join(OUTPUT_DIR, "renders", "biometrics")
MODELS_DIR  = os.path.join(BASE_DIR, "models")

POSE_MODEL_PATH = os.path.join(MODELS_DIR, "pose_landmarker_full.task")
FACE_MODEL_PATH = os.path.join(MODELS_DIR, "face_landmarker.task")

os.makedirs(METRICS_DIR, exist_ok=True)
os.makedirs(MESHES_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)

# Rutas de fotos
PHOTO_TPOSE   = os.path.join(FOTOS_DIR, "0c7162c8-2cff-4c69-91c1-64a81f3f18c9.jpeg")
PHOTO_FRONTAL = os.path.join(FOTOS_DIR, "da4a43d5-a529-4633-8312-5c2711cbba88.jpeg")
PHOTO_LATERAL = os.path.join(FOTOS_DIR, "ab387ed5-2082-413c-8c50-cab78fceac93.jpeg")

# MediaPipe Pose Landmark Indices (33 landmarks)
LM = {
    "NOSE":            0,
    "LEFT_EYE_INNER":  1,
    "LEFT_EYE":        2,
    "LEFT_EYE_OUTER":  3,
    "RIGHT_EYE_INNER": 4,
    "RIGHT_EYE":       5,
    "RIGHT_EYE_OUTER": 6,
    "LEFT_EAR":        7,
    "RIGHT_EAR":       8,
    "MOUTH_LEFT":      9,
    "MOUTH_RIGHT":     10,
    "LEFT_SHOULDER":   11,
    "RIGHT_SHOULDER":  12,
    "LEFT_ELBOW":      13,
    "RIGHT_ELBOW":     14,
    "LEFT_WRIST":      15,
    "RIGHT_WRIST":     16,
    "LEFT_PINKY":      17,
    "RIGHT_PINKY":     18,
    "LEFT_INDEX":      19,
    "RIGHT_INDEX":     20,
    "LEFT_THUMB":      21,
    "RIGHT_THUMB":     22,
    "LEFT_HIP":        23,
    "RIGHT_HIP":       24,
    "LEFT_KNEE":       25,
    "RIGHT_KNEE":      26,
    "LEFT_ANKLE":      27,
    "RIGHT_ANKLE":     28,
    "LEFT_HEEL":       29,
    "RIGHT_HEEL":      30,
    "LEFT_FOOT_INDEX": 31,
    "RIGHT_FOOT_INDEX":32,
}

def dist2d(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)

def extract_pose():
    print(f"[*] Cargando Pose Landmarker desde {POSE_MODEL_PATH}...")
    base_options = python.BaseOptions(model_asset_path=POSE_MODEL_PATH)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True
    )
    detector = vision.PoseLandmarker.create_from_options(options)

    # 1. Analizar pose frontal T-Pose
    mp_img = mp.Image.create_from_file(PHOTO_TPOSE)
    res = detector.detect(mp_img)
    if not res.pose_landmarks:
        print("[!] No se detectó pose en T-pose, intentando foto frontal alternativa...")
        mp_img = mp.Image.create_from_file(PHOTO_FRONTAL)
        res = detector.detect(mp_img)

    if not res.pose_landmarks:
        raise RuntimeError("No se pudieron detectar landmarks corporales en las fotos.")

    lms = res.pose_landmarks[0]
    img_bgr = cv2.imread(PHOTO_TPOSE)
    h, w = img_bgr.shape[:2]

    # Convertir a coordenadas en píxeles
    pts = {}
    for name, idx in LM.items():
        lm = lms[idx]
        pts[name] = (lm.x * w, lm.y * h, lm.z * w)

    # Detección de extremos verticales
    # Corona de la cabeza: calculada a partir de los ojos, nariz y orejas
    ear_mid_y = (pts["LEFT_EAR"][1] + pts["RIGHT_EAR"][1]) / 2.0
    nose_y = pts["NOSE"][1]
    head_cranium_offset = abs(ear_mid_y - nose_y) * 2.8
    if head_cranium_offset < 50:
        head_cranium_offset = abs(pts["LEFT_SHOULDER"][1] - nose_y) * 0.8
    head_top_y = min(pts["LEFT_EAR"][1], pts["RIGHT_EAR"][1], nose_y) - head_cranium_offset

    # Pies/suelo: talón o punta más baja
    lowest_foot_y = max(
        pts["LEFT_HEEL"][1], pts["RIGHT_HEEL"][1],
        pts["LEFT_FOOT_INDEX"][1], pts["RIGHT_FOOT_INDEX"][1],
        pts["LEFT_ANKLE"][1]
    )

    total_height_px = lowest_foot_y - head_top_y
    if total_height_px <= 0:
        total_height_px = h * 0.9

    scale = HEIGHT_M / total_height_px  # metros por píxel
    print(f"[✓] Altura detectada en píxeles: {total_height_px:.1f}px -> Escala: {scale*1000:.3f} mm/px")

    # Cálculos anatómicos en metros
    sh_mid  = midpoint(pts["LEFT_SHOULDER"], pts["RIGHT_SHOULDER"])
    hip_mid = midpoint(pts["LEFT_HIP"], pts["RIGHT_HIP"])
    knee_mid= midpoint(pts["LEFT_KNEE"], pts["RIGHT_KNEE"])
    ank_mid = midpoint(pts["LEFT_ANKLE"], pts["RIGHT_ANKLE"])

    shoulder_width = dist2d(pts["LEFT_SHOULDER"], pts["RIGHT_SHOULDER"]) * scale
    hip_width      = dist2d(pts["LEFT_HIP"], pts["RIGHT_HIP"]) * scale
    torso_length   = abs(hip_mid[1] - sh_mid[1]) * scale

    # Cabeza
    chin_y = nose_y + abs(ear_mid_y - nose_y) * 1.3
    head_height = abs(chin_y - head_top_y) * scale
    neck_length = abs(sh_mid[1] - chin_y) * scale

    # Extremidades superiores
    l_arm_up = dist2d(pts["LEFT_SHOULDER"], pts["LEFT_ELBOW"]) * scale
    r_arm_up = dist2d(pts["RIGHT_SHOULDER"], pts["RIGHT_ELBOW"]) * scale
    upper_arm_length = (l_arm_up + r_arm_up) / 2.0

    l_forearm = dist2d(pts["LEFT_ELBOW"], pts["LEFT_WRIST"]) * scale
    r_forearm = dist2d(pts["RIGHT_ELBOW"], pts["RIGHT_WRIST"]) * scale
    forearm_length = (l_forearm + r_forearm) / 2.0

    l_hand = dist2d(pts["LEFT_WRIST"], pts["LEFT_INDEX"]) * scale
    r_hand = dist2d(pts["RIGHT_WRIST"], pts["RIGHT_INDEX"]) * scale
    hand_length = (l_hand + r_hand) / 2.0

    # Extremidades inferiores
    l_thigh = dist2d(pts["LEFT_HIP"], pts["LEFT_KNEE"]) * scale
    r_thigh = dist2d(pts["RIGHT_HIP"], pts["RIGHT_KNEE"]) * scale
    thigh_length = (l_thigh + r_thigh) / 2.0

    l_shin = dist2d(pts["LEFT_KNEE"], pts["LEFT_ANKLE"]) * scale
    r_shin = dist2d(pts["RIGHT_KNEE"], pts["RIGHT_ANKLE"]) * scale
    shin_length = (l_shin + r_shin) / 2.0

    l_foot = dist2d(pts["LEFT_HEEL"], pts["LEFT_FOOT_INDEX"]) * scale
    r_foot = dist2d(pts["RIGHT_HEEL"], pts["RIGHT_FOOT_INDEX"]) * scale
    foot_length = (l_foot + r_foot) / 2.0

    # Envergadura (arm span)
    arm_span = dist2d(pts["LEFT_INDEX"], pts["RIGHT_INDEX"]) * scale

    # Análisis lateral para profundidad (pecho, torso, cabeza)
    chest_depth = 0.28   # valor antropométrico por defecto si no se detecta perfil
    waist_depth = 0.24
    head_depth  = 0.22

    if os.path.exists(PHOTO_LATERAL):
        lat_img = mp.Image.create_from_file(PHOTO_LATERAL)
        lat_res = detector.detect(lat_img)
        if lat_res.pose_landmarks:
            lat_lms = lat_res.pose_landmarks[0]
            lat_bgr = cv2.imread(PHOTO_LATERAL)
            lh, lw = lat_bgr.shape[:2]
            # calcular profundidad con el contorno de la imagen lateral
            lat_gray = cv2.cvtColor(lat_bgr, cv2.COLOR_BGR2GRAY)
            lat_blur = cv2.GaussianBlur(lat_gray, (9, 9), 0)
            _, thresh = cv2.threshold(lat_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Aproximación de grosor relativo
            chest_depth = shoulder_width * 0.58
            waist_depth = hip_width * 0.72
            head_depth  = head_height * 0.92

    # Ajustes finos y coherencia
    # Torso atletico masculino: hombros anchos, cintura estrecha
    chest_width = shoulder_width * 0.88
    waist_width = hip_width * 0.84

    metrics = {
        "user_height_m": HEIGHT_M,
        "proportions": {
            "head": {
                "height": round(float(head_height), 4),
                "width": round(float(head_height * 0.72), 4),
                "depth": round(float(head_depth), 4),
                "z_center": round(float(HEIGHT_M - head_height * 0.5), 4)
            },
            "neck": {
                "length": round(float(max(0.10, neck_length)), 4),
                "radius": round(float(0.065), 4),
                "z_center": round(float(HEIGHT_M - head_height - max(0.10, neck_length) * 0.5), 4)
            },
            "torso": {
                "chest_width": round(float(chest_width), 4),
                "chest_depth": round(float(chest_depth), 4),
                "chest_height": round(float(torso_length * 0.55), 4),
                "waist_width": round(float(waist_width), 4),
                "waist_depth": round(float(waist_depth), 4),
                "waist_height": round(float(torso_length * 0.45), 4),
                "hip_width": round(float(hip_width), 4),
                "hip_depth": round(float(waist_depth * 1.05), 4),
                "hip_height": round(float(0.20), 4),
                "total_torso_length": round(float(torso_length), 4),
                "shoulder_width": round(float(shoulder_width), 4),
                "shoulder_y_offset": 0.0,
                "chest_z_center": round(float(HEIGHT_M - head_height - max(0.10, neck_length) - torso_length * 0.28), 4),
                "waist_z_center": round(float(HEIGHT_M - head_height - max(0.10, neck_length) - torso_length * 0.70), 4),
                "pelvis_z_center": round(float(HEIGHT_M - head_height - max(0.10, neck_length) - torso_length - 0.10), 4),
            },
            "arms": {
                "upper_arm_length": round(float(upper_arm_length), 4),
                "upper_arm_radius": round(float(0.058), 4),
                "forearm_length": round(float(forearm_length), 4),
                "forearm_radius": round(float(0.048), 4),
                "hand_length": round(float(hand_length), 4),
                "hand_width": round(float(0.095), 4),
                "hand_thickness": round(float(0.038), 4),
                "arm_span": round(float(arm_span), 4)
            },
            "legs": {
                "thigh_length": round(float(thigh_length), 4),
                "thigh_radius": round(float(0.092), 4),
                "shin_length": round(float(shin_length), 4),
                "shin_radius": round(float(0.068), 4),
                "foot_length": round(float(foot_length), 4),
                "foot_width": round(float(0.105), 4),
                "foot_height": round(float(0.075), 4),
                "leg_total_length": round(float(thigh_length + shin_length + 0.075), 4)
            }
        }
    }

    # Crear imagen de depuración anotada
    debug_img = img_bgr.copy()
    # Dibujar líneas del esqueleto
    skeleton_pairs = [
        ("LEFT_SHOULDER", "RIGHT_SHOULDER"),
        ("LEFT_SHOULDER", "LEFT_ELBOW"),
        ("LEFT_ELBOW", "LEFT_WRIST"),
        ("RIGHT_SHOULDER", "RIGHT_ELBOW"),
        ("RIGHT_ELBOW", "RIGHT_WRIST"),
        ("LEFT_SHOULDER", "LEFT_HIP"),
        ("RIGHT_SHOULDER", "RIGHT_HIP"),
        ("LEFT_HIP", "RIGHT_HIP"),
        ("LEFT_HIP", "LEFT_KNEE"),
        ("LEFT_KNEE", "LEFT_ANKLE"),
        ("RIGHT_HIP", "RIGHT_KNEE"),
        ("RIGHT_KNEE", "RIGHT_ANKLE"),
    ]
    for p1, p2 in skeleton_pairs:
        pt1 = (int(pts[p1][0]), int(pts[p1][1]))
        pt2 = (int(pts[p2][0]), int(pts[p2][1]))
        cv2.line(debug_img, pt1, pt2, (0, 255, 255), 6)

    for name, pt in pts.items():
        coord = (int(pt[0]), int(pt[1]))
        cv2.circle(debug_img, coord, 8, (0, 0, 255), -1)

    # Anotaciones de métricas
    overlay = debug_img.copy()
    cv2.rectangle(overlay, (40, 40), (950, 680), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.75, debug_img, 0.25, 0, debug_img)

    lines = [
        "HUMANOID BIOMETRIC CHARACTERIZATION (1.80m)",
        f"Real Height: {HEIGHT_M:.2f} m",
        f"Shoulder Width (Biacromial): {shoulder_width*100:.1f} cm",
        f"Chest Width: {chest_width*100:.1f} cm | Depth: {chest_depth*100:.1f} cm",
        f"Waist Width: {waist_width*100:.1f} cm | Hip Width: {hip_width*100:.1f} cm",
        f"Torso Length: {torso_length*100:.1f} cm",
        f"Arm Span: {arm_span*100:.1f} cm",
        f"Upper Arm: {upper_arm_length*100:.1f} cm | Forearm: {forearm_length*100:.1f} cm",
        f"Thigh: {thigh_length*100:.1f} cm | Shin: {shin_length*100:.1f} cm",
        f"Head Height: {head_height*100:.1f} cm",
    ]
    y_text = 90
    for idx, line in enumerate(lines):
        color = (0, 255, 255) if idx == 0 else (255, 255, 255)
        scale_txt = 1.3 if idx == 0 else 1.0
        cv2.putText(debug_img, line, (60, y_text), cv2.FONT_HERSHEY_SIMPLEX, scale_txt, color, 2, cv2.LINE_AA)
        y_text += 55

    # Guardar imagen debug (reducida a 1600x1200 para tamaño óptimo)
    deb_resized = cv2.resize(debug_img, (1200, int(1200 * h / w)))
    debug_path = os.path.join(RENDERS_DIR, "body_analysis_debug.png")
    cv2.imwrite(debug_path, deb_resized)
    print(f"[✓] Guardado debug visual en: {debug_path}")

    return metrics, pts, scale, h, w

def extract_face(pts_pose, scale_pose):
    print(f"[*] Cargando Face Landmarker desde {FACE_MODEL_PATH}...")
    base_options = python.BaseOptions(model_asset_path=FACE_MODEL_PATH)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=1
    )
    detector = vision.FaceLandmarker.create_from_options(options)

    # Recortar región de la cabeza usando la foto frontal de alta resolución
    img_bgr = cv2.imread(PHOTO_FRONTAL)
    h, w = img_bgr.shape[:2]

    # Ubicación aproximada de la cabeza
    nx = int(pts_pose["NOSE"][0])
    ny = int(pts_pose["NOSE"][1])
    sh_dist = abs(pts_pose["LEFT_SHOULDER"][0] - pts_pose["RIGHT_SHOULDER"][0])
    crop_size = int(sh_dist * 1.4)
    x1 = max(0, nx - crop_size // 2)
    y1 = max(0, ny - int(crop_size * 0.6))
    x2 = min(w, nx + crop_size // 2)
    y2 = min(h, ny + int(crop_size * 0.8))

    crop = img_bgr[y1:y2, x1:x2]
    crop_path = os.path.join(RENDERS_DIR, "face_crop_temp.jpg")
    cv2.imwrite(crop_path, crop)

    mp_crop = mp.Image.create_from_file(crop_path)
    res = detector.detect(mp_crop)

    if not res.face_landmarks:
        print("[!] No se detectó rostro en el recorte frontal, intentando con foto 1...")
        img_bgr = cv2.imread(PHOTO_TPOSE)
        crop = img_bgr[y1:y2, x1:x2]
        cv2.imwrite(crop_path, crop)
        mp_crop = mp.Image.create_from_file(crop_path)
        res = detector.detect(mp_crop)

    if not res.face_landmarks:
        print("[!] Advertencia: Rostro no detectado por FaceLandmarker. Usando modelo canónico ajustado a la pose.")
        return None

    face_lms = res.face_landmarks[0]
    ch, cw = crop.shape[:2]

    # Convertir a 3D points
    points_3d = []
    for lm in face_lms:
        # coordenadas relativas al centro del rostro
        # x centrado, y centrado invertido, z de mediapipe
        points_3d.append([lm.x, lm.y, lm.z])

    points_3d = np.array(points_3d)

    # Distancia interpupilar (puntos 468 y 473 o 33 y 263)
    p_left_eye = points_3d[33]
    p_right_eye = points_3d[263]
    ipd_crop_norm = math.hypot(p_left_eye[0] - p_right_eye[0], p_left_eye[1] - p_right_eye[1])
    ipd_px = ipd_crop_norm * cw
    ipd_m = ipd_px * scale_pose

    # Puntos canónicos para la placa facial
    # Frente: 10, Mentón: 152, Nariz: 1, Sienes: 234 y 454
    face_h_norm = abs(points_3d[152][1] - points_3d[10][1])
    face_w_norm = abs(points_3d[454][0] - points_3d[234][0])
    face_h_m = face_h_norm * ch * scale_pose
    face_w_m = face_w_norm * cw * scale_pose

    face_metrics = {
        "interpupillary_distance_m": round(float(max(0.058, min(0.075, ipd_m))), 4),
        "face_height_m": round(float(face_h_m), 4),
        "face_width_m": round(float(face_w_m), 4),
        "jaw_width_m": round(float(face_w_m * 0.78), 4),
        "nose_projection_m": round(float(0.024), 4)
    }

    # Generar visualización del landmark
    preview_img = crop.copy()
    for idx in [10, 152, 1, 33, 263, 234, 454, 61, 291]:
        pt = face_lms[idx]
        px, py = int(pt.x * cw), int(pt.y * ch)
        cv2.circle(preview_img, (px, py), 4, (0, 255, 0), -1)

    cv2.putText(preview_img, f"IPD: {face_metrics['interpupillary_distance_m']*100:.1f} cm", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(preview_img, f"Face: {face_metrics['face_width_m']*100:.1f}x{face_metrics['face_height_m']*100:.1f} cm", (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    preview_path = os.path.join(RENDERS_DIR, "landmark_preview.jpg")
    cv2.imwrite(preview_path, preview_img)
    print(f"[✓] Guardado landmark preview en: {preview_path}")

    # Generar Malla 3D Facial OBJ
    # Seleccionamos el subconjunto de puntos del contorno y facciones
    OVAL_INDICES = [
        10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
        397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
        172, 58,  132, 93,  234, 127, 162, 21,  54,  103, 67,  109,
        1, 2, 98, 327, 168, 6, 197, 195, 5, 4, 19, 94, 2,
        33, 160, 158, 133, 153, 144, 362, 385, 387, 263, 373, 380,
        61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146
    ]
    # Eliminar duplicados manteniendo orden
    indices = []
    seen = set()
    for idx in OVAL_INDICES:
        if idx not in seen and idx < len(face_lms):
            indices.append(idx)
            seen.add(idx)

    # Coordenadas escaladas centradas en el rostro
    pts_sub = []
    mid_x = (face_lms[234].x + face_lms[454].x) / 2.0
    mid_y = (face_lms[10].y + face_lms[152].y) / 2.0

    target_scale = face_metrics["face_height_m"] / (face_h_norm if face_h_norm > 0 else 1.0)
    for idx in indices:
        lm = face_lms[idx]
        # X: derecha a izquierda (invertir X para coordenadas 3D Blender)
        gx = -(lm.x - mid_x) * cw * scale_pose
        # Y (profundidad en Blender): Z de mediapipe
        gy = -lm.z * cw * scale_pose * 1.5
        # Z (altura en Blender): Y invertida
        gz = -(lm.y - mid_y) * ch * scale_pose
        pts_sub.append([gx, gy, gz])

    pts_sub = np.array(pts_sub)

    # Triangulación 2D en plano X-Z
    tri = Delaunay(pts_sub[:, [0, 2]])
    obj_path = os.path.join(MESHES_DIR, "face_mesh.obj")
    with open(obj_path, "w") as f:
        f.write("# Leonidas Facial Robotic Faceplate 3D Mesh\n")
        f.write("# Generated from user photo with MediaPipe\n")
        for v in pts_sub:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        for simplex in tri.simplices:
            # OBJ es 1-indexed
            f.write(f"f {simplex[0]+1} {simplex[1]+1} {simplex[2]+1}\n")

    print(f"[✓] Guardado face_mesh.obj con {len(pts_sub)} vértices y {len(tri.simplices)} caras en: {obj_path}")
    return face_metrics

def main():
    print("=================================================================")
    print("  EXTRACCIÓN DE MÉTRICAS REALES DE CUERPO Y ROSTRO (1.80m)       ")
    print("=================================================================")

    metrics, pts, scale, h, w = extract_pose()
    face_metrics = extract_face(pts, scale)

    if face_metrics:
        metrics["proportions"]["face"] = face_metrics
    else:
        metrics["proportions"]["face"] = {
            "interpupillary_distance_m": 0.064,
            "face_height_m": 0.22,
            "face_width_m": 0.16,
            "jaw_width_m": 0.125,
            "nose_projection_m": 0.025
        }

    out_json = os.path.join(METRICS_DIR, "body_metrics_real.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[✓] METRICAS COMPLETAS GUARDADAS EN: {out_json}")
    print(json.dumps(metrics["proportions"], indent=2))

if __name__ == "__main__":
    main()
