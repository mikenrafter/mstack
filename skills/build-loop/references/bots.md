# build-loop reference: upstream review bots (§6e)

## Triage script

`scripts/bot-triage` reads a PR's inline comments through `gh` and prints
each bot finding in one line (pass, commit, bot label, file:line, title,
your reply's outcome), with `<details>` blocks stripped (a CodeRabbit
comment shrinks about tenfold).

```sh
BT=<skill dir>/scripts/bot-triage
$BT list OWNER/REPO#N                   # latest pass; --pass all|K; --unanswered
$BT show OWNER/REPO#N <comment id>      # one finding, stripped
$BT guard OWNER/REPO#N                  # exit 1 while a bot thread is unanswered: run before each push
$BT stats OWNER/REPO#A OWNER/REPO#B     # passes, labels, fixed/declined: for the log (step 7)
```

A pass here is one bot's inline comments on one commit; a review with no
inline comments is not counted. Outcomes come from the first word of your
reply (`Fixed …`, `Not changing …`); anything else shows as `replied`.

PR bots (CodeRabbit, Sourcery, Copilot, Macroscope) label their own findings,
and the labels do not track weight. On edge #620, #669 and #671 CodeRabbit
left 45 inline findings: 39 Minor, 5 Major, 1 Trivial. Of the 31 answered,
26 were fixed and 5 declined. Several "Minor" ones were real bugs (a company
ID taken as band evidence, the wrong device handed to the pairing screen);
others were wording. Each push bought another pass: CodeRabbit reviewed 5
pushes on #620, 4 on #669 and 3 on #671, and #669's replies cite fixes in 7
different commits. So: judge each finding's real weight yourself, and spend
pushes sparingly. Babysitting itself follows `babysit-pr`; this section
decides what to do with what the bots say.

1. **Read the whole pass first.** Once a bot starts posting on the latest
   push, let that pass finish (its findings land over a few minutes), then
   triage them together. Do not hold a merge waiting for an advisory bot to
   start (`babysit-pr`).
2. **Verify, then classify by real weight.** Read each against the source and
   put it in one class, ignoring the bot's own label:

   | Class | What it is | Action |
   |---|---|---|
   | **bug** | Real bug in the intended case, or a threat-model exposure | Fix every instance of the class, with a test that fails without it |
   | **edge** | Real, but another path, rare case, hardening or small perf | One-line reply; follow-up list |
   | **taste** | Wording, naming, style, docs, "consider" | One-line reply, or fold in if trivially right and you are pushing anyway |
   | **wrong** | The bot misread the code | Reply with evidence (file:line, test) |
   | **pre-existing** | Not introduced by this PR | One-line reply; follow-up list |

   Test: would a maintainer who knows the code hold the merge for it? If
   not, it is not **bug**, whatever its label.
3. **One push per pass.** Batch every **bug** fix (and any trivially-right
   **taste** fold-ins) into one commit and one push. Never push for
   **taste**, **edge** or **pre-existing** items alone, since a push restarts the bot.
4. **Reply to everything, briefly**, per `leaving-pr-comments`, and resolve
   the threads you answered. A declined Minor needs one sentence, not a
   debate. Do not argue with a bot past one reply.
5. **Bot round cap.** After 3 bot passes, fix only **bug** findings; answer the
   rest in one line. If **bug** findings still come after pass 3, step back as
   in §6b and tell the user.
6. **Repeats across PRs go to a layer.** When a bot finding class shows up on
   a second PR, treat it like a §6c enforcement item: code first, then a guard
   test or lint, then a project checklist. A checklist line alone is the
   weakest fix (example: the copy and settings findings on #669/#671 became
   PERSISTENCE-CHECKLIST lines; a guard test would hold better).
7. **Log it.** Per PR, in the project's research dir or the hand-off report:
   bot passes to quiet, findings per class, and outcome (fixed, wrong,
   intentional, didn't matter). That log shows which bots and which labels
   earn attention.
8. **Practice questions.** After the last bot pass on a PR marked ready, run
   `vigil remind show practice-questions` and answer it if it is due.
