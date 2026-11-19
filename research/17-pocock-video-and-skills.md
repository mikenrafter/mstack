# 17. Matt Pocock's skills, as shown in his 21,000-line feature video

Written 2026-11-18. Sources: the video's auto-captions (69 minutes, pulled
with yt-dlp because Readwise had no transcript), a full clone of
`mattpocock/skills` with all branches and pull-request refs, and Lauren Tan's
`comment-sicko` agent in `cursor/plugins`. Nothing was posted or opened
anywhere. Timestamps like [44:00] point into the video.

## Top findings

1. **Naming the domain chose the data model.** Twenty minutes of arguing about
   whether a thumbnail's drawing is a "diagram", a "diagram snapshot", a
   "thumbnail drawing" or a "thumbnail scene" settled a separate table with a
   nullable "started from snapshot" link. Grade D (one demo).
2. **ADRs were consulted during grilling.** The agent read an old architecture
   decision record (ADR) before proposing a change, and wrote a new one. Pocock
   objected only because it wrote the ADR without asking him. Grade D.
3. **The stacked split was improvised after the fact.** He split a finished
   21,000-line PR into seven PRs: two-way doors (easy to revert) ending in one
   one-way door (hard to revert). There is no skill for this in his repo, on
   any branch. Grade C (reproducible prompt, observed result).
4. **Door labels told him where to spend review.** Of seven PRs, he called only
   the additive schema migration mandatory to review. Grade D.
5. **His retro turned twelve review comments into lint rules with a shrinking
   baseline.** The skill's rule is that a mechanical violation gets a
   deterministic check, and judgement calls go to a standards file the reviewer
   reads. Grade C.
6. **Comment density was the loudest review complaint.** 12% of the repo's lines
   were comments, 18% in the new feature. An audit of about 2,000 comment lines
   found about 940 removable, 7 stale, 22 deletable outright, 18 that excused
   workarounds, and 3 that should be ADRs. Grade C (agent's count, not
   checked).
7. **Since the video, the visible work is a `constrain` skill (unmerged PR
   #1441, 11-17 and 11-18)**: allowlist fences around a tool's API, error
   messages that name the alternative, and a baseline that only shrinks. `main`
   has not changed since 2026-11-12. Grade C.
8. **His own retro found the single-PR approach overloaded review.** The code
   review skill could not cover a diff that size with one agent, and prototype
   code was copied into production instead of reimplemented. Grade C.

## How his process works

The flow below is what the video shows, checked against `ask-matt/SKILL.md`,
which routes between his skills.

1. **Pick by diff size [03:08].** A small diff gets one-shotted. A large one
   starts with `/grill-with-docs`. Work too foggy for one session moves to
   `wayfinder`, which maps decisions as tickets across sessions.
2. **Prompt with the why [05:30].** He describes the friction (leaving the
   thumbnail editor, re-screenshotting diagrams) and leaves the solution open.
   Dictated with Wispr Flow into Claude Code, Opus 5.5, medium effort, inside
   his private "home repo".
3. **Grill [06:00–42:00].** The `grilling` skill maps a design tree and asks
   the whole "frontier" (every decision whose prerequisites are settled) in one
   numbered round, each with a recommended answer worded so "yes" accepts it.
   Facts are the agent's job, found by fresh subagents; decisions are the
   user's. He reached Q40. Two steering moves:
   - "Ask me one question at a time until I say otherwise" at a crux [16:00],
     then "widen out" once it was settled [25:30].
   - He stops when he is answering "yes, yes, yes": the agent is deciding as he
     would [38:50].
4. **Glossary [10:23].** The project keeps a `GLOSSARY.md` of about 560 lines.
   His skill's format: `**Term**:` one or two sentences, `_Avoid_:` synonyms,
   no implementation detail, updated inline as terms settle. During grilling he
   also renamed "component" to "diagram component" because it collided with
   React components, and rejected "scene" because the glossary already used it.
5. **Scenario testing of names [22:37].** When two names compete, the agent
   writes a table of real sentences ("I dragged an arrow in the thumbnail's
   diagram snapshot") against each candidate, including a column for "is this
   how Matt talks". Snapshots cannot change, so that sentence ruled out
   "snapshot".
6. **ADRs [15:19].** `docs/adr/NNNN-slug.md`, as short as one paragraph. Offer
   one only when all three hold: hard to reverse, surprising without context,
   the result of a real trade-off. His framing: the glossary and code say what
   is; ADRs say why, so nobody removes a fence without knowing why it was put
   up.
7. **Prototype in parallel [13:00, 33:13].** While grilling continued, a
   background subagent built three UI variants on one route. Two were bad, which
   told him as much as the good one. Iterating on the winner surfaced a free
   undo history from tldraw.
8. **Spec and tickets [42:28].** `/to-spec` writes a GitHub issue (47 user
   stories, implementation decisions, test seams, out of scope, a link to the
   prototype branch) without interviewing. `/to-tickets` writes sub-issues as
   vertical slices with "blocked by" edges, prefactors first. He did not review
   the nine tickets closely.
9. **Compact, then implement AFK (away from keyboard) [46:28].** Compacting
   right after the conversation became a spec is "almost free", in his words.
   `/implement-spec` runs one fresh subagent per ticket in its own worktree,
   merges each into one integration branch, then runs `code-review` with two
   parallel axes: standards and spec.
10. **Split into a stack [48:43].** Prompt, roughly: break it into smaller PRs,
    each reviewable alone, a run of two-way doors ending in a one-way door. He
    asked for line counts per PR and a feature flag so the largest PR became
    four two-way doors plus a final flag flip.
11. **Human review [51:30].** He reviews for the system that produced the code.
    Each comment is a hypothesis about the agent's environment, aimed at a rule
    that stops it recurring: no `as` outside shared utilities, `interface
    extends` over intersections, no `useEffect` in one directory, a typed
    search-params helper, a typed API client instead of raw `fetch`, and fewer
    comments. Any new lint rule starts loose and tightens over time; he calls
    this a ratchet.
12. **Retro [57:50].** `/retro` read about 30 local session transcripts and the
    12 review comments through `gh`, and returned a ranked list. Root cause: his
    written standards said nothing about his complaints, and his docs taught the
    patterns he rejected, with thousands of existing instances. About 20 issues
    came out, some filed on his own skills repo.
13. **Comment audit [1:04:16].** He pushed the agent to sort comments into
    delete, fix the workaround, or move to an ADR. Workaround comments for
    tldraw quirks became adapter wrappers; race constraints became test names.
    He filed an umbrella issue and floated a skill that treats comments as
    smells.
14. **QA after merge [1:05:58].** He merged the whole stack, then tried the
    feature. Follow-up feedback becomes small issues an agent one-shots.

His summary of where he adds value: alignment at the start (grilling,
prototype) and taste at the end (review, retro).

## What went right

- The language work produced the data model. A separate thumbnail diagram, a
  nullable source link, and a "not lossy" rule came out of naming, not out of
  schema design.
- The written record stopped a wrong turn. The agent ruled out "preserved
  snapshot". Pocock pointed at that glossary term, the agent read ADR 3, and
  it agreed it had been wrong.
- Parallel prototypes during grilling cost no waiting time and killed two bad
  designs before any spec existed.
- The prototype exposed a rendering bug. The agent reproduced it in a browser
  and read pixel colours to locate it. It turned out to be Chrome at 125%
  Windows scaling, not a code bug.
- The door split put his review effort on the single migration.
- The retro found one root cause behind twelve comments, not twelve fixes.
- The shipped feature matched the prototype closely.

## What went wrong

- **The agent made his decisions.** It wrote an ADR and a glossary entry
  ("thumbnail drawing") without asking. He hated the word and wanted ADRs
  decided in the grill.
- **Grilling misread the codebase twice.** It said a diagram search did not
  exist (it did) and proposed soft delete everywhere (mostly present already).
  Facts are supposed to come from fresh research subagents; these slipped
  through.
- **"Yes" accepts the recommendation by design.** That makes "yes, yes, yes"
  ambiguous. It can mean alignment or fatigue. He took it as alignment.
- **A 260k-token subagent got the bug hunt.** He said a fresh one would have
  been better. His repo added "start subagents with a fresh context" on 10-29
  (`7739eae`), but the orchestrator reused a long-lived prototype agent anyway.
- **The stack was retrofitted.** The two-way doors were cut from finished code,
  so none was deployed or verified alone. He then merged all seven in order and
  checked the result once, on production. He said himself he was "cosplaying"
  a production system.
- **Review came after 21,000 lines existed.** His retro found the review skill
  could not cover the diff with one agent. Prototype code was copied into the
  product instead of reimplemented.
- **His docs contradicted his taste.** Agents copied the patterns already in
  the repo and its docs. Rules written later fight thousands of instances.
- **Tests barely appeared.** Reducer tests were mentioned once. Verification
  was the agent's code review plus his manual QA after merge.

## What has changed in the repo since the video

The recording date is unknown. The video says `implement-spec` "came out in
v1.3"; the last tag is `v1.3.2` (2026-10-29). `main` is at `5863806`
(2026-11-12), so it matches what he used if he recorded after that.

Unmerged work since 11-09:

- **`constrain` skill, PR #1441 (`84a81fe` 11-17 to `31964fa` 11-18).** The
  generalised form of his review comments. "Agents handle nuance badly, so
  'use this carefully' fails and 'use only these' works." It builds an
  allowlist fence over imports, property access, method calls and import edges
  (dependency-cruiser, import-linter, depguard, ArchUnit). Every error message
  names what to use instead. A baseline of existing violations only shrinks.
  It interviews through `grilling` and ends by adding one line to `CLAUDE.md`
  naming the fence and its check command. An early draft required a facade;
  `089b6fb` dropped it because a facade is all-or-nothing and an allowlist
  works one occurrence at a time. It fences APIs, not comments.
- **`animatic` skill, PRs #1422 and #1429 (11-12 to 11-13).** Narrated MP4s
  built from still frames. The config branch adds to `CLAUDE.md`: "Every PR
  carries an animatic", posted as a PR comment.
- **chief-of-staff brief block (`49043b4`, 11-09).** Every subagent brief needs
  Commands, a Report section covering refusals, overruns and slips, and an
  exact stop condition.

Earlier, still relevant:

- `chief-of-staff` (in-progress, `5ae4816` 10-31) runs `retro` on about one
  subagent session in five. That automates the feedback loop shown in the
  video.
- `software-factory` (in-progress, `4ae2317` 10-31) describes a daily ratchet
  task that "takes one file off the exception list".
- `pr` (`d75dcf1` 09-17, credited to Dex Horthy's `show-me`) puts
  `**Door:** one-way or two-way` and `**Blast Radius:**` in every PR body. The
  door idea lives in the PR description, not in any splitting rule.
- `writing-for-agents` warns that prohibitions drag the forbidden behaviour
  into context: "write one-line comments" works better than "no comments".
- `codebase-design` cites Ousterhout's "Design It Twice" but rejects his depth
  ratio in favour of "depth as leverage".

No commit anywhere records the comment audit or a comment ban. The video's
retro most likely changed the course-video-manager repo, which is private.

Lauren Tan's `comment-sicko` (in `cursor/plugins/pstack`, last pstack commit
`2f87c85` 11-16) is the stricter source he cited. It keeps only legal headers,
non-obvious behaviour forced by an outside dependency, `prettier-ignore`,
public API doc comments, and issue or RFC links. A surprise in your own code is
marked `MUST KILL` for a rename, extraction, type, or redesign. It reports and
never edits code.

## Where your setup differs

| Topic | Pocock | You | Verdict |
|---|---|---|---|
| Pre-build interview | `grilling`: whole frontier per round, recommended answers, facts by subagents | `question-everything`: designer interview, push back, then cross-model spec review and red tests | Aligned in intent. Yours goes further before code. Take his frontier format and fact/decision split. |
| Glossary | `GLOSSARY.md`, no implementation detail, `_Avoid_` lists, scenario tests | `technical-excellence` §4 lexicon: term, meaning, where it lives. residual has lexicon entries with aliases | Aligned. You lack scenario tests and a rule against framework-word collisions. |
| Decision records | ADRs, three-condition test | None. CLAIM comments and residual forces carry some of it | Gap. |
| Prototypes | Several throwaway variants, in parallel with grilling | Not a step | Gap for UI and feel questions. |
| Implementation | Parallel fresh subagents, one integration branch, AFK | build-loop: one working agent, red/green phases, scored cross-model review | Different bets. Yours costs more and catches more before merge. His catches more at retro. |
| PR shape | One big PR, split after the fact | One PR per build-loop | Neither of you has a stacking skill. You can be first. |
| Review | One agent review (standards and spec), then human taste | Bounded cross-model review with a findings ledger | Yours is stronger on correctness. His turns taste into rules faster. |
| Retro | A skill; mechanical findings become deterministic checks | One-off research (06, 07) and ledger analysis | Gap. Your own data says prose rules did not survive compaction (00-index item 4), which supports his checks-first rule. |
| Ratchet | Lint baselines that only shrink | build-loop bar B10: review stage only rises | Same idea in a different place. Extend yours to lint baselines. |
| Comments | Moving toward bans by folder | CLAIM comments with sources, test WHY lines | Real disagreement. See below. |
| Periodic audits | Retro on one session in five | `adaptive-hardening` with a budget | Yours has the budget control his lacks. Put retro and comment audits under it. |

## Candidate actions

Ranked by value for cost.

1. **Plan stacks at ticket time, labelled by door.** Add a stack plan to
   `question-everything`'s output: ordered slices, each tagged two-way or
   one-way, with at most one one-way door per stack, at the top. Two one-way
   doors make two stacks. Two-way examples: prefactors, glossary and ADR docs,
   additive code behind a flag, tests. One-way examples: migrations that
   transform or drop data, external API contracts, published formats, a flag
   turned on for users, security exposure. Pocock's flag trick turns a large
   behaviour PR into several two-way doors plus one flip. Kent Beck's split
   between structure changes and behaviour changes gives the same cut from the
   other side. This fixes his main failure: his doors were cut after the code
   existed.
2. **Scale the grill to the door.** A full grill on every PR in a seven-PR
   stack will wear you down, and "yes, yes, yes" follows. Grill the stack plan
   once. Grill each one-way door in full and review it yourself. Give each
   two-way door the "ten questions before a pull request ships" step your
   README already plans, cut to three questions, answerable in one batch.
3. **Put a limit on yourself that only tightens.** `file-pr` refuses a PR over
   N changed lines (excluding lockfiles and generated code) without a stack
   plan. Start N at about 800. Record N in `bars.json`, as B10 does, so it only
   drops unless you log an override. Have build-loop print at session start
   how many one-way doors merged without your review, and how many oversized
   PRs you waved through. Raising N requires a written reason.
4. **A retro skill with a checks-first rule.** Inputs: Claude and Codex
   transcripts, review-ledger findings, and your PR comments via `gh`. A
   mechanical finding becomes a deterministic check with a shrinking baseline.
   A judgement call goes to the reviewer's standards file. A skill defect goes
   to an mstack issue for you to approve. Run it at phase boundaries under
   `adaptive-hardening`'s budget. It also checks whether repo docs teach the
   patterns being rejected, his biggest root cause.
5. **ADRs, decided with you.** `docs/adr/NNNN-slug.md`, his three-condition
   test, offered during grilling and written only after you say yes. Where a
   decision answers a residual force, link the force id in the ADR by hand.
   Report 10 warned against turning review notes into residual records
   automatically, and that warning applies here.
6. **Make residual's lexicon the glossary source.** It already stores terms and
   aliases, which match Pocock's `_Avoid_` lists. Export a `GLOSSARY.md` for
   agents without implementation detail. Keep "where it lives" in a separate
   map file so the glossary stays readable. Add two checks to
   `question-everything`: scenario-test competing names, and refuse a term that
   collides with a framework word or an existing glossary term.
7. **A periodic comment-smell audit.** It keeps the comments that pay their
   way and gives each survivor a check. Classify every comment:

   | Class | Action |
   |---|---|
   | Narration that restates code | Delete |
   | Note from an agent session ("added for ticket 4", "now we...") | Delete; add a technical-excellence rule against them |
   | Excuse for a workaround in your own code | Reshape the code (adapter, type, rename); comment dies. Lauren's `MUST KILL` |
   | Constraint from a vendor, platform or protocol | Keep with a link, ideally inside an adapter |
   | Why behind a cross-module decision | Move to an ADR; leave `ADR-0007` |
   | Ordering, race or timing rule | Becomes a test name plus a CLAIM id |
   | Verifiable claim with a source | Keep as CLAIM. This is where you differ from Pocock and Lauren, deliberately |
   | Public interface contract | Keep (Ousterhout) |
   | Stale: contradicts the code | Fix or delete |

   Flag a comment as possibly stale when git blame shows it older than the
   code it sits above. Track comment-line ratio per directory, excluding CLAIM
   lines, and let directories opt into a no-comment baseline that only drops.
   Run it on changed files at PR time and on the whole repo monthly under
   `adaptive-hardening`.
8. **Prototype variants for feel questions.** Add a branch to
   `question-everything`: when the answer depends on how something looks or
   feels, build two or three throwaway variants in a background subagent while
   the interview goes on. Keep the prototype on a `prototype/` branch and
   reimplement it. Pocock's retro caught the copying.
9. **Take the frontier question format, with a guard.** Number every question,
   give a recommended answer, research facts with fresh subagents. Then make
   every fifth question one where the recommendation is "no", or ask you to
   restate a decision in your own words, so a run of "yes" means something.
10. **Door and blast radius in every PR body.** Add two lines to `file-pr`.
    It is the cheapest item here and feeds item 3.

## Things worth keeping that you did not mention

- Prompting with the why gave the agent room to propose the editing modes he
  had not thought of.
- Compacting right after a spec is written is safe because the spec holds the
  decisions. That bears on your compaction findings (00-index item 4): compact
  at a point where everything that matters is already in a file.
- "Smart zone" has softened. He now treats the roughly 150k-token mark as a
  cost and quality trade, not a cliff.
- Review comments are hypotheses about the environment the agent works in,
  each aimed at a rule. That is a cheap test for which of your own review
  comments deserve follow-up.
- A domain rule surfaced in grilling ("nothing lossy, soft delete everywhere")
  became a constraint the agent applied unprompted later. Rules like that
  belong in the glossary or an ADR.
- His skills improve through issues filed from retros. mstack could take the
  same input from your retros.
- `constrain`'s allowlist-plus-baseline design fits Rust (clippy
  `disallowed_methods`, `disallowed_types`) and Nix as well as TypeScript.

## Sources

- Video: Matt Pocock, "Watch me ship a 21,000-line feature with
  mattpocock/skills", 2026-11-18, https://www.youtube.com/watch?v=jVBlkOF8sHk
  (captions saved under the session scratchpad, not committed).
- Repo: https://github.com/mattpocock/skills at `5863806` (2026-11-12);
  branches `constrain-skill` (PR #1441), `animatic-skill` (#1422),
  `animatic-config` (#1429), `chief-of-staff-brief-block`. Accessed
  2026-11-18.
- Key files: `skills/productivity/grilling/SKILL.md`,
  `skills/engineering/domain-modeling/{GLOSSARY-FORMAT,ADR-FORMAT}.md`,
  `skills/engineering/{prototype,to-spec,to-tickets,implement-spec,code-review,pr,retro}/SKILL.md`,
  `skills/engineering/ask-matt/SKILL.md`.
- Lauren Tan, `comment-sicko`,
  https://github.com/cursor/plugins/blob/main/pstack/agents/comment-sicko.md,
  pstack at `2f87c85` (2026-11-16).
- John Ousterhout and Robert C. Martin, comment debate,
  https://github.com/johnousterhout/aposd-vs-clean-code (also cited in 05).
- Kent Beck, *Tidy First?* (O'Reilly, 2023): structure and behaviour changes
  in separate commits.
