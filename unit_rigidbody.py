# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.09.0
#  Module: unit_rigidbody.py
#  Description:
#      Computes and stores the exact physical properties of mechanical parts, including mass, 
#      center of gravity, and the principal inertia tensor derived from 3D CAD meshes.
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
from scipy.spatial.transform import Rotation
import math3d 

MMtoM = 1000.0
DEFAULT_DENSITY = 7850.0  # Default density in kg/m^3 (Steel)

class RigidBody:
    """ Python port of TRigidBody from Unit_RigidBody.pas """
    def __init__(self, name, raw_geom, block_mesh, actor, tree_item, density=DEFAULT_DENSITY, is_ground=False):
        self.name = name
        self.enabled = True
        self.visible = True
        self.is_ground = is_ground      # <--- Flag to lock this body in space
        self.base_color = "slategray"  
        self.show_edges = False         
        self.mesh = block_mesh
        self.actor = actor
        self.tree_item = tree_item
        
        self.raw_geom = raw_geom 
        self.density = density if not is_ground else 0.0 # Ground has 0 density
        
        # Default physical properties (Perfect for the Ground body)
        self.volume = 0.0
        self.mass = 0.0
        self.cog = np.zeros(3)
        self.inertia_tensor = np.eye(3)
        self.principal_inertia = np.zeros(3)
        self.principal_axes = np.eye(3) # Identity Matrix (No rotation)
        self.pos_angles = np.zeros(3) 
        
        # --- Kinematic Velocity States ---
        # 1. Store the user-defined initial states (Used for resets and saving)
        self.initial_velocity = np.zeros(3)         # [vx, vy, vz] in m/s (Global)
        self.initial_angular_velocity = np.zeros(3) # [wx, wy, wz] in rad/s (Local)
        
        # 2. Store the current dynamic states (Used by the solver and PyVista)
        self.velocity = np.zeros(3)         # [vx, vy, vz] in m/s
        self.angular_velocity = np.zeros(3) # [wx, wy, wz] in rad/s --- Represents the LOCAL angular velocity
            
        self.I_check = np.eye(3)
        self.math_error = 0.0
        
        # Only calculate physics if it is a real CAD mesh
        if not self.is_ground:
            self.calculate_mass_properties()

    def calculate_mass_properties(self):
        try:
            physics_mesh = self.raw_geom.copy()
            physics_mesh.apply_scale(1.0 / MMtoM) 
            physics_mesh.density = self.density
            
            self.volume = physics_mesh.volume             
            self.mass = physics_mesh.mass                 
            self.cog = physics_mesh.center_mass           
            
            if abs(self.volume) > 1e-12:
                self.inertia_tensor = physics_mesh.moment_inertia 
                
                components, transform = math3d.calculate_principal_axes(self.inertia_tensor)
                self.principal_inertia = components
                self.principal_axes = transform
                
                I_p_matrix = np.diag(self.principal_inertia)
                self.I_check = self.principal_axes @ I_p_matrix @ self.principal_axes.T
                self.math_error = np.max(np.abs(self.inertia_tensor - self.I_check))
                
                # --- THE FIX: Yaw-Pitch-Roll formulation (Extrinsic XYZ) ---
                r = Rotation.from_matrix(self.principal_axes)
                euler_xyz = r.as_euler('xyz', degrees=True) 
                
                # Assign based on the logic: 0=Z(Yaw), 1=Y(Pitch), 2=X(Roll)
                self.pos_angles = np.array([euler_xyz[2], euler_xyz[1], euler_xyz[0]]) 
            else:
                print(f"Note: '{self.name}' has negligible volume. Defaulting inertia to zero.")
            
            #if not np.any(np.isnan(self.cog)):
            #    self.actor.origin = self.cog * MMtoM 
                
        except Exception as e:
            print(f"Warning: Physics math bypassed for '{self.name}': {e}")
    
    def update_density(self, new_density):
        """ 
        Safely updates the mass and inertia using a strict linear scaling ratio!
        This avoids recalculating Trimesh volume integrals and perfectly preserves 
        the original CAD inertia tensors even after saving and loading.
        """
        if self.is_ground or not self.raw_geom:
            return
            
        if self.density <= 0.0 or new_density <= 0.0:
            print(f"Protection: Density must be strictly positive for '{self.name}'.")
            return
            
        try:
            # 1. Calculate the linear scaling multiplier
            ratio = new_density / self.density
            
            # 2. Scale the core properties
            self.density = new_density
            self.mass = self.mass * ratio                 
            
            if abs(self.volume) > 1e-12:
                # 3. Instantly scale local matrices and vectors perfectly
                self.inertia_tensor = self.inertia_tensor * ratio
                self.principal_inertia = self.principal_inertia * ratio
                
                # --- THE FIX: Recalculate I_check with the CURRENT spatial orientation! ---
                I_p_matrix = np.diag(self.principal_inertia)
                self.I_check = self.principal_axes @ I_p_matrix @ self.principal_axes.T
                
        except Exception as e:
            print(f"Warning: Failed to update density for '{self.name}': {e}")
            
    def center_and_align_mesh(self):
        """ 
        Step 1 of Direct Matrix Animation: 
        Counter-translates and Counter-rotates the raw PyVista mesh so its internal 
        (0,0,0) origin is the physical CoG, and its axes align with the Principal Axes.
        """
        if self.is_ground or not self.mesh:
            return

        # A. Counter-Translate: Move physical CoG to (0,0,0)
        # The PyVista mesh is natively in mm. self.cog is in meters.
        shift_mm = -self.cog * MMtoM 
        self.mesh.translate(shift_mm, inplace=True)

        # B. Counter-Rotate: Twist the mesh to align with the Principal Axes
        # We multiply the mesh vertices by the Transpose (Inverse) of the Principal matrix
        inv_rot = self.principal_axes.T
        
        inv_4x4 = np.eye(4)
        inv_4x4[:3, :3] = inv_rot
        self.mesh.transform(inv_4x4, inplace=True)
        
        # C. Map it immediately back to the global starting position!
        self.update_graphics_matrix(self.cog, self.principal_axes)
        
        # --- Generate the Local Bounding Box for Collision Detection ---
        self.generate_local_aabb()

    def update_graphics_matrix(self, pos_m, rot_3x3):
        """ 
        Step 2 of Direct Matrix Animation: 
        Pushes the exact solver 4x4 matrix directly to the Graphics Card for instant rendering.
        """
        if self.is_ground or not self.actor:
            return
            
        # Construct the 4x4 Homogeneous Matrix
        gpu_matrix = np.eye(4)
        gpu_matrix[:3, :3] = rot_3x3
        gpu_matrix[:3, 3] = pos_m * MMtoM # Convert solver meters -> Viewport mm
        
        # Instantly move/rotate the body on screen
        self.actor.user_matrix = gpu_matrix        
        
    def generate_local_aabb(self):
        """ Extracts the 8 corners of the bounding box strictly from the centered local mesh. """
        if self.is_ground or not self.mesh: return
        
        # The PyVista mesh is natively in mm. We must convert to Physics Meters.
        bounds = self.mesh.bounds # (xmin, xmax, ymin, ymax, zmin, zmax)
        
        xmin, xmax = bounds[0] / MMtoM, bounds[1] / MMtoM
        ymin, ymax = bounds[2] / MMtoM, bounds[3] / MMtoM
        zmin, zmax = bounds[4] / MMtoM, bounds[5] / MMtoM
        
        # Store the 8 corners of the perfect mathematical box
        self.local_corners = np.array([
            [xmin, ymin, zmin], [xmax, ymin, zmin],
            [xmin, ymax, zmin], [xmax, ymax, zmin],
            [xmin, ymin, zmax], [xmax, ymin, zmax],
            [xmin, ymax, zmax], [xmax, ymax, zmax]
        ])

    def get_global_aabb(self):
        """ Calculates the dynamic Axis-Aligned Bounding Box (AABB) in global space. """
        if self.is_ground or getattr(self, 'local_corners', None) is None:
            return None, None
        
        # Instantly transform the 8 corners using the current physics rotation and CoG
        global_corners = (self.principal_axes @ self.local_corners.T).T + self.cog
        
        # Find the absolute min and max spatial coordinates
        min_xyz = np.min(global_corners, axis=0)
        max_xyz = np.max(global_corners, axis=0)
        
        return min_xyz, max_xyz    
    
    def reset_velocities(self):
        """ Restores the body's dynamic velocity back to the user-defined initial state at t=0. """
        self.velocity = self.initial_velocity.copy()
        self.angular_velocity = self.initial_angular_velocity.copy()