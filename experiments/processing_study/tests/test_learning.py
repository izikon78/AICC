"""Numerical and behavioral checks for the actual local neural cost model."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from aicc_processing.learning import CostNetwork, arrays, fit, fit_static, static_choice


class LearningTests(unittest.TestCase):
    def rows(self, count=28, seed=2):
        rng = np.random.default_rng(seed)
        rows = []
        for i in range(count):
            x = rng.normal(size=8)
            ordered = bool(i % 2)
            x[6] = float(ordered)
            rows.append({'features': x.tolist(), 'job': {'ordered': ordered, 'name': str(i)},
                         'times': {'cached': float(np.exp(0.3 * x[0] + 0.2)),
                                   'partitioned': float(np.exp(-0.5 * x[0] + 0.2 * x[1])),
                                   'ordered': float(np.exp(0.2 * x[0] - 1)) if ordered else None}})
        return rows

    def test_numeric_gradients_and_mask(self):
        rng = np.random.default_rng(31)
        net = CostNetwork(hidden=(5, 4))
        x = rng.normal(size=(6, 8)); y = rng.normal(size=(6, 3))
        mask = np.ones_like(y); mask[::2, 2] = 0
        _, gw, gb = net.loss_gradients(x, y, mask)
        for parameter, gradient in zip(net.weights + net.biases, gw + gb):
            for flat in range(min(6, parameter.size)):
                index = np.unravel_index(flat, parameter.shape)
                original = parameter[index]
                parameter[index] = original + 1e-6
                plus = net.loss_gradients(x, y, mask)[0]
                parameter[index] = original - 1e-6
                minus = net.loss_gradients(x, y, mask)[0]
                parameter[index] = original
                self.assertAlmostEqual((plus - minus) / 2e-6, gradient[index], delta=2e-6)

    def test_training_and_serialization(self):
        train, validation = self.rows(42), self.rows(14, 3)
        model, history = fit(train, validation, epochs=180)
        self.assertLess(history['history'][-1]['training_loss'], history['history'][0]['training_loss'])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'weights.json'
            model.save(path)
            loaded = CostNetwork.load(path)
            np.testing.assert_allclose(model.predict_seconds(train[0]['features']), loaded.predict_seconds(train[0]['features']))
        self.assertNotEqual(model.choose(train[0]['features'], False), 'ordered')

    def test_invalid_measurements_are_not_imputed(self):
        for value in (0, -1, float('nan'), float('inf')):
            rows = self.rows(); rows[0]['times']['cached'] = value
            with self.assertRaises(ValueError): arrays(rows)
        with self.assertRaises(ValueError): fit([], self.rows())
        with self.assertRaises(ValueError): fit(self.rows(), self.rows(), epochs=0)

    def test_static_is_best_of_four_policies(self):
        rows = self.rows()
        policy = fit_static(rows)
        actual = sum(r['times'][static_choice(policy, r['job']['ordered'])] for r in rows)
        alternatives = [sum(r['times']['ordered' if ordered and r['job']['ordered'] else plan] for r in rows)
                        for plan in ('cached', 'partitioned') for ordered in (False, True)]
        self.assertEqual(actual, min(alternatives))


if __name__ == '__main__': unittest.main()
