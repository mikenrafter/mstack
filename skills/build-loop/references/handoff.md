# build-loop reference: ship and hand-off (§11–§12)

## 11. Ship

SKILL.md §11 holds the push and approval rule. The rest:

- For a project you do not own, check the PR against its reviewer notes
  (`references/reviewers.md`).
- In a PR body, add:

  `Reviewed with build-loop: <N> rounds with <model> (score <n>/10), then 1 pass with <model> (score <n>/10, bar <n>).`

- Add `on <effort>` only if the tool exposed it.
- If the project forbids harness-attribution trailers, follow the project.

## 12. Hand-off report

- phases and commits; tests run, with counts;
- review rounds, reviewer model (and effort, if exposed), score per round and bar;
- the §6c checkpoint answers, including the enforcement layer per bug class;
- bot passes, findings per class and outcome (§6e);
- fixed and declined findings, with reasons and threat-model verdicts;
- diff size before and after review (`git diff --shortstat <base>`);
- what was pushed and where, or "not pushed";
- anything left red, and why. Report failures, skips and cut-off runs
  faithfully, with output.
