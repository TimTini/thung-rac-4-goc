"""Build and audit V5 reinforced joints; geometry checks are not load tests."""
from pathlib import Path
import json
import os
import re
import subprocess
import sys

import numpy as np
import trimesh

if not __debug__:
    raise RuntimeError('Run this geometry audit without Python -O or PYTHONOPTIMIZE.')

ROOT = Path(__file__).resolve().parent
SCAD = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'thung-rac-4-goc-v5.scad')
OUT = ROOT / (sys.argv[2] if len(sys.argv) > 2 else 'exports/v5')
OUT.mkdir(parents=True, exist_ok=True)
EXE = os.environ.get('OPENSCAD', 'openscad')
SOURCE = SCAD.read_text(encoding='utf-8')


def parameter(name):
    return float(re.search(r'^' + name + r'\s*=\s*([\d.]+);', SOURCE, re.M)[1])


def render(name, view, extra=()):
    command = [EXE, '--backend', 'Manifold', '--hardwarnings', '-D',
               f'view="{view}"', '-o', str(OUT / name), *extra, str(SCAD)]
    if name.endswith('.stl'):
        command[1:1] = ['--export-format', 'binstl']
    result = subprocess.run(command, capture_output=True, text=True)
    (OUT / (name + '.log')).write_text(result.stdout + result.stderr, encoding='utf-8')
    if result.returncode or 'WARNING:' in result.stderr or 'ERROR:' in result.stderr:
        raise RuntimeError(result.stdout + result.stderr)
    print('Rendered', name, flush=True)


def clean(mesh):
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    return mesh


def overlap(a, b):
    # Most of the 190 pairs are disjoint; avoid a Boolean in that case.
    if np.any(np.minimum(a.bounds[1], b.bounds[1]) -
              np.maximum(a.bounds[0], b.bounds[0]) <= 1e-6):
        return 0.0
    result = trimesh.boolean.intersection([a, b], engine='manifold')
    if result.is_empty or min(result.extents) < 1e-6:
        return 0.0
    assert result.is_watertight, ('invalid intersection', result.bounds.tolist(),
                                 float(result.volume), len(result.faces))
    return abs(float(result.volume))


def moved(mesh, delta):
    result = mesh.copy()
    result.apply_translation(delta)
    return result


def rotated(mesh, angle, axis):
    result = mesh.copy()
    result.apply_transform(trimesh.transformations.rotation_matrix(angle, axis))
    return result


report = {'source': SCAD.name, 'physical_load_test': False}
meshes = {}
# The first mode deliberately fails against V4: it has no inter-part floor lock.
for name, components in [('floor_key', 1), ('corner', 1), ('key', 1), ('pin', 1),
                         ('floor_coupon', 2), ('coupon', 2), ('coupon_key', 1)]:
    render(name + '.stl', name)
    mesh = clean(trimesh.load_mesh(OUT / (name + '.stl')))
    assert mesh.is_watertight, name
    assert len(mesh.split(only_watertight=False)) == components, name
    assert abs(mesh.bounds[0, 2]) < 1e-5, (name, 'not on bed')
    assert (mesh.extents[:2] <= 250).all(), (name, 'exceeds 250 mm XY')
    mesh.export(OUT / (name + '.stl'))
    assert trimesh.load_mesh(OUT / (name + '.stl')).is_watertight
    meshes[name] = mesh
    report[name] = {'size_mm': mesh.extents.tolist(), 'components': components,
                    'watertight': True, 'volume_mm3': float(mesh.volume)}

half = parameter('body_size') / 2
height = parameter('body_height')
floor = parameter('floor_thickness')
start = parameter('floor_lock_start')
length = parameter('floor_lock_length')
lock_height = parameter('floor_lock_height')
lock_z = floor + lock_height / 2
pin_y = start + 10
rail_y = half + parameter('rail_projection') / 2

corner = moved(meshes['corner'], [-parameter('floor_lap'), 0, 0])
key = rotated(moved(meshes['key'], [0, -6, -16]), -np.pi / 2, [0, 1, 0])
key = moved(key, [0, rail_y, parameter('key_stop')])
pin = moved(meshes['pin'], [-4, half + parameter('rail_projection') - 14, height - 14])
floor_key = rotated(moved(meshes['floor_key'], [-6, -4, -16]), -np.pi / 2, [0, 1, 0])
floor_key = moved(floor_key, [0, start, lock_z])
floor_pin = rotated(moved(meshes['pin'], [-4, -14, 0]), np.pi / 2, [1, 0, 0])
floor_pin = moved(floor_pin, [10, pin_y + 2, floor + lock_height])

groups = [[] for _ in range(5)]
for i in range(4):
    for prototype, group in zip((corner, key, floor_key, pin, floor_pin), groups):
        group.append(rotated(prototype, i * np.pi / 2, [0, 0, 1]))
bodies, keys, floor_keys, pins, floor_pins = groups
fixed = bodies + keys + floor_keys
parts = fixed + pins + floor_pins
assert len(parts) == 20
report['part_count'] = len(parts)
report['assembled_bounds_mm'] = trimesh.util.concatenate(parts).bounds.tolist()

collisions = []
for i, a in enumerate(fixed):
    for j in range(i + 1, len(fixed)):
        volume = overlap(a, fixed[j])
        assert volume < .01, ('seated solid collision', i, j, volume)
        collisions.append({'parts': [i, j], 'overlap_mm3': volume})
report['fixed_pairwise_intersections'] = collisions
interferences = []
for i, peg in enumerate(pins + floor_pins):
    for j, part in enumerate(fixed):
        volume = overlap(peg, part)
        assert volume < 1, ('excessive seated pin interference', i, j, volume)
        if volume > .01:
            interferences.append({'pin': i, 'part': j, 'interference_mm3': volume})
for i, a in enumerate(pins + floor_pins):
    for b in (pins + floor_pins)[i + 1:]:
        assert overlap(a, b) < .01
report['intentional_pin_interference'] = interferences
report['pair_count'] = len(parts) * (len(parts) - 1) // 2

# Before any keys are installed, the final corner still enters diagonally.
for distance in [.25, .5, 1, 2, 5, 10, 20, 40, 80, half]:
    moving = moved(bodies[0], [distance, distance, 0])
    for other in bodies[1:]:
        assert overlap(moving, other) < .01, ('corner path', distance)
report['sampled_corner_diagonal_path'] = True

for dz in [1, 8, 30, height / 2, height + 5]:
    for other in bodies:
        assert overlap(moved(keys[0], [0, 0, dz]), other) < .01, ('wall key path', dz)
report['sampled_wall_key_path'] = True

# Check all four floor-key paths with the other three already seated.
for i, spline in enumerate(floor_keys):
    direction = np.array([np.sin(i * np.pi / 2), -np.cos(i * np.pi / 2), 0])
    obstacles = bodies + keys + pins + floor_keys[:i] + floor_keys[i + 1:]
    for distance in [.25, 1, 2, 5, 10, 20, 30, 44]:
        for other in obstacles:
            volume = overlap(moved(spline, direction * distance), other)
            assert volume < .01, ('floor key insertion', i, distance, volume)
report['sampled_floor_key_path_mm'] = [.25, 1, 2, 5, 10, 20, 30, 44]
render('floor_key_sweep.stl', 'floor_key_sweep')
sweep = trimesh.load_mesh(OUT / 'floor_key_sweep.stl')
assert sweep.is_watertight
for i in range(4):
    moving_sweep = rotated(sweep, i * np.pi / 2, [0, 0, 1])
    for other in bodies + keys + pins + floor_keys[:i] + floor_keys[i + 1:] + floor_pins[:i] + floor_pins[i + 1:]:
        assert overlap(moving_sweep, other) < .01, ('continuous floor key path', i)
report['continuous_floor_key_free_approach_mm'] = [0, length + 4]

# A floor key must restrain both adjacent panels in both signs of Z and X.
for panel in [bodies[0], bodies[1]]:
    for direction in [[1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]]:
        volume = overlap(floor_keys[0], moved(panel, direction))
        assert volume > .1, ('floor key does not capture panel', direction, volume)
report['floor_key_captures_both_panels_xz_1mm'] = True
# A spline is free along its own axis. The existing wall keys close that DOF
# for every corner in the complete assembly; do not attribute it to the floor key.
for panel in bodies:
    for direction in [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0]]:
        assert sum(overlap(moved(panel, direction), wall_key) for wall_key in keys) > .1
report['wall_keys_restrain_each_panel_xy_1mm'] = True
assert overlap(moved(floor_keys[0], [0, -1, 0]), floor_pins[0]) > .1
assert overlap(moved(keys[0], [0, 0, 1]), pins[0]) > .1
report['pins_block_key_withdrawal_1mm'] = True

# Pin approach: each convex pin piece has an exact translational swept volume.
root = (4.6 + parameter('pin_interference')) / 2
pin_profiles = [[[-root, 0], [-2, -14], [2, -14], [root, 0]],
                [[-4, -.02], [4, -.02], [4, 3], [-4, 3]]]
for floor_mode in [False, True]:
    peg = floor_pins[0] if floor_mode else pins[0]
    direction = np.array([0, 0, 1] if floor_mode else [0, 1, 0])
    obstacles = fixed + (pins if floor_mode else floor_pins)
    seated = [overlap(peg, other) for other in obstacles]
    for distance in [.25, 1, 2, 5, 10, 20, 40, 60]:
        for j, other in enumerate(obstacles):
            allowance = seated[j] + .01 if distance <= 1 else .01
            assert overlap(moved(peg, direction * distance), other) < allowance
    for profile in pin_profiles:
        vertices = np.array([[x, y, z] for x, y in profile for z in [0, 4]])
        hull = trimesh.convex.convex_hull(vertices)
        if floor_mode:
            hull = rotated(hull, np.pi / 2, [1, 0, 0])
            hull = moved(hull, [10, pin_y + 2, floor + lock_height])
        else:
            hull = moved(hull, [0, half + parameter('rail_projection'), height - 14])
        sweep = trimesh.convex.convex_hull(np.vstack([
            hull.vertices + direction * 2, hull.vertices + direction * 60]))
        for other in obstacles:
            assert overlap(sweep, other) < .01, ('continuous pin approach', floor_mode)
report['continuous_pin_free_approach_mm'] = [2, 60]

# Coupon must use exactly the same floor key and pin placement, normalized to its bed.
coupon = moved(meshes['floor_coupon'], [-25, start - 5, 0])
assert overlap(coupon, floor_keys[0]) < .01
assert 0 < overlap(coupon, floor_pins[0]) < 1
report['floor_coupon_compatible'] = True

report['solid_volume_mm3'] = sum(float(part.volume) for part in parts)
(OUT / 'audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('CAD AUDIT OK: 20 parts, 190 pairs; no physical load rating.', flush=True)
for view in ['assembled', 'exploded', 'floor_detail', 'corner_detail', 'floor_coupon']:
    render(view + '.png', view,
           ['--render', '--autocenter', '--viewall', '--imgsize=1300,1000',
            '--projection=o', '--camera=0,0,100,55,0,35,1000', '--colorscheme=Tomorrow'])
