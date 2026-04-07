$fn = 96;

// ============================================================
//  VISNAT MOBILE PLATFORM – OCTAGONAL OPEN FRAME
//  Mecanum wheels, motors, springs – correctly aligned
//  All dimensions in mm
// ============================================================

// ── Core dimensions ──────────────────────────────────────────
body_length      = 610;
body_width       = 610;
body_height      = 180;
body_wall        = 8;
body_corner_r    = 18;

ground_clearance = 120;   // body_bottom_z
wheel_diameter   = 180;
wheel_radius     = wheel_diameter / 2;   // = 90
wheel_width      = 50;                   // tyre width along Y (axle) axis

// ── Derived Z values ─────────────────────────────────────────
axle_z        = wheel_radius;            // = 90  (wheel centre above ground)
body_bottom_z = ground_clearance;        // = 120
body_top_z    = body_bottom_z + body_height;  // = 300

// ── Wheel positions ──────────────────────────────────────────
//  Wheels sit at the 4 corners, OUTSIDE the body frame.
//  Axle runs along Y axis.
//  wheel_x  = distance from robot centre along X to tyre centre
//  wheel_y  = distance from robot centre along Y to tyre centre
//             tyre inner face aligns with body outer wall (body_width/2)
//             so tyre centre = body_width/2 + wheel_width/2
wheel_x = 225;                                        // = 225 mm from centre (X)
wheel_y = body_width/2 + wheel_width/2;               // = 305 + 25 = 330 mm from centre (Y)

// ── Frame geometry ────────────────────────────────────────────
frame_size   = 30;
deck_thick   = 8;
deck_z       = body_bottom_z + 28;
post_d       = 14;
oct_chamfer  = 120;

// ── Top plate ─────────────────────────────────────────────────
plate_thick  = 12;
plate_margin = 6;

// ── Mast ──────────────────────────────────────────────────────
mast_d         = 78;
mast_h         = 184;       // column height so total = 550 mm
mast_collar_w  = 130;
mast_collar_h  = 14;
hazard_ring_h  = 18;
mast_top_w     = 130;
mast_top_h     = 22;

// mast X offset (from image, mast is not centred – slightly offset)
main_mast_x  = -35;
aligned_y    = 0;

// ── Screen mast ───────────────────────────────────────────────
screen_mast_x  = -180;
screen_mast_h  = 1050;
screen_mast_r  = 40;
screen_w       = 355;
screen_h       = 205;
screen_t       = 14;

// ── Bucket holder ─────────────────────────────────────────────
bucket_holder_x = 140;
bucket_d        = 230;
bucket_holder_d = bucket_d + 40;
bucket_holder_h = 22;
bucket_recess_h = 18;

// ── Battery ───────────────────────────────────────────────────
bat_l = 300;  bat_w = 155;  bat_h = 70;

// ── E-stop ────────────────────────────────────────────────────
estop_x = -190;
estop_y =  200;

// ── Motor dimensions ─────────────────────────────────────────
//  Motor is mounted with its axis along Y, inboard of the wheel.
//  Gearbox outer face sits flush with tyre inner face.
mot_d   = 56;
mot_l   = 72;
gbox_d  = 64;
gbox_l  = 34;

//  Motor centre Y distance from robot centre (for +Y side):
//    tyre centre Y         = wheel_y               = 330
//    tyre inner face Y     = wheel_y - wheel_width/2 = 305
//    gearbox outer Y       = 305
//    gearbox centre Y      = 305 - gbox_l/2        = 305 - 17 = 288
//    motor body centre Y   = 305 - gbox_l - mot_l/2 = 305 - 34 - 36 = 235
//  ⟹ we translate the whole motor assembly to (x, ±motor_centre_y, axle_z)
//    and rotate [90,0,0] so the cylinder axis is along Y.
motor_centre_y = wheel_y - wheel_width/2 - gbox_l - mot_l/2;  // = 235

// ── Spring dimensions ─────────────────────────────────────────
//  Springs run vertically from near ground up to body_bottom_z.
//  Positioned just inboard of the tyre inner face.
spr_od    = 30;
spr_wire  = 3.5;
spr_coils = 7;
spr_x     = wheel_x;                        // same X as wheel
spr_y_off = wheel_y - wheel_width/2 - 18;   // = 287  (inboard of tyre)
spr_z_lo  = 8;                              // spring bottom (near ground)
spr_z_hi  = body_bottom_z + 6;             // spring top (at body underside)
spr_h     = spr_z_hi - spr_z_lo;           // = 118 mm  – nicely visible

// ── Upright strut (axle to body) ──────────────────────────────
upright_d = 18;

// ============================================================
//  HELPER MODULES
// ============================================================
module rounded_box(l, w, h, r) {
    hull()
        for (x=[-l/2+r, l/2-r], y=[-w/2+r, w/2-r])
            translate([x,y,0]) cylinder(h=h, r=r);
}

module octagon_2d(l=body_length, w=body_width, c=oct_chamfer) {
    polygon(points=[
        [ l/2-c,  w/2],  [-l/2+c,  w/2],
        [-l/2,    w/2-c],[-l/2,   -w/2+c],
        [-l/2+c, -w/2],  [ l/2-c, -w/2],
        [ l/2,   -w/2+c],[ l/2,    w/2-c]
    ]);
}

module octagon_plate(l, w, c, h) {
    linear_extrude(height=h) octagon_2d(l, w, c);
}

module octagon_ring(l, w, c, t, h) {
    linear_extrude(height=h)
        difference() {
            octagon_2d(l, w, c);
            offset(delta=-t) octagon_2d(l, w, c);
        }
}

// ============================================================
//  CHASSIS BODY  – octagonal open-extrusion frame
// ============================================================
module chassis_body_only() {
    color([0.75, 0.75, 0.78])
    union() {
        // Bottom octagonal frame ring
        translate([0, 0, body_bottom_z])
            octagon_ring(body_length, body_width, oct_chamfer, frame_size, frame_size);

        // Top octagonal frame ring
        translate([0, 0, body_top_z - frame_size])
            octagon_ring(body_length, body_width, oct_chamfer, frame_size, frame_size);

        // 8 Vertical corner posts
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
                cylinder(h=body_height - 2*frame_size, d=post_d);

        // Internal deck plate (inset from outer walls)
        translate([0, 0, deck_z])
            linear_extrude(height=deck_thick)
                offset(delta=-80) octagon_2d(body_length, body_width, oct_chamfer);

        // Longitudinal cross-beams
        translate([0, 0, deck_z + 18])
            cube([body_length-180, 24, 24], center=true);
        translate([0, 0, deck_z + 18])
            cube([24, body_width-180, 24], center=true);
        translate([0, 120, deck_z + 18])
            cube([body_length-220, 24, 24], center=true);
        translate([0, -120, deck_z + 18])
            cube([body_length-220, 24, 24], center=true);

        // Corner brackets
        for (sx=[-1,1]) for (sy=[-1,1])
            translate([sx*170, sy*170, body_bottom_z + 55])
                rotate([0, 0, 45])
                    cube([45, 20, 70], center=true);

        // Horizontal rail extensions to wheel mounts (both sides, both ends)
        // These rails connect the body frame to the axle mount, matching the image
        for (sx=[-1,1]) for (sy=[-1,1]) {
            // Outboard rail from frame to axle stub
            translate([sx*wheel_x,
                       sy*(body_width/2 + (wheel_y - body_width/2)/2),
                       body_bottom_z + frame_size/2])
                cube([frame_size, wheel_y - body_width/2, frame_size], center=true);

            // Axle mount block at wheel position
            translate([sx*wheel_x, sy*wheel_y, body_bottom_z + frame_size/2])
                cube([frame_size+4, frame_size+4, frame_size+4], center=true);
        }
    }
}

// ============================================================
//  TOP PLATE  – octagonal
// ============================================================
module top_plate_only() {
    color([0.78, 0.78, 0.80])
    translate([0, 0, body_top_z]) {
        difference() {
            octagon_plate(body_length-2*plate_margin,
                          body_width -2*plate_margin,
                          oct_chamfer-8, plate_thick);

            // 5×5 bolt grid
            for (x=[-210,-105,0,105,210])
                for (y=[-210,-105,0,105,210])
                    translate([x,y,-1]) cylinder(h=plate_thick+2, d=6.5);

            // Main mast hole
            translate([main_mast_x, aligned_y, -1])
                cylinder(h=plate_thick+2, d=mast_d+8);

            // Screen mast hole
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
//  BATTERY
// ============================================================
module battery_pack_only() {
    color([0.30, 0.30, 0.32])
    translate([0, 10, deck_z + deck_thick + bat_h/2 + 4])
        rounded_box(bat_l, bat_w, bat_h, 10);
}

// ============================================================
//  EMERGENCY STOP
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
//  BUCKET HOLDER
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
//  FULL CHASSIS ASSEMBLY
// ============================================================
module chassis_complete() {
    chassis_body_only();
    top_plate_only();
    battery_pack_only();
    emergency_stop_only();
    bucket_holder_only();
}

// ============================================================
//  CENTRAL MAST
//  Total mast height above top plate = collar + hazard + column + top
//  = 14 + 18 + 184 + 22 = 238 mm
//  Top plate Z = 300, so mast top = 300 + 12 + 238 = 550 mm ✓
// ============================================================
module mast_only() {
    mz = body_top_z + plate_thick;   // = 312

    // Square black collar on top plate
    color([0.18,0.18,0.20])
    translate([main_mast_x, aligned_y, mz]) {
        difference() {
            rounded_box(mast_collar_w, mast_collar_w, mast_collar_h, 8);
            translate([0,0,-1]) cylinder(h=mast_collar_h+2, d=mast_d-4);
            for (x=[-48,48]) for (y=[-48,48])
                translate([x,y,-1]) cylinder(h=mast_collar_h+2, d=9);
        }
    }

    // Hazard ring  (gold + black stripes)
    hz = mz + mast_collar_h;    // = 326
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

    // Main aluminium column
    cz = hz + hazard_ring_h;    // = 344
    color([0.76,0.76,0.78])
    translate([main_mast_x, aligned_y, cz])
        cylinder(d=mast_d, h=mast_h);   // top at 344+184 = 528

    // Mid-collar ring
    color([0.54,0.54,0.57])
    translate([main_mast_x, aligned_y, cz + mast_h*0.42])
        difference() {
            cylinder(d=mast_d+22, h=20);
            translate([0,0,-1]) cylinder(d=mast_d-2, h=22);
        }

    // Top mounting plate  (528 + 22 = 550 ✓)
    color([0.18,0.18,0.20])
    translate([main_mast_x, aligned_y, cz + mast_h]) {
        difference() {
            rounded_box(mast_top_w, mast_top_w, mast_top_h, 8);
            for (x=[-48,48]) for (y=[-48,48])
                translate([x,y,-1]) cylinder(h=mast_top_h+2, d=10);
            translate([0,0,-1]) cylinder(h=mast_top_h+2, d=mast_d-6);
        }
        translate([0,0,mast_top_h]) cylinder(d=mast_d*0.52, h=14);
    }
}

// ============================================================
//  SCREEN MAST + SCREEN
// ============================================================
module screen_system_only() {
    base_z = body_top_z + plate_thick;
    sx = screen_mast_x;

    color([0.72,0.72,0.74])
    translate([sx, aligned_y, base_z])
        cylinder(h=screen_mast_h, r=screen_mast_r);

    color([0.60,0.62,0.65])
    translate([sx, aligned_y, base_z + screen_mast_h])
        cylinder(h=30, r1=24, r2=20);

    color([0.65,0.65,0.67])
    translate([sx, aligned_y, base_z + screen_mast_h - 110])
        cube([24, 90, 110], center=true);

    // Screen glass
    color([0.2, 0.4, 0.8, 0.7])
    translate([sx-35, aligned_y, base_z + screen_mast_h - 110])
        rotate([90,0,90])
            cube([screen_w, screen_h, screen_t], center=true);

    // Screen bezel
    color([0.15,0.15,0.17])
    translate([sx-42, aligned_y, base_z + screen_mast_h - 110])
        rotate([90,0,90])
            difference() {
                cube([screen_w+18, screen_h+18, 10], center=true);
                cube([screen_w-8,  screen_h-8,  12], center=true);
            }
}

// ============================================================
//  MECANUM WHEEL
//  Positioned at origin (axle along Z after rotate).
//  Call with:  translate([wx, wy, axle_z]) wheel_only(angle_dir)
//  angle_dir = +1 or -1 controls roller slant (handedness)
// ============================================================
module wheel_only(angle_dir=1) {
    // rotate([90,0,0]) makes the wheel spin around Y axis
    rotate([90, 0, 0]) {

        // Tyre drum
        color([0.10,0.10,0.10])
        difference() {
            cylinder(d=wheel_diameter, h=wheel_width, center=true);
            cylinder(d=wheel_diameter-36, h=wheel_width+2, center=true);
        }

        // Hub face plate
        color([0.55,0.57,0.60])
        cylinder(d=wheel_diameter-40, h=wheel_width-16, center=true);

        // Centre hub boss
        color([0.42,0.44,0.47])
        cylinder(d=46, h=wheel_width+8, center=true);

        // Outer hub ring
        color([0.52,0.54,0.57])
        difference() {
            cylinder(d=62, h=wheel_width+4, center=true);
            cylinder(d=46, h=wheel_width+6, center=true);
        }

        // Mecanum rollers – 45° slant controlled by angle_dir
        color([0.08,0.08,0.08])
        for (a=[0:45:315])
            rotate([0, 0, a])
                translate([wheel_diameter/2 - 16, 0, 0])
                    rotate([0, angle_dir*45, 0])
                        scale([1, 1, 1.35])
                            cylinder(d=18, h=wheel_width-2, center=true);
    }
}

// ============================================================
//  MOTOR ASSEMBLY
//  Call with:  motor_at(wx, wy)
//  Motor axis is along Y; gearbox faces the wheel (outboard).
//  The translate puts motor body centre at (x, ±motor_centre_y, axle_z).
// ============================================================
module motor_only() {
    // All geometry along Z; caller does rotate([90,0,0]) to align with Y axis.
    // +Z direction = outboard (toward wheel)
    // Gearbox: from Z=0 outward (toward wheel)
    color([0.28,0.28,0.30])
    translate([0, 0, gbox_l/2])
        cylinder(d=gbox_d, h=gbox_l, center=true);

    // Motor body: inboard from Z=0
    color([0.20,0.20,0.22])
    translate([0, 0, -mot_l/2])
        cylinder(d=mot_d, h=mot_l, center=true);

    // Rear end cap
    color([0.16,0.16,0.18])
    translate([0, 0, -mot_l])
        cylinder(d=mot_d-8, h=14, center=true);

    // Output shaft (outboard, toward wheel)
    color([0.60,0.62,0.65])
    translate([0, 0, gbox_l+14])
        cylinder(d=16, h=28, center=true);

    // Mounting flange at gearbox/body interface
    color([0.33,0.33,0.35])
    difference() {
        cylinder(d=gbox_d+20, h=11, center=true);
        cylinder(d=gbox_d-4,  h=13, center=true);
        for (a=[0,90,180,270])
            rotate([0,0,a])
                translate([gbox_d/2+6,0,0])
                    cylinder(d=8, h=13, center=true);
    }

    // Cooling fins on motor body
    color([0.24,0.24,0.26])
    for (a=[0:30:359])
        rotate([0,0,a])
            translate([mot_d/2+2, 0, -mot_l*0.3])
                cube([4, 3, mot_l*0.5], center=true);

    // Encoder cap on rear
    color([0.14,0.14,0.16])
    translate([0, 0, -mot_l-14])
        cylinder(d=mot_d-18, h=16, center=true);
}

module motor_at(wx, wy) {
    sy = sign(wy);   // +1 for +Y side,  -1 for -Y side

    // Motor centre position:
    //   X = wx  (same as wheel)
    //   Y = sy * motor_centre_y   (inboard of tyre inner face)
    //   Z = axle_z               (same height as wheel axle)
    //
    // rotate([90,0,0]) makes motor axis point in Y direction.
    // For +Y side (sy=+1): gearbox faces +Y (toward wheel) → correct
    // For -Y side (sy=-1): need extra 180° flip so gearbox still faces wheel

    translate([wx, sy * motor_centre_y, axle_z])
        rotate([90 * sy, 0, 0])   // +90 for +Y side, -90 for -Y side
            motor_only();
}

// ============================================================
//  AXLE UPRIGHT + STUB
//  Connects wheel to body frame vertically and laterally
// ============================================================
module upright_at(wx, wy) {
    sy = sign(wy);

    // Vertical strut: from axle_z up to body_bottom_z
    color([0.58,0.60,0.63])
    translate([wx, sy*(body_width/2), axle_z])
        cylinder(d=upright_d, h=body_bottom_z - axle_z + frame_size);

    // Horizontal stub axle (Y direction)
    color([0.54,0.56,0.59])
    translate([wx, wy, axle_z])
        rotate([90,0,0])
            cylinder(d=22, h=wheel_width+28, center=true);

    // Lateral brace from frame edge to axle
    color([0.56,0.58,0.61])
    translate([wx,
               sy*(body_width/2 + (abs(wy) - body_width/2)/2),
               axle_z + (body_bottom_z - axle_z)/2])
        cube([upright_d, abs(wy) - body_width/2, upright_d], center=true);
}

// ============================================================
//  COIL SPRING
//  Runs vertically from spr_z_lo to spr_z_hi at each corner.
//  Positioned just inboard of the tyre inner face.
// ============================================================
module spring_only(height) {
    // Shock shaft
    color([0.68,0.68,0.70])
    translate([0,0,-6]) cylinder(d=10, h=height+18);

    // Upper sleeve
    color([0.52,0.52,0.55])
    translate([0,0,height-2]) cylinder(d=15, h=24);

    // Spring coils (gold/yellow like the image)
    color([0.85, 0.72, 0.10])
    for (i=[0:spr_coils-1])
        translate([0, 0, i*(height/spr_coils)])
            rotate_extrude(angle=385, $fn=44)
                translate([spr_od/2, 0]) circle(r=spr_wire);

    // Top and bottom seats
    color([0.48,0.48,0.50]) {
        translate([0,0,-5])       cylinder(d=spr_od+10, h=7);
        translate([0,0,height-2]) cylinder(d=spr_od+10, h=7);
    }

    // Upper bracket
    color([0.60,0.62,0.65])
    translate([-13, -9, height+4]) cube([26,18,20]);
}

module spring_at(wx, wy) {
    sy = sign(wy);
    // X = wx (same as wheel)
    // Y = just inboard of tyre inner face
    spy = sy * spr_y_off;

    translate([wx, spy, spr_z_lo])
        spring_only(spr_h);
}

// ============================================================
//  FULL PREVIEW ASSEMBLY
// ============================================================
module full_robot_preview() {

    // Chassis (body + top plate + internals)
    chassis_complete();

    // Mast
    mast_only();

    // Screen system
    screen_system_only();

    // 4 Mecanum wheels at corners
    // Mecanum handedness (X-pattern for omnidirectional drive):
    //   FL (+x,+y) = angle_dir  +1   ╲
    //   FR (+x,-y) = angle_dir  -1   ╱
    //   RL (-x,+y) = angle_dir  -1   ╱
    //   RR (-x,-y) = angle_dir  +1   ╲
    translate([ wheel_x,  wheel_y, axle_z]) wheel_only( 1);  // FL
    translate([ wheel_x, -wheel_y, axle_z]) wheel_only(-1);  // FR
    translate([-wheel_x,  wheel_y, axle_z]) wheel_only(-1);  // RL
    translate([-wheel_x, -wheel_y, axle_z]) wheel_only( 1);  // RR

    // Motors – one per wheel, inboard, axis along Y
    motor_at( wheel_x,  wheel_y);   // FL motor
    motor_at( wheel_x, -wheel_y);   // FR motor
    motor_at(-wheel_x,  wheel_y);   // RL motor
    motor_at(-wheel_x, -wheel_y);   // RR motor

    // Uprights + axle stubs
    upright_at( wheel_x,  wheel_y);
    upright_at( wheel_x, -wheel_y);
    upright_at(-wheel_x,  wheel_y);
    upright_at(-wheel_x, -wheel_y);

    // Springs – at each corner, vertical, inboard of tyre
    spring_at( wheel_x,  wheel_y);
    spring_at( wheel_x, -wheel_y);
    spring_at(-wheel_x,  wheel_y);
    spring_at(-wheel_x, -wheel_y);
}

// ============================================================
//  RENDER
// ============================================================
full_robot_preview();

// ============================================================
//  DIMENSION SUMMARY
// ============================================================
// Body footprint        : 610 × 610 mm (octagonal, chamfer=120)
// Body height           : 180 mm
// Ground clearance      : 120 mm   (body bottom Z)
// Body top Z            : 300 mm
// Wheel diameter        : 180 mm
// Wheel width (axle Y)  : 50 mm
// Wheel axle Z          : 90 mm    (centre above ground)
// Wheel X positions     : ±225 mm  from robot centre
// Wheel Y positions     : ±330 mm  from robot centre (outside frame)
// Motor centre Y        : ±235 mm  from robot centre (inboard)
// Spring Y position     : ±287 mm  from robot centre
// Spring Z range        : 8 – 126 mm  (height ≈ 118 mm)
// Overall height        : 550 mm   (ground to top of mast plate)
// Mast column height    : 184 mm   (+collar+ring+top = 238 mm above plate)
// ============================================================
