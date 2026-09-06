"""Play selected experimental clips in the saved Blender grid; no API calls."""
import bpy,blf,time,json,argparse,sys
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--study',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
study=args.study.resolve()
names=['s4-delta-i0-k271828','s4-delta-i1-k112358','s4-text-i2-k112358','s4-delta-i3-k112358']
labels=['CARTOON','CLAYMATION','REALISTIC','STYLIZED / GOUACHE']
views=[];start=0
def header():
    area=bpy.context.area
    label=labels[views.index(area)] if area in views else 'GRAY GEOMETRY / FINAL SHIP'
    blf.size(0,18);blf.color(0,.94,.94,.94,1);blf.position(0,18,bpy.context.region.height-34,0);blf.draw(0,label)
def play():
    for area in views:
        clip=area.spaces.active.clip
        area.spaces.active.clip_user.frame_current=1+int((time.perf_counter()-start)*clip.fps)%max(1,clip.frame_duration)
        area.tag_redraw()
    return 1/30
def setup():
    global views,start
    window=bpy.context.window_manager.windows[0]
    views=sorted([a for a in window.screen.areas if a.type=='CLIP_EDITOR'],key=lambda a:(-a.y,a.x))
    for i,area in enumerate(views):
        area.spaces.active.clip=bpy.data.movieclips.load(str(study/(names[i]+'.mp4')),check_existing=True)
        region=next(r for r in area.regions if r.type=='WINDOW')
        with bpy.context.temp_override(window=window,area=area,region=region):bpy.ops.clip.view_all(fit_view=True)
    for area in window.screen.areas:
        if area.type=='TEXT_EDITOR':
            text=bpy.data.texts.new('SELECTED EXPERIMENT RESULTS')
            text.write('FOUR RENDER STYLES\n\nSelected experiment\nresults playing together\n\nSame final Blender mesh\nImage-only conditioning\n\nCartoon\nClaymation\nRealistic\nPainted gouache\n\n768p / five-second clips\nLooping playback\n\nPreviously generated\nNo live inference\nin this recording\n\nExperimental:\nexact detail matching\nis not guaranteed')
            area.spaces.active.text=text;area.spaces.active.font_size=18
    bpy.types.SpaceClipEditor.draw_handler_add(header,(),'WINDOW','POST_PIXEL')
    bpy.types.SpaceView3D.draw_handler_add(header,(),'WINDOW','POST_PIXEL')
    start=time.perf_counter();bpy.app.timers.register(play)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'four-selected-results.blend'))
    (out/'selection.json').write_text(json.dumps(dict(zip(labels,names)),indent=2))
    (out/'ready.flag').write_text('ready')
    return None
bpy.app.timers.register(setup,first_interval=2)
