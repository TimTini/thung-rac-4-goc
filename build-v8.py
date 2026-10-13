"""Audit the V8 integral floor rails; geometry/slicing are not physical load tests."""
from pathlib import Path
import json
import os
import re
import subprocess
import sys

import numpy as np
import trimesh
import manifold3d as m3d

if not __debug__:
    raise RuntimeError('Run this audit without Python -O or PYTHONOPTIMIZE.')
ROOT = Path(__file__).resolve().parent
SCAD = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'thung-rac-4-goc-v8.scad')
OUT = ROOT / (sys.argv[2] if len(sys.argv) > 2 else 'exports/v8')
OUT.mkdir(parents=True, exist_ok=True)
EXE = os.environ.get('OPENSCAD', 'openscad')
SOURCE = SCAD.read_text(encoding='utf-8')


def parameter(name):
    return float(re.search(r'^' + name + r'\s*=\s*([\d.]+);', SOURCE, re.M)[1])


def render(name, view, extra=()):
    (OUT / name).parent.mkdir(parents=True, exist_ok=True)
    cmd = [EXE, '--backend', 'Manifold', '--hardwarnings', '-D', f'view="{view}"',
           '-o', str(OUT / name), *extra, str(SCAD)]
    if name.endswith('.stl'):
        cmd[1:1] = ['--export-format', 'binstl']
    result = subprocess.run(cmd, capture_output=True, text=True)
    diagnostic = result.stdout + result.stderr
    (OUT / (name + '.log')).write_text(diagnostic, encoding='utf-8')
    if result.returncode or 'WARNING:' in diagnostic or 'ERROR:' in diagnostic:
        raise RuntimeError(diagnostic)
    print('Rendered', name, flush=True)


def clean(mesh):
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    return mesh


def solid(mesh):
    value = m3d.Manifold(m3d.Mesh64(np.array(mesh.vertices, dtype=np.float64, order="C", copy=True),
                                  np.array(mesh.faces, dtype=np.uint64, order="C", copy=True)))
    assert value.status() == m3d.Error.NoError, value.status()
    return value


def from_solid(value):
    mesh = value.to_mesh64()
    return trimesh.Trimesh(vertices=mesh.vert_properties[:, :3], faces=mesh.tri_verts,
                           process=False)


def overlap(a, b):
    if np.any(np.minimum(a.bounds[1], b.bounds[1]) -
              np.maximum(a.bounds[0], b.bounds[0]) <= 1e-6):
        return 0.0
    return abs((solid(a) ^ solid(b)).volume())


def moved(mesh, delta):
    result = mesh.copy()
    result.apply_translation(delta)
    return result


def rotated(mesh, angle, axis=(0, 0, 1)):
    result = mesh.copy()
    result.apply_transform(trimesh.transformations.rotation_matrix(angle, axis))
    return result


def first_layer_regions(mesh):
    section = mesh.section(plane_origin=[0, 0, .1], plane_normal=[0, 0, 1])
    assert section is not None
    rings = section.discrete
    regions = 0
    for i, ring in enumerate(rings):
        x, y = ring[0, :2]
        depth = 0
        for j, other in enumerate(rings):
            if i == j:
                continue
            a, b = other[:-1, :2], other[1:, :2]
            crossing = (a[:, 1] > y) != (b[:, 1] > y)
            a, b = a[crossing], b[crossing]
            hits = a[:, 0] + (y-a[:, 1]) * (b[:, 0]-a[:, 0]) / (b[:, 1]-a[:, 1])
            depth += np.count_nonzero(hits > x) % 2
        regions += depth % 2 == 0
    return regions


def swept(mesh, delta):
    """Exact translation union: initial solid plus prisms of leading triangles."""
    delta = np.asarray(delta)
    solids = [mesh, moved(mesh, delta)]
    for tri, normal in zip(mesh.triangles, mesh.face_normals):
        if np.dot(normal, delta) > 1e-7:
            solids.append(trimesh.convex.convex_hull(np.vstack((tri, tri + delta))))
    result = from_solid(m3d.Manifold.batch_boolean([solid(x) for x in solids], m3d.OpType.Add))
    assert result.is_watertight
    return result


report = {'source': SCAD.name, 'physical_load_test': False,
          'slicer_verified_by_this_audit': False, 'part_count': 12, 'pair_count': 66}
meshes = {}
for name in ['corner_ne', 'corner_nw', 'corner_sw', 'corner_se', 'key', 'pin',
             'floor_coupon_male', 'floor_coupon_female', 'floor_coupon']:
    render(name + '.stl', name)
    mesh = clean(trimesh.load_mesh(OUT / (name + '.stl')))
    count = 2 if name == 'floor_coupon' else 1
    assert mesh.is_watertight and len(mesh.split(only_watertight=False)) == count, name
    assert abs(mesh.bounds[0, 2]) < 1e-5, name
    assert (mesh.extents[:2] <= 250).all(), name
    if name.startswith('floor_coupon'):
        bad = (mesh.face_normals[:, 2] < -.708) & (mesh.triangles_center[:, 2] > .01)
        area = float(mesh.area_faces[bad].sum())
        assert area < .01, (name, 'overhang over 45 degrees', area)
        assert first_layer_regions(mesh) == count, name
        report[name + '_overhang_over_45deg_mm2'] = area
    mesh.export(OUT / (name + '.stl'))
    assert trimesh.load_mesh(OUT / (name + '.stl')).is_watertight
    meshes[name] = mesh
    report[name] = {'size_mm': mesh.extents.tolist(), 'components': count,
                   'watertight': True, 'volume_mm3': float(mesh.volume)}

half = parameter('body_size') / 2
height = parameter('body_height')
depth = parameter('floor_rail_depth')
bodies = [rotated(meshes['corner_' + name], i * np.pi / 2)
          for i, name in enumerate(['ne', 'nw', 'sw', 'se'])]
key = moved(rotated(moved(meshes['key'], [0, -6, -16]), -np.pi / 2, (0, 1, 0)),
            [0, half + parameter('rail_projection') / 2, parameter('key_stop')])
pin = moved(meshes['pin'], [-4, half + parameter('rail_projection') - 14, height - 14])
keys = [rotated(key, i * np.pi / 2) for i in range(4)]
pins = [rotated(pin, i * np.pi / 2) for i in range(4)]
parts = bodies + keys + pins
interferences = []
for i, a in enumerate(parts):
    for j, b in enumerate(parts[:i]):
        volume = overlap(a, b)
        if i < 8:
            assert volume < .01, ('assembly collision', i, j, volume)
        else:
            assert volume < 10, ('excess wall pin interference', i, j, volume)
        if volume > .01:
            interferences.append([i, j, volume])
report['wall_pin_press_interferences_mm3'] = interferences

# Four seams: each individual male/female rail pair must resist both Z signs.
for a, b in [(0, 1), (1, 2), (2, 3), (3, 0)]:
    for dz in [-1, 1]:
        volume = overlap(moved(bodies[a], [0, 0, dz]), bodies[b])
        assert volume > 1, ('no integral floor Z retention', a, b, dz, volume)
report['floor_z_retention_each_seam_both_signs'] = True

# First close each row along X. Then move the assembled north row down along Y.
# The whole body sweep includes floor, walls, fillets, ribs and rail joints.
travel = depth + 4
sweep_checks = []
(OUT / 'audit').mkdir(exist_ok=True)
for moving, fixed, axis in [(0, [1], [travel, 0, 0]),
                            (3, [2], [travel, 0, 0]),
                            (0, [2, 3], [0, travel, 0]),
                            (1, [2, 3], [0, travel, 0])]:
    path = swept(bodies[moving], axis)
    path.export(OUT / 'audit' / f'corner_{moving}_sweep_{"x" if axis[0] else "y"}.stl')
    volumes = [overlap(path, bodies[j]) for j in fixed]
    assert max(volumes) < .01, ('continuous assembly path collision', moving, axis, volumes)
    for step in np.linspace(0, 1, 9):
        pose = moved(bodies[moving], np.asarray(axis) * step)
        missing = abs((solid(pose) - solid(path)).volume())
        assert missing < .1, ('sweep missing pose volume', moving, axis, step, missing)
    sweep_checks.append({'moving_corner': moving, 'fixed_corners': fixed,
                         'translation_mm': axis, 'collision_volumes_mm3': volumes})
report['continuous_body_assembly_sweeps'] = sweep_checks

# Wall keys installed last; each key prevents normal withdrawal of adjacent bodies.
for i, k in enumerate(keys):
    key_path = swept(k, [0, 0, height])
    for body in bodies:
        assert overlap(key_path, body) < .01, ('continuous wall key approach', i)
    normal = np.array([1., 0, 0]) @ trimesh.transformations.rotation_matrix(-i*np.pi/2, [0,0,1])[:3,:3]
    for j in [i, (i+1) % 4]:
        assert max(overlap(moved(bodies[j], normal * sign), k) for sign in [-1, 1]) > 1
report['wall_keys_prevent_floor_rail_withdrawal'] = True
report['continuous_wall_key_approach_verified'] = True

# Existing wall pins: free radial approach, then bounded final press interference.
for i, p in enumerate(pins):
    direction = np.array([-np.sin(i*np.pi/2), np.cos(i*np.pi/2), 0])
    pin_path = swept(moved(p, direction * 2), direction * 58)
    for other in bodies + keys:
        assert overlap(pin_path, other) < .01, ('continuous wall pin approach', i)
    for distance in [.1, .5, 1, 2]:
        for other in bodies + keys:
            assert overlap(moved(p, direction * distance), other) < 10, ('pin seating', i, distance)
report['continuous_wall_pin_free_approach_mm'] = [2, 60]

male = moved(meshes['floor_coupon_male'], [-depth, -12, 0])
male = rotated(male, np.pi, (0, 0, 1))
female = moved(meshes['floor_coupon_female'], [0, -12, 0])
assert overlap(male, female) < .01
for dz in [-1, 1]:
    assert overlap(moved(male, [0, 0, dz]), female) > 1
assert overlap(swept(female, [travel, 0, 0]), male) < .01
report['coupon_fit_z_retention_and_continuous_approach'] = True
(OUT / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
print('V8 CAD AUDIT OK: 12 parts, 66 pairs; no physical load rating.', flush=True)
for view in ['assembled', 'exploded', 'floor_detail', 'floor_joint_section']:
    render(view + '.png', view, ['--render', '--autocenter', '--viewall', '--imgsize=1300,1000', '--projection=o', '--camera=0,0,100,55,0,35,1000', '--colorscheme=Tomorrow'])
