"""Ejecutar desde Blender > Scripting, o con --python. Panel N > Mocap."""
from pathlib import Path
import sys
import time
from types import SimpleNamespace
import bpy
ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from mocap.core import Receiver
from mocap.blender_adapter import Retargeter

class MOCAP_OT_start(bpy.types.Operator):
    bl_idname='mocap.start'
    bl_label='Iniciar UDP'
    _active=None
    _generation=0

    def execute(self,context):
        if MOCAP_OT_start._active:
            self.report({'WARNING'},'Ya existe un receptor');return {'CANCELLED'}
        rig=bpy.data.objects.get(context.scene.mocap_rig)
        if rig is None or rig.type!='ARMATURE':
            self.report({'ERROR'},'Rig no encontrado');return {'CANCELLED'}
        try:
            retarget=Retargeter(rig)
            receiver=Receiver(context.scene.mocap_port)
        except (OSError,ValueError) as exc:
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
        previous_action=rig.animation_data.action if rig.animation_data else None
        rig.animation_data_create();rig.animation_data.action=None
        timer=context.window_manager.event_timer_add(1/30,window=context.window)
        MOCAP_OT_start._generation+=1;self._token=MOCAP_OT_start._generation
        MOCAP_OT_start._active=SimpleNamespace(receiver=receiver,retarget=retarget,timer=timer,
            previous_action=previous_action,last_ms=0.,last_count=0,token=self._token)
        context.window_manager.modal_handler_add(self)
        context.scene.mocap_status='Esperando UDP'
        return {'RUNNING_MODAL'}

    def modal(self,context,event):
        run=MOCAP_OT_start._active
        if run is None or run.token!=self._token:return {'CANCELLED'}
        if event.type=='ESC':self.cancel(context);return {'CANCELLED'}
        if event.type!='TIMER' or event.timer!=run.timer:return {'PASS_THROUGH'}
        start=time.perf_counter()
        try:
            packet=run.receiver.poll()
            if packet and packet['tracking']:run.last_count=run.retarget.apply(packet)
            run.last_ms=(time.perf_counter()-start)*1000
            state='STALE: pose retenida' if run.receiver.stale else 'RECIBIENDO'
            context.scene.mocap_status=f'{state} | {run.last_count} huesos | tick {run.last_ms:.1f} ms | rechazados {run.receiver.stats["rejected"]}'
        except Exception as exc:
            self.report({'ERROR'},str(exc));self.cancel(context);return {'CANCELLED'}
        for area in context.screen.areas:
            if area.type=='VIEW_3D':area.tag_redraw()
        return {'RUNNING_MODAL'}

    def cancel(self,context):
        run=MOCAP_OT_start._active
        if run and run.token==self._token:self.stop(context)

    @staticmethod
    def stop(context):
        run=MOCAP_OT_start._active
        if run is None:return
        run.receiver.close();context.window_manager.event_timer_remove(run.timer)
        MOCAP_OT_start._active=None
        run.retarget.rig.animation_data.action=run.previous_action
        context.scene.mocap_status='Detenido; acción anterior restaurada'

class MOCAP_OT_stop(bpy.types.Operator):
    bl_idname='mocap.stop'
    bl_label='Detener UDP'
    def execute(self,context):
        MOCAP_OT_start.stop(context)
        return {'FINISHED'}

class MOCAP_PT_panel(bpy.types.Panel):
    bl_label='Viajero / captura local'
    bl_idname='MOCAP_PT_panel'
    bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Mocap'
    def draw(self,context):
        col=self.layout.column();col.prop(context.scene,'mocap_rig');col.prop(context.scene,'mocap_port')
        col.operator('mocap.start');col.operator('mocap.stop')
        col.label(text=context.scene.mocap_status)
        col.label(text='Fuente: productor externo. ESC detiene.')

CLASSES=(MOCAP_OT_start,MOCAP_OT_stop,MOCAP_PT_panel)
def register():
    old=getattr(bpy.types,'MOCAP_OT_start',None)
    if old and old._active:old.stop(bpy.context)
    for cls in reversed(CLASSES):
        old=getattr(bpy.types,cls.__name__,None)
        if old:bpy.utils.unregister_class(old)
    bpy.types.Scene.mocap_rig=bpy.props.StringProperty(name='Armature',default='RIG_Viajero')
    bpy.types.Scene.mocap_port=bpy.props.IntProperty(name='Puerto',default=5005,min=1024,max=65535)
    bpy.types.Scene.mocap_status=bpy.props.StringProperty(default='Detenido')
    for cls in CLASSES:bpy.utils.register_class(cls)

if __name__=='__main__':register()
