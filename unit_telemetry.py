# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.1
#  Release Date: 2026/09/30
#  Module: unit_telemetry.py
#  Description:
#      Provides a graphical interface for post-processing and visualizing telemetry data 
#      from the simulation, including time histories of body motions, joint reactions, 
#      forces, springs, contacts, bushings, and gear pairs.
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
import pyqtgraph as pg
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QSplitter, QTreeWidget, QTreeWidgetItem, QListWidget,
                               QPushButton, QToolButton, QMessageBox, QFileDialog)
from PySide6.QtGui import QIcon, QPalette # <--- Added QIcon and QPalette
from PySide6.QtCore import Qt, QSize      # <--- Added QSize
import os
import sys

# Professional Scientific Color Palette for the graph curves
# PLOT_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# Color Palette 2 for the graph curves (10 distinct colors)
PLOT_COLORS = ["#ff3535", "#304efa", "#db51fd","#000000",  '#2ca02c', '#ff7f0e', '#8c564b', '#7f7f7f', '#bcbd22', '#17becf']

class TelemetryWindow(QMainWindow):
    # --- ADDED motions_list=None to the arguments ---
    def __init__(self, solver, dt, bodies, joints, forces, springs, contacts, bushings=None, gear_pairs=None, motions_list=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Telemetry Post-Processor")
        self.resize(1200, 500)

        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "icons", "SimPhant_Logo_64x64.ico")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        # --- Memory References ---
        self.solver = solver
        self.dt = dt
        self.bodies = bodies
        self.joints = joints
        self.forces = forces
        self.springs = springs
        self.contacts = contacts
        self.bushings = bushings if bushings is not None else []
        self.gear_pairs = gear_pairs if gear_pairs is not None else [] 
        self.motions_list = motions_list if motions_list is not None else [] 
        
        # Dictionary to store active plot references so we can remove them later
        self.active_curves = {}

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # The main layout only holds the splitter now (no bottom layout)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ==========================================
        # --- TOP SECTION: 3-Panel Splitter ---
        # ==========================================
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, stretch=1) 

        # 1. Left Panel: Component Tree
        self.tree_components = QTreeWidget()
        self.tree_components.setHeaderLabel("Simulation Components")
        self.tree_components.itemClicked.connect(self.on_tree_selection_changed)
        splitter.addWidget(self.tree_components)

        # 2. Middle Panel: Variable List
        self.list_variables = QListWidget()
        splitter.addWidget(self.list_variables)

        # ==========================================
        # --- 3. Right Panel: Toolbar & Graph ---
        # ==========================================
        # Configure global PyQtGraph settings 
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True) 
        
        self.plot_canvas = pg.PlotWidget()
        self.plot_canvas.addLegend(offset=(10, 10)) 
        self.plot_canvas.showGrid(x=True, y=True, alpha=0.3)
        self.plot_canvas.setLabel('bottom', "Time", units='s')

        # --- Create the Modern Tool Buttons (Flat UI) ---
        self.btn_fit_all = QToolButton()
        self.btn_fit_all.setToolTip("Fit All Data to View")
        self.btn_fit_all.setAutoRaise(True)
        
        self.btn_clear = QToolButton()
        self.btn_clear.setToolTip("Clear Graph")
        self.btn_clear.setAutoRaise(True)
        
        self.btn_export_png = QToolButton()
        self.btn_export_png.setToolTip("Save Image as PNG")
        self.btn_export_png.setAutoRaise(True)
        
        self.btn_export_svg = QToolButton()
        self.btn_export_svg.setToolTip("Save Image as SVG")
        self.btn_export_svg.setAutoRaise(True)
        
        self.btn_export_csv = QToolButton()
        self.btn_export_csv.setToolTip("Export Plotted Data as CSV")
        self.btn_export_csv.setAutoRaise(True)

        # --- Create the Top Toolbar Layout ---
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(self.btn_fit_all)
        toolbar_layout.addWidget(self.btn_clear)
        toolbar_layout.addWidget(self.btn_export_png)
        toolbar_layout.addWidget(self.btn_export_svg)
        toolbar_layout.addWidget(self.btn_export_csv)
        toolbar_layout.addStretch() # Pushes buttons to the left

        # --- Assemble the Right Panel ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addLayout(toolbar_layout)   # Toolbar on TOP
        right_layout.addWidget(self.plot_canvas) # Graph on BOTTOM
        
        splitter.addWidget(right_panel)

        # ==========================================
        # --- Crosshair & Coordinate Tracker ---
        # ==========================================
        self.v_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color='gray', width=1, style=Qt.DashLine))
        self.h_line = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(color='gray', width=1, style=Qt.DashLine))
        self.coord_label = pg.TextItem(text="", color='k', fill=pg.mkBrush(color=(255, 255, 255, 200)), anchor=(0, 1))
        
        self.plot_canvas.addItem(self.v_line, ignoreBounds=True)
        self.plot_canvas.addItem(self.h_line, ignoreBounds=True)
        self.plot_canvas.addItem(self.coord_label, ignoreBounds=True)
        
        self.v_line.hide()
        self.h_line.hide()
        self.coord_label.hide()
        
        self.crosshair_active = False 
        
        self.proxy = pg.SignalProxy(self.plot_canvas.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)
        self.plot_canvas.scene().sigMouseClicked.connect(self.on_mouse_clicked)
        # ==========================================

        splitter.setSizes([250, 250, 700])

        # --- CONNECTIONS ---
        self.list_variables.itemDoubleClicked.connect(self.plot_selected_variable)
        
        self.btn_fit_all.clicked.connect(self.fit_all_graphs)
        self.btn_clear.clicked.connect(self.clear_graph)
        self.btn_export_png.clicked.connect(self.export_png)
        self.btn_export_svg.clicked.connect(self.export_svg)
        self.btn_export_csv.clicked.connect(self.export_csv)
       
        # --- Disable the Broken PyQtGraph Exporter ---
        try:
            import pyqtgraph.exporters
            exporters_list = pyqtgraph.exporters.Exporter.Exporter.exporters
            pyqtgraph.exporters.Exporter.Exporter.exporters = [
                exp for exp in exporters_list if exp.__name__ != 'SVGExporter' 
            ]
        except Exception:
            pass 
            
        # ==========================================
        # --- ICON MANAGEMENT ---
        # ==========================================
        self.icon_mapping = {
            self.btn_fit_all: "Slide44.svg", # fit_all
            self.btn_clear: "Slide45.svg", # clear_graph
            self.btn_export_png: "Slide46.svg", # save_png
            self.btn_export_svg: "Slide47.svg", # save_svg
            self.btn_export_csv: "Slide48.svg" # export_csv
        }
        
        # Trigger the icon loader (Safely checks if the method below is added)
        if hasattr(self, 'apply_theme_icons'):
            self.apply_theme_icons()

        self.populate_tree()

    def populate_tree(self):
        """ Populates the Left Panel with categories and components from RAM. """
        self.tree_components.clear()

        # 1. Rigid Bodies
        root_bodies = QTreeWidgetItem(self.tree_components, ["Rigid Bodies"])
        for name, body in self.bodies.items():
            # --- THE FIX: Skip Ground AND disabled bodies ---
            if body.is_ground or not getattr(body, 'enabled', True): continue 
            
            item = QTreeWidgetItem(root_bodies, [name])
            item.setData(0, Qt.UserRole, {"category": "Body", "name": name})

        # 2. Joints
        if self.joints:
            root_joints = QTreeWidgetItem(self.tree_components, ["Joints"])
            for joint in self.joints:
                # --- THE FIX: Skip disabled joints ---
                if not getattr(joint, 'enabled', True): continue
                
                item = QTreeWidgetItem(root_joints, [joint.name])
                item.setData(0, Qt.UserRole, {"category": "Joint", "name": joint.name})

        # 3. Forces & Actuators
        if self.forces:
            root_forces = QTreeWidgetItem(self.tree_components, ["Forces & Actuators"])
            for force in self.forces:
                # --- Skip disabled forces or forces attached to disabled bodies ---
                if not getattr(force, 'enabled', True) or force.parent_body.is_ground or not force.parent_body.enabled: 
                    continue
                    
                item = QTreeWidgetItem(root_forces, [force.name])
                # --- Inject the force_type into the secret metadata dictionary! ---
                item.setData(0, Qt.UserRole, {
                    "category": "Force", 
                    "name": force.name, 
                    "force_type": force.force_type
                })

        # 4. Springs & Bushings
        if self.springs or self.bushings: # <--- THE FIX: Check both lists!
            root_springs = QTreeWidgetItem(self.tree_components, ["Springs & Bushings"])
            
            # --- Populate Springs ---
            for spring in self.springs:
                # --- Skip disabled springs ---
                if not getattr(spring, 'enabled', True) or (spring.body_i.is_ground and spring.body_j.is_ground): 
                    continue
                    
                item = QTreeWidgetItem(root_springs, [spring.name])
                item.setData(0, Qt.UserRole, {"category": "Spring", "name": spring.name})
                
            # --- Populate Bushings ---
            for bushing in self.bushings:
                # --- Skip disabled bushings ---
                if not getattr(bushing, 'enabled', True) or (bushing.body_i.is_ground and bushing.body_j.is_ground): 
                    continue
                item = QTreeWidgetItem(root_springs, [bushing.name])
                item.setData(0, Qt.UserRole, {"category": "Bushing", "name": bushing.name})


        # 5. Contact Pairs
        if self.contacts:
            root_contacts = QTreeWidgetItem(self.tree_components, ["Contact Pairs"])
            for cp in self.contacts:
                # --- THE FIX: Skip disabled contacts ---
                if not getattr(cp, 'enabled', True) or not cp.body_i.enabled or not cp.body_j.enabled: 
                    continue
                    
                item = QTreeWidgetItem(root_contacts, [cp.name])
                item.setData(0, Qt.UserRole, {"category": "Contact", "name": cp.name})

        # --- 6. Gear Constraints ---
        if self.gear_pairs:
            root_gears = QTreeWidgetItem(self.tree_components, ["Gear Constraints"])
            for gear in self.gear_pairs:
                if not getattr(gear, 'enabled', True) or not gear.body_1.enabled or not gear.body_2.enabled: 
                    continue
                item = QTreeWidgetItem(root_gears, [gear.name])
                item.setData(0, Qt.UserRole, {"category": "Gear", "name": gear.name})
                
        # --- 7. Kinematic Motions ---
        if self.motions_list:
            root_motions = QTreeWidgetItem(self.tree_components, ["Kinematic Motions"])
            for motion in self.motions_list:
                # Skip if the motion itself, or its target joint, is disabled
                if not getattr(motion, 'enabled', True) or not getattr(motion.joint, 'enabled', True): 
                    continue
                item = QTreeWidgetItem(root_motions, [motion.name])
                item.setData(0, Qt.UserRole, {"category": "Motion", "name": motion.name})
                
        # Expand all folders by default so the user sees everything
        self.tree_components.expandAll()

    def on_tree_selection_changed(self, item, column):
        """ Populates the Middle Panel with plot-able variables when a component is clicked. """
        self.list_variables.clear()
        
        # Retrieve the hidden secret data we assigned in populate_tree
        item_data = item.data(0, Qt.UserRole)
        if not item_data: return # The user clicked a Root folder (e.g., "Rigid Bodies"), do nothing.
        
        category = item_data["category"]
        comp_name = item_data["name"]
        
        variables_to_list = []
        
        # These variable names mirror exactly what was calculated in export_csv
        if category == "Body":
            variables_to_list = [
                "Position X (m)", "Position Y (m)", "Position Z (m)",
                "Angular Pos Roll_X (rad)", "Angular Pos Pitch_Y (rad)", "Angular Pos Yaw_Z (rad)",
                "Velocity X (m/s)", "Velocity Y (m/s)", "Velocity Z (m/s)",
                "Angular Vel X_loc (rad/s)", "Angular Vel Y_loc (rad/s)", "Angular Vel Z_loc (rad/s)",
                "Kinetic Energy Trans (J)", "Kinetic Energy Rot (J)", "Potential Energy (J)", "Total Energy (J)"
            ]
        elif category == "Joint":
            variables_to_list = [
                "Reaction Fx (N, Global)", "Reaction Fy (N, Global)", "Reaction Fz (N, Global)",
                "Reaction Tx (Nm, Global)", "Reaction Ty (Nm, Global)", "Reaction Tz (Nm, Global)"
            ]
        elif category == "Force":
            # --- Dynamically list ONLY Forces or ONLY Torques ---
            from unit_forces import ForceType
            f_type = item_data.get("force_type")
            
            if f_type in [ForceType.FORCE, ForceType.ACTUATOR]:
                variables_to_list = [
                    "Applied Fx (N, Global)", "Applied Fy (N, Global)", "Applied Fz (N, Global)"
                ]
            else: # TORQUE or E_MOTOR
                variables_to_list = [
                    "Applied Tx (Nm, Local)", "Applied Ty (Nm, Local)", "Applied Tz (Nm, Local)"
                ]
        elif category == "Spring":
            # For Bushings and Springs
            variables_to_list = [
                "Deflection_X (m/rad)", "Velocity_X (m/s)", 
                "Force_Elastic (N/Nm)", "Force_Damping (N/Nm)", "Force_Total (N/Nm)"
            ]
        elif category == "Bushing":
            variables_to_list = [
                "Deflection X (m)", "Deflection Y (m)", "Deflection Z (m)",
                "Rotation X (rad)", "Rotation Y (rad)", "Rotation Z (rad)",
                "Force X (N)", "Force Y (N)", "Force Z (N)",
                "Torque X (Nm)", "Torque Y (Nm)", "Torque Z (Nm)"
            ]    
        elif category == "Contact":
            variables_to_list = [
                "Force_Spring (N)", "Force_Damping (N)", "Force_Total Normal (N)", "Force_Friction (N)"
            ]
        # --- Gear Variables ---
        elif category == "Gear":
            variables_to_list = [
                "Tangential Force_Ft (N)", "Radial Force_Fr (N)", "Axial Force_Fa (N)", "Total Contact Force_Fc (N)"
            ]  
            
        # --- Motion Variables ---
        elif category == "Motion":
            motion = next((m for m in self.motions_list if m.name == comp_name), None)
            if motion:
                if motion.trans_rot.value == 0: # Translational
                    variables_to_list = [
                        "Actuator Force (N)", 
                        "Displacement (m)", 
                        "Velocity (m/s)", 
                        "Acceleration (m/s²)"
                    ]
                else: # Rotational
                    variables_to_list = [
                        "Actuator Torque (Nm)", 
                        "Angular Displacement (rad)", 
                        "Angular Velocity (rad/s)", 
                        "Angular Acceleration (rad/s²)"
                    ]
              
        # Add the variables to the list, hiding the component name inside each one
        for var_name in variables_to_list:
            from PySide6.QtWidgets import QListWidgetItem
            list_item = QListWidgetItem(var_name)
            
            # Hide the full signature so the graph knows exactly what to extract later!
            # Example: {"category": "Body", "name": "Body_1", "variable": "Position X (m)"}
            plot_signature = {
                "category": category,
                "name": comp_name,
                "variable": var_name
            }
            list_item.setData(Qt.UserRole, plot_signature)
            self.list_variables.addItem(list_item)
            
    def plot_selected_variable(self, item):
        """ Slices the raw RAM arrays and plots the mathematical curve. """
        # 1. Extract the secret metadata from the double-clicked item
        meta = item.data(Qt.UserRole)
        if not meta: return
        
        category = meta["category"]
        comp_name = meta["name"]
        var_name = meta["variable"]
        
        # Generate a unique string for the Legend
        curve_id = f"{comp_name} - {var_name}"
        
        # Prevent plotting the exact same curve twice
        if curve_id in self.active_curves:
            return 
            
        # 2. Generate the X-Axis (Time Array)
        num_frames = len(self.solver.simulation_history)
        t_array = np.arange(num_frames) * self.dt
        y_array = None
        
        # ========================================================
        # 3. HIGH-SPEED ARRAY SLICING (Bodies & Contacts)
        # ========================================================
        if category == "Body":
            b_idx = self.solver.body_index_map.get(comp_name)
            if b_idx is None: return
            
            pos_start = b_idx * 7
            vel_start = self.solver.N_pos + (b_idx * 6)
            
            # --- Kinematics ---
            if "Position X" in var_name: y_array = self.solver.simulation_history[:, pos_start + 0]
            elif "Position Y" in var_name: y_array = self.solver.simulation_history[:, pos_start + 1]
            elif "Position Z" in var_name: y_array = self.solver.simulation_history[:, pos_start + 2]
            # --- Angular Positions (Unwrapped Euler Angles) ---
            elif "Angular Pos" in var_name:
                from scipy.spatial.transform import Rotation
                qx = self.solver.simulation_history[:, pos_start + 3]
                qy = self.solver.simulation_history[:, pos_start + 4]
                qz = self.solver.simulation_history[:, pos_start + 5]
                qw = self.solver.simulation_history[:, pos_start + 6]
                
                # SciPy strictly uses scalar-last quaternion format: [x, y, z, w]
                quats = np.vstack((qx, qy, qz, qw)).T
                eulers = Rotation.from_quat(quats).as_euler('xyz', degrees=False)
                
                # We use np.unwrap to prevent ugly 180-degree zigzag jumps on the graph!
                if "Roll_X" in var_name: y_array = np.unwrap(eulers[:, 0])
                elif "Pitch_Y" in var_name: y_array = np.unwrap(eulers[:, 1])
                elif "Yaw_Z" in var_name: y_array = np.unwrap(eulers[:, 2])
            elif "Velocity X" in var_name: y_array = self.solver.simulation_history[:, vel_start + 0]
            elif "Velocity Y" in var_name: y_array = self.solver.simulation_history[:, vel_start + 1]
            elif "Velocity Z" in var_name: y_array = self.solver.simulation_history[:, vel_start + 2]
            elif "Angular Vel X" in var_name: y_array = self.solver.simulation_history[:, vel_start + 3]
            elif "Angular Vel Y" in var_name: y_array = self.solver.simulation_history[:, vel_start + 4]
            elif "Angular Vel Z" in var_name: y_array = self.solver.simulation_history[:, vel_start + 5]
            
            # --- Energy ---
            elif "Kinetic Energy Trans" in var_name:
                body = self.bodies[comp_name]
                vx = self.solver.simulation_history[:, vel_start + 0]
                vy = self.solver.simulation_history[:, vel_start + 1]
                vz = self.solver.simulation_history[:, vel_start + 2]
                y_array = 0.5 * body.mass * (vx**2 + vy**2 + vz**2)
                
            elif "Kinetic Energy Rot" in var_name:
                body = self.bodies[comp_name]
                wx = self.solver.simulation_history[:, vel_start + 3]
                wy = self.solver.simulation_history[:, vel_start + 4]
                wz = self.solver.simulation_history[:, vel_start + 5]
                I = body.principal_inertia
                y_array = 0.5 * (I[0]*wx**2 + I[1]*wy**2 + I[2]*wz**2)
                
            elif "Potential Energy" in var_name:
                body = self.bodies[comp_name]
                px = self.solver.simulation_history[:, pos_start + 0]
                py = self.solver.simulation_history[:, pos_start + 1]
                pz = self.solver.simulation_history[:, pos_start + 2]
                
                g_vec = np.zeros(3)
                for f in self.forces:
                    if getattr(f, 'is_gravity', False) and f.parent_body.name == body.name:
                        if getattr(f, 'enabled', True): # <--- THE BUG FIX
                            g_vec = f.base_vector
                        break
                        
                y_array = -body.mass * (g_vec[0]*px + g_vec[1]*py + g_vec[2]*pz)
                    
            elif "Total Energy" in var_name:
                body = self.bodies[comp_name]
                vx = self.solver.simulation_history[:, vel_start + 0]
                vy = self.solver.simulation_history[:, vel_start + 1]
                vz = self.solver.simulation_history[:, vel_start + 2]
                ke_trans = 0.5 * body.mass * (vx**2 + vy**2 + vz**2)
                
                wx = self.solver.simulation_history[:, vel_start + 3]
                wy = self.solver.simulation_history[:, vel_start + 4]
                wz = self.solver.simulation_history[:, vel_start + 5]
                I = body.principal_inertia
                ke_rot = 0.5 * (I[0]*wx**2 + I[1]*wy**2 + I[2]*wz**2)
                
                px = self.solver.simulation_history[:, pos_start + 0]
                py = self.solver.simulation_history[:, pos_start + 1]
                pz = self.solver.simulation_history[:, pos_start + 2]
                
                g_vec = np.zeros(3)
                for f in self.forces:
                    if getattr(f, 'is_gravity', False) and f.parent_body.name == body.name:
                        if getattr(f, 'enabled', True): # <--- THE BUG FIX
                            g_vec = f.base_vector
                        break
                        
                # --- Full dot product ensures m*g*h works on any axis! ---
                pe = -body.mass * (g_vec[0]*px + g_vec[1]*py + g_vec[2]*pz)
                y_array = ke_trans + ke_rot + pe
                
        elif category == "Contact":
            c_idx = next((i for i, cp in enumerate(self.contacts) if cp.name == comp_name), None)
            if c_idx is not None:
                if "Force_Spring" in var_name: y_array = self.solver.contact_history[:, c_idx, 0]
                elif "Force_Damping" in var_name: y_array = self.solver.contact_history[:, c_idx, 1]
                elif "Total Normal" in var_name: y_array = self.solver.contact_history[:, c_idx, 2]
                elif "Friction" in var_name: y_array = self.solver.contact_history[:, c_idx, 3]

        # --- GEAR FAST EXTRACTION ---
        elif category == "Gear":
            from unit_joints import GearType
            g_idx = next((i for i, g in enumerate(self.gear_pairs) if g.name == comp_name), None)
            
            if g_idx is not None and hasattr(self.solver, 'gear_lambda_history'):
                gear = self.gear_pairs[g_idx]
                
                # F_t is directly extracted from the matrix multipliers
                F_t = self.solver.gear_lambda_history[:, g_idx]
                
                # Apply pure vector math to the entire array at once!
                if "Tangential Force_Ft" in var_name: 
                    y_array = F_t
                elif "Radial Force_Fr" in var_name: 
                    if gear.gear_type == GearType.BEVEL:
                        y_array = np.abs(F_t) * np.tan(gear.alpha) * np.cos(gear.gamma)
                    else:
                        y_array = np.abs(F_t) * np.tan(gear.alpha) / np.cos(gear.beta)
                elif "Axial Force_Fa" in var_name: 
                    if gear.gear_type == GearType.BEVEL:
                        y_array = np.abs(F_t) * np.tan(gear.alpha) * np.sin(gear.gamma)
                    else:
                        y_array = np.abs(F_t) * np.tan(gear.beta) * np.sign(F_t)
                elif "Total Contact Force_Fc" in var_name:
                    if gear.gear_type == GearType.BEVEL:
                        F_r_arr = np.abs(F_t) * np.tan(gear.alpha) * np.cos(gear.gamma)
                        F_a_arr = np.abs(F_t) * np.tan(gear.alpha) * np.sin(gear.gamma)
                    else:
                        F_r_arr = np.abs(F_t) * np.tan(gear.alpha) / np.cos(gear.beta)
                        F_a_arr = np.abs(F_t) * np.tan(gear.beta) * np.sign(F_t)
                    y_array = np.sqrt(F_t**2 + F_r_arr**2 + F_a_arr**2)
        
        # ========================================================
        # --- MOTION FAST EXTRACTION ---
        # ========================================================
        elif category == "Motion":
            # Rebuild the active motions list exactly as the solver sees it to match array indices
            active_motions = [m for m in self.motions_list if getattr(m, 'enabled', True) and getattr(m.joint, 'enabled', True) and m.joint.body_i.enabled and m.joint.body_j.enabled]
            m_idx = next((i for i, m in enumerate(active_motions) if m.name == comp_name), None)
            
            # Get the exact motion object from memory
            motion_obj = next((m for m in self.motions_list if m.name == comp_name), None)
            
            if "Actuator" in var_name:
                if m_idx is not None and hasattr(self.solver, 'motion_lambda_history'):
                    # The solver multiplier inherently contains the exact required actuator effort!
                    y_array = self.solver.motion_lambda_history[:, m_idx]
                    
            elif motion_obj is not None:
                # Re-evaluate the user's compiled math expression over the exact simulation timeline
                y_array = np.zeros(num_frames)
                for i in range(num_frames):
                    t = t_array[i]
                    
                    # f0 = Pos, df = Vel, ddf = Accel
                    f0, df, ddf = motion_obj.get_kinematics(t)
                    
                    # Map the requested variable to the exact kinematic property
                    if "Displacement" in var_name:
                        y_array[i] = f0
                    elif "Velocity" in var_name:
                        y_array[i] = df
                    elif "Acceleration" in var_name:
                        y_array[i] = ddf
                        
        # ========================================================
        # 4. DYNAMIC EXTRACTION (Forces, Joints, Springs)
        # ========================================================
        elif category in ["Force", "Joint", "Spring", "Bushing"]:
            from unit_forces import ForceType
            from unit_joints import JointType
            
            y_array = np.zeros(num_frames)
            
            # --- Safely preserve the user's 3D Viewport! ---
            main_app = self.parent()
            current_frame = 0
            if main_app and hasattr(main_app, 'playback_time'):
                current_frame = int(main_app.playback_time / self.dt)
                current_frame = min(max(current_frame, 0), num_frames - 1)
                
            # Pre-calculate the Joint Lambda Map
            lambda_map = {}
            if category == "Joint":
                l_counter = 0
                for j in self.joints:
                    if not j.enabled: continue
                    lambda_map[j.name] = l_counter
                    if j.joint_type == JointType.SPHERICAL: l_counter += 3
                    elif j.joint_type == JointType.REVOLUTE: l_counter += 5
                    elif j.joint_type == JointType.PRISMATIC: l_counter += 5
                    elif j.joint_type == JointType.CYLINDRICAL: l_counter += 4
                    elif j.joint_type == JointType.PLANAR: l_counter += 3
                    elif j.joint_type == JointType.FIXED: l_counter += 6
                    
            # The Mathematics Loop
            for i in range(num_frames):
                self.solver.unpack_state(self.solver.simulation_history[i])
                
                # --- Calculate the exact time for this specific frame ---
                t = i * self.dt 
                
                # --- FORCE MATH ---
                if category == "Force":
                    force = next((f for f in self.forces if f.name == comp_name), None)
                    if force:
                        body = force.parent_body
                        F_glob, T_loc = np.zeros(3), np.zeros(3)
                        
                        if getattr(force, 'is_gravity', False):
                            F_glob = force.base_vector * body.mass
                        elif force.force_type == ForceType.FORCE:
                            F_glob = force.get_global_vector(t) # <--- ADD t
                            T_loc = np.cross(force.get_local_position(), force.get_local_vector(t)) # <--- ADD t
                        elif force.force_type == ForceType.TORQUE:
                            T_loc = force.get_local_vector(t) # <--- ADD t
                        elif force.force_type == ForceType.ACTUATOR:
                            F_glob_max = force.get_global_vector(t) # <--- ADD t
                            F_max = np.linalg.norm(F_glob_max)
                            scale = 1.0
                            if F_max > 1e-6 and force.speed_max > 0.0:
                                axis_global = F_glob_max / F_max
                                r_glob = body.principal_axes @ force.get_local_position()
                                w_glob = body.principal_axes @ body.angular_velocity
                                v_point_glob = body.velocity + np.cross(w_glob, r_glob) 
                                v_current = np.dot(v_point_glob, axis_global)
                                scale = 1.0 - (v_current / force.speed_max)
                                if not getattr(force, 'allow_braking', True): scale = max(0.0, scale)
                            F_glob = F_glob_max * scale
                        elif force.force_type == ForceType.E_MOTOR:
                            T_loc_max = force.get_local_vector(t) # <--- ADD t
                            T_max = np.linalg.norm(T_loc_max)
                            scale = 1.0
                            if T_max > 1e-6 and force.speed_max > 0.0:
                                axis_local = T_loc_max / T_max
                                omega_current = np.dot(body.angular_velocity, axis_local)
                                scale = 1.0 - (omega_current / force.speed_max)
                                if not getattr(force, 'allow_braking', True): scale = max(0.0, scale)
                            T_loc = T_loc_max * scale

                        if "Fx" in var_name: y_array[i] = F_glob[0]
                        elif "Fy" in var_name: y_array[i] = F_glob[1]
                        elif "Fz" in var_name: y_array[i] = F_glob[2]
                        elif "Tx" in var_name: y_array[i] = T_loc[0]
                        elif "Ty" in var_name: y_array[i] = T_loc[1]
                        elif "Tz" in var_name: y_array[i] = T_loc[2]
                        
                # --- JOINT MATH ---
                elif category == "Joint":
                    joint = next((j for j in self.joints if j.name == comp_name), None)
                    if joint and self.solver.num_equations > 0:
                        l_idx = lambda_map.get(comp_name)
                        if l_idx is not None:
                            lambdas = self.solver.lambda_history[i]
                            F_glob, T_glob = np.zeros(3), np.zeros(3)
                            A_i, A_j = joint.body_i.principal_axes, joint.body_j.principal_axes
                            
                            if joint.joint_type == JointType.SPHERICAL:
                                F_glob = np.array([lambdas[l_idx], lambdas[l_idx+1], lambdas[l_idx+2]])
                            elif joint.joint_type == JointType.REVOLUTE:
                                F_glob = np.array([lambdas[l_idx], lambdas[l_idx+1], lambdas[l_idx+2]])
                                v_glob_i = A_i @ joint.local_axis_i
                                a_glob_j, b_glob_j = A_j @ joint.local_a_j, A_j @ joint.local_b_j
                                T_glob = lambdas[l_idx+3] * np.cross(v_glob_i, a_glob_j) + lambdas[l_idx+4] * np.cross(v_glob_i, b_glob_j)
                            elif joint.joint_type == JointType.PRISMATIC:
                                v_loc_i = joint.local_axis_i
                                # --- THE FIX: Use the exact 1-RF axes! ---
                                a_loc_i = getattr(joint, 'local_a_i', np.array([1.0, 0.0, 0.0]))
                                b_loc_i = getattr(joint, 'local_b_i', np.array([0.0, 1.0, 0.0]))
                                v_glob_i, a_glob_i, b_glob_i = A_i @ v_loc_i, A_i @ a_loc_i, A_i @ b_loc_i
                                a_glob_j, b_glob_j = A_j @ joint.local_a_j, A_j @ joint.local_b_j
                                s_i_glob, s_j_glob = A_i @ joint.local_pos_i, A_j @ joint.local_pos_j
                                d = (joint.body_j.cog + s_j_glob) - (joint.body_i.cog + s_i_glob)
                                F_body_i = -lambdas[l_idx+3] * a_glob_i - lambdas[l_idx+4] * b_glob_i
                                T_pure_i = lambdas[l_idx+0] * np.cross(v_glob_i, a_glob_j) + lambdas[l_idx+1] * np.cross(v_glob_i, b_glob_j) + lambdas[l_idx+2] * np.cross(a_glob_i, b_glob_j)
                                F_glob = -F_body_i
                                T_glob = T_pure_i + np.cross(d, F_body_i)
                            elif joint.joint_type == JointType.CYLINDRICAL:
                                v_loc_i = joint.local_axis_i
                                # --- THE FIX: Use the exact 1-RF axes! ---
                                a_loc_i = getattr(joint, 'local_a_i', np.array([1.0, 0.0, 0.0]))
                                b_loc_i = getattr(joint, 'local_b_i', np.array([0.0, 1.0, 0.0]))
                                v_glob_i, a_glob_i, b_glob_i = A_i @ v_loc_i, A_i @ a_loc_i, A_i @ b_loc_i
                                a_glob_j, b_glob_j = A_j @ joint.local_a_j, A_j @ joint.local_b_j
                                s_i_glob, s_j_glob = A_i @ joint.local_pos_i, A_j @ joint.local_pos_j
                                d = (joint.body_j.cog + s_j_glob) - (joint.body_i.cog + s_i_glob)
                                F_body_i = -lambdas[l_idx+2] * a_glob_i - lambdas[l_idx+3] * b_glob_i
                                T_pure_i = lambdas[l_idx+0] * np.cross(v_glob_i, a_glob_j) + lambdas[l_idx+1] * np.cross(v_glob_i, b_glob_j)
                                F_glob = -F_body_i
                                T_glob = T_pure_i + np.cross(d, F_body_i)
                            elif joint.joint_type == JointType.PLANAR:
                                v_glob_i = A_i @ joint.local_axis_i
                                a_glob_j, b_glob_j = A_j @ joint.local_a_j, A_j @ joint.local_b_j
                                s_i_glob, s_j_glob = A_i @ joint.local_pos_i, A_j @ joint.local_pos_j
                                d = (joint.body_j.cog + s_j_glob) - (joint.body_i.cog + s_i_glob)
                                F_body_i = -lambdas[l_idx+2] * v_glob_i
                                T_pure_i = lambdas[l_idx+0] * np.cross(v_glob_i, a_glob_j) + lambdas[l_idx+1] * np.cross(v_glob_i, b_glob_j)
                                F_glob = -F_body_i
                                T_glob = T_pure_i + np.cross(d, F_body_i)
                            elif joint.joint_type == JointType.FIXED:
                                v_loc_i = joint.local_axis_i
                                # --- THE FIX: Use the exact 1-RF axes! ---
                                a_loc_i = getattr(joint, 'local_a_i', np.array([1.0, 0.0, 0.0]))
                                v_glob_i, a_glob_i = A_i @ v_loc_i, A_i @ a_loc_i
                                a_glob_j, b_glob_j = A_j @ joint.local_a_j, A_j @ joint.local_b_j
                                F_glob = np.array([lambdas[l_idx+0], lambdas[l_idx+1], lambdas[l_idx+2]])
                                T_glob = lambdas[l_idx+3] * np.cross(v_glob_i, a_glob_j) + lambdas[l_idx+4] * np.cross(v_glob_i, b_glob_j) + lambdas[l_idx+5] * np.cross(a_glob_i, b_glob_j)
                                
                            if "Fx" in var_name: y_array[i] = F_glob[0]
                            elif "Fy" in var_name: y_array[i] = F_glob[1]
                            elif "Fz" in var_name: y_array[i] = F_glob[2]
                            elif "Tx" in var_name: y_array[i] = T_glob[0]
                            elif "Ty" in var_name: y_array[i] = T_glob[1]
                            elif "Tz" in var_name: y_array[i] = T_glob[2]
                            
                # --- SPRING MATH ---
                elif category == "Spring":
                    spring = next((s for s in self.springs if s.name == comp_name), None)
                    if spring:
                        A_i, A_j = spring.body_i.principal_axes, spring.body_j.principal_axes
                        if hasattr(spring, 'initial_length'): # Compression Spring
                            r_i_glob = A_i @ spring.local_pos_i
                            r_j_glob = A_j @ spring.local_pos_j
                            p_i = spring.body_i.cog + r_i_glob
                            p_j = spring.body_j.cog + r_j_glob
                            vec_ij = p_j - p_i
                            L = np.linalg.norm(vec_ij)
                            if L >= 1e-8:
                                u_ij = vec_ij / L
                                w_i_glob = A_i @ spring.body_i.angular_velocity
                                w_j_glob = A_j @ spring.body_j.angular_velocity
                                v_i_glob = spring.body_i.velocity + np.cross(w_i_glob, r_i_glob)
                                v_j_glob = spring.body_j.velocity + np.cross(w_j_glob, r_j_glob)
                                L_dot = np.dot(v_j_glob - v_i_glob, u_ij)
                                delta_L = L - spring.initial_length
                                F_def = spring.stiffness * delta_L
                                F_damp = spring.damping * L_dot
                                F_res = F_def + F_damp - spring.preload
                                
                                if "Deflection" in var_name: y_array[i] = delta_L
                                elif "Velocity" in var_name: y_array[i] = L_dot
                                elif "Force_Elastic" in var_name: y_array[i] = F_def
                                elif "Force_Damping" in var_name: y_array[i] = F_damp
                                elif "Force_Total" in var_name: y_array[i] = F_res
                                
                        elif hasattr(spring, 'initial_angle'): # Torsion Spring
                            w_i_glob = A_i @ spring.body_i.angular_velocity
                            w_j_glob = A_j @ spring.body_j.angular_velocity
                            axis_glob = A_i @ spring.local_axis_i
                            ref_i_glob = A_i @ spring.local_ref_i
                            ref_j_glob = A_j @ spring.local_ref_j
                            
                            theta_dot = np.dot(w_j_glob - w_i_glob, axis_glob)
                            y_axis = np.cross(axis_glob, ref_i_glob)
                            proj_j = ref_j_glob - np.dot(ref_j_glob, axis_glob) * axis_glob
                            if np.linalg.norm(proj_j) > 1e-8: proj_j /= np.linalg.norm(proj_j)
                            cos_th = np.dot(ref_i_glob, proj_j)
                            sin_th = np.dot(y_axis, proj_j)
                            current_angle = np.arctan2(sin_th, cos_th)
                            
                            delta_theta = current_angle - spring.initial_angle
                            if delta_theta > np.pi: delta_theta -= 2 * np.pi
                            elif delta_theta < -np.pi: delta_theta += 2 * np.pi
                            
                            T_def = spring.stiffness * delta_theta
                            T_damp = spring.damping * theta_dot
                            T_res = T_def + T_damp - spring.preload
                            
                            if "Deflection" in var_name: y_array[i] = delta_theta
                            elif "Velocity" in var_name: y_array[i] = theta_dot
                            elif "Force_Elastic" in var_name: y_array[i] = T_def
                            elif "Force_Damping" in var_name: y_array[i] = T_damp
                            elif "Force_Total" in var_name: y_array[i] = T_res
                
                # --- BUSHING MATH ---
                elif category == "Bushing":
                    bushing = next((b for b in self.bushings if b.name == comp_name), None)
                    if bushing:
                        A_i, A_j = bushing.body_i.principal_axes, bushing.body_j.principal_axes
                        
                        R_rf_i = A_i @ bushing.local_rot_i
                        
                        w_i_glob = A_i @ bushing.body_i.angular_velocity
                        w_j_glob = A_j @ bushing.body_j.angular_velocity
                        v_i_glob = bushing.body_i.velocity + np.cross(w_i_glob, A_i @ bushing.local_pos_i)
                        v_j_glob = bushing.body_j.velocity + np.cross(w_j_glob, A_j @ bushing.local_pos_j)
                        
                        p_i = bushing.body_i.cog + A_i @ bushing.local_pos_i
                        p_j = bushing.body_j.cog + A_j @ bushing.local_pos_j
                        
                        # Calculate translations
                        delta_x = (R_rf_i.T @ (p_j - p_i)) - bushing.initial_local_pos_j
                        v_rel_loc = R_rf_i.T @ (v_j_glob - v_i_glob)
                        
                        # Calculate rotations
                        R_rel = R_rf_i.T @ A_j
                        R_delta = R_rel @ bushing.initial_rel_rot.T
                        
                        angle = np.arccos(np.clip((np.trace(R_delta) - 1.0) / 2.0, -1.0, 1.0))
                        if angle > 1e-8:
                            axis = np.array([R_delta[2,1]-R_delta[1,2], R_delta[0,2]-R_delta[2,0], R_delta[1,0]-R_delta[0,1]])
                            norm_axis = np.linalg.norm(axis)
                            delta_theta = (axis / norm_axis) * angle if norm_axis > 1e-8 else np.zeros(3)
                        else:
                            delta_theta = np.zeros(3)
                            
                        w_rel_loc = R_rf_i.T @ (w_j_glob - w_i_glob)
                        
                        # Final 6-DOF Local Forces & Torques
                        F_calc_loc = -(bushing.k_trans * delta_x) - (bushing.c_trans * v_rel_loc) + bushing.p_trans
                        T_calc_loc = -(bushing.k_rot * delta_theta) - (bushing.c_rot * w_rel_loc) + bushing.p_rot
                        
                        if "Deflection X" in var_name: y_array[i] = delta_x[0]
                        elif "Deflection Y" in var_name: y_array[i] = delta_x[1]
                        elif "Deflection Z" in var_name: y_array[i] = delta_x[2]
                        elif "Rotation X" in var_name: y_array[i] = delta_theta[0]
                        elif "Rotation Y" in var_name: y_array[i] = delta_theta[1]
                        elif "Rotation Z" in var_name: y_array[i] = delta_theta[2]
                        elif "Force X" in var_name: y_array[i] = F_calc_loc[0]
                        elif "Force Y" in var_name: y_array[i] = F_calc_loc[1]
                        elif "Force Z" in var_name: y_array[i] = F_calc_loc[2]
                        elif "Torque X" in var_name: y_array[i] = T_calc_loc[0]
                        elif "Torque Y" in var_name: y_array[i] = T_calc_loc[1]
                        elif "Torque Z" in var_name: y_array[i] = T_calc_loc[2]
                        
            # --- Safely restore the 3D Viewport math exactly to where it was! ---
            self.solver.unpack_state(self.solver.simulation_history[current_frame])

        # ========================================================
        # 5. SEND TO PYQTGRAPH
        # ========================================================
        if y_array is not None:
            color_hex = PLOT_COLORS[len(self.active_curves) % len(PLOT_COLORS)]
            pen = pg.mkPen(color=color_hex, width=2.5) 
            curve = self.plot_canvas.plot(t_array, y_array, name=curve_id, pen=pen)
            self.active_curves[curve_id] = curve
            self.plot_canvas.autoRange()

    def clear_graph(self):
        """ Wipes the curves from the canvas and deactivates the crosshair. """
        # Safely remove only the curves so we don't accidentally delete the crosshair lines or the legend!
        for curve in self.active_curves.values():
            self.plot_canvas.removeItem(curve)
            
        self.active_curves.clear()
        
        # Turn off the crosshair tracker as requested!
        self.crosshair_active = False
        self.v_line.hide()
        self.h_line.hide()
        self.coord_label.hide()    
        
    def export_png(self):
        """ Saves the current PyQtGraph canvas as a high-resolution image file. """
        if not self.active_curves:
            QMessageBox.warning(self, "No Data", "The graph is empty. Please plot a variable first.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Graph as PNG", "", "PNG Image (*.png)")
        if file_path:
            try:
                # PyQtGraph requires the exporters module to be explicitly imported
                import pyqtgraph.exporters
                exporter = pyqtgraph.exporters.ImageExporter(self.plot_canvas.plotItem)
                
                # Optional: Force a nice, crisp 1920px width for the export
                exporter.parameters()['width'] = 1920 
                
                exporter.export(file_path)
                QMessageBox.information(self, "Success", f"Graph successfully saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"An error occurred while saving the image:\n{str(e)}")

    def export_csv(self):
        """ Extracts the exact data points currently shown on the graph and saves them to a CSV. """
        if not self.active_curves:
            QMessageBox.warning(self, "No Data", "The graph is empty. Please plot a variable first.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Graph Data", "", "CSV Files (*.csv)")
        if not file_path:
            return
            
        import csv
        try:
            headers = ["Time (s)"]
            data_columns = []
            
            # Grab the X-axis (Time) array from the very first active curve
            first_curve = list(self.active_curves.values())[0]
            t_data, _ = first_curve.getData()
            data_columns.append(t_data)
            
            # Grab the Y-axis data for every active curve on the plot
            for curve_id, curve in self.active_curves.items():
                headers.append(curve_id)
                _, y_data = curve.getData()
                data_columns.append(y_data)
                
            # Transpose the columns into horizontal rows for the CSV
            rows = zip(*data_columns)
            
            # Write to file (using European semicolon format to match the main engine)
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(headers)
                
                for row in rows:
                    # Replace dots with commas for European Excel compatibility
                    formatted_row = [f"{val:.6f}".replace('.', ',') for val in row]
                    writer.writerow(formatted_row)
                    
            QMessageBox.information(self, "Success", f"Data successfully exported to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred during export:\n{str(e)}")   
    
    def export_svg(self):
        """ Bypasses the buggy PyQtGraph SVG exporter and uses native Qt6 vector generation! """
        if not self.active_curves:
            QMessageBox.warning(self, "No Data", "The graph is empty. Please plot a variable first.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Graph as SVG", "", "SVG Vector Image (*.svg)")
        if file_path:
            try:
                from PySide6.QtSvg import QSvgGenerator
                from PySide6.QtGui import QPainter
                
                # Initialize the native Qt6 Vector engine
                generator = QSvgGenerator()
                generator.setFileName(file_path)
                
                # Set the SVG resolution to match the exact on-screen aspect ratio
                generator.setSize(self.plot_canvas.size())
                generator.setViewBox(self.plot_canvas.rect())
                generator.setTitle("MBD Telemetry Export")
                
                # Use QPainter to draw the exact PyQtGraph widget directly into the SVG file!
                painter = QPainter()
                painter.begin(generator)
                
                # Render the canvas scene onto the vector painter
                self.plot_canvas.render(painter)
                
                painter.end()
                
                QMessageBox.information(self, "Success", f"Vector Graphic successfully saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"An error occurred while saving the SVG:\n{str(e)}")
            
    def on_mouse_clicked(self, evt):
        """ Toggles the crosshair on and off when the user double-clicks the graph. """
        if evt.double():
            self.crosshair_active = not self.crosshair_active
            
            # If turning off, instantly hide the elements
            if not self.crosshair_active:
                self.v_line.hide()
                self.h_line.hide()
                self.coord_label.hide()

    def mouse_moved(self, evt):
        """ Updates the crosshair and coordinate label if the tracker is active. """
        # Immediately exit if the user has not toggled the tracker on
        if not getattr(self, 'crosshair_active', False):
            return
            
        pos = evt[0]  # Extracts the mouse position
        
        # Check if the mouse is physically inside the plot canvas boundaries
        if self.plot_canvas.sceneBoundingRect().contains(pos):
            
            # Convert screen pixels into mathematical graph coordinates!
            mouse_point = self.plot_canvas.plotItem.vb.mapSceneToView(pos)
            x_val = mouse_point.x()
            y_val = mouse_point.y()
            
            # Move the infinite dashed lines to intersect at the cursor
            self.v_line.setPos(x_val)
            self.h_line.setPos(y_val)
            
            # Update the text label and position it right next to the cursor
            self.coord_label.setText(f"Time (x): {x_val:.4f} s\nValue (y): {y_val:.4f}")
            self.coord_label.setPos(x_val, y_val)
            
            # Ensure the tracking elements are visible
            self.v_line.show()
            self.h_line.show()
            self.coord_label.show()
            
        else:
            # If the user moves the mouse off the graph, hide the tracking UI
            self.v_line.hide()
            self.h_line.hide()
            self.coord_label.hide()      
            
    # ==========================================
    # --- UI & VIEWPORT UTILITIES ---
    # ==========================================
    def fit_all_graphs(self):
        """ Automatically scales the X and Y axes to perfectly fit all plotted curves. """
        self.plot_canvas.enableAutoRange(axis=pg.ViewBox.XYAxes)
        print("Telemetry Viewport: Auto-scaled to Fit All.")

    def apply_theme_icons(self):
        """ 
        Detects Light/Dark mode and loads the corresponding portable SVG icons 
        without relying on hardcoded local paths!
        """
        # 1. Determine if the theme is dark or light based on the actual window color
        bg_color = self.palette().color(QPalette.Window)
        is_dark_theme = bg_color.lightness() < 128
        theme_folder = "dark_ui" if is_dark_theme else "light_ui"

        # 2. Safely locate the 'icons' folder right next to the Python files (supports PyInstaller)
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

        # 3. Apply the icons to the QToolButtons
        for btn_widget, svg_filename in self.icon_mapping.items():
            icon_path = os.path.join(base_dir, "icons", theme_folder, svg_filename)
            
            if os.path.exists(icon_path):
                btn_widget.setIcon(QIcon(icon_path))
                btn_widget.setIconSize(QSize(32, 32)) 
            else:
                print(f"Telemetry Warning: Icon missing at {icon_path}")