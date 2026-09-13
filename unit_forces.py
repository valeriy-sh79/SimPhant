# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.1
#  Release Date: 2026/09/30
#  Module: unit_forces.py
#  Description:
#      Defines the Force class and related enumerations for handling various types of forces and torques
#      applied to rigid bodies, including support for time-dependent expressions and 3D visualization.
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

class ForceType(Enum):
    FORCE = 1
    TORQUE = 2
    E_MOTOR = 3    
    ACTUATOR = 4  
class ForceFrame(Enum):
    SPACE_FIXED = 1
    BODY_FIXED = 2

class Force:
    """ Python port of TForce from Unit_Forces.pas """
    def __init__(self, name, force_type, parent_body, fixed_in, position, vector, plotter):
        self.name = name
        self.force_type = force_type
        self.parent_body = parent_body
        self.fixed_in = fixed_in
        
        # Core mathematical vectors (Local to the body, strictly in METERS)
        self.local_position = np.array(position, dtype=float)
        
        # --- THE FIX: base_vector is now strictly a Unit Direction Vector! ---
        vec_array = np.array(vector, dtype=float)
        mag = np.linalg.norm(vec_array)
        self.base_vector = vec_array / mag if mag > 1e-8 else np.array([1.0, 0.0, 0.0])

        self.enabled = True
        self.visible = True
        self.is_gravity = False

        # User-Defined Properties (UI)
        self.direction = 'Y'
        self.magnitude = mag  # Fallback constant magnitude
        
        # --- NEW: Time-Dependent Math Expression Logic ---
        self.magnitude_expr = str(mag)
        self._eval_func = lambda t: self.magnitude
        
        self.speed_max = 0.0  
        self.allow_braking = True  
        self.source_rf_name = ""

        # 3D Visual Variables
        self.plotter = plotter
        self.actors = []  
        self.base_scale = 1.0
        
        self.create_visuals()
        
    def compile_expression(self, expr_str):
        """ Compiles a UI text string into a high-speed lambda function. """
        self.magnitude_expr = expr_str.strip()
        
        # --- THE FIX: Convert UI Nmm to SI Nm for Torques and E-Motors! ---
        scale_factor = 0.001 if self.force_type in [ForceType.TORQUE, ForceType.E_MOTOR] else 1.0

        # --- Custom Math Functions ---
        def custom_step(x, x0, h0, x1, h1):
            if x <= x0: return float(h0)
            if x >= x1: return float(h1)
            if x1 == x0: return float(h0) 
            u = (x - x0) / (x1 - x0)
            return float(h0 + (h1 - h0) * (u**2) * (3.0 - 2.0 * u))
            
        def custom_if(x, e1, e2):
            if x < 0.0: return float(e1)
            else: return float(e2)
        
        # Safe mathematical dictionary
        safe_dict = {
            "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "pi": np.pi, "exp": np.exp, "sqrt": np.sqrt, "abs": np.abs,
            "step": custom_step, "STEP": custom_step, 
            "IF": custom_if,                          
            "__builtins__": None 
        }
        
        try:
            # 1. Try raw flat numerical conversion first
            val = float(self.magnitude_expr.replace(',', '.'))
            
            # --- Scale to SI before saving to memory! ---
            self.magnitude = val * scale_factor
            self.is_constant = True
            self._eval_func = lambda t: self.magnitude
            
        except ValueError:
            # 2. Parse as a dynamic math function
            self.is_constant = False
            self.magnitude = 0.0 # Functions have no fixed magnitude for Peak Power calculations
            try:
                import re
                # 1. Replace ALL commas with dots (European decimals -> Python decimals)
                clean_str = self.magnitude_expr.replace(',', '.')
                # 2. Replace ALL semicolons with commas (User argument separator -> Python separator)
                clean_str = clean_str.replace(';', ',')
                # 3. Replace lowercase 'if(' with uppercase 'IF('
                safe_expr = re.sub(r'\bif\s*\(', 'IF(', clean_str, flags=re.IGNORECASE)
                
                func = eval(f"lambda t: {safe_expr}", safe_dict)
                func(0.0) 
                
                # --- Wrap it to dynamically scale to SI at runtime! ---
                self._eval_func = lambda t: func(t) * scale_factor
                
            except Exception as e:
                print(f"Warning: Invalid math expression '{self.magnitude_expr}' for '{self.name}'. Defaulting to 0.0.")
                self.magnitude = 0.0
                self._eval_func = lambda t: 0.0

    def set_visible(self, is_visible):
        """ Instantly toggles the 3D arrow/torus visibility """
        self.visible = is_visible
        is_shown = self.visible and self.enabled and self.parent_body.visible
        for act in self.actors:
            act.SetVisibility(is_shown)
            
    def set_selected(self, is_selected):
        """ Temporarily overrides the color to Gold when selected in the UI. """
        display_color = "gold" if is_selected else self.base_color
        for act in self.actors:
            act.prop.color = display_color        
            
    # ==========================================
    # --- TRANSLATIONAL SOLVER HELPERS (Global)
    # ==========================================
    def get_global_position(self):
        """ Returns the exact global coordinate of the force application point. """
        global_pos = (self.parent_body.principal_axes @ self.local_position) + self.parent_body.cog
        return global_pos

    def get_global_vector(self, t=0.0):
        """ Returns the directional vector in global space at a specific time t. """
        current_mag = self._eval_func(t)
                
        if self.fixed_in == ForceFrame.SPACE_FIXED:
            return self.base_vector * current_mag 
        else:
            return (self.parent_body.principal_axes @ self.base_vector) * current_mag

    # ==========================================
    # --- ROTATIONAL SOLVER HELPERS (Local)
    # ==========================================
    def get_local_position(self):
        """ The point of application physically exists on the body. """
        return self.local_position.copy()

    def get_local_vector(self, t=0.0):
        """ Returns the directional vector in local body space at a specific time t. """
        current_mag = self._eval_func(t)
                    
        if self.fixed_in == ForceFrame.BODY_FIXED:
            return self.base_vector * current_mag 
        else:
            return (self.parent_body.principal_axes.T @ self.base_vector) * current_mag

    # ==========================================
    # --- ONE-TIME R-FRAME APPLICATION ---
    # ==========================================
    def apply_initial_rframe(self, rframe):
        """ Calculates the initial local vectors based on a Reference Frame. """
        if not rframe: 
            return

        self.source_rf_name = rframe.name

        # 1. Calculate Local Position
        global_pos_vec = rframe.position - self.parent_body.cog  
        self.local_position = self.parent_body.principal_axes.T @ global_pos_vec 

        # 2. Extract the exact Global Axis
        if self.direction == 'X': global_dir = rframe.transform_matrix[:, 0]
        elif self.direction == 'Y': global_dir = rframe.transform_matrix[:, 1]
        elif self.direction == 'Z': global_dir = rframe.transform_matrix[:, 2]
        else: global_dir = np.array([1.0, 0.0, 0.0])

        # 3. Set the Unit Base Vector (NO MAGNITUDE HERE!)
        if self.fixed_in == ForceFrame.SPACE_FIXED:
            self.base_vector = global_dir 
        else:
            self.base_vector = self.parent_body.principal_axes.T @ global_dir 
            
    # ==========================================
    # --- VISUALIZATION
    # ==========================================
    def create_visuals(self):
        # 1. Store the base color permanently
        self.base_color = "limegreen" if self.is_gravity else ("red" if self.force_type in (ForceType.TORQUE, ForceType.E_MOTOR) else "blue")
        
        # 2. Create the Arrow
        arrow = pv.Arrow(start=(0,0,0), direction=(1,0,0), scale=1.0)
        act_arrow = self.plotter.add_mesh(arrow, color=self.base_color, pickable=False)
        
        # --- THE FIX: Tell the camera to IGNORE this arrow for bounding boxes! ---
        # act_arrow.SetUseBounds(False)
        self.actors.append(act_arrow)
        
        # 3. Add the Torus for Torques
        if self.force_type in (ForceType.TORQUE, ForceType.E_MOTOR): 
            torus = pv.ParametricTorus(ringradius=0.15, crosssectionradius=0.03)
            torus.rotate_y(90, inplace=True)
            act_torus = self.plotter.add_mesh(torus, color=self.base_color, pickable=False)
            
            # --- THE FIX: Tell the camera to IGNORE this torus for bounding boxes! ---
            # act_torus.SetUseBounds(False)
            self.actors.append(act_torus)
            
        for act in self.actors:
            act.SetVisibility(False)
        
    def update_transform(self, scale_size, t=0.0):
        # --- Store the scale so the object remembers its size! ---
        self.base_scale = scale_size 
        
        if not self.visible or not self.enabled or not self.parent_body.visible:
            for act in self.actors:
                act.SetVisibility(False)
            return
            
        g_pos = self.get_global_position()
        g_vec = self.get_global_vector(t)
        mag = np.linalg.norm(g_vec)
        
        if mag < 1e-6:
            for act in self.actors:
                act.SetVisibility(False)
            return
            
        for act in self.actors:
            act.SetVisibility(True)
        
        dir_v = g_vec / mag
        
        # Visual failsafe: Force direction based on mathematical sign!
        if self._eval_func(t) < 0.0:
            dir_v = -dir_v
            
        v1 = np.array([1.0, 0.0, 0.0])
        
        v_cross = np.cross(v1, dir_v)
        c = np.dot(v1, dir_v)
        
        if c < -0.9999:
            R = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]])
        else:
            skew_v = np.array([[0, -v_cross[2], v_cross[1]],
                               [v_cross[2], 0, -v_cross[0]],
                               [-v_cross[1], v_cross[0], 0]])
            R = np.eye(3) + skew_v + (skew_v @ skew_v) * (1 / (1 + c))
            
        # ==========================================
        # --- Increase Size by 50% comparing to the RF arrows size!---
        # ==========================================
        visual_scale = scale_size * 2.5 
            
        mat = np.eye(4)
        mat[:3, :3] = R * visual_scale 
        mat[:3, 3] = g_pos * MMtoM   
        
        for act in self.actors:
            act.user_matrix = mat