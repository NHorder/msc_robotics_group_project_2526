import numpy as np


def inverse(MDH_params, base, target, disp=False, name="Robot"):
    """
    Determine the Inverse Kinematics of the VISNAT 5-DOF robot arm.

    Parameters:
        MDH_params (dict): Robot link lengths extracted from the MDH table:
                           {'L1': float, 'L2': float, 'L3': float, 'L4': float, 'L5': float}
        base       (array-like): [x, y, z] position of the robot base in the workstation (mm).
        target     (array-like): [x, y, z] target position in the workstation (mm).
        disp       (bool):       If True, print joint angles and position info.
        name       (str):        Robot name used in display output.

    Returns:
        np.ndarray: Column vector [TH1, TH2, TH3, TH4, TH5] of joint angles in radians.
    """
    L1 = MDH_params['L1']
    L2 = MDH_params['L2']
    L3 = MDH_params['L3']
    L4 = MDH_params['L4']
    L5 = MDH_params['L5']

    base = np.asarray(base, dtype=float).flatten()
    target = np.asarray(target, dtype=float).flatten()

    # Target in robot frame
    xPR = target[0] - base[0] - 54 - L5
    yPR = target[1] - base[1]
    zPR = target[2] - base[2] - L1

    # --- Theta 1 ---
    TH1 = np.arctan2(yPR, xPR)

    # --- Theta 2 ---
    OAxy = np.sqrt(xPR**2 + yPR**2) - L4
    OA   = np.sqrt(OAxy**2 + zPR**2)

    c = L2
    a = L3
    b = OA

    alpha = np.arccos(np.clip((b**2 + c**2 - a**2) / (2 * b * c), -1.0, 1.0))

    TH2 = -np.pi / 2 + np.arctan2(zPR, OAxy) + alpha

    # --- Theta 3 ---
    beta = np.arccos(np.clip((a**2 + c**2 - b**2) / (2 * a * c), -1.0, 1.0))
    TH3  = -np.pi + beta

    # --- Theta 4 (keeps link 5 horizontal) ---
    TH4 = -np.pi / 2 - TH2 - TH3

    # --- Theta 5 (keeps end-effector aligned with X axis) ---
    TH5 = -TH1

    if disp:
        print(f"Position values (mm) for {name} position, with respect to the base of VISNAT:")
        print(f"  x: {xPR + L5 + 54:.5f}")
        print(f"  y: {yPR:.5f}")
        print(f"  z: {zPR + L1:.5f}\n")

        print(f"Theta values (degrees) for {name} position:")
        for label, val in zip(["TH1", "TH2", "TH3", "TH4", "TH5"],
                               [TH1, TH2, TH3, TH4, TH5]):
            print(f"  {label}: {np.degrees(val):.5f}°")
        print()

    return np.array([TH1, TH2, TH3, TH4, TH5])
