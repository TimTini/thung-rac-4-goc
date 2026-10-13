// V6: recessed T-head floor bridge, inserted from below then slid to lock.
// Joint principle reference (independent geometry, not copied code):
// https://catchit.pl/blog/modular-3d-printed-case-diy-project/
// Still a prototype; reference does not validate this bin or its load rating.
/* [View] */
view = "assembled"; // [assembled,exploded,corner,key,pin,coupon,coupon_key,coupon_pin,floor_key,floor_coupon,floor_detail,underside_detail,corner_detail,floor_joint_section,floor_joint_exploded]
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
floor_clip_y = 50;
floor_clip_travel = 8;
floor_clip_clearance = 0.25;
floor_pad_height = 8;
// Audit displacement, not a validated elastic material response.
floor_latch_press = 0.9;
/* [Printed joints] */
seam_gap = 0.4;
// Slot clearance measured normal to each key face, per side.
key_clearance = 0.25;
rail_width = 48;
rail_projection = 16;
key_stop = 8;
floor_rib_start = 10;
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
assert(floor_rib_start>=8 && floor_rib_start<half/3);
assert(pin_interference>=0 && pin_interference<=0.2);
assert(floor_fillet>0 && floor_fillet<corner_radius-wall);
assert(gusset_run>floor_fillet && gusset_height>floor_rib_height);
assert(gusset_run<half/3-floor_rib_start && gusset_height<body_height-16);
assert(floor_clip_travel>=8 && floor_clip_travel<=10);
assert(floor_clip_clearance>=0.15 && floor_clip_clearance<=0.35);
assert(floor_pad_height>=6+floor_clip_clearance+eps+1.5
       && floor_pad_height>floor_thickness && floor_pad_height<=10);
assert(floor_latch_press>=0.85 && floor_latch_press<=1.1);
assert(floor_latch_press>=1.05-floor_clip_clearance,
       "Pressed latch must clear the bridge-pocket ceiling");
assert(floor_clip_y-floor_clip_travel-8>24,
       "Floor pads must leave the central assembly area open");
assert(floor_clip_y+22<half-wall-gusset_run);
assert(floor_clip_y-floor_clip_travel-4<half/3-floor_rib_width/2
       && floor_clip_y+18>half/3+floor_rib_width/2,
       "Floor pad must intersect the first floor rib");
assert(view=="assembled" || view=="exploded" || view=="corner"
       || view=="key" || view=="pin" || view=="coupon"
       || view=="coupon_key" || view=="coupon_pin" || view=="floor_key"
       || view=="floor_coupon" || view=="floor_detail" || view=="corner_detail"
       || view=="underside_detail" || view=="floor_key_pressed"
       || view=="floor_clip_loading_sweep" || view=="floor_clip_slide_sweep"
       || view=="floor_latch_release_sweep" || view=="floor_joint_section"
       || view=="floor_joint_exploded", "Unknown view");

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

// Each half-pad rises only to Z8 by default, with a sloped top perimeter.
module floor_pad() {
    hull() {
        translate([seam_gap/2,floor_clip_y-floor_clip_travel-8,floor_thickness-eps])
            cube([21-seam_gap/2,30+floor_clip_travel,eps]);
        translate([seam_gap/2,floor_clip_y-floor_clip_travel-4,floor_pad_height-eps])
            cube([17-seam_gap/2,22+floor_clip_travel,eps]);
    }
}
module floor_clip_pocket() {
    c=floor_clip_clearance;
    translate([0,floor_clip_y,0]) {
        // Narrow crossbar instead of a wide rectangular counterbore.
        translate([-14-c,11-floor_clip_travel-c,-eps])
            cube([28+2*c,3+floor_clip_travel+2*c,1.6+c+eps]);
        translate([2-c,2-floor_clip_travel-c,-eps])
            cube([3+2*c,9+floor_clip_travel+2*c,1.6+c+eps]);
        for(x=[-9,9]) {
            translate([x-3.5-c,3-floor_clip_travel-c,-eps])
                cube([7+2*c,8+floor_clip_travel+2*c,1.6+c+eps]);
            translate([x,11+c,0]) rotate([90,0,0])
                linear_extrude(8+floor_clip_travel+2*c)
                    offset(delta=c) floor_hook_profile();
            // Large entry window; the head moves beyond it after the slide.
            translate([x-3.5-c-eps,3-floor_clip_travel-c,-eps])
                cube([7+2*c+2*eps,8+2*c,6+c+2*eps]);
        }
        // Latch loading window and final catch, separated by a solid ceiling.
        for(y=[2-floor_clip_travel,2])
            translate([2-c,y-c,-eps]) cube([3+2*c,3+2*c,2.6+c+eps]);
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
    translate([-2.3,half+2,z-2.25])
        cube([4.6,rail_projection-2+eps,4.5]);
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
            floor_gussets(); mirror([1,-1,0]) floor_gussets();
            floor_pad(); mirror([1,-1,0]) floor_pad();
        }
        slot(); mirror([1,-1,0]) slot();
        pin_bore(retaining_z); mirror([1,-1,0]) pin_bore(retaining_z);
        floor_clip_pocket(); mirror([1,-1,0]) floor_clip_pocket();
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

// Leaf shape used only to bound a manually pressed release motion.
function latch_drop(y,pressed)=pressed ?
    floor_latch_press*(3*pow((11-y)/9,2)-pow((11-y)/9,3))/2 : 0;
module latch_leaf(pressed=false) {
    translate([2,0,0]) rotate([90,0,90]) linear_extrude(3) {
        polygon(concat([for(i=[0:18]) let(y=2+i/2) [y,-latch_drop(y,pressed)]],
                       [for(i=[18:-1:0]) let(y=2+i/2) [y,1.2-latch_drop(y,pressed)]]));
        polygon([[2,1.18-latch_drop(2,pressed)],
                 [2,2.6-latch_drop(2,pressed)],
                 [5,1.18-latch_drop(5,pressed)]]);
    }
}
module floor_hook_profile() {
    // X/Z section: 45-degree shoulders can grow from the stem without support.
    polygon([[-1.8,1.6-eps],[1.8,1.6-eps],[1.8,2.6],[3.5,4.3],
             [3.5,6],[-3.5,6],[-3.5,4.3],[-1.8,2.6]]);
}
module floor_key(pressed=false) {
    union() {
        translate([-14,11,0]) cube([28,3,1.6]);
        latch_leaf(pressed);
        for(x=[-9,9]) {
            translate([x-3.5,3,0]) cube([7,8,1.6]);
            translate([x,11,0]) rotate([90,0,0]) linear_extrude(8) floor_hook_profile();
        }
    }
}
module floor_key_at_seam() {
    translate([0,floor_clip_y,0]) floor_key();
}
module floor_clip_loading_sweep() {
    translate([0,floor_clip_y-floor_clip_travel,0]) {
        translate([-14,11,-15]) cube([28,3,16.6]);
        for(x=[-9,9]) {
            translate([x-1.8,3,-15]) cube([3.6,8,19.3]);
            translate([x-3.5,3,4.3-15]) cube([7,8,16.7]);
            translate([x-3.5,3,-15]) cube([7,8,16.6]);
        }
        translate([2,2,-15]) cube([3,9,16.2]);
        translate([2,2,-15]) cube([3,3,17.6]);
    }
}
module floor_clip_slide_sweep() {
    translate([0,floor_clip_y-floor_clip_travel,0]) {
        translate([-14,11,0]) cube([28,3+floor_clip_travel,1.6]);
        for(x=[-9,9]) {
            translate([x-3.5,3,0]) cube([7,8+floor_clip_travel,1.6]);
            translate([x,11+floor_clip_travel,0]) rotate([90,0,0])
                linear_extrude(8+floor_clip_travel) floor_hook_profile();
        }
        translate([2,2,-floor_latch_press])
            cube([3,9+floor_clip_travel,1.2+floor_latch_press]);
        translate([2,2,0]) cube([3,3+floor_clip_travel,2.6-floor_latch_press]);
    }
}
module floor_latch_release_sweep() {
    // Conservative rest-to-pressed envelope at the seated position.
    translate([0,floor_clip_y,0]) union() {
        floor_key();
        translate([2-eps,2-eps,-floor_latch_press])
            cube([3+2*eps,9+2*eps,1.2+floor_latch_press]);
        translate([2-eps,2-eps,-floor_latch_press])
            cube([3+2*eps,3+2*eps,2.6+floor_latch_press]);
    }
}
module floor_coupon() {
    translate([24,-(floor_clip_y-floor_clip_travel-7),0]) intersection() {
        union() { corner(); rotate([0,0,90]) corner(); }
        translate([-24,floor_clip_y-floor_clip_travel-7,0])
            cube([48,32+floor_clip_travel,floor_pad_height+5]);
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
        color(colors[i]) translate(view=="exploded" ? [explode_distance,explode_distance,0]
                                                 : [0,0,0]) corner();
        color([0.28,0.30,0.33])
            translate(view=="exploded" ? [0,20,50] : [0,0,0]) key_at_seam();
        color([0.95,0.75,0.20])
            translate(view=="exploded" ? [0,50,50] : [0,0,0]) pin_at_seam();
        color([0.28,0.30,0.33])
            translate(view=="exploded" ? [0,-20,30] : [0,0,0]) floor_key_at_seam();
    }
} else if(view=="corner") {
    corner();
} else if(view=="key") {
    print_key();
} else if(view=="pin" || view=="coupon_pin") {
    translate([4,14,0]) pin();
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
} else if(view=="floor_key") {
    translate([14,0,0]) floor_key();
} else if(view=="floor_key_pressed") {
    translate([0,floor_clip_y,0]) floor_key(true);
} else if(view=="floor_clip_loading_sweep") {
    floor_clip_loading_sweep();
} else if(view=="floor_clip_slide_sweep") {
    floor_clip_slide_sweep();
} else if(view=="floor_latch_release_sweep") {
    floor_latch_release_sweep();
} else if(view=="floor_coupon") {
    floor_coupon();
} else if(view=="floor_detail") {
    for(i=[0:3]) rotate([0,0,90*i]) {
        color(colors[i]) intersection() {
            corner(); translate([-100,-100,-eps]) cube([200,200,32]);
        }
        color([0.28,0.30,0.33]) floor_key_at_seam();
    }
} else if(view=="underside_detail") {
    rotate([180,0,0]) for(i=[0:3]) rotate([0,0,90*i]) {
        color(colors[i]) intersection() {
            corner(); translate([-85,-85,-eps]) cube([170,170,16]);
        }
        color([0.28,0.30,0.33]) floor_key_at_seam();
    }
} else if(view=="floor_joint_section" || view=="floor_joint_exploded") {
    for(i=[0:1]) color(colors[i]) intersection() {
        rotate([0,0,90*i]) corner();
        translate([-24,view=="floor_joint_section" ? floor_clip_y+6.5 :
                      floor_clip_y-floor_clip_travel-7,-eps])
            cube([48,view=="floor_joint_section" ? 1 : 32+floor_clip_travel,
                  floor_pad_height+5]);
    }
    color([0.95,0.75,0.20])
        if(view=="floor_joint_section") intersection() {
            floor_key_at_seam();
            translate([-24,floor_clip_y+6.5,-eps]) cube([48,1,floor_pad_height+5]);
        } else translate([0,-floor_clip_travel,-10]) floor_key_at_seam();
} else if(view=="corner_detail") {
    color(colors[0]) intersection() {
        corner(); translate([half/3-20,half-45,-eps]) cube([40,55,45]);
    }
}
