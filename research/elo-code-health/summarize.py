"""Produce inspectable summaries and a Paneweft bundle from recorded observations."""
import copy
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from replay import HERE, ROOT, fix_label, write_json

inventory = json.loads((HERE / 'inventory.json').read_text())
results = json.loads((HERE / 'results.json').read_text())
architecture = json.loads((HERE / 'architecture.json').read_text())
histories = json.loads((HERE / 'history.json').read_text())
groups = defaultdict(list)
for row in results:
    groups[(row['project'], row['definition'], row['split'], row['model'])].append(row)
summary = []
for (project, definition, split, model), rows in groups.items():
    touches = sum(r['eligible_fix_touches'] for r in rows)
    captured = sum(r['captured_fix_touches'] for r in rows)
    summary.append(dict(project=project, definition=definition, split=split, model=model,
                        recall=captured / touches if touches else None,
                        eligible_fix_touches=touches,
                        cold_start_touches=sum(r['cold_start_touches'] for r in rows),
                        nonempty_windows=sum(r['eligible_fix_touches'] > 0 for r in rows)))
write_json('summary.json', summary)

edge = next(p for p in inventory if p['project'] == 'edge')
edge_history = histories['edge']
recent = edge_history[-100:]
touches = Counter(f for c in recent for f in c['files'])
fixes = Counter(f for c in recent if fix_label(c['title']) for f in c['files'])
current = set(subprocess.check_output(['git', '-C', str(ROOT / 'edge'), 'ls-tree',
                                      '-r', '--name-only', edge['sha']], text=True).splitlines())
hotspots = [dict(path=f, touches=count, fix_touches=fixes[f])
            for f, count in touches.most_common() if f in current][:20]
write_json('current-hotspots.json', dict(project='edge', revision=edge['sha'],
                                        window='last 100 first-parent commits',
                                        meaning='observed activity, not predicted defect probability',
                                        files=hotspots))

scenario = dict(id='retention-preserves-complete-night', status='proposed-not-executed',
                project='edge', revision=edge['sha'],
                evidence_commit='c11f5cbac942969a410764e86d1a13bdd39a8651',
                components=['lib/data/db.dart', 'lib/compute/derivation_engine.dart',
                            'lib/data/local_repository_impl.dart'],
                stressor='Retention removes the leading portion of an overnight derive window before a later rederive.',
                outcomes=['A previously complete night is not overwritten from incomplete retained input.',
                          'Deleted rows and the prune cursor commit atomically.',
                          'The prune cursor never decreases.',
                          'Every derive entry path observes the same completeness decision.'],
                candidate_change='Evaluate one typed retained-window decision shared by pruning and derive entry paths.',
                held_out_cases=['DST transition', 'forced sleep window crossing the prune boundary',
                                'failed prune transaction', 'older cursor supplied after a newer cursor',
                                'algorithm-version rederive after pruning'],
                measurements=['outcome pass/fail with independent fixtures',
                              'files requiring edits for a new retention rule',
                              'duplicated decisions across entry paths',
                              'behavior regressions in held-out cases'],
                limits=['No validated force mapping or architectural change has been applied.',
                        'A lower file count or dependency count alone is not a successful outcome.'])
write_json('residual-draft.json', dict(schemaVersion='code-health.residual-draft/1',
                                      status='draft-for-inspection', scenarios=[scenario]))
write_json('evidence.json', dict(schemaVersion='code-health.evidence/1',
                               revisions=inventory, observations=dict(summary=summary,
                               architecture=architecture, current_hotspots=hotspots),
                               hypotheses=[scenario],
                               uncertainty=['Commit titles are unadjudicated weak labels.',
                                            'Cochange is association, including mixed sweeps.',
                                            'Two holdout windows per repository; no significance claim.',
                                            'Historical refs may be stale; source trees were never modified.']))

# Use the installed project's documented wire format, then validate with its CLI.
now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
snapshot = 'edge-health-' + edge['sha'][:12]
reference = dict(repository='edge', id='code-health', kind='research/code-health')
fixture = json.loads((ROOT / 'paneweft/fixtures/components/all.bundle.json').read_text())
view = copy.deepcopy(fixture['views'][0])
view.update(id='health-activity', title='Recent source activity',
            question='Which files changed most in the last 100 mainline commits?',
            entity=reference, snapshotId=snapshot, viewDefinitionId='health-activity-v1')
view['scope'] = dict(repositories=['edge'], roots=[str(ROOT / 'edge')], excludes=['tests', 'generated'],
                     limits=['Last 100 first-parent commits at the pinned revision; top 20 current source files.'])
view['sources'] = [dict(id='activity-evidence', kind='file', repository='mstack',
                        path='research/elo-code-health/current-hotspots.json',
                        sha256=hashlib.sha256((HERE / 'current-hotspots.json').read_bytes()).hexdigest(),
                        capturedAt=now, method='Git first-parent numstat; title-derived weak labels.')]
view['generatedAt'] = now
# Freshness names the pinned historical tree. The actual checkout may differ.
view['freshness'] = dict(repositories=[dict(id='edge', root=str(ROOT / 'edge'),
                                          gitRev=edge['sha'], dirty=bool(subprocess.check_output(
                                              ['git', '-C', str(ROOT / 'edge'), 'status', '--porcelain'], text=True)),
                                          files={})])
view['links'] = []
view['completeness'] = dict(status='partial', gaps=[dict(id='scope',
                            question='What quality risks are absent from this view?',
                            reason='Only activity and weak fix labels; no confirmed defects or scenario outcomes.')])
view['data'] = dict(columns=[dict(key='path', title='Source file', format='text'),
                             dict(key='touches', title='Changes', format='number'),
                             dict(key='fixes', title='Fix-title touches', format='number')],
                    rows=[dict(id='file-' + str(i), label=row['path'], provenance='parsed',
                               evidence=['activity-evidence'],
                               cells=dict(path=row['path'], touches=row['touches'], fixes=row['fix_touches']))
                          for i, row in enumerate(hotspots)],
                    order=dict(key='touches', direction='desc'))
bundle = dict(schemaVersion='paneweft.bundle/1',
              entities=[dict(**reference, snapshotId=snapshot, label='Edge recent source activity',
                             dataRoles=['activity'], relations=[])],
              definitions=[dict(id='health-activity-v1', entityKind='research/code-health',
                                title='Recent source activity', priority=10, component='list',
                                requires=[], dataRole='activity')], views=[view])
write_json('paneweft.bundle.json', bundle)

primary = [r for r in summary if r['definition'] == 'broad' and r['split'] == 'holdout'
           and r['model'] in ['elo', 'fix_count', 'recent_touch_count', 'constant_control']]
lookup = {(r['project'], r['model']): r for r in primary}
table = []
for project in ['edge', 'openstrap-analytics', 'qex', 'diff-core']:
    row = [project] + [f"{100 * lookup[project, m]['recall']:.1f}%" for m in
                       ['elo', 'fix_count', 'recent_touch_count', 'constant_control']]
    row += [str(lookup[project, 'elo']['eligible_fix_touches'])]
    table.append('| ' + ' | '.join(row) + ' |')

report = '''# Historical code health experiment results

## Top findings

- [C] Edge is the best primary subject among the inspected local histories: 637 mainline integrations, 216 fix-title source-touch integrations, and 384 current eligible source files.
- [C] The preregistered Elo aggregation did not outperform recent change frequency on the two held-out windows in any of the four subjects. This rejects using this variant as the default historical hotspot ranking.
- [C] Edge's Elo ranking captured 35.2% of eligible future fix-related file touches at an approximately 20% file budget; recent change frequency captured 56.0% and historical fix count 53.0%.
- [C] The strongest current change pair is derivation engine/database, with 21 cochanges. Patch inspection shows both mixed sweeps and a concrete shared retention invariant. Counts alone cannot justify a boundary change.
- [C] Label quality and limited independent holdouts restrict every predictive claim. These are observed fix-commit involvement proxies, not confirmed defects, calibrated risks, or evidence of successful architectural repair.
- [C, subsequent audit] The all-pairs construction reuses block observations unevenly. At Edge's 80% boundary, one 251-file block creates 31,375 of 93,374 comparisons. This confounds the interpretation of fixed-K results. See `WEIGHTING-PROTOCOL.md` and `WEIGHTING-RESULTS.md` for the separate exploratory diagnostic.

## Project selection

Use Edge for primary longitudinal evaluation. Use Analytics for algorithmic scenarios and Qex for lifecycle/transaction scenarios. Diff-core is a useful portability and confounding check; its history contains many evaluation-only commits and an old source-directory rename. Residual and Paneweft are integration targets, with only six and one fix-title source integrations respectively in the selected histories. That is insufficient for this ranking study.

All refs are cached local refs, pinned in `inventory.json`. The Edge checkout itself was on an older feature branch, so the analysis reads `upstream/main` objects without checking it out. Qex intentionally uses the owner working branch. Edge's pinned head carries a 2026-11-17 date, later than the protocol's UTC date; ordering uses the first-parent chain and makes no wall-clock as-of claim. Commit windows have unequal elapsed durations. No network fetch, source checkout, build, paid model call, or remote write was performed.

## Held-out comparison

Each model chooses ceil(20% of eligible source files), with fractional allocation for tied scores. Percentages below pool the final two chronological windows by fix-related file touches. A file touched in two fix commits contributes twice. The denominators exclude new files that did not exist at the prediction revision; cold-start exclusions were Edge 8, Analytics 0, Qex 1, Diff-core 20. The source filter includes inline Rust test code when it shares a production file, and can include fixture-like source files outside explicitly excluded directories.

| Project | Elo | Historical fix count | Recent change frequency | Random expectation | Eligible fix touches |
|---|---:|---:|---:|---:|---:|
''' + '\n'.join(table) + '''

Equal file count does not imply equal review effort. Large files and routine version stamps can make both activity and defect-count baselines look useful. Neither has been validated for actual inspection time saved. `windows.csv` contains all windows, precision, unique-file recall, positive counts, and cold-start counts; `summary.json` contains all model/label aggregates. Display rounded values are not additional precision.

## Elo definition and sensitivity

After the initial results, the owner questioned K's assumptions. An independent subagent audit found substantial block-size weighting: a file participates in n−1 updates in an n-file block. The largest Edge block supplies 33.6% of comparisons at the 80% prediction boundary; these are dependent transformations of the same observations. Match count is update exposure, not a measure of realized net influence. The initial K=16/32/64 sweep does not isolate this confound. Subsequent simultaneous and normalized-update comparisons are explicitly exploratory on already-inspected windows; the original protocol and results remain unchanged.

This is one specific exploratory Elo construction. In each 25-commit training block, files compete according to their Laplace-smoothed fix/touch rates. Higher observed rate wins. K=32 is fixed; ratings start at 1500. Ratings measure relative involvement under noisy labels. There is no executable challenge difficulty or demonstrated correctness outcome in these matches.

On Edge, K=16 and K=64 capture 37.1% and 36.0%; five shuffled within-block match orders capture 35.2–35.6%. These do not reach the change-frequency baseline. Analytics is less stable: the seeded orders capture 29.8–34.0% versus 25.5% for canonical order. Its permuted-training-label control captures 31.9%, above canonical Elo. A single control is diagnostic and supplies no p-value.

Strict title labels produce Elo recalls of 36.3% for Edge, 17.0% for Analytics, 6.8% for Qex, and 11.3% for Diff-core. The labels alter training histories even when the holdout positive events happen to coincide. Constant-rating controls match the random budget expectation in every window. One Diff-core development window has a single positive touch and two have none; those missing recalls remain null.

The rate-based construction can favor sparsely touched files because smoothing adds a prior rate of one half. It also answers a rate question while the primary metric rewards event volume. This is a reason to distrust this construction's fit to the task, not evidence that every possible Elo model fails. No hyperparameter was selected from the holdout, and no improved variant was fitted after these results.

## Architectural investigation

The last 200 source-touch integrations in Edge contain 12 changes touching more than 20 source files; these are excluded from pair analysis. The remaining 188 produce these candidate relations:

| Pair | Cochanges | Interpretation |
|---|---:|---|
| Derivation engine / database | 21 | Shared retained-data decisions, but inspected mixed sweeps also inflate the count |
| Database / app state | 16 | Storage and orchestration boundary; needs invariant-level inspection |
| Derivation engine / read repository | 15 | Derived output and serving contracts; direct import exists |
| App state / background sync | 9 | Foreground/headless coordination; 9 of 10 background-sync touches also change app state |

`architecture.json` provides support, directional conditional frequencies, example commit SHAs and direct-import checks. The import scan resolves literal Dart relative imports and imports for the declared package at the pinned current revision; it does not prove reachability or absence of indirect dependencies. Current imports never enter the historical ranking evaluation. Conditioning pair membership on files surviving to the current tree introduces survivorship bias into this descriptive scan.

Inspecting the first three examples for the highest-support pair found one concrete retention coupling and two mixed sweeps. See `label-audit.md`. The useful next question is whether retained-window completeness can have one decision interface used by every derive entry path, with atomic pruning metadata, while preserving all existing outcomes. This might reduce duplicated decisions; it might also add an unnecessary abstraction. A behavioral comparison must decide.

## Residual and Paneweft

`evidence.json` separates observations from hypotheses and keeps exact revisions. `residual-draft.json` records one proposed retention stressor, outcomes, component candidates, and held-out cases. It is an analysis interchange file, not a Residual CLI import format. No established force or coupling matrix has been modified.

`paneweft.bundle.json` uses Paneweft's existing list view format to show current activity with parsed provenance and a partial-completeness warning. It deliberately labels activity rather than quality. The real CLI validated the bundle, stored it, and read back all 20 rows in an isolated runtime with the declared production dependencies. An independent JSON Schema validator also accepted it. The session has no registered Edge root, so Paneweft correctly reports freshness as unverified. The pinned historical tree is explicit; the live checkout is different. Results and the session path are recorded in `integration-checks.json`. No viewer server was started.

## Schedule status and follow-up

E0–E5 completed for this bounded observational pass, including the real Paneweft CLI round trip and inline comparison. The proposed behavioral retention comparison and prospective review study have not run. No unattended calendar task or weekly collector was installed. The HTML screenshot preflight was unavailable because this host lacks the browser libraries; the inline HTML renderer accepted and displayed the artifact, and no host browser setup was changed.

The next experiment should be a within-repository behavioral comparison on Edge's retention boundary. Hold correctness outcomes fixed. Compare the current decision paths against one candidate interface, then vary a retention requirement and measure edits and regressions. Only after that experiment should ratings be attached to actual stressor outcomes. A four-week prospective check starts when a collector is installed, not at this report's timestamp.

## Reproduce

From the mstack root, run the following through the local queue:

```sh
qex submit --wait --cpu 1 --mem 128MB -- python3 -m unittest discover -s research/elo-code-health -p 'test_*.py'
qex submit --wait --cpu 1 --mem 384MB -- python3 research/elo-code-health/replay.py --revisions research/elo-code-health/inventory.json
qex submit --wait --cpu 1 --mem 128MB -- python3 research/elo-code-health/check_mutations.py
qex submit --wait --cpu 1 --mem 128MB -- python3 research/elo-code-health/summarize.py
qex submit --wait --cpu 1 --mem 320MB -- python3 research/elo-code-health/check_integration.py
```

With `--revisions`, the script uses the recorded SHAs; without it, it resolves available refs anew. `run.json` binds the protocol and replay script hashes. Nine focused tests cover selection arithmetic, cold starts, missing positives, Elo direction, future exclusion, filtering and a real temporary Git merge. Three deliberate defects must fail those tests: future leakage, reversed rating update, and selecting all tied files. No product test suite was run.

## Where your setup differs

`technical-excellence` asks for explicit invariants and `test-quality` asks for assertions that catch actual defects. The evaluator applies those checks, but the product labels still lack independent adjudication. Paneweft already accepts evidence provenance and completeness, which makes it suitable for showing this distinction. Residual already has outcomes and component relations, so the next step can use checkable stressors rather than inventing a repository-wide quality number.

## Candidate actions

1. Use recent change frequency plus visible fix evidence for the initial investigation queue. It beat this Elo variant on every subject's holdout and is cheaper to explain.
2. Run the retention behavioral comparison on Edge before building automatic rerouting. It has one inspected shared invariant and concrete held-out failure cases.
3. Adjudicate labels and measure inspection time before claiming defect-detection improvement. The current proxy cannot support that claim.
4. Revisit Elo or an ability/difficulty model only with repeated executable stressor outcomes. It would then have a defensible match definition.

## Sources

Local evidence is reproducible from the pinned revisions in `inventory.json`, the saved first-parent histories, the patch audit, and the frozen `PROTOCOL.md`. External background and dated source links are listed in that protocol. Grades C here indicate this bounded, reproducible local experiment; none of the results establish general software-quality effects.
'''
(HERE / 'REPORT.md').write_text(report)

template = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{font:14px var(--font-sans,system-ui);color:var(--foreground);line-height:1.45;margin:0}
button,select{font:inherit;background:var(--secondary);color:var(--foreground);border:1px solid var(--border);border-radius:var(--radius,6px);padding:5px 8px}
.controls{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:12px}label{display:flex;gap:6px;align-items:center}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;margin-bottom:12px}.dot{display:inline-block;width:10px;height:10px;margin-right:4px;border-radius:2px}
.project{margin:14px 0 20px}.name{font-weight:600}.note{color:var(--muted-foreground);font-size:12px;margin:4px 0 8px}
.barrow{display:grid;grid-template-columns:115px 1fr 48px;gap:8px;align-items:center;margin:4px 0;font-size:12px}
.track{height:15px;background:var(--secondary);border-radius:3px;overflow:hidden}.bar{height:15px;border-radius:3px}
table{width:100%;border-collapse:collapse;font-size:12px}td,th{text-align:left;padding:5px;border-bottom:1px solid var(--border)}
summary{cursor:pointer;margin-top:10px}p{margin:10px 0}.warn{padding:12px;background:var(--warning-surface,var(--secondary));border-radius:var(--radius,8px)}
</style></head><body>
<div class="controls"><label>Evidence <select id="definition"><option value="broad">Broad fix titles</option><option value="strict">Strict fix titles</option></select></label><label>Windows <select id="split"><option value="holdout">Held out, final 20%</option><option value="development">Development, 50–80%</option></select></label></div>
<p>Future fix-related file touches captured when selecting about 20% of source files. Higher is better for this proxy.</p>
<div class="legend" id="legend"></div><div id="chart" role="img" aria-label="Comparison of Elo and baseline rankings by project"></div>
<div class="warn">These are noisy commit-title labels. Results do not measure confirmed defects, absolute code quality, or the benefit of an architectural change.</div>
<details><summary>Window-level evidence</summary><div id="windows"></div></details>
<script>
const aggregate=AGGREGATE, windows=WINDOWS;
const models=[['elo','Elo','var(--chart-1)'],['fix_count','Historical fixes','var(--chart-2)'],['recent_touch_count','Recent changes','var(--chart-3)'],['constant_control','Random expectation','var(--muted-foreground)']];
const names={'edge':'Edge','openstrap-analytics':'Analytics','qex':'Qex','diff-core':'Diff-core'};
document.getElementById('legend').innerHTML=models.map(m=>`<span><i class="dot" style="background:${m[2]}"></i>${m[1]}</span>`).join('');
function draw(){const definition=document.getElementById('definition').value, split=document.getElementById('split').value;
document.getElementById('chart').innerHTML=Object.keys(names).map(project=>{let rows=aggregate.filter(r=>r.project===project&&r.definition===definition&&r.split===split);let base=rows.find(r=>r.model==='elo');
return `<div class="project"><div class="name">${names[project]}</div><div class="note">${base.eligible_fix_touches} eligible fix-related file touches · ${base.cold_start_touches} new-file touches excluded · ${base.nonempty_windows} nonempty windows</div>`+models.map(m=>{let r=rows.find(r=>r.model===m[0]);let v=r.recall===null?0:100*r.recall;return `<div class="barrow"><span>${m[1]}</span><div class="track"><div class="bar" style="width:${v}%;background:${m[2]}"></div></div><span>${r.recall===null?'n/a':v.toFixed(1)+'%'}</span></div>`}).join('')+'</div>';}).join('');
let rows=windows.filter(r=>r.definition===definition&&r.split===split&&r.model==='elo');
document.getElementById('windows').innerHTML='<table><thead><tr><th>Project / window</th><th>File budget</th><th>Fix touches</th><th>Elo recall</th></tr></thead><tbody>'+rows.map(r=>`<tr><td>${names[r.project]} ${r.window}</td><td>${Math.round(r.selected_files)} / ${r.eligible_files}</td><td>${r.eligible_fix_touches}</td><td>${r.event_recall===null?'n/a':(100*r.event_recall).toFixed(1)+'%'}</td></tr>`).join('')+'</tbody></table>';}
document.querySelectorAll('select').forEach(e=>e.addEventListener('change',draw));draw();
</script></body></html>'''
(HERE / 'comparison.html').write_text(template.replace('AGGREGATE', json.dumps(summary))
                                     .replace('WINDOWS', json.dumps([r for r in results if r['model'] == 'elo'])))
print('Wrote summary, report, evidence, draft scenario, Paneweft bundle, and interactive chart.')
