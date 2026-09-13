# SimPhant

SimPhant™ is an engineering-focused multibody dynamics (MBD) simulation environment for building, visualizing, and solving mechanical systems. It combines CAD-based geometry, rigid-body physics, constraints, forces, springs, contacts, gears, and motion definitions in a desktop application with an interactive 3D viewport.

## Features

- Interactive 3D visualization powered by PyVista and PyVistaQt
- Rigid-body creation from CAD meshes and procedural primitives
- Mass, center-of-gravity, inertia tensor, and principal-axis calculations
- Reference frames and body positioning tools
- Joints including fixed, spherical, revolute, cylindrical, prismatic, and planar joints
- Forces, torques, actuators, and electric motors
- Compression springs, torsion springs, and bushings
- Collision and contact handling with friction options
- Spur/helical, internal, and bevel gear constraints
- Kinematic motion functions for supported joints
- Multiple numerical solver and integration methods
- Simulation playback, telemetry, CSV export, and video export
- Project save/load support using `.mbd` files
- In-application logging and traceback output for desktop and packaged builds

## License

SimPhant™ is free and open-source software distributed under the GNU General Public License v3.0 (GPLv3). See the `LICENSE` file for the full license text.

## Project Status

SimPhant is under active development. APIs, user-interface details, simulation features, and project-file formats may change between releases.

The source code is publicly available so users and contributors can inspect, use, modify, and share the software under the terms of the project license.

## Choose Your Edition

SimPhant is intended to be available in two forms:

1. **Python source edition** for users who have Python installed and want to run or develop the project from source.
2. **Windows executable edition** for users who want to launch SimPhant directly without installing Python or managing Python packages.

Both editions provide the same application and simulation features. The executable edition is the recommended option for users who only want to run SimPhant.

## Python Source Edition

### Requirements

- Python 3.11 or newer: Runs the SimPhant source code and supports the current NumPy and SciPy dependency versions.
- PySide6: Provides the desktop user interface and Qt application framework.
- PyVista and PyVistaQt: Provide 3D mesh visualization and the Qt-integrated rendering viewport.
- NumPy: Provides array, vector, and matrix operations used throughout the simulation engine.
- SciPy: Provides scientific algorithms, rotations, numerical utilities, and integration support.
- Trimesh: Provides CAD mesh processing, geometry operations, and solid-mesh calculations.
- Numba: Accelerates selected mathematical and physics calculations using just-in-time compilation.

Additional dependencies may be required depending on the enabled solver, CAD, boolean, and video-export features.

### Installation

> TODO: Add complete Python installation instructions.
>
> This section will describe virtual-environment setup, dependency installation, optional packages, and platform-specific requirements.

### Running From Source

> TODO: Add Python launch instructions.
>
> This section will document the command used to start `main.py`, development configuration, and troubleshooting steps.

## Windows Executable Edition

The Windows executable edition is intended for users who do not want to install Python. It will be distributed as a packaged application containing the runtime and required dependencies.

### Requirements

- Windows 10 or newer
- A downloaded SimPhant release package
- No separate Python installation required

> TODO: Confirm the supported Windows versions and hardware requirements.

### Installation

> TODO: Add `.exe` installation instructions.
>
> This section will describe where to download the release, how to extract or install the package, whether an installer is provided, and how to handle Windows security prompts.

### Launching SimPhant

> TODO: Add executable launch instructions.
>
> This section will explain how to start SimPhant using the `.exe` file, where application logs are stored, and how to create a desktop or Start Menu shortcut.

### Executable Releases

> TODO: Add links to the GitHub Releases page and downloadable `.exe` packages.

## Usage

> TODO: Add user documentation.
>
> Planned topics include importing CAD models, creating primitives, defining reference frames and constraints, configuring solver settings, running simulations, reviewing telemetry, and exporting results for both editions.

## Project Files

Example model files are available in the `SaveFiles` directory. These files demonstrate mechanisms and individual features such as joints, springs, gears, contacts, bushings, and motion constraints.

## Development

The main application controller is located in `main.py`. Supporting modules contain the rigid-body model, mathematical kernels, solver, integrators, geometry generators, forces, joints, springs, contacts, gears, project management, and telemetry functionality.

The Qt Designer source is `main_window.ui`. The generated `ui_main_window.py` file should be regenerated from the `.ui` file when the interface changes.

## Documentation

> TODO: Add documentation links and design notes.
>
> This section will link to the user guide, technical documentation, solver notes, file-format documentation, and examples.

## Support

> TODO: Add support information.
>
> This section will provide the issue tracker, discussion channel, contact details, and bug-report guidelines.

## Contributing

> TODO: Add contribution guidelines.
>
> Contributions, bug reports, feature requests, and technical discussions will be documented here after the project workflow is established.

## Author

Valeriy Shapovalov

- GitHub: [valeriy-sh79](https://github.com/valeriy-sh79)
- LinkedIn: [Valeriy Shapovalov](https://www.linkedin.com/in/valeriy-shapovalov-9762a098/)
