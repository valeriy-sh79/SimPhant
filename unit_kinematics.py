# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.1
#  Release Date: 2026/09/30
#  Module: unit_kinematics.py
#  Description:
#      Defines the local reference frame class (RFrame) used to precisely anchor 
#      joints, forces, and geometric primitives in space.
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
import pyvista as pv

# Conversion constant (matches Delphi)
MMtoM = 1000.0

class RFrame:
    """ 
    Python port of TRFrame from Unit_Kinematics.pas.
    Represents a local Reference Frame used for Joints, Forces, and Sensors.
    """
    def __init__(self, name, position, orientation, transform_matrix, plotter, parent_body=None, is_cog=False):
        self.name = name
        self.position = np.array(position, dtype=float)      # Global Position in meters
        self.orientation = np.array(orientation, dtype=float) # Yaw, Pitch, Roll
        self.transform_matrix = np.array(transform_matrix, dtype=float) # 3x3 Rotation Matrix
        
        self.is_cog = is_cog       # Locks the RF from user modification
        self.visible = True        # User visibility toggle
        self.parent_body = parent_body # The RigidBody this CoG belongs to
        self.plotter = plotter
        
        # 3D Visual Variables
        self.actors = []
        self.base_scale = 1.0 # Will be updated dynamically by the Camera Zoom
        
        self.create_visuals()
        
    def create_visuals(self):
        # We build the arrows centered at (0,0,0) with length 1.0.
        # This allows us to size, rotate, and move them mathematically using a 4x4 matrix.
        arr_x = pv.Arrow(start=(0,0,0), direction=(1,0,0), scale=1.0)
        arr_y = pv.Arrow(start=(0,0,0), direction=(0,1,0), scale=1.0)
        arr_z = pv.Arrow(start=(0,0,0), direction=(0,0,1), scale=1.0)
        
        # Standard rendering without the version-breaking kwargs
        act_x = self.plotter.add_mesh(arr_x, color='red', pickable=False)
        act_y = self.plotter.add_mesh(arr_y, color='green', pickable=False)
        act_z = self.plotter.add_mesh(arr_z, color='blue', pickable=False)
        
        self.actors = [act_x, act_y, act_z]
        self.update_transform()

    def update_transform(self):
        """ Recalculates the exact position, rotation, and size of the axes in the viewport. """
        
        # If this is a CoG frame, it must stay perfectly glued to the physics body!
        if self.is_cog and self.parent_body:
            self.position = self.parent_body.cog
            self.transform_matrix = self.parent_body.principal_axes
            self.orientation = self.parent_body.pos_angles
        
        # Create a 4x4 homogenous transformation matrix for VTK
        mat = np.eye(4)
        
        # Apply the 3x3 rotation and the dynamic camera zoom scale
        mat[:3, :3] = self.transform_matrix * self.base_scale
        
        # Apply the global translation (converted from solver meters to viewport mm!)
        mat[:3, 3] = self.position * MMtoM 
        
        # Push the matrix directly to the GPU
        for act in self.actors:
            act.user_matrix = mat
            act.SetVisibility(self.visible)
            
    def set_scale(self, scale):
        """ Called by the camera event to keep axes exactly 40-50 pixels wide. """
        self.base_scale = scale
        self.update_transform()
        
    def set_visible(self, is_visible):
        self.visible = is_visible
        self.update_transform()
        
    def set_selected(self, is_selected):
        """ Toggles the visual 'glow' selection state of the Reference Frame. """
        default_colors = ['red', 'green', 'blue']
        
        for i, act in enumerate(self.actors):
            if is_selected:
                act.prop.color = 'gold'  # Can be changed to 'black' if it looks better
                act.prop.lighting = False # Turning off lighting creates a "glow" effect
            else:
                act.prop.color = default_colors[i]
                act.prop.lighting = True  # Restore normal 3D shading