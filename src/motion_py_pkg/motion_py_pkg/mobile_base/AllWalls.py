"""
Robot Wall-Painting Path Simulation
Python translation of the original MATLAB script.

This version:
- auto-checks and installs missing packages (numpy, matplotlib)
- keeps the original logic intact
"""

import os
import sys
import subprocess
import importlib


# ─────────────────────────────────────────────
#  AUTO-INSTALL MISSING PACKAGES
# ─────────────────────────────────────────────
def ensure_package(package_name: str, import_name: str = None):
    name = import_name or package_name
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError:
        print(f"Missing package detected: {package_name}")
        print(f"Installing {package_name} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return importlib.import_module(name)


np = ensure_package("numpy")
ensure_package("matplotlib")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


# ─────────────────────────────────────────────
#  PARAMETERS
# ─────────────────────────────────────────────
WALL_OFFSET   = 0.75      # 75 cm inward from the painted wall
PAUSE_TIME    = 0.20      # animation pause (seconds)
WALL_HEIGHT   = 3.048     # 10 ft in metres
ROBOT_Z       = 0.10      # robot marker height above floor
PATH_Z        = 0.05      # path drawn slightly above floor
ARROW_LEN     = 0.35      # heading arrow length

ANGLE_MIN       = -3.141590118408203
ANGLE_INCREMENT =  0.003929443191736937

LIDAR_FILE = "./mobile_base/lidar_raw.csv"
RANGE_FILE = "./mobile_base/ranges_raw.csv"


# ─────────────────────────────────────────────
#  WALL DEFINITIONS
# ─────────────────────────────────────────────
wallA_start = np.array([-1.00,  6.00])
wallA_end   = np.array([ 5.50,  6.00])

wallB_start = np.array([ 7.16,  6.00])
wallB_end   = np.array([ 8.74,  6.00])

wallC_start = np.array([ 8.74,  6.00])
wallC_end   = np.array([ 8.80, -1.37])

wallD_start = np.array([ 8.80, -1.37])
wallD_end   = np.array([-1.00, -1.39])

wallE_start = np.array([-1.00, -1.39])
wallE_end   = np.array([-1.00,  6.00])


# Derived t-range constraints (0.5 m gap at each end)
def t_bounds(p1, p2):
    L = np.linalg.norm(p2 - p1)
    return 0.50, L - 0.50


wallA_tStart, wallA_tEnd = t_bounds(wallA_start, wallA_end)
wallB_tStart, wallB_tEnd = t_bounds(wallB_start, wallB_end)
wallC_tStart, wallC_tEnd = t_bounds(wallC_start, wallC_end)
wallD_tStart, wallD_tEnd = t_bounds(wallD_start, wallD_end)
wallE_tStart, wallE_tEnd = t_bounds(wallE_start, wallE_end)


# ═══════════════════════════════════════════════════════════
#  LOCAL FUNCTIONS
# ═══════════════════════════════════════════════════════════
def centred_robot_points(p1, p2, wall_offset, t_start, t_end, side_choice):
    """Return robot positions offset from a wall segment, centred in 1-m bins."""
    dir_vec  = p2 - p1
    L        = np.linalg.norm(dir_vec)
    unit_vec = dir_vec / L

    left_normal  = np.array([-unit_vec[1],  unit_vec[0]])
    right_normal = np.array([ unit_vec[1], -unit_vec[0]])

    if side_choice.lower() == "left":
        normal_vec = left_normal
    elif side_choice.lower() == "right":
        normal_vec = right_normal
    else:
        raise ValueError('side_choice must be "left" or "right".')

    if t_end < t_start:
        raise ValueError(f"t_end ({t_end:.3f}) < t_start ({t_start:.3f}): wall segment too short.")

    # midpoints of 1-m bins: 0.5, 1.5, 2.5, …
    all_midpoints = np.arange(0.5, L, 1.0)
    t_vals = all_midpoints[(all_midpoints >= t_start) & (all_midpoints <= t_end)]

    if t_vals.size == 0:
        t_vals = np.array([(t_start + t_end) / 2.0])

    # append t_end if not already there
    if abs(t_vals[-1] - t_end) > 1e-9:
        t_vals = np.append(t_vals, t_end)

    pts = np.array([p1 + t * unit_vec + wall_offset * normal_vec for t in t_vals])
    return pts


def look_vector_to_wall(p1, p2, side_choice, arrow_len):
    """Return the 2-D heading vector that points FROM the robot TOWARD the wall."""
    dir_vec  = p2 - p1
    unit_vec = dir_vec / np.linalg.norm(dir_vec)

    left_normal  = np.array([-unit_vec[1],  unit_vec[0]])
    right_normal = np.array([ unit_vec[1], -unit_vec[0]])

    if side_choice.lower() == "left":
        inward = left_normal
    elif side_choice.lower() == "right":
        inward = right_normal
    else:
        raise ValueError('side_choice must be "left" or "right".')

    return -arrow_len * inward   # face opposite the offset direction → face wall


def compute_measurement_points(p1, p2, measure_step):
    """Yellow dots spaced every measure_step metres along the wall."""
    dir_vec  = p2 - p1
    L        = np.linalg.norm(dir_vec)
    unit_vec = dir_vec / L
    t_vals   = np.arange(0, L + 1e-9, measure_step)
    t_vals   = t_vals[t_vals <= L]
    return np.array([p1 + t * unit_vec for t in t_vals])


def print_wall_points(wall_name, pts):
    print(f"Wall {wall_name}: {len(pts)} robot points")
    for k, pt in enumerate(pts, 1):
        print(f"  {wall_name}{k} : ({pt[0]:.4f}, {pt[1]:.4f})")


# ─────────────────────────────────────────────
#  3-D DRAWING HELPERS
# ─────────────────────────────────────────────
def draw_wall_3d(ax, p1, p2, h, face_col, alpha=0.65):
    """Draw a rectangular wall patch in 3-D."""
    verts = [[
        (p1[0], p1[1], 0),
        (p2[0], p2[1], 0),
        (p2[0], p2[1], h),
        (p1[0], p1[1], h)
    ]]
    poly = Poly3DCollection(
        verts,
        alpha=alpha,
        facecolor=face_col,
        edgecolor=(0.2, 0.2, 0.2),
        linewidth=1.0
    )
    ax.add_collection3d(poly)


def plot_robot_pts_3(ax, pts, rz, col):
    ax.scatter(
        pts[:, 0],
        pts[:, 1],
        rz * np.ones(len(pts)),
        color=col,
        s=40,
        zorder=5
    )


def plot_heading_arrows_3(ax, pts, rz, face_vec, col):
    for pt in pts:
        ax.quiver(
            pt[0], pt[1], rz,
            face_vec[0], face_vec[1], 0,
            color=col,
            linewidth=1.4,
            length=1,
            normalize=False,
            arrow_length_ratio=0.3
        )


def plot_meas_pts_3(ax, pts, rz):
    ax.scatter(
        pts[:, 0],
        pts[:, 1],
        rz * np.ones(len(pts)),
        color="yellow",
        s=30,
        zorder=4
    )


def label_wall(ax, p1, p2, h, lbl, x_off=0.0):
    mx = (p1[0] + p2[0]) / 2 + x_off
    my = (p1[1] + p2[1]) / 2
    ax.text(mx, my, h + 0.1, lbl, fontweight="bold", ha="center", fontsize=9)


def set_ax_limits(ax, h):
    all_x = [
        wallA_start[0], wallA_end[0], wallB_start[0], wallB_end[0],
        wallC_start[0], wallC_end[0], wallD_start[0], wallD_end[0],
        wallE_start[0], wallE_end[0]
    ]
    all_y = [
        wallA_start[1], wallA_end[1], wallB_start[1], wallB_end[1],
        wallC_start[1], wallC_end[1], wallD_start[1], wallD_end[1],
        wallE_start[1], wallE_end[1]
    ]
    ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
    ax.set_ylim(min(all_y) - 1, max(all_y) + 1)
    ax.set_zlim(0, h + 0.5)


def draw_floor_3d(ax, color, alpha):
    verts = [[
        (wallE_start[0], wallD_start[1], 0),
        (wallC_start[0], wallD_start[1], 0),
        (wallC_start[0], wallA_start[1], 0),
        (wallE_start[0], wallA_start[1], 0)
    ]]
    poly = Poly3DCollection(verts, alpha=alpha, facecolor=color, edgecolor="none")
    ax.add_collection3d(poly)


# ═══════════════════════════════════════════════════════════
#  MAIN SCRIPT
# ═══════════════════════════════════════════════════════════
def main():
    # ── Load files ──────────────────────────────────────────
    for f in (LIDAR_FILE, RANGE_FILE):
        if not os.path.exists(f):
            sys.exit(f"File not found: {f}")

    lidar_xy = np.loadtxt(LIDAR_FILE, delimiter=",")
    if lidar_xy.ndim == 1:
        lidar_xy = lidar_xy.reshape(-1, 1)
    if lidar_xy.shape[1] < 2:
        sys.exit("lidar_raw.csv must contain at least 2 numeric columns [X Y].")
    lidar_xy = lidar_xy[:, :2]
    lidar_xy = lidar_xy[np.all(np.isfinite(lidar_xy), axis=1)]

    ranges_raw = np.loadtxt(RANGE_FILE, delimiter=",").ravel()
    ranges_raw = ranges_raw[np.isfinite(ranges_raw)]

    N      = len(ranges_raw)
    angles = ANGLE_MIN + np.arange(N) * ANGLE_INCREMENT
    M      = min(len(ranges_raw), len(angles))
    ranges = ranges_raw[:M]
    angles = angles[:M]

    range_x = ranges * np.cos(angles)
    range_y = ranges * np.sin(angles)

    scan_pts = np.vstack([lidar_xy, np.column_stack([range_x, range_y])])
    scan_pts = scan_pts[np.all(np.isfinite(scan_pts), axis=1)]

    # ── Robot points ─────────────────────────────────────────
    ptsA = centred_robot_points(wallA_start, wallA_end, WALL_OFFSET, wallA_tStart, wallA_tEnd, "right")
    ptsB = centred_robot_points(wallB_start, wallB_end, WALL_OFFSET, wallB_tStart, wallB_tEnd, "right")
    ptsC = centred_robot_points(wallC_start, wallC_end, WALL_OFFSET, wallC_tStart, wallC_tEnd, "right")
    ptsD = centred_robot_points(wallD_start, wallD_end, WALL_OFFSET, wallD_tStart, wallD_tEnd, "right")
    ptsE = centred_robot_points(wallE_start, wallE_end, WALL_OFFSET, wallE_tStart, wallE_tEnd, "right")

    # ── Measurement points ───────────────────────────────────
    measA = compute_measurement_points(wallA_start, wallA_end, 1.00)
    measB = compute_measurement_points(wallB_start, wallB_end, 1.00)
    measC = compute_measurement_points(wallC_start, wallC_end, 1.00)
    measD = compute_measurement_points(wallD_start, wallD_end, 1.00)
    measE = compute_measurement_points(wallE_start, wallE_end, 1.00)

    # ── Look directions ──────────────────────────────────────
    faceA = look_vector_to_wall(wallA_start, wallA_end, "right", ARROW_LEN)
    faceB = look_vector_to_wall(wallB_start, wallB_end, "right", ARROW_LEN)
    faceC = look_vector_to_wall(wallC_start, wallC_end, "right", ARROW_LEN)
    faceD = look_vector_to_wall(wallD_start, wallD_end, "right", ARROW_LEN)
    faceE = look_vector_to_wall(wallE_start, wallE_end, "right", ARROW_LEN)

    # ── Start position ───────────────────────────────────────
    start_pos = ptsA[0].copy()

    x_min_in = wallE_start[0] + 0.01
    x_max_in = wallC_start[0] - 0.01
    y_min_in = wallD_start[1] + 0.01
    y_max_in = wallA_start[1] - 0.01

    inside_mask = (
        (scan_pts[:, 0] > x_min_in) & (scan_pts[:, 0] < x_max_in) &
        (scan_pts[:, 1] > y_min_in) & (scan_pts[:, 1] < y_max_in)
    )
    inside_scan_pts = scan_pts[inside_mask]

    if len(inside_scan_pts) == 0:
        sys.exit("No scan points were found inside the room boundary.")

    d_inside = np.linalg.norm(inside_scan_pts - start_pos, axis=1)
    idx_closest   = np.argmin(d_inside)
    closest_dist  = d_inside[idx_closest]
    robot_init    = inside_scan_pts[idx_closest]

    dx = robot_init[0] - start_pos[0]
    dy = robot_init[1] - start_pos[1]

    print("\n=================================================")
    print(" ROBOT START POSITION ANALYSIS")
    print("=================================================")
    print(f"Planned start point          : ({start_pos[0]:.4f}, {start_pos[1]:.4f}) m")
    print(f"Closest inside scan point    : ({robot_init[0]:.4f}, {robot_init[1]:.4f}) m")
    print(f"Horizontal offset            : {dx:+.4f} m")
    print(f"Vertical offset              : {dy:+.4f} m")
    print(f"Distance to start            : {closest_dist:.4f} m")
    print("=================================================")

    print("\n--- Robot Points Summary ---")
    print_wall_points("A", ptsA)
    print_wall_points("B", ptsB)
    print_wall_points("C", ptsC)
    print_wall_points("D", ptsD)
    print_wall_points("E", ptsE)

    # ── Build full path  A → B → C → D → E → Start ──────────
    path_pts  = []
    path_dirs = []

    def add(pts, face):
        path_pts.append(pts)
        path_dirs.append(np.tile(face, (len(pts), 1)) if pts.ndim == 2 else face[np.newaxis, :])

    add(robot_init[np.newaxis, :], faceA)
    add(start_pos[np.newaxis, :],  faceA)
    add(ptsA, faceA)
    add(ptsB[:1], faceB)
    add(ptsB, faceB)
    add(ptsC[:1], faceC)
    add(ptsC, faceC)
    add(ptsD[:1], faceD)
    add(ptsD, faceD)
    add(ptsE[:1], faceE)
    add(ptsE, faceE)
    add(start_pos[np.newaxis, :], faceA)

    path_pts  = np.vstack(path_pts)
    path_dirs = np.vstack(path_dirs)

    # ── Labels ───────────────────────────────────────────────
    labels = []
    labels.append("Robot placed at closest inside measured point")
    labels.append("Moving to planned start point")
    for i in range(len(ptsA)):
        labels.append(f"Painting Wall A – A{i+1}")
    labels.append("Transition to Wall B")
    for i in range(len(ptsB)):
        labels.append(f"Painting Wall B – B{i+1}")
    labels.append("Transition to Wall C")
    for i in range(len(ptsC)):
        labels.append(f"Painting Wall C – C{i+1}")
    labels.append("Transition to Wall D")
    for i in range(len(ptsD)):
        labels.append(f"Painting Wall D – D{i+1}")
    labels.append("Transition to Wall E")
    for i in range(len(ptsE)):
        labels.append(f"Painting Wall E – E{i+1}")
    labels.append("Returning to Start Position")

    # ═══════════════════════════════════════════════════════
    #  FIGURE 1 – Static 3-D overview
    # ═══════════════════════════════════════════════════════
    fig1 = plt.figure(figsize=(11, 8), facecolor="white")
    try:
        fig1.canvas.manager.set_window_title("3D Wall Simulation with Robot Path")
    except Exception:
        pass

    ax1 = fig1.add_subplot(111, projection="3d")
    ax1.set_xlabel("X (m)")
    ax1.set_ylabel("Y (m)")
    ax1.set_zlabel("Z (m)")
    ax1.set_title("3D Room Simulation – Robot Faces Main Wall")
    ax1.view_init(elev=25, azim=40)

    draw_floor_3d(ax1, (0.92, 0.92, 0.92), 0.35)
    for ws, we in [
        (wallA_start, wallA_end), (wallB_start, wallB_end),
        (wallC_start, wallC_end), (wallD_start, wallD_end),
        (wallE_start, wallE_end)
    ]:
        draw_wall_3d(ax1, ws, we, WALL_HEIGHT, (0.7, 0.7, 0.7))

    ax1.scatter(lidar_xy[:, 0], lidar_xy[:, 1], 0, color=(0.25, 0.25, 0.25), s=6, zorder=2)
    ax1.scatter(range_x, range_y, 0, color=(0.65, 0.80, 1.00), s=5, zorder=2)

    for pts, face, col in [
        (ptsA, faceA, "r"), (ptsB, faceB, "r"),
        (ptsC, faceC, "r"), (ptsD, faceD, "r"), (ptsE, faceE, "r")
    ]:
        plot_robot_pts_3(ax1, pts, ROBOT_Z, col)
        plot_heading_arrows_3(ax1, pts, ROBOT_Z, face, col)

    for meas in (measA, measB, measC, measD, measE):
        plot_meas_pts_3(ax1, meas, ROBOT_Z)

    ax1.plot(path_pts[:, 0], path_pts[:, 1], PATH_Z * np.ones(len(path_pts)), "g-", linewidth=2.5)

    ax1.scatter(*robot_init, ROBOT_Z, color="cyan", s=100, zorder=6)
    ax1.scatter(*start_pos,  ROBOT_Z, color="magenta", s=100, marker="s", zorder=6)

    label_wall(ax1, wallA_start, wallA_end, WALL_HEIGHT, "Wall A", 0)
    label_wall(ax1, wallB_start, wallB_end, WALL_HEIGHT, "Wall B", 0)
    label_wall(ax1, wallC_start, wallC_end, WALL_HEIGHT, "Wall C", 0.15)
    label_wall(ax1, wallD_start, wallD_end, WALL_HEIGHT, "Wall D", 0)
    label_wall(ax1, wallE_start, wallE_end, WALL_HEIGHT, "Wall E", -0.15)

    set_ax_limits(ax1, WALL_HEIGHT)
    plt.tight_layout()

    # ═══════════════════════════════════════════════════════
    #  FIGURE 2 – Animated dark "Raasta" figure
    # ═══════════════════════════════════════════════════════
    bg = (0.08, 0.08, 0.10)
    fig2 = plt.figure(figsize=(12, 9), facecolor=bg)
    try:
        fig2.canvas.manager.set_window_title("Raasta")
    except Exception:
        pass

    ax2 = fig2.add_subplot(111, projection="3d")
    ax2.set_facecolor(bg)
    ax2.set_xlabel("X (m)", color="white")
    ax2.set_ylabel("Y (m)", color="white")
    ax2.set_zlabel("Z (m)", color="white")
    ax2.set_title("Raasta", color="white")
    ax2.tick_params(colors="white")
    ax2.xaxis.pane.fill = False
    ax2.yaxis.pane.fill = False
    ax2.zaxis.pane.fill = False
    ax2.view_init(elev=28, azim=45)

    draw_floor_3d(ax2, (0.20, 0.20, 0.20), 0.45)
    for ws, we in [
        (wallA_start, wallA_end), (wallB_start, wallB_end),
        (wallC_start, wallC_end), (wallD_start, wallD_end),
        (wallE_start, wallE_end)
    ]:
        draw_wall_3d(ax2, ws, we, WALL_HEIGHT, (0.90, 0.90, 0.90))

    for pts, face in [(ptsA, faceA), (ptsB, faceB), (ptsC, faceC), (ptsD, faceD), (ptsE, faceE)]:
        plot_robot_pts_3(ax2, pts, ROBOT_Z, "r")
        plot_heading_arrows_3(ax2, pts, ROBOT_Z, face, "r")

    for meas in (measA, measB, measC, measD, measE):
        plot_meas_pts_3(ax2, meas, ROBOT_Z)

    for p1, p2, lbl, xoff in [
        (wallA_start, wallA_end, "Wall A",  0.00),
        (wallB_start, wallB_end, "Wall B",  0.00),
        (wallC_start, wallC_end, "Wall C",  0.15),
        (wallD_start, wallD_end, "Wall D",  0.00),
        (wallE_start, wallE_end, "Wall E", -0.15),
    ]:
        mx = (p1[0] + p2[0]) / 2 + xoff
        my = (p1[1] + p2[1]) / 2
        ax2.text(mx, my, WALL_HEIGHT + 0.08, lbl, color="white", fontweight="bold", ha="center")

    set_ax_limits(ax2, WALL_HEIGHT)

    trail_x, trail_y, trail_z = [path_pts[0, 0]], [path_pts[0, 1]], [PATH_Z]
    h_trail, = ax2.plot(trail_x, trail_y, trail_z, "-", color="lime", linewidth=2.5)

    h_bot = ax2.scatter(
        [path_pts[0, 0]], [path_pts[0, 1]], [ROBOT_Z],
        color="lime", s=130, edgecolors="white", linewidths=1.5, zorder=7
    )

    h_arrow = ax2.quiver(
        path_pts[0, 0], path_pts[0, 1], ROBOT_Z,
        path_dirs[0, 0], path_dirs[0, 1], 0,
        color="yellow", linewidth=2, length=1, normalize=False,
        arrow_length_ratio=0.4
    )

    h_info = ax2.text2D(
        0.02, 0.95, "",
        transform=ax2.transAxes,
        color="white",
        fontsize=9,
        fontweight="bold",
        verticalalignment="top"
    )

    plt.tight_layout()
    plt.show(block=False)

    # ── Animation loop ───────────────────────────────────────
    def bot_color(lbl):
        if "closest inside" in lbl:
            return (0, 1, 1)
        if "Moving to" in lbl:
            return (1, 1, 0)
        if "Transition" in lbl:
            return (1, 1, 0)
        if "Returning" in lbl:
            return (0, 1, 0)
        if "Wall A" in lbl:
            return (1, 0.4, 0.2)
        if "Wall B" in lbl:
            return (0.8, 0.5, 1)
        if "Wall C" in lbl:
            return (1, 0.8, 0.2)
        if "Wall D" in lbl:
            return (0.2, 1, 1)
        if "Wall E" in lbl:
            return (1, 0.2, 1)
        return (0, 1, 0)

    for i in range(len(path_pts)):
        trail_x.append(path_pts[i, 0])
        trail_y.append(path_pts[i, 1])
        trail_z.append(PATH_Z)
        h_trail.set_data_3d(trail_x, trail_y, trail_z)

        h_bot._offsets3d = (
            np.array([path_pts[i, 0]]),
            np.array([path_pts[i, 1]]),
            np.array([ROBOT_Z])
        )
        h_bot.set_color([bot_color(labels[i])])

        h_arrow.remove()
        h_arrow = ax2.quiver(
            path_pts[i, 0], path_pts[i, 1], ROBOT_Z,
            path_dirs[i, 0], path_dirs[i, 1], 0,
            color="yellow", linewidth=2, length=1, normalize=False,
            arrow_length_ratio=0.4
        )

        h_info.set_text(f"Step {i+1} / {len(path_pts)}\n{labels[i]}")
        fig2.canvas.draw()
        plt.pause(PAUSE_TIME)

    print("\n3D simulation complete")
    plt.show()

#---------------------------------------------------------------------
# Code added by viksit starts
#---------------------------------------------------------------------
def run_mobile_demo(selected_walls=None):
    
    if selected_walls is None:
        selected_walls = ["A", "B", "C", "D", "E"]

    selected_walls = [str(w).upper().strip() for w in selected_walls]

    print("\n" + "-" * 60)
    print("Mobile Base starting now")
    print(f"Selected walls from coordinator: {selected_walls}")
    print("Running Mobile base code...")
    print("-" * 60)

    main()

    return {
        "success": True,
        "selected_walls": selected_walls,
        "note": "Existing AllWalls.py - Mobile base code's main() executed successfully"
    }
    
#---------------------------------------------------------------------
# Code added by viksit ends
#---------------------------------------------------------------------
if __name__ == "__main__":
    main()