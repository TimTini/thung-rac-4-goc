// Prototype: four rotationally identical L-shaped corners, M4 lap joints.
// Units: mm. Hardware is not included in printable geometry.

/* [View] */
view = "assembled"; // [assembled,exploded,corner,base,coupon]
explode_distance = 32;

/* [Body] */
// Square footprint permits four identical rotated corners.
body_size = 360;
body_height = 240;
wall = 3.2;
floor_thickness = 4;
corner_radius = 18;
rim_height = 12;
rim_extra = 4;

/* [Joints] */
lap_length = 20;
joint_thickness = 8;
// Clearance between mating half-thickness faces, not per side.
fit_clearance = 0.4;
seam_gap = 0.4;
bolt_diameter = 4.5;
joint_end_margin = 30;

/* [Base] */
base_span = 160;
base_width = 64;
base_thickness = 6;

$fn = 48;
eps = 0.02;
half = body_size / 2;
lap_half = joint_thickness / 2;
bolt_z = [joint_end_margin, body_height / 2,
          body_height - joint_end_margin];
base_holes = [[20,20], [60,20], [20,60]];

assert(body_size > 2 * (lap_length + 40), "Body too small for joints");
assert(body_height > 2 * joint_end_margin + 20, "Height too small");
assert(corner_radius > wall && corner_radius < half / 2);
assert(joint_thickness >= 2 * wall && fit_clearance > 0);
assert(lap_half > fit_clearance + 2, "Lap tongue too thin");
assert((lap_length - bolt_diameter)/2 >= 6,
       "Need at least 6 mm material from bore edge to lap end");
assert(seam_gap > 0 && seam_gap < fit_clearance + 0.5);
assert(floor_thickness >= 3 && wall >= 2);
assert(base_span >= 150 && base_width >= 55 && body_size > base_span + 60);
assert(view == "assembled" || view == "exploded" || view == "corner"
       || view == "base" || view == "coupon", "Unknown view");

module rounded_square(size, radius) {
    offset(r = radius)
        square([size - 2 * radius, size - 2 * radius], center = true);
}

module shell() {
    difference() {
        union() {
            linear_extrude(body_height)
                rounded_square(body_size, corner_radius);
            translate([0, 0, body_height - rim_height])
                linear_extrude(rim_height)
                    rounded_square(body_size + 2 * rim_extra,
                                   corner_radius + rim_extra);
        }
        translate([0, 0, floor_thickness])
            linear_extrude(body_height)
                rounded_square(body_size - 2 * wall, corner_radius - wall);
    }
}

// Reinforcement thickens gradually into the wall over the last 10 mm.
module seam_reinforcement() {
    linear_extrude(body_height)
        polygon([[seam_gap/2, half-joint_thickness],
                 [lap_length+4, half-joint_thickness],
                 [lap_length+14, half-wall],
                 [lap_length+14, half], [seam_gap/2, half]]);
}

module floor_bores() {
    for (p = base_holes)
        translate([p[0], p[1], -eps])
            cylinder(h = floor_thickness + 2*eps,
                     d = bolt_diameter);
}

module corner() {
    difference() {
        union() {
            intersection() {
                shell();
                translate([seam_gap/2, seam_gap/2, -eps])
                    cube([half+rim_extra, half+rim_extra, body_height+2*eps]);
            }
            seam_reinforcement();
            mirror([1,-1,0]) seam_reinforcement();
            // Tongue projects across the X seam; it engages the next corner.
            translate([-lap_length, half-joint_thickness, 0])
                cube([lap_length+seam_gap/2+1,
                      lap_half-fit_clearance/2,
                      body_height]);
        }
        // Receiving rebate: counterpart tongue enters after rotation.
        translate([half-joint_thickness-eps, -eps, -eps])
            cube([lap_half+fit_clearance/2+eps,
                  lap_length+fit_clearance,
                  body_height+2*eps]);
        for (z = bolt_z) {
            // Tongue bolt axis is normal to the front/back wall.
            translate([-lap_length/2, half-joint_thickness-1, z])
                rotate([-90,0,0])
                    cylinder(h = joint_thickness+rim_extra+2,
                             d = bolt_diameter);
            // Receiving flange bolt axis is normal to the side wall.
            translate([half-joint_thickness-1, lap_length/2, z])
                rotate([0,90,0])
                    cylinder(h = joint_thickness+rim_extra+2,
                             d = bolt_diameter);
        }
        floor_bores();
    }
}

module base_brace() {
    difference() {
        union() {
            linear_extrude(base_thickness)
                rounded_square(base_width, 6);
            translate([-base_span/2, -base_width/2, 0])
                cube([base_span, base_width, base_thickness]);
            translate([-base_width/2, -base_span/2, 0])
                cube([base_width, base_span, base_thickness]);
        }
        for (a = [0:90:270]) rotate([0,0,a])
            for (p = base_holes)
                translate([p[0],p[1],-eps])
                    cylinder(h = base_thickness+2*eps, d = bolt_diameter);
    }
}

colors = [[0.20,0.62,0.65], [0.93,0.63,0.25],
          [0.35,0.55,0.78], [0.75,0.43,0.53]];

if (view == "assembled" || view == "exploded") {
    for (i = [0:3])
        color(colors[i]) rotate([0,0,90*i])
            translate(view == "exploded" ? [explode_distance,explode_distance,0]
                                         : [0,0,0]) corner();
    color([0.35,0.35,0.38])
        translate([0,0,view == "exploded" ? 40 : floor_thickness])
            base_brace();
} else if (view == "corner") {
    // Flat floor on bed; four identical copies, rotated during assembly.
    translate([lap_length,0,0]) corner();
} else if (view == "base") {
    translate([base_span/2,base_span/2,0]) base_brace();
} else if (view == "coupon") {
    // Two mating seam segments, shortened vertically for fit testing.
    translate([lap_length+8,-(half-joint_thickness-2),-(bolt_z[0]-15)])
    intersection() {
        union() { corner(); rotate([0,0,90]) corner(); }
        translate([-lap_length-8,half-joint_thickness-2,bolt_z[0]-15])
            cube([2*lap_length+16,joint_thickness+rim_extra+4,30]);
    }
}
