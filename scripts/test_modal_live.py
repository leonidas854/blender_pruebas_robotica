"""Prueba automática de eventos TIMER reales en una ventana Blender dedicada."""
from pathlib import Path
import sys,time,socket,json
import bpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import blender_consumer_modal as addon
from mocap.core import PacketBuilder,encode
from mocap.synthetic import pose
# Ventana de prueba dedicada, sólo armature: evita compilar/renderizar el vestuario
# antes de que el bucle de eventos esté disponible. No se guarda esta escena.
full_avatar='--full-avatar' in sys.argv
if not full_avatar:
    for obj in list(bpy.data.objects):
        if obj.name!='RIG_Viajero':bpy.data.objects.remove(obj,do_unlink=True)
addon.register();bpy.context.scene.mocap_port=15055
builder=PacketBuilder('synthetic_live_modal_test');sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
started=None;sent=0;received=0;errors=[];statuses=[];ticks=[]

def step():
    global sent,received,started
    try:
        if started is None:
            result=bpy.ops.mocap.start()
            if result!={'RUNNING_MODAL'}:raise RuntimeError(str(result))
            started=-1
            return .05
        if started==-1:
            started=time.monotonic()
            return .05
        elapsed=time.monotonic()-started
        if elapsed<8.:
            sock.sendto(encode(builder.build(pose(elapsed))),('127.0.0.1',15055));sent+=1
        active=addon.MOCAP_OT_start._active
        if active:
            received=active.receiver.stats['applied'];ticks.append(active.last_ms)
            statuses.append(bpy.context.scene.mocap_status)
        if elapsed<10.:return .04
        if received<5:errors.append('Menos de 5 eventos aplicados')
        if not any('RECIBIENDO' in x for x in statuses):errors.append('Sin estado RECIBIENDO')
        if not any('STALE' in x for x in statuses[-10:]):errors.append('No detectó timeout')
        events=dict(events=active.events,timer_events=active.timer_events) if active else {}
        bpy.ops.mocap.stop();sock.close()
        probe=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);probe.bind(('127.0.0.1',15055));probe.close()
        report=dict(sent=sent,applied=received,live_window_TIMER=True,stale_detected=any('STALE' in x for x in statuses[-10:]),
                    max_tick_ms=max(ticks,default=0),socket_released=True,errors=errors,armature_only=not full_avatar,**events)
    except Exception as exc:
        report=dict(errors=[repr(exc)],sent=sent,applied=received)
    name='validation_modal_lite.json' if 'ligero' in bpy.data.filepath else 'validation_modal_live.json'
    (ROOT/'docs/mocap'/name).write_text(json.dumps(report,indent=2),encoding='utf8')
    bpy.ops.wm.quit_blender()
    return None

bpy.app.timers.register(step,first_interval=.1)
