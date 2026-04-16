import numpy as np
from .create_rot_x import create_rot_x
from .create_rot_z import create_rot_z
from .create_trans import create_trans_x, create_trans_z


def forward(MDH):
    """
    Compute the Forward Kinematics of a 6-DOF robot from its MDH table.

    Each row of MDH is: [alpha, a, d, theta, theta_offset]

    Parameters:
        MDH (np.ndarray): 6x5 Modified Denavit-Hartenberg table with numeric joint values.

    Returns:
        tuple: (T01, T12, T23, T34, T45, T56, T06) — individual link transforms and full
               base-to-end-effector transform, each as 4x4 np.ndarray.
    """
    def link_transform(row):
        A = create_rot_x(row[0])
        B = create_trans_x(row[1])
        C = create_trans_z(row[2])
        D = create_rot_z(row[3], row[4])
        return A @ B @ C @ D

    T01 = link_transform(MDH[0])
    T12 = link_transform(MDH[1])
    T23 = link_transform(MDH[2])
    T34 = link_transform(MDH[3])
    T45 = link_transform(MDH[4])
    T56 = link_transform(MDH[5])

    T06 = T01 @ T12 @ T23 @ T34 @ T45 @ T56

    return T01, T12, T23, T34, T45, T56, T06
