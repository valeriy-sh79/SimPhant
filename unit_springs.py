# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.09.0
#  Module: unit_springs.py
#  Description:
#      Defines compliant physical connections, including 1D compression/torsion springs 
#      and fully spatial 6-DOF bushings with custom stiffness and damping parameters.
#
#  Copyright (C) 2026  Valeriy Shapovalov
#  GitHub: https://github.com/valeriy-sh79

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
import pyvista as pv

class BaseSpring:
    """ Parent class for all compliant elements in the simulation. """
    def __init__(self, name, body_i, rf_i_name, body_j, rf_j_name, plotter):
        self.name = name
        self.body_i = body_i
        self.rf_i_name = rf_i_name
        self.body_j = body_j
        self.rf_j_name = rf_j_name
        
        self.enabled = True
        self.visible = True
        
        self.plotter = plotter
        self.actors = []
        
        # --- Kinematic Memory ---
        self.local_pos_i = np.zeros(3)
        self.local_pos_j = np.zeros(3)
        self.local_axis_i = np.array([0.0, 0.0, 1.0])
        self.local_ref_i = np.array([1.0, 0.0, 0.0])
        self.local_ref_j = np.array([1.0, 0.0, 0.0])
        
    def bind_kinematics(self, rframes_list, axis_choice='Z'):
        """ Extracts the exact local attachment vectors from the global Reference Frames. """
        rf_i = next((rf for rf in rframes_list if rf.name == self.rf_i_name), None)
        rf_j = next((rf for rf in rframes_list if rf.name == self.rf_j_name), None)

        if rf_i:
            self.local_pos_i = self.body_i.principal_axes.T @ (rf_i.position - self.body_i.cog)
            
        if rf_j:
            self.local_pos_j = self.body_j.principal_axes.T @ (rf_j.position - self.body_j.cog)
        elif rf_i:
            # --- THE NVH BEARING UPGRADE ---
            # If Body J has no RF, project RF_I's exact global position into Body J's local coordinate system!
            # This forces the two bodies to share a coincident physical anchor point.
            self.local_pos_j = self.body_j.principal_axes.T @ (rf_i.position - self.body_j.cog)

        # --- Smart Axis Determination ---
        g_axis = np.array([0.0, 0.0, 1.0]) # Failsafe default
        
        if rf_i:
            # 1. If Body J has a valid RF, use the Point-to-Point vector!
            if rf_j and self.rf_j_name.strip() != "":
                vec = rf_j.position - rf_i.position
                mag = np.linalg.norm(vec)
                if mag > 1e-6:
                    g_axis = vec / mag
                else:
                    g_axis = rf_i.transform_matrix[:, 2] # Failsafe if points overlap
            
            # 2. Otherwise, ignore J and use the Combobox axis choice
            else:
                if axis_choice == 'X':
                    g_axis = rf_i.transform_matrix[:, 0]
                elif axis_choice == 'Y':
                    g_axis = rf_i.transform_matrix[:, 1]
                else:
                    g_axis = rf_i.transform_matrix[:, 2]

            # Generate an orthogonal reference vector for twist measurement (the 0-degree mark)
            temp_vec = np.array([1.0, 0.0, 0.0]) if abs(g_axis[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
            g_ref_i = np.cross(g_axis, temp_vec)
            g_ref_i = g_ref_i / np.linalg.norm(g_ref_i)

            # Store inside Body I's local memory
            self.local_axis_i = self.body_i.principal_axes.T @ g_axis
            self.local_ref_i = self.body_i.principal_axes.T @ g_ref_i

        if rf_j:
            # We need a reference vector on Body J to measure twist against Body I.
            # We use RF_J's X-axis. If it happens to be perfectly aligned with the twist axis, use Y.
            g_ref_j = rf_j.transform_matrix[:, 0]
            if abs(np.dot(g_ref_j, g_axis)) > 0.99:
                g_ref_j = rf_j.transform_matrix[:, 1]
                
            self.local_ref_j = self.body_j.principal_axes.T @ g_ref_j
        elif rf_i:
            # --- THE NVH BEARING UPGRADE ---
            # If Body J has no RF, project RF_I's reference vector into Body J's local space.
            # This ensures the rotational twist angle starts perfectly at 0.0!
            self.local_ref_j = self.body_j.principal_axes.T @ g_ref_i
            
    def set_selected(self, is_selected):
        """ Toggles the visual 'glow' selection state of the Spring. """
        for act in self.actors:
            if is_selected:
                act.prop.color = 'gold'
                act.prop.lighting = False # Neon glow effect
            else:
                act.prop.color = getattr(self, 'native_color', 'blue') 
                act.prop.lighting = True  # Restore normal 3D shading
                
        # --- THE FIX: Removed Body Opacity overwrites! ---
        # We let main.py handle the body ghosting using its native 
        # update_selection_visuals and clear_selection methods instead.

class CompressionSpring(BaseSpring):
    """ Translational spring-damper between two Reference Frames. """
    def __init__(self, name, body_i, rf_i_name, body_j, rf_j_name, plotter):
        super().__init__(name, body_i, rf_i_name, body_j, rf_j_name, plotter)
        
        self.stiffness = 0.0
        self.damping = 0.0
        self.preload = 0.0
        self.initial_length = 0.0 
        
        # --- Visual Parameters (Multipliers of the global UI scale) ---
        self.visual_coils = 8        # Modifies the number of coils
        self.visual_radius = 0.2        # Modifies the overall coil width
        self.visual_wire_thickness = 0.03 # Modifies the wire thickness
        
        self.native_color = 'blue'
        self.create_visuals()
         
    def create_visuals(self):
        """ Generates a placeholder Blue 3D Helical Coil """
        # We can leave this as a basic dummy shape because update_transform 
        # instantly overwrites it with the perfectly proportioned version anyway!
        coils = self.visual_coils
        t = np.linspace(0, coils * 2 * np.pi, 150)
        x = self.visual_radius * np.cos(t)
        y = self.visual_radius * np.sin(t)
        z = np.linspace(0, 1.0, 150) 
        
        points = np.column_stack((x, y, z))
        spline = pv.Spline(points, 150)
        tube = spline.tube(radius=self.visual_wire_thickness) 
        
        actor = self.plotter.add_mesh(tube, color='blue', smooth_shading=True)
        actor.SetVisibility(False)
        self.actors.append(actor)

    def update_transform(self, scale_factor=10.0):
        """ Dynamically rebuilds the coil to preserve perfectly circular wire, then rotates it. """
        if not self.visible or not self.enabled:
            for act in self.actors: act.SetVisibility(False)
            return

        # 1. Get global points
        A_i, A_j = self.body_i.principal_axes, self.body_j.principal_axes
        p_i = self.body_i.cog + A_i @ self.local_pos_i
        p_j = self.body_j.cog + A_j @ self.local_pos_j
        
        vec = p_j - p_i
        length = np.linalg.norm(vec)
        if length < 1e-6: return
        
        # --- THE FIX: Read from the new class properties! ---
        length_mm = length * 1000.0
        r_scale = scale_factor * self.visual_radius 
        
        t = np.linspace(0, self.visual_coils * 2 * np.pi, 150)
        x = r_scale * np.cos(t)
        y = r_scale * np.sin(t)
        z = np.linspace(0, length_mm, 150) 
        
        points = np.column_stack((x, y, z))
        spline = pv.Spline(points, 150)
        
        wire_thickness = scale_factor * self.visual_wire_thickness 
        tube = spline.tube(radius=wire_thickness)
        
        if self.actors:
            self.actors[0].mapper.dataset.shallow_copy(tube)
        # ----------------------------------------------------------------------------

        dir_v = vec / length
        v1 = np.array([0.0, 0.0, 1.0]) 
        
        # 2. Rotation Math
        v_cross = np.cross(v1, dir_v)
        c = np.dot(v1, dir_v)
        if c < -0.9999:
            # --- THE FIX: 180-degree rotation around the X-axis flips Z to -Z ---
            R = np.array([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])
        else:
            skew_v = np.array([[0, -v_cross[2], v_cross[1]],
                               [v_cross[2], 0, -v_cross[0]],
                               [-v_cross[1], v_cross[0], 0]])
            R = np.eye(3) + skew_v + (skew_v @ skew_v) * (1 / (1 + c))
            
        # 3. Apply 4x4 Matrix (ONLY Rotation & Translation! No Scaling!)
        mat = np.eye(4)
        mat[:3, :3] = R 
        mat[:3, 3] = p_i * 1000.0 # Convert meters to PyVista mm!
        
        for act in self.actors:
            act.user_matrix = mat
            act.SetVisibility(True)


class TorsionSpring(BaseSpring):
    """ Rotational spring-damper around a specific axis. """
    def __init__(self, name, body_i, rf_i_name, body_j, rf_j_name, axis_choice, plotter):
        super().__init__(name, body_i, rf_i_name, body_j, rf_j_name, plotter)
        
        self.axis_choice = axis_choice 
        self.stiffness = 0.0
        self.damping = 0.0
        self.preload = 0.0
        self.initial_angle = 0.0
        
        # --- Visual Parameters (Multipliers of the global UI scale) ---
        self.visual_coils = 3
        self.visual_inner_radius = 0.2    # Size of the center hole
        self.visual_outer_radius = 1.0    # Overall outer size of the spiral!
        self.visual_wire_thickness = 0.03 # Thickness of the red wire
        
        self.native_color = 'red'
        self.create_visuals()
        
    def create_visuals(self):
        """ Generates a placeholder Red Flat Archimedean Spiral """
        coils = self.visual_coils
        theta = np.linspace(0, coils * 2 * np.pi, 150)
        r = np.linspace(self.visual_inner_radius, self.visual_outer_radius, 150) 
        
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = np.zeros_like(theta)
        
        points = np.column_stack((x, y, z))
        spline = pv.Spline(points, 150)
        tube = spline.tube(radius=self.visual_wire_thickness)
        
        actor = self.plotter.add_mesh(tube, color='red', smooth_shading=True)
        actor.SetVisibility(False)
        self.actors.append(actor)

    def update_transform(self, scale_factor=10.0):
        """ Dynamically rebuilds the spiral to show winding/unwinding, then rotates it. """
        if not self.visible or not self.enabled:
            for act in self.actors: act.SetVisibility(False)
            return
            
        A_i, A_j = self.body_i.principal_axes, self.body_j.principal_axes
        p_i = self.body_i.cog + A_i @ self.local_pos_i
        axis_glob = A_i @ self.local_axis_i 
        
        # --- 1. Calculate dynamic twist angle (delta_theta) ---
        ref_i_glob = A_i @ self.local_ref_i
        ref_j_glob = A_j @ self.local_ref_j
        
        y_axis = np.cross(axis_glob, ref_i_glob)
        proj_j = ref_j_glob - np.dot(ref_j_glob, axis_glob) * axis_glob
        if np.linalg.norm(proj_j) > 1e-8: proj_j /= np.linalg.norm(proj_j)
        
        cos_th = np.dot(ref_i_glob, proj_j)
        sin_th = np.dot(y_axis, proj_j)
        current_angle = np.arctan2(sin_th, cos_th)
        
        delta_theta = current_angle - self.initial_angle
        if delta_theta > np.pi: delta_theta -= 2 * np.pi
        elif delta_theta < -np.pi: delta_theta += 2 * np.pi
        
        # --- 2. Rebuild the Spiral with the added twist! ---
        r_scale = scale_factor * 0.5 
        
        # Add the twist angle to the total coils (prevent it from completely collapsing past 0)
        total_angle = max(0.1, (self.visual_coils * 2 * np.pi) + delta_theta)
        
        theta = np.linspace(0, total_angle, 150)
        r = np.linspace(self.visual_inner_radius * r_scale, self.visual_outer_radius * r_scale, 150)
        
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = np.zeros_like(theta) 
        
        points = np.column_stack((x, y, z))
        spline = pv.Spline(points, 150)
        
        wire_thickness = scale_factor * self.visual_wire_thickness
        tube = spline.tube(radius=wire_thickness)
        
        if self.actors:
            self.actors[0].mapper.dataset.shallow_copy(tube)
        # ----------------------------------------------------------------------------
        
        # --- 3. Rotation Math ---
        v1 = np.array([0.0, 0.0, 1.0]) 
        dir_v = axis_glob / np.linalg.norm(axis_glob)
        
        v_cross = np.cross(v1, dir_v)
        c = np.dot(v1, dir_v)
        if c < -0.9999:
            # --- THE FIX: 180-degree rotation around the X-axis flips Z to -Z ---
            R = np.array([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])
        else:
            skew_v = np.array([[0, -v_cross[2], v_cross[1]],
                               [v_cross[2], 0, -v_cross[0]],
                               [-v_cross[1], v_cross[0], 0]])
            R = np.eye(3) + skew_v + (skew_v @ skew_v) * (1 / (1 + c))
            
        # --- 4. Apply 4x4 Matrix ---
        mat = np.eye(4)
        mat[:3, :3] = R 
        mat[:3, 3] = p_i * 1000.0 
        
        for act in self.actors:
            act.user_matrix = mat
            act.SetVisibility(True)
            
class Bushing(BaseSpring):
    """ 6-DOF Compliant Spring-Damper (Bushing) between two Reference Frames. """
    def __init__(self, name, body_i, rf_i_name, body_j, rf_j_name, plotter):
        super().__init__(name, body_i, rf_i_name, body_j, rf_j_name, plotter)
        
        # Mathematical limits (Stored strictly in SI units!)
        # Trans: N/m, N/(m/s), N
        self.k_trans = np.zeros(3)
        self.c_trans = np.zeros(3)
        self.p_trans = np.zeros(3)
        
        # Rot: Nm/rad, Nm/(rad/s), Nm
        self.k_rot = np.zeros(3)
        self.c_rot = np.zeros(3)
        self.p_rot = np.zeros(3)
        
        # Phase 2 prep: Will store the initial baseline geometry at t=0
        self.initial_local_pos_j = np.zeros(3)
        self.initial_rel_rot = np.eye(3)
        
        # Visual Parameters
        self.native_color = 'purple'
        self.visual_radius = 0.6
        self.visual_length = 0.4
        
        self.create_visuals()

    def create_visuals(self):
        """ Generates a placeholder Purple Cylinder (Rubber Puck) """
        cylinder = pv.Cylinder(radius=self.visual_radius, height=self.visual_length, direction=(0,0,1), resolution=36)
        actor = self.plotter.add_mesh(cylinder, color=self.native_color, smooth_shading=True)
        actor.SetVisibility(False)
        self.actors.append(actor)

    def update_transform(self, scale_factor=10.0):
        """ Anchors the visual bushing puck to Body I's Reference Frame. """
        if not self.visible or not self.enabled:
            for act in self.actors: act.SetVisibility(False)
            return
            
        A_i = self.body_i.principal_axes
        p_i = self.body_i.cog + A_i @ self.local_pos_i
        
        # We align the cylinder to the primary axis (Z) of RF_I
        axis_glob = A_i @ self.local_axis_i 
        
        v1 = np.array([0.0, 0.0, 1.0])
        dir_v = axis_glob / np.linalg.norm(axis_glob)
        
        v_cross = np.cross(v1, dir_v)
        c = np.dot(v1, dir_v)
        if c < -0.9999:
            # --- THE FIX: 180-degree rotation around the X-axis flips Z to -Z ---
            R = np.array([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])
        else:
            skew_v = np.array([[0, -v_cross[2], v_cross[1]],
                               [v_cross[2], 0, -v_cross[0]],
                               [-v_cross[1], v_cross[0], 0]])
            R = np.eye(3) + skew_v + (skew_v @ skew_v) * (1 / (1 + c))
        
        # ==========================================
        # --- Increase Size comparing to the RF arrows size!---
        # ==========================================
        visual_scale = scale_factor * 1 
            
        mat = np.eye(4)
        r_scale = visual_scale * self.visual_radius 
        h_scale = visual_scale * self.visual_length
        scale_mat = np.diag([r_scale, r_scale, h_scale])
        
        mat[:3, :3] = R @ scale_mat
        mat[:3, 3] = p_i * 1000.0 
        
        for act in self.actors:
            act.user_matrix = mat
            act.SetVisibility(True)            
            
    def bind_kinematics(self, rframes_list):
        """ 
        Strict 6-DOF Kinematics: The Bushing's X, Y, and Z axes are perfectly 
        locked to RF_I's orientation. Point-to-Point aiming is completely ignored.
        NEW: We save how RF_I is rotated relative to Body I.
        """
        rf_i = next((rf for rf in rframes_list if rf.name == self.rf_i_name), None)
        rf_j = next((rf for rf in rframes_list if rf.name == self.rf_j_name), None)

        if rf_i:
            self.local_pos_i = self.body_i.principal_axes.T @ (rf_i.position - self.body_i.cog)
            
            # --- THE UPGRADE: Save RF_I's exact local rotation matrix! ---
            self.local_rot_i = self.body_i.principal_axes.T @ rf_i.transform_matrix
            
            g_axis = rf_i.transform_matrix[:, 2] 
            self.local_axis_i = self.body_i.principal_axes.T @ g_axis

        if rf_j:
            self.local_pos_j = self.body_j.principal_axes.T @ (rf_j.position - self.body_j.cog)
        elif rf_i:
            self.local_pos_j = self.body_j.principal_axes.T @ (rf_i.position - self.body_j.cog)       