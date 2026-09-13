# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.1
#  Release Date: 2026/09/30
#  Module: math3d.py
#  Description:
#      Provides low-level 3D mathematical utilities for handling vectors, rotation matrices, 
#      spatial transformations, and quaternions.
#
#  Copyright (C) 2026  Valeriy Shapovalov
#  Contact:
#      Email: valeriy.shapovalov79@gmail.com
#      GitHub: https://github.com/valeriy-sh79
#   
#  This file is part of SimPhant™.
#
#  SimPhant™ is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SimPhant™ is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SimPhant™.  If not, see <https://www.gnu.org/licenses/>.
# =============================================================================

import numpy as np
import math

def calculate_principal_axes(inertia_tensor):
    """
    Python port of Delphi's CalculatePrincipalAxes.
    Uses the Jacobi iterative method and enforces geometric X, Y, Z alignment.
    """
    A = np.array(inertia_tensor, dtype=float)
    V = np.eye(3, dtype=float)

    # 1. The Jacobi iterative diagonalization loop
    for step in range(50):
        p = 0; q = 1
        max_val = abs(A[0, 1])
        
        if abs(A[0, 2]) > max_val:
            max_val = abs(A[0, 2])
            p = 0; q = 2
        if abs(A[1, 2]) > max_val:
            max_val = abs(A[1, 2])
            p = 1; q = 2

        if max_val < 1E-8:
            break

        theta = (A[q, q] - A[p, p]) / (2.0 * A[p, q])
        if theta >= 0:
            t = 1.0 / (theta + math.sqrt(1.0 + theta*theta))
        else:
            t = -1.0 / (-theta + math.sqrt(1.0 + theta*theta))

        c = 1.0 / math.sqrt(1.0 + t*t)
        s = t * c
        tau = s / (1.0 + c)

        temp_A = A[p, q]
        A[p, q] = 0.0
        A[q, p] = 0.0
        A[p, p] = A[p, p] - t * temp_A
        A[q, q] = A[q, q] + t * temp_A

        for i in range(3):
            if i != p and i != q:
                temp_A = A[p, i]
                A[p, i] = temp_A - s * (A[q, i] + tau * temp_A)
                A[i, p] = A[p, i]
                A[q, i] = A[q, i] + s * (temp_A - tau * A[q, i])
                A[i, q] = A[q, i]

        for i in range(3):
            temp_V = V[i, p]
            V[i, p] = temp_V - s * (V[i, q] + tau * temp_V)
            V[i, q] = V[i, q] + s * (temp_V - tau * V[i, q])

    # 2. Force Eigenvectors to align with geometric X, Y, Z axes
    target_col = [0, 0, 0]
    used = [False, False, False]

    for col in range(3):
        max_val = -1.0
        max_idx = 0
        for row in range(3):
            if abs(V[row, col]) > max_val and not used[row]:
                max_val = abs(V[row, col])
                max_idx = row
        target_col[col] = max_idx
        used[max_idx] = True

    NewV = np.zeros((3, 3))
    NewA = np.zeros((3, 3))

    for col in range(3):
        for row in range(3):
            NewV[row, target_col[col]] = V[row, col]
        NewA[target_col[col], target_col[col]] = A[col, col]

    for col in range(3):
        for row in range(3):
            V[row, col] = NewV[row, col]
        A[col, col] = NewA[col, col]

    I1, I2, I3 = A[0, 0], A[1, 1], A[2, 2]

    # 3. Ensure a Right-Handed Coordinate System (Determinant check)
    det = (V[0, 0] * (V[1, 1] * V[2, 2] - V[1, 2] * V[2, 1]) -
           V[0, 1] * (V[1, 0] * V[2, 2] - V[1, 2] * V[2, 0]) +
           V[0, 2] * (V[1, 0] * V[2, 1] - V[1, 1] * V[2, 0]))

    if det < 0:
        V[0, 2] = -V[0, 2]
        V[1, 2] = -V[1, 2]
        V[2, 2] = -V[2, 2]

    principal_inertia = np.array([I1, I2, I3])
    rot_mat = V

    return principal_inertia, rot_mat