# -*- coding: utf-8 -*-
# =============================================================================
#  SimPhant™ — Multibody Dynamics Simulation Software
#  Version: 2026.10.0
#  Module: unit_spline.py
#  Description:
#      Utilities for handling spline expressions and loading spline data from files.
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
import re

import numpy as np
import pyqtgraph as pg
from scipy.interpolate import Akima1DInterpolator

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


SPLINE_PATTERN = re.compile(r'^\s*spline\s*\((.*)\)\s*$', re.IGNORECASE)


class SplineDataError(ValueError):
    """Raised when spline data cannot be loaded or validated."""


def parse_spline_expression(text):
    """Returns the file path embedded in spline(...), or None if text is not a spline expression."""
    if text is None:
        return None

    match = SPLINE_PATTERN.match(str(text).strip())
    if not match:
        return None

    raw_path = match.group(1).strip()
    if len(raw_path) >= 2 and raw_path[0] == raw_path[-1] and raw_path[0] in ('"', "'"):
        raw_path = raw_path[1:-1].strip()

    return raw_path or None


def is_spline_expression(text):
    """Returns True when the text uses spline(...)."""
    return parse_spline_expression(text) is not None


def format_spline_expression(file_path):
    """Formats a file path as a spline(...) expression."""
    return f"spline({os.path.normpath(file_path)})"


def resolve_spline_path(file_path, base_dir=None):
    """Resolves absolute or relative spline file paths."""
    path_text = str(file_path).strip()
    if not path_text:
        raise SplineDataError("Spline file path is empty.")

    resolved = os.path.expandvars(os.path.expanduser(path_text))
    if not os.path.isabs(resolved):
        resolved = os.path.join(base_dir or os.getcwd(), resolved)

    resolved = os.path.normpath(resolved)
    if not os.path.exists(resolved):
        raise SplineDataError(f"Spline file not found:\n{resolved}")

    return resolved


def _split_data_line(line):
    if ';' in line:
        return [part.strip() for part in line.split(';')]
    if '\t' in line:
        return [part.strip() for part in line.split('\t')]

    whitespace_parts = line.split()
    if len(whitespace_parts) > 1:
        return whitespace_parts

    if ',' in line:
        return [part.strip() for part in line.split(',')]

    return whitespace_parts


def _parse_numeric_token(token):
    return float(str(token).strip().replace(',', '.'))


def load_spline_points(file_path):
    """Loads time/value data from a DAT or CSV file."""
    time_values = []

    with open(file_path, 'r', encoding='utf-8-sig') as data_file:
        for raw_line in data_file:
            line = raw_line.strip()
            if not line:
                continue

            parts = _split_data_line(line)
            if len(parts) < 2:
                continue

            try:
                time_value = _parse_numeric_token(parts[0])
                signal_value = _parse_numeric_token(parts[1])
            except ValueError:
                continue

            time_values.append((time_value, signal_value))

    if len(time_values) < 2:
        raise SplineDataError("Spline file must contain at least two valid time/value rows.")

    time_values.sort(key=lambda item: item[0])

    deduplicated = {}
    for time_value, signal_value in time_values:
        deduplicated[time_value] = signal_value

    times = np.array(sorted(deduplicated.keys()), dtype=float)
    values = np.array([deduplicated[time_value] for time_value in times], dtype=float)

    if len(times) < 2:
        raise SplineDataError("Spline file must contain at least two unique time points.")

    return times, values


class TimeSpline:
    """Callable time function backed by Akima interpolation with clamped end values."""

    def __init__(self, times, values):
        self.times = np.asarray(times, dtype=float)
        self.values = np.asarray(values, dtype=float)
        self.interpolator = None
        self.first_derivative = None
        self.second_derivative = None

        try:
            self.interpolator = Akima1DInterpolator(self.times, self.values)
            self.first_derivative = self.interpolator.derivative(1)
            self.second_derivative = self.interpolator.derivative(2)
        except Exception:
            self.interpolator = None
            self.first_derivative = None
            self.second_derivative = None

    def _evaluate_values(self, t_array):
        if self.interpolator is not None:
            y_array = np.asarray(self.interpolator(t_array), dtype=float)
        else:
            y_array = np.interp(t_array, self.times, self.values)

        y_array = np.where(t_array <= self.times[0], self.values[0], y_array)
        y_array = np.where(t_array >= self.times[-1], self.values[-1], y_array)
        return y_array

    def _evaluate_linear_derivatives(self, t_array):
        dy_array = np.zeros_like(t_array, dtype=float)
        ddy_array = np.zeros_like(t_array, dtype=float)

        if len(self.times) < 2:
            return dy_array, ddy_array

        segment_idx = np.searchsorted(self.times, t_array, side='right') - 1
        segment_idx = np.clip(segment_idx, 0, len(self.times) - 2)

        dt = self.times[segment_idx + 1] - self.times[segment_idx]
        dv = self.values[segment_idx + 1] - self.values[segment_idx]
        valid = dt > 0.0
        dy_array[valid] = dv[valid] / dt[valid]
        return dy_array, ddy_array

    def evaluate_kinematics(self, t):
        input_is_scalar = np.isscalar(t)
        t_array = np.atleast_1d(np.asarray(t, dtype=float))

        y_array = self._evaluate_values(t_array)
        dy_array = np.zeros_like(t_array, dtype=float)
        ddy_array = np.zeros_like(t_array, dtype=float)

        inside_mask = (t_array > self.times[0]) & (t_array < self.times[-1])
        if np.any(inside_mask):
            inside_t = t_array[inside_mask]
            if self.first_derivative is not None and self.second_derivative is not None:
                dy_array[inside_mask] = np.asarray(self.first_derivative(inside_t), dtype=float)
                ddy_array[inside_mask] = np.asarray(self.second_derivative(inside_t), dtype=float)
            else:
                dy_inside, ddy_inside = self._evaluate_linear_derivatives(inside_t)
                dy_array[inside_mask] = dy_inside
                ddy_array[inside_mask] = ddy_inside

        if input_is_scalar:
            return float(y_array[0]), float(dy_array[0]), float(ddy_array[0])
        return y_array, dy_array, ddy_array

    def __call__(self, t):
        input_is_scalar = np.isscalar(t)
        t_array = np.atleast_1d(np.asarray(t, dtype=float))

        y_array = self._evaluate_values(t_array)

        if input_is_scalar:
            return float(y_array[0])
        return y_array


def load_spline_file(file_path, base_dir=None):
    """Loads a spline file and returns the callable interpolation object and its data."""
    resolved_path = resolve_spline_path(file_path, base_dir=base_dir)
    times, values = load_spline_points(resolved_path)
    return TimeSpline(times, values), resolved_path, times, values


def load_spline_expression(expression_text, base_dir=None):
    """Loads a spline(...) expression and returns the callable interpolation object and its data."""
    file_path = parse_spline_expression(expression_text)
    if file_path is None:
        raise SplineDataError("Expression is not a spline(...) definition.")
    return load_spline_file(file_path, base_dir=base_dir)


class SplineEditorDialog(QDialog):
    """Simple preview dialog for selecting and validating spline data files."""

    def __init__(self, base_dir=None, initial_expression=None, title="Spline Preview", parent=None):
        super().__init__(parent)
        self.base_dir = base_dir or os.getcwd()
        self.selected_file_path = ""
        self.selected_expression = ""

        self.setWindowTitle(title)
        self.resize(820, 520)

        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Data file:", self))

        self.path_edit = QLineEdit(self)
        self.path_edit.setReadOnly(True)
        top_layout.addWidget(self.path_edit, stretch=1)

        self.btn_browse = QPushButton("Browse...", self)
        self.btn_browse.clicked.connect(self.browse_file)
        top_layout.addWidget(self.btn_browse)

        main_layout.addLayout(top_layout)

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True)

        self.plot_widget = pg.PlotWidget(self)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('bottom', "Time", units='s')
        self.plot_widget.setLabel('left', "Value")
        main_layout.addWidget(self.plot_widget, stretch=1)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        if initial_expression:
            initial_path = parse_spline_expression(initial_expression)
            if initial_path:
                self.load_and_plot(initial_path)

    def browse_file(self):
        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Spline Data File",
            self.base_dir,
            "Data files (*.csv *.dat);;CSV files (*.csv);;DAT files (*.dat);;All files (*)",
        )
        if selected_path:
            self.load_and_plot(selected_path)

    def load_and_plot(self, file_path):
        try:
            spline_func, resolved_path, times, values = load_spline_file(file_path, base_dir=self.base_dir)
        except SplineDataError as exc:
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
            QMessageBox.warning(self, "Spline Data", str(exc))
            return

        self.selected_file_path = resolved_path
        self.selected_expression = format_spline_expression(resolved_path)
        self.path_edit.setText(resolved_path)

        sample_times = np.linspace(times[0], times[-1], max(300, len(times) * 20))
        sample_values = spline_func(sample_times)

        self.plot_widget.clear()
        self.plot_widget.plot(sample_times, sample_values, pen=pg.mkPen('#304efa', width=2.5))
        self.plot_widget.plot(times, values, pen=None, symbol='o', symbolSize=7, symbolBrush='#ff3535')
        self.plot_widget.autoRange()

        self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)