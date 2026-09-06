"""Blender demo: --python ship_live_demo.py -- --env PATH --output DIR [--stream]."""
import argparse
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--env', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--stream', action='store_true')
parser.add_argument('--clips', type=int, default=12)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
out = Path(args.output).resolve()
out.mkdir(parents=True, exist_ok=True)
for line in Path(args.env).read_text(encoding='utf-8-sig').splitlines():
    if line.strip().startswith('FAL_KEY='):
        os.environ['FAL_KEY'] = line.split('=', 1)[1].strip().strip('\"\'')
import addon_utils
addon_utils.enable('bl_ext.user_default.fal_ai', default_set=True)
from bl_ext.user_default.fal_ai import live_preview, live_stream

bpy.context.preferences.view.show_splash = False
scene = bpy.context.scene
scene.name = 'PELAGIC / Expedition ship'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene.render.fps = 24
scene.frame_start, scene.frame_end = 1, 1441
scene.render.resolution_x, scene.render.resolution_y = 848, 480
scene.render.resolution_percentage = 100
scene.render.filepath = str(out)+os.sep

def material(name, color, metallic=0, roughness=.35):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    p=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
    if p:
        p.inputs['Base Color'].default_value=(*color,1)
        p.inputs['Metallic'].default_value=metallic
        p.inputs['Roughness'].default_value=roughness
    return m

navy=material('Hull / Atlantic midnight',(.035,.105,.15),.5)
orange=material('Safety / vermilion',(.97,.24,.045))
white=material('Superstructure / ivory',(.83,.87,.85),.25)
glass=material('Bridge glazing / arctic blue',(.025,.20,.28),.7,.1)
deck=material('Deck / slate',(.20,.28,.29))
steel=material('Rail / brushed aluminium',(.59,.68,.68),.7)
black=material('Rubber / graphite',(.018,.027,.029))
water=material('Ocean / deep teal',(.025,.22,.29),.4,.16)
foam=material('Wake / sea foam',(.54,.79,.81))

bpy.ops.object.empty_add()
ship=bpy.context.object
ship.name='PELAGIC — animated ship root'

def mesh(name, verts, faces, mat, parent=True):
    data=bpy.data.meshes.new(name)
    data.from_pydata(verts,[],faces)
    data.update()
    obj=bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    if parent: obj.parent=ship
    return obj

def box(name, loc, scale, mat, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object
    o.name=name
    o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    o.parent=ship
    if bevel:
        m=o.modifiers.new('Fabricated edges','BEVEL'); m.width=bevel; m.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=radius,depth=depth,location=loc,rotation=rotation)
    o=bpy.context.object; o.name=name; o.data.materials.append(mat); o.parent=ship
    for p in o.data.polygons: p.use_smooth=True
    return o

def pipe(name, points, radius, mat, parent=True):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=radius; c.bevel_resolution=2
    spline=c.splines.new('POLY'); spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,c); scene.collection.objects.link(o); c.materials.append(mat)
    if parent: o.parent=ship
    return o

# Multiple chine stations form the actual hull, including a pointed raised bow.
stations=[(-6.5,1.25),(-5.8,1.75),(-3.8,1.92),(0,1.94),(3,1.7),(5,1.05),(6.65,.025)]
verts=[]
for x,w in stations:
    bow=max(0,(x-2)/4.65)*.42
    verts += [(x,-w,1.5+bow),(x,-w*.94,.1),(x,-w*.52,-.75),(x,w*.52,-.75),(x,w*.94,.1),(x,w,1.5+bow)]
faces=[]
for i in range(len(stations)-1):
    for j in range(6): faces.append((i*6+j,i*6+(j+1)%6,(i+1)*6+(j+1)%6,(i+1)*6+j))
faces += [tuple(reversed(range(6))),tuple(range((len(stations)-1)*6,len(stations)*6))]
hull=mesh('Welded expedition hull',verts,faces,navy)
bevel=hull.modifiers.new('Chine highlights','BEVEL'); bevel.width=.06; bevel.segments=3
hull.modifiers.new('Hull normals','WEIGHTED_NORMAL')
for side in [-1,1]:
    pipe('Safety sheer stripe',[(x,side*w*1.005,1.05+max(0,(x-2)/4.65)*.42) for x,w in stations],.10,orange)
deckverts=[(x,-w*.94,1.52+max(0,(x-2)/4.65)*.42) for x,w in stations]
deckverts += [(x,w*.94,1.52+max(0,(x-2)/4.65)*.42) for x,w in reversed(stations)]
mesh('Weather deck',deckverts,[tuple(range(len(deckverts)))],deck)

# Stacked accommodation, wraparound bridge, roof fittings.
box('Accommodation',(-.9,0,2.13),(5.1,2.8,1.2),white,.12)
box('Bridge level',(.0,0,3.13),(3.6,3.05,.86),white,.10)
box('Bridge visor',(.05,0,3.63),(3.95,3.30,.13),white)
for side in [-1,1]:
    for x in [-1.35,-.62,.12,.85,1.43]:
        box('Bridge window',(x,side*1.535,3.2),(.55,.035,.42),glass,.025)
    for x in [-2.85,-1.95,-1.05,-.15,.75]:
        box('Cabin window',(x,side*1.415,2.28),(.4,.04,.30),glass,.03)
    for x in [-5.7,-4.7,3.35,4.35]:
        cylinder('Hull porthole',(x,side*(1.8 if x<0 else 1.48),.85),.12,.055,black,(math.pi/2,0,0))
for y in [-1.1,-.37,.37,1.1]:
    box('Forward bridge glazing',(1.82,y,3.2),(.035,.55,.42),glass,.025)
box('Funnel',(-2.6,0,3.5),(.8,.85,1.3),orange,.08)
box('Funnel cap',(-2.6,0,4.18),(.9,.95,.16),black)
cylinder('Radar mast',(-.8,0,4.7),.055,2.0,steel)
box('Radar scanner',(-.8,0,5.25),(.18,1.45,.10),white)
pipe('Mast crossbar',[(-.8,-.8,4.7),(-.8,.8,4.7)],.04,steel)
for y in [-.65,.65]: cylinder('Antenna',(-.8,y,5.05),.018,.7,steel)
cylinder('Satellite pedestal',(.85,.65,3.95),.18,.55,white)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.35,location=(.85,.65,4.3))
bpy.context.object.data.materials.append(white); bpy.context.object.parent=ship

# Lifeboats, stern research crane and deck equipment.
for side in [-1,1]:
    box('Rescue launch',(-3.8,side*1.37,2.02),(1.8,.64,.48),orange,.22)
    box('Rescue launch canopy',(-3.9,side*1.37,2.31),(.85,.48,.3),white,.10)
    for x in [-4.4,-3.3]: box('Boat davit',(x,side*1.25,2.25),(.08,.09,1.4),steel)
cylinder('Crane turntable',(-5.4,.8,1.75),.38,.4,orange)
pipe('Articulated research crane',[(-5.4,.8,1.85),(-5.4,.8,3.55),(-6.0,.8,4.0),(-7.5,.8,3.65)],.12,orange)
pipe('Crane cable',[(-7.5,.8,3.65),(-7.5,.8,2.1)],.014,black)
box('Deck laboratory',(-5.1,-.6,1.97),(1.65,.82,.8),white)
for y in [-.6,.6]:
    cylinder('Bow mooring capstan',(4.65,y,1.95),.13,.4,steel)
    pipe('Bow rope',[(4.4,y,1.8),(5.2,y,1.85),(5.65,0,1.95)],.035,black)

# Rail posts and continuous upper/lower handrails.
for side in [-1,1]:
    points=[]
    for (x0,w0),(x1,w1) in zip(stations[:-1],stations[1:]):
        for k in range(max(1,int((x1-x0)/.65))):
            t=k/max(1,int((x1-x0)/.65)); x=x0+(x1-x0)*t; w=w0+(w1-w0)*t
            z=1.55+max(0,(x-2)/4.65)*.42
            pipe('Stanchion',[(x,side*w*.94,z),(x,side*w*.94,z+.5)],.021,steel)
            points.append((x,side*w*.94,z+.5))
    points.append((6.65,0,2.47))
    pipe('Upper handrail',points,.025,white)
    pipe('Lower handrail',[(x,y,z-.24) for x,y,z in points],.016,steel)

# Vessel name applied to both hull sides.
for side in [-1,1]:
    bpy.ops.object.text_add(location=(1.5,side*1.91,.56))
    o=bpy.context.object; o.name='PELAGIC hull marking'; o.data.body='PELAGIC'; o.data.size=.29
    o.data.extrude=.002; o.data.materials.append(white); o.parent=ship
    o.rotation_euler=(math.pi/2,0,0) if side<0 else (math.pi/2,0,math.pi)

# Geometry water, visible even in the fast solid viewport renderer.
size=100; n=100
oceanverts=[]
for j in range(n+1):
    for i in range(n+1):
        x=(i/n-.5)*size; y=(j/n-.5)*size
        z=.055*math.sin(x*1.4+y*.3)+.035*math.sin(y*2.1-x*.25)
        oceanverts.append((x,y,z))
oceanfaces=[(j*(n+1)+i,j*(n+1)+i+1,(j+1)*(n+1)+i+1,(j+1)*(n+1)+i) for j in range(n) for i in range(n)]
ocean=mesh('Open ocean',oceanverts,oceanfaces,water,parent=False)
for p in ocean.data.polygons:p.use_smooth=True
for side in [-1,1]:
    for lane in range(3):
        points=[(-6.1-k*.55,side*(.8+lane*.34+k*.055),.11+.025*math.sin(k)) for k in range(24)]
        pipe('Stern wake',points,.035+lane*.015,foam,parent=False)

# Subtle ship motion; camera sweeps along the starboard side and around the bow.
for axis,expr in [(2,'0.06*sin(frame/24*1.3)')]:
    ship.driver_add('location',axis).driver.expression=expr
ship.driver_add('rotation_euler',0).driver.expression='0.012*sin(frame/24*0.8)'
ship.driver_add('rotation_euler',1).driver.expression='0.007*sin(frame/24*1.1)'
bpy.ops.object.camera_add()
camera=bpy.context.object; camera.name='Director — continuous orbit'; scene.camera=camera
camera.data.lens=44
for frame in range(1,1442,60):
    t=(frame-1)/1440
    angle=math.radians(-65+100*t)
    camera.location=(23*math.cos(angle),23*math.sin(angle),10+1.2*math.sin(t*math.pi*2))
    camera.rotation_euler=(Vector((0,0,1.2))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.keyframe_insert('location',frame=frame)
    camera.keyframe_insert('rotation_euler',frame=frame)
scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
ship.select_set(True); bpy.context.view_layer.objects.active=ship
scene.fal_h3_live.prompt='Cinematic aerial tracking shot of the exact navy blue and ivory expedition research ship PELAGIC with orange lifeboats and orange crane, cruising on a deep teal ocean. Follow the smooth camera movement from the first image to the final image. Preserve the hull silhouette, bridge, railings, mast, colors and all equipment. Realistic moving ocean waves, white foam wake, subtle ship roll, glancing sunlight, maritime documentary cinematography. One continuous shot, no cuts, no new vessels.'
scene.fal_h3_live.max_requests=args.clips
scene.fal_h3_live.resolution='480P'

status_text=bpy.data.texts.new('PELAGIC / live telemetry')
saved=False
def configure():
    window=bpy.context.window_manager.windows[0]
    source=next(a for a in window.screen.areas if a.type=='VIEW_3D')
    with bpy.context.temp_override(window=window,area=source):bpy.ops.fal.h3_layout()
    source=next(a for a in window.screen.areas if a.type=='VIEW_3D')
    space=source.spaces.active
    space.region_3d.view_perspective='CAMERA'
    space.region_3d.view_camera_zoom=0
    space.overlay.show_overlays=False
    space.show_region_ui=False
    space.shading.type='SOLID'; space.shading.light='STUDIO'; space.shading.color_type='MATERIAL'
    space.shading.show_shadows=True; space.shading.show_cavity=True
    space.shading.cavity_type='BOTH'; space.shading.curvature_ridge_factor=1.3
    for area in window.screen.areas:
        if area.type=='PROPERTIES':
            area.type='TEXT_EDITOR'; area.spaces.active.text=status_text
            area.spaces.active.show_line_numbers=False; area.spaces.active.show_word_wrap=True
            area.spaces.active.font_size=16
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'pelagic-ship.blend'))
    if args.stream:
        with bpy.context.temp_override(window=window,area=source):bpy.ops.fal.h3_stream_start()
    def telemetry():
        global saved
        p=scene.fal_h3_live
        status_text.clear()
        status_text.write('PELAGIC\nEXPEDITION / H3 LIVE\n\nFIRST + LAST FRAME\nBoth images: base64\n480p / 5 second clips\n\n'+p.stream_status.replace(' | ','\n')+'\n\n'+p.timing.replace(' | ','\n')+'\n\nCONTROLS\nF3: Stop stream\nN > H3 Live\n\nLeft: AI video\nRight: planned camera\n\nFirst/last conditioning\nTwo requests in flight\nOrdered playback buffer\n')
        if p.last_video and not saved:
            with bpy.context.temp_override(window=window):bpy.ops.screen.screenshot(filepath=str(out/'ship-live-screen.png'))
            saved=True
        return 1
    bpy.app.timers.register(telemetry,first_interval=1)
    return None

if not bpy.app.background:
    bpy.app.timers.register(configure,first_interval=2)
else:
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'pelagic-ship.blend'))
