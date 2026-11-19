#!/usr/bin/env python3
"""Synthetic exact-binomial reference calculations, not empirical power claims."""
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).parent
PREVALENCES = (.1, .3, .6)
SIZES = (40, 60, 120)
TRIGGERS = {'null': (.3, .3), 'moderate': (.65, .15), 'strong': (.8, .1)}


def check_probability(value, name):
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f'{name} must lie in [0,1]')


def population_capture(prevalence, sensitivity, false_positive, budget=.8):
    """Conditional positive capture under a population expected review budget."""
    for value, name in ((prevalence, 'prevalence'), (sensitivity, 'sensitivity'),
                        (false_positive, 'false_positive'), (budget, 'budget')):
        check_probability(value, name)
    trigger_share = prevalence * sensitivity + (1 - prevalence) * false_positive
    if trigger_share <= budget:
        negative_selection = (budget - trigger_share) / (1 - trigger_share) if trigger_share < 1 else 0
        recall = sensitivity + (1 - sensitivity) * negative_selection
    else:
        negative_selection = 0
        recall = budget * sensitivity / trigger_share
    return {'trigger_share': trigger_share, 'negative_trigger_selection_probability': negative_selection,
            'recall': recall, 'gain_vs_random': recall - budget}


@lru_cache(None)
def binomial_probability(trials, probability, successes):
    if not isinstance(trials, int) or trials < 0 or not isinstance(successes, int) or not 0 <= successes <= trials:
        raise ValueError('Require integers with0<=successes<=trials')
    check_probability(probability, 'binomial probability')
    return math.comb(trials, successes) * probability ** successes * (1 - probability) ** (trials - successes)


def binomial_tail(trials, probability, threshold):
    if not isinstance(threshold, int) or not 0 <= threshold <= trials + 1:
        raise ValueError('Threshold must lie between0andtrials+1')
    return sum(binomial_probability(trials, probability, successes) for successes in range(threshold, trials + 1))


@lru_cache(None)
def critical_capture(positives):
    """Independent-positive reference: positive lower95% bound plus>=10pp gain."""
    if positives < 10:
        return None
    minimum_gain_count = (9 * positives + 9) // 10
    for captured in range(minimum_gain_count, positives + 1):
        if binomial_tail(positives, .8, captured) <= .025:
            return captured
    return None


def reference_power(enrolled, prevalence, recall, coverage=1):
    """Exact under the simplified independent-positive-capture reference model.

    It is not the power of a finite-cohort fractional-allocation bootstrap.
    """
    observed_positive_probability = prevalence * coverage
    probability = 0.0
    for positives in range(10, enrolled + 1):
        critical = critical_capture(positives)
        if critical is None:
            continue
        probability += binomial_probability(enrolled, observed_positive_probability, positives) * binomial_tail(positives, recall, critical)
    return probability


def design_effect(enrolled, projects, correlation):
    if not isinstance(enrolled, int) or not isinstance(projects, int) or not 0 < projects <= enrolled:
        raise ValueError('Positive enrollment and project counts required')
    check_probability(correlation, 'within-project correlation')
    cluster_size = enrolled / projects
    effect = 1 + (cluster_size - 1) * correlation
    return {'mean_cluster_size': cluster_size, 'design_effect': effect,
            'variance_equivalent_sample': enrolled / effect}


def main():
    captures, samples, power, dependence = [], [], [], []
    for prevalence in PREVALENCES:
        for trigger, (sensitivity, false_positive) in TRIGGERS.items():
            capture = population_capture(prevalence, sensitivity, false_positive)
            captures.append({'synthetic': True, 'prevalence': prevalence, 'trigger': trigger,
                             'sensitivity': sensitivity, 'false_positive': false_positive, **capture})
            for enrolled in SIZES:
                power.append({'synthetic': True, 'enrolled': enrolled, 'prevalence': prevalence,
                              'trigger': trigger, 'coverage': 1, 'population_recall': capture['recall'],
                              'expected_positives': enrolled * prevalence,
                              'expected_captured_positives': enrolled * prevalence * capture['recall'],
                              'reference_power': reference_power(enrolled, prevalence, capture['recall'])})
                if trigger == 'strong':
                    power.append({'synthetic': True, 'enrolled': enrolled, 'prevalence': prevalence,
                                  'trigger': trigger, 'coverage': .9, 'population_recall': capture['recall'],
                                  'expected_positives': enrolled * prevalence * .9,
                                  'expected_captured_positives': enrolled * prevalence * .9 * capture['recall'],
                                  'reference_power': reference_power(enrolled, prevalence, capture['recall'], .9)})
        for enrolled in SIZES:
            for coverage in (1, .9):
                observed = prevalence * coverage
                samples.append({'synthetic': True, 'enrolled': enrolled, 'prevalence': prevalence,
                                'coverage': coverage, 'expected_complete_outcomes': enrolled * coverage,
                                'expected_observed_positives': enrolled * observed,
                                'probability_at_least10_observed_positives': binomial_tail(enrolled, observed, 10),
                                'probability_observed_negative': 1 - (1 - (1 - prevalence) * coverage) ** enrolled})
    for projects in (3, 6):
        for correlation in (0, .05, .1):
            dependence.append({'synthetic': True, 'enrolled': 60, 'projects': projects,
                               'within_project_correlation': correlation,
                               **design_effect(60, projects, correlation)})
    result = {'synthetic': True, 'not_empirical_estimates': True,
              'protocol_sha256': hashlib.sha256((HERE / 'PROTOCOL.md').read_bytes()).hexdigest(),
              'population_capture': captures, 'positive_count_coverage': samples,
              'simplified_reference_power': power, 'dependence_sensitivity': dependence,
              'reference_power_limit': 'Independent-positive Bernoulli capture model; not actual paired-bootstrap assay power or causal utility.'}
    (HERE / 'results.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
