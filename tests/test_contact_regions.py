import contextlib
import io
import json
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pyvista as pv
import trimesh
from scipy.integrate import trapezoid
from scipy.spatial.transform import Rotation

from integrators import SciPyIntegrator
from unit_collision import ContactPair, RegionContactGeometry, ContactResolutionError
from unit_joints import JointType
from unit_rigidbody import RigidBody
from unit_solver import MBSolver


class ContactRegionTests(unittest.TestCase):
    def setUp(self):
        self.rotation = np.eye(3)
        self.zero = np.zeros(3)
        self.floor = RegionContactGeometry(trimesh.creation.box((100, 100, 30)), 'floor')
        self.ball_mesh = trimesh.creation.icosphere(subdivisions=3, radius=25)
        self.ball = RegionContactGeometry(self.ball_mesh, 'ball')
        self.ball_position = np.array([0.0, 0.0, 0.0395])

    def ball_contact(self, geometry=None):
        return (geometry or self.ball).contact_regions(
            self.floor, self.rotation, self.ball_position, self.rotation, self.zero)

    def test_ball_has_one_region(self):
        points, normals, depths = self.ball_contact()
        self.assertEqual(len(depths), 1)
        self.assertAlmostEqual(depths[0], 0.0005, delta=1e-12)
        np.testing.assert_allclose(points[:, :2], 0.0, atol=1e-11)
        np.testing.assert_allclose(normals, [[0, 0, 1]], atol=1e-9)

    def test_subdivision_does_not_multiply_stiffness(self):
        refined = RegionContactGeometry(self.ball_mesh.subdivide(), 'refined ball')
        for original, subdivided in zip(self.ball_contact(), self.ball_contact(refined)):
            np.testing.assert_allclose(original, subdivided, atol=1e-10)

    def test_swapped_bodies_reverse_normal_only(self):
        points, normals, depths = self.ball_contact()
        reverse = self.floor.contact_regions(
            self.ball, self.rotation, self.zero, self.rotation, self.ball_position)
        np.testing.assert_allclose(reverse[0], points, atol=1e-10)
        np.testing.assert_allclose(reverse[1], -normals, atol=1e-9)
        np.testing.assert_allclose(reverse[2], depths, atol=1e-10)

    def test_touching_and_separated_have_no_force(self):
        for height in (0.04, 0.05):
            with self.subTest(height=height):
                manifold = self.ball.contact_regions(
                    self.floor, self.rotation, np.array([0.0, 0.0, height]),
                    self.rotation, self.zero)
                self.assertEqual(manifold[0].shape, (0, 3))
                self.assertEqual(manifold[2].size, 0)

    def test_picometer_sphere_overlap_has_stable_centroid(self):
        for depth in (1.1123e-11, 1e-9, 1e-7):
            with self.subTest(depth=depth):
                other = RegionContactGeometry(self.ball_mesh.copy(), 'other ball')
                points, normals, depths = self.ball.contact_regions(
                    other, self.rotation, self.zero, self.rotation,
                    np.array([0.05 - depth, 0.0, 0.0]))
                self.assertEqual(len(depths), 1)
                np.testing.assert_allclose(depths, [depth], rtol=0.03, atol=1e-13)
                np.testing.assert_allclose(points[:, 0], [0.025 - depth / 2], atol=1e-12)
                np.testing.assert_allclose(normals, [[-1.0, 0.0, 0.0]], atol=0.03)

    def test_flat_contact_is_centered(self):
        block = RegionContactGeometry(trimesh.creation.box((20, 20, 20)), 'block')
        points, normals, depths = block.contact_regions(
            self.floor, self.rotation, np.array([0.0, 0.0, 0.0245]),
            self.rotation, self.zero)
        self.assertEqual(len(depths), 1)
        np.testing.assert_allclose(points[:, :2], 0.0, atol=1e-11)
        np.testing.assert_allclose(normals, [[0, 0, 1]], atol=1e-10)
        np.testing.assert_allclose(depths, [0.0005], atol=1e-11)

    def test_shallow_overlap_is_not_dropped(self):
        block = RegionContactGeometry(trimesh.creation.box((20, 20, 20)), 'block')
        for depth in (1e-8, 1e-11):
            with self.subTest(depth=depth):
                points, normals, depths = block.contact_regions(
                    self.floor, self.rotation, np.array([0.0, 0.0, 0.025 - depth]),
                    self.rotation, self.zero)
                np.testing.assert_allclose(depths, [depth], rtol=1e-5, atol=1e-13)

    def test_annular_contact_has_centered_resultant(self):
        ring = RegionContactGeometry(trimesh.creation.annulus(10, 20, height=10), 'ring')
        points, normals, depths = ring.contact_regions(
            self.floor, self.rotation, np.array([0.0, 0.0, 0.0195]), self.rotation, self.zero)
        self.assertEqual(len(depths), 1)
        np.testing.assert_allclose(points[:, :2], 0.0, atol=1e-10)
        np.testing.assert_allclose(normals, [[0, 0, 1]], atol=1e-9)
        np.testing.assert_allclose(depths, [0.0005], atol=1e-10)

    def test_level_torus_uses_surfaces_not_hole(self):
        mesh = trimesh.creation.torus(major_radius=9, minor_radius=3)
        torus = RegionContactGeometry(mesh, 'torus')
        for depth in (1e-6, 1e-4):
            with self.subTest(depth=depth):
                position = np.array([0.0, 0.0, 0.018 - depth])
                points, normals, depths = torus.contact_regions(
                    self.floor, self.rotation, position, self.rotation, self.zero)
                self.assertEqual(len(depths), 1)
                np.testing.assert_allclose(points[:, :2], 0.0, atol=1e-10)
                np.testing.assert_allclose(normals, [[0, 0, 1]], atol=1e-9)
                np.testing.assert_allclose(depths, [depth], rtol=1e-5)

    def test_sliver_triangles_have_finite_surface_intervals(self):
        block = RegionContactGeometry(trimesh.creation.box((20, 20, 20)), 'block')
        for angle in (1e-10, 1e-8, 1e-6):
            with self.subTest(angle=angle), np.errstate(divide='raise', invalid='raise'):
                rotation = Rotation.from_euler('y', angle).as_matrix()
                points, normals, depths = block.contact_regions(
                    self.floor, rotation, np.array([0.0, 0.0, 0.0245]), self.rotation, self.zero)
                self.assertEqual(len(depths), 1)
                self.assertTrue(np.isfinite(depths[0]))
                self.assertAlmostEqual(depths[0], 0.0005, delta=2e-8)

    def test_containment_is_an_explicit_geometry_error(self):
        block = RegionContactGeometry(trimesh.creation.box((10, 10, 10)), 'contained block')
        with self.assertRaises(ContactResolutionError):
            block.contact_regions(self.floor, self.rotation, self.zero, self.rotation, self.zero)

    def test_torus_refinement_and_body_swap_preserve_resultant(self):
        mesh = trimesh.creation.torus(major_radius=9, minor_radius=3)
        torus = RegionContactGeometry(mesh, 'torus')
        refined = RegionContactGeometry(mesh.subdivide(), 'refined torus')
        position = np.array([0.0, 0.0, 0.0179])
        reference = torus.contact_regions(self.floor, self.rotation, position, self.rotation, self.zero)
        result = refined.contact_regions(self.floor, self.rotation, position, self.rotation, self.zero)
        for expected, actual in zip(reference, result):
            np.testing.assert_allclose(actual, expected, atol=1e-10)
        reverse = self.floor.contact_regions(torus, self.rotation, self.zero, self.rotation, position)
        np.testing.assert_allclose(reverse[0], reference[0], atol=1e-10)
        np.testing.assert_allclose(reverse[1], -reference[1], atol=1e-10)
        np.testing.assert_allclose(reverse[2], reference[2], atol=1e-10)

    def test_disconnected_overlaps_stay_separate(self):
        left = trimesh.creation.box((10, 10, 20))
        left.apply_translation((-20, 0, 0))
        right = left.copy()
        right.apply_translation((40, 0, 0))
        pair = RegionContactGeometry(trimesh.util.concatenate([left, right]), 'two pads')
        points, normals, depths = pair.contact_regions(
            self.floor, self.rotation, np.array([0.0, 0.0, 0.0245]),
            self.rotation, self.zero)
        self.assertEqual(len(depths), 2)
        np.testing.assert_allclose(points[:, 0], [-0.02, 0.02], atol=1e-11)
        np.testing.assert_allclose(depths, [0.0005, 0.0005], atol=1e-11)

    def test_edge_crossing_without_inside_vertices(self):
        horizontal = RegionContactGeometry(trimesh.creation.box((100, 10, 10)), 'horizontal')
        vertical = RegionContactGeometry(trimesh.creation.box((10, 100, 10)), 'vertical')
        points, normals, depths = horizontal.contact_regions(
            vertical, self.rotation, np.array([0.0, 0.0, 0.0095]),
            self.rotation, self.zero)
        self.assertEqual(len(depths), 1)
        np.testing.assert_allclose(depths, [0.0005], atol=1e-11)

    def test_rigid_transform_preserves_contact(self):
        points, normals, depths = self.ball_contact()
        rotation = Rotation.from_euler('xyz', [0.4, -0.2, 0.8]).as_matrix()
        offset = np.array([2.0, -3.0, 4.0])
        transformed = self.ball.contact_regions(
            self.floor, rotation, rotation @ self.ball_position + offset, rotation, offset)
        np.testing.assert_allclose(transformed[0], points @ rotation.T + offset, atol=1e-10)
        np.testing.assert_allclose(transformed[1], normals @ rotation.T, atol=1e-9)
        np.testing.assert_allclose(transformed[2], depths, atol=1e-10)

    def test_open_mesh_is_rejected(self):
        mesh = trimesh.creation.box()
        mesh.update_faces(np.arange(len(mesh.faces) - 1))
        with self.assertRaisesRegex(ValueError, 'closed'):
            RegionContactGeometry(mesh, 'open mesh')

    def test_v_groove_has_two_balanced_contacts(self):
        slabs = []
        for angle in (-45, 45):
            slab = trimesh.creation.box((100, 100, 30))
            rotation = Rotation.from_euler('y', angle, degrees=True).as_matrix()
            transform = np.eye(4)
            transform[:3, :3] = rotation
            transform[:3, 3] = rotation @ np.array([0.0, 0.0, -15.0])
            slab.apply_transform(transform)
            slabs.append(slab)
        groove = RegionContactGeometry(trimesh.boolean.union(slabs, engine='manifold'), 'groove')
        points, normals, depths = self.ball.contact_regions(
            groove, self.rotation, np.array([0.0, 0.0, 0.0245 * np.sqrt(2)]),
            self.rotation, self.zero)
        self.assertEqual(len(depths), 2)
        self.assertTrue(np.all(normals[:, 2] > 0.6))
        np.testing.assert_allclose(depths[0], depths[1], atol=1e-9)
        np.testing.assert_allclose((normals * depths[:, None]).sum(axis=0)[:2], 0.0, atol=1e-8)

    def test_mesh_offset_from_body_origin(self):
        offset = np.array([100.0, -50.0, 20.0])
        shifted_mesh = self.ball_mesh.copy()
        shifted_mesh.apply_translation(offset)
        shifted = RegionContactGeometry(shifted_mesh, 'offset ball')
        manifold = shifted.contact_regions(
            self.floor, self.rotation, self.ball_position - offset * 0.001,
            self.rotation, self.zero)
        for expected, actual in zip(self.ball_contact(), manifold):
            np.testing.assert_allclose(actual, expected, atol=1e-10)


class SolverRegionTests(unittest.TestCase):
    @staticmethod
    def make_solver():
        bodies = {}
        for name, mesh in (
            ('floor', trimesh.creation.box((100, 100, 30))),
            ('ball', trimesh.creation.icosphere(subdivisions=3, radius=25)),
        ):
            faces = np.column_stack((np.full(len(mesh.faces), 3), mesh.faces)).ravel()
            visual = pv.PolyData(mesh.vertices, faces)
            body = RigidBody(name, mesh, visual, None, None, skip_mass_calculation=True)
            body.generate_local_aabb()
            bodies[name] = body
        bodies['floor'].mass = 2.355
        bodies['floor'].principal_inertia = np.array([0.002139125, 0.002139125, 0.003925])
        ground = RigidBody('Ground', None, None, None, None, is_ground=True)
        joint = SimpleNamespace(
            name='fixed floor', enabled=True, joint_type=JointType.FIXED,
            body_i=ground, body_j=bodies['floor'], local_pos_i=np.zeros(3), local_pos_j=np.zeros(3),
            local_axis_i=np.array([0.0, 0.0, 1.0]), local_axis_j=np.array([0.0, 0.0, 1.0]),
            local_a_i=np.array([0.0, 1.0, 0.0]), local_a_j=np.array([0.0, 1.0, 0.0]),
            local_b_i=np.array([-1.0, 0.0, 0.0]), local_b_j=np.array([-1.0, 0.0, 0.0]))
        ball = bodies['ball']
        ball.mass = 0.5093596158465704
        ball.principal_inertia = np.full(3, 0.0001266086504981501)
        ball.cog = np.array([0.0, 0.0, 0.0395])
        contact = ContactPair('ball-floor', ball, bodies['floor'], 2000.0, 1.0, 0.0)
        gravity = SimpleNamespace(enabled=True, parent_body=ball, is_gravity=True,
                                  base_vector=np.array([0.0, 0.0, -9.81]))
        solver = MBSolver(bodies, [gravity], joints_list=[joint], contact_pairs=[contact])
        solver.prepare_runtime_evaluation_state()
        return solver, contact

    def test_solver_applies_one_force_not_seven(self):
        solver, contact = self.make_solver()
        state = solver.pack_state()
        derivatives = solver.evaluate_derivatives(0.0, state)
        self.assertGreater(contact.current_F_total, 990.0)
        self.assertLess(contact.current_F_total, 1001.0)
        self.assertEqual(solver.solve_profile['contact_points_total'], 1)
        expected = contact.current_F_total / contact.body_i.mass - 9.81
        self.assertAlmostEqual(derivatives[solver.N_pos + 8], expected)
        np.testing.assert_allclose(derivatives[-3:], 0.0, atol=1e-8)

    def test_legacy_search_flags_do_not_duplicate_or_drop_regions(self):
        solver, contact = self.make_solver()
        state = solver.pack_state()
        reference = solver.evaluate_derivatives(0.0, state)
        contact.symmetric_contact_search = False
        contact.contact_candidate_reduction_enabled = False
        np.testing.assert_allclose(solver.evaluate_derivatives(0.0, state), reference)

    def test_damping_is_applied_once_per_region(self):
        solver, contact = self.make_solver()
        contact.damping = 100.0
        contact.body_i.velocity = np.array([0.0, 0.0, -1.0])
        solver.evaluate_derivatives(0.0, solver.pack_state())
        self.assertAlmostEqual(contact.current_F_damp, 100.0, places=7)
        self.assertAlmostEqual(contact.current_F_total, contact.current_F_spring + 100.0)

    def test_linear_damping_ramp_and_no_attraction(self):
        solver, contact = self.make_solver()
        contact.d_max_m = 0.001
        contact.damping = 100.0
        contact.body_i.velocity = np.array([0.0, 0.0, -1.0])
        depth = solver.evaluate_narrow_phase(contact)[0][2][0]
        solver.evaluate_derivatives(0.0, solver.pack_state())
        self.assertAlmostEqual(contact.current_F_damp, 100.0 * depth / 0.001)
        contact.damping = 1e6
        contact.body_i.velocity = np.array([0.0, 0.0, 1.0])
        solver.evaluate_derivatives(0.0, solver.pack_state())
        self.assertEqual(contact.current_F_total, 0.0)

    def test_friction_preserves_action_reaction_and_total_moment(self):
        solver, contact = self.make_solver()
        contact.friction_enabled = True
        contact.body_i.velocity = np.array([1.0, 0.0, 0.0])
        manifold, reverse = solver.evaluate_narrow_phase(contact)
        self.assertEqual(len(reverse[2]), 0)
        forces = np.zeros(solver.N_vel)
        solver._apply_contact_manifold(contact, contact.body_i, contact.body_j, *manifold, forces)
        loads = forces.reshape(-1, 6)
        np.testing.assert_allclose(loads[:, :3].sum(axis=0), 0.0, atol=1e-9)
        total_moment = np.zeros(3)
        for body, load in zip(solver.moving_bodies, loads):
            total_moment += body.principal_axes @ load[3:] + np.cross(body.cog, load[:3])
        np.testing.assert_allclose(total_moment, 0.0, atol=1e-9)
        self.assertGreater(contact.current_F_friction, 0.0)
        self.assertLessEqual(contact.current_F_friction, contact.mu * contact.current_F_total)

    def test_full_impact_peak_impulse_and_energy(self):
        solver, contact = self.make_solver()
        ball = contact.body_i
        ball.cog = np.array([0.0, 0.0, 0.14])
        with contextlib.redirect_stdout(io.StringIO()):
            solver.run_simulation(
                0.15, 1.0 / 20000, integrator=SciPyIntegrator(
                    method='RK45', rtol=1e-7, atol=1e-9, max_step=0.0001),
                post_process=False)
            history_before = solver.simulation_history.copy()
            solver.ensure_postprocessed()
        np.testing.assert_array_equal(solver.simulation_history, history_before)
        force = solver.contact_history[:, 0, 2]
        expected_peak = np.sqrt(2.0 * 9.81 * 0.1) * np.sqrt(contact.stiffness * ball.mass)
        self.assertAlmostEqual(force.max() / expected_peak, 1.0, delta=0.015)
        history = solver.simulation_history
        impulse = trapezoid(force, solver.time_history)
        momentum = ball.mass * (history[-1, 22] - history[0, 22] + 9.81 * 0.15)
        self.assertAlmostEqual(impulse / momentum, 1.0, delta=0.002)
        initial_energy = ball.mass * 9.81 * history[0, 9]
        final_energy = ball.mass * (9.81 * history[-1, 9] + 0.5 * history[-1, 22] ** 2)
        self.assertAlmostEqual(final_energy / initial_energy, 1.0, delta=0.001)
        self.assertLess(np.linalg.norm(history[:, 23:26], axis=1).max(), 1e-7)
        self.assertTrue(np.all(np.isfinite(force)))


class SavedModelTests(unittest.TestCase):
    @staticmethod
    def load_solver(filename):
        with zipfile.ZipFile(Path(__file__).resolve().parents[1] / 'Examples' / filename) as archive:
            model = json.loads(archive.read('model.json'))
            bodies = {'Ground': RigidBody('Ground', None, None, None, None, is_ground=True)}
            for data in model['bodies']:
                mesh = trimesh.load(io.BytesIO(archive.read(data['mesh_file'])), file_type='stl', force='mesh')
                faces = np.column_stack((np.full(len(mesh.faces), 3), mesh.faces)).ravel()
                body = RigidBody(data['name'], mesh, pv.PolyData(mesh.vertices, faces),
                                 None, None, skip_mass_calculation=True)
                for key in ('mass', 'principal_inertia', 'cog', 'principal_axes', 'enabled'):
                    value = data[key]
                    setattr(body, key, np.asarray(value) if isinstance(value, list) else value)
                body.velocity = np.asarray(data['initial_velocity'])
                body.angular_velocity = np.asarray(data['initial_angular_velocity'])
                body.generate_local_aabb()
                bodies[body.name] = body
        joints = []
        for data in model['joints']:
            values = dict(data)
            values['joint_type'] = JointType(values['joint_type'])
            for key in ('body_i', 'body_j'):
                values[key] = bodies[values[key]]
            for key in data:
                if key.startswith('local_'):
                    values[key] = np.asarray(values[key])
            joints.append(SimpleNamespace(**values))
        assert not any(model.get(key) for key in ('springs', 'bushings', 'gears', 'motions'))
        assert all(data.get('is_gravity') for data in model['forces'])
        forces = [SimpleNamespace(enabled=data['enabled'], is_gravity=True,
                                  parent_body=bodies[data['parent_body']],
                                  base_vector=np.asarray(data['base_vector'])) for data in model['forces']]
        contacts = []
        for data in model['contacts']:
            contact = ContactPair(
                data['name'], bodies[data['body_i']], bodies[data['body_j']],
                data['stiffness'] / 1000 ** data['exponent'], data['exponent'], data['damping'] / 1000,
                friction_enabled=data['friction_enabled'], mu=data['mu'],
                slip_tol_ui=data['slip_tolerance'] * 1000, mesh_mode=data['mesh_mode'],
                d_max_ui=data.get('d_max_m', 0.0001) * 1000)
            contact.enabled = data['enabled']
            contacts.append(contact)
        return MBSolver(bodies, forces, joints_list=joints, contact_pairs=contacts,
                        alpha=20, beta=20, epsilon=1e-7)

    def check_model(self, filename, duration):
        solver = self.load_solver(filename)
        integrator = SciPyIntegrator(method='RK45', rtol=1e-3, atol=1e-6)
        with contextlib.redirect_stdout(io.StringIO()):
            solver.run_simulation(duration, 0.002, integrator=integrator, post_process=False)
            history = solver.simulation_history.copy()
            solver.ensure_postprocessed()
        self.assertAlmostEqual(solver.time_history[-1], duration)
        np.testing.assert_array_equal(solver.simulation_history, history)
        self.assertTrue(np.all(np.isfinite(history)))
        self.assertTrue(np.all(np.isfinite(solver.contact_history)))
        self.assertTrue(np.all(solver.contact_history[:, :, 2] >= 0))
        self.assertGreater(solver.contact_history[:, :, 2].max(), 0.0)

    def test_saved_cradle_full_run_and_telemetry(self):
        self.check_model('Newtons_Cradle.mbd', 3.0)

    def test_saved_torus_full_run_and_telemetry(self):
        self.check_model('Torus_falling_on_floor.mbd', 0.5)


class IntegrationRecoveryTests(unittest.TestCase):
    def test_repeated_unresolved_trials_have_bounded_retries(self):
        class Model:
            contact_pairs = [True]

            def evaluate(self, time, state):
                if time > 0:
                    raise ContactResolutionError('persistent trial failure')
                return -state

        class RejectedStep:
            def __init__(self, function, time, state, end, **options):
                self.function, self.time, self.state = function, time, state
                self.h_abs = min(options['max_step'], 0.01)

            def step(self):
                self.function(self.time + self.h_abs, self.state)

        integrator = SciPyIntegrator()
        with patch('integrators.RK45', RejectedStep):
            with self.assertRaisesRegex(ContactResolutionError, '13 step reductions'):
                integrator.solve(Model().evaluate, (0., 1.), np.ones(1), np.linspace(0, 1, 11))
        self.assertEqual(integrator.contact_retries, 13)

    def test_rejected_trial_restarts_from_accepted_state(self):
        class Model:
            contact_pairs = [True]

            def __init__(self):
                self.rejected = False

            def evaluate(self, time, state):
                if time > 0.05 and not self.rejected:
                    self.rejected = True
                    raise ContactResolutionError('injected trial overlap')
                return -state

        for method in ('RK23', 'RK45', 'DOP853', 'Radau', 'BDF', 'LSODA'):
            with self.subTest(method=method):
                model = Model()
                times = np.linspace(0.0, 0.2, 21)
                integrator = SciPyIntegrator(method=method, rtol=1e-7, atol=1e-9)
                history = integrator.solve(model.evaluate, (0.0, 0.2), np.ones(1), times)
                self.assertEqual(integrator.contact_retries, 1)
                np.testing.assert_allclose(history[:, 0], np.exp(-times), rtol=2e-6)

    def test_unresolved_initial_contact_is_not_silently_ignored(self):
        class Model:
            contact_pairs = [True]

            def evaluate(self, time, state):
                raise ContactResolutionError('invalid initial overlap')

        with self.assertRaisesRegex(ContactResolutionError, 'initial overlap'):
            SciPyIntegrator().solve(Model().evaluate, (0.0, 1.0), np.ones(1), np.linspace(0, 1, 11))

    def test_unrelated_errors_are_not_retried(self):
        class Model:
            contact_pairs = [True]

            def evaluate(self, time, state):
                raise ValueError('invalid mesh')

        with self.assertRaisesRegex(ValueError, 'invalid mesh'):
            SciPyIntegrator().solve(Model().evaluate, (0.0, 1.0), np.ones(1), np.linspace(0, 1, 11))


if __name__ == '__main__':
    unittest.main()