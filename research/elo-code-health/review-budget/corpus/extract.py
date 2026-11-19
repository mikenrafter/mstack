"""Read saved review ledgers conservatively; see README.md for label limits."""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = Path('/home/mini/Documents/repos')
ACCEPTED = {'fixed', 'resolved'}
DECLINED = {'declined', 'disagree', 'pre-existing'}
CONSEQUENTIAL = {'should', 'blocker'}
VERIFIED_SUPPLEMENTS = [
    ('phoe-nix.research/w49', 2, 'phoe-nix.research/w49.reply2.txt'),
    ('phoe-nix.research/w46-vigil', 2, 'phoe-nix.research/w46-vigil.reply2.txt'),
    ('phoe-nix.research/w46-vigil', 3, 'phoe-nix.research/w46-vigil.reply-t2.txt'),
    ('phoe-nix.research/w47-router', 2, 'phoe-nix.research/w47-router.reply2.txt'),
    ('phoe-nix.research/w47-router', 4, 'phoe-nix.research/w47-router.reply-t2b.txt'),
    ('paneweft.research/review', 6, 'paneweft.research/review.reply-t2b.txt'),
    ('edge.research/sol/db-split', 2, 'edge.research/sol/db-split-review-t2.md'),
    ('residual-cli.research/reviewer-notes', 3, 'residual-cli.research/reviewer-notes.reply-t2.txt'),
    ('phoe-nix.research/vigil-disk-full', 3, 'phoe-nix.research/vigil-disk-full.reply3.txt'),
    ('phoe-nix.research/vigil-disk-full', 4, 'phoe-nix.research/vigil-disk-full.reply-t2.txt'),
    ('phoe-nix.research/vigil-disk-full', 5, 'phoe-nix.research/vigil-disk-full.reply-t2b.txt'),
    ('paneweft.research/v1/review', 6, 'paneweft.research/v1/review-t2-r1.txt'),
    ('paneweft.research/v1/review', 7, 'paneweft.research/v1/review-t2-r2.txt'),
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_ledger(data, path, source_hash):
    """Returns retrospective observations; omitted findings remain unknown.

    CLAIM(discovery-once): each finding belongs only to its explicit discovery
    round, never every later review [test_discovery_once_and_lag].
    CLAIM(censor-unobserved): missing rounds are never synthesized as clean
    reviews [test_gaps_and_censoring].
    """
    rounds = data.get('rounds')
    if not isinstance(rounds, list):
        raise ValueError('No rounds list')
    if any(type(r.get('n')) is not int or r['n'] < 1 for r in rounds):
        raise ValueError('Every round must explicitly name a positive integer n')
    numbers = [r['n'] for r in rounds]
    if len(set(numbers)) != len(numbers) or numbers != sorted(numbers):
        raise ValueError('Round numbers duplicate or source order is not increasing')
    group = str(path.relative_to(ROOT)).removesuffix('.ledger.json')
    project = path.relative_to(ROOT).parts[0].removesuffix('.research')
    source = {'path': str(path), 'sha256': source_hash}
    explicit = isinstance(data.get('findings'), dict)
    raw_findings = data.get('findings', {})
    if not isinstance(raw_findings, dict):
        raise ValueError('Unsupported findings format')
    findings = []
    claims_seen = {}
    for key, raw in raw_findings.items():
        number = raw.get('round')
        if type(number) is not int or number not in numbers:
            raise ValueError(f'Finding {key} has no recorded discovery round')
        normalized_claim = re.sub(r'\s+', ' ', raw.get('claim', '')).strip().lower()
        possible_duplicate = claims_seen.get(normalized_claim) if normalized_claim else None
        if normalized_claim:
            claims_seen.setdefault(normalized_claim, key)
        severity = raw.get('severity')
        status = raw.get('status')
        consequential = severity in CONSEQUENTIAL
        finding = dict(group_id=group, finding_id=key, discovery_round=number,
                       source=source, source_pointer=f'/findings/{key}',
                       severity=severity, needed_for_bar=raw.get('needed'),
                       tier=raw.get('tier'), class_name=raw.get('class'),
                       class_canonical=raw.get('class_canonical'),
                       pre_existing=raw.get('pre_existing'), locations=raw.get('where'),
                       claim=raw.get('claim'), suggested_fix=raw.get('fix'),
                       final_status=status, final_evidence=raw.get('evidence'),
                       disposition=('recorded_fixed' if status in ACCEPTED else
                                    'recorded_declined_or_preexisting' if status in DECLINED else
                                    'recorded_open' if status == 'open' else 'unknown'),
                       final_status_timestamp=None, independent_validity='unknown',
                       reported_consequential=consequential,
                       exact_claim_duplicate_of=possible_duplicate,
                       semantic_duplicate_status='unknown',
                       accepted_consequential_proxy=bool(consequential and status in ACCEPTED
                                                         and possible_duplicate is None))
        findings.append(finding)
    observations = []
    for index, raw in enumerate(rounds):
        previous = rounds[:index]
        new = [f for f in findings if f['discovery_round'] == raw['n']]
        consequential = [f for f in new if f['reported_consequential']]
        accepted = [f for f in consequential if f['accepted_consequential_proxy']]
        unresolved = [f for f in consequential if f['final_status'] == 'open']
        prior_findings = [f for f in findings if f['discovery_round'] < raw['n']]
        next_round = rounds[index+1]['n'] if index+1 < len(rounds) else None
        observation = dict(group_id=group, project=project, source=source,
                           source_pointer=f'/rounds/{index}',
                           round=raw['n'], ordinal=index+1, tier=raw.get('tier'),
                           approach=raw.get('approach'), phase=raw.get('phase'),
                           reviewer=raw.get('reviewer'), reviewed_sha=raw.get('sha'),
                           score=raw.get('score'), concern_scores=raw.get('scores'),
                           verdict=raw.get('verdict'), review_timestamp=None,
                           timestamp_status='not_recorded',
                           next_recorded_round=next_round,
                           next_round_status=('observed' if next_round is not None else 'right_censored'),
                           findings_object_present=explicit,
                           coverage_status=('structured_summary_unverified_completeness' if explicit
                                            else 'missing_findings_object'),
                           new_finding_ids=[f['finding_id'] for f in new],
                           new_recorded_findings=len(new) if explicit else None,
                           new_severity_counts=dict(collections.Counter(f['severity'] for f in new)) if explicit else None,
                           new_reported_consequential=len(consequential) if explicit else None,
                           new_accepted_consequential_proxy=len(accepted) if explicit else None,
                           new_open_consequential=len(unresolved) if explicit else None,
                           new_needed_yes_consequential=sum(f['needed_for_bar']=='yes' for f in consequential) if explicit else None,
                           new_status_counts=dict(collections.Counter(f['final_status'] for f in new)) if explicit else None,
                           true_new_valid_consequential=None,
                           zero_count_meaning='no matching row in saved ledger; not evidence of clean code',
                           current_round_extra_fields={k:v for k,v in raw.items() if k not in
                                                       {'n','tier','approach','phase','reviewer','sha','score','scores','verdict'}},
                           features_before_round={
                               'completed_recorded_rounds': len(previous),
                               'previous_round': previous[-1]['n'] if previous else None,
                               'previous_score': previous[-1].get('score') if previous else None,
                               'previous_verdict': previous[-1].get('verdict') if previous else None,
                               'previous_tier': previous[-1].get('tier') if previous else None,
                               'previous_approach': previous[-1].get('approach') if previous else None,
                               'previous_reviewer': previous[-1].get('reviewer') if previous else None,
                               'previous_reviewed_sha': previous[-1].get('sha') if previous else None,
                               'prior_scores': [r.get('score') for r in previous],
                               'prior_verdicts': [r.get('verdict') for r in previous],
                           },
                           reconstructed_prior_finding_features={
                               'recorded_discoveries': len(prior_findings) if explicit else None,
                               'reported_consequential': sum(f['reported_consequential'] for f in prior_findings) if explicit else None,
                               'warning': 'Final ledger classifications may have been edited; not guaranteed available online.'},
                           policy_role='unknown_requires_historical_schedule',
                           final_dispositions_are_predictors=False)
        observations.append(observation)
    group_row = dict(group_id=group, project=project, source=source,
                     intent=data.get('intent'), base=data.get('base'),
                     repository_recorded=data.get('repo'),
                     group_independence='not_established; cluster by project',
                     recorded_rounds=len(rounds), findings_object_present=explicit,
                     recorded_findings=len(findings) if explicit else None,
                     ledger_final_state_metadata={k:data.get(k) for k in
                                                  ['bar','phase','shape','stage','categories','paths','checks','review_gate']},
                     metadata_temporality='final snapshot; not pre-review predictors',
                     review_timestamps_available=False)
    return group_row, observations, findings


def augment(rounds, findings):
    """Add verified report discoveries, separating repeated resolution statements."""
    events = []
    for group, number, relative in VERIFIED_SUPPLEMENTS:
        path = ROOT / relative
        raw = path.read_bytes()
        source = dict(path=str(path), sha256=digest(raw))
        observation = next(r for r in rounds if r['group_id'] == group and r['round'] == number)
        text = raw.decode()
        score_values = [float(value) for value in re.findall(r'^SCORE(?:\[[^\]]+\])?:\s*([\d.]+)/10', text, re.M)]
        verdict = re.search(r'^VERDICT:\s*(\w+)', text, re.M)
        if (not score_values or min(score_values) != observation['score'] or not verdict
                or verdict[1] != observation['verdict']):
            raise ValueError('Verified supplemental report no longer matches round score/verdict')
        observation['supplemental_sources'] = [source]
        observation['supplemental_mapping_basis'] = 'manual independent audit, matching tier/sequence/score/verdict and finding references'
        observation['coverage_status'] = 'full_structured_reply_manually_mapped'
        for line_number, line in enumerate(text.splitlines(), 1):
            header = re.match(r'^(\w\d+) \[(should|blocker|nit)\] \[needed for bar: (yes|no)\] \[class: ([^\]]+)\] (.*)', line)
            resolved = re.match(r'^(\w\d+) resolved(?:[:.]|\s*$)', line, re.I)
            if resolved:
                events.append(dict(group_id=group, finding_id=resolved[1], observed_in_round=number,
                                   status='resolved', source=source, source_line=line_number))
            if not header:
                continue
            key, severity, needed, class_name, claim = header.groups()
            if any(f['group_id']==group and f['finding_id']==key for f in findings):
                events.append(dict(group_id=group, finding_id=key, observed_in_round=number,
                                   status='repeated_tagged_finding', source=source, source_line=line_number))
                continue
            findings.append(dict(group_id=group, finding_id=key, discovery_round=number,
                                 source=source, source_line=line_number, source_pointer=None,
                                 severity=severity, needed_for_bar=needed, tier=observation['tier'],
                                 class_name=class_name, class_canonical=None, pre_existing=None,
                                 locations=None, claim=claim, suggested_fix=None,
                                 final_status='unknown', final_evidence=None,
                                 disposition='unknown', final_status_timestamp=None,
                                 independent_validity='unknown', reported_consequential=severity in CONSEQUENTIAL,
                                 exact_claim_duplicate_of=None, semantic_duplicate_status='unknown',
                                 accepted_consequential_proxy=False,
                                 source_kind='supplemental_discovery_omitted_from_ledger'))
    for event in events:
        if event['status'] != 'resolved':
            continue
        for finding in findings:
            if (finding['group_id']==event['group_id'] and finding['finding_id']==event['finding_id']
                    and finding['discovery_round'] < event['observed_in_round']):
                finding.setdefault('disposition_events', []).append(event)
                if finding.get('source_kind') == 'supplemental_discovery_omitted_from_ledger':
                    finding.update(final_status='resolved', disposition='recorded_fixed',
                                   final_evidence=event,
                                   accepted_consequential_proxy=finding['reported_consequential'])
    for observation in rounds:
        own = [f for f in findings if f['group_id']==observation['group_id']
               and f['discovery_round']==observation['round']]
        observation['ledger_snapshot_counts'] = {key:observation[key] for key in
                                                 ['new_recorded_findings','new_severity_counts',
                                                  'new_reported_consequential','new_accepted_consequential_proxy',
                                                  'new_open_consequential','new_needed_yes_consequential','new_status_counts']}
        complete_reply = bool(observation.get('supplemental_sources'))
        known_any = bool(own)
        observation['new_finding_ids'] = [f['finding_id'] for f in own]
        observation['recorded_consequential_lower_bound'] = sum(f['reported_consequential'] for f in own)
        observation['recorded_accepted_consequential_lower_bound'] = sum(f['accepted_consequential_proxy'] for f in own)
        observation['new_recorded_findings'] = len(own) if known_any or complete_reply else None
        observation['new_severity_counts'] = dict(collections.Counter(f['severity'] for f in own)) if known_any or complete_reply else None
        observation['new_reported_consequential'] = observation['recorded_consequential_lower_bound'] if known_any or complete_reply else None
        observation['new_accepted_consequential_proxy'] = observation['recorded_accepted_consequential_lower_bound'] if known_any or complete_reply else None
        observation['new_open_consequential'] = sum(f['reported_consequential'] and f['final_status']=='open' for f in own) if known_any or complete_reply else None
        observation['new_needed_yes_consequential'] = sum(f['reported_consequential'] and f['needed_for_bar']=='yes' for f in own) if known_any or complete_reply else None
        observation['new_status_counts'] = dict(collections.Counter(f['final_status'] for f in own)) if known_any or complete_reply else None
        observation['documented_consequential_discovery'] = True if observation['recorded_consequential_lower_bound'] else False if complete_reply else None
        observation['documented_accepted_consequential_discovery'] = True if observation['recorded_accepted_consequential_lower_bound'] else False if complete_reply and not observation['recorded_consequential_lower_bound'] else None
        observation['true_new_valid_consequential'] = None
        observation['coverage_is_exhaustive_of_real_defects'] = False
    return events


def discover():
    roots = sorted(ROOT.glob('*.research')) + [ROOT/'mstack'/'research']
    output = subprocess.check_output(['rg','--files','--hidden', *map(str, roots)], text=True)
    paths = []
    for line in output.splitlines():
        p = Path(line)
        if p.is_symlink() or p.suffix.lower() not in {'.md','.txt','.json','.jsonl'}:
            continue
        if any(part in {'node_modules','.git','target','dist','sources','releases','t3-nightly-deploy'} for part in p.parts):
            continue
        if HERE in p.parents:
            continue
        if re.search(r'review|round|reply|ledger', p.name, re.I):
            paths.append(p)
    return sorted(set(paths))


def main():
    manifest = json.loads((HERE/'source-manifest.json').read_text())
    for path, expected_hash in manifest['sha256'].items():
        if digest(Path(path).read_bytes()) != expected_hash:
            raise ValueError(f'Frozen input changed: {path}; preserve this corpus before a new census')
    frozen_ledgers = set(manifest['reviewed_ledger_paths'])
    inventory, groups, rounds, findings, errors = [], [], [], [], []
    for path in discover():
        size = path.stat().st_size
        is_ledger = path.name.endswith('.ledger.json')
        row = dict(path=str(path), bytes=size, kind='structured_ledger' if is_ledger else 'supplemental_candidate',
                   extraction_status='inventory_only', group_id=None,
                   round=None, timestamp=None,
                   timestamp_note='filenames and mtimes are not review timestamps')
        if size > 2_000_000:
            row.update(extraction_status='excluded_size_over_2MB', sha256=None)
            inventory.append(row)
            continue
        raw = path.read_bytes()
        row['sha256'] = digest(raw)
        if is_ledger:
            if str(path) not in frozen_ledgers:
                row['extraction_status'] = 'outside_frozen_reviewed_census_not_a_negative'
                inventory.append(row)
                continue
            try:
                data = json.loads(raw)
                group, observations, entries = parse_ledger(data, path, row['sha256'])
                if observations:
                    groups.append(group)
                    rounds.extend(observations)
                    findings.extend(entries)
                    row.update(extraction_status='parsed', group_id=group['group_id'])
                else:
                    row.update(extraction_status='no_recorded_reviews_not_a_negative', group_id=group['group_id'])
            except (ValueError, KeyError, TypeError) as exc:
                row['extraction_status'] = 'parse_error'
                errors.append(dict(path=str(path), error=str(exc)))
        inventory.append(row)
    events = augment(rounds, findings)
    summary = dict(structured_groups=len(groups), observed_rounds=len(rounds),
                   finding_entities=len(findings), source_candidates=len(inventory),
                   project_groups=dict(collections.Counter(g['project'] for g in groups)),
                   finding_severities=dict(collections.Counter(f['severity'] for f in findings)),
                   final_statuses=dict(collections.Counter(f['final_status'] for f in findings)),
                   supplemental_findings=sum(f.get('source_kind')=='supplemental_discovery_omitted_from_ledger' for f in findings),
                   supplemental_verified_rounds=len(VERIFIED_SUPPLEMENTS),
                   documented_reported_labels=dict(collections.Counter(str(r['documented_consequential_discovery']) for r in rounds)),
                   documented_accepted_labels=dict(collections.Counter(str(r['documented_accepted_consequential_discovery']) for r in rounds)),
                   rounds_missing_findings=sum(r['new_recorded_findings'] is None for r in rounds),
                   parser_errors=errors,
                   sampling='available local saved research artifacts; not all reviews',
                   censoring='absence of a later review is unknown yield, never a negative',
                   extractor_sha256=digest(Path(__file__).read_bytes()))
    for name, rows in [('sources',inventory),('groups',groups),('rounds',rounds),('findings',findings),('disposition-events',events)]:
        (HERE/f'{name}.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows))
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary))
    if errors:
        raise SystemExit('Parse errors require inspection')


if __name__ == '__main__':
    main()
