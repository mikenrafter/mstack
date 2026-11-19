"""Extract the frozen wake-pr family without inferring reviews from filenames."""
import collections
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
POOL=Path('/home/mini/Documents/repos/edge.research/wake-pr')
# These whole chains have linked prompts or an explicit saved round ledger.
CHAINS={'t12':5,'t3':5,'p8a':5,'cls1':5,'hmm-code':3}
TAG=re.compile(r'^([A-Z][A-Z0-9]*(?:-\d+)?) \[(blocker|should|nit|consider)\] (.+)$')
STATUS=re.compile(r'^([A-Z][A-Z0-9]*(?:-\d+)?) (CLOSED|OPEN)\b(.*)$')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def report(text):
    """CLAIM(report-only): only explicit tagged discoveries count [test_prompt_exclusion]."""
    verdicts=re.findall(r'^VERDICT: (APPROVE|CHANGES)\s*$',text,re.M)
    if len(verdicts)!=1:
        raise ValueError('Report requires exactly one explicit verdict')
    findings=[]
    statuses=[]
    for line_number,line in enumerate(text.splitlines(),1):
        tagged=TAG.match(line)
        status=STATUS.match(line)
        if tagged:
            key,severity,claim=tagged.groups()
            findings.append(dict(finding_id=key,severity=severity,claim=claim,source_line=line_number))
        if status:
            key,value,description=status.groups()
            statuses.append(dict(finding_id=key,status=value,description=description,source_line=line_number))
    explicit_negative=bool(re.search(r'No new findings\b',text,re.I))
    narrow_negative=bool(re.search(r'No new regressions or shipping blockers found|no new code regressions found',text,re.I))
    return dict(verdict=verdicts[0],findings=findings,statuses=statuses,
                explicit_negative=explicit_negative,narrow_negative=narrow_negative)


def lagged(previous):
    # CLAIM(lag-only): the upcoming report never supplies its own features [test_lag].
    before=previous[-1] if previous else {}
    return dict(completed_recorded_rounds=len(previous),previous_round=before.get('round'),
                previous_score=before.get('score'),previous_verdict=before.get('verdict'),
                previous_tier=before.get('tier'),previous_approach=before.get('approach'),
                previous_reviewer=before.get('reviewer'),previous_reviewed_sha=before.get('reviewed_sha'),
                prior_scores=[r.get('score') for r in previous],
                prior_verdicts=[r.get('verdict') for r in previous])


def assemble(chain, reports):
    numbers=[r[0] for r in reports]
    if numbers!=sorted(set(numbers)):
        raise ValueError('Explicit report rounds must be unique and increasing')
    rows=[]
    entities=[]
    seen={}
    for number,parsed,source,metadata in reports:
        new=[]
        repeated=[]
        for raw in parsed['findings']:
            key=raw['finding_id']
            if key in seen:
                repeated.append(key)
                continue
            entity=dict(raw,group_id=f'external/wake-pr/{chain}',discovery_round=number,
                        source=source,reported_consequential=raw['severity'] in {'blocker','should'},
                        independent_validity='unknown',semantic_duplicate_status='unknown',
                        final_status='unknown',resolution_events=[])
            entities.append(entity)
            seen[key]=entity
            new.append(entity)
        for status in parsed['statuses']:
            entity=seen.get(status['finding_id'])
            if entity and entity['discovery_round']<number:
                entity['resolution_events'].append(dict(status,observed_in_round=number,source=source))
                entity['final_status']=status['status']
        consequential=any(f['reported_consequential'] for f in new)
        # Full paired reports enumerating only nits are documented negatives in scope.
        documented= True if consequential else False if parsed['explicit_negative'] or bool(new) else None
        unmasked=documented
        scope_compatible=not metadata.get('final_budget_round',False)
        if documented is False and not scope_compatible:
            documented=None
        row=dict(group_id=f'external/wake-pr/{chain}',project=metadata['project'],
                 round=number,ordinal=len(rows)+1,source=source,score=None,
                 tier=None,approach=None,phase=None,reviewer=metadata.get('reviewer'),
                 verdict=parsed['verdict'],reviewed_sha=metadata.get('reviewed_sha'),
                 review_timestamp=None,timestamp_status='not_recorded',
                 report_scope='paired_complete_code_review_reply',
                 chronology_evidence=metadata['chronology_evidence'],
                 prompt_source=metadata.get('prompt_source'),
                 prompt_final_budget_round=metadata.get('final_budget_round',False),
                 scope_compatible_for_negative=scope_compatible,
                 raw_documented_consequential_discovery=unmasked,
                 negative_evidence_kind=('explicit_no_new_findings' if parsed['explicit_negative'] else
                                         'complete_report_has_only_nonconsequential_tags' if new and not consequential else
                                         'narrow_no_regressions_or_shipping_blockers' if parsed['narrow_negative'] else None),
                 documented_new_blocker=any(f['severity']=='blocker' for f in new) if new or parsed['explicit_negative'] or parsed['narrow_negative'] else None,
                 findings_policy_warning='Final budgeted prompts prioritize shipping blockers; threshold drift possible.',
                 new_finding_ids=[f['finding_id'] for f in new],repeated_tagged_ids=repeated,
                 new_recorded_findings=len(new),new_severity_counts=dict(collections.Counter(f['severity'] for f in new)),
                 documented_consequential_discovery=documented,
                 documented_accepted_consequential_discovery=None,
                 true_new_valid_consequential=None,
                 features_before_round=lagged(rows),policy_role='historical_schedule_unknown',
                 evaluation_role='external_replication_only_no_tuning')
        rows.append(row)
    for index,row in enumerate(rows):
        own=[f for f in entities if f['discovery_round']==row['round']]
        accepted=any(f['reported_consequential'] and f['final_status']=='CLOSED' for f in own)
        row['documented_accepted_consequential_discovery']=True if accepted else False if row['documented_consequential_discovery'] is False else None
        row['next_recorded_round']=rows[index+1]['round'] if index+1<len(rows) else None
        row['next_round_status']='observed' if index+1<len(rows) else 'right_censored'
    return rows,entities


def main():
    manifest=json.loads((HERE/'source-manifest.json').read_text())
    sources={}
    for entry in manifest['sources']:
        path=Path(entry['path'])
        raw=path.read_bytes()
        if sha(raw)!=entry['sha256']:
            raise ValueError(f'Frozen source changed: {path}')
        sources[path.name]=dict(entry,text=raw.decode())
    inventory=[]
    rows=[]
    findings=[]
    used=set()
    mapping=[]
    for chain,length in CHAINS.items():
        reports=[]
        for number in range(1,length+1):
            name=f'review-{chain}-r{number}-findings.md'
            source=sources[name]
            source_ref={k:v for k,v in source.items() if k!='text'}
            prompt_name=f'review-{chain}-r{number}.md'
            prompt=sources.get(prompt_name)
            if prompt:
                prompt_text=prompt['text']
                if number>1 and not re.search(rf'\bround {number}\b',prompt_text,re.I):
                    raise ValueError('No explicit round identity in paired prompt')
                if number>1:
                    predecessor=f'review-{chain}-r{number-1}-findings.md'
                    if predecessor not in prompt_text:
                        raise ValueError('Prompt does not link immediately preceding report')
                if number==1:
                    next_prompt=sources[f'review-{chain}-r2.md']['text']
                    if name not in next_prompt or not re.search(r'round[- ]1',next_prompt,re.I):
                        raise ValueError('Initial report lacks explicit round-one reference')
                snapshot=re.search(r'(?:detached at|branch [^\n]*? at) ([0-9a-f]{7,40})',prompt_text)
                metadata=dict(project='openstrap-analytics' if chain=='hmm-code' else 'edge',
                              reviewed_sha=snapshot[1] if snapshot else None,
                              chronology_evidence='Paired prompt states round and links previous report; next prompt anchors round one.',
                              prompt_source={k:v for k,v in prompt.items() if k!='text'},
                              final_budget_round=bool(re.search(r'FINAL budgeted round',prompt_text,re.I)))
                used.add(prompt_name)
            elif chain=='t3' and number==1:
                ledger=sources['review-t3-ledger.md']
                if 'Round 1: CHANGES' not in ledger['text'] or name not in ledger['text']:
                    raise ValueError('Missing explicit first-round ledger evidence')
                metadata=dict(project='edge',reviewed_sha='fc8545a4',reviewer='Opus stand-in',
                              chronology_evidence='Explicit saved T3 ledger identifies round 1, range80fbd41b..fc8545a4 and reply path.')
                used.add('review-t3-ledger.md')
            else:
                raise ValueError('Report lacks prompt or explicit ledger evidence')
            parsed=report(source['text'])
            reports.append((number,parsed,source_ref,metadata))
            used.add(name)
            mapping.append(dict(group_id=f'external/wake-pr/{chain}',round=number,
                                report=source_ref,**metadata))
        own,entities=assemble(chain,reports)
        rows.extend(own)
        findings.extend(entities)
    for name,source in sorted(sources.items()):
        inventory.append({**{k:v for k,v in source.items() if k!='text'},
                          'extraction_status':'used' if name in used else 'inventory_only',
                          'exclusion_reason':None if name in used else
                          'No complete paired explicit round chain in selected family, or redundant supporting ledger.'})
    summary=dict(groups=len(CHAINS),rounds=len(rows),later_rounds=sum(r['ordinal']>1 for r in rows),
                 findings=len(findings),severity_counts=dict(collections.Counter(f['severity'] for f in findings)),
                 reported_labels=dict(collections.Counter(str(r['documented_consequential_discovery']) for r in rows)),
                 later_reported_labels=dict(collections.Counter(str(r['documented_consequential_discovery']) for r in rows if r['ordinal']>1)),
                 later_raw_reported_labels=dict(collections.Counter(str(r['raw_documented_consequential_discovery']) for r in rows if r['ordinal']>1)),
                 accepted_labels=dict(collections.Counter(str(r['documented_accepted_consequential_discovery']) for r in rows)),
                 family_files=len(sources),used_files=len(used),
                 evaluation_role='external_replication_only_no_tuning',
                 warnings=['Source-folder Edge differs from Analytics target for HMM-code.',
                           'Four Tracks groups share code and cannot be treated as independent.',
                           'Scores and tiers are missing; no numerical values are imputed in the corpus.',
                           'Final budgeted round prompts can alter reporting thresholds.',
                           'Report IDs distinguish entries, not independently adjudicated defect mechanisms.'])
    for name,value in [('rounds',rows),('findings',findings),('inventory',inventory),('mapping',mapping)]:
        (HERE/f'{name}.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in value))
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary))


if __name__=='__main__':
    main()
