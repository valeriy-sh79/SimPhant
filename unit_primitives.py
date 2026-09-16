# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.09.0
#  Module: unit_primitives.py
#  Description:
#      Contains procedural mesh generators for creating standard parameterized geometric shapes
#      like boxes, cylinders, spheres, and structural links.
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
import trimesh

class PrimitiveGenerator:
    """ 
    Procedural generator for standard 3D CAD primitives. 
    All meshes are natively centered at their volumetric Center of Mass (0,0,0) 
    and returned as strictly watertight trimesh.Trimesh objects.
    """
    
    @staticmethod
    def _revolve_profile(profile_rz, N_radial=48):
        """ 
        A universal Surface of Revolution engine. 
        Takes a 2D profile (Radius, Z-Height) and spins it 360 degrees into a watertight 3D shell. 
        """
        vertices = []
        angles = np.linspace(0, 2 * np.pi, N_radial, endpoint=False)
        cos_a = np.cos(angles)
        sin_a = np.sin(angles)

        # 1. Spin the vertices
        for r, z in profile_rz:
            for c, s in zip(cos_a, sin_a):
                vertices.append([r * c, r * s, z])

        vertices = np.array(vertices)
        faces = []
        M = len(profile_rz)

        # 2. Stitch the geometry faces together
        for i in range(M - 1):
            row1 = i * N_radial
            row2 = (i + 1) * N_radial
            for j in range(N_radial):
                j_next = (j + 1) % N_radial
                v0 = row1 + j
                v1 = row1 + j_next
                v2 = row2 + j_next
                v3 = row2 + j
                
                faces.append([v0, v1, v2])
                faces.append([v0, v2, v3])

        # 3. Trimesh 'process=True' acts as a magic cleanup tool!
        # It automatically merges all duplicated vertices at the poles (r=0) 
        # and deletes the flattened, zero-area triangles, perfectly sealing the mesh.
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
        
        # Auto-flip normals outward if the profile traced inside-out
        if mesh.volume < 0.0:
            mesh.faces = np.fliplr(mesh.faces)
            mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces, process=True)

        return mesh

    @staticmethod
    def generate_box(length_x, width_y, height_z):
        # Failsafe clamping to prevent zero-volume crashes
        lx = max(length_x, 0.001)
        wy = max(width_y, 0.001)
        hz = max(height_z, 0.001)
        return trimesh.creation.box(extents=[lx, wy, hz])

    @staticmethod
    def generate_sphere(radius):
        r = max(radius, 0.001)
        # Icosphere creates a beautiful, symmetrical geodesic sphere
        return trimesh.creation.icosphere(subdivisions=3, radius=r)

    @staticmethod
    def generate_prism(n_sides, circum_radius, length_z):
        n = max(int(n_sides), 3)
        r = max(circum_radius, 0.001)
        hz = max(length_z, 0.001)
        return trimesh.creation.cylinder(radius=r, height=hz, sections=n)

    @staticmethod
    def generate_tube(outer_radius, inner_radius, length_z):
        r_out = max(outer_radius, inner_radius)
        r_in = min(outer_radius, inner_radius)
        hz = max(length_z, 0.001)
        
        # If user typed identical radii, enforce a 1mm thickness
        if r_out - r_in < 0.001: 
            r_out = r_in + 0.001
            
        # Draw a closed rectangular box in 2D
        profile = [
            (r_in, hz / 2.0),
            (r_in, -hz / 2.0),
            (r_out, -hz / 2.0),
            (r_out, hz / 2.0),
            (r_in, hz / 2.0) # Close the loop
        ]
        return PrimitiveGenerator._revolve_profile(profile)

    @staticmethod
    def generate_torus(major_radius, minor_radius):
        r_maj = max(major_radius, 0.002)
        # Protect against the torus mathematically passing through its own center
        r_min = max(0.001, min(minor_radius, r_maj - 0.001))
        
        # Draw a 2D circle shifted outwards by the Major Radius
        angles = np.linspace(0, 2 * np.pi, 32, endpoint=True)
        profile = []
        for a in angles:
            r = r_maj + r_min * np.cos(a)
            z = r_min * np.sin(a)
            profile.append((r, z))
            
        return PrimitiveGenerator._revolve_profile(profile)

    @staticmethod
    def generate_truncated_cone(bottom_radius, top_radius, length_z):
        r_bot = max(bottom_radius, 0.0)
        r_top = max(top_radius, 0.0)
        hz = max(length_z, 0.001)
        
        if r_bot == 0.0 and r_top == 0.0:
            r_bot = 0.001
            
        # Tracing from Top Pole -> Top Edge -> Bottom Edge -> Bottom Pole
        profile = [
            (0.0, hz / 2.0),
            (r_top, hz / 2.0),
            (r_bot, -hz / 2.0),
            (0.0, -hz / 2.0)
        ]
        return PrimitiveGenerator._revolve_profile(profile)

    @staticmethod
    def generate_link(cyl_radius, sphere_radius, length_z):
        # Enforce that the spheres are always slightly thicker than the joining cylinder
        r_s = max(sphere_radius, 0.002)
        r_c = max(0.001, min(cyl_radius, r_s - 0.001))
        hz = max(length_z, 0.0)
        
        # Calculate exactly where the cylinder mathematically intersects the spheres
        h_int = np.sqrt(r_s**2 - r_c**2)
        
        # 1. Map the outer hull of the Top Sphere (stopping at intersection)
        phi_int_top = np.arctan2(r_c, -h_int)
        phi_top = np.linspace(0, phi_int_top, 16)
        top_r = r_s * np.sin(phi_top)
        top_z = (hz / 2.0) + r_s * np.cos(phi_top)
        
        # 2. Map the outer hull of the Bottom Sphere (starting at intersection)
        phi_int_bot = np.arctan2(r_c, h_int)
        phi_bot = np.linspace(phi_int_bot, np.pi, 16)
        bot_r = r_s * np.sin(phi_bot)
        bot_z = (-hz / 2.0) + r_s * np.cos(phi_bot)
        
        profile = []
        for r, z in zip(top_r, top_z): profile.append((r, z))
        # The straight vertical drop of the cylinder is implied by connecting top to bottom!
        for r, z in zip(bot_r, bot_z): profile.append((r, z))
        
        return PrimitiveGenerator._revolve_profile(profile)