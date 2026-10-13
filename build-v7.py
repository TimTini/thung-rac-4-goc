"""Audit the V7 sliding cap rails; geometry/slicing are not physical load tests."""
from pathlib import Path
import json
import os
import re
import subprocess
import sys

import numpy as np
import trimesh

if not __debug__:
    raise RuntimeError('Run this audit without Python -O or PYTHONOPTIMIZE.')
ROOT = Path(__file__).resolve().parent
SCAD = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'thung-rac-4-goc-v7.scad')
OUT = ROOT / (sys.argv[2] if len(sys.argv) > 2 else 'exports/v7')
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


def overlap(a, b):
    if np.any(np.minimum(a.bounds[1], b.bounds[1]) -
              np.maximum(a.bounds[0], b.bounds[0]) <= 1e-6):
        return 0.0
    result = trimesh.boolean.intersection([a, b], engine='manifold')
    if result.is_empty or min(result.extents) < 1e-6:
        return 0.0
    assert result.is_watertight
    return abs(float(result.volume))


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


report = {'source': SCAD.name, 'physical_load_test': False, 'slicer_verified_by_this_audit': False}
meshes = {}
for name, count in [('floor_key', 1), ('corner', 1), ('floor_pin', 1), ('key', 1),
                    ('pin', 1), ('floor_coupon', 2), ('floor_coupon_key', 1)]:
    render(name + '.stl', name)
    mesh = clean(trimesh.load_mesh(OUT / (name + '.stl')))
    assert mesh.is_watertight, name
    assert len(mesh.split(only_watertight=False)) == count, name
    assert abs(mesh.bounds[0, 2]) < 1e-5, (name, 'not on bed')
    assert (mesh.extents[:2] <= 250).all(), (name, 'exceeds 250 mm XY')
    if name == 'floor_key':
        assert mesh.extents[1] >= 80, ('expected long sliding rail', mesh.extents.tolist())
    if name in {'floor_key', 'floor_coupon_key', 'floor_pin'}:
        bad = (mesh.face_normals[:, 2] < -.708) & (mesh.triangles_center[:, 2] > .01)
        area = float(mesh.area_faces[bad].sum())
        assert area < .01, ('unsupported downward faces above bed', name, area)
        assert first_layer_regions(mesh) == 1, ('disconnected first layer', name)
        report[name + '_overhang_over_45deg_mm2'] = area
    mesh.export(OUT / (name + '.stl'))
    assert trimesh.load_mesh(OUT / (name + '.stl')).is_watertight
    meshes[name] = mesh
    report[name] = {'size_mm': mesh.extents.tolist(), 'components': count,
                   'watertight': True, 'volume_mm3': float(mesh.volume)}

half = parameter('body_size') / 2
height = parameter('body_height')
floor = parameter('floor_thickness')
start = parameter('floor_rail_start')
length = parameter('floor_rail_length')
short = parameter('floor_coupon_length')
clearance = parameter('floor_rail_clearance')
corner = meshes['corner'].copy()
key = moved(rotated(moved(meshes['key'], [0, -6, -16]), -np.pi / 2, (0, 1, 0)),
            [0, half + parameter('rail_projection') / 2, parameter('key_stop')])
pin = moved(meshes['pin'], [-4, half + parameter('rail_projection') - 14, height - 14])


def seated_rail(mesh, rail_length):
    return moved(rotated(moved(mesh, [-10.5, -rail_length, -(floor + 5)]), np.pi, (1, 0, 0)),
                 [0, start, 0])


floor_key = seated_rail(meshes['floor_key'], length)
floor_pin = moved(rotated(moved(meshes['floor_pin'], [-3, -3, -4.2]), np.pi, (1, 0, 0)),
                  [5, start + 8, floor + 2])
groups = [[] for _ in range(5)]
for i in range(4):
    for prototype, group in zip((corner, key, floor_key, pin, floor_pin), groups):
        group.append(rotated(prototype, i * np.pi / 2))
bodies, keys, rails, pins, floor_pins = groups
fixed = bodies + keys + rails
parts = fixed + pins + floor_pins
assert len(parts) == 20
report['part_count'] = 20
report['pair_count'] = 190
report['assembled_bounds_mm'] = trimesh.util.concatenate(parts).bounds.tolist()
for i, a in enumerate(fixed):
    for j, b in enumerate(fixed[i + 1:], i + 1):
        volume = overlap(a, b)
        assert volume < .01, ('seated collision', i, j, volume)
interference = []
for i, peg in enumerate(pins + floor_pins):
    for j, other in enumerate(fixed):
        volume = overlap(peg, other)
        assert volume < 1, ('excessive pin interference', i, j, volume)
        if volume > .01:
            interference.append({'pin': i, 'part': j, 'volume_mm3': volume})
    for other in (pins + floor_pins)[i + 1:]:
        assert overlap(peg, other) < .01
report['intentional_pin_interference'] = interference

for panel in bodies[:2]:
    for delta in [[1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]]:
        assert overlap(floor_key, moved(panel, delta)) > .1, ('rail does not capture panel', delta)
for panel in bodies:
    for delta in [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0]]:
        assert sum(overlap(moved(panel, delta), k) for k in keys) > .1
report['floor_rail_captures_both_panels_xz_1mm'] = True
report['wall_keys_restrain_each_panel_xy_1mm'] = True
assert overlap(moved(floor_key, [0, -1, 0]), floor_pin) > .1
assert sum(overlap(moved(floor_key, [0, 1, 0]), b) for b in bodies) > .1
report['head_stops_forward_pin_stops_reverse_1mm'] = True

render('audit/floor_key_sweep.stl', 'floor_key_sweep')
sweep = clean(trimesh.load_mesh(OUT / 'audit/floor_key_sweep.stl'))
assert sweep.is_watertight
sweep.export(OUT / 'audit/floor_key_sweep.stl')
for i in range(4):
    envelope = rotated(sweep, i * np.pi / 2)
    obstacles = bodies + keys + pins + rails[:i] + rails[i + 1:] + floor_pins[:i] + floor_pins[i + 1:]
    for j, other in enumerate(obstacles):
        volume = overlap(envelope, other)
        assert volume < .01, ('continuous rail path blocked', i, j, volume)
for distance in np.linspace(0, length + 3, 17):
    candidate = moved(floor_key, [0, -distance, 0])
    outside = trimesh.boolean.difference([candidate, sweep], engine='manifold')
    assert outside.is_empty or abs(float(outside.volume)) < .01, 'Sweep misses rail geometry'
report['continuous_rail_free_approach_mm'] = [0, length + 3]

# Exact axial swept volume of the tapered round floor pin over its free approach.
render('audit/floor_pin_sweep.stl', 'floor_pin_sweep')
pin_sweep = clean(trimesh.load_mesh(OUT / 'audit/floor_pin_sweep.stl'))
assert pin_sweep.is_watertight
for other in fixed:
    assert overlap(pin_sweep, other) < .01, 'Floor pin free approach blocked'
seated = [overlap(floor_pin, other) for other in fixed]
for dz in [.1, .25, .5, 1, 2, 5, 15]:
    for j, other in enumerate(fixed):
        limit = seated[j] + .01 if dz < 1 else .01
        assert overlap(moved(floor_pin, [0, 0, dz]), other) < limit
report['continuous_floor_pin_free_approach_mm'] = [1, 15]

for d in [.25, 1, 5, 20, 80, half]:
    for other in bodies[1:]:
        assert overlap(moved(bodies[0], [d, d, 0]), other) < .01
for dz in [1, 8, 30, height / 2, height + 5]:
    for other in bodies:
        assert overlap(moved(keys[0], [0, 0, dz]), other) < .01
assert overlap(moved(keys[0], [0, 0, 1]), pins[0]) > .1
report['sampled_corner_and_wall_key_paths'] = True
root = (4.6 + parameter('pin_interference')) / 2
for profile in [[[-root, 0], [-2, -14], [2, -14], [root, 0]],
                [[-4, -.02], [4, -.02], [4, 3], [-4, 3]]]:
    vertices = np.array([[x, y, z] for x, y in profile for z in [0, 4]])
    vertices += [0, half + parameter('rail_projection'), height - 14]
    envelope = trimesh.convex.convex_hull(np.vstack([vertices + [0, 2, 0], vertices + [0, 60, 0]]))
    for other in fixed:
        assert overlap(envelope, other) < .01
report['continuous_wall_pin_free_approach_mm'] = [2, 60]

coupon = moved(meshes['floor_coupon'], [-18, start - 4, 0])
coupon_key = seated_rail(meshes['floor_coupon_key'], short)
assert overlap(coupon, coupon_key) < .01
assert overlap(coupon, floor_pin) < .01
for delta in [[1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]]:
    assert overlap(moved(coupon, delta), coupon_key) > .1
report['short_coupon_compatible'] = True
report['solid_volume_mm3'] = sum(float(part.volume) for part in parts)
(OUT / 'audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('V7 CAD AUDIT OK: 20 parts, 190 pairs; no physical load rating.', flush=True)
for view in ['assembled', 'floor_detail', 'floor_key', 'floor_pin', 'floor_joint_section', 'floor_joint_exploded']:
    render(view + '.png', view, ['--render', '--autocenter', '--viewall', '--imgsize=1300,1000',
                                '--projection=o', '--camera=0,0,100,55,0,35,1000', '--colorscheme=Tomorrow'])
