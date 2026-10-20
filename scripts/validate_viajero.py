"""Validate the saved deliverable in a fresh Blender process, without modifying it."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]


def validate():
    target = ROOT / "blender/personaje_final.blend"
    assert target.is_file(), "Falta la escena ensamblada personaje_final.blend"
    bpy.ops.wm.open_mainfile(filepath=str(target))
    scene = bpy.context.scene
    required = ["Cuerpo", "Rostro", "Camisa", "Chaleco", "Abrigo", "Pantalon.L",
                "Pantalon.R", "Bufanda", "Bota.L", "Bota.R", "Bolso",
                "Talisman_Disco", "Gafas_Aro.L", "Gafas_Aro.R", "RIG_Viajero"]
    missing = [n for n in required if n not in bpy.data.objects]
    assert not missing, f"Faltan componentes: {missing}"
    rig = bpy.data.objects["RIG_Viajero"]
    assert len(rig.data.bones) >= 50, "Falta esqueleto corporal/dedos"
    meshes = [o for o in bpy.data.collections["PERSONAJE"].all_objects if o.type == "MESH"]
    assert all(o.data.materials for o in meshes), "Malla sin material"
    assert all(o.data.uv_layers for o in meshes), "Malla sin UV"
    assert all(any(m.type == "ARMATURE" for m in o.modifiers) for o in meshes), "Malla sin vincular al rig"
    for o in meshes:
        assert all(v.groups and abs(sum(g.weight for g in v.groups) - 1) < .002
                   for v in o.data.vertices), f"Pesos incompletos en {o.name}"
    rig.animation_data_clear()
    for b in rig.pose.bones:
        b.matrix_basis.identity()
    scene.frame_set(1)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    coords = [o.evaluated_get(dg).matrix_world @ Vector(c) for o in meshes
              for c in o.evaluated_get(dg).bound_box]
    height = max(p.z for p in coords) - min(p.z for p in coords)
    assert abs(height - 1.8) < .012, f"Altura incorrecta: {height}"
    coat=bpy.data.objects["Abrigo"]
    rest_width=coat.evaluated_get(dg).dimensions.x
    rig.animation_data_create()
    rig.animation_data.action=bpy.data.actions["02_T_pose"]
    scene.frame_set(1);bpy.context.view_layer.update()
    posed_width=coat.evaluated_get(bpy.context.evaluated_depsgraph_get()).dimensions.x
    assert posed_width < rest_width*1.2, "Los brazos arrastran paneles del torso del abrigo"
    rig.animation_data.action=bpy.data.actions["01_A_pose"]
    scene.frame_set(1);bpy.context.view_layer.update()
    assert len(bpy.data.actions) >= 10, "Faltan pruebas de pose"
    assert bpy.data.objects["Rostro"].data.shape_keys, "Faltan expresiones"
    assert len(bpy.data.objects["Rostro"].data.shape_keys.key_blocks) >= 4
    for o in meshes:
        if o.data.shape_keys:
            assert all(abs(k.value)<1e-6 for k in list(o.data.shape_keys.key_blocks)[1:]), \
                f"La pose neutral tiene expresiones activas: {o.name}"
    assert scene.unit_settings.system == "METRIC"
    assert len([o for o in scene.objects if o.type == "LIGHT"]) >= 3
    report = {
        "blender": bpy.app.version_string,
        "height_m": height, "meshes": len(meshes),
        "vertices": sum(len(o.data.vertices) for o in meshes),
        "bones": len(rig.data.bones),
        "actions": [a.name for a in bpy.data.actions],
        "materials": sorted({m.name for o in meshes for m in o.data.materials}),
        "checks": "PASS: componentes, escala, UV, materiales, pesos normalizados, rig y acciones",
        "limits": "Las comprobaciones no certifican parecido facial, retopología de producción ni ausencia de colisiones en toda animación.",
    }
    (ROOT / "docs/validacion_viajero.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    validate()
