import numpy as np
from .forward import forward


def jacobian(MDH):
    """
    Compute the Jacobian (and its linear sub-matrix) for the VISNAT robot at a given
    joint configuration.

    Parameters:
        MDH (np.ndarray): 6x5 MDH table with *numeric* joint angles already substituted.

    Returns:
        tuple:
            J    (np.ndarray): 6x5 full Jacobian matrix.
            LinJ (np.ndarray): 3x5 linear-velocity sub-matrix (top 3 rows of J).
    """
    T01, T12, T23, T34, T45, T56, T06 = forward(MDH)

    T02 = T01 @ T12
    T03 = T02 @ T23
    T04 = T03 @ T34
    T05 = T04 @ T45

    # Z-axis (column 2, 0-indexed) of each frame — rotation axes for revolute joints
    R01 = T01[:3, 2]
    R02 = T02[:3, 2]
    R03 = T03[:3, 2]
    R04 = T04[:3, 2]
    R05 = T05[:3, 2]

    # Origin of each frame (translation column)
    D01 = T01[:3, 3]
    D02 = T02[:3, 3]
    D03 = T03[:3, 3]
    D04 = T04[:3, 3]
    D05 = T05[:3, 3]
    D06 = T06[:3, 3]

    # Vectors from each joint origin to the end-effector
    D16 = D06 - D01
    D26 = D06 - D02
    D36 = D06 - D03
    D46 = D06 - D04
    D56 = D06 - D05

    # Linear velocity rows: z_i × (p_e − p_i)
    J1 = np.cross(R01, D16)
    J2 = np.cross(R02, D26)
    J3 = np.cross(R03, D36)
    J4 = np.cross(R04, D46)
    J5 = np.cross(R05, D56)

    # Full 6x5 Jacobian: [linear; angular]
    J = np.vstack([
        np.column_stack([J1, J2, J3, J4, J5]),   # linear  (3x5)
        np.column_stack([R01, R02, R03, R04, R05]) # angular (3x5)
    ])

    LinJ = J[:3, :]

    return J, LinJ
