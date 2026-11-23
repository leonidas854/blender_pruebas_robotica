"""Prueba automática de eventos TIMER reales en una ventana Blender dedicada."""
from pathlib import Path
import sys,time,socket,json
import bpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import blender_consumer_modal as addon
from mocap.core import PacketBuilder,encode
from mocap.synthetic import pose
addon.register();bpy.context.scene.mocap_port=15055
builder=PacketBuilder('synthetic_live_modal_test');sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
started=None;sent=0;received=0;errors=[];statuses=[];ticks=[]

def step():
    global sent,received,started
    if started is None:started=time.monotonic()
    elapsed=time.monotonic()-started
    try:
        if elapsed<.5:return .1
        if addon.MOCAP_OT_start._active is None and sent==0:
            result=bpy.ops.mocap.start()
            if result!={'RUNNING_MODAL'}:raise RuntimeError(str(result))
        if elapsed<2.5:
            sock.sendto(encode(builder.build(pose(elapsed))),('127.0.0.1',15055));sent+=1
        active=addon.MOCAP_OT_start._active
        if active:
            received=active.receiver.stats['applied'];ticks.append(active.last_ms)
            statuses.append(bpy.context.scene.mocap_status)
        if elapsed<3.5:return .04
        if received<5:errors.append('Menos de 5 eventos aplicados')
        if not any('RECIBIENDO' in x for x in statuses):errors.append('Sin estado RECIBIENDO')
        if not any('STALE' in x for x in statuses[-10:]):errors.append('No detectó timeout')
        bpy.ops.mocap.stop();sock.close()
        probe=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);probe.bind(('127.0.0.1',15055));probe.close()
        report=dict(sent=sent,applied=received,live_window_TIMER=True,stale_detected=any('STALE' in x for x in statuses[-10:]),
                    max_tick_ms=max(ticks,default=0),socket_released=True,errors=errors)
    except Exception as exc:
        report=dict(errors=[repr(exc)],sent=sent,applied=received)
    (ROOT/'docs/mocap/validation_modal_live.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    bpy.ops.wm.quit_blender()
    return None

bpy.app.timers.register(step,first_interval=.1)
