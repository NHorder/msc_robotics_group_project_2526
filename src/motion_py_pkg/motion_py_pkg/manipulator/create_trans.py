import numpy as np


def create_trans_x(a):
    """
    Create the 4x4 homogeneous transformation matrix for a translation along the X axis.

    Parameters:
        a (float): Distance of translation in mm.

    Returns:
        np.ndarray: 4x4 transformation matrix.
    """
    return np.array([
        [1, 0, 0, a],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ], dtype=float)


def create_trans_z(d):
    """
    Create the 4x4 homogeneous transformation matrix for a translation along the Z axis.

    Parameters:
        d (float): Distance of translation in mm.

    Returns:
        np.ndarray: 4x4 transformation matrix.
    """
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, d],
        [0, 0, 0, 1],
    ], dtype=float)
