"""Actualiza únicamente las copias mocap con un inicio portátil."""
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
bootstrap="""from pathlib import Path
import bpy, runpy
here = Path(bpy.data.filepath).resolve().parent
root = next((p for p in (here, *here.parents) if (p/'blender_consumer_modal.py').is_file()), None)
if root is None:
    raise RuntimeError('No se encuentra blender_consumer_modal.py junto al proyecto')
runpy.run_path(str(root/'blender_consumer_modal.py'), run_name='__main__')
"""
bpy.context.preferences.filepaths.save_version=0
for name in ['robot_humanoide_mocap.blend','prueba_A_sintetica.blend','robot_humanoide_retargeting.blend']:
    path=ROOT/'blender/mocap'/name
    bpy.ops.wm.open_mainfile(filepath=str(path))
    text=bpy.data.texts.get('INICIAR_MOCAP.py')
    if text:text.clear();text.write(bootstrap)
    bpy.context.scene.display.shading.show_shadows=False
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    print('PORTABLE',name)
