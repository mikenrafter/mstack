# 16. Veil or Jujutsu for landing agent flurries on Edge (PLAN W40)

Written 2026-11-12. Research only. Nothing in Edge, its worktrees or its
branches was changed. Nothing was committed.

Labels: **[measured]** means I ran it or counted it here. **[inferred]** means I
reasoned from what I read. **[claimed]** means the project says so and I did not
check it.

## Recommendation

1. Edge stays on git and GitHub. Veil cannot be used with it, and jj is not
   shown to be worth a switch yet.
2. Do not adopt veil. It is nine days old, has one author, no release, needs a
   Postgres and S3 server, and its owner has made "no git interop" permanent.
3. jj is a real option, but the replay shows it does not remove the conflict
   work. It removes the stalled rebase, not the resolutions.
4. Smallest first step: add `jujutsu` to one agent's tools and have it use a
   colocated clone for the "rebase onto `integrate/next`" step only, for one
   week, on one non-critical branch family. Record rounds and wall time.
5. Revisit veil only if it ships a 1.0 with a git bridge, or if Edge drops
   GitHub. Revisit a wider jj move if the week shows fewer interventions or
   fewer lost-work incidents than git.

## 1. How Edge lands flurries today

Sources: `edge.research/RULES.md` (A.1, A.3, 2026-10-27 rules), `chat-cls-merge.md`,
`merge-decisions-log.md`, and the `edge` repo.

**The process [measured from the notes].** Agents work in one git worktree each
(74 worktrees under `edge.worktrees`, plus the main checkout). To land, an
agent fetches, rebases its branch onto `origin/integrate/upstream`, tests, then
pushes `HEAD:integrate/next HEAD:integrate/upstream`. Pushes must be
fast-forwards. There is no merge queue. Collisions are settled by chat
(`chat-cls-merge.md`: "fetch + rebase onto it before you push, and say what you
pushed"). A test lock and memory limits (`edge-test`) keep the 7 GB machine
alive. Git hazards that RULES.md already records: a stray checkout hung a suite
(A.3), a conflicted rebase once pushed its mid-rebase HEAD (2026-10-27),
`git stash` is shared across worktrees (2026-10-27).

**Volume [measured].**

| What | Number |
|---|---|
| Pushes to `origin/integrate/next` seen in this clone's reflog, 2026-10-19 to 11-12 | 103 on 13 days |
| Of those, fast-forward | 103 (all) |
| Commits landed by those pushes | 573 (mean 5.6 per push) |
| Busiest day | 2026-10-27: 20 pushes, 114 commits |
| Second busiest | 2026-10-21: 21 pushes, 82 commits |
| Merge commits on `origin/integrate/next` since 10-17 | 16 of 718 commits (2%) |
| Worktrees created per day | 8 to 13 on the busiest days (10-22, 10-23, 10-27), about 2.7 on average |
| Worktree life, creation to last commit | median 4.5 hours, p90 3.4 days, max 8.3 days |
| Worktree HEADs already inside `origin/integrate/next` | 44 of 74 |

The reflog only shows updates seen by this clone, so pushes are a floor. The
older local `integrate/next` (stale at 2026-10-21) shows the earlier pattern: 542
merge commits in 2,830, 161 of them on 2026-10-04 alone, when PR merges were the
landing method. Since 10-17 the method is rebase and fast-forward.

**Conflicts [partly measured].** Edge does not record conflicts anywhere I could
count. I found three signals.
- The big one: the 2026-10-18 catch-up of the fork onto upstream main. Trial
  merge: 135 conflicting files, 291 hunks in a dry 3-way (`merge-decisions-log.md`,
  `cls-merge-notes.md`). It was not done as a rebase of 373 commits ("would stop
  on hundreds of conflicts", decision D3). It became one merge plus topical
  commits.
- Routine landings: one conflict in a CLS merge (D6), and a `db.dart` conflict
  while rebasing PR branches (resume note, 2026-11-01).
- Resolution is by an agent or by Sol, with the project's `resolve_hunks.py`
  to pick sides per hunk. Typical hot files: `db.dart`, `app_state*`, the `.arb`
  language files, `lib/ui2`.

So the pattern is: most landings are clean fast-forwards of small stacks. The
cost is in a few large rebases of stale branches.

## 2. Veil

Source: clone at `veil.research/src` (commit `1384ff8e`, 2026-11-12), README,
`CLAUDE.md`, `docs/HUB.md`, `docs/guide/workspaces-and-agents.md`,
`docs/design/scale/LOAD.md`. [github.com/RKKatakam/veil](https://github.com/RKKatakam/veil).

**Model.** A server (the Hub) holds the code, in PostgreSQL or YugabyteDB plus
S3. The `vl` client is always connected; there is no offline mode. The client
engine is very close to jj: working copy auto-snapshotted, stable change ids,
an undoable operation log, conflicts stored as data in the change, workspaces
with no directory. On top of that: sandboxes (bubblewrap on Linux; macOS runs
unconfined), per-folder permissions enforced by the server, signed agent
attribution, "dead end" records, and `vl land`.

**Landing [per HUB.md §13.19 and §13.30, read not run].** `vl land` submits a
change. The server lands non-overlapping changes in batches with one move of
`main`. For overlapping paths it runs a 3-way text merge on a pool of 8 workers,
re-queues up to 3 times, and then answers `conflict` to the submitter with the
base, tip and your version of each path. Binary files and new files with
different content fail the merge. "Land first, test after": `main@tested` is the
newest passing `main`, and the server bisects and reverts a culprit.

**Guarantees and limits.**
- Conflict handling is a line-level 3-way merge, the same class as git's. [inferred]
  I found nothing that resolves semantic conflicts, so Edge's hot files
  (`db.dart`, `.arb`) would conflict the same way.
- Permissions are real server-side folder access. Edge has one trusted owner and
  a few agents on one machine, so it has little use for them. [inferred]
- Throughput [claimed, one 32-core box]: 500 landings a second held for 3
  minutes, about 1,000 in 15-second bursts, and open bug BUG-1955 where a mixed
  load lands about 230 a second. Edge lands about 20 pushes on its busiest day.
  The scale is four to five orders of magnitude beyond the need. [inferred]

**Git interop: none, on purpose.** `CLAUDE.md`: "Veil does not interoperate
with Git (no import, export, sync, colocation ...). Owner decision, 2026-11-05:
permanent." `BUGS.md` says bug ids from "the removed Git interop are retired",
so it once existed and was cut. For Edge this ends the question: Edge's upstream
work is GitHub PRs from git branches (`OpenStrap/edge`), and the fork lives on
GitHub.

**Maturity [measured from the clone and `gh api`].**
- First commit 2026-11-03; 1,343 commits in 9 days; one author (the contributor
  list shows one). 15 stars, 1 fork, no GitHub releases, `0.1.0`, "pre-release"
  in its own README.
- About 314,000 lines of Rust in 535 files; 3,276 `#[test]` attributes; 59
  `#[ignore]`d bug reproductions. `docs/BUGS.md` is 1.5 MB with 747 rows; the
  README says about 75 bugs were found in review and ten benchmark misses were
  filed on 2026-11-12, five fixed.
- The project instructions file shows the code is largely written by an AI
  agent under a heavy process. That is not a defect in itself, but nobody else
  has run it. [inferred]
- Dual MIT or Apache-2.0 in `Cargo.toml` and both license files (GitHub reports
  Apache-2.0).
- Not proven, by its own README: several machines, failover, the macOS sandbox.

**Cost to adopt for Edge [inferred].** Run Postgres and an object store, build
the server from source (no release), move 3,300 commits of history with no
importer, give up GitHub PRs, CI and the fork flow. Every one of the 74
worktree workflows and `edge.research` scripts would be rewritten.

## 3. Jujutsu (jj)

Sources: [github.com/jj-vcs/jj](https://github.com/jj-vcs/jj) (read 2026-11-12),
[git compatibility](https://docs.jj-vcs.dev/latest/git-compatibility/),
[concurrency](https://docs.jj-vcs.dev/latest/technical/concurrency/),
[working copy and workspaces](https://docs.jj-vcs.dev/latest/working-copy/),
`jj help absorb`.

**Model.** The working copy is a commit and is snapshotted by every command.
Changes have stable ids across rewrites. Rebasing never stops: conflicts are
stored in the commit, descendants are rebased automatically, and you resolve
when you choose. The operation log records every command and allows `jj undo`
and `jj op restore`. There are no locks: concurrent commands from several
workspaces are merged as operations, with conflicts shown as data.

**For many concurrent agent changes.**
- Stacking: `jj rebase -b BRANCH -d TARGET` moves a whole stack in one command
  and finishes even with conflicts.
- Deferral: a conflicted commit can be left, and a different agent can
  resolve it later. Resolving the lowest conflicted commit re-rebases its
  descendants, which can clear their conflicts at no cost.
- `jj absorb` moves edits in the working copy into the closest earlier commit
  that touched those lines, which suits review fixes on a stack. [documented,
  not exercised here]
- Workspaces: `jj workspace add` gives one working copy per agent on one repo.
  Rewriting a commit from another workspace makes a workspace "stale", fixed by
  `jj workspace update-stale`.
- Undo: `jj op restore` undid my own mistaken test rebase cleanly. [measured]

**Git interop.** Colocated repos share `.git` and `.jj`; jj imports and exports
on every command, and uses git's own transport and authentication, so GitHub
pushes and fetches work. Gaps: no git hooks, no LFS, no submodule checkout, no
`.gitattributes`, no partial clone, no `git worktree` (use `jj workspace`), only
remote settings and `core.excludesFile` read from git config, and "bugs
remain when interleaving mutating jj and git commands". Conflicted files look
odd to git tools. Edge has 74 git worktrees, so a move means converting those
to jj workspaces.

**Maturity.** First commit 2020-12-18; 32,462 stars, 1,285 forks, 1,225 open
issues (`gh api`, 2026-11-12). Releases about monthly: 0.45.1 (2026-09-03),
0.46.0 (10-07), 0.47.0 (11-04), 0.47.1 (11-05). Apache-2.0. Google is a main
contributor but not a supported Google product. The README still calls it
experimental, says only the git backend is production-ready, and expects format
and workflow changes before 1.0. Many people use it daily, but there is no 1.0.

**Install here [measured].** `nix eval nixpkgs#jujutsu.version` gives `0.41.0`;
`nix shell nixpkgs#jujutsu` fetched it from cache in 4 seconds. That is six
minor versions behind upstream's 0.47.1, so a pinned newer build is likely
needed for new features.

## 4. Replay on Edge history

**Setup [measured].** `git clone --local` of Edge to
`veil.research/replay`, then two scratch copies (since deleted to free 2.5 GB;
logs and scripts kept in `veil.research/replay`). Target tip: live
`origin/integrate/next` at `54eacba6` (2026-11-12). I landed nine unlanded
branches onto it, one after another, each rebased onto the moving tip and then
fast-forwarded in. The same order and the same rule (at a conflict, take the
branch's own side) was used for both tools. Scripts: `replay/git-replay.sh`,
`replay/jj-replay.sh`.

The nine branches: `wake/dev-harness-b`, `agg/pairing-ux-mockups`,
`meals/rework`, `cls/header-v2`, `next/nav-guides`, `cls/spiral-ring-mock`,
`wake/630-stack`, `haptics/core`, `ed/1-sync-import` (100 commits in all).
The last three are based on upstream main and are 1,111 commits behind the tip,
so they are a hard case, not a typical landing. The first six are on the
`integrate/next` line.

| Landing | Commits | git: stops | git: files | jj: rounds | jj: files | git secs | jj secs |
|---|---|---|---|---|---|---|---|
| wake/dev-harness-b | 17 | 0 | 0 | 0 | 0 | 1 | 1 |
| agg/pairing-ux-mockups | 25 | 8 | 39 | 8 | 39 | 4 | 11 |
| meals/rework | 8 | 0 | 0 | 0 | 0 | 1 | 1 |
| cls/header-v2 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| next/nav-guides | 26 | 5 | 28 | 6 | 33 | 4 | 11 |
| cls/spiral-ring-mock | 5 | 0 | 0 | 0 | 0 | 1 | 1 |
| wake/630-stack | 21 | 8 | 21 | 8 | 21 | 3 | **1,049** |
| haptics/core | 3 and 2 | 2 | 27 | 2 | 27 | 3 | 2 |
| ed/1-sync-import | 4 and 3 | 2 | 3 | 2 | 3 | 1 | 1 |
| **Total** | | **25** | **118** | **26** | **123** | 19 | about 1,077 |

"Stop" is a place where `git rebase` halts. "Round" is one `jj resolve` of the
lowest conflicted commit. Both are one manual resolution. The git commit count
differs by one for `haptics/core` and `ed/1-sync-import` because the jj copy
counts after earlier landings and drops commits already present.

What the replay shows [measured]:
- Five of nine landings were clean in both tools. Four needed work, and the
  count of manual resolutions was the same: 25 for git, 26 for jj. jj did not
  save resolutions here.
- The difference is how the work arrives. jj finished every rebase. It reported
  24 of 25 commits conflicted on `agg/pairing-ux-mockups` and 26 of 26 on
  `next/nav-guides` at once, but only 8 and 6 rounds cleared them, because
  resolving the lowest commit cleared the descendants. Git stops 8 times mid
  rebase with the tree in a half-state.
- Hunk counts are not comparable (git 385 total, jj 155): git counts markers at
  each stop, jj counts them in the lowest conflicted commit. Treat them as
  rough.
- **jj was slow on the hard case.** `wake/630-stack` took 1,049 s (17.5 min,
  one core, 470 MB) against git's 3 s, for 21 commits on a base 1,111 commits
  behind. I did not find the cause; it may be fixed in newer versions (this was
  0.41.0). It is the main practical finding against jj for Edge's stale-branch
  case.
- Disk: jj's scratch copy was 2.0 GB against git's 0.5 GB. [measured, includes
  the colocated checkout]
- The replay took the branch's own side at every conflict, which says nothing
  about whether the result is correct. It measures how often a human or agent
  must intervene, not how hard each intervention is.

Not tested: `jj absorb`, `jj workspace`, concurrent agents against one repo, the
push path to GitHub, and any veil run (I did not run veil's server).

## 5. Criteria

| Criterion | Veil | jj | Edge today (git) |
|---|---|---|---|
| Conflict handling at volume | Server 3-way text merge, 3 re-queues, then back to the agent; conflicts stored as data in rebases [read] | Rebase never stops; conflicts stored, resolved lowest-first, descendants follow [measured] | Rebase stops per conflicted commit [measured] |
| Number of manual resolutions | Not measured; same merge class as git [inferred] | 26 vs git's 25 on nine landings [measured] | 25 [measured] |
| Rebase and stack ergonomics | Same ideas as jj plus `vl land` [read] | Best of the three: `rebase -b`, auto-rebase of descendants, `absorb` [read, partly measured] | Fine for small stacks; fragile for stale ones |
| Agent isolation and permissions | Strongest: sandbox, folder access, signed attribution [read] | Workspaces only; no sandbox or permissions [read] | Worktrees plus owner-set process limits |
| Git interop | None, permanent [read] | Colocated, GitHub works; no hooks, no `git worktree` [read] | Native |
| Maturity | 9 days, 1 author, no release, 15 stars [measured] | 6 years, 32k stars, monthly releases, still pre-1.0 [measured] | Stable |
| Cost to adopt | Server, S3, no importer, lose GitHub [inferred] | Install, convert worktrees to workspaces, retrain scripts [inferred] | None |
| Speed on a stale branch | n/a | 1,049 s vs 3 s [measured] | 3 s [measured] |

## 6. What this means for Edge

Edge's pain is not the volume of landings. About 20 pushes on a busy day, nearly
all clean fast-forwards, is small. The pain is a few big rebases of stale
branches and the git hazards recorded in RULES.md (detached HEADs, shared
stash, mid-rebase pushes). jj would remove those hazard classes: no stash, no
detached-HEAD state, no half-finished rebase, and undo by operation. [inferred]
It would not reduce the number of conflicts that need a decision, and on the
stale-branch case it was far slower in this test.

Veil attacks a problem Edge does not have (thousands of agents on one trunk) and
costs what Edge cannot pay (leaving git and GitHub).

## 7. What would change the answer

- Veil ships 1.0 with a working git bridge, has a second maintainer, and runs
  across several machines as it says it will.
- Edge moves off GitHub, or the agent count grows by two orders of magnitude.
- A week of jj on one agent shows fewer interventions, no lost work, and
  rebases that are not slower than git's. A re-run of the 17.5 minute case on a
  current jj (0.47 or later) would be the first check.
- jj's slow case turns out to be a bug fixed upstream, or gets reproduced with
  a smaller example. Either way it needs a look before anyone trusts jj with a
  stale 1,000-commit rebase.
- Edge's semantic conflicts (same logic changed two ways) turn out to dominate.
  Neither tool helps then; an agent resolver would.

## Sources

- Veil repo and docs: [github.com/RKKatakam/veil](https://github.com/RKKatakam/veil),
  cloned and `gh api` read 2026-11-12.
- Jujutsu: [github.com/jj-vcs/jj](https://github.com/jj-vcs/jj),
  [git compatibility](https://docs.jj-vcs.dev/latest/git-compatibility/),
  [concurrency](https://docs.jj-vcs.dev/latest/technical/concurrency/),
  [working copy](https://docs.jj-vcs.dev/latest/working-copy/), all read 2026-11-12.
- Anthropic, [Redesigning source control](https://www.anthropic.com/research/redesigning-source-control),
  2026-10-13 (the Scion design veil follows; the post says Scion is not offered
  as a product and is not "a suitable replacement for git for general use").
- Edge: `edge.research/RULES.md`, `merge-decisions-log.md`, `cls-merge-notes.md`,
  `chat-cls-merge.md`, `agg-resume-note.md`; git history of `edge`
  (`origin/integrate/next` reflog and log, worktree creation times).
- Replay logs and scripts: `veil.research/replay/` (`git-replay.log`,
  `jj-replay.log`, `git-replay.sh`, `jj-replay.sh`).
