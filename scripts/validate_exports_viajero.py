"""Reimport both interchange files in empty scenes and verify real content."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
reports=[]
for suffix in ["glb","fbx"]:
    path=ROOT/f"exports/{suffix}/viajero.{suffix}"
    assert path.exists() and path.stat().st_size>10000,f"Exportación vacía: {path}"
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if suffix=="glb":
        bpy.ops.import_scene.gltf(filepath=str(path))
    else:
        bpy.ops.import_scene.fbx(filepath=str(path))
    rigs=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"]
    meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    assert rigs and len(rigs[0].data.bones)>=50,f"Rig ausente/incompleto en {suffix}"
    assert len(meshes)>100,f"Exportación incompleta en {suffix}"
    for rig in rigs:
        rig.animation_data_clear()
        for b in rig.pose.bones:b.matrix_basis.identity()
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    points=[o.evaluated_get(dg).matrix_world@Vector(c) for o in meshes
            for c in o.evaluated_get(dg).bound_box]
    height=max(p.z for p in points)-min(p.z for p in points)
    assert abs(height-1.8)<.02,f"Escala de {suffix}: {height}"
    assert all(o.data.materials for o in meshes),f"Material ausente en {suffix}"
    assert all(o.data.uv_layers for o in meshes),f"UV ausentes en {suffix}"
    morphs=sum(bool(o.data.shape_keys) for o in meshes)
    assert morphs>=3,f"Shape keys ausentes en {suffix}"
    if suffix=="glb":
        assert len(bpy.data.actions)>=13,"GLB sin acciones esperadas"
    reports.append({"format":suffix,"meshes":len(meshes),"bones":len(rigs[0].data.bones),
                    "height_m":height,"morph_meshes":morphs,"actions":len(bpy.data.actions),
                    "status":"PASS"})
(ROOT/"docs/validacion_exportaciones.json").write_text(json.dumps(reports,indent=2))
print("EXPORT_REIMPORT_OK",json.dumps(reports))
