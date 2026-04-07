$fn = 96;

// ============================================================
// VISNAT MOBILE PLATFORM - OCTAGONAL CHASSIS + MECANUM WHEELS
// V.I.S.N.A.T engraved in white on all 4 long flat sides
// ============================================================

// ---------------- Dimensions ----------------
body_length      = 610;
body_width       = 610;
body_height      = 180;
body_wall        = 8;
body_corner_r    = 18;

ground_clearance = 120;

wheel_diameter   = 180;
wheel_radius     = wheel_diameter / 2;
wheel_width      = 50;
axle_z           = wheel_radius;        // = 90

body_bottom_z    = ground_clearance;    // = 120
body_top_z       = body_bottom_z + body_height;  // = 300

// top plate
plate_thick      = 12;
plate_margin     = 6;

// central mast
mast_d           = 78;
mast_h           = 230;
mast_collar_w    = 130;
mast_collar_h    = 12;
mast_top_w       = 130;
mast_top_h       = 20;

// aligned layout positions
screen_mast_x    = -180;
main_mast_x      = -35;
bucket_holder_x  = 140;
aligned_y        = 0;

// battery
bat_l = 300;
bat_w = 155;
bat_h = 70;

// e-stop
estop_x = -190;
estop_y =  200;

// spring
spr_od           = 30;
spr_wire         = 3.5;
spr_coils        = 6;

// motor
mot_d            = 56;
mot_l            = 72;
gbox_d           = 64;
gbox_l           = 34;

// screen mast + screen
screen_mast_h    = 1050;
screen_mast_r    = 40;
screen_w         = 355;
screen_h         = 205;
screen_t         = 14;

// bucket holder
bucket_d         = 230;
bucket_holder_d  = bucket_d + 40;
bucket_holder_h  = 22;
bucket_recess_h  = 18;

// frame parameters
frame_size       = 30;
deck_thick       = 8;
deck_z           = body_bottom_z + frame_size + deck_thick/2;
post_d           = 14;

// side panel
side_panel_thick = 4;

// octagon parameters
oct_chamfer      = 120;

// wheel placement on chamfered corner faces
short_face_mid   = body_length/2 - oct_chamfer/2;
wheel_face_gap   = wheel_width/2 + 24;
wheel_corner_c   = short_face_mid + wheel_face_gap/sqrt(2);

// ── Logo text parameters ────────────────────────────────────
//  Long flat sides of octagon:
//    FRONT (+Y face): y = +body_width/2  = +305, normal +Y
//    REAR  (-Y face): y = -body_width/2  = -305, normal -Y
//    RIGHT (+X face): x = +body_length/2 = +305, normal +X
//    LEFT  (-X face): x = -body_length/2 = -305, normal -X
//  Available face width = body_length - 2*oct_chamfer = 370 mm
//  Text is extruded outward from the panel face

logo_text        = "V.I.S.N.A.T";
logo_size        = 36;           // font size (mm)
logo_depth       = 3.5;          // extrusion depth beyond panel face
logo_z           = body_bottom_z + body_height * 0.50;  // vertical centre = 210
logo_face_offset = body_width/2 + side_panel_thick + 0.2; // = 309.7

// ---------------- Helpers ----------------
module rounded_box(l, w, h, r) {
    hull()
        for (x = [-l/2 + r, l/2 - r], y = [-w/2 + r, w/2 - r])
            translate([x, y, 0]) cylinder(h = h, r = r);
}

module beam_x(len, size=frame_size) {
    cube([len, size, size], center=true);
}

module beam_y(len, size=frame_size) {
    cube([size, len, size], center=true);
}

module octagon_2d(l=body_length, w=body_width, c=oct_chamfer) {
    polygon(points=[
        [ l/2-c,  w/2],  [-l/2+c,  w/2],
        [-l/2,    w/2-c],[-l/2,   -w/2+c],
        [-l/2+c, -w/2],  [ l/2-c, -w/2],
        [ l/2,   -w/2+c],[ l/2,    w/2-c]
    ]);
}

module octagon_plate(l=body_length, w=body_width, c=oct_chamfer, h=10) {
    linear_extrude(height=h) octagon_2d(l,w,c);
}

module octagon_ring(l=body_length, w=body_width, c=oct_chamfer, t=frame_size, h=frame_size) {
    linear_extrude(height=h)
        difference() {
            octagon_2d(l,w,c);
            offset(delta=-t) octagon_2d(l,w,c);
        }
}

module side_segment_panel(p1, p2, z0, h, t=4) {
    dx = p2[0]-p1[0]; dy = p2[1]-p1[1];
    len = sqrt(dx*dx+dy*dy);
    ang = atan2(dy,dx);
    translate([(p1[0]+p2[0])/2, (p1[1]+p2[1])/2, z0+h/2])
        rotate([0,0,ang])
            cube([len, t, h], center=true);
}

// ============================================================
//  V.I.S.N.A.T LOGO  –  white raised text on all 4 long sides
//
//  Each face needs a different rotate + translate sequence:
//
//  +Y face (FRONT):
//    linear_extrude → text lies in XZ plane, extruded in +Y
//    rotate([90,0,0]) → text now faces +Y, extruded outward
//    translate([0, +logo_face_offset, logo_z])
//
//  -Y face (REAR):
//    rotate([90,0,180]) → text faces -Y, readable from outside
//    translate([0, -logo_face_offset, logo_z])
//
//  +X face (RIGHT):
//    rotate([90,0,90]) → text faces +X
//    translate([+logo_face_offset, 0, logo_z])
//
//  -X face (LEFT):
//    rotate([90,0,-90]) → text faces -X, readable from outside
//    translate([-logo_face_offset, 0, logo_z])
// ============================================================
module logo_text_2d() {
    text(logo_text,
         size     = logo_size,
         font     = "Liberation Sans:style=Bold",
         halign   = "center",
         valign   = "center");
}

module visnat_side_text_all() {

    color([1, 1, 1])   // white

    union() {

        // ── FRONT face  (+Y, normal pointing +Y) ──────────────
        translate([0, logo_face_offset, logo_z])
            rotate([90, 0, 0])
                linear_extrude(height = logo_depth)
                    logo_text_2d();

        // ── REAR face  (-Y, normal pointing -Y) ───────────────
        // rotate 180° around Z so text reads correctly from outside
        translate([0, -logo_face_offset, logo_z])
            rotate([90, 0, 180])
                linear_extrude(height = logo_depth)
                    logo_text_2d();

        // ── RIGHT face  (+X, normal pointing +X) ──────────────
        translate([logo_face_offset, 0, logo_z])
            rotate([90, 0, 90])
                linear_extrude(height = logo_depth)
                    logo_text_2d();

        // ── LEFT face  (-X, normal pointing -X) ───────────────
        translate([-logo_face_offset, 0, logo_z])
            rotate([90, 0, -90])
                linear_extrude(height = logo_depth)
                    logo_text_2d();
    }
}

// ============================================================
// CHASSIS BODY – octagonal sealed style
// ============================================================
module chassis_body_only() {
    color([0.75,0.75,0.78])
    union() {

        // Bottom octagonal frame ring
        translate([0,0,body_bottom_z])
            octagon_ring(body_length, body_width, oct_chamfer, frame_size, frame_size);

        // Top octagonal frame ring
        translate([0,0,body_top_z - frame_size])
            octagon_ring(body_length, body_width, oct_chamfer, frame_size, frame_size);

        // 8 vertical corner posts
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
                cylinder(h = body_height - 2*frame_size, d = post_d);

        // Internal deck plate
        translate([0, 0, deck_z])
            linear_extrude(height = deck_thick, center = true)
                offset(delta=-80)
                    octagon_2d(body_length, body_width, oct_chamfer);

        // Internal support beams
        translate([0, 0, deck_z + 18]) beam_x(body_length - 180, 24);
        translate([0, 0, deck_z + 18]) beam_y(body_width  - 180, 24);
        translate([0,  120, deck_z + 18]) beam_x(body_length - 220, 24);
        translate([0, -120, deck_z + 18]) beam_x(body_length - 220, 24);

        // Corner support brackets
        for (sx=[-1,1]) for (sy=[-1,1])
            translate([sx*170, sy*170, body_bottom_z + 55])
                rotate([0,0,45]) cube([45, 20, 70], center=true);

        // Sealed side panels on all 8 faces
        panel_pts = [
            [ body_length/2-oct_chamfer,  body_width/2],
            [-body_length/2+oct_chamfer,  body_width/2],
            [-body_length/2,              body_width/2-oct_chamfer],
            [-body_length/2,             -body_width/2+oct_chamfer],
            [-body_length/2+oct_chamfer, -body_width/2],
            [ body_length/2-oct_chamfer, -body_width/2],
            [ body_length/2,             -body_width/2+oct_chamfer],
            [ body_length/2,              body_width/2-oct_chamfer]
        ];

        for (i = [0:7]) {
            p1 = panel_pts[i];
            p2 = panel_pts[(i+1)%8];
            side_segment_panel(
                p1, p2,
                body_bottom_z + frame_size,
                body_height - 2*frame_size,
                side_panel_thick
            );
        }
    }
}

// ============================================================
// TOP PLATE
// ============================================================
module top_plate_only() {
    color([0.78,0.78,0.80])
    translate([0, 0, body_top_z]) {
        difference() {
            octagon_plate(body_length-2*plate_margin,
                          body_width -2*plate_margin,
                          oct_chamfer-8, plate_thick);

            for (x=[-210,-105,0,105,210])
                for (y=[-210,-105,0,105,210])
                    translate([x,y,-1]) cylinder(h=plate_thick+2, d=6.5);

            translate([main_mast_x,  aligned_y, -1])
                cylinder(h=plate_thick+2, d=mast_d+8);

            translate([screen_mast_x, aligned_y, -1])
                cylinder(h=plate_thick+2, d=screen_mast_r*2+8);
        }
        // Perimeter bolt heads
        color([0.50,0.50,0.53])
        for (i=[-4:4]) for (s=[-1,1]) {
            translate([i*58, s*(body_width/2-plate_margin-14), plate_thick])
                cylinder(d=5, h=3.5);
            translate([s*(body_length/2-plate_margin-14), i*58, plate_thick])
                cylinder(d=5, h=3.5);
        }
    }
}

// ============================================================
// BATTERY
// ============================================================
module battery_pack_only() {
    color([0.30,0.30,0.32])
    translate([0, 10, deck_z + deck_thick/2 + bat_h/2 + 6])
        rounded_box(bat_l, bat_w, bat_h, 10);
}

// ============================================================
// EMERGENCY STOP
// ============================================================
module emergency_stop_only() {
    ez = body_top_z + plate_thick;
    color("gold")
    translate([estop_x, estop_y, ez])
        rounded_box(68, 52, 18, 6);
    color("red")
    translate([estop_x, estop_y, ez+18]) {
        cylinder(d=42, h=13);
        translate([0,0,9]) sphere(d=44);
    }
    color([0.28,0.28,0.28])
    translate([estop_x, estop_y, ez+10]) cylinder(d=14, h=14);
}

// ============================================================
// BUCKET HOLDER
// ============================================================
module bucket_holder_only() {
    base_z = body_top_z + plate_thick;
    color([0.60,0.62,0.65])
    translate([bucket_holder_x, aligned_y, base_z]) {
        difference() {
            cylinder(d=bucket_holder_d, h=bucket_holder_h);
            translate([0,0,4]) cylinder(d=bucket_d, h=bucket_recess_h+2);
        }
    }
}

// ============================================================
// FULL CHASSIS (body + plate + internals + logo)
// ============================================================
module chassis_complete() {
    chassis_body_only();
    top_plate_only();
    battery_pack_only();
    emergency_stop_only();
    bucket_holder_only();
    visnat_side_text_all();   // ← white logo on all 4 long sides
}

// ============================================================
// CENTRAL MAST
// ============================================================
module mast_only() {
    mz = body_top_z + plate_thick;   // = 312

    // Square collar
    color([0.18,0.18,0.20])
    translate([main_mast_x, aligned_y, mz]) {
        difference() {
            rounded_box(mast_collar_w, mast_collar_w, mast_collar_h, 8);
            translate([0,0,-1]) cylinder(h=mast_collar_h+2, d=mast_d-4);
        }
    }

    // Hazard ring
    hz = mz + mast_collar_h;
    color("gold")
    translate([main_mast_x, aligned_y, hz]) {
        difference() {
            cylinder(d=mast_d+34, h=16);
            translate([0,0,-1]) cylinder(d=mast_d+2, h=18);
        }
    }
    color("black")
    translate([main_mast_x, aligned_y, hz])
        for (i=[0:7])
            rotate([0,0,i*45])
                translate([mast_d/2+14, 0, 8])
                    rotate([90,45,0]) cube([14,20,12], center=true);

    // Main column
    cz = hz + 16;
    color([0.76,0.76,0.78])
    translate([main_mast_x, aligned_y, cz])
        cylinder(d=mast_d, h=mast_h);

    // Mid-collar ring
    color([0.54,0.54,0.57])
    translate([main_mast_x, aligned_y, cz + mast_h*0.40])
        difference() {
            cylinder(d=mast_d+20, h=18);
            translate([0,0,-1]) cylinder(d=mast_d-2, h=20);
        }

    // Top plate
    color([0.18,0.18,0.20])
    translate([main_mast_x, aligned_y, cz + mast_h]) {
        difference() {
            rounded_box(mast_top_w, mast_top_w, mast_top_h, 8);
            for (x=[-48,48]) for (y=[-48,48])
                translate([x,y,-1]) cylinder(h=mast_top_h+2, d=9);
            translate([0,0,-1]) cylinder(h=mast_top_h+2, d=mast_d-6);
        }
        translate([0,0,mast_top_h]) cylinder(d=mast_d*0.52, h=12);
    }
}

// ============================================================
// SCREEN PLATFORM + SCREEN
// ============================================================
module screen_system_only() {
    base_z = body_top_z + plate_thick;
    sx = screen_mast_x;

    color([0.72,0.72,0.74])
    translate([sx, aligned_y, base_z])
        cylinder(h=screen_mast_h, r=screen_mast_r);

    color([0.60,0.62,0.65])
    translate([sx, aligned_y, base_z+screen_mast_h])
        cylinder(h=30, r1=24, r2=20);

    color([0.65,0.65,0.67])
    translate([sx, aligned_y, base_z+screen_mast_h-110])
        cube([24, 90, 110], center=true);

    // Screen glass
    color([0.20, 0.40, 0.80, 0.70])
    translate([sx-35, aligned_y, base_z+screen_mast_h-110])
        rotate([90,0,90])
            cube([screen_w, screen_h, screen_t], center=true);

    // Screen bezel
    color([0.15,0.15,0.17])
    translate([sx-42, aligned_y, base_z+screen_mast_h-110])
        rotate([90,0,90])
            difference() {
                cube([screen_w+18, screen_h+18, 10], center=true);
                cube([screen_w-8,  screen_h-8,  12], center=true);
            }
}

// ============================================================
// MECANUM WHEEL
// angle_dir = +1 or -1 controls roller slant
// ============================================================
module wheel_only(angle_dir=1) {
    rotate([90,0,0]) {
        color([0.10,0.10,0.10])
        difference() {
            cylinder(d=wheel_diameter, h=wheel_width, center=true);
            cylinder(d=wheel_diameter-36, h=wheel_width+2, center=true);
        }
        color([0.55,0.57,0.60])
        cylinder(d=wheel_diameter-40, h=wheel_width-16, center=true);
        color([0.42,0.44,0.47])
        cylinder(d=46, h=wheel_width+8, center=true);
        color([0.52,0.54,0.57])
        difference() {
            cylinder(d=62, h=wheel_width+4, center=true);
            cylinder(d=46, h=wheel_width+6, center=true);
        }
        color([0.08,0.08,0.08])
        for (a=[0:45:315])
            rotate([0,0,a])
                translate([wheel_diameter/2-16, 0, 0])
                    rotate([0, angle_dir*45, 0])
                        scale([1,1,1.35])
                            cylinder(d=18, h=wheel_width-2, center=true);
    }
}

// ============================================================
// MOTOR
// Axis along Z; caller rotates to match face normal direction
// ============================================================
module motor_only() {
    color([0.28,0.28,0.30])
    translate([0,0,-gbox_l/2]) cylinder(d=gbox_d, h=gbox_l, center=true);

    color([0.20,0.20,0.22])
    translate([0,0,mot_l/2])   cylinder(d=mot_d,  h=mot_l,  center=true);

    color([0.16,0.16,0.18])
    translate([0,0,mot_l])     cylinder(d=mot_d-8, h=14,    center=true);

    color([0.60,0.62,0.65])
    translate([0,0,-gbox_l-14]) cylinder(d=16,    h=28,     center=true);

    color([0.33,0.33,0.35])
    difference() {
        cylinder(d=gbox_d+20, h=11, center=true);
        cylinder(d=gbox_d-4,  h=13, center=true);
        for (a=[0,90,180,270])
            rotate([0,0,a]) translate([gbox_d/2+6,0,0])
                cylinder(d=8, h=13, center=true);
    }

    color([0.24,0.24,0.26])
    for (a=[0:30:359])
        rotate([0,0,a])
            translate([mot_d/2+2, 0, -mot_l*0.3])
                cube([4,3,mot_l*0.5], center=true);

    color([0.14,0.14,0.16])
    translate([0,0,-mot_l-14]) cylinder(d=mot_d-18, h=16, center=true);
}

// ============================================================
// SPRING
// ============================================================
module spring_only(h=46) {
    color([0.68,0.68,0.70])
    translate([0,0,-6]) cylinder(d=10, h=h+18);

    color([0.52,0.52,0.55])
    translate([0,0,h-2]) cylinder(d=15, h=24);

    color([0.85,0.72,0.10])
    for (i=[0:spr_coils-1])
        translate([0,0,i*(h/spr_coils)])
            rotate_extrude(angle=385, $fn=44)
                translate([spr_od/2,0]) circle(r=spr_wire);

    color([0.48,0.48,0.50]) {
        translate([0,0,-5])   cylinder(d=spr_od+8, h=7);
        translate([0,0,h-2])  cylinder(d=spr_od+8, h=7);
    }
    color([0.60,0.62,0.65])
    translate([-13,-9,h+4]) cube([26,18,20]);
}

// ============================================================
// POSITIONED ASSEMBLY PARTS
// Wheels on the four SHORT CHAMFERED DIAGONAL faces
// nx, ny = outward unit normal of that chamfered face
// ============================================================

module motor_at(x, y, nx, ny, rotz) {
    motor_offset = 78;
    mx = x - nx * motor_offset;
    my = y - ny * motor_offset;

    // Rotate the motor so its axis points along the face normal (nx,ny)
    face_angle = atan2(ny, nx);

    translate([mx, my, axle_z])
        rotate([0, 0, face_angle])      // align motor axis with face normal
            rotate([90, 0, 0])           // tilt from Z to XY plane
                motor_only();
}

module spring_at(x, y, nx, ny) {
    spring_offset = 42;
    spx = x - nx * spring_offset;
    spy = y - ny * spring_offset;

    spz_lo = axle_z + 12;
    spz_hi = body_bottom_z + 8;
    sp_h   = spz_hi - spz_lo;

    translate([spx, spy, spz_lo])
        spring_only(sp_h);
}

// One complete corner: wheel + motor + spring
module wheel_corner_module(x, y, rotz, hand, nx, ny) {
    translate([x, y, axle_z])
        rotate([0, 0, rotz])
            wheel_only(hand);

    motor_at(x, y, nx, ny, rotz);
    spring_at(x, y, nx, ny);
}

// ============================================================
// FULL PREVIEW ASSEMBLY
// ============================================================
module full_robot_preview() {

    chassis_complete();
    mast_only();
    screen_system_only();

    // ── Four mecanum wheels on the short chamfered corner faces ──
    //
    //  Corner positions: wheel_corner_c from centre along each diagonal
    //  Face normals point diagonally outward at 45°
    //
    //  Mecanum X-pattern handedness (for omnidirectional drive):
    //    NE (+x,+y)  ╲   angle_dir = +1
    //    NW (-x,+y)  ╱   angle_dir = -1
    //    SW (-x,-y)  ╲   angle_dir = +1
    //    SE (+x,-y)  ╱   angle_dir = -1

    // NE corner  (face normal = +X+Y diagonal, normalised)
    wheel_corner_module(
         wheel_corner_c,  wheel_corner_c,  // wheel XY position
        -45,                               // wheel rotation (aligns tyre with chamfer)
         1,                                // mecanum handedness
         1/sqrt(2),  1/sqrt(2)            // face normal (nx, ny)
    );

    // NW corner
    wheel_corner_module(
        -wheel_corner_c,  wheel_corner_c,
         45,
        -1,
        -1/sqrt(2),  1/sqrt(2)
    );

    // SW corner
    wheel_corner_module(
        -wheel_corner_c, -wheel_corner_c,
        -45,
         1,
        -1/sqrt(2), -1/sqrt(2)
    );

    // SE corner
    wheel_corner_module(
         wheel_corner_c, -wheel_corner_c,
         45,
        -1,
         1/sqrt(2), -1/sqrt(2)
    );
}

// ============================================================
// RENDER
// ============================================================
full_robot_preview();

// ============================================================
// DIMENSION SUMMARY
// ============================================================
// Body footprint         : 610 × 610 mm (octagonal, chamfer=120)
// Long flat face width   : 370 mm (4 faces, logo applied here)
// Body height            : 180 mm
// Ground clearance       : 120 mm
// Wheel diameter         : 180 mm
// Axle height            : 90 mm
// Overall height         : ~550 mm (body top + mast)
// Logo text              : V.I.S.N.A.T  size=36 mm  depth=3.5 mm
// Logo Z centre          : 210 mm  (mid-height of chassis panels)
// Logo on faces          : +Y (front), -Y (rear), +X (right), -X (left)
// ============================================================
