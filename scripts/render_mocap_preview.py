"""Video breve de ensayo, rotulado; no sustituye videos personales de rúbrica."""
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
s=bpy.context.scene
s.render.engine='BLENDER_WORKBENCH';s.display.shading.show_shadows=False
s.render.resolution_x=720;s.render.resolution_y=960;s.render.resolution_percentage=100
s.render.fps=30;s.frame_start=1;s.frame_end=180
s.camera=bpy.data.objects['CAM_Mocap'];s.camera.data.ortho_scale=2.22
text=bpy.data.curves.new('AVISO_ENSAYO','FONT');text.body='ENSAYO SINTETICO\nNO ES CAPTURA PERSONAL'
text.align_x='CENTER';text.size=.041;text.space_line=1.2
ob=bpy.data.objects.new('AVISO_ENSAYO',text);s.collection.objects.link(ob);ob.parent=s.camera
ob.location=(0,.99,-3);ob.rotation_euler=(0,0,0)
mat=bpy.data.materials.new('Aviso_blanco');mat.diffuse_color=(1,1,1,1);text.materials.append(mat)
s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG'
s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='MEDIUM'
tag='B' if 'retargeting' in Path(bpy.data.filepath).stem else 'A'
s.render.filepath=str(ROOT/'entrega/mocap'/f'ensayo_sintetico_{tag}.mp4')
bpy.ops.render.render(animation=True)
print('SYNTHETIC_PREVIEW_WRITTEN',s.render.filepath)
