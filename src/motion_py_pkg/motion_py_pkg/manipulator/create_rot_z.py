import numpy as np


def create_rot_z(th, thoff):
    """
    Create the 4x4 homogeneous transformation matrix for a rotation around the Z axis.

    Parameters:
        th    (float): Angle of rotation in radians.
        thoff (float): Angle offset in radians (handles pi/2 and -pi/2 special cases).

    Returns:
        np.ndarray: 4x4 transformation matrix.
    """
    if np.isclose(thoff, -np.pi / 2):
        rotation = np.array([
            [ np.sin(th),  np.cos(th), 0],
            [-np.cos(th),  np.sin(th), 0],
            [          0,           0, 1],
        ])
    elif np.isclose(thoff, np.pi / 2):
        rotation = np.array([
            [-np.sin(th), -np.cos(th), 0],
            [ np.cos(th), -np.sin(th), 0],
            [          0,           0, 1],
        ])
    else:
        rotation = np.array([
            [np.cos(th), -np.sin(th), 0],
            [np.sin(th),  np.cos(th), 0],
            [         0,           0, 1],
        ])

    translation = np.array([[0], [0], [0]])
    homogeneous = np.array([[0, 0, 0, 1]])

    return np.block([[rotation, translation], [homogeneous]])
