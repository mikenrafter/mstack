"""Present one pinned historical causal case using Paneweft's real graph wire format."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

import jsonschema
from referencing import Registry, Resource

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
REPOS=Path('/home/mini/Documents/repos')
PANE=REPOS/'paneweft'
SCHEMA=PANE/'src/schemas'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(['git','--no-replace-objects','-C',str(PANE),*args])


def selected(run):
    return {a['fullName']:a for suite in run['test_report']['testResults']
            for a in suite['assertionResults'] if a['status']!='skipped'}


def semantic(bundle):
    view=bundle['views'][0]
    graph=view['data']
    nodes={n['id'] for n in graph['nodes']}
    edges={e['id']:e for e in graph['edges']}
    if len(nodes)!=len(graph['nodes']) or len(edges)!=len(graph['edges']):
        raise ValueError('Duplicate graph ids')
    sources={s['id'] for s in view['sources']}
    for item in graph['nodes']+graph['edges']:
        if not set(item['evidence'])<=sources:
            raise ValueError('Unknown evidence source')
        if item['provenance']=='inferred' and not set(item['basis'])<=sources|nodes|set(edges):
            raise ValueError('Unknown inference basis')
    for edge in edges.values():
        if edge['from'] not in nodes or edge['to'] not in nodes:
            raise ValueError('Dangling graph edge')
    for path in graph.get('paths',[]):
        chain=[edges[e] for e in path['edgeIds']]
        if any(left['to']!=right['from'] for left,right in zip(chain,chain[1:])):
            raise ValueError('Disconnected named path')


def main():
    capture=datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z')
    archive=HERE/'sources'
    archive.mkdir(exist_ok=True)
    sources=[]
    manifest=[]
    def store(key,raw,name,origin,method):
        hashed=digest(raw)
        path=archive/f'{hashed}-{name}'
        if path.exists() and path.read_bytes()!=raw:
            raise ValueError('Content-addressed capture changed')
        path.write_bytes(raw)
        sources.append(dict(id=key,kind='file',repository='evidence',path=str(path),
                            sha256=hashed,capturedAt=capture,method=method))
        manifest.append(dict(id=key,path=str(path),sha256=hashed,origin=origin,
                             bytes=len(raw),capturedAt=capture))
        return raw
    for key,path in [
        ('replay-results',PARENT/'cancellation-reproduction.json'),
        ('replay-report',PARENT/'REPRODUCTION.md'),
        ('audit',PARENT/'EVIDENCE-AUDIT.md'),
        ('prior-review',REPOS/'paneweft.research/v1/review-t2-r1.txt'),
        ('next-review',REPOS/'paneweft.research/v1/review-t2-r2.txt'),
        ('first-fix-report',REPOS/'paneweft.research/v1/fix-t2-r1-report.md'),
        ('next-fix-report',REPOS/'paneweft.research/v1/fix-t5-report.md'),
    ]:
        store(key,path.read_bytes(),path.name,str(path),'Exact saved evidence bytes, captured for this historical case; not current checkout freshness.')
    reproduction=json.loads((PARENT/'cancellation-reproduction.json').read_text())
    before=reproduction['versions']['before']
    after=reproduction['versions']['after']
    if git('rev-parse',f'{after}^').decode().strip()!=before:
        raise ValueError('Expected directly adjacent historical revisions')
    for role,revision in [('before',before),('after',after)]:
        store(f'jobs-{role}',git('show',f'{revision}:src/v1/jobs.ts'),f'jobs-{role}.ts',
              f'git:{PANE}@{revision}:src/v1/jobs.ts','Pinned Git blob; read-only capture.')
        store(f'commit-{role}',git('show','--no-patch','--format=%H%n%P%n%cI%n%B',revision),
              f'commit-{role}.txt',f'git:{PANE}@{revision}','Commit metadata and message; a historical author assertion.')
    tests=store('identical-tests',git('show',f'{after}:src/v1/jobs.test.ts'),'jobs.test.ts',
                f'git:{PANE}@{after}:src/v1/jobs.test.ts','Pinned test blob used identically in both saved replay runs.')
    if digest(tests)!=reproduction['test_sha256']:
        raise ValueError('Saved reproduction test hash differs from captured Git blob')
    captured={s['id']:s for s in sources}
    historical_fingerprint=dict(id='paneweft',root=str(PANE),gitRev=after,dirty=False,
                                files={'src/v1/jobs.ts':captured['jobs-after']['sha256'],
                                       'src/v1/jobs.test.ts':digest(tests)})
    store('fix-diff',git('diff',before,after,'--','src/v1/jobs.ts','src/v1/jobs.test.ts'),
          'fix.diff',f'git:{PANE}:{before}..{after}','Exact adjacent revision diff; production jobs.ts plus regression tests.')
    runs={r['name']:r for r in reproduction['runs']}
    old,new=selected(runs['before']),selected(runs['after'])
    if len(old)!=3 or set(old)!=set(new):
        raise ValueError('Expected identical three selected scenarios')
    if not all(old[name]['status']=='failed' and new[name]['status']=='passed' for name in old):
        raise ValueError('Expected same scenarios fail before and pass after')
    nodes=[]
    edges=[]
    def item(key,label,evidence,provenance='read',**extra):
        return dict(id=key,label=label,evidence=evidence,provenance=provenance,**extra)
    def node(key,label,group,evidence,provenance='read',**extra):
        nodes.append(item(key,label,evidence,provenance,group=group,**extra))
    def edge(key,left,right,label,evidence,provenance='read',**extra):
        edges.append(item(key,label,evidence,provenance,**{'from':left,'to':right,'relation':label},**extra))
    node('t4','T4: fresh-repository discovery requires an owner catalogue refresh','Historical review',['prior-review'])
    node('export-first','3fa003c: T4 fix introduces export-first staging','Historical source change',['commit-before','jobs-before','first-fix-report'])
    node('case','One historical cancellation case: T5 plus related T6 scenario','Defect family',['next-review','next-fix-report','audit'])
    node('before-tests','At 3fa003c: identical three scenarios fail','Saved independent replay',['replay-results','identical-tests'],'parsed')
    node('fix','d89c0e7: stage job-ID guard, cancellation recheck and current-stage cancel','Historical source change',['commit-after','fix-diff','jobs-after'])
    node('after-tests','At d89c0e7: identical three scenarios pass; historical bug fixed','Saved independent replay',['replay-results','identical-tests'],'parsed')
    edge('t4-fixed-by','t4','export-first','reported fixed by',['first-fix-report','commit-before'])
    edge('new-exposure','export-first','case','supported fix-induced interaction',['audit','next-review','fix-diff'],'inferred',
         reason='Export-first creates the stage transition implicated by T5; adjacent revision and same-test replay support this single historical case.',basis=['export-first','case','replay-results','fix-diff'])
    edge('case-fails','case','before-tests','reproduced at historical revision',['replay-results'],'parsed')
    edge('corrected-by','before-tests','fix','corrected in adjacent commit',['replay-results','fix-diff'],'inferred',
         reason='d89c0e7 directly follows 3fa003c; production jobs.ts and regression tests are the only changed files; identical tests change from fail to pass.',basis=['before-tests','fix','replay-results','fix-diff'])
    edge('fix-passes','fix','after-tests','same selected tests pass',['replay-results'],'parsed')
    scenario_specs=[
        ('a cancel that saw the export stop','T5: cancel holding stopped export must not finalize the newer run'),
        ('a cancel written after the export finish read cancel.json','T5: late cancel.json must prevent the next-stage submission'),
        ('cancel after the export stopped but before it was processed','T6: stopped export not yet processed must record cancellation'),
    ]
    scenario_records=[]
    for index,(fragment,label) in enumerate(scenario_specs,1):
        matching=[name for name in old if fragment in name]
        if len(matching)!=1:
            raise ValueError('Scenario label must match exactly one captured test')
        name=matching[0]
        key=f'scenario-{index}'
        node(key,label,'Related test scenario',['replay-results','identical-tests'],'parsed')
        edge(f'family-scenario-{index}','case',key,'one related scenario',['replay-results','next-fix-report'],'parsed')
        scenario_records.append(dict(id=key,test_full_name=name,before_status=old[name]['status'],
                                     after_status=new[name]['status'],test_sha256=digest(tests),
                                     scenario_independence='not_independent; one inspected causal family'))
    focus_reason='The demonstrated interaction crosses export/run advancement, cancellation intent and lease-protected state. This supports a review question, not an architecture optimization.'
    node('contract','Review focus: lifecycle and cancellation state ownership','Proposed review focus',['fix-diff','next-fix-report'],'inferred',
         reason=focus_reason,basis=['case','fix','fix-diff'])
    node('residual','Proposed component/outcome mapping; no Residual objects changed','Proposed integration',['fix-diff','replay-results'],'inferred',
         reason='Candidate executable outcomes are grounded in the three tests; mapping has not been imported or approved as a Residual force.',basis=['contract','before-tests','after-tests'])
    node('rerouting','Hypothesis: inspect one stage-aware owner for cancellation decisions','Unmeasured architecture hypothesis',['fix-diff','next-fix-report'],'inferred',
         reason='An alternative boundary might simplify stage ownership; no rerouting candidate has been implemented or compared.',basis=['contract','case'])
    edge('focus-from-case','case','contract','motivates a focused review',['fix-diff','next-fix-report'],'inferred',reason=focus_reason,basis=['case','fix'])
    edge('propose-mapping','contract','residual','proposed mapping only',['replay-results'],'inferred',
         reason='Outcomes can be attached to component candidates for later author review; this is not a registered force or defect probability.',basis=['contract','before-tests','after-tests'])
    edge('hypothesis-only','contract','rerouting','unmeasured alternative',['fix-diff'],'inferred',
         reason='Single-case evidence identifies a contract to examine; it does not establish a superior architecture.',basis=['contract'])
    snapshot='paneweft-case-3fa003c-d89c0e7'
    entity=dict(repository='paneweft',id='cancellation-history',kind='research/review-case')
    view=dict(schemaVersion='paneweft.view/1',id='cancellation-evidence-graph',
              title='One historical cancellation case, from review to reproduced fix',
              question='How did one review fix create a new cancellation interaction, and what evidence shows the later fix works?',
              entity=entity,snapshotId=snapshot,component='graph',viewDefinitionId='case-history-graph',
              scope=dict(repositories=['paneweft','evidence'],roots=[str(archive)],excludes=[],
                         limits=['One historical causal family; three related scenarios.',
                                 'Pinned revisions only; no current checkout or live policy claim.',
                                 'Saved independent replay used fake Qex and Cargo peers.']),
              sources=sources,generatedAt=capture,
              freshness=dict(repositories=[historical_fingerprint]),links=[],
              completeness=dict(status='partial',gaps=[
                  dict(id='current-tree',question='Does the current checkout contain a defect?',reason='Not assessed. This bug is fixed at historical d89c0e7. The supplied fingerprint is an expected historical snapshot, not an observation of current files; an unregistered session must report unverified.'),
                  dict(id='interop',question='Does this prove real runner interoperability?',reason='No. Production service, filesystem and lease paths ran with fake Qex/Cargo peers.'),
                  dict(id='architecture',question='Does rerouting improve architecture or review allocation?',reason='Not measured. Proposed mappings and review focus are hypotheses only.')]),
              data=dict(nodes=nodes,edges=edges,layout='layered',paths=[
                  dict(id='historical-case',edgeIds=['t4-fixed-by','new-exposure','case-fails','corrected-by','fix-passes'])]))
    bundle=dict(schemaVersion='paneweft.bundle/1',entities=[dict(entity,snapshotId=snapshot,
                label='Pinned Paneweft cancellation history',dataRoles=['history'],relations=[])],
                definitions=[dict(id='case-history-graph',entityKind=entity['kind'],title='Historical evidence',
                                  component='graph',requires=[],dataRole='history',priority=10)],views=[view])
    semantic(bundle)
    schema_paths=sorted(SCHEMA.rglob('*.json'))
    schemas=[json.loads(path.read_text()) for path in schema_paths]
    registry=Registry().with_resources((s['$id'],Resource.from_contents(s)) for s in schemas if '$id' in s)
    validator=jsonschema.Draft202012Validator(json.loads((SCHEMA/'bundle.schema.json').read_text()),
                                            registry=registry,format_checker=jsonschema.FormatChecker())
    errors=[str(e) for e in validator.iter_errors(bundle)]
    if errors:
        raise ValueError(errors)
    invalid=json.loads(json.dumps(bundle))
    invalid['views'][0]['data']['edges'][0]['to']='missing-node'
    try:
        semantic(invalid)
    except ValueError:
        dangling_rejected=True
    else:
        raise ValueError('Semantic checker accepts dangling edge')
    invalid=json.loads(json.dumps(bundle))
    invalid['views'][0]['data']['nodes'][0]['qualityScore']=100
    unknown_field_rejected=bool(list(validator.iter_errors(invalid)))
    if not unknown_field_rejected:
        raise ValueError('Real schema accepts invented graph quality field')
    proposal=dict(schema='research.residual-component-outcome-proposal/1',status='proposed',
                  imported=False,existing_residual_objects_modified=False,force_created=False,
                  basis=['case','contract','replay-results'],
                  component_candidates=[dict(path='src/v1/jobs.ts',functions=['finish','finishExport','cancel'],
                                             revision=after,role='Stage transition, lease and cancellation decisions')],
                  outcome_candidates=[dict(id='stage-owner',statement='Only the current stage job may finalize its state.',scenario='scenario-1'),
                                      dict(id='cancel-before-submit',statement='A cancellation observed while finishing export prevents the next run submission.',scenario='scenario-2'),
                                      dict(id='stopped-export-cancel',statement='Cancellation of an unprocessed stopped export ends cancelled without running the example.',scenario='scenario-3')],
                  limitations=['Outcome candidates are scoped to the captured tests.',
                               'A concrete bug has not been registered as a Residual stressor.',
                               'No proposed boundary or rerouting has been measured.'])
    def write(name,value):
        (HERE/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    write('paneweft.bundle.json',bundle)
    write('evidence-manifest.json',dict(capturedAt=capture,sources=manifest))
    write('scenarios.json',dict(causal_cases=1,scenario_count=3,before=before,after=after,scenarios=scenario_records))
    write('residual-proposal.json',proposal)
    write('checks.json',dict(passed=True,json_schema_errors=errors,nodes=len(nodes),edges=len(edges),
                            test_blob_matches_replay=True,identical_selected_scenarios=True,
                            direct_parent_verified=True,dangling_edge_rejected=dangling_rejected,
                            invented_quality_field_rejected=unknown_field_rejected,
                            expected_historical_fingerprint=historical_fingerprint,
                            freshness_fingerprint_basis='Pinned Git blobs at d89c0e7, not an observation of the working tree; dirty=false describes the expected committed snapshot.',
                            expected_cli_freshness_without_registration='unverified',
                            empty_freshness_integration_record='cli-checks.empty-freshness-v1.json',
                            bundle_sha256=digest((HERE/'paneweft.bundle.json').read_bytes()),
                            generator_sha256=digest(Path(__file__).read_bytes()),
                            schema_revision=git('rev-parse','HEAD').decode().strip(),
                            schema_files={str(p):digest(p.read_bytes()) for p in schema_paths},
                            cli_executed=False,viewer_rendered=False,subject_tests_rerun=False))
    print(json.dumps(dict(passed=True,nodes=len(nodes),edges=len(edges),captured_sources=len(sources),
                          causal_cases=1,scenario_count=3,bundle=str(HERE/'paneweft.bundle.json'))))


if __name__=='__main__':
    main()
