// V3 prototype: entirely printed joints; no screws, nuts, or glue.
/* [View] */
view = "assembled"; // [assembled,exploded,corner,key,pin,coupon,coupon_key,coupon_pin]
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
/* [Printed joints] */
seam_gap = 0.4;
// Slot clearance measured normal to each key face, per side.
key_clearance = 0.25;
rail_width = 48;
rail_projection = 16;
key_stop = 8;
floor_lap = 8;
floor_clearance = 0.3;
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
assert(floor_lap>=8 && floor_clearance>0 && floor_clearance<0.6);
assert(pin_interference>=0 && pin_interference<=0.2);
assert(view=="assembled" || view=="exploded" || view=="corner"
       || view=="key" || view=="pin" || view=="coupon"
       || view=="coupon_key" || view=="coupon_pin", "Unknown view");

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
            translate([0,0,body_height-12]) linear_extrude(12)
                rounded_square(body_size+8,corner_radius+4);
            hull() {
                translate([0,0,body_height/2-band_height/2]) linear_extrude(eps)
                    rounded_square(body_size,corner_radius);
                translate([0,0,body_height/2-band_height/2+band_projection])
                    linear_extrude(band_height-band_projection)
                        rounded_square(body_size+2*band_projection,
                                       corner_radius+band_projection);
            }
        }
        translate([0,0,floor_thickness]) linear_extrude(body_height+1)
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
        translate([floor_lap+2,p-floor_rib_width/2,floor_thickness-eps])
            cube([half-wall-floor_lap-2,floor_rib_width,floor_rib_height+eps]);
        translate([p-floor_rib_width/2,floor_lap+2,floor_thickness-eps])
            cube([floor_rib_width,half-wall-floor_lap-2,floor_rib_height+eps]);
    }
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
    translate([-rail_width/2-1,rail_y-2.3,z-2.25])
        cube([rail_width+2,4.6,4.5]);
}

module corner(retaining_z=pin_z) {
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
            // Lower tongue; mating upper rebate is on the other floor edge.
            translate([-floor_lap,floor_lap+2,0])
                cube([floor_lap+seam_gap/2+1,half-wall-2*floor_lap-4,
                      (floor_thickness-floor_clearance)/2]);
        }
        slot(); mirror([1,-1,0]) slot();
        pin_bore(retaining_z); mirror([1,-1,0]) pin_bore(retaining_z);
        // Longer rebate leaves clearance for diagonal, same-height assembly.
        translate([2-floor_clearance,-eps,-eps])
            cube([half-wall-4+2*floor_clearance,floor_lap+floor_clearance,
                  (floor_thickness+floor_clearance)/2+eps]);
    }
}

module key(length=key_length, bore_z=pin_z-key_stop) {
    difference() {
        union() {
            linear_extrude(length) bowtie();
            translate([-16,-6,length]) cube([32,12,4]);
        }
        translate([-17,-2.3,bore_z-2.25]) cube([34,4.6,4.5]);
    }
}

module pin() {
    // Wedge taper only in Y; flat bottom for printing without supports.
    linear_extrude(4) union() {
        polygon([[-rail_width/2,-(4.6+pin_interference)/2],
                 [rail_width/2,-2], [rail_width/2,2],
                 [-rail_width/2,(4.6+pin_interference)/2]]);
        translate([-rail_width/2-3,-4]) square([3+eps,8]);
    }
}

module key_at_seam() {
    translate([0,rail_y,key_stop]) key();
}
module pin_at_seam() {
    translate([0,rail_y,pin_z-2]) pin();
}
module print_key(length=key_length,bore_z=pin_z-key_stop) {
    translate([0,6,16]) rotate([0,90,0]) key(length,bore_z);
}

colors=[[0.20,0.62,0.65],[0.93,0.63,0.25],
        [0.35,0.55,0.78],[0.75,0.43,0.53]];
if(view=="assembled" || view=="exploded") {
    for(i=[0:3]) rotate([0,0,90*i]) {
        color(colors[i]) translate(view=="exploded" ? [explode_distance,explode_distance,0]
                                                 : [0,0,0]) corner();
        color([0.28,0.30,0.33])
            translate(view=="exploded" ? [0,20,50] : [0,0,0]) key_at_seam();
        color([0.95,0.75,0.20])
            translate(view=="exploded" ? [-35,20,50] : [0,0,0]) pin_at_seam();
    }
} else if(view=="corner") {
    translate([floor_lap,0,0]) corner();
} else if(view=="key") {
    print_key();
} else if(view=="pin" || view=="coupon_pin") {
    translate([rail_width/2+3,4,0]) pin();
} else if(view=="coupon_key") {
    print_key(coupon_height-key_stop,coupon_height-12-key_stop);
} else if(view=="coupon") {
    // Two full rail halves, includes bottom stop and the same retaining bore.
    translate([rail_width/2+1,-(half-2),0]) intersection() {
        union() { corner(coupon_height-12);
                  rotate([0,0,90]) corner(coupon_height-12); }
        translate([-rail_width/2-1,half-2,0])
            cube([rail_width+2,rail_projection+4,coupon_height]);
    }
}
