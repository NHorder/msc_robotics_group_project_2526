import numpy as np
from .forward import forward
from .jacobian import jacobian


def verify(path_angles, MDH_base, print_transforms=False, robot="Robot"):
    """
    Verify the inverse kinematics solution and check for singularities along the path.

    Parameters:
        path_angles     (np.ndarray): 5 x N array of joint angles (radians) for each path point.
        MDH_base        (np.ndarray): 6x5 MDH table (with symbolic theta positions — angles
                                      are substituted per path point inside this function).
        print_transforms (bool):      If True, print T06 at every path point.
        robot           (str):        Robot name for display output.
    """
    n_points = path_angles.shape[1]
    singular = False
    close    = False

    for i in range(n_points):
        th = path_angles[:, i]          # [TH1 … TH5]

        # Build numeric MDH for this configuration
        MDH_num = MDH_base.copy().astype(float)
        MDH_num[0, 3] = th[0]
        MDH_num[1, 3] = th[1]
        MDH_num[2, 3] = th[2]
        MDH_num[3, 3] = th[3]
        MDH_num[4, 3] = th[4]
        # Row 5 (joint 6) has a fixed angle of 0 — already set in the base table.

        if print_transforms:
            _, _, _, _, _, _, T06 = forward(MDH_num) if False else (None,)*7  # placeholder
            # Re-use jacobian's internal forward call below; compute T06 separately
            from forward import forward as fwd
            T06 = fwd(MDH_num)[-1]
            print(f"Transformation Matrix T for the {robot} at target {i + 1}:")
            print(T06, "\n")

        J, LinJ = jacobian(MDH_num)

        r_lin  = np.linalg.matrix_rank(LinJ)
        r_full = np.linalg.matrix_rank(J)
        s_lin  = np.linalg.svd(LinJ, compute_uv=False)
        s_full = np.linalg.svd(J,    compute_uv=False)

        if r_lin < 3 or r_full < 5:
            print(f"Determinant of the {robot} is zero at target {i + 1}, singular configuration.")
            singular = True
        elif np.min(s_lin) < 1e-4 or np.min(s_full) < 1e-4:
            print(f"Jacobian is close to singular at target {i + 1} for the {robot}.")
            close = True

    if singular:
        print("\nYour path is not safe as you are at a singularity at some point.\n")
    elif close:
        print("\nYour path may not be safe as you are close to singularity.\n")
    else:
        print("\nYour path is completely safe.\n")
