# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant® — Multibody Dynamics Simulation Software
#  Version: 2026.11.1
#  Module: unit_robotics.py
#  Description:
#      Universal serial-chain discovery, Forward Kinematics (FK), analytical
#      Geometric Jacobian, 6-DOF Damped Least-Squares Inverse Kinematics (IK)
#      solver with box-constraint joint limits, and the RoboticsWindow UI.
#
#  Copyright (C) 2026  Valeriy Shapovalov
#  GitHub: https://github.com/valeriy-sh79

#  This file is part of SimPhant.
#
#  SimPhant is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SimPhant is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SimPhant.  If not, see <https://www.gnu.org/licenses/>.
# =============================================================================

from dataclasses import dataclass, field
from collections import deque
from time import perf_counter
import ctypes
from ctypes import wintypes
import gc
import os
import re
import sys
import numpy as np
import pyvista as pv
import pyqtgraph as pg
from scipy.interpolate import BPoly, CubicSpline
from scipy.spatial.transform import Rotation, Slerp

from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QComboBox, QPushButton, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QSlider, QDoubleSpinBox,
    QSpinBox, QTabWidget, QWidget, QMessageBox, QFrame, QSplitter,
    QTreeWidgetItem, QDockWidget, QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QEvent, QAbstractNativeEventFilter
from PySide6.QtGui import QColor, QFont, QPalette, QAccessible

from unit_joints import JointType
from unit_kinematics import RFrame, MMtoM
from unit_motions import JointMotion
from unit_spline import format_spline_expression
from math_kernels import (
    matrix_to_pos_angles_deg_numba,
    pos_angles_deg_to_matrix_numba,
    forward_kinematics_chain_numba,
    compute_geometric_jacobian_numba,
    compute_pose_error_numba,
    solve_ik_dls_numba,
)


# =============================================================================
#  WINDOWS UI AUTOMATION (WM_GETOBJECT) SHIELD
# =============================================================================
_WM_GETOBJECT = 0x003D
_WIN_MSG_ID_OFFSET = wintypes.MSG.message.offset if sys.platform == "win32" else 8
_GLOBAL_UIA_SHIELD = None


class WinUiaNativeEventFilter(QAbstractNativeEventFilter):
    """
    Prevents Windows 11 background UI Automation clients (WM_GETOBJECT = 0x003D) from
    attaching synchronous COM property-change hooks onto QTableWidget / QSlider / QDoubleSpinBox,
    which otherwise stall Qt's Win32 message loop for 125-260 ms during live slider drags.
    """
    def __init__(self):
        super().__init__()
        self.enabled = True
        self.blocked_wm_getobject = 0

    def nativeEventFilter(self, eventType, message):
        if sys.platform != "win32" or eventType != b"windows_generic_MSG":
            return False, 0

        msg_id = ctypes.c_uint.from_address(int(message) + _WIN_MSG_ID_OFFSET).value
        if self.enabled and msg_id == _WM_GETOBJECT:
            self.blocked_wm_getobject += 1
            if QAccessible.isActive():
                QAccessible.setActive(False)
            return True, 0

        return False, 0


def install_win_uia_shield():
    """Installs the singleton Win32 WM_GETOBJECT shield on QApplication (idempotent)."""
    global _GLOBAL_UIA_SHIELD
    if sys.platform != "win32":
        return None
    app_qt = QApplication.instance()
    if app_qt is None:
        return None
    if _GLOBAL_UIA_SHIELD is None:
        _GLOBAL_UIA_SHIELD = WinUiaNativeEventFilter()
        app_qt.installNativeEventFilter(_GLOBAL_UIA_SHIELD)
    if QAccessible.isActive():
        QAccessible.setActive(False)
    return _GLOBAL_UIA_SHIELD


def is_dark_ui_theme(widget=None) -> bool:
    """Detects whether the active Qt or Windows color scheme is dark (matches main.py)."""
    app = QApplication.instance()
    if app is not None:
        style_hints = app.styleHints()
        if style_hints is not None and hasattr(style_hints, "colorScheme"):
            try:
                color_scheme = style_hints.colorScheme()
                if color_scheme == Qt.ColorScheme.Dark:
                    return True
                if color_scheme == Qt.ColorScheme.Light:
                    return False
            except Exception:
                pass

    palette = widget.palette() if widget is not None else (app.palette() if app is not None else None)
    if palette is not None:
        return palette.color(QPalette.Window).lightness() < 128

    return False


class RoboticsChainError(ValueError):
    """Raised when a valid serial kinematic chain cannot be constructed between two bodies."""


def matrix_to_pos_angles_deg(rot_matrix):
    """
    Converts a 3x3 rotation matrix to SimPhant's [Yaw(Z), Pitch(Y), Roll(X)] Euler array in degrees
    (extrinsic 'xyz' convention matching RigidBody.pos_angles and RFrame.orientation).
    """
    return matrix_to_pos_angles_deg_numba(np.ascontiguousarray(rot_matrix, dtype=np.float64))


def pos_angles_deg_to_matrix(orientation_zyx_deg):
    """
    Converts SimPhant's [Yaw(Z), Pitch(Y), Roll(X)] array in degrees to a 3x3 rotation matrix.
    """
    return pos_angles_deg_to_matrix_numba(np.ascontiguousarray(orientation_zyx_deg, dtype=np.float64))


def _rot_z(theta):
    """3x3 elemental rotation matrix about local Z axis by angle `theta` (radians)."""
    c = float(np.cos(theta))
    s = float(np.sin(theta))
    return np.array([
        [c, -s, 0.0],
        [s,  c, 0.0],
        [0.0, 0.0, 1.0],
    ], dtype=float)


def _joint_triad_i(joint):
    """Returns the 3x3 orthonormal joint triad [a_i, b_i, axis_i] in body_i's local frame."""
    return np.column_stack((joint.local_a_i, joint.local_b_i, joint.local_axis_i))


def _joint_triad_j(joint):
    """Returns the 3x3 orthonormal joint triad [a_j, b_j, axis_j] in body_j's local frame."""
    return np.column_stack((joint.local_a_j, joint.local_b_j, joint.local_axis_j))


def measure_joint_coordinate_si(joint, sign=1):
    """
    Measures the current joint coordinate q in SI units (`rad` for Revolute, `m` for Prismatic)
    directly from the current global poses of `joint.body_i` and `joint.body_j`.
    Matches `MBSolver.initialize_motions()` and `evaluate_derivatives()`.
    """
    A_i = joint.body_i.principal_axes
    A_j = joint.body_j.principal_axes
    v_glob_i = A_i @ joint.local_axis_i

    if joint.joint_type == JointType.REVOLUTE:
        ref_i_glob = A_i @ joint.local_a_i
        ref_j_glob = A_j @ joint.local_a_j
        y_axis = np.cross(v_glob_i, ref_i_glob)
        proj_j = ref_j_glob - np.dot(ref_j_glob, v_glob_i) * v_glob_i
        norm_p = np.linalg.norm(proj_j)
        if norm_p > 1e-8:
            proj_j = proj_j / norm_p
        theta = float(np.arctan2(np.dot(y_axis, proj_j), np.dot(ref_i_glob, proj_j)))
        return float(sign) * theta

    if joint.joint_type == JointType.PRISMATIC:
        s_i_glob = A_i @ joint.local_pos_i
        s_j_glob = A_j @ joint.local_pos_j
        d = (joint.body_j.cog + s_j_glob) - (joint.body_i.cog + s_i_glob)
        dist = float(np.dot(d, v_glob_i))
        return float(sign) * dist

    return 0.0


@dataclass
class ChainStep:
    """One directed joint step from `parent_body` to `child_body` along a kinematic chain."""
    joint: object
    parent_body: object
    child_body: object
    direction_sign: int       # +1 if parent == joint.body_i and child == joint.body_j, else -1
    dof_index: int | None     # 0..N_dof-1 for REVOLUTE/PRISMATIC, None for FIXED
    F_i: np.ndarray = field(repr=False, default=None)
    F_j: np.ndarray = field(repr=False, default=None)


@dataclass
class FKState:
    """Result of a pure Forward Kinematics evaluation for a vector `q`."""
    q: np.ndarray
    body_poses: dict          # body_name -> (pos_m (3,), rot_3x3 (3,3))
    tcp_pos: np.ndarray       # (3,) global TCP position in meters
    tcp_rot: np.ndarray       # (3,3) global TCP rotation matrix
    joint_anchors: list       # list of (3,) global anchor positions for each active DOF
    joint_axes: list          # list of (3,) global signed unit axis vectors for each active DOF


@dataclass
class IKResult:
    """Result of an Inverse Kinematics solve."""
    success: bool
    q: np.ndarray
    iterations: int
    pos_error_mm: float
    rot_error_deg: float
    tcp_pos: np.ndarray
    tcp_rot: np.ndarray
    saturated_joints: list
    message: str


@dataclass
class TrajectoryWaypoint:
    """One timestamped Cartesian / Joint-Space waypoint for Step 3 trajectory planning."""
    time_s: float
    pos_m: np.ndarray
    rot_mat: np.ndarray
    segment_type: str = "MOVEL"   # "MOVEL" (Cartesian Linear + SLERP) or "MOVEJ" (Joint-Space)
    label: str = ""


@dataclass
class TrajectoryResult:
    """Complete solved joint-space and task-space trajectory ready for preview & spline export."""
    success: bool
    times: np.ndarray                # (N,) timestamps in seconds starting at 0.0
    q_traj: np.ndarray               # (N, N_dof) unwrapped SI joint positions (rad or m)
    qd_traj: np.ndarray              # (N, N_dof) SI joint velocities (rad/s or m/s)
    qdd_traj: np.ndarray             # (N, N_dof) SI joint accelerations (rad/s^2 or m/s^2)
    tcp_pos_traj: np.ndarray         # (N, 3) achieved global TCP positions in meters
    target_pos_traj: np.ndarray      # (N, 3) reference Cartesian positions in meters
    pos_err_mm_traj: np.ndarray      # (N,) Cartesian tracking error in mm
    waypoint_indices: list           # sample index for each user waypoint
    waypoint_converged: list         # bool per user waypoint
    waypoint_errors_mm: list         # pos error (mm) at each user waypoint
    waypoint_rot_errors_deg: list    # rot error (deg) at each user waypoint
    failed_samples: int
    max_pos_error_mm: float
    max_rot_error_deg: float
    saturated_joints: list
    message: str


def _quintic_step(tau: float) -> float:
    """Minimum-jerk quintic time-scaling s(tau) = 10*tau^3 - 15*tau^4 + 6*tau^5 on [0, 1]."""
    u = float(np.clip(tau, 0.0, 1.0))
    return u * u * u * (10.0 + u * (-15.0 + 6.0 * u))


def _build_c2_clamped_bpoly(t_knots: np.ndarray, y_knots: np.ndarray) -> BPoly:
    """
    Constructs a C2-continuous piecewise quintic BPoly through `(t_knots, y_knots)`
    with exact zero velocity and zero acceleration at `t_knots[0]` and `t_knots[-1]`.
    `y_knots` has shape `(M, D)`.
    """
    m = len(t_knots)
    if m == 2:
        derivs = [
            [y_knots[0], np.zeros_like(y_knots[0]), np.zeros_like(y_knots[0])],
            [y_knots[1], np.zeros_like(y_knots[1]), np.zeros_like(y_knots[1])],
        ]
        return BPoly.from_derivatives(t_knots, derivs)

    cs = CubicSpline(t_knots, y_knots, axis=0, bc_type="clamped")
    v_int = cs(t_knots, 1)
    a_int = cs(t_knots, 2)
    derivs = [[y_knots[0], np.zeros_like(y_knots[0]), np.zeros_like(y_knots[0])]]
    for idx in range(1, m - 1):
        derivs.append([y_knots[idx], v_int[idx], a_int[idx]])
    derivs.append([y_knots[-1], np.zeros_like(y_knots[-1]), np.zeros_like(y_knots[-1])])
    return BPoly.from_derivatives(t_knots, derivs)


class KinematicChain:
    """
    Robot-agnostic kinematic chain discovered directly from SimPhant `RigidBody`, `Joint`,
    and `RFrame` objects. Supports arbitrary serial chains of REVOLUTE, PRISMATIC, and FIXED
    joints, plus automatic rigid propagation to side-branch subtrees and attached RFrames.
    """
    SUPPORTED_JOINT_TYPES = (JointType.REVOLUTE, JointType.PRISMATIC, JointType.FIXED)
    ACTIVE_JOINT_TYPES = (JointType.REVOLUTE, JointType.PRISMATIC)

    def __init__(self, physics_bodies, joints_list, base_body_name, ee_body_name,
                 tcp_rf=None, rframes_list=None):
        self.physics_bodies = physics_bodies
        self.joints_list = joints_list
        self.rframes_list = rframes_list if rframes_list is not None else []

        if base_body_name not in physics_bodies:
            raise RoboticsChainError(f"Base body '{base_body_name}' not found in scene.")
        if ee_body_name not in physics_bodies:
            raise RoboticsChainError(f"End-Effector body '{ee_body_name}' not found in scene.")
        if base_body_name == ee_body_name:
            raise RoboticsChainError("Base Body and End-Effector Body must be different bodies.")

        self.base_body = physics_bodies[base_body_name]
        self.ee_body = physics_bodies[ee_body_name]
        self.tcp_rf = tcp_rf

        self.chain_steps: list[ChainStep] = []
        self.active_joints: list = []
        self.active_steps: list[ChainStep] = []
        self.chain_bodies: list = []
        self.side_branch_bodies: dict[str, list] = {}  # chain_body_name -> list of side-branch RigidBody objects

        self._discover_chain()
        self._discover_side_branches()
        self._capture_tcp_offset()
        self._capture_initial_snapshot()
        self._pack_numba_arrays()
        self._cache_moved_scene_elements()

        self.current_q = self.initial_q.copy()

    @property
    def num_dof(self) -> int:
        return len(self.active_joints)

    def is_base_fixed_to_ground(self, joints_list=None) -> bool:
        """
        Returns True if `self.base_body` is rigidly constrained to `Ground` via one or more
        enabled `JointType.FIXED` joints (or if `self.base_body` itself is `Ground`).
        """
        if getattr(self.base_body, 'is_ground', False):
            return True
        if not getattr(self.base_body, 'enabled', True):
            return False

        joints = joints_list if joints_list is not None else self.joints_list
        fixed_adj = {}
        for joint in joints:
            if not getattr(joint, 'enabled', True) or joint.joint_type != JointType.FIXED:
                continue
            b_i = joint.body_i
            b_j = joint.body_j
            if b_i is None or b_j is None:
                continue
            if not getattr(b_i, 'enabled', True) or not getattr(b_j, 'enabled', True):
                continue
            fixed_adj.setdefault(b_i.name, []).append(b_j)
            fixed_adj.setdefault(b_j.name, []).append(b_i)

        visited = {self.base_body.name}
        queue = deque([self.base_body])
        while queue:
            curr = queue.popleft()
            if getattr(curr, 'is_ground', False):
                return True
            for nbr in fixed_adj.get(curr.name, ()):
                if nbr.name not in visited:
                    visited.add(nbr.name)
                    queue.append(nbr)
        return False

    # ------------------------------------------------------------------
    # Graph Discovery & Subtree Bookkeeping
    # ------------------------------------------------------------------
    def _discover_chain(self):
        """Finds the kinematic path of enabled joints from `base_body` to `ee_body` via BFS."""
        adj = {}
        for joint in self.joints_list:
            if not getattr(joint, 'enabled', True):
                continue
            b_i = joint.body_i
            b_j = joint.body_j
            if b_i is None or b_j is None:
                continue
            if not getattr(b_i, 'enabled', True) or not getattr(b_j, 'enabled', True):
                continue
            # Do not traverse through Ground unless Ground was explicitly chosen as Base Body
            if b_i.is_ground and b_i.name != self.base_body.name:
                continue
            if b_j.is_ground and b_j.name != self.base_body.name:
                continue
            adj.setdefault(b_i.name, []).append((b_j.name, joint, +1))
            adj.setdefault(b_j.name, []).append((b_i.name, joint, -1))

        queue = deque([self.base_body.name])
        prev = {self.base_body.name: None}

        while queue:
            curr_name = queue.popleft()
            if curr_name == self.ee_body.name:
                break
            for nbr_name, joint, sign in adj.get(curr_name, []):
                if nbr_name not in prev:
                    prev[nbr_name] = (curr_name, joint, sign)
                    queue.append(nbr_name)

        if self.ee_body.name not in prev:
            raise RoboticsChainError(
                f"No connected path of enabled joints found between "
                f"'{self.base_body.name}' and '{self.ee_body.name}'."
            )

        # Reconstruct path from base_body -> ee_body
        raw_edges = []
        cursor = self.ee_body.name
        while prev[cursor] is not None:
            parent_name, joint, sign = prev[cursor]
            raw_edges.append((parent_name, cursor, joint, sign))
            cursor = parent_name
        raw_edges.reverse()

        self.chain_bodies = [self.base_body]
        dof_counter = 0
        for parent_name, child_name, joint, sign in raw_edges:
            if joint.joint_type not in self.SUPPORTED_JOINT_TYPES:
                raise RoboticsChainError(
                    f"Joint '{joint.name}' on the path has type '{joint.joint_type.name}', "
                    f"which is not supported in a serial kinematic chain (use REVOLUTE, PRISMATIC, or FIXED)."
                )
            parent_body = self.physics_bodies[parent_name]
            child_body = self.physics_bodies[child_name]

            if joint.joint_type in self.ACTIVE_JOINT_TYPES:
                dof_idx = dof_counter
                dof_counter += 1
            else:
                dof_idx = None

            step = ChainStep(
                joint=joint,
                parent_body=parent_body,
                child_body=child_body,
                direction_sign=sign,
                dof_index=dof_idx,
                F_i=_joint_triad_i(joint),
                F_j=_joint_triad_j(joint),
            )
            self.chain_steps.append(step)
            self.chain_bodies.append(child_body)
            if dof_idx is not None:
                self.active_joints.append(joint)
                self.active_steps.append(step)

        if self.num_dof == 0:
            raise RoboticsChainError(
                f"Path from '{self.base_body.name}' to '{self.ee_body.name}' contains "
                f"no movable (Revolute or Prismatic) joints."
            )

    def _discover_side_branches(self):
        """
        For each moving body in the chain, finds any downstream side-branch bodies
        (e.g. a second arm on a torso, or gripper fingers on a wrist) so they ride
        along rigidly whenever that chain body moves.
        """
        chain_body_names = {b.name for b in self.chain_bodies}
        adj = {}
        for joint in self.joints_list:
            if not getattr(joint, 'enabled', True):
                continue
            b_i, b_j = joint.body_i, joint.body_j
            if b_i is None or b_j is None or b_i.is_ground or b_j.is_ground:
                continue
            if not getattr(b_i, 'enabled', True) or not getattr(b_j, 'enabled', True):
                continue
            adj.setdefault(b_i.name, []).append(b_j.name)
            adj.setdefault(b_j.name, []).append(b_i.name)

        visited_global = set(chain_body_names)
        # Skip base_body (index 0) because base_body stays stationary in chain FK
        for chain_body in self.chain_bodies[1:]:
            branch_list = []
            queue = deque([chain_body.name])
            while queue:
                curr = queue.popleft()
                for nbr in adj.get(curr, []):
                    if nbr not in visited_global:
                        visited_global.add(nbr)
                        nbr_body = self.physics_bodies.get(nbr)
                        if nbr_body is not None and not nbr_body.is_ground:
                            branch_list.append(nbr_body)
                            queue.append(nbr)
            self.side_branch_bodies[chain_body.name] = branch_list

    def _capture_tcp_offset(self):
        """Captures the constant local offset of the TCP relative to `ee_body`."""
        A_ee = self.ee_body.principal_axes
        r_ee = self.ee_body.cog

        if self.tcp_rf is not None:
            if getattr(self.tcp_rf, 'parent_body', None) is self.ee_body and hasattr(self.tcp_rf, 'local_position'):
                self.tcp_local_pos = self.tcp_rf.local_position.copy()
                self.tcp_local_rot = self.tcp_rf.local_rotation.copy()
            else:
                self.tcp_local_pos = A_ee.T @ (self.tcp_rf.position - r_ee)
                self.tcp_local_rot = A_ee.T @ self.tcp_rf.transform_matrix
        else:
            self.tcp_local_pos = np.zeros(3, dtype=float)
            self.tcp_local_rot = np.eye(3, dtype=float)

    def _capture_initial_snapshot(self):
        """Stores the initial scene state so 'Reset to Initial Pose' is exact."""
        self.initial_q = self.read_current_q_from_bodies()

        self.initial_body_states = {}
        for name, body in self.physics_bodies.items():
            if body.is_ground:
                continue
            self.initial_body_states[name] = (
                body.cog.copy(),
                body.principal_axes.copy(),
                body.pos_angles.copy(),
                body.I_check.copy() if getattr(body, 'I_check', None) is not None else None,
            )

        self.initial_rframe_states = {}
        self.rframe_body_attachments = []  # [(rf, parent_body, p_local, R_local)]
        for rf in self.rframes_list:
            if rf.name == "Global_RF":
                continue
            self.initial_rframe_states[rf.name] = (
                rf.position.copy(),
                rf.orientation.copy(),
                rf.transform_matrix.copy(),
            )
            if getattr(rf, 'is_cog', False):
                continue
            # Attach non-CoG RFrame to its parent_body (or to ee_body if it is explicitly chosen as tcp_rf)
            parent = getattr(rf, 'parent_body', None)
            if (parent is None or getattr(parent, 'is_ground', False)) and rf is self.tcp_rf:
                parent = self.ee_body
            if parent is not None and not getattr(parent, 'is_ground', False):
                if getattr(rf, 'parent_body', None) is parent and hasattr(rf, 'local_position'):
                    p_loc = rf.local_position.copy()
                    R_loc = rf.local_rotation.copy()
                else:
                    p_loc = parent.principal_axes.T @ (rf.position - parent.cog)
                    R_loc = parent.principal_axes.T @ rf.transform_matrix
                self.rframe_body_attachments.append((rf, parent, p_loc, R_loc))

    def _pack_numba_arrays(self):
        """Pre-packs contiguous float64/int32 arrays for Numba JIT FK, Jacobian, and DLS IK."""
        n_steps = len(self.chain_steps)
        self._nb_step_types = np.empty(n_steps, dtype=np.int32)
        self._nb_step_signs = np.empty(n_steps, dtype=np.float64)
        self._nb_step_dof_idx = np.empty(n_steps, dtype=np.int32)
        self._nb_p_parent = np.empty((n_steps, 3), dtype=np.float64)
        self._nb_p_child = np.empty((n_steps, 3), dtype=np.float64)
        self._nb_F_parent = np.empty((n_steps, 3, 3), dtype=np.float64)
        self._nb_F_child_T = np.empty((n_steps, 3, 3), dtype=np.float64)
        self._nb_axis_parent = np.empty((n_steps, 3), dtype=np.float64)

        for s, step in enumerate(self.chain_steps):
            joint = step.joint
            if joint.joint_type == JointType.REVOLUTE:
                self._nb_step_types[s] = 1
            elif joint.joint_type == JointType.PRISMATIC:
                self._nb_step_types[s] = 2
            else:
                self._nb_step_types[s] = 0

            self._nb_step_signs[s] = float(step.direction_sign)
            self._nb_step_dof_idx[s] = step.dof_index if step.dof_index is not None else -1

            if step.direction_sign == 1:
                self._nb_p_parent[s] = joint.local_pos_i
                self._nb_p_child[s] = joint.local_pos_j
                self._nb_F_parent[s] = step.F_i
                self._nb_F_child_T[s] = step.F_j.T
                self._nb_axis_parent[s] = joint.local_axis_i
            else:
                self._nb_p_parent[s] = joint.local_pos_j
                self._nb_p_child[s] = joint.local_pos_i
                self._nb_F_parent[s] = step.F_j
                self._nb_F_child_T[s] = step.F_i.T
                self._nb_axis_parent[s] = joint.local_axis_j

        self._nb_dof_types = np.empty(self.num_dof, dtype=np.int32)
        for k, joint in enumerate(self.active_joints):
            self._nb_dof_types[k] = 1 if joint.joint_type == JointType.REVOLUTE else 2

        self._nb_tcp_local_pos = np.ascontiguousarray(self.tcp_local_pos, dtype=np.float64)
        self._nb_tcp_local_rot = np.ascontiguousarray(self.tcp_local_rot, dtype=np.float64)

    def _cache_moved_scene_elements(self):
        """Caches only the RFrames and Joints affected by moving this chain to avoid redundant VTK updates."""
        moved_names = {b.name for b in self.chain_bodies[1:]}
        for branches in self.side_branch_bodies.values():
            for b in branches:
                moved_names.add(b.name)
        self._moved_body_names = moved_names
        self._moved_rframe_attachments = [
            item for item in self.rframe_body_attachments if item[1].name in moved_names
        ]
        self._moved_cog_rframes = [
            rf for rf in self.rframes_list
            if getattr(rf, 'is_cog', False) and rf.parent_body and rf.parent_body.name in moved_names
        ]
        self._moved_joints = [
            j for j in self.joints_list
            if j.body_i.name in moved_names or j.body_j.name in moved_names
        ]

    # ------------------------------------------------------------------
    # Joint Coordinate & Limit Helpers
    # ------------------------------------------------------------------
    def read_current_q_from_bodies(self) -> np.ndarray:
        """Reads the current joint coordinates `q` (in SI: rad or m) from the scene bodies."""
        q = np.zeros(self.num_dof, dtype=float)
        for step in self.active_steps:
            q[step.dof_index] = measure_joint_coordinate_si(step.joint, step.direction_sign)
        return q

    def get_joint_bounds(self, enforce_limits=True):
        """
        Returns `(q_min, q_max, is_bounded)` arrays of length `num_dof` in SI units.
        """
        q_min = np.full(self.num_dof, -np.inf, dtype=float)
        q_max = np.full(self.num_dof, +np.inf, dtype=float)
        is_bounded = np.zeros(self.num_dof, dtype=bool)

        if not enforce_limits:
            return q_min, q_max, is_bounded

        for idx, joint in enumerate(self.active_joints):
            if getattr(joint, 'limits_enabled', False):
                lo = float(getattr(joint, 'limit_min', -np.pi))
                hi = float(getattr(joint, 'limit_max', +np.pi))
                if lo > hi:
                    lo, hi = hi, lo
                q_min[idx] = lo
                q_max[idx] = hi
                is_bounded[idx] = True
        return q_min, q_max, is_bounded

    def clamp_q(self, q, enforce_limits=True) -> np.ndarray:
        """Clamps joint vector `q` to active joint limits when `enforce_limits` is True."""
        q_arr = np.asarray(q, dtype=float).copy()
        if not enforce_limits:
            return q_arr
        q_min, q_max, is_bounded = self.get_joint_bounds(enforce_limits=True)
        for i in range(self.num_dof):
            if is_bounded[i]:
                q_arr[i] = float(np.clip(q_arr[i], q_min[i], q_max[i]))
        return q_arr

    # ------------------------------------------------------------------
    # Forward Kinematics & Scene Application
    # ------------------------------------------------------------------
    def forward_kinematics(self, q) -> FKState:
        """
        Pure mathematical Forward Kinematics pass for joint vector `q` (SI units: rad / m),
        accelerated via Numba `@njit`. Does NOT mutate scene bodies or VTK actors.
        """
        q_arr = np.ascontiguousarray(q, dtype=np.float64)
        if q_arr.shape != (self.num_dof,):
            raise ValueError(f"Expected q of shape ({self.num_dof},), got {q_arr.shape}.")

        base_pos = np.ascontiguousarray(self.base_body.cog, dtype=np.float64)
        base_rot = np.ascontiguousarray(self.base_body.principal_axes, dtype=np.float64)

        body_pos, body_rot, joint_anchors, joint_axes, tcp_pos, tcp_rot = forward_kinematics_chain_numba(
            q_arr,
            base_pos,
            base_rot,
            self._nb_step_types,
            self._nb_step_signs,
            self._nb_step_dof_idx,
            self._nb_p_parent,
            self._nb_p_child,
            self._nb_F_parent,
            self._nb_F_child_T,
            self._nb_axis_parent,
            self._nb_tcp_local_pos,
            self._nb_tcp_local_rot,
        )

        body_poses = {
            body.name: (body_pos[idx], body_rot[idx])
            for idx, body in enumerate(self.chain_bodies)
        }

        return FKState(
            q=q_arr.copy(),
            body_poses=body_poses,
            tcp_pos=tcp_pos,
            tcp_rot=tcp_rot,
            joint_anchors=joint_anchors,
            joint_axes=joint_axes,
        )

    def apply_fk_to_scene(self, q, app=None, render=True, perf_out=None) -> FKState:
        """
        Evaluates Forward Kinematics at `q` and updates moved chain bodies, side-branch bodies,
        CoG and attached RFrames, Joints, Forces, Springs, and Bushings in the 3D scene.
        """
        t0 = perf_counter()
        # Rewind any cached simulation playback state FIRST so it does not overwrite our new pose
        if app is not None and hasattr(app, 'invalidate_results'):
            app.invalidate_results()
        t_inv = perf_counter()

        fk = self.forward_kinematics(q)
        self.current_q = fk.q.copy()
        t_fk = perf_counter()

        # 1. Update chain bodies and propagate rigid deltas to side-branch subtrees
        for chain_body in self.chain_bodies[1:]:
            new_pos, new_rot = fk.body_poses[chain_body.name]
            old_pos, old_rot, _, _ = self.initial_body_states[chain_body.name]

            self._set_body_pose(chain_body, new_pos, new_rot)

            branches = self.side_branch_bodies.get(chain_body.name)
            if branches:
                delta_rot = new_rot @ old_rot.T
                for branch_body in branches:
                    b_init_pos, b_init_rot, _, _ = self.initial_body_states[branch_body.name]
                    b_pos = new_pos + delta_rot @ (b_init_pos - old_pos)
                    b_rot = delta_rot @ b_init_rot
                    self._set_body_pose(branch_body, b_pos, b_rot)

        # 2. Update non-CoG RFrames attached to moved bodies (including tool0 / joint RFs)
        for rf, parent_body, p_loc, R_loc in self._moved_rframe_attachments:
            rf.position = parent_body.cog + parent_body.principal_axes @ p_loc
            rf.transform_matrix = parent_body.principal_axes @ R_loc
            rf.orientation = matrix_to_pos_angles_deg_numba(rf.transform_matrix)
            rf.update_transform()

        # 3. Refresh moved scene visual actors (CoG RFrames, Joints, Forces, Springs, Bushings)
        t_gl_ms = self._refresh_scene_actors(app=app, render=render, only_moved=True, return_render_ms=True)
        t_end = perf_counter()

        if perf_out is not None:
            perf_out["inv_ms"] = (t_inv - t0) * 1000.0
            perf_out["fk_ms"] = (t_fk - t_inv) * 1000.0
            perf_out["vtk_ms"] = ((t_end - t_fk) * 1000.0) - t_gl_ms
            perf_out["gl_ms"] = t_gl_ms

        return fk

    def restore_initial_pose(self, app=None, render=True):
        """Restores every body and RFrame in the scene back to the snapshot taken at chain init."""
        for name, (cog, rot, pos_angles, i_check) in self.initial_body_states.items():
            body = self.physics_bodies.get(name)
            if body is None or body.is_ground:
                continue
            body.cog = cog.copy()
            body.principal_axes = rot.copy()
            body.pos_angles = pos_angles.copy()
            if i_check is not None:
                body.I_check = i_check.copy()
            body.update_graphics_matrix(body.cog, body.principal_axes)

        for rf in self.rframes_list:
            if rf.name in self.initial_rframe_states:
                pos, ori, mat = self.initial_rframe_states[rf.name]
                rf.position = pos.copy()
                rf.orientation = ori.copy()
                rf.transform_matrix = mat.copy()
                rf.update_transform()

        self.current_q = self.initial_q.copy()
        self._refresh_scene_actors(app=app, render=render, only_moved=False)

    @staticmethod
    def _set_body_pose(body, new_pos, new_rot):
        body.cog = new_pos.copy()
        body.principal_axes = new_rot.copy()
        body.pos_angles = matrix_to_pos_angles_deg_numba(body.principal_axes)
        if getattr(body, 'principal_inertia', None) is not None:
            body.I_check = (body.principal_axes * body.principal_inertia) @ body.principal_axes.T
        body.update_graphics_matrix(body.cog, body.principal_axes)

    def _refresh_scene_actors(self, app=None, render=True, only_moved=False, return_render_ms=False):
        current_scale = self.rframes_list[0].base_scale if self.rframes_list else 10.0

        cog_rframes = self._moved_cog_rframes if only_moved else [
            rf for rf in self.rframes_list
            if getattr(rf, 'is_cog', False) and rf.parent_body and not rf.parent_body.is_ground
        ]
        for rf in cog_rframes:
            rf.position = rf.parent_body.cog
            rf.transform_matrix = rf.parent_body.principal_axes
            rf.orientation = rf.parent_body.pos_angles
            rf.update_transform()

        joints_to_update = self._moved_joints if only_moved else self.joints_list
        for joint in joints_to_update:
            joint.update_transform(current_scale)

        render_ms = 0.0
        if app is not None:
            moved_names = self._moved_body_names
            for force in getattr(app, 'forces_list', []):
                if not only_moved or force.parent_body.name in moved_names:
                    force.update_transform(current_scale)
            for spring in getattr(app, 'springs_list', []):
                if not only_moved or spring.body_i.name in moved_names or spring.body_j.name in moved_names:
                    spring.update_transform(current_scale)
            for bushing in getattr(app, 'bushings_list', []):
                if not only_moved or bushing.body_i.name in moved_names or bushing.body_j.name in moved_names:
                    bushing.update_transform(current_scale)
            if getattr(app, 'selected_body', None) and app.selected_body in self.physics_bodies:
                if not only_moved or app.selected_body in moved_names:
                    app.display_body_properties(self.physics_bodies[app.selected_body])
            if render and getattr(app, 'plotter', None) is not None:
                t_r0 = perf_counter()
                app.plotter.render()
                render_ms = (perf_counter() - t_r0) * 1000.0
        if return_render_ms:
            return render_ms

    # ------------------------------------------------------------------
    # Analytical Geometric Jacobian & Damped Least-Squares IK Solver
    # ------------------------------------------------------------------
    def compute_jacobian(self, q, fk_state: FKState | None = None) -> np.ndarray:
        """
        Computes the exact 6 x N_dof geometric Jacobian J(q) in global coordinates via Numba `@njit`.
        """
        fk = fk_state if fk_state is not None else self.forward_kinematics(q)
        anchors = np.ascontiguousarray(fk.joint_anchors, dtype=np.float64)
        axes = np.ascontiguousarray(fk.joint_axes, dtype=np.float64)
        p_tcp = np.ascontiguousarray(fk.tcp_pos, dtype=np.float64)
        return compute_geometric_jacobian_numba(self._nb_dof_types, anchors, axes, p_tcp)

    @staticmethod
    def compute_pose_error(tcp_pos, tcp_rot, target_pos, target_rot=None, mode="6D"):
        """
        Computes the 6D task-space error vector `e = [e_pos; e_rot]` in global coordinates,
        plus scalar `(pos_err_m, rot_err_rad)` via Numba `@njit`.
        """
        if mode == "PositionOnly" or target_rot is None:
            mode_code = 1
            t_rot = np.eye(3, dtype=np.float64)
        elif mode == "PositionPlusAxis":
            mode_code = 2
            t_rot = np.ascontiguousarray(target_rot, dtype=np.float64)
        else:
            mode_code = 0
            t_rot = np.ascontiguousarray(target_rot, dtype=np.float64)

        return compute_pose_error_numba(
            np.ascontiguousarray(tcp_pos, dtype=np.float64),
            np.ascontiguousarray(tcp_rot, dtype=np.float64),
            np.ascontiguousarray(target_pos, dtype=np.float64),
            t_rot,
            mode_code,
        )

    def solve_ik(
        self,
        target_pos,
        target_rot=None,
        q_init=None,
        mode="6D",
        enforce_limits=True,
        pos_tol_mm=0.1,
        rot_tol_deg=0.1,
        max_iters=150,
        damping=0.05,
        max_step_rad=0.35,
        allow_restarts=True,
    ) -> IKResult:
        """
        Solves Inverse Kinematics for `(target_pos, target_rot)` using Damped Least-Squares
        (Levenberg-Marquardt) with active-set box-constraint projection and optional multi-start fallback.
        """
        q_start = self.current_q.copy() if q_init is None else np.asarray(q_init, dtype=float).copy()
        q_min, q_max, is_bounded = self.get_joint_bounds(enforce_limits=enforce_limits)

        # Build candidate starting configurations (primary q_start + mid-range / random fallbacks if allowed)
        q_mid = np.zeros(self.num_dof, dtype=float)
        for i in range(self.num_dof):
            if is_bounded[i]:
                q_mid[i] = 0.5 * (q_min[i] + q_max[i])

        candidates = [self.clamp_q(q_start, enforce_limits=enforce_limits)]
        if allow_restarts:
            if not np.allclose(candidates[0], q_mid, atol=1e-3):
                candidates.append(self.clamp_q(q_mid, enforce_limits=enforce_limits))
            rng = np.random.default_rng(42)
            for _ in range(2):
                span = np.where(is_bounded, 0.35 * (q_max - q_min), 0.8)
                q_rand = q_mid + rng.uniform(-1.0, 1.0, size=self.num_dof) * span
                candidates.append(self.clamp_q(q_rand, enforce_limits=enforce_limits))

        best_result = None
        for attempt_idx, q_seed in enumerate(candidates):
            res = self._solve_ik_single(
                target_pos=target_pos,
                target_rot=target_rot,
                q_seed=q_seed,
                mode=mode,
                enforce_limits=enforce_limits,
                q_min=q_min,
                q_max=q_max,
                is_bounded=is_bounded,
                q_mid=q_mid,
                pos_tol_mm=pos_tol_mm,
                rot_tol_deg=rot_tol_deg,
                max_iters=max_iters if attempt_idx == 0 else max(80, max_iters // 2),
                damping=damping,
                max_step_rad=max_step_rad,
            )
            if res.success:
                return res
            if best_result is None or (
                res.pos_error_mm + 2.0 * res.rot_error_deg
                < best_result.pos_error_mm + 2.0 * best_result.rot_error_deg
            ):
                best_result = res

        return best_result

    def _solve_ik_single(
        self,
        target_pos,
        target_rot,
        q_seed,
        mode,
        enforce_limits,
        q_min,
        q_max,
        is_bounded,
        q_mid,
        pos_tol_mm,
        rot_tol_deg,
        max_iters,
        damping,
        max_step_rad,
    ) -> IKResult:
        pos_tol_m = max(float(pos_tol_mm) * 1e-3, 1e-7)
        rot_tol_rad = max(float(np.deg2rad(rot_tol_deg)), 1e-6)
        check_rot = (mode != "PositionOnly") and (target_rot is not None)

        if mode == "PositionOnly" or not check_rot:
            mode_code = 1
            t_rot = np.eye(3, dtype=np.float64)
        elif mode == "PositionPlusAxis":
            mode_code = 2
            t_rot = np.ascontiguousarray(target_rot, dtype=np.float64)
        else:
            mode_code = 0
            t_rot = np.ascontiguousarray(target_rot, dtype=np.float64)

        q, iters_used, pos_err_m, rot_err_rad, tcp_pos, tcp_rot = solve_ik_dls_numba(
            np.ascontiguousarray(q_seed, dtype=np.float64),
            np.ascontiguousarray(self.base_body.cog, dtype=np.float64),
            np.ascontiguousarray(self.base_body.principal_axes, dtype=np.float64),
            self._nb_step_types,
            self._nb_step_signs,
            self._nb_step_dof_idx,
            self._nb_p_parent,
            self._nb_p_child,
            self._nb_F_parent,
            self._nb_F_child_T,
            self._nb_axis_parent,
            self._nb_dof_types,
            self._nb_tcp_local_pos,
            self._nb_tcp_local_rot,
            np.ascontiguousarray(target_pos, dtype=np.float64),
            t_rot,
            mode_code,
            bool(enforce_limits),
            np.ascontiguousarray(q_min, dtype=np.float64),
            np.ascontiguousarray(q_max, dtype=np.float64),
            np.ascontiguousarray(is_bounded, dtype=np.bool_),
            np.ascontiguousarray(q_mid, dtype=np.float64),
            pos_tol_m,
            rot_tol_rad,
            int(max_iters),
            float(damping),
            float(max_step_rad),
        )

        pos_err_mm = float(pos_err_m) * 1000.0
        rot_err_deg = float(np.rad2deg(rot_err_rad))
        converged = (pos_err_m <= pos_tol_m) and (not check_rot or rot_err_rad <= rot_tol_rad)

        saturated = []
        if enforce_limits:
            for idx, joint in enumerate(self.active_joints):
                if is_bounded[idx]:
                    if abs(q[idx] - q_min[idx]) < 1e-4 or abs(q[idx] - q_max[idx]) < 1e-4:
                        saturated.append(joint.name)

        if converged:
            msg = (
                f"[OK] IK Converged in {iters_used} iterations | "
                f"Pos err: {pos_err_mm:.3f} mm"
                + (f" | Rot err: {rot_err_deg:.3f} deg" if check_rot else "")
            )
        else:
            sat_info = f" | Limit reached: {', '.join(saturated)}" if saturated else ""
            msg = (
                f"[WARN] Target not fully reached ({iters_used} iters) | "
                f"Best Pos err: {pos_err_mm:.2f} mm"
                + (f" | Rot err: {rot_err_deg:.2f} deg" if check_rot else "")
                + sat_info
            )

        return IKResult(
            success=converged,
            q=q,
            iterations=int(iters_used),
            pos_error_mm=pos_err_mm,
            rot_error_deg=rot_err_deg,
            tcp_pos=tcp_pos,
            tcp_rot=tcp_rot,
            saturated_joints=saturated,
            message=msg,
        )

    # ------------------------------------------------------------------
    # Step 3: Cartesian / Joint-Space Trajectory Planner & Motion Export
    # ------------------------------------------------------------------
    def _unwrap_joint_step(self, q_new: np.ndarray, q_prev: np.ndarray, enforce_limits: bool) -> np.ndarray:
        """
        Keeps Revolute joint coordinates continuous relative to `q_prev` (avoiding +/- 2*pi jumps)
        while respecting active `[q_min, q_max]` stroke bounds.
        """
        q_out = np.asarray(q_new, dtype=float).copy()
        q_min, q_max, is_bounded = self.get_joint_bounds(enforce_limits=enforce_limits)
        for k, joint in enumerate(self.active_joints):
            if joint.joint_type != JointType.REVOLUTE:
                continue
            diff = (q_out[k] - q_prev[k] + np.pi) % (2.0 * np.pi) - np.pi
            cand = q_prev[k] + diff
            if enforce_limits and is_bounded[k]:
                if q_min[k] - 1e-6 <= cand <= q_max[k] + 1e-6:
                    q_out[k] = float(np.clip(cand, q_min[k], q_max[k]))
                else:
                    q_out[k] = float(np.clip(q_out[k], q_min[k], q_max[k]))
            else:
                q_out[k] = cand
        return q_out

    def plan_trajectory(
        self,
        waypoints: list[TrajectoryWaypoint],
        sample_rate_hz: float = 100.0,
        timing_mode: str = "quintic_stop",
        ik_mode: str = "6D",
        enforce_limits: bool = True,
        pos_tol_mm: float = 0.2,
        rot_tol_deg: float = 0.2,
        max_iters: int = 150,
        damping: float = 0.05,
        q_seed: np.ndarray | None = None,
    ) -> TrajectoryResult:
        """
        Plans a smooth, C2-continuous time-parameterized trajectory across 2 or more waypoints.
        Supports:
          - `timing_mode == "quintic_stop"`: Minimum-jerk quintic rest-to-rest on each segment,
            allowing per-segment mixing of `"MOVEL"` (Cartesian Linear + SLERP) and `"MOVEJ"` (Joint-Space).
          - `timing_mode == "smooth_spline"`: Global C2 pass-through spline across all waypoints
            with exact zero velocity & zero acceleration at start and end.
        """
        if len(waypoints) < 2:
            raise ValueError("At least 2 waypoints are required to generate a trajectory.")

        wp_times = np.array([float(wp.time_s) for wp in waypoints], dtype=float)
        if wp_times[0] < 0.0:
            raise ValueError("First waypoint time must be >= 0.0 s.")
        if np.any(np.diff(wp_times) <= 1e-6):
            raise ValueError("Waypoint times must be strictly increasing (t_0 < t_1 < ... < t_N).")

        rate = max(float(sample_rate_hz), 10.0)
        q_initial_seed = self.clamp_q(
            self.current_q.copy() if q_seed is None else np.asarray(q_seed, dtype=float).copy(),
            enforce_limits=enforce_limits,
        )
        check_rot = (ik_mode != "PositionOnly")

        # 1. Build exact sample timeline hitting every user waypoint timestamp.
        #    Also, if Waypoint 0 is at t_0 > 0 and is NOT already at Home (q = 0), prepend Home (q = 0)
        #    at t = 0.0 so the robot ramps smoothly from Zero All (q = 0) -> Waypoint 0 without teleporting!
        q_zero_start = self.clamp_q(np.zeros(self.num_dof, dtype=float), enforce_limits=enforce_limits)
        fk_zero_start = self.forward_kinematics(q_zero_start)
        _, p_err_z0, r_err_z0 = self.compute_pose_error(
            fk_zero_start.tcp_pos, fk_zero_start.tcp_rot, waypoints[0].pos_m, waypoints[0].rot_mat, mode=ik_mode
        )
        wp0_is_zero = (p_err_z0 * 1000.0 <= pos_tol_mm) and (
            not check_rot or np.rad2deg(r_err_z0) <= rot_tol_deg
        )

        prepended_home = (wp_times[0] > 1e-6) and (not wp0_is_zero)
        if prepended_home:
            eff_waypoints = [
                TrajectoryWaypoint(
                    time_s=0.0,
                    pos_m=fk_zero_start.tcp_pos.copy(),
                    rot_mat=fk_zero_start.tcp_rot.copy(),
                    segment_type="START",
                    label="Home_q0",
                )
            ] + list(waypoints)
        else:
            eff_waypoints = list(waypoints)

        eff_wp_times = np.array([float(wp.time_s) for wp in eff_waypoints], dtype=float)
        time_segments = []
        if eff_wp_times[0] > 1e-9:
            n_pre = max(2, int(np.ceil(eff_wp_times[0] * rate)) + 1)
            time_segments.append(np.linspace(0.0, eff_wp_times[0], n_pre, endpoint=False))

        eff_sample_indices = []
        running_count = sum(len(seg) for seg in time_segments)
        for m in range(len(eff_waypoints) - 1):
            eff_sample_indices.append(running_count)
            seg_dur = eff_wp_times[m + 1] - eff_wp_times[m]
            n_seg = max(2, int(np.ceil(seg_dur * rate)) + 1)
            seg_t = np.linspace(eff_wp_times[m], eff_wp_times[m + 1], n_seg, endpoint=(m == len(eff_waypoints) - 2))
            time_segments.append(seg_t)
            running_count += len(seg_t)
        eff_sample_indices.append(running_count - 1)

        times = np.concatenate(time_segments)
        n_samples = len(times)

        q_traj = np.zeros((n_samples, self.num_dof), dtype=float)
        tcp_pos_traj = np.zeros((n_samples, 3), dtype=float)
        target_pos_traj = np.zeros((n_samples, 3), dtype=float)
        pos_err_mm_traj = np.zeros(n_samples, dtype=float)
        rot_err_deg_traj = np.zeros(n_samples, dtype=float)

        saturated_set = set()
        failed_samples = 0

        # Solve effective Waypoint 0 (if prepended_home or wp0_is_zero, start cleanly from q_zero_start!)
        if prepended_home or wp0_is_zero:
            q_wp0 = q_zero_start.copy()
            wp0_ok = True
            wp0_perr_mm = 0.0 if prepended_home else p_err_z0 * 1000.0
            wp0_rerr_deg = 0.0 if prepended_home else float(np.rad2deg(r_err_z0))
        else:
            fk_seed = self.forward_kinematics(q_initial_seed)
            _, p_err0, r_err0 = self.compute_pose_error(
                fk_seed.tcp_pos, fk_seed.tcp_rot, eff_waypoints[0].pos_m, eff_waypoints[0].rot_mat, mode=ik_mode
            )
            if p_err0 * 1000.0 <= pos_tol_mm and (not check_rot or np.rad2deg(r_err0) <= rot_tol_deg):
                q_wp0 = q_initial_seed.copy()
                wp0_ok = True
                wp0_perr_mm = p_err0 * 1000.0
                wp0_rerr_deg = float(np.rad2deg(r_err0))
            else:
                res0 = self.solve_ik(
                    target_pos=eff_waypoints[0].pos_m,
                    target_rot=eff_waypoints[0].rot_mat,
                    q_init=q_initial_seed,
                    mode=ik_mode,
                    enforce_limits=enforce_limits,
                    pos_tol_mm=pos_tol_mm,
                    rot_tol_deg=rot_tol_deg,
                    max_iters=max_iters,
                    damping=damping,
                    allow_restarts=True,
                )
                q_wp0 = self._unwrap_joint_step(res0.q, q_initial_seed, enforce_limits=enforce_limits)
                wp0_ok = res0.success
                wp0_perr_mm = res0.pos_error_mm
                wp0_rerr_deg = res0.rot_error_deg
                saturated_set.update(res0.saturated_joints)

        fk_wp0 = self.forward_kinematics(q_wp0)

        # Fill optional initial hold [0, eff_wp_times[0]]
        first_wp_idx = eff_sample_indices[0]
        for idx in range(first_wp_idx + 1):
            q_traj[idx] = q_wp0
            tcp_pos_traj[idx] = fk_wp0.tcp_pos
            target_pos_traj[idx] = eff_waypoints[0].pos_m
            pos_err_mm_traj[idx] = wp0_perr_mm
            rot_err_deg_traj[idx] = wp0_rerr_deg
            if not wp0_ok and idx == first_wp_idx:
                failed_samples += 1

        eff_wp_converged = [bool(wp0_ok)]
        eff_wp_errors_mm = [float(wp0_perr_mm)]
        eff_wp_rot_errors_deg = [float(wp0_rerr_deg)]

        track_pos_tol_mm = min(float(pos_tol_mm) * 0.01, 1e-4)
        track_rot_tol_deg = min(float(rot_tol_deg) * 0.01, 1e-4)
        all_movej = all(str(wp.segment_type).upper() == "MOVEJ" for wp in eff_waypoints[1:])

        if timing_mode == "smooth_spline" and len(eff_waypoints) > 2:
            if all_movej:
                # Solve IK sequentially at waypoints, then C2 BPoly in joint space
                wp_qs = [q_wp0]
                q_prev = q_wp0.copy()
                for m in range(1, len(eff_waypoints)):
                    res_m = self.solve_ik(
                        target_pos=eff_waypoints[m].pos_m,
                        target_rot=eff_waypoints[m].rot_mat,
                        q_init=q_prev,
                        mode=ik_mode,
                        enforce_limits=enforce_limits,
                        pos_tol_mm=pos_tol_mm,
                        rot_tol_deg=rot_tol_deg,
                        max_iters=max_iters,
                        damping=damping,
                        allow_restarts=True,
                    )
                    q_m = self._unwrap_joint_step(res_m.q, q_prev, enforce_limits=enforce_limits)
                    wp_qs.append(q_m)
                    q_prev = q_m
                    saturated_set.update(res_m.saturated_joints)
                    eff_wp_converged.append(bool(res_m.success))
                    eff_wp_errors_mm.append(float(res_m.pos_error_mm))
                    eff_wp_rot_errors_deg.append(float(res_m.rot_error_deg))
                    if not res_m.success:
                        failed_samples += 1

                q_bpoly = _build_c2_clamped_bpoly(eff_wp_times, np.vstack(wp_qs))
                for idx in range(first_wp_idx + 1, n_samples):
                    q_s = self.clamp_q(q_bpoly(times[idx]), enforce_limits=enforce_limits)
                    fk_s = self.forward_kinematics(q_s)
                    q_traj[idx] = q_s
                    tcp_pos_traj[idx] = fk_s.tcp_pos
                    target_pos_traj[idx] = fk_s.tcp_pos
            else:
                # Continuous C2 Cartesian spline across all waypoints + warm-started IK
                pos_knots = np.array([wp.pos_m for wp in eff_waypoints], dtype=float)
                quats = Rotation.from_matrix(np.array([wp.rot_mat for wp in eff_waypoints])).as_quat()
                for m in range(1, len(quats)):
                    if np.dot(quats[m], quats[m - 1]) < 0.0:
                        quats[m] = -quats[m]

                pos_bpoly = _build_c2_clamped_bpoly(eff_wp_times, pos_knots)
                quat_bpoly = _build_c2_clamped_bpoly(eff_wp_times, quats)

                q_prev = q_wp0.copy()
                wp_idx_set = {eff_sample_indices[m]: m for m in range(1, len(eff_waypoints))}

                for idx in range(first_wp_idx + 1, n_samples):
                    t_curr = times[idx]
                    p_des = pos_bpoly(t_curr)
                    q_raw = quat_bpoly(t_curr)
                    q_nrm = np.linalg.norm(q_raw)
                    r_des = Rotation.from_quat(q_raw / q_nrm).as_matrix() if q_nrm > 1e-12 else eff_waypoints[-1].rot_mat

                    res_s = self.solve_ik(
                        target_pos=p_des,
                        target_rot=r_des,
                        q_init=q_prev,
                        mode=ik_mode,
                        enforce_limits=enforce_limits,
                        pos_tol_mm=track_pos_tol_mm,
                        rot_tol_deg=track_rot_tol_deg,
                        max_iters=max(60, max_iters // 2),
                        damping=damping,
                        max_step_rad=0.20,
                        allow_restarts=False,
                    )
                    q_curr = self._unwrap_joint_step(res_s.q, q_prev, enforce_limits=enforce_limits)
                    fk_curr = self.forward_kinematics(q_curr)
                    _, p_err, r_err = self.compute_pose_error(
                        fk_curr.tcp_pos, fk_curr.tcp_rot, p_des, r_des, mode=ik_mode
                    )
                    p_err_mm = p_err * 1000.0
                    r_err_deg = float(np.rad2deg(r_err))
                    ok_s = (p_err_mm <= pos_tol_mm) and (not check_rot or r_err_deg <= rot_tol_deg)

                    q_traj[idx] = q_curr
                    tcp_pos_traj[idx] = fk_curr.tcp_pos
                    target_pos_traj[idx] = p_des
                    pos_err_mm_traj[idx] = p_err_mm
                    rot_err_deg_traj[idx] = r_err_deg
                    saturated_set.update(res_s.saturated_joints)
                    if not ok_s:
                        failed_samples += 1
                    q_prev = q_curr

                    if idx in wp_idx_set:
                        eff_wp_converged.append(bool(ok_s))
                        eff_wp_errors_mm.append(float(p_err_mm))
                        eff_wp_rot_errors_deg.append(float(r_err_deg))
        else:
            # Segment-by-segment Quintic Minimum-Jerk (Rest-to-Rest at each waypoint, mixed MOVEL / MOVEJ)
            q_seg_start = q_wp0.copy()
            for m in range(len(eff_waypoints) - 1):
                i_start = eff_sample_indices[m]
                i_end = eff_sample_indices[m + 1]
                t_a = eff_wp_times[m]
                t_b = eff_wp_times[m + 1]
                seg_dur = t_b - t_a
                wp_a = eff_waypoints[m]
                wp_b = eff_waypoints[m + 1]
                seg_type = str(wp_b.segment_type).upper()
                if prepended_home and m == 0 and seg_type == "START":
                    seg_type = "MOVEJ"

                if seg_type == "MOVEJ":
                    res_b = self.solve_ik(
                        target_pos=wp_b.pos_m,
                        target_rot=wp_b.rot_mat,
                        q_init=q_seg_start,
                        mode=ik_mode,
                        enforce_limits=enforce_limits,
                        pos_tol_mm=pos_tol_mm,
                        rot_tol_deg=rot_tol_deg,
                        max_iters=max_iters,
                        damping=damping,
                        allow_restarts=True,
                    )
                    q_seg_end = self._unwrap_joint_step(res_b.q, q_seg_start, enforce_limits=enforce_limits)
                    saturated_set.update(res_b.saturated_joints)
                    if not res_b.success:
                        failed_samples += 1

                    for idx in range(i_start + 1, i_end + 1):
                        s = _quintic_step((times[idx] - t_a) / seg_dur)
                        q_s = (1.0 - s) * q_seg_start + s * q_seg_end
                        fk_s = self.forward_kinematics(q_s)
                        q_traj[idx] = q_s
                        tcp_pos_traj[idx] = fk_s.tcp_pos
                        target_pos_traj[idx] = fk_s.tcp_pos
                        if idx == i_end:
                            pos_err_mm_traj[idx] = res_b.pos_error_mm
                            rot_err_deg_traj[idx] = res_b.rot_error_deg

                    eff_wp_converged.append(bool(res_b.success))
                    eff_wp_errors_mm.append(float(res_b.pos_error_mm))
                    eff_wp_rot_errors_deg.append(float(res_b.rot_error_deg))
                    q_seg_start = q_seg_end.copy()
                else:
                    # MOVEL: Cartesian straight line + SLERP orientation with warm-started IK
                    slerp = Slerp([0.0, 1.0], Rotation.from_matrix([wp_a.rot_mat, wp_b.rot_mat]))
                    q_prev = q_seg_start.copy()
                    end_ok = True
                    end_perr_mm = 0.0
                    end_rerr_deg = 0.0

                    for idx in range(i_start + 1, i_end + 1):
                        s = _quintic_step((times[idx] - t_a) / seg_dur)
                        p_des = (1.0 - s) * wp_a.pos_m + s * wp_b.pos_m
                        r_des = slerp(s).as_matrix()

                        res_s = self.solve_ik(
                            target_pos=p_des,
                            target_rot=r_des,
                            q_init=q_prev,
                            mode=ik_mode,
                            enforce_limits=enforce_limits,
                            pos_tol_mm=track_pos_tol_mm,
                            rot_tol_deg=track_rot_tol_deg,
                            max_iters=max(60, max_iters // 2),
                            damping=damping,
                            max_step_rad=0.20,
                            allow_restarts=False,
                        )
                        q_curr = self._unwrap_joint_step(res_s.q, q_prev, enforce_limits=enforce_limits)
                        fk_curr = self.forward_kinematics(q_curr)
                        _, p_err, r_err = self.compute_pose_error(
                            fk_curr.tcp_pos, fk_curr.tcp_rot, p_des, r_des, mode=ik_mode
                        )
                        p_err_mm = p_err * 1000.0
                        r_err_deg = float(np.rad2deg(r_err))
                        ok_s = (p_err_mm <= pos_tol_mm) and (not check_rot or r_err_deg <= rot_tol_deg)

                        q_traj[idx] = q_curr
                        tcp_pos_traj[idx] = fk_curr.tcp_pos
                        target_pos_traj[idx] = p_des
                        pos_err_mm_traj[idx] = p_err_mm
                        rot_err_deg_traj[idx] = r_err_deg
                        saturated_set.update(res_s.saturated_joints)
                        if not ok_s:
                            failed_samples += 1

                        if idx == i_end:
                            end_ok = ok_s
                            end_perr_mm = p_err_mm
                            end_rerr_deg = r_err_deg
                        q_prev = q_curr

                    eff_wp_converged.append(bool(end_ok))
                    eff_wp_errors_mm.append(float(end_perr_mm))
                    eff_wp_rot_errors_deg.append(float(end_rerr_deg))
                    q_seg_start = q_prev.copy()

        if prepended_home:
            wp_sample_indices = eff_sample_indices[1:]
            waypoint_converged = eff_wp_converged[1:]
            waypoint_errors_mm = eff_wp_errors_mm[1:]
            waypoint_rot_errors_deg = eff_wp_rot_errors_deg[1:]
        else:
            wp_sample_indices = eff_sample_indices
            waypoint_converged = eff_wp_converged
            waypoint_errors_mm = eff_wp_errors_mm
            waypoint_rot_errors_deg = eff_wp_rot_errors_deg

        # Compute smooth numerical velocity & acceleration histories (forcing exact 0 at endpoints)
        qd_traj = np.gradient(q_traj, times, axis=0)
        qd_traj[0] = 0.0
        qd_traj[-1] = 0.0
        qdd_traj = np.gradient(qd_traj, times, axis=0)
        qdd_traj[0] = 0.0
        qdd_traj[-1] = 0.0

        max_pos_err = float(np.max(pos_err_mm_traj)) if n_samples > 0 else 0.0
        max_rot_err = float(np.max(rot_err_deg_traj)) if n_samples > 0 else 0.0
        all_ok = (failed_samples == 0) and all(waypoint_converged)
        saturated_list = [j.name for j in self.active_joints if j.name in saturated_set]

        singularity_note = ""
        rev_indices = [k for k, j in enumerate(self.active_joints) if j.joint_type == JointType.REVOLUTE]
        if rev_indices and n_samples > 1:
            peak_deg_s = float(np.rad2deg(np.max(np.abs(qd_traj[:, rev_indices]))))
            if peak_deg_s > 400.0:
                fast_k = rev_indices[int(np.argmax(np.max(np.abs(qd_traj[:, rev_indices]), axis=0)))]
                singularity_note = (
                    f" | Note: High joint speed ({self.active_joints[fast_k].name}: {peak_deg_s:.0f} deg/s) "
                    f"near wrist/arm singularity -- consider MOVEJ or non-zero wrist angle"
                )

        if all_ok:
            msg = (
                f"[OK] Trajectory solved ({n_samples} samples, T = {times[-1]:.2f} s) | "
                f"Max TCP err: {max_pos_err:.3f} mm"
                + (f", {max_rot_err:.3f} deg" if check_rot else "")
                + singularity_note
            )
        else:
            sat_txt = f" | Limits hit: {', '.join(saturated_list)}" if saturated_list else ""
            msg = (
                f"[WARN] Trajectory has {failed_samples}/{n_samples} unconverged samples | "
                f"Max TCP err: {max_pos_err:.2f} mm{sat_txt}{singularity_note}"
            )

        return TrajectoryResult(
            success=all_ok,
            times=times,
            q_traj=q_traj,
            qd_traj=qd_traj,
            qdd_traj=qdd_traj,
            tcp_pos_traj=tcp_pos_traj,
            target_pos_traj=target_pos_traj,
            pos_err_mm_traj=pos_err_mm_traj,
            waypoint_indices=wp_sample_indices,
            waypoint_converged=waypoint_converged,
            waypoint_errors_mm=waypoint_errors_mm,
            waypoint_rot_errors_deg=waypoint_rot_errors_deg,
            failed_samples=failed_samples,
            max_pos_error_mm=max_pos_err,
            max_rot_error_deg=max_rot_err,
            saturated_joints=saturated_list,
            message=msg,
        )

    def export_trajectory_to_motions(
        self,
        traj_result: TrajectoryResult,
        app,
        sync_sim_time: bool = True,
    ) -> list:
        """
        Exports a solved `TrajectoryResult` into SimPhant `JointMotion` spline drivers:
          1) Invalidates stale results first and snaps the 3D robot to exact `q_traj[0]` at t = 0
             so `MBSolver.initialize_motions()` records the exact starting joint baselines.
          2) Writes relative displacement CSV files (`rad` for Revolute, `mm` for Prismatic)
             starting at `0.0` at `t = 0.0`.
          3) Creates or updates one `JointMotion` per active chain joint in `app.motions_list`
             and the Project Explorer tree.
        """
        if traj_result is None or len(traj_result.times) < 2:
            raise ValueError("No valid solved trajectory to export.")

        # 1. Clear stale solver state FIRST, then snap scene to Zero All (q = 0) baseline
        if hasattr(app, 'invalidate_results'):
            app.invalidate_results()
        q_zero = self.clamp_q(np.zeros(self.num_dof, dtype=float), enforce_limits=True)
        self.apply_fk_to_scene(q_zero, app=app, render=True)

        # 2. Choose deterministic output folder for spline CSV files
        proj_file = getattr(app, 'current_project_file', None)
        if proj_file:
            base_folder = os.path.dirname(os.path.abspath(proj_file))
            stem = os.path.splitext(os.path.basename(proj_file))[0]
        else:
            base_folder = getattr(app, 'working_dir', None) or os.getcwd()
            stem = re.sub(r'[^\w\-]+', '_', f"{self.base_body.name}_{self.ee_body.name}")

        spline_out_dir = os.path.join(base_folder, "splines", f"{stem}_IK")
        os.makedirs(spline_out_dir, exist_ok=True)

        if not hasattr(app, 'motions_list'):
            app.motions_list = []
        if not hasattr(app, 'node_motions') or app.node_motions is None:
            app.node_motions = QTreeWidgetItem(app.ui.treeHierarchy, ["Motions"])

        exported_motions = []
        times = traj_result.times

        for k, step in enumerate(self.active_steps):
            joint = step.joint
            sign = float(step.direction_sign)
            is_rev = (joint.joint_type == JointType.REVOLUTE)
            trans_rot_idx = 1 if is_rev else 0

            # Displacement relative to q_zero (Zero All q=0) in JointMotion's expected units (rad for Rot, mm for Trans)
            unit_mult = 1.0 if is_rev else 1000.0
            rel_vals = sign * (traj_result.q_traj[:, k] - q_zero[k]) * unit_mult

            safe_jname = re.sub(r'[^\w\-]+', '_', joint.name)
            csv_path = os.path.normpath(os.path.join(spline_out_dir, f"IK_Motion_{safe_jname}.csv"))
            data_mat = np.column_stack((times, rel_vals))
            np.savetxt(csv_path, data_mat, fmt="%.6f; %.10f", encoding="utf-8")

            spline_expr = format_spline_expression(csv_path)

            # Reuse existing motion on this joint if present (respects 1-motion-per-joint rule)
            existing = next(
                (m for m in app.motions_list if m.joint is joint and m.trans_rot.value == trans_rot_idx),
                None,
            )
            if existing is None:
                existing = next((m for m in app.motions_list if m.joint.name == joint.name), None)

            if existing is not None:
                existing.trans_rot = existing.trans_rot.__class__(trans_rot_idx)
                existing.motion_type = existing.motion_type.__class__(0)  # DISPLACEMENT
                existing.enabled = True
                existing.compile_expression(spline_expr, base_dir=getattr(app, 'working_dir', None))
                motion_obj = existing
            else:
                base_mname = f"IK_Motion_{joint.name}"
                m_name = base_mname
                cnt = 2
                existing_names = {m.name for m in app.motions_list}
                while m_name in existing_names:
                    m_name = f"{base_mname}_{cnt}"
                    cnt += 1

                motion_obj = JointMotion(m_name, joint, trans_rot_idx, 0)  # 0 = DISPLACEMENT
                motion_obj.enabled = True
                motion_obj.compile_expression(spline_expr, base_dir=getattr(app, 'working_dir', None))
                app.motions_list.append(motion_obj)
                QTreeWidgetItem(app.node_motions, [motion_obj.name])

            exported_motions.append(motion_obj)

        app.node_motions.setExpanded(True)
        if sync_sim_time and hasattr(app, 'ui') and hasattr(app.ui, 'Edit_SimulationTime'):
            app.ui.Edit_SimulationTime.setText(f"{float(times[-1]):.3f}")

        if hasattr(app, 'refresh_tree_visuals'):
            app.refresh_tree_visuals()

        return exported_motions


# =============================================================================
#  UNIVERSAL ROBOTICS & INVERSE KINEMATICS UI (Step 1 & Step 2)
# =============================================================================

class RoboticsWindow(QDialog):
    """
    Universal Robotics & Inverse Kinematics Workbench for SimPhant.
    Tab 1 provides:
      - Automatic serial-chain discovery between any Base Body and End-Effector Body
      - Whole-chain Joint Table with editable Stroke & Effort limits and interactive FK sliders
      - 6-DOF / 3-DOF / 5-DOF Damped Least-Squares IK solver with live 3D viewport preview
    """
    SLIDER_STEPS = 1000
    MIN_RENDER_INTERVAL_S = 0.008  # ~120 FPS synchronous budget (avoids deferring 7ms frames to WM_TIMER)

    def __init__(self, app, parent=None):
        super().__init__(parent or app)
        self.app = app
        self._uia_shield = install_win_uia_shield()
        self.chain: KinematicChain | None = None
        self._updating_ui = False
        self._row_widgets = []
        self._has_saturated_highlights = False
        self._is_docked = False
        self._dock_widget: QDockWidget | None = None
        self._gc_paused_for_drag = False
        self._plotter_timer_was_active = False

        # Step 3: Trajectory Planner & Preview state
        self._waypoints: list[TrajectoryWaypoint] = []
        self._wp_row_widgets: list[dict] = []
        self.last_trajectory: TrajectoryResult | None = None
        self._traj_preview_actors: list = []
        self._traj_play_idx: int = 0

        # Theme-aware semantic state trackers
        self._theme_refresh_pending = False
        self._chain_summary_state = "info"
        self._perf_stats_state = "ok"
        self._effort_summary_state = "info"

        # Performance telemetry trackers
        self._last_render_time = 0.0
        self._prev_frame_wall_time = 0.0
        self._first_pending_event_time = 0.0
        self._pending_event_count = 0
        self._perf_frame_counter = 0
        self._debugger_active = self._detect_debugger()

        self._fk_coalesce_timer = QTimer(self)
        self._fk_coalesce_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._fk_coalesce_timer.setSingleShot(True)
        self._fk_coalesce_timer.timeout.connect(self._flush_coalesced_fk)

        self._ik_coalesce_timer = QTimer(self)
        self._ik_coalesce_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._ik_coalesce_timer.setSingleShot(True)
        self._ik_coalesce_timer.timeout.connect(self._flush_coalesced_live_ik)

        self._traj_play_timer = QTimer(self)
        self._traj_play_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._traj_play_timer.timeout.connect(self._on_traj_play_tick)

        self.setWindowTitle("SimPhant™ — Robotics & Inverse Kinematics Workbench")
        self.resize(1120, 740)
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        self._pause_plotter_background_timer()

        self._build_ui()
        self._install_theme_change_hooks()
        self.apply_theme_colors()
        self.populate_scene_selectors()
        self.rebuild_chain(auto_quiet=True)
        if getattr(self.app, "robotics_project_state", None):
            self.import_project_state(self.app.robotics_project_state)

    def _pause_plotter_background_timer(self):
        plotter = getattr(self.app, "plotter", None)
        rt = getattr(plotter, "render_timer", None) if plotter is not None else None
        if rt is not None and rt.isActive():
            self._plotter_timer_was_active = True
            rt.stop()

    def _restore_plotter_background_timer(self):
        if self._plotter_timer_was_active:
            plotter = getattr(self.app, "plotter", None)
            rt = getattr(plotter, "render_timer", None) if plotter is not None else None
            if rt is not None and not rt.isActive():
                rt.start()
            self._plotter_timer_was_active = False

    def _resume_gc_if_paused(self):
        if self._gc_paused_for_drag:
            gc.enable()
            self._gc_paused_for_drag = False

    @staticmethod
    def _detect_debugger() -> bool:
        if sys.gettrace() is not None:
            return True
        if hasattr(sys, "monitoring"):
            try:
                for tool_id in range(6):
                    if sys.monitoring.get_tool(tool_id) is not None:
                        return True
            except Exception:
                pass
        return False

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self._dialog_root_layout = QVBoxLayout(self)
        self._dialog_root_layout.setContentsMargins(0, 0, 0, 0)

        self._content_widget = QWidget(self)
        self._dialog_root_layout.addWidget(self._content_widget)

        main_layout = QVBoxLayout(self._content_widget)
        main_layout.setContentsMargins(10, 10, 10, 8)
        main_layout.setSpacing(8)

        # --- Top Bar: Kinematic Chain Selection ---
        chain_group = QGroupBox("Kinematic Chain Definition")
        chain_layout = QGridLayout(chain_group)
        chain_layout.setContentsMargins(10, 6, 10, 6)
        chain_layout.setHorizontalSpacing(8)
        chain_layout.setVerticalSpacing(5)

        chain_layout.addWidget(QLabel("Base Body:"), 0, 0)
        self.cmbBaseBody = QComboBox()
        self.cmbBaseBody.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.cmbBaseBody.setMinimumContentsLength(8)
        self.cmbBaseBody.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cmbBaseBody.setToolTip("Select the fixed root/base body of the kinematic chain (stays stationary during posing).")
        chain_layout.addWidget(self.cmbBaseBody, 0, 1)

        chain_layout.addWidget(QLabel("End-Effector:"), 0, 2)
        self.cmbEEBody = QComboBox()
        self.cmbEEBody.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.cmbEEBody.setMinimumContentsLength(8)
        self.cmbEEBody.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cmbEEBody.setToolTip("Select the tip/end-effector body at the end of the kinematic chain to control.")
        chain_layout.addWidget(self.cmbEEBody, 0, 3)

        chain_layout.addWidget(QLabel("TCP Frame:"), 0, 4)
        self.cmbTCPRF = QComboBox()
        self.cmbTCPRF.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.cmbTCPRF.setMinimumContentsLength(8)
        self.cmbTCPRF.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cmbTCPRF.setToolTip("Select the Tool Center Point (TCP) Reference Frame to track and solve IK for, or use the End-Effector CoG.")
        chain_layout.addWidget(self.cmbTCPRF, 0, 5)

        self.btnRebuildChain = QPushButton("Rebuild Chain")
        self.btnRebuildChain.setStyleSheet("font-weight: bold; padding: 4px 8px;")
        self.btnRebuildChain.setToolTip("Re-scan scene bodies, joints, and Reference Frames to rebuild the active kinematic chain.")
        chain_layout.addWidget(self.btnRebuildChain, 0, 6)

        self.btnToggleDock = QPushButton("Dock Left")
        self.btnToggleDock.setToolTip("Dock the Robotics Workbench on the left side of the main SimPhant window or pop it out as a floating window.")
        self.btnToggleDock.setStyleSheet("padding: 4px 8px;")
        chain_layout.addWidget(self.btnToggleDock, 0, 7)

        chain_layout.setColumnStretch(1, 1)
        chain_layout.setColumnStretch(3, 1)
        chain_layout.setColumnStretch(5, 1)

        self.lblChainSummary = QLabel("No active kinematic chain.")
        self.lblChainSummary.setWordWrap(True)
        self.lblChainSummary.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
        chain_layout.addWidget(self.lblChainSummary, 1, 0, 1, 8)

        main_layout.addWidget(chain_group)

        # --- Central TabWidget (Tab 1: Chain, FK & IK | Tab 2: Trajectory Planner & Motions) ---
        self.tabs = QTabWidget()
        self.tabFkIk = QWidget()
        self.tabTrajectory = QWidget()
        self.tabs.addTab(self.tabFkIk, "1. Chain, Joint Limits, FK && IK")
        self.tabs.addTab(self.tabTrajectory, "2. Trajectory Planner && Motions")
        main_layout.addWidget(self.tabs, stretch=1)

        self._build_tab_fk_ik()
        self._build_tab_trajectory()

        # --- Bottom Performance Status Line ---
        perf_bar = QHBoxLayout()
        perf_bar.setContentsMargins(2, 0, 2, 0)
        perf_bar.setSpacing(8)

        dbg_flag = "YES (F5 Debugger)" if self._debugger_active else "No"
        self.lblPerfStats = QLabel(
            f"Perf [Debugger: {dbg_flag}] — Move any slider or solve IK to view live FPS and FK / VTK / OpenGL timings."
        )
        self.lblPerfStats.setWordWrap(True)
        self.lblPerfStats.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        perf_bar.addWidget(self.lblPerfStats, stretch=1)

        main_layout.addLayout(perf_bar)

        # --- Wire top-level signals ---
        self.cmbBaseBody.currentIndexChanged.connect(self._on_chain_selector_changed)
        self.cmbEEBody.currentIndexChanged.connect(self._on_ee_body_changed)
        self.cmbTCPRF.currentIndexChanged.connect(self._on_chain_selector_changed)
        self.btnRebuildChain.clicked.connect(lambda: self.rebuild_chain(auto_quiet=False))
        self.btnToggleDock.clicked.connect(self.toggle_dock_mode)

    def _build_tab_fk_ik(self):
        tab_layout = QVBoxLayout(self.tabFkIk)
        tab_layout.setContentsMargins(6, 6, 6, 6)

        splitter = QSplitter(Qt.Orientation.Vertical)
        tab_layout.addWidget(splitter, stretch=1)

        # ==============================================================
        # TOP PANE: Active Chain Joint Table (Limits + FK Sliders)
        # ==============================================================
        joint_group = QGroupBox("Active Chain Joints — Stroke Limits, Forward Kinematics Sliders && Effort Ratings")
        jg_layout = QVBoxLayout(joint_group)

        toolbar_layout = QHBoxLayout()
        self.chkEnforceLimits = QCheckBox("Enforce Joint Stroke Limits in FK && IK")
        self.chkEnforceLimits.setChecked(True)
        self.chkEnforceLimits.setStyleSheet("font-weight: bold;")
        self.chkEnforceLimits.setToolTip("Keep all limited joints strictly inside their [Min, Max] stroke bounds during FK posing and IK solving.")
        toolbar_layout.addWidget(self.chkEnforceLimits)

        self.btnEnableAllLimits = QPushButton("Check All Limits")
        self.btnEnableAllLimits.setToolTip("Enable stroke limits ('Limit On') for all joints in the active chain.")
        self.btnDisableAllLimits = QPushButton("Uncheck All Limits")
        self.btnDisableAllLimits.setToolTip("Disable stroke limits ('Limit On') for all joints in the active chain.")
        self.btnZeroJoints = QPushButton("Zero All (q = 0)")
        self.btnZeroJoints.setToolTip("Set all joint coordinates in the active chain to zero (clamped to active stroke limits).")
        self.btnResetInitialPose = QPushButton("Reset to Initial Pose")
        self.btnResetInitialPose.setToolTip("Restore all bodies and Reference Frames to the initial pose captured when the chain was built.")
        toolbar_layout.addWidget(self.btnEnableAllLimits)
        toolbar_layout.addWidget(self.btnDisableAllLimits)
        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(self.btnZeroJoints)
        toolbar_layout.addWidget(self.btnResetInitialPose)
        jg_layout.addLayout(toolbar_layout)

        self.tblJoints = QTableWidget(0, 9)
        self.tblJoints.setHorizontalHeaderLabels([
            "#", "Joint Name", "Child Body", "Type", "Limit On",
            "Min (deg / mm)", "Max (deg / mm)", "Current q (deg / mm)",
            "Interactive Pose Slider",
        ])
        # Add 10th column for Max Effort
        self.tblJoints.setColumnCount(10)
        self.tblJoints.setHorizontalHeaderLabels([
            "#", "Joint Name", "Child Body", "Type", "Limit On",
            "Min (deg/mm)", "Max (deg/mm)", "Current q (deg/mm)",
            "Interactive Pose Slider", "Max Effort (Nm/N)"
        ])
        header = self.tblJoints.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)
        self.tblJoints.verticalHeader().setVisible(False)
        self.tblJoints.setAlternatingRowColors(True)
        jg_layout.addWidget(self.tblJoints, stretch=1)

        splitter.addWidget(joint_group)

        # ==============================================================
        # BOTTOM PANE: TCP Pose Readout & Inverse Kinematics Solver
        # ==============================================================
        ik_container = QWidget()
        ik_outer = QHBoxLayout(ik_container)
        ik_outer.setContentsMargins(0, 0, 0, 0)
        ik_outer.setSpacing(10)

        # --- Left Box: Current TCP Pose + Target Pose Inputs ---
        pose_group = QGroupBox("End-Effector / TCP Pose && IK Target Coordinates")
        pose_grid = QGridLayout(pose_group)
        pose_grid.setHorizontalSpacing(8)
        pose_grid.setVerticalSpacing(6)

        # Headers
        self.lblCurrPoseHdr = QLabel("Current TCP Pose")
        self.lblTargPoseHdr = QLabel("IK Target Pose")
        pose_grid.addWidget(self.lblCurrPoseHdr, 0, 1, 1, 2)
        pose_grid.addWidget(self.lblTargPoseHdr, 0, 3, 1, 2)

        self.lblCurrX = QLabel("0.000")
        self.lblCurrY = QLabel("0.000")
        self.lblCurrZ = QLabel("0.000")
        self.lblCurrRoll = QLabel("0.000")
        self.lblCurrPitch = QLabel("0.000")
        self.lblCurrYaw = QLabel("0.000")
        for lbl in (self.lblCurrX, self.lblCurrY, self.lblCurrZ,
                    self.lblCurrRoll, self.lblCurrPitch, self.lblCurrYaw):
            lbl.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            lbl.setMinimumWidth(85)
            lbl.setStyleSheet(
                "background-color: #f4f6f9; color: #111111; font-weight: bold; "
                "padding: 2px 5px; font-family: Consolas, monospace;"
            )

        self.dsbTargetX = self._make_coord_spinbox(-100000.0, 100000.0, 10.0, " mm")
        self.dsbTargetX.setToolTip("Desired global X coordinate of the TCP (mm).")
        self.dsbTargetY = self._make_coord_spinbox(-100000.0, 100000.0, 10.0, " mm")
        self.dsbTargetY.setToolTip("Desired global Y coordinate of the TCP (mm).")
        self.dsbTargetZ = self._make_coord_spinbox(-100000.0, 100000.0, 10.0, " mm")
        self.dsbTargetZ.setToolTip("Desired global Z coordinate of the TCP (mm).")
        self.dsbTargetRoll = self._make_coord_spinbox(-360.0, 360.0, 5.0, " °")
        self.dsbTargetRoll.setToolTip("Desired global Roll angle around X axis (degrees).")
        self.dsbTargetPitch = self._make_coord_spinbox(-360.0, 360.0, 5.0, " °")
        self.dsbTargetPitch.setToolTip("Desired global Pitch angle around Y axis (degrees).")
        self.dsbTargetYaw = self._make_coord_spinbox(-360.0, 360.0, 5.0, " °")
        self.dsbTargetYaw.setToolTip("Desired global Yaw angle around Z axis (degrees).")

        rows_spec = [
            ("X Position (mm):", self.lblCurrX, self.dsbTargetX),
            ("Y Position (mm):", self.lblCurrY, self.dsbTargetY),
            ("Z Position (mm):", self.lblCurrZ, self.dsbTargetZ),
            ("Roll — X Angle (deg):", self.lblCurrRoll, self.dsbTargetRoll),
            ("Pitch — Y Angle (deg):", self.lblCurrPitch, self.dsbTargetPitch),
            ("Yaw — Z Angle (deg):", self.lblCurrYaw, self.dsbTargetYaw),
        ]
        for row_idx, (title, curr_w, targ_w) in enumerate(rows_spec, start=1):
            pose_grid.addWidget(QLabel(title), row_idx, 0)
            pose_grid.addWidget(curr_w, row_idx, 1, 1, 2)
            pose_grid.addWidget(targ_w, row_idx, 3, 1, 2)

        btn_row = QHBoxLayout()
        self.btnCopyCurrToTarget = QPushButton("Copy Current TCP → Target")
        self.btnCopyCurrToTarget.setToolTip("Copy the current 3D TCP position and orientation into the IK Target Pose fields.")
        self.btnCreateTargetRF = QPushButton("Create Visual Target RF at Target Pose")
        self.btnCreateTargetRF.setToolTip("Create a visible 3D Reference Frame in the viewport at the current IK Target Pose coordinates.")
        btn_row.addWidget(self.btnCopyCurrToTarget)
        btn_row.addWidget(self.btnCreateTargetRF)
        pose_grid.addLayout(btn_row, 7, 0, 1, 5)

        rf_pick_row = QHBoxLayout()
        rf_pick_row.addWidget(QLabel("Load Target from RFrame:"))
        self.cmbTargetRF = QComboBox()
        self.cmbTargetRF.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.cmbTargetRF.setMinimumContentsLength(8)
        self.cmbTargetRF.setToolTip("Select an existing Reference Frame in the scene to copy its 3D pose into the IK target.")
        rf_pick_row.addWidget(self.cmbTargetRF, stretch=1)
        self.btnLoadTargetFromRF = QPushButton("Load RF Pose")
        self.btnLoadTargetFromRF.setToolTip("Copy the 3D position and orientation of the selected Reference Frame into the IK Target Pose fields.")
        rf_pick_row.addWidget(self.btnLoadTargetFromRF)
        pose_grid.addLayout(rf_pick_row, 8, 0, 1, 5)

        ik_outer.addWidget(pose_group, stretch=3)

        # --- Right Box: IK Solver Settings & Execution ---
        solver_group = QGroupBox("Inverse Kinematics (IK) Solver Controls")
        solver_layout = QVBoxLayout(solver_group)

        settings_grid = QGridLayout()
        settings_grid.addWidget(QLabel("IK Task Mode:"), 0, 0)
        self.cmbIKMode = QComboBox()
        self.cmbIKMode.addItem("6D Full Pose (Position X,Y,Z + Orientation)", "6D")
        self.cmbIKMode.addItem("3D Position Only (X, Y, Z — Free Orientation)", "PositionOnly")
        self.cmbIKMode.addItem("5D Position + Tool Z-Axis Alignment", "PositionPlusAxis")
        self.cmbIKMode.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.cmbIKMode.setMinimumContentsLength(14)
        self.cmbIKMode.setToolTip("Choose which TCP coordinates IK solves for: 6D full pose, 3D position only, or 5D position + Z-axis alignment.")
        settings_grid.addWidget(self.cmbIKMode, 0, 1, 1, 3)

        settings_grid.addWidget(QLabel("Pos Tolerance:"), 1, 0)
        self.dsbPosTol = QDoubleSpinBox()
        self.dsbPosTol.setDecimals(3)
        self.dsbPosTol.setRange(0.001, 100.0)
        self.dsbPosTol.setValue(0.100)
        self.dsbPosTol.setSuffix(" mm")
        self.dsbPosTol.setToolTip("Maximum allowed TCP position error (mm) for IK convergence.")
        settings_grid.addWidget(self.dsbPosTol, 1, 1)

        settings_grid.addWidget(QLabel("Rot Tolerance:"), 1, 2)
        self.dsbRotTol = QDoubleSpinBox()
        self.dsbRotTol.setDecimals(3)
        self.dsbRotTol.setRange(0.001, 45.0)
        self.dsbRotTol.setValue(0.100)
        self.dsbRotTol.setSuffix(" °")
        self.dsbRotTol.setToolTip("Maximum allowed TCP orientation error (degrees) for IK convergence.")
        settings_grid.addWidget(self.dsbRotTol, 1, 3)

        settings_grid.addWidget(QLabel("Max Iterations:"), 2, 0)
        self.spnMaxIters = QSpinBox()
        self.spnMaxIters.setRange(10, 2000)
        self.spnMaxIters.setValue(150)
        self.spnMaxIters.setToolTip("Maximum number of Damped Least-Squares iterations per IK solve.")
        settings_grid.addWidget(self.spnMaxIters, 2, 1)

        settings_grid.addWidget(QLabel("DLS Damping (λ):"), 2, 2)
        self.dsbDamping = QDoubleSpinBox()
        self.dsbDamping.setDecimals(4)
        self.dsbDamping.setRange(0.0001, 2.0)
        self.dsbDamping.setSingleStep(0.01)
        self.dsbDamping.setValue(0.0500)
        self.dsbDamping.setToolTip("Singularity damping factor λ for smooth, stable steps near workspace boundaries.")
        settings_grid.addWidget(self.dsbDamping, 2, 3)

        solver_layout.addLayout(settings_grid)

        self.chkLiveIK = QCheckBox("Live Interactive IK (auto-solve on Target edit)")
        self.chkLiveIK.setToolTip("Automatically solve IK and move the 3D robot whenever any IK Target Pose coordinate is edited.")
        solver_layout.addWidget(self.chkLiveIK)

        self.btnSolveIK = QPushButton("Solve IK && Apply Pose to Robot")
        self.btnSolveIK.setToolTip("Solve Inverse Kinematics for the specified Target Pose and apply the resulting joint angles to the 3D robot.")
        self.btnSolveIK.setMinimumHeight(38)
        self.btnSolveIK.setStyleSheet(
            "QPushButton { background-color: #1f6feb; color: white; font-weight: bold; font-size: 13px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #1158c7; }"
        )
        solver_layout.addWidget(self.btnSolveIK)

        self.lblIKStatus = QLabel("Ready. Adjust FK sliders or set a Target Pose and click 'Solve IK'.")
        self.lblIKStatus.setWordWrap(True)
        self.lblIKStatus.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        self.lblIKStatus.setStyleSheet("background-color: #f8f9fa; color: #111111; padding: 6px; font-weight: bold;")
        solver_layout.addWidget(self.lblIKStatus)
        solver_layout.addStretch(1)

        ik_outer.addWidget(solver_group, stretch=2)
        splitter.addWidget(ik_container)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        # --- Wire Tab 1 Signals ---
        self.chkEnforceLimits.toggled.connect(self._on_enforce_limits_toggled)
        self.btnEnableAllLimits.clicked.connect(lambda: self._set_all_joint_limits_enabled(True))
        self.btnDisableAllLimits.clicked.connect(lambda: self._set_all_joint_limits_enabled(False))
        self.btnZeroJoints.clicked.connect(self.zero_all_joints)
        self.btnResetInitialPose.clicked.connect(self.reset_to_initial_pose)

        self.btnCopyCurrToTarget.clicked.connect(self.copy_current_tcp_to_target)
        self.btnCreateTargetRF.clicked.connect(self.create_visual_target_rf)
        self.btnLoadTargetFromRF.clicked.connect(self.load_target_from_selected_rf)
        self.btnSolveIK.clicked.connect(self.solve_and_apply_ik)
        self.cmbIKMode.currentIndexChanged.connect(self._on_ik_mode_changed)

        for spn in (self.dsbTargetX, self.dsbTargetY, self.dsbTargetZ,
                    self.dsbTargetRoll, self.dsbTargetPitch, self.dsbTargetYaw):
            spn.valueChanged.connect(self._on_target_spinbox_changed)

    def _build_tab_trajectory(self):
        tab_layout = QVBoxLayout(self.tabTrajectory)
        tab_layout.setContentsMargins(6, 6, 6, 6)

        v_splitter = QSplitter(Qt.Orientation.Vertical)
        tab_layout.addWidget(v_splitter, stretch=1)

        # ==============================================================
        # TOP PANE: Waypoint Sequence Table
        # ==============================================================
        wp_group = QGroupBox("Cartesian / Joint Waypoint Sequence (Ordered by Time t)")
        wp_layout = QVBoxLayout(wp_group)

        wp_bar = QHBoxLayout()
        wp_bar.setSpacing(6)
        self.btnAddCurrPoseWp = QPushButton("+ Add Current Pose")
        self.btnAddCurrPoseWp.setStyleSheet("font-weight: bold; padding: 3px 8px;")
        self.btnAddCurrPoseWp.setToolTip(
            "Append a new waypoint using the robot's current 3D TCP pose in the viewport."
        )
        wp_bar.addWidget(self.btnAddCurrPoseWp)

        self.cmbWpSourceRF = QComboBox()
        self.cmbWpSourceRF.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.cmbWpSourceRF.setMinimumContentsLength(8)
        self.cmbWpSourceRF.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cmbWpSourceRF.setToolTip(
            "Select a scene Reference Frame (e.g. IK_Target_1) to add as a trajectory waypoint."
        )
        wp_bar.addWidget(self.cmbWpSourceRF, stretch=1)

        self.btnAddRFrameWp = QPushButton("+ Add RF")
        self.btnAddRFrameWp.setToolTip(
            "Append a new waypoint at the selected Reference Frame's 3D position and orientation."
        )
        wp_bar.addWidget(self.btnAddRFrameWp)

        self.btnPreviewSelectedWp = QPushButton("Jump To")
        self.btnPreviewSelectedWp.setToolTip(
            "Solve IK for the selected waypoint row and move the 3D robot to preview that waypoint."
        )
        wp_bar.addWidget(self.btnPreviewSelectedWp)

        self.btnMoveWpUp = QPushButton("↑")
        self.btnMoveWpUp.setFixedWidth(28)
        self.btnMoveWpUp.setToolTip("Move the selected waypoint earlier in the sequence (swapping timestamps).")
        self.btnMoveWpDown = QPushButton("↓")
        self.btnMoveWpDown.setFixedWidth(28)
        self.btnMoveWpDown.setToolTip("Move the selected waypoint later in the sequence (swapping timestamps).")
        self.btnDeleteWp = QPushButton("Delete")
        self.btnDeleteWp.setToolTip("Remove the currently selected waypoint row from the table.")
        self.btnClearWps = QPushButton("Clear")
        self.btnClearWps.setToolTip("Clear all waypoints and remove any 3D trajectory preview path.")

        wp_bar.addWidget(self.btnMoveWpUp)
        wp_bar.addWidget(self.btnMoveWpDown)
        wp_bar.addWidget(self.btnDeleteWp)
        wp_bar.addWidget(self.btnClearWps)

        self.chkShow3DPath = QCheckBox("Show 3D Path")
        self.chkShow3DPath.setChecked(True)
        self.chkShow3DPath.setToolTip(
            "Display the planned 3D TCP trajectory curve and waypoint spheres in the SimPhant viewport."
        )
        wp_bar.addWidget(self.chkShow3DPath)
        wp_layout.addLayout(wp_bar)

        self.tblWaypoints = QTableWidget(0, 10)
        self.tblWaypoints.setHorizontalHeaderLabels([
            "#", "Time t (s)", "Segment Type",
            "X (mm)", "Y (mm)", "Z (mm)",
            "Roll (°)", "Pitch (°)", "Yaw (°)", "IK Status"
        ])
        self.tblWaypoints.verticalHeader().setVisible(False)
        self.tblWaypoints.setAlternatingRowColors(True)
        self.tblWaypoints.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblWaypoints.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        wp_hdr = self.tblWaypoints.horizontalHeader()
        for col in range(9):
            wp_hdr.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        wp_hdr.setSectionResizeMode(9, QHeaderView.ResizeMode.Stretch)
        wp_layout.addWidget(self.tblWaypoints, stretch=1)

        v_splitter.addWidget(wp_group)

        # ==============================================================
        # BOTTOM PANE: Left = Planner/Preview/Export | Right = Plot & Effort Check
        # ==============================================================
        bottom_widget = QWidget()
        bottom_h_layout = QHBoxLayout(bottom_widget)
        bottom_h_layout.setContentsMargins(0, 0, 0, 0)
        bottom_h_layout.setSpacing(10)

        # --- Left Group: Trajectory Solver, Scrubber & Motion Export ---
        ctrl_group = QGroupBox("Trajectory Generation, Preview && Export to SimPhant")
        ctrl_layout = QVBoxLayout(ctrl_group)

        cfg_grid = QGridLayout()
        cfg_grid.addWidget(QLabel("Timing Profile:"), 0, 0)
        self.cmbTimingMode = QComboBox()
        self.cmbTimingMode.addItem("Quintic Rest-to-Rest (Smooth Stop at Each Waypoint)", "quintic_stop")
        self.cmbTimingMode.addItem("Continuous C² Spline (Pass Through Waypoints)", "smooth_spline")
        self.cmbTimingMode.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.cmbTimingMode.setMinimumContentsLength(14)
        self.cmbTimingMode.setToolTip(
            "Choose whether the robot comes to a smooth C² stop at each waypoint or cruises continuously through interior waypoints."
        )
        cfg_grid.addWidget(self.cmbTimingMode, 0, 1, 1, 3)

        cfg_grid.addWidget(QLabel("Sample Rate:"), 1, 0)
        self.spnSampleRateHz = QSpinBox()
        self.spnSampleRateHz.setRange(20, 1000)
        self.spnSampleRateHz.setSingleStep(25)
        self.spnSampleRateHz.setValue(100)
        self.spnSampleRateHz.setSuffix(" Hz")
        self.spnSampleRateHz.setToolTip(
            "Number of IK trajectory samples per second written into the exported spline CSV files."
        )
        cfg_grid.addWidget(self.spnSampleRateHz, 1, 1)

        self.lblIkHint = QLabel("(Uses IK Mode && Limits from Tab 1)")
        cfg_grid.addWidget(self.lblIkHint, 1, 2, 1, 2)
        ctrl_layout.addLayout(cfg_grid)

        self.btnSolveTrajectory = QPushButton("1. Solve Trajectory IK && Preview 3D Path")
        self.btnSolveTrajectory.setMinimumHeight(34)
        self.btnSolveTrajectory.setStyleSheet(
            "QPushButton { background-color: #1f6feb; color: white; font-weight: bold; font-size: 12px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #1158c7; }"
        )
        self.btnSolveTrajectory.setToolTip(
            "Compute warm-started Inverse Kinematics across the entire timeline and draw the 3D TCP path."
        )
        ctrl_layout.addWidget(self.btnSolveTrajectory)

        # Preview Scrubber Row
        scrub_row = QHBoxLayout()
        self.btnPlayPreview = QPushButton("▶ Play Preview")
        self.btnPlayPreview.setEnabled(False)
        self.btnPlayPreview.setToolTip("Animate the solved kinematic trajectory directly in the 3D viewport.")
        scrub_row.addWidget(self.btnPlayPreview)

        self.sldPreviewTime = QSlider(Qt.Orientation.Horizontal)
        self.sldPreviewTime.setRange(0, 0)
        self.sldPreviewTime.setEnabled(False)
        self.sldPreviewTime.setToolTip("Scrub through the solved trajectory in time to inspect robot posture and clearance.")
        scrub_row.addWidget(self.sldPreviewTime, stretch=1)

        self.lblPreviewTime = QLabel("t = 0.000 / 0.000 s")
        scrub_row.addWidget(self.lblPreviewTime)
        ctrl_layout.addLayout(scrub_row)

        self.chkSyncSimTime = QCheckBox("Sync Main Simulation Time (T_end) to Trajectory")
        self.chkSyncSimTime.setChecked(True)
        self.chkSyncSimTime.setToolTip(
            "Automatically set SimPhant's Simulation Time field to match the last waypoint's timestamp when exporting."
        )
        ctrl_layout.addWidget(self.chkSyncSimTime)

        self.btnExportMotions = QPushButton("2. Apply to Scene as JointMotions (Spline Drivers)")
        self.btnExportMotions.setMinimumHeight(34)
        self.btnExportMotions.setEnabled(False)
        self.btnExportMotions.setToolTip(
            "Snap the robot to Waypoint 1 (t=0), write per-joint spline CSVs, and create/update JointMotion drivers in SimPhant."
        )
        ctrl_layout.addWidget(self.btnExportMotions)

        self.lblTrajStatus = QLabel(
            "Add at least 2 waypoints (e.g. pose robot → '+ Add Current Robot Pose'), then click '1. Solve Trajectory IK'."
        )
        self.lblTrajStatus.setWordWrap(True)
        self.lblTrajStatus.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        self.lblTrajStatus.setStyleSheet("background-color: #f8f9fa; color: #111111; padding: 6px; font-weight: bold;")
        ctrl_layout.addWidget(self.lblTrajStatus)
        ctrl_layout.addStretch(1)

        bottom_h_layout.addWidget(ctrl_group, stretch=2)

        # --- Right Group: Trajectory Plot & Post-Solve Actuator Effort Check ---
        plot_group = QGroupBox("Trajectory Curves && Inverse-Dynamics Actuator Effort Check")
        plot_layout = QVBoxLayout(plot_group)

        plot_bar = QHBoxLayout()
        plot_bar.addWidget(QLabel("Plot:"))
        self.cmbTrajPlotMode = QComboBox()
        self.cmbTrajPlotMode.addItem("Planned Joint Positions q(t) [deg / mm]", "pos")
        self.cmbTrajPlotMode.addItem("Planned Joint Velocities dq/dt [deg/s / mm/s]", "vel")
        self.cmbTrajPlotMode.addItem("Planned TCP Tracking Error [mm]", "err")
        self.cmbTrajPlotMode.addItem("Solved Actuator Effort τ(t) from Last MBSolver Run [Nm / N]", "effort")
        self.cmbTrajPlotMode.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.cmbTrajPlotMode.setMinimumContentsLength(14)
        self.cmbTrajPlotMode.setToolTip("Select which trajectory or dynamic actuator curve to display in the chart.")
        plot_bar.addWidget(self.cmbTrajPlotMode, stretch=1)

        self.btnCheckTorques = QPushButton("Check Peak Torques (Last Solve)")
        self.btnCheckTorques.setToolTip(
            "Extract required inverse-dynamics actuator torques/forces from the most recent MBSolver simulation "
            "and compare them against each joint's Max Effort rating."
        )
        plot_bar.addWidget(self.btnCheckTorques)
        plot_layout.addLayout(plot_bar)

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True)
        self.plotTraj = pg.PlotWidget()
        self.plotTraj.showGrid(x=True, y=True, alpha=0.3)
        self.plotTraj.setLabel('bottom', "Time", units='s')
        self.plotTraj.setLabel('left', "Value")
        self.plotTrajLegend = self.plotTraj.addLegend(offset=(8, 8))
        plot_layout.addWidget(self.plotTraj, stretch=1)

        self.lblEffortSummary = QLabel(
            "Actuator Effort Check: Run SimPhant's 'Solve' after exporting JointMotions, then click 'Check Peak Torques'."
        )
        self.lblEffortSummary.setWordWrap(True)
        self.lblEffortSummary.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
        plot_layout.addWidget(self.lblEffortSummary)

        bottom_h_layout.addWidget(plot_group, stretch=3)
        v_splitter.addWidget(bottom_widget)
        v_splitter.setStretchFactor(0, 2)
        v_splitter.setStretchFactor(1, 3)

        # --- Wire Tab 2 Signals ---
        self.btnAddCurrPoseWp.clicked.connect(self.add_waypoint_from_current_pose)
        self.btnAddRFrameWp.clicked.connect(self.add_waypoint_from_selected_rf)
        self.btnPreviewSelectedWp.clicked.connect(self.jump_robot_to_selected_waypoint)
        self.btnMoveWpUp.clicked.connect(lambda: self._move_selected_waypoint(-1))
        self.btnMoveWpDown.clicked.connect(lambda: self._move_selected_waypoint(+1))
        self.btnDeleteWp.clicked.connect(self.delete_selected_waypoint)
        self.btnClearWps.clicked.connect(self.clear_all_waypoints)
        self.chkShow3DPath.toggled.connect(self._on_show_3d_path_toggled)

        self.btnSolveTrajectory.clicked.connect(self.solve_trajectory_from_ui)
        self.btnPlayPreview.clicked.connect(self.toggle_trajectory_preview_playback)
        self.sldPreviewTime.valueChanged.connect(self._on_preview_slider_changed)
        self.btnExportMotions.clicked.connect(self.export_trajectory_motions_from_ui)
        self.cmbTrajPlotMode.currentIndexChanged.connect(self._refresh_trajectory_plot)
        self.btnCheckTorques.clicked.connect(self.check_peak_torques_from_last_solve)

    @staticmethod
    def _make_coord_spinbox(min_val, max_val, step, suffix):
        spn = QDoubleSpinBox()
        spn.setDecimals(3)
        spn.setRange(min_val, max_val)
        spn.setSingleStep(step)
        spn.setSuffix(suffix)
        spn.setMinimumWidth(110)
        return spn

    # ------------------------------------------------------------------
    # Theme-Aware Palette & Dynamic Label Styling (Dark / Light Windows Mode)
    # ------------------------------------------------------------------
    def _theme_colors(self) -> dict[str, str]:
        target_widget = getattr(self, "_content_widget", None) or self
        if is_dark_ui_theme(target_widget):
            return {
                "blue": "#66d9ef",
                "green": "#a6e22e",
                "orange": "#ffb86c",
                "red": "#ff6b6b",
                "muted": "#b0b8c4",
                "btn_dis_bg": "#555555",
                "btn_dis_fg": "#aaaaaa",
            }
        return {
            "blue": "#0550ae",
            "green": "#116329",
            "orange": "#b34700",
            "red": "#a40e26",
            "muted": "#57606a",
            "btn_dis_bg": "#d0d7de",
            "btn_dis_fg": "#57606a",
        }

    def _style_chain_summary_label(self, colors: dict[str, str] | None = None):
        c = colors or self._theme_colors()
        col = c["red"] if self._chain_summary_state == "error" else c["blue"]
        self.lblChainSummary.setStyleSheet(f"color: {col}; font-weight: bold;")

    def _style_perf_stats_label(self, colors: dict[str, str] | None = None):
        c = colors or self._theme_colors()
        if self._perf_stats_state == "warn":
            self.lblPerfStats.setStyleSheet(
                f"color: {c['orange']}; font-family: Consolas, monospace; font-size: 11px; font-weight: bold;"
            )
        else:
            self.lblPerfStats.setStyleSheet(
                f"color: {c['green']}; font-family: Consolas, monospace; font-size: 11px;"
            )

    def _style_effort_summary_label(self, colors: dict[str, str] | None = None):
        c = colors or self._theme_colors()
        state_map = {
            "info": c["blue"],
            "ok": c["green"],
            "warn": c["orange"],
            "error": c["red"],
        }
        col = state_map.get(self._effort_summary_state, c["blue"])
        self.lblEffortSummary.setStyleSheet(f"color: {col}; font-size: 11px; font-weight: bold;")

    def _style_waypoint_status_item(self, w_dict: dict, colors: dict[str, str] | None = None):
        c = colors or self._theme_colors()
        st = w_dict.get("stat_state", "pending")
        if st == "ok":
            fg = c["green"]
        elif st == "warn":
            fg = c["orange"]
        else:
            fg = c["muted"]
        w_dict["item_stat"].setForeground(QColor(fg))

    def apply_theme_colors(self):
        """Applies high-contrast dark or light accent colors matching the current OS / Qt theme."""
        try:
            c = self._theme_colors()
            self._style_chain_summary_label(c)
            self._style_perf_stats_label(c)
            self._style_effort_summary_label(c)
            self.lblCurrPoseHdr.setStyleSheet(f"font-weight: bold; color: {c['blue']};")
            self.lblTargPoseHdr.setStyleSheet(f"font-weight: bold; color: {c['orange']};")
            self.lblIkHint.setStyleSheet(f"color: {c['blue']}; font-size: 11px;")
            self.lblPreviewTime.setStyleSheet(
                f"font-family: Consolas, monospace; font-weight: bold; color: {c['blue']};"
            )
            self.btnExportMotions.setStyleSheet(
                "QPushButton { background-color: #238636; color: white; font-weight: bold; font-size: 12px; border-radius: 4px; }"
                "QPushButton:hover { background-color: #2ea043; }"
                f"QPushButton:disabled {{ background-color: {c['btn_dis_bg']}; color: {c['btn_dis_fg']}; }}"
            )
            for w in getattr(self, "_wp_row_widgets", []):
                self._style_waypoint_status_item(w, c)
        except RuntimeError:
            pass

    def _install_theme_change_hooks(self):
        app = QApplication.instance()
        if app is None:
            return
        style_hints = app.styleHints()
        if style_hints is not None and hasattr(style_hints, "colorSchemeChanged"):
            try:
                style_hints.colorSchemeChanged.connect(self._schedule_theme_refresh)
            except (RuntimeError, TypeError):
                pass

    def _schedule_theme_refresh(self, *args):
        if self._theme_refresh_pending:
            return
        self._theme_refresh_pending = True
        QTimer.singleShot(0, self._flush_theme_refresh)

    def _flush_theme_refresh(self):
        self._theme_refresh_pending = False
        self.apply_theme_colors()

    def changeEvent(self, event):
        if event.type() in (
            QEvent.Type.PaletteChange,
            QEvent.Type.ApplicationPaletteChange,
            QEvent.Type.ThemeChange,
            QEvent.Type.StyleChange,
        ):
            self._schedule_theme_refresh()
        super().changeEvent(event)

    # ------------------------------------------------------------------
    # Scene Discovery & Chain Population
    # ------------------------------------------------------------------
    def populate_scene_selectors(self):
        """Populates Base Body, End-Effector Body, TCP RF, and Target RF combo boxes from the scene."""
        self._updating_ui = True
        try:
            prev_base = self.cmbBaseBody.currentData()
            prev_ee = self.cmbEEBody.currentData()

            self.cmbBaseBody.clear()
            self.cmbEEBody.clear()

            enabled_bodies = [
                b for b in self.app.physics_bodies.values()
                if not b.is_ground and getattr(b, 'enabled', True)
            ]
            for b in enabled_bodies:
                self.cmbBaseBody.addItem(b.name, b.name)
                self.cmbEEBody.addItem(b.name, b.name)

            # Smart default selection: root link -> deepest leaf link
            default_base, default_ee = self._guess_default_chain_endpoints(enabled_bodies)
            base_to_pick = prev_base if prev_base in self.app.physics_bodies else default_base
            ee_to_pick = prev_ee if prev_ee in self.app.physics_bodies else default_ee

            if base_to_pick:
                idx = self.cmbBaseBody.findData(base_to_pick)
                if idx >= 0:
                    self.cmbBaseBody.setCurrentIndex(idx)
            if ee_to_pick:
                idx = self.cmbEEBody.findData(ee_to_pick)
                if idx >= 0:
                    self.cmbEEBody.setCurrentIndex(idx)

            self._populate_tcp_rf_combo()
            self._populate_target_rf_combo()
        finally:
            self._updating_ui = False

    def _guess_default_chain_endpoints(self, enabled_bodies):
        """Heuristically finds the root link and the longest-chain leaf link in the scene."""
        if len(enabled_bodies) < 2:
            names = [b.name for b in enabled_bodies]
            return (names[0] if names else None), (names[-1] if len(names) > 1 else None)

        child_set = set()
        parent_set = set()
        ground_anchored = set()
        adj = {}
        for j in getattr(self.app, 'joints_list', []):
            if not getattr(j, 'enabled', True):
                continue
            bi, bj = j.body_i, j.body_j
            if bi.is_ground and not bj.is_ground:
                ground_anchored.add(bj.name)
                continue
            if bj.is_ground and not bi.is_ground:
                ground_anchored.add(bi.name)
                continue
            if not bi.is_ground and not bj.is_ground:
                parent_set.add(bi.name)
                child_set.add(bj.name)
                adj.setdefault(bi.name, []).append(bj.name)
                adj.setdefault(bj.name, []).append(bi.name)

        # Prefer a body anchored to Ground, or a parent body that is never a child
        roots = [b.name for b in enabled_bodies if b.name in ground_anchored]
        if not roots:
            roots = [b.name for b in enabled_bodies if b.name in parent_set and b.name not in child_set]
        base_name = roots[0] if roots else enabled_bodies[0].name

        # BFS from base_name to find the farthest connected body
        visited = {base_name: 0}
        queue = deque([base_name])
        farthest_name = enabled_bodies[-1].name
        max_dist = -1
        while queue:
            curr = queue.popleft()
            d = visited[curr]
            if d > max_dist and curr != base_name:
                max_dist = d
                farthest_name = curr
            for nbr in adj.get(curr, []):
                if nbr not in visited:
                    visited[nbr] = d + 1
                    queue.append(nbr)

        return base_name, farthest_name

    def _populate_tcp_rf_combo(self):
        prev_tcp = self.cmbTCPRF.currentData()
        self.cmbTCPRF.blockSignals(True)
        self.cmbTCPRF.clear()

        ee_name = self.cmbEEBody.currentData()
        ee_body = self.app.physics_bodies.get(ee_name) if ee_name else None

        self.cmbTCPRF.addItem(f"<End-Effector CoG ({ee_name or 'None'})>", "__EE_COG__")

        preferred_rf_name = None
        for rf in getattr(self.app, 'rframes', []):
            if rf.name == "Global_RF" or getattr(rf, 'is_cog', False):
                continue
            parent_name = rf.parent_body.name if getattr(rf, 'parent_body', None) else "Ground"
            label = f"{rf.name}  [{parent_name}]"
            self.cmbTCPRF.addItem(label, rf.name)
            if ee_body is not None and getattr(rf, 'parent_body', None) is ee_body:
                # Prefer a non-joint TCP frame like 'tool0' if available on the EE body
                if not rf.name.startswith("RF_joint") and preferred_rf_name is None:
                    preferred_rf_name = rf.name

        if prev_tcp and self.cmbTCPRF.findData(prev_tcp) >= 0:
            self.cmbTCPRF.setCurrentIndex(self.cmbTCPRF.findData(prev_tcp))
        elif preferred_rf_name and self.cmbTCPRF.findData(preferred_rf_name) >= 0:
            self.cmbTCPRF.setCurrentIndex(self.cmbTCPRF.findData(preferred_rf_name))
        else:
            self.cmbTCPRF.setCurrentIndex(0)

        self.cmbTCPRF.blockSignals(False)

    def _populate_target_rf_combo(self):
        prev_targ = self.cmbTargetRF.currentData()
        prev_wp_rf = self.cmbWpSourceRF.currentData() if hasattr(self, 'cmbWpSourceRF') else None
        self.cmbTargetRF.blockSignals(True)
        self.cmbTargetRF.clear()
        if hasattr(self, 'cmbWpSourceRF'):
            self.cmbWpSourceRF.blockSignals(True)
            self.cmbWpSourceRF.clear()
        for rf in getattr(self.app, 'rframes', []):
            if getattr(rf, 'is_cog', False):
                continue
            self.cmbTargetRF.addItem(rf.name, rf.name)
            if hasattr(self, 'cmbWpSourceRF'):
                self.cmbWpSourceRF.addItem(rf.name, rf.name)
        if prev_targ and self.cmbTargetRF.findData(prev_targ) >= 0:
            self.cmbTargetRF.setCurrentIndex(self.cmbTargetRF.findData(prev_targ))
        if hasattr(self, 'cmbWpSourceRF') and prev_wp_rf and self.cmbWpSourceRF.findData(prev_wp_rf) >= 0:
            self.cmbWpSourceRF.setCurrentIndex(self.cmbWpSourceRF.findData(prev_wp_rf))
        self.cmbTargetRF.blockSignals(False)
        if hasattr(self, 'cmbWpSourceRF'):
            self.cmbWpSourceRF.blockSignals(False)

    def _on_ee_body_changed(self):
        if self._updating_ui:
            return
        self._populate_tcp_rf_combo()
        self.rebuild_chain(auto_quiet=True)

    def _on_chain_selector_changed(self):
        if self._updating_ui:
            return
        self.rebuild_chain(auto_quiet=True)

    def rebuild_chain(self, auto_quiet=False):
        """Constructs the `KinematicChain` for the selected Base Body, EE Body, and TCP RF."""
        self.stop_trajectory_preview_playback()
        self.clear_3d_preview_actors(render=False)
        self._invalidate_solved_trajectory()

        base_name = self.cmbBaseBody.currentData()
        ee_name = self.cmbEEBody.currentData()
        tcp_key = self.cmbTCPRF.currentData()

        if not base_name or not ee_name:
            self.chain = None
            self.tblJoints.setRowCount(0)
            self.lblChainSummary.setText("Select a valid Base Body and End-Effector Body.")
            return

        tcp_rf = None
        if tcp_key and tcp_key != "__EE_COG__":
            tcp_rf = next((r for r in getattr(self.app, 'rframes', []) if r.name == tcp_key), None)

        try:
            self.chain = KinematicChain(
                physics_bodies=self.app.physics_bodies,
                joints_list=getattr(self.app, 'joints_list', []),
                base_body_name=base_name,
                ee_body_name=ee_name,
                tcp_rf=tcp_rf,
                rframes_list=getattr(self.app, 'rframes', []),
            )
        except RoboticsChainError as exc:
            self.chain = None
            self.tblJoints.setRowCount(0)
            self._chain_summary_state = "error"
            self.lblChainSummary.setText(f"[WARN] {exc}")
            self._style_chain_summary_label()
            if not auto_quiet:
                QMessageBox.warning(self, "Kinematic Chain Error", str(exc))
            return

        tcp_label = tcp_rf.name if tcp_rf is not None else f"CoG({ee_name})"
        body_path_str = " → ".join(b.name for b in self.chain.chain_bodies)
        self._chain_summary_state = "info"
        self._style_chain_summary_label()
        self.lblChainSummary.setText(
            f"Active Chain ({self.chain.num_dof} DOF, TCP: {tcp_label}):  {body_path_str}"
        )

        self._populate_joint_table()
        fk = self.chain.forward_kinematics(self.chain.current_q)
        self._update_tcp_readout(fk.tcp_pos, fk.tcp_rot)
        self.copy_current_tcp_to_target()
        self.lblIKStatus.setText(
            f"Chain ready ({self.chain.num_dof} active joints). Drag sliders for FK or click 'Solve IK'."
        )

    # ------------------------------------------------------------------
    # Joint Table Population & Interactive FK Sliders
    # ------------------------------------------------------------------
    @staticmethod
    def _unit_scale(joint) -> float:
        """Conversion factor from internal SI (`rad` or `m`) to UI display (`deg` or `mm`)."""
        if joint.joint_type == JointType.PRISMATIC:
            return 1000.0
        return float(180.0 / np.pi)

    @staticmethod
    def _default_unbounded_range_ui(joint):
        if joint.joint_type == JointType.PRISMATIC:
            return -1000.0, 1000.0
        return -180.0, 180.0

    def _populate_joint_table(self):
        self._updating_ui = True
        self._row_widgets = []
        self.tblJoints.setRowCount(0)

        if self.chain is None:
            self._updating_ui = False
            return

        self.tblJoints.setRowCount(self.chain.num_dof)
        for row, step in enumerate(self.chain.active_steps):
            joint = step.joint
            scale = self._unit_scale(joint)
            is_rev = (joint.joint_type == JointType.REVOLUTE)
            unit_str = "°" if is_rev else " mm"

            # Col 0: #
            item_idx = QTableWidgetItem(str(row + 1))
            item_idx.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_idx.setFlags(item_idx.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tblJoints.setItem(row, 0, item_idx)

            # Col 1: Joint Name
            item_name = QTableWidgetItem(joint.name)
            item_name.setFlags(item_name.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tblJoints.setItem(row, 1, item_name)

            # Col 2: Child Body
            item_child = QTableWidgetItem(step.child_body.name)
            item_child.setFlags(item_child.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tblJoints.setItem(row, 2, item_child)

            # Col 3: Type
            item_type = QTableWidgetItem("Revolute" if is_rev else "Prismatic")
            item_type.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_type.setFlags(item_type.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tblJoints.setItem(row, 3, item_type)

            # Col 4: Limit On checkbox
            chk_lim = QCheckBox()
            chk_lim.setChecked(bool(getattr(joint, 'limits_enabled', False)))
            chk_lim.setToolTip("Enable or disable stroke limits for this joint.")
            chk_container = QWidget()
            chk_lay = QHBoxLayout(chk_container)
            chk_lay.setContentsMargins(0, 0, 0, 0)
            chk_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_lay.addWidget(chk_lim)
            self.tblJoints.setCellWidget(row, 4, chk_container)

            # Col 5: Min Limit spinbox
            spn_min = QDoubleSpinBox()
            spn_min.setDecimals(2)
            spn_min.setRange(-100000.0, 100000.0)
            spn_min.setSingleStep(5.0 if is_rev else 10.0)
            spn_min.setSuffix(unit_str)
            spn_min.setValue(float(getattr(joint, 'limit_min', -np.pi)) * scale)
            spn_min.setToolTip("Lower mechanical stroke limit for this joint.")
            self.tblJoints.setCellWidget(row, 5, spn_min)

            # Col 6: Max Limit spinbox
            spn_max = QDoubleSpinBox()
            spn_max.setDecimals(2)
            spn_max.setRange(-100000.0, 100000.0)
            spn_max.setSingleStep(5.0 if is_rev else 10.0)
            spn_max.setSuffix(unit_str)
            spn_max.setValue(float(getattr(joint, 'limit_max', +np.pi)) * scale)
            spn_max.setToolTip("Upper mechanical stroke limit for this joint.")
            self.tblJoints.setCellWidget(row, 6, spn_max)

            # Col 7: Current q spinbox
            spn_q = QDoubleSpinBox()
            spn_q.setDecimals(3)
            spn_q.setRange(-100000.0, 100000.0)
            spn_q.setSingleStep(1.0 if is_rev else 5.0)
            spn_q.setSuffix(unit_str)
            spn_q.setValue(float(self.chain.current_q[row]) * scale)
            spn_q.setToolTip("Current joint angle/displacement (edit to pose via Forward Kinematics).")
            self.tblJoints.setCellWidget(row, 7, spn_q)

            # Col 8: Interactive Pose Slider
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, self.SLIDER_STEPS)
            slider.setToolTip("Drag or use arrow keys to interactively pose this joint in 3D.")
            self.tblJoints.setCellWidget(row, 8, slider)

            # Col 9: Max Effort spinbox
            spn_eff = QDoubleSpinBox()
            spn_eff.setDecimals(2)
            spn_eff.setRange(0.0, 1000000.0)
            spn_eff.setSingleStep(5.0)
            spn_eff.setSuffix(" Nm" if is_rev else " N")
            spn_eff.setValue(float(getattr(joint, 'max_effort', 0.0)))
            spn_eff.setToolTip("Maximum actuator torque/force rating for this joint.")
            self.tblJoints.setCellWidget(row, 9, spn_eff)

            row_dict = {
                "joint": joint,
                "scale": scale,
                "chk_lim": chk_lim,
                "spn_min": spn_min,
                "spn_max": spn_max,
                "spn_q": spn_q,
                "slider": slider,
                "spn_eff": spn_eff,
            }
            self._row_widgets.append(row_dict)
            self._sync_row_slider_from_q(row)

            # Connect per-row signals
            chk_lim.toggled.connect(lambda state, r=row: self._on_row_limit_changed(r))
            spn_min.valueChanged.connect(lambda val, r=row: self._on_row_limit_changed(r))
            spn_max.valueChanged.connect(lambda val, r=row: self._on_row_limit_changed(r))
            spn_eff.valueChanged.connect(lambda val, r=row: self._on_row_effort_changed(r))
            spn_q.valueChanged.connect(lambda val, r=row: self._on_row_q_spinbox_changed(r))
            slider.sliderPressed.connect(self._on_slider_drag_started)
            slider.sliderReleased.connect(self._on_slider_drag_ended)
            slider.valueChanged.connect(lambda s_val, r=row: self._on_row_slider_changed(r))

        # Size non-slider columns once to contents, then lock to Interactive so slider drags never relayout columns
        header = self.tblJoints.horizontalHeader()
        for col in (0, 1, 2, 3, 4, 5, 6, 7, 9):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.tblJoints.resizeColumnsToContents()
        for col in (0, 1, 2, 3, 4, 5, 6, 7, 9):
            w_col = max(self.tblJoints.columnWidth(col) + (12 if col == 7 else 4), 36)
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
            self.tblJoints.setColumnWidth(col, w_col)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)

        self._has_saturated_highlights = False
        self._updating_ui = False

    def _get_row_effective_bounds_ui(self, row):
        w = self._row_widgets[row]
        joint = w["joint"]
        if self.chkEnforceLimits.isChecked() and w["chk_lim"].isChecked():
            lo = float(w["spn_min"].value())
            hi = float(w["spn_max"].value())
            if lo > hi:
                lo, hi = hi, lo
            if abs(hi - lo) < 1e-6:
                hi = lo + 1.0
            return lo, hi
        return self._default_unbounded_range_ui(joint)

    def _sync_row_slider_from_q(self, row):
        w = self._row_widgets[row]
        lo, hi = self._get_row_effective_bounds_ui(row)
        q_ui = float(w["spn_q"].value())
        ratio = (q_ui - lo) / (hi - lo) if hi > lo else 0.5
        s_val = int(round(np.clip(ratio, 0.0, 1.0) * self.SLIDER_STEPS))
        w["slider"].blockSignals(True)
        w["slider"].setValue(s_val)
        w["slider"].blockSignals(False)

    def _on_row_limit_changed(self, row):
        if self._updating_ui or self.chain is None:
            return
        w = self._row_widgets[row]
        joint = w["joint"]
        scale = w["scale"]

        lo_ui = float(w["spn_min"].value())
        hi_ui = float(w["spn_max"].value())
        if lo_ui > hi_ui:
            lo_ui, hi_ui = hi_ui, lo_ui

        joint.limits_enabled = bool(w["chk_lim"].isChecked())
        joint.limit_min = lo_ui / scale
        joint.limit_max = hi_ui / scale

        # Clamp current q if limits are active
        if self.chkEnforceLimits.isChecked() and joint.limits_enabled:
            q_ui = float(w["spn_q"].value())
            if q_ui < lo_ui or q_ui > hi_ui:
                w["spn_q"].setValue(float(np.clip(q_ui, lo_ui, hi_ui)))
        self._sync_row_slider_from_q(row)

    def _on_row_effort_changed(self, row):
        if self._updating_ui or self.chain is None:
            return
        w = self._row_widgets[row]
        w["joint"].max_effort = float(w["spn_eff"].value())

    def _on_enforce_limits_toggled(self, checked):
        if self._updating_ui or self.chain is None:
            return
        q_clamped = self.chain.clamp_q(self.chain.current_q, enforce_limits=checked)
        self._apply_q_and_sync_ui(q_clamped)

    def _set_all_joint_limits_enabled(self, enabled: bool):
        if self.chain is None:
            return
        self._updating_ui = True
        for row, w in enumerate(self._row_widgets):
            w["chk_lim"].setChecked(enabled)
            w["joint"].limits_enabled = enabled
        self._updating_ui = False
        q_clamped = self.chain.clamp_q(
            self.chain.current_q, enforce_limits=self.chkEnforceLimits.isChecked()
        )
        self._apply_q_and_sync_ui(q_clamped)

    def _on_row_q_spinbox_changed(self, row):
        if self._updating_ui or self.chain is None:
            return
        w = self._row_widgets[row]
        q_ui = float(w["spn_q"].value())
        if self.chkEnforceLimits.isChecked() and w["chk_lim"].isChecked():
            lo, hi = self._get_row_effective_bounds_ui(row)
            q_ui = float(np.clip(q_ui, lo, hi))
            if abs(q_ui - w["spn_q"].value()) > 1e-6:
                w["spn_q"].blockSignals(True)
                w["spn_q"].setValue(q_ui)
                w["spn_q"].blockSignals(False)

        self.chain.current_q[row] = q_ui / w["scale"]
        self._sync_row_slider_from_q(row)
        self._clear_saturation_highlights()
        self._request_fk_render()

    def _on_row_slider_changed(self, row):
        if self._updating_ui or self.chain is None:
            return
        w = self._row_widgets[row]
        lo, hi = self._get_row_effective_bounds_ui(row)
        ratio = float(w["slider"].value()) / float(self.SLIDER_STEPS)
        q_ui = lo + ratio * (hi - lo)

        w["spn_q"].blockSignals(True)
        w["spn_q"].setValue(q_ui)
        w["spn_q"].blockSignals(False)

        self.chain.current_q[row] = q_ui / w["scale"]
        self._clear_saturation_highlights()
        self._request_fk_render()

    def _request_fk_render(self):
        """
        Non-starving leading + trailing frame throttle:
        - Always renders immediately once MIN_RENDER_INTERVAL_S has elapsed, even if a trailing QTimer
          was pending (prevents Win32 WM_MOUSEMOVE / WM_KEYDOWN input streams from starving WM_TIMER!).
        - Schedules a PreciseTimer trailing flush so the final slider position is always rendered.
        """
        if self.chain is None:
            return
        now = perf_counter()
        if self._pending_event_count == 0:
            self._first_pending_event_time = now
        self._pending_event_count += 1

        elapsed = now - self._last_render_time
        if elapsed >= self.MIN_RENDER_INTERVAL_S:
            if self._fk_coalesce_timer.isActive():
                self._fk_coalesce_timer.stop()
            self._flush_coalesced_fk()
        elif not self._fk_coalesce_timer.isActive():
            wait_ms = max(1, int((self.MIN_RENDER_INTERVAL_S - elapsed) * 1000.0))
            self._fk_coalesce_timer.start(wait_ms)

    def _on_slider_drag_started(self):
        if gc.isenabled() and not self._gc_paused_for_drag:
            gc.disable()
            self._gc_paused_for_drag = True

    def _on_slider_drag_ended(self):
        if self._fk_coalesce_timer.isActive():
            self._fk_coalesce_timer.stop()
            self._flush_coalesced_fk()
        self._resume_gc_if_paused()

    def _flush_coalesced_fk(self):
        if self.chain is None:
            return
        if QAccessible.isActive():
            QAccessible.setActive(False)
        t_start = perf_counter()
        dt_between_ms = (t_start - self._prev_frame_wall_time) * 1000.0 if self._prev_frame_wall_time > 0.0 else 0.0
        self._prev_frame_wall_time = t_start
        self._last_render_time = t_start

        events_merged = max(1, self._pending_event_count)
        event_lat_start = self._first_pending_event_time if self._pending_event_count > 0 else t_start
        self._pending_event_count = 0

        perf = {}
        fk = self.chain.apply_fk_to_scene(self.chain.current_q, app=self.app, render=True, perf_out=perf)

        t_ui0 = perf_counter()
        self._update_tcp_readout(fk.tcp_pos, fk.tcp_rot)
        t_end = perf_counter()

        perf["ui_ms"] = (t_end - t_ui0) * 1000.0
        perf["total_ms"] = (t_end - t_start) * 1000.0
        perf["lat_ms"] = (t_end - event_lat_start) * 1000.0
        perf["dt_between_ms"] = dt_between_ms
        perf["events"] = events_merged
        self._record_perf_telemetry("FK", perf)

    def _record_perf_telemetry(self, source_tag: str, perf: dict):
        self._perf_frame_counter += 1
        total_ms = perf.get("total_ms", 0.0)
        fk_ms = perf.get("fk_ms", 0.0)
        vtk_ms = perf.get("vtk_ms", 0.0)
        gl_ms = perf.get("gl_ms", 0.0)
        ui_ms = perf.get("ui_ms", 0.0)
        lat_ms = perf.get("lat_ms", total_ms)
        dt_between = perf.get("dt_between_ms", 0.0)
        events = perf.get("events", 1)

        # Effective FPS during continuous motion (if consecutive frames are within 400 ms), else instantaneous capacity
        if 1.0 < dt_between < 400.0:
            fps_est = 1000.0 / dt_between
        else:
            fps_est = 1000.0 / max(total_ms, 0.1)

        mode_str = "Docked" if self._is_docked else "Floating"
        dbg_str = "YES" if self._debugger_active else "No"

        summary_text = (
            f"Perf #{self._perf_frame_counter} [{source_tag} | {mode_str} | Dbg:{dbg_str}]: "
            f"Work={total_ms:.1f}ms (~{fps_est:.0f} FPS) | "
            f"FK={fk_ms:.2f}ms  VTK={vtk_ms:.2f}ms  OpenGL={gl_ms:.2f}ms  UI={ui_ms:.2f}ms | "
            f"Lat={lat_ms:.1f}ms (ev={events})"
        )
        self._perf_stats_state = "warn" if (total_ms > 30.0 or lat_ms > 50.0) else "ok"
        self._style_perf_stats_label()
        self.lblPerfStats.setText(summary_text)

    def _apply_q_and_sync_ui(self, q, saturated_names=None):
        if self.chain is None:
            return
        self._fk_coalesce_timer.stop()
        self._ik_coalesce_timer.stop()
        self._pending_event_count = 0
        t_start = perf_counter()
        self._last_render_time = t_start
        saturated_set = set(saturated_names or [])
        self._updating_ui = True
        try:
            if QAccessible.isActive():
                QAccessible.setActive(False)
            perf = {}
            fk = self.chain.apply_fk_to_scene(q, app=self.app, render=True, perf_out=perf)
            t_ui0 = perf_counter()
            for row, w in enumerate(self._row_widgets):
                q_ui = float(fk.q[row]) * w["scale"]
                w["spn_q"].setValue(q_ui)
                self._sync_row_slider_from_q(row)
                if w["joint"].name in saturated_set:
                    w["spn_q"].setStyleSheet("background-color: #fff3cd; color: #856404; font-weight: bold;")
                elif self._has_saturated_highlights:
                    w["spn_q"].setStyleSheet("")
            self._has_saturated_highlights = len(saturated_set) > 0
            self._update_tcp_readout(fk.tcp_pos, fk.tcp_rot)
            t_end = perf_counter()
            perf["ui_ms"] = (t_end - t_ui0) * 1000.0
            perf["total_ms"] = (t_end - t_start) * 1000.0
            perf["lat_ms"] = perf["total_ms"]
            perf["dt_between_ms"] = 0.0
            perf["events"] = 1
            self._record_perf_telemetry("IK/Sync", perf)
        finally:
            self._updating_ui = False

    def _clear_saturation_highlights(self):
        if not self._has_saturated_highlights:
            return
        for w in self._row_widgets:
            w["spn_q"].setStyleSheet("")
        self._has_saturated_highlights = False

    def zero_all_joints(self):
        if self.chain is None:
            return
        self.stop_trajectory_preview_playback()
        q_zero = self.chain.clamp_q(
            np.zeros(self.chain.num_dof, dtype=float),
            enforce_limits=self.chkEnforceLimits.isChecked(),
        )
        self._apply_q_and_sync_ui(q_zero)
        self.lblIKStatus.setText("Set all joints to q = 0 (clamped to active stroke limits).")

    def reset_to_initial_pose(self):
        if self.chain is None:
            return
        self.chain.restore_initial_pose(app=self.app, render=True)
        self._apply_q_and_sync_ui(self.chain.initial_q.copy())
        self.lblIKStatus.setStyleSheet("background-color: #f8f9fa; color: #111111; padding: 6px; font-weight: bold;")
        self.lblIKStatus.setText("Restored initial robot pose.")

    # ------------------------------------------------------------------
    # TCP Readout & IK Solver Actions
    # ------------------------------------------------------------------
    def _update_tcp_readout(self, tcp_pos_m, tcp_rot_mat):
        pos_mm = tcp_pos_m * MMtoM
        ori_zyx = matrix_to_pos_angles_deg(tcp_rot_mat)  # [Yaw(Z), Pitch(Y), Roll(X)]
        self.lblCurrX.setText(f"{pos_mm[0]:.3f}")
        self.lblCurrY.setText(f"{pos_mm[1]:.3f}")
        self.lblCurrZ.setText(f"{pos_mm[2]:.3f}")
        self.lblCurrRoll.setText(f"{ori_zyx[2]:.3f}")
        self.lblCurrPitch.setText(f"{ori_zyx[1]:.3f}")
        self.lblCurrYaw.setText(f"{ori_zyx[0]:.3f}")

    def copy_current_tcp_to_target(self):
        if self.chain is None:
            return
        fk = self.chain.forward_kinematics(self.chain.current_q)
        pos_mm = fk.tcp_pos * MMtoM
        ori_zyx = matrix_to_pos_angles_deg(fk.tcp_rot)
        self._set_target_spinboxes(
            pos_mm[0], pos_mm[1], pos_mm[2],
            ori_zyx[2], ori_zyx[1], ori_zyx[0]
        )

    def _set_target_spinboxes(self, x_mm, y_mm, z_mm, roll_deg, pitch_deg, yaw_deg):
        self._updating_ui = True
        try:
            self.dsbTargetX.setValue(float(x_mm))
            self.dsbTargetY.setValue(float(y_mm))
            self.dsbTargetZ.setValue(float(z_mm))
            self.dsbTargetRoll.setValue(float(roll_deg))
            self.dsbTargetPitch.setValue(float(pitch_deg))
            self.dsbTargetYaw.setValue(float(yaw_deg))
        finally:
            self._updating_ui = False

    def load_target_from_selected_rf(self):
        rf_name = self.cmbTargetRF.currentData()
        if not rf_name:
            return
        rf = next((r for r in getattr(self.app, 'rframes', []) if r.name == rf_name), None)
        if rf is None:
            return
        pos_mm = rf.position * MMtoM
        ori_zyx = matrix_to_pos_angles_deg(rf.transform_matrix)
        self._set_target_spinboxes(
            pos_mm[0], pos_mm[1], pos_mm[2],
            ori_zyx[2], ori_zyx[1], ori_zyx[0]
        )
        if self.chkLiveIK.isChecked():
            self.solve_and_apply_ik()

    def create_visual_target_rf(self):
        """Creates a visible RFrame in the SimPhant scene at the current IK Target coordinates."""
        target_pos_m, target_rot = self._get_target_pose_si()
        ori_zyx = matrix_to_pos_angles_deg(target_rot)

        existing_names = {r.name for r in getattr(self.app, 'rframes', [])}
        idx = 1
        rf_name = f"IK_Target_{idx}"
        while rf_name in existing_names:
            idx += 1
            rf_name = f"IK_Target_{idx}"

        new_rf = RFrame(
            name=rf_name,
            position=target_pos_m,
            orientation=ori_zyx,
            transform_matrix=target_rot,
            plotter=self.app.plotter,
            parent_body=self.app.physics_bodies.get("Ground"),
            is_cog=False,
        )
        current_scale = self.app.rframes[0].base_scale if self.app.rframes else 10.0
        new_rf.set_scale(current_scale)
        self.app.rframes.append(new_rf)
        if hasattr(self.app, 'node_rframes'):
            QTreeWidgetItem(self.app.node_rframes, [rf_name])
            self.app.node_rframes.setExpanded(True)

        self._populate_target_rf_combo()
        idx_combo = self.cmbTargetRF.findData(rf_name)
        if idx_combo >= 0:
            self.cmbTargetRF.setCurrentIndex(idx_combo)

        if getattr(self.app, 'plotter', None) is not None:
            self.app.plotter.render()
        self.lblIKStatus.setText(f"Created visual Reference Frame '{rf_name}' at Target Pose.")

    def _get_target_pose_si(self):
        pos_m = np.array([
            self.dsbTargetX.value(),
            self.dsbTargetY.value(),
            self.dsbTargetZ.value(),
        ], dtype=float) / MMtoM
        ori_zyx = np.array([
            self.dsbTargetYaw.value(),
            self.dsbTargetPitch.value(),
            self.dsbTargetRoll.value(),
        ], dtype=float)
        rot_mat = pos_angles_deg_to_matrix(ori_zyx)
        return pos_m, rot_mat

    def _on_ik_mode_changed(self):
        mode = self.cmbIKMode.currentData()
        rot_enabled = (mode != "PositionOnly")
        self.dsbTargetRoll.setEnabled(rot_enabled)
        self.dsbTargetPitch.setEnabled(rot_enabled)
        self.dsbTargetYaw.setEnabled(rot_enabled)
        self.dsbRotTol.setEnabled(rot_enabled)
        if self.chkLiveIK.isChecked():
            self.solve_and_apply_ik()

    def _on_target_spinbox_changed(self):
        if self._updating_ui:
            return
        if self.chkLiveIK.isChecked():
            now = perf_counter()
            elapsed = now - self._last_render_time
            if elapsed >= self.MIN_RENDER_INTERVAL_S:
                if self._ik_coalesce_timer.isActive():
                    self._ik_coalesce_timer.stop()
                self._flush_coalesced_live_ik()
            elif not self._ik_coalesce_timer.isActive():
                wait_ms = max(1, int((self.MIN_RENDER_INTERVAL_S - elapsed) * 1000.0))
                self._ik_coalesce_timer.start(wait_ms)

    def _flush_coalesced_live_ik(self):
        self._last_render_time = perf_counter()
        self.solve_and_apply_ik()

    def solve_and_apply_ik(self) -> IKResult | None:
        if self.chain is None:
            return None

        target_pos_m, target_rot = self._get_target_pose_si()
        mode = self.cmbIKMode.currentData() or "6D"
        enforce_limits = self.chkEnforceLimits.isChecked()

        result = self.chain.solve_ik(
            target_pos=target_pos_m,
            target_rot=target_rot,
            q_init=self.chain.current_q,
            mode=mode,
            enforce_limits=enforce_limits,
            pos_tol_mm=self.dsbPosTol.value(),
            rot_tol_deg=self.dsbRotTol.value(),
            max_iters=self.spnMaxIters.value(),
            damping=self.dsbDamping.value(),
        )

        self._apply_q_and_sync_ui(result.q, saturated_names=result.saturated_joints)

        if result.success:
            self.lblIKStatus.setStyleSheet(
                "background-color: #d4edda; color: #155724; padding: 6px; font-weight: bold;"
            )
        else:
            self.lblIKStatus.setStyleSheet(
                "background-color: #fff3cd; color: #856404; padding: 6px; font-weight: bold;"
            )
        self.lblIKStatus.setText(result.message)
        return result

    # ------------------------------------------------------------------
    # Step 3 (Tab 2): Waypoint Management, Trajectory Solve, Preview & Export
    # ------------------------------------------------------------------
    def _next_default_waypoint_time(self) -> float:
        if not self._waypoints:
            return 0.0
        return round(float(self._waypoints[-1].time_s) + 1.5, 3)

    def add_waypoint_from_current_pose(self):
        if self.chain is None:
            return
        fk = self.chain.forward_kinematics(self.chain.current_q)
        wp = TrajectoryWaypoint(
            time_s=self._next_default_waypoint_time(),
            pos_m=fk.tcp_pos.copy(),
            rot_mat=fk.tcp_rot.copy(),
            segment_type="MOVEL",
            label=f"Pose_{len(self._waypoints) + 1}",
        )
        self._waypoints.append(wp)
        self._invalidate_solved_trajectory()
        self._rebuild_waypoint_table()
        self.tblWaypoints.selectRow(len(self._waypoints) - 1)
        self._update_3d_preview_actors()
        self._persist_state_to_app()

    def add_waypoint_from_selected_rf(self):
        rf_name = self.cmbWpSourceRF.currentData()
        if not rf_name:
            return
        rf = next((r for r in getattr(self.app, 'rframes', []) if r.name == rf_name), None)
        if rf is None:
            return
        wp = TrajectoryWaypoint(
            time_s=self._next_default_waypoint_time(),
            pos_m=rf.position.copy(),
            rot_mat=rf.transform_matrix.copy(),
            segment_type="MOVEL",
            label=rf.name,
        )
        self._waypoints.append(wp)
        self._invalidate_solved_trajectory()
        self._rebuild_waypoint_table()
        self.tblWaypoints.selectRow(len(self._waypoints) - 1)
        self._update_3d_preview_actors()
        self._persist_state_to_app()

    def jump_robot_to_selected_waypoint(self):
        if self.chain is None or not self._waypoints:
            return
        row = self.tblWaypoints.currentRow()
        if row < 0 or row >= len(self._waypoints):
            row = 0
        self._sync_waypoints_from_table()
        wp = self._waypoints[row]
        res = self.chain.solve_ik(
            target_pos=wp.pos_m,
            target_rot=wp.rot_mat,
            q_init=self.chain.current_q,
            mode=self.cmbIKMode.currentData() or "6D",
            enforce_limits=self.chkEnforceLimits.isChecked(),
            pos_tol_mm=self.dsbPosTol.value(),
            rot_tol_deg=self.dsbRotTol.value(),
            max_iters=self.spnMaxIters.value(),
            damping=self.dsbDamping.value(),
        )
        self._apply_q_and_sync_ui(res.q, saturated_names=res.saturated_joints)
        self.lblTrajStatus.setStyleSheet("background-color: #f8f9fa; color: #111111; padding: 6px; font-weight: bold;")
        self.lblTrajStatus.setText(f"Waypoint #{row + 1}: {res.message}")

    def _move_selected_waypoint(self, delta: int):
        row = self.tblWaypoints.currentRow()
        new_row = row + delta
        if row < 0 or new_row < 0 or new_row >= len(self._waypoints):
            return
        self._sync_waypoints_from_table()
        # Swap poses/segment types while keeping monotonic timestamps in place
        t_a, t_b = self._waypoints[row].time_s, self._waypoints[new_row].time_s
        self._waypoints[row], self._waypoints[new_row] = self._waypoints[new_row], self._waypoints[row]
        self._waypoints[row].time_s = t_a
        self._waypoints[new_row].time_s = t_b
        self._invalidate_solved_trajectory()
        self._rebuild_waypoint_table()
        self.tblWaypoints.selectRow(new_row)
        self._update_3d_preview_actors()
        self._persist_state_to_app()

    def delete_selected_waypoint(self):
        row = self.tblWaypoints.currentRow()
        if row < 0 or row >= len(self._waypoints):
            return
        self._sync_waypoints_from_table()
        self._waypoints.pop(row)
        self._invalidate_solved_trajectory()
        self._rebuild_waypoint_table()
        if self._waypoints:
            self.tblWaypoints.selectRow(min(row, len(self._waypoints) - 1))
        self._update_3d_preview_actors()
        self._persist_state_to_app()

    def clear_all_waypoints(self):
        self.stop_trajectory_preview_playback()
        self._waypoints.clear()
        self._invalidate_solved_trajectory()
        self._rebuild_waypoint_table()
        self.clear_3d_preview_actors(render=True)
        self._persist_state_to_app()
        self.lblTrajStatus.setStyleSheet("background-color: #f8f9fa; color: #111111; padding: 6px; font-weight: bold;")
        self.lblTrajStatus.setText("Cleared all waypoints.")

    def _rebuild_waypoint_table(self):
        self._updating_ui = True
        self._wp_row_widgets = []
        self.tblWaypoints.setRowCount(len(self._waypoints))

        for row, wp in enumerate(self._waypoints):
            pos_mm = wp.pos_m * MMtoM
            ori_zyx = matrix_to_pos_angles_deg(wp.rot_mat)  # [Yaw(Z), Pitch(Y), Roll(X)]

            # Col 0: #
            item_idx = QTableWidgetItem(str(row + 1))
            item_idx.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_idx.setFlags(item_idx.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tblWaypoints.setItem(row, 0, item_idx)

            # Col 1: Time t (s)
            spn_t = QDoubleSpinBox()
            spn_t.setDecimals(3)
            spn_t.setRange(0.0, 10000.0)
            spn_t.setSingleStep(0.5)
            spn_t.setSuffix(" s")
            spn_t.setValue(float(wp.time_s))
            spn_t.setToolTip("Arrival timestamp for this waypoint in seconds (must increase strictly down the table).")
            self.tblWaypoints.setCellWidget(row, 1, spn_t)

            # Col 2: Segment Type
            cmb_seg = QComboBox()
            if row == 0:
                cmb_seg.addItem("Start Pose (t₀)", "START")
                cmb_seg.setEnabled(False)
                cmb_seg.setToolTip("Initial starting waypoint of the trajectory.")
            else:
                cmb_seg.addItem("Linear TCP (MOVEL)", "MOVEL")
                cmb_seg.addItem("Joint-Space (MOVEJ)", "MOVEJ")
                idx_seg = cmb_seg.findData(wp.segment_type.upper())
                cmb_seg.setCurrentIndex(idx_seg if idx_seg >= 0 else 0)
                cmb_seg.setToolTip(
                    "MOVEL moves the TCP in a straight 3D line + SLERP; MOVEJ interpolates smoothly in joint space."
                )
            self.tblWaypoints.setCellWidget(row, 2, cmb_seg)

            # Cols 3..5: X, Y, Z (mm)
            spn_x = self._make_coord_spinbox(-100000.0, 100000.0, 10.0, " mm")
            spn_y = self._make_coord_spinbox(-100000.0, 100000.0, 10.0, " mm")
            spn_z = self._make_coord_spinbox(-100000.0, 100000.0, 10.0, " mm")
            spn_x.setValue(float(pos_mm[0]))
            spn_y.setValue(float(pos_mm[1]))
            spn_z.setValue(float(pos_mm[2]))
            spn_x.setToolTip("Waypoint global X position (mm).")
            spn_y.setToolTip("Waypoint global Y position (mm).")
            spn_z.setToolTip("Waypoint global Z position (mm).")
            self.tblWaypoints.setCellWidget(row, 3, spn_x)
            self.tblWaypoints.setCellWidget(row, 4, spn_y)
            self.tblWaypoints.setCellWidget(row, 5, spn_z)

            # Cols 6..8: Roll, Pitch, Yaw (deg)
            spn_roll = self._make_coord_spinbox(-360.0, 360.0, 5.0, " °")
            spn_pitch = self._make_coord_spinbox(-360.0, 360.0, 5.0, " °")
            spn_yaw = self._make_coord_spinbox(-360.0, 360.0, 5.0, " °")
            spn_roll.setValue(float(ori_zyx[2]))
            spn_pitch.setValue(float(ori_zyx[1]))
            spn_yaw.setValue(float(ori_zyx[0]))
            spn_roll.setToolTip("Waypoint Roll angle around X (deg).")
            spn_pitch.setToolTip("Waypoint Pitch angle around Y (deg).")
            spn_yaw.setToolTip("Waypoint Yaw angle around Z (deg).")
            self.tblWaypoints.setCellWidget(row, 6, spn_roll)
            self.tblWaypoints.setCellWidget(row, 7, spn_pitch)
            self.tblWaypoints.setCellWidget(row, 8, spn_yaw)

            # Col 9: IK Status
            item_stat = QTableWidgetItem("Pending")
            item_stat.setFlags(item_stat.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tblWaypoints.setItem(row, 9, item_stat)

            w_dict = {
                "spn_t": spn_t,
                "cmb_seg": cmb_seg,
                "spn_x": spn_x,
                "spn_y": spn_y,
                "spn_z": spn_z,
                "spn_roll": spn_roll,
                "spn_pitch": spn_pitch,
                "spn_yaw": spn_yaw,
                "item_stat": item_stat,
                "stat_state": "pending",
            }
            self._style_waypoint_status_item(w_dict)
            self._wp_row_widgets.append(w_dict)

            for w_sig in (spn_t, spn_x, spn_y, spn_z, spn_roll, spn_pitch, spn_yaw):
                w_sig.valueChanged.connect(self._on_waypoint_cell_edited)
            cmb_seg.currentIndexChanged.connect(self._on_waypoint_cell_edited)

        self.tblWaypoints.resizeColumnsToContents()
        self._updating_ui = False

    def _sync_waypoints_from_table(self):
        for row, w in enumerate(self._wp_row_widgets):
            if row >= len(self._waypoints):
                break
            wp = self._waypoints[row]
            wp.time_s = float(w["spn_t"].value())
            if row > 0:
                wp.segment_type = str(w["cmb_seg"].currentData() or "MOVEL")
            wp.pos_m = np.array([
                w["spn_x"].value(),
                w["spn_y"].value(),
                w["spn_z"].value(),
            ], dtype=float) / MMtoM
            wp.rot_mat = pos_angles_deg_to_matrix(np.array([
                w["spn_yaw"].value(),
                w["spn_pitch"].value(),
                w["spn_roll"].value(),
            ], dtype=float))

    def _on_waypoint_cell_edited(self, *args):
        if self._updating_ui:
            return
        self._sync_waypoints_from_table()
        self._invalidate_solved_trajectory()
        self._update_3d_preview_actors()
        self._persist_state_to_app()

    def _invalidate_solved_trajectory(self):
        self.stop_trajectory_preview_playback()
        self.last_trajectory = None
        if hasattr(self, 'btnPlayPreview'):
            self.btnPlayPreview.setEnabled(False)
            self.sldPreviewTime.blockSignals(True)
            self.sldPreviewTime.setRange(0, 0)
            self.sldPreviewTime.setValue(0)
            self.sldPreviewTime.blockSignals(False)
            self.sldPreviewTime.setEnabled(False)
            self.lblPreviewTime.setText("t = 0.000 / 0.000 s")
            self.btnExportMotions.setEnabled(False)
        colors = self._theme_colors()
        for w in getattr(self, '_wp_row_widgets', []):
            w["item_stat"].setText("Pending")
            w["stat_state"] = "pending"
            self._style_waypoint_status_item(w, colors)

    def solve_trajectory_from_ui(self) -> TrajectoryResult | None:
        if self.chain is None:
            return None
        self._sync_waypoints_from_table()
        if len(self._waypoints) < 2:
            QMessageBox.information(
                self,
                "Trajectory Planner",
                "Please add at least 2 waypoints before solving a trajectory."
            )
            return None

        try:
            q_zero_seed = self.chain.clamp_q(
                np.zeros(self.chain.num_dof, dtype=float),
                enforce_limits=self.chkEnforceLimits.isChecked(),
            )
            res = self.chain.plan_trajectory(
                waypoints=self._waypoints,
                sample_rate_hz=float(self.spnSampleRateHz.value()),
                timing_mode=self.cmbTimingMode.currentData() or "quintic_stop",
                ik_mode=self.cmbIKMode.currentData() or "6D",
                enforce_limits=self.chkEnforceLimits.isChecked(),
                pos_tol_mm=self.dsbPosTol.value(),
                rot_tol_deg=self.dsbRotTol.value(),
                max_iters=self.spnMaxIters.value(),
                damping=self.dsbDamping.value(),
                q_seed=q_zero_seed,
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Trajectory Timing Error", str(exc))
            return None

        self.last_trajectory = res

        # Update per-waypoint status cells
        colors = self._theme_colors()
        for row, w in enumerate(self._wp_row_widgets):
            if row < len(res.waypoint_converged):
                ok = res.waypoint_converged[row]
                p_err = res.waypoint_errors_mm[row]
                r_err = res.waypoint_rot_errors_deg[row]
                if ok:
                    w["item_stat"].setText(f"OK ({p_err:.2f} mm, {r_err:.2f} deg)")
                    w["stat_state"] = "ok"
                else:
                    w["item_stat"].setText(f"WARN ({p_err:.1f} mm, {r_err:.1f} deg)")
                    w["stat_state"] = "warn"
                self._style_waypoint_status_item(w, colors)

        # Enable preview scrubber & export button
        n_frames = len(res.times)
        self.sldPreviewTime.blockSignals(True)
        self.sldPreviewTime.setRange(0, max(0, n_frames - 1))
        self.sldPreviewTime.setValue(0)
        self.sldPreviewTime.blockSignals(False)
        self.sldPreviewTime.setEnabled(True)
        self.btnPlayPreview.setEnabled(True)
        self.btnExportMotions.setEnabled(True)
        self.lblPreviewTime.setText(f"t = {res.times[0]:.3f} / {res.times[-1]:.3f} s")

        if res.success:
            self.lblTrajStatus.setStyleSheet(
                "background-color: #d4edda; color: #155724; padding: 6px; font-weight: bold;"
            )
        else:
            self.lblTrajStatus.setStyleSheet(
                "background-color: #fff3cd; color: #856404; padding: 6px; font-weight: bold;"
            )
        self.lblTrajStatus.setText(res.message)

        # Snap preview to t=0, draw 3D curve, and plot planned curves
        self._apply_q_and_sync_ui(res.q_traj[0], saturated_names=res.saturated_joints)
        self._update_3d_preview_actors()
        if self.cmbTrajPlotMode.currentData() == "effort":
            self.cmbTrajPlotMode.setCurrentIndex(0)
        else:
            self._refresh_trajectory_plot()
        return res

    # ------------------------------------------------------------------
    # 3D Viewport Path & Waypoint Visualization + Kinematic Playback
    # ------------------------------------------------------------------
    def clear_3d_preview_actors(self, render=False):
        plotter = getattr(self.app, 'plotter', None)
        if plotter is not None:
            for act in self._traj_preview_actors:
                try:
                    plotter.remove_actor(act)
                except Exception:
                    pass
            if render:
                plotter.render()
        self._traj_preview_actors.clear()

    def _on_show_3d_path_toggled(self, checked):
        if checked:
            self._update_3d_preview_actors()
        else:
            self.clear_3d_preview_actors(render=True)

    def _update_3d_preview_actors(self):
        self.clear_3d_preview_actors(render=False)
        if not hasattr(self, 'chkShow3DPath') or not self.chkShow3DPath.isChecked():
            return
        plotter = getattr(self.app, 'plotter', None)
        if plotter is None:
            return

        # 1. Waypoint spheres (scaled proportionally to scene RFrame size)
        base_scale = self.app.rframes[0].base_scale if getattr(self.app, 'rframes', None) else 15.0
        wp_radius_mm = max(float(base_scale) * 0.14, 2.5)
        for idx, wp in enumerate(self._waypoints):
            center_mm = wp.pos_m * MMtoM
            sph = pv.Sphere(radius=wp_radius_mm, center=center_mm, theta_resolution=16, phi_resolution=16)
            color = "#2ea043" if idx == 0 else ("#ff6b6b" if idx == len(self._waypoints) - 1 else "#ffb86c")
            act = plotter.add_mesh(sph, color=color, pickable=False, reset_camera=False, render=False)
            self._traj_preview_actors.append(act)

        # 2. Continuous TCP trajectory polyline (if solved) or dashed straight segments between waypoints
        if self.last_trajectory is not None and len(self.last_trajectory.tcp_pos_traj) >= 2:
            pts_mm = self.last_trajectory.tcp_pos_traj * MMtoM
            poly = pv.lines_from_points(pts_mm)
            act_line = plotter.add_mesh(
                poly, color="#00d2ff", line_width=3.0, pickable=False, reset_camera=False, render=False
            )
            self._traj_preview_actors.append(act_line)
        elif len(self._waypoints) >= 2:
            pts_mm = np.array([wp.pos_m * MMtoM for wp in self._waypoints], dtype=float)
            poly = pv.lines_from_points(pts_mm)
            act_line = plotter.add_mesh(
                poly, color="#ffb86c", line_width=2.0, pickable=False, reset_camera=False, render=False
            )
            self._traj_preview_actors.append(act_line)

        plotter.render()

    def _on_preview_slider_changed(self, sample_idx: int):
        if self._updating_ui or self.chain is None or self.last_trajectory is None:
            return
        n = len(self.last_trajectory.times)
        if sample_idx < 0 or sample_idx >= n:
            return
        t_cur = self.last_trajectory.times[sample_idx]
        t_end = self.last_trajectory.times[-1]
        self.lblPreviewTime.setText(f"t = {t_cur:.3f} / {t_end:.3f} s")
        self.chain.current_q = self.last_trajectory.q_traj[sample_idx].copy()
        self._request_fk_render()

    def toggle_trajectory_preview_playback(self):
        if self._traj_play_timer.isActive():
            self.stop_trajectory_preview_playback()
            return
        if self.last_trajectory is None or len(self.last_trajectory.times) < 2:
            return
        if self.sldPreviewTime.value() >= len(self.last_trajectory.times) - 1:
            self.sldPreviewTime.setValue(0)
        self._traj_play_idx = self.sldPreviewTime.value()
        self._traj_play_wall_start = perf_counter() - float(self.last_trajectory.times[self._traj_play_idx])
        self.btnPlayPreview.setText("⏸ Pause Preview")
        self._traj_play_timer.start(16)  # ~60 FPS real-time preview

    def stop_trajectory_preview_playback(self):
        if hasattr(self, '_traj_play_timer') and self._traj_play_timer.isActive():
            self._traj_play_timer.stop()
        if hasattr(self, 'btnPlayPreview'):
            self.btnPlayPreview.setText("▶ Play Preview")

    def _on_traj_play_tick(self):
        if self.last_trajectory is None or self.chain is None:
            self.stop_trajectory_preview_playback()
            return
        elapsed_t = perf_counter() - self._traj_play_wall_start
        times = self.last_trajectory.times
        if elapsed_t >= times[-1]:
            idx = len(times) - 1
            self.sldPreviewTime.setValue(idx)
            self._apply_q_and_sync_ui(self.last_trajectory.q_traj[idx])
            self.stop_trajectory_preview_playback()
            return
        idx = int(np.searchsorted(times, elapsed_t))
        idx = min(max(idx, 0), len(times) - 1)
        if idx != self.sldPreviewTime.value():
            self.sldPreviewTime.setValue(idx)

    # ------------------------------------------------------------------
    # Export to SimPhant JointMotions & Post-Solve Effort Check / Plotting
    # ------------------------------------------------------------------
    def export_trajectory_motions_from_ui(self):
        if self.chain is None or self.last_trajectory is None:
            return
        self.stop_trajectory_preview_playback()
        try:
            motions = self.chain.export_trajectory_to_motions(
                self.last_trajectory,
                app=self.app,
                sync_sim_time=self.chkSyncSimTime.isChecked(),
            )
        except Exception as exc:
            QMessageBox.critical(self, "Export Motions Error", f"Failed to export JointMotions:\n{exc}")
            return

        self.zero_all_joints()
        self.sldPreviewTime.blockSignals(True)
        self.sldPreviewTime.setValue(0)
        self.sldPreviewTime.blockSignals(False)
        self.lblPreviewTime.setText(
            f"t = {self.last_trajectory.times[0]:.3f} / {self.last_trajectory.times[-1]:.3f} s"
        )
        m_names = ", ".join(m.name for m in motions)
        base_name = self.chain.base_body.name
        base_fixed = self.chain.is_base_fixed_to_ground(getattr(self.app, 'joints_list', None))

        if base_fixed:
            self.lblTrajStatus.setStyleSheet(
                "background-color: #d4edda; color: #155724; padding: 6px; font-weight: bold;"
            )
            self.lblTrajStatus.setText(
                f"[OK] Exported {len(motions)} spline JointMotions ({m_names}) relative to Home (q = 0). "
                f"Click SimPhant's 'Solve' button to run dynamic simulation!"
            )
        else:
            self.lblTrajStatus.setStyleSheet(
                "background-color: #fff3cd; color: #856404; padding: 6px; font-weight: bold;"
            )
            self.lblTrajStatus.setText(
                f"[WARN] Exported {len(motions)} spline JointMotions ({m_names}), "
                f"but Base Body '{base_name}' is NOT fixed to 'Ground'! "
                f"Constrain '{base_name}' to 'Ground' with a Fixed Joint before clicking 'Solve'."
            )
            QMessageBox.warning(
                self,
                "Base Body Not Fixed to Ground",
                f"JointMotion spline drivers ({len(motions)}) were exported, "
                f"but the Base Body '{base_name}' is not constrained to 'Ground' by an enabled Fixed Joint.\n\n"
                f"Before running the dynamic solver ('Solve'), please constrain '{base_name}' to 'Ground' "
                f"using a Fixed Joint — otherwise the robot will fall under gravity during simulation.",
            )

    def _refresh_trajectory_plot(self):
        if not hasattr(self, 'plotTraj'):
            return
        self.plotTraj.clear()
        self.plotTrajLegend = self.plotTraj.addLegend(offset=(8, 8))
        mode = self.cmbTrajPlotMode.currentData()

        palette = [
            "#1f77b4", "#d62728", "#2ca02c", "#ff7f0e",
            "#9467bd", "#8c564b", "#e377c2", "#17becf",
        ]

        if mode == "effort":
            self._plot_last_solve_efforts(palette)
            return

        if self.last_trajectory is None or self.chain is None:
            self.plotTraj.setLabel('left', "Value")
            return

        times = self.last_trajectory.times
        if mode == "pos":
            self.plotTraj.setLabel('left', "Joint Position (deg / mm)")
            for k, joint in enumerate(self.chain.active_joints):
                scale = self._unit_scale(joint)
                pen = pg.mkPen(color=palette[k % len(palette)], width=2)
                self.plotTraj.plot(times, self.last_trajectory.q_traj[:, k] * scale, pen=pen, name=joint.name)
        elif mode == "vel":
            self.plotTraj.setLabel('left', "Joint Velocity (deg/s / mm/s)")
            for k, joint in enumerate(self.chain.active_joints):
                scale = self._unit_scale(joint)
                pen = pg.mkPen(color=palette[k % len(palette)], width=2)
                self.plotTraj.plot(times, self.last_trajectory.qd_traj[:, k] * scale, pen=pen, name=joint.name)
        elif mode == "err":
            self.plotTraj.setLabel('left', "TCP Tracking Error (mm)")
            pen = pg.mkPen(color="#d62728", width=2)
            self.plotTraj.plot(times, self.last_trajectory.pos_err_mm_traj, pen=pen, name="TCP Pos Error (mm)")

    def check_peak_torques_from_last_solve(self):
        solver = getattr(self.app, 'solver', None)
        if solver is None or getattr(solver, 'simulation_history', None) is None:
            QMessageBox.information(
                self,
                "No Dynamic Simulation Results",
                "Please export the trajectory to JointMotions and click SimPhant's 'Solve' button first."
            )
            return

        try:
            solver.ensure_postprocessed(getattr(self.app, 'simulation_dt', None))
        except Exception as exc:
            QMessageBox.warning(self, "Post-Processing Error", f"Could not extract actuator efforts:\n{exc}")
            return

        idx_eff = self.cmbTrajPlotMode.findData("effort")
        if idx_eff >= 0 and self.cmbTrajPlotMode.currentIndex() != idx_eff:
            self.cmbTrajPlotMode.setCurrentIndex(idx_eff)
        else:
            self._refresh_trajectory_plot()

    def _plot_last_solve_efforts(self, palette):
        self.plotTraj.setLabel('left', "Actuator Effort (Nm / N)")
        solver = getattr(self.app, 'solver', None)
        if (
            self.chain is None
            or solver is None
            or getattr(solver, 'simulation_history', None) is None
        ):
            return

        try:
            solver.ensure_postprocessed(getattr(self.app, 'simulation_dt', None))
        except Exception:
            return

        mot_hist = getattr(solver, 'motion_lambda_history', None)
        if mot_hist is None or mot_hist.shape[1] == 0:
            self._effort_summary_state = "warn"
            self._style_effort_summary_label()
            self.lblEffortSummary.setText("No active JointMotions were present in the last MBSolver run.")
            return

        active_motions = [
            m for m in getattr(self.app, 'motions_list', [])
            if getattr(m, 'enabled', True)
            and getattr(m.joint, 'enabled', True)
            and m.joint.body_i.enabled
            and m.joint.body_j.enabled
        ]
        t_arr = (
            solver.time_history
            if getattr(solver, 'time_history', None) is not None
            else np.arange(mot_hist.shape[0], dtype=float) * float(getattr(self.app, 'simulation_dt', 0.01))
        )
        n_rows = min(len(t_arr), mot_hist.shape[0])
        t_arr = t_arr[:n_rows]

        summary_parts = []
        any_overloaded = False

        for k, joint in enumerate(self.chain.active_joints):
            m_idx = next((i for i, m in enumerate(active_motions) if m.joint is joint or m.joint.name == joint.name), None)
            if m_idx is None or m_idx >= mot_hist.shape[1]:
                continue
            effort_curve = mot_hist[:n_rows, m_idx]
            pen = pg.mkPen(color=palette[k % len(palette)], width=2)
            self.plotTraj.plot(t_arr, effort_curve, pen=pen, name=joint.name)

            peak_val = float(np.max(np.abs(effort_curve))) if n_rows > 0 else 0.0
            unit = "Nm" if joint.joint_type == JointType.REVOLUTE else "N"
            rated = float(getattr(joint, 'max_effort', 0.0))
            if rated > 1e-6:
                pct = 100.0 * peak_val / rated
                if peak_val > rated:
                    any_overloaded = True
                    summary_parts.append(f"{joint.name}: {peak_val:.1f}/{rated:.0f}{unit} ({pct:.0f}% OVER!)")
                else:
                    summary_parts.append(f"{joint.name}: {peak_val:.1f} {unit} ({pct:.0f}%)")
            else:
                summary_parts.append(f"{joint.name}: {peak_val:.1f} {unit}")

        if not summary_parts:
            self._effort_summary_state = "warn"
            self.lblEffortSummary.setText("No matching JointMotions found in the last solve for the active chain.")
        elif any_overloaded:
            self._effort_summary_state = "error"
            self.lblEffortSummary.setText("[WARN] Peak Effort Exceeds Rating -- " + " | ".join(summary_parts))
        else:
            self._effort_summary_state = "ok"
            self.lblEffortSummary.setText("[OK] Peak Actuator Efforts -- " + " | ".join(summary_parts))
        self._style_effort_summary_label()

    # ------------------------------------------------------------------
    # Project Save / Load Serialization (Tab 2 Waypoints & Settings)
    # ------------------------------------------------------------------
    def _persist_state_to_app(self):
        if self.app is not None:
            self.app.robotics_project_state = self.export_project_state()

    def export_project_state(self) -> dict:
        """Serializes active chain selection, planner settings, and Tab 2 waypoints for `.mbd` saving."""
        self._sync_waypoints_from_table()
        waypoints_data = []
        for wp in self._waypoints:
            waypoints_data.append({
                "time_s": float(wp.time_s),
                "pos_m": np.asarray(wp.pos_m, dtype=float).tolist(),
                "rot_mat": np.asarray(wp.rot_mat, dtype=float).tolist(),
                "segment_type": str(wp.segment_type),
                "label": str(wp.label),
            })
        return {
            "base_body": self.cmbBaseBody.currentData() or "",
            "ee_body": self.cmbEEBody.currentData() or "",
            "tcp_rf": self.cmbTCPRF.currentData() or "__EE_COG__",
            "ik_mode": self.cmbIKMode.currentData() or "6D",
            "enforce_limits": bool(self.chkEnforceLimits.isChecked()),
            "timing_mode": self.cmbTimingMode.currentData() or "quintic_stop",
            "sample_rate_hz": int(self.spnSampleRateHz.value()),
            "sync_sim_time": bool(self.chkSyncSimTime.isChecked()),
            "show_3d_path": bool(self.chkShow3DPath.isChecked()),
            "waypoints": waypoints_data,
        }

    def import_project_state(self, state: dict | None):
        """Restores saved chain selection, planner settings, and Tab 2 waypoints from an `.mbd` dictionary."""
        if not state or not isinstance(state, dict):
            self.clear_all_waypoints()
            return

        self._updating_ui = True
        try:
            base_name = state.get("base_body")
            ee_name = state.get("ee_body")
            if base_name and self.cmbBaseBody.findData(base_name) >= 0:
                self.cmbBaseBody.setCurrentIndex(self.cmbBaseBody.findData(base_name))
            if ee_name and self.cmbEEBody.findData(ee_name) >= 0:
                self.cmbEEBody.setCurrentIndex(self.cmbEEBody.findData(ee_name))
            self._populate_tcp_rf_combo()
            tcp_rf = state.get("tcp_rf")
            if tcp_rf and self.cmbTCPRF.findData(tcp_rf) >= 0:
                self.cmbTCPRF.setCurrentIndex(self.cmbTCPRF.findData(tcp_rf))

            ik_mode = state.get("ik_mode")
            if ik_mode and self.cmbIKMode.findData(ik_mode) >= 0:
                self.cmbIKMode.setCurrentIndex(self.cmbIKMode.findData(ik_mode))
            if "enforce_limits" in state:
                self.chkEnforceLimits.setChecked(bool(state["enforce_limits"]))
            timing_mode = state.get("timing_mode")
            if timing_mode and self.cmbTimingMode.findData(timing_mode) >= 0:
                self.cmbTimingMode.setCurrentIndex(self.cmbTimingMode.findData(timing_mode))
            if "sample_rate_hz" in state:
                self.spnSampleRateHz.setValue(int(state["sample_rate_hz"]))
            if "sync_sim_time" in state:
                self.chkSyncSimTime.setChecked(bool(state["sync_sim_time"]))
            if "show_3d_path" in state:
                self.chkShow3DPath.setChecked(bool(state["show_3d_path"]))
        finally:
            self._updating_ui = False

        self.rebuild_chain(auto_quiet=True)

        restored_wps = []
        for wp_d in state.get("waypoints", []):
            try:
                restored_wps.append(
                    TrajectoryWaypoint(
                        time_s=float(wp_d.get("time_s", 0.0)),
                        pos_m=np.array(wp_d["pos_m"], dtype=float),
                        rot_mat=np.array(wp_d["rot_mat"], dtype=float),
                        segment_type=str(wp_d.get("segment_type", "MOVEL")),
                        label=str(wp_d.get("label", "")),
                    )
                )
            except Exception:
                continue

        self._waypoints = restored_wps
        self._invalidate_solved_trajectory()
        self._rebuild_waypoint_table()
        if self.is_workbench_open():
            self._update_3d_preview_actors()
        self._persist_state_to_app()

    # ------------------------------------------------------------------
    # Dock / Float Mode
    # ------------------------------------------------------------------
    def is_workbench_open(self) -> bool:
        if self._is_docked and self._dock_widget is not None:
            return self._dock_widget.isVisible()
        return self.isVisible()

    def present_workbench(self):
        install_win_uia_shield()
        self._pause_plotter_background_timer()
        self.apply_theme_colors()
        if self._is_docked and self._dock_widget is not None:
            self._dock_widget.show()
            self._dock_widget.raise_()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
        if self._waypoints:
            self._update_3d_preview_actors()

    def toggle_dock_mode(self):
        """Switches the Robotics Workbench between a floating window and a left-side docked panel in MainWindow."""
        if not self._is_docked:
            if self._dock_widget is None:
                self._dock_widget = QDockWidget("Robotics && Inverse Kinematics Workbench", self.app)
                self._dock_widget.setAllowedAreas(
                    Qt.DockWidgetArea.LeftDockWidgetArea
                    | Qt.DockWidgetArea.RightDockWidgetArea
                    | Qt.DockWidgetArea.BottomDockWidgetArea
                    | Qt.DockWidgetArea.TopDockWidgetArea
                )
                self._dock_widget.visibilityChanged.connect(self._on_dock_visibility_changed)
            self._dialog_root_layout.removeWidget(self._content_widget)
            self._dock_widget.setWidget(self._content_widget)
            self.app.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._dock_widget)
            self._dock_widget.show()
            self.app.resizeDocks([self._dock_widget], [520], Qt.Orientation.Horizontal)
            self.hide()
            self._is_docked = True
            self.btnToggleDock.setText("Float Window")
            self.apply_theme_colors()
        else:
            if self._dock_widget is not None:
                self._dock_widget.setWidget(None)
                self.app.removeDockWidget(self._dock_widget)
                self._dock_widget.hide()
            self._dialog_root_layout.addWidget(self._content_widget)
            self._content_widget.show()
            self._is_docked = False
            self.btnToggleDock.setText("Dock Left")
            self.apply_theme_colors()
            self.show()
            self.raise_()
            self.activateWindow()

    def _on_dock_visibility_changed(self, visible: bool):
        if self._is_docked and not visible:
            self._persist_state_to_app()
            self._fk_coalesce_timer.stop()
            self._ik_coalesce_timer.stop()
            self.stop_trajectory_preview_playback()
            self.clear_3d_preview_actors(render=True)
            self._resume_gc_if_paused()
            self._restore_plotter_background_timer()

    def closeEvent(self, event):
        self._persist_state_to_app()
        self._fk_coalesce_timer.stop()
        self._ik_coalesce_timer.stop()
        self.stop_trajectory_preview_playback()
        self.clear_3d_preview_actors(render=True)
        self._resume_gc_if_paused()
        self._restore_plotter_background_timer()
        super().closeEvent(event)
