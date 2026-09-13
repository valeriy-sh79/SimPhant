# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.1
#  Release Date: 2026/09/30
#  Module: unit_collision.py
#  Description:
#      Defines the ContactPair class for handling collision interactions between rigid bodies, 
#      including normal and frictional forces using the Hunt-Crossley / Hertzian non-linear penalty model.
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

class ContactPair:
    """ 
    Defines a specific collision interaction between two rigid bodies.
    Uses the Hunt-Crossley / Hertzian non-linear penalty model.
    """
    def __init__(self, name, body_i, body_j, stiffness_ui, exponent, damping_ui, 
                 friction_enabled=False, mu=0.3, slip_tol_ui=10.0, mesh_mode=0):
        self.name = name
        self.body_i = body_i
        self.body_j = body_j
        
        self.exponent = exponent
        
        # ==========================================
        # --- NORMAL FORCE UNIT CONVERSIONS ---
        # ==========================================
        # Stiffness: UI (N/mm^n) -> Solver SI (N/m^n)
        self.stiffness = stiffness_ui * (1000.0 ** self.exponent) 
        
        # Damping: UI (N/(mm/s)) -> Solver SI (N/(m/s))
        self.damping = damping_ui * 1000.0 
        
        # ==========================================
        # --- FRICTION PROPERTIES ---
        # ==========================================
        self.friction_enabled = friction_enabled
        self.mu = mu
        
        # Slip Tolerance: UI (mm/s) -> Solver SI (m/s)
        self.slip_tolerance = slip_tol_ui / 1000.0 
        
        # --- Store the Mesh Simplification Mode ---
        self.mesh_mode = mesh_mode # <--- Changed here (0=Standard, 1=Fine, 2=Decimate, 3=ConvexHull)
        
        # Trackers for the CSV
        self.current_F_spring = 0.0
        self.current_F_damp = 0.0
        self.current_F_total = 0.0
        self.current_F_friction = 0.0 
        
        self.enabled = True
        self.tree_item = None