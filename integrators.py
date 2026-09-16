# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.09.0
#  Module: integrators.py
#  Description:
#     Implements various numerical integration strategies for solving the equations of motion 
#     in multibody dynamics simulations.
#     Houses the numerical ODE integrators, including custom fixed-step solvers (RK4, Euler) 
#     and wrappers for SciPy's adaptive algorithms.  
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
from scipy.integrate import solve_ivp
import logging

class IntegratorStrategy:
    """ Base class for all numerical integrators """
    def solve(self, dynamics_func, t_span, Y0, t_eval, progress_callback=None):
        raise NotImplementedError("Integrators must implement the solve method.")

class CustomRK4(IntegratorStrategy):
    """ The original rock-solid manual RK4 integrator with Crash Armor. """
    def solve(self, dynamics_func, t_span, Y0, t_eval, progress_callback=None):
        num_steps = len(t_eval)
        num_states = len(Y0)
        Y_history = np.zeros((num_steps, num_states))
        
        Y_history[0] = Y0
        Y_current = np.copy(Y0)
        
        dt = t_eval[1] - t_eval[0]
        
        for i in range(1, num_steps):
            t = t_eval[i-1]
            
            try:
                # Standard RK4 Sub-steps
                k1 = dynamics_func(t, Y_current)
                k2 = dynamics_func(t + dt/2.0, Y_current + (dt/2.0) * k1)
                k3 = dynamics_func(t + dt/2.0, Y_current + (dt/2.0) * k2)
                k4 = dynamics_func(t + dt, Y_current + dt * k3)
                
                Y_new = Y_current + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
                
                # --- PROTECT AGAINST NUMERICAL EXPLOSIONS ---
                if np.any(np.isnan(Y_new)) or np.any(np.isinf(Y_new)):
                    raise ValueError("Numerical explosion (NaN/Infinity) generated.")
                    
                Y_current = Y_new
                Y_history[i] = Y_current
                
            except Exception as e:
                # --- THE FIX: Hard-Crash Armor and Data Rescue ---
                msg = (f"RK4 Crash at t={t:.5f}s!\n"
                       f"The physics are too stiff for this time step (dt={dt}s).\n"
                       f"Error: {e}")
                
                logging.error(msg)
                print(f"CRITICAL: {msg}")
                
                # Slices the array to keep exactly what we successfully calculated
                Y_history = Y_history[:i] 
                
                # Break cleanly and hand the rescued array to the post-processor!
                break 
            
            # Update UI progress bar
            if progress_callback and i % max(1, (num_steps // 100)) == 0:
                progress_callback(int((i / num_steps) * 100))
                
        # --- Statusbar: 100%
        if progress_callback:
            progress_callback(100)
                    
        return Y_history

class CustomEuler(IntegratorStrategy):
    """ Standard Explicit Euler. Fast, but accumulates energy/drift rapidly. """
    def solve(self, dynamics_func, t_span, Y0, t_eval, progress_callback=None):
        num_steps = len(t_eval)
        Y_history = np.zeros((num_steps, len(Y0)))
        
        Y_history[0] = Y0
        Y_current = np.copy(Y0)
        dt = t_eval[1] - t_eval[0]
        
        for i in range(1, num_steps):
            t = t_eval[i-1]
            
            # Simple Forward Step: Y_new = Y_old + dt * dY
            dY = dynamics_func(t, Y_current)
            Y_current = Y_current + dt * dY
            Y_history[i] = Y_current
            
            if progress_callback and i % max(1, (num_steps // 100)) == 0:
                progress_callback(int((i / num_steps) * 100))
                
        if progress_callback: progress_callback(100)
        return Y_history

class CustomSymplecticEuler(IntegratorStrategy):
    """ 
    Semi-Implicit Euler. Evaluates acceleration to step Velocity first, 
    then uses the NEW velocity to step Position. Excellent energy conservation.
    """
    def solve(self, dynamics_func, t_span, Y0, t_eval, progress_callback=None):
        num_steps = len(t_eval)
        num_states = len(Y0)
        half_idx = num_states // 2  # Split states into [Positions, Velocities]
        
        Y_history = np.zeros((num_steps, num_states))
        Y_history[0] = Y0
        Y_current = np.copy(Y0)
        dt = t_eval[1] - t_eval[0]
        
        for i in range(1, num_steps):
            t = t_eval[i-1]
            
            # 1. Evaluate current state to get Accelerations
            dY_old = dynamics_func(t, Y_current)
            accelerations = dY_old[half_idx:]
            
            # 2. Step Velocities FIRST (Symplectic magic happens here)
            new_velocities = Y_current[half_idx:] + dt * accelerations
            
            # 3. Create a temporary state with the NEW velocities to calculate correct Position kinematics
            Y_temp = np.copy(Y_current)
            Y_temp[half_idx:] = new_velocities
            dY_temp = dynamics_func(t, Y_temp)
            position_derivatives = dY_temp[:half_idx]
            
            # 4. Step Positions using the NEW velocity derivatives
            new_positions = Y_current[:half_idx] + dt * position_derivatives
            
            # 5. Pack the final state
            Y_current[:half_idx] = new_positions
            Y_current[half_idx:] = new_velocities
            
            Y_history[i] = Y_current
            
            if progress_callback and i % max(1, (num_steps // 100)) == 0:
                progress_callback(int((i / num_steps) * 100))
                
        if progress_callback: progress_callback(100)
        return Y_history

class SciPyIntegrator(IntegratorStrategy):
    """ 
    A universal wrapper for SciPy's advanced integrators.
    Methods supported: 'RK45', 'RK23', 'DOP853', 'Radau', 'BDF', 'LSODA'
    """
    # --- THE UPGRADE: Accept the advanced tolerances ---
    def __init__(self, method='RK45', rtol=1e-3, atol=1e-6, max_step=np.inf):
        self.method = method
        self.rtol = rtol
        self.atol = atol
        self.max_step = max_step

    def solve(self, dynamics_func, t_span, Y0, t_eval, progress_callback=None):
        import logging
        # Log the exact tolerances used for this run
        logging.info(f"Starting SciPy Integrator: {self.method} | rtol={self.rtol}, atol={self.atol}, max_step={self.max_step}")
        
        t_start, t_end = t_span
        total_time = t_end - t_start
        
        # We use a dictionary to store state inside the wrapper function
        # This tracks the highest percentage we have rendered so far.
        tracker = {'last_rendered_percent': 0}
        
        def tracked_dynamics(t, y):
            """ 
            This wrapper intercepts 't' before passing it to the heavy physics math.
            It throttles the UI updates so they ONLY fire every 2%.
            """
            if progress_callback:
                current_percent = int((t / total_time) * 100)
                
                # SciPy occasionally steps backwards if it rejects a stiff time-step.
                # We only update if we have crossed a new 2% threshold moving forward.
                if current_percent >= tracker['last_rendered_percent'] + 2:
                    progress_callback(current_percent)
                    tracker['last_rendered_percent'] = current_percent
                    
            # Call the actual heavy physics math!
            return dynamics_func(t, y)
        
        # Pass the 'tracked_dynamics' wrapper instead of the raw dynamics_func
        # This is for UI ProgressBar update every 2%, otherwise we can call fun=dynamics_func directly in 1 single step

        # --- THE UPGRADE: Inject the tolerances into the solver ---
        solution = solve_ivp(
            fun=tracked_dynamics,
            t_span=t_span,
            y0=Y0,
            method=self.method,
            t_eval=t_eval,
            vectorized=False,
            rtol=self.rtol,         # <--- Applied here!
            atol=self.atol,         # <--- Applied here!
            max_step=self.max_step  # <--- Applied here!
        )
        
        if not solution.success:
            logging.error(f"Integration failed: {solution.message}")
            print(f"Solver Error: {solution.message}")
            
        # Guarantee it hits 100% at the very end
        if progress_callback:
            progress_callback(100) 
            
        return solution.y.T