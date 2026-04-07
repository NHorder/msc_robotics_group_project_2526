$fn = 96;

// ═══════════════════════════════════════════════════════════════════════
//  VISNAT MOBILE PLATFORM  –  ROS2-ready modular OpenSCAD
//  Updated with:
//   - octagonal chassis
//   - mecanum wheels
//   - wheels mounted on short chamfered sides
//   - moved main mast
//   - added screen mast + screen
//   - added bucket holder mold
//   - screen mast, main mast, and bucket holder aligned on X-axis
// ═══════════════════════════════════════════════════════════════════════

// ── Export selector (override via CLI -D flag) ──────────────────────────
EXPORT_LINK = "all";   // "all" | "base_link" | "wheel_fl" | "wheel_fr" | "wheel_rl" | "wheel_rr"

// ═══════════════════════════════════════════════════════════════════════
//  DIMENSIONS  (all in mm; divide by 1000 for URDF metres)
// ═══════════════════════════════════════════════════════════════════════

// ── Wheel ────────────────────────────────────────────────────────────────
wheel_diameter   = 180;
wheel_radius     = wheel_diameter / 2;
wheel_width      = 52;
axle_z           = wheel_radius;

// ── Body ─────────────────────────────────────────────────────────────────
body_length      = 610;
body_width       = 610;
body_height      = 180;
body_wall        = 9;
body_corner_r    = 18;

// ── Vertical layout ─────────────────────────────────────────────────────
ground_clearance = 120;
body_bottom_z    = ground_clearance;
body_top_z       = body_bottom_z + body_height;

// ── Top plate ───────────────────────────────────────────────────────────
plate_thick      = 12;
plate_margin     = 6;

// ── Main mast ───────────────────────────────────────────────────────────
mast_d           = 82;
mast_collar_w    = 140;
mast_collar_h    = 14;
hazard_ring_h    = 18;
mast_col_start_z = body_top_z + plate_thick + mast_collar_h + hazard_ring_h;
mast_h           = 184;
mast_top_w       = 140;
mast_top_h       = 22;

// ── Added aligned layout positions ──────────────────────────────────────
screen_mast_x    = -180;
main_mast_x      = -35;
bucket_holder_x  = 140;
aligned_y        = 0;

// ── Screen mast + screen ────────────────────────────────────────────────
screen_mast_h    = 1050;   // 105 cm
screen_mast_r    = 40;     // radius 4 cm
screen_w         = 355;    // approx 16" width
screen_h         = 205;    // approx 16" height
screen_t         = 14;

// ── Bucket holder ───────────────────────────────────────────────────────
bucket_d         = 230;
bucket_holder_d  = bucket_d + 40;
bucket_holder_h  = 22;
bucket_recess_h  = 18;

// ── Coil spring ─────────────────────────────────────────────────────────
spr_od           = 32;
spr_wire         = 3.8;
spr_coils        = 6;

// ── Motor ───────────────────────────────────────────────────────────────
mot_d            = 60;
mot_l            = 76;
gbox_d           = 68;
gbox_l           = 36;

// ── Battery ─────────────────────────────────────────────────────────────
bat_l = 300; bat_w = 150; bat_h = 72;

// ── E-stop ──────────────────────────────────────────────────────────────
estop_x = -body_length/2 + 65;
estop_y =  body_width/2  - 65;

// ── Octagon / wheel placement ───────────────────────────────────────────
oct_chamfer      = 120;
frame_size       = 30;
short_face_mid   = body_length/2 - oct_chamfer/2;
wheel_face_gap   = wheel_width/2 + 24;
wheel_corner_c   = short_face_mid + wheel_face_gap/sqrt(2);

// ═══════════════════════════════════════════════════════════════════════
//  HELPERS
// ═══════════════════════════════════════════════════════════════════════
module rounded_box(l, w, h, r) {
    hull()
        for (x=[-l/2+r, l/2-r], y=[-w/2+r, w/2-r])
            translate([x, y, 0]) cylinder(h=h, r=r);
}

module box_shell(l, w, h, r, wall) {
    difference() {
        rounded_box(l, w, h, r);
        translate([0, 0, wall])
            rounded_box(l-2*wall, w-2*wall, h, max(r-wall, 2));
    }
}

module beam_x(len, size=frame_size) {
    cube([len, size, size], center=true);
}

module beam_y(len, size=frame_size) {
    cube([size, len, size], center=true);
}

module octagon_2d(l=body_length, w=body_width, c=oct_chamfer) {
    polygon(points=[
        [ l/2-c,  w/2],
        [-l/2+c,  w/2],
        [-l/2,    w/2-c],
        [-l/2,   -w/2+c],
        [-l/2+c, -w/2],
        [ l/2-c, -w/2],
        [ l/2,   -w/2+c],
        [ l/2,    w/2-c]
    ]);
}

module octagon_plate(l=body_length, w=body_width, c=oct_chamfer, h=10) {
    linear_extrude(height=h)
        octagon_2d(l,w,c);
}

module octagon_ring(l=body_length, w=body_width, c=oct_chamfer, t=frame_size, h=frame_size) {
    linear_extrude(height=h)
        difference() {
            octagon_2d(l,w,c);
            offset(delta=-t) octagon_2d(l,w,c);
        }
}

// ═══════════════════════════════════════════════════════════════════════
//  BASE LINK
// ═══════════════════════════════════════════════════════════════════════
module base_link() {

    // ── Octagonal chassis body ─────────────────────────────────────────
    color([0.71, 0.73, 0.75])
    union() {
        // bottom ring
        translate([0,0,body_bottom_z])
            octagon_ring(body_length, body_width, oct_chamfer, frame_size, frame_size);

        // top ring
        translate([0,0,body_top_z - frame_size])
            octagon_ring(body_length, body_width, oct_chamfer, frame_size, frame_size);

        // vertical posts
        for (p = [
            [ body_length/2-oct_chamfer,  body_width/2-frame_size/2],
            [-body_length/2+oct_chamfer,  body_width/2-frame_size/2],
            [-body_length/2+frame_size/2, body_width/2-oct_chamfer],
            [-body_length/2+frame_size/2,-body_width/2+oct_chamfer],
            [-body_length/2+oct_chamfer, -body_width/2+frame_size/2],
            [ body_length/2-oct_chamfer, -body_width/2+frame_size/2],
            [ body_length/2-frame_size/2,-body_width/2+oct_chamfer],
            [ body_length/2-frame_size/2, body_width/2-oct_chamfer]
        ])
            translate([p[0], p[1], body_bottom_z + frame_size])
                cylinder(h = body_height - 2*frame_size, d = 14);

        // internal deck
        translate([0, 0, body_bottom_z + 28 - 4])
            linear_extrude(height = 8)
                offset(delta=-80)
                    octagon_2d(body_length, body_width, oct_chamfer);

        // support beams
        translate([0, 0, body_bottom_z + 46]) beam_x(body_length - 180, 24);
        translate([0, 0, body_bottom_z + 46]) beam_y(body_width - 180, 24);
        translate([0, 120, body_bottom_z + 46]) beam_x(body_length - 220, 24);
        translate([0,-120, body_bottom_z + 46]) beam_x(body_length - 220, 24);
    }

    _hazard_band();
    _panel_rivets();

    // ── Top plate ──────────────────────────────────────────────────────
    color([0.74, 0.76, 0.78])
    translate([0, 0, body_top_z]) {
        difference() {
            octagon_plate(body_length - 2*plate_margin,
                          body_width  - 2*plate_margin,
                          oct_chamfer - 8,
                          plate_thick);

            for (x=[-210,-105,0,105,210])
                for (y=[-210,-105,0,105,210])
                    translate([x, y, -1]) cylinder(h=plate_thick+2, d=7);

            // moved main mast hole
            translate([main_mast_x, aligned_y, -1])
                cylinder(h=plate_thick+2, d=mast_d+8);

            // added screen mast locating hole
            translate([screen_mast_x, aligned_y, -1])
                cylinder(h=plate_thick+2, d=screen_mast_r*2 + 8);
        }

        color([0.50, 0.50, 0.53])
        for (i=[-3:3]) for (s=[-1,1]) {
            translate([i*75, s*170, plate_thick]) cylinder(d=6, h=4);
            translate([s*170, i*75, plate_thick]) cylinder(d=6, h=4);
        }
    }

    // ── Main mast ──────────────────────────────────────────────────────
    _central_mast();

    // ── Screen mast + screen ───────────────────────────────────────────
    _screen_system();

    // ── Bucket holder ──────────────────────────────────────────────────
    _bucket_holder();

    // ── Battery pack ───────────────────────────────────────────────────
    _battery_pack();

    // ── Emergency stop ─────────────────────────────────────────────────
    _emergency_stop();

    // ── Wheel uprights + springs + motors on chamfered faces ──────────
    _wheel_upright( wheel_corner_c,  wheel_corner_c,  1/sqrt(2),  1/sqrt(2), -45);
    _wheel_upright(-wheel_corner_c,  wheel_corner_c, -1/sqrt(2),  1/sqrt(2),  45);
    _wheel_upright(-wheel_corner_c, -wheel_corner_c, -1/sqrt(2), -1/sqrt(2), -45);
    _wheel_upright( wheel_corner_c, -wheel_corner_c,  1/sqrt(2), -1/sqrt(2),  45);

    _corner_spring( wheel_corner_c,  wheel_corner_c,  1/sqrt(2),  1/sqrt(2));
    _corner_spring(-wheel_corner_c,  wheel_corner_c, -1/sqrt(2),  1/sqrt(2));
    _corner_spring(-wheel_corner_c, -wheel_corner_c, -1/sqrt(2), -1/sqrt(2));
    _corner_spring( wheel_corner_c, -wheel_corner_c,  1/sqrt(2), -1/sqrt(2));

    _wheel_motor( wheel_corner_c,  wheel_corner_c,  1/sqrt(2),  1/sqrt(2), -45);
    _wheel_motor(-wheel_corner_c,  wheel_corner_c, -1/sqrt(2),  1/sqrt(2),  45);
    _wheel_motor(-wheel_corner_c, -wheel_corner_c, -1/sqrt(2), -1/sqrt(2), -45);
    _wheel_motor( wheel_corner_c, -wheel_corner_c,  1/sqrt(2), -1/sqrt(2),  45);
}

// ═══════════════════════════════════════════════════════════════════════
//  WHEEL LINK - MECANUM STYLE
//  handed = +1 or -1
// ═══════════════════════════════════════════════════════════════════════
module wheel_link(handed = 1) {
    rotate([90, 0, 0]) {
        color([0.10,0.10,0.10])
        difference() {
            cylinder(d=wheel_diameter, h=wheel_width, center=true);
            cylinder(d=wheel_diameter-36, h=wheel_width+2, center=true);
        }

        color([0.58, 0.60, 0.63])
        cylinder(d=wheel_diameter-40, h=wheel_width-16, center=true);

        color([0.44, 0.46, 0.49])
        cylinder(d=46, h=wheel_width+10, center=true);

        color([0.54, 0.56, 0.59])
        difference() {
            cylinder(d=62, h=wheel_width+4, center=true);
            cylinder(d=46, h=wheel_width+6, center=true);
        }

        color([0.07, 0.07, 0.07])
        for (a=[0:45:315])
            rotate([0,0,a])
                translate([wheel_diameter/2-16, 0, 0])
                    rotate([0, handed*45, 0])
                        scale([1,1,1.35])
                            cylinder(d=18, h=wheel_width-2, center=true);
    }
}

// ═══════════════════════════════════════════════════════════════════════
//  INTERNAL HELPER MODULES
// ═══════════════════════════════════════════════════════════════════════

module _hazard_band() {
    bz     = body_top_z - 38;
    band_h = 24;
    sw     = 18;

    color("gold")
    difference() {
        translate([0,0,bz]) octagon_plate(body_length+2, body_width+2, oct_chamfer+4, band_h);
        translate([0,0,bz-1]) octagon_plate(body_length-2*body_wall,
                                            body_width-2*body_wall,
                                            oct_chamfer-8,
                                            band_h+2);
    }
    color("black")
    for (side=[0:7])
        rotate([0,0,side*45])
            translate([0, body_width/2 - 40, bz+band_h/2])
                rotate([90,45,0])
                    cube([sw*0.85, band_h*1.4, body_wall+2], center=true);
}

module _panel_rivets() {
    rz1 = body_top_z - 22;
    rz2 = body_bottom_z + 20;
    color([0.50, 0.50, 0.53])
    for (rz=[rz1, rz2]) {
        for (a=[0:45:315])
            rotate([0,0,a])
                translate([215,0,rz])
                    sphere(d=5.5);
    }
}

module _central_mast() {
    mz = body_top_z + plate_thick;

    color([0.18, 0.18, 0.20])
    translate([main_mast_x, aligned_y, mz]) {
        difference() {
            rounded_box(mast_collar_w, mast_collar_w, mast_collar_h, 8);
            translate([0,0,-1]) cylinder(h=mast_collar_h+2, d=mast_d-4);
            for (x=[-48,48]) for (y=[-48,48])
                translate([x,y,-1]) cylinder(h=mast_collar_h+2, d=9);
        }
    }

    hz = mz + mast_collar_h;
    color("gold")
    translate([main_mast_x, aligned_y, hz]) {
        difference() {
            cylinder(d=mast_d+38, h=hazard_ring_h);
            translate([0,0,-1]) cylinder(d=mast_d+2, h=hazard_ring_h+2);
        }
    }

    color("black")
    translate([main_mast_x, aligned_y, hz])
        for (i=[0:7])
            rotate([0,0,i*45])
                translate([mast_d/2+16, 0, hazard_ring_h/2])
                    rotate([90,45,0]) cube([15,22,13], center=true);

    color([0.76, 0.76, 0.78])
    translate([main_mast_x, aligned_y, mast_col_start_z])
        cylinder(d=mast_d, h=mast_h);

    color([0.54, 0.54, 0.57])
    translate([main_mast_x, aligned_y, mast_col_start_z + mast_h*0.42])
        difference() {
            cylinder(d=mast_d+22, h=20);
            translate([0,0,-1]) cylinder(d=mast_d-2, h=22);
        }

    color([0.18, 0.18, 0.20])
    translate([main_mast_x, aligned_y, mast_col_start_z + mast_h]) {
        difference() {
            rounded_box(mast_top_w, mast_top_w, mast_top_h, 8);
            for (x=[-48,48]) for (y=[-48,48])
                translate([x,y,-1]) cylinder(h=mast_top_h+2, d=10);
            translate([0,0,-1]) cylinder(h=mast_top_h+2, d=mast_d-6);
        }
        translate([0,0,mast_top_h]) cylinder(d=mast_d*0.52, h=14);
    }
}

module _screen_system() {
    base_z = body_top_z + plate_thick;
    sx = screen_mast_x;
    sy = aligned_y;

    color([0.72, 0.72, 0.75])
    translate([sx, sy, base_z])
        cylinder(h=screen_mast_h, r=screen_mast_r);

    color([0.60, 0.60, 0.63])
    translate([sx, sy, base_z + screen_mast_h])
        cylinder(h=30, r1=24, r2=20);

    color([0.25, 0.25, 0.27])
    translate([sx, sy, base_z + screen_mast_h - 110])
        cube([24, 90, 110], center=true);

    color([0.08, 0.08, 0.09])
    translate([sx - 35, sy, base_z + screen_mast_h - 110])
        rotate([90, 0, 90])
            cube([screen_w, screen_h, screen_t], center=true);

    color([0.20, 0.20, 0.22])
    translate([sx - 42, sy, base_z + screen_mast_h - 110])
        rotate([90, 0, 90])
            difference() {
                cube([screen_w + 18, screen_h + 18, 10], center=true);
                cube([screen_w - 8, screen_h - 8, 12], center=true);
            }
}

module _bucket_holder() {
    base_z = body_top_z + plate_thick;
    color([0.60, 0.62, 0.65])
    translate([bucket_holder_x, aligned_y, base_z]) {
        difference() {
            cylinder(d=bucket_holder_d, h=bucket_holder_h);
            translate([0,0,4])
                cylinder(d=bucket_d, h=bucket_recess_h + 2);
        }
    }
}

module _battery_pack() {
    translate([0, 12, body_bottom_z + 28 + bat_h/2 + 10]) {
        color([0.17, 0.17, 0.19])
        rounded_box(bat_l, bat_w, bat_h, 10);
        color([0.11, 0.11, 0.13])
        for (i=[-2:2])
            translate([i*52, 0, bat_h])
                cube([8, bat_w-12, 4], center=true);
    }
}

module _emergency_stop() {
    ez = body_top_z + plate_thick;
    color("gold")
    translate([estop_x, estop_y, ez])
        rounded_box(72, 56, 20, 6);
    color("red")
    translate([estop_x, estop_y, ez+20]) {
        cylinder(d=44, h=14);
        translate([0,0,10]) sphere(d=46);
    }
    color([0.28,0.28,0.28])
    translate([estop_x, estop_y, ez+12]) cylinder(d=15, h=14);
}

module _wheel_upright(x, y, nx, ny, rotz) {
    // axle tube aligned to wheel
    color([0.54,0.56,0.59])
    translate([x, y, axle_z])
        rotate([0,0,rotz])
            rotate([90,0,0])
                cylinder(d=24, h=wheel_width+28, center=true);

    // upright support inward from wheel center
    ux = x - nx*45;
    uy = y - ny*45;

    color([0.58,0.60,0.63])
    translate([ux-10, uy-8, axle_z])
        cube([20, 16, body_bottom_z - axle_z + 22]);

    // brace toward chassis
    bx = x - nx*85;
    by = y - ny*85;

    color([0.56,0.58,0.61])
    translate([(ux+bx)/2, (uy+by)/2, body_bottom_z + body_height*0.26])
        rotate([0,0,rotz])
            cube([70, 16, 16], center=true);
}

module _corner_spring(x, y, nx, ny) {
    spx = x - nx*(wheel_width/2 + 18);
    spy = y - ny*(wheel_width/2 + 18);
    spz_lo = axle_z + 14;
    spz_hi = body_bottom_z + 10;
    sp_h   = spz_hi - spz_lo;

    color([0.68,0.68,0.70])
    translate([spx, spy, spz_lo-8]) cylinder(d=11, h=sp_h+20);

    color([0.52,0.52,0.55])
    translate([spx, spy, spz_hi-4]) cylinder(d=16, h=26);

    color([0.85, 0.72, 0.10])
    translate([spx, spy, spz_lo]) {
        for (i=[0:spr_coils-1])
            translate([0,0,i*(sp_h/spr_coils)])
                rotate_extrude(angle=385, $fn=44)
                    translate([spr_od/2,0]) circle(r=spr_wire);
    }

    color([0.48,0.48,0.50]) {
        translate([spx, spy, spz_lo-5]) cylinder(d=spr_od+10, h=7);
        translate([spx, spy, spz_hi-2]) cylinder(d=spr_od+10, h=7);
    }
}

module _wheel_motor(x, y, nx, ny, rotz) {
    motor_offset = 78;
    mx = x - nx*motor_offset;
    my = y - ny*motor_offset;

    translate([mx, my, axle_z])
        rotate([0,0,rotz])
            rotate([90,0,0]) {
                color([0.28,0.28,0.30])
                translate([0,0,-gbox_l/2]) cylinder(d=gbox_d, h=gbox_l, center=true);

                color([0.20,0.20,0.22])
                translate([0,0,mot_l/2]) cylinder(d=mot_d, h=mot_l, center=true);

                color([0.16,0.16,0.18])
                translate([0,0,mot_l]) cylinder(d=mot_d-8, h=15, center=true);

                color([0.60,0.62,0.65])
                translate([0,0,-gbox_l-15]) cylinder(d=17, h=30, center=true);

                color([0.33,0.33,0.35])
                difference() {
                    cylinder(d=gbox_d+22, h=11, center=true);
                    cylinder(d=gbox_d-4,  h=13, center=true);
                    for (a=[0,90,180,270])
                        rotate([0,0,a]) translate([gbox_d/2+7,0,0])
                            cylinder(d=8, h=13, center=true);
                }
            }
}

// ═══════════════════════════════════════════════════════════════════════
//  EXPORT SELECTOR
// ═══════════════════════════════════════════════════════════════════════
module platform_model() {
    if (EXPORT_LINK == "base_link") {
        base_link();

    } else if (EXPORT_LINK == "wheel_fl") {
        wheel_link(handed=1);

    } else if (EXPORT_LINK == "wheel_fr") {
        wheel_link(handed=-1);

    } else if (EXPORT_LINK == "wheel_rl") {
        wheel_link(handed=-1);

    } else if (EXPORT_LINK == "wheel_rr") {
        wheel_link(handed=1);

    } else {
        base_link();

        // Wheels on short chamfered sides
        // FL
        translate([ wheel_corner_c,  wheel_corner_c, axle_z])
            rotate([0,0,-45]) wheel_link(handed=1);

        // FR
        translate([-wheel_corner_c,  wheel_corner_c, axle_z])
            rotate([0,0,45]) wheel_link(handed=-1);

        // RL
        translate([-wheel_corner_c, -wheel_corner_c, axle_z])
            rotate([0,0,-45]) wheel_link(handed=-1);

        // RR
        translate([ wheel_corner_c, -wheel_corner_c, axle_z])
            rotate([0,0,45]) wheel_link(handed=1);
    }
}

platform_model();