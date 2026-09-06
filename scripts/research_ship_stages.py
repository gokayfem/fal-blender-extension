"""Geometry stages injected into the established live demo runner."""
def refined_hull():
    obj=objects['hull']
    verts=[]; faces=[]; count=65; sides=25
    for i in range(count):
        t=i/(count-1); x=-6.3+13.5*t
        width=2.12*(.72+.28*math.sin(min(t/.55,1)*math.pi/2))
        if t>.62: width*=max(.008, math.cos((t-.62)/.38*math.pi/2))
        for j in range(sides):
            angle=math.pi+math.pi*j/(sides-1)
            verts.append((x,width*math.cos(angle),1.35+1.97*math.sin(angle)))
    for i in range(count-1):
        for j in range(sides):
            faces.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
    faces += [tuple(reversed(range(sides))),tuple(range((count-1)*sides,count*sides))]
    mesh=bpy.data.meshes.new('Faired hull / 65 stations');mesh.from_pydata(verts,[],faces);mesh.update()
    obj.data=mesh;obj.modifiers.clear();obj.scale=(1,1,1)
    for poly in mesh.polygons: poly.use_smooth=len(poly.vertices)==4 and poly.index%sides!=sides-1
    return []

def decks():
    result=[box('Extended aft equipment deck',(-3.95,0,1.47),(4.1,3.65,.18)),
            box('Forecastle raised deck',(3.2,0,1.6),(2.6,2.65,.5)),
            box('Aft laboratory',(-3.6,0,2.0),(1.55,2.3,.95))]
    for side in (-1,1):
        result.append(box('Bridge wing',(.1,side*1.8,2.57),(3.8,.72,.18)))
        for x in (-2,-1.25,-.5,.25,1):
            # Layered framing and inset inner pane are actual mesh.
            result.append(box('Deckhouse window surround',(x,side*1.391,2.1),(.55,.055,.43)))
            result.append(box('Recessed window pane',(x,side*1.424,2.1),(.44,.02,.32)))
    return result

def access():
    result=[]
    for side in (-1,1):
        for i in range(8):
            result.append(box('Stair tread',(-2.85+i*.17,side*1.68,1.42+i*.145),(.23,.52,.08)))
        for y in (side*1.4,side*1.94):
            result.append(pipe('Stair handrail',[(-2.9,y,2.05),(-1.55,y,3.18)],.025))
        for x in (-3.7,-2.7,-1.7,-.7,.3,1.3,2.3,3.3):
            result.append(pipe('Deck railing stanchion',[(x,side*1.98,1.45),(x,side*1.98,2.08)],.026))
        for z in (1.77,2.08):
            result.append(pipe('Continuous safety rail',[(-5.9,side*1.55,z),(-4,side*1.98,z),(2.4,side*1.98,z),(4.1,side*1.42,z),(6.8,0,z)],.026))
    return result

def machinery():
    result=crane()
    result.append(box('Crane rotating pedestal',(-4,.7,1.7),(.65,.65,.65)))
    result.append(pipe('Hydraulic ram',[(-4,.68,2.3),(-4.7,.68,3.65)],.07))
    for x in (-5.65,3.7):
        for side in (-1,1):
            result.append(box('Bollard base',(x,side*1.05,1.84),(.65,.4,.12)))
            for dx in (-.18,.18):
                result.append(pipe('Mooring bollard',[(x+dx,side*1.05,1.9),(x+dx,side*1.05,2.18)],.07))
    for i in range(7):
        result.append(box('Ventilation grille slat',(-3.6,-1.18,1.75+i*.07),(1,.08,.025)))
    return result

def outfitting():
    result=[]
    for side in (-1,1):
        for x in (-3.2,-1.6,0,1.6):
            bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=12,location=(x,side*2.06,.95),rotation=(math.pi/2,0,0),major_radius=.22,minor_radius=.075)
            o=bpy.context.object;o.name='Rubber hull fender';o.color=(.55,.55,.55,1)
            for f in o.data.polygons:f.use_smooth=True
            result.append(o)
        result.append(box('Rescue tender cradle',(-2.1,side*1.66,1.6),(1.65,.55,.15)))
        result.append(box('Rescue tender',(-2.1,side*1.66,1.84),(1.55,.52,.32)))
    for x,y in ((-.65,0),(.65,.6),(.8,-.6)):
        result.append(pipe('Navigation antenna',[(x,y,3.5),(x,y,4.6)],.018))
    for x in (2.2,2.9,3.6):result.append(box('Foredeck hatch',(x,0,1.9),(.52,.65,.08)))
    for obj in scene.objects:
        for mod in obj.modifiers:
            if mod.type=='BEVEL':mod.segments=4
        if obj.type=='CURVE':obj.data.bevel_resolution=4
    return result

stages=stages[:5]+[
    ('Enlarge and fair the hull',refined_hull,'Larger research vessel hull with smooth continuous rounded plating and a tapered bow. Preserve the existing wheelhouse and mast.'),
    ('Expand decks and laboratory',decks,'The visible raised foredeck, aft laboratory, bridge wings and layered window frames are now present. Preserve their exact dimensions.'),
    ('Build stairs and safety rails',access,'Real stair treads, inclined handrails, fine deck stanchions and continuous rails follow the visible geometry. Preserve every modeled deck level.'),
    ('Assemble working deck equipment',machinery,'The aft articulated crane has a pedestal, hydraulic ram and cable. Retain the modeled mooring bollards and ventilation grille.'),
    ('Finish fittings and refined surfaces',outfitting,'Fully outfitted research workboat with the visible fenders, compact tenders, navigation antennas, hatches, crane, fine rails and stairs. Detailed manufactured surfaces with clean smooth hull plating. No additional large structures.')]
