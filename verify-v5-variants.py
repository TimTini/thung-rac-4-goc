"""Re-run the real V5 mesh/assembly audit for representative parameter variants."""
from pathlib import Path
import os
import re
import subprocess
import sys

if not __debug__:
    raise RuntimeError('Run variant verification without Python -O or PYTHONOPTIMIZE.')

ROOT = Path(__file__).resolve().parent
SOURCE = (ROOT / 'thung-rac-4-goc-v5.scad').read_text(encoding='utf-8')
WORK = ROOT / 'work/v5-variants'
WORK.mkdir(parents=True, exist_ok=True)
VARIANTS = {
    'smaller': {'body_size': 320, 'body_height': 200},
    'thicker': {'body_size': 390, 'body_height': 230, 'wall': 4,
                'floor_thickness': 5, 'floor_fillet': 4,
                'gusset_run': 20, 'gusset_height': 30, 'floor_lock_height': 18},
    'zero_wedge': {'pin_interference': 0, 'key_clearance': .15},
}
for name, changes in VARIANTS.items():
    source = SOURCE
    for parameter, value in changes.items():
        source, count = re.subn(r'^' + parameter + r'\s*=\s*[\d.]+;',
                                f'{parameter} = {value};', source, count=1, flags=re.M)
        assert count == 1, parameter
    path = WORK / (name + '.scad')
    path.write_text(source, encoding='utf-8')
    subprocess.run([sys.executable, '-B', str(ROOT / 'build-v5.py'), str(path),
                    str(WORK / name)], check=True)
    print('VARIANT AUDIT OK:', name, flush=True)

# Misplaced rails must be rejected instead of silently losing their connection to ribs.
bad_source = re.sub(r'^floor_lock_start = 30;', 'floor_lock_start = 90;', SOURCE, flags=re.M)
bad = WORK / 'invalid_rail.scad'
bad.write_text(bad_source, encoding='utf-8')
result = subprocess.run([os.environ.get('OPENSCAD', 'openscad'), '--backend', 'Manifold',
                         '--hardwarnings', '-D', 'view="corner"', '-o',
                         str(WORK / 'invalid.stl'), str(bad)], capture_output=True, text=True)
diagnostic = result.stdout + result.stderr
assert result.returncode != 0 and 'Floor rail must intersect' in diagnostic, diagnostic
print('INVALID RAIL REJECTED', flush=True)
optimized = subprocess.run([sys.executable, '-O', str(ROOT / 'build-v5.py')],
                           capture_output=True, text=True)
assert optimized.returncode != 0 and 'without Python -O' in optimized.stderr
print('OPTIMIZED PYTHON AUDIT REJECTED', flush=True)
