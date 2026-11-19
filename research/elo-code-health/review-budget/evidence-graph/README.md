# One longitudinal review-fix evidence graph

`paneweft.bundle.json` presents one historical Paneweft cancellation regression family. Three related scenarios fail at `3fa003c852bef303ffe48c788093c2659d677870` and pass at its direct child `d89c0e7b750786a84ef8bf9a468967707333a9eb`. This is a fixed historical defect, not a current defect report or a quality score.

The graph follows T4's fresh-repository catalogue failure, its export-first staging fix, the subsequent T5 cancellation finding and related T6 scenario, the failing-before/passing-after replay, and a proposed review focus on lifecycle state ownership. The original T5 reply is saved. T6 appears in the fix report and test cases; its original discovery wording and round remain unknown.

The main path links the first review to a source change, then one new interaction and its correction. The three scenario branches remain within the same family. They are not three independent observations supporting more review rounds.

## Evidence and interpretation

The result is grade C, a controlled local behavioral reproduction with one inspected case and explicit runtime boundaries. The replay ran production `createJobService`, cancellation, filesystem state and leases with fake Qex/Cargo peers. The same test bytes, hash `8f1083aaf7162e923310a9d55ee6e542ec3fcc15dd84da862eb1ccb602506b91`, were used for both revisions. Three selected assertions failed before and passed after; 74 unrelated tests were not selected. The graph generator parses those saved results and does not rerun the product tests.

The fixing commit directly follows the export-first commit. Its only changed files are production `src/v1/jobs.ts` and regression `src/v1/jobs.test.ts`. This strengthens the narrow causal claim about these tested behaviors. The earlier T4 fix is linked to the later interaction through the inspected source and historical reports. It does not establish a general relationship between architecture complexity, review count and defect risk.

Provenance is visible per node and edge:

- `read` denotes historical report assertions or inspected pinned code/commit evidence.
- `parsed` denotes facts extracted from the saved replay JSON, including the same three scenario outcomes.
- `inferred` denotes the causal synthesis, review-focus recommendation or unmeasured architecture proposal. Each includes a reason and supporting basis IDs.

No `observed` label is added merely by importing a saved report. Sources are copied byte-for-byte into content-addressed files under `sources/`. `evidence-manifest.json` records their original locations, hashes and capture times. Git blobs and commit messages are preserved separately from prose reports. Capture time means artifact capture, not review time or code freshness.

## Paneweft and Residual

The bundle uses the sibling Paneweft repository's actual bundle, envelope, graph, entity, definition and common schemas. Its graph layout and item structure follow `fixtures/components/graph.json` and the graph golden. It contains 12 nodes and 11 edges, with a named historical path and typed relations.

`freshness.repositories` contains an expected historical fingerprint for repository `paneweft`, root `/home/mini/Documents/repos/paneweft`, revision `d89c0e7b750786a84ef8bf9a468967707333a9eb`, and the captured Git-blob hashes of `src/v1/jobs.ts` and `src/v1/jobs.test.ts`. This is a comparison target, not an observation of the working tree. Its `dirty=false` describes the expected committed snapshot. An isolated CLI session without a registered Paneweft root must report `unverified`, rather than imply current freshness. Completeness remains partial and names missing current-tree assessment, real-runner interoperability and architectural comparison.

An initial real CLI integration round-tripped all 11 exact edges but reported `fresh` because the first bundle supplied an empty repository-fingerprint list. Empty checking was therefore unsafe for this presentation's intended uncertainty. That result is retained unchanged in `cli-checks.empty-freshness-v1.json`; it concerns the earlier bundle hash. The generator now supplies the genuine expected historical fingerprint. This is an artifact integration correction, not a new product bug report. The regenerated bundle passed a separate pinned CLI check: validation, storage and inspection preserve all 11 exact edges, and freshness is `unverified` with `REPOSITORY_NOT_REGISTERED`. The saved `cli-checks.json` binds this result to bundle SHA-256 `3d44d4e36d704fcccaf25ea2c6dd2d612c3038b211693b2f284a47c2c0edc038`. `checks.json` describes the generator's schema checks; its `cli_executed=false` does not describe this separate integration run.

`residual-proposal.json` is an analysis proposal, not a Residual import payload. It links the candidate `finish`, `finishExport` and `cancel` responsibilities to three candidate test outcomes. No force/stressor, existing outcome or component matrix was created or changed. The graph's suggested stage-aware cancellation owner is an unimplemented hypothesis. A behavioral comparison would be required before recommending rerouting.

## Validation

Run the bounded generator from the mstack root:

```sh
qex submit --follow --cpu 1 --mem 256MB -- python3 research/elo-code-health/review-budget/evidence-graph/generate.py
```

`checks.json` records successful validation against the actual Draft 2020-12 JSON schemas, schema file hashes and checkout revision, graph-reference checks, adjacent-commit verification, matching selected scenarios and the test-blob hash. It also records the expected historical fingerprint and required unregistered-session outcome. Negative checks confirm rejection of a dangling graph edge and an invented `qualityScore` field. This verifies the wire bundle and evidence consistency. CLI checks are recorded separately by bundle hash. No browser rendering, current checkout freshness or new predictive-model gain is claimed.
