"""Reproduce V3 rib collision missed by the original final-position audit."""
from pathlib import Path
import json
import numpy as np
import trimesh

root=Path(__file__).resolve().parent
directory=root/"exports/v3"
corner=trimesh.load_mesh(directory/"corner.stl")
corner.apply_translation([-8,0,0])
bodies=[]
for i in range(4):
    body=corner.copy()
    body.apply_transform(trimesh.transformations.rotation_matrix(i*np.pi/2,[0,0,1]))
    bodies.append(body)
pin=trimesh.load_mesh(directory/"pin.stl")
pin.apply_translation([-27,184,226])
report=[]
for dx in [-60,-45,-35,-30,-20,-10,0]:
    moving=pin.copy()
    moving.apply_translation([dx,0,0])
    for i,body in enumerate(bodies):
        overlap=trimesh.boolean.intersection([moving,body],engine="manifold")
        overlap.update_faces(overlap.nondegenerate_faces())
        volume=0 if overlap.is_empty or min(overlap.extents)<1e-6 else abs(float(overlap.volume))
        if volume>0.01:
            report.append({"pin_translation_x_mm":dx,"body":i,
                           "intersection_mm3":volume,"bounds_mm":overlap.bounds.tolist()})
assert any(item["intersection_mm3"]>50 for item in report)
(directory/"pin-path-failure.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
