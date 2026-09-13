# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.1
#  Release Date: 2026/09/30
#  Module: unit_gears.py
#  Description:
#      Procedurally generates mathematically accurate 3D CAD meshes for various gear types, 
#      including spur, helical, internal, and bevel gears.
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
import trimesh

class GearGenerator:
    """ 
    Procedural generator for 3D kinematic gear meshes. 
    Outputs trimesh.Trimesh objects natively centered at the Pitch Circle Mid-Plane.
    """
    
    @staticmethod
    def generate_helical_gear(module, z, width, pressure_angle_deg=20.0, helix_angle_deg=0.0, bore_radius=0.0):
        beta = np.radians(helix_angle_deg)
        alpha_t = np.radians(pressure_angle_deg)
        
        r_pitch = (module * z) / 2.0
        r_tip = r_pitch + module       
        r_root = r_pitch - (1.25 * module) 
        
        # --- THE FIX: Exact Linear Thickness to Angular Arc Mapping ---
        angle_per_tooth = 2.0 * np.pi / z
        
        # Calculate linear thicknesses (mm) at the pitch, tip, and root
        t_pitch = (np.pi * module) / 2.0
        t_tip = t_pitch - 2.0 * (r_tip - r_pitch) * np.tan(alpha_t)
        t_root = t_pitch + 2.0 * (r_pitch - r_root) * np.tan(alpha_t)
        
        # Failsafe: Prevent negative thickness (pointy teeth) by clamping to 5% of module
        t_tip = max(t_tip, 0.05 * module)
        
        # Convert linear thicknesses to precise arc angles at their respective radii
        tip_arc_angle = t_tip / r_tip
        # Anti-Undercutting Clamp: Guarantee at least a 5% gap at the root for low tooth counts
        root_arc_angle = min(t_root / r_root, angle_per_tooth * 0.95)
        
        outer_pts, inner_pts = [], []
        
        for i in range(z):
            theta_center = i * angle_per_tooth
            theta_1 = theta_center - (root_arc_angle / 2.0)
            theta_2 = theta_center - (tip_arc_angle / 2.0)
            theta_3 = theta_center + (tip_arc_angle / 2.0)
            theta_4 = theta_center + (root_arc_angle / 2.0)
            
            outer_pts.append([r_root * np.cos(theta_1), r_root * np.sin(theta_1), 0.0])
            outer_pts.append([r_tip * np.cos(theta_2),  r_tip * np.sin(theta_2),  0.0])
            outer_pts.append([r_tip * np.cos(theta_3),  r_tip * np.sin(theta_3),  0.0])
            outer_pts.append([r_root * np.cos(theta_4), r_root * np.sin(theta_4), 0.0])
            
            if bore_radius > 0:
                inner_pts.extend([
                    [bore_radius * np.cos(theta_1), bore_radius * np.sin(theta_1), 0.0],
                    [bore_radius * np.cos(theta_2), bore_radius * np.sin(theta_2), 0.0],
                    [bore_radius * np.cos(theta_3), bore_radius * np.sin(theta_3), 0.0],
                    [bore_radius * np.cos(theta_4), bore_radius * np.sin(theta_4), 0.0]
                ])

        if bore_radius > 0:
            vertices = np.vstack((outer_pts, inner_pts))
            faces = []
            N = z * 4
            for i in range(N):
                nxt = (i + 1) % N
                faces.extend([3, i, nxt, i + N])          
                faces.extend([3, nxt, nxt + N, i + N])    
            gear_face = pv.PolyData(vertices, faces)
        else:
            vertices = np.array(outer_pts)
            face_sequence = [len(vertices)] + list(range(len(vertices)))
            gear_face = pv.PolyData(vertices, face_sequence)
        
        gear_3d = gear_face.extrude((0, 0, width), capping=True)
        gear_3d.points[:, 2] -= (width / 2.0)
        
        if helix_angle_deg != 0.0:
            pts = gear_3d.points
            z_vals = pts[:, 2]
            
            twist_angles = z_vals * np.tan(beta) / r_pitch
            cos_th = np.cos(twist_angles)
            sin_th = np.sin(twist_angles)
            
            x_new = pts[:, 0] * cos_th - pts[:, 1] * sin_th
            y_new = pts[:, 0] * sin_th + pts[:, 1] * cos_th
            
            gear_3d.points[:, 0] = x_new
            gear_3d.points[:, 1] = y_new
            gear_3d.compute_normals(inplace=True)
        
        gear_3d = gear_3d.clean().triangulate()
        tri_mesh = trimesh.Trimesh(vertices=gear_3d.points, faces=gear_3d.faces.reshape(-1, 4)[:, 1:4], process=True)
        
        if tri_mesh.volume < 0.0:
            tri_mesh.faces = np.fliplr(tri_mesh.faces)
            tri_mesh = trimesh.Trimesh(vertices=tri_mesh.vertices, faces=tri_mesh.faces, process=True)
            
        return tri_mesh, 0.0

    @staticmethod
    def generate_inner_gear(module, z, width, pressure_angle_deg=20.0, helix_angle_deg=0.0, outer_radius=None):
        beta = np.radians(helix_angle_deg)
        alpha_t = np.radians(pressure_angle_deg)
        
        r_pitch = (module * z) / 2.0
        r_tip = r_pitch - module           
        r_root = r_pitch + (1.25 * module) 
        
        if outer_radius is None or outer_radius <= r_root:
            outer_radius = r_root + (2.0 * module) 
            
        # --- THE FIX: Exact Linear Thickness to Angular Arc Mapping ---
        angle_per_tooth = 2.0 * np.pi / z
        t_pitch = (np.pi * module) / 2.0
        
        # For inner gears, tip is closer to the center, root is further out
        t_tip = t_pitch - 2.0 * (r_pitch - r_tip) * np.tan(alpha_t)
        t_root = t_pitch + 2.0 * (r_root - r_pitch) * np.tan(alpha_t)
        
        t_tip = max(t_tip, 0.05 * module)
        
        tip_arc_angle = t_tip / r_tip
        root_arc_angle = min(t_root / r_root, angle_per_tooth * 0.95)
        
        teeth_pts, rim_pts = [], []
        
        for i in range(z):
            theta_center = i * angle_per_tooth
            theta_1 = theta_center - (root_arc_angle / 2.0)
            theta_2 = theta_center - (tip_arc_angle / 2.0)
            theta_3 = theta_center + (tip_arc_angle / 2.0)
            theta_4 = theta_center + (root_arc_angle / 2.0)
            
            teeth_pts.append([r_root * np.cos(theta_1), r_root * np.sin(theta_1), 0.0])
            teeth_pts.append([r_tip * np.cos(theta_2),  r_tip * np.sin(theta_2),  0.0])
            teeth_pts.append([r_tip * np.cos(theta_3),  r_tip * np.sin(theta_3),  0.0])
            teeth_pts.append([r_root * np.cos(theta_4), r_root * np.sin(theta_4), 0.0])
            
            rim_pts.extend([
                [outer_radius * np.cos(theta_1), outer_radius * np.sin(theta_1), 0.0],
                [outer_radius * np.cos(theta_2), outer_radius * np.sin(theta_2), 0.0],
                [outer_radius * np.cos(theta_3), outer_radius * np.sin(theta_3), 0.0],
                [outer_radius * np.cos(theta_4), outer_radius * np.sin(theta_4), 0.0]
            ])

        vertices = np.vstack((teeth_pts, rim_pts))
        faces = []
        N = z * 4
        for i in range(N):
            nxt = (i + 1) % N
            faces.extend([3, i, nxt, i + N])          
            faces.extend([3, nxt, nxt + N, i + N])    
            
        gear_face = pv.PolyData(vertices, faces)
        gear_3d = gear_face.extrude((0, 0, width), capping=True)
        gear_3d.points[:, 2] -= (width / 2.0)
        
        if helix_angle_deg != 0.0:
            pts = gear_3d.points
            z_vals = pts[:, 2]
            
            twist_angles = z_vals * np.tan(beta) / r_pitch
            cos_th = np.cos(twist_angles)
            sin_th = np.sin(twist_angles)
            
            x_new = pts[:, 0] * cos_th - pts[:, 1] * sin_th
            y_new = pts[:, 0] * sin_th + pts[:, 1] * cos_th
            
            gear_3d.points[:, 0] = x_new
            gear_3d.points[:, 1] = y_new
            gear_3d.compute_normals(inplace=True)
        
        gear_3d = gear_3d.clean().triangulate()
        tri_mesh = trimesh.Trimesh(vertices=gear_3d.points, faces=gear_3d.faces.reshape(-1, 4)[:, 1:4], process=True)
        
        if tri_mesh.volume < 0.0:
            tri_mesh.faces = np.fliplr(tri_mesh.faces)
            tri_mesh = trimesh.Trimesh(vertices=tri_mesh.vertices, faces=tri_mesh.faces, process=True)
            
        return tri_mesh, 0.0

    @staticmethod
    def generate_bevel_gear(module, z, width, pressure_angle_deg=20.0, pitch_angle_deg=45.0, bore_radius=0.0):
        r_pitch_mid = (module * z) / 2.0
        
        alpha = np.radians(pressure_angle_deg)
        gamma = np.radians(pitch_angle_deg)
        
        r_tip_mid = r_pitch_mid + module * np.cos(gamma)
        r_root_mid = r_pitch_mid - 1.25 * module * np.cos(gamma)
        
        z_tip_mid = module * np.sin(gamma)
        z_root_mid = -1.25 * module * np.sin(gamma)
        
        if 0.0 < pitch_angle_deg < 89.9:
            apex_z = r_pitch_mid / np.tan(gamma)
            tan_g = np.tan(gamma)
            
            def get_chamfer(z_plane):
                scale_root = (apex_z - z_plane) / (apex_z - z_root_mid)
                r_root = max(r_root_mid * scale_root, 0.001)
                
                K_tip = r_tip_mid / (apex_z - z_tip_mid)
                r_tip = (K_tip * (apex_z - z_plane + r_root * tan_g)) / (1.0 + K_tip * tan_g)
                z_tip = z_plane + (r_tip - r_root) * tan_g
                return r_root, z_plane, r_tip, z_tip
                
            r_root_0, z_root_0, r_tip_0, z_tip_0 = get_chamfer(-width / 2.0)
            r_root_w, z_root_w, r_tip_w, z_tip_w = get_chamfer(width / 2.0)
            
        else:
            r_root_0, z_root_0, r_tip_0, z_tip_0 = max(r_root_mid, 0.001), -width / 2.0, max(r_tip_mid, 0.001), -width / 2.0
            r_root_w, z_root_w, r_tip_w, z_tip_w = max(r_root_mid, 0.001), width / 2.0, max(r_tip_mid, 0.001), width / 2.0
            
        # --- THE FIX: Exact Linear Thickness to Angular Arc Mapping ---
        angle_per_tooth = 2.0 * np.pi / z
        t_pitch = (np.pi * module) / 2.0
        
        t_tip = t_pitch - 2.0 * (r_tip_mid - r_pitch_mid) * np.tan(alpha)
        t_root = t_pitch + 2.0 * (r_pitch_mid - r_root_mid) * np.tan(alpha)
        
        t_tip = max(t_tip, 0.05 * module)
        
        # The angular proportions are mathematically constant across the entire cone!
        tip_arc_angle = t_tip / r_tip_mid
        root_arc_angle = min(t_root / r_root_mid, angle_per_tooth * 0.95)
        
        N = z * 4
        outer_0, inner_0 = [], []
        outer_1, inner_1 = [], []
        
        for i in range(z):
            theta_center = i * angle_per_tooth
            theta_1 = theta_center - (root_arc_angle / 2.0)
            theta_2 = theta_center - (tip_arc_angle / 2.0)
            theta_3 = theta_center + (tip_arc_angle / 2.0)
            theta_4 = theta_center + (root_arc_angle / 2.0)
            
            # Heel Face (Z = -width/2 chamfers)
            outer_0.append([r_root_0 * np.cos(theta_1), r_root_0 * np.sin(theta_1), z_root_0])
            outer_0.append([r_tip_0 * np.cos(theta_2),  r_tip_0 * np.sin(theta_2),  z_tip_0])
            outer_0.append([r_tip_0 * np.cos(theta_3),  r_tip_0 * np.sin(theta_3),  z_tip_0])
            outer_0.append([r_root_0 * np.cos(theta_4), r_root_0 * np.sin(theta_4), z_root_0])
            
            # Toe Face (Z = +width/2 chamfers)
            outer_1.append([r_root_w * np.cos(theta_1), r_root_w * np.sin(theta_1), z_root_w])
            outer_1.append([r_tip_w * np.cos(theta_2),  r_tip_w * np.sin(theta_2),  z_tip_w])
            outer_1.append([r_tip_w * np.cos(theta_3),  r_tip_w * np.sin(theta_3),  z_tip_w])
            outer_1.append([r_root_w * np.cos(theta_4), r_root_w * np.sin(theta_4), z_root_w])
            
            if bore_radius > 0:
                inner_0.extend([
                    [bore_radius * np.cos(theta_1), bore_radius * np.sin(theta_1), -width / 2.0],
                    [bore_radius * np.cos(theta_2), bore_radius * np.sin(theta_2), -width / 2.0],
                    [bore_radius * np.cos(theta_3), bore_radius * np.sin(theta_3), -width / 2.0],
                    [bore_radius * np.cos(theta_4), bore_radius * np.sin(theta_4), -width / 2.0],
                ])
                inner_1.extend([
                    [bore_radius * np.cos(theta_1), bore_radius * np.sin(theta_1), width / 2.0],
                    [bore_radius * np.cos(theta_2), bore_radius * np.sin(theta_2), width / 2.0],
                    [bore_radius * np.cos(theta_3), bore_radius * np.sin(theta_3), width / 2.0],
                    [bore_radius * np.cos(theta_4), bore_radius * np.sin(theta_4), width / 2.0],
                ])

        if bore_radius > 0:
            vertices = np.vstack((outer_0, outer_1, inner_0, inner_1))
        else:
            vertices = np.vstack((outer_0, outer_1, [[0,0, -width / 2.0], [0,0, width / 2.0]]))
            
        faces_list = []
        def add_quad_tri(p1, p2, p3, p4):
            faces_list.append([p1, p2, p3])
            faces_list.append([p1, p3, p4])
            
        for i in range(N):
            nxt = (i + 1) % N
            add_quad_tri(i, nxt, nxt + N, i + N) # Flanks
            if bore_radius > 0:
                add_quad_tri(2*N + nxt, 2*N + i, 3*N + i, 3*N + nxt) # Bore

        for tooth in range(z):
            i0 = tooth * 4
            i1 = i0 + 1
            i2 = i0 + 2
            i3 = i0 + 3
            i4 = (tooth * 4 + 4) % N 
            
            # --- BACK FACE (Heel) ---
            add_quad_tri(i0, i3, i2, i1) 
            if bore_radius > 0:
                b0, b1, b2, b3, b4 = 2*N + i0, 2*N + i1, 2*N + i2, 2*N + i3, 2*N + i4
                faces_list.extend([[i0, b0, b1], [i0, b1, b2], [i0, b2, b3], [i0, b3, i3]])
                faces_list.extend([[i3, b3, b4], [i3, b4, i4]])
            else:
                center_bottom = 2 * N
                faces_list.extend([[i0, center_bottom, i3], [i3, center_bottom, i4]])
                
            # --- FRONT FACE (Toe) ---
            t0, t1, t2, t3, t4 = N + i0, N + i1, N + i2, N + i3, N + i4
            add_quad_tri(t0, t1, t2, t3) 
            if bore_radius > 0:
                c0, c1, c2, c3, c4 = 3*N + i0, 3*N + i1, 3*N + i2, 3*N + i3, 3*N + i4
                faces_list.extend([[t0, c1, c0], [t0, c2, c1], [t0, c3, c2], [t0, t3, c3]])
                faces_list.extend([[t3, c4, c3], [t3, t4, c4]])
            else:
                center_top = 2 * N + 1
                faces_list.extend([[t0, t3, center_top], [t3, t4, center_top]])
                
        faces_array = np.array(faces_list)
        
        tri_mesh = trimesh.Trimesh(vertices=vertices, faces=faces_array, process=True)
        
        if tri_mesh.volume < 0.0:
            tri_mesh.faces = np.fliplr(tri_mesh.faces)
            tri_mesh = trimesh.Trimesh(vertices=tri_mesh.vertices, faces=tri_mesh.faces, process=True)
            
        return tri_mesh, 0.0