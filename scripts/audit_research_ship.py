import bpy, bmesh, json
from pathlib import Path
hull=bpy.data.objects['01 / Hull']
bm=bmesh.new();bm.from_mesh(hull.data)
result={
    'objects':len(bpy.context.scene.objects),
    'mesh_objects':sum(o.type=='MESH' for o in bpy.context.scene.objects),
    'hull_vertices':len(bm.verts),
    'hull_faces':len(bm.faces),
    'hull_nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
    'hull_dimensions':list(hull.dimensions),
    'mesh_vertices_total':sum(len(o.data.vertices) for o in bpy.context.scene.objects if o.type=='MESH'),
    'camera_location':list(bpy.context.scene.camera.location),
    'camera_lens':bpy.context.scene.camera.data.lens,
}
bm.free()
Path(bpy.data.filepath).with_name('mesh-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
