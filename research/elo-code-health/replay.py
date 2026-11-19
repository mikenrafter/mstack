"""Read-only, standard-library replay. Definitions and limitations: PROTOCOL.md.

CLAIM(no-future): all training counters/ratings use commits[:cutoff].
Proof: test_future_labels_cannot_change_frozen_training_scores.
Errors from Git or malformed numstat abort the run; never reuse partial results.
"""
from __future__ import annotations

import csv
import argparse
import hashlib
import itertools
import json
import math
import posixpath
import random
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
PROJECTS = [('edge', 'upstream/main'), ('openstrap-analytics', 'upstream/main'),
            ('diff-core', 'upstream/main'), ('qex', 'HEAD'),
            ('residual-cli', 'feat/reviewer-notes'), ('paneweft', 'main')]


@dataclass(frozen=True)
class Commit:
    sha: str
    date: str
    title: str
    files: tuple[str, ...]


def git(repository, *arguments):
    return subprocess.check_output(['git', '-C', str(repository), *arguments],
                                   text=True, encoding='utf-8', errors='strict')


def eligible_source(path):
    parts = path.lower().split('/')
    return (parts[0] in {'lib', 'src', 'crates', 'packages'}
            and not any(p in {'test', 'tests', '__tests__', 'fixtures', 'generated',
                              'node_modules', 'vendor', 'target', 'dist'} for p in parts)
            and Path(path).suffix in {'.dart', '.rs', '.ts', '.tsx', '.js', '.jsx', '.py'}
            and not re.search(r'(?:_test\.dart|\.(?:g|freezed)\.dart|\.(?:test|spec)\.[jt]sx?|\.d\.ts)$', path)
            and not parts[-1].startswith('test_'))


def fix_label(title, definition='broad'):
    if definition == 'strict':
        return bool(re.search(r'^fix(?:\([^)]*\))?:|/fix/', title, re.I))
    return bool(re.search(r'\b(?:fix|fixes|fixed|bug|regression|race|deadlock|crash)\b', title, re.I))


def history(repository, sha):
    text = git(repository, '-c', 'core.quotePath=false', 'log', sha, '--first-parent',
               '--reverse', '--format=@@@%H%x09%cs%x09%s', '--numstat',
               '--no-renames', '--diff-merges=first-parent')
    commits = []
    for chunk in text.split('@@@')[1:]:
        lines = chunk.splitlines()
        identity, date, title = lines[0].split('\t', 2)
        files = set()
        for line in lines[1:]:
            if not line.strip():
                continue
            added, removed, path = line.split('\t', 2)
            if eligible_source(path):
                files.add(path)
        commits.append(Commit(identity, date, title, tuple(sorted(files))))
    return commits


def tree_files(repository, sha):
    return {p for p in git(repository, 'ls-tree', '-r', '--name-only', sha).splitlines()
            if eligible_source(p)}


def replay_scores(commits, cutoff, eligible, *, definition='broad', k=32,
                  order=None, permute_labels=False):
    # ↳ CLAIM(no-future). A prediction tree supplies eligibility, never future paths.
    training = commits[:cutoff]
    labels = [fix_label(c.title, definition) for c in training]
    if permute_labels:
        random.Random(1729).shuffle(labels)
    touches, fixes, recent_touches, recent_fixes = Counter(), Counter(), Counter(), Counter()
    ratings = defaultdict(lambda: 1500.0)
    rng = random.Random(order)
    for start in range(0, len(training), 25):
        block_touches, block_fixes = Counter(), Counter()
        for index in range(start, min(start + 25, len(training))):
            files = training[index].files
            block_touches.update(files)
            touches.update(files)
            if labels[index]:
                block_fixes.update(files)
                fixes.update(files)
            if index >= cutoff - 100:
                recent_touches.update(files)
                if labels[index]:
                    recent_fixes.update(files)
        pairs = list(itertools.combinations(sorted(block_touches), 2))
        if order is not None:
            rng.shuffle(pairs)
        for left, right in pairs:
            rate_left = (block_fixes[left] + 1) / (block_touches[left] + 2)
            rate_right = (block_fixes[right] + 1) / (block_touches[right] + 2)
            actual = 1 if rate_left > rate_right else 0 if rate_left < rate_right else 0.5
            expected = 1 / (1 + 10 ** ((ratings[right] - ratings[left]) / 400))
            change = k * (actual - expected)
            # CLAIM(elo-update): both sides share a zero-sum update [equal-rating fixture].
            ratings[left] += change
            ratings[right] -= change
    return {
        'fix_count': {f: fixes[f] for f in eligible},
        'recent_fix_count': {f: recent_fixes[f] for f in eligible},
        'recent_touch_count': {f: recent_touches[f] for f in eligible},
        'smoothed_fix_rate': {f: (fixes[f] + 1) / (touches[f] + 2) for f in eligible},
        'elo': {f: ratings[f] for f in eligible},
        'constant_control': {f: 0 for f in eligible},
    }


def selection(scores):
    """CLAIM(tie-budget): fractional tie weights sum to ceil(n/5) [tie fixtures]."""
    if not scores:
        return {}
    remaining = math.ceil(len(scores) * 0.2)
    groups = defaultdict(list)
    for path, score in scores.items():
        groups[score].append(path)
    selected = {}
    for score in sorted(groups, reverse=True):
        files = groups[score]
        weight = min(1.0, remaining / len(files))
        selected.update((f, weight) for f in files)
        remaining -= weight * len(files)
        if remaining <= 1e-10:
            break
    return selected


def metrics(scores, future, definition):
    selected = selection(scores)
    events = Counter(f for c in future if fix_label(c.title, definition) for f in c.files)
    eligible_events = {f: n for f, n in events.items() if f in scores}
    total = sum(eligible_events.values())
    captured = sum(n * selected.get(f, 0) for f, n in eligible_events.items())
    unique_captured = sum(selected.get(f, 0) for f in eligible_events)
    budget = sum(selected.values())
    return dict(event_recall=captured / total if total else None,
                unique_recall=unique_captured / len(eligible_events) if eligible_events else None,
                precision=unique_captured / budget if total and budget else None,
                captured_fix_touches=captured, eligible_fix_touches=total,
                cold_start_touches=sum(n for f, n in events.items() if f not in scores),
                selected_files=budget, eligible_files=len(scores),
                fix_commits=sum(fix_label(c.title, definition) for c in future))


def architecture(repository, commits, sha):
    present = tree_files(repository, sha)
    source_commits = [c for c in commits if c.files][-200:]
    usable = [c for c in source_commits if len(c.files) <= 20]
    touches, pairs, examples = Counter(), Counter(), defaultdict(list)
    for commit in usable:
        files = sorted(set(commit.files) & present)
        touches.update(files)
        for pair in itertools.combinations(files, 2):
            pairs[pair] += 1
            if len(examples[pair]) < 3:
                examples[pair].append(commit.sha)
    imports = set()
    if repository.name == 'edge':
        package = re.search(r'^name:\s*(\S+)', git(repository, 'show', f'{sha}:pubspec.yaml'), re.M)
        prefix = 'package:' + package.group(1) + '/' if package else ''
        for source in sorted(present):
            body = git(repository, 'show', f'{sha}:{source}')
            for target in re.findall(r"(?:import|export)\s+['\"]([^'\"]+)", body):
                if target.startswith('package:'):
                    # Only resolve the package declared by this revision.
                    resolved = 'lib/' + target[len(prefix):] if prefix and target.startswith(prefix) else ''
                elif ':' in target:
                    continue
                else:
                    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), target))
                if resolved in present:
                    imports.add((source, resolved))
    rows = []
    for pair, support in pairs.items():
        left, right = pair
        if support < 3 or posixpath.dirname(left) == posixpath.dirname(right):
            continue
        rows.append(dict(left=left, right=right, support=support,
                         left_touches=touches[left], right_touches=touches[right],
                         p_right_given_left=support / touches[left],
                         p_left_given_right=support / touches[right],
                         jaccard=support / (touches[left] + touches[right] - support),
                         direct_import=((left, right) in imports or (right, left) in imports)
                         if repository.name == 'edge' else None,
                         commits=examples[pair]))
    rows.sort(key=lambda r: (-r['support'], -r['jaccard'], r['left'], r['right']))
    return dict(source_commits=len(source_commits), usable_commits=len(usable),
                excluded_broad_commits=len(source_commits) - len(usable),
                resolved_import_edges=len(imports) if repository.name == 'edge' else None,
                pairs=rows[:30])


def write_json(name, contents):
    (HERE / name).write_text(json.dumps(contents, indent=2, sort_keys=True) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revisions', type=Path,
                        help='Read exact project SHAs/refs from a saved inventory.json.')
    arguments = parser.parse_args()
    pinned = {row['project']: row for row in json.loads(arguments.revisions.read_text())} if arguments.revisions else {}
    inventory, results, coupling, histories = [], [], {}, {}
    for project, ref in PROJECTS:
        repository = ROOT / project
        sha = git(repository, 'rev-parse', pinned[project]['sha'] if pinned else ref).strip()
        ref = pinned[project]['ref'] if pinned else ref
        commits = history(repository, sha)
        histories[project] = commits
        inventory.append(dict(project=project, ref=ref, sha=sha,
                              shallow=git(repository, 'rev-parse', '--is-shallow-repository').strip(),
                              first_parent_commits=len(commits),
                              source_touch_commits=sum(bool(c.files) for c in commits),
                              fix_title_commits=sum(fix_label(c.title) for c in commits),
                              fix_source_commits=sum(bool(c.files) and fix_label(c.title) for c in commits),
                              oldest=commits[0].date, newest=commits[-1].date,
                              source_files=len(tree_files(repository, sha))))
        print(json.dumps(inventory[-1]), flush=True)
        if project in {'residual-cli', 'paneweft'}:
            continue
        coupling[project] = architecture(repository, commits, sha)
        for tenth in range(5, 10):
            cutoff, end = len(commits) * tenth // 10, len(commits) * (tenth + 1) // 10
            present = tree_files(repository, commits[cutoff - 1].sha)
            future = commits[cutoff:end]
            for definition in ['broad', 'strict']:
                variants = replay_scores(commits, cutoff, present, definition=definition)
                if definition == 'broad':
                    for k in [16, 64]:
                        variants[f'elo_k{k}'] = replay_scores(commits, cutoff, present, k=k)['elo']
                    for seed in range(5):
                        variants[f'elo_order{seed}'] = replay_scores(commits, cutoff, present, order=seed)['elo']
                    variants['elo_permuted_labels'] = replay_scores(
                        commits, cutoff, present, permute_labels=True)['elo']
                for model, scores in variants.items():
                    measured = metrics(scores, future, definition)
                    results.append(dict(project=project, definition=definition, model=model,
                                        window=f'{tenth * 10}-{(tenth + 1) * 10}%',
                                        split='holdout' if tenth >= 8 else 'development',
                                        cutoff=cutoff, end=end,
                                        training_revision=commits[cutoff - 1].sha,
                                        cutoff_date=commits[cutoff - 1].date,
                                        end_date=commits[end - 1].date, **measured))
            print(f'{project} window {tenth * 10}% done', flush=True)
    write_json('inventory.json', inventory)
    write_json('results.json', results)
    write_json('architecture.json', coupling)
    write_json('history.json', {p: [asdict(c) for c in cs] for p, cs in histories.items()})
    write_json('run.json', dict(protocol_sha256=hashlib.sha256((HERE / 'PROTOCOL.md').read_bytes()).hexdigest(),
                               code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                               replay_order='first-parent topological', revisions=inventory))
    with (HERE / 'windows.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    print('Finished. Results are fix-involvement proxies, not confirmed defects.', flush=True)


if __name__ == '__main__':
    main()
