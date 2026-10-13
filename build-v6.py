"""Audit a recessed floor bridge; elastic latch motion is geometry only."""
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
SCAD = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'thung-rac-4-goc-v6.scad')
OUT = ROOT / (sys.argv[2] if len(sys.argv) > 2 else 'exports/v6')
OUT.mkdir(parents=True, exist_ok=True)
EXE = os.environ.get('OPENSCAD', 'openscad')
SOURCE = SCAD.read_text(encoding='utf-8')


def parameter(name):
    return float(re.search(r'^' + name + r'\s*=\s*([\d.]+);', SOURCE, re.M)[1])


def render(name, view, extra=()):
    (OUT / name).parent.mkdir(parents=True, exist_ok=True)
    command = [EXE, '--backend', 'Manifold', '--hardwarnings', '-D',
               f'view="{view}"', '-o', str(OUT / name), *extra, str(SCAD)]
    if name.endswith('.stl'):
        command[1:1] = ['--export-format', 'binstl']
    result = subprocess.run(command, capture_output=True, text=True)
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


report = {'source': SCAD.name, 'physical_load_test': False,
          'elastic_force_or_strain_verified': False}
meshes = {}
for name, count in [('floor_key', 1), ('floor_coupon', 2), ('corner', 1),
                    ('key', 1), ('pin', 1), ('coupon', 2), ('coupon_key', 1)]:
    render(name + '.stl', name)
    mesh = clean(trimesh.load_mesh(OUT / (name + '.stl')))
    assert mesh.is_watertight, name
    assert len(mesh.split(only_watertight=False)) == count, name
    assert abs(mesh.bounds[0, 2]) < 1e-5, (name, 'not on bed')
    assert (mesh.extents[:2] <= 250).all(), (name, 'exceeds 250 mm XY')
    if name == 'floor_key':
        assert mesh.extents[2] <= 6.01, ('floor bridge must be low profile', mesh.extents.tolist())
        unsupported = ((mesh.face_normals[:, 2] < -.708) &
                       (mesh.triangles_center[:, 2] > .01))
        area = float(mesh.area_faces[unsupported].sum())
        assert area < .01, ('floor clip has downward faces steeper than 45 degrees above bed', area)
        first_layer = mesh.section(plane_origin=[0, 0, .1], plane_normal=[0, 0, 1])
        assert first_layer is not None and len(first_layer.discrete) == 1, 'Clip first layer must be connected'
        report['floor_clip_downward_overhang_over_45deg_above_bed_mm2'] = area
        report['floor_clip_first_layer_connected'] = True
    mesh.export(OUT / (name + '.stl'))
    assert trimesh.load_mesh(OUT / (name + '.stl')).is_watertight
    meshes[name] = mesh
    report[name] = {'size_mm': mesh.extents.tolist(), 'components': count,
                   'watertight': True, 'volume_mm3': float(mesh.volume)}

half = parameter('body_size') / 2
height = parameter('body_height')
seat = parameter('floor_clip_y')
travel = parameter('floor_clip_travel')
clearance = parameter('floor_clip_clearance')
pad_height = parameter('floor_pad_height')
roof_bottom = 6 + clearance + parameter('eps')
roof = pad_height - roof_bottom
assert roof >= 1.5, ('insufficient roof above T pocket', roof)
report['pocket_roof_thickness_mm'] = roof
bridge_span = max(3 + travel + 2 * clearance, 7 + 2 * clearance)
assert bridge_span <= 14, ('new floor pocket nominal bridge too long', bridge_span)
report['new_floor_pocket_nominal_bridge_span_mm'] = bridge_span
report['slicer_support_or_bridging_verified'] = False
corner = meshes['corner'].copy()
key = rotated(moved(meshes['key'], [0, -6, -16]), -np.pi / 2, (0, 1, 0))
key = moved(key, [0, half + parameter('rail_projection') / 2, parameter('key_stop')])
pin = moved(meshes['pin'], [-4, half + parameter('rail_projection') - 14, height - 14])
clip = moved(meshes['floor_key'], [-14, seat, 0])
groups = [[] for _ in range(4)]
for i in range(4):
    for prototype, group in zip((corner, key, clip, pin), groups):
        group.append(rotated(prototype, i * np.pi / 2))
bodies, keys, clips, pins = groups
fixed = bodies + keys + clips
parts = fixed + pins
assert len(parts) == 16
report['part_count'] = 16
report['pair_count'] = 120
report['assembled_bounds_mm'] = trimesh.util.concatenate(parts).bounds.tolist()
for i, a in enumerate(fixed):
    for j, b in enumerate(fixed[i + 1:], i + 1):
        volume = overlap(a, b)
        assert volume < .01, ('seated collision', i, j, volume)
interferences = []
for i, peg in enumerate(pins):
    for j, part in enumerate(fixed):
        volume = overlap(peg, part)
        assert volume < 1, ('excessive pin interference', i, j, volume)
        if volume > .01:
            interferences.append({'pin': i, 'part': j, 'volume_mm3': volume})
    for other in pins[i + 1:]:
        assert overlap(peg, other) < .01
report['intentional_wall_pin_interference'] = interferences

for panel in bodies[:2]:
    for delta in [[1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]]:
        volume = overlap(clips[0], moved(panel, delta))
        assert volume > .1, ('floor clip not capturing panel', delta, volume)
report['clip_captures_both_panels_xz_1mm'] = True
for panel in bodies:
    for delta in [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0]]:
        assert sum(overlap(moved(panel, delta), wall_key) for wall_key in keys) > .1
report['wall_keys_restrain_each_panel_xy_1mm'] = True
# Verify actual solid material above each head pocket, not just nominal dimensions.
for x, panel in [(9, bodies[0]), (-9, bodies[1])]:
    probe = trimesh.creation.box(extents=[7 + 2 * clearance, 8 + 2 * clearance, roof])
    probe.apply_translation([x, seat + 7, roof_bottom + roof / 2])
    assert abs(overlap(probe, panel) - probe.volume) < .01, ('pocket roof missing', x)
    ledge = trimesh.creation.box(extents=[.5, 2, .5])
    ledge.apply_translation([np.sign(x) * 12.4, seat + 9, 3.0])
    assert abs(overlap(ledge, panel) - ledge.volume) < .01, ('head bearing ledge missing', x)
report['roof_and_head_bearing_ledges_solid_probes'] = True
assert sum(overlap(moved(clips[0], [0, -1, 0]), panel) for panel in bodies) > .1
report['resting_latch_blocks_clip_withdrawal_1mm'] = True

# Source-generated conservative envelopes preserve both T heads and the latch.
# Pressed latch envelope is a chosen displacement shape, not a solved elastic state.
envelopes = {}
for view in ['floor_clip_loading_sweep', 'floor_clip_slide_sweep', 'floor_latch_release_sweep',
             'floor_key_pressed']:
    artifact = OUT / 'audit' / (view + '.stl')
    render('audit/' + view + '.stl', view)
    envelope = clean(trimesh.load_mesh(artifact))
    assert envelope.is_watertight, view
    envelope.export(artifact)
    envelopes[view] = envelope
    for i in range(4):
        moving_envelope = rotated(envelope, i * np.pi / 2)
        obstacles = bodies + keys + pins + clips[:i] + clips[i + 1:]
        for j, other in enumerate(obstacles):
            volume = overlap(moving_envelope, other)
            assert volume < .01, (view, i, j, volume)
report['continuous_clip_loading_from_below_mm'] = [0, 15]
report['continuous_pressed_clip_slide_mm'] = [0, travel]
report['continuous_latch_release_clearance'] = True
pressed = trimesh.load_mesh(OUT / 'audit/floor_key_pressed.stl')
for distance in np.linspace(0, travel, 17):
    for panel in bodies:
        assert overlap(moved(pressed, [0, -distance, 0]), panel) < .01
# Independently ensure the envelopes contain the real meshes at sampled poses.
poses = {
    'floor_clip_loading_sweep': [moved(clips[0], [0, -travel, -d]) for d in np.linspace(0, 15, 7)],
    'floor_clip_slide_sweep': [moved(pressed, [0, -d, 0]) for d in np.linspace(0, travel, 17)],
    'floor_latch_release_sweep': [clips[0], pressed],
}
for view, candidates in poses.items():
    for candidate in candidates:
        outside = trimesh.boolean.difference([candidate, envelopes[view]], engine='manifold')
        assert outside.is_empty or abs(float(outside.volume)) < .01, ('sweep misses key geometry', view)
report['sweeps_contain_actual_posed_meshes'] = True

# Existing assembly paths remain sampled, separate from the new continuous sweeps.
for d in [.25, .5, 1, 2, 5, 10, 20, 40, 80, half]:
    for panel in bodies[1:]:
        assert overlap(moved(bodies[0], [d, d, 0]), panel) < .01, ('corner path', d)
for dz in [1, 8, 30, height / 2, height + 5]:
    for panel in bodies:
        assert overlap(moved(keys[0], [0, 0, dz]), panel) < .01
report['sampled_corner_and_wall_key_paths'] = True
assert overlap(moved(keys[0], [0, 0, 1]), pins[0]) > .1
root = (4.6 + parameter('pin_interference')) / 2
profiles = [[[-root, 0], [-2, -14], [2, -14], [root, 0]],
            [[-4, -.02], [4, -.02], [4, 3], [-4, 3]]]
for profile in profiles:
    vertices = np.array([[x, y, z] for x, y in profile for z in [0, 4]])
    vertices += [0, half + parameter('rail_projection'), height - 14]
    sweep = trimesh.convex.convex_hull(np.vstack([vertices + [0, 2, 0], vertices + [0, 60, 0]]))
    for other in fixed:
        assert overlap(sweep, other) < .01
seated = [overlap(pins[0], other) for other in fixed]
for distance in [.25, 1, 2, 5, 10, 20, 40, 60]:
    for j, other in enumerate(fixed):
        limit = seated[j] + .01 if distance <= 1 else .01
        assert overlap(moved(pins[0], [0, distance, 0]), other) < limit
report['continuous_wall_pin_free_approach_mm'] = [2, 60]

coupon = moved(meshes['floor_coupon'], [-24, seat - travel - 7, 0])
assert overlap(coupon, clips[0]) < .01
for delta in [[1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]]:
    assert overlap(moved(coupon, delta), clips[0]) > .1
report['coupon_compatible_and_captured'] = True
report['solid_volume_mm3'] = sum(float(part.volume) for part in parts)
(OUT / 'audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('V6 CAD AUDIT OK: 16 parts; elastic latch force and physical load unverified.', flush=True)
for view in ['assembled', 'floor_detail', 'underside_detail', 'floor_coupon', 'floor_key',
             'corner_detail', 'floor_joint_section', 'floor_joint_exploded']:
    render(view + '.png', view, ['--render', '--autocenter', '--viewall', '--imgsize=1300,1000',
                                '--projection=o', '--camera=0,0,100,55,0,35,1000',
                                '--colorscheme=Tomorrow'])
