"""
Robot Painting Path Simulation — Python equivalent of the MATLAB code.
Requires: numpy, matplotlib
Install:  pip install numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.animation as animation
import time

# ============================================================
# PARAMETERS
# ============================================================
LIDAR_FILE      = 'lidar_raw.csv'
RANGE_FILE      = 'ranges_raw.csv'

WALL_OFFSET     = 0.75      # 75 cm from painted wall
PAUSE_TIME      = 0.50      # animation frame pause (seconds)
WALL_HEIGHT     = 3.048     # 10 ft in metres
ROBOT_Z         = 0.10
PATH_Z          = 0.05
ARROW_LEN       = 0.35

ANGLE_MIN       = -3.141590118408203
ANGLE_INCREMENT =  0.003929443191736937

# ============================================================
# WALL DEFINITIONS
# ============================================================
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

# ============================================================
# SIDE GAP RANGES
# ============================================================
wallA_tStart = 0.50
wallA_tEnd   = np.linalg.norm(wallA_end - wallA_start) - 0.50

wallD_tStart = 0.50
wallD_tEnd   = np.linalg.norm(wallD_end - wallD_start) - 0.50

wallE_tStart = 0.50
wallE_tEnd   = np.linalg.norm(wallE_end - wallE_start) - 0.50


# ============================================================
# LOCAL FUNCTIONS
# ============================================================

def centred_robot_points(p1, p2, wall_offset, t_start, t_end, side_choice):
    """Place robot points at midpoints of 1m segments within [t_start, t_end]."""
    dir_vec  = p2 - p1
    L        = np.linalg.norm(dir_vec)
    unit_vec = dir_vec / L

    left_normal  = np.array([-unit_vec[1],  unit_vec[0]])
    right_normal = np.array([ unit_vec[1], -unit_vec[0]])

    if side_choice.lower() == 'left':
        normal_vec = left_normal
    elif side_choice.lower() == 'right':
        normal_vec = right_normal
    else:
        raise ValueError("side_choice must be 'left' or 'right'")

    if t_end < t_start:
        raise ValueError(f"t_end ({t_end:.3f}) < t_start ({t_start:.3f}): wall too short")

    all_midpoints = np.arange(0.5, L - 0.5 + 1e-9, 1.0)
    t_vals = all_midpoints[(all_midpoints >= t_start) & (all_midpoints <= t_end)]

    if len(t_vals) == 0:
        t_vals = np.array([(t_start + t_end) / 2])

    if abs(t_vals[-1] - t_end) > 1e-9:
        t_vals = np.append(t_vals, t_end)

    pts = np.array([p1 + t * unit_vec + wall_offset * normal_vec for t in t_vals])
    return pts


def look_vector_to_wall(p1, p2, side_choice, arrow_len):
    """Unit vector pointing FROM robot TOWARD the wall it is painting."""
    dir_vec  = p2 - p1
    unit_vec = dir_vec / np.linalg.norm(dir_vec)

    left_normal  = np.array([-unit_vec[1],  unit_vec[0]])
    right_normal = np.array([ unit_vec[1], -unit_vec[0]])

    if side_choice.lower() == 'left':
        inward = left_normal
    elif side_choice.lower() == 'right':
        inward = right_normal
    else:
        raise ValueError("side_choice must be 'left' or 'right'")

    return -arrow_len * inward   # point back toward wall


def compute_measurement_points(p1, p2, measure_step):
    """Yellow 1m measurement points along the wall."""
    dir_vec  = p2 - p1
    L        = np.linalg.norm(dir_vec)
    unit_vec = dir_vec / L
    t_vals   = np.arange(0, L + 1e-9, measure_step)
    t_vals   = t_vals[t_vals <= L]
    return np.array([p1 + t * unit_vec for t in t_vals])


def draw_wall_3d(ax, p1, p2, height, face_color, alpha=0.65):
    """Draw an extruded wall as a 3D patch."""
    xs = [p1[0], p2[0], p2[0], p1[0]]
    ys = [p1[1], p2[1], p2[1], p1[1]]
    zs = [0,     0,     height, height]
    verts = [list(zip(xs, ys, zs))]
    poly  = Poly3DCollection(verts, alpha=alpha,
                             facecolor=face_color, edgecolor=[0.2,0.2,0.2],
                             linewidth=0.8)
    ax.add_collection3d(poly)


def plot_robot_pts_3d(ax, pts, rz, color):
    ax.scatter(pts[:,0], pts[:,1], rz * np.ones(len(pts)),
               c=[color], s=50, zorder=5)


def plot_heading_arrows_3d(ax, pts, rz, face_vec, color):
    ax.quiver(pts[:,0], pts[:,1], rz * np.ones(len(pts)),
              face_vec[0] * np.ones(len(pts)),
              face_vec[1] * np.ones(len(pts)),
              np.zeros(len(pts)),
              color=color, linewidth=1.4, length=1.0, normalize=False)


def plot_meas_pts_3d(ax, pts, rz):
    ax.scatter(pts[:,0], pts[:,1], rz * np.ones(len(pts)),
               c='yellow', s=35, zorder=4, edgecolors='goldenrod', linewidths=0.5)


def set_ax_limits(ax, height):
    ax.set_xlim([min(wallE_start[0], wallD_end[0]) - 1,
                 max(wallC_start[0], wallD_start[0]) + 1])
    ax.set_ylim([min(wallD_start[1], wallE_start[1]) - 1,
                 max(wallA_start[1], wallE_end[1]) + 1])
    ax.set_zlim([0, height + 0.5])


def print_wall_points(name, pts):
    print(f"Wall {name}: {len(pts)} robot points")
    for k, p in enumerate(pts):
        print(f"  {name}{k+1} : ({p[0]:.4f}, {p[1]:.4f})")


# ============================================================
# LOAD DATA
# ============================================================
lidar_xy = np.loadtxt(LIDAR_FILE, delimiter=',')
if lidar_xy.ndim == 1:
    lidar_xy = lidar_xy.reshape(1, -1)
lidar_xy = lidar_xy[:, :2]
lidar_xy = lidar_xy[np.all(np.isfinite(lidar_xy), axis=1)]

ranges_raw = np.loadtxt(RANGE_FILE, delimiter=',').flatten()
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

# ============================================================
# ROBOT POINTS
# ============================================================
pts_A = centred_robot_points(wallA_start, wallA_end, WALL_OFFSET,
                              wallA_tStart, wallA_tEnd, 'right')
pts_D = centred_robot_points(wallD_start, wallD_end, WALL_OFFSET,
                              wallD_tStart, wallD_tEnd, 'right')
pts_E = centred_robot_points(wallE_start, wallE_end, WALL_OFFSET,
                              wallE_tStart, wallE_tEnd, 'right')

# ============================================================
# LOOK DIRECTION VECTORS
# ============================================================
face_A = look_vector_to_wall(wallA_start, wallA_end, 'right', ARROW_LEN)
face_D = look_vector_to_wall(wallD_start, wallD_end, 'right', ARROW_LEN)
face_E = look_vector_to_wall(wallE_start, wallE_end, 'right', ARROW_LEN)

# ============================================================
# YELLOW MEASUREMENT POINTS
# ============================================================
meas_A = compute_measurement_points(wallA_start, wallA_end, 1.00)
meas_D = compute_measurement_points(wallD_start, wallD_end, 1.00)
meas_E = compute_measurement_points(wallE_start, wallE_end, 1.00)

# ============================================================
# START POSITION
# ============================================================
start_pos = pts_A[0].copy()

x_min = wallE_start[0] + 0.01
x_max = wallC_start[0] - 0.01
y_min = wallD_start[1] + 0.01
y_max = wallA_start[1] - 0.01

inside_mask = (
    (scan_pts[:,0] > x_min) & (scan_pts[:,0] < x_max) &
    (scan_pts[:,1] > y_min) & (scan_pts[:,1] < y_max)
)
inside_scan_pts = scan_pts[inside_mask]

if len(inside_scan_pts) == 0:
    raise RuntimeError("No scan points found inside the room boundary.")

d_inside     = np.linalg.norm(inside_scan_pts - start_pos, axis=1)
idx_closest  = np.argmin(d_inside)
closest_dist = d_inside[idx_closest]
robot_init   = inside_scan_pts[idx_closest].copy()

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
print("=================================================\n")
print("--- Robot Points Summary ---")
print_wall_points('A', pts_A)
print_wall_points('D', pts_D)
print_wall_points('E', pts_E)

# ============================================================
# BUILD PATH:  A -> D -> E -> START
# ============================================================
path_pts  = []
path_dirs = []

def add_pts(pts, face):
    for p in pts:
        path_pts.append(p)
        path_dirs.append(face)

add_pts([robot_init], face_A)
add_pts([start_pos],  face_A)
add_pts(pts_A,        face_A)
add_pts([pts_D[0]],   face_D)
add_pts(pts_D,        face_D)
add_pts([pts_E[0]],   face_E)
add_pts(pts_E,        face_E)
add_pts([start_pos],  face_A)

path_pts  = np.array(path_pts)
path_dirs = np.array(path_dirs)

# ============================================================
# LABELS
# ============================================================
labels = []
labels.append("Robot placed at closest inside measured point")
labels.append("Moving to planned start point")
for i in range(len(pts_A)):
    labels.append(f"Painting Wall A – A{i+1}")
labels.append("Transition to Wall D")
for i in range(len(pts_D)):
    labels.append(f"Painting Wall D – D{i+1}")
labels.append("Transition to Wall E")
for i in range(len(pts_E)):
    labels.append(f"Painting Wall E – E{i+1}")
labels.append("Returning to Start Position")

# ============================================================
# 3D STATIC FIGURE
# ============================================================
fig1 = plt.figure(figsize=(12,8), facecolor='white')
ax1  = fig1.add_subplot(111, projection='3d')
ax1.set_facecolor('white')
ax1.set_xlabel('X (m)'); ax1.set_ylabel('Y (m)'); ax1.set_zlabel('Z (m)')
ax1.set_title('3D Room Simulation – Painting Wall A, D and E')
ax1.view_init(elev=25, azim=40)

# Floor
xx = [wallE_start[0], wallC_start[0], wallC_start[0], wallE_start[0]]
yy = [wallD_start[1], wallD_start[1], wallA_start[1], wallA_start[1]]
zz = [0, 0, 0, 0]
floor_poly = Poly3DCollection([list(zip(xx,yy,zz))], alpha=0.35,
                               facecolor=[0.92,0.92,0.92], edgecolor='none')
ax1.add_collection3d(floor_poly)

wall_col = [0.7, 0.7, 0.7]
for ws, we in [(wallA_start,wallA_end),(wallB_start,wallB_end),
               (wallC_start,wallC_end),(wallD_start,wallD_end),(wallE_start,wallE_end)]:
    draw_wall_3d(ax1, ws, we, WALL_HEIGHT, wall_col)

ax1.scatter(lidar_xy[:,0], lidar_xy[:,1], np.zeros(len(lidar_xy)),
            c=[[0.25,0.25,0.25]], s=8)
ax1.scatter(range_x, range_y, np.zeros(len(range_x)),
            c=[[0.65,0.80,1.00]], s=6)

plot_robot_pts_3d(ax1, pts_A, ROBOT_Z, 'red')
plot_heading_arrows_3d(ax1, pts_A, ROBOT_Z, face_A, 'red')
plot_robot_pts_3d(ax1, pts_D, ROBOT_Z, 'red')
plot_heading_arrows_3d(ax1, pts_D, ROBOT_Z, face_D, 'red')
plot_robot_pts_3d(ax1, pts_E, ROBOT_Z, 'red')
plot_heading_arrows_3d(ax1, pts_E, ROBOT_Z, face_E, 'red')

plot_meas_pts_3d(ax1, meas_A, ROBOT_Z)
plot_meas_pts_3d(ax1, meas_D, ROBOT_Z)
plot_meas_pts_3d(ax1, meas_E, ROBOT_Z)

ax1.plot(path_pts[:,0], path_pts[:,1],
         PATH_Z * np.ones(len(path_pts)), 'g-', linewidth=2.5)
ax1.scatter(*robot_init, ROBOT_Z, c='cyan',   s=100, zorder=6)
ax1.scatter(*start_pos,  ROBOT_Z, c='magenta', s=100, marker='s', zorder=6)

for ws, we, lbl, xoff in [
        (wallA_start, wallA_end, 'Wall A',  0),
        (wallD_start, wallD_end, 'Wall D',  0),
        (wallE_start, wallE_end, 'Wall E', -0.15)]:
    mx = (ws[0] + we[0]) / 2 + xoff
    my = (ws[1] + we[1]) / 2
    ax1.text(mx, my, WALL_HEIGHT + 0.1, lbl, fontweight='bold', ha='center')

set_ax_limits(ax1, WALL_HEIGHT)

# ============================================================
# 3D ANIMATION FIGURE
# ============================================================
fig2 = plt.figure(figsize=(12,8), facecolor=[0.08,0.08,0.10])
ax2  = fig2.add_subplot(111, projection='3d')
ax2.set_facecolor([0.08,0.08,0.10])
ax2.xaxis.pane.fill = False
ax2.yaxis.pane.fill = False
ax2.zaxis.pane.fill = False
ax2.tick_params(colors='white')
ax2.xaxis.label.set_color('white')
ax2.yaxis.label.set_color('white')
ax2.zaxis.label.set_color('white')
ax2.set_xlabel('X (m)'); ax2.set_ylabel('Y (m)'); ax2.set_zlabel('Z (m)')
ax2.set_title('3D Robot Painting Simulation – Wall A, D and E', color='white')
ax2.view_init(elev=28, azim=45)

floor_poly2 = Poly3DCollection([list(zip(xx,yy,zz))], alpha=0.45,
                                facecolor=[0.20,0.20,0.20], edgecolor='none')
ax2.add_collection3d(floor_poly2)

wall_col2 = [0.90, 0.90, 0.90]
for ws, we in [(wallA_start,wallA_end),(wallB_start,wallB_end),
               (wallC_start,wallC_end),(wallD_start,wallD_end),(wallE_start,wallE_end)]:
    draw_wall_3d(ax2, ws, we, WALL_HEIGHT, wall_col2)

plot_robot_pts_3d(ax2, pts_A, ROBOT_Z, 'red')
plot_heading_arrows_3d(ax2, pts_A, ROBOT_Z, face_A, 'red')
plot_robot_pts_3d(ax2, pts_D, ROBOT_Z, 'red')
plot_heading_arrows_3d(ax2, pts_D, ROBOT_Z, face_D, 'red')
plot_robot_pts_3d(ax2, pts_E, ROBOT_Z, 'red')
plot_heading_arrows_3d(ax2, pts_E, ROBOT_Z, face_E, 'red')

plot_meas_pts_3d(ax2, meas_A, ROBOT_Z)
plot_meas_pts_3d(ax2, meas_D, ROBOT_Z)
plot_meas_pts_3d(ax2, meas_E, ROBOT_Z)

for ws, we, lbl, xoff in [
        (wallA_start, wallA_end, 'Wall A',  0),
        (wallD_start, wallD_end, 'Wall D',  0),
        (wallE_start, wallE_end, 'Wall E', -0.15)]:
    mx = (ws[0] + we[0]) / 2 + xoff
    my = (ws[1] + we[1]) / 2
    ax2.text(mx, my, WALL_HEIGHT + 0.08, lbl,
             color='white', fontweight='bold', ha='center')

set_ax_limits(ax2, WALL_HEIGHT)

# Animated elements
trail_line, = ax2.plot([], [], [], '-', color='lime', linewidth=2.5)
robot_dot   = ax2.scatter([], [], [], c='lime', s=130,
                          edgecolors='white', linewidths=1.5, zorder=10)
info_text   = ax2.text2D(0.02, 0.95, '', transform=ax2.transAxes,
                          color='white', fontsize=9, fontweight='bold',
                          verticalalignment='top')

# Quiver for animated arrow (rebuild each frame as quiver doesn't update cleanly)
arrow_container = [None]

def get_robot_color(lbl):
    if "closest inside" in lbl: return 'cyan'
    if "Moving to"      in lbl: return 'yellow'
    if "Transition"     in lbl: return 'yellow'
    if "Returning"      in lbl: return 'lime'
    if "Wall A"         in lbl: return '#FF6633'
    if "Wall D"         in lbl: return '#33FFFF'
    if "Wall E"         in lbl: return '#FF33FF'
    return 'lime'

def animate(i):
    # Trail
    trail_line.set_data(path_pts[:i+1,0], path_pts[:i+1,1])
    trail_line.set_3d_properties(PATH_Z * np.ones(i+1))

    # Robot dot
    robot_dot._offsets3d = (
        np.array([path_pts[i,0]]),
        np.array([path_pts[i,1]]),
        np.array([ROBOT_Z])
    )

    # Remove old arrow, draw new one
    if arrow_container[0] is not None:
        arrow_container[0].remove()
    arrow_container[0] = ax2.quiver(
        path_pts[i,0], path_pts[i,1], ROBOT_Z,
        path_dirs[i,0], path_dirs[i,1], 0,
        color='yellow', linewidth=2, length=1.0, normalize=False
    )

    lbl = labels[i]
    info_text.set_text(f"Step {i+1} / {len(path_pts)}\n{lbl}")

    # Colour
    col = get_robot_color(lbl)
    robot_dot.set_facecolor(col)

    return trail_line, robot_dot, info_text

ani = animation.FuncAnimation(
    fig2, animate,
    frames=len(path_pts),
    interval=int(PAUSE_TIME * 1000),
    blit=False,
    repeat=False
)

print("\n3D simulation complete")
plt.tight_layout()
plt.show()