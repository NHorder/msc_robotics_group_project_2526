"""
VISNAT_Arm.py
=============
Python translation of VISNAT_Arm.m

Main entry point for the VISNAT painting robot arm:
  - Defines the MDH table and robot geometry
  - Plans the painting path (boustrophedon / zigzag)
  - Interpolates waypoints along the path
  - Computes inverse kinematics for every waypoint
  - Checks for singularities along the entire path
  - Plots the XYZ Cartesian path

Usage:
    th, overlapping_ratio = visnat_arm(top_l, bot_r)

    # Example (equivalent to MATLAB call):
    # th, r = visnat_arm([445.2, 500, 2700], [445.2, -500, 100])
"""
#%%

import math
import numpy as np
import matplotlib.pyplot as plt

from .inverse import inverse
from .jacobian import jacobian
from .verify import verify
#%%

# ---------------------------------------------------------------------------
# MDH helper — build a numeric MDH table given five joint angles
# ---------------------------------------------------------------------------

def _build_mdh(th1, th2, th3, th4, th5):
    """Return the 6×5 numeric MDH table for VISNAT at the given joint angles."""
    return np.array([
        [0,          0,      300,   th1,  0       ],
        [np.pi/2,    0,      0,     th2,  np.pi/2 ],
        [0,          900,    0,     th3,  0       ],
        [0,          1300,   0,     th4,  0       ],
        [-np.pi/2,   100,    0,     th5,  0       ],
        [0,          156.5,  0,     0,    0       ],
    ], dtype=float)


def visnat_arm(top_l, bot_r):
    """
    Plan and execute the VISNAT painting arm path.

    Parameters:
        top_l (array-like): [x, y, z] of the top-left corner of the painting surface (mm).
        bot_r (array-like): [x, y, z] of the bottom-right corner of the painting surface (mm).

    Returns:
        th               (np.ndarray): 5 × N array of joint angles (radians) for every
                                       interpolated path point.
        overlapping_ratio (float):     Ratio of total painting area to total overlap area.
    """
    top_l = np.asarray(top_l, dtype=float)
    bot_r = np.asarray(bot_r, dtype=float)

    # -----------------------------------------------------------------------
    # Robot constants
    # -----------------------------------------------------------------------
    BASE_SIZE     = 304.8   # mm
    ROLLER_SIZE   = 228.6   # mm
    MOVING_SPEED  = 500     # mm/s
    PAINTING_SPEED = 70     # mm/s

    # MDH link lengths used by Inverse()
    MDH_PARAMS = {
        'L1': 300,    # MDH[0, 2]  — d1
        'L2': 900,    # MDH[2, 1]  — a3
        'L3': 1300,   # MDH[3, 1]  — a4
        'L4': 100,    # MDH[4, 1]  — a5
        'L5': 156.5,  # MDH[5, 1]  — a6 (end-effector offset)
    }

    # Robot base position in the workstation
    robot_base = np.array([0.0, 0.0, 300.0])

    # -----------------------------------------------------------------------
    # Home position
    # -----------------------------------------------------------------------
    home = np.array([710.5, 0.0, 400.0])

    # -----------------------------------------------------------------------
    # Path geometry
    # -----------------------------------------------------------------------
    ymax_l = top_l[1] - (ROLLER_SIZE / 2) - 20
    ymax_r = bot_r[1] + (ROLLER_SIZE / 2) + 20
    ymax   = ymax_l - ymax_r

    nb_path = math.ceil(ymax / (ROLLER_SIZE - 10))
    y_disp  = ymax / nb_path

    one_overlap      = ROLLER_SIZE - y_disp
    total_overlap    = one_overlap * nb_path
    overlapping_ratio = ymax / total_overlap

    x_max_l = top_l[0] + BASE_SIZE
    x_max_r = bot_r[0] + BASE_SIZE
    xmax    = x_max_l - x_max_r
    x_disp  = xmax / nb_path

    z_max = top_l[2] - 60
    z_min = bot_r[2] + 60

    # -----------------------------------------------------------------------
    # Build waypoint list  (each column: [x, y, z, speed])
    # -----------------------------------------------------------------------
    def col(x, y, z, spd):
        return np.array([[x], [y], [z], [spd]])

    pos_path = col(*home, MOVING_SPEED)   # start at Home

    i = 0
    nb_path_loop = nb_path + 1  # same increment as MATLAB

    while i < nb_path_loop:
        # Going DOWN
        app_top = col(x_max_l + i*x_disp - 10, ymax_l - i*y_disp, z_max, MOVING_SPEED)
        top_pt  = col(x_max_l + i*x_disp,      ymax_l - i*y_disp, z_max, PAINTING_SPEED)
        bot_pt  = col(x_max_l + i*x_disp,      ymax_l - i*y_disp, z_min, PAINTING_SPEED)
        app_bot = col(x_max_l + i*x_disp - 10, ymax_l - i*y_disp, z_min, PAINTING_SPEED)
        pos_path = np.hstack([pos_path, app_top, top_pt, bot_pt, app_bot])
        i += 1

        if i + 1 <= nb_path_loop:
            # Going UP
            app_bot2 = col(x_max_l + i*x_disp - 10, ymax_l - i*y_disp, z_max, PAINTING_SPEED)
            bot_pt2  = col(x_max_l + i*x_disp,      ymax_l - i*y_disp, z_max, PAINTING_SPEED)
            top_pt2  = col(x_max_l + i*x_disp,      ymax_l - i*y_disp, z_min, PAINTING_SPEED)
            app_top2 = col(x_max_l + i*x_disp - 10, ymax_l - i*y_disp, z_min, MOVING_SPEED)
            pos_path = np.hstack([pos_path, app_top2, top_pt2, bot_pt2, app_bot2])
            i += 1

    pos_path = np.hstack([pos_path, col(*home, MOVING_SPEED)])  # return Home

    # -----------------------------------------------------------------------
    # Plot XYZ Cartesian path
    # -----------------------------------------------------------------------
    fig = plt.figure()
    ax  = fig.add_subplot(111, projection='3d')
    ax.plot(pos_path[0, :], pos_path[1, :], pos_path[2, :], '-x')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Robot XYZ Path')
    ax.set_aspect('equal')
    ax.grid(True)
    plt.tight_layout()
    plt.show()

    # -----------------------------------------------------------------------
    # Interpolate path: generate dense target positions
    # -----------------------------------------------------------------------
    dt = 0.5  # time step (s) between interpolated points

    target_pos = col(*home, MOVING_SPEED)  # start at Home

    for i in range(1, pos_path.shape[1]):
        p_prev = pos_path[:, i - 1]
        p_curr = pos_path[:, i]

        seg_dist   = np.linalg.norm(p_curr[:3] - p_prev[:3])
        speed      = p_curr[3]
        seg_nb_pos = max(1, math.ceil(seg_dist / (dt * speed)))

        for j in range(1, seg_nb_pos + 1):
            interp = p_prev + (p_curr - p_prev) * (j / seg_nb_pos)
            target_pos = np.hstack([target_pos, interp.reshape(4, 1)])

    # -----------------------------------------------------------------------
    # Inverse Kinematics for every interpolated point
    # -----------------------------------------------------------------------
    th_list = []
    n_pts   = target_pos.shape[1]

    print(f"Computing inverse kinematics for {n_pts} path points…")

    for i in range(n_pts):
        xyz = target_pos[:3, i]
        angles = inverse(MDH_PARAMS, robot_base, xyz, disp=False, name='VISNAT')
        th_list.append(angles)

    th = np.column_stack(th_list)   # shape: 5 × n_pts

    # -----------------------------------------------------------------------
    # Singularity verification
    # -----------------------------------------------------------------------
    print("Verifying singularities…")
    verify(th, _build_mdh(0, 0, 0, 0, 0), print_transforms=False, robot='VISNAT')

    return th, overlapping_ratio

#---------------------------------------------------------------------
# Code added by viksit starts
#---------------------------------------------------------------------
def run_manipulator_demo(wall_name: str):
    wall_name = str(wall_name).upper().strip()

    wall_regions = {
        "A": ([445.2,  500, 2700], [445.2, -500, 100]),
        "B": ([445.2,  500, 2700], [445.2, -500, 100]),
        "C": ([445.2,  500, 2700], [445.2, -500, 100]),
        "D": ([445.2,  500, 2700], [445.2, -500, 100]),
        "E": ([445.2,  500, 2700], [445.2, -500, 100]),
    }

    if wall_name not in wall_regions:
        raise ValueError(f"Unsupported wall name: {wall_name}")

    top_left, bottom_right = wall_regions[wall_name]

    print("\n" + "-" * 60)
    print("MANIPULATOR Code starts")
    print(f"Selected wall from coordinator: {wall_name}")
    print(f"Painting region top-left    : {top_left}")
    print(f"Painting region bottom-right: {bottom_right}")
    print("-" * 60)

    th, ratio = visnat_arm(top_left, bottom_right)

    return {
        "success": True,
        "wall_name": wall_name,
        "joint_trajectory_shape": th.shape,
        "overlap_ratio": float(ratio)
    }
#---------------------------------------------------------------------
# Code added by viksit ends
#---------------------------------------------------------------------    

# ---------------------------------------------------------------------------
# Script entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    top_left     = [445.2,  500, 2700]
    bottom_right = [445.2, -500,  100]

    th, ratio = visnat_arm(top_left, bottom_right)

    print(f"Overlapping ratio: {ratio:.4f}")
    print(f"Joint angle array shape: {th.shape}  (5 joints × {th.shape[1]} path points)")
