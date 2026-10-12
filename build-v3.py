"""Render/audit glue-free, hardware-free V3; requires trimesh/manifold3d."""
from pathlib import Path
import json
import re
import subprocess
import os
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parent
SCAD=ROOT/"thung-rac-4-goc-v3.scad"
OUT=ROOT/"exports/v3"
OUT.mkdir(exist_ok=True)
EXE=os.environ.get("OPENSCAD", "openscad")
source=SCAD.read_text(encoding="utf-8")
def p(name):
    return float(re.search(r"^"+name+r"\s*=\s*([\d.]+);",source,re.M)[1])

def render(name,view,extra=()):
    cmd=[str(EXE),"--backend","Manifold","--hardwarnings","-D",f'view="{view}"',
         "-o",str(OUT/name),*extra,str(SCAD)]
    if name.endswith(".stl"):
        cmd[1:1]=["--export-format","binstl"]
    result=subprocess.run(cmd,capture_output=True,text=True)
    (OUT/(name+".log")).write_text(result.stdout+result.stderr,encoding="utf-8")
    if result.returncode or "WARNING:" in result.stderr or "ERROR:" in result.stderr:
        raise RuntimeError(result.stdout+result.stderr)
    print("Rendered",name,flush=True)

def clean(mesh):
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    return mesh

def overlap_volume(a,b):
    overlap=clean(trimesh.boolean.intersection([a,b],engine="manifold"))
    if overlap.is_empty or min(overlap.extents)<1e-6:
        return 0.0
    assert overlap.is_watertight
    return abs(float(overlap.volume))

report={}
meshes={}
for name,components in [("corner",1),("key",1),("pin",1),("coupon",2),
                         ("coupon_key",1),("coupon_pin",1)]:
    render(name+".stl",name)
    mesh=clean(trimesh.load_mesh(OUT/(name+".stl")))
    assert mesh.is_watertight,name
    assert len(mesh.split(only_watertight=False))==components,name
    assert abs(mesh.bounds[0,2])<1e-6,(name,"not on bed")
    assert (mesh.extents<=256).all(),(name,"exceeds assumed build cube")
    mesh.export(OUT/(name+".stl"))
    assert trimesh.load_mesh(OUT/(name+".stl")).is_watertight
    meshes[name]=mesh
    report[name]={"size_mm":mesh.extents.tolist(),"bounds_mm":mesh.bounds.tolist(),
                  "components":components,"watertight":True,"volume_mm3":float(mesh.volume)}

half=p("body_size")/2
height=p("body_height")
rail_y=half+p("rail_projection")/2
corner=meshes["corner"].copy()
corner.apply_translation([-p("floor_lap"),0,0])
key=meshes["key"].copy()
key.apply_translation([0,-6,-16])
key.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[0,1,0]))
key.apply_translation([0,rail_y,p("key_stop")])
pin=meshes["pin"].copy()
pin.apply_translation([-p("rail_width")/2-3,rail_y-4,height-14])
bodies=[]
keys=[]
pins=[]
for i in range(4):
    rotation=trimesh.transformations.rotation_matrix(i*np.pi/2,[0,0,1])
    for origin,collection in [(corner,bodies),(key,keys),(pin,pins)]:
        part=origin.copy()
        part.apply_transform(rotation)
        collection.append(part)

# Body and spline pairs must be separate solids without interference.
parts=bodies+keys
collisions=[]
for i in range(len(parts)):
    for j in range(i+1,len(parts)):
        volume=overlap_volume(parts[i],parts[j])
        assert volume<0.01,("solid collision",i,j,volume)
        collisions.append({"parts":[i,j],"overlap_mm3":volume})
report["body_key_pairwise_intersections"]=collisions

# The wedge has intentional interference; separate it from all collision claims.
wedges=[]
for i,pin_part in enumerate(pins):
    for j,part in enumerate(parts):
        volume=overlap_volume(pin_part,part)
        assert volume<8,("excessive wedge interference",i,j,volume)
        if volume>0.01:
            wedges.append({"pin":i,"part":j,"interference_mm3":volume})
report["intentional_wedge_interference"]=wedges

# Final corner approaches horizontally; do not assume vertical drop with floor laps.
horizontal=[]
for d in [0.5,2,5,10,20,40]:
    moving=bodies[0].copy()
    moving.apply_translation([d,d,0])
    for fixed in bodies[1:]:
        assert overlap_volume(moving,fixed)<0.01,("corner insertion blocked",d)
    horizontal.append(d)
report["sampled_last_corner_diagonal_xy_clear_mm"]=horizontal

vertical=[]
for dz in [1,8,30,height/2,height+5]:
    moving=keys[0].copy()
    moving.apply_translation([0,0,dz])
    for fixed in bodies:
        assert overlap_volume(moving,fixed)<0.01,("key insertion blocked",dz)
    vertical.append(dz)
report["sampled_key_vertical_insertion_clear_mm"]=vertical

# Geometry checks must distinguish a useful lock from an oversized loose slot.
locked=keys[0]
for direction in [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0]]:
    moved=locked.copy()
    moved.apply_translation(direction)
    assert sum(overlap_volume(moved,b) for b in bodies)>0.1,("key not captured",direction)
report["key_captured_against_xy_1mm_translation"]=True
raised=keys[0].copy()
raised.apply_translation([0,0,1])
assert overlap_volume(raised,pins[0])>0.1,"Pin does not retain key vertically"
report["pin_blocks_key_1mm_lift"]=True

# Coupon uses the identical profile and wedge; validate shortened geometry.
coupon=meshes["coupon"].copy()
coupon.apply_translation([-p("rail_width")/2-1,half-2,0])
coupon_key=meshes["coupon_key"].copy()
coupon_key.apply_translation([0,-6,-16])
coupon_key.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[0,1,0]))
coupon_key.apply_translation([0,rail_y,p("key_stop")])
assert overlap_volume(coupon,coupon_key)<0.01
report["coupon_key_clear"]=True
coupon_pin=meshes["coupon_pin"].copy()
coupon_pin.apply_translation([-p("rail_width")/2-3,rail_y-4,28])
coupon_wedge=overlap_volume(coupon,coupon_pin)
assert coupon_wedge<8
assert overlap_volume(coupon_key,coupon_pin)<0.01
coupon_lift=coupon_key.copy()
coupon_lift.apply_translation([0,0,1])
assert overlap_volume(coupon_lift,coupon_pin)>0.1
report["coupon_pin_interference_mm3"]=coupon_wedge
report["coupon_pin_blocks_key_1mm_lift"]=True
report["printed_parts_count"]=12
report["hardware_count"]=0
report["solid_volume_mm3"]=sum(m.volume for m in bodies+keys+pins)
combined=trimesh.util.concatenate(bodies+keys+pins)
report["assembled_bounds_mm"]=combined.bounds.tolist()
report["assembled_size_mm"]=combined.extents.tolist()
(OUT/"audit.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2),flush=True)
for view in ["assembled","exploded","coupon"]:
    render(view+".png",view,["--render","--autocenter","--viewall","--imgsize=1300,1000",
                            "--projection=o","--camera=0,0,100,55,0,35,1000",
                            "--colorscheme=Tomorrow"])
