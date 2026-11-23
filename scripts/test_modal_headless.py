"""Integración del método modal con eventos simulados; NO prueba visual de GUI."""
from pathlib import Path
from types import SimpleNamespace
import sys,time,json,socket
import bpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import blender_consumer_modal as addon
from mocap.core import PacketBuilder,encode
from mocap.synthetic import pose

class Timer:
    def as_pointer(self):return 99
class WM:
    def event_timer_add(self,*a,**kw):return Timer()
    def event_timer_remove(self,timer):self.removed=True
    def modal_handler_add(self,op):self.handler=op
wm=WM();wm.removed=False
addon.register();bpy.context.scene.mocap_port=15056
ctx=SimpleNamespace(scene=bpy.context.scene,window=bpy.context.window,screen=SimpleNamespace(areas=[]),window_manager=wm)
fake=SimpleNamespace(report=lambda *x:None)
fake.stop=addon.MOCAP_OT_start.stop
fake.cancel=lambda context:addon.MOCAP_OT_start.cancel(fake,context)
errors=[];sent=0
try:
    assert addon.MOCAP_OT_start.execute(fake,ctx)=={'RUNNING_MODAL'}
    run=addon.MOCAP_OT_start._active;event=SimpleNamespace(type='TIMER',timer=run.timer)
    before=tuple(bpy.data.objects['RIG_Viajero'].pose.bones['forearm.L'].rotation_quaternion)
    sender=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);builder=PacketBuilder('synthetic_modal_integration')
    for i in range(12):
        sender.sendto(encode(builder.build(pose(i/30),t=i/30)),('127.0.0.1',15056));sent+=1
        run.last_tick=time.monotonic()-1
        assert addon.MOCAP_OT_start.modal(fake,ctx,event)=={'RUNNING_MODAL'}
    after=tuple(bpy.data.objects['RIG_Viajero'].pose.bones['forearm.L'].rotation_quaternion)
    assert before!=after
    assert addon.MOCAP_OT_start.modal(fake,ctx,SimpleNamespace(type='MOUSEMOVE'))=={'PASS_THROUGH'}
    run.receiver.last_tracking=time.monotonic()-1
    run.last_tick=time.monotonic()-1
    addon.MOCAP_OT_start.modal(fake,ctx,event)
    assert 'STALE' in ctx.scene.mocap_status
    applied=run.receiver.stats['applied']
    fake.cancel(ctx);sender.close()
    probe=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);probe.bind(('127.0.0.1',15056));probe.close()
    assert wm.removed
    report=dict(events='SIMULATED_TIMER',UDP='real_localhost',sent=sent,applied=applied,
                pose_changed=before!=after,stale_detected=True,socket_released=True,timer_removed=True,
                pass_through=True,errors=[],visual_GUI_test='See separate validation_modal_live.json; personal visual demonstration still pending')
except Exception as exc:report=dict(errors=[repr(exc)],sent=sent)
(ROOT/'docs/mocap/validation_modal_integration.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
if report['errors']:raise RuntimeError(report['errors'])
