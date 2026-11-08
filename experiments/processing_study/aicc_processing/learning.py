"""Actual local neural-network training for runtime prediction, using NumPy.

Two ReLU hidden layers are trained with masked squared error and Adam. This is
a small learned cost model, not LLM fine-tuning, a native-opcode model, or proof
that an autonomous system invented a new algorithm.
"""
import json
from pathlib import Path
import numpy as np

PLANS = ('cached', 'partitioned', 'ordered')


class CostNetwork:
    def __init__(self, features=8, hidden=(32, 16), seed=7):
        rng = np.random.default_rng(seed)
        dims = (features, *hidden, len(PLANS))
        self.weights = [rng.normal(0, np.sqrt(2 / a), (a, b)) for a, b in zip(dims[:-1], dims[1:])]
        self.biases = [np.zeros(b) for b in dims[1:]]
        self.x_mean = np.zeros(features)
        self.x_scale = np.ones(features)
        self.y_mean = np.zeros(len(PLANS))
        self.y_scale = np.ones(len(PLANS))

    def forward(self, x):
        activations = [x]
        pre = []
        for i, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            z = activations[-1] @ weight + bias
            pre.append(z)
            activations.append(np.maximum(z, 0) if i < len(self.weights) - 1 else z)
        return activations[-1], activations, pre

    def loss_gradients(self, x, y, mask):
        prediction, activations, pre = self.forward(x)
        denominator = max(1.0, float(mask.sum()))
        error = (prediction - y) * mask
        loss = float((error ** 2).sum() / denominator)
        delta = 2 * error / denominator
        gw = [None] * len(self.weights)
        gb = [None] * len(self.biases)
        for i in range(len(self.weights) - 1, -1, -1):
            gw[i] = activations[i].T @ delta
            gb[i] = delta.sum(axis=0)
            if i:
                delta = (delta @ self.weights[i].T) * (pre[i - 1] > 0)
        return loss, gw, gb

    def predict_seconds(self, features):
        x = (np.asarray(features, dtype=float).reshape(-1, len(self.x_mean)) - self.x_mean) / self.x_scale
        y, _, _ = self.forward(x)
        return np.exp(np.clip(y * self.y_scale + self.y_mean, -30, 30))

    def choose(self, features, ordered):
        costs = self.predict_seconds(features)[0]
        eligible = range(len(PLANS)) if ordered else range(len(PLANS) - 1)
        return PLANS[min(eligible, key=lambda i: costs[i])]

    def save(self, path, metadata=None):
        value = {'architecture': [len(self.x_mean), *[len(b) for b in self.biases]],
                 'plans': list(PLANS), 'weights': [w.tolist() for w in self.weights],
                 'biases': [b.tolist() for b in self.biases],
                 'x_mean': self.x_mean.tolist(), 'x_scale': self.x_scale.tolist(),
                 'y_mean': self.y_mean.tolist(), 'y_scale': self.y_scale.tolist(),
                 'metadata': metadata or {}}
        Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')

    @classmethod
    def load(cls, path):
        value = json.loads(Path(path).read_text())
        if value['plans'] != list(PLANS):
            raise ValueError('Model plan vocabulary does not match')
        model = cls(value['architecture'][0], tuple(value['architecture'][1:-1]))
        model.weights = [np.asarray(w, dtype=float) for w in value['weights']]
        model.biases = [np.asarray(b, dtype=float) for b in value['biases']]
        for name in ('x_mean', 'x_scale', 'y_mean', 'y_scale'):
            setattr(model, name, np.asarray(value[name], dtype=float))
        return model


def arrays(rows):
    if not rows:
        raise ValueError('Timing dataset must not be empty')
    for row in rows:
        if len(row['features']) != 8 or not np.isfinite(row['features']).all():
            raise ValueError('Expected eight finite features')
        for plan in PLANS:
            value = row['times'].get(plan)
            if value is not None and (not np.isfinite(value) or value <= 0):
                raise ValueError('Measured execution times must be positive and finite')
        if any(row['times'].get(p) is None for p in PLANS[:-1]):
            raise ValueError('Every job must measure both unrestricted optimized plans')
        if row['job']['ordered'] and row['times'].get('ordered') is None:
            raise ValueError('Ordered jobs must measure the ordered plan')
    x = np.array([row['features'] for row in rows], dtype=float)
    mask = np.array([[row['times'].get(plan) is not None for plan in PLANS] for row in rows], dtype=float)
    y = np.array([[np.log(row['times'][plan]) if row['times'].get(plan) is not None else 0.0 for plan in PLANS] for row in rows])
    return x, y, mask


def fit(train_rows, validation_rows, epochs=900, learning_rate=0.006, seed=7):
    if not isinstance(epochs, int) or isinstance(epochs, bool) or epochs < 1:
        raise ValueError('epochs must be a positive integer')
    model = CostNetwork(seed=seed)
    x, y, mask = arrays(train_rows)
    vx, vy, vm = arrays(validation_rows)
    model.x_mean = x.mean(axis=0)
    model.x_scale = np.maximum(x.std(axis=0), 0.1)
    model.y_mean = (y * mask).sum(axis=0) / np.maximum(mask.sum(axis=0), 1)
    model.y_scale = np.maximum(np.sqrt((((y - model.y_mean) ** 2) * mask).sum(axis=0) / np.maximum(mask.sum(axis=0), 1)), 0.1)
    x = (x - model.x_mean) / model.x_scale
    vx = (vx - model.x_mean) / model.x_scale
    y = (y - model.y_mean) / model.y_scale
    vy = (vy - model.y_mean) / model.y_scale
    parameters = model.weights + model.biases
    first = [np.zeros_like(p) for p in parameters]
    second = [np.zeros_like(p) for p in parameters]
    best_loss = float('inf')
    best = None
    history = []
    for epoch in range(1, epochs + 1):
        loss, gw, gb = model.loss_gradients(x, y, mask)
        for i, (p, gradient) in enumerate(zip(parameters, gw + gb)):
            gradient = np.clip(gradient, -10, 10)
            first[i] = 0.9 * first[i] + 0.1 * gradient
            second[i] = 0.999 * second[i] + 0.001 * gradient ** 2
            p -= learning_rate * (first[i] / (1 - 0.9 ** epoch)) / (np.sqrt(second[i] / (1 - 0.999 ** epoch)) + 1e-8)
        validation_loss = model.loss_gradients(vx, vy, vm)[0]
        if validation_loss < best_loss:
            best_loss = validation_loss
            best = [p.copy() for p in parameters]
            best_epoch = epoch
        if epoch == 1 or epoch % 50 == 0:
            history.append({'epoch': epoch, 'training_loss': loss, 'validation_loss': validation_loss})
    for parameter, saved in zip(parameters, best):
        parameter[:] = saved
    return model, {'architecture': [8, 32, 16, 3], 'epochs_attempted': epochs,
                   'selected_epoch': best_epoch, 'validation_loss': best_loss, 'history': history,
                   'optimizer': 'Adam', 'loss': 'masked squared error on normalized log execution time'}


def fit_static(train_rows):
    arrays(train_rows)  # Validate measurements before selecting a policy.
    candidates = []
    for ordinary in PLANS[:-1]:
        for use_ordered in (False, True):
            policy = {'unordered_plan': ordinary, 'use_ordered_when_declared': use_ordered}
            total = sum(row['times'][static_choice(policy, row['job']['ordered'])] for row in train_rows)
            candidates.append({**policy, 'training_kernel_seconds': total})
    return {**min(candidates, key=lambda p: p['training_kernel_seconds']), 'candidate_policies': candidates}


def static_choice(policy, ordered):
    return 'ordered' if ordered and policy['use_ordered_when_declared'] else policy['unordered_plan']


def evaluate(model, policy, test_rows):
    records = []
    for row in test_rows:
        eligible = [plan for plan in PLANS if row['times'].get(plan) is not None]
        chosen = model.choose(row['features'], row['job']['ordered'])
        static = static_choice(policy, row['job']['ordered'])
        oracle = min(eligible, key=lambda plan: row['times'][plan])
        records.append({'job': row['job']['name'], 'learned': chosen, 'static': static, 'oracle': oracle,
                        'learned_seconds': row['times'][chosen], 'static_seconds': row['times'][static],
                        'oracle_seconds': row['times'][oracle]})
    return {'records': records, 'learned_kernel_seconds': sum(r['learned_seconds'] for r in records),
            'static_kernel_seconds': sum(r['static_seconds'] for r in records),
            'oracle_kernel_seconds': sum(r['oracle_seconds'] for r in records),
            'oracle_matches': sum(r['learned'] == r['oracle'] for r in records),
            'jobs': len(records), 'selection_overhead_included': False,
            'note': 'Kernel-only estimates from measured held-out jobs. Separate end-to-end workers include feature/inference/binding overhead.'}
