#!/usr/bin/env python3
"""
scripts/face_mesh_extractor.py
Extracción de puntos faciales 3D, métricas antropométricas y generación de malla 3D (OBJ)
a partir de una fotografía para modelado y caracterización robótica en Blender.
"""

import os
import sys
import json
import argparse
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from scipy.spatial import Delaunay

# Puntos clave canónicos de MediaPipe (468/478 landmarks)
KEY_POINTS = {
    "forehead": 10,
    "chin": 152,
    "nose_tip": 1,
    "nose_bridge": 168,
    "left_eye_outer": 33,
    "left_eye_inner": 133,
    "right_eye_inner": 362,
    "right_eye_outer": 263,
    "left_pupil": 468,
    "right_pupil": 473,
    "left_temple": 234,
    "right_temple": 454,
    "mouth_left": 61,
    "mouth_right": 291,
    "lip_upper": 0,
    "lip_lower": 17,
}

# Índices del contorno facial externo para delimitar la máscara
OVAL_INDICES = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
    397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
    172, 58,  132, 93,  234, 127, 162, 21,  54,  103, 67,  109
]

def load_detector(model_path: str = "models/face_landmarker.task"):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Modelo no encontrado en {model_path}. Ejecuta el instalador.")

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=1
    )
    return vision.FaceLandmarker.create_from_options(options)

def extract_features(image_path: str, output_dir: str = "character_data"):
    os.makedirs(output_dir, exist_ok=True)
    detector = load_detector()

    mp_image = mp.Image.create_from_file(image_path)
    cv_image = cv2.imread(image_path)
    h, w, _ = cv_image.shape

    print(f"[*] Analizando imagen ({w}x{h} px)...")
    results = detector.detect(mp_image)

    if not results.face_landmarks:
        print("[!] No se detectó ningún rostro en la imagen.")
        return None

    landmarks = results.face_landmarks[0]
    num_landmarks = len(landmarks)
    print(f"[+] Rostro detectado con éxito ({num_landmarks} landmarks 3D).")

    # Extraer coordenadas 3D en espacio métrico normalizado
    # MediaPipe: x [0..1] izq->der, y [0..1] arr->aba, z relativo a profundidad
    coords = np.zeros((num_landmarks, 3), dtype=np.float32)
    for idx, lm in enumerate(landmarks):
        # Convertir a sistema centrado en la cabeza (X derecha, Y arriba, Z hacia el frente)
        coords[idx, 0] = (lm.x - 0.5) * 2.0
        coords[idx, 1] = -(lm.y - 0.5) * 2.0  # Invertir eje Y para Blender
        coords[idx, 2] = -lm.z * 2.0          # Z positivo hacia afuera de la cara

    # Normalizar escala de la cabeza (frente a barbilla = 1.0 unidad)
    forehead_pt = coords[KEY_POINTS["forehead"]]
    chin_pt = coords[KEY_POINTS["chin"]]
    head_height = float(np.linalg.norm(forehead_pt - chin_pt))
    if head_height > 1e-4:
        scale = 1.0 / head_height
        coords *= scale

    # Centrar en el puente nasal (landmark 168)
    origin = coords[KEY_POINTS["nose_bridge"]].copy()
    coords -= origin

    # Calcular métricas antropométricas para el robot
    left_pupil_idx = KEY_POINTS["left_pupil"] if num_landmarks > 468 else KEY_POINTS["left_eye_inner"]
    right_pupil_idx = KEY_POINTS["right_pupil"] if num_landmarks > 468 else KEY_POINTS["right_eye_inner"]

    left_pupil = coords[left_pupil_idx]
    right_pupil = coords[right_pupil_idx]
    interpupillary_dist = float(np.linalg.norm(left_pupil - right_pupil))

    left_temple = coords[KEY_POINTS["left_temple"]]
    right_temple = coords[KEY_POINTS["right_temple"]]
    face_width = float(np.linalg.norm(left_temple - right_temple))

    nose_tip = coords[KEY_POINTS["nose_tip"]]
    nose_projection = float(nose_tip[2])

    mouth_left = coords[KEY_POINTS["mouth_left"]]
    mouth_right = coords[KEY_POINTS["mouth_right"]]
    mouth_width = float(np.linalg.norm(mouth_left - mouth_right))

    metrics = {
        "interpupillary_distance": interpupillary_dist,
        "face_width": face_width,
        "face_height": 1.0,
        "face_aspect_ratio": face_width / 1.0,
        "nose_projection": nose_projection,
        "mouth_width": mouth_width,
        "left_eye_pos": [float(x) for x in left_pupil],
        "right_eye_pos": [float(x) for x in right_pupil],
        "chin_pos": [float(x) for x in coords[KEY_POINTS["chin"]]],
        "forehead_pos": [float(x) for x in coords[KEY_POINTS["forehead"]]],
        "nose_tip_pos": [float(x) for x in nose_tip],
    }

    # Guardar métricas en JSON
    metrics_path = os.path.join(output_dir, "character_profile.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"[+] Métricas guardadas en: {metrics_path}")

    # Generar triangulación 2D -> Malla 3D usando Delaunay sobre plano frontal (XY)
    # Filtramos triángulos con aristas excesivamente largas
    tri = Delaunay(coords[:, :2])
    valid_faces = []
    max_edge_len = 0.25  # Evitar caras que crucen el fondo
    for simplex in tri.simplices:
        p0, p1, p2 = coords[simplex[0]], coords[simplex[1]], coords[simplex[2]]
        d01 = np.linalg.norm(p0 - p1)
        d12 = np.linalg.norm(p1 - p2)
        d20 = np.linalg.norm(p2 - p0)
        if d01 < max_edge_len and d12 < max_edge_len and d20 < max_edge_len:
            valid_faces.append(simplex)

    # Exportar archivo OBJ
    obj_path = os.path.join(output_dir, "face_mesh.obj")
    with open(obj_path, "w", encoding="utf-8") as f:
        f.write("# Face Mesh generada para Caracterizacion de Robotica\n")
        f.write("o FacePlatedModel\n")
        for v in coords:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        for lm in landmarks:
            f.write(f"vt {lm.x:.6f} {1.0 - lm.y:.6f}\n")
        for face in valid_faces:
            # 1-indexed para OBJ
            f.write(f"f {face[0]+1}/{face[0]+1} {face[1]+1}/{face[1]+1} {face[2]+1}/{face[2]+1}\n")
    print(f"[+] Malla 3D OBJ guardada en: {obj_path} ({len(coords)} vertices, {len(valid_faces)} caras)")

    # Generar imagen de preview con anotaciones
    preview_img = cv_image.copy()
    for idx, lm in enumerate(landmarks):
        px, py = int(lm.x * w), int(lm.y * h)
        if idx in KEY_POINTS.values():
            cv2.circle(preview_img, (px, py), 4, (0, 255, 255), -1)
        elif idx in OVAL_INDICES:
            cv2.circle(preview_img, (px, py), 2, (0, 255, 0), -1)
        else:
            cv2.circle(preview_img, (px, py), 1, (255, 100, 0), -1)

    # Resaltar ojos y centro
    for pt_idx in (left_pupil_idx, right_pupil_idx):
        if pt_idx < len(landmarks):
            px, py = int(landmarks[pt_idx].x * w), int(landmarks[pt_idx].y * h)
            cv2.circle(preview_img, (px, py), 6, (0, 0, 255), 2)

    preview_path = os.path.join(output_dir, "landmark_preview.jpg")
    cv2.imwrite(preview_path, preview_img)
    print(f"[+] Vista previa con landmarks guardada en: {preview_path}")

    return metrics

def main():
    parser = argparse.ArgumentParser(description="Extrae malla 3D y landmarks de rostro con MediaPipe")
    parser.add_argument("--image", type=str, default="character_data/photo.jpg", help="Ruta de la imagen de entrada")
    parser.add_argument("--output", type=str, default="character_data", help="Directorio de salida")
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"[!] Error: La imagen {args.image} no existe. Toma una foto con scripts/capture_photo.py primero.")
        sys.exit(1)

    result = extract_features(args.image, args.output)
    sys.exit(0 if result is not None else 1)

if __name__ == "__main__":
    main()
