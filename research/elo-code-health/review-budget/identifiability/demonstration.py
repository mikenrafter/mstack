#!/usr/bin/env python3
"""Synthetic rational-arithmetic demonstration; no fitted or empirical rates."""
from dataclasses import dataclass
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).parent


def probability(value: F, name: str) -> F:
    value = F(value)
    if not 0 <= value <= 1:
        raise ValueError(f'{name} must lie in [0,1]')
    return value


@dataclass(frozen=True)
class World:
    name: str
    prevalence: F
    sensitivity: F

    def __post_init__(self):
        probability(self.prevalence, 'prevalence')
        probability(self.sensitivity, 'sensitivity')

    @property
    def finding_probability(self):
        return self.prevalence * self.sensitivity


def count_likelihood(world: World, trials: int, findings: int) -> F:
    """Count probability for independent first screens, not evolving reviews."""
    if not isinstance(trials, int) or not isinstance(findings, int) or not 0 <= findings <= trials:
        raise ValueError('Require integers with 0<=findings<=trials')
    q = world.finding_probability
    return math.comb(trials, findings) * q ** findings * (1 - q) ** (trials - findings)


def residual_risk(world: World, repair: F, hazard: F, finding=None) -> F:
    """Conditional successful-repair hazard; no finding produces no edit.

    CLAIM(residual-mixture): marginal risk equals the probability-weighted
    finding/no-finding risks [test_demonstration.test_conditional_mixture].
    """
    repair, hazard = probability(repair, 'repair'), probability(hazard, 'hazard')
    q = world.finding_probability
    if finding is None:
        return world.prevalence - repair * (1 - hazard) * q
    if type(finding) is not bool:
        raise ValueError('finding must be Boolean or None for an unobserved result')
    if finding:
        if q == 0:
            raise ValueError('Cannot condition on an impossible finding')
        return 1 - repair * (1 - hazard)
    if q == 1:
        raise ValueError('Cannot condition on an impossible no-finding event')
    return world.prevalence * (1 - world.sensitivity) / (1 - q)


def utility(prevalence: F, sensitivity: F, repair: F, hazard: F,
            defect_loss: F, review_cost: F) -> dict:
    p = probability(prevalence, 'prevalence')
    s, r, h = (probability(sensitivity, 'sensitivity'), probability(repair, 'repair'),
               probability(hazard, 'hazard'))
    if defect_loss < 0 or review_cost < 0:
        raise ValueError('Costs must be nonnegative')
    q = p * s
    avoided_loss = defect_loss * r * q
    fix_hazard_cost = defect_loss * r * h * q
    net = avoided_loss - fix_hazard_cost - review_cost
    return {'finding_probability': q, 'avoided_defect_loss': avoided_loss,
            'fix_hazard_cost': fix_hazard_cost, 'review_cost': review_cost,
            'net_utility': net, 'decision': 'review' if net > 0 else 'stop' if net < 0 else 'indifferent'}


def elo_trace(outcomes, k0, decay=False):
    """Same finite input sequence gives the same deterministic risk-rating trace."""
    rating, trace = 1500.0, [1500.0]
    for prior_observations, outcome in enumerate(outcomes):
        if outcome not in (0, 1):
            raise ValueError('Binary observations required')
        q = 1 / (1 + 10 ** ((1500 - rating) / 400))
        k = k0 / (1 + prior_observations / 4) if decay else k0
        rating += k * (outcome - q)
        trace.append(rating)
    return trace


def serializable(value):
    if isinstance(value, F):
        return {'exact': str(value), 'decimal': float(value)}
    if isinstance(value, dict):
        return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(item) for item in value]
    return value


def main():
    worlds = (World('A', F(1, 5), F(1)), World('B', F(4, 5), F(1, 4)))
    repair, hazard, loss, cost = F(1), F(1, 10), F(100), F(5)
    states = (('immediate_initial_screen', 'initial'), ('after_first_result_unobserved', None),
              ('after_first_finding', True), ('after_first_no_finding', False))
    cases = []
    for state_name, finding in states:
        for world in worlds:
            prevalence = world.prevalence if finding == 'initial' else residual_risk(world, repair, hazard, finding)
            cases.append({'synthetic': True, 'information_state': state_name, 'world': world.name,
                          'defect_probability': prevalence, 'sensitivity': world.sensitivity,
                          **utility(prevalence, world.sensitivity, repair, hazard, loss, cost)})
    likelihoods = [{'synthetic': True, 'trials': n, 'findings': k,
                    'world_A': count_likelihood(worlds[0], n, k),
                    'world_B': count_likelihood(worlds[1], n, k)}
                   for n, k in ((0, 0), (1, 0), (1, 1), (4, 2), (20, 4))]
    sequence = [0, 1, 0, 0, 1]
    traces = {f'K{k}_fixed': elo_trace(sequence, k) for k in (8, 32, 64)}
    traces['K32_decay'] = elo_trace(sequence, 32, True)
    result = {'synthetic': True, 'not_empirical_estimates': True,
              'protocol_sha256': hashlib.sha256((HERE / 'PROTOCOL.md').read_bytes()).hexdigest(),
              'parameters': {'repair_success': repair, 'conditional_fix_hazard': hazard,
                             'defect_loss': loss, 'review_cost': cost},
              'worlds': [{'name': world.name, 'prevalence': world.prevalence,
                          'sensitivity': world.sensitivity, 'initial_finding_probability': world.finding_probability}
                         for world in worlds],
              'finite_count_likelihoods': likelihoods, 'decision_cases': cases,
              'initial_screen_sequence': sequence, 'rating_traces_identical_for_both_worlds': traces}
    result = serializable(result)
    (HERE / 'results.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'synthetic': True, 'decision_cases': result['decision_cases']}))


if __name__ == '__main__':
    main()
