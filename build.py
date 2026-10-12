"""Render prototype and audit meshes. Requires trimesh and manifold3d."""
from pathlib import Path
import json
import os
import subprocess
import numpy as np

import trimesh

ROOT = Path(__file__).resolve().parent
SCAD = ROOT / "thung-rac-4-goc.scad"
EXE = os.environ.get("OPENSCAD", "openscad")
OUT = ROOT / "exports"
OUT.mkdir(exist_ok=True)


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
                   ("coupon.stl", "coupon"), ("assembly.off", "assembled")]:
    render(name, view)

report = {}
for name, expected in [("corner.stl", 1), ("base.stl", 1), ("coupon.stl", 2),
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
corner.apply_translation([-20, 0, 0])
parts = []
for i in range(4):
    part = corner.copy()
    part.apply_transform(trimesh.transformations.rotation_matrix(i * 3.141592653589793/2,
                                                               [0, 0, 1]))
    parts.append(part)
base = trimesh.load_mesh(OUT / "base.stl")
base.apply_translation([-80, -80, 4])
parts.append(base)
collisions = []
for i in range(len(parts)):
    for j in range(i + 1, len(parts)):
        overlap = trimesh.boolean.intersection([parts[i], parts[j]], engine="manifold")
        # Face-only contact has no volume; avoid evaluating its mass properties.
        volume = (abs(float(overlap.volume))
                  if not overlap.is_empty and overlap.is_watertight else 0.0)
        assert overlap.is_empty or overlap.is_watertight or not overlap.nondegenerate_faces().any()
        assert volume < 0.01, ("collision", i, j, volume)
        collisions.append({"parts": [i,j], "overlap_mm3": volume})
report["pairwise_intersections"] = collisions
# Tongue axis [-10, y, z] aligns with rotated receiver [x, 10, z].
# Values below correspond to the default SCAD parameters, like placement above.
rotation = trimesh.transformations.rotation_matrix(np.pi/2, [0,0,1])
receiver_axis = trimesh.transform_points([[171,10,30], [185,10,30]], rotation)
tongue_axis = np.array([[-10,171,30], [-10,185,30]])
assert np.allclose(receiver_axis, tongue_axis, atol=1e-6)
report["default_mating_bore_axes_mm"] = {
    "tongue": tongue_axis.tolist(), "rotated_receiver": receiver_axis.tolist()}
insertion = []
for dz in [1, 30, 120, 239, 241]:
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
(OUT / "audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2), flush=True)

for view in ["assembled", "exploded"]:
    render(view + ".png", view,
           ["--render", "--autocenter", "--viewall", "--imgsize=1300,1000",
            "--projection=o", "--camera=0,0,100,55,0,35,1000", "--colorscheme=Tomorrow"])
