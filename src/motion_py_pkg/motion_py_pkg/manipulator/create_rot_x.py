import numpy as np


def create_rot_x(a):
    """
    Create the 4x4 homogeneous transformation matrix for a rotation around the X axis.

    Parameters:
        a (float): Angle of rotation in radians.

    Returns:
        np.ndarray: 4x4 transformation matrix.
    """
    rotation = np.array([
        [1,       0,        0],
        [0, np.cos(a), -np.sin(a)],
        [0, np.sin(a),  np.cos(a)],
    ])
    translation = np.array([[0], [0], [0]])
    homogeneous = np.array([[0, 0, 0, 1]])

    return np.block([[rotation, translation], [homogeneous]])
