# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.1
#  Release Date: 2026/09/30
#  Module: unit_joints.py
#  Description:
#      Defines various joint types and kinematic gear pair constraints for multibody dynamics simulations.
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
from enum import Enum
import pyvista as pv

MMtoM = 1000.0

class JointType(Enum):
    FIXED = 1
    SPHERICAL = 2
    REVOLUTE = 3
    CYLINDRICAL = 4
    PRISMATIC = 5
    PLANAR = 6

class GearType(Enum):
    SPUR_HELICAL = 1
    INTERNAL = 2
    BEVEL = 3

class GearPair:
    """ 
    Kinematic Coupler Constraint. 
    Mathematically links two Revolute joints to transmit power without 3D mesh collisions.
    """
    def __init__(self, name, joint_1, joint_2, gear_type, module_n, z1, z2, alpha_deg=20.0, beta_deg=0.0, gamma_deg=45.0):
        self.name = name
        self.enabled = True
        
        self.joint_1 = joint_1
        self.joint_2 = joint_2
        
        self.body_1 = joint_1.body_j
        self.body_2 = joint_2.body_j
        
        # In professional gear trains (Planetary), both shafts mount to the same Carrier or Ground
        self.carrier = joint_1.body_i 
        
        self.gear_type = gear_type
        self.module_n = module_n
        self.z1 = z1
        self.z2 = z2
        self.alpha = np.radians(alpha_deg)
        self.beta = np.radians(beta_deg)
        self.gamma = np.radians(gamma_deg)
        
        self.last_lambda = 0.0 # Stores F_t (Tangential Force) to calculate bearing loads
        
        # Local vectors locked into the Carrier's Reference Frame
        self.n1_loc = np.zeros(3)
        self.n2_loc = np.zeros(3)
        self.ur_loc = np.zeros(3)  # Radial separating vector
        self.za_loc = np.zeros(3)  # Axial thrust vector
        self.p_pitch_loc = np.zeros(3)
        
    def bind_kinematics(self):
        """ Calculates the 3D Pitch Point and Tangent vectors at t=0 and locks them to the Carrier. """
        A_c = self.carrier.principal_axes if not self.carrier.is_ground else np.eye(3)
        c_cog = self.carrier.cog if not self.carrier.is_ground else np.zeros(3)
        
        # --- Extract true Global Geometry regardless of what the joints are anchored to! ---
        c1_glob = self.joint_1.body_i.cog + self.joint_1.body_i.principal_axes @ self.joint_1.local_pos_i
        c2_glob = self.joint_2.body_i.cog + self.joint_2.body_i.principal_axes @ self.joint_2.local_pos_i
        
        z1_glob = self.joint_1.body_i.principal_axes @ self.joint_1.local_axis_i
        z2_glob = self.joint_2.body_i.principal_axes @ self.joint_2.local_axis_i
        
        # --- Convert module from millimeters to meters for the solver! ---
        # --- Calculate theoretical radii directly from Transverse Module ---
        m_t = self.module_n / MMtoM
        r1 = (m_t * self.z1) / 2.0
        r2 = (m_t * self.z2) / 2.0
        
        d_vec = c2_glob - c1_glob
        dist = np.linalg.norm(d_vec)
        
        sign_2 = 1.0 # External gears rotate oppositely (+1)
        
        if self.gear_type == GearType.SPUR_HELICAL:
            ur_glob = d_vec / dist if dist > 1e-6 else np.array([1., 0., 0.])
            p_pitch_glob = c1_glob + r1 * ur_glob
            za_glob = z1_glob
            
        elif self.gear_type == GearType.INTERNAL:
            ur_glob = -d_vec / dist if dist > 1e-6 else np.array([1., 0., 0.])
            p_pitch_glob = c1_glob + r1 * ur_glob
            za_glob = z1_glob
            sign_2 = -1.0 # Internal rings rotate in the same direction! (-1)
            
        elif self.gear_type == GearType.BEVEL:
            # For Bevel, radial separation force acts perpendicularly to the intersecting axes
            t_glob = np.cross(z1_glob, z2_glob)
            if np.linalg.norm(t_glob) > 1e-6: t_glob /= np.linalg.norm(t_glob)
            else: t_glob = np.array([0., 1., 0.])
            ur_glob = np.cross(t_glob, z1_glob)
            p_pitch_glob = c1_glob + r1 * ur_glob
            za_glob = z1_glob
            sign_2 = 1.0
            
        # The Willis Magic Vectors: Torque = Pitch Radius * Axis
        n1_glob = r1 * z1_glob
        n2_glob = sign_2 * r2 * z2_glob
        
        # Stamp into the Carrier's Local Frame!
        self.n1_loc = A_c.T @ n1_glob
        self.n2_loc = A_c.T @ n2_glob
        self.ur_loc = A_c.T @ ur_glob
        self.za_loc = A_c.T @ za_glob
        self.p_pitch_loc = A_c.T @ (p_pitch_glob - c_cog)

class Joint:
    """ Python port of TJoint. Represents a kinematic constraint between two bodies. """
    def __init__(self, name, joint_type, body_i, body_j, plotter):
        self.name = name
        self.joint_type = joint_type
        self.body_i = body_i
        self.body_j = body_j
        
        self.enabled = True
        self.visible = True

        # --- MATHEMATICAL CORE (Stamped from RFs) ---
        # Position of the Anchor point in local coordinates
        self.local_pos_i = np.zeros(3)
        self.local_pos_j = np.zeros(3)
        
        # Primary Axis (Calculated from Anchor to Target, or just Z-axis of Anchor)
        self.local_axis_i = np.array([0.0, 0.0, 1.0])
        self.local_axis_j = np.array([0.0, 0.0, 1.0])

        # --- Orthogonal Plane Axes for Revolute/Cylindrical constraints ---
        self.local_a_j = np.array([1.0, 0.0, 0.0]) # Local X-axis
        self.local_b_j = np.array([0.0, 1.0, 0.0]) # Local Y-axis
        
        # --- THE FIX: Add Body I's Orthogonal Plane Axes ---
        self.local_a_i = np.array([1.0, 0.0, 0.0])
        self.local_b_i = np.array([0.0, 1.0, 0.0])
        
        # UI Memory Trackers
        self.source_anchor_name = ""
        self.source_target_name = ""

        # Visualization
        self.plotter = plotter
        self.actors = []
        self.base_color = "cyan" # Distinct color for Joints
        
        self.create_visuals()

    # ==========================================
    # --- ONE-TIME R-FRAME APPLICATION ---
    # ==========================================
    def apply_initial_rfs(self, anchor_rf, target_rf=None):
        """ 
        Calculates the local constraint coordinates for BOTH bodies based on the RFs.
        This stamps the math and severs the link to the original RFs.
        """
        if not anchor_rf:
            return

        self.source_anchor_name = anchor_rf.name
        if target_rf:
            self.source_target_name = target_rf.name

        global_anchor_pos = anchor_rf.position

        # 1. Stamp Anchor Position into Local Body I
        vec_to_anchor_i = global_anchor_pos - self.body_i.cog
        self.local_pos_i = self.body_i.principal_axes.T @ vec_to_anchor_i

        # 2. Stamp Anchor Position into Local Body J
        vec_to_anchor_j = global_anchor_pos - self.body_j.cog
        self.local_pos_j = self.body_j.principal_axes.T @ vec_to_anchor_j

        # 3. Determine Axis Vector (Anchor to Target, or fallback to Anchor's Z-axis)
        if target_rf:
            global_axis = target_rf.position - global_anchor_pos
            mag = np.linalg.norm(global_axis)
            if mag > 1e-6:
                global_axis = global_axis / mag
            else:
                global_axis = anchor_rf.transform_matrix[:, 2] # Fallback to Z
        else:
            global_axis = anchor_rf.transform_matrix[:, 2] # Fallback to Z

        # 4. Stamp Axis Vector into Local Bodies
        self.local_axis_i = self.body_i.principal_axes.T @ global_axis
        self.local_axis_j = self.body_j.principal_axes.T @ global_axis

        # --- Generate the Orthogonal Triad (a and b) for Body J ---
        # Pick an arbitrary vector that isn't parallel to global_axis
        if abs(global_axis[0]) < 0.9:
            temp_vec = np.array([1.0, 0.0, 0.0])
        else:
            temp_vec = np.array([0.0, 1.0, 0.0])
            
        # Cross products guarantee perfect 90-degree orthogonality!
        global_a = np.cross(global_axis, temp_vec)
        global_a = global_a / np.linalg.norm(global_a) # Normalize X-axis
        global_b = np.cross(global_axis, global_a)     # Generate Y-axis
        
        # Stamp into Local Body J
        self.local_a_j = self.body_j.principal_axes.T @ global_a
        self.local_b_j = self.body_j.principal_axes.T @ global_b
        
        # --- THE FIX: Stamp the exact same initial vectors into Body I! ---
        self.local_a_i = self.body_i.principal_axes.T @ global_a
        self.local_b_i = self.body_i.principal_axes.T @ global_b

    # ==========================================
    # --- VISUALIZATION ---
    # ==========================================
    def create_visuals(self):
        """ Generates a 3D icon based on the Joint Type """
        self.actors = []
        
        # Color mapping by type to make them easily distinguishable
        type_colors = {
            JointType.FIXED: "darkgray",
            JointType.SPHERICAL: "red", #magenta
            JointType.REVOLUTE: "red", #cyan
            JointType.CYLINDRICAL: "blue", #orange
            JointType.PRISMATIC: "blue", #yellow
            JointType.PLANAR: "darkgray" #purple
        }
        self.base_color = type_colors.get(self.joint_type, "cyan")

        if self.joint_type == JointType.SPHERICAL:
            geom = pv.Sphere(radius=0.5)
        elif self.joint_type in [JointType.REVOLUTE, JointType.CYLINDRICAL]:
            geom = pv.Cylinder(direction=(0,0,1), radius=0.3, height=1.5)
        elif self.joint_type == JointType.PRISMATIC:
            geom = pv.Cube(x_length=0.4, y_length=0.4, z_length=1.5)
        elif self.joint_type == JointType.PLANAR:
            geom = pv.Plane(i_size=1.5, j_size=1.5)
        else: # FIXED
            geom = pv.Cube(x_length=0.8, y_length=0.8, z_length=0.8)

        act = self.plotter.add_mesh(geom, color=self.base_color, pickable=False)
        self.actors.append(act)
        
        for a in self.actors:
            a.SetVisibility(False)

    def set_visible(self, is_visible):
        self.visible = is_visible
        # Only show if both the joint and its primary body are visible
        is_shown = self.visible and self.enabled and self.body_i.visible
        for act in self.actors:
            act.SetVisibility(is_shown)

    def set_selected(self, is_selected):
        display_color = "gold" if is_selected else self.base_color
        for act in self.actors:
            act.prop.color = display_color

    def update_transform(self, scale_size):
        """ Visually glues the Joint icon to Body_I in the viewport without spinning artifacts. """
        if not self.visible or not self.enabled or not self.body_i.visible:
            for act in self.actors:
                act.SetVisibility(False)
            return

        for act in self.actors:
            act.SetVisibility(True)

        # 1. Find Global Position (Tracking Body_I)
        g_pos = (self.body_i.principal_axes @ self.local_pos_i) + self.body_i.cog
        
        # 2. Calculate Local Rotation Matrix (Constant alignment to local_axis_i)
        v1 = np.array([0.0, 0.0, 1.0]) # Native geometry points along Z
        l_axis = self.local_axis_i
        
        v_cross = np.cross(v1, l_axis)
        c = np.dot(v1, l_axis)
        
        if c < -0.9999:
            local_R = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]])
        else:
            skew_v = np.array([[0, -v_cross[2], v_cross[1]],
                               [v_cross[2], 0, -v_cross[0]],
                               [-v_cross[1], v_cross[0], 0]])
            local_R = np.eye(3) + skew_v + (skew_v @ skew_v) * (1 / (1 + c))

        # 3. Apply Body I's full 3D rotation to the local alignment
        # This locks the twist and completely eliminates the spinning bug!
        global_R = self.body_i.principal_axes @ local_R

        # ==========================================
        # --- Adjust Size comparing to the RF arrows size!---
        # ==========================================
        visual_scale = scale_size * 0.7 # Slightly smaller than the RF arrows for clarity 
        
        # 4. Construct 4x4 homogenous matrix for the graphics card
        mat = np.eye(4)
        mat[:3, :3] = global_R * visual_scale # scale_size
        mat[:3, 3] = g_pos * MMtoM 

        for act in self.actors:
            act.user_matrix = mat