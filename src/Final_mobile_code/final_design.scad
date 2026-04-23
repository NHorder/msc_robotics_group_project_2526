$fn = 96;
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

wheel_x          = body_length/2 - 42;
wheel_y          = body_width/2 + wheel_width/2 + 16;

plate_thick      = 12;
plate_margin     = 6;


// ============================================================
// Tank geometry
// ============================================================
tank_l        = 280;
tank_w        = 200;
tank_h        = 220;
tank_wall_t   = 6;
tank_corner_r = 18;


// ============================================================
// Layout positions
// ============================================================
main_mast_x      = 0;
main_mast_y      = 0;

screen_mast_x    = -240;
screen_mast_y    = 0;

// Main tank
tank_x           = 150;
tank_y           = -165;

// Second tank
aux_tank_l        = 280;
aux_tank_w        = 200;
aux_tank_h        = tank_h;
aux_tank_wall_t   = tank_wall_t;
aux_tank_corner_r = 14;

tank_gap          = 26;

// Auto-position second tank to the left of main tank
aux_tank_x        = tank_x - (tank_l/2 + aux_tank_l/2 + tank_gap);
aux_tank_y        = tank_y;

// Joining mast between tanks
join_mast_h       = tank_h;
join_mast_l       = 34;
join_mast_w       = min(tank_w, aux_tank_w) - 14;
join_mast_r       = 8;

join_mast_x       = (tank_x - tank_l/2 + aux_tank_x + aux_tank_l/2) / 2;
join_mast_y       = (tank_y + aux_tank_y) / 2;

// Top bridge joining both tanks
join_bridge_t     = 18;
join_bridge_l     = (tank_x - tank_l/2) - (aux_tank_x + aux_tank_l/2);
join_bridge_w     = min(tank_w, aux_tank_w) - 22;


// ============================================================
// LiDAR positions
// ============================================================
lidar_plate_z    = body_top_z + plate_thick;

// LiDAR 1 remains on top plate
lidar1_x         = 0;
lidar1_y         = 240;
lidar1_z         = lidar_plate_z;
lidar1_rot_z     = 0;

// LiDAR 2 moves to top of joining mast
lidar2_x         = join_mast_x;
lidar2_y         = join_mast_y;
lidar2_z         = body_top_z + plate_thick + join_mast_h + join_bridge_t;
lidar2_rot_z     = 0;


// battery
bat_l = 300;
bat_w = 155;
bat_h = 70;

// e-stop
estop_x = -165;
estop_y = -999;
estop_z = 250;

// spring
spr_od    = 30;
spr_wire  = 3.5;
spr_coils = 6;

// motor
mot_d  = 56;
mot_l  = 72;
gbox_d = 64;
gbox_l = 34;

// screen mast + screen
screen_mast_h = 1050;
screen_mast_r = 40;
screen_w      = 205;
screen_h      = 230;
screen_t      = 14;

// access flap
flap_w           = 150;
flap_h           = 90;
flap_t           = 5;
flap_x           = -95;
flap_y           = 135;
flap_corner_r    = 12;
flap_recess_gap  = 6;

// internal deck
deck_thick = 8;
deck_z     = body_bottom_z + 32;

// logo
logo_text          = "V.I.S.N.A.T";
logo_size          = 36;
logo_depth         = 3.5;
logo_z             = body_bottom_z + body_height * 0.50;
logo_face_offset_x = body_length/2 + 4.2;
logo_face_offset_y = body_width/2  + 4.2;

// manipulator
manipulator_file        = "Manipulator_repaired.stl";
manipulator_scale       = 1.0;
manipulator_fit_scale   = 8;

manipulator_rot_x       = 0;
manipulator_rot_y       = 0;
manipulator_rot_z       = 0;

manipulator_offset_x    = -120;
manipulator_offset_y    = -500;

manipulator_adapter_d   = 90;
manipulator_adapter_h   = 16;


// ============================================================
// Colour palette
// ============================================================
col_body        = [0.92, 0.93, 0.95];
col_top         = [0.96, 0.97, 0.98];
col_trim        = [0.78, 0.83, 0.88];
col_tank_pad    = [0.68, 0.72, 0.76];
col_dark        = [0.30, 0.34, 0.40];
col_metal       = [0.55, 0.58, 0.63];
col_screen      = [0.14, 0.32, 0.68, 0.75];
col_bezel       = [0.12, 0.14, 0.16];
col_bumper      = [0.95, 0.42, 0.36];
col_wheel       = [0.10, 0.10, 0.12];
col_hub         = [0.55, 0.58, 0.63];
col_spoke       = [0.68, 0.70, 0.74];
col_flap        = [0.75, 0.75, 0.75];
col_logo        = [0.1, 0.1, 0.1];
col_adapter     = [0.65,0.69,0.74];
col_manipulator = [0.63,0.66,0.70];
col_lidar_body  = [0.18,0.20,0.22];
col_lidar_top   = [0.30,0.34,0.38];
col_lidar_glass = [0.10,0.45,0.65];
col_rs_body     = [0.82,0.84,0.86];
col_rs_face     = [0.20,0.22,0.25];
col_rs_glass    = [0.10,0.38,0.62];
col_tank_body   = [0.92, 0.95, 0.98, 0.82];


// ============================================================
// HELPERS
// ============================================================
module rounded_box(l, w, h, r) {
    hull() {
        for (x = [-l/2 + r, l/2 - r], y = [-w/2 + r, w/2 - r])
            translate([x, y, 0]) cylinder(h = h, r = r);
    }
}

module rounded_rect_2d(l, w, r) {
    hull() {
        for (x = [-l/2 + r, l/2 - r], y = [-w/2 + r, w/2 - r])
            translate([x, y]) circle(r = r);
    }
}

module box_shell(l, w, h, r, wall) {
    difference() {
        rounded_box(l, w, h, r);
        translate([0,0,wall])
            rounded_box(l - 2*wall, w - 2*wall, h, max(r - wall, 2));
    }
}


// ============================================================
// LOGO
// ============================================================
module logo_text_2d() {
    text(
        logo_text,
        size = logo_size,
        font = "Liberation Sans:style=Bold",
        halign = "center",
        valign = "center"
    );
}

module visnat_side_text_all() {
    color(col_logo)
    union() {
        translate([0, -logo_face_offset_y, logo_z])
            rotate([90,0,0])
                linear_extrude(height = logo_depth+4.0)
                    logo_text_2d();

        translate([0, logo_face_offset_y, logo_z])
            rotate([90,0,180])
                linear_extrude(height = logo_depth)
                    logo_text_2d();

        translate([logo_face_offset_x, 0, logo_z])
            rotate([90,0,90])
                linear_extrude(height = logo_depth)
                    logo_text_2d();

        translate([-logo_face_offset_x, 0, logo_z])
            rotate([90,0,-90])
                linear_extrude(height = logo_depth)
                    logo_text_2d();
    }
}


// ============================================================
// CHASSIS BODY
// ============================================================
module chassis_body_only() {
    color(col_body)
    translate([0,0,body_bottom_z]) {
        box_shell(body_length, body_width, body_height, body_corner_r, body_wall);

        color([0.82,0.84,0.87])
        translate([0,0,30])
            rounded_box(body_length - 90, body_width - 90, deck_thick, 12);
    }
}


// ============================================================
// TOP PLATE
// ============================================================
module top_plate_only() {
    color(col_top)
    translate([0,0,body_top_z]) {
        difference() {
            rounded_box(
                body_length - 2*plate_margin,
                body_width  - 2*plate_margin,
                plate_thick,
                body_corner_r - 4
            );

            for (x = [-210,-105,0,105,210])
                for (y = [-210,-105,0,105,210])
                    translate([x,y,-1]) cylinder(h = plate_thick + 2, d = 6.5);

            translate([screen_mast_x, screen_mast_y, -1])
                cylinder(h = plate_thick + 2, d = screen_mast_r*2 + 8);

            translate([main_mast_x, main_mast_y, -1])
                cylinder(h = plate_thick + 2, d = 70);

            translate([flap_x, flap_y, -1])
                linear_extrude(height = plate_thick + 2)
                    rounded_rect_2d(
                        flap_w - flap_recess_gap,
                        flap_h - flap_recess_gap,
                        flap_corner_r - 2
                    );

            translate([lidar1_x, lidar1_y, plate_thick - 5])
                rounded_box(58, 58, 8, 6);
        }

        color(col_metal)
        for (i = [-4:4])
            for (s = [-1,1]) {
                translate([i*58, s*(body_width/2 - plate_margin - 14), plate_thick])
                    cylinder(d = 5, h = 3.5);

                translate([s*(body_length/2 - plate_margin - 14), i*58, plate_thick])
                    cylinder(d = 5, h = 3.5);
            }
    }
}


// ============================================================
// ACCESS FLAP
// ============================================================
module access_flap_only() {
    flap_z = body_top_z + plate_thick + 0.6;

    color(col_flap)
    translate([flap_x, flap_y, flap_z])
        linear_extrude(height = flap_t+3.0)
            rounded_rect_2d(flap_w, flap_h, flap_corner_r);

    color([0,0,0])
    translate([flap_x, flap_y, flap_z+flap_t])
        linear_extrude(height=3.0)
            difference() {
                rounded_rect_2d(flap_w+6, flap_h+6, flap_corner_r+2);
                rounded_rect_2d(flap_w-8, flap_h-8, flap_corner_r-2);
            }

    color([0.55,0.58,0.63])
    translate([flap_x, flap_y + flap_h/2 - 16, flap_z + flap_t + 1.5])
        rounded_box(32, 10, 8, 3);
}


// ============================================================
// BATTERY
// ============================================================
module battery_pack_only() {
    color([0.25,0.27,0.30])
    translate([0, 10, deck_z + deck_thick/2 + bat_h/2 + 6])
        rounded_box(bat_l, bat_w, bat_h, 10);
}


// ============================================================
// EMERGENCY STOP
// ============================================================
module emergency_stop_only() {
    ex     = estop_x;
    ey     = -(body_width/2);
    ez_mid = body_bottom_z + body_height * 0.85;

    color([0.92, 0.75, 0.18])
    translate([ex, ey - 9, ez_mid])
        rotate([90, 0, 0])
            rounded_box(72, 56, 18, 7);

    color([0.90, 0.14, 0.14])
    translate([ex, ey - 22, ez_mid]) {
        rotate([90, 0, 0]) cylinder(d = 42, h = 14, $fn = 36);
        translate([0, -12, 0]) sphere(d = 46, $fn = 36);
    }

    color([0.25, 0.25, 0.25])
    translate([ex, ey - 12, ez_mid])
        rotate([90, 0, 0]) cylinder(d = 14, h = 16, $fn = 24);

    color([0.70, 0.72, 0.76])
    translate([ex, ey, ez_mid])
        rotate([90, 0, 0])
            rounded_box(82, 66, 5, 8);

    color([0.12, 0.12, 0.14])
    translate([ex, ey - 18.5, ez_mid - 20])
        rotate([90, 0, 0])
            linear_extrude(height = 1.8)
                text(
                    "E-STOP",
                    size = 8,
                    font = "Liberation Sans:style=Bold",
                    halign = "center",
                    valign = "center"
                );
}


// ============================================================
// GENERIC SWAPPABLE TANK
// ============================================================
module swappable_tank_at(tx, ty, tl, tw, th, wall_t, corner_r, label_main="PAINT", label_vol="40 L") {
    base_z = body_top_z + plate_thick + 6;

    color(col_tank_body)
    translate([tx, ty, base_z])
        difference() {
            rounded_box(tl, tw, th, corner_r);
            translate([0, 0, wall_t])
                rounded_box(
                    tl - 2*wall_t,
                    tw - 2*wall_t,
                    th,
                    max(corner_r - 3, 3)
                );
        }

    color([0.75, 0.78, 0.82])
    translate([tx, ty, base_z])
        rounded_box(tl + 8, tw + 8, wall_t + 2, corner_r + 2);

    color([0.40, 0.70, 0.90, 0.70])
    translate([tx + tl/2 - wall_t - 1, ty, base_z + th*0.10])
        rounded_box(6, 18, th*0.80, 3);

    color([0.30, 0.32, 0.36])
    translate([tx, ty + tw/4, base_z + th])
        cylinder(d = 44, h = 16, $fn = 32);

    color([0.50, 0.52, 0.56])
    translate([tx, ty + tw/4, base_z + th + 16])
        cylinder(d = 36, h = 7, $fn = 32);

    color([0.28, 0.30, 0.34])
    translate([tx + 18, ty + tw/4, base_z + th + 20])
        cylinder(d = 8, h = 10, $fn = 16);

    color([0.30, 0.32, 0.36])
    translate([tx, ty - tw/2 - 4, base_z + 34])
        rotate([90, 0, 0])
            cylinder(d = 26, h = 18, $fn = 24);

    color([0.22, 0.24, 0.28])
    translate([tx, ty - tw/2 - 22, base_z + 34])
        rotate([90, 0, 0])
            cylinder(d = 14, h = 12, $fn = 20);

    color([0.60, 0.63, 0.67])
    for (sy3 = [-1, 1]) {
        hy = ty + sy3 * (tw/2 + 6);

        translate([tx, hy, base_z + th * 0.72])
            rotate([90, 0, 0])
                rounded_box(tl * 0.45, 18, 12, 4);

        translate([tx - tl*0.16, hy, base_z + th * 0.65])
            rotate([90, 0, 0])
                rounded_box(12, 42, 10, 3);

        translate([tx + tl*0.16, hy, base_z + th * 0.65])
            rotate([90, 0, 0])
                rounded_box(12, 42, 10, 3);
    }

    color([0.45, 0.47, 0.52])
    for (lx = [-1,1], ly2 = [-1,1])
        translate([
            tx + lx*(tl/2 - 10),
            ty + ly2*(tw/2 - 10),
            base_z - 2
        ])
            cylinder(d = 18, h = 14, $fn = 20);

    color([1.0, 1.0, 1.0, 0.90])
    translate([tx, ty - tw/2 - 0.5, base_z + th * 0.38])
        rotate([90, 0, 0])
            linear_extrude(height = 2)
                rounded_rect_2d(tl * 0.52, th * 0.24, 6);

    color([0.15, 0.35, 0.65])
    translate([tx, ty - tw/2 - 3, base_z + th * 0.50])
        rotate([90, 0, 0])
            linear_extrude(height = 3)
                text(
                    label_vol,
                    size = 20,
                    font = "Liberation Sans:style=Bold",
                    halign = "center",
                    valign = "center"
                );

    color([0.20, 0.20, 0.22])
    translate([tx, ty - tw/2 - 3, base_z + th * 0.38])
        rotate([90, 0, 0])
            linear_extrude(height = 3)
                text(
                    label_main,
                    size = 11,
                    font = "Liberation Sans:style=Bold",
                    halign = "center",
                    valign = "center"
                );
}

module swappable_tank() {
    swappable_tank_at(
        tank_x, tank_y,
        tank_l, tank_w, tank_h,
        tank_wall_t, tank_corner_r,
        "PAINT", "40 L"
    );
}

module aux_swappable_tank() {
    swappable_tank_at(
        aux_tank_x, aux_tank_y,
        aux_tank_l, aux_tank_w, aux_tank_h,
        aux_tank_wall_t, aux_tank_corner_r,
        "PAINT", "40 L"
    );
}


// ============================================================
// JOINING MAST BETWEEN TANKS
// ============================================================
module tank_join_mast_only() {
    base_z = body_top_z + plate_thick + 6;

    color([0.70, 0.74, 0.79])
    translate([join_mast_x, join_mast_y, base_z])
        rounded_box(join_mast_l, join_mast_w, join_mast_h, join_mast_r);

    color([0.62, 0.66, 0.71])
    translate([
        (tank_x - tank_l/2 + aux_tank_x + aux_tank_l/2) / 2,
        join_mast_y,
        base_z + join_mast_h
    ])
        rounded_box(join_bridge_l + join_mast_l, join_bridge_w, join_bridge_t, 8);

    color([0.28, 0.30, 0.34])
    translate([
        (tank_x - tank_l/2 + aux_tank_x + aux_tank_l/2) / 2,
        join_mast_y,
        base_z + join_mast_h - 32
    ])
        rotate([0,90,0])
            cylinder(d = 18, h = join_bridge_l + join_mast_l, center = true, $fn = 28);
}


// ============================================================
// MANIPULATOR ADAPTER + STL
// ============================================================
module manipulator_adapter_only() {
    color(col_adapter)
    translate([
        main_mast_x + manipulator_offset_x,
        main_mast_y + manipulator_offset_y,
        body_top_z + plate_thick
    ])
        rounded_box(90, 70, manipulator_adapter_h, 10);
}

module manipulator_stl_only() {
    color(col_manipulator)
    render(convexity = 20)
    translate([
        main_mast_x + manipulator_offset_x,
        main_mast_y + manipulator_offset_y,
        body_top_z + plate_thick + manipulator_adapter_h
    ])
        rotate([manipulator_rot_x, manipulator_rot_y, manipulator_rot_z])
            scale([
                manipulator_scale * manipulator_fit_scale,
                manipulator_scale * manipulator_fit_scale,
                manipulator_scale * manipulator_fit_scale
            ])
                import(manipulator_file, convexity = 20);
}


// ============================================================
// LiDAR SENSOR MODULE
// ============================================================
module lidar_sensor_topplate() {
    color(col_lidar_body)
    rounded_box(54, 54, 18, 8);

    color(col_lidar_top)
    translate([0,0,18])
        cylinder(d = 42, h = 16, $fn = 48);

    color(col_lidar_glass)
    translate([0,0,20])
        difference() {
            cylinder(d = 38, h = 10, $fn = 48);
            cylinder(d = 30, h = 12, $fn = 48);
        }

    color([0.50,0.52,0.55])
    translate([0,0,30])
        cylinder(d = 10, h = 6, $fn = 32);

    color(col_metal)
    for (bx = [-18,18], by = [-18,18])
        translate([bx, by, 18])
            cylinder(d = 4, h = 5, $fn = 12);

    color([0.12,0.14,0.16])
    translate([0,-25,4])
        rounded_box(8, 6, 12, 2);
}

module lidar_at_top(x, y, z, rz=0) {
    translate([x, y, z])
        rotate([0, 0, rz])
            lidar_sensor_topplate();
}


// ============================================================
// Intel RealSense D435i
// ============================================================
module realsense_d435i_only() {
    color(col_rs_body)
    rounded_box(90, 26, 25, 6);

    color(col_rs_face)
    translate([0,11,12.5])
        rounded_box(82,4,14,2);

    color(col_rs_glass)
    translate([-22,13.5,12.5])
        rotate([90,0,0]) cylinder(d = 12, h = 4);

    color(col_rs_glass)
    translate([22,13.5,12.5])
        rotate([90,0,0]) cylinder(d = 12, h = 4);

    color([0.15,0.18,0.22])
    translate([0,13.5,12.5])
        rotate([90,0,0]) cylinder(d = 7, h = 4);

    color(col_metal)
    translate([0,0,-12]) cylinder(d = 14, h = 12);
}

module realsense_at_screen_top() {
    cam_z = body_top_z + plate_thick + screen_mast_h + 24;
    translate([screen_mast_x, screen_mast_y, cam_z])
        realsense_d435i_only();
}

// ============================================================
// VISNAT PROJECT PLAQUE — top plate label
// ============================================================
module visnat_project_plaque() {
    plaque_x  = 150;
    plaque_y  = 150;
    plaque_z  = body_top_z + plate_thick + 4.0;
    plaque_l  = 210;
    plaque_w  = 130;
    plaque_t  = 4.0;

    cu_col   = [0.10, 0.15, 0.32];
    text_col = [0.0,  0.0,  0.0];
    bg_col   = [0.96, 0.96, 0.97];

    color(bg_col)
    translate([plaque_x, plaque_y, plaque_z])
        linear_extrude(height = plaque_t)
            rounded_rect_2d(plaque_l, plaque_w, 7);

    color([0.0, 0.0, 0.0])
    translate([plaque_x, plaque_y, plaque_z + plaque_t])
        linear_extrude(height = 1.5)
            difference() {
                rounded_rect_2d(plaque_l + 1, plaque_w + 1, 7);
                rounded_rect_2d(plaque_l - 5, plaque_w - 5, 5);
            }

    logo_cx = plaque_x - plaque_l/2 + 38;
    logo_cy = plaque_y + 8;
    logo_lz = plaque_z + plaque_t;
    logo_r  = 30;

    color(cu_col)
    translate([logo_cx, logo_cy, logo_lz])
        linear_extrude(height = 2.5)
            difference() {
                circle(r = logo_r,     $fn = 72);
                circle(r = logo_r - 3, $fn = 72);
            }

    color(bg_col)
    translate([logo_cx, logo_cy, logo_lz])
        linear_extrude(height = 1.0)
            circle(r = logo_r - 3, $fn = 72);

    color(cu_col)
    translate([logo_cx, logo_cy, logo_lz])
        linear_extrude(height = 2.5)
            difference() {
                difference() {
                    circle(r = logo_r - 5,  $fn = 72);
                    circle(r = logo_r - 14, $fn = 72);
                }
                polygon(points = [
                    [0, 0],
                    [logo_r * cos(-58), logo_r * sin(-58)],
                    [logo_r,  0],
                    [logo_r * cos( 58), logo_r * sin( 58)]
                ]);
                rotate([0,0, 42])
                translate([logo_r - 10, 0, 0])
                    square([12, 12]);
                rotate([0,0,-42])
                translate([logo_r - 10,-12, 0])
                    square([12, 12]);
            }

    color(cu_col)
    translate([logo_cx + 1, logo_cy + 5, logo_lz])
        linear_extrude(height = 2.5)
            text("Cranfield", size = 7.5,
                 font = "Liberation Serif:style=Bold",
                 halign = "center", valign = "center");

    color(cu_col)
    translate([logo_cx + 1, logo_cy - 6, logo_lz])
        linear_extrude(height = 2.5)
            text("University", size = 6,
                 font = "Liberation Serif",
                 halign = "center", valign = "center");

    tx  = plaque_x + 18;
    tz  = plaque_z + plaque_t;

    color(cu_col)
    translate([tx, plaque_y + 48, tz])
        linear_extrude(height = 2.5)
            text("V.I.S.N.A.T", size = 11,
                 font = "Liberation Sans:style=Bold",
                 halign = "center", valign = "center");

    color(text_col)
    translate([tx, plaque_y + 38, tz])
        linear_extrude(height = 2.5)
            rounded_rect_2d(112, 2, 0.5);

    color(text_col)
    translate([tx, plaque_y + 28, tz])
        linear_extrude(height = 2.5)
            text("a project by Viksit, Sebastien,", size = 7,
                 font = "Liberation Sans",
                 halign = "center", valign = "center");

    color(text_col)
    translate([tx, plaque_y + 19, tz])
        linear_extrude(height = 2.5)
            text("Nathan, Alma and Tanish", size = 7,
                 font = "Liberation Sans",
                 halign = "center", valign = "center");

    color(text_col)
    translate([tx, plaque_y + 11, tz])
        linear_extrude(height = 2.5)
            rounded_rect_2d(112, 1.5, 0.5);

    color(text_col)
    translate([tx, plaque_y + 2, tz])
        linear_extrude(height = 2.5)
            text("Group 1", size = 6,
                 font = "Liberation Sans:style=Bold",
                 halign = "center", valign = "center");

    color(text_col)
    translate([tx, plaque_y - 9, tz])
        linear_extrude(height = 2.5)
            text("MSc Robotics", size = 6,
                 font = "Liberation Sans:style=Bold",
                 halign = "center", valign = "center");
}

// ============================================================
// FULL CHASSIS
// ============================================================
module chassis_complete() {
    chassis_body_only();
    top_plate_only();
    battery_pack_only();
    emergency_stop_only();
    access_flap_only();
    visnat_side_text_all();
    visnat_project_plaque();
}

// ============================================================
// SCREEN + MAST
// ============================================================
module screen_system_only() {
    base_z = body_top_z + plate_thick;
    sx = screen_mast_x;
    sy = screen_mast_y;

    color([0.72,0.76,0.80])
    translate([sx,sy,base_z])
        cylinder(h = screen_mast_h, r = screen_mast_r);

    color([0.62,0.66,0.71])
    translate([sx,sy,base_z + screen_mast_h])
        cylinder(h = 30, r1 = 24, r2 = 20);

    color([0.74,0.78,0.82])
    translate([sx,sy,base_z + screen_mast_h - 80])
        cube([22, 22, 80], center = true);

    translate([sx, sy - screen_mast_r/2 - 4, base_z + screen_mast_h + 12])
        color([0.74,0.78,0.82])
            cube([22, screen_mast_r + 8, 16], center = true);

    color(col_screen)
    translate([sx, sy - screen_mast_r - 8, base_z + screen_mast_h + 18])
        rotate([90, 0, 0])
            translate([0, -screen_w/2, 0])
                cube([screen_h, screen_w, screen_t], center = true);

    color(col_bezel)
    translate([sx, sy - screen_mast_r - 8, base_z + screen_mast_h + 18])
        rotate([90, 0, 0])
            translate([0, -screen_w/2, 0])
                difference() {
                    cube([screen_h + 18, screen_w + 18, 10], center = true);
                    cube([screen_h - 8,  screen_w - 8,  12], center = true);
                }
}


// ============================================================
// WHEEL
// ============================================================
module wheel_only() {
    rotate([90,0,0]) {
        color(col_wheel)
        difference() {
            cylinder(d = wheel_diameter, h = wheel_width, center = true);
            cylinder(d = wheel_diameter - 28, h = wheel_width + 2, center = true);
        }

        color([0.13,0.13,0.15])
        cylinder(d = wheel_diameter - 20, h = wheel_width - 10, center = true);

        color(col_spoke)
        cylinder(d = wheel_diameter - 42, h = wheel_width - 14, center = true);

        color([0.78,0.80,0.83])
        for (a = [0:60:359])
            rotate([0,0,a])
                translate([(wheel_diameter/2 - 22)/2,0,0])
                    cube([wheel_diameter/2 - 22, 10, wheel_width - 18], center = true);

        color(col_hub)
        cylinder(d = 46, h = wheel_width + 8, center = true);

        color([0.60,0.63,0.67])
        difference() {
            cylinder(d = 62, h = wheel_width + 4, center = true);
            cylinder(d = 46, h = wheel_width + 6, center = true);
        }

        color([0.06,0.06,0.06])
        for (i = [-3:3])
            translate([0,0,i*6])
                rotate_extrude()
                    translate([wheel_diameter/2 - 6,0])
                        square([5,2], center = true);
    }
}


// ============================================================
// MOTOR
// ============================================================
module motor_only() {
    color([0.34,0.36,0.39])
    translate([0,0,-gbox_l/2]) cylinder(d = gbox_d, h = gbox_l, center = true);

    color([0.28,0.30,0.33])
    translate([0,0,mot_l/2]) cylinder(d = mot_d, h = mot_l, center = true);

    color([0.20,0.22,0.24])
    translate([0,0,mot_l]) cylinder(d = mot_d - 8, h = 14, center = true);

    color([0.68,0.70,0.74])
    translate([0,0,-gbox_l - 14]) cylinder(d = 16, h = 28, center = true);

    color([0.42,0.44,0.48])
    difference() {
        cylinder(d = gbox_d + 20, h = 11, center = true);
        cylinder(d = gbox_d - 4,  h = 13, center = true);

        for (a = [0,90,180,270])
            rotate([0,0,a])
                translate([gbox_d/2 + 6, 0, 0])
                    cylinder(d = 8, h = 13, center = true);
    }
}


// ============================================================
// SPRING
// ============================================================
module spring_only(h=46) {
    color([0.72,0.72,0.75])
    translate([0,0,-6]) cylinder(d = 10, h = h + 18);

    color([0.60,0.61,0.64])
    translate([0,0,h - 2]) cylinder(d = 15, h = 24);

    color([0.84,0.76,0.30])
    for (i = [0:spr_coils-1])
        translate([0,0,i*(h/spr_coils)])
            rotate_extrude(angle = 385, $fn = 44)
                translate([spr_od/2,0]) circle(r = spr_wire);

    color([0.56,0.57,0.60]) {
        translate([0,0,-5])  cylinder(d = spr_od + 8, h = 7);
        translate([0,0,h - 2]) cylinder(d = spr_od + 8, h = 7);
    }

    color([0.68,0.70,0.74])
    translate([-13,-9,h + 4]) cube([26,18,20]);
}


// ============================================================
// MOTOR + SPRING PLACEMENT
// ============================================================
module motor_at(x, y) {
    sy2 = y >= 0 ? 1 : -1;
    motor_y = y - sy2*(wheel_width/2 + gbox_l + mot_l/2 + 4);

    rz = (y >= 0) ? 0 : 180;

    translate([x, motor_y, axle_z])
        rotate([90, 0, rz])
            motor_only();
}
module spring_at(x, y) {
    sy2 = y >= 0 ? 1 : -1;
    spx = x;
    spy = y - sy2*(wheel_width/2 + 12);
    spz_lo = axle_z + 12;
    spz_hi = body_bottom_z + 8;
    sp_h   = spz_hi - spz_lo;

    translate([spx, spy, spz_lo]) spring_only(sp_h);
}

module wheel_side_module(x, y) {
    translate([x, y, axle_z]) wheel_only();
    motor_at(x, y);
    spring_at(x, y);
}


// ============================================================
// HUMAN-FRIENDLY COSMETIC COVERS
// ============================================================
module friendly_top_skin_only() {
    skin_z = body_top_z + plate_thick + 1.2;

    color([0.97,0.97,0.99,0.95])
    translate([0,0,skin_z])
        difference() {
            rounded_box(body_length - 26, body_width - 26, 8, 22);

            translate([lidar1_x, lidar1_y, -1])
                rounded_box(62, 62, 12, 8);
        }
}

module manipulator_base_shroud_only() {
    shroud_z = body_top_z + plate_thick;
    shroud_h = 95;

    color([0.84,0.87,0.91])
    translate([main_mast_x, main_mast_y, shroud_z])
        difference() {
            rounded_box(130,120,shroud_h,22);
            translate([0,0,-1]) cylinder(d = 102, h = shroud_h + 2);
            translate([0,44,30])
                rotate([90,0,0]) cylinder(d = 50, h = 34, center = true);
        }
}

module tank_base_pad() {
    bz = body_top_z + plate_thick + 2;

    color([0.68, 0.72, 0.76])
    translate([tank_x, tank_y, bz])
        difference() {
            rounded_box(tank_l + 20, tank_w + 20, 8, tank_corner_r + 4);
            translate([0, 0, -1])
                rounded_box(tank_l - 16, tank_w - 16, 12, tank_corner_r - 4);
        }

    color([0.68, 0.72, 0.76])
    translate([aux_tank_x, aux_tank_y, bz])
        difference() {
            rounded_box(aux_tank_l + 16, aux_tank_w + 16, 8, aux_tank_corner_r + 4);
            translate([0, 0, -1])
                rounded_box(aux_tank_l - 12, aux_tank_w - 12, 12, aux_tank_corner_r - 3);
        }

    color([0.72, 0.76, 0.80])
    translate([join_mast_x, join_mast_y, bz])
        rounded_box(join_mast_l + 12, join_mast_w + 8, 8, 6);
}

module wheel_fender_at(x, y) {
    sy2 = y >= 0 ? 1 : -1;

    color([0.90,0.92,0.95])
    translate([x, y - sy2*18, axle_z + 54])
        rotate([90,0,0])
            difference() {
                cylinder(d = wheel_diameter + 36, h = wheel_width + 22, center = true);
                cylinder(d = wheel_diameter + 6,  h = wheel_width + 24, center = true);
                translate([0,-60,0])
                    cube([wheel_diameter + 80, 120, wheel_width + 30], center = true);
            }
}

module friendly_bumper_only() {
    bz = body_bottom_z + 34;

    color(col_bumper) {
        translate([0,  body_width/2 + 8, bz]) rounded_box(250,26,30,10);
        translate([0, -body_width/2 - 8, bz]) rounded_box(250,26,30,10);
    }
}

module screen_bezel_friendly_only() {
    base_z = body_top_z + plate_thick;
    sx = screen_mast_x;
    sy = screen_mast_y;

    color(col_bezel)
    translate([sx, sy - screen_mast_r - 8, base_z + screen_mast_h + 18])
        rotate([90, 0, 0])
            translate([0, -screen_w/2, screen_t/2 + 2])
                difference() {
                    rounded_box(screen_h + 34, screen_w + 30, 6, 14);
                    translate([0,0,-1])
                        rounded_box(screen_h + 8, screen_w + 6, 8, 10);
                }
}

module screen_mast_shroud_only() {
    base_z = body_top_z + plate_thick + 8;

    color([0.84,0.88,0.92])
    translate([screen_mast_x, screen_mast_y, base_z])
        difference() {
            rounded_box(84,84,120,16);
            translate([0,0,-1])
                cylinder(d = screen_mast_r*2 + 10, h = 122);
        }
}

module side_soft_trim_only() {
    tz = body_bottom_z + body_height*0.50;

    color([0.90,0.92,0.95,0.85]) {
        translate([0,  body_width/2 + 4,  tz]) rounded_box(body_length - 90, 8, 42, 4);
        translate([0, -body_width/2 - 4, tz]) rounded_box(body_length - 90, 8, 42, 4);
        translate([ body_length/2 + 4, 0, tz]) rounded_box(8, body_width - 90, 42, 4);
        translate([-body_length/2 - 4, 0, tz]) rounded_box(8, body_width - 90, 42, 4);
    }
}

module human_friendly_cover_set() {
    friendly_top_skin_only();
    manipulator_base_shroud_only();
    tank_base_pad();
    screen_bezel_friendly_only();
    screen_mast_shroud_only();
    friendly_bumper_only();
    side_soft_trim_only();

    wheel_fender_at( wheel_x,  wheel_y);
    wheel_fender_at(-wheel_x,  wheel_y);
    wheel_fender_at( wheel_x, -wheel_y);
    wheel_fender_at(-wheel_x, -wheel_y);
}


// ============================================================
// BRAKE PEDAL
// ============================================================
module brake_pedal() {
    pedal_l   = 80;
    pedal_w   = 40;
    pedal_t   = 14;
    pedal_x   = 20;
    pedal_y   = -(body_width/2 + pedal_w/2 + 18);
    pedal_z   = body_bottom_z + 18;

    arm_w     = 14;
    arm_h     = 40;
    arm_d     = 18;

    bracket_y = -(body_width/2 + 4);

    color([0.40, 0.42, 0.46])
    translate([pedal_x, bracket_y, pedal_z + pedal_t/2])
        rotate([90, 0, 0])
            rounded_box(arm_w, arm_h, arm_d, 4);

    color([0.55, 0.57, 0.62])
    translate([pedal_x, bracket_y - arm_d/2, pedal_z + pedal_t/2])
        rotate([90, 0, 0])
            cylinder(d = arm_w - 2, h = 6, $fn = 24);

    color([0.35, 0.37, 0.41])
    hull() {
        translate([pedal_x, bracket_y - arm_d/2 - 2, pedal_z + pedal_t/2])
            rotate([90, 0, 0])
                cylinder(d = arm_w - 4, h = 4, $fn = 24);

        translate([pedal_x, pedal_y, pedal_z + pedal_t/2])
            rotate([90, 0, 0])
                cylinder(d = arm_w - 2, h = 4, $fn = 24);
    }

    color([0.22, 0.24, 0.27])
    translate([pedal_x, pedal_y, pedal_z])
        difference() {
            rounded_box(pedal_l, pedal_w, pedal_t, 6);

            for (i = [-3:1:3])
                translate([i * 10, 0, pedal_t - 3])
                    rounded_box(4, pedal_w - 8, 6, 1);
        }

    color([0.90, 0.35, 0.20])
    translate([pedal_x, pedal_y, pedal_z + pedal_t - 2])
        difference() {
            rounded_box(pedal_l + 2, pedal_w + 2, 3, 6);
            translate([0, 0, -1])
                rounded_box(pedal_l - 6, pedal_w - 6, 6, 4);
        }

    color([0.85, 0.87, 0.90])
    translate([pedal_x, pedal_y - pedal_w/2 - 1.5, pedal_z + pedal_t/2])
        rotate([90, 0, 0])
            linear_extrude(height = 2)
                text(
                    "BRAKE",
                    size = 8,
                    font = "Liberation Sans:style=Bold",
                    halign = "center",
                    valign = "center"
                );
}

// ============================================================
// PAINT PIPE SYSTEM — pipe_od 28, connected to manipulator arm
// ============================================================
pipe_od      = 28;
pipe_wall    = 3.0;
pipe_col     = [0.55, 0.75, 0.95, 0.32];
pipe_col2    = [0.55, 0.85, 0.70, 0.32];
fitting_col  = [0.50, 0.53, 0.58];
junction_col = [0.40, 0.43, 0.48];

pipe_base_z  = body_top_z + plate_thick + 6 + tank_h + 16;

wrap_r       = 70;

// Junction sits behind the arm, at arm-base height
merge_x      = main_mast_x;
merge_y      = main_mast_y - wrap_r - 8;
merge_z      = body_top_z + plate_thick + manipulator_adapter_h + 40;

// Connection point ON the manipulator adapter ring
arm_connect_x = main_mast_x;
arm_connect_y = main_mast_y;
arm_connect_z = body_top_z + plate_thick + manipulator_adapter_h;

// EE link: rises up along the arm centreline
ee_link_z    = arm_connect_z + 160;

// ── HELPERS ──────────────────────────────────────────────────
module pipe_segment(p1, p2, od) {
    hull() {
        translate(p1) sphere(d = od, $fn = 32);
        translate(p2) sphere(d = od, $fn = 32);
    }
}

module pipe_arc(cx, cy, cz, r, a_start, a_end, steps = 40, od = pipe_od) {
    for (i = [0 : steps - 2]) {
        a1 = a_start + i       * (a_end - a_start) / (steps - 1);
        a2 = a_start + (i + 1) * (a_end - a_start) / (steps - 1);
        hull() {
            translate([cx + r*cos(a1), cy + r*sin(a1), cz])
                sphere(d = od, $fn = 32);
            translate([cx + r*cos(a2), cy + r*sin(a2), cz])
                sphere(d = od, $fn = 32);
        }
    }
}

module pipe_elbow(p1, p_corner, p2, od) {
    pipe_segment(p1, p_corner, od);
    pipe_segment(p_corner, p2, od);
}

module pipe_rise(x, y, z1, z2, od = pipe_od) {
    pipe_segment([x, y, z1], [x, y, z2], od);
}

// ── FITTINGS ─────────────────────────────────────────────────
module tank_outlet_fitting(tx, ty) {
    fz = body_top_z + plate_thick + 6 + tank_h;

    color(fitting_col) {
        translate([tx, ty - tank_w/2 - 4, fz + 8])
            rotate([90, 0, 0])
                cylinder(d = pipe_od + 8, h = 20, $fn = 28);

        translate([tx, ty - tank_w/2 - 24, fz + 8])
            rotate([90, 0, 0])
                cylinder(d = pipe_od + 6, h = 16, $fn = 24);
    }
}

module junction_block() {
    color(junction_col)
    translate([merge_x, merge_y, merge_z])
        rounded_box(56, 32, 26, 7);

    // Two inlet ports (one per pipe)
    color([0.60, 0.63, 0.67]) {
        translate([merge_x - 10, merge_y, merge_z + 13])
            rotate([0, 90, 0])
                cylinder(d = pipe_od - 4, h = 30, center = true, $fn = 24);
    }

    // Single outlet port pointing toward arm
    color([0.60, 0.63, 0.67])
    translate([merge_x, merge_y + 16, merge_z + 13])
        rotate([90, 0, 0])
            cylinder(d = pipe_od - 4, h = 20, $fn = 24);
}

// Clamp ring where merged pipe meets the manipulator adapter
module arm_pipe_clamp() {
    color(fitting_col)
    translate([arm_connect_x, arm_connect_y - manipulator_adapter_d/2 - 4, arm_connect_z + 8])
        rotate([90, 0, 0]) {
            difference() {
                cylinder(d = pipe_od + 14, h = 18, center = true, $fn = 28);
                cylinder(d = pipe_od + 1,  h = 20, center = true, $fn = 28);
            }
        }

    // Two bolts on the clamp
    color([0.55, 0.57, 0.62])
    for (bx = [-10, 10])
        translate([arm_connect_x + bx,
                   arm_connect_y - manipulator_adapter_d/2 - 12,
                   arm_connect_z + 8])
            rotate([90, 0, 0])
                cylinder(d = 5, h = 8, $fn = 12);
}

module ee_nozzle_connector() {
    color(fitting_col)
    translate([arm_connect_x, arm_connect_y, ee_link_z])
        rounded_box(40, 30, 20, 6);

    color([0.70, 0.73, 0.78])
    translate([arm_connect_x, arm_connect_y, ee_link_z + 20])
        cylinder(d = 20, h = 14, $fn = 24);

    color([0.45, 0.48, 0.52])
    translate([arm_connect_x, arm_connect_y, ee_link_z + 30])
        cylinder(d = 11, h = 18, $fn = 20);
}

// ── PIPE FROM MAIN TANK ───────────────────────────────────────
module pipe_from_main_tank() {
    tx_out = tank_x;
    ty_out = tank_y - tank_w/2 - 14;
    tz_out = pipe_base_z + 8;

    arc_entry_a = -20;
    arc_exit_a  = -90;

    color(pipe_col) {
        // Rise from tank outlet
        pipe_rise(tx_out, ty_out, pipe_base_z - 18, tz_out);

        // Run to arc entry with smooth elbow
        pipe_elbow(
            [tx_out, ty_out, tz_out],
            [main_mast_x + wrap_r * cos(arc_entry_a), ty_out, tz_out],
            [main_mast_x + wrap_r * cos(arc_entry_a),
             main_mast_y + wrap_r * sin(arc_entry_a), tz_out],
            pipe_od
        );

        // Arc around mast
        pipe_arc(main_mast_x, main_mast_y, tz_out,
                 wrap_r, arc_entry_a, arc_exit_a, 40);

        // Elbow down into junction block
        pipe_elbow(
            [main_mast_x + wrap_r * cos(arc_exit_a),
             main_mast_y + wrap_r * sin(arc_exit_a), tz_out],
            [merge_x - 10, merge_y, tz_out],
            [merge_x - 10, merge_y, merge_z + 13],
            pipe_od
        );
    }
}

// ── PIPE FROM AUX TANK ────────────────────────────────────────
module pipe_from_aux_tank() {
    ax_out = aux_tank_x;
    ay_out = aux_tank_y - aux_tank_w/2 - 14;
    az_out = pipe_base_z + 26;

    arc_entry_a = -160;
    arc_exit_a  = -90;

    color(pipe_col2) {
        // Rise from aux tank outlet
        pipe_rise(ax_out, ay_out, pipe_base_z - 18, az_out);

        // Run to arc entry with smooth elbow
        pipe_elbow(
            [ax_out, ay_out, az_out],
            [main_mast_x + wrap_r * cos(arc_entry_a), ay_out, az_out],
            [main_mast_x + wrap_r * cos(arc_entry_a),
             main_mast_y + wrap_r * sin(arc_entry_a), az_out],
            pipe_od
        );

        // Arc around mast (opposite side)
        pipe_arc(main_mast_x, main_mast_y, az_out,
                 wrap_r, arc_entry_a, arc_exit_a, 40);

        // Elbow down into junction block (offset slightly from main pipe)
        pipe_elbow(
            [main_mast_x + wrap_r * cos(arc_exit_a),
             main_mast_y + wrap_r * sin(arc_exit_a), az_out],
            [merge_x + 10, merge_y, az_out],
            [merge_x + 10, merge_y, merge_z + 13],
            pipe_od
        );
    }
}

// ── MERGED PIPE: junction → arm adapter → up to EE ───────────
module pipe_merged_to_ee() {
    color([0.65, 0.82, 0.90, 0.35]) {
        pipe_segment(
            [merge_x, merge_y + 16, merge_z + 13],
            [merge_x, arm_connect_y - manipulator_adapter_d/2 - 4, merge_z + 13],
            pipe_od
        );

        pipe_segment(
            [arm_connect_x, arm_connect_y - manipulator_adapter_d/2 - 4, merge_z + 13],
            [arm_connect_x, arm_connect_y - manipulator_adapter_d/2 - 4, arm_connect_z + 8],
            pipe_od
        );

        pipe_segment(
            [arm_connect_x, arm_connect_y - manipulator_adapter_d/2 - 4, arm_connect_z + 8],
            [arm_connect_x, arm_connect_y, arm_connect_z + 16],
            pipe_od
        );

        pipe_segment(
            [arm_connect_x, arm_connect_y, arm_connect_z + 16],
            [arm_connect_x, arm_connect_y, ee_link_z],
            pipe_od
        );
    }
}

// ── FULL SYSTEM ───────────────────────────────────────────────
module paint_pipe_system() {
    tank_outlet_fitting(tank_x,     tank_y);
    tank_outlet_fitting(aux_tank_x, aux_tank_y);
    pipe_from_main_tank();
    pipe_from_aux_tank();
    junction_block();
    pipe_merged_to_ee();
    arm_pipe_clamp();
    ee_nozzle_connector();
}
// ============================================================
// FULL PREVIEW ASSEMBLY
// ============================================================
module full_robot_preview() {
    chassis_complete();
    screen_system_only();
    // manipulator_adapter_only();   // removed to eliminate floating disc
   

    lidar_at_top(lidar1_x, lidar1_y, lidar1_z, lidar1_rot_z);

    swappable_tank();
    aux_swappable_tank();
    tank_join_mast_only();

    lidar_at_top(lidar2_x, lidar2_y, lidar2_z, lidar2_rot_z);

    realsense_at_screen_top();

    wheel_side_module( wheel_x,  wheel_y);
    wheel_side_module(-wheel_x,  wheel_y);
    wheel_side_module( wheel_x, -wheel_y);
    wheel_side_module(-wheel_x, -wheel_y);

    human_friendly_cover_set();
    brake_pedal();
    paint_pipe_system();
}


// ============================================================
// RENDER
// ============================================================
full_robot_preview();