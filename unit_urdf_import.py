# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.10.1
#  Module: unit_urdf_import.py
#  Description:
#      Parses URDF (Unified Robot Description Format) robot models into a
#      lightweight, SimPhant-independent data model (links, joints, materials)
#      that later import stages use to populate RigidBody/Joint/RFrame objects.
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

import os
import logging
from collections import deque
import xml.etree.ElementTree as ET

import numpy as np
import trimesh
import pyvista as pv

# Matches the MMtoM convention used throughout unit_rigidbody.py / main.py:
# SimPhant's mesh/actor layer is natively in millimeters, while URDF assets
# (and all physics-side vectors in this module) are expressed in meters.
MMtoM = 1000.0


class UrdfParseError(Exception):
    """ Raised when a URDF file cannot be parsed into a usable kinematic model. """


# =============================================================================
# --- GEOMETRIC HELPERS ---
# Shared by the parser (joint/visual/inertial <origin> tags) and, later, by the
# Phase 4 forward-kinematics walker -- so both stages compose transforms the
# exact same, unambiguous way.
# =============================================================================
def _parse_floats(text, count, default=0.0):
    """ Parses a whitespace-separated string of floats, padding/truncating to exactly `count` values. """
    if not text:
        return [default] * count
    vals = [float(v) for v in text.strip().split()]
    if len(vals) < count:
        vals += [default] * (count - len(vals))
    return vals[:count]


def rpy_to_matrix(rpy):
    """
    Converts URDF fixed-axis roll-pitch-yaw angles (radians) into a 3x3 rotation matrix.
    Per the URDF spec, rpy is a fixed-axis (extrinsic) rotation applied in order
    roll (X) -> pitch (Y) -> yaw (Z), which composes as R = Rz(yaw) @ Ry(pitch) @ Rx(roll).
    """
    roll, pitch, yaw = rpy
    cr, sr = np.cos(roll), np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw), np.sin(yaw)

    Rx = np.array([[1.0, 0.0, 0.0], [0.0, cr, -sr], [0.0, sr, cr]])
    Ry = np.array([[cp, 0.0, sp], [0.0, 1.0, 0.0], [-sp, 0.0, cp]])
    Rz = np.array([[cy, -sy, 0.0], [sy, cy, 0.0], [0.0, 0.0, 1.0]])

    return Rz @ Ry @ Rx


def origin_to_matrix(origin_elem):
    """
    Builds a 4x4 homogeneous transform from a URDF <origin xyz="" rpy=""/> element.
    A missing <origin> tag defaults to identity (xyz="0 0 0" rpy="0 0 0"), per the URDF spec.
    """
    xyz = np.zeros(3)
    rpy = np.zeros(3)
    if origin_elem is not None:
        xyz = np.array(_parse_floats(origin_elem.get('xyz'), 3))
        rpy = np.array(_parse_floats(origin_elem.get('rpy'), 3))

    T = np.eye(4)
    T[:3, :3] = rpy_to_matrix(rpy)
    T[:3, 3] = xyz
    return T


def compose_transforms(*transforms):
    """
    Composes an ordered chain of 4x4 homogeneous transforms (outermost/parent first).
    URDF has THREE independent <origin> tags per link (joint origin, visual origin,
    inertial origin) that are easy to conflate -- always go through this single helper
    so the composition order stays unambiguous and consistent across the parser and
    the later forward-kinematics walker.
    """
    result = np.eye(4)
    for T in transforms:
        result = result @ T
    return result


# =============================================================================
# --- PATH RESOLUTION HELPERS ---
# =============================================================================
def _resolve_package_uri(filename, base_dir, max_levels=3):
    """
    Resolves a ROS-style 'package://...' mesh URI to an absolute filesystem path,
    without requiring an actual ROS package index (catkin/ament/ROS_PACKAGE_PATH).

    Real-world URDF files disagree on exactly what follows 'package://':
      - standard form:    package://<package_name>/<path-inside-package>
      - abbreviated form:  package://<path-relative-to-package-root>  (no package name
        segment at all -- seen e.g. in some auto-generated/deprecated URDF exports)

    Since we don't have a ROS package resolver available, this walks upward from the
    .urdf file's own directory (its most common location is '<package>/urdf/robot.urdf',
    i.e. one level below the package root, but some files sit directly in the package
    root) and, at each candidate root, tries both interpretations above. The first
    candidate that exists on disk wins; returns None if nothing matches.
    """
    rel = filename[len('package://'):]
    if not rel:
        return None
    rel = rel.replace('\\', '/')
    first_segment, _, remainder = rel.partition('/')

    search_dir = base_dir
    for _ in range(max_levels + 1):
        # Standard form: '<search_dir>' *is* the package named by the first path segment.
        if remainder and os.path.basename(os.path.normpath(search_dir)) == first_segment:
            candidate = os.path.normpath(os.path.join(search_dir, remainder))
            if os.path.isfile(candidate):
                return candidate
        # Abbreviated/root-relative form: the whole URI tail is relative to this root.
        candidate = os.path.normpath(os.path.join(search_dir, rel))
        if os.path.isfile(candidate):
            return candidate

        parent = os.path.dirname(search_dir)
        if parent == search_dir:
            break
        search_dir = parent

    return None


# =============================================================================
# --- DATA MODEL ---
# =============================================================================
class UrdfVisual:
    """ A single <visual> entry: a mesh plus its local offset and resolved color. """
    def __init__(self, origin, mesh_path, color_rgba=None):
        self.origin = origin            # 4x4 matrix: visual mesh frame, relative to the owning link's frame
        self.mesh_path = mesh_path      # absolute, resolved filesystem path to the mesh asset
        self.color_rgba = color_rgba    # (r, g, b, a) floats in [0, 1], or None if unresolved


class UrdfInertial:
    """ A link's <inertial> block: mass, center of mass, and inertia tensor about the CoM. """
    def __init__(self, origin, mass, inertia_tensor):
        self.origin = origin                      # 4x4 matrix: CoM position/orientation, relative to the link frame
        self.mass = mass                          # kg
        self.inertia_tensor = inertia_tensor      # 3x3 symmetric numpy array, kg*m^2, about the inertial frame


class UrdfLink:
    """ A single <link>: optional mass properties, and zero or more visual meshes. """
    def __init__(self, name):
        self.name = name
        self.inertial = None    # UrdfInertial or None (placeholder/sensor-frame links have none)
        self.visuals = []       # list[UrdfVisual] (can be empty for placeholder links)

    @property
    def has_geometry(self):
        return len(self.visuals) > 0

    @property
    def has_mass(self):
        return self.inertial is not None and self.inertial.mass > 0.0


class UrdfJoint:
    """ A single <joint>: connects a parent link to a child link with a fixed offset and motion axis. """
    def __init__(self, name, joint_type, parent, child, origin, axis):
        self.name = name
        self.joint_type = joint_type   # raw URDF string: 'revolute', 'continuous', 'prismatic', 'fixed', 'planar', 'floating'
        self.parent = parent           # parent link name
        self.child = child             # child link name
        self.origin = origin           # 4x4 matrix: child/joint frame, relative to the parent link's frame
        self.axis = axis               # normalized 3-vector, expressed in the joint (child) frame


class UrdfRobot:
    """
    In-memory representation of a parsed URDF robot description, fully decoupled from
    SimPhant's own RigidBody/Joint classes so the XML parsing stays independently testable.
    Later import stages (mesh loading, mass-property assignment, forward kinematics,
    RigidBody/Joint instantiation) consume this model without re-touching the XML.
    """
    def __init__(self, name, base_dir):
        self.name = name
        self.base_dir = base_dir           # Directory containing the .urdf file (mesh paths resolve against this)
        self.materials = {}                 # material name -> (r, g, b, a)
        self.links = {}                      # link name -> UrdfLink
        self.joints = {}                     # joint name -> UrdfJoint
        self.children_of = {}                 # parent link name -> list[joint name]
        self.root_link_name = None
        self.skipped_visuals = []             # [(link_name, reason)] for diagnostics (e.g. package:// URIs, primitives)

    # ------------------------------------------
    @classmethod
    def parse(cls, urdf_path):
        """ Parses a .urdf file on disk into a fully-linked UrdfRobot model. """
        if not os.path.isfile(urdf_path):
            raise UrdfParseError(f"URDF file not found: {urdf_path}")

        try:
            tree = ET.parse(urdf_path)
        except ET.ParseError as e:
            raise UrdfParseError(f"Malformed URDF XML in '{urdf_path}': {e}") from e

        root = tree.getroot()
        if root.tag != 'robot':
            raise UrdfParseError(f"Expected a <robot> root element, found <{root.tag}>.")

        base_dir = os.path.dirname(os.path.abspath(urdf_path))
        robot = cls(name=root.get('name', 'unnamed_robot'), base_dir=base_dir)

        # 1. First pass: collect globally-defined named materials (<material> declared at <robot> level).
        #    These are referenced by name only from inside <link><visual><material name="..."/>.
        for mat_elem in root.findall('material'):
            mat_name = mat_elem.get('name')
            if not mat_name:
                continue
            color_elem = mat_elem.find('color')
            if color_elem is not None and color_elem.get('rgba'):
                robot.materials[mat_name] = tuple(_parse_floats(color_elem.get('rgba'), 4, default=1.0))

        # 2. Second pass: links (mass properties + visual geometry).
        for link_elem in root.findall('link'):
            link_name = link_elem.get('name')
            if not link_name:
                continue
            robot.links[link_name] = robot._parse_link(link_elem)

        # 3. Third pass: joints + parent->children bookkeeping for the tree walk.
        for joint_elem in root.findall('joint'):
            joint = robot._parse_joint(joint_elem)
            robot.joints[joint.name] = joint
            robot.children_of.setdefault(joint.parent, []).append(joint.name)

        robot._validate_tree()
        robot._identify_root_link()
        return robot

    # ------------------------------------------
    def _parse_link(self, link_elem):
        link = UrdfLink(name=link_elem.get('name'))

        inertial_elem = link_elem.find('inertial')
        if inertial_elem is not None:
            link.inertial = self._parse_inertial(inertial_elem)

        for visual_elem in link_elem.findall('visual'):
            visual = self._parse_visual(link.name, visual_elem)
            if visual is not None:
                link.visuals.append(visual)

        return link

    @staticmethod
    def _parse_inertial(inertial_elem):
        origin = origin_to_matrix(inertial_elem.find('origin'))

        mass_elem = inertial_elem.find('mass')
        mass = float(mass_elem.get('value', 0.0)) if mass_elem is not None else 0.0

        inertia_elem = inertial_elem.find('inertia')
        if inertia_elem is not None:
            ixx = float(inertia_elem.get('ixx', 0.0))
            ixy = float(inertia_elem.get('ixy', 0.0))
            ixz = float(inertia_elem.get('ixz', 0.0))
            iyy = float(inertia_elem.get('iyy', 0.0))
            iyz = float(inertia_elem.get('iyz', 0.0))
            izz = float(inertia_elem.get('izz', 0.0))
        else:
            ixx = ixy = ixz = iyy = iyz = izz = 0.0

        inertia_tensor = np.array([
            [ixx, ixy, ixz],
            [ixy, iyy, iyz],
            [ixz, iyz, izz],
        ])

        return UrdfInertial(origin=origin, mass=mass, inertia_tensor=inertia_tensor)

    def _parse_visual(self, link_name, visual_elem):
        origin = origin_to_matrix(visual_elem.find('origin'))

        geometry_elem = visual_elem.find('geometry')
        mesh_path = None
        if geometry_elem is not None:
            mesh_elem = geometry_elem.find('mesh')
            if mesh_elem is not None:
                filename = mesh_elem.get('filename')
                if filename:
                    if filename.startswith('package://'):
                        resolved = _resolve_package_uri(filename, self.base_dir)
                        if resolved is None:
                            self.skipped_visuals.append(
                                (link_name, f"Could not resolve package:// URI (no ROS package index available): {filename}"))
                            return None
                        mesh_path = resolved
                    else:
                        mesh_path = os.path.normpath(os.path.join(self.base_dir, filename))
            else:
                # Primitive geometry (<box>/<cylinder>/<sphere>) -- SimPhant already has its
                # own PrimitiveGenerator; mapping URDF primitives to it is a future enhancement.
                self.skipped_visuals.append((link_name, "Non-mesh primitive geometry (box/cylinder/sphere) not yet supported"))

        if mesh_path is None:
            return None

        color_rgba = None
        material_elem = visual_elem.find('material')
        if material_elem is not None:
            color_elem = material_elem.find('color')
            if color_elem is not None and color_elem.get('rgba'):
                color_rgba = tuple(_parse_floats(color_elem.get('rgba'), 4, default=1.0))
            else:
                color_rgba = self.materials.get(material_elem.get('name'))

        return UrdfVisual(origin=origin, mesh_path=mesh_path, color_rgba=color_rgba)

    @staticmethod
    def _parse_joint(joint_elem):
        name = joint_elem.get('name')
        joint_type = joint_elem.get('type', 'fixed')

        parent_elem = joint_elem.find('parent')
        child_elem = joint_elem.find('child')
        if parent_elem is None or child_elem is None:
            raise UrdfParseError(f"Joint '{name}' is missing a <parent> or <child> link reference.")

        origin = origin_to_matrix(joint_elem.find('origin'))

        axis_elem = joint_elem.find('axis')
        if axis_elem is not None and axis_elem.get('xyz'):
            axis = np.array(_parse_floats(axis_elem.get('xyz'), 3))
        else:
            axis = np.array([1.0, 0.0, 0.0])  # URDF default axis per spec

        norm = np.linalg.norm(axis)
        axis = axis / norm if norm > 1e-9 else np.array([1.0, 0.0, 0.0])

        return UrdfJoint(
            name=name, joint_type=joint_type,
            parent=parent_elem.get('link'), child=child_elem.get('link'),
            origin=origin, axis=axis,
        )

    # ------------------------------------------
    def _validate_tree(self):
        for joint in self.joints.values():
            if joint.parent not in self.links:
                raise UrdfParseError(f"Joint '{joint.name}' references unknown parent link '{joint.parent}'.")
            if joint.child not in self.links:
                raise UrdfParseError(f"Joint '{joint.name}' references unknown child link '{joint.child}'.")

        # Each link must be the child of at most one joint (strict tree, no closed kinematic loops).
        child_counts = {}
        for joint in self.joints.values():
            child_counts[joint.child] = child_counts.get(joint.child, 0) + 1
        offenders = [name for name, count in child_counts.items() if count > 1]
        if offenders:
            raise UrdfParseError(f"Link(s) {offenders} are the <child> of more than one joint (closed kinematic loops are not supported).")

    def _identify_root_link(self):
        child_links = {joint.child for joint in self.joints.values()}
        roots = [name for name in self.links if name not in child_links]

        if len(roots) == 0:
            raise UrdfParseError("No root link found -- every link is a joint child (possible cycle).")
        if len(roots) > 1:
            raise UrdfParseError(f"Multiple disconnected root links found: {roots}. Only single-tree robots are supported.")

        self.root_link_name = roots[0]

    # ------------------------------------------
    def get_child_joints(self, link_name):
        """ Returns the UrdfJoint objects whose <parent> is `link_name`, in declaration order. """
        return [self.joints[j_name] for j_name in self.children_of.get(link_name, [])]

    def iter_links_breadth_first(self):
        """ Yields (UrdfLink, parent_UrdfJoint_or_None) pairs, walking the tree root -> leaves. """
        queue = deque([(self.root_link_name, None)])
        visited = set()
        while queue:
            link_name, parent_joint = queue.popleft()
            if link_name in visited:
                continue
            visited.add(link_name)
            yield self.links[link_name], parent_joint
            for joint in self.get_child_joints(link_name):
                queue.append((joint.child, joint))

    def summary(self):
        """ A short human-readable diagnostic summary, useful for post-import logging. """
        total_mass = sum(link.inertial.mass for link in self.links.values() if link.inertial)
        meshless = [l.name for l in self.links.values() if not l.has_geometry]
        massless = [l.name for l in self.links.values() if not l.has_mass]
        return (
            f"Robot '{self.name}': {len(self.links)} links, {len(self.joints)} joints, "
            f"root='{self.root_link_name}', total_mass={total_mass:.3f} kg\n"
            f"  Meshless links ({len(meshless)}): {meshless}\n"
            f"  Massless links ({len(massless)}): {massless}\n"
            f"  Skipped visuals: {self.skipped_visuals}"
        )


# =============================================================================
# --- MESH LOADING & MERGING ---
# Loads each link's visual mesh file(s), places them in the link's local frame via
# their own <visual><origin>, and folds multiple pieces into the single solid that
# RigidBody expects. Links with no visual geometry at all (bare sensor/attachment
# frames, e.g. 'imu_in_pelvis') return None here -- callers should create an
# RFrame-only entry for those instead of a RigidBody (per project decision).
# =============================================================================
def _notify(warn_callback, message):
    """ Routes a diagnostic message to the caller's callback, or prints it if none was given. """
    if warn_callback:
        warn_callback(message)
    else:
        print(f"[URDF Import] {message}")


def _trimesh_to_polydata(mesh):
    """ Converts a trimesh.Trimesh into a PyVista PolyData (for the VTK-based boolean fallback). """
    faces_padded = np.insert(mesh.faces, 0, 3, axis=1)
    return pv.PolyData(mesh.vertices, faces_padded.flatten())


def _polydata_to_trimesh(polydata):
    """ Converts a triangulated PyVista surface back into a trimesh.Trimesh, flipping inverted normals. """
    if polydata is None:
        return None

    surface = polydata.extract_surface(algorithm='dataset_surface').triangulate().clean()
    if surface.n_cells == 0 or surface.faces.size == 0:
        return None

    faces = surface.faces.reshape((-1, 4))[:, 1:4]
    mesh = trimesh.Trimesh(vertices=np.array(surface.points), faces=faces, process=True)

    if mesh.volume < 0.0:
        mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=np.fliplr(mesh.faces), process=True)

    return mesh


def _boolean_union_pair(mesh_a, mesh_b, tol_volume=1e-9):
    """
    Attempts a watertight boolean union of two trimesh solids already positioned in the
    same local frame -- mirroring SimPhant's existing Boolean Union feature (see
    MainWindow._build_union_trimesh in main.py): Manifold engine preferred, PyVista/VTK
    fallback. Union is intentionally only attempted when the pieces truly overlap; two
    pieces that don't intersect are reported back as "no_intersection" so the caller can
    fall back to plain concatenation instead (correct and lossless for disjoint/adjacent
    visual pieces, which is the common case for multi-visual URDF links).

    Returns (merged_trimesh, "manifold" | "pyvista") on success,
    or (None, reason_string) when a union could not be produced.
    """
    try:
        import manifold3d  # noqa: F401

        intersection_geom = trimesh.boolean.intersection([mesh_a, mesh_b], engine='manifold')
        if intersection_geom is None or intersection_geom.is_empty or abs(intersection_geom.volume) <= tol_volume:
            return None, "no_intersection"

        union_geom = trimesh.boolean.union([mesh_a, mesh_b], engine='manifold')
        if union_geom is None or union_geom.is_empty:
            return None, "empty_union"

        union_geom = trimesh.Trimesh(vertices=union_geom.vertices, faces=union_geom.faces, process=True)
        if union_geom.volume < 0.0:
            union_geom = trimesh.Trimesh(vertices=union_geom.vertices, faces=np.fliplr(union_geom.faces), process=True)

        if not union_geom.is_watertight or abs(union_geom.volume) <= tol_volume:
            return None, "non_watertight_union"

        return union_geom, "manifold"

    except ImportError:
        pass
    except Exception as manifold_exc:
        logging.warning(f"Manifold boolean path unavailable or failed: {manifold_exc}")

    try:
        pd_a = _trimesh_to_polydata(mesh_a).clean().triangulate()
        pd_b = _trimesh_to_polydata(mesh_b).clean().triangulate()

        intersection_surface = pd_a.boolean_intersection(pd_b)
        intersection_geom = _polydata_to_trimesh(intersection_surface)
        if intersection_geom is None or abs(intersection_geom.volume) <= tol_volume:
            return None, "no_intersection"

        union_surface = pd_a.boolean_union(pd_b)
        union_geom = _polydata_to_trimesh(union_surface)
        if union_geom is None or not union_geom.is_watertight or abs(union_geom.volume) <= tol_volume:
            return None, "pyvista_union_failed"

        return union_geom, "pyvista"

    except Exception as pyvista_exc:
        return None, f"error: {pyvista_exc}"


def merge_link_visual_meshes(link, warn_callback=None):
    """
    Loads and merges all <visual> meshes of a URDF link into a single trimesh solid,
    expressed in the link's own local frame (meters, matching UrdfInertial/UrdfJoint).

    Strategy: fold the pieces together one at a time. For each new piece, first try a
    watertight boolean union against the accumulated mesh (correct when visual pieces
    physically overlap); when the pieces don't intersect, union intentionally bails out,
    so fall back to plain concatenation, which is exactly right for disjoint/adjacent
    pieces -- the normal case for multi-visual links. Only a piece that neither unions
    nor loads cleanly is skipped, with a warning; it never aborts the whole link.

    Returns None if the link has no visual geometry at all (placeholder/sensor-frame links).
    """
    if not link.visuals:
        return None

    loaded = []
    for visual in link.visuals:
        try:
            raw_mesh = trimesh.load(visual.mesh_path, force='mesh')
        except Exception as exc:
            _notify(warn_callback, f"Link '{link.name}': failed to load mesh '{visual.mesh_path}': {exc}")
            continue

        if raw_mesh is None or raw_mesh.is_empty:
            _notify(warn_callback, f"Link '{link.name}': mesh '{visual.mesh_path}' is empty, skipped.")
            continue

        raw_mesh.apply_transform(visual.origin)
        loaded.append(raw_mesh)

    if not loaded:
        return None

    merged = loaded[0]
    for piece in loaded[1:]:
        union_mesh, status = _boolean_union_pair(merged, piece)

        if union_mesh is not None:
            merged = union_mesh
        elif status == "no_intersection":
            merged = trimesh.util.concatenate([merged, piece])
        else:
            _notify(warn_callback, f"Link '{link.name}': could not merge one visual mesh ({status}); it was skipped.")

    return merged


def load_link_render_mesh(link, warn_callback=None):
    """
    Loads, positions, and merges a link's visual meshes into a single mm-scale trimesh
    solid ready to become a RigidBody's raw_geom/block_mesh. Returns None for meshless
    links -- the caller should create an RFrame-only entry for those instead.
    """
    merged_m = merge_link_visual_meshes(link, warn_callback=warn_callback)
    if merged_m is None:
        return None

    merged_m.apply_scale(MMtoM)  # URDF meters -> SimPhant's native millimeter mesh convention
    return merged_m


def load_all_link_meshes(robot, warn_callback=None):
    """
    Loads the merged, mm-scale render mesh for every link in the robot that has visual
    geometry. Returns a dict {link_name: trimesh.Trimesh}; meshless links are simply
    absent from the result (callers route those to RFrame-only creation).
    """
    meshes = {}
    for link in robot.links.values():
        mesh = load_link_render_mesh(link, warn_callback=warn_callback)
        if mesh is not None:
            meshes[link.name] = mesh
    return meshes


# =============================================================================
# --- FORWARD KINEMATICS ---
# Walks the URDF tree root -> leaves, composing each joint's <origin> transform to
# obtain every link's world-frame pose at the robot's zero/reference configuration
# (the same "initial pose" convention SimPhant already uses for CAD-imported bodies).
# All transforms/positions here stay in meters; mm scaling only happens at the very
# end, when a link's render mesh is placed into world space.
# =============================================================================
def compute_forward_kinematics(robot):
    """
    Returns a dict {link_name: 4x4 world transform (meters)}, obtained by composing
    joint origins root -> leaves (a joint's own <origin> is relative to its parent
    link's frame). The root link sits at the world origin (identity) -- SimPhant has
    no notion of the floating-base joint some URDFs declare (it is commented out in
    the G1 file, and is not part of the strict parent/child tree the parser validates).
    """
    world_transforms = {robot.root_link_name: np.eye(4)}
    for link, parent_joint in robot.iter_links_breadth_first():
        if parent_joint is None:
            continue  # root link, already seeded above
        parent_world = world_transforms[parent_joint.parent]
        world_transforms[link.name] = compose_transforms(parent_world, parent_joint.origin)
    return world_transforms


def joint_world_anchor(joint, world_transforms):
    """
    Returns a joint's anchor position in world meters. A URDF joint's anchor/axis
    frame is mathematically identical to its own child link's world transform (both
    equal parent_world @ joint.origin) -- this accessor just reuses that already-
    computed transform rather than recomputing anything redundantly.
    """
    return world_transforms[joint.child][:3, 3]


def joint_world_axis(joint, world_transforms):
    """
    Returns a joint's rotation/translation axis as a world-frame unit vector. URDF's
    <axis> is defined in the joint's own (= child link's) frame, so this just rotates
    it by the child link's world orientation.
    """
    child_rotation = world_transforms[joint.child][:3, :3]
    axis_world = child_rotation @ joint.axis
    norm = np.linalg.norm(axis_world)
    return axis_world / norm if norm > 1e-12 else axis_world


def world_mass_properties(link, link_world_transform):
    """
    Returns (mass, cog_world_m, inertia_world) derived from a link's URDF <inertial>
    block, ready for RigidBody.set_mass_properties(). The inertia tensor is rotated
    from the link's local inertial frame into world-aligned axes via the similarity
    transform I_world = R @ I_local @ R.T (R = link world rotation * inertial origin
    rotation), matching how CAD-imported bodies already receive a world-aligned
    inertia tensor from trimesh (computed on an already link-positioned mesh).

    Returns None if the link has no <inertial> block at all -- callers should fall
    back to RigidBody's own volumetric calculate_mass_properties() for a link that
    has visual geometry but no supplied mass data (not present in G1, but valid URDF).
    """
    if link.inertial is None:
        return None

    com_local = np.append(link.inertial.origin[:3, 3], 1.0)
    cog_world = (link_world_transform @ com_local)[:3]

    R = link_world_transform[:3, :3] @ link.inertial.origin[:3, :3]
    inertia_world = R @ link.inertial.inertia_tensor @ R.T

    return link.inertial.mass, cog_world, inertia_world


def place_mesh_in_world(local_mesh_mm, link_world_transform):
    """
    Places an already-merged, already-mm-scaled link mesh (expressed in the link's
    own local frame, as produced by load_link_render_mesh) into world space for
    RigidBody creation. Rotation is carried over unchanged from the link's world
    transform; translation is converted meters -> mm to match the mesh's own
    millimeter convention (rotating unit-less mesh coordinates needs no rescaling).
    """
    T_mm = link_world_transform.copy()
    T_mm[:3, 3] *= MMtoM
    world_mesh = local_mesh_mm.copy()
    world_mesh.apply_transform(T_mm)
    return world_mesh
