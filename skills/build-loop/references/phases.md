# build-loop reference: scope, red, spec gate, green (§3–§5)

SKILL.md §1 decides the intent and the scope. This file holds what happens
between that and the review loop (§6).

## 3. Scope and base

1. `git status --short`. Never stash, discard or include unrelated changes.
   If the change paths do not separate cleanly from other edits, stop and ask.
2. `git fetch origin`, then find the base:
   - PR: `gh pr view <n> --json baseRefName,headRefOid`. Check the branch out
     only if the tree is clean and `HEAD` is the PR head (or ahead only by this
     change). Base:
     `git merge-base HEAD origin/<baseRefName>`.
   - Local: `git merge-base HEAD origin/<default-branch>`. No remote: a base
     the user names, or `HEAD` for uncommitted changes only.
3. The change is base to working tree in those paths, plus untracked files.
   Use ONE diff command every round.
4. State intent and out-of-scope in 1-2 sentences. Run covering checks; note
   missing or pre-failing ones in the brief.
5. Fresh worktree: run project setup first.
6. Commit the current state; record the base SHA.

## 4. Red (one run)

One implementer run writes failing tests for the WHOLE scope, plus only the
stubs needed to compile. No behaviour. Prompt it with `test-quality`. On a
pilot, the scope is the pilot's own cases (`references/scoping.md`).

Verify the red gate yourself:
- tests fail on assertions, not on compile or import errors;
- failures match the intended contract gaps;
- controls (tests that must stay green) pass;
- each test states its WHY, and CLAIM ids where a claim is proved;
- each test carries `# catches:` naming a plausible wrong implementation it
  fails; none nameable means likely tautology (`test-quality`).
- a test of the form *when X, then Y* names its witness:
  `# reaches: <test that drives the system into X>`.

Commit red.

## 4a. Spec review gate (before green)

Load `question-everything`. Before the spec is written, interview the designer
and yourself (its §1–§3) on states, edges, data lifecycle, precedence, safety,
checklists and reuse. Push back until the detail is high-fidelity.

After red is committed, send the spec, the red tests and the checklists to
the reviewer (Sol). Ask it also to write short wrong implementations that pass
the red tests; each one is a missing test. Fix the spec and red tests, then
re-verify the red gate. At most two spec rounds; anything still open becomes a
logged default (§1a). Then start green and the review loop (§6). On a pilot the
gate may run alongside green (`references/scoping.md`).

## 5. Green

Batch size follows §2. Each prompt carries: what earlier phases did (commit
SHAs, report paths), file pointers, decisions, the remaining red tests, and
"stop when" criteria. The implementer writes its report early and keeps it
current, so a cut-off run leaves one.

Prefer a type-level fix to a runtime check (`technical-excellence`).

Verify between phases with the project's runner, on touched suites plus
guards. Commit each phase before the next.

**Spot mutations.** After green, apply 2-3 of the `# catches:` wrong
implementations and check the matching tests go red. A green implementer that
edits a red test says so in its report; the edit becomes a review finding.

**Commit hygiene.** Check `git diff --cached --stat` before every commit; in
a shared tree use `git commit --only -- <paths>`.

**Crash or cut-off.** If a run dies or ends without a report, read the diff,
run the tests and judge the state yourself. Do not trust silence or a stale report.
