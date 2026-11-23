"""Captura externa: webcam/video -> MediaPipe Tasks -> One Euro -> JSON UDP."""
import argparse
import json
import socket
import time
from pathlib import Path
from mocap.core import PacketBuilder, encode, joint_state

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--camera',type=int,default=0)
    ap.add_argument('--video',type=Path)
    ap.add_argument('--synthetic',action='store_true',help='Fixture, no captura real')
    ap.add_argument('--seconds',type=float,default=0,help='0: hasta Q/Ctrl+C')
    ap.add_argument('--port',type=int,default=5005)
    ap.add_argument('--ros-port',type=int,default=5006)
    ap.add_argument('--min-cutoff',type=float,default=1.)
    ap.add_argument('--beta',type=float,default=.03)
    ap.add_argument('--model',type=Path,default=Path(__file__).parent/'models/pose_landmarker_full.task')
    ap.add_argument('--record',type=Path,help='JSONL de landmarks; contiene datos personales')
    ap.add_argument('--sample',type=Path,help='Último JointState válido')
    ap.add_argument('--no-preview',action='store_true')
    args=ap.parse_args()
    source='synthetic_fixture' if args.synthetic else ('video:'+args.video.name if args.video else 'webcam')
    builder=PacketBuilder(source,args.min_cutoff,args.beta)
    writer=None;cap=None;detector=None;count=0;tracked=0;durations=[];start=time.monotonic()
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
        if args.record:
            args.record.parent.mkdir(parents=True,exist_ok=True)
            writer=args.record.open('w',encoding='utf8')
        if not args.synthetic:
            import cv2
            import mediapipe as mp
            if not args.model.is_file():raise FileNotFoundError(args.model)
            cap=cv2.VideoCapture(str(args.video) if args.video else args.camera)
            if not cap.isOpened():raise RuntimeError('No se pudo abrir cámara/video')
            options=mp.tasks.vision.PoseLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(args.model)),
                running_mode=mp.tasks.vision.RunningMode.VIDEO,num_poses=1,
                min_pose_detection_confidence=.5,min_tracking_confidence=.5)
            detector=mp.tasks.vision.PoseLandmarker.create_from_options(options)
            fps=cap.get(cv2.CAP_PROP_FPS) or 30.
        last_ms=-1
        while not args.seconds or time.monotonic()-start<args.seconds:
            before=time.monotonic();elapsed=before-start
            if args.synthetic:
                from mocap.synthetic import pose
                points=pose(elapsed);filter_t=before
            else:
                ok,frame=cap.read()
                if not ok:break
                # Video usa su propio tiempo; webcam, reloj monotónico de captura.
                stamp=max(last_ms+1,int(count/fps*1000) if args.video else int(elapsed*1000))
                last_ms=stamp;filter_t=stamp/1000
                rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                result=detector.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb),stamp)
                points=[dict(x=p.x,y=p.y,z=p.z,visibility=p.visibility) for p in result.pose_world_landmarks[0]] if result.pose_world_landmarks else []
                if not args.no_preview:
                    cv2.putText(frame,'Q: salir | WORLD landmarks | '+str(bool(points)),(15,30),cv2.FONT_HERSHEY_SIMPLEX,.65,(0,220,0),2)
                    cv2.imshow('Mocap Viajero - imagen sin espejo',frame)
                    if cv2.waitKey(1)&255==ord('q'):break
            packet=builder.build(points,filter_t)
            data=encode(packet)
            sock.sendto(data,('127.0.0.1',args.port))
            sock.sendto(data,('127.0.0.1',args.ros_port))
            if writer:writer.write(data.decode()+'\n')
            if packet['tracking']:
                tracked+=1
                if args.sample:
                    args.sample.parent.mkdir(parents=True,exist_ok=True)
                    args.sample.write_text(json.dumps(joint_state(packet),indent=2),encoding='utf8')
            count+=1;durations.append((time.monotonic()-before)*1000)
            if args.synthetic:time.sleep(max(0,1/30-(time.monotonic()-before)))
            elif args.video:time.sleep(max(0,count/fps-(time.monotonic()-start)))
    except KeyboardInterrupt:pass
    finally:
        if detector:detector.close()
        if cap:cap.release()
        if not args.synthetic:
            try:cv2.destroyAllWindows()
            except NameError:pass
        if writer:writer.close()
        sock.close()
    report=dict(source=source,frames=count,tracked=tracked,elapsed_s=time.monotonic()-start,
                mean_producer_ms=sum(durations)/len(durations) if durations else None,
                warning='Tiempo de productor, NO latencia extremo a extremo')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
