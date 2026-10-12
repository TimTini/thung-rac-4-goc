"""Render prototype and audit meshes. Requires trimesh and manifold3d."""
from pathlib import Path
import json
import subprocess
import re
import os
import numpy as np

import trimesh

ROOT = Path(__file__).resolve().parent
SCAD = ROOT / "thung-rac-4-goc-v2.scad"
EXE = os.environ.get("OPENSCAD", "openscad")
OUT = ROOT / "exports/v2"
OUT.mkdir(exist_ok=True)
source = SCAD.read_text(encoding="utf-8")
def parameter(name):
    return float(re.search(r"^" + name + r"\s*=\s*([\d.]+);", source, re.M)[1])

half = parameter("body_size")/2
lap = parameter("lap_length")
floor = parameter("floor_thickness")
base_span = parameter("base_span")
band = parameter("band_projection")
band_height = parameter("band_height")
height = parameter("body_height")
bridge_width = parameter("bridge_width")
bridge_thickness = parameter("bridge_thickness")
frame_height = parameter("frame_height")
joint = parameter("joint_thickness")


def render(name, view, extra=()):
    command = [str(EXE), "--backend", "Manifold", "--hardwarnings",
               "-D", f'view="{view}"', "-o", str(OUT / name),
               *extra, str(SCAD)]
    if name.endswith(".stl"):
        command[1:1] = ["--export-format", "binstl"]
    result = subprocess.run(command, capture_output=True, text=True)
    (OUT / (name + ".log")).write_text(result.stdout + result.stderr,
                                      encoding="utf-8")
    if result.returncode or "WARNING:" in result.stderr or "ERROR:" in result.stderr:
        raise RuntimeError(result.stdout + result.stderr)
    print("Rendered", name, flush=True)


for name, view in [("corner.stl", "corner"), ("base.stl", "base"),
                   ("frame.stl", "frame"), ("bridge.stl", "bridge"),
                   ("coupon.stl", "coupon"), ("assembly.off", "assembled")]:
    render(name, view)

report = {}
for name, expected in [("corner.stl", 1), ("base.stl", 1), ("coupon.stl", 2),
                       ("frame.stl", 1), ("bridge.stl", 1),
                       ("assembly.off", 1)]:
    mesh = trimesh.load_mesh(OUT / name)
    # Manifold triangulation can emit zero-area slivers at coplanar unions.
    # Remove only these faces; never fill holes or change the solid geometry.
    removed = int((~mesh.nondegenerate_faces()).sum())
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    components = mesh.split(only_watertight=False)
    report[name] = {"watertight": bool(mesh.is_watertight),
                    "components": len(components),
                    "bounds_mm": mesh.bounds.tolist(),
                    "size_mm": mesh.extents.tolist(),
                    "volume_mm3": float(mesh.volume),
                    "zero_area_faces_removed": removed}
    assert mesh.is_watertight, (name, "open mesh")
    assert len(components) == expected, (name, len(components), expected)
    if name.endswith(".stl"):
        mesh.export(OUT / name)
        assert trimesh.load_mesh(OUT / name).is_watertight

corner = trimesh.load_mesh(OUT / "corner.stl")
corner.apply_translation([-lap, 0, 0])
parts = []
for i in range(4):
    part = corner.copy()
    part.apply_transform(trimesh.transformations.rotation_matrix(i * 3.141592653589793/2,
                                                               [0, 0, 1]))
    parts.append(part)
base = trimesh.load_mesh(OUT / "base.stl")
base.apply_translation([-base_span/2, -base_span/2, floor])
parts.append(base)
for i in range(4):
    frame = trimesh.load_mesh(OUT / "frame.stl")
    frame_min = min(10,10+parameter("frame_width")/2-8)
    frame.apply_translation([frame_min,frame_min,-frame_height])
    frame.apply_transform(trimesh.transformations.rotation_matrix(i*np.pi/2,[0,0,1]))
    parts.append(frame)
    bridge = trimesh.load_mesh(OUT / "bridge.stl")
    bridge.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    bridge.apply_translation([-bridge_width/2,half+band+bridge_thickness,
                              height/2-band_height/2])
    bridge.apply_transform(trimesh.transformations.rotation_matrix(i*np.pi/2,[0,0,1]))
    parts.append(bridge)
collisions = []
for i in range(len(parts)):
    for j in range(i + 1, len(parts)):
        overlap = trimesh.boolean.intersection([parts[i], parts[j]], engine="manifold")
        overlap.update_faces(overlap.nondegenerate_faces())
        # Coplanar contact is a surface, not a watertight solid or collision.
        flat_contact = not overlap.is_empty and min(overlap.extents) < 1e-6
        volume = (abs(float(overlap.volume))
                  if not overlap.is_empty and not flat_contact else 0.0)
        assert overlap.is_empty or flat_contact or overlap.is_watertight, (i,j)
        assert volume < 0.01, ("collision", i, j, volume)
        collisions.append({"parts": [i,j], "overlap_mm3": volume})
report["pairwise_intersections"] = collisions
rotation = trimesh.transformations.rotation_matrix(np.pi/2, [0,0,1])
start = half-joint-1
end = half+band+bridge_thickness+1
receiver_axis = trimesh.transform_points([[start,lap/2,30], [end,lap/2,30]], rotation)
tongue_axis = np.array([[-lap/2,start,30], [-lap/2,end,30]])
assert np.allclose(receiver_axis, tongue_axis, atol=1e-6)
report["mating_bore_axes_mm"] = {
    "tongue": tongue_axis.tolist(), "rotated_receiver": receiver_axis.tolist()}
insertion = []
for dz in [1, height/8, height/2, height-1, height+1]:
    moving = parts[3].copy()
    moving.apply_translation([0, 0, dz])
    for j in range(3):
        overlap = trimesh.boolean.intersection([moving, parts[j]], engine="manifold")
        overlap.update_faces(overlap.nondegenerate_faces())
        assert overlap.is_empty, ("vertical insertion blocked", dz, j)
    insertion.append(dz)
report["last_corner_vertical_insertion_clear_at_z_mm"] = insertion
report["corner_fits_assumed_256_cube"] = bool((corner.extents <= 256).all())
assert report["corner_fits_assumed_256_cube"]
# Verify added holes really pass through mating meshes (clearance cylinders).
radius = parameter("bolt_diameter")/2-0.15
probes = []
for x in [-lap/2,lap/2]:
    probe = trimesh.creation.cylinder(radius=radius,height=end-start,sections=32)
    probe.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    probe.apply_translation([x,(start+end)/2,height/2])
    probes.append(("band",probe))
frame_width = parameter("frame_width")
outer = half-10-frame_width/2
inner = 10+frame_width/2
for x,y in [(20,20),(60,20),(20,60),(outer,outer),(outer,inner),(inner,outer)]:
    probe = trimesh.creation.cylinder(radius=radius,
                                     height=frame_height+floor+parameter("base_thickness")+2,
                                     sections=32)
    probe.apply_translation([x,y,(-frame_height+floor+parameter("base_thickness"))/2])
    probes.append(("floor",probe))
for name,probe in probes:
    for part in parts:
        overlap = trimesh.boolean.intersection([probe,part],engine="manifold")
        overlap.update_faces(overlap.nondegenerate_faces())
        assert overlap.is_empty, ("blocked bore",name)
report["clear_bore_probes"] = len(probes)
(OUT / "audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2), flush=True)

for view in ["assembled", "exploded"]:
    render(view + ".png", view,
           ["--render", "--autocenter", "--viewall", "--imgsize=1300,1000",
            "--projection=o", "--camera=0,0,100,55,0,35,1000", "--colorscheme=Tomorrow"])
