"""Repeat V8 mesh/assembly checks for size, fit and rail length variants."""
from pathlib import Path
import os
import re
import subprocess
import sys

if not __debug__:
    raise RuntimeError('Run variant verification without Python -O or PYTHONOPTIMIZE.')
ROOT = Path(__file__).resolve().parent
SOURCE = (ROOT / 'thung-rac-4-goc-v8.scad').read_text(encoding='utf-8')
WORK = ROOT / 'work/v8-variants'
WORK.mkdir(parents=True, exist_ok=True)
VARIANTS = {
    'smaller': {'body_size': 320, 'body_height': 200},
    'larger': {'body_size': 390, 'body_height': 230, 'wall': 4, 'floor_thickness': 5,
               'gusset_run': 14, 'gusset_height': 18},
    'deeper': {'floor_rail_depth': 10, 'floor_rib_start': 13, 'floor_rail_clearance': .35},
    'tight_fit': {'floor_rail_clearance': .15, 'pin_interference': 0},
}


def replace(source, parameter, value):
    source, count = re.subn(r'^' + parameter + r'\s*=\s*[\d.]+;',
                            f'{parameter} = {value};', source, count=1, flags=re.M)
    assert count == 1, parameter
    return source


for name, changes in VARIANTS.items():
    source = SOURCE
    for parameter, value in changes.items():
        source = replace(source, parameter, value)
    path = WORK / (name + '.scad')
    path.write_text(source, encoding='utf-8')
    subprocess.run([sys.executable, '-B', str(ROOT / 'build-v8.py'), str(path),
                    str(WORK / name)], check=True)
    print('V8 VARIANT AUDIT OK:', name, flush=True)

for name, parameter, value, message in [
        ('excess_depth', 'floor_rail_depth', 12, 'Assertion'),
        ('rib_collision', 'floor_rib_start', 9, 'Floor ribs must clear'),
        ('thin_roof', 'floor_socket_height', 9, 'Assertion')]:
    path = WORK / (name + '.scad')
    path.write_text(replace(SOURCE, parameter, value), encoding='utf-8')
    result = subprocess.run([os.environ.get('OPENSCAD', 'openscad'), '--backend', 'Manifold',
                             '--hardwarnings', '-D', 'view="corner_ne"', '-o',
                             str(WORK / (name + '.stl')), str(path)], capture_output=True, text=True)
    diagnostic = result.stdout + result.stderr
    assert result.returncode != 0 and message in diagnostic, diagnostic
    print('INVALID CONFIG REJECTED:', name, flush=True)
result = subprocess.run([sys.executable, '-O', str(ROOT / 'build-v8.py')], capture_output=True, text=True)
assert result.returncode != 0 and 'without Python -O' in result.stderr
print('OPTIMIZED AUDIT REJECTED', flush=True)
