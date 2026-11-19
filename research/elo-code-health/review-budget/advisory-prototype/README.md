# Object-snapshot evidence collector

This research prototype captures the installed build-loop policy's next action on a byte-pinned ledger and a named Git commit. Every result disables execution. It does not rate code, approve a change, run a review, or establish that an additional round would help.

The scope is Git objects. Uncommitted working-tree changes are outside coverage. A final historical ledger is not an authentic earlier decision snapshot; the output preserves that uncertainty.

`boundary_observed` describes the canonical gate on the supplied ledger and named object at collection time. It does not reconstruct a historical as-of decision or cover the live working tree. Each capture includes its UTC collection time and collector source hash. Repeated captures can have different event timestamps; identical serialized records remain idempotent in the content-addressed store. Git replacement refs are disabled so they cannot substitute other code behind a named commit.

The supplied ledger asserts that reviews and exchanges happened. Script and ledger hashes preserve those assertions; they do not authenticate reviewer identity, actual review execution, or completion of every past gate. Structural checks reject duplicate/nonincreasing/nonpositive round IDs and impossible phase order. They are not a replacement for the canonical workflow or proof of its history.

```sh
python collector.py capture \
  --source-root /home/mini/Documents/repos \
  --ledger /home/mini/Documents/repos/phoe-nix.research/w49.ledger.json \
  --repo /home/mini/Documents/repos/phoe-nix \
  --revision 4b397f979b8ba308e55e371ed1f8ab142dd6d219 \
  --store /home/mini/Documents/repos/mstack/research/elo-code-health/review-budget/advisory-prototype/observations
```

Omit `--revision` to resolve HEAD as an object-only snapshot. Explicit revisions must be full commit IDs. Source paths must lie inside the explicitly selected source root; symlinks and oversize inputs are refused. Stored research records must remain under this prototype directory. Exit 0 means a capture completed, including an honest insufficient-evidence result; exit 2 means capture/input validation failed. Both emit JSON. Neither exit code grants approval.

Optional `--fact FILE` accepts this shape:

```json
{
  "category": "cancellation",
  "accepted": true,
  "fix_revision": "<full ancestor commit ID>",
  "diff_sha256": "<canonical Git diff SHA256>",
  "artifact_path": "<bounded source-root-contained report path>",
  "artifact_sha256": "<report bytes SHA256>"
}
```

Categories are `async-wait`, `lock-or-lease`, `cancellation`, `transaction-publication`, and `multi-stage-transition`. The fix must have exactly one parent and be an ancestor of the target object. Diff bytes use:

```sh
git -c core.fsmonitor=false -c core.quotePath=true \
  -c diff.algorithm=myers -c diff.mnemonicPrefix=false -C REPO \
  diff --binary --full-index --no-renames --no-ext-diff --no-textconv PARENT FIX --
```

Matching hashes establish byte identity and Git reachability. They do not verify the report's meaning. Both category and acceptance remain supplied assertions. An accepted structural-fix trigger can produce an owner-action candidate only at a covered canonical STOP-AGREED boundary. Allocation remains unresolved, and execution stays disabled. Missing triggers never recommend fewer reviews.

Outcomes are separate immutable records:

```sh
python collector.py record-outcome \
  --observation /absolute/path/to/observation-HASH.json \
  --outcome /absolute/path/to/outcome-input.json \
  --store /absolute/path/inside/advisory-prototype/outcomes
```

An unobserved input is `{"state":"unobserved","reason":"No additional review performed."}`. A reported input has `state: reported`, `report_path`, `report_sha256`, and `scope`, which is `all-material-findings`, `blockers-only`, or `partial`. Outcome inputs and reports must reside under this prototype directory. Reported text never becomes an inferred clean negative or independently accepted defect.

The trusted boundary is the local user, installed policy, Git binary, and selected repository metadata. This is not a hostile multi-user service. No arbitrary executable policy path is accepted. Git hooks, repository scripts, external diff, textconv, and builds do not run. A policy hash change requires adapter review rather than automatic acceptance. Reads use bounded regular files and no-follow directory walks; subprocesses have time and output limits.

`IMPLEMENTATION-PROTOCOL.md` records the frozen scope. `test_collector.py` exercises CLI behavior and the actual canonical seam. `check_mutations.py` runs three isolated known-wrong variants. `smoke-records/` contains the real object-only w49 capture, which correctly reports a required tier-2 review pending. It is descriptive and is not a historical optional-review training label.
