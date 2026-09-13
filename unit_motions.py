# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.1
#  Release Date: 2026/09/30
#  Module: unit_motions.py
#  Description:
#      Formulates user-defined kinematic motion drivers (displacement, velocity, acceleration) 
#      that explicitly dictate the movement of joint degrees of freedom.
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
import re
from enum import Enum

class MotionTransRot(Enum):
    TRANSLATIONAL = 0
    ROTATIONAL = 1

class MotionType(Enum):
    DISPLACEMENT = 0
    VELOCITY = 1

# ==========================================
# SAFE MATH COMPILER ENVIRONMENT
# ==========================================
def custom_step(x, x0, h0, x1, h1):
    """ Smooth STEP function (Hermite interpolation). """
    if x <= x0: return float(h0)
    if x >= x1: return float(h1)
    if x1 == x0: return float(h0) 
    u = (x - x0) / (x1 - x0)
    return float(h0 + (h1 - h0) * (u**2) * (3.0 - 2.0 * u))
    
def custom_if(x, e1, e2):
    """ Simplified IF function: (condition, value_if_negative, value_if_positive_or_zero) """
    if x < 0.0: return float(e1)
    else: return float(e2)

SAFE_DICT = {
    "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan,
    "pi": np.pi, "exp": np.exp, "sqrt": np.sqrt, "abs": np.abs,
    "step": custom_step, "STEP": custom_step,
    "IF": custom_if,
    "__builtins__": None 
}

# ==========================================
# THE KINEMATIC MOTION CLASS
# ==========================================
class JointMotion:
    """ 
    Rheonomic Constraint Driver. 
    Parses a user's time-dependent function and calculates velocity and acceleration dynamically.
    """
    def __init__(self, name, joint, trans_rot, motion_type):
        self.name = name
        self.joint = joint
        self.trans_rot = MotionTransRot(trans_rot)  # 0: Translational, 1: Rotational
        self.motion_type = MotionType(motion_type)  # 0: Displacement, 1: Velocity
        
        self.enabled = True
        self.expression_str = "0.0"
        self.compiled_func = lambda t: 0.0

    def compile_expression(self, text):
        """ Compiles a UI text string into a high-speed lambda function. """
        self.expression_str = text.strip()
        if not self.expression_str:
            self.compiled_func = lambda t: 0.0
            return

        try:
            # 1. Replace ALL commas with dots (European decimals -> Python decimals)
            clean_str = self.expression_str.replace(',', '.')
            # 2. Replace ALL semicolons with commas (User argument separator -> Python separator)
            clean_str = clean_str.replace(';', ',')
            # 3. Replace lowercase 'if(' with uppercase 'IF(' case-insensitively
            safe_expr = re.sub(r'\bif\s*\(', 'IF(', clean_str, flags=re.IGNORECASE)
            
            # Compile into a callable lambda function
            self.compiled_func = eval(f"lambda t: {safe_expr}", SAFE_DICT)
            self.compiled_func(0.0) # Test evaluate to catch syntax errors immediately
        except Exception as e:
            print(f"Error compiling motion expression '{self.expression_str}': {e}")
            self.compiled_func = lambda t: 0.0

    def get_kinematics(self, t):
        """
        Uses Central Finite Differences to evaluate f(t), f'(t), and f''(t).
        Automatically handles unit conversion from UI to SI for the solver matrix.
        Returns: (position, velocity, acceleration)
        """
        h = 1e-5 # Time step for CFD (10 microseconds gives extreme precision)
        
        # 1. Evaluate base function at t, t+h, and t-h
        f0 = self.compiled_func(t)
        fp = self.compiled_func(t + h)
        fm = self.compiled_func(t - h)
        
        # 2. Unit Conversion
        # UI Translational is defined in mm -> Solver strictly requires meters.
        # UI Rotational is defined in rad -> Solver requires radians (no change).
        scale = 0.001 if self.trans_rot == MotionTransRot.TRANSLATIONAL else 1.0
        
        f0 *= scale
        fp *= scale
        fm *= scale

        # 3. Central Finite Difference Math
        df = (fp - fm) / (2.0 * h)
        ddf = (fp - 2.0 * f0 + fm) / (h**2)

        # 4. Route data based on user's definition choice
        if self.motion_type == MotionType.DISPLACEMENT:
            # User defined position: Return (Pos, Vel, Acc)
            return f0, df, ddf
        else:
            # User defined velocity: f0 IS the velocity, df IS the acceleration.
            # We return 0.0 for position, which we will handle cleanly in the KKT Baumgarte parameters.
            return 0.0, f0, df