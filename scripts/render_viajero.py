"""Render and export the saved character. Does not rebuild modelling work."""
import bpy
import sys
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import build_viajero as build
import viajero_lib as g


def render_all(group="all"):
    s=bpy.context.scene
    rig=bpy.data.objects["RIG_Viajero"]
    g.COL=bpy.data.collections["ESTUDIO"]
    build.setup_world()
    scale=s["factor_escala"];low=s["suelo_origen"]
    def p(x,y,z):return (x*scale,y*scale,(z-low)*scale)
    for name,loc,target,size in [
        ("CAM_Perfil_derecho",(5,0,.92),(0,0,.92),2.12),
        ("CAM_Rostro_frontal",(0,-3,1.65),p(0,0,1.67),.40),
        ("CAM_Rostro_perfil",(-3,0,1.65),p(0,0,1.67),.40),
        ("CAM_Cabello",(.8,-1.8,2.15),p(0,.015,1.75),.33),
        ("CAM_Abrigo",(1.7,-3,1.7),p(0,0,1.25),.96),
        ("CAM_Cinturones",(.5,-3,1.2),p(0,-.1,1.04),.58),
        ("CAM_Bolso",(1.6,-2,1.3),p(.24,0,.93),.40),
        ("CAM_Botas",(.8,-2,.6),p(0,-.04,.15),.47)]:
        if name not in bpy.data.objects:g.camera(name,loc,target,size)
    # A perspective presentation camera is explicitly distinct from the orthographic views.
    hero=bpy.data.objects.get("CAM_Hero") or g.camera("CAM_Hero",(2.3,-4.8,1.95),(0,0,.94),2.2)
    hero.data.type="PERSP";hero.data.lens=72
    for name,camera in [("frente","CAM_Frente"),("perfil_izquierdo","CAM_Perfil"),
                        ("perfil_derecho","CAM_Perfil_derecho"),("espalda","CAM_Espalda"),
                        ("tres_cuartos","CAM_Tres_cuartos")]:
        if group not in {"all","views"}:continue
        build.render_view(camera,f"renders/turnaround/{name}.png",(1200,1600),samples=48)
    for name,camera in [
        ("rostro_frente","CAM_Rostro_frontal"),("rostro_perfil","CAM_Rostro_perfil"),
        ("cabello","CAM_Cabello"),("abrigo","CAM_Abrigo"),
        ("cinturones","CAM_Cinturones"),("bolso","CAM_Bolso"),("botas","CAM_Botas"),
        ("talisman","CAM_Talisman")]:
        if group not in {"all","details"}:continue
        folder="rostro" if name.startswith(("rostro","cabello")) else "accesorios"
        build.render_view(camera,f"renders/{folder}/{name}.png",(1200,1200),samples=48)
    for action in bpy.data.actions:
        if group not in {"all","poses"}:continue
        if not action.name[:2].isdigit():continue
        build.render_view("CAM_Frente",f"renders/poses/{action.name}.png",(720,960),
                          action=action.name,samples=24)
    if group in {"all","final"}:
        build.render_view("CAM_Hero","renders/final/viajero_presentacion.png",
                          (1920,2400),action="13_Presentacion",samples=96)
        build.render_view("CAM_Hero","renders/final/viajero_1920x1080.png",
                          (1920,1080),action="13_Presentacion",samples=64)
    # Neutral A pose is the canonical rest view. Retain the presentation camera selection.
    rig.animation_data.action=bpy.data.actions["01_A_pose"]
    s.frame_set(1);s.camera=bpy.data.objects["CAM_Tres_cuartos"]
    s.render.resolution_x=1600;s.render.resolution_y=2000
    s.render.filepath="//renders/final/nuevo_render.png"
    g.activate(rig)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"blender/personaje_final.blend"))
    evidence={
        "lights":[{"name":o.name,"position":list(o.location),"power_w":o.data.energy,
                   "size_m":o.data.size,"color":list(o.data.color)}
                  for o in bpy.data.objects if o.type=="LIGHT"],
        "materials": {m.name:{"nodes":[{"name":n.name,"type":n.bl_idname} for n in m.node_tree.nodes],
            "links":[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name]
                     for l in m.node_tree.links]}
            for m in bpy.data.materials if m.use_nodes},
        "camera_types": {o.name:o.data.type for o in bpy.data.objects if o.type=="CAMERA"}
    }
    (ROOT/"docs/evidencia_escena.json").write_text(json.dumps(evidence,indent=2,ensure_ascii=False))
    if group in {"all","export"}:export()


def export():
    """Portable geometry/rig export; procedural shaders are simplified to PBR values."""
    rig=bpy.data.objects["RIG_Viajero"]
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    for o in bpy.data.collections["PERSONAJE"].all_objects:
        if o.type=="MESH" and not o.hide_render:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.gltf(filepath=str(ROOT/"exports/glb/viajero.glb"),
        use_selection=True,export_format="GLB",export_animations=True,
        export_animation_mode="ACTIONS",export_morph=True,export_skins=True)
    bpy.ops.export_scene.fbx(filepath=str(ROOT/"exports/fbx/viajero.fbx"),
        use_selection=True,object_types={"MESH","ARMATURE"},add_leaf_bones=False,
        bake_anim=False,apply_unit_scale=True,path_mode="AUTO")
    print("VIAJERO_EXPORT_OK",flush=True)


if __name__=="__main__":
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/"blender/personaje_final.blend"))
    args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    group=args[args.index("--group")+1] if "--group" in args else "all"
    assert group in {"all","views","details","poses","final","export"},group
    render_all(group)
