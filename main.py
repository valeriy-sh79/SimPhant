# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.1
#  Release Date: 2026/09/30
#  Module: main.py
#  Description:
#     Main entry point for the SimPhant application. Initializes and runs the main window.
#     Serves as the primary application entry point and GUI controller, managing user interactions, 
#     the PyVista 3D viewport, and simulation dispatching.
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

import sys
import os   
import trimesh
import numpy as np
import pyvista as pv
import random

import logging

from pyvistaqt import QtInteractor
from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QVBoxLayout,
                               QTreeWidgetItem, QColorDialog, QInputDialog, QMessageBox,
                               QDialog, QLabel, QPushButton) # <--- Added InputDialog and MessageBox

from ui_main_window import Ui_MainWindow
from unit_rigidbody import RigidBody, MMtoM, DEFAULT_DENSITY
from unit_kinematics import RFrame  
from scipy.spatial.transform import Rotation
from unit_collision import ContactPair

from unit_kinematics import RFrame
from unit_forces import Force, ForceType, ForceFrame  
from unit_joints import Joint, JointType
from unit_solver import MBSolver
from PySide6.QtCore import QTimer, QEvent, Qt, QObject, Signal
from unit_springs import CompressionSpring, TorsionSpring, Bushing 
from unit_project import ProjectManager
from unit_motions import JointMotion, MotionTransRot, MotionType
from math_kernels import warm_up_numba_kernels

APP_NAME = "SimPhant"
APP_MAIN_WINDOW_TITLE = "SimPhant Physics Engine - MBD Simulator"
APP_DESCRIPTION = "Advanced Multibody Dynamics (MBD) Physics Engine & Simulation Environment"
APP_VERSION = "2026.1"
APP_RELEASE_DATE = "2026/09/30"
APP_LICENSE = "GNU General Public License v3.0"
APP_CREDITS_NAME = "Valeriy Shapovalov"
APP_CREDITS_URL = "https://www.linkedin.com/in/valeriy-shapovalov-9762a098/"
APP_SOURCE_REPOSITORY_URL = "https://github.com/valeriy-sh79/SimPhant"
APP_RELEASES_URL = "https://github.com/valeriy-sh79/SimPhant/releases"
APP_ISSUES_URL = "https://github.com/valeriy-sh79/SimPhant/issues"
APP_DOCUMENTATION_SITE_URL = "https://valeriy-sh79.github.io/simphant-docs/"
APP_DOCUMENTATION_REPOSITORY_URL = "https://github.com/valeriy-sh79/simphant-docs"


def get_app_base_dir():
    """Returns the portable application base directory."""
    return getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))


def populate_simphant_info_layout(layout, parent, include_loading=False):
    """Adds the shared SimPhant information block used by About and startup dialogs."""
    logo_label = QLabel(parent)
    logo_label.setAlignment(Qt.AlignCenter)

    logo_path = os.path.join(get_app_base_dir(), "icons", "SimPhant_Logo.svg")
    if os.path.exists(logo_path):
        from PySide6.QtGui import QIcon

        logo_pixmap = QIcon(logo_path).pixmap(150, 150)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setFixedSize(150, 150)

    layout.addWidget(logo_label, alignment=Qt.AlignCenter)

    title_label = QLabel(parent)
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setText(APP_NAME)
    title_label.setStyleSheet("font-size: 18pt;")
    layout.addWidget(title_label)

    text_label = QLabel(parent)
    text_label.setAlignment(Qt.AlignCenter)
    text_label.setWordWrap(True)
    text_label.setText(
        f"{APP_DESCRIPTION}\n\n"
        f"Version: {APP_VERSION}\n"
        f"Release date: {APP_RELEASE_DATE}\n"
        f"License: {APP_LICENSE}"
    )
    layout.addWidget(text_label)

    credits_label = QLabel(parent)
    credits_label.setAlignment(Qt.AlignCenter)
    credits_label.setOpenExternalLinks(True)
    credits_label.setText(
        f'Copyright (C) 2026: <a href="{APP_CREDITS_URL}">{APP_CREDITS_NAME}</a>'
    )
    layout.addWidget(credits_label)

    links_label = QLabel(parent)
    links_label.setAlignment(Qt.AlignCenter)
    links_label.setOpenExternalLinks(True)
    links_label.setWordWrap(True)
    links_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
    links_label.setText(
        f'<a href="{APP_SOURCE_REPOSITORY_URL}">Source code</a> | '
        f'<a href="{APP_RELEASES_URL}">Windows releases</a><br>'
        f'<a href="{APP_DOCUMENTATION_SITE_URL}">Documentation website</a> | '
        f'<a href="{APP_DOCUMENTATION_REPOSITORY_URL}">Documentation source</a><br>'
        f'<a href="{APP_ISSUES_URL}">Issue tracker</a>'
    )
    layout.addWidget(links_label)

    if include_loading:
        loading_label = QLabel(parent)
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setText("Loading.....")
        layout.addWidget(loading_label)


class EmittingStream(QObject):
    """Redirects a stdout/stderr-like stream to both the original console and a Qt signal."""
    text_written = Signal(str)

    def __init__(self, original_stream=None):
        super().__init__()
        self.original_stream = original_stream

    def write(self, text):
        if self.original_stream:
            try:
                self.original_stream.write(text)
            except Exception:
                pass
        if text:
            self.text_written.emit(text)

    def flush(self):
        if self.original_stream:
            try:
                self.original_stream.flush()
            except Exception:
                pass


def create_startup_dialog():
    """Builds the simple startup window shown while the solver kernels warm up."""
    dialog = QDialog()
    dialog.setWindowTitle(f"Starting {APP_NAME}...")
    dialog.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
    dialog.setMinimumWidth(420)

    layout = QVBoxLayout(dialog)

    intro_label = QLabel(dialog)
    intro_label.setAlignment(Qt.AlignCenter)
    intro_path = os.path.join(get_app_base_dir(), "icons", "Intro_Picture.jpg")
    if os.path.exists(intro_path):
        from PySide6.QtGui import QPixmap

        intro_label.setPixmap(QPixmap(intro_path))
    layout.addWidget(intro_label, alignment=Qt.AlignCenter)

    title_label = QLabel(APP_NAME, dialog)
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setStyleSheet("font-size: 18pt;")
    layout.addWidget(title_label)

    description_label = QLabel(APP_DESCRIPTION, dialog)
    description_label.setAlignment(Qt.AlignCenter)
    description_label.setWordWrap(True)
    layout.addWidget(description_label)

    version_label = QLabel(f"Version: {APP_VERSION}", dialog)
    version_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(version_label)
    return dialog

def parse_ui_float(text_value):
    """ 
    Universal float parser that safely handles European ',' and US '.' separators. 
    It strips empty spaces and instantly maps commas to dots before hitting Python's float().
    """
    if not text_value:
        return 0.0
        
    # 1. Convert to string and remove leading/trailing spaces
    clean_str = str(text_value).strip()
    
    # 2. Replace the European comma with a Python-friendly dot
    clean_str = clean_str.replace(',', '.')
    
    # 3. Cast to float (will still raise ValueError if the user typed letters)
    return float(clean_str)
        
class PhysicsEngineMain(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # --- Initialize Project Directories and Logger ---
        self.working_dir = os.getcwd()
        self.output_dir = os.path.join(os.getcwd(), "LogCSV")
        os.makedirs(self.output_dir, exist_ok=True)
        
        log_file = os.path.join(self.output_dir, "debug_log.txt")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            filemode='w' # 'w' overwrites the log every time user restarts the app
        )
        logging.info("Application Started. Physics Engine Initialized.")
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(APP_MAIN_WINDOW_TITLE)

        # Configure dock widget corner ownership so dckProperties reaches the bottom
        # and dckTraceback spans from the left side up to dckProperties.
        self.setCorner(Qt.Corner.BottomRightCorner, Qt.DockWidgetArea.RightDockWidgetArea)
        self.setCorner(Qt.Corner.BottomLeftCorner, Qt.DockWidgetArea.BottomDockWidgetArea)
        QTimer.singleShot(0, self.minimize_traceback_dock)

        # --- Redirect print()/stdout/stderr into the dckTraceback dock (needed for EXE builds without a console) ---
        self._redirect_std_streams_to_traceback()

        base_dir = get_app_base_dir()
        logo_path = os.path.join(base_dir, "icons", "SimPhant_Logo_64x64.ico")
        if os.path.exists(logo_path):
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(logo_path))

        self.viewport_layout = QVBoxLayout(self.ui.viewportWidget)
        self.viewport_layout.setContentsMargins(0, 0, 0, 0)
        
        self.plotter = QtInteractor(self.ui.viewportWidget)
        # Increase rotation sensitivity (Default is 10.0. Try 20.0 to 30.0 for faster rotation)
        self.plotter.iren.get_interactor_style().SetMotionFactor(20.0)
        # Enable hardware anti-aliasing to smooth out jagged pixel edges
        #self.plotter.enable_anti_aliasing('msaa', multi_samples=4) #do not see the difference
        self.viewport_layout.addWidget(self.plotter)
        self.plotter.show_grid(font_size=10)
        self.plotter.add_axes() #(interactive=True, line_width=4)
        # show_message=False removes the default PyVista on-screen text
        self.plotter.enable_mesh_picking(callback=self.on_mesh_picked, show=False, left_clicking=True, show_message=False)
        
        # Build Top-Level Tree Nodes
        self.ui.treeHierarchy.setHeaderLabel("Project Explorer")
        self.node_bodies = QTreeWidgetItem(self.ui.treeHierarchy, ["Rigid Bodies"])
        self.node_rframes = QTreeWidgetItem(self.ui.treeHierarchy, ["Reference Frames"]) # --- RFrames Tree Node ---
        self.node_joints = QTreeWidgetItem(self.ui.treeHierarchy, ["Joints"])
        self.node_forces = QTreeWidgetItem(self.ui.treeHierarchy, ["Forces"]) #Forces & Actuators
        self.node_springs = QTreeWidgetItem(self.ui.treeHierarchy, ["Springs"]) #Springs (& Bushings)
        self.node_bushings = QTreeWidgetItem(self.ui.treeHierarchy, ["Bushings"])
        self.node_contacts = QTreeWidgetItem(self.ui.treeHierarchy, ["Contacts"]) # Contacts Node
        self.node_motions = QTreeWidgetItem(self.ui.treeHierarchy, ["Motions"]) # Motions Tree Node
        self.ui.treeHierarchy.expandAll()

        # Connect UI Signals
        self.ui.treeHierarchy.itemSelectionChanged.connect(self.on_tree_selected)
        
        
        # --- File Menu Connections ---
        # State tracker for direct saving
        self.current_project_file = None
        
        # 1. The new universal topological splitter
        self.ui.actionImport_CAD.triggered.connect(self.import_cad_universal)
        self.ui.actionSetWorkingDir.triggered.connect(self.set_working_directory)
        
        # --- Save, New, Open, and Exit Actions ---
        self.ui.actionNew_Project.triggered.connect(self.new_project)
        self.ui.actionOpen_Project.triggered.connect(self.open_project)
        self.ui.actionSave_Project.triggered.connect(self.save_project)
        self.ui.actionSave_ProjectAs.triggered.connect(self.save_project_as)
        self.ui.actionExit.triggered.connect(self.close)
        if hasattr(self.ui, 'actionAbout_SimPhant'):
            self.ui.actionAbout_SimPhant.triggered.connect(self.show_about_dialog)
        if hasattr(self.ui, 'actionShowTraceback'):
            self.ui.actionShowTraceback.triggered.connect(self.show_traceback_dock)
        
        # 2. Original material-based OBJ splitter
        self.ui.actionImport_OBJ.triggered.connect(self.import_cad_obj_materials)
        
        self.ui.treeHierarchy.itemDoubleClicked.connect(self.on_tree_double_clicked)  
        
        self.ui.btnUpdateBody.clicked.connect(self.update_body_properties)
        self.ui.chkEnabled.toggled.connect(self.toggle_body_enabled)
        self.ui.chkVisible.toggled.connect(self.toggle_body_visible)
        # --- Initial Velocities Connection ---
        self.ui.btnAssignVelocities.clicked.connect(self.assign_initial_velocities)
            
        # --- Gear Creation Button ---
        self.ui.btnCreateGear.clicked.connect(self.create_gear_from_ui)
        self.ui.cmbGearType.currentIndexChanged.connect(self.on_gear_type_changed)
        # Gear Pair Constraint Connections
        self.ui.btnCreateGearPair.clicked.connect(self.create_gear_pair_from_ui)
        self.ui.cmbJointGearType.currentIndexChanged.connect(self.on_joint_gear_type_changed)
        self.ui.btnRenameGearPair.clicked.connect(self.rename_gear_pair)
        self.ui.btnDelGearPair.clicked.connect(self.delete_gear_pair)
        self.ui.chkEnabledGearPair.toggled.connect(self.toggle_gearpair_enabled)
        self.ui.btnUpdateGearPair.clicked.connect(self.update_gear_pair)
        
        self.ui.dsbJointPitchAngle.setVisible(False)
        self.ui.lblJointPitchAngle.setVisible(False)
        
        # --- Gravity UI Connections ---
        self.ui.btnUpdateGravity.clicked.connect(self.update_gravity)
        self.ui.chkEnabledGravity.toggled.connect(self.toggle_gravity_enabled) 
        self.ui.chkVisibleGravity.toggled.connect(self.toggle_gravity_visible)
        
        self.ui.btnColorPicker.clicked.connect(self.change_body_color)
        # Global UI Feature Connections
        
        self.ui.btnColorAllBodies.clicked.connect(self.change_all_bodies_color)
        self.ui.btnRandomColor.clicked.connect(self.apply_random_colors)   
        self.ui.btnUnselectAll.clicked.connect(self.clear_selection)
 
        # --- Update Force UI Connections ---
        self.ui.btnAddForceTorque.clicked.connect(self.add_custom_force)
        self.ui.btnDelForceTorque.clicked.connect(self.delete_custom_force)
        # --- Actuator Toggle ---
        self.ui.chkActuatorMode.toggled.connect(self.ui.frmActuatorSettings.setEnabled)
        
        self.ui.chkEnabledForce.toggled.connect(self.toggle_force_enabled)  
        self.ui.cmbForceType.currentIndexChanged.connect(self.on_force_type_changed)
        self.ui.btnUpdateForceTorque.clicked.connect(self.update_custom_force) 
        self.ui.btnRenameForce.clicked.connect(self.rename_force)
        # --- UI Connections: Forces, Torques, and Actuators ---
        # 0 = Force, 1 = Torque
        self.ui.btnForce.clicked.connect(lambda: self.prepare_new_force(0, is_actuator=False))
        self.ui.btnTorque.clicked.connect(lambda: self.prepare_new_force(1, is_actuator=False))
        self.ui.Edit_ForceValue.textChanged.connect(self.validate_force_expression)
        # --- Live UI check for Kinematic Motions ---
        self.ui.Edit_MotionFunction.textChanged.connect(self.validate_motion_expression)
        
        # New buttons: Pass the same type_idx, but set is_actuator to True!
        self.ui.btnActuator.clicked.connect(lambda: self.prepare_new_force(0, is_actuator=True))
        self.ui.btnEmotor.clicked.connect(lambda: self.prepare_new_force(1, is_actuator=True))
        
        # --- Joint UI Connections ---
        self.ui.btnCleanBodiesRFs.clicked.connect(self.clean_joint_rfs_bodies) 
        self.ui.btnAddJoint.clicked.connect(self.add_custom_joint)
        self.ui.btnDelJoint.clicked.connect(self.delete_custom_joint)
        self.ui.chkEnabledJoint.toggled.connect(self.toggle_joint_enabled)
        self.ui.btnRenameJoint.clicked.connect(self.rename_joint)
        
        # --- Smart Joint Creation Buttons ---
        self.ui.btnFixedJt.clicked.connect(lambda: self.prepare_new_joint(0))
        self.ui.btnSphericalJt.clicked.connect(lambda: self.prepare_new_joint(1))
        self.ui.btnRevoluteJt.clicked.connect(lambda: self.prepare_new_joint(2))
        self.ui.btnCylindricalJt.clicked.connect(lambda: self.prepare_new_joint(3))
        self.ui.btnPrismaticJt.clicked.connect(lambda: self.prepare_new_joint(4))
        self.ui.btnPlanarJt.clicked.connect(lambda: self.prepare_new_joint(5))

        # --- Joint Motion Creation Buttons ---
        self.ui.btnTranslMotion.clicked.connect(lambda: self.prepare_new_motion(0))
        self.ui.btnRotMotion.clicked.connect(lambda: self.prepare_new_motion(1))
        self.ui.cmbMotionTransRot.currentIndexChanged.connect(self.on_motion_trans_rot_changed)
        self.ui.cmbMotionType.currentIndexChanged.connect(self.on_motion_trans_rot_changed)
        
        # --- UI Connections: Kinematic Motions ---
        self.ui.btnAddMotion.clicked.connect(self.add_motion)
        self.ui.btnUpdateMotion.clicked.connect(self.update_motion)
        self.ui.btnDelMotion.clicked.connect(self.delete_motion)
        self.ui.btnRenameMotion.clicked.connect(self.rename_motion)
        self.ui.chkEnabledMotion.toggled.connect(self.toggle_motion_enabled)
        
        # --- UI Button Connections ---
        self.ui.btnSolve.clicked.connect(self.run_physics_simulation)  
        # --- Break Solving Button ---
        if hasattr(self.ui, 'btnBreakSolving'):
            self.ui.btnBreakSolving.clicked.connect(self.cancel_simulation) 
        # --- Connect the Optional CSV Export Button ---
        self.ui.btnExportCSV.clicked.connect(self.export_csv_results)
        self.ui.btnTelemetry.clicked.connect(self.open_telemetry_window)
        # --- Dynamic Solver Settings UI ---
        self.ui.cmbSolverMethod.currentIndexChanged.connect(self.on_solver_method_changed)
        self.on_solver_method_changed(self.ui.cmbSolverMethod.currentIndex()) # Initialize state
        
        self.ui.progressBar.setValue(0)
        
        self.ui.btnBody.clicked.connect(self.show_body_page)
        self.ui.btnRF.clicked.connect(self.show_RF_page)
        self.ui.btnBoolean.clicked.connect(self.show_Boolean_page)
        self.ui.btnCleanBoolBodies.clicked.connect(self.clean_boolean_body_fields)
        self.ui.btnUniteBodies.clicked.connect(self.unite_bodies_from_ui)
        
        
        self.ui.btnHelicalGear.clicked.connect(lambda: self.prepare_new_gear(0))
        self.ui.btnInnerGear.clicked.connect(lambda: self.prepare_new_gear(1))
        self.ui.btnBevelGear.clicked.connect(lambda: self.prepare_new_gear(2))
        
        self.ui.btnBox.clicked.connect(lambda: self.prepare_new_primitive(0))
        self.ui.btnTube.clicked.connect(lambda: self.prepare_new_primitive(1))
        self.ui.btnSphere.clicked.connect(lambda: self.prepare_new_primitive(2))
        self.ui.btnPrism.clicked.connect(lambda: self.prepare_new_primitive(3))
        self.ui.btnTorus.clicked.connect(lambda: self.prepare_new_primitive(4))
        self.ui.btnCone.clicked.connect(lambda: self.prepare_new_primitive(5))
        self.ui.btnLink.clicked.connect(lambda: self.prepare_new_primitive(6))
        
        
        self.ui.btnGearJoint.clicked.connect(self.show_GearJoint_page)
        # --- Primitives Generator Connection ---
        if hasattr(self.ui, 'btnCreatePrimitive'):
            self.ui.btnCreatePrimitive.clicked.connect(self.create_primitive_from_ui)
        # --- Hook up the dynamic dimension labels! ---
        if hasattr(self.ui, 'cmbPrimitiveType'):
            self.ui.cmbPrimitiveType.currentIndexChanged.connect(self.on_primitive_type_changed)
            
        # --- UI Connections: Compression Springs ---
        self.ui.btnAddCompSpring.clicked.connect(self.add_comp_spring)
        self.ui.btnUpdateCompSpring.clicked.connect(self.update_comp_spring)
        self.ui.btnDelCompSpring.clicked.connect(self.delete_comp_spring)
        self.ui.btnComprSpring.clicked.connect(self.prepare_new_comp_spring)
        self.ui.btnRenameCompSpring.clicked.connect(self.rename_comp_spring)
        self.ui.chkEnabledCompSpring.toggled.connect(self.toggle_comp_spring_enabled)

        # --- UI Connections: Torsion Springs ---
        self.ui.btnAddTorsSpring.clicked.connect(self.add_tors_spring)
        self.ui.btnUpdateTorsSpring.clicked.connect(self.update_tors_spring)
        self.ui.btnDelTorsSpring.clicked.connect(self.delete_tors_spring)
        self.ui.btnTorsionSpring.clicked.connect(self.prepare_new_tors_spring)
        self.ui.btnRenameTorsSpring.clicked.connect(self.rename_tors_spring)
        self.ui.chkEnabledTorsSpring.toggled.connect(self.toggle_tors_spring_enabled)
       
       # --- UI Connections: Contacts ---
        self.ui.btnAddContact.clicked.connect(self.add_contact)
        self.ui.btnUpdateContact.clicked.connect(self.update_contact)
        self.ui.btnDelContact.clicked.connect(self.delete_contact)
        self.ui.btnContact.clicked.connect(self.prepare_new_contact)
        self.ui.btnRenameContact.clicked.connect(self.rename_contact)
        self.ui.chkEnabledContact.toggled.connect(self.toggle_contact_enabled)
        
        # --- Toggle Friction Frame ---
        self.ui.chkContactFriction.toggled.connect(self.ui.frmContactFriction.setEnabled)
        
        # Optional: Connect the spinbox to update the label dynamically
        # self.ui.dsbForceExponent.valueChanged.connect(self.update_contact_unit_label) # Just write 'N/mm^e'
    
        self.ui.btnForce.clicked.connect(self.show_Force_page)
        self.ui.btnTorque.clicked.connect(self.show_Force_page)
        self.ui.btnSimulation.clicked.connect(self.show_Simulation_page)
        
        # --- Animation & Playback Variables ---
        self.playback_timer = QTimer(self)
        self.playback_timer.timeout.connect(self.on_playback_tick)
        self.playback_time = 0.0
        self.simulation_dt = 0.01 # Will be overwritten by the Solver
        
        # --- Animation UI Connections ---
        self.ui.btnRunAnimation.clicked.connect(self.run_animation)
        self.ui.btnPauseAnimation.clicked.connect(self.pause_animation)
        self.ui.btnStopAnimation.clicked.connect(self.stop_animation)
        self.ui.hslAnimSpeed.valueChanged.connect(self.update_speed_label)
        # --- Video Export Connection ---
        if hasattr(self.ui, 'btnExportVideo'):
            self.ui.btnExportVideo.clicked.connect(self.export_video)
        # --- Step Forward / Backward Connections ---
        self.ui.btnStepForward.clicked.connect(self.step_forward_animation)
        self.ui.btnStepBackward.clicked.connect(self.step_backward_animation)
        
        # --- Lock playback controls until a solve is complete! ---
        self.ui.btnRunAnimation.setEnabled(False)
        self.ui.btnPauseAnimation.setEnabled(False)
        self.ui.btnStopAnimation.setEnabled(False)
        self.ui.btnStepForward.setEnabled(False)   
        self.ui.btnStepBackward.setEnabled(False)  
        
        # self.ui.btnRenameBody.clicked.connect(self.rename_body)    
           
        # Initialize default label
        self.update_speed_label(self.ui.hslAnimSpeed.value())
           
        # Engine Memory
        self.physics_bodies = {}    
        self.rframes = []           # --- RFrame Array ---
        # --- Internal Engine State for Gravity ---
        self.global_gravity = np.array([0.0, -9.81, 0.0])
        
        self.forces_list = []       # --- Forces Array ---
        # self.joint_base_size = 50.0 # --- UI Scale reference for arrows/joints ---
        # --- Add to Engine Memory variables ---
        self.joints_list = []
        self.springs_list = []
        self.contact_pairs = [] # Store our explicit contact pairs!
        self.selected_joint = None       
        self.body_counter = 0       
        self.selected_body = None   
        self.selected_rframe = None # Tracks the currently active RFrame
        self.selected_force = None # Tracks the currently active Force/Torque
        
        self.gear_pairs_list = []
        self.bushings_list = [] 
        # --- Motions Array ---
        self.motions_list = []
        self.selected_motion = None
        
        # --- UI Connections: Bushings ---
        self.ui.btnAddBushing.clicked.connect(self.add_bushing)
        self.ui.btnUpdateBushing.clicked.connect(self.update_bushing)
        self.ui.btnDelBushing.clicked.connect(self.delete_bushing)
        self.ui.btnBushing.clicked.connect(self.prepare_new_bushing) 
        self.ui.btnRenameBushing.clicked.connect(self.rename_bushing)
        self.ui.chkEnabledBushing.toggled.connect(self.toggle_bushing_enabled)
        
        self.ui.lbl_Bushing_RFBodyJ.hide() # Hide the label for now, unless Bushing with 2 RFs is properly tested
        self.ui.Edit_RFBodyJ_Bushing.hide() # Hide the input field for now, unless Bushing with 2 RFs is properly tested

        # --- Viewport State Trackers ---
        self.edges_visible = False
        self.grid_visible = True
        self.bg_is_light = True

        # --- UPDATE: Global UI Feature Connections ---
        self.ui.btnEdges.clicked.connect(self.toggle_all_edges)
        self.ui.btnGrid.clicked.connect(self.toggle_grid)
        self.ui.btnUnhideAll.clicked.connect(self.unhide_all)
        self.ui.btnHideAllExceptSelected.clicked.connect(self.hide_all_except_selected)
        self.ui.btnBackgroundTheme.clicked.connect(self.toggle_background)
        if hasattr(self.ui, 'btnXY_view'):
            self.ui.btnXY_view.clicked.connect(self.set_xy_view)
        if hasattr(self.ui, 'btnZY_view'):
            self.ui.btnZY_view.clicked.connect(self.set_zy_view)
        if hasattr(self.ui, 'btnXZ_view'):
            self.ui.btnXZ_view.clicked.connect(self.set_xz_view)
        # --- Connect the Checkable Toggle Button ---
        self.ui.btnHideShowObjects.toggled.connect(self.toggle_auxiliary_objects)
        # --- VIEWPORT UI CONNECTIONS ---
        if hasattr(self.ui, 'btnProjection'):
            self.ui.btnProjection.clicked.connect(self.toggle_projection)
        self.ui.btnRenameBody.clicked.connect(self.rename_body)    
           
        if hasattr(self.ui, 'btnFitAll'):
            self.ui.btnFitAll.clicked.connect(self.fit_all_camera)
        if hasattr(self.ui, 'btnDeleteBody'):
            self.ui.btnDeleteBody.clicked.connect(self.delete_body)
        if hasattr(self.ui, 'btnCopyBody'):
            self.ui.btnCopyBody.clicked.connect(self.copy_body)    
        # Force a scale calculation the instant auto-scaling is re-enabled
        if hasattr(self.ui, 'btnScaleVisuals'):
            self.ui.btnScaleVisuals.toggled.connect(lambda checked: self.update_rframe_scales() if not checked else None)
        # --- RFrames Button Connections ---
        self.ui.btnAddUpdateRF.clicked.connect(self.add_rf)       # Creates a new auto-named RF
        self.ui.btnUpdateRF.clicked.connect(self.update_rf)       # Updates existing
        self.ui.btnRenameRF.clicked.connect(self.rename_rf)       # Renames existing
        self.ui.btnDeleteRF.clicked.connect(self.delete_rf)       # Deletes existing
        
        self.ui.btnShiftRF.clicked.connect(self.shift_rf)
        self.ui.btnRotateRF.clicked.connect(self.rotate_rf)
        self.ui.dsbShift_RF.setRange(-500.0, 500.0) 
        self.ui.dsbRotate_RF.setRange(-500.0, 500.0)
        self.ui.dsbHelixAngle.setRange(-45.0, 45.0)
        
        # Keep the existing color buttons...
        self.ui.btnRandomColor.clicked.connect(self.apply_random_colors)
        
        # --- Create the Universal Ground Body ---
        ground_tree_item = QTreeWidgetItem(self.node_bodies, ["Ground"])
        ground_body = RigidBody(
            name="Ground", 
            raw_geom=None, block_mesh=None, actor=None, 
            tree_item=ground_tree_item, density=0.0, is_ground=True
        )
        self.physics_bodies["Ground"] = ground_body

        # Parallel projection in the Viewport is often preferred for engineering applications to avoid perspective distortion.
        self.plotter.enable_parallel_projection()
        # self.plotter.disable_parallel_projection()
        
        # --- Create Global Reference Frame (Index 0) ---
        global_rf = RFrame(
            name="Global_RF", 
            position=[0, 0, 0], 
            orientation=[0, 0, 0], 
            transform_matrix=np.eye(3), 
            plotter=self.plotter, 
            parent_body=ground_body, # <--- Bind to Ground
            is_cog=False # <------------- To check if we need to have TRUE here ----------------
        )
        self.rframes.append(global_rf)
        QTreeWidgetItem(self.node_rframes, ["Global_RF"])
        
        # --- Hook Camera Events for Constant Pixel Sizing ---
        # This calls update_rframe_scales() anytime the user pans, zooms, or rotates the viewport!
        self.plotter.camera.AddObserver("ModifiedEvent", self.update_rframe_scales)
        
        # Set iitial background color at start
        self.plotter.set_background('lightgray')
        
        # ==========================================
        # --- ICON MANAGEMENT ---
        # ==========================================
        self._current_theme_folder = None
        self._theme_refresh_pending = False

        # Map the UI buttons to their exact SVG filenames
        self.icon_mapping = {
            self.ui.btnFixedJt: "Slide1.svg",
            self.ui.btnSphericalJt: "Slide2.svg",
            self.ui.btnRevoluteJt: "Slide3.svg",
            self.ui.btnCylindricalJt: "Slide4.svg",
            self.ui.btnPrismaticJt: "Slide5.svg",
            self.ui.btnPlanarJt: "Slide6.svg",
            self.ui.btnBody: "Slide7.svg",
            self.ui.btnRF: "Slide8.svg",
            self.ui.btnHelicalGear: "Slide9.svg",
            self.ui.btnInnerGear: "Slide10.svg",
            self.ui.btnBevelGear: "Slide11.svg",
            self.ui.btnGearJoint: "Slide12.svg",
            self.ui.btnBox: "Slide13.svg",
            self.ui.btnTube: "Slide14.svg",
            self.ui.btnSphere: "Slide15.svg",
            self.ui.btnPrism: "Slide16.svg",
            self.ui.btnTorus: "Slide17.svg",
            self.ui.btnCone: "Slide18.svg",
            self.ui.btnLink: "Slide19.svg",
            self.ui.btnForce: "Slide20.svg",
            self.ui.btnTorque: "Slide21.svg",
            self.ui.btnActuator: "Slide22.svg",
            self.ui.btnEmotor: "Slide23.svg",
            self.ui.btnContact: "Slide24.svg",
            self.ui.btnComprSpring: "Slide25.svg",
            self.ui.btnTorsionSpring: "Slide26.svg",
            self.ui.btnBushing: "Slide27.svg",
            self.ui.btnTranslMotion: "Slide28.svg",
            self.ui.btnRotMotion: "Slide29.svg",
            self.ui.btnSimulation: "Slide30.svg",
            self.ui.btnSolve: "Slide31.svg",
            self.ui.btnTelemetry: "Slide32.svg",
            self.ui.btnExportCSV: "Slide33.svg",
            self.ui.btnFitAll: "Slide34.svg",
            self.ui.btnGrid: "Slide35.svg",
            self.ui.btnEdges: "Slide36.svg",
            self.ui.btnHideAllExceptSelected: "Slide37.svg",
            self.ui.btnUnhideAll: "Slide38.svg",
            self.ui.btnBackgroundTheme: "Slide39.svg",
            self.ui.btnProjection: "Slide40.svg",
            self.ui.btnUnselectAll: "Slide41.svg",
            self.ui.btnHideShowObjects: "Slide42.svg",
            self.ui.btnExportVideo: "Slide43.svg",
            self.ui.btnScaleVisuals: "Slide49.svg",
            self.ui.btnBreakSolving: "Slide50.svg",
            self.ui.btnBoolean: "Slide51.svg",
            self.ui.btnXY_view: "Slide52.svg",
            self.ui.btnZY_view: "Slide53.svg",
            self.ui.btnXZ_view: "Slide54.svg",

        }
        self._install_theme_change_hooks()
        # Apply the icons based on the OS startup theme
        self.apply_theme_icons()   
         
    def new_project(self):
        """ Safely clears the scene for a new project, prompting to save first. """
        if not self.prompt_to_save_changes(): return
            
        self.clear_scene_for_loading()
        self.current_project_file = None
        self.setWindowTitle(APP_MAIN_WINDOW_TITLE)
        
        # Reset default UI settings
        self.ui.Edit_GravityX.setText("0.0")
        self.ui.Edit_GravityY.setText("-9.81")
        self.ui.Edit_GravityZ.setText("0.0")
        self.update_gravity()
        print("New project created.")

    def open_project(self):
        """ Safely opens a project, prompting to save current work first. """
        if not self.prompt_to_save_changes(): return
            
        file_filter = "MBD Project (*.mbd);;All Files (*)"
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Project", self.working_dir, file_filter)
        if filepath:
            self.clear_scene_for_loading()
            ProjectManager.load_project(self, filepath)
            
            # --- Extract the saved gravity vector from the loaded project! ---
            for force in self.forces_list:
                if getattr(force, 'is_gravity', False):
                    self.global_gravity = force.base_vector.copy()
                    break
                
            # Save state and update Window Title
            self.current_project_file = filepath
            self.setWindowTitle(f"SimPhant Physics Engine - {os.path.basename(filepath)}")
            
            self.update_rframe_scales() 
            self.ui.btnHideShowObjects.setChecked(False)

    def save_project(self):
        """ Saves directly to the active file. If no file is active, triggers Save As. """
        if not self.current_project_file:
            return self.save_project_as()
        else:
            # --- THE FIX: Rewind the visuals to t=0, but DO NOT delete the solver! ---
            if hasattr(self, 'playback_timer'):
                self.playback_time = 0.0
                self.render_playback_frame()
                
            ProjectManager.save_project(self, self.current_project_file)
            return True

    def save_project_as(self):
        """ Opens a dialog to define a new save location. """
        
        # --- THE FIX: Rewind the visuals to t=0, but DO NOT delete the solver! ---
        if hasattr(self, 'playback_timer'):
            self.playback_time = 0.0
            self.render_playback_frame()
            
        file_filter = "MBD Project (*.mbd);;All Files (*)"
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Project As", self.working_dir, file_filter)
        if filepath:
            if not filepath.endswith('.mbd'): filepath += '.mbd'
            ProjectManager.save_project(self, filepath)
            
            # Save state and update Window Title
            self.current_project_file = filepath
            self.setWindowTitle(f"SimPhant Physics Engine - {os.path.basename(filepath)}")
            return True
            
        return False # User cancelled the dialog
    
    def update_rframe_scales(self, *args):
        """ Dynamically scales RFrames, Forces, Springs, and Bushings to keep a constant screen size. """
        
        # If the user checked the 'btnScaleVisuals' button, lock the scaling immediately!
        if hasattr(self.ui, 'btnScaleVisuals') and self.ui.btnScaleVisuals.isChecked():
            return        
        
        if not hasattr(self, 'plotter') or not self.plotter.camera:
            return

        camera = self.plotter.camera
        import numpy as np
        import math
        
        # ==========================================
        # --- THE UNIFIED SCALING MATH ---
        # ==========================================
        if camera.GetParallelProjection():
            # In Orthographic mode, ParallelScale is exactly the half-height of the viewport.
            viewport_half_height = camera.GetParallelScale()
        else:
            # In Perspective mode, we use trigonometry to calculate the exact 
            # mathematical half-height at the focal point using the Camera's View Angle!
            distance = np.linalg.norm(np.array(camera.position) - np.array(camera.focal_point))
            view_angle_rad = math.radians(camera.GetViewAngle())
            viewport_half_height = distance * math.tan(view_angle_rad / 2.0)

        # Now BOTH modes share the exact same scale basis!
        # Tune this single multiplier (e.g., 0.15) to adjust the size of the arrows for the whole app.
        # Define the Reference Frames Arrows size here!
        base_scale = viewport_half_height * 0.15 

        # ==========================================
        # --- THE PERFORMANCE FIX: SMART CACHE ---
        # ==========================================
        # If the scale hasn't changed (e.g., the user is just rotating or panning), 
        # instantly abort to save massive CPU/GPU resources!
        if hasattr(self, '_last_base_scale') and abs(self._last_base_scale - base_scale) < 1e-6:
            return
            
        # Update the memory with the new scale
        self._last_base_scale = base_scale


        # 1. Update RFrames
        for rf in getattr(self, 'rframes', []):
            rf.set_scale(base_scale)
            
        # 2. Update Forces
        for force in getattr(self, 'forces_list', []):
            if hasattr(force, 'update_transform'):
                force.update_transform(base_scale, t=0.0)
                
        # 3. Update Springs
        for spring in getattr(self, 'springs_list', []):
            if hasattr(spring, 'update_transform'):
                spring.update_transform(base_scale)
                
        # 4. Update Bushings
        for bushing in getattr(self, 'bushings_list', []):
            if hasattr(bushing, 'update_transform'):
                bushing.update_transform(base_scale)

        # 5. Update Joints
        for joint in getattr(self, 'joints_list', []):
            if hasattr(joint, 'update_transform'):
                joint.update_transform(base_scale)
                

    def apply_theme_icons(self):
        """ 
        Detects if the OS/App is currently using a Dark or Light theme, 
        and safely loads the portable icons without hardcoded local paths.
        """
        from PySide6.QtGui import QIcon
        from PySide6.QtCore import QSize
        import os

        theme_folder = self._get_theme_folder()
        if theme_folder == self._current_theme_folder:
            return

        # 1. Calculate the portable base directory (where main.py lives, supports PyInstaller)
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

        # 2. Loop through the dictionary and apply the icons!
        for btn_widget, svg_filename in self.icon_mapping.items():
            # Build the safe, portable path: e.g., ".../Project/icons/dark_ui/box.svg"
            icon_path = os.path.join(base_dir, "icons", theme_folder, svg_filename)
            
            if os.path.exists(icon_path):
                btn_widget.setIcon(QIcon(icon_path))
                btn_widget.setIconSize(QSize(40, 40)) # Adjust size (24x24 or 32x32) as needed
            else:
                print(f"Warning: Icon missing at {icon_path}")

        self._current_theme_folder = theme_folder

    def _get_theme_folder(self):
        """Returns the icon folder that matches the live Windows/Qt color scheme."""
        app = QApplication.instance()
        if app is not None:
            style_hints = app.styleHints()
            if style_hints is not None and hasattr(style_hints, 'colorScheme'):
                try:
                    color_scheme = style_hints.colorScheme()
                    if color_scheme == Qt.ColorScheme.Dark:
                        return "dark_ui"
                    if color_scheme == Qt.ColorScheme.Light:
                        return "light_ui"
                except Exception:
                    pass

        from PySide6.QtGui import QPalette

        bg_color = self.palette().color(QPalette.Window)
        return "dark_ui" if bg_color.lightness() < 128 else "light_ui"

    def _install_theme_change_hooks(self):
        """Subscribes to Qt theme notifications so icons follow live Windows theme changes."""
        app = QApplication.instance()
        if app is None:
            return

        style_hints = app.styleHints()
        if style_hints is not None and hasattr(style_hints, 'colorSchemeChanged'):
            try:
                style_hints.colorSchemeChanged.connect(self.schedule_theme_icon_refresh)
            except (RuntimeError, TypeError):
                pass

    def schedule_theme_icon_refresh(self, *args):
        """Defers icon refresh until Qt finishes processing the theme transition."""
        if self._theme_refresh_pending:
            return

        self._theme_refresh_pending = True
        QTimer.singleShot(0, self._refresh_theme_icons)

    def _refresh_theme_icons(self):
        """Refreshes theme-sensitive icons after a palette or system theme change."""
        self._theme_refresh_pending = False
        self.apply_theme_icons()

    def changeEvent(self, event):
        """Refreshes theme-dependent UI when Windows or Qt updates the color scheme."""
        if event.type() in (
            QEvent.PaletteChange,
            QEvent.ApplicationPaletteChange,
            QEvent.ThemeChange,
            QEvent.StyleChange,
        ):
            self.schedule_theme_icon_refresh()

        super().changeEvent(event)

    def minimize_traceback_dock(self):
        """Resizes dckTraceback to its minimal height immediately."""
        if hasattr(self.ui, 'dckTraceback'):
            self.resizeDocks([self.ui.dckTraceback], [1], Qt.Orientation.Vertical)

    def show_traceback_dock(self):
        """Shows the Traceback dock widget if it was hidden or closed."""
        if hasattr(self.ui, 'dckTraceback'):
            self.ui.dckTraceback.show()
            self.ui.dckTraceback.raise_()

    def _redirect_std_streams_to_traceback(self):
        """Mirrors all stdout/stderr output (print statements, tracebacks) into the txbTraceback widget."""
        self._stdout_original = sys.stdout
        self._stderr_original = sys.stderr

        self._stdout_stream = EmittingStream(self._stdout_original)
        self._stderr_stream = EmittingStream(self._stderr_original)
        self._stdout_stream.text_written.connect(self._append_traceback_text)
        self._stderr_stream.text_written.connect(self._append_traceback_text)

        sys.stdout = self._stdout_stream
        sys.stderr = self._stderr_stream

    def _restore_std_streams(self):
        """Restores the original stdout/stderr streams captured before redirection."""
        if hasattr(self, '_stdout_original'):
            sys.stdout = self._stdout_original
        if hasattr(self, '_stderr_original'):
            sys.stderr = self._stderr_original

    def _append_traceback_text(self, text):
        """Appends redirected stdout/stderr text to the end of the Traceback dock."""
        if not hasattr(self.ui, 'txbTraceback'):
            return
        cursor = self.ui.txbTraceback.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.ui.txbTraceback.setTextCursor(cursor)
        self.ui.txbTraceback.insertPlainText(text)
        self.ui.txbTraceback.ensureCursorVisible()

    def showEvent(self, event):
        """Ensures dckTraceback resizes to its minimal height on display."""
        super().showEvent(event)
        QTimer.singleShot(0, self.minimize_traceback_dock)

    def clear_scene_for_loading(self):
        """ Safely purges all memory and 3D actors to prepare for a new file. """
        self.clear_selection()
        
        # 1. Remove all 3D Actors from the Viewport
        for b in self.physics_bodies.values():
            if not b.is_ground and b.actor: self.plotter.remove_actor(b.actor)
        for r in self.rframes:
            if r.name != "Global_RF":
                for act in r.actors: self.plotter.remove_actor(act)
        for lst in [self.forces_list, self.joints_list, getattr(self, 'springs_list', []), getattr(self, 'bushings_list', [])]:
            for item in lst:
                for act in item.actors: self.plotter.remove_actor(act)
                
        # 2. Reset Engine Memory (Keep Ground and Global_RF)
        self.physics_bodies = {"Ground": self.physics_bodies["Ground"]}
        self.rframes = [self.rframes[0]]
        self.forces_list.clear()
        self.joints_list.clear()
        if hasattr(self, 'springs_list'): self.springs_list.clear()
        if hasattr(self, 'bushings_list'): self.bushings_list.clear()
        if hasattr(self, 'contact_pairs'): self.contact_pairs.clear()
        # --- Purge Motions memory! ---
        if hasattr(self, 'motions_list'): self.motions_list.clear()
        self.selected_motion = None
        # --- Purge the Gear memory! ---
        if hasattr(self, 'gear_pairs_list'): self.gear_pairs_list.clear() 
        # ---------------------------------------
        self.body_counter = 0
        
        # 3. Clear Tree Hierarchy UI
        # --- Add node_gear_pairs to the UI wipe list! ---
        for node in [self.node_bodies, self.node_rframes, self.node_joints, 
                     self.node_forces, self.node_springs, getattr(self, 'node_bushings', None), 
                     getattr(self, 'node_contacts', None), getattr(self, 'node_gear_pairs', None),
                     getattr(self, 'node_motions', None)]: # <--- Added node_motions
            if node: node.takeChildren()
        
        # --- Re-insert Ground and Global_RF into the UI Tree! ---
        from PySide6.QtWidgets import QTreeWidgetItem
        ground_tree_item = QTreeWidgetItem(self.node_bodies, ["Ground"])
        self.physics_bodies["Ground"].tree_item = ground_tree_item
        QTreeWidgetItem(self.node_rframes, ["Global_RF"])
        
        # ==========================================
        # --- Lock Playback UI on clear ---
        # ==========================================
        self.playback_time = 0.0
        self.ui.lblAnimationTime.setText("Time: 0.000 s")
        self.ui.btnRunAnimation.setEnabled(False)
        self.ui.btnPauseAnimation.setEnabled(False)
        self.ui.btnStopAnimation.setEnabled(False)
        self.ui.btnStepForward.setEnabled(False)   
        self.ui.btnStepBackward.setEnabled(False)
        
        # --- Lock CSV Export and tracking flag! ---
        if hasattr(self.ui, 'btnExportCSV'):
            self.ui.btnExportCSV.setEnabled(False)
            self.ui.btnTelemetry.setEnabled(True)
        self._results_were_valid = False
            
        self.plotter.render()
        print("Scene cleared.")
        
    def set_working_directory(self):
        """ Allows the user to define where imports, CSVs, and default saves are stored. """
        dir_path = QFileDialog.getExistingDirectory(self, "Select Working Directory", self.working_dir)
        if dir_path:
            self.working_dir = dir_path
            self.output_dir = os.path.join(self.working_dir, "LogCSV")
            os.makedirs(self.output_dir, exist_ok=True)
            print(f"Working directory updated to: {self.working_dir}")

    def show_about_dialog(self):
        """Displays the About SimPhant window with logo and program metadata."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"About {APP_NAME}")
        dialog.setModal(True)
        dialog.setMinimumWidth(420)

        layout = QVBoxLayout(dialog)
        populate_simphant_info_layout(layout, dialog)
        
        # ----- Close button
        close_button = QPushButton("OK", dialog)
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

        dialog.exec()

    def _get_existing_working_dir(self):
        """Returns a valid starting directory for file dialogs."""
        if self.working_dir and os.path.exists(self.working_dir):
            return self.working_dir
        return os.getcwd()
    
    def prompt_to_save_changes(self):
        """ Prompts the user to save changes. Returns False if user cancels the operation. """
        if self.body_counter == 0:
            return True # Nothing to save
            
        reply = QMessageBox.question(self, 'Save Project?',
                                     "Do you want to save the current project before proceeding?",
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                                     
        if reply == QMessageBox.Cancel:
            return False
        elif reply == QMessageBox.Yes:
            return self.save_project() # Returns False if they cancel the 'Save As' dialog!
        
        return True # User chose 'No', proceed anyway

    def closeEvent(self, event):
        """ Intercepts the application closure to prevent accidental data loss. """
        if self.prompt_to_save_changes():
            self._restore_std_streams()
            event.accept()
        else:
            event.ignore()
            
    def import_cad_obj_materials(self):
        """ Option 2: The original Fake Material Injection parser for complex assemblies. """
        default_dir = self._get_existing_working_dir()
            
        file_filter = "OBJ Files (*.obj);;All Files (*)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Import OBJ (Material Split)", default_dir, file_filter)
        if not file_path: return

        import tempfile
        try:
            original_cad_name = os.path.splitext(os.path.basename(file_path))[0]
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            new_lines = []
            group_count = 0

            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('g ') or stripped.startswith('o '):
                    group_count += 1
                    new_lines.append(line)
                    next_line = lines[i+1].strip() if i+1 < len(lines) else ""
                    if not next_line.startswith('usemtl'):
                        new_lines.append(f"usemtl CADForceSplit_{group_count}\n")
                elif stripped.startswith('usemtl'):
                    if group_count == 0: group_count += 1
                    new_lines.append(f"usemtl CADForceSplit_{group_count}\n")
                else:
                    new_lines.append(line)

            temp_file_path = os.path.join(tempfile.gettempdir(), 'CAD_temp_assembly.obj')
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            # Load the scene and extract the list of meshes
            scene = trimesh.load(temp_file_path, force='scene')
            meshes_list = list(scene.geometry.values())
            
            # --- Pass to the Master Pipeline! ---
            self._process_imported_meshes(meshes_list, original_cad_name)

            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        except Exception as e:
            print(f"Error loading OBJ file: {e}")

    def import_cad_universal(self):
        """ Option 1: Universal Topological Splitter for STL, PLY, and generic OBJ files. """
        # .obj and .ply files do not work here :(
        default_dir = self._get_existing_working_dir()
            
        file_filter = "CAD Files (*.stl);;All Files (*)" # .obj and .ply files do not work here :(
        file_path, _ = QFileDialog.getOpenFileName(self, "Import CAD (*.stl)", default_dir, file_filter)      
        if not file_path: return

        try:
            original_cad_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # 1. Force the file to load as a single, flattened mesh
            loaded_mesh = trimesh.load(file_path, force='mesh')
            
            # 2. Split the mesh mathematically based on vertex connectivity
            split_meshes = loaded_mesh.split(only_watertight=False)
            
            # --- Pass to the Master Pipeline! ---
            self._process_imported_meshes(split_meshes, original_cad_name)
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import CAD file:\n{str(e)}")
            import traceback
            traceback.print_exc()
            
    def _process_imported_meshes(self, meshes_list, original_cad_name="Assembly"):
        """ Unified pipeline to wrap trimesh objects, create bodies, RFrames, and Gravity. """
        blocks_processed = 0

        for geom in meshes_list:
            # 1. Pad faces for PyVista (Insert the number 3 at the start of every triangle array)
            faces_padded = np.insert(geom.faces, 0, 3, axis=1)
            block_mesh = pv.PolyData(geom.vertices, faces_padded.flatten())

            if block_mesh.n_points == 0:
                continue

            # --- THE FIX: Weld disconnected vertices and compute crisp CAD lighting normals! ---
            # This is to avoid extra shadows around all edges
            block_mesh = block_mesh.clean().compute_normals(split_vertices=True, feature_angle=60)
            # ---------------------------------------------------------------------------------
            
            # 2. Setup names and 3D viewport actors
            self.body_counter += 1
            body_name = f"Body_{self.body_counter}"
            
            actor = self.plotter.add_mesh(block_mesh, color="slategray", 
                                          show_edges=self.edges_visible, 
                                          pickable=True, smooth_shading=True)
            
            tree_item = QTreeWidgetItem(self.node_bodies, [body_name])

            # 3. Instantiate the RigidBody Python Port
            new_body = RigidBody(body_name, geom, block_mesh, actor, tree_item)
            
            # --- CRITICAL: Pre-twist and align the mesh for direct matrix animation! ---
            new_body.center_and_align_mesh() 
            self.physics_bodies[body_name] = new_body
            
            # 4. Automatically generate a CoG R-Frame for this body
            rf_name = f"RF_CoG_{body_name}"
            cog_rf = RFrame(
                name=rf_name, position=new_body.cog, orientation=new_body.pos_angles,
                transform_matrix=new_body.principal_axes, plotter=self.plotter,
                parent_body=new_body, is_cog=True
            )
            self.rframes.append(cog_rf)
            QTreeWidgetItem(self.node_rframes, [rf_name])

            blocks_processed += 1

        self.node_bodies.setExpanded(True)
        self.node_rframes.setExpanded(True)
        
        # 5. CALCULATE 15% JOINT/FORCE SCALE SIZE
        max_dist = 30.0 
        for body in self.physics_bodies.values():
            dist = np.linalg.norm(body.cog) * MMtoM
            if dist > max_dist: max_dist = dist
        # self.joint_base_size = max(max_dist * 0.15, 0.05)

        # 6. AUTO-GENERATE GRAVITY FORCES
        for name, body in self.physics_bodies.items():
            if body.is_ground: continue
            self._create_gravity_force_for_body(body)
        
        # 7. Finalize UI and Camera
        self.update_rframe_scales() 
        self.ui.Edit_GravityX.setText("0.0")
        self.ui.Edit_GravityY.setText("-9.81")
        self.ui.Edit_GravityZ.setText("0.0")
        
        self.plotter.reset_camera()
        print(f"Imported {blocks_processed} distinct bodies from '{original_cad_name}'.")        

    # ==========================================
    # --- SELECTION & VISUAL LOGIC ---
    # ==========================================
    
    def update_multi_selection_visuals(self, active_names_list):
        """ Highlights multiple bodies simultaneously (e.g. for Joints) without changing the single selected_body. """
        self.selected_body = None # Clear single selection to protect the UI properties
        
        for name, body in self.physics_bodies.items():
            if body.is_ground: continue
            
            if name in active_names_list:
                body.actor.prop.opacity = 0.5   # Make transparent
                # --- THE FIX OPTIONAL: Make sure the selected body ALSO turns black if disabled! ---
                body.actor.prop.color = body.base_color if body.enabled else "black"
            else:
                body.actor.prop.opacity = 1.0 if body.enabled else 0.5
                body.actor.prop.color = body.base_color if body.enabled else "black"
                body.actor.SetVisibility(body.visible)
                
        # Update CoG RFrames based on Parent Visibility
        # --- THE FIX: Respect the auxiliary hide button! ---
        hide_aux = self.ui.btnHideShowObjects.isChecked()
        for rf in self.rframes:
            if rf.is_cog and rf.parent_body:
                if hide_aux:
                    rf.set_visible(False)
                else:
                    rf.set_visible(rf.parent_body.visible)
                
    def update_selection_visuals(self, active_name):
        self.selected_body = active_name

        for name, body in self.physics_bodies.items():
            if body.is_ground: continue # Skip the invisible ground
            
            if name == active_name:
                body.actor.prop.opacity = 0.5  
                # --- THE FIX: Make sure the selected body ALSO turns black if disabled! ---
                body.actor.prop.color = body.base_color if body.enabled else "black" 
            else:
                body.actor.prop.opacity = 1.0 if body.enabled else 0.5
                body.actor.prop.color = body.base_color if body.enabled else "black"
                body.actor.SetVisibility(body.visible)
                
        # Update CoG RFrames based on Parent Visibility
        # --- THE FIX: Respect the auxiliary hide button! ---
        hide_aux = self.ui.btnHideShowObjects.isChecked()
        for rf in self.rframes:
            if rf.is_cog and rf.parent_body:
                if hide_aux:
                    rf.set_visible(False)
                else:
                    rf.set_visible(rf.parent_body.visible)

        self.plotter.render()
    
    def toggle_projection(self):
        """ Toggles the 3D Viewport between Perspective and Orthographic (Parallel) projection. """
        # Read the current state directly from the PyVista/VTK camera
        is_ortho = self.plotter.camera.parallel_projection
        
        if is_ortho:
            self.plotter.disable_parallel_projection()
            print("Viewport Projection: Perspective")
            # If the button has text, we can optionally update it here
            # self.ui.btnProjection.setText("Orthographic") 
        else:
            self.plotter.enable_parallel_projection()
            print("Viewport Projection: Orthographic")
            # self.ui.btnProjection.setText("Perspective")
            
        # Force the viewport to redraw immediately with the new camera matrix
        self.update_rframe_scales()
        self.plotter.render()

    def _set_global_plane_view(self, camera_offset, view_up, label):
        """Orients the viewport to a global principal plane and fits all visible bodies."""
        if not hasattr(self, 'plotter') or self.plotter is None or self.plotter.camera is None:
            return

        camera = self.plotter.camera
        focal_point = np.array(camera.focal_point, dtype=float)
        camera_position = np.array(camera.position, dtype=float)
        distance = np.linalg.norm(camera_position - focal_point)
        if distance < 1e-6:
            distance = 1.0

        new_position = focal_point + np.array(camera_offset, dtype=float) * distance
        self.plotter.camera_position = [new_position.tolist(), focal_point.tolist(), list(view_up)]
        self.plotter.reset_camera()
        self.update_rframe_scales()
        self.plotter.render()
        print(f"Viewport oriented to {label}.")

    def set_xy_view(self):
        """Sets the viewport to the global XY plane with +Y up and +X right."""
        self._set_global_plane_view([0.0, 0.0, 1.0], [0.0, 1.0, 0.0], "Global XY View")

    def set_zy_view(self):
        """Sets the viewport to the global ZY plane with +Y up and +Z left."""
        self._set_global_plane_view([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], "Global ZY View")

    def set_xz_view(self):
        """Sets the viewport to the global XZ plane with +Z down and +X right."""
        self._set_global_plane_view([0.0, 1.0, 0.0], [0.0, 0.0, -1.0], "Global XZ View")
        
    def clear_selection(self):
        """ Resets all visuals, memory, and UI selections via the Unselect All button. """
        self.selected_body = None
        self.selected_rframe = None

        # 1. Reset Body Visuals (Solid Colors, No Transparency)
        for body in self.physics_bodies.values():
            if body.is_ground: continue # Skip the invisible ground
            body.actor.prop.opacity = 1.0 if body.enabled else 0.5
            body.actor.prop.color = body.base_color if body.enabled else "black"
        # --- Clear Velocity Fields ---
        if hasattr(self.ui, 'Edit_Vx0'):
            for field in [self.ui.Edit_Vx0, self.ui.Edit_Vy0, self.ui.Edit_Vz0, 
                          self.ui.Edit_Wx0, self.ui.Edit_Wy0, self.ui.Edit_Wz0]:
                field.setText("0.0")
                
        # 2. Reset RFrame Visuals (Remove Glow)
        for rf in self.rframes:
            rf.set_selected(False)
        # --- Reset Force Visuals (Remove Gold) ---
        self.update_force_selection_visuals(None)
        
        # 3. Clear UI Tree Selection Safely
        self.ui.treeHierarchy.blockSignals(True)
        self.ui.treeHierarchy.clearSelection()
        self.ui.treeHierarchy.blockSignals(False)

        # 4. Reset Properties Text Box
        html = """
        <div style="font-family: 'Segoe UI', sans-serif; font-size: 12px;">
            <p>No body selected.</p>
        </div>
        """
        self.ui.txbBodyProperties.setHtml(html)

        # --- 5. Clean UI Input Fields ---
        # Clear Names
        self.ui.EditName.setText("")
        self.ui.Edit_RFName.setText("")
        
        self.ui.Edit_ForceName.setText("")
        self.ui.Edit_ForceValue.setText("1")
        self.ui.Edit_BodyForce.setText("")
        self.ui.Edit_RFForce.setText("")
        if hasattr(self.ui, 'Edit_GearPairName'):
            self.ui.Edit_GearPairName.setText("")
        
        # Assign 0-values
        self.ui.EditDensity.setText("0")
        
        self.ui.EditRF_X_Pos.setText("0")
        self.ui.EditRF_Y_Pos.setText("0")
        self.ui.EditRF_Z_Pos.setText("0")
        
        self.ui.EditRF_X_Angle.setText("0")
        self.ui.EditRF_Y_Angle.setText("0")
        self.ui.EditRF_Z_Angle.setText("0")
        
        self.selected_body = None
        self.selected_rframe = None
        self.selected_force = None
        
        self.update_joint_selection_visuals(None)
        
        # --- Reset Springs ---
        if hasattr(self, 'springs_list'):
            for spring in self.springs_list:
                spring.set_selected(False)
        
        # --- un-glow the bushings ----        
        if hasattr(self, 'bushings_list'):
            for bushing in self.bushings_list:
                bushing.set_selected(False)
                        
        # Force the screen to redraw
        self.plotter.render()
        
    def update_rf_selection_visuals(self, active_rf_name):
        self.selected_rframe = active_rf_name

        for rf in self.rframes:
            if rf.name == active_rf_name:
                rf.set_selected(True)
            else:
                rf.set_selected(False)

        self.plotter.render()

    def display_body_properties(self, body):
        
        I_mm2 = body.inertia_tensor * 1000000.0
        P_mm2 = body.principal_inertia * 1000000.0
        Check_mm2 = body.I_check * 1000000.0

        # --- Convert solver volume (m³) back to UI volume (mm³) ---
        vol_mm3 = body.volume * 1e9
        
        html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; font-size: 12px;"> 
            <b>--- Body Properties ---</b><br>
            <b>Name:</b> {body.name}<br>
            <b>Density:</b> {body.density:.2f} kg/(m³)<br>
            <b>Mass:</b> {body.mass:.4f} kg<br>
            <b>Volume:</b> {vol_mm3:,.2f} mm³<br>
            <b>CoG, mm:</b> X: {body.cog[0]*MMtoM:.4f} | Y: {body.cog[1]*MMtoM:.4f} | Z: {body.cog[2]*MMtoM:.4f}<br><br>
            
            <b>Inertia Tensor [I] (w.r.t CoG), kg*mm²:</b><br>
            [ {I_mm2[0,0]:12.3f}, {I_mm2[0,1]:12.3f}, {I_mm2[0,2]:12.3f} ]<br>
            [ {I_mm2[1,0]:12.3f}, {I_mm2[1,1]:12.3f}, {I_mm2[1,2]:12.3f} ]<br>
            [ {I_mm2[2,0]:12.3f}, {I_mm2[2,1]:12.3f}, {I_mm2[2,2]:12.3f} ]<br><br>

            <b>Principal Moments of Inertia, kg*mm²:</b><br>
            I1: {P_mm2[0]:12.3f}<br>
            I2: {P_mm2[1]:12.3f}<br>
            I3: {P_mm2[2]:12.3f}<br><br>

            <b>Rotation Matrix (Principal Axes w.r.t Global):</b><br>
            [ {body.principal_axes[0,0]:10.4f}, {body.principal_axes[0,1]:10.4f}, {body.principal_axes[0,2]:10.4f} ]<br>
            [ {body.principal_axes[1,0]:10.4f}, {body.principal_axes[1,1]:10.4f}, {body.principal_axes[1,2]:10.4f} ]<br>
            [ {body.principal_axes[2,0]:10.4f}, {body.principal_axes[2,1]:10.4f}, {body.principal_axes[2,2]:10.4f} ]<br><br>

            <b>Orientation (Yaw-Pitch-Roll):</b><br>
            Yaw (Z): {body.pos_angles[0]:12.3f}°<br>
            Pitch &nbsp;&nbsp;(Y): {body.pos_angles[1]:12.3f}°<br>
            Roll &nbsp;&nbsp;(X): {body.pos_angles[2]:12.3f}°<br><br>

            <b>--- Mathematical verification ---</b><br>
            <b>Check: I_global = R * I_principal * R^T (kg*mm²)</b><br>
            [ {Check_mm2[0,0]:12.3f}, {Check_mm2[0,1]:12.3f}, {Check_mm2[0,2]:12.3f} ]<br>
            [ {Check_mm2[1,0]:12.3f}, {Check_mm2[1,1]:12.3f}, {Check_mm2[1,2]:12.3f} ]<br>
            [ {Check_mm2[2,0]:12.3f}, {Check_mm2[2,1]:12.3f}, {Check_mm2[2,2]:12.3f} ]<br>
            <b>Max Tensor Error:</b> {body.math_error:.3e}
        </div>
        """
        self.ui.txbBodyProperties.setHtml(html)

    def on_tree_selected(self):
        """ SINGLE CLICK: Updates tracking variables and 3D viewport highlights ONLY. """
        selected_items = self.ui.treeHierarchy.selectedItems()
        if not selected_items: return

        item_name = selected_items[0].text(0)
        current_page = self.ui.stckProperties.currentIndex() # Get current UI page

        # --- SMART UI AUTO-FILL FOR SPRINGS ---
        # (Assuming 'item_name' is the text of the clicked tree item)
        is_body = item_name in self.physics_bodies
        is_rframe = any(rf.name == item_name for rf in self.rframes)
        is_joint = any(j.name == item_name for j in getattr(self, 'joints_list', []))
        
        if is_body or is_rframe or is_joint:
            # Check if the Compression Spring page is currently active
            if self.ui.Edit_BodyI_CompSpring.isVisible():
                if is_body:
                    if not self.ui.Edit_BodyI_CompSpring.text():
                        self.ui.Edit_BodyI_CompSpring.setText(item_name)
                    elif self.ui.Edit_BodyI_CompSpring.text() != item_name:
                        self.ui.Edit_BodyJ_CompSpring.setText(item_name)
                elif is_rframe:
                    if not self.ui.Edit_RFBodyI_CompSpring.text():
                        self.ui.Edit_RFBodyI_CompSpring.setText(item_name)
                    elif self.ui.Edit_RFBodyI_CompSpring.text() != item_name:
                        self.ui.Edit_RFBodyJ_CompSpring.setText(item_name)
                        
            # Check if the Torsion Spring page is currently active
            elif self.ui.Edit_BodyI_TorsSpring.isVisible():
                if is_body:
                    if not self.ui.Edit_BodyI_TorsSpring.text():
                        self.ui.Edit_BodyI_TorsSpring.setText(item_name)
                    elif self.ui.Edit_BodyI_TorsSpring.text() != item_name:
                        self.ui.Edit_BodyJ_TorsSpring.setText(item_name)
                elif is_rframe:
                    if not self.ui.Edit_RFBodyI_TorsSpring.text():
                        self.ui.Edit_RFBodyI_TorsSpring.setText(item_name)
                    elif self.ui.Edit_RFBodyI_TorsSpring.text() != item_name:
                        self.ui.Edit_RFBodyJ_TorsSpring.setText(item_name)
                        
            # Check if the Bushing page is currently active
            elif self.ui.Edit_BodyI_Bushing.isVisible():
                if is_body:
                    if not self.ui.Edit_BodyI_Bushing.text():
                        self.ui.Edit_BodyI_Bushing.setText(item_name)
                    elif self.ui.Edit_BodyI_Bushing.text() != item_name:
                        self.ui.Edit_BodyJ_Bushing.setText(item_name)
                elif is_rframe:
                    if not self.ui.Edit_RFBodyI_Bushing.text():
                        self.ui.Edit_RFBodyI_Bushing.setText(item_name)
                    # elif self.ui.Edit_RFBodyI_Bushing.text() != item_name:    # Hide the input field for now, unless Bushing with 2 RFs is properly tested
                    #     self.ui.Edit_RFBodyJ_Bushing.setText(item_name)       
                        
            # --- Check if the Contact page is currently active ---
            elif self.ui.stckProperties.currentIndex() == 8: 
                if is_body and item_name != "Ground":
                    if not self.ui.Edit_BodyI_Contact.text():
                        self.ui.Edit_BodyI_Contact.setText(item_name)
                    elif self.ui.Edit_BodyI_Contact.text() != item_name:
                        self.ui.Edit_BodyJ_Contact.setText(item_name)            
                        
            # --- Check if the Gear page is currently active ---
            elif self.ui.stckProperties.currentIndex() == 9:
                if is_rframe:
                    self.ui.Edit_RFGear.setText(item_name)     
                    
            # --- Auto-Fill for Gear Pair Constraint Page ---
            elif self.ui.stckProperties.currentIndex() == 10: 
                if is_joint:
                    if not self.ui.Edit_JointGear1.text():
                        self.ui.Edit_JointGear1.setText(item_name)
                    elif self.ui.Edit_JointGear1.text() != item_name:
                        self.ui.Edit_JointGear2.setText(item_name)
                elif is_body:
                    self.ui.Edit_JointCarrier.setText(item_name)  
                             
            # --- Auto-Fill for Motions Page ---
            elif self.ui.stckProperties.currentIndex() == 12: # 12 is Motions page index
                if is_joint:
                    self.ui.Edit_MotionJoint.setText(item_name)
                    
            # --- Auto-Fill for Primitives Page ---
            elif hasattr(self.ui, 'Edit_RFPrimitive') and self.ui.Edit_RFPrimitive.isVisible():
                if is_rframe:
                    if not self.ui.Edit_RFPrimitive.text():
                        self.ui.Edit_RFPrimitive.setText(item_name)
                    elif self.ui.Edit_RFPrimitive.text() != item_name:
                        # Only fill the second target if the primitive is a Link!
                        if "Link" in self.ui.cmbPrimitiveType.currentText() and hasattr(self.ui, 'Edit_RFPrimTarget'):
                            self.ui.Edit_RFPrimTarget.setText(item_name)
                            
        # 1. Did the user click a Rigid Body?
        if item_name in self.physics_bodies:
            self.selected_force = None
            self.selected_joint = None
            self.update_selection_visuals(item_name)
            self.update_rf_selection_visuals(None)
            self.update_force_selection_visuals(None)
            self.update_joint_selection_visuals(None)
            self.update_spring_selection_visuals(None) # <--- ADDED
            
            # --- AUTO-FILL JOINT UI ---
            if current_page == 2: 
                current_i = self.ui.Edit_Body_I.text().strip()
                current_j = self.ui.Edit_Body_J.text().strip()
                if not current_i: self.ui.Edit_Body_I.setText(item_name)
                elif not current_j and current_i != item_name: self.ui.Edit_Body_J.setText(item_name)
                    
            # --- AUTO-FILL FORCE UI ---
            elif current_page == 3:
                if item_name != "Ground" and not self.ui.Edit_BodyForce.text().strip():
                    self.ui.Edit_BodyForce.setText(item_name)

            # --- AUTO-FILL BOOLEAN UNION UI ---
            elif current_page == 14:
                if item_name != "Ground":
                    current_i = self.ui.Edit_Body_I_Boolean.text().strip()
                    current_j = self.ui.Edit_Body_J_Boolean.text().strip()
                    if not current_i:
                        self.ui.Edit_Body_I_Boolean.setText(item_name)
                    elif not current_j and current_i != item_name:
                        self.ui.Edit_Body_J_Boolean.setText(item_name)

        # 2. Did the user click a Reference Frame?
        elif any(rf.name == item_name for rf in self.rframes):
            self.selected_force = None
            self.selected_joint = None
            self.update_rf_selection_visuals(item_name)
            self.update_force_selection_visuals(None)
            self.update_joint_selection_visuals(None)
            self.update_spring_selection_visuals(None) # <--- ADDED
            
            # --- AUTO-FILL JOINT UI ---
            if current_page == 2: 
                current_anchor = self.ui.Edit_RF_Anchor.text().strip()
                current_target = self.ui.Edit_RF_Target.text().strip()
                if not current_anchor: self.ui.Edit_RF_Anchor.setText(item_name)
                elif not current_target and current_anchor != item_name: self.ui.Edit_RF_Target.setText(item_name)

            # --- AUTO-FILL FORCE UI ---
            elif current_page == 3:
                if not self.ui.Edit_RFForce.text().strip():
                    self.ui.Edit_RFForce.setText(item_name)

        # 3. Did the user click a Force or Torque?
        elif any(f.name == item_name for f in self.forces_list):
            force = next((f for f in self.forces_list if f.name == item_name), None)
            if force:
                self.selected_force = item_name
                self.selected_joint = None
                self.update_selection_visuals(force.parent_body.name)
                self.update_rf_selection_visuals(None)
                self.update_force_selection_visuals(item_name)
                self.update_joint_selection_visuals(None)
                self.update_spring_selection_visuals(None) # <--- ADDED

        # 4. Did the user click a Joint?
        elif any(j.name == item_name for j in self.joints_list):
            joint = next((j for j in self.joints_list if j.name == item_name), None)
            if joint:
                self.selected_force = None
                self.selected_joint = item_name
                self.update_multi_selection_visuals([joint.body_i.name, joint.body_j.name])
                self.update_rf_selection_visuals(None)
                self.update_force_selection_visuals(None)
                self.update_joint_selection_visuals(item_name)
                self.update_spring_selection_visuals(None) # <--- ADDED

        # --- 5. Did the user click a Spring? ---
        elif any(s.name == item_name for s in getattr(self, 'springs_list', [])):
            spring = next((s for s in self.springs_list if s.name == item_name), None)
            if spring:
                self.selected_force = None
                self.selected_joint = None
                
                # Dim the rest of the scene, keeping Body I and Body J visible
                self.update_multi_selection_visuals([spring.body_i.name, spring.body_j.name])
                
                # Turn off all other highlights
                self.update_rf_selection_visuals(None)
                self.update_force_selection_visuals(None)
                self.update_joint_selection_visuals(None)
                
                # Turn ON the Spring highlight (This triggers the gold color and ghost opacity!)
                self.update_spring_selection_visuals(item_name)

        # --- 6. Did the user click a Bushing? ---
        elif any(b.name == item_name for b in getattr(self, 'bushings_list', [])):
            bushing = next((b for b in self.bushings_list if b.name == item_name), None)
            if bushing:
                self.selected_force = None
                self.selected_joint = None
                
                # Dim the rest of the scene, keeping Body I and Body J visible
                self.update_multi_selection_visuals([bushing.body_i.name, bushing.body_j.name])
                
                # Turn off all other highlights
                self.update_rf_selection_visuals(None)
                self.update_force_selection_visuals(None)
                self.update_joint_selection_visuals(None)
                
                # Turn ON the Bushing highlight (This uses the shared Spring visualizer!)
                self.update_spring_selection_visuals(item_name)

        # --- 7. Did the user click a Contact Pair? ---
        elif any(c.name == item_name for c in getattr(self, 'contact_pairs', [])):
            contact = next((c for c in self.contact_pairs if c.name == item_name), None)
            if contact:
                self.selected_force = None
                self.selected_joint = None
                
                # Dim the rest of the scene, keeping Body I and Body J visible
                self.update_multi_selection_visuals([contact.body_i.name, contact.body_j.name])
                
                # Turn off all other highlights
                self.update_rf_selection_visuals(None)
                self.update_force_selection_visuals(None)
                self.update_joint_selection_visuals(None)
                self.update_spring_selection_visuals(None)

        # --- 8. Did the user click a Gear Pair? ---
        elif any(g.name == item_name for g in getattr(self, 'gear_pairs_list', [])):
            gear = next((g for g in self.gear_pairs_list if g.name == item_name), None)
            if gear:
                self.selected_force = None
                self.selected_joint = None
                
                # Dim the rest of the scene, keeping Gear 1, Gear 2, and Carrier visible!
                self.update_multi_selection_visuals([gear.body_1.name, gear.body_2.name, gear.carrier.name])
                
                # Turn off all other highlights
                self.update_rf_selection_visuals(None)
                self.update_force_selection_visuals(None)
                self.update_joint_selection_visuals(None)
                self.update_spring_selection_visuals(None)
                
                # Populate the read-only name field
                if hasattr(self.ui, 'Edit_GearPairName'):
                    self.ui.Edit_GearPairName.setText(gear.name)
                    
        # --- Did the user click a Motion? ---
        elif any(m.name == item_name for m in getattr(self, 'motions_list', [])):
            motion = next((m for m in self.motions_list if m.name == item_name), None)
            if motion:
                self.selected_force = None
                self.selected_joint = motion.joint.name
                self.selected_motion = motion.name
                
                # Highlight the affected joint bodies visually
                self.update_multi_selection_visuals([motion.joint.body_i.name, motion.joint.body_j.name])
                self.update_rf_selection_visuals(None)
                self.update_force_selection_visuals(None)
                self.update_joint_selection_visuals(motion.joint.name)
                self.update_spring_selection_visuals(None)            
        
        self.plotter.render()
    
    def on_tree_double_clicked(self, item, column):
        """ DOUBLE CLICK: Shows the Dock, switches StackedWidget page, and populates UI properties. """
        item_name = item.text(0)
        
        # 1. Show the Dock Widget (if it was closed by the user)
        self.ui.dckProperties.show()
        
        # 2. Populate UI and switch pages based on item type
        # Double-click on the Body
        if item_name in self.physics_bodies:
            body = self.physics_bodies[item_name] # Double-click on the Body
            
            # Switch to Body Page (Index 0)
            self.ui.stckProperties.setCurrentIndex(0)
            
            self.ui.EditName.setText(body.name)
            self.ui.EditDensity.setText(str(body.density))
            
            """if body.name != 'Ground':
               self.ui.Edit_BodyForce.setText(body.name)
            self.ui.Edit_ForceName.setText("")"""
            
            self.ui.chkEnabled.blockSignals(True)
            self.ui.chkVisible.blockSignals(True)
            self.ui.chkEnabled.setChecked(body.enabled)
            self.ui.chkVisible.setChecked(body.visible)
            self.ui.chkEnabled.blockSignals(False)
            self.ui.chkVisible.blockSignals(False)
            
            self.ui.cmbForceAnchorXYZ.setEnabled(True)
            self.display_body_properties(body)
        
            # --- Populate Initial Velocities ---
            if hasattr(self.ui, 'Edit_Vx0'):
                # Linear (Solver: m/s -> UI: mm/s)
                self.ui.Edit_Vx0.setText(f"{body.initial_velocity[0] * 1000.0:.3f}")
                self.ui.Edit_Vy0.setText(f"{body.initial_velocity[1] * 1000.0:.3f}")
                self.ui.Edit_Vz0.setText(f"{body.initial_velocity[2] * 1000.0:.3f}")
                
                # Angular (Solver: rad/s -> UI: rad/s)
                self.ui.Edit_Wx0.setText(f"{body.initial_angular_velocity[0]:.3f}")
                self.ui.Edit_Wy0.setText(f"{body.initial_angular_velocity[1]:.3f}")
                self.ui.Edit_Wz0.setText(f"{body.initial_angular_velocity[2]:.3f}")
            
        # Double-click on the RF    
        elif any(rf.name == item_name for rf in self.rframes): 
            rf = next((r for r in self.rframes if r.name == item_name), None)
            if rf:
                # Switch to RF Page (Index 1)
                self.ui.stckProperties.setCurrentIndex(1)
                
                self.ui.Edit_RFName.setText(rf.name)
                
                """self.ui.Edit_RFForce.setText(rf.name)
                self.ui.Edit_ForceName.setText("")"""
                
                self.ui.EditRF_X_Pos.setText(f"{rf.position[0] * MMtoM:.3f}")
                self.ui.EditRF_Y_Pos.setText(f"{rf.position[1] * MMtoM:.3f}")
                self.ui.EditRF_Z_Pos.setText(f"{rf.position[2] * MMtoM:.3f}")
                
                self.ui.EditRF_Z_Angle.setText(f"{rf.orientation[0]:.3f}")
                self.ui.EditRF_Y_Angle.setText(f"{rf.orientation[1]:.3f}")
                self.ui.EditRF_X_Angle.setText(f"{rf.orientation[2]:.3f}")
                
                self.ui.cmbForceAnchorXYZ.setEnabled(True)
                self.ui.btnAddForceTorque.setEnabled(True)
                
        # Double-click on the Joint
        elif any(j.name == item_name for j in self.joints_list): # Double-click on the Joint
            joint = next((j for j in self.joints_list if j.name == item_name), None)
            if joint:
                # Switch to Joints Page (Index 2)
                self.ui.stckProperties.setCurrentIndex(2)
                
                self.ui.Edit_Joint_Name.setText(joint.name)
                self.ui.Edit_Body_I.setText(joint.body_i.name)
                self.ui.Edit_Body_J.setText(joint.body_j.name)
                
                # --- THE FIX: Load the saved RF names into the UI ---
                self.ui.Edit_RF_Anchor.setText(getattr(joint, 'source_anchor_name', ""))
                self.ui.Edit_RF_Target.setText(getattr(joint, 'source_target_name', ""))
                
                # --- UPDATE: Map JointType to ComboBox Index ---
                type_map = {
                    JointType.FIXED: 0, JointType.SPHERICAL: 1, 
                    JointType.REVOLUTE: 2, JointType.CYLINDRICAL: 3, 
                    JointType.PRISMATIC: 4, JointType.PLANAR: 5
                }
                self.ui.cmbJointType.setCurrentIndex(type_map.get(joint.joint_type, 0))
                
                self.ui.chkEnabledJoint.blockSignals(True)
                self.ui.chkEnabledJoint.setChecked(joint.enabled)
                self.ui.chkEnabledJoint.blockSignals(False)
                
                self.ui.btnAddJoint.setEnabled(False)
                
        # Double-click on the Force        
        elif any(f.name == item_name for f in self.forces_list):
            force = next((f for f in self.forces_list if f.name == item_name), None)
            if force:
                self.ui.stckProperties.setCurrentIndex(3)
                
                self.ui.Edit_ForceName.setText(force.name)
                self.ui.Edit_BodyForce.setText(force.parent_body.name)
                # --- Load the saved RF name into the UI ---
                self.ui.Edit_RFForce.setText(getattr(force, 'source_rf_name', ""))
                
                # Setup Type Dropdown
                is_torque = force.force_type in (ForceType.TORQUE, ForceType.E_MOTOR)
                self.ui.cmbForceType.setCurrentIndex(1 if is_torque else 0)
                
                # --- Convert internal SI Nm back to UI Nmm! ---
                display_mag = force.magnitude * 1000.0 if is_torque else force.magnitude
                # self.ui.Edit_ForceValue.setText(f"{display_mag:.3f}") # Before the formula integration
                self.ui.Edit_ForceValue.setText(force.magnitude_expr)
                
                self.ui.cmbSpaceBody.setCurrentIndex(0 if force.fixed_in == ForceFrame.SPACE_FIXED else 1)
                
                # --- Setup Actuator Mode UI ---
                is_actuator = force.force_type in (ForceType.E_MOTOR, ForceType.ACTUATOR)
                self.ui.chkActuatorMode.setChecked(is_actuator)
                
                if is_actuator:
                    # Convert rad/s -> RPM OR m/s -> mm/s for the UI display
                    ui_speed = force.speed_max * (30.0 / np.pi) if is_torque else (force.speed_max * 1000.0)
                    self.ui.Edit_MaxActuatorSpeed.setText(f"{ui_speed:.3f}")
                    
                    # --- Calculate Peak Power for existing Actuator ---
                    try:
                        # Check if the expression is a pure number
                        float(force.magnitude_expr.replace(',', '.'))
                        # If it is, calculate peak power in Watts (Nm/s or N*m/s)
                        peak_power = (force.magnitude * force.speed_max) / 4.0  
                    except ValueError:
                        # It is a math function (e.g. sin(t), step(...)), skip calculation
                        peak_power = 0.0
                        
                    self.ui.Edit_ActPowerLimit.setText(f"{peak_power:.3f}")
                    # --- Load Braking State ---
                    self.ui.chkAllowActuatorBraking.setChecked(force.allow_braking)
                else:
                    self.ui.Edit_MaxActuatorSpeed.setText("0.0")
                    self.ui.Edit_ActPowerLimit.setText("0.000")
                    self.ui.chkAllowActuatorBraking.setChecked(True)
                    
                self.ui.cmbForceAnchorXYZ.setEnabled(False)
                self.ui.btnAddForceTorque.setEnabled(False)
                
                self.ui.chkEnabledForce.blockSignals(True)
                self.ui.chkEnabledForce.setChecked(force.enabled)
                self.ui.chkEnabledForce.blockSignals(False)
                
                self.ui.lblNNm.setText('Value, Nmm' if is_torque else 'Value, N')
                
        # Double-click on the Spring
        elif any(s.name == item_name for s in self.springs_list):
            spring = next((s for s in self.springs_list if s.name == item_name), None)
            if not spring: return
            
            if isinstance(spring, CompressionSpring):
                # Switch to Compression Page
                self.ui.stckProperties.setCurrentIndex(5) 
                
                self.ui.Edit_CompSpringName.setText(spring.name)
                self.ui.Edit_BodyI_CompSpring.setText(spring.body_i.name)
                self.ui.Edit_BodyJ_CompSpring.setText(spring.body_j.name)
                self.ui.Edit_RFBodyI_CompSpring.setText(spring.rf_i_name)
                self.ui.Edit_RFBodyJ_CompSpring.setText(spring.rf_j_name)
                
                # Convert SI back to UI units
                self.ui.Edit_StiffnessCompSpring.setText(f"{spring.stiffness / 1000.0:.3f}")
                self.ui.Edit_DampingCompSpring.setText(f"{spring.damping / 1000.0:.3f}")
                self.ui.Edit_PreloadCompSpring.setText(f"{spring.preload:.3f}")
                
                self.ui.chkEnabledCompSpring.blockSignals(True)
                self.ui.chkEnabledCompSpring.setChecked(spring.enabled)
                self.ui.chkEnabledCompSpring.blockSignals(False)
                self.ui.btnAddCompSpring.setEnabled(False)
                
            elif isinstance(spring, TorsionSpring):
                # Switch to Torsion Page
                self.ui.stckProperties.setCurrentIndex(6) 
                
                self.ui.Edit_TorsSpringName.setText(spring.name)
                self.ui.Edit_BodyI_TorsSpring.setText(spring.body_i.name)
                self.ui.Edit_BodyJ_TorsSpring.setText(spring.body_j.name)
                self.ui.Edit_RFBodyI_TorsSpring.setText(spring.rf_i_name)
                self.ui.Edit_RFBodyJ_TorsSpring.setText(spring.rf_j_name)
                self.ui.cmbSpringBodyIAnchorXYZ.setCurrentText(spring.axis_choice)
                
                # Convert SI back to UI units
                self.ui.Edit_StiffnessTorsSpring.setText(f"{spring.stiffness * 1000.0:.3f}")
                self.ui.Edit_DampingTorsSpring.setText(f"{spring.damping * 1000.0:.3f}")
                self.ui.Edit_PreloadTorsSpring.setText(f"{spring.preload * 1000.0:.3f}")
                
                self.ui.chkEnabledTorsSpring.blockSignals(True)
                self.ui.chkEnabledTorsSpring.setChecked(spring.enabled)
                self.ui.chkEnabledTorsSpring.blockSignals(False)
                self.ui.btnAddTorsSpring.setEnabled(False)    
    
        # --- Double-click on the Bushing ---
        elif hasattr(self, 'bushings_list') and any(b.name == item_name for b in self.bushings_list):
            bushing = next((b for b in self.bushings_list if b.name == item_name), None)
            if not bushing: return
            
            # Switch to Bushing Page (Assuming index 7!)
            self.ui.stckProperties.setCurrentIndex(7) 
            
            # 1. Populate Header
            self.ui.Edit_BushingName.setText(bushing.name)
            self.ui.Edit_BodyI_Bushing.setText(bushing.body_i.name)
            self.ui.Edit_BodyJ_Bushing.setText(bushing.body_j.name)
            self.ui.Edit_RFBodyI_Bushing.setText(bushing.rf_i_name)
            self.ui.Edit_RFBodyJ_Bushing.setText(bushing.rf_j_name)
            
            # 2. Populate Translational Arrays (Convert SI back to UI N/mm)
            self.ui.Edit_Kx.setText(f"{bushing.k_trans[0] / 1000.0:.3f}")
            self.ui.Edit_Ky.setText(f"{bushing.k_trans[1] / 1000.0:.3f}")
            self.ui.Edit_Kz.setText(f"{bushing.k_trans[2] / 1000.0:.3f}")
            
            self.ui.Edit_Cx.setText(f"{bushing.c_trans[0] / 1000.0:.3f}")
            self.ui.Edit_Cy.setText(f"{bushing.c_trans[1] / 1000.0:.3f}")
            self.ui.Edit_Cz.setText(f"{bushing.c_trans[2] / 1000.0:.3f}")
            
            self.ui.Edit_Px.setText(f"{bushing.p_trans[0]:.3f}")
            self.ui.Edit_Py.setText(f"{bushing.p_trans[1]:.3f}")
            self.ui.Edit_Pz.setText(f"{bushing.p_trans[2]:.3f}")
            
            # 3. Populate Rotational Arrays (Convert SI back to UI Nmm/rad)
            self.ui.Edit_KRx.setText(f"{bushing.k_rot[0] * 1000.0:.3f}")
            self.ui.Edit_KRy.setText(f"{bushing.k_rot[1] * 1000.0:.3f}")
            self.ui.Edit_KRz.setText(f"{bushing.k_rot[2] * 1000.0:.3f}")
            
            self.ui.Edit_CRx.setText(f"{bushing.c_rot[0] * 1000.0:.3f}")
            self.ui.Edit_CRy.setText(f"{bushing.c_rot[1] * 1000.0:.3f}")
            self.ui.Edit_CRz.setText(f"{bushing.c_rot[2] * 1000.0:.3f}")
            
            self.ui.Edit_PRx.setText(f"{bushing.p_rot[0] * 1000.0:.3f}")
            self.ui.Edit_PRy.setText(f"{bushing.p_rot[1] * 1000.0:.3f}")
            self.ui.Edit_PRz.setText(f"{bushing.p_rot[2] * 1000.0:.3f}")
            
            # 4. Lock Checkbox and Disable Add Button
            self.ui.chkEnabledBushing.blockSignals(True)
            self.ui.chkEnabledBushing.setChecked(bushing.enabled)
            self.ui.chkEnabledBushing.blockSignals(False)
            
            self.ui.btnAddBushing.setEnabled(False)
    
        # --- Double-click on a Contact Pair ---
        elif hasattr(self, 'contact_pairs') and any(c.name == item_name for c in self.contact_pairs):
            contact = next((c for c in self.contact_pairs if c.name == item_name), None)
            if not contact: return
            
            # Switch to Contact Page
            self.ui.stckProperties.setCurrentIndex(8) 
            
            self.ui.Edit_ContactName.setText(contact.name)
            self.ui.Edit_BodyI_Contact.setText(contact.body_i.name)
            self.ui.Edit_BodyJ_Contact.setText(contact.body_j.name)
            
            # Extract Exponent first
            n = contact.exponent
            self.ui.dsbForceExponent.setValue(n)
            
            # Convert SI Solver units back to UI Units!
            # Stiffness UI (N/mm^n) = Stiffness SI / (1000^n)
            ui_stiffness = contact.stiffness / (1000.0 ** n)
            # Damping UI (N/(mm/s)) = Damping SI / 1000
            ui_damping = contact.damping / 1000.0
            
            self.ui.Edit_ContactStiffness.setText(f"{ui_stiffness:.3f}")
            self.ui.Edit_ContactDamping.setText(f"{ui_damping:.3f}")
            
            # --- Load Friction Properties ---
            self.ui.chkContactFriction.blockSignals(True)
            self.ui.chkContactFriction.setChecked(contact.friction_enabled)
            self.ui.chkContactFriction.blockSignals(False)
            
            self.ui.frmContactFriction.setEnabled(contact.friction_enabled)
            self.ui.dsbContactFrictionCoeff.setValue(contact.mu)
            
            # Convert SI (m/s) back to UI (mm/s)
            self.ui.dsbTolVelocity.setValue(contact.slip_tolerance * 1000.0)
            
            
            # Lock Checkbox and Disable Add Button
            self.ui.chkEnabledContact.blockSignals(True)
            self.ui.chkEnabledContact.setChecked(contact.enabled)
            self.ui.chkEnabledContact.blockSignals(False)
            
            self.ui.btnAddContact.setEnabled(False)
            
            # --- Load Mesh Resolution State Safely ---
            if hasattr(self.ui, 'cmbContactMesh'):
                self.ui.cmbContactMesh.blockSignals(True)
                # Fallback to 0 (Standard) if mesh_mode isn't found in older saves
                self.ui.cmbContactMesh.setCurrentIndex(getattr(contact, 'mesh_mode', 0))
                self.ui.cmbContactMesh.blockSignals(False)
    
        # --- Double-click on a Gear Constraint ---
        elif hasattr(self, 'gear_pairs_list') and any(g.name == item_name for g in self.gear_pairs_list):
            gear = next((g for g in self.gear_pairs_list if g.name == item_name), None)
            if not gear: return
            
            # Switch to Gear Constraint Page (Index 10)
            self.ui.stckProperties.setCurrentIndex(10)
            
            # 1. Map GearType enum to ComboBox Index
            from unit_joints import GearType
            if gear.gear_type == GearType.SPUR_HELICAL: type_idx = 0
            elif gear.gear_type == GearType.INTERNAL: type_idx = 1
            else: type_idx = 2
            
            self.ui.cmbJointGearType.setCurrentIndex(type_idx)
            
            # 2. Populate String Fields
            self.ui.Edit_JointGear1.setText(gear.joint_1.name)
            self.ui.Edit_JointGear2.setText(gear.joint_2.name)
            self.ui.Edit_JointCarrier.setText(gear.carrier.name)
            
            # 3. Populate Numerical Fields
            self.ui.dsbNTeethGear1.setValue(gear.z1)
            self.ui.dsbNTeethGear2.setValue(gear.z2)
            self.ui.dsbJointModule.setValue(gear.module_n)
            
            # import numpy as np
            self.ui.dsbJointPressureAngle.setValue(np.degrees(gear.alpha))
            self.ui.dsbJointHelixAngle.setValue(np.degrees(gear.beta))
            self.ui.dsbJointPitchAngle.setValue(np.degrees(gear.gamma))
            
            # 4. Disable the Create button so the user doesn't accidentally spawn duplicates
            self.ui.btnCreateGearPair.setEnabled(False)
            self.ui.btnUpdateGearPair.setEnabled(True) # <--- Enable Update
            
            # --- Sync the Enabled Checkbox ---
            if hasattr(self.ui, 'chkEnabledGearPair'):
                self.ui.chkEnabledGearPair.blockSignals(True)
                self.ui.chkEnabledGearPair.setChecked(gear.enabled)
                self.ui.chkEnabledGearPair.blockSignals(False)
                
        # --- Double-click on a Motion ---
        elif hasattr(self, 'motions_list') and any(m.name == item_name for m in self.motions_list):
            motion = next((m for m in self.motions_list if m.name == item_name), None)
            if not motion: return
            
            # Switch to Motions Page (Index 12)
            self.ui.stckProperties.setCurrentIndex(12)
            self.ui.dckProperties.show()
            
            self.ui.Edit_MotionName.setText(motion.name)
            self.ui.Edit_MotionJoint.setText(motion.joint.name)
            self.ui.Edit_MotionFunction.setText(motion.expression_str)
            
            # Update Combo Boxes safely
            self.ui.cmbMotionTransRot.blockSignals(True)
            self.ui.cmbMotionTransRot.setCurrentIndex(motion.trans_rot.value)
            self.ui.cmbMotionTransRot.blockSignals(False)
            
            self.ui.cmbMotionType.blockSignals(True)
            self.ui.cmbMotionType.setCurrentIndex(motion.motion_type.value)
            self.ui.cmbMotionType.blockSignals(False)
            
            # Force the label unit update
            self.on_motion_trans_rot_changed(motion.trans_rot.value)
            
            self.ui.chkEnabledMotion.blockSignals(True)
            self.ui.chkEnabledMotion.setChecked(motion.enabled)
            self.ui.chkEnabledMotion.blockSignals(False)
            
            # Disable add button when editing existing
            self.ui.btnAddMotion.setEnabled(False)
            
            
    def prepare_new_motion(self, type_idx):
        """ Prepares the UI for defining a brand new joint motion of the selected type. """
        # 1) Unselect all items in Viewport and Tree
        self.clear_selection()
        
        # 2) Clean properties
        self.ui.Edit_MotionName.setText("")
        self.ui.Edit_MotionJoint.setText("")
        self.ui.Edit_MotionFunction.setText("0.0")
        
        self.ui.chkEnabledMotion.blockSignals(True)
        self.ui.chkEnabledMotion.setChecked(True)
        self.ui.chkEnabledMotion.blockSignals(False)
        
        # 3) Set Joint Motion Type in the ComboBox, activate the AddMotion button
        self.ui.cmbMotionTransRot.setCurrentIndex(type_idx) # 0 = Displacement, 1 = Velocity
        self.ui.btnAddMotion.setEnabled(True)
        
        # 4) Display the Dock (if closed) and open the Joint Page
        self.ui.stckProperties.setCurrentIndex(12)
        self.ui.dckProperties.show()
    
    def on_motion_trans_rot_changed(self, index):
        """ Updates the Motion function unit label dynamically based on ComboBox selection. """
       
        if self.ui.cmbMotionTransRot.currentIndex() == 0:
            if self.ui.cmbMotionType.currentIndex() == 0: self.ui.lblMotion.setText('mm')
            elif self.ui.cmbMotionType.currentIndex() == 1: self.ui.lblMotion.setText('mm/sec')
        elif self.ui.cmbMotionTransRot.currentIndex() == 1:
            if self.ui.cmbMotionType.currentIndex() == 0: self.ui.lblMotion.setText('rad')
            elif self.ui.cmbMotionType.currentIndex() == 1: self.ui.lblMotion.setText('rad/sec')

    def prepare_new_joint(self, type_idx):
        """ Prepares the UI for defining a brand new joint of the selected type. """
        # 1) Unselect all items in Viewport and Tree
        self.clear_selection()
        
        # 2) Clean properties
        self.ui.Edit_Joint_Name.setText("")
        self.ui.Edit_Body_I.setText("")
        self.ui.Edit_Body_J.setText("")
        self.ui.Edit_RF_Anchor.setText("")
        self.ui.Edit_RF_Target.setText("")
        self.ui.cmbAnchorXYZ.setEnabled(True)
        
        # Set Anchor Direction to Z and Enable Joint
        self.ui.cmbAnchorXYZ.setCurrentText("Z")
        
        self.ui.chkEnabledJoint.blockSignals(True)
        self.ui.chkEnabledJoint.setChecked(True)
        self.ui.chkEnabledJoint.blockSignals(False)
        
        # 3) Set Joint Type in the ComboBox, activate the AddJoint button
        self.ui.cmbJointType.setCurrentIndex(type_idx)
        self.ui.btnAddJoint.setEnabled(True)
        self.ui.cmbAnchorXYZ.setEnabled(True)
        
        # 4 & 5) Display the Dock (if closed) and open the Joint Page
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(2)
    
    def prepare_new_force(self, type_idx, is_actuator=False):
        """ Prepares the UI for defining a brand new Force, Torque, Actuator, or E-Motor. """
        self.clear_selection()
        
        self.ui.Edit_ForceName.setText("")
        self.ui.Edit_BodyForce.setText("")
        self.ui.Edit_RFForce.setText("")
        
        self.ui.cmbForceAnchorXYZ.setEnabled(True)
        self.ui.cmbForceAnchorXYZ.setCurrentText("Z")
        self.ui.cmbSpaceBody.setCurrentIndex(0) 
        self.ui.Edit_ForceValue.setText("1.0")
        
        # --- THE FIX: Set Actuator Mode based on the clicked button! ---
        self.ui.chkActuatorMode.setChecked(is_actuator)
        self.ui.Edit_MaxActuatorSpeed.setText("0.0")
        self.ui.Edit_ActPowerLimit.setText("0.000")
        self.ui.chkAllowActuatorBraking.setChecked(True)
        
        self.ui.chkEnabledForce.blockSignals(True)
        self.ui.chkEnabledForce.setChecked(True)
        self.ui.chkEnabledForce.blockSignals(False)
        self.ui.btnAddForceTorque.setEnabled(True)
        
        self.ui.cmbForceType.blockSignals(True)
        self.ui.cmbForceType.setCurrentIndex(type_idx)
        self.ui.cmbForceType.blockSignals(False)
        
        # Label updates for magnitude and speed units
        if type_idx == 0:
            self.ui.lblNNm.setText('Value, N')
            self.ui.btnAddForceTorque.setText('Create Force')
            self.ui.lblSpeedUnit.setText('Max Speed, mm/s')
        else:
            self.ui.lblNNm.setText('Value, Nmm')
            self.ui.btnAddForceTorque.setText('Create Torque')
            self.ui.lblSpeedUnit.setText('Max Speed, rpm')

            
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(3)
        
    def toggle_joint_enabled(self, state):
        if not self.selected_joint: return
        joint = next((j for j in self.joints_list if j.name == self.selected_joint), None)
        if joint:
            joint.enabled = state
            joint.visible = state # Keep internal tracker in sync
            
            if state: 
                self._auto_enable_linked_bodies(joint)
            else:
                # --- Cascading Disable Logic for Gears! ---
                for gear in getattr(self, 'gear_pairs_list', []):
                    if gear.joint_1.name == joint.name or gear.joint_2.name == joint.name:
                        gear.enabled = False
                        print(f"Auto-disabled Gear Constraint '{gear.name}' because its joint was disabled.")
                            
            # --- Re-calculate the 3D mesh position before showing it! ---
            current_scale = self.rframes[0].base_scale if self.rframes else 10.0
            joint.update_transform(current_scale)
            
            # --- Respect the Global Hide button ---
            if self.ui.btnHideShowObjects.isChecked():
                joint.set_visible(False)
            else:
                joint.set_visible(state)
            
            self.refresh_tree_visuals()
            self.plotter.render()
            
            if hasattr(self, 'invalidate_results'):
                self.invalidate_results()

    def delete_custom_joint(self):
        """ Deletes the Joint currently displayed in the Edit_Joint_Name field. """
        target_name = self.ui.Edit_Joint_Name.text().strip()
        if not target_name:
            print("Please select a Joint to delete.")
            return

        joint = next((j for j in self.joints_list if j.name == target_name), None)
        if not joint: return

        # --- THE UPGRADE: Ask for permission! ---
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete Joint '{joint.name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No: return
        # ----------------------------------------
        self._delete_motions_for_joints([joint])

        # 1. Ask the graphics card to destroy the 3D actors
        for act in joint.actors:
            self.plotter.remove_actor(act)
            
        # 2. Delete from engine memory
        self.joints_list.remove(joint)
        
        # 3. Delete from TreeView
        for i in range(self.node_joints.childCount()):
            if self.node_joints.child(i).text(0) == joint.name:
                self.node_joints.takeChild(i)
                break
                
        # 4. Clean up UI and 3D Visuals
        self.ui.Edit_Joint_Name.setText("")
        self.ui.Edit_Body_I.setText("")
        self.ui.Edit_Body_J.setText("")
        self.ui.Edit_RF_Anchor.setText("")
        self.ui.Edit_RF_Target.setText("")
        self.ui.btnAddJoint.setEnabled(True)
        self.ui.cmbAnchorXYZ.setEnabled(True)
        
        self.clear_selection()
        self.invalidate_results()
        
        self.plotter.render()
        print(f"Deleted Joint '{joint.name}'.")

    def _delete_motions_for_joints(self, joints_to_delete):
        """Removes kinematic motions attached to joints that are being deleted."""
        if not joints_to_delete or not hasattr(self, 'motions_list'):
            return

        joint_names = {joint.name for joint in joints_to_delete}
        motions_to_delete = [
            motion for motion in self.motions_list
            if getattr(motion, 'joint', None) and motion.joint.name in joint_names
        ]

        if not motions_to_delete:
            return

        for motion in motions_to_delete:
            self.motions_list.remove(motion)

            if hasattr(self, 'node_motions') and self.node_motions:
                for i in range(self.node_motions.childCount()):
                    if self.node_motions.child(i).text(0) == motion.name:
                        self.node_motions.takeChild(i)
                        break

        if self.selected_motion in joint_names or any(m.name == self.selected_motion for m in motions_to_delete):
            self.selected_motion = None

        if any(self.ui.Edit_MotionName.text().strip() == motion.name for motion in motions_to_delete):
            self.ui.Edit_MotionName.setText("")
            self.ui.Edit_MotionJoint.setText("")
            self.ui.Edit_MotionFunction.setText("0.0")
            self.ui.btnAddMotion.setEnabled(True)
    
    def rename_joint(self):
        """ Triggers a pop-up window to safely rename the targeted Joint. """
        target_name = self.ui.Edit_Joint_Name.text().strip()
        if not target_name:
            print("Please select a Joint to rename.")
            return

        joint = next((j for j in self.joints_list if j.name == target_name), None)
        if not joint: return

        old_name = joint.name

        # 1. Trigger Pop-up
        new_name, ok = QInputDialog.getText(self, "Rename Joint", "Enter new name:", text=old_name)

        # 2. Validate input
        if not ok or not new_name.strip(): return 
        new_name = new_name.strip()
        if new_name == old_name: return 

        if any(j.name == new_name for j in self.joints_list):
            QMessageBox.warning(self, "Rename Error", f"A Joint with the name '{new_name}' already exists!")
            return

        # 3. Update Object and UI Box
        joint.name = new_name
        self.selected_joint = new_name
        self.ui.Edit_Joint_Name.setText(new_name)

        # 4. Update Tree Hierarchy visually
        for i in range(self.node_joints.childCount()):
            if self.node_joints.child(i).text(0) == old_name:
                self.node_joints.child(i).setText(0, new_name)
                break

        print(f"Successfully renamed Joint '{old_name}' to '{new_name}'.")
                            
    def on_mesh_picked(self, picked_mesh):
        picked_actor = self.plotter.picker.GetActor()
        
        if not picked_actor:
            return

        for name, body in self.physics_bodies.items():
            if body.actor == picked_actor:
                self.update_selection_visuals(name)
                
                self.ui.treeHierarchy.blockSignals(True)
                self.ui.treeHierarchy.setCurrentItem(body.tree_item)
                self.ui.treeHierarchy.blockSignals(False)
                
                self.on_tree_selected()
                break

    # ==========================================
    # --- COMPONENT EVENTS ---
    # ==========================================
    # ==========================================
    # --- ANIMATION & PLAYBACK CONTROLS ---
    # ==========================================
    
    def show_body_page(self):
        """Body property page is displayed""" 
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(0)
        # We can add other actions here later!
        
    def show_RF_page(self):
        """RF property page is displayed""" 
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(1)
        # We can add other actions here later!
        
    def show_Joint_page(self):
        """Joint property page is displayed""" 
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(2)
        # We can add other actions here later!   
        
    def show_Force_page(self):
        """Force property page is displayed""" 
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(3)
        
        # --- Sync UI text fields with the internal global gravity! ---
        self.ui.Edit_GravityX.setText(f"{self.global_gravity[0]:.3g}")
        self.ui.Edit_GravityY.setText(f"{self.global_gravity[1]:.3g}")
        self.ui.Edit_GravityZ.setText(f"{self.global_gravity[2]:.3g}")  
        
    def show_Simulation_page(self):
        """Joint property page is displayed""" 
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(4)
        # We can add other actions here later!   

    def show_Boolean_page(self):
        """Boolean union page is displayed."""
        self.clear_selection()
        self.clean_boolean_body_fields()
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(14)

    def clean_boolean_body_fields(self):
        """Clears the body selectors on the boolean union page."""
        self.ui.Edit_Body_I_Boolean.setText("")
        self.ui.Edit_Body_J_Boolean.setText("")

    def _generate_unique_body_name(self, prefix):
        counter = 1
        body_name = f"{prefix}_{counter}"
        while body_name in self.physics_bodies:
            counter += 1
            body_name = f"{prefix}_{counter}"
        return body_name

    def _body_to_world_polydata(self, body):
        """Builds a world-space PyVista mesh from the body's local render mesh."""
        if body.is_ground or body.mesh is None:
            raise ValueError("Ground or empty bodies cannot participate in boolean union.")

        world_mesh = body.mesh.copy()
        world_mesh = world_mesh.extract_surface(algorithm='dataset_surface').triangulate().clean()

        world_matrix = np.eye(4)
        world_matrix[:3, :3] = body.principal_axes
        world_matrix[:3, 3] = body.cog * MMtoM
        world_mesh.transform(world_matrix, inplace=True)

        return world_mesh.extract_surface(algorithm='dataset_surface').triangulate().clean()

    def _polydata_to_trimesh(self, polydata):
        """Converts a triangulated PyVista surface into a watertight trimesh when possible."""
        if polydata is None:
            return None

        surface = polydata.extract_surface(algorithm='dataset_surface').triangulate().clean()
        if surface.n_cells == 0 or surface.faces.size == 0:
            return None

        faces = surface.faces.reshape((-1, 4))[:, 1:4]
        mesh = trimesh.Trimesh(vertices=np.array(surface.points), faces=faces, process=True)

        if mesh.volume < 0.0:
            flipped_faces = np.fliplr(mesh.faces)
            mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=flipped_faces, process=True)

        return mesh

    def _body_to_world_trimesh(self, body):
        """Builds a world-space trimesh solid from the current body pose."""
        return self._polydata_to_trimesh(self._body_to_world_polydata(body))

    def _create_gravity_force_for_body(self, body, enabled=None, visible=None):
        """Creates the standard gravity force for a body using the current project gravity state."""
        if body.is_ground:
            return None

        if any(f.parent_body == body and getattr(f, 'is_gravity', False) for f in self.forces_list):
            return None

        if enabled is None:
            enabled = self.ui.chkEnabledGravity.isChecked()
        if visible is None:
            visible = self.ui.chkVisibleGravity.isChecked()

        grav_force = Force(
            name=f"Grav_{body.name}",
            force_type=ForceType.FORCE,
            parent_body=body,
            fixed_in=ForceFrame.SPACE_FIXED,
            position=[0.0, 0.0, 0.0],
            vector=self.global_gravity.copy(),
            plotter=self.plotter,
        )

        grav_force.is_gravity = True
        grav_force.base_vector = self.global_gravity.copy()
        grav_force.base_color = "limegreen"
        grav_force.enabled = enabled
        grav_force.visible = visible

        for act in grav_force.actors:
            act.prop.color = "limegreen"

        current_scale = self.rframes[0].base_scale if self.rframes else 10.0
        grav_force.update_transform(current_scale)
        grav_force.set_visible(visible)
        self.forces_list.append(grav_force)
        return grav_force

    def _build_union_trimesh(self, body_i, body_j):
        """Builds a boolean-unioned trimesh, preferring Manifold when available."""
        mesh_i_tm = self._body_to_world_trimesh(body_i)
        mesh_j_tm = self._body_to_world_trimesh(body_j)
        if mesh_i_tm is None or mesh_j_tm is None:
            raise ValueError("Failed to prepare one or both bodies for boolean union.")

        tol_volume = 1e-12

        try:
            import manifold3d  # noqa: F401

            intersection_geom = trimesh.boolean.intersection([mesh_i_tm, mesh_j_tm], engine='manifold')
            if intersection_geom is None or intersection_geom.is_empty or abs(intersection_geom.volume) <= tol_volume:
                return None, "no_intersection"

            union_geom = trimesh.boolean.union([mesh_i_tm, mesh_j_tm], engine='manifold')
            if union_geom is None or union_geom.is_empty:
                raise ValueError("Manifold boolean union returned an empty mesh.")

            union_geom = trimesh.Trimesh(vertices=union_geom.vertices, faces=union_geom.faces, process=True)
            if union_geom.volume < 0.0:
                union_geom = trimesh.Trimesh(vertices=union_geom.vertices, faces=np.fliplr(union_geom.faces), process=True)

            if not union_geom.is_watertight or abs(union_geom.volume) <= tol_volume:
                raise ValueError("Manifold boolean union returned a non-watertight or zero-volume mesh.")

            return union_geom, "manifold"

        except Exception as manifold_exc:
            logging.warning(f"Manifold boolean path unavailable or failed: {manifold_exc}")

        mesh_i = self._body_to_world_polydata(body_i)
        mesh_j = self._body_to_world_polydata(body_j)

        intersection_surface = mesh_i.boolean_intersection(mesh_j)
        intersection_geom = self._polydata_to_trimesh(intersection_surface)
        if intersection_geom is None or abs(intersection_geom.volume) <= tol_volume:
            return None, "no_intersection"

        union_surface = mesh_i.boolean_union(mesh_j)
        union_geom = self._polydata_to_trimesh(union_surface)
        if union_geom is None or not union_geom.is_watertight or abs(union_geom.volume) <= tol_volume:
            raise ValueError("PyVista boolean union produced an invalid mesh.")

        return union_geom, "pyvista"

    def _create_body_from_trimesh(self, geom, body_name, color="lightblue", density=DEFAULT_DENSITY, reset_camera=True):
        """Wraps a trimesh solid into the standard body, CoG RF, and gravity pipeline."""
        faces_padded = np.insert(geom.faces, 0, 3, axis=1)
        pv_mesh = pv.PolyData(geom.vertices, faces_padded.flatten())
        pv_mesh = pv_mesh.clean().triangulate().compute_normals(split_vertices=True, feature_angle=60)

        actor = self.plotter.add_mesh(
            pv_mesh,
            color=color,
            show_edges=self.edges_visible,
            pickable=True,
            smooth_shading=True,
        )
        tree_item = QTreeWidgetItem(self.node_bodies, [body_name])

        new_body = RigidBody(body_name, geom.copy(), pv_mesh, actor, tree_item, density=density)
        new_body.base_color = color
        new_body.center_and_align_mesh()

        self.physics_bodies[body_name] = new_body
        self.body_counter += 1

        rf_name = f"RF_CoG_{body_name}"
        cog_rf = RFrame(
            name=rf_name,
            position=new_body.cog.copy(),
            orientation=new_body.pos_angles.copy(),
            transform_matrix=new_body.principal_axes.copy(),
            plotter=self.plotter,
            parent_body=new_body,
            is_cog=True,
        )
        self.rframes.append(cog_rf)
        QTreeWidgetItem(self.node_rframes, [rf_name])

        self._create_gravity_force_for_body(new_body)

        self.node_bodies.setExpanded(True)
        self.node_rframes.setExpanded(True)
        self.update_rframe_scales()

        if reset_camera:
            self.plotter.reset_camera()

        self.ui.treeHierarchy.blockSignals(True)
        self.ui.treeHierarchy.setCurrentItem(tree_item)
        self.ui.treeHierarchy.blockSignals(False)
        self.on_tree_selected()

        if hasattr(self, 'invalidate_results'):
            self.invalidate_results()

        return new_body

    def unite_bodies_from_ui(self):
        """Builds a new body from the boolean union of two existing rigid bodies."""
        body_i_name = self.ui.Edit_Body_I_Boolean.text().strip()
        body_j_name = self.ui.Edit_Body_J_Boolean.text().strip()

        if not body_i_name or not body_j_name:
            QMessageBox.warning(self, "Boolean Union", "Please select Body I and Body J first.")
            return

        if body_i_name == body_j_name:
            QMessageBox.warning(self, "Boolean Union", "Please select two different bodies.")
            return

        body_i = self.physics_bodies.get(body_i_name)
        body_j = self.physics_bodies.get(body_j_name)
        if body_i is None or body_j is None:
            QMessageBox.warning(self, "Boolean Union", "One or both selected bodies do not exist.")
            return

        if body_i.is_ground or body_j.is_ground:
            QMessageBox.warning(self, "Boolean Union", "Ground cannot be used in boolean union.")
            return

        if abs(body_i.density - body_j.density) > 1e-9:
            print(
                f"Warning: Bodies '{body_i.name}' and '{body_j.name}' have different densities. "
                f"Using the density of '{body_i.name}' for the united body."
            )

        try:
            union_geom, engine_name = self._build_union_trimesh(body_i, body_j)
            if union_geom is None:
                QMessageBox.information(
                    self,
                    "Boolean Union",
                    "Selected bodies do not intersect. No united body was created.",
                )
                return

            new_name = self._generate_unique_body_name("Union")
            new_body = self._create_body_from_trimesh(
                union_geom,
                new_name,
                color="lightblue",
                density=body_i.density,
                reset_camera=True,
            )
            print(f"Successfully united '{body_i.name}' and '{body_j.name}' into '{new_body.name}' using {engine_name}.")

        except Exception as exc:
            QMessageBox.warning(
                self,
                "Boolean Union",
                f"Failed to unite the selected bodies:\n{exc}",
            )
        
    def prepare_new_gear(self, gear_idx):
        """ Prepares the UI for defining a brand new gear of the selected type. """ 
        self.clear_selection()
        
        # Clear the Reference Frame text box to prevent accidental overlap
        if hasattr(self.ui, 'Edit_RFGear'):
            self.ui.Edit_RFGear.setText("")
        
        # Safely set the combo box to the requested gear type
        self.ui.cmbGearType.blockSignals(True)
        self.ui.cmbGearType.setCurrentIndex(gear_idx)
        self.ui.cmbGearType.blockSignals(False)
        
        # Force the UI to update the dynamic dimension states (enables/disables specific inputs!)
        self.on_gear_type_changed(gear_idx)
        
        # Display the Dock and switch to Gear Page (Index 9)
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(9)       
        
    def show_GearJoint_page(self):
        """Gear Constraintproperty page is displayed""" 
        
        self.ui.Edit_GearPairName.setText("")
        self.ui.Edit_JointGear1.setText("")
        self.ui.Edit_JointGear2.setText("")
        self.ui.Edit_JointCarrier.setText("")
        self.ui.btnCreateGearPair.setEnabled(True)
        self.ui.btnUpdateGearPair.setEnabled(False) # <--- Disable Update
        
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(10)
        # We can add other actions here later!      
    
    def prepare_new_primitive(self, prim_idx):
        """ Prepares the UI for defining a brand new primitive of the selected type. """ 
        self.clear_selection()
        
        # clear_selection() zeroes EditDensity; restore the default steel density for new primitives.
        self.ui.EditDensity.setText(str(int(DEFAULT_DENSITY)))
        
        self.ui.Edit_RFPrimitive.setText("")
        self.ui.Edit_RFPrimTarget.setText("")
        self.ui.cmbRF_PrimXYZ.setCurrentIndex(2) # Default to Z
        
        # Safely set the combo box to the requested primitive type
        self.ui.cmbPrimitiveType.blockSignals(True)
        self.ui.cmbPrimitiveType.setCurrentIndex(prim_idx) 
        self.ui.cmbPrimitiveType.blockSignals(False)
        
        # Force the UI to update the dynamic dimension labels!
        self.on_primitive_type_changed(prim_idx)
        
        # Display the Dock and switch to Primitives Page (Index 11)
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(11)
    
    def on_primitive_type_changed(self, index):
        """ Dynamically updates the dimension labels and visibility based on the selected primitive type. """
        prim_type = self.ui.cmbPrimitiveType.currentText()
        
        # 1. Default state: Show all 3 dimensions
        self.ui.lblPrimDim2.setVisible(True)
        self.ui.dsbPrimDim2.setVisible(True)
        self.ui.lblPrimDim3.setVisible(True)
        self.ui.dsbPrimDim3.setVisible(True)
        self.ui.Edit_RFPrimTarget.setVisible(False)  # Hide the target RF by default 
        self.ui.lblPrimRFTarget.setVisible(False)
        
        # 2. Update text and hide unused parameters
        if "Box" in prim_type:
            self.ui.lblPrimDim1.setText("Length (X), mm")
            self.ui.lblPrimDim2.setText("Width (Y), mm")
            self.ui.lblPrimDim3.setText("Height (Z), mm")
            # Default Box dimensions
            self.ui.dsbPrimDim1.setValue(50.0)
            self.ui.dsbPrimDim2.setValue(50.0)
            self.ui.dsbPrimDim3.setValue(50.0)
            
        elif "Cylinder" in prim_type or "Tube" in prim_type:
            self.ui.lblPrimDim1.setText("Outer Radius, mm")
            self.ui.lblPrimDim2.setText("Inner Radius, mm")
            self.ui.lblPrimDim3.setText("Height, mm")
            # Default Cylinder dimensions
            self.ui.dsbPrimDim1.setValue(25.0)
            self.ui.dsbPrimDim2.setValue(15.0)
            self.ui.dsbPrimDim3.setValue(50.0)
            
        elif "Sphere" in prim_type:
            self.ui.lblPrimDim1.setText("Radius, mm")
            # Default Sphere dimensions
            self.ui.dsbPrimDim1.setValue(25.0)
            # Hide Dimensions 2 and 3
            self.ui.lblPrimDim2.setVisible(False)
            self.ui.dsbPrimDim2.setVisible(False)
            self.ui.lblPrimDim3.setVisible(False)
            self.ui.dsbPrimDim3.setVisible(False)
            
        elif "Prism" in prim_type:
            self.ui.lblPrimDim1.setText("Number of Sides (n)")
            self.ui.lblPrimDim2.setText("Circum-Radius, mm")
            self.ui.lblPrimDim3.setText("Height, mm")
            # Default Prism dimensions
            self.ui.dsbPrimDim1.setValue(6)
            self.ui.dsbPrimDim2.setValue(25.0)
            self.ui.dsbPrimDim3.setValue(50.0)

        elif "Torus" in prim_type:
            self.ui.lblPrimDim1.setText("Major Radius, mm")
            self.ui.lblPrimDim2.setText("Minor Radius, mm")
            # Default Torus dimensions
            self.ui.dsbPrimDim1.setValue(25.0)
            self.ui.dsbPrimDim2.setValue(10.0)
            # Hide Dimension 3
            self.ui.lblPrimDim3.setVisible(False)
            self.ui.dsbPrimDim3.setVisible(False)
            
        elif "Cone" in prim_type:
            self.ui.lblPrimDim1.setText("Bottom Radius, mm")
            self.ui.lblPrimDim2.setText("Top Radius, mm")
            self.ui.lblPrimDim3.setText("Height, mm")
            # Default Cone dimensions
            self.ui.dsbPrimDim1.setValue(25.0)
            self.ui.dsbPrimDim2.setValue(15.0)
            self.ui.dsbPrimDim3.setValue(50.0)

        elif "Link" in prim_type:
            self.ui.lblPrimDim1.setText("Cylinder Radius, mm")
            self.ui.lblPrimDim2.setText("Sphere Radius, mm")
            self.ui.lblPrimDim3.setText("Length, mm")
            # Default Link dimensions
            self.ui.dsbPrimDim1.setValue(2.0)
            self.ui.dsbPrimDim2.setValue(5.0)
            self.ui.dsbPrimDim3.setValue(50.0)
            self.ui.Edit_RFPrimTarget.setVisible(True)  # Unhide the target RF for Link
            self.ui.lblPrimRFTarget.setVisible(True)
                           
    def update_speed_label(self, value):
        """ Updates the textbox dynamically as the user drags the speed slider. """
        self.ui.Edit_AnimationSpeed.setText(f"{value}%")

    def run_animation(self):
        """ Clamps the FPS, calculates the real-time interval, and starts the timer. """
        if not hasattr(self, 'solver') or not hasattr(self.solver, 'simulation_history'):
            print("Warning: Please run the solver before playing the animation.")
            return
            
        # Parse and clamp FPS strictly between 5 and 60
        try:
            fps = int(self.ui.Edit_FPS.text())
        except ValueError:
            fps = 30
            
        fps = max(5, min(60, fps))
        self.ui.Edit_FPS.setText(str(fps)) # Fix the UI if user typed a strange value
        
        interval_ms = int(1000.0 / fps)
        self.playback_timer.start(interval_ms)

    def invalidate_results(self, *args, **kwargs):
        """ 
        Phase 3: The 'Dirty Model' Failsafe. 
        Wipes simulation data and locks playback/export UI if the physical model is modified. 
        """
        # --- Prevent double-firing if the data is already wiped! ---
        if getattr(self, 'solver', None) is None:
            return
        
        # 1. Stop animation if it is currently running
        if hasattr(self, 'playback_timer') and self.playback_timer.isActive():
            self.playback_timer.stop()
            
        # 2. Rewind visuals to t=0
        self.playback_time = 0.0
        if hasattr(self, 'render_playback_frame'):
            self.render_playback_frame()
            
        # 3. Destroy the invalidated mathematical results (Prevents saving bad data!)
        self.solver = None 
        
        # 4. Lock the Playback UI
        self.ui.btnRunAnimation.setEnabled(False)
        self.ui.btnPauseAnimation.setEnabled(False)
        self.ui.btnStopAnimation.setEnabled(False)
        self.ui.btnStepForward.setEnabled(False)
        self.ui.btnStepBackward.setEnabled(False)
        
        # 5. Lock the CSV Export Button
        if hasattr(self.ui, 'btnExportCSV'):
            self.ui.btnExportCSV.setEnabled(False)
            self.ui.btnTelemetry.setEnabled(False)
        # 6. Reset UI Time Label
        if hasattr(self.ui, 'lblAnimationTime'):
            self.ui.lblAnimationTime.setText("Time: 0.000 s")
            
        # Only print if we actually deleted something (prevents log spam)
        if hasattr(self, '_results_were_valid') and self._results_were_valid:
            print("Model modified: Results invalidated and animation locked. Please solve again.")
            self._results_were_valid = False

    def pause_animation(self):
        """ Freezes the animation exactly where it is. """
        self.playback_timer.stop()

    def stop_animation(self):
        """ Stops the timer and violently snaps the universe back to t=0. """
        self.playback_timer.stop()
        self.playback_time = 0.0
        self.render_playback_frame()

    def on_playback_tick(self):
        """ Triggered by QTimer. Calculates how much simulation time passed this frame. """
        fps = int(self.ui.Edit_FPS.text())
        speed_pct = self.ui.hslAnimSpeed.value() / 100.0
        
        # How much SIMULATION time passes in one visual frame?
        real_time_step = 1.0 / fps
        sim_time_step = real_time_step * speed_pct
        
        self.playback_time += sim_time_step
        self.render_playback_frame()

    def step_forward_animation(self):
        """ Pauses auto-playback and steps the animation forward by exactly one calculated simulation frame. """
        if not hasattr(self, 'solver') or getattr(self.solver, 'simulation_history', None) is None:
            return
            
        self.pause_animation() # Stop auto-playback if it is running
        
        try:
            fps = int(self.ui.Edit_FPS.text())
        except ValueError:
            fps = 30
            
        speed_pct = self.ui.hslAnimSpeed.value() / 100.0
        sim_time_step = (1.0 / fps) * speed_pct
        
        # Calculate maximum possible time from the recorded history
        max_idx = len(self.solver.simulation_history) - 1
        max_time = max_idx * self.simulation_dt
        
        self.playback_time += sim_time_step
        
        # Prevent stepping past the end of the simulation
        if self.playback_time > max_time:
            self.playback_time = max_time
            
        self.render_playback_frame()

    def step_backward_animation(self):
        """ Pauses auto-playback and rewinds the animation by exactly one calculated simulation frame. """
        if not hasattr(self, 'solver') or getattr(self.solver, 'simulation_history', None) is None:
            return
            
        self.pause_animation() # Stop auto-playback if it is running
        
        try:
            fps = int(self.ui.Edit_FPS.text())
        except ValueError:
            fps = 30
            
        speed_pct = self.ui.hslAnimSpeed.value() / 100.0
        sim_time_step = (1.0 / fps) * speed_pct
        
        self.playback_time -= sim_time_step
        
        # Prevent stepping backwards past t=0
        if self.playback_time < 0.0:
            self.playback_time = 0.0
            
        self.render_playback_frame()

    def render_playback_frame(self):
        """ 
        Finds the correct recorded state for self.playback_time, unpacks it, 
        and pushes it to the GPU via Direct Matrix updates.
        """
        # --- Instantly abort if the solver memory is wiped or missing! ---
        if getattr(self, 'solver', None) is None or getattr(self.solver, 'simulation_history', None) is None:
            return
        if not hasattr(self, 'solver'): return
        
        # 1. Find the closest row in the history array
        row_idx = int(self.playback_time / self.simulation_dt)
        max_idx = len(self.solver.simulation_history) - 1
        
        if row_idx >= max_idx:
            row_idx = max_idx
            self.playback_timer.stop()
            
        # 2. Unpack mathematical state from the 1D Array
        state_vector = self.solver.simulation_history[row_idx]
        self.solver.unpack_state(state_vector)
        
        # 3. Push math to the PyVista GPU Matrices
        for body in self.physics_bodies.values():
            if not body.is_ground:
                body.update_graphics_matrix(body.cog, body.principal_axes)
                
        # --- STEP 2 UPGRADE: Sync CoG Reference Frames! ---
        for rf in self.rframes:
            if rf.is_cog and not rf.parent_body.is_ground:
                # Copy the exact physics state from the parent body to the RF
                rf.position = rf.parent_body.cog
                rf.transform_matrix = rf.parent_body.principal_axes
                rf.orientation = rf.parent_body.pos_angles
                rf.update_transform()
                
        # --- STEP 1 UPGRADE: Fix disappearing forces & exploding joints! ---
        # Dynamically grab the exact scale currently used by the UI camera zoom
        current_scale = self.rframes[0].base_scale if self.rframes else 10.0
        
        for force in self.forces_list:
            # --- Pass playback time so arrows pulse and flip dynamically! ---
            force.update_transform(current_scale, t=self.playback_time) # current_scale * 1.5
            
        for joint in self.joints_list:
            # Joints scale correctly and inherently track their parent's CoG!
            joint.update_transform(current_scale) 
            
        # --- Animate the Springs! ---
        for spring in self.springs_list:
            spring.update_transform(current_scale)
            
        # --- Animate Bushings ---
        for bushing in getattr(self, 'bushings_list', []):
            bushing.update_transform(current_scale)
                    
        # 4. Update Time Label and Render
        self.ui.lblAnimationTime.setText(f"Time: {self.playback_time:.3f} s")
        self.plotter.render()
    
    def export_video(self):
        """ 
        Renders a high-quality, frame-perfect video of the simulation. 
        Incorporates UI animation speed and maximizes render quality.
        """
        if getattr(self, 'solver', None) is None or getattr(self.solver, 'simulation_history', None) is None:
            QMessageBox.warning(self, "No Data", "Please run or load a simulation before exporting a video.")
            return
            
        # --- Offer WebM as the primary, patent-free default! ---
        file_filter = "WebM Video (*.webm);;MP4 Video (*.mp4);;All Files (*)"
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Animation Video", self.working_dir, file_filter)
        
        if not filepath: return
        
        # Enforce extension based on user selection
        if not (filepath.endswith('.mp4') or filepath.endswith('.webm')): 
            if "MP4" in _:
                filepath += '.mp4'
            else:
                filepath += '.webm'
        
        # 1. Determine Output Framerate from UI
        try:
            target_fps = int(self.ui.Edit_FPS.text())
        except ValueError:
            target_fps = 30
        target_fps = max(10, min(60, target_fps)) # Clamp between 10 and 60 FPS
        
        # --- Extract the UI Animation Speed ---
        speed_pct = self.ui.hslAnimSpeed.value() / 100.0
        
        # 2. Calculate the array step size to match the video framerate AND user speed
        video_dt = (1.0 / target_fps) * speed_pct
        sim_dt = self.simulation_dt
        step_size = max(1, int(round(video_dt / sim_dt)))
        
        history_len = len(self.solver.simulation_history)
        frame_indices = list(range(0, history_len, step_size))
        
        # --- Dynamically select codec and pass explicit FFmpeg quality parameters! ---
        if filepath.endswith('.webm'):
            video_codec = 'libvpx-vp9' 
            # VP9 requires explicit CRF and a 0 bitrate to unlock max visual quality
            writer_kwargs = {'ffmpeg_params': ['-crf', '15', '-b:v', '0']}
        else:
            video_codec = 'libx264'    
            # H.264 perfectly understands PyVista's native quality=10 parameter
            writer_kwargs = {} 
            
        try:
            # 3. Lock UI & Initialize PyVista Movie Writer
            self.ui.progressBar.setValue(0)
            
            # Pass the codec and the kwargs (using **) to properly instruct FFmpeg!
            self.plotter.open_movie(
                filepath, 
                framerate=target_fps, 
                quality=10, 
                codec=video_codec, 
                **writer_kwargs
            )
            
            # Extract standard UI scale for visuals
            current_scale = self.rframes[0].base_scale if self.rframes else 10.0
            
            # 4. The Mathematical Render Loop
            for count, row_idx in enumerate(frame_indices):
                # Unpack mathematical state from the 1D Array
                state_vector = self.solver.simulation_history[row_idx]
                self.solver.unpack_state(state_vector)
                
                # --- Calculate exact time for this frame ---
                current_t = row_idx * self.simulation_dt
                
                # Push math to the PyVista GPU Matrices
                for body in self.physics_bodies.values():
                    if not body.is_ground:
                        body.update_graphics_matrix(body.cog, body.principal_axes)
                        
                for rf in self.rframes:
                    if rf.is_cog and not rf.parent_body.is_ground:
                        rf.position = rf.parent_body.cog
                        rf.transform_matrix = rf.parent_body.principal_axes
                        rf.orientation = rf.parent_body.pos_angles
                        rf.update_transform()
                        
                for force in self.forces_list: 
                    # --- Pass time to the video renderer! ---
                    force.update_transform(current_scale, t=current_t)
                
                for joint in getattr(self, 'joints_list', []): joint.update_transform(current_scale)
                for spring in getattr(self, 'springs_list', []): spring.update_transform(current_scale)
                for bushing in getattr(self, 'bushings_list', []): bushing.update_transform(current_scale)
                
                # Write the exact frame directly into the video file
                self.plotter.render()
                self.plotter.write_frame()
                
                # Update UI Progress Bar smoothly
                progress = int((count / len(frame_indices)) * 100)
                self.ui.progressBar.setValue(progress)
                QApplication.processEvents() 
                
            # 5. Finalize the video file
            self.plotter.mwriter.close()
            self.ui.progressBar.setValue(100)
            
            QMessageBox.information(self, "Success", f"Video successfully exported to:\n{filepath}")
            
        except AttributeError:
            QMessageBox.critical(self, "Export Error", "Failed to start the video writer. Ensure 'imageio' and 'imageio-ffmpeg' are installed via your terminal:\npip install imageio imageio-ffmpeg")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred during video export:\n{str(e)}")
        finally:
            self.ui.progressBar.setValue(0)
            # Rewind the scene cleanly back to t=0
            self.playback_time = 0.0
            self.render_playback_frame()
        
    def is_body_constrained(self, body_name):
        """ Checks if a body is part of any existing joint or bushing constraint. """
        for j in self.joints_list:
            if j.body_i.name == body_name or j.body_j.name == body_name:
                return True
                
        # --- Check if locked by a Bushing ---
        if hasattr(self, 'bushings_list'):
            for b in self.bushings_list:
                if b.body_i.name == body_name or b.body_j.name == body_name:
                    return True
                    
        return False
    # ==========================================
    # --- SIMULATION CONTROL ---
    # ==========================================
    def on_solver_method_changed(self, index):
        """ Hides advanced SciPy settings if a Custom Fixed-Step integrator is selected. """
        # Indices 0, 1, 2 are Custom Solvers. Indices 3+ are SciPy Adaptive Solvers.
        is_adaptive = (index > 2)
        
        # Enable or Show the frame based on the selection
        if hasattr(self.ui, 'frmAdvancedSolver'):
            self.ui.frmAdvancedSolver.setEnabled(is_adaptive)
            # Optional: self.ui.frmAdvancedSolver.setVisible(is_adaptive)
    
    def run_physics_simulation(self):
        """ Reads the UI parameters, initializes the solver, and crunches the math. """
        # --- Rewind to t=0 before starting a new simulation ---
        # If the user played an animation, the bodies are stuck at t_end.
        # We must rewind the math memory and visuals back to the original initial state!
        
        # Check for 'simulation_history' instead of 'Y_history'!
        if hasattr(self, 'solver') and self.solver and getattr(self.solver, 'simulation_history', None) is not None:
            self.playback_time = 0.0
            self.render_playback_frame()
            print("Resetting physical state to t=0 from previous simulation...")
            
        # Return the system to initial state before the simulation starts (it does not work if simulation crashed)
        # self.stop_animation()
        
        try:
            # Read UI Inputs
            t_end = parse_ui_float(self.ui.Edit_SimulationTime.text())
            steps_per_sec = int(self.ui.Edit_StepsPerSec.text())
            
            if t_end <= 0 or steps_per_sec <= 0:
                print("Error: Time and Steps must be greater than zero.")
                return
                
            dt = 1.0 / steps_per_sec
            
            # --- Extract Baumgarte Parameters ---
            try:
                # We assume alpha = beta for critical damping
                baumgarte_val = parse_ui_float(self.ui.Edit_Alpha_Beta.text())
            except ValueError:
                baumgarte_val = 20.0 # Safe fallback
                self.ui.Edit_Alpha_Beta.setText("20")
                
            # --- Extract Tikhonov Compliance (Epsilon) ---
            compliance_map = {0: 0.0, 1: 1e-5, 2: 1e-7, 3: 1e-9, 4: 1e-11}
            compliance_idx = self.ui.cmbSolverCompliance.currentIndex()
            epsilon_val = compliance_map.get(compliance_idx, 1e-7) 
            
        except ValueError:
            print("Error: Invalid numerical input for simulation parameters.")
            return

        print(f"Initializing Solver: T_end={t_end}s, dt={dt}s, Alpha/Beta={baumgarte_val}, Epsilon={epsilon_val}")
        
        # 1. Lock UI to prevent user interference during math
        self.ui.btnSolve.setEnabled(False)
        self.ui.progressBar.setValue(0)
        
        # 2. Instantiate the Mathematical Solver
        self.solver = MBSolver(
            self.physics_bodies, 
            self.forces_list, 
            self.joints_list,
            self.springs_list + self.bushings_list, # <--- Give the solver both lists!,
            self.contact_pairs,
            gear_pairs=getattr(self, 'gear_pairs_list', []),
            motions_list=getattr(self, 'motions_list', []),
            epsilon=epsilon_val,
            alpha=baumgarte_val,
            beta=baumgarte_val
        )
        
        # --- Smart extraction of Advanced Tolerances ---
        try:
            # Slices "1e-3 (Default)" -> "1e-3" -> 0.001
            r_str = self.ui.cmbRtol.currentText().split()[0]
            a_str = self.ui.cmbAtol.currentText().split()[0]
            rtol_val = float(r_str)
            atol_val = float(a_str)
            
            # Dynamic max_step based on dt!
            max_step_idx = self.ui.cmbMaxStep.currentIndex()
            if max_step_idx == 0:   max_step_val = np.inf
            elif max_step_idx == 1: max_step_val = dt
            elif max_step_idx == 2: max_step_val = dt / 2.0
            else:                   max_step_val = dt / 10.0
                
        except Exception as e:
            print("UI extraction error, defaulting tolerances.")
            rtol_val, atol_val, max_step_val = 1e-3, 1e-6, np.inf

        # --- Extract Integrator Selection ---
        from integrators import CustomRK4, CustomEuler, CustomSymplecticEuler, SciPyIntegrator
        
        integrator_idx = self.ui.cmbSolverMethod.currentIndex()
        if integrator_idx == 0:   active_integrator = CustomRK4()
        elif integrator_idx == 1: active_integrator = CustomEuler()
        elif integrator_idx == 2: active_integrator = CustomSymplecticEuler()
        
        # --- THE UPGRADE: Pass the new kwargs to all SciPy Integrators! ---
        elif integrator_idx == 3: active_integrator = SciPyIntegrator(method='RK45', rtol=rtol_val, atol=atol_val, max_step=max_step_val)
        elif integrator_idx == 4: active_integrator = SciPyIntegrator(method='RK23', rtol=rtol_val, atol=atol_val, max_step=max_step_val)
        elif integrator_idx == 5: active_integrator = SciPyIntegrator(method='DOP853', rtol=rtol_val, atol=atol_val, max_step=max_step_val)
        elif integrator_idx == 6: active_integrator = SciPyIntegrator(method='Radau', rtol=rtol_val, atol=atol_val, max_step=max_step_val)
        elif integrator_idx == 7: active_integrator = SciPyIntegrator(method='BDF', rtol=rtol_val, atol=atol_val, max_step=max_step_val)
        elif integrator_idx == 8: active_integrator = SciPyIntegrator(method='LSODA', rtol=rtol_val, atol=atol_val, max_step=max_step_val)
        else:                     active_integrator = CustomRK4()
        
        # 3. Create the UI Callback
        def update_progress(percent):
            self.ui.progressBar.setValue(percent)
            QApplication.processEvents() 

        # 4. Run the simulation
        backup_Y = None
        try:
            logging.info(f"User requested solve: T={t_end}s, dt={dt}s")
            
            # ========================================================================
            # --- THE NEW UPGRADE: Apply Initial Velocities Before the Solver Starts! ---
            # ========================================================================
            for body in self.physics_bodies.values():
                if not body.is_ground:
                    body.reset_velocities()
                    
            # --- THE FIX: Take a Snapshot of the initial physical state! ---
            backup_Y = self.solver.pack_state()
            
            # Run the mathematical solver
            self.solver.run_simulation(
                t_end, 
                dt, 
                integrator=active_integrator, 
                progress_callback=update_progress
            )
            
            print("Simulation solved and recorded successfully! Ready for playback.")
            
            # --- Automatic CSV Export is deactivated
            # csv_path = os.path.join(self.output_dir, "simulation_results.csv")
            # self.solver.export_csv(csv_path, dt)
            
            self._results_were_valid = True
            # --- Unlock animation controls! ---
            self.ui.btnRunAnimation.setEnabled(True)
            self.ui.btnPauseAnimation.setEnabled(True)
            self.ui.btnStopAnimation.setEnabled(True)
            self.ui.btnStepForward.setEnabled(True)  
            self.ui.btnStepBackward.setEnabled(True)
            
            # --- Re-enable the CSV Export button! ---
            if hasattr(self.ui, 'btnExportCSV'):
                self.ui.btnExportCSV.setEnabled(True)
                self.ui.btnTelemetry.setEnabled(True)
            # Reset playback clock and store dt
            self.simulation_dt = dt
            self.playback_time = 0.0
            self.render_playback_frame() # Snap to t=0 on success
            
        except Exception as e:
            logging.error(f"Simulation Crashed: {e}", exc_info=True)
            print(f"Simulation Crashed: {e}")
            
            # --- Attempt a Rescue Export of partial data! ---
            if hasattr(self.solver, 'simulation_history') and len(self.solver.simulation_history) > 0:
                try:
                    print("Attempting to rescue partial simulation data...")
                    rescue_csv_path = os.path.join(self.output_dir, "simulation_results_CRASH.csv")
                    self.solver.export_csv(rescue_csv_path, dt)
                    print(f"Partial data successfully rescued to '{rescue_csv_path}'!")
                except Exception as csv_e:
                    print(f"Could not export partial data: {csv_e}")
            
            # --- Failsafe Restore on Crash ---
            if backup_Y is not None:
                print("Failsafe: Restoring pre-simulation initial conditions...")
                
                # 1. Unpack the snapshot back into the math memory
                self.solver.unpack_state(backup_Y)
                
                # 2. Push the restored math to the PyVista GPU Matrices
                for body in self.physics_bodies.values():
                    if not body.is_ground:
                        body.update_graphics_matrix(body.cog, body.principal_axes)
                        
                # 3. Sync CoG Reference Frames
                for rf in self.rframes:
                    if rf.is_cog and not rf.parent_body.is_ground:
                        rf.position = rf.parent_body.cog
                        rf.transform_matrix = rf.parent_body.principal_axes
                        rf.orientation = rf.parent_body.pos_angles
                        rf.update_transform()
                        
                # 4. Sync Forces and Joints visuals
                current_scale = self.rframes[0].base_scale if self.rframes else 10.0
                for force in self.forces_list:
                    force.update_transform(current_scale) 
                for joint in self.joints_list:
                    joint.update_transform(current_scale)
                
                # ---  Sync Springs & Bushings on Crash Rewind ---
                for spring in self.springs_list:
                    spring.update_transform(current_scale)
                    
                # --- ADD THIS: Failsafe for Bushings ---
                for bushing in getattr(self, 'bushings_list', []):
                    bushing.update_transform(current_scale)
                    
                # 5. Force the screen to redraw
                self.plotter.render()
                
        finally:
            # Unlock UI
            self.ui.btnSolve.setEnabled(True)
            # Ensure progress bar doesn't stay stuck halfway on a crash
            self.ui.progressBar.setValue(0)
    
    def cancel_simulation(self):
        """ Sends an instant kill-signal to the mathematical solver. """
        if hasattr(self, 'solver') and self.solver:
            self.solver.cancel_flag = True
            print("Abort signal sent! Halting collision detection...")
            # self.ui.progressBar.setFormat("Aborting...")
            
     # ==========================================
     # --- JOINTS UI LOGIC ---
     # These methods handle the logic of "pushing" the currently selected Body or RF from the tree
     # into QLineEdit boxes, filling I and Anchor first, then J and Target.
     # ==========================================
    
    def export_csv_results(self):
        """ Phase 5: Optional CSV Export Triggered by the UI. """
        if not hasattr(self, 'solver') or getattr(self.solver, 'simulation_history', None) is None:
            QMessageBox.warning(self, "Export Error", "No simulation results available to export. Please run or load a simulation first.")
            return
            
        file_filter = "CSV Telemetry (*.csv);;All Files (*)"
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Simulation Telemetry", self.output_dir, file_filter)
        
        if filepath:
            if not filepath.endswith('.csv'): filepath += '.csv'
            
            # Temporarily disable the button to prevent double-clicks during export
            self.ui.btnExportCSV.setEnabled(False)
            QApplication.processEvents()
            
            try:
                self.solver.export_csv(filepath, self.simulation_dt)
                QMessageBox.information(self, "Export Success", f"Telemetry successfully exported to:\n{os.path.basename(filepath)}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"An error occurred during export:\n{str(e)}")
            finally:
                self.ui.btnExportCSV.setEnabled(True)
            
    def clean_joint_rfs_bodies(self):
        """Cleans the Bodies and RFs in the Joint ptoperty page"""
        self.ui.Edit_Body_I.setText("")
        self.ui.Edit_Body_J.setText("")
        self.ui.Edit_RF_Anchor.setText("")
        self.ui.Edit_RF_Target.setText("")
        self.ui.Edit_Joint_Name.setText("")
        self.ui.btnAddJoint.setEnabled(True)
        self.ui.cmbAnchorXYZ.setEnabled(True)

    # This method reads the UI, checks the "One Joint per Pair" rule, stamps the math using 
    # 'decoupled from RFs approach', and visualizes it.
    def add_custom_joint(self):
        """ Validates inputs, checks for redundant constraints, and creates the Joint. """
        body_i_name = self.ui.Edit_Body_I.text().strip()
        body_j_name = self.ui.Edit_Body_J.text().strip()
        anchor_name = self.ui.Edit_RF_Anchor.text().strip()
        target_name = self.ui.Edit_RF_Target.text().strip()

        if not body_i_name or not body_j_name or not anchor_name:
            print("Error: Body I, Body J, and Anchor RF are strictly required.")
            return

        # 1. Protection: Check for existing joint between this pair!
        for j in self.joints_list:
            if (j.body_i.name == body_i_name and j.body_j.name == body_j_name) or \
               (j.body_i.name == body_j_name and j.body_j.name == body_i_name):
                print(f"Warning: A joint ('{j.name}') already exists between these two bodies!")
                return

        # 2. Retrieve Objects
        b_i = self.physics_bodies.get(body_i_name)
        b_j = self.physics_bodies.get(body_j_name)
        rf_a = next((r for r in self.rframes if r.name == anchor_name), None)
        rf_t = next((r for r in self.rframes if r.name == target_name), None) if target_name else None

        if not b_i or not b_j or not rf_a:
            return

        # --- 3. Determine Joint Type from UI ComboBox ---
        type_idx = self.ui.cmbJointType.currentIndex()
        if type_idx == 0:   j_type, type_str = JointType.FIXED, "Fixed"
        elif type_idx == 1: j_type, type_str = JointType.SPHERICAL, "Spherical"
        elif type_idx == 2: j_type, type_str = JointType.REVOLUTE, "Revolute"
        elif type_idx == 3: j_type, type_str = JointType.CYLINDRICAL, "Cylindrical"
        elif type_idx == 4: j_type, type_str = JointType.PRISMATIC, "Prismatic"
        elif type_idx == 5: j_type, type_str = JointType.PLANAR, "Planar"
        else:               j_type, type_str = JointType.FIXED, "Fixed"

        auto_generated_target = False

        # --- Auto-Generate Target RF if missing! ---
        if j_type != JointType.SPHERICAL and not rf_t:
            auto_generated_target = True
            axis_choice = self.ui.cmbAnchorXYZ.currentText().strip().upper()
            
            local_vec = np.zeros(3)
            if axis_choice == 'X': local_vec[0] = 0.001
            elif axis_choice == 'Y': local_vec[1] = 0.001
            else: local_vec[2] = 0.001 
                
            global_shift = rf_a.transform_matrix @ local_vec
            new_pos = rf_a.position + global_shift
            
            counter = len(self.rframes) + 1
            # auto_rf_name = f"Target_{type_str}_{counter}"
            auto_rf_name = f"Target_{axis_choice}_{type_str}_{counter}"
            while any(r.name == auto_rf_name for r in self.rframes):
                counter += 1
                # auto_rf_name = f"Target_{type_str}_{counter}"
                auto_rf_name = f"Target_{axis_choice}_{type_str}_{counter}"
                
            rf_t = RFrame(
                name=auto_rf_name, position=new_pos,
                orientation=rf_a.orientation.copy(), 
                transform_matrix=rf_a.transform_matrix.copy(),
                plotter=self.plotter, parent_body=self.physics_bodies.get("Ground"), 
                is_cog=False
            )
            
            self.rframes.append(rf_t)

        # 4. Generate Name & Create
        counter = len(self.joints_list) + 1
        j_name = f"Jt_{type_str}_{counter}"
        
        new_joint = Joint(name=j_name, joint_type=j_type, body_i=b_i, body_j=b_j, plotter=self.plotter)
        
        # Stamp the math and discard the RF link!
        new_joint.apply_initial_rfs(anchor_rf=rf_a, target_rf=rf_t)
        # new_joint.update_transform(self.joint_base_size * 1.0) 
        
        # Extract standard UI scale for visuals
        current_scale = self.rframes[0].base_scale if self.rframes else 10.0
        new_joint.update_transform(current_scale) 
        
        self.joints_list.append(new_joint)
        
        # Add to Tree Hierarchy
        new_item = QTreeWidgetItem(self.node_joints, [new_joint.name])
        self.node_joints.setExpanded(True)
        
        # Instant Cleanup of Auto-Generated RF
        if auto_generated_target and rf_t:
            for act in rf_t.actors: self.plotter.remove_actor(act)
            self.rframes.remove(rf_t)

        # --- 5. Auto-Select the new joint and update UI ---
        self.ui.treeHierarchy.blockSignals(True)
        self.ui.treeHierarchy.setCurrentItem(new_item)
        self.ui.treeHierarchy.blockSignals(False)
        
        self.selected_joint = new_joint.name
        self.ui.Edit_Joint_Name.setText(j_name)
        # self.ui.Edit_RF_Anchor.setText("") # Disconnected
        # self.ui.Edit_RF_Target.setText("") # Disconnected
        self.ui.btnAddJoint.setEnabled(False)
        self.ui.cmbAnchorXYZ.setEnabled(True)
        
        self.update_multi_selection_visuals([new_joint.body_i.name, new_joint.body_j.name])
        self.update_rf_selection_visuals(None)
        self.update_force_selection_visuals(None)
        self.update_joint_selection_visuals(new_joint.name)
        
        self.update_rframe_scales()
        self.plotter.render()
        self.invalidate_results()
        print(f"Created {type_str} Joint: '{j_name}'")
            
     # --- END of JOINTS UI LOGIC ---
     # ==========================================   
    def update_joint_selection_visuals(self, active_name):
        """ Toggles the gold highlight for the active Joint. """
        for j in self.joints_list:
            j.set_selected(j.name == active_name)
                     
    def update_force_selection_visuals(self, active_name):
        """ Toggles the gold highlight for the active force/torque. """
        for force in self.forces_list:
            force.set_selected(force.name == active_name)
            
    def update_spring_selection_visuals(self, active_name):
        """ Toggles the gold highlight for the active Spring. """
        if hasattr(self, 'springs_list'):
            for spring in self.springs_list:
                spring.set_selected(spring.name == active_name)
        # --- Bushings ----        
        if hasattr(self, 'bushings_list'):
            for bushing in self.bushings_list:
                bushing.set_selected(bushing.name == active_name)
                               
    def update_custom_force(self):
        """ Updates the Force or Torque currently displayed in the Edit_ForceName field. """
        target_name = self.ui.Edit_ForceName.text().strip()
        if not target_name:
            print("Please select a Force or Torque to update.")
            return

        force = next((f for f in self.forces_list if f.name == target_name), None)
        if not force: return

        # --- Protection ---
        if force.is_gravity:
            print("Protection: Cannot modify auto-generated gravity vectors.")
            return
            
        # 1. Determine Type, Frame, and Speed Limits
        is_torque = (self.ui.cmbForceType.currentIndex() == 1)
        
        # We no longer strictly parse this as a float because it can be an equation!
        try:
            user_mag = parse_ui_float(self.ui.Edit_ForceValue.text())
            is_constant = True
        except ValueError:
            user_mag = 1.0 # Placeholder
            is_constant = False
            
        # --- THE UPGRADE: Convert UI Nmm to SI Nm for the solver! ---
        magnitude = user_mag / 1000.0 if is_torque else user_mag
        
        is_body_fixed = (self.ui.cmbSpaceBody.currentIndex() == 1)
        new_fixed = ForceFrame.BODY_FIXED if is_body_fixed else ForceFrame.SPACE_FIXED
        
        is_actuator = self.ui.chkActuatorMode.isChecked()
        allow_braking = self.ui.chkAllowActuatorBraking.isChecked()
        speed_max_si = 0.0
        
        if is_actuator:
            new_f_type = ForceType.E_MOTOR if is_torque else ForceType.ACTUATOR
            try:
                raw_speed = parse_ui_float(self.ui.Edit_MaxActuatorSpeed.text())
                # Convert RPM -> rad/s OR mm/s -> m/s
                speed_max_si = raw_speed * (np.pi / 30.0) if is_torque else (raw_speed / 1000.0)
                
                # Calculate and display Peak Mechanical Power (Watts)
                if is_constant:
                    peak_power = (magnitude * speed_max_si) / 4.0
                else:
                    peak_power = 0.0
                self.ui.Edit_ActPowerLimit.setText(f"{peak_power:.3f}")
                
            except ValueError:
                print("Error: Invalid numerical max speed.")
                return
        else:
            new_f_type = ForceType.TORQUE if is_torque else ForceType.FORCE
            self.ui.Edit_ActPowerLimit.setText("0.000") # Clear if not an actuator

        # 2. Reference Frame Transition Protection (Global <-> Local)
        if force.fixed_in != new_fixed:
            if new_fixed == ForceFrame.BODY_FIXED:
                force.base_vector = force.parent_body.principal_axes.T @ force.base_vector
            else:
                force.base_vector = force.parent_body.principal_axes @ force.base_vector

        # --- PRE-UPDATE TRACKING ---
        old_f_type = force.force_type

        # 3. Apply Mathematical Updates
        force.force_type = new_f_type
        force.fixed_in = new_fixed
        force.speed_max = speed_max_si
        force.allow_braking = allow_braking
        
        # --- Compile the new math expression! ---
        force.compile_expression(self.ui.Edit_ForceValue.text())

        # 4. Rebuild 3D Geometry if the fundamental type changed
        if old_f_type != new_f_type:
            # Ask PyVista to delete the old meshes (arrow/torus)
            for act in force.actors:
                self.plotter.remove_actor(act)
                
            force.actors.clear()
            force.create_visuals() # Rebuild the correct geometry

        # 5. Finalize UI and Visuals
        # force.update_transform(self.joint_base_size * 2.0)
        current_scale = self.rframes[0].base_scale if self.rframes else 1.0
        force.update_transform(current_scale)
        
        self.invalidate_results()
        self.plotter.render()
        print(f"Updated Force/Torque/Actuator '{force.name}'.")
    
    def rename_force(self):
        """ Triggers a pop-up window to safely rename the targeted Force/Torque. """
        target_name = self.ui.Edit_ForceName.text().strip()
        if not target_name:
            print("Please select a Force or Torque to rename.")
            return

        force = next((f for f in self.forces_list if f.name == target_name), None)
        if not force: return

        # --- Protections ---
        if force.is_gravity:
            print("Protection: Cannot rename auto-generated gravity vectors.")
            return

        old_name = force.name

        # 1. Trigger Pop-up
        new_name, ok = QInputDialog.getText(self, "Rename Force/Torque", "Enter new name:", text=old_name)

        # 2. Validate input
        if not ok or not new_name.strip(): return 
        new_name = new_name.strip()
        if new_name == old_name: return 

        if any(f.name == new_name for f in self.forces_list):
            QMessageBox.warning(self, "Rename Error", f"A Force/Torque with the name '{new_name}' already exists!")
            return

        # 3. Update Object and UI Box
        force.name = new_name
        self.selected_force = new_name
        self.ui.Edit_ForceName.setText(new_name)

        # 4. Update Tree Hierarchy visually
        for i in range(self.node_forces.childCount()):
            if self.node_forces.child(i).text(0) == old_name:
                self.node_forces.child(i).setText(0, new_name)
                break

        print(f"Successfully renamed Force/Torque '{old_name}' to '{new_name}'.")
    
    def on_force_type_changed(self, index):
        """ Updates the Force/Torque unit label dynamically based on ComboBox selection. """
        if index == 1:
            self.ui.lblNNm.setText('Value, Nmm')
            self.ui.btnAddForceTorque.setText('Create Torque')
            self.ui.lblSpeedUnit.setText('Max Speed, rpm')
        else:
            self.ui.lblNNm.setText('Value, N')
            self.ui.btnAddForceTorque.setText('Create Force')
            self.ui.lblSpeedUnit.setText('Max Speed, mm/s')
            
    def toggle_force_enabled(self, state):
        """ Toggles the physical state of the selected custom force. """
        if not self.selected_force: return
            
        force = next((f for f in self.forces_list if f.name == self.selected_force), None)
        if force:
            force.enabled = state
            force.visible = state # Keep internal tracker in sync
            
            if state: 
                self._auto_enable_linked_bodies(force)
            
            # --- THE FIX: Re-calculate the 3D mesh position before showing it! ---
            current_scale = self.rframes[0].base_scale if self.rframes else 10.0
            force.update_transform(current_scale)
            
            # --- THE FIX: Respect the Global Hide button ---
            if self.ui.btnHideShowObjects.isChecked():
                force.set_visible(False)
            else:
                force.set_visible(state)
            
            self.refresh_tree_visuals()
            self.plotter.render()
            
            if hasattr(self, 'invalidate_results'):
                self.invalidate_results()

    def delete_custom_force(self):
        """ Deletes the Force or Torque currently displayed in the Edit_ForceName field. """
        target_name = self.ui.Edit_ForceName.text().strip()
        if not target_name:
            print("Please select a Force or Torque to delete.")
            return

        force = next((f for f in self.forces_list if f.name == target_name), None)
        if not force: return

        # --- Protection ---
        if force.is_gravity:
            print("Protection: Cannot delete auto-generated gravity vectors.")
            return
        
        # --- THE UPGRADE: Ask for permission! ---
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete Force/Torque '{force.name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No: return
        # ----------------------------------------
        # 1. Ask the graphics card to destroy the 3D actors
        for act in force.actors:
            self.plotter.remove_actor(act)
            
        # 2. Delete from engine memory
        self.forces_list.remove(force)
        
        # 3. Delete from TreeView
        for i in range(self.node_forces.childCount()):
            if self.node_forces.child(i).text(0) == force.name:
                self.node_forces.takeChild(i)
                break
                
        # 4. Clean up UI and 3D Visuals
        self.ui.Edit_ForceName.setText("")
        self.ui.Edit_BodyForce.setText("")
        self.ui.Edit_RFForce.setText("")
        self.ui.btnAddForceTorque.setEnabled(True)
        self.ui.cmbForceAnchorXYZ.setEnabled(True)
        
        self.clear_selection()
        self.invalidate_results()
        self.plotter.render()
        print(f"Deleted Force/Torque '{force.name}'.")
        
    def update_body_properties(self):
        """ Only handles physical properties like Density now. """
        if not self.selected_body:
            return

        body = self.physics_bodies[self.selected_body]
        
        # --- Ground Protection ---
        if body.is_ground:
            print("Protection: Cannot change the density of the Ground.")
            return
        
        try:
            new_density = parse_ui_float(self.ui.EditDensity.text())
        except ValueError:
            print("Invalid density value.")
            return

        # --- THE UPGRADE: Apply to all bodies if the checkbox is ticked ---
        if self.ui.chkApplyAllDensity.isChecked():
            updated_count = 0
            for b in self.physics_bodies.values():
                if not b.is_ground:
                    b.update_density(new_density)
                    updated_count += 1
            print(f"Density updated to {new_density} kg/m³ for all {updated_count} bodies.")
        else:
            # Safely recalculate mass and inertia for just the selected body
            body.update_density(new_density)
            print(f"Density for '{body.name}' updated successfully.")
            
        # Refresh the UI text box for the currently active body
        self.display_body_properties(body)
        
        # Trigger the Dirty Model pattern (invalidate previous simulation math)
        if hasattr(self, 'invalidate_results'):
            self.invalidate_results()

    def rename_body(self):
        """ Triggers a pop-up window to safely rename the active Rigid Body. """
        if not self.selected_body:
            print("Please select a body to rename.")
            return
            
        body = self.physics_bodies[self.selected_body]
        
        # --- Ground Protection ---
        if body.is_ground:
            print("Protection: Cannot rename the Ground body.")
            return
        
        old_name = body.name
        
        # 1. Trigger the Pop-up Window
        new_name, ok = QInputDialog.getText(self, "Rename Body", "Enter new name:", text=old_name)
        
        # 2. Validate the user input
        if not ok or not new_name.strip():
            return # User clicked Cancel or entered empty text
            
        new_name = new_name.strip()
        if new_name == old_name:
            return # No change made
            
        if new_name in self.physics_bodies:
            QMessageBox.warning(self, "Rename Error", f"A body with the name '{new_name}' already exists!")
            return

        # 3. Update associated RFrame names
        old_rf_name = f"RF_CoG_{old_name}"
        new_rf_name = f"RF_CoG_{new_name}"
        
        for rf in self.rframes:
            if rf.name == old_rf_name:
                rf.name = new_rf_name
                # Find and update the tree item for the RF
                for i in range(self.node_rframes.childCount()):
                    if self.node_rframes.child(i).text(0) == old_rf_name:
                        self.node_rframes.child(i).setText(0, new_rf_name)
                        break
                break

        # --- Update associated Gravity Force name! ---
        old_grav_name = f"Grav_{old_name}"
        new_grav_name = f"Grav_{new_name}"
        
        for force in self.forces_list:
            if force.name == old_grav_name and getattr(force, 'is_gravity', False):
                force.name = new_grav_name
                # Find and update the tree item for the Force
                for i in range(self.node_forces.childCount()):
                    if self.node_forces.child(i).text(0) == old_grav_name:
                        self.node_forces.child(i).setText(0, new_grav_name)
                        break
                break
        # ----------------------------------------------------
        
        # 4. Update the Physics Engine Dictionary Keys
        self.physics_bodies[new_name] = self.physics_bodies.pop(old_name)
        
        # 5. Update the Body Object and Tree Hierarchy
        body.name = new_name
        body.tree_item.setText(0, new_name)
        self.selected_body = new_name
        
        # 6. Refresh UI displays
        self.ui.EditName.setText(new_name)
        self.display_body_properties(body)
        
        print(f"Successfully renamed '{old_name}' to '{new_name}'.")
    
    def assign_initial_velocities(self):
        """ Reads the UI, converts linear mm/s to m/s, and assigns initial velocities. """
        if not self.selected_body:
            print("Please select a Rigid Body to assign velocities.")
            return

        body = self.physics_bodies[self.selected_body]
        if body.is_ground:
            print("Protection: Cannot assign velocities to the Ground body.")
            QMessageBox.warning(self, "Protection", "Cannot assign initial momentum or velocity to the mathematical Ground anchor.")
            return

        try:
            # Linear (UI: mm/s -> Solver: m/s)
            vx0 = parse_ui_float(self.ui.Edit_Vx0.text()) / 1000.0
            vy0 = parse_ui_float(self.ui.Edit_Vy0.text()) / 1000.0
            vz0 = parse_ui_float(self.ui.Edit_Vz0.text()) / 1000.0

            # Angular (UI: rad/s -> Solver: rad/s)
            wx0 = parse_ui_float(self.ui.Edit_Wx0.text())
            wy0 = parse_ui_float(self.ui.Edit_Wy0.text())
            wz0 = parse_ui_float(self.ui.Edit_Wz0.text())

            # Store as initial conditions
            body.initial_velocity = np.array([vx0, vy0, vz0])
            body.initial_angular_velocity = np.array([wx0, wy0, wz0])

            # Instantly apply them to the current physical state
            body.reset_velocities()

            print(f"Initial velocities assigned to '{body.name}'.")
            
            if hasattr(self, 'invalidate_results'):
                self.invalidate_results()

        except ValueError:
            print("Error: Invalid numerical input for velocities.")
    
    def fit_all_camera(self):
        """ Resets the camera to fit all visible actors in the 3D viewport. """
        self.plotter.reset_camera()
        self.plotter.render()
        print("Viewport zoom adjusted to fit all bodies.")

    def delete_body(self):
        """ Permanently deletes the selected body and all explicitly attached components. """
        target_name = self.ui.EditName.text().strip()
        if not target_name:
            print("Please select a Rigid Body to delete.")
            return

        body = self.physics_bodies.get(target_name)
        if not body: return

        # --- Ground Protection ---
        if body.is_ground:
            QMessageBox.warning(self, "Protection", "Cannot delete the Ground body.")
            return
            
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to completely delete '{body.name}' and ALL attached constraints (Joints, Forces, Springs, etc.)?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No: return
        
        # Helper function to completely wipe a component from memory, rendering, and the UI
        def wipe_component(comp, comp_list, tree_node):
            if hasattr(comp, 'actors'):
                for act in comp.actors: self.plotter.remove_actor(act)
            if comp in comp_list: comp_list.remove(comp)
            if tree_node:
                for i in range(tree_node.childCount()):
                    if tree_node.child(i).text(0) == comp.name:
                        tree_node.takeChild(i)
                        break

        # 1. Gather all attached components
        rfs_to_delete = [rf for rf in self.rframes if getattr(rf, 'parent_body', None) == body]
        forces_to_delete = [f for f in self.forces_list if getattr(f, 'parent_body', None) == body]
        joints_to_delete = [j for j in getattr(self, 'joints_list', []) if j.body_i == body or j.body_j == body]
        springs_to_delete = [s for s in getattr(self, 'springs_list', []) if s.body_i == body or s.body_j == body]
        bushings_to_delete = [b for b in getattr(self, 'bushings_list', []) if b.body_i == body or b.body_j == body]
        contacts_to_delete = [c for c in getattr(self, 'contact_pairs', []) if c.body_i == body or c.body_j == body]
        gears_to_delete = [g for g in getattr(self, 'gear_pairs_list', []) if g.body_1 == body or g.body_2 == body or getattr(g, 'carrier', None) == body]

        # 2. Obliterate them!
        self._delete_motions_for_joints(joints_to_delete)
        for rf in rfs_to_delete: wipe_component(rf, self.rframes, self.node_rframes)
        for f in forces_to_delete: wipe_component(f, self.forces_list, self.node_forces)
        for j in joints_to_delete: wipe_component(j, getattr(self, 'joints_list', []), getattr(self, 'node_joints', None))
        for s in springs_to_delete: wipe_component(s, getattr(self, 'springs_list', []), getattr(self, 'node_springs', None))
        for b in bushings_to_delete: wipe_component(b, getattr(self, 'bushings_list', []), getattr(self, 'node_bushings', None))
        for c in contacts_to_delete: wipe_component(c, getattr(self, 'contact_pairs', []), getattr(self, 'node_contacts', None))
        for g in gears_to_delete: wipe_component(g, getattr(self, 'gear_pairs_list', []), getattr(self, 'node_gear_pairs', None))

        # 3. Delete the body itself
        if body.actor: self.plotter.remove_actor(body.actor)
        for i in range(self.node_bodies.childCount()):
            if self.node_bodies.child(i).text(0) == body.name:
                self.node_bodies.takeChild(i)
                break
        del self.physics_bodies[body.name]

        self.clear_selection()
        if hasattr(self, 'invalidate_results'):
            self.invalidate_results()
        self.plotter.render()
        print(f"Deleted Body '{target_name}' and all its attached components.")

    def copy_body(self):
        """ Creates a perfectly overlaid physical copy of the selected body with matching mass properties. """
        target_name = self.ui.EditName.text().strip()
        if not target_name:
            print("Please select a Rigid Body to copy.")
            return

        src_body = self.physics_bodies.get(target_name)
        if not src_body: return

        # --- Ground Protection ---
        if src_body.is_ground:
            QMessageBox.warning(self, "Protection", "Cannot copy the Ground body.")
            return

        # 1. Generate unique extended name
        base_new_name = target_name + "_Copy"
        new_name = base_new_name
        counter = 1
        while new_name in self.physics_bodies:
            counter += 1
            new_name = f"{base_new_name}_{counter}"

        # 2. Deep copy the underlying mesh data
        new_raw_geom = src_body.raw_geom.copy()
        
        # --- Rebuild the PyVista mesh instead of looking for the missing attribute! ---
        faces_padded = np.insert(new_raw_geom.faces, 0, 3, axis=1)
        new_block_mesh = pv.PolyData(new_raw_geom.vertices, faces_padded.flatten())
        new_block_mesh = new_block_mesh.clean().compute_normals(split_vertices=True, feature_angle=60)

        # 3. Build the new PyVista Actor
        new_actor = self.plotter.add_mesh(new_block_mesh, color=src_body.base_color, 
                                          show_edges=self.edges_visible, 
                                          pickable=True, smooth_shading=True)
        if not src_body.visible:
            new_actor.SetVisibility(False)

        # 4. Build the new RigidBody Object
        new_tree_item = QTreeWidgetItem(self.node_bodies, [new_name])
        new_body = RigidBody(new_name, new_raw_geom, new_block_mesh, new_actor, new_tree_item)
        
        # Center the mathematical inertia tensor based on the cloned geometry
        new_body.center_and_align_mesh() 
        
        # 5. Perfect Spatial Overlap & Properties Match
        new_body.cog = src_body.cog.copy()
        new_body.principal_axes = src_body.principal_axes.copy()
        new_body.pos_angles = src_body.pos_angles.copy()
        new_body.base_color = src_body.base_color
        new_body.enabled = src_body.enabled
        new_body.visible = src_body.visible
        
        # Recalculate exact mass and inertia using the original density!
        new_body.update_density(src_body.density) 
        
        # Push the exact same 3D transform matrix to the GPU
        new_body.update_graphics_matrix(new_body.cog, new_body.principal_axes)
        
        # Add to global dictionary
        self.physics_bodies[new_name] = new_body
        self.body_counter += 1

        # 6. Auto-generate the CoG R-Frame
        rf_name = f"RF_CoG_{new_name}"
        cog_rf = RFrame(
            name=rf_name, position=new_body.cog.copy(), orientation=new_body.pos_angles.copy(),
            transform_matrix=new_body.principal_axes.copy(), plotter=self.plotter,
            parent_body=new_body, is_cog=True
        )
        self.rframes.append(cog_rf)
        QTreeWidgetItem(self.node_rframes, [rf_name])

        # 7. Auto-generate the Gravity Vector
        self._create_gravity_force_for_body(
            new_body,
            enabled=src_body.enabled and self.ui.chkEnabledGravity.isChecked(),
            visible=src_body.visible and self.ui.chkVisibleGravity.isChecked(),
        )

        # 8. Focus the UI on the newly copied body
        self.ui.treeHierarchy.blockSignals(True)
        self.ui.treeHierarchy.setCurrentItem(new_tree_item)
        self.ui.treeHierarchy.blockSignals(False)
        
        if hasattr(self, 'update_rframe_scales'):
            self.update_rframe_scales()
          
        self.on_tree_selected()
        
        if hasattr(self, 'invalidate_results'):
            self.invalidate_results()
        
        print(f"Successfully copied '{target_name}' -> '{new_name}'.")
    
    def _auto_enable_linked_bodies(self, component):
        """ 
        Universal DWIM (Do What I Mean) Helper.
        If a user enables a component, this safely checks if the attached bodies 
        are disabled. If they are, it auto-enables them and restores their gravity!
        """
        bodies_woke_up = False
        gravity_allowed = self.ui.chkVisibleGravity.isChecked()
        
        def wake_body(body):
            if body is not None and not body.enabled:
                body.enabled = True
                print(f"Auto-enabled '{body.name}' to support '{component.name}'.")
                
                # --- Auto-restore this body's Gravity ---
                for force in self.forces_list:
                    if force.parent_body.name == body.name and getattr(force, 'is_gravity', False):
                        force.enabled = True
                        force.set_visible(gravity_allowed)
                return True
            return False

        # 1. Check Forces (They use 'parent_body')
        if hasattr(component, 'parent_body'):
            if wake_body(component.parent_body): bodies_woke_up = True
            
        # 2. Check Joints, Springs, Contacts (They use 'body_i' and 'body_j')
        if hasattr(component, 'body_i'):
            if wake_body(component.body_i): bodies_woke_up = True
            
        if hasattr(component, 'body_j'):
            if wake_body(component.body_j): bodies_woke_up = True
            
        # 3. If we woke any bodies up, instantly refresh the UI and Viewport!
        if bodies_woke_up:
            self.update_selection_visuals(self.selected_body)
            self.refresh_tree_visuals()
    
    def refresh_tree_visuals(self):
        """ Sweeps the TreeHierarchy and dynamically updates fonts/colors based on states without altering the text string! """
        from PySide6.QtGui import QColor, QBrush, QFont
        
        def apply_format(node, obj_dict_or_list):
            if not node: return
            for i in range(node.childCount()):
                item = node.child(i)
                name = item.text(0)
                
                # Retrieve the matching physics object from memory
                obj = None
                if isinstance(obj_dict_or_list, dict):
                    obj = obj_dict_or_list.get(name)
                else:
                    obj = next((x for x in obj_dict_or_list if getattr(x, 'name', '') == name), None)
                    
                if obj:
                    is_enabled = getattr(obj, 'enabled', True)
                    is_visible = getattr(obj, 'visible', True)
                    
                    # 1. Apply Fonts
                    font = item.font(0)
                    font.setStrikeOut(not is_enabled) # Strikeout if disabled
                    font.setItalic(not is_visible)    # Italic if hidden
                    item.setFont(0, font)
                    
                    # 2. Apply Colors
                    if not is_enabled:
                        item.setForeground(0, QBrush(QColor("gray")))
                    elif not is_visible:
                        item.setForeground(0, QBrush(QColor("darkgray")))
                    else:
                        item.setForeground(0, QBrush()) # Clear formatting, restore default UI text color

        # Sweep all nodes
        apply_format(self.node_bodies, self.physics_bodies)
        apply_format(self.node_forces, self.forces_list)
        apply_format(self.node_joints, getattr(self, 'joints_list', []))
        apply_format(self.node_springs, getattr(self, 'springs_list', []))
        apply_format(getattr(self, 'node_bushings', self.node_springs), getattr(self, 'bushings_list', []))
        apply_format(getattr(self, 'node_contacts', None), getattr(self, 'contact_pairs', []))
        apply_format(getattr(self, 'node_motions', None), getattr(self, 'motions_list', []))
        # --- Sweep the Gear Pairs for formatting! ---
        apply_format(getattr(self, 'node_gear_pairs', None), getattr(self, 'gear_pairs_list', []))
        
    def toggle_body_enabled(self, state):
        if not self.selected_body:
            return
            
        body = self.physics_bodies[self.selected_body]
        
        # --- 1. Ground Protection Failsafe ---
        if body.is_ground and not state:
            print("Protection: Cannot disable the Ground body.")
            self.ui.chkEnabled.blockSignals(True)
            self.ui.chkEnabled.setChecked(True) # Force checkbox back to True
            self.ui.chkEnabled.blockSignals(False)
            return
            
        body.enabled = state
        
        # --- 2. Cascading Disable Logic ---
        if not state:
            current_scale = self.rframes[0].base_scale if self.rframes else 10.0
            
            # Disable attached Forces
            for force in self.forces_list:
                if force.parent_body.name == body.name:
                    force.enabled = False
                    force.visible = False
                    force.set_visible(False) # <--- Force to False
                    
            # Disable attached Joints
            for joint in getattr(self, 'joints_list', []):
                if joint.body_i.name == body.name or joint.body_j.name == body.name:
                    joint.enabled = False
                    joint.visible = False
                    joint.set_visible(False) # <--- Force to False
                    
            for spring in getattr(self, 'springs_list', []):
                if spring.body_i.name == body.name or spring.body_j.name == body.name:
                    spring.enabled = False
                    spring.update_transform(current_scale)
                    
            for bushing in getattr(self, 'bushings_list', []):
                if bushing.body_i.name == body.name or bushing.body_j.name == body.name:
                    bushing.enabled = False
                    bushing.update_transform(current_scale)
                    
            for contact in getattr(self, 'contact_pairs', []):
                if contact.body_i.name == body.name or contact.body_j.name == body.name:
                    contact.enabled = False
            
            # --- Disable attached Gears ---
            for gear in getattr(self, 'gear_pairs_list', []):
                if gear.body_1.name == body.name or gear.body_2.name == body.name or gear.carrier.name == body.name:
                    gear.enabled = False
                            
            print(f"Disabled '{body.name}' and all its attached components.")
        else:
            # --- THE UPGRADE: Auto-Enable Gravity when Body is Enabled! ---
            gravity_allowed = self.ui.chkVisibleGravity.isChecked()
            hide_aux = self.ui.btnHideShowObjects.isChecked()
            current_scale = self.rframes[0].base_scale if self.rframes else 10.0
            
            for force in self.forces_list:
                if force.parent_body.name == body.name and getattr(force, 'is_gravity', False):
                    force.enabled = True
                    force.visible = True
                    
                    # --- Recalculate 3D transform before showing! ---
                    # force.update_transform(getattr(self, 'joint_base_size', current_scale) * 2.0)
                    
                    current_scale = self.rframes[0].base_scale if self.rframes else 1.0
                    force.update_transform(current_scale)               
                    
                    if hide_aux:
                        force.set_visible(False)
                    else:
                        force.set_visible(gravity_allowed)
                        
            print(f"Enabled '{body.name}' and its Gravity force. Other attached components must be re-enabled manually.")

        # --- 3. Instant UI & Viewport Update ---
        self.update_selection_visuals(self.selected_body)
        self.refresh_tree_visuals() # Refresh the fonts/colors in the tree!
        self.plotter.render()
        
        if hasattr(self, 'invalidate_results'):
            self.invalidate_results()

    def toggle_body_visible(self, state):
        if self.selected_body:
            body = self.physics_bodies[self.selected_body]
            body.visible = state
            
            if body.actor:
                body.actor.SetVisibility(state)
            
            # --- Respect the auxiliary hide button! ---
            hide_aux = self.ui.btnHideShowObjects.isChecked()
            
            # Hide/Show associated RFrames
            for rf in self.rframes:
                if rf.is_cog and rf.parent_body == body:
                    if hide_aux:
                        rf.set_visible(False)
                    else:
                        rf.set_visible(state)
                    
            # Hide/Show associated Forces
            gravity_allowed = self.ui.chkVisibleGravity.isChecked() 
            for force in self.forces_list:
                if force.parent_body == body:
                    if hide_aux:
                        force.set_visible(False)
                    elif force.is_gravity and state:
                        force.set_visible(gravity_allowed)
                    else:
                        force.set_visible(state)
                        
            self.refresh_tree_visuals()        
            self.plotter.render()
            
    def toggle_body_edges(self, state):
        if not self.selected_body:
            return
            
        body = self.physics_bodies[self.selected_body]
        body.show_edges = state
        body.actor.prop.show_edges = state
        self.plotter.render()

    def change_body_color(self):
        if not self.selected_body:
            return
            
        body = self.physics_bodies[self.selected_body]
        
        # --- THE FIX: The Ground has no visual mesh, so we cannot paint it ---
        if body.is_ground: 
            print("Protection: Cannot paint the invisible Ground body.")
            return
        
        color = QColorDialog.getColor()
        
        if color.isValid():
            hex_color = color.name()
            body.base_color = hex_color
            
            # --- THE FIX: Ensure the actor exists before applying color ---
            if body.actor:
                body.actor.prop.color = hex_color
            
            self.ui.btnColorPicker.setStyleSheet(f"background-color: {hex_color};")
            self.plotter.render()
            
            
    def toggle_all_edges(self):
        """ Toggles wireframes for all bodies globally. """
        self.edges_visible = not self.edges_visible
        
        for body in self.physics_bodies.values():
            # --- THE FIX: Skip the invisible Ground body ---
            if body.is_ground: continue 
                
            body.show_edges = self.edges_visible
            if body.actor:
                body.actor.prop.show_edges = self.edges_visible
            
        self.plotter.render()

    def change_all_bodies_color(self):
        """ Applies a single chosen color to all bodies. """
        if not self.physics_bodies:
            return
            
        color = QColorDialog.getColor()
        
        if color.isValid():
            hex_color = color.name()
            
            for name, body in self.physics_bodies.items():
                # --- THE FIX: Skip the invisible Ground body ---
                if body.is_ground: continue 
                    
                body.base_color = hex_color
                
                if body.actor:
                    body.actor.prop.color = hex_color if body.enabled else "black"
                    
            self.plotter.render()

    def apply_random_colors(self):
        """ Rapid visual splitting: applies a random distinct color to every body. """
        if not self.physics_bodies:
            return
            
        for name, body in self.physics_bodies.items():
            # --- THE FIX: Skip the invisible Ground body ---
            if body.is_ground: continue 
                
            hex_color = f"#{random.randint(0, 0xFFFFFF):06x}"
            body.base_color = hex_color
            
            #if name != self.selected_body:
            if body.actor:
                body.actor.prop.color = hex_color if body.enabled else "black"
                
        self.plotter.render()
        
    # ==========================================
    # --- REFERENCE FRAME MANAGEMENT ---
    # ==========================================

    def _get_rf_inputs(self):
        """ Helper method to extract and convert the UI inputs for RFs. """
        try:
            x_mm = parse_ui_float(self.ui.EditRF_X_Pos.text())
            y_mm = parse_ui_float(self.ui.EditRF_Y_Pos.text())
            z_mm = parse_ui_float(self.ui.EditRF_Z_Pos.text())
            
            ang_x = parse_ui_float(self.ui.EditRF_X_Angle.text()) 
            ang_y = parse_ui_float(self.ui.EditRF_Y_Angle.text()) 
            ang_z = parse_ui_float(self.ui.EditRF_Z_Angle.text()) 
            
            pos_m = np.array([x_mm, y_mm, z_mm]) / MMtoM
            orientation = np.array([ang_z, ang_y, ang_x]) 
            rot_matrix = Rotation.from_euler('xyz', [ang_x, ang_y, ang_z], degrees=True).as_matrix()
            
            return pos_m, orientation, rot_matrix
        except ValueError:
            print("Invalid numerical input for RF position or orientation.")
            return None, None, None

    # ==========================================
    # --- REFERENCE FRAME MANAGEMENT ---
    # ==========================================
    
    def is_rf_locked(self, rf_name):
        """ Dynamically checks if an RF is currently used to define any existing component. """
        # Check Forces
        if any(getattr(f, 'source_rf_name', '') == rf_name for f in self.forces_list): return True
        # Check Joints
        if any(getattr(j, 'source_anchor_name', '') == rf_name or getattr(j, 'source_target_name', '') == rf_name for j in self.joints_list): return True
        # Check Springs
        if any(getattr(s, 'rf_i_name', '') == rf_name or getattr(s, 'rf_j_name', '') == rf_name for s in getattr(self, 'springs_list', [])): return True
        # Check Bushings
        if any(getattr(b, 'rf_i_name', '') == rf_name or getattr(b, 'rf_j_name', '') == rf_name for b in getattr(self, 'bushings_list', [])): return True
        
        return False

    def add_rf(self):
        """ Creates a brand new RF with an auto-generated name and selects it in the tree. """
        pos_m, orientation, rot_matrix = self._get_rf_inputs()
        if pos_m is None: return

        # Auto-generate a unique name (RF_1, RF_2, etc.)
        counter = 1
        new_rf_name = f"RF_{counter}"
        while any(r.name == new_rf_name for r in self.rframes):
            counter += 1
            new_rf_name = f"RF_{counter}"

        new_rf = RFrame(
            name=new_rf_name,
            position=pos_m,
            orientation=orientation,
            transform_matrix=rot_matrix,
            plotter=self.plotter,
            parent_body=self.physics_bodies.get("Ground"), # Anchored to space
            is_cog=False
        )
        self.rframes.append(new_rf)
        
        # 1. Create the item and save it to a variable
        new_item = QTreeWidgetItem(self.node_rframes, [new_rf_name])
        self.node_rframes.setExpanded(True)
        self.update_rframe_scales() 
        current_scale = self.rframes[0].base_scale if self.rframes else 10.0
        new_rf.set_scale(current_scale)
        
        # 2. Safely focus the Tree on the new item
        self.ui.treeHierarchy.blockSignals(True)
        self.ui.treeHierarchy.setCurrentItem(new_item)
        self.ui.treeHierarchy.blockSignals(False)
        
        # 3. Immediately select the new RF so the user sees it in the UI
        self.selected_rframe = new_rf_name
        self.ui.Edit_RFName.setText(new_rf_name)
        self.update_rf_selection_visuals(new_rf_name) # Highlight it in the 3D viewport!
        
        self.fit_all_camera()
        
        # Toggle the visibility of the grid to force a visual refresh so grid covers the new RF correctly.
        self.grid_visible = not self.grid_visible
        self.toggle_grid()
        
        print(f"Created new Custom RF '{new_rf_name}'.")
        self.plotter.render()

    def update_rf(self):
        """ Updates the RF whose name is currently displayed in the read-only Edit_RFName box. """
        target_name = self.ui.Edit_RFName.text().strip()
        if not target_name:
            print("Please select a Reference Frame to update.")
            return

        existing_rf = next((r for r in self.rframes if r.name == target_name), None)
        if not existing_rf: return
        
        if existing_rf.name == "Global_RF":
            print("Protection: Cannot modify the Global Reference Frame.")
            return
        # --- THE FIX: Block updates if locked! ---
        if self.is_rf_locked(existing_rf.name):
            print(f"Protection: Cannot edit '{existing_rf.name}'. It is locked by an existing component.")
            return
            
        pos_m, orientation, rot_matrix = self._get_rf_inputs()
        if pos_m is None: return
            
        if existing_rf.is_cog:
            if not self.ui.chkMoveBody.isChecked():
                print(f"Protection: Please check 'Move Body' to adjust '{existing_rf.parent_body.name}'.")
                return
            if self.is_body_constrained(existing_rf.parent_body.name):
                print(f"Protection: Cannot move '{existing_rf.parent_body.name}'. It is locked by an existing joint.")
                return
            
            # --- THE FIX: Rewind FIRST so the update isn't erased! ---
            if hasattr(self, 'invalidate_results'):
                self.invalidate_results()
                
            body = existing_rf.parent_body
            body.cog = pos_m
            body.principal_axes = rot_matrix
            body.pos_angles = orientation
            body.update_graphics_matrix(body.cog, body.principal_axes)
                
            # --- Visually update all attached Springs and Forces! ---
            current_scale = self.rframes[0].base_scale if self.rframes else 10.0
            
            for force in self.forces_list:
                if force.parent_body.name == body.name:
                    force.update_transform(current_scale)
                    
            for spring in getattr(self, 'springs_list', []):
                if spring.body_i.name == body.name or spring.body_j.name == body.name:
                    spring.update_transform(current_scale)
            
        else:
            existing_rf.position = pos_m
            existing_rf.orientation = orientation
            existing_rf.transform_matrix = rot_matrix
            
        existing_rf.update_transform()
        
        print(f"Updated RF '{existing_rf.name}'.")
        self.plotter.render()

    def rename_rf(self):
        """ Triggers a pop-up window to safely rename the targeted RF. """
        target_name = self.ui.Edit_RFName.text().strip()
        if not target_name:
            print("Please select a Reference Frame to rename.")
            return

        rf = next((r for r in self.rframes if r.name == target_name), None)
        if not rf: return

        # --- Protections ---
        if rf.is_cog or rf.name == "Global_RF":
            print(f"Protection: Cannot rename core Reference Frame '{rf.name}'.")
            return
        # --- THE FIX: Block renaming if locked! ---
        if self.is_rf_locked(rf.name):
            print(f"Protection: Cannot rename '{rf.name}'. It is locked by an existing component.")
            return
        
        # 1. Trigger Pop-up
        new_name, ok = QInputDialog.getText(self, "Rename Reference Frame", "Enter new name:", text=target_name)

        # 2. Validate input
        if not ok or not new_name.strip(): return 
        new_name = new_name.strip()
        if new_name == target_name: return 

        if any(r.name == new_name for r in self.rframes):
            QMessageBox.warning(self, "Rename Error", f"An RF with the name '{new_name}' already exists!")
            return

        # 3. Update Object and UI Box
        rf.name = new_name
        self.selected_rframe = new_name
        self.ui.Edit_RFName.setText(new_name)

        # 4. Update Tree Hierarchy visually
        for i in range(self.node_rframes.childCount()):
            if self.node_rframes.child(i).text(0) == target_name:
                self.node_rframes.child(i).setText(0, new_name)
                break

        print(f"Successfully renamed RF '{target_name}' to '{new_name}'.")

    def delete_rf(self):
        """ Completely purges the targeted Reference Frame from the engine. """
        target_name = self.ui.Edit_RFName.text().strip()
        if not target_name:
            print("Please select a Reference Frame to delete.")
            return
            
        rf = next((r for r in self.rframes if r.name == target_name), None)
        if not rf: return
            
        if rf.is_cog or rf.name == "Global_RF":
            print(f"Protection: Cannot delete core Reference Frame '{rf.name}'.")
            return
        # --- THE FIX: Block deletion if locked! ---
        if self.is_rf_locked(rf.name):
            print(f"Protection: Cannot delete '{rf.name}'. It is locked by an existing component.")
            return
        # --- THE UPGRADE: Ask for permission! ---
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete Reference Frame '{rf.name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No: return
        # ----------------------------------------    
        # 1. Ask the graphics card to destroy the 3D actors
        for act in rf.actors:
            self.plotter.remove_actor(act)
            
        # 2. Delete from engine memory
        self.rframes.remove(rf)
        
        # 3. Delete from TreeView
        for i in range(self.node_rframes.childCount()):
            if self.node_rframes.child(i).text(0) == rf.name:
                self.node_rframes.takeChild(i)
                break
                
        # 4. Clean up visuals
        self.clear_selection()
        print(f"Deleted RF '{rf.name}'.")
        
    def shift_rf(self):
        """ Shifts the selected Reference Frame (or its Parent Body) along LOCAL axes. """
        if not self.selected_rframe:
            print("No Reference Frame selected.")
            return

        rf = next((r for r in self.rframes if r.name == self.selected_rframe), None)
        if not rf: return
        
        # --- Assembly Dislocation Protections ---
        if rf.name == "Global_RF":
            print("Protection: Cannot move the Global Reference Frame.")
            return
        # --- THE FIX: Block shifting if locked! ---
        if self.is_rf_locked(rf.name) and not rf.is_cog:
            print(f"Protection: Cannot shift '{rf.name}'. It is locked by an existing component.")
            return
            
        if rf.is_cog:
            if not self.ui.chkMoveBody.isChecked():
                print("Protection: Please check 'Move Body' to adjust CAD assembly positions.")
                return
            if self.is_body_constrained(rf.parent_body.name):
                print(f"Protection: Cannot move '{rf.parent_body.name}'. It is locked by an existing joint.")
                return

        try:
            shift_mm = float(self.ui.dsbShift_RF.value())  
            # shift_mm = parse_ui_float(self.ui.Edit_Shift_RF.text())  
        except ValueError:
            print("Invalid numerical input for shift distance.")
            return

        # 1. Create the Local Translation Vector
        local_vec = np.zeros(3)
        if self.ui.rbnRFalongX.isChecked(): local_vec[0] = shift_mm
        elif self.ui.rbnRFalongY.isChecked(): local_vec[1] = shift_mm
        elif self.ui.rbnRFalongZ.isChecked(): local_vec[2] = shift_mm

        # 2. Convert Local Vector to Global Vector
        global_vec = rf.transform_matrix @ local_vec
        global_shift_m = global_vec / MMtoM

        # 3. Apply the shift to the Body OR the floating RF
        if rf.is_cog:
            # --- THE FIX: Rewind FIRST so the shift isn't erased! ---
            if hasattr(self, 'invalidate_results'):
                self.invalidate_results()
            body = rf.parent_body
            body.cog = body.cog + global_shift_m
            body.update_graphics_matrix(body.cog, body.principal_axes)
                
            # --- Visually update all attached Springs and Forces! ---
            current_scale = self.rframes[0].base_scale if self.rframes else 10.0
            
            for force in self.forces_list:
                if force.parent_body.name == body.name:
                    force.update_transform(current_scale)
                    
            for spring in getattr(self, 'springs_list', []):
                if spring.body_i.name == body.name or spring.body_j.name == body.name:
                    spring.update_transform(current_scale)    
                
        else:
            rf.position = rf.position + global_shift_m

        # 4. Update visuals and UI text
        rf.update_transform()

        self.ui.EditRF_X_Pos.setText(f"{rf.position[0] * MMtoM:.3f}")
        self.ui.EditRF_Y_Pos.setText(f"{rf.position[1] * MMtoM:.3f}")
        self.ui.EditRF_Z_Pos.setText(f"{rf.position[2] * MMtoM:.3f}")

        self.plotter.render()

    def rotate_rf(self):
        """ Rotates the selected Reference Frame (or its Parent Body) around LOCAL axes. """
        if not self.selected_rframe:
            print("No Reference Frame selected.")
            return

        rf = next((r for r in self.rframes if r.name == self.selected_rframe), None)
        if not rf: return
        
        # --- Assembly Dislocation Protections ---
        if rf.name == "Global_RF":
            print("Protection: Cannot move the Global Reference Frame.")
            return
        # --- THE FIX: Block rotating if locked! ---
        if self.is_rf_locked(rf.name) and not rf.is_cog:
            print(f"Protection: Cannot rotate '{rf.name}'. It is locked by an existing component.")
            return
            
        if rf.is_cog:
            if not self.ui.chkMoveBody.isChecked():
                print("Protection: Please check 'Move Body' to adjust CAD assembly positions.")
                return
            if self.is_body_constrained(rf.parent_body.name):
                print(f"Protection: Cannot rotate '{rf.parent_body.name}'. It is locked by an existing joint.")
                return

        try:
            angle_deg = float(self.ui.dsbRotate_RF.value())
            # angle_deg = parse_ui_float(self.ui.Edit_Rotate_RF.text())
        except ValueError:
            print("Invalid numerical input for rotation angle.")
            return

        # 1. Create a Rotation object for the new Local transformation
        if self.ui.rbnRFaroundX.isChecked(): local_rot = Rotation.from_euler('x', angle_deg, degrees=True)
        elif self.ui.rbnRFaroundY.isChecked(): local_rot = Rotation.from_euler('y', angle_deg, degrees=True)
        elif self.ui.rbnRFaroundZ.isChecked(): local_rot = Rotation.from_euler('z', angle_deg, degrees=True)

        # 2. Get the current Global Rotation
        current_rot = Rotation.from_matrix(rf.transform_matrix)

        # 3. Matrix Multiplication: Current * Local
        new_rot = current_rot * local_rot

        # 4. Apply the rotation to the Body OR the floating RF
        euler_xyz = new_rot.as_euler('xyz', degrees=True)
        new_orientation = np.array([euler_xyz[2], euler_xyz[1], euler_xyz[0]])
        
        if rf.is_cog:
            # --- THE FIX: Rewind FIRST so the rotation isn't erased! ---
            if hasattr(self, 'invalidate_results'):
                self.invalidate_results()
                
            body = rf.parent_body
            body.principal_axes = new_rot.as_matrix()
            body.pos_angles = new_orientation
            body.update_graphics_matrix(body.cog, body.principal_axes)
                
            # --- Visually update all attached Springs and Forces! ---
            current_scale = self.rframes[0].base_scale if self.rframes else 10.0
            
            for force in self.forces_list:
                if force.parent_body.name == body.name:
                    force.update_transform(current_scale)
                    
            for spring in getattr(self, 'springs_list', []):
                if spring.body_i.name == body.name or spring.body_j.name == body.name:
                    spring.update_transform(current_scale)    
                
        else:
            rf.transform_matrix = new_rot.as_matrix()
            rf.orientation = new_orientation

        # 5. Update visuals and UI text
        rf.update_transform()

        self.ui.EditRF_Z_Angle.setText(f"{rf.orientation[0]:.3f}")
        self.ui.EditRF_Y_Angle.setText(f"{rf.orientation[1]:.3f}")
        self.ui.EditRF_X_Angle.setText(f"{rf.orientation[2]:.3f}")

        self.plotter.render()
        
    # ==========================================
    # --- GRAVITY & FORCES ---
    # ==========================================

    def update_gravity(self):
        """ Reads the UI inputs, updates the INTERNAL global gravity, and re-aligns arrows. """
        try:
            g_x = parse_ui_float(self.ui.Edit_GravityX.text())
            g_y = parse_ui_float(self.ui.Edit_GravityY.text())
            g_z = parse_ui_float(self.ui.Edit_GravityZ.text())
        except ValueError:
            print("Invalid numerical input for Gravity.")
            return

        # --- Overwrite the internal global variable! ---
        self.global_gravity = np.array([g_x, g_y, g_z])

        # Loop through all forces and update the ones flagged as Gravity
        for force in self.forces_list:
            if force.is_gravity:
                force.base_vector = self.global_gravity.copy()
                
                # force.update_transform(self.joint_base_size * 2.0)
                current_scale = self.rframes[0].base_scale if self.rframes else 1.0
                force.update_transform(current_scale)
                
        self.invalidate_results()        
        self.plotter.render()
        print(f"Global Gravity updated to: [{g_x}, {g_y}, {g_z}] m/s²")

    def toggle_gravity_enabled(self, state):
        """ Toggles whether gravity affects the simulation, and updates visibility accordingly. """
        # --- Explicitly check the UI visibility box state ---
        is_visible = self.ui.chkVisibleGravity.isChecked()
        
        for force in self.forces_list:
            if force.is_gravity:
                force.enabled = state
                
                # Apply the explicit visibility state
                force.set_visible(is_visible)
                
        if hasattr(self, 'invalidate_results'):
            self.invalidate_results()    
            
        # self.update_gravity()     
        
        self.update_rframe_scales()   
        self.plotter.render()
        print(f"Gravity Enabled: {state}")

    def toggle_gravity_visible(self, state):
        """ Explicitly hides or unhides the Lime-Green gravity arrows in the viewport. """
        
        current_scale = self.rframes[0].base_scale if self.rframes else 10.0
        for force in self.forces_list:
            if force.is_gravity:
                force.set_visible(state)
                force.update_transform(current_scale) #, t=0.0)
                
        self.plotter.render()   
         
    def add_custom_force(self):
        """ Validates inputs, extracts coordinates from the RF, and creates the Force/Torque. """
        body_name = self.ui.Edit_BodyForce.text().strip()
        rf_name = self.ui.Edit_RFForce.text().strip()
        
        if not body_name or not rf_name:
            print("Error: A Body and a Reference Frame are strictly required.")
            return

        body = self.physics_bodies.get(body_name)
        rf = next((r for r in self.rframes if r.name == rf_name), None)
        
        if not body or not rf: return
 
        # --- Ground Protection ---
        if body.is_ground:
            QMessageBox.warning(self, "Protection", "Forces and Actuators cannot be applied to the Ground.")
            return
            
        # 1. Determine Type, Frame, and Speed Limits
        is_torque = (self.ui.cmbForceType.currentIndex() == 1)
        
        # We no longer strictly parse this as a float because it can be an equation!
        try:
            user_mag = parse_ui_float(self.ui.Edit_ForceValue.text())
            is_constant = True
        except ValueError:
            user_mag = 1.0 # Placeholder
            is_constant = False
            
        # --- THE UPGRADE: Convert UI Nmm to SI Nm for the solver! ---
        magnitude = user_mag / 1000.0 if is_torque else user_mag
        
        f_frame = ForceFrame.SPACE_FIXED if self.ui.cmbSpaceBody.currentIndex() == 0 else ForceFrame.BODY_FIXED
        axis_choice = self.ui.cmbForceAnchorXYZ.currentText().strip().upper()
        
        is_actuator = self.ui.chkActuatorMode.isChecked()
        allow_braking = self.ui.chkAllowActuatorBraking.isChecked()
        speed_max_si = 0.0
        
        if is_actuator:
            f_type = ForceType.E_MOTOR if is_torque else ForceType.ACTUATOR
            type_str = "EMotor" if is_torque else "Actuator"
            try:
                raw_speed = parse_ui_float(self.ui.Edit_MaxActuatorSpeed.text())
                # Convert RPM -> rad/s OR mm/s -> m/s
                speed_max_si = raw_speed * (np.pi / 30.0) if is_torque else (raw_speed / 1000.0)
                
                # --- Calculate and display Peak Mechanical Power (Watts) ---
                if is_constant:
                    peak_power = (magnitude * speed_max_si) / 4.0
                else:
                    peak_power = 0.0
                self.ui.Edit_ActPowerLimit.setText(f"{peak_power:.3f}")
                
            except ValueError:
                print("Error: Invalid numerical max speed.")
                return
        else:
            f_type = ForceType.TORQUE if is_torque else ForceType.FORCE
            type_str = "Torque" if is_torque else "Force"
            self.ui.Edit_ActPowerLimit.setText("0.000") # Clear if not an actuator

        # 2. Extract Mathematical Vectors (Stamp and Disconnect)
        # Position: Convert RF global position to Body's local coordinates
        global_pos = rf.position
        local_pos = body.principal_axes.T @ (global_pos - body.cog)

        # Direction: Extract the chosen axis from the RF's rotation matrix
        if axis_choice == 'X': global_dir = rf.transform_matrix[:, 0]
        elif axis_choice == 'Y': global_dir = rf.transform_matrix[:, 1]
        else: global_dir = rf.transform_matrix[:, 2] # Default Z
            
        global_vec = global_dir * magnitude
        
        # --- THE FIX: Pass Global or Local based on the user's selection! ---
        if f_frame == ForceFrame.SPACE_FIXED:
            final_vec = global_vec
        else:
            final_vec = body.principal_axes.T @ global_vec

        # 3. Generate Name & Create
        counter = len(self.forces_list) + 1
        f_name = f"{type_str}_{counter}"
        while any(f.name == f_name for f in self.forces_list):
            counter += 1
            f_name = f"{type_str}_{counter}"

        new_force = Force(
            name=f_name, force_type=f_type, parent_body=body, 
            fixed_in=f_frame, position=local_pos, vector=final_vec, plotter=self.plotter
        )
        # --- Compile the math expression! ---
        new_force.compile_expression(self.ui.Edit_ForceValue.text())
        
        new_force.allow_braking = allow_braking
        new_force.speed_max = speed_max_si
        # new_force.magnitude = magnitude
        new_force.direction = axis_choice
        # new_force.update_transform(self.joint_base_size * 2.0)
        current_scale = self.rframes[0].base_scale if self.rframes else 1.0
        new_force.update_transform(current_scale)
        
        self.forces_list.append(new_force)

        # 4. Add to Tree Hierarchy
        new_item = QTreeWidgetItem(self.node_forces, [new_force.name])
        self.node_forces.setExpanded(True)

        # 5. Auto-Select the new force and update UI
        self.ui.treeHierarchy.blockSignals(True)
        self.ui.treeHierarchy.setCurrentItem(new_item)
        self.ui.treeHierarchy.blockSignals(False)
        
        self.selected_force = new_force.name
        self.ui.Edit_ForceName.setText(f_name)
        # self.ui.Edit_RFForce.setText("") # Disconnected!
        
        # Disable Add Button, as we are now viewing an existing Force
        self.ui.btnAddForceTorque.setEnabled(False)
        
        self.update_selection_visuals(body.name)
        self.update_force_selection_visuals(new_force.name)
        
        self.invalidate_results()
        
        # --- Instantly sync the new force to the camera scale! ---
        self.update_rframe_scales()
        self.plotter.render()
        print(f"Created {type_str}: '{f_name}'")

    def validate_force_expression(self, text):
        """ Real-time compiler check for Forces! Colors the text box RED if the math is broken. """
        expr_str = text.strip()
        if not expr_str:
            self.ui.Edit_ForceValue.setStyleSheet("background-color: #ffcccc; color: black;") 
            return

        def custom_step(x, x0, h0, x1, h1): return 0.0
        def custom_if(x, e1, e2): return 0.0
        safe_dict = { "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "pi": np.pi, "exp": np.exp, "sqrt": np.sqrt, "abs": np.abs, "step": custom_step, "STEP": custom_step, "IF": custom_if, "__builtins__": None }

        try:
            float(expr_str.replace(',', '.'))
            self.ui.Edit_ForceValue.setStyleSheet("") 
        except ValueError:
            try:
                import re
                clean_str = expr_str.replace(',', '.')
                clean_str = clean_str.replace(';', ',')
                safe_expr = re.sub(r'\bif\s*\(', 'IF(', clean_str, flags=re.IGNORECASE)
                func = eval(f"lambda t: {safe_expr}", safe_dict)
                func(0.0) 
                self.ui.Edit_ForceValue.setStyleSheet("") 
            except Exception:
                self.ui.Edit_ForceValue.setStyleSheet("background-color: #ffcccc; color: black;")

    def validate_motion_expression(self, text):
        """ Real-time compiler check for Kinematic Motions! Colors the text box RED if the math is broken. """
        expr_str = text.strip()
        if not expr_str:
            self.ui.Edit_MotionFunction.setStyleSheet("background-color: #ffcccc; color: black;") 
            return

        def custom_step(x, x0, h0, x1, h1): return 0.0
        def custom_if(x, e1, e2): return 0.0
        safe_dict = { "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "pi": np.pi, "exp": np.exp, "sqrt": np.sqrt, "abs": np.abs, "step": custom_step, "STEP": custom_step, "IF": custom_if, "__builtins__": None }

        try:
            float(expr_str.replace(',', '.'))
            self.ui.Edit_MotionFunction.setStyleSheet("") 
        except ValueError:
            try:
                import re
                clean_str = expr_str.replace(',', '.')
                clean_str = clean_str.replace(';', ',')
                safe_expr = re.sub(r'\bif\s*\(', 'IF(', clean_str, flags=re.IGNORECASE)
                func = eval(f"lambda t: {safe_expr}", safe_dict)
                func(0.0) 
                self.ui.Edit_MotionFunction.setStyleSheet("") 
            except Exception:
                self.ui.Edit_MotionFunction.setStyleSheet("background-color: #ffcccc; color: black;")
    
    # ==========================================
    # --- COMPRESSION SPRINGS ---
    # ==========================================
    def prepare_new_comp_spring(self):
        """ Prepares the UI for a new Compression Spring. """
        self.clear_selection()
        self.ui.Edit_CompSpringName.setText("")
        self.ui.Edit_BodyI_CompSpring.setText("")
        self.ui.Edit_BodyJ_CompSpring.setText("")
        self.ui.Edit_RFBodyI_CompSpring.setText("")
        self.ui.Edit_RFBodyJ_CompSpring.setText("")
        
        self.ui.Edit_StiffnessCompSpring.setText("0.1")
        self.ui.Edit_DampingCompSpring.setText("0.001")
        self.ui.Edit_PreloadCompSpring.setText("0.0")
        
        self.ui.chkEnabledCompSpring.blockSignals(True)
        self.ui.chkEnabledCompSpring.setChecked(True)
        self.ui.chkEnabledCompSpring.blockSignals(False)
        
        self.ui.btnAddCompSpring.setEnabled(True)
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(5) 

    def add_comp_spring(self):
        body_i_name = self.ui.Edit_BodyI_CompSpring.text().strip()
        body_j_name = self.ui.Edit_BodyJ_CompSpring.text().strip()
        if not body_i_name or not body_j_name: return
        
        body_i = self.physics_bodies.get(body_i_name)
        body_j = self.physics_bodies.get(body_j_name)
        if not body_i or not body_j: return
        
        try:
            # UI: N/mm -> SI: N/m (* 1000)
            k_si = parse_ui_float(self.ui.Edit_StiffnessCompSpring.text()) * 1000.0
            # UI: N/(mm/s) -> SI: N/(m/s) (* 1000)
            c_si = parse_ui_float(self.ui.Edit_DampingCompSpring.text()) * 1000.0
            # UI: N -> SI: N
            p_si = parse_ui_float(self.ui.Edit_PreloadCompSpring.text())
        except ValueError:
            print("Error: Invalid numerical values for spring parameters.")
            return

        counter = len(self.springs_list) + 1
        s_name = f"CompSpring_{counter}"
        while any(s.name == s_name for s in self.springs_list):
            counter += 1
            s_name = f"CompSpring_{counter}"

        spring = CompressionSpring(
            name=s_name, body_i=body_i, rf_i_name=self.ui.Edit_RFBodyI_CompSpring.text().strip(),
            body_j=body_j, rf_j_name=self.ui.Edit_RFBodyJ_CompSpring.text().strip(), plotter=self.plotter
        )
        
        spring.stiffness = k_si
        spring.damping = c_si
        spring.preload = p_si

        # Lock in the geometric vectors
        spring.bind_kinematics(self.rframes)
        self.springs_list.append(spring)
        QTreeWidgetItem(self.node_springs, [spring.name])
        
        self.ui.Edit_CompSpringName.setText(spring.name)
        self.ui.btnAddCompSpring.setEnabled(False)
        self.invalidate_results()
        print(f"Added {spring.name}")
        
        # Force visual update
        spring.update_transform(self.rframes[0].base_scale if self.rframes else 10.0)
        self.update_rframe_scales()
        self.plotter.render()

    def update_comp_spring(self):
        target_name = self.ui.Edit_CompSpringName.text().strip()
        spring = next((s for s in self.springs_list if s.name == target_name), None)
        if not spring: return
        
        try:
            spring.stiffness = parse_ui_float(self.ui.Edit_StiffnessCompSpring.text()) * 1000.0
            spring.damping = parse_ui_float(self.ui.Edit_DampingCompSpring.text()) * 1000.0
            spring.preload = parse_ui_float(self.ui.Edit_PreloadCompSpring.text())
        except ValueError: return
        
        self.invalidate_results()
        print(f"Updated {spring.name}")

    def delete_comp_spring(self):
        target_name = self.ui.Edit_CompSpringName.text().strip()
        spring = next((s for s in self.springs_list if s.name == target_name), None)
        if not spring: return
        
        # --- THE UPGRADE: Ask for permission! ---
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete Compression Spring '{spring.name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No: return
        # ----------------------------------------
        
        for act in spring.actors: self.plotter.remove_actor(act)
        self.springs_list.remove(spring)
        for i in range(self.node_springs.childCount()):
            if self.node_springs.child(i).text(0) == spring.name:
                self.node_springs.takeChild(i)
                break
            
        self.invalidate_results()    
        self.ui.Edit_CompSpringName.setText("")
        self.plotter.render()
        
    def rename_comp_spring(self):
        """ Triggers a pop-up window to safely rename the targeted Compression Spring. """
        target_name = self.ui.Edit_CompSpringName.text().strip()
        if not target_name:
            print("Please select a Compression Spring to rename.")
            return

        spring = next((s for s in self.springs_list if s.name == target_name), None)
        if not spring: return

        old_name = spring.name
        new_name, ok = QInputDialog.getText(self, "Rename Compression Spring", "Enter new name:", text=old_name)

        if not ok or not new_name.strip(): return 
        new_name = new_name.strip()
        if new_name == old_name: return 

        if any(s.name == new_name for s in self.springs_list):
            QMessageBox.warning(self, "Rename Error", f"A Spring with the name '{new_name}' already exists!")
            return

        spring.name = new_name
        self.ui.Edit_CompSpringName.setText(new_name)

        for i in range(self.node_springs.childCount()):
            if self.node_springs.child(i).text(0) == old_name:
                self.node_springs.child(i).setText(0, new_name)
                break

        print(f"Successfully renamed Compression Spring '{old_name}' to '{new_name}'.")
        if hasattr(self, 'invalidate_results'):
            self.invalidate_results()
            
    def toggle_comp_spring_enabled(self, state):
        """ Toggles the physical and visual state of the selected Compression Spring. """
        target_name = self.ui.Edit_CompSpringName.text().strip()
        if not target_name: return
        
        spring = next((s for s in self.springs_list if s.name == target_name), None)
        if spring:
            spring.enabled = state
            
            # --- THE FIX: Call Smart Enable! ---
            if state: 
                self._auto_enable_linked_bodies(spring)
            # -----------------------------------
                
            current_scale = self.rframes[0].base_scale if self.rframes else 10.0
            spring.update_transform(current_scale) # Visually hides/shows it
            
            self.refresh_tree_visuals()
            self.plotter.render()
            
            if hasattr(self, 'invalidate_results'):
                self.invalidate_results()
                        
    # ==========================================
    # --- TORSION SPRINGS ---
    # ==========================================
    def prepare_new_tors_spring(self):
        self.clear_selection()
        self.ui.Edit_TorsSpringName.setText("")
        self.ui.Edit_BodyI_TorsSpring.setText("")
        self.ui.Edit_BodyJ_TorsSpring.setText("")
        self.ui.Edit_RFBodyI_TorsSpring.setText("")
        self.ui.Edit_RFBodyJ_TorsSpring.setText("")
        self.ui.cmbSpringBodyIAnchorXYZ.setCurrentIndex(2) # Default Z
        
        self.ui.Edit_StiffnessTorsSpring.setText("10.0")
        self.ui.Edit_DampingTorsSpring.setText("0.01")
        self.ui.Edit_PreloadTorsSpring.setText("0.0")
        
        self.ui.chkEnabledTorsSpring.blockSignals(True)
        self.ui.chkEnabledTorsSpring.setChecked(True)
        self.ui.chkEnabledTorsSpring.blockSignals(False)
        
        self.ui.btnAddTorsSpring.setEnabled(True)
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(6) 

    def add_tors_spring(self):
        body_i_name = self.ui.Edit_BodyI_TorsSpring.text().strip()
        body_j_name = self.ui.Edit_BodyJ_TorsSpring.text().strip()
        if not body_i_name or not body_j_name: return
        
        body_i = self.physics_bodies.get(body_i_name)
        body_j = self.physics_bodies.get(body_j_name)
        if not body_i or not body_j: return
        
        try:
            # UI: Nmm/rad -> SI: Nm/rad (/ 1000)
            k_si = parse_ui_float(self.ui.Edit_StiffnessTorsSpring.text()) / 1000.0
            # UI: Nmm/(rad/s) -> SI: Nm/(rad/s) (/ 1000)
            c_si = parse_ui_float(self.ui.Edit_DampingTorsSpring.text()) / 1000.0
            # UI: Nmm -> SI: Nm (/ 1000)
            p_si = parse_ui_float(self.ui.Edit_PreloadTorsSpring.text()) / 1000.0
        except ValueError: return

        counter = len(self.springs_list) + 1
        s_name = f"TorsSpring_{counter}"
        while any(s.name == s_name for s in self.springs_list):
            counter += 1
            s_name = f"TorsSpring_{counter}"

        spring = TorsionSpring(
            name=s_name, body_i=body_i, rf_i_name=self.ui.Edit_RFBodyI_TorsSpring.text().strip(),
            body_j=body_j, rf_j_name=self.ui.Edit_RFBodyJ_TorsSpring.text().strip(), 
            axis_choice=self.ui.cmbSpringBodyIAnchorXYZ.currentText().strip().upper(),
            plotter=self.plotter
        )
        
        spring.stiffness = k_si
        spring.damping = c_si
        spring.preload = p_si

        # Lock in the geometric vectors
        axis_choice = self.ui.cmbSpringBodyIAnchorXYZ.currentText().strip().upper()
        spring.bind_kinematics(self.rframes, axis_choice)
        self.springs_list.append(spring)
        QTreeWidgetItem(self.node_springs, [spring.name])
        
        self.ui.Edit_TorsSpringName.setText(spring.name)
        self.ui.btnAddTorsSpring.setEnabled(False)
        
        self.invalidate_results()
        print(f"Added {spring.name}")
        
        # Force visual update
        spring.update_transform(self.rframes[0].base_scale if self.rframes else 10.0)
        self.update_rframe_scales()
        self.plotter.render()

    def update_tors_spring(self):
        target_name = self.ui.Edit_TorsSpringName.text().strip()
        spring = next((s for s in self.springs_list if s.name == target_name), None)
        if not spring: return
        
        try:
            spring.stiffness = parse_ui_float(self.ui.Edit_StiffnessTorsSpring.text()) / 1000.0
            spring.damping = parse_ui_float(self.ui.Edit_DampingTorsSpring.text()) / 1000.0
            spring.preload = parse_ui_float(self.ui.Edit_PreloadTorsSpring.text()) / 1000.0
            
            # Update Axis and RF J if they changed
            spring.axis_choice = self.ui.cmbSpringBodyIAnchorXYZ.currentText().strip().upper()
            spring.rf_j_name = self.ui.Edit_RFBodyJ_TorsSpring.text().strip()
        except ValueError: return
        
        self.invalidate_results()
        print(f"Updated {spring.name}")

    def delete_tors_spring(self):
        target_name = self.ui.Edit_TorsSpringName.text().strip()
        spring = next((s for s in self.springs_list if s.name == target_name), None)
        if not spring: return
        
        # --- THE UPGRADE: Ask for permission! ---
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete Torsion Spring '{spring.name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No: return
        # ----------------------------------------
        
        for act in spring.actors: self.plotter.remove_actor(act)
        self.springs_list.remove(spring)
        for i in range(self.node_springs.childCount()):
            if self.node_springs.child(i).text(0) == spring.name:
                self.node_springs.takeChild(i)
                break
            
        self.invalidate_results()    
        self.ui.Edit_TorsSpringName.setText("")
        self.plotter.render()
        
    def rename_tors_spring(self):
        """ Triggers a pop-up window to safely rename the targeted Torsion Spring. """
        target_name = self.ui.Edit_TorsSpringName.text().strip()
        if not target_name:
            print("Please select a Torsion Spring to rename.")
            return

        spring = next((s for s in self.springs_list if s.name == target_name), None)
        if not spring: return

        old_name = spring.name
        new_name, ok = QInputDialog.getText(self, "Rename Torsion Spring", "Enter new name:", text=old_name)

        if not ok or not new_name.strip(): return 
        new_name = new_name.strip()
        if new_name == old_name: return 

        if any(s.name == new_name for s in self.springs_list):
            QMessageBox.warning(self, "Rename Error", f"A Spring with the name '{new_name}' already exists!")
            return

        spring.name = new_name
        self.ui.Edit_TorsSpringName.setText(new_name)

        for i in range(self.node_springs.childCount()):
            if self.node_springs.child(i).text(0) == old_name:
                self.node_springs.child(i).setText(0, new_name)
                break

        print(f"Successfully renamed Torsion Spring '{old_name}' to '{new_name}'.")
        if hasattr(self, 'invalidate_results'):
            self.invalidate_results()
    
    def toggle_tors_spring_enabled(self, state):
        """ Toggles the physical and visual state of the selected Torsion Spring. """
        target_name = self.ui.Edit_TorsSpringName.text().strip()
        if not target_name: return
        
        spring = next((s for s in self.springs_list if s.name == target_name), None)
        if spring:
            spring.enabled = state
            
            # --- THE FIX: Call Smart Enable! ---
            if state: 
                self._auto_enable_linked_bodies(spring)
            # -----------------------------------
                
            current_scale = self.rframes[0].base_scale if self.rframes else 10.0
            spring.update_transform(current_scale) # Visually hides/shows it
            
            self.refresh_tree_visuals()
            self.plotter.render()
            
            if hasattr(self, 'invalidate_results'):
                self.invalidate_results()
            
    # ==========================================
    # --- BUSHINGS ---
    # ==========================================
    def prepare_new_bushing(self):
        self.clear_selection()
        self.ui.Edit_BushingName.setText("")
        self.ui.Edit_BodyI_Bushing.setText("")
        self.ui.Edit_BodyJ_Bushing.setText("")
        self.ui.Edit_RFBodyI_Bushing.setText("")
        self.ui.Edit_RFBodyJ_Bushing.setText("")
               
        for field in [self.ui.Edit_Kx, self.ui.Edit_Ky, self.ui.Edit_Kz,
                      self.ui.Edit_Cx, self.ui.Edit_Cy, self.ui.Edit_Cz,
                      self.ui.Edit_Px, self.ui.Edit_Py, self.ui.Edit_Pz]:
            field.setText("0.0")
            
        for field in [self.ui.Edit_KRx, self.ui.Edit_KRy, self.ui.Edit_KRz,
                      self.ui.Edit_CRx, self.ui.Edit_CRy, self.ui.Edit_CRz,
                      self.ui.Edit_PRx, self.ui.Edit_PRy, self.ui.Edit_PRz]:
            field.setText("0.0")
            
        self.ui.chkEnabledBushing.blockSignals(True)
        self.ui.chkEnabledBushing.setChecked(True)
        self.ui.chkEnabledBushing.blockSignals(False)
        
        self.ui.btnAddBushing.setEnabled(True)
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(7) 

    def _read_bushing_ui_arrays(self):
        """ Helper: Extracts UI inputs, converts to SI, and returns NumPy arrays. """
        # Trans: UI (N/mm) -> SI (N/m) * 1000
        k_t = np.array([parse_ui_float(self.ui.Edit_Kx.text()), parse_ui_float(self.ui.Edit_Ky.text()), parse_ui_float(self.ui.Edit_Kz.text())]) * 1000.0
        c_t = np.array([parse_ui_float(self.ui.Edit_Cx.text()), parse_ui_float(self.ui.Edit_Cy.text()), parse_ui_float(self.ui.Edit_Cz.text())]) * 1000.0
        p_t = np.array([parse_ui_float(self.ui.Edit_Px.text()), parse_ui_float(self.ui.Edit_Py.text()), parse_ui_float(self.ui.Edit_Pz.text())])
        
        # Rot: UI (Nmm/rad) -> SI (Nm/rad) / 1000
        k_r = np.array([parse_ui_float(self.ui.Edit_KRx.text()), parse_ui_float(self.ui.Edit_KRy.text()), parse_ui_float(self.ui.Edit_KRz.text())]) / 1000.0
        c_r = np.array([parse_ui_float(self.ui.Edit_CRx.text()), parse_ui_float(self.ui.Edit_CRy.text()), parse_ui_float(self.ui.Edit_CRz.text())]) / 1000.0
        p_r = np.array([parse_ui_float(self.ui.Edit_PRx.text()), parse_ui_float(self.ui.Edit_PRy.text()), parse_ui_float(self.ui.Edit_PRz.text())]) / 1000.0
        return k_t, c_t, p_t, k_r, c_r, p_r

    def add_bushing(self):
        body_i_name = self.ui.Edit_BodyI_Bushing.text().strip()
        body_j_name = self.ui.Edit_BodyJ_Bushing.text().strip()
        if not body_i_name or not body_j_name: return
        
        body_i = self.physics_bodies.get(body_i_name)
        body_j = self.physics_bodies.get(body_j_name)
        if not body_i or not body_j: return
        
        try:
            k_t, c_t, p_t, k_r, c_r, p_r = self._read_bushing_ui_arrays()
        except ValueError: return

        counter = len(self.bushings_list) + 1
        b_name = f"Bushing_{counter}"
        while any(b.name == b_name for b in self.bushings_list):
            counter += 1
            b_name = f"Bushing_{counter}"

        bushing = Bushing(
            name=b_name, body_i=body_i, rf_i_name=self.ui.Edit_RFBodyI_Bushing.text().strip(),
            body_j=body_j, rf_j_name=self.ui.Edit_RFBodyJ_Bushing.text().strip(), plotter=self.plotter
        )
        
        bushing.k_trans, bushing.c_trans, bushing.p_trans = k_t, c_t, p_t
        bushing.k_rot, bushing.c_rot, bushing.p_rot = k_r, c_r, p_r

        # Bind the geometric triad directly to RF_I!
        bushing.bind_kinematics(self.rframes)
        
        self.bushings_list.append(bushing)
        QTreeWidgetItem(self.node_bushings, [bushing.name])
        
        self.ui.Edit_BushingName.setText(bushing.name)
        self.ui.btnAddBushing.setEnabled(False)
        
        self.invalidate_results()
        print(f"Added {bushing.name}")
        
        bushing.update_transform(self.rframes[0].base_scale if self.rframes else 10.0)
        self.update_rframe_scales()
        self.plotter.render()

    def update_bushing(self):
        target_name = self.ui.Edit_BushingName.text().strip()
        bushing = next((b for b in self.bushings_list if b.name == target_name), None)
        if not bushing: return
        
        try:
            k_t, c_t, p_t, k_r, c_r, p_r = self._read_bushing_ui_arrays()
            bushing.k_trans, bushing.c_trans, bushing.p_trans = k_t, c_t, p_t
            bushing.k_rot, bushing.c_rot, bushing.p_rot = k_r, c_r, p_r
            bushing.rf_j_name = self.ui.Edit_RFBodyJ_Bushing.text().strip()
        except ValueError: return
        
        self.invalidate_results()
        print(f"Updated {bushing.name}")

    def delete_bushing(self):
        target_name = self.ui.Edit_BushingName.text().strip()
        bushing = next((b for b in self.bushings_list if b.name == target_name), None)
        if not bushing: return
        
        # --- THE UPGRADE: Ask for permission! ---
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete Bushing '{bushing.name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No: return
        # ----------------------------------------
        
        for act in bushing.actors: self.plotter.remove_actor(act)
        self.bushings_list.remove(bushing)
        for i in range(self.node_bushings.childCount()):
            if self.node_bushings.child(i).text(0) == bushing.name:
                self.node_bushings.takeChild(i)
                break
        self.ui.Edit_BushingName.setText("")
        
        self.invalidate_results()
        self.plotter.render()

    def rename_bushing(self):
        """ Triggers a pop-up window to safely rename the targeted Bushing. """
        target_name = self.ui.Edit_BushingName.text().strip()
        if not target_name:
            print("Please select a Bushing to rename.")
            return

        bushing = next((b for b in self.bushings_list if b.name == target_name), None)
        if not bushing: return

        old_name = bushing.name
        new_name, ok = QInputDialog.getText(self, "Rename Bushing", "Enter new name:", text=old_name)

        if not ok or not new_name.strip(): return 
        new_name = new_name.strip()
        if new_name == old_name: return 

        if any(b.name == new_name for b in self.bushings_list):
            QMessageBox.warning(self, "Rename Error", f"A Bushing with the name '{new_name}' already exists!")
            return

        bushing.name = new_name
        self.ui.Edit_BushingName.setText(new_name)

        for i in range(self.node_bushings.childCount()):
            if self.node_bushings.child(i).text(0) == old_name:
                self.node_bushings.child(i).setText(0, new_name)
                break

        print(f"Successfully renamed Bushing '{old_name}' to '{new_name}'.")
        if hasattr(self, 'invalidate_results'):
            self.invalidate_results()
    
    def toggle_bushing_enabled(self, state):
        """ Toggles the physical and visual state of the selected Bushing. """
        target_name = self.ui.Edit_BushingName.text().strip()
        if not target_name: return
        
        bushing = next((b for b in getattr(self, 'bushings_list', []) if b.name == target_name), None)
        if bushing:
            bushing.enabled = state
            
            # --- THE FIX: Call Smart Enable! ---
            if state: 
                self._auto_enable_linked_bodies(bushing)
            # -----------------------------------
                
            current_scale = self.rframes[0].base_scale if self.rframes else 10.0
            bushing.update_transform(current_scale) # Visually hides/shows it
            
            self.refresh_tree_visuals()
            self.plotter.render()
            
            if hasattr(self, 'invalidate_results'):
                self.invalidate_results()
            
    # ==========================================
    # --- CONTACT PAIRS ---
    # ==========================================
    def prepare_new_contact(self):
        """ Prepares the UI Page 8 for defining a brand new Contact pair. """
        self.clear_selection()
        self.ui.Edit_ContactName.setText("")
        self.ui.Edit_BodyI_Contact.setText("")
        self.ui.Edit_BodyJ_Contact.setText("")
        
        # Default physical parameters for steel/hard plastic
        self.ui.Edit_ContactStiffness.setText("500.0")
        self.ui.Edit_ContactDamping.setText("10.0")
        self.ui.dsbForceExponent.setValue(1.5)
        
        # --- Reset Friction UI ---
        self.ui.chkContactFriction.setChecked(False)
        self.ui.frmContactFriction.setEnabled(False)
        self.ui.dsbContactFrictionCoeff.setValue(0.3)
        
        self.ui.dsbTolVelocity.setValue(10.0)
        
        # --- Reset Combo Box to Standard (Index 0) ---
        if hasattr(self.ui, 'cmbContactMesh'):
            self.ui.cmbContactMesh.setCurrentIndex(0)
        
        self.ui.chkEnabledContact.blockSignals(True)
        self.ui.chkEnabledContact.setChecked(True)
        self.ui.chkEnabledContact.blockSignals(False)
        
        self.ui.btnAddContact.setEnabled(True)
        self.ui.dckProperties.show()
        self.ui.stckProperties.setCurrentIndex(8) 

    def add_contact(self):
        """ Extracts UI inputs, converts units to SI, and creates the ContactPair. """
        body_i_name = self.ui.Edit_BodyI_Contact.text().strip()
        body_j_name = self.ui.Edit_BodyJ_Contact.text().strip()
        if not body_i_name or not body_j_name: return
        
        body_i = self.physics_bodies.get(body_i_name)
        body_j = self.physics_bodies.get(body_j_name)
        if not body_i or not body_j: return

        # --- Ground Protection ---
        if body_i.is_ground or body_j.is_ground:
            QMessageBox.warning(self, "Protection", "The Ground has no physical CAD mesh for collision detection.\n\nTip: To create a solid floor, generate a Fixed 'Box' primitive and connect it to the Ground using a Fixed Joint.")
            return
                
        # Prevent identical pairs
        for cp in self.contact_pairs:
            if (cp.body_i == body_i and cp.body_j == body_j) or (cp.body_i == body_j and cp.body_j == body_i):
                print(f"Warning: A contact constraint already exists between these bodies.")
                return

        try:
            k_ui = parse_ui_float(self.ui.Edit_ContactStiffness.text())
            c_ui = parse_ui_float(self.ui.Edit_ContactDamping.text())
            n_exp = float(self.ui.dsbForceExponent.value())
            
            # --- Extract Friction ---
            frict_on = self.ui.chkContactFriction.isChecked()
            mu_val = float(self.ui.dsbContactFrictionCoeff.value())
            slip_val = float(self.ui.dsbTolVelocity.value())
            # --- Extract Fine Mesh State ---
            
            # --- Extract Mesh Simplification Mode ---
            m_mode = self.ui.cmbContactMesh.currentIndex() if hasattr(self.ui, 'cmbContactMesh') else 0
            
        except ValueError: 
            print("Error: Invalid numerical values for contact parameters.")
            return

        counter = len(self.contact_pairs) + 1
        c_name = f"Contact_{counter}"
        while any(c.name == c_name for c in self.contact_pairs):
            counter += 1
            c_name = f"Contact_{counter}"

        # Initialize passing the raw UI values; unit_collision handles the (1000**n) conversion natively!
        new_contact = ContactPair(
            name=c_name, 
            body_i=body_i, 
            body_j=body_j, 
            stiffness_ui=k_ui, 
            exponent=n_exp, 
            damping_ui=c_ui,
            friction_enabled=frict_on,  
            mu=mu_val,                  
            slip_tol_ui=slip_val,   
            mesh_mode=m_mode       
        )
        
        self.contact_pairs.append(new_contact)
        QTreeWidgetItem(self.node_contacts, [new_contact.name])
        
        self.ui.Edit_ContactName.setText(new_contact.name)
        self.ui.btnAddContact.setEnabled(False)
        
        self.invalidate_results()
        print(f"Added {new_contact.name} (K: {k_ui} N/mm^{n_exp}, C: {c_ui} N/(mm/s), Exp: {n_exp})")
        self.plotter.render()

    def update_contact(self):
        """ Updates an existing Contact Pair and dynamically recalculates the SI conversion. """
        target_name = self.ui.Edit_ContactName.text().strip()
        contact = next((c for c in self.contact_pairs if c.name == target_name), None)
        if not contact: return
        
        try:
            k_ui = parse_ui_float(self.ui.Edit_ContactStiffness.text())
            c_ui = parse_ui_float(self.ui.Edit_ContactDamping.text())
            n_exp = float(self.ui.dsbForceExponent.value())
            
            # --- Extract Friction ---
            frict_on = self.ui.chkContactFriction.isChecked()
            mu_val = float(self.ui.dsbContactFrictionCoeff.value())
            slip_val = float(self.ui.dsbTolVelocity.value())
            
            # --- Extract Mesh Simplification Mode ---
            m_mode = self.ui.cmbContactMesh.currentIndex() if hasattr(self.ui, 'cmbContactMesh') else 0
            
            # --- Update Mesh Mode Property ---
            contact.mesh_mode = m_mode
            
            contact.exponent = n_exp
            # UI (N/mm^n) -> SI (N/m^n)
            contact.stiffness = k_ui * (1000.0 ** n_exp)
            # UI (N/(mm/s)) -> SI (N/(m/s))
            contact.damping = c_ui * 1000.0
            
            # --- Update Friction Math ---
            contact.friction_enabled = frict_on
            contact.mu = mu_val
            contact.slip_tolerance = slip_val / 1000.0
            
            # --- Update Fine Mesh Property ---
            contact.mesh_mode=m_mode
            
            # Optional: Enable flag
            contact.enabled = self.ui.chkEnabledContact.isChecked()
            
        except ValueError: return
        
        self.invalidate_results()
        print(f"Updated {contact.name}")

    def delete_contact(self):
        """ Permanently deletes the selected Contact Pair. """
        target_name = self.ui.Edit_ContactName.text().strip()
        contact = next((c for c in self.contact_pairs if c.name == target_name), None)
        if not contact: return
        
        # --- THE UPGRADE: Ask for permission! ---
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete Contact Pair '{contact.name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No: return
        # ----------------------------------------
        
        self.contact_pairs.remove(contact)
        
        for i in range(self.node_contacts.childCount()):
            if self.node_contacts.child(i).text(0) == contact.name:
                self.node_contacts.takeChild(i)
                break
                
        self.ui.Edit_ContactName.setText("")
        self.ui.Edit_BodyI_Contact.setText("")
        self.ui.Edit_BodyJ_Contact.setText("")
        self.ui.btnAddContact.setEnabled(True)
        
        self.clear_selection()
        self.plotter.render()
        
        self.invalidate_results()
        print(f"Deleted {target_name}")

    def rename_contact(self):
        """ Triggers a pop-up window to safely rename the targeted Contact Pair. """
        target_name = self.ui.Edit_ContactName.text().strip()
        if not target_name:
            print("Please select a Contact Pair to rename.")
            return

        contact = next((c for c in self.contact_pairs if c.name == target_name), None)
        if not contact: return

        old_name = contact.name
        new_name, ok = QInputDialog.getText(self, "Rename Contact", "Enter new name:", text=old_name)

        if not ok or not new_name.strip(): return 
        new_name = new_name.strip()
        if new_name == old_name: return 

        if any(c.name == new_name for c in self.contact_pairs):
            QMessageBox.warning(self, "Rename Error", f"A Contact Pair with the name '{new_name}' already exists!")
            return

        contact.name = new_name
        self.ui.Edit_ContactName.setText(new_name)

        for i in range(self.node_contacts.childCount()):
            if self.node_contacts.child(i).text(0) == old_name:
                self.node_contacts.child(i).setText(0, new_name)
                break

        print(f"Successfully renamed Contact Pair '{old_name}' to '{new_name}'.")
        if hasattr(self, 'invalidate_results'):
            self.invalidate_results()
    
    def toggle_contact_enabled(self, state):
        """ Toggles whether the selected Contact Pair computes collisions. """
        target_name = self.ui.Edit_ContactName.text().strip()
        if not target_name: return
        
        contact = next((c for c in getattr(self, 'contact_pairs', []) if c.name == target_name), None)
        if contact:
            contact.enabled = state
            
        # --- THE FIX: Call Smart Enable! ---
            if state: 
                self._auto_enable_linked_bodies(contact)
        # -----------------------------------
                    
            if hasattr(self, 'invalidate_results'):
                self.invalidate_results()
        
        self.refresh_tree_visuals()
            
    # ==========================================
    # --- VIEWPORT DISPLAY TOGGLES ---
    # ==========================================

    def toggle_all_edges(self):
        """ Toggles wireframes for all bodies globally. Replaces chkShowEdges. """
        self.edges_visible = not self.edges_visible
        
        for body in self.physics_bodies.values():
            if body.is_ground: continue 
            body.show_edges = self.edges_visible
            body.actor.prop.show_edges = self.edges_visible
            
        self.plotter.render()

    def toggle_grid(self):
        """ Toggles the PyVista 3D measurement grid on and off with theme-aware coloring. """
        self.grid_visible = not self.grid_visible
        
        if self.grid_visible:
            # Check the current background theme to choose the right grid color
            grid_color = 'black' if self.bg_is_light else 'gray'
            self.plotter.show_grid(color=grid_color, font_size=10)
        else:
            self.plotter.remove_bounds_axes() # Removes the grid overlay
            
        self.plotter.render()

    def toggle_auxiliary_objects(self, is_hidden):
        """ 
        Declutters the viewport by hiding all RFs, Joints, Forces, and Bushings.
        Only Bodies and Compression/Torsion Springs remain visible when checked.
        """
        show_objects = not is_hidden
        current_scale = self.rframes[0].base_scale if self.rframes else 10.0
        
        # 1. Reference Frames
        for rf in self.rframes:
            if show_objects:
                if rf.is_cog and rf.parent_body:
                    rf.set_visible(rf.parent_body.visible)
                else:
                    rf.set_visible(True)
            else:
                rf.set_visible(False)

        # 2. Joints
        for joint in getattr(self, 'joints_list', []):
            joint.set_visible(show_objects)
            if show_objects:
                joint.update_transform(current_scale)

        # 3. Forces & Torques (Respecting the separate Gravity checkbox!)
        gravity_allowed = self.ui.chkVisibleGravity.isChecked()
        for force in getattr(self, 'forces_list', []):
            if show_objects:
                if force.is_gravity:
                    force.set_visible(gravity_allowed) 
                else:
                    force.set_visible(True)
                force.update_transform(current_scale, t=self.playback_time)
            else:
                force.set_visible(False)

        # 4. Bushings (Uses BaseSpring inheritance)
        for bushing in getattr(self, 'bushings_list', []):
            bushing.visible = show_objects
            bushing.update_transform(current_scale)

        self.refresh_tree_visuals()
        self.plotter.render()

    def unhide_all(self):
        """ Restores visibility to all objects in the scene and updates the Tree. """
        # 1. Unhide Bodies
        for name, body in self.physics_bodies.items():
            if body.is_ground: continue 
                
            body.visible = True
            if body.actor:
                body.actor.SetVisibility(True)
            
            # Sync the UI checkbox if this happens to be the currently selected body
            if name == self.selected_body:
                self.ui.chkVisible.blockSignals(True)
                self.ui.chkVisible.setChecked(True)
                self.ui.chkVisible.blockSignals(False)

        # 2. Unhide Reference Frames
        for rf in self.rframes:
            rf.set_visible(True)

        # 3. Unhide Components (Joints, Forces, Springs, Bushings)
        current_scale = self.rframes[0].base_scale if self.rframes else 10.0
        
        for joint in getattr(self, 'joints_list', []):
            joint.visible = True
            joint.set_visible(True)
            
        gravity_allowed = self.ui.chkVisibleGravity.isChecked() 
        for force in getattr(self, 'forces_list', []):
            force.visible = True
            if force.is_gravity:
                force.set_visible(gravity_allowed)
            else:
                force.set_visible(True)
                
        for spring in getattr(self, 'springs_list', []):
            spring.visible = True
            spring.update_transform(current_scale)
            
        for bushing in getattr(self, 'bushings_list', []):
            bushing.visible = True
            bushing.update_transform(current_scale)
        
        # 3.5 Uncheck the "Hide/Show Objects" button to reflect the unhidden state
        
        self.ui.btnHideShowObjects.setChecked(False)
        hide_aux = False # self.ui.btnHideShowObjects.isChecked()
        
        # 4. Refresh the UI Tree and Viewport
        self.refresh_tree_visuals()
        self.plotter.render()

    def hide_all_except_selected(self):
        """ Isolates the currently selected body, hiding everything else except its linked components. 
            Related components that are already hidden will remain hidden.
        """
        if not self.selected_body:
            print("Please select a single Rigid Body first.")
            return

        current_scale = self.rframes[0].base_scale if self.rframes else 10.0

        # 1. Hide Bodies (Unhide ONLY the explicitly selected body)
        for name, body in self.physics_bodies.items():
            if body.is_ground: continue 
                
            if name == self.selected_body:
                body.visible = True
                if body.actor:
                    body.actor.SetVisibility(True)
                
                # Sync the UI checkbox for the selected body
                self.ui.chkVisible.blockSignals(True)
                self.ui.chkVisible.setChecked(True)
                self.ui.chkVisible.blockSignals(False)
            else:
                body.visible = False
                if body.actor:
                    body.actor.SetVisibility(False)

        # 2. Hide RFrames (Leave Global RF and active CoG RF alone, hide everything else)
        for rf in getattr(self, 'rframes', []):
            if rf.name == "Global_RF":
                pass # Do not unhide, keep current state
            elif getattr(rf, 'is_cog', False) and getattr(rf, 'parent_body', None) and rf.parent_body.name == self.selected_body:
                pass # Do not unhide, keep current state
            else:
                rf.set_visible(False)

        # 3. Hide Forces (Leave forces attached to the active body alone, hide everything else)
        for force in getattr(self, 'forces_list', []):
            if getattr(force, 'parent_body', None) and force.parent_body.name == self.selected_body:
                pass # Do not unhide, keep current state
            else:
                force.visible = False
                force.set_visible(False)
                
        # 4. Hide Joints
        for joint in getattr(self, 'joints_list', []):
            if joint.body_i.name == self.selected_body or joint.body_j.name == self.selected_body:
                pass # Do not unhide, keep current state
            else:
                joint.visible = False
                joint.set_visible(False)
                
        # 5. Hide Springs
        for spring in getattr(self, 'springs_list', []):
            if spring.body_i.name == self.selected_body or spring.body_j.name == self.selected_body:
                pass # Do not unhide, keep current state
            else:
                spring.visible = False
                spring.update_transform(current_scale)
                
        # 6. Hide Bushings
        for bushing in getattr(self, 'bushings_list', []):
            if bushing.body_i.name == self.selected_body or bushing.body_j.name == self.selected_body:
                pass # Do not unhide, keep current state
            else:
                bushing.visible = False
                bushing.update_transform(current_scale)

        # 7. Refresh the UI Tree and Viewport
        self.refresh_tree_visuals()                 
        self.plotter.render()

    def toggle_background(self):
        """ Toggles the viewport background and dynamically updates the grid and axes contrast. """
        self.bg_is_light = not self.bg_is_light
        
        # Determine appropriate contrast color based on the new background
        contrast_color = 'black' if self.bg_is_light else 'gray'
        
        if self.bg_is_light:
            self.plotter.set_background('lightgray')
        else:
            self.plotter.set_background('#1e1e1e') 
            
        # 1. Re-draw the grid with the new contrasting color
        if self.grid_visible:
            self.plotter.show_grid(color=contrast_color, font_size=10)
            
        # 2. Re-draw the XYZ Axes in the corner with the new text color
        self.plotter.add_axes(color=contrast_color)
        
        #self.plotter.reset_camera()                    
        self.plotter.render()

    def open_telemetry_window(self):
        """ Launches the Post-Processor if simulation results exist. """
        if getattr(self, 'solver', None) is None or getattr(self.solver, 'simulation_history', None) is None:
            QMessageBox.warning(self, "No Data", "Please run or load a simulation before opening Telemetry.")
            return

        from unit_telemetry import TelemetryWindow
        
        # Create and show the floating window
        self.telemetry_window = TelemetryWindow(
            solver=self.solver,
            dt=self.simulation_dt,
            bodies=self.physics_bodies,
            joints=getattr(self, 'joints_list', []),
            forces=self.forces_list,
            springs=getattr(self, 'springs_list', []),
            contacts=getattr(self, 'contact_pairs', []),
            bushings=getattr(self, 'bushings_list', []), 
            gear_pairs=getattr(self, 'gear_pairs_list', []),
            motions_list=getattr(self, 'motions_list', []),
            parent=self 
        )
        self.telemetry_window.show()

    # =====================
    # -----  GEARS
    # =====================
    
    def on_gear_type_changed(self, index):
        """ Dynamically enables/disables Gear inputs based on the selected type. """
        # 0: Helical, 1: Inner Ring, 2: Bevel
        self.ui.dsbHelixAngle.setEnabled(index in [0, 1])
        self.ui.dsbPitchAngle.setEnabled(index == 2)
        self.ui.dsbBoreDia.setEnabled(index in [0, 2])
        self.ui.dsbRimDia.setEnabled(index == 1)
        
        self.ui.dsbHelixAngle.setVisible(index in [0, 1])
        self.ui.dsbPitchAngle.setVisible(index == 2)
        self.ui.dsbBoreDia.setVisible(index in [0, 2])
        self.ui.dsbRimDia.setVisible(index == 1)
        
        self.ui.lblHelixAngle.setVisible(index in [0, 1])
        self.ui.lblPitchAngle.setVisible(index == 2)
        self.ui.lblBoreDia.setVisible(index in [0, 2])
        self.ui.lblRimDia.setVisible(index == 1)
        
        """
        # Set unapplicable values based on gear type
        if index == 0:  # Helical
            self.ui.dsbRimDia.setValue(0.0)
            self.ui.dsbPitchAngle.setValue(0.0)
        elif index == 1:  # Inner Ring
            self.ui.dsbBoreDia.setValue(0.0)
            self.ui.dsbPitchAngle.setValue(0.0)
        elif index == 2:  # Bevel
            self.ui.dsbHelixAngle.setValue(0.0)
            self.ui.dsbRimDia.setValue(0.0)
        """
        
    def on_joint_gear_type_changed(self, index):
        """ 0: Helical/Spur, 1: Inner Ring, 2: Bevel """
        self.ui.dsbJointHelixAngle.setEnabled(index in [0, 1])
        self.ui.dsbJointPitchAngle.setEnabled(index == 2)
        
        self.ui.dsbJointHelixAngle.setVisible(index in [0, 1])
        self.ui.dsbJointPitchAngle.setVisible(index == 2)
        
        self.ui.lblJointHelixAngle.setVisible(index in [0, 1])
        self.ui.lblJointPitchAngle.setVisible(index == 2)
            
    def create_gear_from_ui(self):
        """ Phase 4: Reads the UI inputs, generates the mesh, and aligns it to the user's RF. """
        rf_name = self.ui.Edit_RFGear.text().strip()
        if not rf_name:
            print("Error: Please select a Reference Frame to position the Gear.")
            return

        target_rf = next((r for r in self.rframes if r.name == rf_name), None)
        if not target_rf: 
            return

        # 1. Read UI Inputs
        gear_type = self.ui.cmbGearType.currentIndex()
        module = float(self.ui.dsbModule.value())
        z = int(self.ui.dsbNTeeth.value())
        width = float(self.ui.dsbGearWidth.value())
        alpha = float(self.ui.dsbPressureAngle.value())
        beta = float(self.ui.dsbHelixAngle.value())
        gamma = float(self.ui.dsbPitchAngle.value())
        
        # Generator expects radii, but UI provides Diameters!
        bore = float(self.ui.dsbBoreDia.value()) / 2.0 
        rim = float(self.ui.dsbRimDia.value()) / 2.0

        from unit_gears import GearGenerator

        # 2. Call the Procedural Generator
        if gear_type == 0: # Helical/Spur
            tri_mesh, back_face_z = GearGenerator.generate_helical_gear(module, z, width, alpha, beta, bore)
            prefix = "HelicalGear" if beta != 0.0 else "SpurGear"
            
        elif gear_type == 1: # Inner Ring
            tri_mesh, back_face_z = GearGenerator.generate_inner_gear(module, z, width, alpha, beta, rim)
            prefix = "RingGear"
            
        elif gear_type == 2: # Bevel
            tri_mesh, back_face_z = GearGenerator.generate_bevel_gear(module, z, width, alpha, gamma, bore)
            prefix = "BevelGear"

        gear_name = f"{prefix}_M{int(module)}_Z{z}"

        # 3. Pass to the Master Physics Pipeline (Spawns Body & CoG RF)
        self._process_imported_meshes([tri_mesh], original_cad_name=gear_name)

        body_name = f"Body_{self.body_counter}"
        new_gear_body = self.physics_bodies[body_name]

        # =========================================================
        # 4. MATHEMATICAL ALIGNMENT TO THE SELECTED REFERENCE FRAME
        # =========================================================
        axis_choice = self.ui.cmbRF_GearXYZ.currentText().strip().upper()

        # Generate a rotation matrix that rotates the Gear's local Z-axis (the extrusion vector)
        # so that it points down the user's selected axis (X, Y, or Z).
        if axis_choice == 'X':
            # Local Z -> Global X
            alignment_R = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])
        elif axis_choice == 'Y':
            # Local Z -> Global Y
            alignment_R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
        else:
            # Local Z -> Global Z (No change)
            alignment_R = np.eye(3)

        # Apply the RF's full spatial rotation to our axis permutation
        final_rot_matrix = target_rf.transform_matrix @ alignment_R

        # Calculate the local offset of the flat "Hub" face relative to the new CoG (in meters!)
        local_hub_offset_mm = np.array([0.0, 0.0, back_face_z]) - new_gear_body.raw_geom.center_mass
        local_hub_offset_m = local_hub_offset_mm / MMtoM

        # Shift the CoG in global space so the Hub face lands EXACTLY on target_rf.position
        global_cog = target_rf.position - (final_rot_matrix @ local_hub_offset_m)

        # 5. Apply the Transform to the Physics Body
        new_gear_body.cog = global_cog
        new_gear_body.principal_axes = final_rot_matrix

        from scipy.spatial.transform import Rotation
        r = Rotation.from_matrix(final_rot_matrix)
        euler_xyz = r.as_euler('xyz', degrees=True)
        new_gear_body.pos_angles = np.array([euler_xyz[2], euler_xyz[1], euler_xyz[0]])

        new_gear_body.update_graphics_matrix(new_gear_body.cog, new_gear_body.principal_axes)

        # 6. Update the auto-generated CoG RF to track the newly aligned body
        rf_cog_name = f"RF_CoG_{body_name}"
        cog_rf = next((r for r in self.rframes if r.name == rf_cog_name), None)
        if cog_rf:
            cog_rf.position = new_gear_body.cog
            cog_rf.orientation = new_gear_body.pos_angles
            cog_rf.transform_matrix = new_gear_body.principal_axes
            cog_rf.update_transform()

        # 7. Fix the Gravity Visual Bug
        # Since the CoG moved, we must tell any attached forces to redraw their arrows.
        current_scale = self.rframes[0].base_scale if self.rframes else 1.0
        for force in self.forces_list:
            if force.parent_body.name == new_gear_body.name:
                force.update_transform(current_scale)

        self.plotter.render()
        self.invalidate_results()
        print(f"Gear '{gear_name}' successfully aligned to '{rf_name}' along the {axis_choice}-Axis!")

    def validate_gear_pair(self, joint_1, joint_2, carrier_body, gear_type, module, z1, z2, beta1_deg, beta2_deg, gamma1_deg, gamma2_deg):
        """ Evaluates the Critical and Non-Critical Gear Checklist. Returns (is_valid, msg) """
        
        GearType = gear_type
        # ==========================================
        # 1. CRITICAL TOPOLOGY CHECKS
        # ==========================================
        if joint_1.body_j.name == joint_2.body_j.name:
            return False, "CRITICAL ERROR: Joint 1 and Joint 2 cannot point to the same Gear body."
            
        if carrier_body.name == joint_1.body_j.name or carrier_body.name == joint_2.body_j.name:
            return False, "CRITICAL ERROR: The Carrier cannot be the gear itself!"

        # --- Extract true global positions ---
        p1 = joint_1.body_i.cog + joint_1.body_i.principal_axes @ joint_1.local_pos_i
        p2 = joint_2.body_i.cog + joint_2.body_i.principal_axes @ joint_2.local_pos_i
        
        # --- Rename to axis1 and axis2 to avoid overwriting z1, z2 (Teeth!) ---
        axis1 = joint_1.body_i.principal_axes @ joint_1.local_axis_i
        axis2 = joint_2.body_i.principal_axes @ joint_2.local_axis_i
        
        # Calculate theoretical radii
        # --- Convert module from millimeters to meters! ---
        # --- Calculate theoretical radii directly from Transverse Module ---
        module_m = module / 1000.0
        beta1, beta2 = np.radians(beta1_deg), np.radians(beta2_deg)
        r1 = (module_m * z1) / 2.0
        r2 = (module_m * z2) / 2.0
        
        dist_vec = p2 - p1
        actual_dist = np.linalg.norm(dist_vec)
        dot_axes = np.clip(np.dot(axis1, axis2), -1.0, 1.0)
        angle_between_axes = np.degrees(np.arccos(abs(dot_axes)))

        # ==========================================
        # 2. CRITICAL GEOMETRY CHECKS
        # ==========================================
        if gear_type in [GearType.SPUR_HELICAL, GearType.INTERNAL]:
            # Check Parallel
            if angle_between_axes > 0.5: # 0.5 degree tolerance
                return False, f"CRITICAL ERROR: Helical/Inner gear axes must be parallel. Current angle is {angle_between_axes:.2f}°."
                
        elif gear_type == GearType.BEVEL:
            # Check Intersection (Shortest distance between two 3D lines)
            cross_z = np.cross(axis1, axis2)
            norm_cross = np.linalg.norm(cross_z)
            if norm_cross > 1e-6:
                shortest_distance = abs(np.dot(dist_vec, cross_z / norm_cross))
                if shortest_distance > 0.002: # 2 mm tolerance
                    return False, f"CRITICAL ERROR: Bevel gear axes do not intersect! Shortest distance is {shortest_distance*1000:.1f} mm. Hypoid gears are not supported."
        
        # ==========================================
        # 3. WARNING CHECKS (Not Critical)
        # ==========================================
        warnings = []
        
        if gear_type == GearType.SPUR_HELICAL:
            theoretical_dist = r1 + r2
            if abs(actual_dist - theoretical_dist) > 0.005: # 5mm warning
                warnings.append(f"WARNING: CAD center distance ({actual_dist*1000:.1f} mm) does not match theoretical distance ({(r1+r2)*1000:.1f} mm).")
            # Check Helical Handedness
            if beta1_deg != 0.0 and beta2_deg != 0.0 and (beta1_deg * beta2_deg > 0):
                warnings.append("WARNING: Both external helical gears have the same twist direction. Teeth will physically grind.")

        elif gear_type == GearType.INTERNAL:
            theoretical_dist = abs(r1 - r2)
            if abs(actual_dist - theoretical_dist) > 0.005:
                warnings.append(f"WARNING: CAD center distance ({actual_dist*1000:.1f} mm) does not match theoretical distance ({theoretical_dist*1000:.1f} mm).")

        elif gear_type == GearType.BEVEL:
            theoretical_angle = gamma1_deg + gamma2_deg
            if abs(angle_between_axes - theoretical_angle) > 0.5:
                warnings.append(f"WARNING: Joint shaft angle ({angle_between_axes:.1f}°) does not match theoretical gear pitch angles ({theoretical_angle:.1f}°).")
                
        warning_str = "\n".join(warnings)
        return True, warning_str
    
    def create_gear_pair_from_ui(self):
        # 1. Read the UI Text Fields
        j1_name = self.ui.Edit_JointGear1.text().strip()
        j2_name = self.ui.Edit_JointGear2.text().strip()
        carrier_name = self.ui.Edit_JointCarrier.text().strip()

        if not j1_name or not j2_name or not carrier_name:
            QMessageBox.critical(self, "Error", "Please select Joint 1, Joint 2, and the Carrier Body.")
            return

        # 2. Retrieve Objects from Memory
        joint_1 = next((j for j in self.joints_list if j.name == j1_name), None)
        joint_2 = next((j for j in self.joints_list if j.name == j2_name), None)
        
        if carrier_name.lower() == "ground":
            # Find the actual ground body in the dict
            carrier = next((b for b in self.physics_bodies.values() if b.is_ground), None)
        else:
            carrier = self.physics_bodies.get(carrier_name)

        if not joint_1 or not joint_2 or not carrier:
            QMessageBox.critical(self, "Error", "Could not find the specified Joints or Carrier in the project.")
            return

        # 3. Read Geometry Parameters
        gear_type_idx = self.ui.cmbJointGearType.currentIndex()
        module = float(self.ui.dsbJointModule.value())
        z1 = float(self.ui.dsbNTeethGear1.value())
        z2 = float(self.ui.dsbNTeethGear2.value())
        alpha = float(self.ui.dsbJointPressureAngle.value())
        beta = float(self.ui.dsbJointHelixAngle.value())
        gamma1 = float(self.ui.dsbJointPitchAngle.value())
        gamma2 = 90.0 - gamma1 # Assuming a 90-degree shaft intersection for bevels

        from unit_joints import GearType, GearPair
        if gear_type_idx == 0: g_type = GearType.SPUR_HELICAL
        elif gear_type_idx == 1: g_type = GearType.INTERNAL
        else: g_type = GearType.BEVEL

        # 4. Strict Inner Gear Rule
        if g_type == GearType.INTERNAL and z1 >= z2:
            QMessageBox.warning(self, "Logic Error", "For Inner Gears, Joint 2 must be the outer Ring Gear. Please ensure Z2 is strictly greater than Z1.")
            return

        # 5. Run the Mathematical Validation Checklist!
        is_valid, warning_msg = self.validate_gear_pair(
            joint_1, joint_2, carrier, g_type, module, z1, z2, beta, -beta, gamma1, gamma2
        )

        if not is_valid:
            QMessageBox.critical(self, "Topological Error", warning_msg)
            return

        if warning_msg: # If it's valid but has CAD warnings
            reply = QMessageBox.warning(self, "Geometric Warning", warning_msg + "\n\nDo you want to create the constraint anyway?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No: return

        # 6. Create the Gear Constraint!
        gear_name = f"GearConstraint_{len(self.gear_pairs_list)+1}"
        new_gear_pair = GearPair(
            name=gear_name,
            joint_1=joint_1,
            joint_2=joint_2,
            gear_type=g_type,
            module_n=module,
            z1=z1,
            z2=z2,
            alpha_deg=alpha,
            beta_deg=beta,
            gamma_deg=gamma1
        )
        
        # Override the auto-assigned carrier with the User's explicitly chosen Carrier
        new_gear_pair.carrier = carrier
        
        self.gear_pairs_list.append(new_gear_pair)

        # 7. Add to Tree Hierarchy
        from PySide6.QtWidgets import QTreeWidgetItem
        if not hasattr(self, 'node_gear_pairs'):
            self.node_gear_pairs = QTreeWidgetItem(self.ui.treeHierarchy, ["Gear Constraints"])
        
        QTreeWidgetItem(self.node_gear_pairs, [gear_name])
        self.ui.treeHierarchy.expandAll()
        self.invalidate_results()
        
        QMessageBox.information(self, "Success", f"Gear Pair '{gear_name}' successfully added to the solver!")

    def update_gear_pair(self):
        """ Updates the mathematical geometry of the selected Gear Pair Constraint. """
        target_name = self.ui.Edit_GearPairName.text().strip()
        if not target_name:
            QMessageBox.warning(self, "Error", "Please select a Gear Constraint to update.")
            return

        gear = next((g for g in getattr(self, 'gear_pairs_list', []) if g.name == target_name), None)
        if not gear: return

        # 1. Read Geometry Parameters from the UI
        gear_type_idx = self.ui.cmbJointGearType.currentIndex()
        module = float(self.ui.dsbJointModule.value())
        z1 = float(self.ui.dsbNTeethGear1.value())
        z2 = float(self.ui.dsbNTeethGear2.value())
        alpha = float(self.ui.dsbJointPressureAngle.value())
        beta = float(self.ui.dsbJointHelixAngle.value())
        gamma1 = float(self.ui.dsbJointPitchAngle.value())
        gamma2 = 90.0 - gamma1 # Assuming a 90-degree shaft intersection for bevels

        from unit_joints import GearType
        if gear_type_idx == 0: g_type = GearType.SPUR_HELICAL
        elif gear_type_idx == 1: g_type = GearType.INTERNAL
        else: g_type = GearType.BEVEL

        # 2. Strict Inner Gear Rule
        if g_type == GearType.INTERNAL and z1 >= z2:
            QMessageBox.warning(self, "Logic Error", "For Inner Gears, Joint 2 must be the outer Ring Gear. Please ensure Z2 is strictly greater than Z1.")
            return

        # 3. Run Mathematical Validation (Passing existing joints with new geometry!)
        is_valid, warning_msg = self.validate_gear_pair(
            gear.joint_1, gear.joint_2, gear.carrier, g_type, module, z1, z2, beta, -beta, gamma1, gamma2
        )

        if not is_valid:
            QMessageBox.critical(self, "Topological Error", warning_msg)
            return

        if warning_msg: 
            reply = QMessageBox.warning(self, "Geometric Warning", warning_msg + "\n\nDo you want to apply these updates anyway?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No: return

        # 4. Apply Updates to the Object (Converting UI degrees back to internal radians)
        import numpy as np
        gear.gear_type = g_type
        gear.module_n = module
        gear.z1 = z1
        gear.z2 = z2
        gear.alpha = np.radians(alpha)
        gear.beta = np.radians(beta)
        gear.gamma = np.radians(gamma1)

        if hasattr(self, 'invalidate_results'):
            self.invalidate_results()
            
        print(f"Updated Gear Constraint '{gear.name}'.")

    def rename_gear_pair(self):
        """ Triggers a pop-up window to safely rename the targeted Gear Constraint. """
        target_name = self.ui.Edit_GearPairName.text().strip()
        if not target_name:
            print("Please select a Gear Constraint to rename.")
            return

        gear = next((g for g in self.gear_pairs_list if g.name == target_name), None)
        if not gear: return

        old_name = gear.name
        new_name, ok = QInputDialog.getText(self, "Rename Gear Constraint", "Enter new name:", text=old_name)

        if not ok or not new_name.strip(): return 
        new_name = new_name.strip()
        if new_name == old_name: return 

        if any(g.name == new_name for g in self.gear_pairs_list):
            QMessageBox.warning(self, "Rename Error", f"A Gear Constraint with the name '{new_name}' already exists!")
            return

        # Update Memory and UI Box
        gear.name = new_name
        self.ui.Edit_GearPairName.setText(new_name)

        # Update Tree Hierarchy visually
        if hasattr(self, 'node_gear_pairs'):
            for i in range(self.node_gear_pairs.childCount()):
                if self.node_gear_pairs.child(i).text(0) == old_name:
                    self.node_gear_pairs.child(i).setText(0, new_name)
                    break

        print(f"Successfully renamed Gear Constraint '{old_name}' to '{new_name}'.")
        if hasattr(self, 'invalidate_results'):
            self.invalidate_results()

    def delete_gear_pair(self):
        """ Permanently deletes the selected Gear Constraint. """
        target_name = self.ui.Edit_GearPairName.text().strip()
        if not target_name:
            print("Please select a Gear Constraint to delete.")
            return

        gear = next((g for g in self.gear_pairs_list if g.name == target_name), None)
        if not gear: return

        # Prompt for Safety
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete Gear Constraint '{gear.name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No: return

        # 1. Delete from engine memory
        self.gear_pairs_list.remove(gear)
        
        # 2. Delete from TreeView
        if hasattr(self, 'node_gear_pairs'):
            for i in range(self.node_gear_pairs.childCount()):
                if self.node_gear_pairs.child(i).text(0) == gear.name:
                    self.node_gear_pairs.takeChild(i)
                    break
                
        # 3. Clean up UI
        self.ui.Edit_GearPairName.setText("")
        
        # Re-enable the Create button in case the user previously double-clicked the deleted gear
        if hasattr(self.ui, 'btnCreateGearPair'):
            self.ui.btnCreateGearPair.setEnabled(True) 
        
        self.ui.btnUpdateGearPair.setEnabled(False) # <--- Disable Update
        self.clear_selection()
        self.plotter.render()
        
        self.invalidate_results()
        print(f"Deleted Gear Constraint '{target_name}'.")
    
    def toggle_gearpair_enabled(self, state):
        """ Toggles the solver state of the selected Gear Pair Constraint. """
        target_name = self.ui.Edit_GearPairName.text().strip()
        if not target_name: return
        
        gear = next((g for g in getattr(self, 'gear_pairs_list', []) if g.name == target_name), None)
        if gear:
            gear.enabled = state
            
            self.refresh_tree_visuals()
            if hasattr(self, 'invalidate_results'):
                self.invalidate_results()
    
    def create_primitive_from_ui(self):
        """ Reads the UI, generates the requested 3D primitive, and injects it into the engine. """
        target_rf_name = self.ui.Edit_RFPrimitive.text().strip()
        rf1 = next((rf for rf in self.rframes if rf.name == target_rf_name), None)
        
        if not rf1:
            print("Please select a valid Target Reference Frame for the Primitive.")
            return

        prim_type = self.ui.cmbPrimitiveType.currentText()
        
        # Safely extract dimensions
        def get_dim(widget):
            if hasattr(widget, 'value'): return widget.value()
            else: return parse_ui_float(widget.text())
            
        d1 = get_dim(self.ui.dsbPrimDim1)
        d2 = get_dim(self.ui.dsbPrimDim2)
        d3 = get_dim(self.ui.dsbPrimDim3)
        
        axis_idx = self.ui.cmbRF_PrimXYZ.currentIndex() # 0: X, 1: Y, 2: Z
        
        # ==========================================
        # 1. Special "Dynamic Link" Logic
        # ==========================================
        is_dynamic_link = False
        rf2 = None
        target_rf2_name = getattr(self.ui, 'Edit_RFPrimTarget', None)
        R_dynamic_align = np.eye(3)
        
        if target_rf2_name and target_rf2_name.text().strip() and "Link" in prim_type:
            rf2 = next((rf for rf in self.rframes if rf.name == target_rf2_name.text().strip()), None)
            if rf2:
                is_dynamic_link = True
                p1 = rf1.position.copy()
                p2 = rf2.position.copy()
                
                # --- THE FIX 1: Convert Distance from Meters to Millimeters! ---
                from unit_rigidbody import MMtoM
                d3 = np.linalg.norm(p2 - p1) * MMtoM
                
                # --- THE FIX 2: Calculate the Spatial Rotation Matrix (Do not mutate the raw mesh) ---
                vec = p2 - p1
                if np.linalg.norm(vec) > 1e-8:
                    vec = vec / np.linalg.norm(vec)
                    z_axis = np.array([0, 0, 1])
                    rot_axis = np.cross(z_axis, vec)
                    sin_angle = np.linalg.norm(rot_axis)
                    cos_angle = np.dot(z_axis, vec)
                    
                    import trimesh.transformations as tf
                    if sin_angle > 1e-8:
                        rot_axis = rot_axis / sin_angle
                        angle = np.arctan2(sin_angle, cos_angle)
                        R_dynamic_align = tf.rotation_matrix(angle, rot_axis)[:3, :3]
                    elif cos_angle < 0:
                        R_dynamic_align = tf.rotation_matrix(np.pi, [1, 0, 0])[:3, :3]
                
        # ==========================================
        # 2. Call the Math Generator
        # ==========================================
        from unit_primitives import PrimitiveGenerator
        mesh_3d = None
        base_name = "Prim"
        
        if "Box" in prim_type:
            mesh_3d = PrimitiveGenerator.generate_box(d1, d2, d3)
            base_name = "Box"
        elif "Cylinder" in prim_type or "Tube" in prim_type:
            mesh_3d = PrimitiveGenerator.generate_tube(d1, d2, d3) 
            base_name = "Tube"
        elif "Sphere" in prim_type:
            mesh_3d = PrimitiveGenerator.generate_sphere(d1)
            base_name = "Sphere"
        elif "Prism" in prim_type:
            mesh_3d = PrimitiveGenerator.generate_prism(d1, d2, d3) 
            base_name = "Prism"
        elif "Torus" in prim_type:
            mesh_3d = PrimitiveGenerator.generate_torus(d1, d2)
            base_name = "Torus"
        elif "Cone" in prim_type:
            mesh_3d = PrimitiveGenerator.generate_truncated_cone(d1, d2, d3)
            base_name = "Cone"
        elif "Link" in prim_type:
            mesh_3d = PrimitiveGenerator.generate_link(d1, d2, d3)
            base_name = "Link"
        else:
            return

        # ==========================================
        # 3. Integrate into the MBD Engine
        # ==========================================
        import pyvista as pv
        from unit_forces import Force, ForceType, ForceFrame
        from PySide6.QtWidgets import QTreeWidgetItem
        
        # Convert Trimesh to PyVista PolyData
        faces_padded = np.insert(mesh_3d.faces, 0, 3, axis=1)
        pv_mesh = pv.PolyData(mesh_3d.vertices, faces_padded.flatten())
        pv_mesh = pv_mesh.clean().compute_normals(split_vertices=True, feature_angle=60)

        new_name = base_name + "_1"
        counter = 1
        while new_name in self.physics_bodies:
            counter += 1
            new_name = f"{base_name}_{counter}"

        new_actor = self.plotter.add_mesh(pv_mesh, color="lightblue", show_edges=self.edges_visible, pickable=True, smooth_shading=True)
        new_tree_item = QTreeWidgetItem(self.node_bodies, [new_name])
        
        # Create the Body. This inherently calculates mass and principal axes!
        new_body = RigidBody(new_name, mesh_3d, pv_mesh, new_actor, new_tree_item)
        new_body.center_and_align_mesh()

        # ==========================================
        # 4. Place the object in 3D Space
        # ==========================================
        from scipy.spatial.transform import Rotation
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            if is_dynamic_link:
                new_body.cog = (p1 + p2) / 2.0 
                # Apply the dynamically calculated target vector matrix!
                new_body.principal_axes = R_dynamic_align 
            else:
                new_body.cog = rf1.position.copy()
                
                # Assign Static Matrix mappings (Local Z to Target X, Y, or Z)
                if axis_idx == 0:
                    alignment_R = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]]) # Z -> X
                elif axis_idx == 1:
                    alignment_R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]]) # Z -> Y
                else:
                    alignment_R = np.eye(3) # Z -> Z
                    
                new_body.principal_axes = rf1.transform_matrix.copy() @ alignment_R

            # --- THE FIX: Extract in Degrees, and map to [Yaw_Z, Pitch_Y, Roll_X]! ---
            euler_xyz = Rotation.from_matrix(new_body.principal_axes).as_euler('xyz', degrees=True)
            new_body.pos_angles = np.array([euler_xyz[2], euler_xyz[1], euler_xyz[0]])
                        
        # Calculate Mass Properties
        new_body.base_color = "lightblue"
        try:
            density = parse_ui_float(self.ui.EditDensity.text())
        except:
            density = DEFAULT_DENSITY
        new_body.update_density(density)
        new_body.update_graphics_matrix(new_body.cog, new_body.principal_axes)

        self.physics_bodies[new_name] = new_body
        self.body_counter += 1

        # ==========================================
        # 5. Auto-generate CoG RF and Gravity
        # ==========================================
        rf_name = f"RF_CoG_{new_name}"
        cog_rf = RFrame(
            name=rf_name, position=new_body.cog.copy(), orientation=new_body.pos_angles.copy(),
            transform_matrix=new_body.principal_axes.copy(), plotter=self.plotter,
            parent_body=new_body, is_cog=True
        )
        self.rframes.append(cog_rf)
        QTreeWidgetItem(self.node_rframes, [rf_name])

        self._create_gravity_force_for_body(new_body)

        self.plotter.reset_camera()
        
        # Focus UI
        self.ui.treeHierarchy.blockSignals(True)
        self.ui.treeHierarchy.setCurrentItem(new_tree_item)
        self.ui.treeHierarchy.blockSignals(False)
        self.on_tree_selected()
        
        if hasattr(self, 'invalidate_results'):
            self.invalidate_results()
            
        print(f"Successfully generated primitive: '{new_name}'.")
    
    # ==========================================
    # --- KINEMATIC MOTIONS LOGIC ---
    # ==========================================
    def add_motion(self):
        """ Validates inputs, links to the joint, and compiles the motion math. """
        joint_name = self.ui.Edit_MotionJoint.text().strip()
        if not joint_name:
            QMessageBox.warning(self, "Error", "A target Joint is strictly required.")
            return

        joint = next((j for j in self.joints_list if j.name == joint_name), None)
        if not joint: 
            QMessageBox.warning(self, "Error", "Selected Joint does not exist.")
            return
            
        # --- THE FIX: Move the import to the very top of the logic! ---
        from unit_joints import JointType
        
        # 1. Read parameters
        trans_rot_idx = self.ui.cmbMotionTransRot.currentIndex()
        motion_type_idx = self.ui.cmbMotionType.currentIndex()
        math_expr = self.ui.Edit_MotionFunction.text().strip()
        
        # 2. Protection: 1 Motion per Joint (Exception: Cylindrical allows 1 Trans + 1 Rot)
        existing_motions = [m for m in self.motions_list if m.joint.name == joint.name]
        
        if existing_motions:
            if joint.joint_type == JointType.CYLINDRICAL:
                if len(existing_motions) >= 2:
                    QMessageBox.warning(self, "Protection", f"Cylindrical Joint '{joint.name}' already has both translational and rotational motions applied!")
                    return
                # Prevent two of the same type
                if existing_motions[0].trans_rot.value == trans_rot_idx:
                    m_type_str = "Translational" if trans_rot_idx == 0 else "Rotational"
                    QMessageBox.warning(self, "Protection", f"Cylindrical Joint '{joint.name}' already has a {m_type_str} motion applied!")
                    return
            else:
                QMessageBox.warning(self, "Protection", f"Joint '{joint.name}' already has a motion constraint applied!")
                return

        # 3. UI PROTECTIONS: translational motion is for prismatic joints, rotational for revolute
        if joint.joint_type == JointType.REVOLUTE and trans_rot_idx == 0:
            QMessageBox.warning(self, "Kinematic Error", "A Revolute Joint only supports Rotational Motion.")
            return
        if joint.joint_type == JointType.PRISMATIC and trans_rot_idx == 1:
            QMessageBox.warning(self, "Kinematic Error", "A Prismatic Joint only supports Translational Motion.")
            return
        if joint.joint_type in (JointType.FIXED, JointType.SPHERICAL, JointType.PLANAR):
            QMessageBox.warning(self, "Kinematic Error", "Fixed, Planar and Spherical Joints do not support 1-DOF Kinematic Motions.")
            return
        
        # 4. Generate Name & Create
        counter = len(self.motions_list) + 1
        prefix = "Rot" if trans_rot_idx == 1 else "Trans"
        m_name = f"{prefix}Motion_{counter}"
        while any(m.name == m_name for m in self.motions_list):
            counter += 1
            m_name = f"{prefix}Motion_{counter}"

        new_motion = JointMotion(m_name, joint, trans_rot_idx, motion_type_idx)
        new_motion.compile_expression(math_expr)
        
        # ==========================================
        # --- INITIAL CONDITION PROTECTIONS ---
        # ==========================================
        pos0, vel0, acc0 = new_motion.get_kinematics(0.0)
        
        if new_motion.motion_type.value == 0 and abs(pos0) > 1e-6: # Displacement Check
            reply = QMessageBox.warning(self, "Kinematic Warning",
                f"The specified Displacement function does not start at 0 (Initial Offset: {pos0:.3f}).\n\n"
                "This forces the solver to attempt an instant 'teleportation' at t=0, causing infinite acceleration and probable solver failure.\n\n"
                "Tip: Use the STEP() function to smoothly ramp up displacement.\n\n"
                "Do you want to proceed anyway?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No: return
            
        elif new_motion.motion_type.value == 1 and abs(vel0) > 1e-6: # Velocity Check
            reply = QMessageBox.warning(self, "Kinematic Warning",
                f"The specified Velocity function does not start at 0 (Initial Velocity: {vel0:.3f}).\n\n"
                "This acts as an instant hammer strike (infinite initial acceleration) on the joint at t=0, causing extreme reaction force spikes.\n\n"
                "Tip: Use the STEP() function to smoothly ramp up velocity.\n\n"
                "Do you want to proceed anyway?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No: return
        # ==========================================
        
        # 5. Save to engine
        self.motions_list.append(new_motion)
        QTreeWidgetItem(self.node_motions, [new_motion.name])
        self.node_motions.setExpanded(True)
        
        # 6. Update UI
        self.ui.Edit_MotionName.setText(new_motion.name)
        self.selected_motion = new_motion.name
        self.ui.btnAddMotion.setEnabled(False)
        
        self.invalidate_results()
        print(f"Created Kinematic Motion: '{new_motion.name}' on '{joint.name}'.")

    def update_motion(self):
        """ Recompiles the math expression and updates the combo boxes. """
        target_name = self.ui.Edit_MotionName.text().strip()
        motion = next((m for m in self.motions_list if m.name == target_name), None)
        if not motion: return
        
        trans_rot_idx = self.ui.cmbMotionTransRot.currentIndex()
        joint = motion.joint
        
        # --- THE FIX: Move the import to the very top of the logic! ---
        from unit_joints import JointType
        
        # --- UI PROTECTIONS: Translational motion is for prismatic joints, rotational for revolute ---
        if joint.joint_type == JointType.REVOLUTE and trans_rot_idx == 0:
            QMessageBox.warning(self, "Kinematic Error", "A Revolute Joint only supports Rotational Motion.")
            return
        if joint.joint_type == JointType.PRISMATIC and trans_rot_idx == 1:
            QMessageBox.warning(self, "Kinematic Error", "A Prismatic Joint only supports Translational Motion.")
            return
        if joint.joint_type in (JointType.FIXED, JointType.SPHERICAL, JointType.PLANAR):
            QMessageBox.warning(self, "Kinematic Error", "Fixed, Planar and Spherical Joints do not support 1-DOF Kinematic Motions.")
            return
            
        # --- Protect Cylindrical from having two of the same type! ---
        if joint.joint_type == JointType.CYLINDRICAL:
            other_motions = [m for m in self.motions_list if m.joint.name == joint.name and m.name != motion.name]
            if other_motions and other_motions[0].trans_rot.value == trans_rot_idx:
                m_type_str = "Translational" if trans_rot_idx == 0 else "Rotational"
                QMessageBox.warning(self, "Kinematic Error", f"Cannot apply. Joint '{joint.name}' already has another {m_type_str} motion applied!")
                return
        # -----------------------------------
        
        motion.trans_rot = MotionTransRot(trans_rot_idx)
        motion.motion_type = MotionType(self.ui.cmbMotionType.currentIndex())
        motion.compile_expression(self.ui.Edit_MotionFunction.text().strip())
        
        # ==========================================
        # --- INITIAL CONDITION PROTECTIONS ---
        # ==========================================
        pos0, vel0, acc0 = motion.get_kinematics(0.0)
        
        if motion.motion_type.value == 0 and abs(pos0) > 1e-6: 
            reply = QMessageBox.warning(self, "Kinematic Warning",
                f"The specified Displacement function does not start at 0 (Initial Offset: {pos0:.3f}).\n\n"
                "This forces the solver to attempt an instant 'teleportation' at t=0, causing infinite acceleration and probable solver failure.\n\n"
                "Tip: Use the STEP() function to smoothly ramp up displacement.\n\n"
                "Do you want to apply this update anyway?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No: return
            
        elif motion.motion_type.value == 1 and abs(vel0) > 1e-6: 
            reply = QMessageBox.warning(self, "Kinematic Warning",
                f"The specified Velocity function does not start at 0 (Initial Velocity: {vel0:.3f}).\n\n"
                "This acts as an instant hammer strike (infinite initial acceleration) on the joint at t=0, causing extreme reaction force spikes.\n\n"
                "Tip: Use the STEP() function to smoothly ramp up velocity.\n\n"
                "Do you want to apply this update anyway?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No: return
        # ==========================================
        
        self.invalidate_results()
        print(f"Updated Kinematic Motion '{motion.name}'.")

    def delete_motion(self):
        """ Permanently deletes the selected Motion driver. """
        target_name = self.ui.Edit_MotionName.text().strip()
        motion = next((m for m in getattr(self, 'motions_list', []) if m.name == target_name), None)
        if not motion: return
        
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Delete Kinematic Motion '{motion.name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No: return
        
        self.motions_list.remove(motion)
        
        for i in range(self.node_motions.childCount()):
            if self.node_motions.child(i).text(0) == motion.name:
                self.node_motions.takeChild(i)
                break
                
        self.ui.Edit_MotionName.setText("")
        self.ui.Edit_MotionJoint.setText("")
        self.ui.btnAddMotion.setEnabled(True)
        
        self.clear_selection()
        self.invalidate_results()
        print(f"Deleted Motion '{target_name}'.")

    def rename_motion(self):
        """ Safely renames the selected Motion. """
        target_name = self.ui.Edit_MotionName.text().strip()
        motion = next((m for m in self.motions_list if m.name == target_name), None)
        if not motion: return

        new_name, ok = QInputDialog.getText(self, "Rename Motion", "Enter new name:", text=motion.name)
        if not ok or not new_name.strip(): return 
        new_name = new_name.strip()
        if new_name == motion.name: return 

        if any(m.name == new_name for m in self.motions_list):
            QMessageBox.warning(self, "Rename Error", f"A Motion with the name '{new_name}' already exists!")
            return

        old_name = motion.name
        motion.name = new_name
        self.ui.Edit_MotionName.setText(new_name)
        self.selected_motion = new_name

        for i in range(self.node_motions.childCount()):
            if self.node_motions.child(i).text(0) == old_name:
                self.node_motions.child(i).setText(0, new_name)
                break
        self.invalidate_results()

    def toggle_motion_enabled(self, state):
        """ Turns the kinematic constraint on or off mathematically. """
        target_name = self.ui.Edit_MotionName.text().strip()
        motion = next((m for m in getattr(self, 'motions_list', []) if m.name == target_name), None)
        if motion:
            motion.enabled = state
            
            # Optionally wake up attached bodies
            if state:
                self._auto_enable_linked_bodies(motion.joint)
                
            self.refresh_tree_visuals()
            self.invalidate_results()    
        
if __name__ == "__main__":
    # Option 1
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 

    startup_dialog = create_startup_dialog()
    startup_dialog.show()
    startup_dialog.raise_()
    startup_dialog.activateWindow()
    app.processEvents()

    try:
        warm_up_numba_kernels()
    except Exception as exc:
        print(f"Warning: Startup Numba warm-up failed. First solve may still JIT compile: {exc}")
    
    # Option 2
    """import qdarktheme 
    app = QApplication(sys.argv)
    
    # Apply the dark theme globally BEFORE creating the Main Window! 
    qdarktheme.setup_theme(
        theme="dark",
        corner_shape="rounded", # sharp  rounded
        custom_colors={
            "[dark]": {
                "primary": "#DFDFDF",
            }
        },
    )"""
    
    # Option 3
    # Import the modern material library
    """from qt_material import apply_stylesheet 
    app = QApplication(sys.argv)
     # Apply a modern dark theme (Try 'dark_teal.xml', 'dark_blue.xml', or 'dark_amber.xml')
    apply_stylesheet(app, theme='dark_teal.xml', style = 'Fusion',  invert_secondary = False)"""
    
    
    #----------------------------------
    window = PhysicsEngineMain()
    window.show()
    
    # --- Reset the camera to ensure all objects are visible in the viewport (to make the Global RF in a proper size)
    window.plotter.reset_camera()
    window.plotter.render()
    app.processEvents()
    startup_dialog.close()
    # ------------
    
    sys.exit(app.exec())
    