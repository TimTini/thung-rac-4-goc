"""Native, expression-driven Fusion model of thung-rac-4-goc-v4.scad.

Run in Fusion. Offline import exposes the SAME profile expressions consumed by
build(), so geometry tests do not test a separate copy of the model.
"""
import math
import traceback

VERIFY_VARIANTS = False
DEFAULTS = {
    'body_size': 360, 'body_height': 240, 'wall': 3.2,
    'floor_thickness': 4, 'corner_radius': 18,
    'rib_projection': 10, 'rib_thickness': 3,
    'band_projection': 8, 'band_height': 24,
    'floor_rib_height': 8, 'floor_rib_width': 4,
    'seam_gap': .4, 'key_clearance': .25,
    'rail_width': 48, 'rail_projection': 16, 'key_stop': 8,
    'floor_lap': 8, 'floor_clearance': .3, 'pin_interference': .1,
    'rib_fillet': 1.5,
}
COMMENTS = dict(zip(DEFAULTS, (
    'Cạnh thân danh nghĩa; mm; thay đổi lòng chứa và vị trí ray/chốt',
    'Chiều cao thân; mm; đổi đồng thời chiều dài khóa và cao độ chốt',
    'Dày thành; mm; giữ ít nhất 3 mm',
    'Dày đáy; mm; điều khiển cả hai bậc môi ghép',
    'Bán kính góc ngoài; mm; góc lòng bằng bán kính trừ thành',
    'Độ nhô gân ngoài; mm', 'Dày thân gân ngoài; mm',
    'Độ nhô đai giữa thân; mm', 'Chiều cao đai; mm',
    'Chiều cao gân đáy trong; mm', 'Rộng gân đáy trong; mm',
    'Khe giữa bốn góc; mm; tác động thân và hai nửa ray',
    'Khe vuông góc từng mặt khóa; mm; 0,15 đến 0,5',
    'Rộng tổng hai nửa ray; mm', 'Độ nhô ray ngoài thành; mm',
    'Cao vai chặn đáy khóa; mm', 'Dài môi ghép đáy; mm',
    'Khe ghép đáy; mm; dưới 0,6',
    'Ép nêm tại gốc chốt; mm; cho phép 0 đến 0,2',
    'Bán kính bo gân ngoài; mm; liên kết fillet native',
)))
DERIVED = {
    'half_body': ('body_size / 2', 'mm'),
    'rail_y': ('half_body + rail_projection / 2', 'mm'),
    'key_length': ('body_height - key_stop', 'mm'),
    'pin_z': ('body_height - 12 mm', 'mm'),
}


def layout(p):
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    require(all(math.isfinite(v) and (v >= 0 if k == 'pin_interference' else v > 0)
                for k, v in p.items()), 'Tham số phải hữu hạn và dương; pin_interference được bằng 0.')
    require(p['body_size'] >= 320 and p['body_height'] >= 120, 'body_size >= 320; body_height >= 120 mm.')
    require(3 <= p['wall'] < p['corner_radius'] < p['body_size']/4, 'wall/corner_radius không hợp lệ.')
    require(p['wall'] <= 8, 'wall tối đa 8 mm để lỗ chốt không xuyên lòng.')
    require(p['floor_thickness'] >= 4, 'floor_thickness ít nhất 4 mm.')
    require(.15 <= p['key_clearance'] <= .5, 'key_clearance phải trong 0,15..0,5 mm.')
    require(0 < p['seam_gap'] < 1, 'seam_gap phải trong 0..1 mm.')
    require(44 <= p['rail_width'] < p['body_size']/3 and p['rail_projection'] >= 16,
            'rail_width hoặc rail_projection không đủ/vượt thân.')
    require(8 <= p['floor_lap'] < p['body_size']/8 and 0 < p['floor_clearance'] < .6,
            'floor_lap/floor_clearance không hợp lệ.')
    require(0 <= p['pin_interference'] <= .2, 'pin_interference phải trong 0..0,2 mm.')
    require(p['key_stop'] + 4 < p['body_height'] - 14.25, 'key_stop quá cao so với lỗ chốt.')
    require(p['band_height'] > p['band_projection'] and p['band_height'] < p['body_height']/2,
            'band_height phải lớn hơn band_projection và dưới nửa chiều cao.')
    require(p['floor_thickness'] + p['floor_rib_height'] < p['body_height'] - 16,
            'Gân đáy quá cao so với chốt.')
    extent = max(p['rail_projection'] + 3, p['rib_projection'], p['band_projection'], 4)
    part_extent=max(p['rail_projection'],p['rib_projection'],p['band_projection'],4)
    return {'solid_count':12,'assembled_bounds_mm':(p['body_size']+2*extent,)*2+(p['body_height']+4,),
            'part_bounds_mm':[(p['body_size']/2+part_extent+p['floor_lap'],p['body_size']/2+part_extent-p['seam_gap']/2,p['body_height']),
                              (32,12,p['body_height']-p['key_stop']+4),(8,17,4)]}


def evaluate(expression, p):
    """Evaluate our arithmetic-only mm expressions for offline verification."""
    values = dict(p)
    for name, (expr, _) in DERIVED.items():
        values[name] = eval(expr.replace(' mm', ''), {'__builtins__': {}}, values)
    return eval(str(expression).replace(' mm', ''), {'__builtins__': {}}, values)


def _evaluate_profile(profile, p):
    if isinstance(profile, dict):
        result = dict(profile)
        result['points'] = [(evaluate(x, p), evaluate(y, p)) for x, y in profile['points']]
        result['center'] = (evaluate(profile['center'][0], p), evaluate(profile['center'][1], p))
        return result
    if profile and isinstance(profile[0], (list, tuple)) and profile[0] and \
            isinstance(profile[0][0], (list, tuple)):
        return [_evaluate_profile(child, p) for child in profile]
    return [(evaluate(x, p), evaluate(y, p)) for x, y in profile]


def evaluate_step(step, p):
    result = dict(step, profile=_evaluate_profile(step['profile'], p),
                  z=evaluate(step['z'], p), depth=evaluate(step['depth'], p))
    if 'sections' in step:
        result['sections'] = [_evaluate_profile(section, p) for section in step['sections']]
    return result


def rectangle(x, y, width, height):
    return [(x, y), ('('+x+')+('+width+')', y),
            ('('+x+')+('+width+')', '('+y+')+('+height+')'),
            (x, '('+y+')+('+height+')')]


def quarter_outline(expansion='0 mm', wall=False):
    """Compact analytic rounded-square quarter profile.

    The native builder creates true circular arcs from this descriptor; points
    are only arc endpoints and straight boundary endpoints.  Each arc carries
    (start, end, z_normal_sign, radius_expression) so Fusion gets a driving
    radial dimension — center+endpoints alone leave the arc under-constrained.
    """
    g = 'seam_gap / 2'
    out = 'half_body + ('+expansion+')'
    centre = '(half_body - corner_radius)'
    # Outer edge moves with expansion; corner center stays fixed on the body.
    outer_radius = 'corner_radius + ('+expansion+')'
    if not wall:
        return {'kind': 'rounded_outline',
                'points': [(g, g), (out, g), (out, centre), (centre, out), (g, out)],
                'center': (centre, centre),
                'arcs': [(2, 3, 1, outer_radius)]}
    inner_edge = 'half_body-wall'
    return {'kind': 'rounded_outline',
            'points': [(g, out), (centre, out), (out, centre), (out, g),
                       (inner_edge, g), (inner_edge, centre), (centre, inner_edge),
                       (g, inner_edge)],
            'center': (centre, centre),
            'arcs': [(1, 2, -1, outer_radius), (5, 6, 1, 'corner_radius-wall')]}


BOWTIE = [(-16,-4),(-6,-2),(6,-2),(16,-4),(16,4),(6,2),(-6,2),(-16,4)]
BOWTIE_ROUND_MM = 0.6


def bowtie():
    """Nominal source profile; Fusion rounds it and applies clearance natively."""
    return [(str(x)+' mm', 'rail_y + '+str(y)+' mm') for x, y in BOWTIE]


def geometry_plan(p):
    """Ordered native extrusion operations, shared with offline geometry tests."""
    layout(p)
    steps=[]
    def add(name, target, operation, profile, z, depth, feature_kind=None):
        step = dict(name=name, target=target, operation=operation, profile=profile, z=z, depth=depth)
        if isinstance(profile, dict):
            step['profile_kind'] = profile['kind']
        elif 'dovetail slot' in name:
            step['profile_kind'] = 'bowtie_offset'
        elif name == 'Key stem':
            step['profile_kind'] = 'bowtie'
        elif name.startswith('Outer rib'):
            step['profile_kind'] = 'rib_offset'
        elif name in {'Bottom tongue', 'Bottom rebate', 'Floor rib X1', 'Floor rib X2',
                      'Floor rib Y1', 'Floor rib Y2', 'Rail Y pin bore', 'Rail X pin bore',
                      'Key head', 'Pin head'}:
            step['profile_kind'] = 'rectangle'
        if feature_kind:
            step['feature_kind'] = feature_kind
        steps.append(step)
    def box(name,target,operation,x,y,w,h,z,depth):
        add(name,target,operation,rectangle(x,y,w,h),z,depth)
    add('Corner floor','corner','new',quarter_outline(),'0 mm','floor_thickness')
    add('Corner walls','corner','join',quarter_outline(wall=True),'floor_thickness','body_height-floor_thickness')
    add('Top rim','corner','join',quarter_outline('4 mm',wall=True),'body_height-12 mm','12 mm')
    band_z = 'body_height/2-band_height/2'
    add('Middle band ramp', 'corner', 'join', quarter_outline(wall=True), band_z,
        'band_projection', 'loft')
    steps[-1]['sections'] = [quarter_outline('band_projection', wall=True)]
    add('Middle band straight', 'corner', 'join', quarter_outline('band_projection', wall=True),
        '('+band_z+')+band_projection', 'band_height-band_projection')
    rib_profiles=[]
    for i,f in enumerate(('.34','.66'),1):
        rib=[('half_body*'+f+' - rib_thickness/2 - 2 mm','half_body-wall/2'),
             ('half_body*'+f+' + rib_thickness/2 + 2 mm','half_body-wall/2'),
             ('half_body*'+f+' + rib_thickness/2','half_body+rib_projection-1.5 mm'),
             ('half_body*'+f+' - rib_thickness/2','half_body+rib_projection-1.5 mm')]
        rib_profiles.extend((rib, [(y,x) for x,y in rib]))
    add('Outer ribs','corner','join',rib_profiles,'0 mm','body_height')
    steps[-1]['profile_kind'] = 'rib_group'
    steps[-1]['offset_signs'] = ['-1','1','-1','1']
    steps[-1]['offset_parameter'] = 'rib_fillet'
    floor_rib_profiles=[]
    for f in ('1/3','2/3'):
        rib=rectangle('floor_lap+2 mm','half_body*('+f+')-floor_rib_width/2',
                      'half_body-wall-floor_lap-2 mm','floor_rib_width')
        floor_rib_profiles.extend((rib, [(y,x) for x,y in rib]))
    add('Floor ribs','corner','join',floor_rib_profiles,
        'floor_thickness-.02 mm','floor_rib_height+.02 mm')
    steps[-1]['profile_kind'] = 'rectangle_group'
    box('Bottom tongue','corner','join','-floor_lap','floor_lap+2 mm',
        'floor_lap+seam_gap/2+1 mm','half_body-wall-2*floor_lap-4 mm','0 mm','(floor_thickness-floor_clearance)/2')
    box('Bottom rebate','corner','cut','2 mm-floor_clearance','-.02 mm',
        'half_body-wall-4 mm+2*floor_clearance','floor_lap+floor_clearance+.02 mm',
        '0 mm','(floor_thickness+floor_clearance)/2')
    rail=[('seam_gap/2','half_body-wall/2'),('rail_width/2','half_body-wall/2'),
          ('rail_width/2-3 mm','half_body+rail_projection'),('seam_gap/2','half_body+rail_projection')]
    # BOWTIE is CCW, so Autodesk's positive-right offset is outward for Y;
    # transposing it for X reverses winding and therefore reverses the sign.
    for axis,profile,offset_sign in (('Y',rail,'1'),('X',[(y,x) for x,y in rail],'-1')):
        add('Rail '+axis,'corner','join',profile,'0 mm','body_height')
        slot=bowtie()
        add('Rail '+axis+' dovetail slot','corner','cut',slot if axis=='Y' else [(y,x) for x,y in slot],
            'key_stop','key_length+.02 mm')
        steps[-1]['offset_sign'] = offset_sign
    bore=rectangle('-2.3 mm','half_body+2 mm','4.6 mm','rail_projection-2 mm+.02 mm')
    add('Rail Y pin bore','corner','cut',bore,'pin_z-2.25 mm','4.5 mm')
    add('Rail X pin bore','corner','cut',[(y,x) for x,y in bore],'pin_z-2.25 mm','4.5 mm')
    add('Key stem','key','new',bowtie(),'key_stop','key_length')
    box('Key head','key','join','-16 mm','rail_y-6 mm','32 mm','12 mm','body_height','4 mm')
    add('Key pin bore','key','cut',bore,'pin_z-2.25 mm','4.5 mm')
    out='half_body+rail_projection'
    add('Pin wedge','pin','new',[
        ('-(4.6 mm+pin_interference)/2',out),('-2 mm',out+'-14 mm'),
        ('2 mm',out+'-14 mm'),('(4.6 mm+pin_interference)/2',out)],'pin_z-2 mm','4 mm')
    box('Pin head','pin','join','-4 mm',out+'-.02 mm','8 mm','3.02 mm','pin_z-2 mm','4 mm')
    return steps


def _collection(core, items):
    result=core.ObjectCollection.create()
    for item in items:
        result.add(item)
    return result


def _coordinate_axes(sketch, core):
    """Fixed construction datums; only model points receive parameter dimensions."""
    axes=[]
    for start,end in (((0,-1,0),(0,1,0)),((-1,0,0),(1,0,0))):
        line=sketch.sketchCurves.sketchLines.addByTwoPoints(
            core.Point3D.create(*start),core.Point3D.create(*end))
        line.isConstruction=True
        line.isFixed=True
        # Fixing a line leaves its endpoints free to slide along it in Fusion.
        line.startSketchPoint.isFixed=True
        line.endSketchPoint.isFixed=True
        axes.append(line)
    return axes  # Y datum measures X; X datum measures Y.


def _drive_point(sketch, axes, design, core, step, vertex, point, expressions, coords):
    """Drive an existing sketch point from the fixed construction datums."""
    for axis, expression in enumerate(expressions):
        if abs(coords[axis]) < 1e-8:
            constraint=sketch.geometricConstraints
            if axis == 0:
                constraint.addVerticalPoints(sketch.originPoint, point)
            else:
                constraint.addHorizontalPoints(sketch.originPoint, point)
            continue
        try:
            dim=sketch.sketchDimensions.addOffsetDimension(
                axes[axis], point, core.Point3D.create(coords[0]+.3, coords[1]+.3, 0), True)
        except Exception as error:
            constraints=[c.objectType for c in point.geometricConstraints]
            raise RuntimeError(
                '{} vertex {} axis {} expression {}: xy_cm=({}, {}), fixed={}, '
                'reference={}, fullyConstrained={}, constraints={}; {}'.format(
                    step['name'], vertex, 'XY'[axis], expression,
                    point.geometry.x, point.geometry.y, point.isFixed,
                    point.isReference, point.isFullyConstrained, constraints, error)) from error
        dim.parameter.expression='abs('+expression+')'
    return point


def _dimension_point(sketch, axes, design, core, step, vertex, expressions):
    coords=[design.unitsManager.evaluateExpression(e, 'mm') for e in expressions]
    point=sketch.sketchPoints.add(core.Point3D.create(coords[0], coords[1], 0))
    return _drive_point(sketch, axes, design, core, step, vertex, point, expressions, coords)


def _finish_sketch(sketch):
    if not sketch.isFullyConstrained:
        raise RuntimeError('Sketch chưa đủ ràng buộc: '+sketch.name)
    if sketch.profiles.count != 1:
        raise RuntimeError('Cần đúng một profile kín: '+sketch.name)
    return sketch


def _finish_multi_sketch(sketch, expected_profiles=None, minimum_profiles=None):
    if not sketch.isFullyConstrained:
        raise RuntimeError('Sketch chưa đủ ràng buộc: '+sketch.name)
    if expected_profiles is not None and sketch.profiles.count != expected_profiles:
        raise RuntimeError('Cần đúng {} profile kín: {}'.format(expected_profiles, sketch.name))
    if minimum_profiles is not None and sketch.profiles.count < minimum_profiles:
        raise RuntimeError('Cần ít nhất {} profile kín: {}'.format(minimum_profiles, sketch.name))
    return sketch


def _rounded_sketch(sketch, axes, design, core, step):
    profile=step['profile']
    points=[_dimension_point(sketch, axes, design, core, step, i+1, pair)
            for i, pair in enumerate(profile['points'])]
    centre=_dimension_point(sketch, axes, design, core, step, len(points)+1, profile['center'])
    # arc map: (start, end) -> (z_normal_sign, radius_expression)
    arcs={}
    for item in profile['arcs']:
        start, end, direction, radius_expr = item[0], item[1], item[2], item[3]
        arcs[(start, end)] = (direction, radius_expr)
    for i in range(len(points)):
        j=(i+1)%len(points)
        if (i, j) in arcs:
            direction, radius_expr = arcs[(i, j)]
            normal=core.Vector3D.create(0, 0, direction)
            arc=sketch.sketchCurves.sketchArcs.addByCenterStartEnd(
                centre, points[i], points[j], normal)
            if arc is None:
                raise RuntimeError('Không tạo được cung bo góc: '+step['name'])
            # Same pattern as bowtie fillets / TimetableBoard: driving radius
            # locks the arc; dimensioned center+chord alone is not enough.
            text=core.Point3D.create(arc.centerSketchPoint.geometry.x+.03,
                                     arc.centerSketchPoint.geometry.y+.03, 0)
            radius_dim=sketch.sketchDimensions.addRadialDimension(arc, text)
            radius_dim.parameter.expression=radius_expr
        else:
            sketch.sketchCurves.sketchLines.addByTwoPoints(points[i], points[j])
    return _finish_sketch(sketch)


def _rectangle_sketch(sketch, axes, design, core, step, finish=True):
    """Fully constrain an axis-aligned rectangle by driving every corner.

    TimetableBoard's one-anchor + width/height pattern assumes
    addTwoPointRectangle installs Horizontal/Vertical edge constraints.
    Through the API those edge constraints are not reliable: locking only
    the diagonal still leaves the other two corners free to shear.  That is
    why Floor ribs stayed under-constrained after the previous fix even
    though offline mocks reported isFullyConstrained=True.

    Driving all four corners matches _polygon_sketch, which Fusion already
    accepts for multi-profile Outer ribs groups in this same script.
    """
    points=[_dimension_point(sketch, axes, design, core, step, i+1, pair)
            for i, pair in enumerate(step['profile'])]
    for i in range(len(points)):
        sketch.sketchCurves.sketchLines.addByTwoPoints(
            points[i], points[(i+1)%len(points)])
    return _finish_sketch(sketch) if finish else sketch


def _rounded_bowtie_sketch(sketch, axes, design, core, step, offset=False):
    # Keep the expression-driven polygon as construction geometry.  Fillet
    # trims its input curves, so a separately created, unanchored copy carries
    # the rounded profile without trimming the dimensioned parent vertices.
    parent_points=[_dimension_point(sketch, axes, design, core, step, i+1, pair)
                   for i, pair in enumerate(step['profile'])]
    parent_lines=[sketch.sketchCurves.sketchLines.addByTwoPoints(
        parent_points[i], parent_points[(i+1)%len(parent_points)])
        for i in range(len(parent_points))]
    for line in parent_lines:
        line.isConstruction=True
    model_lines=[]
    for i, parent in enumerate(parent_lines):
        start=parent_points[i].geometry
        end=parent_points[(i+1)%len(parent_points)].geometry
        model=sketch.sketchCurves.sketchLines.addByTwoPoints(
            core.Point3D.create(start.x, start.y, 0),
            core.Point3D.create(end.x, end.y, 0))
        sketch.geometricConstraints.addCollinear(model, parent)
        model_lines.append(model)
    arcs=sketch.sketchCurves.sketchArcs
    fillet_arcs=[]
    for i in range(len(model_lines)):
        first=model_lines[i-1]
        second=model_lines[i]
        first_point=first.endSketchPoint.geometry
        second_point=second.startSketchPoint.geometry
        arc=arcs.addFillet(first, first_point, second, second_point,
                           BOWTIE_ROUND_MM/10)
        if arc is None:
            raise RuntimeError('Không tạo được fillet parent bowtie tại đỉnh {}.'.format(i+1))
        fillet_arcs.append(arc)
        radius=sketch.sketchDimensions.addRadialDimension(
            arc, core.Point3D.create(arc.centerSketchPoint.geometry.x + .03,
                                     arc.centerSketchPoint.geometry.y + .03, 0))
        radius.parameter.expression=str(BOWTIE_ROUND_MM)+' mm'
    # addFillet trims each support line at the next corner.  Keep the ordered
    # closed chain explicitly; Offset2 uses this flow direction to interpret
    # the positive-right sign and must not depend on collection enumeration.
    parent_curves=[]
    for i, line in enumerate(model_lines):
        parent_curves.extend((line, fillet_arcs[(i+1) % len(fillet_arcs)]))
    if not offset:
        return _finish_sketch(sketch)
    value=core.ValueInput.createByString
    sign=step.get('offset_sign','1')
    expression=sign+' * key_clearance'
    offset_input=sketch.geometricConstraints.createOffsetInput(parent_curves, value(expression))
    offset_constraint=sketch.geometricConstraints.addOffset2(offset_input)
    for curve in parent_curves:
        curve.isConstruction=True
    offset_constraint.dimension.parameter.expression=expression
    return _finish_sketch(sketch)


def _polygon_sketch(sketch, axes, design, core, step, offset=False, finish=True):
    points=[_dimension_point(sketch, axes, design, core, step, i+1, pair)
            for i, pair in enumerate(step['profile'])]
    lines=[sketch.sketchCurves.sketchLines.addByTwoPoints(points[i], points[(i+1)%len(points)])
           for i in range(len(points))]
    if offset:
        value=core.ValueInput.createByString
        sign=step.get('offset_sign','1')
        parameter=step.get('offset_parameter','key_clearance')
        expression=sign+' * '+parameter
        offset_input=sketch.geometricConstraints.createOffsetInput(lines, value(expression))
        offset_constraint=sketch.geometricConstraints.addOffset2(offset_input)
        for line in lines:
            line.isConstruction=True
        offset_constraint.dimension.parameter.expression=expression
    return _finish_sketch(sketch) if finish else sketch


def _group_sketch(sketch, axes, design, core, step, kind):
    profiles=step['profile']
    for index, profile in enumerate(profiles):
        child=dict(step, name=step['name']+' {}'.format(index+1),
                   profile=profile, profile_kind=kind)
        if kind == 'rib_offset':
            child['offset_sign'] = step['offset_signs'][index]
            child['offset_parameter'] = step['offset_parameter']
            _polygon_sketch(sketch, axes, design, core, child, True, False)
        else:
            _rectangle_sketch(sketch, axes, design, core, child, False)
    # Disjoint rib tools have one closed profile per source rectangle.  The
    # crossing floor rectangles are different: Fusion exposes the planar
    # arrangement (16 bounded regions for the default layout), and all of
    # those regions must be supplied to one Extrude Join.  Require at least
    # one enclosed profile per source rectangle without assuming a topology
    # count that can change when the parameter domain changes.
    if kind == 'rectangle':
        return _finish_multi_sketch(sketch, minimum_profiles=len(profiles))
    return _finish_multi_sketch(sketch, expected_profiles=len(profiles))


def polygon_sketch(comp, design, step):
    import adsk.core as core
    value=core.ValueInput.createByString
    plane_input=comp.constructionPlanes.createInput()
    plane_input.setByOffset(comp.xYConstructionPlane, value(step['z']))
    plane=comp.constructionPlanes.add(plane_input)
    plane.name=step['name']+' height'
    plane.isLightBulbOn=False
    sketch=comp.sketches.add(plane)
    sketch.name=step['name']+' profile'
    axes=_coordinate_axes(sketch, core)
    kind=step.get('profile_kind')
    if kind == 'rounded_outline':
        return _rounded_sketch(sketch, axes, design, core, step)
    if kind == 'rectangle':
        return _rectangle_sketch(sketch, axes, design, core, step)
    if kind == 'rib_group':
        return _group_sketch(sketch, axes, design, core, step, 'rib_offset')
    if kind == 'rectangle_group':
        return _group_sketch(sketch, axes, design, core, step, 'rectangle')
    if kind in ('bowtie', 'bowtie_offset'):
        return _rounded_bowtie_sketch(sketch, axes, design, core, step,
                                      kind == 'bowtie_offset')
    return _polygon_sketch(sketch, axes, design, core, step, kind == 'rib_offset')


def _loft_feature(comp, design, step, core, fusion):
    lower=polygon_sketch(comp, design, step)
    upper_step=dict(step, name=step['name']+' upper', profile=step['sections'][0],
                    z='('+step['z']+')+('+step['depth']+')')
    upper=polygon_sketch(comp, design, upper_step)
    inp=comp.features.loftFeatures.createInput(fusion.FeatureOperations.JoinFeatureOperation)
    inp.loftSections.add(lower.profiles.item(0))
    inp.loftSections.add(upper.profiles.item(0))
    feature=comp.features.loftFeatures.add(inp)
    lower.isVisible=False
    upper.isVisible=False
    feature.name=step['name']
    return feature


def _fillet_rib_tools(comp, design, feature, core, name):
    """Fillet all standalone rib tools in one native feature before Combine."""
    height=design.userParameters.itemByName('body_height').value
    edge_set=core.ObjectCollection.create()
    for body_index in range(feature.bodies.count):
        body=feature.bodies.item(body_index)
        for edge in body.edges:
            if edge.length > height*.9:
                edge_set.add(edge)
    if edge_set.count == 0:
        raise RuntimeError(name+': không tìm thấy cạnh đứng để bo gân ngoài.')
    inp=comp.features.filletFeatures.createInput()
    inp.edgeSetInputs.addConstantRadiusEdgeSet(
        edge_set, core.ValueInput.createByString('rib_fillet'), False)
    result=comp.features.filletFeatures.add(inp)
    result.name=name+' native fillet'
    return result


def build(design, progress):
    import adsk.core as core
    import adsk.fusion as fusion
    comp=design.rootComponent.occurrences.addNewComponent(core.Matrix3D.create()).component
    comp.name='FourCornerBinV4'
    value=core.ValueInput.createByString
    for name,number in DEFAULTS.items():
        design.userParameters.add(name,value(str(number)+' mm'),'mm',COMMENTS[name])
    for name,(expression,unit) in DERIVED.items():
        design.userParameters.add(name,value(expression),unit,'Tự tính; giữ công thức.')
    bodies={}
    for step in geometry_plan(DEFAULTS):
        progress(step['name'])
        if step.get('feature_kind') == 'loft':
            feature=_loft_feature(comp, design, step, core, fusion)
            bodies[step['target']]=feature.bodies.item(0)
            continue
        sketch=polygon_sketch(comp,design,step)
        # A Join extrusion can absorb every touching body in the component.
        # Keep heads as NewBody tools, then Combine only with their named key
        # or pin target; corner Join steps are created before those bodies.
        combine_tool = step['operation'] == 'join' and step['target'] != 'corner'
        if step['operation']=='cut':
            op=fusion.FeatureOperations.CutFeatureOperation
        elif step['operation']=='join' and not step['name'].startswith('Outer rib') and not combine_tool:
            op=fusion.FeatureOperations.JoinFeatureOperation
        else:
            op=fusion.FeatureOperations.NewBodyFeatureOperation
        profile_count=sketch.profiles.count
        if profile_count == 1:
            profile_input=sketch.profiles.item(0)
        else:
            profile_input=_collection(core,
                [sketch.profiles.item(i) for i in range(profile_count)])
        inp=comp.features.extrudeFeatures.createInput(profile_input,op)
        if step['operation']=='cut':
            inp.participantBodies=[bodies[step['target']]]
        inp.setOneSideExtent(fusion.DistanceExtentDefinition.create(value(step['depth'])),fusion.ExtentDirections.PositiveExtentDirection)
        feature=comp.features.extrudeFeatures.add(inp)
        feature.name=step['name']
        sketch.isVisible=False
        if step['operation']=='new':
            bodies[step['target']]=feature.bodies.item(0)
            bodies[step['target']].name=step['target'].title()+' 1'
        elif step.get('profile_kind') == 'rib_group':
            fillet=_fillet_rib_tools(comp, design, feature, core, step['name'])
            combine=comp.features.combineFeatures.createInput(
                bodies[step['target']], _collection(core,
                [fillet.bodies.item(i) for i in range(fillet.bodies.count)]))
            combine.operation=fusion.FeatureOperations.JoinFeatureOperation
            combine.isKeepToolBodies=False
            joined=comp.features.combineFeatures.add(combine)
            joined.name=step['name']+' join'
            bodies[step['target']]=joined.bodies.item(0)
        elif combine_tool:
            combine=comp.features.combineFeatures.createInput(
                bodies[step['target']], _collection(core, [feature.bodies.item(0)]))
            combine.operation=fusion.FeatureOperations.JoinFeatureOperation
            combine.isKeepToolBodies=False
            joined=comp.features.combineFeatures.add(combine)
            joined.name=step['name']+' join'
            bodies[step['target']]=joined.bodies.item(0)
        elif step['operation']=='join':
            bodies[step['target']]=feature.bodies.item(0)
        else:
            bodies[step['target']]=feature.bodies.item(0)
    progress('Fourfold assembly')
    inp=comp.features.circularPatternFeatures.createInput(_collection(core,list(bodies.values())),comp.zConstructionAxis)
    inp.quantity=value('4')
    inp.totalAngle=value('360 deg')
    inp.isSymmetric=False
    comp.features.circularPatternFeatures.add(inp).name='4 corners + 4 keys + 4 pins'
    return comp


def check_model(design):
    import adsk.fusion as fusion
    if not design.computeAll():
        raise RuntimeError('computeAll thất bại.')
    p={name:design.userParameters.itemByName(name).value*10 for name in DEFAULTS}
    expected_layout=layout(p)
    expected=expected_layout['assembled_bounds_mm']
    comp=design.rootComponent.occurrences.item(0).component
    for i in range(design.timeline.count):
        entity=design.timeline.item(i).entity
        if hasattr(entity,'healthState') and entity.healthState!=fusion.FeatureHealthStates.HealthyFeatureHealthState:
            raise RuntimeError(entity.name+': '+entity.errorOrWarningMessage)
    for sketch in comp.sketches:
        if not sketch.isFullyConstrained:
            raise RuntimeError('Sketch chưa đủ ràng buộc: '+sketch.name)
    if comp.bRepBodies.count!=12 or any(not b.isSolid for b in comp.bRepBodies):
        raise RuntimeError('Cần đúng 12 solid bodies.')
    boxes=[body.preciseBoundingBox for body in comp.bRepBodies]
    expected_parts=sorted(tuple(sorted(round(v,3) for v in size)) for size in expected_layout['part_bounds_mm'] for _ in range(4))
    actual_parts=sorted(tuple(sorted(round(10*(getattr(b.maxPoint,axis)-getattr(b.minPoint,axis)),3) for axis in ('x','y','z'))) for b in boxes)
    if actual_parts!=expected_parts:
        raise RuntimeError('Sai kích thước từng part: '+str(actual_parts))
    actual=[]
    for axis in ('x','y','z'):
        actual.append(10*(max(getattr(b.maxPoint,axis) for b in boxes)-min(getattr(b.minPoint,axis) for b in boxes)))
    if any(abs(a-b)>.05 for a,b in zip(actual,expected)):
        raise RuntimeError('Sai kích thước bao: '+str(actual)+'; cần '+str(expected))
    return actual


def verify_variants(design):
    params=design.userParameters
    original={name:params.itemByName(name).expression for name in DEFAULTS}
    try:
        for changes in ({'body_size':400,'body_height':220},{'wall':4,'floor_thickness':5},
                        {'rail_projection':18,'key_clearance':.3,'pin_interference':0}):
            for name,expr in original.items():
                params.itemByName(name).expression=expr
            for name,number in changes.items():
                params.itemByName(name).expression=str(number)+' mm'
            check_model(design)
    finally:
        for name,expr in original.items():
            params.itemByName(name).expression=expr
        check_model(design)


def run(context):
    import adsk.core as core
    import adsk.fusion as fusion
    app=core.Application.get()
    ui=app.userInterface
    dialog=ui.createProgressDialog()
    stage='Validate parameters'
    def progress(name):
        nonlocal stage
        stage=name
        dialog.message=name
        dialog.progressValue+=1
        __import__('adsk').doEvents()
    try:
        layout(DEFAULTS)
        app.documents.add(core.DocumentTypes.FusionDesignDocumentType)
        design=fusion.Design.cast(app.activeProduct)
        design.designType=fusion.DesignTypes.ParametricDesignType
        dialog.show('Thùng rác V4','Dựng native features',0,40,0)
        dialog.isCancelButtonShown=False
        build(design,progress)
        progress('Check geometry')
        bounds=check_model(design)
        if VERIFY_VARIANTS:
            progress('Verify variants and restore')
            verify_variants(design)
        app.activeViewport.fit()
        ui.messageBox('Đã dựng 12 solid V4. Kích thước bao mm: '+str(bounds)+'\nChỉnh Modify > Change Parameters.')
    except Exception:
        ui.messageBox('Lỗi tại '+stage+'\n'+traceback.format_exc())
    finally:
        dialog.hide()
