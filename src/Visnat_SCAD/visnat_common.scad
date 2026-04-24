$fn = 96;

// ============================================================
// VISNAT MOBILE PLATFORM - SEALED SQUARE CHASSIS + CLASSIC WHEELS
// Manipulator scaled up from inches -> cm style correction
// Chassis fully covered from all sides
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
axle_z           = wheel_radius;

body_bottom_z    = ground_clearance;
body_top_z       = body_bottom_z + body_height;

// classic side wheel locations
wheel_x          = body_length/2 - 42;
wheel_y          = body_width/2 + wheel_width/2 + 16;

// top plate
plate_thick      = 12;
plate_margin     = 6;

// manipulator anchor position
main_mast_x      = -35;
aligned_y        = 0;

// ============================================================
// STL manipulator import settings
// IMPORTANT: STL is assumed to have been modelled in inches
// We therefore apply 2.54x correction to match cm-style sizing
// ============================================================
manipulator_file        = "Manipulator.stl";
manipulator_base_scale  = 0.35;      // previous fitted visual scale
manipulator_unit_scale  = 2.54;      // inches -> cm correction
manipulator_scale       = manipulator_base_scale * manipulator_unit_scale;

manipulator_rot_x       = 0;
manipulator_rot_y       = 0;
manipulator_rot_z       = 0;

// clip away lower pedestal/box from STL
manipulator_cut_z       = 0;

// optional XY fine tune
manipulator_offset_x    = 0;
manipulator_offset_y    = 0;

// mounting adapter to attach manipulator to chassis
manipulator_adapter_d   = 90;
manipulator_adapter_h   = 16;

// aligned layout positions
screen_mast_x    = -180;
bucket_holder_x  = 140;

// battery
bat_l = 300;
bat_w = 155;
bat_h = 70;

// e-stop
estop_x = -190;
estop_y = 200;

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

// access flap
flap_w           = 120;
flap_h           = 78;
flap_t           = 5;
flap_x           = -120;
flap_y           = 150;
flap_corner_r    = 12;
flap_recess_gap  = 6;

// internal deck
deck_thick       = 8;
deck_z           = body_bottom_z + 32;

// logo text parameters
logo_text          = "V.I.S.N.A.T";
logo_size          = 36;
logo_depth         = 3.5;
logo_z             = body_bottom_z + body_height * 0.50;
logo_face_offset_x = body_length/2 + 4.2;
logo_face_offset_y = body_width/2  + 4.2;

// ---------------- Helpers ----------------
module rounded_box(l, w, h, r) {
    hull()
        for (x = [-l/2 + r, l/2 - r], y = [-w/2 + r, w/2 - r])
            translate([x, y, 0]) cylinder(h = h, r = r);
}

module rounded_rect_2d(l, w, r) {
    hull()
        for (x = [-l/2 + r, l/2 - r], y = [-w/2 + r, w/2 - r])
            translate([x, y]) circle(r = r);
}

module box_shell(l, w, h, r, wall) {
    difference() {
        rounded_box(l, w, h, r);
        translate([0, 0, wall])
            rounded_box(l - 2*wall, w - 2*wall, h, max(r - wall, 2));
    }
}

// ============================================================
// V.I.S.N.A.T LOGO
// ============================================================
module logo_text_2d() {
    text(logo_text,
         size   = logo_size,
         font   = "Liberation Sans:style=Bold",
         halign = "center",
         valign = "center");
}

module visnat_side_text_all() {
    color([1, 1, 1])
    union() {
        // front +Y
        translate([0, logo_face_offset_y, logo_z])
            rotate([90, 0, 0])
                linear_extrude(height = logo_depth)
                    logo_text_2d();

        // rear -Y
        translate([0, -logo_face_offset_y, logo_z])
            rotate([90, 0, 180])
                linear_extrude(height = logo_depth)
                    logo_text_2d();

        // right +X
        translate([logo_face_offset_x, 0, logo_z])
            rotate([90, 0, 90])
                linear_extrude(height = logo_depth)
                    logo_text_2d();

        // left -X
        translate([-logo_face_offset_x, 0, logo_z])
            rotate([90, 0, -90])
                linear_extrude(height = logo_depth)
                    logo_text_2d();
    }
}

// ============================================================
// CHASSIS BODY - FULLY SEALED SQUARE STYLE
// ============================================================
module chassis_body_only() {
    color([0.75,0.75,0.78])
    translate([0, 0, body_bottom_z]) {
        // sealed outer body with NO side openings
        box_shell(body_length, body_width, body_height, body_corner_r, body_wall);

        // internal lower deck
        color([0.38,0.38,0.40])
        translate([0, 0, 30])
            rounded_box(body_length - 90, body_width - 90, deck_thick, 12);
    }
}

// ============================================================
// TOP PLATE
// ============================================================
module top_plate_only() {
    color([0.78,0.78,0.80])
    translate([0, 0, body_top_z]) {
        difference() {
            rounded_box(body_length - 2*plate_margin,
                        body_width  - 2*plate_margin,
                        plate_thick,
                        body_corner_r - 4);

            for (x=[-210,-105,0,105,210])
                for (y=[-210,-105,0,105,210])
                    translate([x,y,-1]) cylinder(h=plate_thick+2, d=6.5);

            // screen mast hole
            translate([screen_mast_x, aligned_y, -1])
                cylinder(h=plate_thick+2, d=screen_mast_r*2+8);

            // manipulator locating hole
            translate([main_mast_x, aligned_y, -1])
                cylinder(h=plate_thick+2, d=70);

            // flap opening
            translate([flap_x, flap_y, -1])
                linear_extrude(height = plate_thick + 2)
                    rounded_rect_2d(flap_w - flap_recess_gap,
                                    flap_h - flap_recess_gap,
                                    flap_corner_r - 2);
        }

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
// ACCESS FLAP
// ============================================================
module access_flap_only() {
    flap_z = body_top_z + plate_thick + 0.4;

    color([1,1,1])
    translate([flap_x, flap_y, flap_z])
        linear_extrude(height = flap_t)
            rounded_rect_2d(flap_w, flap_h, flap_corner_r);

    color([0.85,0.85,0.87])
    for (xx = [-20, 20])
        translate([flap_x + xx, flap_y + flap_h/2 - 8, flap_z + flap_t/2])
            cube([10, 8, flap_t + 2], center=true);
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
// MANIPULATOR ADAPTER
// ============================================================
module manipulator_adapter_only() {
    color([0.45,0.45,0.48])
    translate([main_mast_x + manipulator_offset_x,
               aligned_y   + manipulator_offset_y,
               body_top_z + plate_thick])
        cylinder(d = manipulator_adapter_d, h = manipulator_adapter_h);
}

// ============================================================
// IMPORTED MANIPULATOR STL
// ============================================================
module manipulator_stl_only() {
    color([0.55,0.55,0.58])
    translate([main_mast_x + manipulator_offset_x,
               aligned_y   + manipulator_offset_y,
               body_top_z + plate_thick + manipulator_adapter_h])
        rotate([manipulator_rot_x, manipulator_rot_y, manipulator_rot_z])
            scale([manipulator_scale, manipulator_scale, manipulator_scale])
                intersection() {
                    import(manipulator_file, convexity=20);
                    translate([-2000, -2000, manipulator_cut_z])
                        cube([4000, 4000, 4000]);
                }
}

// ============================================================
// FULL CHASSIS
// ============================================================
module chassis_complete() {
    chassis_body_only();
    top_plate_only();
    battery_pack_only();
    emergency_stop_only();
    bucket_holder_only();
    access_flap_only();
    visnat_side_text_all();
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

    color([0.20, 0.40, 0.80, 0.70])
    translate([sx-35, aligned_y, base_z+screen_mast_h-110])
        rotate([90,0,90])
            cube([screen_w, screen_h, screen_t], center=true);

    color([0.15,0.15,0.17])
    translate([sx-42, aligned_y, base_z+screen_mast_h-110])
        rotate([90,0,90])
            difference() {
                cube([screen_w+18, screen_h+18, 10], center=true);
                cube([screen_w-8,  screen_h-8,  12], center=true);
            }
}

// ============================================================
// CLASSIC RUBBER WHEEL
// ============================================================
module wheel_only() {
    rotate([90,0,0]) {
        color([0.10,0.10,0.10])
        difference() {
            cylinder(d=wheel_diameter, h=wheel_width, center=true);
            cylinder(d=wheel_diameter-28, h=wheel_width+2, center=true);
        }

        color([0.12,0.12,0.12])
        cylinder(d=wheel_diameter-20, h=wheel_width-10, center=true);

        color([0.58,0.60,0.63])
        cylinder(d=wheel_diameter-42, h=wheel_width-14, center=true);

        color([0.50,0.52,0.55])
        for (a=[0:60:359])
            rotate([0,0,a])
                translate([(wheel_diameter/2-22)/2, 0, 0])
                    cube([wheel_diameter/2-22, 10, wheel_width-18], center=true);

        color([0.42,0.44,0.47])
        cylinder(d=46, h=wheel_width+8, center=true);

        color([0.52,0.54,0.57])
        difference() {
            cylinder(d=62, h=wheel_width+4, center=true);
            cylinder(d=46, h=wheel_width+6, center=true);
        }

        color([0.07,0.07,0.07])
        for (i=[-3:3])
            translate([0,0,i*6])
                rotate_extrude()
                    translate([wheel_diameter/2-6,0])
                        square([5,2], center=true);
    }
}

// ============================================================
// MOTOR
// ============================================================
module motor_only() {
    color([0.28,0.28,0.30])
    translate([0,0,-gbox_l/2]) cylinder(d=gbox_d, h=gbox_l, center=true);

    color([0.20,0.20,0.22])
    translate([0,0,mot_l/2]) cylinder(d=mot_d, h=mot_l, center=true);

    color([0.16,0.16,0.18])
    translate([0,0,mot_l]) cylinder(d=mot_d-8, h=14, center=true);

    color([0.60,0.62,0.65])
    translate([0,0,-gbox_l-14]) cylinder(d=16, h=28, center=true);

    color([0.33,0.33,0.35])
    difference() {
        cylinder(d=gbox_d+20, h=11, center=true);
        cylinder(d=gbox_d-4, h=13, center=true);
        for (a=[0,90,180,270])
            rotate([0,0,a]) translate([gbox_d/2+6,0,0])
                cylinder(d=8, h=13, center=true);
    }
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
        translate([0,0,-5]) cylinder(d=spr_od+8, h=7);
        translate([0,0,h-2]) cylinder(d=spr_od+8, h=7);
    }

    color([0.60,0.62,0.65])
    translate([-13,-9,h+4]) cube([26,18,20]);
}

// ============================================================
// POSITIONED ASSEMBLY PARTS - CLASSIC SIDE WHEELS
// ============================================================
module motor_at(x, y) {
    sy = y >= 0 ? 1 : -1;
    motor_y = y - sy * (wheel_width/2 + gbox_l + mot_l/2 + 4);

    translate([x, motor_y, axle_z])
        rotate([90,0,0])
            motor_only();
}

module spring_at(x, y) {
    sy = y >= 0 ? 1 : -1;

    spx = x;
    spy = y - sy * (wheel_width/2 + 12);

    spz_lo = axle_z + 12;
    spz_hi = body_bottom_z + 8;
    sp_h   = spz_hi - spz_lo;

    translate([spx, spy, spz_lo])
        spring_only(sp_h);
}

module wheel_side_module(x, y) {
    translate([x, y, axle_z])
        wheel_only();

    motor_at(x, y);
    spring_at(x, y);
}

// ============================================================
// FULL PREVIEW ASSEMBLY
// ============================================================
module full_robot_preview() {
    chassis_complete();
    screen_system_only();
    manipulator_adapter_only();
    manipulator_stl_only();

    wheel_side_module( wheel_x,  wheel_y);
    wheel_side_module(-wheel_x,  wheel_y);
    wheel_side_module( wheel_x, -wheel_y);
    wheel_side_module(-wheel_x, -wheel_y);
}

// ============================================================
// NOTE
// No automatic render call here.
// Use separate files with:
//   use <visnat_common.scad>
//   chassis_complete();
//   motor_only();
//   spring_only();
//   wheel_only();
//   screen_system_only();
//   access_flap_only();
//   manipulator_adapter_only();
//   manipulator_stl_only();
// ============================================================