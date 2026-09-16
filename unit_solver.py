# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.09.0
#  Module: unit_solver.py
#  Description:
#      The core Multibody Dynamics (MBD) engine that formulates the Augmented DAE matrices, 
#      integrates the physics step, and extracts exact reaction forces.
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
import scipy.linalg
import os
import csv
import logging
import warnings

from integrators import CustomRK4, SciPyIntegrator
from scipy.spatial.transform import Rotation
from unit_forces import ForceType
from unit_joints import JointType, GearType

# By default, SciPy formats quaternions as [x, y, z, w] (scalar last).
# We will strictly follow this convention to avoid mathematical bugs.

from math_kernels import solve_kkt_system_numba, assemble_jacobian_numba, assemble_gear_jacobian_numba

class MBSolver:
    """ The Core Multibody Dynamics Solver (Hybrid Formulation) """
    
    # --- Added springs_list AND gear_pairs to the arguments here! ---
    def __init__(self, physics_bodies, forces_list, joints_list=None, springs_list=None, contact_pairs=None, gear_pairs=None, motions_list=None, epsilon=1e-7, alpha=20.0, beta=20.0):
        self.forces_list = forces_list 
        self.joints_list = joints_list if joints_list is not None else [] 
        self.springs_list = springs_list if springs_list is not None else []
        self.contact_pairs = contact_pairs if contact_pairs is not None else []
        # --- Safely store the gear pairs ---
        self.gear_pairs = gear_pairs if gear_pairs is not None else []
        # --- Safely store the contact pairs ---
        self.contact_pairs = contact_pairs if contact_pairs is not None else []
        # --- Safely store the kinematic motions ---
        self.motions_list = motions_list if motions_list is not None else []
        # --- Solver Tuning Parameters ---
        self.epsilon = epsilon
        self.alpha = alpha
        self.beta = beta
        
        # 1. Filter out the ground AND disabled bodies. 
        self.moving_bodies = [b for b in physics_bodies.values() if not b.is_ground and b.enabled]
        self.num_bodies = len(self.moving_bodies)
        
        # 2. Map bodies to their indices for fast matrix assembly
        self.body_index_map = {body.name: idx for idx, body in enumerate(self.moving_bodies)}
        
        # 3. Determine State Vector Size
        self.N_pos = self.num_bodies * 7 # [X, Y, Z, qx, qy, qz, qw]
        self.N_vel = self.num_bodies * 6 # [Vx, Vy, Vz, Wx_local, Wy_local, Wz_local]
        self.N_total = self.N_pos + self.N_vel

        # 4. PRE-COMPUTE THE CONSTANT MASS MATRIX
        self.M_constant = self.build_constant_mass_matrix()
        
        # 5. Pre-factorize the Mass Matrix for extreme solving speed
        # (lu, piv) stores the factorized data so we never have to invert M during the loop!
        self.lu_M = scipy.linalg.lu_factor(self.M_constant)
        
        # 6. Pre-Count Constraints to size the Jacobian Matrix & Reaction Forces
        self.num_equations = 0
        for joint in self.joints_list:
            if not joint.enabled: continue
            
            if joint.joint_type == JointType.SPHERICAL: 
                self.num_equations += 3
            elif joint.joint_type == JointType.REVOLUTE: 
                self.num_equations += 5
            elif joint.joint_type == JointType.PRISMATIC: 
                self.num_equations += 5
            elif joint.joint_type == JointType.CYLINDRICAL: 
                self.num_equations += 4
            elif joint.joint_type == JointType.PLANAR: 
                self.num_equations += 3
            elif joint.joint_type == JointType.FIXED: 
                self.num_equations += 6
                                    
        self.current_lambdas = np.zeros(self.num_equations)
        # --- Immediate Abort Flag ---
        self.cancel_flag = False
        
    # ==========================================
    # --- PHASE 1: THE STATE MANAGER ---
    # ==========================================
    
    def pack_state(self):
        """ Gathers 3D object states into a single 1D solver array Y. """
        Y = np.zeros(self.N_total)
        pos_idx = 0
        vel_idx = self.N_pos
        
        for body in self.moving_bodies:
            # Translations (Global)
            Y[pos_idx : pos_idx+3] = body.cog
            
            # Rotations (Quaternions via SciPy [x, y, z, w])
            r = Rotation.from_matrix(body.principal_axes)
            Y[pos_idx+3 : pos_idx+7] = r.as_quat() 
            
            # Velocities (Global Linear, LOCAL Angular)
            Y[vel_idx : vel_idx+3] = body.velocity
            Y[vel_idx+3 : vel_idx+6] = body.angular_velocity # Treated as Local in Hybrid!
            
            pos_idx += 7
            vel_idx += 6
            
        return Y

    def unpack_state(self, Y):
        """ Pushes 1D array back into 3D objects, updating matrices instantly. """
        pos_idx = 0
        vel_idx = self.N_pos
        
        for body in self.moving_bodies:
            body.cog = Y[pos_idx : pos_idx+3]
            quat = Y[pos_idx+3 : pos_idx+7]
            
            # --- THE FIX: Protection against Numerical Explosions (NaNs or Zeros) ---
            if np.any(np.isnan(quat)) or np.any(np.isinf(quat)):
                print(f"CRITICAL WARNING: Numerical explosion detected on '{body.name}'.")
                quat = np.array([0.0, 0.0, 0.0, 1.0]) # Reset to identity
            
            # Normalize quaternion to prevent ballooning/distortion
            q_norm = np.linalg.norm(quat)
            if q_norm > 1e-12:
                quat = quat / q_norm
            else:
                quat = np.array([0.0, 0.0, 0.0, 1.0]) 
            
            r = Rotation.from_quat(quat)
            body.principal_axes = r.as_matrix()
            
            # Euler angles are UI/export helpers; quaternion + matrix remain authoritative.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                euler_xyz = r.as_euler('xyz', degrees=True)
            body.pos_angles = np.array([euler_xyz[2], euler_xyz[1], euler_xyz[0]])
            
            body.velocity = Y[vel_idx : vel_idx+3]
            body.angular_velocity = Y[vel_idx+3 : vel_idx+6]
            
            pos_idx += 7
            vel_idx += 6

    


    def prepare_static_numba_data(self):
        """ Gathers all static joint data ONCE before the solver loops start. """
        # --- Only include joints if BOTH bodies are currently enabled ---
        active_joints = [
            j for j in self.joints_list 
            if j.enabled and j.body_i.enabled and j.body_j.enabled
        ]
        N_j = len(active_joints)
        
        self.num_equations = 0
        self.j_types = np.zeros(N_j, dtype=np.int32)
        self.b_idx_i = np.zeros(N_j, dtype=np.int32)
        self.b_idx_j = np.zeros(N_j, dtype=np.int32)
        
        self.j_pos_i, self.j_pos_j = np.zeros((N_j, 3)), np.zeros((N_j, 3))
        self.j_axis_i = np.zeros((N_j, 3))
        self.j_a_j, self.j_b_j = np.zeros((N_j, 3)), np.zeros((N_j, 3))
        
        # --- THE FIX: Add arrays for Body I ---
        self.j_a_i, self.j_b_i = np.zeros((N_j, 3)), np.zeros((N_j, 3))
        
        for k, joint in enumerate(active_joints):
            self.j_types[k] = joint.joint_type.value # 1=Fixed, 2=Spherical, etc.
            self.b_idx_i[k] = -1 if joint.body_i.is_ground else self.body_index_map[joint.body_i.name]
            self.b_idx_j[k] = -1 if joint.body_j.is_ground else self.body_index_map[joint.body_j.name]
            
            self.j_pos_i[k], self.j_pos_j[k] = joint.local_pos_i, joint.local_pos_j
            self.j_axis_i[k] = joint.local_axis_i
            self.j_a_j[k], self.j_b_j[k] = joint.local_a_j, joint.local_b_j
            
            # --- THE FIX: Populate Body I arrays ---
            self.j_a_i[k], self.j_b_i[k] = joint.local_a_i, joint.local_b_i
            
            if joint.joint_type == JointType.SPHERICAL: self.num_equations += 3
            elif joint.joint_type == JointType.REVOLUTE: self.num_equations += 5
            elif joint.joint_type == JointType.PRISMATIC: self.num_equations += 5
            elif joint.joint_type == JointType.CYLINDRICAL: self.num_equations += 4
            elif joint.joint_type == JointType.PLANAR: self.num_equations += 3
            elif joint.joint_type == JointType.FIXED: self.num_equations += 6

        # --- PREPARE GEAR COUPLERS ---
        active_gears = [g for g in self.gear_pairs if g.enabled and g.body_1.enabled and g.body_2.enabled]
        self.num_gear_eq = len(active_gears)
        
        self.g_b_idx_1 = np.zeros(self.num_gear_eq, dtype=np.int32)
        self.g_b_idx_2 = np.zeros(self.num_gear_eq, dtype=np.int32)
        self.g_b_idx_c = np.zeros(self.num_gear_eq, dtype=np.int32)
        self.g_n1_loc = np.zeros((self.num_gear_eq, 3))
        self.g_n2_loc = np.zeros((self.num_gear_eq, 3))
        
        for k, gear in enumerate(active_gears):
            gear.bind_kinematics() # Calculate Epicyclic Geometry at t=0
            
            self.g_b_idx_1[k] = -1 if gear.body_1.is_ground else self.body_index_map[gear.body_1.name]
            self.g_b_idx_2[k] = -1 if gear.body_2.is_ground else self.body_index_map[gear.body_2.name]
            self.g_b_idx_c[k] = -1 if gear.carrier.is_ground else self.body_index_map[gear.carrier.name]
            
            self.g_n1_loc[k] = gear.n1_loc
            self.g_n2_loc[k] = gear.n2_loc

    def pack_dynamic_states(self):
        """ Quickly dumps current states to flat arrays for Numba. """
        N_b = self.num_bodies
        pos, vel, ang = np.zeros((N_b, 3)), np.zeros((N_b, 3)), np.zeros((N_b, 3))
        rot = np.zeros((N_b, 3, 3))
        
        for i, body in enumerate(self.moving_bodies):
            pos[i], vel[i], ang[i] = body.cog, body.velocity, body.angular_velocity
            rot[i] = body.principal_axes
            
        return pos, rot, vel, ang

    # ==========================================
    # --- PHASE 2: HYBRID EVALUATOR ---
    # ==========================================
    
    def initialize_springs(self):
        """ Calculates the t=0 resting lengths and angles for all compliant elements. """
        for spring in self.springs_list:
            if not spring.enabled: continue

            # Get Global attachment points
            r_i_glob = spring.body_i.principal_axes @ spring.local_pos_i
            r_j_glob = spring.body_j.principal_axes @ spring.local_pos_j
            p_i = spring.body_i.cog + r_i_glob
            p_j = spring.body_j.cog + r_j_glob

            if hasattr(spring, 'initial_length'): # Compression Spring
                spring.initial_length = np.linalg.norm(p_j - p_i)

            elif hasattr(spring, 'initial_angle'): # Torsion Spring
                axis_glob = spring.body_i.principal_axes @ spring.local_axis_i
                ref_i_glob = spring.body_i.principal_axes @ spring.local_ref_i
                ref_j_glob = spring.body_j.principal_axes @ spring.local_ref_j

                # Project J's reference axis onto the plane perpendicular to the primary twist axis
                y_axis = np.cross(axis_glob, ref_i_glob)
                proj_j = ref_j_glob - np.dot(ref_j_glob, axis_glob) * axis_glob
                if np.linalg.norm(proj_j) > 1e-8: 
                    proj_j /= np.linalg.norm(proj_j)

                # Calculate resting angle using atan2
                cos_th = np.dot(ref_i_glob, proj_j)
                sin_th = np.dot(y_axis, proj_j)
                spring.initial_angle = np.arctan2(sin_th, cos_th)
             
            # --- Capture Bushing Baseline ---
            elif hasattr(spring, 'k_trans'): # Bushing
                # Calculate current global attachment points
                p_i = spring.body_i.cog + spring.body_i.principal_axes @ spring.local_pos_i
                p_j = spring.body_j.cog + spring.body_j.principal_axes @ spring.local_pos_j
                
                # Store J's position relative to I, strictly in I's local coordinate system!
                spring.initial_local_pos_j = spring.body_i.principal_axes.T @ (p_j - p_i)
                
                # Store the rotation matrix of J relative to I
                spring.initial_rel_rot = spring.body_i.principal_axes.T @ spring.body_j.principal_axes 
    
    def initialize_motions(self):
        """ Calculates the t=0 resting lengths and angles for kinematic drivers. """
        for motion in self.motions_list:
            if not motion.enabled: continue
            
            joint = motion.joint
            A_i, A_j = joint.body_i.principal_axes, joint.body_j.principal_axes
            
            if motion.trans_rot.value == 1: # Rotational
                v_glob_i = A_i @ joint.local_axis_i
                ref_i_glob = A_i @ joint.local_a_i
                ref_j_glob = A_j @ joint.local_a_j
                
                y_axis = np.cross(v_glob_i, ref_i_glob)
                proj_j = ref_j_glob - np.dot(ref_j_glob, v_glob_i) * v_glob_i
                if np.linalg.norm(proj_j) > 1e-8: proj_j /= np.linalg.norm(proj_j)
                
                cos_th = np.dot(ref_i_glob, proj_j)
                sin_th = np.dot(y_axis, proj_j)
                motion.initial_angle = np.arctan2(sin_th, cos_th)
                
            else: # Translational
                s_i_glob = A_i @ joint.local_pos_i
                s_j_glob = A_j @ joint.local_pos_j
                d = (joint.body_j.cog + s_j_glob) - (joint.body_i.cog + s_i_glob)
                v_glob_i = A_i @ joint.local_axis_i
                
                motion.initial_dist = np.dot(d, v_glob_i)
                    
    def build_constant_mass_matrix(self):
        """ Assembles the constant 6N x 6N Mass Matrix (Evaluated ONCE). """
        M = np.zeros((self.N_vel, self.N_vel))
        
        for idx, body in enumerate(self.moving_bodies):
            row_start = idx * 6
            
            # 1. Translational Mass (Global)
            M[row_start:row_start+3, row_start:row_start+3] = np.eye(3) * body.mass
            
            # 2. Rotational Inertia (Local - STRICTLY CONSTANT)
            I_local = np.diag(body.principal_inertia)
            M[row_start+3:row_start+6, row_start+3:row_start+6] = I_local
            
        return M

    def build_force_vector(self, t):
        """ Assembles the 6N x 1 Force Vector (Global F, Local T) incl.Actuators """
        Q = np.zeros(self.N_vel)
        
        # 1. Apply Local Gyroscopic Forces
        for idx, body in enumerate(self.moving_bodies):
            w_loc = body.angular_velocity
            I_loc = np.diag(body.principal_inertia)
            
            # Local Gyroscopic Torque = -(w_loc x (I_loc * w_loc))
            gyro_torque = -np.cross(w_loc, I_loc @ w_loc)
            
            row_start = idx * 6
            Q[row_start+3 : row_start+6] = gyro_torque
            
        # 2. Apply Active Forces (Gravity, Thrusters, Motors, Actuators)
        for force in self.forces_list:
            # Skip if force, body, or gravity is disabled!
            if not force.enabled or force.parent_body.is_ground or not force.parent_body.enabled:
                continue
                
            body = force.parent_body    
            body_idx = self.body_index_map.get(body.name)
            if body_idx is None: continue
            row_start = body_idx * 6
            
            if force.is_gravity:
                # F = m * g
                actual_force = force.base_vector * body.mass
                Q[row_start : row_start+3] += actual_force
                
            elif force.force_type == ForceType.FORCE:
                F_global = force.get_global_vector(t)
                Q[row_start : row_start+3] += F_global
                
                r_loc = force.get_local_position() 
                F_loc = force.get_local_vector(t)   
                Q[row_start+3 : row_start+6] += np.cross(r_loc, F_loc)
                
            elif force.force_type == ForceType.TORQUE:
                T_loc = force.get_local_vector(t)
                Q[row_start+3 : row_start+6] += T_loc

            elif force.force_type == ForceType.E_MOTOR:
                # --- E-MOTOR: Rotational Speed Limit ---
                T_loc_max = force.get_local_vector(t)
                T_max = np.linalg.norm(T_loc_max)
                
                # Failsafe: Only apply curve if max speed is defined
                if T_max > 1e-6 and force.speed_max > 0.0:
                    axis_local = T_loc_max / T_max
                    
                    # 1. Project current angular velocity onto the motor axis
                    omega_current = np.dot(body.angular_velocity, axis_local)
                    
                    # 2. Calculate torque scaling: T = T_max * (1 - w / w_max)
                    scale = 1.0 - (omega_current / force.speed_max)
                    # --- Prevent regenerative braking if disabled ---
                    if not force.allow_braking:
                        scale = max(0.0, scale)
                    T_dynamic = T_loc_max * scale
                    
                    Q[row_start+3 : row_start+6] += T_dynamic
                else:
                    # Fallback to standard constant torque if speed_max is 0
                    Q[row_start+3 : row_start+6] += T_loc_max

            elif force.force_type == ForceType.ACTUATOR:
                # --- ACTUATOR: Linear Speed Limit ---
                F_global_max = force.get_global_vector(t)
                F_max = np.linalg.norm(F_global_max)
                
                if F_max > 1e-6 and force.speed_max > 0.0:
                    axis_global = F_global_max / F_max
                    
                    # 1. Calculate the global velocity of the exact point where the force is applied
                    r_glob = body.principal_axes @ force.get_local_position()
                    w_glob = body.principal_axes @ body.angular_velocity
                    
                    # (Assumes body.velocity stores the global linear velocity [vx, vy, vz])
                    v_point_glob = body.velocity + np.cross(w_glob, r_glob) 
                    
                    # 2. Project current velocity onto the actuator axis
                    v_current = np.dot(v_point_glob, axis_global)
                    
                    # 3. Calculate force scaling: F = F_max * (1 - v / v_max)
                    scale = 1.0 - (v_current / force.speed_max)
                    # --- Prevent active braking if disabled ---
                    if not force.allow_braking:
                        scale = max(0.0, scale)
                    F_dynamic_global = F_global_max * scale
                    
                    # Apply Translational Force
                    Q[row_start : row_start+3] += F_dynamic_global
                    
                    # Apply corresponding Local Torque for off-center actuators
                    F_dynamic_local = body.principal_axes.T @ F_dynamic_global
                    Q[row_start+3 : row_start+6] += np.cross(force.get_local_position(), F_dynamic_local)
                else:
                    # Fallback to standard constant force
                    Q[row_start : row_start+3] += F_global_max
                    Q[row_start+3 : row_start+6] += np.cross(force.get_local_position(), force.get_local_vector(t))
        
        # 3. Inject Bearing Forces (Radial & Axial Separations) from Gears!
        for gear in self.gear_pairs:
            if not gear.enabled or not gear.body_1.enabled or not gear.body_2.enabled: continue
                
            F_t = gear.last_lambda # Borrow previous time-step's Tangential Force
            if abs(F_t) < 1e-8: continue
            
            # Mathematical Derivation of Shaft Forces
            if gear.gear_type == GearType.BEVEL:
                # For Bevel Gears, the pressure angle thrust acts on a cone!
                # It decomposes into Radial and Axial loads based on the Pitch Angle (gamma).
                F_r = abs(F_t) * np.tan(gear.alpha) * np.cos(gear.gamma)
                F_a = abs(F_t) * np.tan(gear.alpha) * np.sin(gear.gamma)
            else:
                # For Spur/Helical/Internal Gears
                F_r = abs(F_t) * np.tan(gear.alpha) / np.cos(gear.beta)
                F_a = abs(F_t) * np.tan(gear.beta) * np.sign(F_t)
            
            A_c = gear.carrier.principal_axes if not gear.carrier.is_ground else np.eye(3)
            c_cog = gear.carrier.cog if not gear.carrier.is_ground else np.zeros(3)
            
            # Map tracking vectors back to global
            ur_glob = A_c @ gear.ur_loc
            za_glob = A_c @ gear.za_loc
            
            # --- Calculate the Orthogonal Tangential Vector ---
            ut_glob = np.cross(za_glob, ur_glob)
            
            # Apply Radial/Axial to Body 1, Reaction applies to Body 2
            F_active_1 = (-F_r * ur_glob) + (F_a * za_glob)
            F_active_2 = -F_active_1
            
            # --- Calculate Linear Tangential Push ---
            # --- Add the Minus Sign! (Matches Lagrangian Q - Phi^T*Lambda) ---
            F_t_linear_1 = -F_t * ut_glob
            F_t_linear_2 = -F_t_linear_1
            
            p_pitch_glob = c_cog + A_c @ gear.p_pitch_loc
            
            idx_1 = self.body_index_map.get(gear.body_1.name)
            idx_2 = self.body_index_map.get(gear.body_2.name)
            
            # --- Retrieve the Carrier index ---
            idx_c = self.body_index_map.get(gear.carrier.name) 
            
            # Add separation forces to the shafts. 
            if idx_1 is not None:
                r1 = p_pitch_glob - gear.body_1.cog
                # Add ALL linear forces (including Ft) to translation [0:3]
                Q[idx_1*6 : idx_1*6+3] += F_active_1 + F_t_linear_1
                # Add ONLY Fr and Fa to rotation [3:6]. (Ft torque is handled flawlessly by Phi_q Matrix!)
                Q[idx_1*6+3 : idx_1*6+6] += gear.body_1.principal_axes.T @ np.cross(r1, F_active_1)
            
            if idx_2 is not None:
                r2 = p_pitch_glob - gear.body_2.cog
                Q[idx_2*6 : idx_2*6+3] += F_active_2 + F_t_linear_2
                Q[idx_2*6+3 : idx_2*6+6] += gear.body_2.principal_axes.T @ np.cross(r2, F_active_2)
                
            # --- Cancel the fake double-torque on the Carrier! ---
            # F_t_linear_1 and 2 physically pull on the joints, which naturally creates a torque on the Carrier.
            # However, our matrix Phi_q ALSO applies this exact torque mathematically! 
            # We must subtract the manual linear couple from the Carrier to prevent double-torquing!
            if idx_c is not None:
                r_c1 = gear.body_1.cog - gear.carrier.cog
                r_c2 = gear.body_2.cog - gear.carrier.cog
                
                # Calculate the extraneous global moment generated by our manual linear forces
                M_extra_glob = np.cross(r_c1, F_t_linear_1) + np.cross(r_c2, F_t_linear_2)
                
                # Subtract it from the Carrier's local rotational torque
                Q[idx_c*6+3 : idx_c*6+6] -= gear.carrier.principal_axes.T @ M_extra_glob
        
        # 3. Apply Compliant Spring-Damper Forces
        # It calculates the dynamic Delta_L, projects the velocities using dot products
        # and mathematically pushes the two bodies apart or twists them together
        
        for spring in self.springs_list:
            if not spring.enabled or (spring.body_i.is_ground and spring.body_j.is_ground):
                continue

            # Safe index retrieval (Ground bodies have no row in Q)
            idx_i = self.body_index_map.get(spring.body_i.name)
            idx_j = self.body_index_map.get(spring.body_j.name)
            row_i = idx_i * 6 if idx_i is not None else None
            row_j = idx_j * 6 if idx_j is not None else None

            A_i, A_j = spring.body_i.principal_axes, spring.body_j.principal_axes
            w_i_glob = A_i @ spring.body_i.angular_velocity
            w_j_glob = A_j @ spring.body_j.angular_velocity
            
            r_i_glob = A_i @ spring.local_pos_i
            r_j_glob = A_j @ spring.local_pos_j
            p_i = spring.body_i.cog + r_i_glob
            p_j = spring.body_j.cog + r_j_glob

            if hasattr(spring, 'initial_length'): 
                # --- COMPRESSION SPRING MATH ---
                vec_ij = p_j - p_i
                L = np.linalg.norm(vec_ij)
                if L < 1e-8: continue
                u_ij = vec_ij / L

                # Calculate velocities at the exact attachment points
                v_i_glob = spring.body_i.velocity + np.cross(w_i_glob, r_i_glob)
                v_j_glob = spring.body_j.velocity + np.cross(w_j_glob, r_j_glob)

                # Project relative velocity onto the spring axis
                L_dot = np.dot(v_j_glob - v_i_glob, u_ij)
                delta_L = L - spring.initial_length

                # F_mag = K*x + C*v - Preload
                F_mag = (spring.stiffness * delta_L) + (spring.damping * L_dot) - spring.preload

                F_i_glob = F_mag * u_ij  # Force on I pulls towards J if stretched
                F_j_glob = -F_i_glob

                if row_i is not None:
                    Q[row_i : row_i+3] += F_i_glob
                    Q[row_i+3 : row_i+6] += A_i.T @ np.cross(r_i_glob, F_i_glob)
                if row_j is not None:
                    Q[row_j : row_j+3] += F_j_glob
                    Q[row_j+3 : row_j+6] += A_j.T @ np.cross(r_j_glob, F_j_glob)

            elif hasattr(spring, 'initial_angle'): 
                # --- TORSION SPRING MATH ---
                axis_glob = A_i @ spring.local_axis_i
                ref_i_glob = A_i @ spring.local_ref_i
                ref_j_glob = A_j @ spring.local_ref_j

                # Project relative angular velocity onto the twist axis
                theta_dot = np.dot(w_j_glob - w_i_glob, axis_glob)

                # Calculate current twist angle purely geometrically (Stateless & Safe!)
                y_axis = np.cross(axis_glob, ref_i_glob)
                proj_j = ref_j_glob - np.dot(ref_j_glob, axis_glob) * axis_glob
                if np.linalg.norm(proj_j) > 1e-8: proj_j /= np.linalg.norm(proj_j)

                cos_th = np.dot(ref_i_glob, proj_j)
                sin_th = np.dot(y_axis, proj_j)
                current_angle = np.arctan2(sin_th, cos_th)

                # Shortest path angular difference (Valid for twists within +/- 180 degrees)
                delta_theta = current_angle - spring.initial_angle
                if delta_theta > np.pi: delta_theta -= 2 * np.pi
                elif delta_theta < -np.pi: delta_theta += 2 * np.pi

                # Tau_mag = K*theta + C*w - Preload
                tau_mag = (spring.stiffness * delta_theta) + (spring.damping * theta_dot) - spring.preload

                T_i_glob = tau_mag * axis_glob
                T_j_glob = -T_i_glob

                if row_i is not None:
                    Q[row_i+3 : row_i+6] += A_i.T @ T_i_glob
                if row_j is not None:
                    Q[row_j+3 : row_j+6] += A_j.T @ T_j_glob
                    
            # --- Core Bushing Physics ---
            elif hasattr(spring, 'k_trans'): 
                A_i, A_j = spring.body_i.principal_axes, spring.body_j.principal_axes
                
                # --- THE UPGRADE: Calculate the Global Rotation of RF_I ---
                R_rf_i = A_i @ spring.local_rot_i
                
                r_i_glob = A_i @ spring.local_pos_i
                r_j_glob = A_j @ spring.local_pos_j
                p_i = spring.body_i.cog + r_i_glob
                p_j = spring.body_j.cog + r_j_glob
                
                w_i_glob = A_i @ spring.body_i.angular_velocity
                w_j_glob = A_j @ spring.body_j.angular_velocity
                v_i_glob = spring.body_i.velocity + np.cross(w_i_glob, r_i_glob)
                v_j_glob = spring.body_j.velocity + np.cross(w_j_glob, r_j_glob)
                
                # 1. Translational Kinematics (Projected perfectly into RF_I's rotated frame!)
                current_local_pos_j = R_rf_i.T @ (p_j - p_i)
                delta_x = current_local_pos_j - spring.initial_local_pos_j
                v_rel_loc = R_rf_i.T @ (v_j_glob - v_i_glob)
                
                # 2. Rotational Kinematics (Extracting the delta Euler angles in RF_I's frame)
                R_rel = R_rf_i.T @ A_j
                R_delta = R_rel @ spring.initial_rel_rot.T
                
                # Safely extract the rotation vector (axis * angle) from the matrix
                angle = np.arccos(np.clip((np.trace(R_delta) - 1.0) / 2.0, -1.0, 1.0))
                if angle > 1e-8:
                    axis = np.array([R_delta[2,1]-R_delta[1,2], R_delta[0,2]-R_delta[2,0], R_delta[1,0]-R_delta[0,1]])
                    norm_axis = np.linalg.norm(axis)
                    delta_theta = (axis / norm_axis) * angle if norm_axis > 1e-8 else np.zeros(3)
                else:
                    delta_theta = np.zeros(3)
                    
                w_rel_loc = A_i.T @ (w_j_glob - w_i_glob)
                
                # 3. Calculate 6-DOF Local Forces & Torques (Generated strictly at RF_I)
                F_calc_loc = -(spring.k_trans * delta_x) - (spring.c_trans * v_rel_loc) + spring.p_trans
                T_calc_loc = -(spring.k_rot * delta_theta) - (spring.c_rot * w_rel_loc) + spring.p_rot
                
                F_calc_glob = R_rf_i @ F_calc_loc
                T_calc_glob = R_rf_i @ T_calc_loc
                
                # 4. Action-Reaction (Applying the stiffness strictly at p_i)
                # Body I feels the raw reaction forces exactly at p_i
                F_i_glob = -F_calc_glob
                T_i_glob = -T_calc_glob
                
                # Body J feels the forces shifted from p_i to p_j via the Parallel Axis Theorem!
                F_j_glob = F_calc_glob
                T_j_glob = T_calc_glob - np.cross(p_j - p_i, F_calc_glob)
                
                if row_i is not None:
                    Q[row_i : row_i+3] += F_i_glob
                    Q[row_i+3 : row_i+6] += A_i.T @ (np.cross(r_i_glob, F_i_glob) + T_i_glob)
                if row_j is not None:
                    Q[row_j : row_j+3] += F_j_glob
                    Q[row_j+3 : row_j+6] += A_j.T @ (np.cross(r_j_glob, F_j_glob) + T_j_glob)
                    
        return Q

    def get_quaternion_derivative_local(self, w_loc, q):
        """ 
        Shabana's Local Formulation: dq/dt = 1/2 * G_bar^T * w_local 
        Expects SciPy Quaternions: [qx, qy, qz, qw].
        """
        qx, qy, qz, qw = q
        wx, wy, wz = w_loc
        
        # Extracted directly from quaternion multiplication rules
        dqx =  0.5 * ( qw*wx + qy*wz - qz*wy )
        dqy =  0.5 * ( qw*wy + qz*wx - qx*wz )
        dqz =  0.5 * ( qw*wz + qx*wy - qy*wx )
        dqw = -0.5 * ( qx*wx + qy*wy + qz*wz )
        
        return np.array([dqx, dqy, dqz, dqw])

    def evaluate_derivatives(self, t, Y):
        """ Calculates dY/dt = [ Position_Derivatives, Accelerations ] """
        
        # --- Instantly break the integration loop if the user clicked Abort! ---
        if getattr(self, 'cancel_flag', False):
            raise InterruptedError("Simulation manually aborted by the user.")
        
        self.unpack_state(Y)
        
        # --- Zero out contact trackers for this sub-step ---
        for cp in self.contact_pairs:
            cp.current_F_spring = 0.0
            cp.current_F_damp = 0.0
            cp.current_F_total = 0.0
            cp.current_F_friction = 0.0
            
        # --- Phase 1 & 2 Collision Detection ---
        if not hasattr(self, 'last_collision_print_time'):
            self.last_collision_print_time = -1.0 
            
        print_telemetry = (t - self.last_collision_print_time) >= 0.05
        
        overlapping_pairs = self.check_broadphase_collisions(t)
        
        # --- Iterate through ContactPair objects, not tuples! ---
        for cp in overlapping_pairs:
            contact_manifold = self.evaluate_narrow_phase(cp.body_i, cp.body_j, getattr(cp, 'mesh_mode', 0))
            
            if len(contact_manifold) > 0 and print_telemetry:
                max_depth = max([c['depth'] for c in contact_manifold]) * 1000.0 # Convert to mm
                print(f"[{t:.3f}s] NARROW PHASE: {len(contact_manifold)} points between {cp.body_i.name} & {cp.body_j.name} (Max Depth: {max_depth:.2f} mm)")
                self.last_collision_print_time = t
        
        
        Q = self.build_force_vector(t)

        # ==========================================
        # --- PHASE 3 - COMPLIANT CONTACT FORCES ---
        # ==========================================
        active_contacts = self.check_broadphase_collisions(t)
        
        for cp in active_contacts:
            # We pass the two bodies defined in the pair to the Narrow Phase
            contact_manifold = self.evaluate_narrow_phase(cp.body_i, cp.body_j, getattr(cp, 'mesh_mode', 0))
            
            for contact in contact_manifold:
                pen = contact['body_pen']
                tar = contact['body_tar']
                p_glob = contact['point']
                n_glob = contact['normal'] 
                depth = contact['depth']
                
                idx_pen = self.body_index_map.get(pen.name)
                idx_tar = self.body_index_map.get(tar.name)
                row_pen = idx_pen * 6 if idx_pen is not None else None
                row_tar = idx_tar * 6 if idx_tar is not None else None
                
                # 1. Kinematics (Relative Velocity)
                r_pen = p_glob - pen.cog
                r_tar = p_glob - tar.cog
                
                w_pen_glob = pen.principal_axes @ pen.angular_velocity
                w_tar_glob = tar.principal_axes @ tar.angular_velocity
                
                v_pen_point = pen.velocity + np.cross(w_pen_glob, r_pen)
                v_tar_point = tar.velocity + np.cross(w_tar_glob, r_tar)
                
                v_rel = v_pen_point - v_tar_point
                v_rel_normal = np.dot(v_rel, n_glob)
                
                # --- NEW: TANGENTIAL KINEMATICS ---
                # Subtract the normal velocity from the total velocity to get pure sliding velocity
                v_rel_tangent = v_rel - (v_rel_normal * n_glob)
                v_slip = np.linalg.norm(v_rel_tangent)
                
                # 2. Normal Force Math: K * (depth^n) + C * v_n * depth
                F_spring = cp.stiffness * (depth ** cp.exponent)
                
                # --- THE FIX: Apply damping continuously in BOTH directions to bleed energy! ---
                # (Removing the 'if v_rel_normal < 0:' condition stabilizes explicit solvers)
                F_damp = -cp.damping * v_rel_normal * depth
                
                F_mag_normal = F_spring + F_damp
                
                # Failsafe: Normal force can never pull bodies together
                if F_mag_normal < 0: F_mag_normal = 0.0 
                
                # --- REGULARIZED FRICTION MATH ---
                F_frict_glob = np.zeros(3)
                F_mag_friction = 0.0
                
                # --- THE FIX: Only apply friction if enabled by the user! ---
                if cp.friction_enabled and v_slip > 1e-6 and cp.mu > 0.0:
                    # The smooth tanh curve prevents solver explosions near 0 velocity
                    mu_eff = cp.mu * np.tanh(v_slip / cp.slip_tolerance)
                    
                    F_mag_friction = mu_eff * F_mag_normal
                    
                    # Direction is exactly opposite to sliding
                    frict_dir = -v_rel_tangent / v_slip 
                    F_frict_glob = frict_dir * F_mag_friction
                
                # 3. Combine Normal and Friction Vectors
                F_pen_glob = (n_glob * F_mag_normal) + F_frict_glob
                F_tar_glob = -F_pen_glob
                
                # Track scalar forces for the CSV
                cp.current_F_spring += F_spring
                cp.current_F_damp += F_damp
                cp.current_F_total += F_mag_normal
                cp.current_F_friction += F_mag_friction # NEW
                
                # 4. Inject Forces & Torques (Unchanged!)
                if row_pen is not None:
                    Q[row_pen : row_pen+3] += F_pen_glob
                    T_pen = np.cross(r_pen, F_pen_glob)
                    Q[row_pen+3 : row_pen+6] += pen.principal_axes.T @ T_pen
                    
                if row_tar is not None:
                    Q[row_tar : row_tar+3] += F_tar_glob
                    T_tar = np.cross(r_tar, F_tar_glob)
                    Q[row_tar+3 : row_tar+6] += tar.principal_axes.T @ T_tar
        # ==========================================

        # ==========================================
        # --- PHASE 4 - KINEMATIC MOTIONS INJECTION ---
        # ==========================================
        # ==========================================
        # --- PREPARE EQUATION COUNTS ---
        # ==========================================
        active_motions = [m for m in self.motions_list if m.enabled and m.joint.enabled and m.joint.body_i.enabled and m.joint.body_j.enabled]
        self.num_motion_eq = len(active_motions)
        
        num_total_eq = self.num_equations + self.num_gear_eq + self.num_motion_eq
        
        if num_total_eq > 0:
            pos, rot, vel, ang = self.pack_dynamic_states()
            
            # 1. Gather Standard Joints
            if self.num_equations > 0:
                Phi_q, gamma_star = assemble_jacobian_numba(
                    self.num_equations, self.N_vel, self.j_types, self.b_idx_i, self.b_idx_j,
                    pos, rot, vel, ang, self.j_pos_i, self.j_pos_j, self.j_axis_i, 
                    self.j_a_i, self.j_b_i, self.j_a_j, self.j_b_j, self.alpha, self.beta
                )
            else:
                Phi_q = np.zeros((0, self.N_vel))
                gamma_star = np.zeros(0)
                
            # 2. Gather Gear Couplers
            if self.num_gear_eq > 0:
                Phi_q_gears, gamma_star_gears = assemble_gear_jacobian_numba(
                    self.num_gear_eq, self.N_vel, self.g_b_idx_1, self.g_b_idx_2, self.g_b_idx_c,
                    self.g_n1_loc, self.g_n2_loc, rot
                )
                if self.num_equations > 0:
                    Phi_q = np.vstack((Phi_q, Phi_q_gears))
                    gamma_star = np.concatenate((gamma_star, gamma_star_gears))
                else:
                    Phi_q = Phi_q_gears
                    gamma_star = gamma_star_gears

            # ==========================================
            # 3. PHASE 4 - KINEMATIC MOTIONS INJECTION
            # ==========================================
            if self.num_motion_eq > 0:
                Phi_q_mot = np.zeros((self.num_motion_eq, self.N_vel))
                gamma_star_mot = np.zeros(self.num_motion_eq)
                
                for k, motion in enumerate(active_motions):
                    joint = motion.joint
                    f0, df, ddf = motion.get_kinematics(t)
                    
                    b_beta = self.beta if motion.motion_type.value == 0 else 0.0 
                    
                    idx_i = self.body_index_map.get(joint.body_i.name) if not joint.body_i.is_ground else -1
                    idx_j = self.body_index_map.get(joint.body_j.name) if not joint.body_j.is_ground else -1
                    
                    col_i, col_j = idx_i * 6 if idx_i >= 0 else -1, idx_j * 6 if idx_j >= 0 else -1
                    
                    A_i = joint.body_i.principal_axes
                    A_j = joint.body_j.principal_axes
                    w_i = joint.body_i.angular_velocity
                    w_j = joint.body_j.angular_velocity
                    v_i = joint.body_i.velocity
                    v_j = joint.body_j.velocity
                    
                    r_i = joint.body_i.cog
                    r_j = joint.body_j.cog
                    
                    w_glob_i, w_glob_j = A_i @ w_i, A_j @ w_j
                    v_glob_i = A_i @ joint.local_axis_i
                    
                    if motion.trans_rot.value == 1: # Rotational
                        if col_i >= 0: Phi_q_mot[k, col_i+3 : col_i+6] = -joint.local_axis_i
                        if col_j >= 0: Phi_q_mot[k, col_j+3 : col_j+6] = A_j.T @ v_glob_i
                            
                        w_rel = w_glob_j - w_glob_i
                        v_dot_i = np.cross(w_glob_i, v_glob_i)
                        
                        phi_dot_kin = np.dot(w_rel, v_glob_i)
                        gamma_kin = -np.dot(w_rel, v_dot_i)
                        err_vel = phi_dot_kin - df
                        
                        ref_i_glob, ref_j_glob = A_i @ joint.local_a_i, A_j @ joint.local_a_j
                        y_axis = np.cross(v_glob_i, ref_i_glob)
                        proj_j = ref_j_glob - np.dot(ref_j_glob, v_glob_i) * v_glob_i
                        if np.linalg.norm(proj_j) > 1e-8: proj_j /= np.linalg.norm(proj_j)
                        
                        theta_curr = np.arctan2(np.dot(y_axis, proj_j), np.dot(ref_i_glob, proj_j))
                        raw_err = (theta_curr - getattr(motion, 'initial_angle', 0.0)) - f0
                        err_pos = (raw_err + np.pi) % (2 * np.pi) - np.pi
                        
                        gamma_star_mot[k] = ddf + gamma_kin - (2.0 * self.alpha * err_vel) - ((b_beta**2) * err_pos)
                        
                    else: # Translational
                        s_i_glob, s_j_glob = A_i @ joint.local_pos_i, A_j @ joint.local_pos_j
                        d = (r_j + s_j_glob) - (r_i + s_i_glob)
                        
                        if col_i >= 0:
                            Phi_q_mot[k, col_i : col_i+3] = -v_glob_i
                            Phi_q_mot[k, col_i+3 : col_i+6] = A_i.T @ np.cross(v_glob_i, d + s_i_glob)
                        if col_j >= 0:
                            Phi_q_mot[k, col_j : col_j+3] = v_glob_i
                            Phi_q_mot[k, col_j+3 : col_j+6] = A_j.T @ np.cross(s_j_glob, v_glob_i)
                            
                        d_dot = v_j + np.cross(w_glob_j, s_j_glob) - v_i - np.cross(w_glob_i, s_i_glob)
                        v_dot_i = np.cross(w_glob_i, v_glob_i)
                        d_cent = np.cross(w_glob_j, np.cross(w_glob_j, s_j_glob)) - np.cross(w_glob_i, np.cross(w_glob_i, s_i_glob))
                        v_cent_i = np.cross(w_glob_i, v_dot_i)
                        
                        phi_dot_kin = np.dot(d_dot, v_glob_i) + np.dot(d, v_dot_i)
                        gamma_kin = -(np.dot(d_cent, v_glob_i) + 2.0 * np.dot(d_dot, v_dot_i) + np.dot(d, v_cent_i))
                        
                        err_vel = phi_dot_kin - df
                        err_pos = np.dot(d, v_glob_i) - getattr(motion, 'initial_dist', 0.0) - f0
                        
                        gamma_star_mot[k] = ddf + gamma_kin - (2.0 * self.alpha * err_vel) - ((b_beta**2) * err_pos)
                        
                # 4. Stack the Motion matrices onto the main KKT matrices
                if self.num_equations + self.num_gear_eq > 0:
                    Phi_q = np.vstack((Phi_q, Phi_q_mot))
                    gamma_star = np.concatenate((gamma_star, gamma_star_mot))
                else:
                    Phi_q = Phi_q_mot
                    gamma_star = gamma_star_mot

            # ==========================================
            # 5. SOLVE KKT SYSTEM
            # ==========================================
            try:
                lambdas = solve_kkt_system_numba(self.M_constant, Phi_q, Q, gamma_star, self.epsilon)
            except np.linalg.LinAlgError:
                Minv_Q = scipy.linalg.lu_solve(self.lu_M, Q)
                Minv_PhiT = scipy.linalg.lu_solve(self.lu_M, Phi_q.T)
                C_matrix = Phi_q @ Minv_PhiT
                RHS_lambda = Phi_q @ Minv_Q - gamma_star
                lambdas, _, _, _ = np.linalg.lstsq(C_matrix, RHS_lambda, rcond=None)

            # Store the standard joint forces (used heavily for CSV export)
            self.current_lambdas = lambdas[:self.num_equations] if self.num_equations > 0 else np.zeros(0)
            
            # Store the Gear forces for the NEXT active bearing load injection step
            if self.num_gear_eq > 0:
                # --- THE FIX: Add an upper boundary so it doesn't swallow the Motion forces! ---
                end_gear_idx = self.num_equations + self.num_gear_eq
                gear_lambdas = lambdas[self.num_equations : end_gear_idx]
                
                self.current_gear_lambdas = gear_lambdas
                active_gears = [g for g in self.gear_pairs if g.enabled and g.body_1.enabled and g.body_2.enabled]
                for k, gear in enumerate(active_gears):
                    gear.last_lambda = gear_lambdas[k]
            
            # --- Store the Motion Forces for the CSV! ---
            if self.num_motion_eq > 0:
                start_idx = self.num_equations + self.num_gear_eq
                self.current_motion_lambdas = lambdas[start_idx : start_idx + self.num_motion_eq]
            
            constraint_forces = Phi_q.T @ lambdas
            RHS_accel = Q - constraint_forces
            accelerations = scipy.linalg.lu_solve(self.lu_M, RHS_accel)
            
        else:
            self.current_lambdas = np.zeros(0)
            self.current_gear_lambdas = np.zeros(0)
            accelerations = scipy.linalg.lu_solve(self.lu_M, Q)
            
        dY = np.zeros(self.N_total)
        pos_idx, vel_idx, accel_idx = 0, self.N_pos, 0
        
        for body in self.moving_bodies:
            dY[pos_idx : pos_idx+3] = body.velocity
            dq = self.get_quaternion_derivative_local(body.angular_velocity, Y[pos_idx+3 : pos_idx+7])
            dY[pos_idx+3 : pos_idx+7] = dq
            dY[vel_idx : vel_idx+6] = accelerations[accel_idx : accel_idx+6]
            pos_idx += 7; vel_idx += 6; accel_idx += 6
            
        return dY
    

    def run_simulation(self, t_end, dt, integrator=None, progress_callback=None):
        """ 
        Runs the mathematical simulation using the Strategy Pattern. 
        integrator: Defaults to CustomRK4 if None is provided.
        """
        if integrator is None:
            integrator = CustomRK4()
            
        num_steps = int(t_end / dt)
        total_frames = num_steps + 1    
        
        # Define the exact time points we want data for
        t_eval = np.linspace(0.0, t_end, total_frames)
        t_span = (0.0, t_end)
        
        # 1. Grab initial state
        initial_Y = self.pack_state()
        
        msg = f"Starting Solver: {total_frames} frames up to {t_end}s using {integrator.__class__.__name__}..."
        print(msg)
        logging.info(msg)

        # --- Pack Static Joint Data for Numba! ---
        self.prepare_static_numba_data()
        self.initialize_springs() # Capture t=0 geometry for springs definition
        self.initialize_motions()
        
        # ==========================================
        # PHASE 1: THE INTEGRATION (CRUNCHING THE ODE)
        # ==========================================
        # This single line handles the entire timeline!
        # SciPy will adaptively shrink dt internally to resolve collisions/stiffness.
        Y_history = integrator.solve(self.evaluate_derivatives, t_span, initial_Y, t_eval, progress_callback)
        
        # ==========================================
        # PHASE 2: POST-PROCESSING (EXTRACTING FORCES)
        # ==========================================
        # --- Dynamically read how many frames actually survived! The result csv-file is recorded even if simulation crashed ---
        actual_frames = len(Y_history)
        
        self.simulation_history = np.zeros((actual_frames, self.N_total))
        self.lambda_history = np.zeros((actual_frames, self.num_equations))
        self.gear_lambda_history = np.zeros((actual_frames, self.num_gear_eq)) if hasattr(self, 'num_gear_eq') else np.zeros((actual_frames, 0))
        # --- Create a history matrix for explicit Contact Pairs ---
        self.contact_history = np.zeros((actual_frames, len(self.contact_pairs), 4))
        self.motion_lambda_history = np.zeros((actual_frames, getattr(self, 'num_motion_eq', 0)))
        
        print(f"Integration finished. Extracting Reaction Forces for {actual_frames} recorded frames...")
        
        for i in range(actual_frames):
            t = t_eval[i]
            Y_frame = Y_history[i]
            
            try:
                # Evaluate once to populate self.current_lambdas
                self.evaluate_derivatives(t, Y_frame)
            except Exception as e:
                # If the math explodes on the exact frame it died, stop processing cleanly
                print(f"Post-processing stopped early at frame {i} due to math error.")
                self.simulation_history = self.simulation_history[:i]
                self.lambda_history = self.lambda_history[:i]
                self.gear_lambda_history = self.gear_lambda_history[:i]
                self.contact_history = self.contact_history[:i] # Ensure this array gets truncated too!
                break
                
            # Save the frame
            self.simulation_history[i, :] = Y_frame
            self.lambda_history[i, :] = self.current_lambdas
            
            if hasattr(self, 'current_gear_lambdas'):
                self.gear_lambda_history[i, :] = self.current_gear_lambdas
            if hasattr(self, 'current_motion_lambdas'):
                self.motion_lambda_history[i, :] = self.current_motion_lambdas
                
            # --- Save the contact forces to memory ---
            for idx, cp in enumerate(self.contact_pairs):
                self.contact_history[i, idx, 0] = getattr(cp, 'current_F_spring', 0.0)
                self.contact_history[i, idx, 1] = getattr(cp, 'current_F_damp', 0.0)
                self.contact_history[i, idx, 2] = getattr(cp, 'current_F_total', 0.0)
                self.contact_history[i, idx, 3] = getattr(cp, 'current_F_friction', 0.0)
                
        logging.info("Simulation Math & Post-Processing Complete.")
        print("Simulation complete!") # "Simulation complete (or aborted gracefully)."
        return self.simulation_history
    
    # ==========================================
    # --- PHASE 4: POST-PROCESSING ---
    # ==========================================
    
    def export_csv(self, filepath, dt):
        """ Exports the entire simulation history to a human-readable CSV. """
        logging.info(f"Starting CSV Export to {filepath}...")
        
        # 1. Build the Header Row dynamically
        headers = ["Time (s)"]
        for body in self.moving_bodies:
            name = body.name
            headers.extend([
                f"{name}_X (m)", f"{name}_Y (m)", f"{name}_Z (m)", 
                f"{name}_Yaw (deg)", f"{name}_Pitch (deg)", f"{name}_Roll (deg)",
                f"{name}_Vx (m/s)", f"{name}_Vy (m/s)", f"{name}_Vz (m/s)", 
                f"{name}_Wx_loc (rad/s)", f"{name}_Wy_loc (rad/s)", f"{name}_Wz_loc (rad/s)",
                f"{name}_Wx_glob (rad/s)", f"{name}_Wy_glob (rad/s)", f"{name}_Wz_glob (rad/s)",
                f"{name}_KE_Trans (J)", f"{name}_KE_Rot (J)", f"{name}_KE_Total (J)",
                f"{name}_PE (J)", f"{name}_Energy_Total (J)"
            ])
            
        # --- Export Headers for Forces & Actuators ---
        for force in self.forces_list:
            if not force.enabled or force.parent_body.is_ground or not force.parent_body.enabled:
                continue
            name = force.name
            if getattr(force, 'is_gravity', False):
                headers.extend([f"{name}_Fx (N, Glob)", f"{name}_Fy (N, Glob)", f"{name}_Fz (N, Glob)"])
            elif force.force_type in (ForceType.FORCE, ForceType.ACTUATOR):
                headers.extend([
                    f"{name}_Fx (N, Loc)", f"{name}_Fy (N, Loc)", f"{name}_Fz (N, Loc)",
                    f"{name}_Fx (N, Glob)", f"{name}_Fy (N, Glob)", f"{name}_Fz (N, Glob)"
                ])
            elif force.force_type in (ForceType.TORQUE, ForceType.E_MOTOR):
                headers.extend([
                    f"{name}_Tx (Nm, Loc)", f"{name}_Ty (Nm, Loc)", f"{name}_Tz (Nm, Loc)",
                    f"{name}_Tx (Nm, Glob)", f"{name}_Ty (Nm, Glob)", f"{name}_Tz (Nm, Glob)"
                ])
                
        # --- Export Headers for Springs & Bushings ---
        for spring in self.springs_list:
            # 1. STRICT GHOST CHECK: Ensure the object is actively enabled
            if not getattr(spring, 'enabled', True):
                continue
                
            # 2. Ensure it isn't attached to missing or disabled bodies
            if not getattr(spring.body_i, 'enabled', True) or not getattr(spring.body_j, 'enabled', True):
                continue
                
            if spring.body_i.is_ground and spring.body_j.is_ground:
                continue
                
            name = spring.name
            if hasattr(spring, 'initial_length'): # Compression Spring
                headers.extend([
                    f"{name}_Def_dx (m)", f"{name}_Vel_v (m/s)", 
                    f"{name}_F_def_kx (N)", f"{name}_F_damp_cv (N)", f"{name}_F_result (N)"
                ])
            elif hasattr(spring, 'initial_angle'): # Torsion Spring
                headers.extend([
                    f"{name}_Def_dTh (rad)", f"{name}_Vel_w (rad/s)", 
                    f"{name}_T_def_kTh (Nm)", f"{name}_T_damp_cw (Nm)", f"{name}_T_result (Nm)"
                ])
            elif hasattr(spring, 'k_trans'): # Bushing
                headers.extend([
                    f"{name}_dx (m)", f"{name}_dy (m)", f"{name}_dz (m)",
                    f"{name}_dRx (rad)", f"{name}_dRy (rad)", f"{name}_dRz (rad)",
                    f"{name}_Fx (N)", f"{name}_Fy (N)", f"{name}_Fz (N)",
                    f"{name}_Tx (Nm)", f"{name}_Ty (Nm)", f"{name}_Tz (Nm)"
                ])

        # Add Reaction Force Headers (Joints)
        if self.num_equations > 0:
            for joint in self.joints_list:
                if not joint.enabled: continue
                name = joint.name
                if joint.joint_type == JointType.SPHERICAL:
                    headers.extend([f"{name}_Fx (N, Global)", f"{name}_Fy (N, Global)", f"{name}_Fz (N, Global)"])
                elif joint.joint_type in (JointType.REVOLUTE, JointType.PRISMATIC, JointType.CYLINDRICAL, JointType.PLANAR, JointType.FIXED): 
                    headers.extend([
                        f"{name}_Fx (N, Global)", f"{name}_Fy (N, Global)", f"{name}_Fz (N, Global)",
                        f"{name}_Tx (Nm, Global)", f"{name}_Ty (Nm, Global)", f"{name}_Tz (Nm, Global)" 
                    ])
        
        # --- Export Headers for Gear Constraints! ---
        for gear in self.gear_pairs:
            if not gear.enabled or not gear.body_1.enabled or not gear.body_2.enabled: continue
            name = gear.name
            headers.extend([f"{name}_Ft_tangential (N)", f"{name}_Fr_radial (N)", f"{name}_Fa_axial (N)", f"{name}_Fc_contact (N)"])
               
        # --- Contact Pair Headers ---
        for cp in self.contact_pairs:
            headers.extend([
                f"{cp.name}_F_elastic (N)",
                f"{cp.name}_F_damping (N)",
                f"{cp.name}_F_total (N)",
                f"{cp.name}_F_friction (N)"
            ])
        
        # --- Export Headers for Kinematic Motions ---
        for motion in self.motions_list:
            if not motion.enabled or not motion.joint.enabled: continue
            unit = "N" if motion.trans_rot.value == 0 else "Nm"
            headers.append(f"{motion.name}_Actuator_Effort ({unit})")
                        
        def fmt(val):
            return f"{val:.6f}".replace('.', ',')
            
        # 2. Open and Write to File
        try:
            with open(filepath, mode='w', newline='') as file:
                writer = csv.writer(file, delimiter=';') 
                writer.writerow(headers)
                
                total_frames = len(self.simulation_history)
                for i in range(total_frames):
                    t = i * dt 
                    row_data = [fmt(t)]
                    
                    self.unpack_state(self.simulation_history[i])
                    
                    # A. Record Body States
                    for body in self.moving_bodies:
                        v = body.velocity
                        ke_trans = 0.5 * body.mass * np.dot(v, v)
                        
                        w_loc = body.angular_velocity
                        w_glob = body.principal_axes @ w_loc
                        
                        I_loc = body.principal_inertia 
                        ke_rot = 0.5 * np.dot(w_loc, I_loc * w_loc)
                        ke_total = ke_trans + ke_rot
                        
                        g_vector = np.array([0.0, 0.0, 0.0])
                        for force in self.forces_list:
                            if force.parent_body.name == body.name and getattr(force, 'is_gravity', False):
                                # --- THE FIX: Check if gravity is actually enabled before using it! ---
                                if force.enabled:
                                    g_vector = force.base_vector
                                break
                                
                        pe = -body.mass * np.dot(g_vector, body.cog)
                        total_energy = ke_total + pe
                        
                        row_data.extend([
                            fmt(body.cog[0]), fmt(body.cog[1]), fmt(body.cog[2]),
                            fmt(body.pos_angles[0]), fmt(body.pos_angles[1]), fmt(body.pos_angles[2]),
                            fmt(v[0]), fmt(v[1]), fmt(v[2]),
                            fmt(w_loc[0]), fmt(w_loc[1]), fmt(w_loc[2]),
                            fmt(w_glob[0]), fmt(w_glob[1]), fmt(w_glob[2]),
                            fmt(ke_trans), fmt(ke_rot), fmt(ke_total), fmt(pe), fmt(total_energy)
                        ])
                        
                    # B. --- Record Applied Forces & Actuators ---
                    for force in self.forces_list:
                        if not force.enabled or force.parent_body.is_ground or not force.parent_body.enabled:
                            continue
                            
                        body = force.parent_body
                        if getattr(force, 'is_gravity', False):
                            F_glob = force.base_vector * body.mass
                            row_data.extend([fmt(F_glob[0]), fmt(F_glob[1]), fmt(F_glob[2])])
                            
                        elif force.force_type == ForceType.FORCE:
                            F_glob = force.get_global_vector(t)
                            F_loc = force.get_local_vector(t)
                            row_data.extend([fmt(F_loc[0]), fmt(F_loc[1]), fmt(F_loc[2]), fmt(F_glob[0]), fmt(F_glob[1]), fmt(F_glob[2])])
                            
                        elif force.force_type == ForceType.TORQUE:
                            T_glob = force.get_global_vector(t)
                            T_loc = force.get_local_vector(t)
                            row_data.extend([fmt(T_loc[0]), fmt(T_loc[1]), fmt(T_loc[2]), fmt(T_glob[0]), fmt(T_glob[1]), fmt(T_glob[2])])
                            
                        elif force.force_type == ForceType.ACTUATOR:
                            F_glob_max = force.get_global_vector(t)
                            F_max = np.linalg.norm(F_glob_max)
                            scale = 1.0
                            if F_max > 1e-6 and force.speed_max > 0.0:
                                axis_global = F_glob_max / F_max
                                r_glob = body.principal_axes @ force.get_local_position()
                                w_glob = body.principal_axes @ body.angular_velocity
                                v_point_glob = body.velocity + np.cross(w_glob, r_glob) 
                                v_current = np.dot(v_point_glob, axis_global)
                                scale = 1.0 - (v_current / force.speed_max)
                                if not force.allow_braking: scale = max(0.0, scale)
                                
                            F_glob = F_glob_max * scale
                            F_loc = body.principal_axes.T @ F_glob
                            row_data.extend([fmt(F_loc[0]), fmt(F_loc[1]), fmt(F_loc[2]), fmt(F_glob[0]), fmt(F_glob[1]), fmt(F_glob[2])])
                            
                        elif force.force_type == ForceType.E_MOTOR:
                            T_loc_max = force.get_local_vector(t)
                            T_max = np.linalg.norm(T_loc_max)
                            scale = 1.0
                            if T_max > 1e-6 and force.speed_max > 0.0:
                                axis_local = T_loc_max / T_max
                                omega_current = np.dot(body.angular_velocity, axis_local)
                                scale = 1.0 - (omega_current / force.speed_max)
                                if not force.allow_braking: scale = max(0.0, scale)
                                
                            T_loc = T_loc_max * scale
                            T_glob = body.principal_axes @ T_loc
                            row_data.extend([fmt(T_loc[0]), fmt(T_loc[1]), fmt(T_loc[2]), fmt(T_glob[0]), fmt(T_glob[1]), fmt(T_glob[2])])

                    # C. --- Record Compliant Springs ---
                    for spring in self.springs_list:
                        # STRICT GHOST CHECK: Ensure the object is actively enabled
                        if not getattr(spring, 'enabled', True):
                            continue
                            
                        # Ensure it isn't attached to missing or disabled bodies
                        if not getattr(spring.body_i, 'enabled', True) or not getattr(spring.body_j, 'enabled', True):
                            continue
                            
                        if spring.body_i.is_ground and spring.body_j.is_ground:
                            continue
                            
                        A_i, A_j = spring.body_i.principal_axes, spring.body_j.principal_axes
                        w_i_glob = A_i @ spring.body_i.angular_velocity
                        w_j_glob = A_j @ spring.body_j.angular_velocity
                        r_i_glob = A_i @ spring.local_pos_i
                        r_j_glob = A_j @ spring.local_pos_j
                        p_i = spring.body_i.cog + r_i_glob
                        p_j = spring.body_j.cog + r_j_glob
                        
                        if hasattr(spring, 'initial_length'): 
                            vec_ij = p_j - p_i
                            L = np.linalg.norm(vec_ij)
                            if L < 1e-8:
                                row_data.extend([fmt(0.0)] * 5)
                                continue
                                
                            u_ij = vec_ij / L
                            v_i_glob = spring.body_i.velocity + np.cross(w_i_glob, r_i_glob)
                            v_j_glob = spring.body_j.velocity + np.cross(w_j_glob, r_j_glob)
                            
                            L_dot = np.dot(v_j_glob - v_i_glob, u_ij)
                            delta_L = L - spring.initial_length
                            
                            F_def = spring.stiffness * delta_L
                            F_damp = spring.damping * L_dot
                            F_res = F_def + F_damp - spring.preload
                            
                            # Log Kinematics + Forces (Global vectors removed!)
                            row_data.extend([
                                fmt(delta_L), fmt(L_dot),
                                fmt(F_def), fmt(F_damp), fmt(F_res)
                            ])
                            
                        elif hasattr(spring, 'initial_angle'): 
                            axis_glob = A_i @ spring.local_axis_i
                            ref_i_glob = A_i @ spring.local_ref_i
                            ref_j_glob = A_j @ spring.local_ref_j
                            
                            theta_dot = np.dot(w_j_glob - w_i_glob, axis_glob)
                            
                            y_axis = np.cross(axis_glob, ref_i_glob)
                            proj_j = ref_j_glob - np.dot(ref_j_glob, axis_glob) * axis_glob
                            if np.linalg.norm(proj_j) > 1e-8: proj_j /= np.linalg.norm(proj_j)
                            
                            cos_th = np.dot(ref_i_glob, proj_j)
                            sin_th = np.dot(y_axis, proj_j)
                            current_angle = np.arctan2(sin_th, cos_th)
                            
                            delta_theta = current_angle - spring.initial_angle
                            if delta_theta > np.pi: delta_theta -= 2 * np.pi
                            elif delta_theta < -np.pi: delta_theta += 2 * np.pi
                            
                            T_def = spring.stiffness * delta_theta
                            T_damp = spring.damping * theta_dot
                            T_res = T_def + T_damp - spring.preload
                            
                            # Log Kinematics + Torques (Global vectors removed!)
                            row_data.extend([
                                fmt(delta_theta), fmt(theta_dot),
                                fmt(T_def), fmt(T_damp), fmt(T_res)
                            ])
                            
                        # --- Bushing CSV Telemetry ---
                        # --- ADD THIS: Bushing CSV Telemetry (Orientation Upgraded) ---
                        elif hasattr(spring, 'k_trans'): 
                            A_i, A_j = spring.body_i.principal_axes, spring.body_j.principal_axes
                            
                            # --- THE UPGRADE: Calculate the Global Rotation of RF_I ---
                            R_rf_i = A_i @ spring.local_rot_i
                            
                            w_i_glob = A_i @ spring.body_i.angular_velocity
                            w_j_glob = A_j @ spring.body_j.angular_velocity
                            v_i_glob = spring.body_i.velocity + np.cross(w_i_glob, A_i @ spring.local_pos_i)
                            v_j_glob = spring.body_j.velocity + np.cross(w_j_glob, A_j @ spring.local_pos_j)
                            
                            p_i = spring.body_i.cog + A_i @ spring.local_pos_i
                            p_j = spring.body_j.cog + A_j @ spring.local_pos_j
                            
                            # 1. Project translations into RF_I's rotated frame!
                            delta_x = (R_rf_i.T @ (p_j - p_i)) - spring.initial_local_pos_j
                            v_rel_loc = R_rf_i.T @ (v_j_glob - v_i_glob)
                            
                            # 2. Extract delta Euler angles in RF_I's rotated frame!
                            R_rel = R_rf_i.T @ A_j
                            R_delta = R_rel @ spring.initial_rel_rot.T
                            
                            angle = np.arccos(np.clip((np.trace(R_delta) - 1.0) / 2.0, -1.0, 1.0))
                            if angle > 1e-8:
                                axis = np.array([R_delta[2,1]-R_delta[1,2], R_delta[0,2]-R_delta[2,0], R_delta[1,0]-R_delta[0,1]])
                                norm_axis = np.linalg.norm(axis)
                                delta_theta = (axis / norm_axis) * angle if norm_axis > 1e-8 else np.zeros(3)
                            else:
                                delta_theta = np.zeros(3)
                                
                            w_rel_loc = R_rf_i.T @ (w_j_glob - w_i_glob)
                            
                            # 3. Recalculate local forces/torques using the corrected orientations
                            F_calc_loc = -(spring.k_trans * delta_x) - (spring.c_trans * v_rel_loc) + spring.p_trans
                            T_calc_loc = -(spring.k_rot * delta_theta) - (spring.c_rot * w_rel_loc) + spring.p_rot
                            
                            row_data.extend([
                                fmt(delta_x[0]), fmt(delta_x[1]), fmt(delta_x[2]),
                                fmt(delta_theta[0]), fmt(delta_theta[1]), fmt(delta_theta[2]),
                                fmt(F_calc_loc[0]), fmt(F_calc_loc[1]), fmt(F_calc_loc[2]),
                                fmt(T_calc_loc[0]), fmt(T_calc_loc[1]), fmt(T_calc_loc[2])
                            ]) 

                    # D. Add the Reaction Forces (Joint Lambdas)    
                    if self.num_equations > 0:
                        lambdas = self.lambda_history[i]
                        idx = 0
                        for joint in self.joints_list:
                            if not joint.enabled: continue
                            if joint.joint_type == JointType.SPHERICAL:
                                row_data.extend([fmt(lambdas[idx]), fmt(lambdas[idx+1]), fmt(lambdas[idx+2])])
                                idx += 3
                            elif joint.joint_type == JointType.REVOLUTE: 
                                A_i, A_j = joint.body_i.principal_axes, joint.body_j.principal_axes
                                v_glob_i = A_i @ joint.local_axis_i
                                a_glob_j = A_j @ joint.local_a_j
                                b_glob_j = A_j @ joint.local_b_j
                                T_glob = lambdas[idx+3] * np.cross(v_glob_i, a_glob_j) + lambdas[idx+4] * np.cross(v_glob_i, b_glob_j)
                                row_data.extend([
                                    fmt(lambdas[idx]), fmt(lambdas[idx+1]), fmt(lambdas[idx+2]),
                                    fmt(T_glob[0]), fmt(T_glob[1]), fmt(T_glob[2]) 
                                ])
                                idx += 5    
                            elif joint.joint_type == JointType.PRISMATIC: 
                                A_i = joint.body_i.principal_axes
                                A_j = joint.body_j.principal_axes
                                
                                # --- THE FIX: Use the exact 1-RF axes! ---
                                v_loc_i = joint.local_axis_i
                                a_loc_i = getattr(joint, 'local_a_i', np.array([1.0, 0.0, 0.0]))
                                b_loc_i = getattr(joint, 'local_b_i', np.array([0.0, 1.0, 0.0]))
                                
                                # Rotate all vectors to Global Frame
                                v_glob_i = A_i @ v_loc_i
                                a_glob_i = A_i @ a_loc_i
                                b_glob_i = A_i @ b_loc_i
                                
                                a_glob_j = A_j @ joint.local_a_j
                                b_glob_j = A_j @ joint.local_b_j
                                
                                s_i_glob = A_i @ joint.local_pos_i
                                s_j_glob = A_j @ joint.local_pos_j
                                d = (joint.body_j.cog + s_j_glob) - (joint.body_i.cog + s_i_glob)
                                
                                F_body_i = -lambdas[idx+3] * a_glob_i - lambdas[idx+4] * b_glob_i
                                T_pure_i = lambdas[idx+0] * np.cross(v_glob_i, a_glob_j) + \
                                           lambdas[idx+1] * np.cross(v_glob_i, b_glob_j) + \
                                           lambdas[idx+2] * np.cross(a_glob_i, b_glob_j)
                                
                                F_glob = -F_body_i
                                T_glob = T_pure_i + np.cross(d, F_body_i)
                                
                                row_data.extend([
                                    fmt(F_glob[0]), fmt(F_glob[1]), fmt(F_glob[2]),
                                    fmt(T_glob[0]), fmt(T_glob[1]), fmt(T_glob[2]) 
                                ])
                                idx += 5

                            elif joint.joint_type == JointType.CYLINDRICAL:
                                A_i = joint.body_i.principal_axes
                                A_j = joint.body_j.principal_axes
                                
                                # --- THE FIX: Use the exact 1-RF axes! ---
                                v_loc_i = joint.local_axis_i
                                a_loc_i = getattr(joint, 'local_a_i', np.array([1.0, 0.0, 0.0]))
                                b_loc_i = getattr(joint, 'local_b_i', np.array([0.0, 1.0, 0.0]))
                                
                                v_glob_i = A_i @ v_loc_i
                                a_glob_i = A_i @ a_loc_i
                                b_glob_i = A_i @ b_loc_i
                                
                                a_glob_j = A_j @ joint.local_a_j
                                b_glob_j = A_j @ joint.local_b_j
                                
                                s_i_glob = A_i @ joint.local_pos_i
                                s_j_glob = A_j @ joint.local_pos_j
                                d = (joint.body_j.cog + s_j_glob) - (joint.body_i.cog + s_i_glob)
                                
                                F_body_i = -lambdas[idx+2] * a_glob_i - lambdas[idx+3] * b_glob_i
                                T_pure_i = lambdas[idx+0] * np.cross(v_glob_i, a_glob_j) + \
                                           lambdas[idx+1] * np.cross(v_glob_i, b_glob_j)
                                
                                F_glob = -F_body_i
                                T_glob = T_pure_i + np.cross(d, F_body_i)
                                
                                row_data.extend([
                                    fmt(F_glob[0]), fmt(F_glob[1]), fmt(F_glob[2]),
                                    fmt(T_glob[0]), fmt(T_glob[1]), fmt(T_glob[2]) 
                                ])
                                idx += 4

                            elif joint.joint_type == JointType.PLANAR:
                                # (Leave Planar as it was, it already uses v_glob_i correctly)
                                A_i = joint.body_i.principal_axes
                                A_j = joint.body_j.principal_axes
                                
                                v_glob_i = A_i @ joint.local_axis_i
                                a_glob_j = A_j @ joint.local_a_j
                                b_glob_j = A_j @ joint.local_b_j
                                
                                s_i_glob = A_i @ joint.local_pos_i
                                s_j_glob = A_j @ joint.local_pos_j
                                d = (joint.body_j.cog + s_j_glob) - (joint.body_i.cog + s_i_glob)
                                
                                F_body_i = -lambdas[idx+2] * v_glob_i
                                T_pure_i = lambdas[idx+0] * np.cross(v_glob_i, a_glob_j) + \
                                           lambdas[idx+1] * np.cross(v_glob_i, b_glob_j)
                                
                                F_glob = -F_body_i
                                T_glob = T_pure_i + np.cross(d, F_body_i)
                                
                                row_data.extend([
                                    fmt(F_glob[0]), fmt(F_glob[1]), fmt(F_glob[2]),
                                    fmt(T_glob[0]), fmt(T_glob[1]), fmt(T_glob[2]) 
                                ])
                                idx += 3

                            elif joint.joint_type == JointType.FIXED:
                                A_i = joint.body_i.principal_axes
                                A_j = joint.body_j.principal_axes
                                
                                # --- THE FIX: Use the exact 1-RF axes! ---
                                v_loc_i = joint.local_axis_i
                                a_loc_i = getattr(joint, 'local_a_i', np.array([1.0, 0.0, 0.0]))
                                
                                v_glob_i = A_i @ v_loc_i
                                a_glob_i = A_i @ a_loc_i
                                
                                a_glob_j = A_j @ joint.local_a_j
                                b_glob_j = A_j @ joint.local_b_j
                                
                                F_glob = np.array([lambdas[idx+0], lambdas[idx+1], lambdas[idx+2]])
                                T_glob = lambdas[idx+3] * np.cross(v_glob_i, a_glob_j) + \
                                         lambdas[idx+4] * np.cross(v_glob_i, b_glob_j) + \
                                         lambdas[idx+5] * np.cross(a_glob_i, b_glob_j)
                                         
                                row_data.extend([
                                    fmt(F_glob[0]), fmt(F_glob[1]), fmt(F_glob[2]),
                                    fmt(T_glob[0]), fmt(T_glob[1]), fmt(T_glob[2]) 
                                ])
                                idx += 6
                    
                    # F. --- Record Kinematic Motion Actuator Effort ---
                    if hasattr(self, 'motion_lambda_history') and getattr(self, 'num_motion_eq', 0) > 0:
                        mot_lambdas = self.motion_lambda_history[i]
                        m_idx = 0
                        for motion in self.motions_list:
                            if not motion.enabled or not motion.joint.enabled: continue
                            row_data.append(fmt(mot_lambdas[m_idx]))
                            m_idx += 1
                    
                    # --- Export Telemetry for Gear Constraints ---
                    if hasattr(self, 'gear_lambda_history'):
                        gear_lambdas = self.gear_lambda_history[i]
                        g_idx = 0
                        for gear in self.gear_pairs:
                            if not gear.enabled or not gear.body_1.enabled or not gear.body_2.enabled: continue
                            F_t = gear_lambdas[g_idx]
                            
                            # Safely handle Bevel vs Standard
                            if gear.gear_type == GearType.BEVEL:
                                F_r = abs(F_t) * np.tan(gear.alpha) * np.cos(gear.gamma)
                                F_a = abs(F_t) * np.tan(gear.alpha) * np.sin(gear.gamma)
                            else:
                                F_r = abs(F_t) * np.tan(gear.alpha) / np.cos(gear.beta)
                                F_a = abs(F_t) * np.tan(gear.beta) * np.sign(F_t)
                                
                            F_c = np.sqrt(F_t**2 + F_r**2 + F_a**2)
                            row_data.extend([fmt(F_t), fmt(F_r), fmt(F_a), fmt(F_c)])
                            g_idx += 1
                                        
                    # E. --- Record Contact Pairs ---
                    for idx, cp in enumerate(self.contact_pairs):
                        f_spr = self.contact_history[i, idx, 0]
                        f_dmp = self.contact_history[i, idx, 1]
                        f_tot = self.contact_history[i, idx, 2]
                        f_frict = self.contact_history[i, idx, 3]
                        
                        row_data.extend([fmt(f_spr), fmt(f_dmp), fmt(f_tot), fmt(f_frict)])
                                            
                    writer.writerow(row_data)
                    
            logging.info("CSV Export Complete with Comprehensive Force/Spring Data.")
            print(f"Data exported successfully to: {filepath}")
            
        except Exception as e:
            logging.error(f"Failed to write CSV: {e}")
            print(f"Error exporting CSV: {e}")
            
    def check_broadphase_collisions(self, t):
        """ Broad Phase: Checks AABB overlap ONLY for explicit Contact Pairs. """
        active_contacts = []
        
        for cp in self.contact_pairs:
            # Skip if the contact pair or either body is disabled
            if not cp.enabled or not cp.body_i.enabled or not cp.body_j.enabled:
                continue
                
            min_i, max_i = cp.body_i.get_global_aabb()
            min_j, max_j = cp.body_j.get_global_aabb()
            
            if min_i is None or min_j is None: 
                continue
            
            """    
            # ==========================================
            # --- THE DEBUG LOGGER ---
            # Calculate the exact numerical overlap (positive = overlapping, negative = gap)
            amt_x = min(max_i[0], max_j[0]) - max(min_i[0], min_j[0])
            amt_y = min(max_i[1], max_j[1]) - max(min_i[1], min_j[1])
            amt_z = min(max_i[2], max_j[2]) - max(min_i[2], min_j[2])

            # Print ONLY if the boxes are very close to each other (gap is less than 10mm)
            if amt_x > -0.01 and amt_y > -0.01 and amt_z > -0.01:
                # We multiply by 1000 so the console prints it nicely in millimeters
                print(f"[{t:.3f}s - {cp.name}] AABB Overlaps -> X: {amt_x*1000.0:.3f} mm | Y: {amt_y*1000.0:.3f} mm | Z: {amt_z*1000.0:.3f} mm")
            # ==========================================
            """
                
            # --- The AABB Overlap Math ---
            overlap_x = (min_i[0] <= max_j[0]) and (max_i[0] >= min_j[0])
            overlap_y = (min_i[1] <= max_j[1]) and (max_i[1] >= min_j[1])
            overlap_z = (min_i[2] <= max_j[2]) and (max_i[2] >= min_j[2])
            
            if overlap_x and overlap_y and overlap_z:
                active_contacts.append(cp)
                
        return active_contacts    
    
    def evaluate_narrow_phase(self, body_a, body_b, mesh_mode=0):
        """ Narrow Phase: Vertex-to-Mesh Proximity Check with dynamic simplification modes. """
        import trimesh

        def get_collision_mesh(body, mode):
            # Dynamic cache naming so we don't accidentally mix mesh types!
            mesh_attr = f'collision_mesh_mode_{mode}'
            
            if not hasattr(body, mesh_attr):
                # MODE 3: Convex Hull (Fastest, Shrink-wrapped)
                if mode == 3: 
                    # Body.raw_geom is already a Trimesh object, so we can extract the hull instantly!
                    hull = body.raw_geom.convex_hull
                    setattr(body, mesh_attr, hull)
                    return hull
                
                # --- PyVista Modifications ---
                if mode == 1:   # MODE 1: Fine (High-Res)
                    clean_mesh = body.mesh.clean().subdivide(1, subfilter='linear')
                elif mode == 2: # MODE 2: Decimate (Reduce triangles by 50%)
                    clean_mesh = body.mesh.clean().decimate(0.5)
                else:           # MODE 0: Standard
                    clean_mesh = body.mesh.clean()
                
                # Convert back to Trimesh for proximity searching
                verts = clean_mesh.points
                try:
                    faces = clean_mesh.faces.reshape((-1, 4))[:, 1:4]
                except ValueError:
                    faces = clean_mesh.faces.reshape((-1, 3))
                    
                setattr(body, mesh_attr, trimesh.Trimesh(vertices=verts, faces=faces))
                
            return getattr(body, mesh_attr)

        contacts = []

        min_a, max_a = body_a.get_global_aabb()
        min_b, max_b = body_b.get_global_aabb()
        overlap_min = np.maximum(min_a, min_b) - 0.001 
        overlap_max = np.minimum(max_a, max_b) + 0.001

        def get_penetrations(penetrator, target):
            # Extract the user's chosen mesh complexity
            pen_mesh = get_collision_mesh(penetrator, mesh_mode)
            tar_mesh = get_collision_mesh(target, mesh_mode)

            local_verts_m = pen_mesh.vertices * 0.001 
            global_verts_m = (penetrator.principal_axes @ local_verts_m.T).T + penetrator.cog
            
            in_box = np.all((global_verts_m >= overlap_min) & (global_verts_m <= overlap_max), axis=1)
            candidate_verts_m = global_verts_m[in_box]
            
            if len(candidate_verts_m) == 0: 
                return []

            target_local_candidates_m = (target.principal_axes.T @ (candidate_verts_m - target.cog).T).T
            target_local_candidates_mm = target_local_candidates_m * 1000.0
            
            try:
                closest_pts_mm, distances_mm, tri_ids = tar_mesh.nearest.on_surface(target_local_candidates_mm)
            except Exception as e:
                print(f"  -> ERROR: Trimesh proximity crashed! {e}")
                return []

            manifold = []
            for i in range(len(target_local_candidates_mm)):
                vec_to_vertex = target_local_candidates_mm[i] - closest_pts_mm[i]
                local_normal = tar_mesh.face_normals[tri_ids[i]]
                
                dot_prod = np.dot(vec_to_vertex, local_normal)
                depth_m = distances_mm[i] * 0.001
                
                if dot_prod < -1e-5:
                    if depth_m < 1e-6: continue
                    global_normal = target.principal_axes @ local_normal
                    manifold.append({
                        'body_pen': penetrator,          
                        'body_tar': target,              
                        'point': candidate_verts_m[i],    
                        'normal': global_normal,         
                        'depth': depth_m                   
                    })
            return manifold

        contacts.extend(get_penetrations(body_a, body_b))
        contacts.extend(get_penetrations(body_b, body_a))
        
        return contacts