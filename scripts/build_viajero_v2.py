"""Run through the local Blender MCP bridge or Blender 5.2 Python runner."""
import bpy
import sys
import json
import importlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from viajero_v2 import common,anatomy,hair,wardrobe,scene
from viajero_v2.common import activate
for module in (common,anatomy,hair,wardrobe,scene): importlib.reload(module)


def main():
    target=ROOT/'blender/v2/viajero_esculpido.blend'
    backup=ROOT/'blender/v2/sesion_antes_de_v2.blend'
    if not backup.exists():bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True)
    rig=bpy.data.objects['RIG_Viajero'];rig.animation_data.action=bpy.data.actions['01_A_pose']
    bpy.context.scene.frame_set(1)
    body=anatomy.build(rig)
    print('V2_ANATOMY',len(body.data.vertices),flush=True)
    hair.build(rig);print('V2_HAIR',flush=True)
    wardrobe.pants(rig);wardrobe.sculpt_existing();wardrobe.scarf_and_collars(rig);wardrobe.boots(rig)
    print('V2_WARDROBE',flush=True)
    scene.setup()
    for o in bpy.data.collections['PERSONAJE'].all_objects:
        if o.type=='MESH':
            for m in o.modifiers:
                if m.type=='ARMATURE':m.use_deform_preserve_volume=True
    s=bpy.context.scene;s['version_entrega']='v2 escultorica 2026-11-22'
    s['alcance']='Personaje, rig FK y renders. Captura de movimiento fuera de esta entrega.'
    s['limitaciones']='Escultura procedural editable; parecido interpretado; sin retopologia facial ni mocap.'
    bpy.context.preferences.filepaths.save_version=1
    activate(body);bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(target))
    scene.render(ROOT,'iteracion_02_cuerpo','V2_TresCuartos',(750,1000),24,'13_Presentacion')
    scene.render(ROOT,'iteracion_02_rostro','V2_RostroFrente',(700,700),32)
    # Reproduce the later reviewed corrections as part of the complete build.
    from render_viajero_v2 import normalize_height,test_pose
    from refine_viajero_v2 import refine
    from fix_viajero_v2_layers import main as fix_layers
    from relax_viajero_v2_anatomy import main as relax_anatomy
    from blend_viajero_v2_anatomy import main as blend_anatomy
    normalize_height();test_pose();refine();fix_layers();relax_anatomy(iterations=240);blend_anatomy();relax_anatomy()
    from restore_viajero_v2_hands import main as restore_hands
    restore_hands()
    print('V2_BUILD_OK',flush=True)


if __name__=='__main__':main()
