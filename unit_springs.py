# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.10.2
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

import re
from dataclasses import dataclass

import numpy as np
import pyvista as pv
from scipy.spatial.transform import Rotation

# ==========================================
# SAFE MATH COMPILER ENVIRONMENT (shared with Force / JointMotion expressions)
# ==========================================
def _custom_step(x, x0, h0, x1, h1):
    """ Smooth STEP function (Hermite interpolation). """
    if x <= x0: return float(h0)
    if x >= x1: return float(h1)
    if x1 == x0: return float(h0)
    u = (x - x0) / (x1 - x0)
    return float(h0 + (h1 - h0) * (u**2) * (3.0 - 2.0 * u))

def _custom_if(x, e1, e2):
    """ Simplified IF function: (condition, value_if_negative, value_if_positive_or_zero) """
    if x < 0.0: return float(e1)
    else: return float(e2)

_SPRING_SAFE_DICT = {
    "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan,
    "pi": np.pi, "exp": np.exp, "sqrt": np.sqrt, "abs": np.abs,
    "step": _custom_step, "STEP": _custom_step,
    "IF": _custom_if,
    "__builtins__": None
}

def compile_two_arg_expression(expr_str, arg1, arg2):
    """ Compiles 'expr_str' into f(arg1, arg2). Returns (callable, ok); on failure the callable returns 0.0. """
    zero = lambda a, b: 0.0
    expr_str = expr_str.strip()
    if not expr_str:
        return zero, True

    try:
        val = float(expr_str.replace(',', '.'))
        return (lambda a, b: val), True
    except ValueError:
        pass

    try:
        clean_str = expr_str.replace(',', '.').replace(';', ',')
        safe_expr = re.sub(r'\bif\s*\(', 'IF(', clean_str, flags=re.IGNORECASE)
        func = eval(f"lambda {arg1}, {arg2}: {safe_expr}", _SPRING_SAFE_DICT)
        func(0.0, 0.0)  # Test evaluate to catch syntax errors immediately
        return func, True
    except Exception:
        return zero, False

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
        
        # --- Non-Linear Force Characteristic F(x, v) ---
        self.is_nonlinear = False
        self.nonlinear_expr = "0"
        self._nonlinear_func = lambda x, v: 0.0
        
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

    def compile_nonlinear_force(self, expr_str):
        """ Compiles the user's F(x, v) text into a callable. x in mm, v in mm/s, returns N.
        Follows F_spring = F_preload - F(x, v): to replicate a linear K/C spring use
        F(x, v) = -K*x - C*v (same sign convention as the documented spring force law). """
        self.nonlinear_expr = expr_str.strip()
        func, ok = compile_two_arg_expression(self.nonlinear_expr, "x", "v")
        if not ok:
            print(f"Warning: Invalid non-linear spring expression '{self.nonlinear_expr}' for '{self.name}'")
        self._nonlinear_func = func
        return ok

    def evaluate_nonlinear_force(self, delta_L, L_dot):
        """ Evaluates F(x, v) with x/v converted from SI (m, m/s) to UI units (mm, mm/s).
        Returns F(x, v) as defined by the user (expansion-positive, per F_spring = F_preload - F(x, v)). """
        try:
            return float(self._nonlinear_func(delta_L * 1000.0, L_dot * 1000.0))
        except Exception:
            return 0.0

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
        
        # --- Non-Linear Torque Characteristic T(theta, omega) ---
        self.is_nonlinear = False
        self.nonlinear_expr = "0"
        self._nonlinear_func = lambda theta, omega: 0.0
        
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

    def compile_nonlinear_torque(self, expr_str):
        """ Compiles the user's T(theta, omega) text. theta in rad, omega in rad/s, returns Nmm.
        Follows T_spring = T_preload - T(theta, omega): a linear K/C spring is T = -K*theta - C*omega. """
        self.nonlinear_expr = expr_str.strip()
        func, ok = compile_two_arg_expression(self.nonlinear_expr, "theta", "omega")
        if not ok:
            print(f"Warning: Invalid non-linear spring expression '{self.nonlinear_expr}' for '{self.name}'")
        self._nonlinear_func = func
        return ok

    def evaluate_nonlinear_torque(self, delta_theta, theta_dot):
        """ Evaluates T(theta, omega) in SI (rad, rad/s) and returns Nm (the user expression is in Nmm). """
        try:
            return float(self._nonlinear_func(delta_theta, theta_dot)) / 1000.0
        except Exception:
            return 0.0

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
            
def _rotation_vector(R):
    """ Rotation vector (axis * angle, rad) of a 3x3 rotation matrix. Closed form, accurate for small angles. """
    v = 0.5 * np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])   # sin(angle) * axis
    s = np.linalg.norm(v)
    c = 0.5 * (np.trace(R) - 1.0)                                                  # cos(angle)
    if s < 1e-12:
        return v if c > 0.0 else Rotation.from_matrix(R).as_rotvec()
    if c > -0.999:
        return v * (np.arctan2(s, c) / s)
    return Rotation.from_matrix(R).as_rotvec()    # Close to 180 deg the closed form loses the axis


@dataclass
class BushingState:
    """ Instantaneous bushing kinematics and loads. All SI. 'loc' = components along the RF_I axes. """
    u: np.ndarray        # Translational deformation of the J anchor relative to RF_I (loc)
    phi: np.ndarray      # Rotational deformation: rotation vector of the J anchor relative to RF_I (loc)
    u_dot: np.ndarray    # Rate of u (loc)
    w_rel: np.ndarray    # Angular velocity of Body J relative to RF_I (loc)
    F_loc: np.ndarray    # Bushing force acting on Body J (loc)
    T_loc: np.ndarray    # Bushing torque acting on Body J (loc)
    F_i: np.ndarray      # Generalized load on Body I: global force ...
    M_i: np.ndarray      # ... and torque about its CoG in its principal (local) axes
    F_j: np.ndarray      # Generalized load on Body J: global force ...
    M_j: np.ndarray      # ... and torque about its CoG in its principal (local) axes


class Bushing(BaseSpring):
    """ 6-DOF Compliant Spring-Damper (Bushing) between two Reference Frames.

    RF_I defines the bushing frame: the axes along which stiffness, damping and preload act. The frame is
    fixed to Body I, so it moves and rotates with it. RF_J only defines the anchor of Body J (position and
    orientation); when it is empty the anchor coincides with RF_I. The bushing is force-free (apart from
    the preload) in the pose of the model at t=0: deformations are measured from that pose. """
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
        
        # Orientation of RF_I / the J anchor expressed in the principal axes of Body I / Body J
        self.local_rot_i = np.eye(3)
        self.local_rot_j = np.eye(3)
        
        # Pose of the J anchor relative to RF_I at t=0 (the force-free reference), see capture_baseline()
        self.ref_pos = np.zeros(3)
        self.ref_rot = np.eye(3)
        
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
        locked to RF_I's orientation (fixed to Body I). Point-to-Point aiming is ignored.
        RF_I gives the anchor and frame on Body I, RF_J the anchor on Body J. If RF_J is empty,
        the anchor on Body J is placed at the exact position and orientation of RF_I.
        """
        rf_i = next((rf for rf in rframes_list if rf.name == self.rf_i_name), None)
        rf_j = next((rf for rf in rframes_list if rf.name == self.rf_j_name), None)
        A_i, A_j = self.body_i.principal_axes, self.body_j.principal_axes

        if rf_i:
            self.local_pos_i = A_i.T @ (rf_i.position - self.body_i.cog)
            self.local_rot_i = A_i.T @ rf_i.transform_matrix
            self.local_axis_i = A_i.T @ rf_i.transform_matrix[:, 2]

        anchor_j = rf_j if rf_j else rf_i
        if anchor_j:
            self.local_pos_j = A_j.T @ (anchor_j.position - self.body_j.cog)
            self.local_rot_j = A_j.T @ anchor_j.transform_matrix

    def restore_local_rot_j(self, rframes_list):
        """ Project files saved before the J anchor orientation existed: rebuild it from RF_J (or from RF_I). """
        rf_j = next((rf for rf in rframes_list if rf.name == self.rf_j_name), None)
        A_j = self.body_j.principal_axes
        if rf_j:
            self.local_rot_j = A_j.T @ rf_j.transform_matrix
        else:
            self.local_rot_j = A_j.T @ (self.body_i.principal_axes @ self.local_rot_i)

    def capture_baseline(self):
        """ Stores the pose of the J anchor relative to RF_I in the current (t=0) configuration. """
        A_i, A_j = self.body_i.principal_axes, self.body_j.principal_axes
        E = A_i @ self.local_rot_i
        p_i = self.body_i.cog + A_i @ self.local_pos_i
        p_j = self.body_j.cog + A_j @ self.local_pos_j
        self.ref_pos = E.T @ (p_j - p_i)
        self.ref_rot = E.T @ A_j

    def evaluate(self):
        """ Single source of truth for the bushing physics: deformation, rates, wrench and the loads on both bodies.

        Deformation = pose of the J anchor measured in the (moving) RF_I frame, relative to t=0. The force F
        and torque T act on Body J (F at its anchor); Body I receives the reaction (-F at its anchor, -T) plus
        the couple -d x F, with d the vector between the anchors, so the pair is a pure internal action:
        linear and angular momentum are conserved and the stiffness terms derive from a potential. """
        bi, bj = self.body_i, self.body_j
        A_i, A_j = bi.principal_axes, bj.principal_axes
        E = A_i @ self.local_rot_i                  # RF_I axes in the global frame

        r_i = A_i @ self.local_pos_i                # CoG -> anchor, global
        r_j = A_j @ self.local_pos_j
        d = (bj.cog + r_j) - (bi.cog + r_i)         # Anchor I -> anchor J, global

        w_i = A_i @ bi.angular_velocity             # Angular velocities are stored in the local axes of each body
        w_j = A_j @ bj.angular_velocity
        v_pi = bi.velocity + np.cross(w_i, r_i)
        v_pj = bj.velocity + np.cross(w_j, r_j)

        # RF_I rotates with Body I, so the rate of d seen from RF_I excludes the frame rotation (w_i x d)
        u = E.T @ d - self.ref_pos
        u_dot = E.T @ (v_pj - v_pi - np.cross(w_i, d))
        phi = _rotation_vector(E.T @ A_j @ self.ref_rot.T)
        w_rel = E.T @ (w_j - w_i)

        F_loc = self.p_trans - self.k_trans * u - self.c_trans * u_dot
        T_loc = self.p_rot - self.k_rot * phi - self.c_rot * w_rel
        F_g = E @ F_loc
        T_g = E @ T_loc

        return BushingState(
            u=u, phi=phi, u_dot=u_dot, w_rel=w_rel, F_loc=F_loc, T_loc=T_loc,
            F_i=-F_g, M_i=A_i.T @ (np.cross(r_i, -F_g) - T_g - np.cross(d, F_g)),
            F_j=F_g, M_j=A_j.T @ (np.cross(r_j, F_g) + T_g),
        )