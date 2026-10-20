#!/usr/bin/env python3
"""
scripts/capture_photo.py
Módulo de captura y preparación de fotografía para caracterización 3D en robótica.
Permite capturar desde webcam en tiempo real o procesar una imagen existente (JPG/PNG).
"""

import os
import sys
import argparse
import cv2

def capture_from_webcam(output_path: str, camera_index: int = 0):
    print(f"[*] Iniciando cámara web (índice {camera_index})...")
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"[!] Error: No se pudo abrir la cámara {camera_index}.")
        print("[*] Si estás en un portátil con múltiples cámaras, prueba con --camera 1")
        return False

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("[*] Controles:")
    print("    [ESPACIO] : Capturar foto")
    print("    [ESC / Q] : Cancelar")

    window_name = "Captura de Foto - Robotica (Presiona ESPACIO)"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    captured = False
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[!] Error al leer cuadro de la cámara.")
            break

        # Espejo horizontal para que la visualización sea natural
        display_frame = cv2.flip(frame, 1)

        # Guía visual para centrar el rostro
        h, w = display_frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        radius_x, radius_y = int(w * 0.22), int(h * 0.35)
        overlay = display_frame.copy()
        cv2.ellipse(overlay, (center_x, center_y), (radius_x, radius_y), 0, 0, 360, (0, 255, 200), 2)
        cv2.putText(overlay, "Centra tu rostro aqui y presiona ESPACIO", (center_x - 220, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 200), 2)
        cv2.imshow(window_name, overlay)

        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # ESPACIO
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, display_frame)
            print(f"[+] Foto capturada y guardada exitosamente en: {output_path}")
            captured = True
            break
        elif key in (27, ord('q'), ord('Q')):
            print("[*] Captura cancelada por el usuario.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return captured

def process_existing_image(input_image_path: str, output_path: str):
    if not os.path.exists(input_image_path):
        print(f"[!] Error: El archivo no existe: {input_image_path}")
        return False

    img = cv2.imread(input_image_path)
    if img is None:
        print(f"[!] Error: No se pudo decodificar la imagen: {input_image_path}")
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img)
    h, w = img.shape[:2]
    print(f"[+] Imagen procesada ({w}x{h} px) guardada en: {output_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Captura o procesa fotografía para modelado 3D de robótica")
    parser.add_argument("--image", type=str, help="Ruta a una imagen existente (JPG/PNG)")
    parser.add_argument("--camera", type=int, default=0, help="Índice de la webcam (default: 0)")
    parser.add_argument("--output", type=str, default="character_data/photo.jpg", help="Ruta de salida")
    args = parser.parse_args()

    os.makedirs("character_data", exist_ok=True)

    if args.image:
        success = process_existing_image(args.image, args.output)
    else:
        success = capture_from_webcam(args.output, args.camera)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
