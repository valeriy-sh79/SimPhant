# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant® — Multibody Dynamics Simulation Software
#  Version: 2026.11.1
#  Module: unit_project.py
#  Description:
#      Handles saving and loading the complete MBD simulation state, including exporting meshes and project data.
#
#  Copyright (C) 2026  Valeriy Shapovalov
#  GitHub: https://github.com/valeriy-sh79
#   
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

import os
import json
import zipfile
import tempfile
import shutil
import numpy as np
import pyvista as pv

from unit_spline import (
    SplineDataError,
    format_spline_expression,
    parse_spline_expression,
    resolve_spline_path,
)

# This module acts as a translator. It converts the Python objects into JSON dictionaries, 
# exports the PyVista meshes to .stl files, and zips them into a single file.

class ProjectManager:
    """ Handles saving and loading the complete MBD simulation state. """

    @staticmethod
    def _bundle_spline_for_save(expr_str, cached_spline_path, splines_dir, bundled_map, used_arc_names, base_dir=None):
        """
        If `expr_str` is a `spline(...)` expression whose file exists on disk, copies that file
        into `splines_dir` (deduplicated by source path) and returns its ZIP-relative path
        (e.g. `'splines/my_curve.csv'`). Returns `None` for non-spline expressions or missing files.
        """
        raw_path = parse_spline_expression(expr_str)
        if raw_path is None:
            return None

        source_path = None
        try:
            source_path = resolve_spline_path(raw_path, base_dir=base_dir)
        except SplineDataError:
            if cached_spline_path and os.path.isfile(cached_spline_path):
                source_path = os.path.normpath(cached_spline_path)

        if not source_path or not os.path.isfile(source_path):
            print(f"Warning: Could not find spline file '{raw_path}' to embed into .mbd archive.")
            return None

        norm_src = os.path.normcase(os.path.abspath(source_path))
        if norm_src in bundled_map:
            return bundled_map[norm_src]

        os.makedirs(splines_dir, exist_ok=True)
        orig_name = os.path.basename(source_path) or "spline_data.csv"
        stem, ext = os.path.splitext(orig_name)
        if not ext:
            ext = ".csv"

        candidate = f"{stem}{ext}"
        counter = 2
        while candidate.lower() in used_arc_names:
            candidate = f"{stem}_{counter}{ext}"
            counter += 1

        used_arc_names.add(candidate.lower())
        shutil.copy2(source_path, os.path.join(splines_dir, candidate))

        arc_rel_path = f"splines/{candidate}"
        bundled_map[norm_src] = arc_rel_path
        return arc_rel_path

    @staticmethod
    def _resolve_or_extract_spline_expr(expr_str, embedded_rel_path, temp_dir, mbd_filepath, base_dir, extracted_map):
        """
        Resolves a `spline(...)` expression when loading an `.mbd` archive:
          1) If the CSV/DAT file exists at its saved location, loads directly from that location
             and ignores any embedded copy inside the `.mbd`.
          2) If the file or directory does NOT exist at the saved location, extracts the embedded
             spline file from the `.mbd` into `<mbd_dir>/splines/<mbd_stem>/` (with safe fallbacks)
             and returns `spline(<extracted_path>)`.
          3) For legacy `.mbd` files without embedded splines, returns `expr_str` unchanged so
             existing warning/fallback behavior is preserved without failing project load.
        """
        raw_path = parse_spline_expression(expr_str)
        if raw_path is None:
            return expr_str

        # 1. Prefer the saved file location if it exists on disk
        mbd_dir = os.path.dirname(os.path.abspath(mbd_filepath)) if mbd_filepath else None
        for candidate_base in (base_dir, mbd_dir):
            try:
                existing_path = resolve_spline_path(raw_path, base_dir=candidate_base)
                if os.path.isfile(existing_path):
                    return format_spline_expression(existing_path)
            except SplineDataError:
                pass

        # 2. Saved path does not exist -> locate embedded spline inside extracted temp_dir
        embedded_src = None
        if embedded_rel_path:
            rel_parts = [p for p in str(embedded_rel_path).replace("\\", "/").split("/") if p and p not in (".", "..")]
            if rel_parts:
                cand = os.path.join(temp_dir, *rel_parts)
                if os.path.isfile(cand):
                    embedded_src = cand

        if embedded_src is None:
            # Legacy .mbd without embedded spline file: do not fail here; let compile_expression warn cleanly
            return expr_str

        cache_key = os.path.normcase(os.path.abspath(embedded_src))
        if cache_key in extracted_map and os.path.isfile(extracted_map[cache_key]):
            return format_spline_expression(extracted_map[cache_key])

        mbd_stem = os.path.splitext(os.path.basename(mbd_filepath))[0] if mbd_filepath else "project"
        filename = os.path.basename(embedded_src)

        candidate_dirs = []
        if mbd_dir:
            candidate_dirs.append(os.path.join(mbd_dir, "splines", mbd_stem))
        if base_dir:
            candidate_dirs.append(os.path.join(base_dir, "splines", mbd_stem))
        candidate_dirs.append(os.path.join(tempfile.gettempdir(), "SimPhant_splines", mbd_stem))

        dest_path = None
        for target_dir in candidate_dirs:
            try:
                os.makedirs(target_dir, exist_ok=True)
                target_file = os.path.join(target_dir, filename)
                shutil.copy2(embedded_src, target_file)
                dest_path = os.path.normpath(target_file)
                break
            except OSError:
                continue

        if dest_path is None:
            return expr_str

        extracted_map[cache_key] = dest_path
        print(f"[Project Load] Spline not found at '{raw_path}'; extracted embedded spline to '{dest_path}'.")
        return format_spline_expression(dest_path)

    @staticmethod
    def save_project(app, filepath):
        """ Exports the scene to a zipped .mbd file. """
        temp_dir = tempfile.mkdtemp()
        meshes_dir = os.path.join(temp_dir, "meshes")
        splines_dir = os.path.join(temp_dir, "splines")
        os.makedirs(meshes_dir)
        bundled_splines = {}
        used_spline_arc_names = set()
        base_dir = getattr(app, 'working_dir', None)
        
        data = {
            "version": "1.0",
            "gravity": [float(app.ui.Edit_GravityX.text().replace(',', '.')),
                        float(app.ui.Edit_GravityY.text().replace(',', '.')),
                        float(app.ui.Edit_GravityZ.text().replace(',', '.'))],
            "bodies": [],
            "rframes": [],  
            "forces": [],
            "joints": [],
            "springs": [],
            "bushings": [],
            "contacts": [],
            "gears": [], 
            "motions": [],
            "solver_settings": {}
        }
        
        # 1. Save Bodies and export their 3D Meshes
        for name, body in app.physics_bodies.items():
            if body.is_ground: continue
            
            # Save the PyVista mesh to the temporary folder
            mesh_filename = f"{name}.stl"
            mesh_path = os.path.join(meshes_dir, mesh_filename)
            body.mesh.save(mesh_path)
            
            data["bodies"].append({
                "name": body.name,
                "density": body.density,
                # Saved so reopening the project does not need a mesh volume integral (absent in older files).
                "volume": body.volume,
                # --- Save the exact mathematical mass and inertia! ---
                "mass": body.mass,
                "principal_inertia": body.principal_inertia.tolist(),
                "inertia_tensor": body.inertia_tensor.tolist(),
                # --------------------------------------------------------------
                "cog": body.cog.tolist(),
                "principal_axes": body.principal_axes.tolist(),
                "pos_angles": body.pos_angles.tolist(),
                "initial_velocity": getattr(body, 'initial_velocity', np.zeros(3)).tolist(),
                "initial_angular_velocity": getattr(body, 'initial_angular_velocity', np.zeros(3)).tolist(),
                "enabled": body.enabled,
                "visible": body.visible,
                "base_color": body.base_color,
                "mesh_file": f"meshes/{mesh_filename}"
            })
            
        # 2. Save Custom Reference Frames (Skip CoGs and Global)
        for rf in app.rframes:
            if rf.is_cog or rf.name == "Global_RF": continue
            data["rframes"].append({
                "name": rf.name,
                "position": rf.position.tolist(),
                "orientation": rf.orientation.tolist(),
                "transform_matrix": rf.transform_matrix.tolist(),
                "parent_body": rf.parent_body.name if rf.parent_body else "Ground"
            })
            
        # --- 3. Save Forces & Actuators ---
        for force in app.forces_list:
            force_expr = getattr(force, 'magnitude_expr', str(force.magnitude))
            is_grav = getattr(force, 'is_gravity', False)
            force_entry = {
                "name": force.name,
                "force_type": force.force_type.value,
                "parent_body": force.parent_body.name,
                "fixed_in": force.fixed_in.value,
                "local_position": force.local_position.tolist(),
                "base_vector": force.base_vector.tolist(),
                "enabled": force.enabled,
                "visible": force.visible,
                "direction": force.direction,
                "magnitude": force_expr,
                "speed_max": force.speed_max,
                "allow_braking": getattr(force, 'allow_braking', True),
                "source_rf_name": getattr(force, 'source_rf_name', ""),
                "is_gravity": is_grav
            }
            if not is_grav:
                spline_arc = ProjectManager._bundle_spline_for_save(
                    force_expr,
                    getattr(force, 'spline_file_path', None),
                    splines_dir,
                    bundled_splines,
                    used_spline_arc_names,
                    base_dir=base_dir,
                )
                if spline_arc is not None:
                    force_entry["spline_file"] = spline_arc
            data["forces"].append(force_entry)

        # --- 4. Save Joints ---
        for joint in app.joints_list:
            data["joints"].append({
                "name": joint.name,
                "joint_type": joint.joint_type.value,
                "body_i": joint.body_i.name,
                "body_j": joint.body_j.name,
                "enabled": joint.enabled,
                "local_pos_i": joint.local_pos_i.tolist(),
                "local_pos_j": joint.local_pos_j.tolist(),
                "local_axis_i": joint.local_axis_i.tolist(),
                "local_axis_j": joint.local_axis_j.tolist(),
                # --- THE FIX: Save Body I's perpendicular constraint axes! ---
                "local_a_i": getattr(joint, 'local_a_i', [1,0,0]).tolist(),
                "local_b_i": getattr(joint, 'local_b_i', [0,1,0]).tolist(),
                # -------------------------------------------------------------
                "local_a_j": getattr(joint, 'local_a_j', [1,0,0]).tolist(),
                "local_b_j": getattr(joint, 'local_b_j', [0,1,0]).tolist(),
                "source_anchor_name": getattr(joint, 'source_anchor_name', ""),
                "source_target_name": getattr(joint, 'source_target_name', ""),
                "limits_enabled": bool(getattr(joint, 'limits_enabled', False)),
                "limit_min": float(getattr(joint, 'limit_min', -np.pi)),
                "limit_max": float(getattr(joint, 'limit_max', np.pi)),
                "max_effort": float(getattr(joint, 'max_effort', 0.0)),
                "max_velocity": float(getattr(joint, 'max_velocity', 0.0))
            })

        # --- 5. Save Springs ---
        for spring in getattr(app, 'springs_list', []):
            s_data = {
                "name": spring.name,
                "type": "compression" if hasattr(spring, 'initial_length') else "torsion",
                "body_i": spring.body_i.name,
                "body_j": spring.body_j.name,
                "rf_i_name": spring.rf_i_name,
                "rf_j_name": spring.rf_j_name,
                "stiffness": spring.stiffness,
                "damping": spring.damping,
                "preload": spring.preload,
                "enabled": spring.enabled,
                # --- THE FIX: Save the exact internal mathematical vectors! ---
                "local_pos_i": spring.local_pos_i.tolist(),
                "local_pos_j": spring.local_pos_j.tolist(),
                "local_axis_i": spring.local_axis_i.tolist(),
                "local_ref_i": spring.local_ref_i.tolist(),
                "local_ref_j": spring.local_ref_j.tolist()
            }
            if s_data["type"] == "torsion":
                s_data["axis_choice"] = getattr(spring, 'axis_choice', 'Z')
            s_data["is_nonlinear"] = getattr(spring, 'is_nonlinear', False)
            s_data["nonlinear_expr"] = getattr(spring, 'nonlinear_expr', '0')
            data["springs"].append(s_data)

        # --- 6. Save Bushings ---
        for bushing in getattr(app, 'bushings_list', []):
            data["bushings"].append({
                "name": bushing.name,
                "body_i": bushing.body_i.name,
                "body_j": bushing.body_j.name,
                "rf_i_name": bushing.rf_i_name,
                "rf_j_name": bushing.rf_j_name,
                "k_trans": bushing.k_trans.tolist(),
                "c_trans": bushing.c_trans.tolist(),
                "p_trans": bushing.p_trans.tolist(),
                "k_rot": bushing.k_rot.tolist(),
                "c_rot": bushing.c_rot.tolist(),
                "p_rot": bushing.p_rot.tolist(),
                "enabled": bushing.enabled,
                # --- THE FIX: Save the exact internal mathematical vectors! ---
                "local_pos_i": bushing.local_pos_i.tolist(),
                "local_pos_j": bushing.local_pos_j.tolist(),
                "local_axis_i": bushing.local_axis_i.tolist(),
                "local_rot_i": bushing.local_rot_i.tolist(),
                "local_rot_j": bushing.local_rot_j.tolist()
            })

        # --- 7. Save Contacts ---
        for cp in getattr(app, 'contact_pairs', []):
            data["contacts"].append({
                "name": cp.name,
                "body_i": cp.body_i.name,
                "body_j": cp.body_j.name,
                "stiffness": cp.stiffness,
                "exponent": cp.exponent,
                "damping": cp.damping,
                "friction_enabled": cp.friction_enabled,
                "mu": cp.mu,
                "slip_tolerance": cp.slip_tolerance,
                "mesh_mode": getattr(cp, 'mesh_mode', 0), # <--- THE NEW VARIABLE
                "symmetric_contact_search": getattr(cp, 'symmetric_contact_search', True),
                "contact_candidate_reduction_enabled": getattr(cp, 'contact_candidate_reduction_enabled', True),
                "d_max_m": getattr(cp, 'd_max_m', 0.0001),
                "enabled": cp.enabled
            })

        # --- 8. Save Gears ---
        for gear in getattr(app, 'gear_pairs_list', []):
            data["gears"].append({
                "name": gear.name,
                "enabled": gear.enabled,
                "joint_1": gear.joint_1.name,
                "joint_2": gear.joint_2.name,
                "carrier": gear.carrier.name,
                "gear_type": gear.gear_type.value,
                "module": gear.module_n,
                "z1": gear.z1,
                "z2": gear.z2,
                "alpha_deg": np.degrees(gear.alpha),
                "beta_deg": np.degrees(gear.beta),
                "gamma_deg": np.degrees(gear.gamma)
            })
        
        # --- 8.5 Save Kinematic Motions ---
        for motion in getattr(app, 'motions_list', []):
            motion_entry = {
                "name": motion.name,
                "joint": motion.joint.name,
                "trans_rot": motion.trans_rot.value,
                "motion_type": motion.motion_type.value,
                "expression_str": motion.expression_str,
                "enabled": motion.enabled
            }
            spline_arc = ProjectManager._bundle_spline_for_save(
                motion.expression_str,
                getattr(motion, 'spline_file_path', None),
                splines_dir,
                bundled_splines,
                used_spline_arc_names,
                base_dir=base_dir,
            )
            if spline_arc is not None:
                motion_entry["spline_file"] = spline_arc
            data["motions"].append(motion_entry)
        
        # --- 9. Save Solver Settings & Robotics Trajectory Waypoints ---
        if getattr(app, 'robotics_window', None) is not None:
            app.robotics_project_state = app.robotics_window.export_project_state()
        if getattr(app, 'robotics_project_state', None):
            data["robotics"] = app.robotics_project_state

        data["solver_settings"] = {
            "t_end": app.ui.Edit_SimulationTime.text(),
            "steps_per_sec": app.ui.Edit_StepsPerSec.text(),
            "baumgarte": app.ui.Edit_Alpha_Beta.text(),
            "compliance_idx": app.ui.cmbSolverCompliance.currentIndex(),
            "method_idx": app.ui.cmbSolverMethod.currentIndex(),
            "rtol_idx": app.ui.cmbRtol.currentIndex() if hasattr(app.ui, 'cmbRtol') else 1,
            "atol_idx": app.ui.cmbAtol.currentIndex() if hasattr(app.ui, 'cmbAtol') else 2,
            "max_step_idx": app.ui.cmbMaxStep.currentIndex() if hasattr(app.ui, 'cmbMaxStep') else 0
        }
        
        # --- 10. Write JSON, Compress Results, and ZIP it! ---
        json_path = os.path.join(temp_dir, "model.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        # THE UPGRADE: Check if simulation results exist, and binary compress them!
        results_path = None
        if hasattr(app, 'solver') and app.solver is not None:
            if getattr(app.solver, 'simulation_history', None) is not None:
                results_path = os.path.join(temp_dir, "results.npz")
                diagnostics_ready = bool(getattr(app.solver, 'diagnostics_ready', False))
                time_history = getattr(app.solver, 'time_history', None)
                if time_history is None:
                    time_history = np.arange(len(app.solver.simulation_history), dtype=float) * app.simulation_dt

                lambda_history = app.solver.lambda_history if diagnostics_ready and getattr(app.solver, 'lambda_history', None) is not None else np.zeros((0, getattr(app.solver, 'num_equations', 0)))
                gear_lambda_history = getattr(app.solver, 'gear_lambda_history', None) if diagnostics_ready and getattr(app.solver, 'gear_lambda_history', None) is not None else np.zeros((0, getattr(app.solver, 'num_gear_eq', 0)))
                contact_history = getattr(app.solver, 'contact_history', None) if diagnostics_ready and getattr(app.solver, 'contact_history', None) is not None else np.zeros((0, len(getattr(app, 'contact_pairs', [])), 4))
                motion_lambda_history = getattr(app.solver, 'motion_lambda_history', None) if diagnostics_ready and getattr(app.solver, 'motion_lambda_history', None) is not None else np.zeros((0, getattr(app.solver, 'num_motion_eq', 0)))

                np.savez_compressed(
                    results_path,
                    simulation_history=app.solver.simulation_history,
                    time_history=time_history,
                    diagnostics_ready=np.array([1 if diagnostics_ready else 0], dtype=np.int8),
                    lambda_history=lambda_history,
                    contact_history=contact_history,
                    
                    # --- Embed the gear forces into the save file! ---
                    gear_lambda_history=gear_lambda_history,
                    
                    # --- Embed the Motion actuator forces into the save file! ---
                    motion_lambda_history=motion_lambda_history,
                    
                    dt=np.array([app.simulation_dt])
                )
            
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(json_path, arcname="model.json")
            
            # Embed the binary results into the ZIP if they exist!
            if results_path and os.path.exists(results_path):
                zipf.write(results_path, arcname="results.npz")
                
            for root, _, files in os.walk(meshes_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arc_name = os.path.join("meshes", file)
                    zipf.write(full_path, arcname=arc_name)

            if os.path.isdir(splines_dir):
                for root, _, files in os.walk(splines_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arc_name = f"splines/{file}"
                        zipf.write(full_path, arcname=arc_name)
                    
        shutil.rmtree(temp_dir) # Clean up temp files
        print(f"Project saved successfully to {filepath}")

    @staticmethod
    def load_project(app, filepath):
        """ Restores the scene from a zipped .mbd file. """
        temp_dir = tempfile.mkdtemp()
        extracted_splines = {}
        base_dir = getattr(app, 'working_dir', None)
        
        with zipfile.ZipFile(filepath, 'r') as zipf:
            zipf.extractall(temp_dir)
            
        json_path = os.path.join(temp_dir, "model.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 1. Restore Gravity
        app.ui.Edit_GravityX.setText(str(data["gravity"][0]))
        app.ui.Edit_GravityY.setText(str(data["gravity"][1]))
        app.ui.Edit_GravityZ.setText(str(data["gravity"][2]))

        # --- Instantly sync the engine memory to bypass Force normalization! ---
        app.global_gravity = np.array([data["gravity"][0], data["gravity"][1], data["gravity"][2]])
        
        # 2. Restore Bodies
        from PySide6.QtWidgets import QTreeWidgetItem
        from unit_rigidbody import RigidBody
        from unit_kinematics import RFrame
        from unit_forces import Force, ForceType, ForceFrame
        from unit_joints import Joint, JointType
        from unit_springs import CompressionSpring, TorsionSpring, Bushing
        from unit_collision import ContactPair
        
        import trimesh # <--- Ensure this is imported!
        
        for b_data in data["bodies"]:
            mesh_path = os.path.join(temp_dir, b_data["mesh_file"])
            loaded_mesh = pv.read(mesh_path)
            
            # --- THE FIX: Weld STL vertices and compute crisp CAD lighting normals! ---
            # This is to avoid extra shadows around all edges
            loaded_mesh = loaded_mesh.clean().compute_normals(split_vertices=True, feature_angle=60)
            # --------------------------------------------------------------------------
            
            # --- Reconstruct the Trimesh geometry for mass calculations! ---
            verts = loaded_mesh.points
            try:
                # PyVista faces are usually padded with the vertex count [3, v1, v2, v3]
                faces = loaded_mesh.faces.reshape((-1, 4))[:, 1:4]
            except ValueError:
                faces = loaded_mesh.faces.reshape((-1, 3))
                
            restored_trimesh = trimesh.Trimesh(vertices=verts, faces=faces)
            # ------------------------------------------------------------------------
            
            app.body_counter += 1
            actor = app.plotter.add_mesh(loaded_mesh, color=b_data["base_color"], smooth_shading=True)
            tree_item = QTreeWidgetItem(app.node_bodies, [b_data["name"]])
            
            # Every mass property is restored from the file, so the mesh integral is skipped.
            # Files saved before "volume" existed derive it as V = m / density (exact for a
            # homogeneous body). Only files lacking the mass data itself (or with a non-positive
            # density) fall back to the original behavior: the constructor recomputes from the mesh.
            mass_keys = ("mass", "inertia_tensor", "principal_inertia", "cog", "principal_axes")
            has_saved_mass_props = all(k in b_data for k in mass_keys) and b_data.get("density", 0.0) > 1e-12

            # --- THE FIX: Pass restored_trimesh instead of None! ---
            new_body = RigidBody(b_data["name"], restored_trimesh, loaded_mesh, actor, tree_item,
                                 skip_mass_calculation=has_saved_mass_props)
            
            new_body.density = b_data["density"]
            if has_saved_mass_props:
                new_body.volume = float(b_data["volume"]) if "volume" in b_data else float(b_data["mass"]) / new_body.density
            new_body.cog = np.array(b_data["cog"])
            new_body.principal_axes = np.array(b_data["principal_axes"])
            new_body.pos_angles = np.array(b_data["pos_angles"])
            # --- NEW: Load Initial Velocities (With [0,0,0] fallback for old projects!) ---
            new_body.initial_velocity = np.array(b_data.get("initial_velocity", [0.0, 0.0, 0.0]))
            new_body.initial_angular_velocity = np.array(b_data.get("initial_angular_velocity", [0.0, 0.0, 0.0]))
            
            # Instantly apply them to the dynamic state
            new_body.reset_velocities()
            new_body.enabled = b_data["enabled"]
            new_body.visible = b_data["visible"]
            new_body.base_color = b_data["base_color"]
            
            # Load exact mass properties directly!
            new_body.mass = b_data.get("mass", 1.0)
            new_body.principal_inertia = np.array(b_data.get("principal_inertia", [1,1,1]))
            new_body.inertia_tensor = np.array(b_data.get("inertia_tensor", np.eye(3).tolist()))
            
            # Restore UI check properties
            new_body.I_check = new_body.principal_axes @ np.diag(new_body.principal_inertia) @ new_body.principal_axes.T
            new_body.math_error = np.max(np.abs(new_body.inertia_tensor - new_body.I_check))
            
            new_body.update_graphics_matrix(new_body.cog, new_body.principal_axes)
            # --- THE FIX: Regenerate the Local Bounding Box for Collision Detection! ---
            new_body.generate_local_aabb()
            # ---------------------------------------------------------------------------
            app.physics_bodies[new_body.name] = new_body
            
            # Recreate CoG RF
            rf_name = f"RF_CoG_{new_body.name}"
            cog_rf = RFrame(name=rf_name, position=new_body.cog, orientation=new_body.pos_angles,
                            transform_matrix=new_body.principal_axes, plotter=app.plotter,
                            parent_body=new_body, is_cog=True)
            app.rframes.append(cog_rf)
            QTreeWidgetItem(app.node_rframes, [rf_name])
 
        """
        # --- THE FIX: Recalculate Base Size for Joints & Forces! (NO USAGE) ---
        from unit_rigidbody import MMtoM
        max_dist = 30.0 
        for body in app.physics_bodies.values():
            if body.is_ground: continue
            dist = np.linalg.norm(body.cog) * MMtoM
            if dist > max_dist: max_dist = dist
        app.joint_base_size = max(max_dist * 0.15, 0.05) """
        
        # 3. Restore Custom RFrames
        for rf_data in data["rframes"]:
            parent = app.physics_bodies.get(rf_data["parent_body"])
            new_rf = RFrame(
                name=rf_data["name"], position=np.array(rf_data["position"]),
                orientation=np.array(rf_data["orientation"]),
                transform_matrix=np.array(rf_data["transform_matrix"]),
                plotter=app.plotter, parent_body=parent, is_cog=False
            )
            app.rframes.append(new_rf)
            QTreeWidgetItem(app.node_rframes, [new_rf.name])
        
        # --- 4. Restore Forces ---
        for f_data in data.get("forces", []):
            try:
                parent = app.physics_bodies.get(f_data.get("parent_body"))
                # --- THE Purge ghost gravity forces from corrupted save files! ---
                is_grav = f_data.get("is_gravity", False)
                if is_grav and parent:
                    # If the parent body already received a gravity force, destroy this duplicate!
                    if any(f.parent_body == parent and getattr(f, 'is_gravity', False) for f in app.forces_list):
                        print(f"Cleaned up duplicate ghost gravity force for body '{parent.name}'.")
                        continue
                # ----------------------------------------------------------------------
                new_f = Force(
                    name=f_data.get("name", "Force"), force_type=ForceType(f_data.get("force_type", 0)),
                    parent_body=parent, fixed_in=ForceFrame(f_data.get("fixed_in", 0)),
                    position=np.array(f_data.get("local_position", [0,0,0])), 
                    vector=np.array(f_data.get("base_vector", [0,0,0])), plotter=app.plotter
                )
                new_f.direction = f_data.get("direction", 'Z')
                new_f.speed_max = f_data.get("speed_max", 0.0)
                new_f.allow_braking = f_data.get("allow_braking", True)
                new_f.source_rf_name = f_data.get("source_rf_name", "")
                new_f.enabled = f_data.get("enabled", True)
                new_f.visible = f_data.get("visible", True)
                
                new_f.is_gravity = f_data.get("is_gravity", False)
                if new_f.is_gravity:
                    new_f.base_color = "limegreen"
                    for act in new_f.actors: act.prop.color = "limegreen"
                    
                    # --- THE FIX 1: Override the crushed vector with the true gravity vector! ---
                    new_f.base_vector = app.global_gravity.copy()
                    
                    # --- THE FIX 2: Override the 0.0 string to guarantee the arrow is visible! ---
                    g_mag = np.linalg.norm(app.global_gravity)
                    new_f.compile_expression(str(g_mag) if g_mag > 1e-6 else "0.0")
                        
                    # Sync the UI Checkboxes
                    if hasattr(app.ui, 'chkVisibleGravity'):
                        new_f.visible = app.ui.chkVisibleGravity.isChecked()
                        
                    app.ui.chkEnabledGravity.blockSignals(True)
                    app.ui.chkEnabledGravity.setChecked(new_f.enabled)
                    app.ui.chkEnabledGravity.blockSignals(False)
                else:
                    # For standard forces, safely load the expression (fallback to "magnitude" for very old saves)
                    expr_str = f_data.get("expression_str", str(f_data.get("magnitude", "0.0")))
                    resolved_expr = ProjectManager._resolve_or_extract_spline_expr(
                        expr_str,
                        f_data.get("spline_file"),
                        temp_dir=temp_dir,
                        mbd_filepath=filepath,
                        base_dir=base_dir,
                        extracted_map=extracted_splines,
                    )
                    new_f.compile_expression(resolved_expr, base_dir=base_dir)
                    new_f.visible = f_data.get("visible", True)
                    # --- Only add Custom Forces to the Tree! ---
                    QTreeWidgetItem(app.node_forces, [new_f.name])
                    
                app.forces_list.append(new_f)
            except Exception as e:
                print(f"Warning: Failed to load a force. Skipping. Error: {e}")

        # --- 5. Restore Joints ---
        for j_data in data.get("joints", []):
            b_i = app.physics_bodies.get(j_data["body_i"])
            b_j = app.physics_bodies.get(j_data["body_j"])
            new_j = Joint(name=j_data["name"], joint_type=JointType(j_data["joint_type"]), 
                          body_i=b_i, body_j=b_j, plotter=app.plotter)  
                              
            # Restore Exact Math Vectors directly!
            new_j.local_pos_i = np.array(j_data["local_pos_i"])
            new_j.local_pos_j = np.array(j_data["local_pos_j"])
            new_j.local_axis_i = np.array(j_data["local_axis_i"])
            new_j.local_axis_j = np.array(j_data["local_axis_j"])
            
            # --- Restore Body I's perpendicular constraint axes! ---
            new_j.local_a_i = np.array(j_data.get("local_a_i", [1,0,0]))
            new_j.local_b_i = np.array(j_data.get("local_b_i", [0,1,0]))
            # ----------------------------------------------------------------
    
            new_j.local_a_j = np.array(j_data.get("local_a_j", [1,0,0]))
            new_j.local_b_j = np.array(j_data.get("local_b_j", [0,1,0]))
            
            new_j.source_anchor_name = j_data.get("source_anchor_name", "")
            new_j.source_target_name = j_data.get("source_target_name", "")
            new_j.enabled = j_data.get("enabled", True)
            default_lim = 1.0 if new_j.joint_type == JointType.PRISMATIC else np.pi
            new_j.limits_enabled = bool(j_data.get("limits_enabled", False))
            new_j.limit_min = float(j_data.get("limit_min", -default_lim))
            new_j.limit_max = float(j_data.get("limit_max", default_lim))
            new_j.max_effort = float(j_data.get("max_effort", 0.0))
            new_j.max_velocity = float(j_data.get("max_velocity", 0.0))
            
            app.joints_list.append(new_j)
            QTreeWidgetItem(app.node_joints, [new_j.name])

        # --- 6. Restore Springs ---
        for s_data in data.get("springs", []):
            b_i, b_j = app.physics_bodies.get(s_data["body_i"]), app.physics_bodies.get(s_data["body_j"])
            if s_data["type"] == "compression":
                spring = CompressionSpring(s_data["name"], b_i, s_data["rf_i_name"], b_j, s_data["rf_j_name"], app.plotter)
                # DELETE THIS LINE: spring.bind_kinematics(app.rframes)
                spring.is_nonlinear = s_data.get("is_nonlinear", False)
                spring.compile_nonlinear_force(s_data.get("nonlinear_expr", "0"))
            else:
                spring = TorsionSpring(s_data["name"], b_i, s_data["rf_i_name"], b_j, s_data["rf_j_name"], s_data.get("axis_choice", 'Z'), app.plotter)
                # DELETE THIS LINE: spring.bind_kinematics(app.rframes, spring.axis_choice)
                spring.is_nonlinear = s_data.get("is_nonlinear", False)
                spring.compile_nonlinear_torque(s_data.get("nonlinear_expr", "0"))
                
            spring.stiffness, spring.damping, spring.preload = s_data["stiffness"], s_data["damping"], s_data["preload"]
            spring.enabled = s_data.get("enabled", True)
            
            # --- Restore Exact Math Vectors directly! ---
            spring.local_pos_i = np.array(s_data.get("local_pos_i", [0,0,0]))
            spring.local_pos_j = np.array(s_data.get("local_pos_j", [0,0,0]))
            spring.local_axis_i = np.array(s_data.get("local_axis_i", [0,0,1]))
            spring.local_ref_i = np.array(s_data.get("local_ref_i", [1,0,0]))
            spring.local_ref_j = np.array(s_data.get("local_ref_j", [1,0,0]))
            
            app.springs_list.append(spring)
            QTreeWidgetItem(app.node_springs, [spring.name])

        # --- 7. Restore Bushings ---
        for b_data in data.get("bushings", []):
            b_i, b_j = app.physics_bodies.get(b_data["body_i"]), app.physics_bodies.get(b_data["body_j"])
            bushing = Bushing(b_data["name"], b_i, b_data["rf_i_name"], b_j, b_data["rf_j_name"], app.plotter)
            
            bushing.k_trans, bushing.c_trans, bushing.p_trans = np.array(b_data["k_trans"]), np.array(b_data["c_trans"]), np.array(b_data["p_trans"])
            bushing.k_rot, bushing.c_rot, bushing.p_rot = np.array(b_data["k_rot"]), np.array(b_data["c_rot"]), np.array(b_data["p_rot"])
            bushing.enabled = b_data.get("enabled", True)
            
            # DELETE THIS LINE: bushing.bind_kinematics(app.rframes)
            
            # --- THE FIX: Restore Exact Math Vectors directly! ---
            bushing.local_pos_i = np.array(b_data.get("local_pos_i", [0,0,0]))
            bushing.local_pos_j = np.array(b_data.get("local_pos_j", [0,0,0]))
            bushing.local_axis_i = np.array(b_data.get("local_axis_i", [0,0,1]))
            bushing.local_rot_i = np.array(b_data.get("local_rot_i", np.eye(3).tolist()))
            if "local_rot_j" in b_data:
                bushing.local_rot_j = np.array(b_data["local_rot_j"])
            else:
                bushing.restore_local_rot_j(app.rframes)   # Older project files do not store it
            
            app.bushings_list.append(bushing)
            QTreeWidgetItem(getattr(app, 'node_bushings', app.node_springs), [bushing.name])

        # --- 8. Restore Contacts ---
        for c_data in data.get("contacts", []):
            b_i, b_j = app.physics_bodies.get(c_data["body_i"]), app.physics_bodies.get(c_data["body_j"])
            
            # --- Legacy Support Check ---
            # Try to grab the new integer mode. If it doesn't exist, fall back to checking the old boolean!
            m_mode = c_data.get("mesh_mode", None)
            if m_mode is None:
                m_mode = 1 if c_data.get("fine_mesh", False) else 0
                
            # Pass dummy UI parameters to the constructor, including our extracted m_mode
            cp = ContactPair(c_data["name"], b_i, b_j, stiffness_ui=1.0, exponent=1.5, damping_ui=1.0, 
                             friction_enabled=False, mu=0.0, slip_tol_ui=1.0, mesh_mode=m_mode)
            
            cp.stiffness = c_data["stiffness"]
            cp.exponent = c_data["exponent"]
            cp.damping = c_data["damping"]
            cp.friction_enabled = c_data.get("friction_enabled", False)
            cp.mu = c_data.get("mu", 0.3)
            cp.slip_tolerance = c_data.get("slip_tolerance", 0.01)
            # Older save files predate this upgrade, so default both to enabled.
            cp.symmetric_contact_search = c_data.get("symmetric_contact_search", True)
            cp.contact_candidate_reduction_enabled = c_data.get("contact_candidate_reduction_enabled", True)
            # Older save files predate the d_max damping saturation; 0.1mm matches the new UI default.
            cp.d_max_m = c_data.get("d_max_m", 0.0001)
            cp.enabled = c_data.get("enabled", True)
            
            app.contact_pairs.append(cp)
            QTreeWidgetItem(getattr(app, 'node_contacts'), [cp.name])
            
            

        # --- 8.5 Restore Gears ---
        for gd in data.get("gears", []):
            from unit_joints import GearType, GearPair
            
            if not hasattr(app, 'gear_pairs_list'):
                app.gear_pairs_list = []
                
            j1 = next((j for j in app.joints_list if j.name == gd["joint_1"]), None)
            j2 = next((j for j in app.joints_list if j.name == gd["joint_2"]), None)
            
            carrier_name = gd["carrier"]
            if carrier_name == "Ground":
                carrier = app.physics_bodies["Ground"]
            else:
                carrier = app.physics_bodies.get(carrier_name)
            
            if j1 and j2 and carrier:
                new_gear = GearPair(
                    name=gd["name"],
                    joint_1=j1,
                    joint_2=j2,
                    gear_type=GearType(gd["gear_type"]),
                    module_n=gd.get("module", 2.0),
                    z1=gd.get("z1", 20),
                    z2=gd.get("z2", 20),
                    alpha_deg=gd.get("alpha_deg", 20.0),
                    beta_deg=gd.get("beta_deg", 0.0),
                    gamma_deg=gd.get("gamma_deg", 45.0)
                )
                new_gear.enabled = gd.get("enabled", True)
                new_gear.carrier = carrier
                app.gear_pairs_list.append(new_gear)
                
                # Add to Tree Hierarchy UI
                if not hasattr(app, 'node_gear_pairs'):
                    app.node_gear_pairs = QTreeWidgetItem(app.ui.treeHierarchy, ["Gear Constraints"])
                
                QTreeWidgetItem(app.node_gear_pairs, [new_gear.name])
        
        # --- 8.6 Restore Kinematic Motions ---
        for m_data in data.get("motions", []):
            from unit_motions import JointMotion
            from PySide6.QtWidgets import QTreeWidgetItem
            
            if not hasattr(app, 'motions_list'):
                app.motions_list = []
                
            # Find the target joint the motion belongs to
            joint = next((j for j in app.joints_list if j.name == m_data["joint"]), None)
            
            if joint:
                new_motion = JointMotion(
                    name=m_data["name"],
                    joint=joint,
                    trans_rot=m_data.get("trans_rot", 0),
                    motion_type=m_data.get("motion_type", 0)
                )
                
                # Recompile the math string safely (prefer saved spline path, else extract from .mbd)
                motion_expr = ProjectManager._resolve_or_extract_spline_expr(
                    m_data.get("expression_str", "0.0"),
                    m_data.get("spline_file"),
                    temp_dir=temp_dir,
                    mbd_filepath=filepath,
                    base_dir=base_dir,
                    extracted_map=extracted_splines,
                )
                new_motion.compile_expression(motion_expr, base_dir=base_dir)
                new_motion.enabled = m_data.get("enabled", True)
                
                app.motions_list.append(new_motion)
                
                # Rebuild the Tree Hierarchy UI Node if it doesn't exist
                if not hasattr(app, 'node_motions'):
                    app.node_motions = QTreeWidgetItem(app.ui.treeHierarchy, ["Motions"])
                
                QTreeWidgetItem(app.node_motions, [new_motion.name])
        
        # --- 9. Restore Solver Settings & Robotics Trajectory Waypoints ---
        app.robotics_project_state = data.get("robotics", None)
        if getattr(app, 'robotics_window', None) is not None:
            app.robotics_window.populate_scene_selectors()
            app.robotics_window.import_project_state(app.robotics_project_state)

        if "solver_settings" in data:
            s_set = data["solver_settings"]
            app.ui.Edit_SimulationTime.setText(s_set.get("t_end", "10.0"))
            app.ui.Edit_StepsPerSec.setText(s_set.get("steps_per_sec", "100"))
            app.ui.Edit_Alpha_Beta.setText(s_set.get("baumgarte", "20"))
            app.ui.cmbSolverCompliance.setCurrentIndex(s_set.get("compliance_idx", 2))
            app.ui.cmbSolverMethod.setCurrentIndex(s_set.get("method_idx", 0))
            if hasattr(app.ui, 'cmbRtol'): app.ui.cmbRtol.setCurrentIndex(s_set.get("rtol_idx", 1))
            if hasattr(app.ui, 'cmbAtol'): app.ui.cmbAtol.setCurrentIndex(s_set.get("atol_idx", 2))
            if hasattr(app.ui, 'cmbMaxStep'): app.ui.cmbMaxStep.setCurrentIndex(s_set.get("max_step_idx", 0))

        # --- 10. Update ALL Visuals with exact sizing ---
        # shutil.rmtree(temp_dir)
        
        # 1. First, force the camera to look at the newly loaded bodies!
        app.plotter.reset_camera()
        
        # 2. Now that the camera is correct, calculate the visual scales
        app.update_rframe_scales()
        
        # 3. Extract the perfectly calculated scales
        current_scale = app.rframes[0].base_scale if app.rframes else 10.0
        
        # 4. Apply the scales to all components
        for force in app.forces_list: force.update_transform(current_scale)
        for joint in app.joints_list: joint.update_transform(current_scale)
        for spring in getattr(app, 'springs_list', []): spring.update_transform(current_scale)
        for bushing in getattr(app, 'bushings_list', []): bushing.update_transform(current_scale)

        if hasattr(app, 'update_rframe_scales'):
            app.update_rframe_scales()
            
        # --- Trigger the tree visualizer after everything is loaded! ---
        if hasattr(app, 'refresh_tree_visuals'):
            app.refresh_tree_visuals()
        
        # --- Force body visual states (black/transparent ghosting) to sync! ---
        if hasattr(app, 'update_selection_visuals'):
            app.update_selection_visuals(None)
                
        app.plotter.render()
        print(f"Project loaded successfully from {filepath}")
        
        # --- THE UPGRADE: Phase 2 State Restoration ---
        results_path = os.path.join(temp_dir, "results.npz")
        if os.path.exists(results_path):
            try:
                from unit_solver import MBSolver
                
                # --- Use 'with' to force NumPy to close the file handle! ---
                with np.load(results_path) as npz:
                    app.simulation_dt = float(npz['dt'][0])
                    
                    try:
                        baumgarte_val = float(app.ui.Edit_Alpha_Beta.text().strip().replace(',', '.'))
                    except Exception:
                        baumgarte_val = 20.0
                    compliance_map = {0: 0.0, 1: 1e-5, 2: 1e-7, 3: 1e-9, 4: 1e-11}
                    epsilon_val = compliance_map.get(app.ui.cmbSolverCompliance.currentIndex(), 1e-7)

                    # Instantiate a "Dummy" solver purely as a mathematical data container
                    app.solver = MBSolver(
                        app.physics_bodies, 
                        app.forces_list, 
                        app.joints_list,
                        getattr(app, 'springs_list', []) + getattr(app, 'bushings_list', []),
                        getattr(app, 'contact_pairs', []),
                        # --- Hand the gears to the dummy solver! ---
                        gear_pairs=getattr(app, 'gear_pairs_list', []),
                        # --- Hand the loaded motions to the dummy solver! ---
                        motions_list=getattr(app, 'motions_list', []),
                        epsilon=epsilon_val,
                        alpha=baumgarte_val,
                        beta=baumgarte_val
                    )
                    
                    # Inject the mathematical memory
                    app.solver.simulation_history = npz['simulation_history']
                    if 'time_history' in npz:
                        app.solver.time_history = np.array(npz['time_history'], copy=True)
                    else:
                        app.solver.time_history = np.arange(len(app.solver.simulation_history), dtype=float) * app.simulation_dt

                    diagnostics_ready = bool(npz['diagnostics_ready'][0]) if 'diagnostics_ready' in npz else False
                    app.solver._clear_postprocess_histories()

                    if diagnostics_ready:
                        actual_frames = len(app.solver.simulation_history)
                        lambda_history = np.array(npz['lambda_history'], copy=True)
                        contact_history = np.array(npz['contact_history'], copy=True)
                        gear_lambda_history = np.array(npz['gear_lambda_history'], copy=True) if 'gear_lambda_history' in npz else np.zeros((actual_frames, 0))
                        motion_lambda_history = np.array(npz['motion_lambda_history'], copy=True) if 'motion_lambda_history' in npz else np.zeros((actual_frames, 0))

                        if lambda_history.shape[0] == actual_frames and contact_history.shape[0] == actual_frames:
                            app.solver.lambda_history = lambda_history
                            app.solver.contact_history = contact_history
                            app.solver.gear_lambda_history = gear_lambda_history
                            app.solver.motion_lambda_history = motion_lambda_history
                            app.solver.diagnostics_ready = True
                    
                # --------------------------------------------------------------------
                
                # Instantly unlock the Playback UI!
                app.ui.btnRunAnimation.setEnabled(True)
                app.ui.btnPauseAnimation.setEnabled(True)
                app.ui.btnStopAnimation.setEnabled(True)
                app.ui.btnStepForward.setEnabled(True)  
                app.ui.btnStepBackward.setEnabled(True)
                
                # --- Re-enable the CSV Export and tracking flag! ---
                if hasattr(app.ui, 'btnExportCSV'):
                    app.ui.btnExportCSV.setEnabled(True)
                app._results_were_valid = True
                
                print("Embedded simulation results loaded successfully! Ready for playback.")
            except Exception as e:
                print(f"Warning: Could not load embedded results: {e}")
        else:
            # --- Lock the animation controls if no results exist! ---
            app.ui.btnRunAnimation.setEnabled(False)
            app.ui.btnPauseAnimation.setEnabled(False)
            app.ui.btnStopAnimation.setEnabled(False)
            app.ui.btnStepForward.setEnabled(False)  
            app.ui.btnStepBackward.setEnabled(False)
            
            if hasattr(app.ui, 'btnExportCSV'):
                app.ui.btnExportCSV.setEnabled(False)
            app._results_were_valid = False
            
            print("No embedded simulation results found. Animation controls locked.")        
                
        # Clean up the temp directory safely
        shutil.rmtree(temp_dir)        