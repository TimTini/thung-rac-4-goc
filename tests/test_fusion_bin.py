"""Source-derived geometry checks; no Autodesk import required."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bin_fusion', ROOT / 'fusion/ThungRac4Goc/ThungRac4Goc.py')
bin_model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bin_model)

class GeometryTest(unittest.TestCase):
    def plan(self, **changes):
        return bin_model.geometry_plan(dict(bin_model.DEFAULTS, **changes))

    def test_seed_floor_uses_seam_gap_and_outer_corner(self):
        plan = self.plan()
        floor = bin_model.evaluate_step(plan[0], bin_model.DEFAULTS)
        points = floor['profile']['points']
        self.assertEqual(points[0], (0.2, 0.2))
        self.assertEqual(max(p[0] for p in points), 180)
        self.assertEqual(max(p[1] for p in points), 180)
        self.assertNotIn((180, 180), points)
        self.assertEqual(floor['depth'], 4)

    def test_rounded_outlines_are_analytic_profiles(self):
        plan = self.plan()
        floor = next(step for step in plan if step['name'] == 'Corner floor')
        self.assertEqual(floor['profile_kind'], 'rounded_outline')
        self.assertEqual(len(floor['profile']['arcs']), 1)
        self.assertEqual(len(floor['profile']['arcs'][0]), 4)
        self.assertEqual(floor['profile']['arcs'][0][3], 'corner_radius + (0 mm)')
        self.assertLess(len(floor['profile']['points']), 8)
        self.assertNotIn('12 chords', bin_model.quarter_outline.__doc__ or '')
        wall = bin_model.quarter_outline(wall=True)
        self.assertEqual([arc[3] for arc in wall['arcs']],
                         ['corner_radius + (0 mm)', 'corner_radius-wall'])
        rim = bin_model.quarter_outline('4 mm', wall=True)
        self.assertEqual(rim['arcs'][0][3], 'corner_radius + (4 mm)')

    def test_rounded_sketch_applies_driving_radial_dimensions(self):
        """Corner floor failed fully-constrained without arc radius dims."""
        from types import SimpleNamespace as NS
        from unittest.mock import patch
        radials = []
        def add_point(coords):
            return NS(geometry=NS(x=coords[0], y=coords[1]), geometricConstraints=[],
                      isFixed=False, isReference=False, isFullyConstrained=False)
        def add_arc(center, start, end, normal):
            return NS(centerSketchPoint=NS(geometry=NS(x=1, y=1)))
        def add_radial(arc, text, isDriving=True):
            result = NS(parameter=NS(expression=''))
            radials.append((arc, text, isDriving, result))
            return result
        sketch = NS(sketchPoints=NS(add=add_point), originPoint=object(),
                    sketchDimensions=NS(
                        addOffsetDimension=lambda *args: NS(parameter=NS(expression='')),
                        addRadialDimension=add_radial),
                    sketchCurves=NS(sketchLines=NS(addByTwoPoints=lambda *a: NS()),
                                    sketchArcs=NS(addByCenterStartEnd=add_arc)),
                    isFullyConstrained=True, profiles=NS(count=1))
        design = NS(unitsManager=NS(evaluateExpression=lambda expr, unit: 1))
        core = NS(Point3D=NS(create=lambda *args: args),
                  Vector3D=NS(create=lambda *args: args))
        step = next(s for s in bin_model.geometry_plan(bin_model.DEFAULTS)
                    if s['name'] == 'Corner floor')
        bin_model._rounded_sketch(sketch, [NS(), NS()], design, core, step)
        self.assertEqual(len(radials), 1)
        self.assertEqual(radials[0][3].parameter.expression, 'corner_radius + (0 mm)')
        source = (ROOT / 'fusion/ThungRac4Goc/ThungRac4Goc.py').read_text(encoding='utf-8')
        self.assertIn('addRadialDimension', source)
        self.assertIn('radius_dim.parameter.expression', source)

    def test_rectangle_sketch_drives_every_corner(self):
        """Floor ribs stayed free when only the diagonal was locked.

        Offline mocks hardcode isFullyConstrained=True, so assert the real
        DOF strategy: every corner gets axis offsets (8 for a rectangle away
        from the origin), and four closing lines — not one-anchor + size dims.
        """
        from types import SimpleNamespace as NS
        points, offsets, lines = [], [], []
        def add_point(coords):
            point = NS(geometry=NS(x=coords[0], y=coords[1]), geometricConstraints=[],
                       isFixed=False, isReference=False, isFullyConstrained=False)
            points.append(point)
            return point
        def add_offset(axis, point, text, isDriving=True):
            result = NS(parameter=NS(expression=''))
            offsets.append((axis, point, result))
            return result
        def add_line(a, b):
            lines.append((a, b))
            return NS()
        sketch = NS(sketchPoints=NS(add=add_point), originPoint=object(),
                    sketchDimensions=NS(addOffsetDimension=add_offset),
                    sketchCurves=NS(sketchLines=NS(addByTwoPoints=add_line)),
                    isFullyConstrained=True, profiles=NS(count=1))
        design = NS(unitsManager=NS(evaluateExpression=lambda expr, unit: 2))
        core = NS(Point3D=NS(create=lambda *args: args))
        floor = next(s for s in bin_model.geometry_plan(bin_model.DEFAULTS)
                     if s['name'] == 'Floor ribs')
        child = dict(floor, name='Floor ribs 1', profile=floor['profile'][0],
                     profile_kind='rectangle')
        # Deliberately leave isFullyConstrained True on the mock: the prior
        # false-positive test trusted that flag. Structural counts must still
        # prove all four corners are driven.
        bin_model._rectangle_sketch(sketch, [NS(), NS()], design, core, child)
        self.assertEqual(len(points), 4)
        self.assertEqual(len(offsets), 8)
        self.assertEqual(len(lines), 4)
        self.assertEqual({id(point) for _, point, _ in offsets},
                         {id(point) for point in points})
        for i in range(4):
            self.assertIs(lines[i][0], points[i])
            self.assertIs(lines[i][1], points[(i + 1) % 4])
        source = (ROOT / 'fusion/ThungRac4Goc/ThungRac4Goc.py').read_text(encoding='utf-8')
        rect_fn = source[source.index('def _rectangle_sketch'):
                         source.index('def _rounded_bowtie_sketch')]
        # Ignore the docstring (it may name the rejected API); assert the body.
        doc_start = rect_fn.index('"""')
        body = rect_fn[rect_fn.index('"""', doc_start + 3) + 3:]
        self.assertIn('_dimension_point', body)
        self.assertNotIn('addTwoPointRectangle', body)
        self.assertNotIn('addDistanceDimension', body)

    def test_floor_ribs_group_drives_all_source_corners(self):
        """Multi-rectangle Floor ribs must constrain 4 corners × 4 rectangles."""
        from types import SimpleNamespace as NS
        offsets, lines = [], []
        def add_point(coords):
            return NS(geometry=NS(x=coords[0], y=coords[1]), geometricConstraints=[],
                      isFixed=False, isReference=False, isFullyConstrained=False)
        def add_offset(axis, point, text, isDriving=True):
            result = NS(parameter=NS(expression=''))
            offsets.append(result)
            return result
        sketch = NS(sketchPoints=NS(add=add_point), originPoint=object(),
                    sketchDimensions=NS(addOffsetDimension=add_offset),
                    sketchCurves=NS(sketchLines=NS(
                        addByTwoPoints=lambda a, b: lines.append((a, b)) or NS())),
                    isFullyConstrained=True, profiles=NS(count=16))
        design = NS(unitsManager=NS(evaluateExpression=lambda expr, unit: 2))
        core = NS(Point3D=NS(create=lambda *args: args))
        floor = next(s for s in bin_model.geometry_plan(bin_model.DEFAULTS)
                     if s['name'] == 'Floor ribs')
        bin_model._group_sketch(sketch, [NS(), NS()], design, core, floor, 'rectangle')
        self.assertEqual(len(floor['profile']), 4)
        self.assertEqual(len(offsets), 4 * 4 * 2)
        self.assertEqual(len(lines), 4 * 4)
    def test_wall_profile_samples_as_a_closed_shell_quarter(self):
        import math
        profile = bin_model._evaluate_profile(bin_model.quarter_outline(wall=True),
                                              bin_model.DEFAULTS)
        points = profile['points']
        center = profile['center']
        arcs = {(item[0], item[1]): item[2] for item in profile['arcs']}
        sampled = []
        for i, start in enumerate(points):
            end = points[(i + 1) % len(points)]
            direction = arcs.get((i, (i + 1) % len(points)))
            if direction is None:
                sampled.append(start)
                continue
            start_angle = math.atan2(start[1] - center[1], start[0] - center[0])
            end_angle = math.atan2(end[1] - center[1], end[0] - center[0])
            if direction > 0:
                while end_angle <= start_angle:
                    end_angle += 2 * math.pi
            else:
                while end_angle >= start_angle:
                    end_angle -= 2 * math.pi
            radius = math.hypot(start[0] - center[0], start[1] - center[1])
            sampled.extend((center[0] + radius * math.cos(start_angle +
                             (end_angle - start_angle) * j / 24),
                            center[1] + radius * math.sin(start_angle +
                             (end_angle - start_angle) * j / 24))
                           for j in range(24))
        area = abs(sum(sampled[i][0] * sampled[(i + 1) % len(sampled)][1] -
                      sampled[(i + 1) % len(sampled)][0] * sampled[i][1]
                      for i in range(len(sampled))) / 2)
        self.assertAlmostEqual(min(x for x, y in sampled), .2, places=6)
        self.assertAlmostEqual(max(x for x, y in sampled), 180, places=6)
        self.assertAlmostEqual(min(y for x, y in sampled), .2, places=6)
        self.assertAlmostEqual(max(y for x, y in sampled), 180, places=6)
        self.assertAlmostEqual(area, 1117.9, delta=.5)

    def test_key_and_pin_are_centered_and_correct_v4_sizes(self):
        plan = self.plan()
        key = next(s for s in plan if s['name'] == 'Key stem')
        evaluated = bin_model.evaluate_step(key, bin_model.DEFAULTS)
        self.assertEqual(evaluated['profile'], [(-16,184),(-6,186),(6,186),(16,184),(16,192),(6,190),(-6,190),(-16,192)])
        pin = next(s for s in plan if s['name'] == 'Pin wedge')
        points = bin_model.evaluate_step(pin, bin_model.DEFAULTS)['profile']
        self.assertEqual([(round(x,6),round(y,6)) for x,y in points], [(-2.35,196),(-2,182),(2,182),(2.35,196)])

    def test_bores_share_rail_key_pin_coordinates(self):
        steps = [bin_model.evaluate_step(s, bin_model.DEFAULTS) for s in self.plan()]
        bores = [s for s in steps if 'pin bore' in s['name'].lower()]
        self.assertEqual(len(bores), 3)
        first = bores[0]
        self.assertEqual(first['profile'], [(-2.3,182), (2.3,182), (2.3,196.02),(-2.3,196.02)])
        self.assertEqual((first['z'],first['depth']), (225.75,4.5))
        self.assertEqual(bores[2]['profile'], first['profile'])

    def test_slot_reuses_rounded_parent_and_reverses_offset_for_mirror(self):
        key = next(s for s in self.plan() if s['name']=='Key stem')
        y_slot = next(s for s in self.plan() if s['name']=='Rail Y dovetail slot')
        x_slot = next(s for s in self.plan() if s['name']=='Rail X dovetail slot')
        self.assertEqual(bin_model.evaluate_step(key, bin_model.DEFAULTS)['profile'],
                         bin_model.evaluate_step(y_slot, bin_model.DEFAULTS)['profile'])
        self.assertEqual(y_slot['offset_sign'], '1')
        self.assertEqual(x_slot['offset_sign'], '-1')
        self.assertEqual(bin_model.BOWTIE_ROUND_MM, .6)

    def test_native_slot_uses_driving_fusion_offset(self):
        source = (ROOT / 'fusion/ThungRac4Goc/ThungRac4Goc.py').read_text(encoding='utf-8')
        self.assertIn('createOffsetInput', source)
        self.assertIn('addOffset2', source)
        self.assertIn("'key_clearance'", source)

    def test_ribs_are_outside_floor_rebate_and_lap_exist(self):
        steps = [bin_model.evaluate_step(s,bin_model.DEFAULTS) for s in self.plan()]
        ribs = next(s for s in steps if s['name']=='Outer ribs')
        self.assertEqual(len(ribs['profile']), 4)
        self.assertGreater(max(y for profile in ribs['profile'] for x,y in profile),180)
        self.assertTrue(any(s['name']=='Bottom rebate' and s['operation']=='cut' for s in steps))
        self.assertTrue(any(s['name']=='Bottom tongue' and min(x for x,y in s['profile'])==-8 for s in steps))

    def test_floor_rib_source_rectangles_have_one_planar_union(self):
        """The four crossing source rectangles cover one exact union.

        Fusion may expose the bounded planar arrangement as 16 profiles.  The
        builder therefore selects every arrangement profile for one Join
        extrusion; this offline check proves the source coverage and catches a
        missing or duplicated rectangle without assuming Fusion's profile
        enumeration order.
        """
        floor = next(s for s in self.plan() if s['name'] == 'Floor ribs')
        rectangles = [
            [(x, y) for x, y in profile]
            for profile in bin_model._evaluate_profile(floor['profile'], bin_model.DEFAULTS)
        ]
        self.assertEqual(len(rectangles), 4)
        xs = sorted({x for rect in rectangles for x, _ in rect})
        ys = sorted({y for rect in rectangles for _, y in rect})

        def covered(x, y):
            return any(min(px for px, _ in rect) < x < max(px for px, _ in rect) and
                       min(py for _, py in rect) < y < max(py for _, py in rect)
                       for rect in rectangles)

        union_area = sum((x2 - x1) * (y2 - y1)
                         for x1, x2 in zip(xs, xs[1:])
                         for y1, y2 in zip(ys, ys[1:])
                         if covered((x1 + x2) / 2, (y1 + y2) / 2))
        source_area = sum((max(x for x, _ in rect) - min(x for x, _ in rect)) *
                          (max(y for _, y in rect) - min(y for _, y in rect))
                          for rect in rectangles)
        rib_width = bin_model.DEFAULTS['floor_rib_width']
        self.assertAlmostEqual(union_area, source_area - 4 * rib_width ** 2)

    def test_geometry_follows_size_and_clearance(self):
        p=dict(bin_model.DEFAULTS,body_size=400,rail_projection=18,pin_interference=.2)
        steps=[bin_model.evaluate_step(s,p) for s in bin_model.geometry_plan(p)]
        pin=next(s for s in steps if s['name']=='Pin wedge')
        self.assertEqual(pin['profile'][0],(-2.4,218))
        floor=steps[0]
        self.assertEqual(max(x for x,y in floor['profile']['points']),200)

    def test_zero_interference_is_valid_but_invalid_material_is_rejected(self):
        bin_model.layout(dict(bin_model.DEFAULTS,pin_interference=0))
        for change in ({'key_clearance':.05},{'floor_thickness':3},{'pin_interference':.5},{'wall':30}):
            with self.subTest(change=change),self.assertRaises(ValueError):
                bin_model.layout(dict(bin_model.DEFAULTS,**change))

    def test_middle_band_keeps_ramp_then_expanded_straight(self):
        ramp = next(step for step in self.plan() if step['name'] == 'Middle band ramp')
        straight = next(step for step in self.plan() if step['name'] == 'Middle band straight')
        self.assertEqual(ramp['feature_kind'], 'loft')
        self.assertEqual(ramp['depth'], 'band_projection')
        self.assertEqual(len(ramp['sections']), 1)
        self.assertEqual(straight['depth'], 'band_height-band_projection')
        self.assertEqual(straight['profile']['points'], ramp['sections'][0]['points'])

    def test_rectangles_are_marked_for_native_rectangle_constructor(self):
        self.assertTrue(any(step.get('profile_kind') == 'rectangle'
                            for step in self.plan()))

    def test_source_fillet_radius_is_a_linked_parameter(self):
        self.assertIn('rib_fillet', bin_model.DEFAULTS)
        self.assertIn('rib_fillet', bin_model.COMMENTS)
        ribs = next(step for step in self.plan() if step['name']=='Outer ribs')
        self.assertEqual(ribs['profile_kind'], 'rib_group')
        self.assertEqual(ribs['offset_signs'], ['-1','1','-1','1'])
        self.assertEqual(ribs['offset_parameter'], 'rib_fillet')
        source = (ROOT / 'fusion/ThungRac4Goc/ThungRac4Goc.py').read_text(encoding='utf-8')
        self.assertIn('createOffsetInput', source)
        self.assertIn("parameter=step.get('offset_parameter'", source)


class NativeOperationTest(unittest.TestCase):
    def test_offset_builder_uses_associative_model_parameter(self):
        from types import SimpleNamespace as NS
        calls=[]
        class Collection(list):
            def item(self,index): return self[index]
        lines=[]
        def add_point(coords):
            return NS(geometry=NS(x=coords[0],y=coords[1]), geometricConstraints=[],
                      isFixed=False, isReference=False, isFullyConstrained=False)
        def add_line(a,b):
            line=NS(isConstruction=False)
            lines.append(line)
            return line
        def create_offset(curves, value):
            calls.append((curves, value))
            return NS()
        offset=NS(dimension=NS(parameter=NS(expression='')))
        sketch=NS(sketchPoints=NS(add=add_point), originPoint=object(),
                  sketchDimensions=NS(addOffsetDimension=lambda *args: NS(parameter=NS(expression=''))),
                  sketchCurves=NS(sketchLines=NS(addByTwoPoints=add_line)),
                  geometricConstraints=NS(createOffsetInput=create_offset,
                                          addOffset2=lambda inp: offset),
                  isFullyConstrained=True, profiles=NS(count=1))
        axes=[NS() for _ in range(2)]
        design=NS(unitsManager=NS(evaluateExpression=lambda expr, unit: 1))
        core=NS(Point3D=NS(create=lambda *args: args),
                ValueInput=NS(createByString=lambda expr: expr))
        step=next(s for s in bin_model.geometry_plan(bin_model.DEFAULTS)
                  if s.get('profile_kind') == 'bowtie_offset')
        bin_model._polygon_sketch(sketch, axes, design, core, step, offset=True)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(calls[0][0]), 8)
        self.assertEqual(calls[0][1], '1 * key_clearance')
        self.assertTrue(all(line.isConstruction for line in lines))
        self.assertEqual(offset.dimension.parameter.expression, '1 * key_clearance')

    def test_rounded_bowtie_parent_drives_native_offset(self):
        from types import SimpleNamespace as NS
        calls, fillets, parent_lines, model_curves = [], [], [], []
        def add_point(coords):
            return NS(geometry=NS(x=coords[0], y=coords[1]), geometricConstraints=[],
                      isFixed=False, isReference=False, isFullyConstrained=False)
        def add_line(a, b):
            def geometry(value):
                if hasattr(value, 'geometry'):
                    return value.geometry
                return NS(x=value[0], y=value[1])
            line = NS(kind='line', isConstruction=False,
                      startSketchPoint=NS(geometry=geometry(a)),
                      endSketchPoint=NS(geometry=geometry(b)))
            if hasattr(a, 'geometry'):
                parent_lines.append(line)
            else:
                model_curves.append(line)
            return line
        def add_fillet(*args):
            arc = NS(kind='arc', isConstruction=False,
                     centerSketchPoint=NS(geometry=NS(x=0, y=0)))
            fillets.append(args)
            model_curves.append(arc)
            return arc
        def add_collinear(*args):
            return NS()
        def create_offset(curves, value):
            calls.append((curves, value))
            return NS()
        offset = NS(dimension=NS(parameter=NS(expression='')))
        curves = NS(sketchLines=NS(addByTwoPoints=add_line),
                    sketchArcs=NS(addFillet=add_fillet))
        sketch = NS(sketchPoints=NS(add=add_point), originPoint=object(),
                    sketchDimensions=NS(addOffsetDimension=lambda *args:
                                       NS(parameter=NS(expression=''))),
                    sketchCurves=curves,
                    findConnectedCurves=lambda first: (_ for _ in ()).throw(
                        AssertionError('explicit curve order required')),
                    geometricConstraints=NS(addCollinear=add_collinear,
                                            createOffsetInput=create_offset,
                                            addOffset2=lambda inp: offset),
                    isFullyConstrained=True, profiles=NS(count=1))
        sketch.sketchDimensions.addRadialDimension = lambda *args: NS(
            parameter=NS(expression=''))
        design = NS(unitsManager=NS(evaluateExpression=lambda expr, unit: 1))
        core = NS(Point3D=NS(create=lambda *args: args),
                  ValueInput=NS(createByString=lambda expr: expr))
        step = next(s for s in bin_model.geometry_plan(bin_model.DEFAULTS)
                    if s.get('profile_kind') == 'bowtie_offset')
        bin_model._rounded_bowtie_sketch(sketch, [NS(), NS()], design, core, step, True)
        self.assertEqual(len(fillets), 8)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], '1 * key_clearance')
        self.assertEqual(len(calls[0][0]), 16)
        self.assertEqual([curve.kind for curve in calls[0][0]],
                         ['line','arc'] * 8)
        self.assertTrue(all(curve.isConstruction for curve in parent_lines))
        self.assertTrue(all(curve.isConstruction for curve in model_curves))
        self.assertEqual(offset.dimension.parameter.expression, '1 * key_clearance')

    def test_join_ownership_keeps_heads_as_targeted_combine_tools(self):
        from types import SimpleNamespace as NS
        from unittest.mock import patch
        operations=[]
        combines=[]
        current={}
        class Collection(list):
            @property
            def count(self): return len(self)
            def add(self,item): self.append(item)
            def item(self,index): return self[index]
        def extrude_input(profile,operation):
            result=NS(profile=profile,operation=operation)
            result.setOneSideExtent=lambda *args:None
            return result
        class Body:
            name=''
            edges=[NS(length=100)]
        def extrude_add(inp):
            operations.append(inp)
            return NS(name='',bodies=Collection([Body()]))
        def loft_input(operation):
            return NS(operation=operation,loftSections=NS(add=lambda profile: None))
        def loft_add(inp):
            return NS(name='',bodies=Collection([Body()]))
        def fillet_input():
            return NS(edgeSetInputs=NS(addConstantRadiusEdgeSet=lambda *args: True))
        def fillet_add(inp):
            return NS(name='',bodies=Collection([Body()]))
        def combine_input(target, tools):
            return NS(target=target, tools=tools)
        def combine_add(inp):
            combines.append(inp)
            return NS(name='', bodies=Collection([inp.target]))
        class Progress:
            def __call__(self,name):current['name']=name
        pattern=NS(createInput=lambda *args:NS(),add=lambda inp:NS(name=''))
        comp=NS(name='',zConstructionAxis=object(),features=NS(
            extrudeFeatures=NS(createInput=extrude_input,add=extrude_add),
            loftFeatures=NS(createInput=loft_input,add=loft_add),
            filletFeatures=NS(createInput=fillet_input,add=fillet_add),
            combineFeatures=NS(createInput=combine_input,add=combine_add),
            circularPatternFeatures=pattern))
        params=NS(add=lambda *args:None,
                  itemByName=lambda name:NS(value=24) if name == 'body_height' else NS(value=1))
        design=NS(rootComponent=NS(occurrences=NS(addNewComponent=lambda x:NS(component=comp))),
                  userParameters=params)
        core=NS(ValueInput=NS(createByString=str),Matrix3D=NS(create=object),ObjectCollection=NS(create=Collection))
        fusion=NS(FeatureOperations=NS(NewBodyFeatureOperation='new',CutFeatureOperation='cut',JoinFeatureOperation='join'),
                  ExtentDirections=NS(PositiveExtentDirection=1),DistanceExtentDefinition=NS(create=lambda x:x))
        adsk=NS(core=core,fusion=fusion)
        def sketch(*args):
            step = args[2]
            profile_count = {'rib_group': 4, 'rectangle_group': 16}.get(
                step.get('profile_kind'), 1)
            return NS(profiles=Collection([object() for _ in range(profile_count)]),
                      isVisible=True)
        with patch.dict('sys.modules',{'adsk':adsk,'adsk.core':core,'adsk.fusion':fusion}),patch.object(bin_model,'polygon_sketch',sketch):
            bin_model.build(design,Progress())
        plan=bin_model.geometry_plan(bin_model.DEFAULTS)
        extrude_plan=[step for step in plan if step.get('feature_kind') != 'loft']
        self.assertEqual(len(operations),len(extrude_plan))
        for step,inp in zip(extrude_plan,operations):
            expected='new' if (step['name'].startswith('Outer rib') or
                               (step['operation'] == 'join' and step['target'] != 'corner')) else {
                'cut':'cut','join':'join','new':'new'}[step['operation']]
            self.assertEqual(inp.operation, expected, step['name'])
            if step['operation']=='cut': self.assertEqual(len(inp.participantBodies),1)
        floor_index = next(i for i, step in enumerate(extrude_plan)
                           if step['name'] == 'Floor ribs')
        self.assertEqual(operations[floor_index].profile.count, 16)
        self.assertTrue(all(inp.operation in ('new', 'cut', 'join') for inp in operations))
        self.assertEqual(sum(inp.operation == 'join' for inp in operations),
                         sum(s['operation'] == 'join' and s['target'] == 'corner' and
                             not s['name'].startswith('Outer rib')
                             for s in extrude_plan))
        self.assertEqual(len(combines), 3)
        self.assertEqual([len(inp.tools) for inp in combines], [1, 1, 1])
        # The two head combines must target the already-built key/pin body and
        # use the current head as a distinct tool; a broad Join would lose this
        # ownership boundary when the head touches the corner rails.
        self.assertIsNot(combines[1].target, combines[1].tools.item(0))
        self.assertIsNot(combines[2].target, combines[2].tools.item(0))

    def test_all_default_source_values_match_scad(self):
        import re
        source=(ROOT/'thung-rac-4-goc-v4.scad').read_text(encoding='utf-8')
        for name,value in bin_model.DEFAULTS.items():
            match=re.search(r'^'+name+r'\s*=\s*([\d.]+);',source,re.M)
            if name == 'rib_fillet':
                self.assertEqual(value, 1.5)
                continue
            self.assertIsNotNone(match,name)
            self.assertEqual(float(match[1]),value,name)


class ConstraintDiagnosticTest(unittest.TestCase):
    def test_solver_failure_reports_vertex_axis_and_point_state(self):
        from types import SimpleNamespace as NS
        from unittest.mock import patch
        point=NS(geometry=NS(x=.02,y=.02),isFixed=False,isReference=False,
                 isFullyConstrained=False,geometricConstraints=[])
        def fail(*args):
            raise RuntimeError('VCS_SKETCH_OVER_CONSTRAINTS')
        sketch=NS(sketchPoints=NS(add=lambda p:point),originPoint=object(),
                  sketchDimensions=NS(addOffsetDimension=fail),
                  sketchCurves=NS(sketchLines=NS(addByTwoPoints=lambda *args:NS(startSketchPoint=NS(isFixed=False),endSketchPoint=NS(isFixed=False)))))
        plane_input=NS(setByOffset=lambda *a:None)
        comp=NS(xYConstructionPlane=object(),constructionPlanes=NS(
            createInput=lambda:plane_input, add=lambda i:NS()),sketches=NS(add=lambda p:sketch))
        design=NS(unitsManager=NS(evaluateExpression=lambda *a:.02))
        core=NS(ValueInput=NS(createByString=str),Point3D=NS(create=lambda *a:a),
                Vector3D=NS(create=lambda *a:a))
        fusion=NS(DimensionOrientations=NS(HorizontalDimensionOrientation=0,VerticalDimensionOrientation=1))
        adsk=NS(core=core,fusion=fusion)
        step=bin_model.geometry_plan(bin_model.DEFAULTS)[0]
        with patch.dict('sys.modules',{'adsk':adsk,'adsk.core':core,'adsk.fusion':fusion}):
            with self.assertRaisesRegex(RuntimeError,'Corner floor vertex 1 axis X.*fixed=False.*VCS_SKETCH_OVER_CONSTRAINTS'):
                bin_model.polygon_sketch(comp,design,step)


class CoordinateOffsetRegressionTest(unittest.TestCase):
    def test_floor_equal_y_vertices_use_two_independent_axis_offsets(self):
        from types import SimpleNamespace as NS
        from unittest.mock import patch
        axes, offsets, points = [], [], []
        def line(a,b):
            result=NS(a=a,b=b,isConstruction=False,isFixed=False,
                      startSketchPoint=NS(isFixed=False),endSketchPoint=NS(isFixed=False))
            axes.append(result)
            return result
        def add_point(coords):
            result=NS(geometry=NS(x=coords[0],y=coords[1]))
            points.append(result)
            return result
        def offset(axis,point,text,isDriving=True):
            self.assertTrue(axis.isConstruction)
            self.assertTrue(axis.startSketchPoint.isFixed)
            self.assertTrue(axis.endSketchPoint.isFixed)
            self.assertTrue(axis.isFixed)
            self.assertTrue(isDriving)
            result=NS(parameter=NS(expression=''))
            offsets.append((axis,point,result))
            return result
        def add_arc(*args):
            return NS(centerSketchPoint=NS(geometry=NS(x=1,y=1)))
        sketch=NS(sketchPoints=NS(add=add_point),originPoint=object(),
            sketchDimensions=NS(addOffsetDimension=offset,
                                addRadialDimension=lambda *args: NS(parameter=NS(expression=''))),
            sketchCurves=NS(sketchLines=NS(addByTwoPoints=line),
                             sketchArcs=NS(addByCenterStartEnd=add_arc)),
            isFullyConstrained=True,profiles=NS(count=1))
        plane_input=NS(setByOffset=lambda *a:None)
        comp=NS(xYConstructionPlane=object(),constructionPlanes=NS(
            createInput=lambda:plane_input,add=lambda i:NS()),sketches=NS(add=lambda p:sketch))
        p=dict(bin_model.DEFAULTS)
        for name,(expr,unit) in bin_model.DERIVED.items():
            p[name]=eval(expr.replace(' mm',''),{'__builtins__':{}},p)
        design=NS(unitsManager=NS(evaluateExpression=lambda expr,unit:eval(expr.replace(' mm',''),{'__builtins__':{}},p)/10))
        core=NS(ValueInput=NS(createByString=str),Point3D=NS(create=lambda *a:a),
                Vector3D=NS(create=lambda *a:a))
        fusion=NS(DimensionOrientations=NS(HorizontalDimensionOrientation=0,VerticalDimensionOrientation=1))
        adsk=NS(core=core,fusion=fusion)
        step=bin_model.geometry_plan(bin_model.DEFAULTS)[0]
        with patch.dict('sys.modules',{'adsk':adsk,'adsk.core':core,'adsk.fusion':fusion}):
            bin_model.polygon_sketch(comp,design,step)
        self.assertEqual(len(offsets),2*len(step['profile']['points'])+2)
        self.assertIs(offsets[0][0],offsets[2][0])
        self.assertIs(offsets[1][0],offsets[3][0])
        self.assertIsNot(offsets[0][0],offsets[1][0])
        self.assertEqual(offsets[1][2].parameter.expression,'abs(seam_gap / 2)')
        self.assertEqual(offsets[3][2].parameter.expression,'abs(seam_gap / 2)')
        self.assertAlmostEqual(points[0].geometry.y,.02)
        self.assertAlmostEqual(points[1].geometry.y,.02)

if __name__ == '__main__':
    unittest.main()
