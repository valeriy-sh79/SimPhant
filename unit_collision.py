# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.10.2
#  Module: unit_collision.py
#  Description:
#      Defines the ContactPair class for handling collision interactions between rigid bodies, 
#      including normal and frictional forces using the Hunt-Crossley / Hertzian non-linear penalty model.
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
from manifold3d import Error, Manifold, Mesh64
from trimesh.ray.ray_triangle import ray_triangle_candidates


def empty_contact_manifold():
    return np.empty((0, 3)), np.empty((0, 3)), np.empty(0)


class ContactResolutionError(ValueError):
    """An overlap has no resolved single separating direction at this trial state."""


class RegionContactGeometry:
    """Cached closed solid and surface queries, expressed in local meters."""

    def __init__(self, mesh_mm, name):
        self.name = name
        self.mesh = mesh_mm.copy()
        if not self.mesh.is_volume or not np.all(np.isfinite(self.mesh.vertices)):
            raise ValueError(f"Contact geometry '{name}' must be a closed, consistently oriented solid.")
        self.mesh.apply_scale(0.001)
        self.origin = self.mesh.bounds.mean(axis=0)
        self.mesh.apply_translation(-self.origin)
        self.solid = Manifold(Mesh64(
            vert_properties=np.ascontiguousarray(self.mesh.vertices, dtype=np.float64),
            tri_verts=np.ascontiguousarray(self.mesh.faces, dtype=np.uint64),
        ))
        if self.solid.status() != Error.NoError or self.solid.is_empty():
            raise ValueError(f"Contact geometry '{name}' is not a valid Manifold solid: {self.solid.status()}.")
        self.surface_ids = np.unique(self.solid.to_mesh64().run_original_id)

    def _region_contact(self, region, tolerance):
        """Measure opposite surface patches, without requiring an interior centroid."""
        mesh = region.to_mesh64()
        vertices = np.asarray(mesh.vert_properties[:, :3])
        origin = 0.5 * (vertices.min(axis=0) + vertices.max(axis=0))
        scale = float(np.ptp(vertices, axis=0).max())
        if scale <= tolerance:
            return None
        surface = trimesh.Trimesh(vertices=(vertices - origin) / scale,
                                  faces=mesh.tri_verts, process=False)
        owners = np.repeat(np.asarray(mesh.run_original_id), np.diff(mesh.run_index) // 3)
        self_faces = np.isin(owners, self.surface_ids)
        area_vectors = surface.face_normals * surface.area_faces[:, None]
        normal = -area_vectors[self_faces].sum(axis=0)
        magnitude = np.linalg.norm(normal)
        patch_area = surface.area_faces[self_faces].sum()
        if not np.any(self_faces) or np.all(self_faces) or magnitude <= 1e-8 * patch_area:
            raise ContactResolutionError(f"Unresolved or contained overlap on '{self.name}'.")
        normal /= magnitude
        facing = surface.face_normals @ normal
        if np.any(facing[self_faces] > 0.05) or np.any(facing[~self_faces] < -0.05):
            raise ContactResolutionError(f"Overlap wraps beyond a separating surface on '{self.name}'.")

        samples = np.vstack((surface.vertices, surface.triangles_center))
        projected = samples @ normal
        rays = samples + (projected.min() - projected - 1.0)[:, None] * normal
        directions = np.tile(normal, (len(rays), 1))
        candidates, candidate_rays = ray_triangle_candidates(rays, directions, surface.triangles_tree)
        locations, valid_planes = trimesh.intersections.planes_lines(
            surface.triangles[candidates, 0], surface.face_normals[candidates],
            rays[candidate_rays], directions[candidate_rays])
        candidates, candidate_rays = candidates[valid_planes], candidate_rays[valid_planes]
        try:
            with np.errstate(divide='raise', invalid='raise'):
                barycentric = trimesh.triangles.points_to_barycentric(
                    surface.triangles[candidates], locations, method='cross')
        except FloatingPointError as exc:
            raise ContactResolutionError(f"Degenerate overlap triangles on '{self.name}'.") from exc
        hit = np.all((barycentric >= -1e-13) & (barycentric <= 1 + 1e-13), axis=1)
        face_ids, ray_ids = candidates[hit], candidate_rays[hit]
        if len(face_ids) < 2:
            raise ContactResolutionError(f"No opposing surface hits on '{self.name}'.")
        distances = (np.einsum('ij,ij->i', surface.triangles_center[face_ids] - rays[ray_ids],
                               surface.face_normals[face_ids]) / facing[face_ids]
                     + rays[ray_ids] @ normal)
        order = np.lexsort((distances, ray_ids))
        ray_ids, distances, face_ids = ray_ids[order], distances[order], face_ids[order]
        valid = ((ray_ids[1:] == ray_ids[:-1]) & self_faces[face_ids[:-1]]
                 & ~self_faces[face_ids[1:]] & (facing[face_ids[:-1]] < 0)
                 & (facing[face_ids[1:]] > 0))
        if not np.any(valid):
            raise ContactResolutionError(f"No opposing surface interval on '{self.name}'.")
        depth = float(np.max(np.diff(distances)[valid])) * scale
        if depth <= tolerance:
            return None
        center = surface.center_mass * scale + origin
        if not np.all(np.isfinite(center)) or not np.isfinite(depth):
            raise ContactResolutionError(f"Non-finite overlap measurement on '{self.name}'.")
        return center, normal, depth

    def contact_regions(self, other, rotation, position, other_rotation, other_position):
        """Return one common application point, normal on self, and depth per overlap volume."""
        relative_rotation = rotation.T @ other_rotation
        relative_position = (rotation.T @ (other_position - position)
                             + relative_rotation @ other.origin - self.origin)
        transform = np.column_stack((relative_rotation, relative_position))
        intersection = self.solid ^ other.solid.transform(transform)
        if intersection.status() != Error.NoError:
            raise ValueError(f"Contact intersection '{self.name}' / '{other.name}' failed: {intersection.status()}.")
        if intersection.is_empty():
            return empty_contact_manifold()

        tolerance = max(self.solid.get_tolerance(), other.solid.get_tolerance(), 1e-12)
        contacts = []
        for region in intersection.decompose():
            if region.volume() <= tolerance ** 3:
                continue
            contact = self._region_contact(region, tolerance)
            if contact is not None:
                contacts.append(contact)
        if not contacts:
            return empty_contact_manifold()
        points, normals, depths = (np.asarray(values) for values in zip(*contacts))
        order = np.lexsort((points[:, 2], points[:, 1], points[:, 0]))
        world_origin = position + rotation @ self.origin
        return (np.ascontiguousarray(points[order] @ rotation.T + world_origin),
                np.ascontiguousarray(normals[order] @ rotation.T),
                np.ascontiguousarray(depths[order]))


class ContactPair:
    """ 
    Nonlinear penalty stiffness and linear-ramped damping per solid overlap region.
    Legacy vertex-search flags are retained for project-file compatibility only.
    """
    def __init__(self, name, body_i, body_j, stiffness_ui, exponent, damping_ui, 
                 friction_enabled=False, mu=0.3, slip_tol_ui=10.0, mesh_mode=0,
                 symmetric_contact_search=True, contact_candidate_reduction_enabled=True,
                 d_max_ui=0.1):
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
        
        # Legacy project fields; region contact does not use vertex-search tuning.
        self.symmetric_contact_search = symmetric_contact_search
        self.contact_candidate_reduction_enabled = contact_candidate_reduction_enabled
        
        # Penetration Depth (d_max): UI (mm) -> Solver SI (m).
        # Damping coefficient ramps 0 -> damping over [0, d_max], then saturates (ADAMS IMPACT model).
        self.d_max_m = d_max_ui / 1000.0
        
        # Trackers for the CSV
        self.current_F_spring = 0.0
        self.current_F_damp = 0.0
        self.current_F_total = 0.0
        self.current_F_friction = 0.0 
        
        self.enabled = True
        self.tree_item = None