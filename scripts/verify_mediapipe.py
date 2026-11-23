"""Prueba de inferencia sobre fotografía existente; no captura de movimiento."""
from pathlib import Path
import sys,json,time,hashlib
import cv2,mediapipe as mp
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mocap.core import PacketBuilder,encode,points_blender
photo=ROOT/'referencias/fotografias_originales/foto_01_cuerpo_tpose.jpeg'
model=ROOT/'models/pose_landmarker_full.task'
frame=cv2.imread(str(photo));frame=cv2.resize(frame,(720,960))
options=mp.tasks.vision.PoseLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_path=str(model)),
    running_mode=mp.tasks.vision.RunningMode.VIDEO,num_poses=1)
times=[];results=[];builder=PacketBuilder('existing_photo_STATIC_validation')
with mp.tasks.vision.PoseLandmarker.create_from_options(options) as detector:
    for i in range(3):
        image=mp.Image(image_format=mp.ImageFormat.SRGB,data=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        t=time.perf_counter();result=detector.detect_for_video(image,i*33);times.append((time.perf_counter()-t)*1000)
        if not result.pose_world_landmarks:raise RuntimeError('No se detectó pose en la foto')
        points=[dict(x=p.x,y=p.y,z=p.z,visibility=p.visibility) for p in result.pose_world_landmarks[0]]
        packet=builder.build(points,t=i*.033);encode(packet);results.append(packet)
report=dict(mediapipe=mp.__version__,opencv=cv2.__version__,input='existing personal photo; repeated static frames, NOT motion capture',
            world_landmarks=len(points),frames=3,inference_ms=times,
            left_shoulder_x=points[11]['x'],right_shoulder_x=points[12]['x'],
            visible_landmarks=sum(p['visibility']>=.6 for p in points),
            model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),errors=[])
if points[11]['x']<=points[12]['x']:report['errors'].append('Revisar orientación de lado izquierdo en imagen sin espejo')
(ROOT/'docs/mocap/validation_mediapipe.json').write_text(json.dumps(report,indent=2),encoding='utf8')
(ROOT/'tmp/mocap/photo_validation_landmarks.json').write_text(json.dumps(results[-1],indent=2),encoding='utf8')
# Archivo efímero para recorrer exactamente la ruta --video del productor.
writer=cv2.VideoWriter(str(ROOT/'tmp/mocap/foto_estatica_PRUEBA_API.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),30,(720,960))
if not writer.isOpened():raise RuntimeError('No se pudo crear video de prueba')
for _ in range(45):writer.write(frame)
writer.release()
for tag in ('A','B'):
    video=ROOT/'entrega/mocap'/f'ensayo_sintetico_{tag}.mp4'
    if not video.exists():continue
    cap=cv2.VideoCapture(str(video));cap.set(cv2.CAP_PROP_POS_FRAMES,45);ok,img=cap.read()
    if ok:cv2.imwrite(str(ROOT/'tmp/mocap'/f'preview_{tag}_frame45.png'),img)
    cap.release()
print(json.dumps(report,indent=2))
if report['errors']:raise RuntimeError(report['errors'])
