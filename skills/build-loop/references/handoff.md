# build-loop reference: ship and hand-off (§11–§12)

## 11. Ship

SKILL.md §11 holds the push and approval rule. The rest:

- Before opening any PR, run the project's FULL test suite on the head and
  on its base, on the same machine image, and compare them file by file (owner,
  2026-11-20). A selection by import graph is not enough: it misses tests that
  scan source text (a fork PR passed 3,986 selected tests and broke upstream
  main on such a guard). State the full-suite counts in the body and name each
  failure as inherited from the base. Run it again before a later push.
- For a project you do not own, check the PR against its reviewer notes
  (`references/reviewers.md`).
- In a PR body, add:

  `Reviewed with build-loop: <N> rounds with <model> (score <n>/10), then 1 pass with <model> (score <n>/10, bar <n>).`

- Add the Review check (`pr-stacks` §5) and run its teach-back (§4).
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
