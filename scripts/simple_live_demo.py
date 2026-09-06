"""Recorded, scripted geometry build. Start by creating OUTPUT/start-build.flag."""
import argparse
import json
import math
import os
from pathlib import Path
import sys
import time

import bpy
import blf
from mathutils import Vector

parser=argparse.ArgumentParser()
parser.add_argument('--env',required=True)
parser.add_argument('--output',required=True)
parser.add_argument('--grid',action='store_true')
parser.add_argument('--keep-live',action='store_true')
parser.add_argument('--start-stage',type=int,default=0,choices=range(7))
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
for line in Path(args.env).read_text(encoding='utf-8-sig').splitlines():
    if line.strip().startswith('FAL_KEY='):
        os.environ['FAL_KEY']=line.split('=',1)[1].strip().strip('\"\'');break
import addon_utils
addon_utils.enable('bl_ext.user_default.fal_ai',default_set=True)
from bl_ext.user_default.fal_ai import live_preview, live_grid, stage_prompts
bpy.context.preferences.view.show_splash=False
scene=bpy.context.scene;scene.name='IMAGE ONLY / MEASURED LIVE DEMO'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene.render.filepath=str(out)+os.sep
scene.render.resolution_x=848;scene.render.resolution_y=480;scene.render.resolution_percentage=100
scene.frame_start=1;scene.frame_end=120
scene.render.fps=24
bpy.ops.mesh.primitive_plane_add(size=200)
bpy.context.object.name='Ground plane / interpreted as ocean'
bpy.context.object.color=(.16,.16,.16,1)
bpy.ops.object.camera_add(location=(17,-23,15))
camera=bpy.context.object;camera.name='Fixed comparison camera';camera.data.lens=47
camera.rotation_euler=(Vector((0,0,1.2))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera=camera
objects={}

def box(name,loc,scale):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    obj=bpy.context.object;obj.name=name;obj.scale=scale;obj.color=(.55,.55,.55,1)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bevel=obj.modifiers.new('Soft fabrication edges','BEVEL');bevel.width=.04;bevel.segments=2
    obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return obj

def pipe(name,points,radius=.045):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=2
    sp=c.splines.new('POLY');sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):p.co=(*co,1)
    obj=bpy.data.objects.new(name,c);scene.collection.objects.link(obj);obj.color=(.55,.55,.55,1)
    return obj

def hull():
    stations=[(-5,1.2),(-4,1.75),(0,1.85),(3,1.3),(5.6,.03)]
    verts=[]
    for x,w in stations:
        verts += [(x,-w,1.35),(x,-w*.9,.06),(x,-w*.5,-.6),(x,w*.5,-.6),(x,w*.9,.06),(x,w,1.35)]
    faces=[]
    for i in range(len(stations)-1):
        for j in range(6):faces.append((i*6+j,i*6+(j+1)%6,(i+1)*6+(j+1)%6,(i+1)*6+j))
    faces += [tuple(reversed(range(6))),tuple(range(24,30))]
    mesh=bpy.data.meshes.new('Hull topology');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new('01 / Hull',mesh);scene.collection.objects.link(obj);obj.color=(.55,.55,.55,1)
    bevel=obj.modifiers.new('Hull chines','BEVEL');bevel.width=.06;bevel.segments=3
    obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    obj.scale.x=.65;objects['hull']=obj
    return [obj]

def lengthen():
    obj=objects['hull'];obj.scale.x=1
    return [obj]

def cabin():return [box('02 / Deckhouse',(-.6,0,1.98),(4.8,2.75,1.25))]

def bridge():
    result=[box('03 / Upper bridge',(.1,0,2.95),(3.2,2.95,.75)),box('Bridge roof',(.1,0,3.37),(3.5,3.18,.14))]
    # Geometry recesses/frames, not colored materials.
    for side in [-1,1]:
        for x in [-1.05,-.35,.35,1.05]:
            result.append(box('Window frame',(x,side*1.49,3.0),(.5,.045,.35)))
    return result

def mast():
    return [pipe('04 / Mast',[(-.65,0,3.45),(-.65,0,5.45)],.045),
            box('Radar',(-.65,0,5.0),(.18,1.45,.09)),
            box('Funnel',(-2.5,0,2.95),(.65,.7,1.4)),box('Funnel cap',(-2.5,0,3.67),(.78,.83,.14))]

def crane():
    return [pipe('05 / Articulated deck crane',[(-4,.7,1.4),(-4,.7,3.4),(-4.8,.7,3.8),(-6.3,.7,3.5)],.12),
            pipe('Crane cable',[(-6.3,.7,3.5),(-6.3,.7,1.6)],.017)]

def finish():
    result=[]
    for side in [-1,1]:
        result.append(box('06 / Rescue boat',(-2.9,side*1.38,1.78),(1.45,.58,.4)))
        points=[(-4.8,side*1.25,1.92),(-3.8,side*1.65,1.92),(0,side*1.78,1.92),(3,side*1.25,1.92),(5.5,0,1.92)]
        result.append(pipe('Deck handrail',points,.025))
        for x in [-4,-3,-2,-1,0,1,2,3]:
            y=side*(1.65 if x<1 else 1.45)
            result.append(pipe('Rail post',[(x,y,1.35),(x,y,1.92)],.02))
    return result

stages=[('Block out the hull',hull,'Bare-hull assembly stage. Only one low boat hull with an uninterrupted empty deck is present. Smoothly faired steel hull plating with gently curved sides, clean tapered bow, subtly rounded gunwale and flat finished deck. Zero raised structures. A real bare boat hull, not a polygonal slab. Keep all volume low within the reference envelope.'),
        ('Stretch the vessel',lengthen,'The same bare-hull assembly is now elongated. Only the longer low hull and uninterrupted empty deck exist. Smooth continuous curved hull plating, refined bow, rounded gunwale edge. Zero raised structures. Preserve the changed long proportions.'),
        ('Build the deckhouse',cabin,'The real hull now supports exactly one low deckhouse. Interpret the rectangular proxy as a welded steel enclosure with subtly rounded fabrication corners and solid blank walls. No openings are modeled in this enclosure yet. All remaining deck area stays clear. Only hull plus this one enclosure exist.'),
        ('Add the bridge',bridge,'The hull now supports a lower deckhouse and an upper wheelhouse with a roof. The modeled rectangular face frames define the actual windows: install dark reflective glazing within precisely those frames. Refine corners and roof thickness into plausible marine construction. Preserve the sparse two-level arrangement.'),
        ('Raise the mast',mast,'The existing hull, deckhouse, glazed wheelhouse and roof remain. The newly modeled thin vertical rod and crossbar are a slender metal mast, and the short rectangular stack is a marine exhaust. Interpret these existing parts realistically, retaining their exact arrangement and sparse scale.'),
        ('Assemble the crane',crane,'The existing assemblies remain. The newly modeled bent arm at the left rear is a small deck lifting crane, with the modeled hanging line as its cable. Refine it as manufactured hydraulic equipment within the existing arm envelope. Keep the rest of the deck clear.'),
        ('Fit out the deck',finish,'Interpret the currently visible components as the parts of a compact coastal workboat. Refine the hull into faired continuous plating, enclosure corners into welded marine construction, modeled window frames into proper glazing, slender rods and rails into metal tubes, and the lifting arm into a plausible small crane. The small side proxies are compact rescue tenders. Only realize components actually present in Image 1; removed parts stay absent and new visible parts follow their physical role. Keep the current sparse design and broad uncluttered areas.')]
base_prompt='Preserve the existing component count, relative heights and boundaries. Window-frame rectangles indicate glazing: make interiors dark reflective glass without moving their borders. Preserve the roof outline, crane, mast, rails and empty deck areas. Do not invent equipment. Object category: small coastal workboat. CURRENT ASSEMBLY: '
p=scene.fal_h3_live;p.grid_guidance='PER_STYLE_TEXT';p.grid_seed=112358;p.style_manifest='' ;p.preview_mode='REFERENCE';p.source_format='JPEG';p.resolution='768P';p.max_requests=20;p.settle_seconds=.8
for _, create_initial, _ in stages[:args.start_stage]:
    create_initial()
state=dict(stage=args.start_stage-1,phase='waiting',started=0,phase_at=0,previous_video='',motion=[],history=[],done=False)
text=bpy.data.texts.new('LIVE BUILD / telemetry')
window=None;source=None;preview=None;grid_views=[]


def active_session():
    return live_grid._session if args.grid else live_preview._session

def header(label):
    if bpy.app.driver_namespace.get('fal_capture_active'):return
    if label=='GRID':
        index=next((i for i,a in enumerate(grid_views) if a==bpy.context.area),None)
        label=live_grid.STYLES[index][0] if index is not None else 'H3 / LIVE'
        session=active_session()
        if session and index in session.get('pending',set()): label += ' / UPDATING'
    blf.size(0,18 if args.grid else 22);blf.color(0,.94,.94,.94,1);blf.position(0,20,bpy.context.region.height-40,0);blf.draw(0,label)

def status_file():
    (out/'build-status.json').write_text(json.dumps(dict(initial_stage=args.start_stage,stage=state['stage'],phase=state['phase'],status=p.status,timing=p.timing,video=p.last_video,history=state['history'],done=state['done']),indent=2))

def tick():
    now=time.perf_counter()
    if (out/'stop-build.flag').exists():
        live_grid._session=None
        live_preview._session=None
        state['phase']='stopped';state['done']=True
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'gray-live-build.blend'))
        status_file();return None
    if state['phase']=='waiting':
        if not (out/'start-build.flag').exists():return .1
        state['started']=now;state['recording_epoch']=time.time();state['phase']='next';state['phase_at']=now+2
    if state['phase']=='next' and now>=state['phase_at']:
        state['stage']+=1
        if state['stage']>=len(stages):
            if not args.keep_live:
                with bpy.context.temp_override(window=window,area=source):
                    if args.grid:bpy.ops.fal.h3_grid_stop()
                    else:bpy.ops.fal.h3_stop()
            state['phase']='complete';state['done']=True
            text.clear();text.write(f'LIVE BUILD COMPLETE\n\n{len(state["history"])} geometry edits\n'+(f'{len(state["history"])*4} fresh clips\n4 parallel styles\n' if args.grid else f'{len(state["history"])} fresh clips\n')+'\nGray source geometry\nGenerated during recording\n\n'+p.timing+'\n\n'+('LIVE REFRESH IS ON\nEdit geometry to update\n' if args.keep_live else 'Start to keep editing\n')+'N > H3 Live\nStop four-style grid\n')
            bpy.ops.wm.save_as_mainfile(filepath=str(out/'gray-live-build.blend'))
            with bpy.context.temp_override(window=window):bpy.ops.screen.screenshot(filepath=str(out/'final-screen.png'))
            status_file();return None
        title,create,brief=stages[state['stage']]
        state['edit_started']=time.time()
        old_scale=objects['hull'].scale.copy() if state['stage']==1 else None
        new_objects=create();state['motion']=[]
        for obj in new_objects:
            target=obj.scale.copy();initial=old_scale if old_scale is not None else target*.015
            state['motion'].append((obj,initial.copy(),target));obj.scale=initial
        p.prompt=stage_prompts.for_stage(state["stage"]) if args.grid else live_grid.prompts_for(stage_prompts.for_stage(state["stage"]))[0]
        state['previous_video']=p.last_video;state['phase']='building';state['phase_at']=now
        if active_session() is None:
            with bpy.context.temp_override(window=window,area=source):
                if args.grid:bpy.ops.fal.h3_grid_start()
                else:bpy.ops.fal.h3_start(auto=True)
    if state['phase']=='building':
        t=min(1,(now-state['phase_at'])/1.8);t=t*t*(3-2*t)
        for obj,initial,target in state['motion']:obj.scale=initial.lerp(target,t)
        if t>=1:state['phase']='rendering';state['phase_at']=now
    if state['phase']=='rendering':
        if p.last_video and p.last_video!=state['previous_video']:
            state['history'].append(dict(stage=state['stage']+1,title=stages[state['stage']][0],edit_started_epoch=state['edit_started'],visible_epoch=time.time(),edit_to_visible_seconds=now-state['phase_at'],video=p.last_video,timing=p.timing))
            if args.grid and active_session():state['history'][-1]['grid']=active_session()['history'][-1]
            state['phase']='next';state['phase_at']=now+5
        elif now-state['phase_at']>100 or (active_session() is None and ('failed' in p.status.lower() or 'stopped' in p.status.lower())):
            state['phase']='error';state['done']=True;status_file();return None
    elapsed=now-state['started'] if state['started'] else 0
    title=stages[state['stage']][0] if 0<=state['stage']<len(stages) else 'Preparing'
    text.clear();text.write('GRAY GEOMETRY\n'+('FOUR LIVE WORLDS' if args.grid else 'LIVE FILM')+'\n\nScripted live build\nContinuous recording\n\n'+f'STAGE {state["stage"]+1} / {len(stages)}\n'+title+'\n\n'+state['phase'].upper()+'\n'+p.status+'\n\n'+p.timing.replace(' | ','\n')+f'\n\nElapsed {elapsed:.1f}s\n\n832px camera images\nImage-only references\nH3 Max / 768p\n\nNo viewport materials\nNo prerecorded AI clips\n\nN > H3 Live\nF3 > Stop\n')
    source.tag_redraw();preview.tag_redraw();status_file()
    return .075

def configure_final(grid_source=None,views=None):
    global source,preview,grid_views
    if args.grid:
        source=grid_source;grid_views=views;preview=views[0]
    else:
        areas=sorted([a for a in window.screen.areas if a.type in {'VIEW_3D','CLIP_EDITOR'}],key=lambda a:a.x)
        source,preview=areas[0],areas[1];source.type='VIEW_3D';preview.type='CLIP_EDITOR'
    space=source.spaces.active;space.overlay.show_overlays=False;space.show_region_ui=False
    space.show_region_toolbar=False;space.show_region_tool_header=False;space.show_gizmo=False
    space.shading.type='SOLID';space.shading.light='STUDIO';space.shading.color_type='OBJECT';space.shading.single_color=(.6,.6,.6)
    space.shading.background_type='VIEWPORT';space.shading.background_color=(.035,.035,.035)
    space.shading.show_shadows=True;space.shading.show_cavity=True;space.shading.cavity_type='BOTH'
    space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=-3 if args.grid else 22
    preview.spaces.active.show_region_ui=False;preview.spaces.active.show_region_toolbar=False
    for area in window.screen.areas:
        if area.type=='PROPERTIES':
            area.type='TEXT_EDITOR';area.spaces.active.text=text;area.spaces.active.font_size=16
            area.spaces.active.show_line_numbers=False;area.spaces.active.show_word_wrap=True
    bpy.types.SpaceView3D.draw_handler_add(header,('GRAY GEOMETRY / LIVE BUILD',),'WINDOW','POST_PIXEL')
    bpy.types.SpaceClipEditor.draw_handler_add(header,('GRID' if args.grid else 'H3 / GENERATED LIVE',),'WINDOW','POST_PIXEL')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'gray-live-build.blend'))
    text.write('GRAY GEOMETRY\nLIVE FILM\n\nReady for recording\n\nThe geometry will be\nbuilt here in stages.\n\nEach stage triggers a\nnew AI generation.\n')
    (out/'ready.flag').write_text('ready')
    bpy.app.timers.register(tick,first_interval=.2)
    return None

def configure():
    global window
    window=bpy.context.window_manager.windows[0]
    if args.grid:
        live_grid.create_layout(window,configure_final)
        return None
    area=next(a for a in window.screen.areas if a.type=='VIEW_3D')
    with bpy.context.temp_override(window=window,area=area):bpy.ops.fal.h3_layout()
    bpy.app.timers.register(configure_final,first_interval=.3)
    return None

bpy.app.timers.register(configure,first_interval=2)
