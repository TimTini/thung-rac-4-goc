// Visualization only: shows the exported V4 key orientation on a 250 mm bed.
// Do not export this scene as an STL; use exports/v4/key.stl for printing.
color([0.22,0.24,0.27]) translate([0,0,-1]) cube([250,250,1]);
// 5 mm brim envelope, shown only as a visual footprint.
color([0.85,0.70,0.22]) translate([2,114,0.01]) cube([246,22,0.1]);
color([0.25,0.65,0.70]) translate([7,119,0.2])
    import("exports/v4/key.stl");
color([0.95,0.95,0.95]) translate([125,225,0.1])
    linear_extrude(0.2) text("250 x 250 mm",size=10,halign="center");
color([0.95,0.95,0.95]) translate([125,85,0.1])
    linear_extrude(0.2) text("Key: 236 x 12 mm",size=9,halign="center");
