# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.10.0
#  Module: math_kernels.py
#  Description:
#      Provides optimized mathematical kernels for multibody dynamics simulations, including
#      functions for handling rotational and translational locks, as well as other common
#      vector and matrix operations used in the simulation engine.
#
#  Copyright (C) 2026  Valeriy Shapovalov
#  GitHub: https://github.com/valeriy-sh79
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
from numba import njit

_NUMBA_WARMED_UP = False

# ==========================================
# NUMBA HELPER MATH FUNCTIONS
# ==========================================
@njit(fastmath=True)
def skew(v):
    return np.array([
        [0.0, -v[2], v[1]],
        [v[2], 0.0, -v[0]],
        [-v[1], v[0], 0.0]
    ])

@njit(fastmath=True)
def assign_spherical_lock(Phi_q, gamma_star, row_idx, col_i, col_j,
                          r_i, r_j, s_i_glob, s_j_glob, v_i, v_j, 
                          w_i, w_j, sp_i, sp_j, A_i, A_j, alpha, beta):
    Phi = (r_i + s_i_glob) - (r_j + s_j_glob)
    w_cross_sp_i = np.cross(w_i, sp_i)
    w_cross_sp_j = np.cross(w_j, sp_j)
    Phi_dot = (v_i + A_i @ w_cross_sp_i) - (v_j + A_j @ w_cross_sp_j)
    
    acc_cent_i = np.cross(w_i, w_cross_sp_i)
    acc_cent_j = np.cross(w_j, w_cross_sp_j)
    gamma = -A_i @ acc_cent_i + A_j @ acc_cent_j
    g_star = gamma - (2.0 * alpha * Phi_dot) - ((beta ** 2) * Phi)
    
    J_wi_sph = -A_i @ skew(sp_i)
    J_wj_sph = A_j @ skew(sp_j)
    
    for m in range(3):
        if col_i >= 0:
            Phi_q[row_idx + m, col_i + m] = 1.0
            Phi_q[row_idx + m, col_i+3:col_i+6] = J_wi_sph[m, :]
        if col_j >= 0:
            Phi_q[row_idx + m, col_j + m] = -1.0
            Phi_q[row_idx + m, col_j+3:col_j+6] = J_wj_sph[m, :]
        gamma_star[row_idx + m] = g_star[m]

@njit(fastmath=True)
def assign_rotational_lock(Phi_q, gamma_star, row_idx, col_i, col_j, 
                           vec_i, vec_j, vec_dot_i, vec_dot_j, vec_cent_i, vec_cent_j, 
                           A_i, A_j, alpha, beta):
    Phi = np.dot(vec_i, vec_j)
    Phi_dot = np.dot(vec_dot_i, vec_j) + np.dot(vec_i, vec_dot_j)
    gamma = -(np.dot(vec_cent_i, vec_j) + 2.0 * np.dot(vec_dot_i, vec_dot_j) + np.dot(vec_i, vec_cent_j))
    
    if col_i >= 0: Phi_q[row_idx, col_i+3:col_i+6] = A_i.T @ np.cross(vec_i, vec_j)
    if col_j >= 0: Phi_q[row_idx, col_j+3:col_j+6] = A_j.T @ np.cross(vec_j, vec_i)
    gamma_star[row_idx] = gamma - (2.0 * alpha * Phi_dot) - ((beta ** 2) * Phi)

@njit(fastmath=True)
def assign_translational_lock(Phi_q, gamma_star, row_idx, col_i, col_j,
                              d, d_dot, d_cent, vec_i, vec_dot_i, vec_cent_i,
                              s_i_glob, s_j_glob, A_i, A_j, alpha, beta):
    Phi = np.dot(d, vec_i)
    Phi_dot = np.dot(d_dot, vec_i) + np.dot(d, vec_dot_i)
    gamma = -(np.dot(d_cent, vec_i) + 2.0 * np.dot(d_dot, vec_dot_i) + np.dot(d, vec_cent_i))
    
    if col_i >= 0:
        Phi_q[row_idx, col_i:col_i+3] = -vec_i
        Phi_q[row_idx, col_i+3:col_i+6] = A_i.T @ np.cross(vec_i, d + s_i_glob)
    if col_j >= 0:
        Phi_q[row_idx, col_j:col_j+3] = vec_i
        Phi_q[row_idx, col_j+3:col_j+6] = A_j.T @ np.cross(s_j_glob, vec_i)
    gamma_star[row_idx] = gamma - (2.0 * alpha * Phi_dot) - ((beta ** 2) * Phi)


# ==========================================
# CORE JIT-COMPILED SOLVER KERNELS
# ==========================================

@njit(fastmath=True)
def assemble_jacobian_numba(num_equations, num_states_vel, j_types, b_idx_i, b_idx_j,
                            pos, rot, vel, ang, j_pos_i, j_pos_j, j_axis_i, 
                            j_a_i, j_b_i, # <--- THE FIX: Add arguments
                            j_a_j, j_b_j,
                            alpha, beta):
    
    """ Builds the global Phi_q and gamma_star matrices purely in C. """
    Phi_q = np.zeros((num_equations, num_states_vel))
    gamma_star = np.zeros(num_equations)
    row_idx = 0

    for k in range(len(j_types)):
        j_type = j_types[k]
        idx_i, idx_j = b_idx_i[k], b_idx_j[k]

        # 1. State Extraction (Handle Ground as -1)
        if idx_i >= 0:
            r_i, A_i = pos[idx_i], rot[idx_i]
            v_i, w_i = vel[idx_i], ang[idx_i]
            col_i = idx_i * 6
        else:
            r_i, A_i, v_i, w_i, col_i = np.zeros(3), np.eye(3), np.zeros(3), np.zeros(3), -1
            
        if idx_j >= 0:
            r_j, A_j = pos[idx_j], rot[idx_j]
            v_j, w_j = vel[idx_j], ang[idx_j]
            col_j = idx_j * 6
        else:
            r_j, A_j, v_j, w_j, col_j = np.zeros(3), np.eye(3), np.zeros(3), np.zeros(3), -1

        # 2. Local Vectors & Global Rotations
        sp_i, sp_j = j_pos_i[k], j_pos_j[k]
        
        # Extract pre-stamped orthogonal vectors for Body I and Body J
        v_loc_i, a_loc_i, b_loc_i = j_axis_i[k], j_a_i[k], j_b_i[k]
        a_loc_j, b_loc_j = j_a_j[k], j_b_j[k]
        
        w_glob_i, w_glob_j = A_i @ w_i, A_j @ w_j
        s_i_glob, s_j_glob = A_i @ sp_i, A_j @ sp_j

        # Simply apply the global rotation directly to our pre-stamped vectors:
        v_glob_i = A_i @ v_loc_i
        a_glob_i, b_glob_i = A_i @ a_loc_i, A_i @ b_loc_i
        a_glob_j, b_glob_j = A_j @ a_loc_j, A_j @ b_loc_j

        # 4. Global Derivatives & Accelerations
        d = (r_j + s_j_glob) - (r_i + s_i_glob)
        
        v_dot_i, a_dot_i, b_dot_i = np.cross(w_glob_i, v_glob_i), np.cross(w_glob_i, a_glob_i), np.cross(w_glob_i, b_glob_i)
        a_dot_j, b_dot_j = np.cross(w_glob_j, a_glob_j), np.cross(w_glob_j, b_glob_j)
        d_dot = v_j + np.cross(w_glob_j, s_j_glob) - v_i - np.cross(w_glob_i, s_i_glob)

        v_cent_i, a_cent_i, b_cent_i = np.cross(w_glob_i, v_dot_i), np.cross(w_glob_i, a_dot_i), np.cross(w_glob_i, b_dot_i)
        a_cent_j, b_cent_j = np.cross(w_glob_j, a_dot_j), np.cross(w_glob_j, b_dot_j)
        d_cent = np.cross(w_glob_j, np.cross(w_glob_j, s_j_glob)) - np.cross(w_glob_i, np.cross(w_glob_i, s_i_glob))

        # ==========================================
        # JOINT MAPPING LOGIC (1=FIXED, 2=SPHERICAL, 3=REVOLUTE, 4=CYLINDRICAL, 5=PRISMATIC, 6=PLANAR)
        # ==========================================
        
        # --- Shared Spherical Constraints (Rows 1, 2, 3) ---
        if j_type in (1, 2, 3): 
            assign_spherical_lock(Phi_q, gamma_star, row_idx, col_i, col_j, r_i, r_j, s_i_glob, s_j_glob, v_i, v_j, w_i, w_j, sp_i, sp_j, A_i, A_j, alpha, beta)
            row_idx += 3

        # --- Rotational Locks ---
        if j_type in (1, 3, 4, 5, 6): # Prevent Pitch
            assign_rotational_lock(Phi_q, gamma_star, row_idx, col_i, col_j, v_glob_i, a_glob_j, v_dot_i, a_dot_j, v_cent_i, a_cent_j, A_i, A_j, alpha, beta); row_idx += 1
        if j_type in (1, 3, 4, 5, 6): # Prevent Yaw/Roll
            assign_rotational_lock(Phi_q, gamma_star, row_idx, col_i, col_j, v_glob_i, b_glob_j, v_dot_i, b_dot_j, v_cent_i, b_cent_j, A_i, A_j, alpha, beta); row_idx += 1
        if j_type in (1, 5): # Prevent Twist
            assign_rotational_lock(Phi_q, gamma_star, row_idx, col_i, col_j, a_glob_i, b_glob_j, a_dot_i, b_dot_j, a_cent_i, b_cent_j, A_i, A_j, alpha, beta); row_idx += 1

        # --- Translational Locks ---
        if j_type in (4, 5): # Prevent Slider X/Y Derailment
            assign_translational_lock(Phi_q, gamma_star, row_idx, col_i, col_j, d, d_dot, d_cent, a_glob_i, a_dot_i, a_cent_i, s_i_glob, s_j_glob, A_i, A_j, alpha, beta); row_idx += 1
            assign_translational_lock(Phi_q, gamma_star, row_idx, col_i, col_j, d, d_dot, d_cent, b_glob_i, b_dot_i, b_cent_i, s_i_glob, s_j_glob, A_i, A_j, alpha, beta); row_idx += 1
        if j_type == 6: # Prevent Planar Lift
            assign_translational_lock(Phi_q, gamma_star, row_idx, col_i, col_j, d, d_dot, d_cent, v_glob_i, v_dot_i, v_cent_i, s_i_glob, s_j_glob, A_i, A_j, alpha, beta); row_idx += 1

    return Phi_q, gamma_star

@njit(fastmath=True)
def assemble_gear_jacobian_numba(num_gear_eq, num_states_vel, g_b_idx_1, g_b_idx_2, g_b_idx_c, g_n1_loc, g_n2_loc, rot):
    """ 
    Assembles the 1-row Coupler Constraint Jacobian for perfectly rigid Epicyclic/Bevel gears!
    Math: w_1 * r_1 + w_2 * r_2 - w_carrier * (r_1 + r_2) = 0
    """
    Phi_q = np.zeros((num_gear_eq, num_states_vel))
    gamma_star = np.zeros(num_gear_eq)
    
    for k in range(num_gear_eq):
        idx_1, idx_2, idx_c = g_b_idx_1[k], g_b_idx_2[k], g_b_idx_c[k]
        
        # 1. Carrier tracking maps the gears into dynamically moving global space
        A_c = rot[idx_c] if idx_c >= 0 else np.eye(3)
        n1_glob = A_c @ g_n1_loc[k]
        n2_glob = A_c @ g_n2_loc[k]
        
        col_1 = idx_1 * 6 if idx_1 >= 0 else -1
        col_2 = idx_2 * 6 if idx_2 >= 0 else -1
        col_c = idx_c * 6 if idx_c >= 0 else -1
        
        # 2. Place Willis Kinematics into the Angular Velocity columns!
        if col_1 >= 0:
            Phi_q[k, col_1+3 : col_1+6] = rot[idx_1].T @ n1_glob
        if col_2 >= 0:
            Phi_q[k, col_2+3 : col_2+6] = rot[idx_2].T @ n2_glob
            
        if col_c >= 0:
            # Carrier balances the torque (Action = Reaction)
            Phi_q[k, col_c+3 : col_c+6] = -rot[idx_c].T @ (n1_glob + n2_glob)
            
        # Standard velocity-level rigid coupling (Baumgarte gamma stabilizes inherently)
        gamma_star[k] = 0.0
        
    return Phi_q, gamma_star

# @njit(nopython=True, fastmath=True) # this line was originally here but was changed to the line below to avoid the warning
@njit(fastmath=True)
def solve_kkt_system_numba(M, Phi_q, Q, gamma_star, epsilon):
    """ Solves the Schur Complement. """
    Minv_Q = np.linalg.solve(M, Q)
    Minv_PhiT = np.linalg.solve(M, Phi_q.T)
    C_matrix = Phi_q @ Minv_PhiT
    RHS_lambda = Phi_q @ Minv_Q - gamma_star
    
    if epsilon > 0.0:
        for i in range(C_matrix.shape[0]):
            C_matrix[i, i] += epsilon
            
    lambdas = np.linalg.solve(C_matrix, RHS_lambda)
    return lambdas


@njit(fastmath=True)
def apply_contact_manifold_numba(row_pen, row_tar,
                                 pen_cog, tar_cog,
                                 pen_velocity, tar_velocity,
                                 w_pen_glob, w_tar_glob,
                                 pen_rot_t, tar_rot_t,
                                 points_glob, normals_glob, depths,
                                 stiffness, exponent, damping,
                                 friction_enabled, mu, slip_tolerance,
                                 Q):
    """Applies one contact manifold into Q and returns accumulated scalar contact forces."""
    total_f_spring = 0.0
    total_f_damp = 0.0
    total_f_normal = 0.0
    total_f_friction = 0.0

    for idx in range(depths.shape[0]):
        p_glob = points_glob[idx]
        n_glob = normals_glob[idx]
        depth = depths[idx]

        r_pen = p_glob - pen_cog
        r_tar = p_glob - tar_cog

        v_pen_point = pen_velocity + np.cross(w_pen_glob, r_pen)
        v_tar_point = tar_velocity + np.cross(w_tar_glob, r_tar)

        v_rel = v_pen_point - v_tar_point
        v_rel_normal = np.dot(v_rel, n_glob)
        v_rel_tangent = v_rel - (v_rel_normal * n_glob)
        v_slip = np.linalg.norm(v_rel_tangent)

        f_spring = stiffness * (depth ** exponent)
        f_damp = -damping * v_rel_normal * depth
        f_mag_normal = f_spring + f_damp
        if f_mag_normal < 0.0:
            f_mag_normal = 0.0

        f_frict_glob = np.zeros(3)
        f_mag_friction = 0.0

        if friction_enabled and v_slip > 1e-6 and mu > 0.0:
            mu_eff = mu * np.tanh(v_slip / slip_tolerance)
            f_mag_friction = mu_eff * f_mag_normal
            frict_dir = -v_rel_tangent / v_slip
            f_frict_glob = frict_dir * f_mag_friction

        f_pen_glob = (n_glob * f_mag_normal) + f_frict_glob
        f_tar_glob = -f_pen_glob

        total_f_spring += f_spring
        total_f_damp += f_damp
        total_f_normal += f_mag_normal
        total_f_friction += f_mag_friction

        if row_pen >= 0:
            for axis in range(3):
                Q[row_pen + axis] += f_pen_glob[axis]
            t_pen = np.cross(r_pen, f_pen_glob)
            t_pen_loc = pen_rot_t @ t_pen
            for axis in range(3):
                Q[row_pen + 3 + axis] += t_pen_loc[axis]

        if row_tar >= 0:
            for axis in range(3):
                Q[row_tar + axis] += f_tar_glob[axis]
            t_tar = np.cross(r_tar, f_tar_glob)
            t_tar_loc = tar_rot_t @ t_tar
            for axis in range(3):
                Q[row_tar + 3 + axis] += t_tar_loc[axis]

    return total_f_spring, total_f_damp, total_f_normal, total_f_friction


def warm_up_numba_kernels():
    """Precompiles the Numba kernels used by the constrained solver."""
    global _NUMBA_WARMED_UP

    if _NUMBA_WARMED_UP:
        return

    joint_types = np.array([1, 4], dtype=np.int32)
    body_idx_i = np.array([-1, 0], dtype=np.int32)
    body_idx_j = np.array([0, -1], dtype=np.int32)

    pos = np.zeros((1, 3), dtype=np.float64)
    rot = np.zeros((1, 3, 3), dtype=np.float64)
    rot[0] = np.eye(3, dtype=np.float64)
    vel = np.zeros((1, 3), dtype=np.float64)
    ang = np.zeros((1, 3), dtype=np.float64)

    j_pos_i = np.zeros((2, 3), dtype=np.float64)
    j_pos_j = np.zeros((2, 3), dtype=np.float64)
    j_axis_i = np.array([
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0],
    ], dtype=np.float64)
    j_a_i = np.array([
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
    ], dtype=np.float64)
    j_b_i = np.array([
        [0.0, 1.0, 0.0],
        [0.0, 1.0, 0.0],
    ], dtype=np.float64)
    j_a_j = np.array([
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
    ], dtype=np.float64)
    j_b_j = np.array([
        [0.0, 1.0, 0.0],
        [0.0, 1.0, 0.0],
    ], dtype=np.float64)

    assemble_jacobian_numba(
        10,
        6,
        joint_types,
        body_idx_i,
        body_idx_j,
        pos,
        rot,
        vel,
        ang,
        j_pos_i,
        j_pos_j,
        j_axis_i,
        j_a_i,
        j_b_i,
        j_a_j,
        j_b_j,
        20.0,
        20.0,
    )

    g_b_idx_1 = np.array([0], dtype=np.int32)
    g_b_idx_2 = np.array([-1], dtype=np.int32)
    g_b_idx_c = np.array([-1], dtype=np.int32)
    g_n1_loc = np.array([[0.0, 0.0, 1.0]], dtype=np.float64)
    g_n2_loc = np.array([[0.0, 1.0, 0.0]], dtype=np.float64)

    assemble_gear_jacobian_numba(
        1,
        6,
        g_b_idx_1,
        g_b_idx_2,
        g_b_idx_c,
        g_n1_loc,
        g_n2_loc,
        rot,
    )

    M = np.eye(2, dtype=np.float64)
    Phi_q = np.array([[1.0, 0.0]], dtype=np.float64)
    Q = np.zeros(2, dtype=np.float64)
    gamma_star = np.zeros(1, dtype=np.float64)
    solve_kkt_system_numba(M, Phi_q, Q, gamma_star, 1e-7)

    contact_Q = np.zeros(12, dtype=np.float64)
    apply_contact_manifold_numba(
        0,
        6,
        np.zeros(3, dtype=np.float64),
        np.array([0.0, 0.0, -0.01], dtype=np.float64),
        np.zeros(3, dtype=np.float64),
        np.zeros(3, dtype=np.float64),
        np.zeros(3, dtype=np.float64),
        np.zeros(3, dtype=np.float64),
        np.eye(3, dtype=np.float64),
        np.eye(3, dtype=np.float64),
        np.array([[0.0, 0.0, 0.0]], dtype=np.float64),
        np.array([[0.0, 0.0, 1.0]], dtype=np.float64),
        np.array([0.001], dtype=np.float64),
        1e5,
        1.5,
        10.0,
        True,
        0.3,
        0.01,
        contact_Q,
    )

    _NUMBA_WARMED_UP = True