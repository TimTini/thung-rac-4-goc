// V7: low male floor rails with a removable sliding cap; FDM cap-down printing.
// Joint principle reference (independent geometry, not copied code):
// https://catchit.pl/blog/modular-3d-printed-case-diy-project/
// Still a prototype; reference does not validate this bin or its load rating.
/* [View] */
view = "assembled"; // [assembled,exploded,corner,key,pin,coupon,coupon_key,floor_key,floor_pin,floor_coupon,floor_coupon_key,floor_detail,floor_joint_section,floor_joint_exploded]
explode_distance = 32;
/* [Body] */
body_size = 360;
body_height = 240;
wall = 3.2;
floor_thickness = 4;
corner_radius = 18;
/* [Reinforcement] */
rib_projection = 10;
rib_thickness = 3;
band_projection = 8;
band_height = 24;
floor_rib_height = 8;
floor_rib_width = 4;
floor_fillet = 3;
gusset_run = 12;
gusset_height = 16;
/* [Floor joints] */
floor_rail_start = 46;
floor_rail_length = 80;
floor_rail_clearance = 0.25;
floor_pin_interference = 0.05;
floor_coupon_length = 24;
/* [Printed joints] */
seam_gap = 0.4;
// Slot clearance measured normal to each key face, per side.
key_clearance = 0.25;
rail_width = 48;
rail_projection = 16;
key_stop = 8;
floor_rib_start = 11;
// Positive value is intentional wedge interference at the entry end.
pin_interference = 0.1;

$fn=48;
eps=0.02;
half=body_size/2;
key_length=body_height-key_stop;
pin_z=body_height-12;
rail_y=half+rail_projection/2;
coupon_height=42;
assert(body_size>=320 && body_height>=120);
assert(wall>=3 && floor_thickness>=4);
assert(corner_radius>wall && corner_radius<half/2);
assert(key_clearance>=0.15 && key_clearance<=0.5);
assert(seam_gap>0 && seam_gap<1);
assert(rail_width>=44 && rail_projection>=16);
assert(floor_rib_start>=11 && floor_rib_start<half/3,
       "Floor ribs must clear the 21 mm sliding cap");
assert(pin_interference>=0 && pin_interference<=0.2);
assert(floor_fillet>0 && floor_fillet<corner_radius-wall);
assert(gusset_run>floor_fillet && gusset_height>floor_rib_height);
assert(gusset_run<half/3-floor_rib_start && gusset_height<body_height-16);
assert(floor_rail_length>=60 && floor_rail_length<=100);
assert(floor_rail_start>(floor_rail_length+9)/2+1,
       "Central loading gap too short with opposite rail seated");
assert(floor_rail_start+floor_rail_length<half-wall-gusset_run-4);
assert(floor_rail_clearance>=0.15 && floor_rail_clearance<=0.4);
assert(floor_pin_interference>=0 && floor_pin_interference<=0.1);
assert(floor_coupon_length>=16 && floor_coupon_length<=floor_rail_length);
assert(floor_rail_start<half/3 && floor_rail_start+floor_rail_length>2*half/3,
       "Floor rail must span both floor rib positions");
assert(view=="assembled" || view=="exploded" || view=="corner" || view=="key"
       || view=="pin" || view=="coupon" || view=="coupon_key" || view=="floor_key"
       || view=="floor_pin" || view=="floor_coupon" || view=="floor_coupon_key"
       || view=="floor_detail" || view=="floor_joint_section" || view=="floor_joint_exploded"
       || view=="floor_key_sweep" || view=="floor_pin_sweep", "Unknown view");

module rounded_square(size,radius) {
    offset(r=radius) square(size-2*radius,center=true);
}

// Wide ends and narrow middle lock both halves against pulling apart.
module bowtie() {
    offset(r=0.6) offset(delta=-0.6)
    polygon([[-16,-4],[-6,-2],[6,-2],[16,-4],
             [16,4],[6,2],[-6,2],[-16,4]]);
}

module shell() {
    difference() {
        union() {
            linear_extrude(body_height) rounded_square(body_size,corner_radius);
            hull() {
                translate([0,0,body_height-12]) linear_extrude(eps)
                    rounded_square(body_size,corner_radius);
                translate([0,0,body_height-8]) linear_extrude(8)
                    rounded_square(body_size+8,corner_radius+4);
            }
            hull() {
                translate([0,0,body_height/2-band_height/2]) linear_extrude(eps)
                    rounded_square(body_size,corner_radius);
                translate([0,0,body_height/2-band_height/2+band_projection])
                    linear_extrude(band_height-band_projection)
                        rounded_square(body_size+2*band_projection,
                                       corner_radius+band_projection);
            }
        }
        // Eight circular-profile segments form the internal floor cove.
        for(i=[0:7]) hull() {
            for(j=[i:i+1]) let(a=90*j/8,
                inset=floor_fillet*(1-sin(a)),
                z=floor_thickness+floor_fillet*(1-cos(a)))
                translate([0,0,z]) linear_extrude(eps)
                    rounded_square(body_size-2*wall-2*inset,
                                   corner_radius-wall-inset);
        }
        translate([0,0,floor_thickness+floor_fillet]) linear_extrude(body_height+1)
            rounded_square(body_size-2*wall,corner_radius-wall);
    }
}

module face_ribs() {
    for(x=[half*0.34,half*0.66]) translate([x,half,0])
        linear_extrude(body_height) offset(r=1.5)
            polygon([[-rib_thickness/2-2,-wall/2],
                     [rib_thickness/2+2,-wall/2],
                     [rib_thickness/2,rib_projection-1.5],
                     [-rib_thickness/2,rib_projection-1.5]]);
}

module floor_ribs() {
    for(p=[half/3,2*half/3]) {
        translate([floor_rib_start,p-floor_rib_width/2,floor_thickness-eps])
            cube([half-wall-floor_rib_start,floor_rib_width,floor_rib_height+eps]);
        translate([p-floor_rib_width/2,floor_rib_start,floor_thickness-eps])
            cube([floor_rib_width,half-wall-floor_rib_start,floor_rib_height+eps]);
    }
}

module floor_gussets() {
    for(p=[half/3,2*half/3])
        translate([p-floor_rib_width/2,half-wall+eps,floor_thickness-eps])
            rotate([90,0,90]) linear_extrude(floor_rib_width)
                polygon([[-gusset_run,0],[0,0],[0,gusset_height+eps]]);
}

// A low trapezoid expands 2 mm per side over 3 mm height (<45 degree overhang).
module floor_male_profile() {
    polygon([[-1,0],[1,0],[3,3],[-3,3]]);
}
module floor_rail(length=floor_rail_length) {
    translate([5,floor_rail_start+length,floor_thickness-eps])
        rotate([90,0,0]) linear_extrude(length) floor_male_profile();
}
module floor_pin_bore() {
    translate([5,floor_rail_start+8,floor_thickness+2])
        cylinder(h=3+eps,d=3.1);
}

module rail() {
    translate([seam_gap/2,half-wall/2,0])
        linear_extrude(body_height)
            polygon([[0,0],[rail_width/2-seam_gap/2,0],
                     [rail_width/2-seam_gap/2-3,rail_projection+wall/2],
                     [0,rail_projection+wall/2]]);
}

module slot() {
    translate([0,rail_y,key_stop]) linear_extrude(body_height-key_stop+eps)
        offset(delta=key_clearance) bowtie();
}

module pin_bore(z) {
    translate([-2.3,half+2,z-2.25])
        cube([4.6,rail_projection-2+eps,4.5]);
}

module corner(retaining_z=pin_z, floor_length=floor_rail_length) {
    difference() {
        union() {
            intersection() {
                shell();
                translate([seam_gap/2,seam_gap/2,-eps])
                    cube([half+band_projection,half+band_projection,body_height+2*eps]);
            }
            face_ribs(); mirror([1,-1,0]) face_ribs();
            rail(); mirror([1,-1,0]) rail();
            floor_ribs();
            floor_gussets(); mirror([1,-1,0]) floor_gussets();
            floor_rail(floor_length); mirror([1,-1,0]) floor_rail(floor_length);
        }
        slot(); mirror([1,-1,0]) slot();
        pin_bore(retaining_z); mirror([1,-1,0]) pin_bore(retaining_z);
        floor_pin_bore();
    }
}

module key(length=key_length, bore_z=pin_z-key_stop) {
    difference() {
        union() {
            linear_extrude(length) bowtie();
            translate([-16,-6,length]) cube([32,12,4]);
        }
        translate([-2.3,2-rail_projection/2,bore_z-2.25])
            cube([4.6,rail_projection-2+eps,4.5]);
    }
}

module pin() {
    // Short radial wedge points inward (-Y); outside head remains accessible.
    linear_extrude(4) union() {
        polygon([[-(4.6+pin_interference)/2,0],[-2,-14],
                 [2,-14],[(4.6+pin_interference)/2,0]]);
        translate([-4,-eps]) square([8,3+eps]);
    }
}

// Local rail cap, Y=0..length; channels are open at the leading end and underside.
module floor_key_core(length) {
    difference() {
        translate([-10.5,0,floor_thickness+floor_rail_clearance])
            cube([21,length,5-floor_rail_clearance]);
        for(x=[-5,5])
            translate([x,length+eps,floor_thickness-eps]) rotate([90,0,0])
                linear_extrude(length+2*eps)
                    offset(delta=floor_rail_clearance) floor_male_profile();
    }
}
module floor_key(length=floor_rail_length) {
    difference() {
        union() {
            floor_key_core(length);
            translate([-10.5,-3,floor_thickness+floor_rail_clearance])
                cube([21,3,5-floor_rail_clearance]);
        }
        translate([5,8,floor_thickness+2]) cylinder(h=3+eps,d=3.1);
    }
}
module print_floor_key(length=floor_rail_length) {
    translate([10.5,length,floor_thickness+5]) rotate([180,0,0]) floor_key(length);
}
module floor_key_at_seam() {
    translate([0,floor_rail_start,0]) floor_key();
}
module floor_pin() {
    union() {
        cylinder(h=3,d1=2.8,d2=3.1+floor_pin_interference);
        translate([0,0,3]) cylinder(h=1.2,d=6);
    }
}
module floor_pin_at_seam() {
    translate([5,floor_rail_start+8,floor_thickness+2]) floor_pin();
}
module floor_key_sweep() {
    travel=floor_rail_length+3;
    translate([0,floor_rail_start-travel,0]) union() {
        floor_key_core(floor_rail_length+travel);
        translate([-10.5,-3,floor_thickness+floor_rail_clearance])
            cube([21,3+travel,5-floor_rail_clearance]);
    }
}
module floor_pin_sweep() {
    translate([5,floor_rail_start+8,floor_thickness+2]) union() {
        hull() for(d=[1,15]) translate([0,0,d])
            cylinder(h=3,d1=2.8,d2=3.1+floor_pin_interference);
        translate([0,0,4]) cylinder(h=15.2,d=6);
    }
}
module floor_coupon() {
    translate([18,-(floor_rail_start-4),0]) intersection() {
        union() { corner(floor_length=floor_coupon_length);
                  rotate([0,0,90]) corner(floor_length=floor_coupon_length); }
        translate([-18,floor_rail_start-4,-eps])
            cube([36,floor_coupon_length+8,floor_thickness+8+eps]);
    }
}

module key_at_seam() {
    translate([0,rail_y,key_stop]) key();
}
module pin_at_seam() {
    translate([0,half+rail_projection,pin_z-2]) pin();
}
module print_key(length=key_length,bore_z=pin_z-key_stop) {
    translate([0,6,16]) rotate([0,90,0]) key(length,bore_z);
}

colors=[[0.20,0.62,0.65],[0.93,0.63,0.25],
        [0.35,0.55,0.78],[0.75,0.43,0.53]];
if(view=="assembled" || view=="exploded") {
    for(i=[0:3]) rotate([0,0,90*i]) {
        color(colors[i]) translate(view=="exploded" ? [explode_distance,explode_distance,0] : [0,0,0]) corner();
        color([0.28,0.30,0.33]) translate(view=="exploded" ? [0,20,50] : [0,0,0]) key_at_seam();
        color([0.95,0.75,0.20]) translate(view=="exploded" ? [0,50,50] : [0,0,0]) pin_at_seam();
        color([0.28,0.30,0.33]) translate(view=="exploded" ? [0,-25,30] : [0,0,0]) floor_key_at_seam();
        color([0.95,0.75,0.20]) translate(view=="exploded" ? [0,0,50] : [0,0,0]) floor_pin_at_seam();
    }
} else if(view=="corner") {
    corner();
} else if(view=="key") {
    print_key();
} else if(view=="pin") {
    translate([4,14,0]) pin();
} else if(view=="coupon_key") {
    print_key(coupon_height-key_stop,coupon_height-12-key_stop);
} else if(view=="coupon") {
    translate([rail_width/2+1,-(half-2),0]) intersection() {
        union() { corner(coupon_height-12); rotate([0,0,90]) corner(coupon_height-12); }
        translate([-rail_width/2-1,half-2,0]) cube([rail_width+2,rail_projection+4,coupon_height]);
    }
} else if(view=="floor_key") {
    print_floor_key();
} else if(view=="floor_pin") {
    translate([3,3,4.2]) rotate([180,0,0]) floor_pin();
} else if(view=="floor_coupon_key") {
    print_floor_key(floor_coupon_length);
} else if(view=="floor_coupon") {
    floor_coupon();
} else if(view=="floor_key_sweep") {
    floor_key_sweep();
} else if(view=="floor_pin_sweep") {
    floor_pin_sweep();
} else if(view=="floor_detail") {
    for(i=[0:3]) rotate([0,0,90*i]) {
        color(colors[i]) intersection() { corner(); translate([-150,-150,-eps]) cube([300,300,16]); }
        color([0.28,0.30,0.33]) floor_key_at_seam();
        color([0.95,0.75,0.20]) floor_pin_at_seam();
    }
} else if(view=="floor_joint_section" || view=="floor_joint_exploded") {
    for(i=[0:1]) color(colors[i]) intersection() {
        rotate([0,0,90*i]) corner(floor_length=floor_coupon_length);
        translate([-18,view=="floor_joint_section" ? floor_rail_start+15 : floor_rail_start-4,-eps])
            cube([36,view=="floor_joint_section" ? 1 : floor_coupon_length+8,floor_thickness+8+eps]);
    }
    color([0.95,0.75,0.20])
        if(view=="floor_joint_section") intersection() {
            translate([0,floor_rail_start,0]) floor_key(floor_coupon_length);
            translate([-18,floor_rail_start+15,-eps]) cube([36,1,floor_thickness+8+eps]);
        } else translate([0,floor_rail_start-floor_coupon_length-3,0]) floor_key(floor_coupon_length);
}
