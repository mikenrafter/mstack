# Experiment schedule and disposition

The authorized window starts 2026-11-17 07:06:26 UTC and ends at 09:06:26 UTC. All reviewers and research agents use Codex. No live skill, product source, review cap or mandatory gate changes in this pass.

## Completed experiments

| Experiment | Frozen design | Run and result |
| --- | --- | --- |
| Review-label extraction | `PROTOCOL.md`, `corpus/` | 21 change groups, 75 rounds; 39 labeled later accepted-finding proxies, with 15 later outcomes unknown. Labels and provenance audited. |
| Forecast comparison | `models/PROTOCOL.md` | Complete-change and project holdouts. K8/16/32/64, fixed/decayed, simple prevalence, lag bucket and logistic. No meaningful gain. Optimizer defect corrected; invalid outputs quarantined. |
| External replication | `models/EXTERNAL-PROTOCOL.md` | Five separate chains, 14 known reported-finding outcomes; no accepted-defect target. No candidate clears the frozen gates. |
| Revision-shape diagnostic | `models/fix-shape/PROTOCOL.md` | Same 39 labeled rounds; frozen churn/state/coverage features worsen loss. No follow-on feature search. |
| Historical regression replay | `REPRODUCTION.md` | Identical three tests fail before and pass after one adjacent Paneweft fix. One family, not three independent defects. |
| Missing-outcome bounds | `missing-outcomes/PROTOCOL.md` | All 32,768 completions checked. No completion rescues the fixed forecast's 10% improvement target. |
| Observation collector | `advisory-prototype/IMPLEMENTATION-PROTOCOL.md` | Sixteen focused tests, mutation checks and independent review. All 21 real ledgers smoke-tested; three supported captures, 18 explicit legacy refusals. |
| Paneweft graph | `evidence-graph/` | Actual pinned CLI validates, stores and inspects all 11 exact edges. Historical freshness remains unverified. |
| Imperfect-test identifiability | `identifiability/PROTOCOL.md` | Exact synthetic equal-likelihood examples show why finding rate alone cannot identify code risk and reviewer detection. |
| Sampling feasibility | `power/PROTOCOL.md` | Exact positive-count calculations and explicitly simplified power references; 40- and 60-change examples are feasibility references, not promised statistical power. |
| Capture–recapture stress | `capture-recapture/SIMULATION-PROTOCOL.md` | 120,000 synthetic trials expose shared-difficulty, dependence and changed-snapshot failure modes. No empirical LLM gain. |
| Public human-inspection matrices | `capture-recapture/EMPIRICAL-PROTOCOL.md` plus explicit source amendment | All eight matrices and 602 pairs retained. Fixed two-list estimator underestimates remaining reference faults on average throughout. |
| Exact coverage curves | `capture-recapture/COVERAGE-PROTOCOL.md` | All 65,528 finite teams enumerated and independently checked. Seven of eight full pools miss some listed faults. |
| Focused historical challenge | `blind-challenge/PROTOCOL.md` | Fresh source-only contexts distinguish the known family across two versions. Shared parent hypothesis limits later independence; no accuracy/rating estimate. |

## Proposed next experiment

This is a proposal, not an installed automation or permission to run additional live reviews. It is the single initial schedule; the more expensive paired-review design in the uncertainty memo is a later alternative.

1. **Ten passive captures.** On new schema-2 review decisions, record the policy version, immutable ledger, code object, coverage, trigger facts and missing outcomes. Verify every mapping. No added reviews and no prediction claim.
2. **Ten-inspection feasibility checkpoint.** If a valid research allocation is separately agreed within existing gates and caps, collect one standardized independent inspection per sampled frozen change. Select samples independently of the trigger and keep the reviewer blind to it. Freeze private findings before parent feedback. Check effort, adjudication and missingness; this checkpoint cannot establish success.
3. **Fixed endpoint: 60 independently observed eligible changes or six weeks, whichever comes first.** Keep the trigger unchanged. Observe outcomes for every sampled change before evaluating offline prioritization at an 80% inspection budget. Forty independent changes are a minimum coverage criterion, not an alternative endpoint. Missing/unperformed reviews remain unknown. Closely related changes share one group. Do not extend automatically or add thresholds when results disappoint.
4. **One decision report.** Require the capture, independence, positive-count and matched-budget criteria in `advisory-design/DESIGN.md`. Report inspect-all's capture and cost. A negative or underpowered result retires the predictive claim. Any extension needs a separate budget decision.

The fixed trigger is an accepted review fix changing concurrency/lifecycle responsibilities. It is a conservative, post-hoc policy hypothesis, not a validated prediction. The failed revision-shape diagnostic does not support its discrimination. Sparse evidence favors an explicit request for inspection under the owner's preference; it never becomes an approval, lower mandatory floor or cap extension.

Start instrumentation with **phoe-nix**, whose three modern ledgers exercised the current collector. Use **Paneweft** for executable lifecycle cases and end-to-end evidence views. Keep **Edge** for high-volume longitudinal source activity and as a future enrollment project once its review decisions are captured in the supported format. Volume alone does not supply optional-review labels.

Capture–recapture needs a different second-stage design: complete private detection sets from independent reviews on exactly the same artifact and scope before fixes. Existing repeat-suppression/diff-only records do not qualify. Do not spend on paired extra reviews merely to fit that model during the first pilot.

To estimate optimal round count or avoided shipped defects, a later study must also measure review cost, repair outcomes and induced regressions with a defensible causal comparison. The proposed first pilot only tests prioritizing one additional authorized inspection.
