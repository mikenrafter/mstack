# Career and communication for a working engineer (2026-11)

Research date: 2026-11-10. Scope: communicating better at work, and searching
for a software job in the 2025–2026 market. Read-only research; no outreach
was done. Format follows `BRIEF.md`.

Evidence grades: **A** controlled study or benchmark with published data and
method; **B** large-scale observational data (n stated); **C** practitioner
report with concrete numbers or a reproducible demo; **D** opinion, anecdote.
Most career advice is grade D. I say so where it is.

## Top findings

- **Junior software hiring is weaker than senior hiring; the cause is
  disputed.** Indeed postings across occupations were 7.5% down year on year
  for entry-level roles and 14.7% up for senior roles as of May 2026. These
  are not software-only rates. Software development's senior share was 69.3%
  in Q1 2026. [Indeed, 2026-07-23](https://hiringlab.indeed.com/2026/07/23/the-labor-market-is-tilting-toward-seniority/).
  Stanford payroll data puts employment of developers aged 22–25 nearly 20%
  below its late-2022 peak by September 2025, [November 2025 paper](https://digitaleconomy.stanford.edu/app/uploads/2025/12/CanariesintheCoalMine_Nov25.pdf). LinkedIn's 2026
  report attributes the broad slowdown mainly to macroeconomic forces;
  whether AI inhibits entry-level recovery remains unclear. Grade
  **B** for direction, **D** for the AI explanation. The widely quoted "67%
  collapse" traces to one blog; do not repeat it.
- **Referrals correlate with interview and hire odds at one firm.** Referred applicants were more likely to be interviewed and hired
  (association only). Pragmatic Engineer's July 2026 interviews with 50+ hiring
  managers and engineers say the same: inbound applications are noise (one
  recruiter: 1,000+ per posting, 98% unqualified). Grade **B** (one firm) + **C**.
- **Polished application writing stopped being a signal once AI could produce
  it.** After Freelancer.com added a one-click AI proposal tool, tailored
  proposals stopped predicting who finished the job and employers paid less for
  them. Freelance proposals, not résumés, but the best published evidence on
  what AI does to application signals. Grade **A/B** (one platform). Shift
  effort from polish to things an employer can verify.
- **Structured interviews are the best-validated selection method.** The 2022
  revision of the meta-analyses puts them at validity 0.42 (down from 0.51),
  still top. This assesses employer-designed interviews, not STAR coaching
  or preparation efficacy. Grade **B** for meta-analytic predictive
  associations; candidate preparation remains **D**. An overcorrection
  dispute exists. [Sackett et al., 2022](https://gwern.net/doc/statistics/meta-analysis/2021-sackett.pdf).
- **Being watched reduced performance in a small experiment.** In a randomized trial,
  48 computer-science students solving a whiteboard problem under observation
  performed less than half as well as those solving it privately. This does
  not measure the effect of mock-interview practice. Interviewing.io says
  5+ mock interviews roughly double pass odds; grade **C** (vendor data).
- **Long gaps cost callbacks, mostly in the first eight months.** A field
  experiment with 12,054 fictitious résumés found callbacks fell about 45%
  (about 7% to 4%) between one and eight months unemployed, then flattened.
  Grade **A**. Dated, visible work during a gap is the usual counter; I found no
  study proving it works.
- **Moderately weak ties produce the most job moves.** LinkedIn randomized
  "People You May Know" for 20+ million members: inverted-U in tie strength,
  varying by industry. Grade **A/B**.
- **AI raises individual writing quality and makes group output more alike.**
  In a pre-registered experiment, AI-assisted stories were rated better and
  showed a similarity increase equal to 10.7% of the human-only score range
  in the one-idea condition and 8.9% in the five-idea condition. These are
  not relative increases in average similarity. Your voice is what an agent
  flattens. Use agents as critics, not ghostwriters. Grade **A** (short fiction).
- **Decision documents work because they force thinking.** Google, Amazon and
  Oxide describe the same mechanism: write the problem, options and trade-offs
  down before building and let people disagree in writing. Grade **C/D**
  (first-party self-reports that agree; no controlled comparison found).
- **AI in interviews is uneven.** Google is piloting Gemini in a
  code-comprehension round; Meta, Canva and Cognition allow AI in some rounds;
  Anthropic's reported default is no AI unless told; other firms are returning
  to in-person rounds over cheating. Grade **C** (press and roundups). Read each
  employer's instructions before every round.

## Limits

- Most advice here has no controlled evidence. Where the best source is a book
  or essay I grade it D and give you something to test.
- I could not open Fournier's chapter text, noidea.dog, Pragmatic Engineer's
  paywalled parts, or Indeed/LinkedIn PDFs in the initial pass. Cross-review checked the
  LinkedIn PDF and Indeed article directly. "Search summary" below means I saw a
  claim only in a summary of the primary source.
- The void host is offline, so I did not see your newest `diff-core` and
  `residual-cli` work or agent transcripts.
- I left contact details, salary and employer names from your job-seeking files
  out on purpose.

---

# Part 1. Communication

Most workplace communication failures are failures of structure and timing, not
eloquence: the reader did not know what you wanted, learned it late, or heard
about the problem when it was expensive to fix. Everything below moves that
earlier.

## 1.1 Writing for busy readers

**Core idea.** People scan. Nielsen and Morkes found 79% of users always
scanned a new page and 16% read word by word; concise, scannable, objective text
scored 124% better on usability. The 81 users were spread across three
1997 studies, not all in the final comparison. **A** for the website
comparison; **D** for transfer to workplace messages. Put the decision or ask first, then the reason, then detail, and say
what you want from the reader and by when in the first two lines.

**Sources.** Nielsen and Morkes, "Concise, scannable, and objective" (1997).
Julia Evans, ["How to ask good questions"](https://jvns.ca/blog/good-questions/)
(2016-12-31).

**Exercise this week.** Take your last three messages that needed a decision.
Rewrite each so the first two lines say what you need, from whom, by when. Send
the next real one that way. The ones you cannot write that way are the ones
where you do not yet know what you want.

**Agents.** Ask an agent to be a rushed reader: "Reply with the first thing you
would do after the first two lines, and list what you could not tell." Do not
ask it to rewrite. Use `plain-writing` and `unslop` as a last check.

## 1.2 Design docs and RFCs

**Core idea.** A design doc is written before the code by the people who will
build it, to surface trade-offs while they are cheap. Malte Ubl on Google's
practice (2020-07-06): write one when the right solution is ambiguous; skip it
if it would only be an implementation manual; use a 1–3 page "mini design doc"
for incremental work. Sections: context and scope, goals and non-goals (a
non-goal is a reasonable thing you chose not to do), the design, alternatives
considered (he calls it among the most important), cross-cutting concerns.

Amazon uses a six-page narrative memo, read silently at the meeting start. The
2017 shareholder letter says a good memo "probably should take a week or more"
and that authors' names never appear. The PR/FAQ (a future press release plus
FAQ written before building) is described in Bryar and Carr's *Working
Backwards* (2021; not read here). Oxide's RFDs (RFD 1, 2020-07-24) live in a
git repo, move through states (prediscussion to published, committed or
abandoned), and are discussed in a pull request: "Writing down ideas is
important: it allows them to be rigorously formulated." Oxide's RFD index is
public, a free corpus of real engineering RFCs.

Will Larson's strategy structure (2023-02-13, from Rumelt) suits a document
arguing for a direction: **diagnosis**, **guiding policies** (a policy with no
trade-off is suspect), **coherent actions**.

**Sources.** Ubl, [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/);
[Oxide RFD 1](https://oxide.computer/blog/rfd-1-requests-for-discussion);
Larson, [Writing engineering strategy](https://lethain.com/eng-strategies/);
Reilly, *The Staff Engineer's Path* (2022), ch. 3 "Creating the Big Picture".
Grade **C/D**.

**Exercise this week.** Pick a decision from your own repos (why a scout module
uses its language, say). Write a 1-page retrospective design doc: context,
goals, non-goals, the choice, two rejected alternatives and why, one risk. It
doubles as portfolio material (2.3).

**Agents.** After writing, ask: "List three alternatives I did not consider and
the strongest objection to my choice." Keep what is true. Do not let it write
"alternatives considered"; that section is your evidence of thinking.

## 1.3 Status updates and managing up

**Core idea.** Your manager explains your work upward in two sentences to
people without your context. A good update makes those sentences easy: what
changed, what is at risk, what you need and from whom. Bring problems with a
proposed next step. Fournier's *The Manager's Path* (2017) covers working with
your own manager early on (chapter 1 per the publisher listing; I could not
read it or confirm a "How to be managed" section).

Evans's ["brag document"](https://jvns.ca/blog/brag-documents/) (2019-06-28) is
a running list of what you did and its impact, so your manager can advocate for
you and you can recall it at review time or in a job search. Grade D, cheap,
widely adopted.

**Exercise this week.** Start a brag document. Backfill 12 months from commits,
PRs and notes, with numbers and a "what I learned" line. Write the weekly
update you would have sent for last week in the three-part shape.

**Agents.** Let the agent mine `git log` and PR history for the raw list ("group
these 40 commits by outcome"). You write the impact sentence; agent-written
impact statements sound like everyone else's.

## 1.4 Saying no, pushing back, disagreeing with seniors

**Core idea.** Silence is cheap now and costly later; blunt pushback damages the
relationship. Three practitioner frameworks, all grade D:

- *Radical Candor* (Kim Scott): care personally × challenge directly. Both is
  radical candor; challenge without care is obnoxious aggression; care without
  challenge is ruinous empathy; neither is manipulative insincerity. A check on
  your default, with no outcome data found.
- *Crucial Conversations*: weigh the risk of *not* speaking, and separate facts
  from the story you tell about them. Supporting survey data come from the
  authors' training company.
- Disagree and commit (Bezos, 2016 letter): "Look, I know we disagree on this
  but will you gamble with me on it?" It applies *after* you have said your
  piece, and the letter says real misalignment should be escalated, not settled
  by exhaustion.

Background at grade **B**: Edmondson's 1999 observational study of 51 teams
found associations among psychological safety, learning and performance,
[primary paper](https://web.mit.edu/curhan/www/docs/Articles/15341_Readings/Group_Performance/Edmondson%20Psychological%20safety.pdf); Google's Project Aristotle
later named it the top team factor. Popular statistics attached to it ("27%
lower turnover") lacked primary sources in what I found.

A script for seniors (my synthesis, D): "You're optimizing for X. I'm concerned
Y will make that harder, because Z. Would it help if I sketched both options
with costs?" It states the shared goal, names the risk with a reason, and
offers work instead of a verdict.

**Sources.** Scott, *Radical Candor*, ch. 1–2; Patterson et al., *Crucial
Conversations*; Bezos 2016 letter, "High-Velocity Decision Making."

**Exercise this week.** Write down one disagreement you swallowed in the last
year. Draft what you would say now using the script, and say it aloud.

**Agents.** Role-play a slightly impatient senior who challenges your
reasoning, not your tone. Run it three times with different personalities, then
ask which of your sentences gave room to dismiss you ("I just feel", "maybe").

## 1.5 Code review etiquette

**Core idea.** Comment on the code, not the person; explain why; label
importance; praise good work. Google's public guide: let the author choose the
fix unless direct guidance is clearly better; mark "Nit:", "Optional/Consider:"
or "FYI:". Speed counts too: in Google's study (Sadowski et al., ICSE-SEIP
2018; 12 interviews, a 44-respondent survey, logs of about 9 million changes)
changes were small and reviewed quickly, with a median first response under an
hour for small changes (figures from secondary summaries; check the paper).
Grade **B**, one company.

**Sources.** Google [eng-practices, "How to write code review comments"](https://github.com/google/eng-practices/blob/master/review/reviewer/comments.md);
Sadowski et al., [Modern Code Review at Google](https://research.google/pubs/modern-code-review-a-case-study-at-google/).

**Exercise this week.** Review one PR (yours, or an open-source one) with every
comment carrying a severity label and a "because". Rewrite any "why did you
use X?" that hides an instruction as a statement about the code.

**Agents.** Have the agent review your *comments*: "Which could read as
criticism of the author? Which has no reason?" That is a more tractable tool for
`diff-core` than a bug-finding agent.

## 1.6 Asking for help

**Core idea.** State your understanding and ask whether it is right; ask for
concrete facts; say when you do not know a term; do a little research first;
choose who and when. Rule of thumb (my synthesis, D): after 30 minutes stuck,
write the full question; it often solves itself.

**Exercise this week.** Next time you are stuck, write what you tried, expected,
saw and suspect before asking anyone. Ask only if still stuck.

**Agents.** Use an agent to tighten the written question, then send it to a
human when stakes or context are high. Asking the agent first every time erodes
the skill you are building.

## 1.7 Meetings and async writing

**Core idea.** Move information into writing; use meetings for decisions and
for conversations that need tone. Every meeting needs a stated output, a
pre-read, and written notes afterward. Amazon's silent-reading start is one
pattern; GitLab's public handbook describes async-first work (I could not
retrieve it). Evidence: D.

**Exercise this week.** Before any meeting write "The decision I want to leave
with is __". Afterwards send three lines: decisions, owners, dates.

**Agents.** Summarize transcripts into action items, then check them; summaries
drop hedges and misattribute agreement.

## 1.8 Explaining trade-offs to non-engineers

**Core idea.** Use the listener's terms: cost, time, risk, what they decide.
McKenzie's ["Don't Call Yourself a Programmer"](https://www.kalzumeus.com/2011/10/28/dont-call-yourself-a-programmer/)
(2011-10-28): engineers are paid for business value; describe work as money
saved or risk reduced; be able to explain what you do to an outsider. Grade D,
old, aged well. A table works: Option / Cost / Risk / What you give up / My
recommendation.

Your own work notes describe a project where it took months to learn users
cared about two of five PDF pages. A one-page "what the user does, what must
always be true" document in week one is the fix for that class of failure. It
is a communication artifact, not a technical one.

**Sources.** McKenzie; Reilly ch. 2–3 ("Three Maps", "Creating the Big
Picture": map people and problem before proposing).

**Exercise this week.** Explain one technical decision from your repos in six
sentences to a non-engineer using the table; ask them what they would decide.

**Agents.** Have an agent play a stakeholder who says "I don't understand X"
whenever you slip into jargon. Count interruptions.

---

# Part 2. Career and job search (2025–2026)

## 2.1 The market

Pragmatic Engineer (2026-05-26): top tech companies hiring about 20% more than a
year earlier, US and UK postings up, Germany and France down, AI engineering
demand "explosive". A Stack Overflow Blog post (2026-10-22; written by a
communications manager at a hiring marketplace, so lower reliability) says junior
postings fell 64% and junior share of hires went from 15% to 7% between 2022 and
2025/26. In July 2026 Pragmatic Engineer reported very high applicant counts,
fake or AI-assisted candidates, and engineers saying referrals are their only
route to interviews. Direction: **B**. AI as cause: **D**.

Implication: at a junior-to-mid level you compete in the thinnest slice.
Evidence of seniority-like behavior (owning something end to end, writing
decisions down, working in other people's code) matters more than keywords.

## 2.2 What gets interviews: evidence ladder

| Practice | Evidence | Grade |
|---|---|---|
| Referral | Higher interview and hire odds at one firm (NY Fed SR 568; association only). 2026 hiring-manager interviews say it dominates. Dan Luu notes Google found referrals add little *quality* signal, so employers discount them even as they open doors. | B (one firm) + C |
| Weak-tie networking | Moderately weak ties best for job moves; inverted-U (Rajkumar et al., Science 2022, n>20M). | A/B |
| Mass cold applications | Hiring managers call inbound noise. No controlled interview-rate-per-application estimate found. | C/D |
| Tailored cover letter | Signal collapsed after AI tools (Galdin and Silbert 2025, proposals). Reported as widely seen as pointless by hiring managers (Pragmatic Engineer; summary of a paywalled piece). | A/B proposals; D jobs |
| Public work you can be asked about | Recruiters and maintainers form impressions from GitHub activity (Marlow et al., CSCW 2013, qualitative). 2026 "AI portfolio" advice comes from blogs. | C/D |
| Shorter gap | Callbacks −45% by 8 months (Kroft et al., QJE 2013, n=12,054). | A |
| Résumé formatting | "6-second scan" and ATS rejection rates trace to marketing blogs. No engineer-specific study found. | D |
| Interview practice | The n=48 trial tests observation, not practice. Vendor data associates 5+ mocks with later passes. | C for practice association; D for dose |
| Structured interview design | Best-ranked predictive association in Sackett et al. 2022. This does not test candidate answer structure. | B; D for STAR advice |

Implication: spend hours on a short list of specific companies, on conversations
with people there, and on interview practice, not on tailoring documents.

## 2.3 Positioning and showing your work

**Core idea.** What survives AI-generated polish is verifiable specifics: a
thing a stranger can open or run, the reasoning behind it, and evidence other
people used or reviewed it. Galdin and Silbert's takeaway fits: "what have you
done lately?" backed by records.

**Presenting a large NixOS and agent-tooling body of work credibly** (D, my
synthesis; no controlled evidence on portfolios exists):

1. **Choose three, not fifty.** A reader cannot assess 55 scout modules. Pick an
   infrastructure piece with real constraints (the APK build queue or cache
   registry), a tool you shipped (a Rust scout module or Firefox extension), and
   a collaboration with other people (see 2.7).
2. **One page per piece, in design-doc form**: problem, constraints, rejected
   options, what you built, one measurable result, one thing that went wrong.
   The "went wrong" line is what makes it credible.
3. **Show process, including AI use.** Hiring managers in 2026 are described (in
   blogs) as skeptical of repos that look prompted into existence and as wanting
   you to defend each decision. Your fauxx work has an `AIUSE.md`; do the same
   on your repos: what you wrote, what an agent wrote, what you rejected. Present
   `build-loop` and `test-quality` as a method in one paragraph, not a toolbox.
4. **Lead with outcomes a non-Nix reader can follow.** "Reproducible builds
   across three machines, removing a class of deploy failure" beats "flake with
   55 modules". No number? Give a before/after.
5. **Make the entry 90 seconds**: what it is, who it is for, a 30-second demo,
   how to run it. Your `portfolio-strategy.md` already says this; its Ideas Bank
   is still empty.
6. **Match audience.** Nix and Rust fit platform, infra, developer-tools and
   build-system roles. Pragmatic Engineer's coverage suggests specialized
   profiles are in demand relative to generalists (summary of a paywalled piece,
   **C**). Name your target roles and make the three pieces point at them.

**Exercise this week.** Choose the three pieces. Write case study 1 and the AI
paragraph for its README.

**Agents.** Have the agent read the repo and ask the questions a skeptical hiring
manager would; answer in your words. Then ask it to find claims the repo does
not support. Do not have it write the case study.

## 2.4 Résumé

**Core idea.** Read quickly, usually after someone already has a reason to look
(referral, message, good repo). The best-supported principle is specificity:
concrete verbs, scope, numbers, outcome. McKenzie's "describe business results"
applies; Larson's guide on promotion packets is a good template for "what
changed because of me". Your `references-on-resume.md` reached the sensible
conclusion (no references section; separate sheet on request).

**Exercise this week.** Add "so that ___" to every bullet. If you cannot finish
the sentence, replace the bullet. Cut to one page.

**Agents.** Use for keyword checks against a posting and for finding unsupported
claims. Keep a `voice-sample.md` of your own writing; tell the agent to preserve
its rhythm and add no adjectives you did not write.

## 2.5 Interviews

**Behavioural.** Structure stories as Situation, Task, Action, Result: most time
on Action (what *you* decided and did) and a specific result. Employer-designed structured
interviews rank first among the compared selection methods (Sackett et al. 2022: validity
0.42, 80% credibility interval 0.18–0.66). This does not test STAR preparation. Prepare six stories as a practice choice: a conflict, a
mistake, a disagreement with a senior, leading without authority, a trade-off
decision, a project that went wrong. Your 14-month project with late user
discovery is a strong "mistake and what I changed" story. Spolsky's
["Guerrilla Guide to Interviewing"](https://www.joelonsoftware.com/2006/10/25/the-guerrilla-guide-to-interviewing-version-30/)
(2006, updated 2016) shows what interviewers look for: "smart and gets things
done," and being able to say what you personally did on team projects.
*Exercise:* write six one-page STAR stories, 90 seconds spoken, one number each;
record two.

**System design.** Practise a 45-minute design: requirements, scale estimate,
components, trade-offs, failure modes. Kleppmann and Riccomini's *Designing
Data-Intensive Applications*, 2nd ed. (2026) is the standard background. Prep
method evidence: D. *Exercise:* design the APK build queue aloud in 40 minutes,
then have a human poke holes.

**Take-homes and AI** (C/D; 2026 blogs). The common pattern is a short, scoped
take-home followed by a live walkthrough where you explain and extend your code.
Some employers allow AI and ask how you used it; Anthropic's reported default is
no AI in live rounds or take-homes unless told; Google's pilot allows Gemini in a
code-comprehension round and evaluates prompting, verification and debugging.
Ask the recruiter in writing what is allowed, and disclose AI use when it is.
*Exercise:* do a timed take-home with an agent allowed, then explain every
function aloud without it. Rewrite or learn what you cannot explain.

**Practice.** The observed-vs-private trial (Behroozi et al., FSE 2020, 48
computer-science students) found less than half the performance under observation. A field experiment (Jabarian and
Henkel, CESifo WP 12984; 70,884 customer-service applications) found AI-led
first-round interviews gave about 12% more offers than
human-led ones in one firm. The exact 70,884 sample and 18% starts figure
were not independently recovered from the full paper [unverified]; the
accessible abstract says 70,000 applicants. Treat automated-screen preparation
as a proposal, not a forecast from this experiment.

**Agents.** Use an agent as interviewer only: it asks, waits, scores against a
rubric you wrote, and shows no model answer until you have given yours. After
each mock, write two lines in your own words on what to change. Your
`interview-practice` records have scaffolding; the missing step, as far as I
could tell, is doing it aloud with a human weekly.

## 2.6 Negotiation and evaluating offers

**Core idea.** McKenzie's ["Salary Negotiation"](https://www.kalzumeus.com/2012/01/23/salary-negotiation/)
(2012-01-23) is still the clearest guide. Verified rules: negotiate only after a
"Yes-If"; negotiate every offer; the person across is spending a budget, not
their own money; never give a number first; deflect salary-history questions;
trade information in pieces; offer to table salary and trade on vacation, hours
or development; use email for time and a written trail; repeat their words back.
Grade D, with a huge reception and no better alternative found.

Evaluating offers: look past total compensation to manager quality, what you
will learn, who reviews your work, and how long the team has stayed together.
Ask how disagreement is handled in design review, what a good first six months
looks like, and who left in the last year. Your job-seeking repo's
negotiation notes (about 6,300 words) already cover this; use them as reference,
not more reading.

**Exercise this week.** Write and say aloud a reply to "What are your salary
expectations?" that names no number, plus an email for "I'm excited; can we
discuss the base number?"

**Agents.** Role-play the recruiter with hardball variants. Do not ask an agent
for your number; use real data you can cite.

## 2.7 Networking without hating it

**Core idea.** Moderately weak ties help most (Rajkumar et al.), referrals
dominate in 2026 reports, and referrals carry weight when the referrer can say
something specific about you. Be useful where the people you want to work with
already are (open-source threads, public RFCs), then ask people you have really
exchanged with for 20 minutes about their work, not for a job.

Your clearest asset: git author names in your clones suggest roughly 400 of
about 1,800 commits in `edge` and 43 in `fauxx` are yours, among other
contributors. If accurate, maintainers who reviewed your work can speak
specifically, which beats any cold message. I cannot tell from the repos who
they are or whether they would act as references; ask them.

**Sources.** Rajkumar et al., Science 2022; Larson, "Build a network of peers"
and "Being visible" ([staffeng.com](https://staffeng.com/guides/)); Reilly,
["Being Glue"](https://noidea.dog/glue) (2018 talk; page not retrieved).

**Exercise this week.** List 15 people you have had a real technical exchange
with. Message three, asking for 20 minutes on how their team works. No job ask.

**Agents.** Research the person's public work and suggest a specific question;
write the message yourself.

## 2.8 Using agents without losing your voice

Doshi and Hauser (2024) found AI help raised individual writing quality and
reduced the diversity of the group's output; Galdin and Silbert show what
happens to a signal when everyone can produce it cheaply. Rule: **agents
critique and question; you write.** Practices (D):

- Keep `voice-sample.md`: five pieces you are proud of. Paste it into editing
  requests with "preserve this voice; propose edits as a diff; no new content".
- Write the first draft yourself; ask the agent for the reader's reaction, the
  missing step, or the strongest objection.
- Never let an agent decide what happened in your own history; it rounds
  stories up.
- Run `unslop` and `plain-writing` last, as filters.
- For interviews, agent output you cannot reproduce aloud is a liability;
  interviewers are reported to watch for conversational lag (Pragmatic
  Engineer, July 2026).

---

# Where you likely are

Inference from what was readable, offered tentatively. Correct it where wrong.

- **You build a lot, carefully, with a visible method.** `phoe-nix` has about
  360 commits since March 2026 and about 55 scout modules; your skills encode a
  review discipline many engineers lack. This is real capability.
- **Some of your best evidence is collaborative.** The author counts suggest
  you worked inside other people's projects with outside reviewers: the thing a
  solo repo cannot show and employers say they cannot see.
- **You may be putting systems before conversations.** The job-seeking repo
  holds an agent pipeline with application submission, about 21 application
  files, 87 company files, and about 33,000 words of research notes. In a quick
  search I found no recorded outcomes (interviews, replies), and the portfolio
  file's Ideas Bank and release schedule are still placeholders. If that holds,
  section 2.2 suggests moving effort from building the machine to a fixed weekly
  block of conversations, human mock interviews and one shipped write-up.
- **Some of your hardest lessons were about communication structure.** Your
  notes describe a long project where key user needs surfaced late, UX concerns
  raised in meetings went unheeded, and you were early in your career with
  impostor feelings. To me that reads as a team with no written user stories and
  no place for concerns, not a personal failing. It makes "write the decision and
  the risk where others can see it" your highest-value habit and your best
  interview story.
- **A gap may need explanation.** The 2013 callback experiment does not predict
  your individual callback trajectory in 2026. Dated public work and named
  collaborators are plausible evidence to show, with no measured offset to
  unemployment-duration effects established here.
- **You already have plenty to read.** Negotiation, résumé and portfolio
  notes exist in depth. The bottleneck looks like practice with other people.

---

# Candidate actions (ranked by expected value over cost)

All action frequencies and doses below are planning choices, grade D.

1. **Weekly human mock interview or talk-through**, starting this week. The
   stress experiment supports the relevance of observation, not this treatment.
   Practice-effect evidence is vendor observation, C; the weekly dose is D.
2. **Three one-page case studies** with a "what went wrong" line and an AI-use
   paragraph per repo. Cheap, verifiable, doubles as interview material.
3. **Fixed outreach: three real messages a week** to people you have exchanged
   work with, maintainers first. Weak ties (A/B), referrals (B).
4. **Ask the `edge` and `fauxx` maintainers if they would speak for you.** Fast;
   uses your strongest asset.
5. **Start the brag document today** from git history; update biweekly.
6. **Six STAR stories; record two.** A preparation proposal, D. Structured
   interview validity does not validate this format or dose.
7. **Cut application volume; target 10–15 named companies** where you can reach a
   person. Hiring-manager reports (C) and the proposal-signal study (A/B).
8. **Write RFC-style notes for your next real change**, and publish one. Grade
   C/D, compounding.
9. **Practise take-homes with AI allowed and disallowed**, always able to explain
   every line aloud.
10. **Defer** management-focused reading (Drasner) and further job-search tooling.

---

# 12-week study plan

About 6–8 hours a week. Each week has one reading, one writing deliverable and
one practice-with-a-human item. Every deliverable doubles as job-search material.

| Wk | Theme | Read | Write | Practise with a human |
|---|---|---|---|---|
| 1 | Baseline | Evans: brag docs, good questions | Brag doc (12 months); pick 3 portfolio pieces; list 15 contacts | Mock behavioural #1; 3 outreach messages |
| 2 | Busy readers | Nielsen and Morkes; Amazon 2017 letter | Rewrite 3 messages "ask first"; case study 1 | Mock #2; read case study aloud |
| 3 | Design docs | Ubl; Oxide RFD 1 + two RFDs | Retrospective design doc | Engineer critiques it; 3 outreach |
| 4 | Strategy | Larson, engineering strategy; Bezos 2016 | Diagnosis/policies/actions page for one system; case study 2 | Mock system design |
| 5 | Pushback | Radical Candor ch. 1–2; Crucial Conversations (part 1); Edmondson abstract | Scripts for 3 situations | Role-play all 3; 3 outreach |
| 6 | Review and asking | Google eng-practices; Sadowski (skim) | Review 3 OSS PRs with labels; one good question | Pair-review, ask for tone feedback |
| 7 | Résumé and stories | Reilly ch. 1, 3; Larson, promotion packets | "So that" résumé; six STAR stories | Recorded mock behavioural; engineer reads résumé |
| 8 | System design | DDIA 2e ch. 1–2 (plus role-relevant chapters) | Written design of your build queue; case study 3 | Two mock designs |
| 9 | AI-era interviews | Employer instructions; Galdin and Silbert (Tuck summary) | Take-home with and without AI, "how I used AI" note | Explain your code aloud; they ask "why" |
| 10 | Negotiation | McKenzie, both essays | Email scripts: expectations, counter, delay; offer sheet | Recruiter role-play with pushback |
| 11 | Visibility | Rajkumar abstract; Larson, Being visible; Reilly, Being Glue | Publish one write-up; update brag doc | Two coffee chats; written follow-up |
| 12 | Review | Your week-1 baseline | Retrospective, next 12 weeks, revised voice sample | Full mock loop (behavioural, design, take-home walkthrough) |

**Two rules.** (1) Do the human practice even when it is awkward; the research
says the awkwardness is the point. (2) Agents may critique, role-play, search
and mine your history. They may not draft anything with your name on it. When
you want a draft, write a bad one and ask what is missing.

---

# Sources

Fetched or searched 2026-11-10 unless stated. "Search summary" means I saw the
claim only in a summary of the primary source.

**Market and hiring**
- Orosz and Salmon, "State of the job market 2026," Pragmatic Engineer, 2026-05-26: https://newsletter.pragmaticengineer.com/p/state-of-the-job-market-2026
- Orosz, "Tech jobs market 2026, part 3: hiring," 2026-07-07 (partly paywalled): https://newsletter.pragmaticengineer.com/p/tech-jobs-market-in-2026-part-3-hiring
- Zimermanova, "Is AI really reshaping the developer market?", Stack Overflow Blog, 2026-10-22: https://stackoverflow.blog/2026/10/22/is-ai-really-reshaping-the-developer-market/
- LinkedIn Economic Graph, US software engineer talent landscape 2026, PDF checked in cross-review: https://economicgraph.linkedin.com/content/dam/me/economicgraph/en-us/PDF/us-software-engineer-talent-landscape-2026.pdf
- Kroft, Lange, Notowidigdo, QJE 2013, [primary paper](https://users.nber.org/~notom/research/Kroft_Lange_Noto_Resume_Study.pdf); the 45% figure was located in its indexed text. [Experiment-team summary](https://www.povertyactionlab.org/print/pdf/node/2091) confirms 12,054 resumes and 3,040 openings.
- Brown, Setren, Topa, NY Fed Staff Report 568: https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr568.html
- Rajkumar et al., Science, 2022-09-16: https://pubmed.ncbi.nlm.nih.gov/36107999/
- Galdin and Silbert, arXiv 2511.08785, Nov 2025: https://arxiv.org/abs/2511.08785 ; Tuck summary, 2026-01-05: https://tuck.dartmouth.edu/news/articles/what-happens-to-hiring-when-ai-writes-job-applications
- Marlow, Dabbish, Herbsleb, CSCW 2013: https://xia.cs.cmu.edu/resources/Documents/marlow-cscw13.pdf
- Luu, "Hiring and the market for lemons" (undated, c. 2016): https://danluu.com/hiring-lemons/

**Interviews**
- Sackett et al., J. Applied Psychology 2022, [primary paper checked in cross-review](https://gwern.net/doc/statistics/meta-analysis/2021-sackett.pdf); 2023 reply: https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/A20984B138319E3D432E643978BF026D/S175494262300024Xa.pdf/revisiting-the-design-of-selection-systems-in-light-of-new-findings-regarding-the-validity-of-widely-used-predictors.pdf
- Behroozi et al., ESEC/FSE 2020: https://2020.esec-fse.org/details/fse-2020-papers/140/Does-Stress-Impact-Technical-Interview-Performance-
- Jabarian and Henkel, CESifo WP 12984: https://econpapers.repec.org/RePEc:ces:ceswps:_12984
- interviewing.io practice claim, vendor observation with no causal design exposed, located in the [hiring-process guide](https://interviewing.io/guides/hiring-process), accessed 2026-11-10. The original exact blog link remains unverified.
- Spolsky, Guerrilla Guide to Interviewing 3.0, 2006-10-25 (updated 2016-12-05): https://www.joelonsoftware.com/2006/10/25/the-guerrilla-guide-to-interviewing-version-30/
- Google AI-assisted interviews via Yahoo Finance/Business Insider, 2026-05 (original not retrieved): https://finance.yahoo.com/sectors/technology/articles/asking-kid-math-test-without-151500986.html
- Take-home and AI-round roundups (blogs, C/D): https://www.techinterview.org/post/3233475330/ai-era-take-home-assignments-2026-how-they-changed/ ; https://www.greatfrontend.com/blog/ai-assisted-coding-interviews-for-frontend-developers
- In-person interview return (press): https://www.entrepreneur.com/business-news/google-mckinsey-reintroduce-in-person-interviews-due-to-ai/496041
- Kleppmann and Riccomini, DDIA 2e, 2026: https://martin.kleppmann.com/2026/03/24/designing-data-intensive-applications-2e.html

**Communication**
- Ubl, "Design Docs at Google," 2020-07-06: https://www.industrialempathy.com/posts/design-docs-at-google/
- Oxide RFD 1, 2020-07-24: https://oxide.computer/blog/rfd-1-requests-for-discussion ; index: https://rfd.shared.oxide.computer/
- Bezos letters: 2017 https://www.aboutamazon.com/news/company-news/2017-letter-to-shareholders ; 2016 https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders
- Larson, "Writing engineering strategy," 2023-02-13: https://lethain.com/eng-strategies/ ; Staff Engineer guides: https://staffeng.com/guides/
- Reilly, *The Staff Engineer's Path* (2022; Part I only confirmed): https://www.oreilly.com/library/view/the-staff-engineers/9781098118723/ ; "Being Glue" notes: https://pelayoarbues.github.io/literature-notes/Articles/Being-Glue-talk
- Fournier, *The Manager's Path* (2017; partial TOC): https://www.oreilly.com/library/view/the-managers-path/9781491973882/
- Orosz, *The Software Engineer's Guidebook* (2023; job-search content unconfirmed): https://www.oreilly.com/library/view/-/9789083381831/
- McKenzie, "Don't Call Yourself a Programmer," 2011-10-28: https://www.kalzumeus.com/2011/10/28/dont-call-yourself-a-programmer/ ; "Salary Negotiation," 2012-01-23: https://www.kalzumeus.com/2012/01/23/salary-negotiation/
- Evans, "How to ask good questions," 2016-12-31: https://jvns.ca/blog/good-questions/ ; "Write a brag document," 2019-06-28: https://jvns.ca/blog/brag-documents/
- Google eng-practices: https://github.com/google/eng-practices/blob/master/review/reviewer/comments.md
- Sadowski et al., ICSE-SEIP 2018: https://research.google/pubs/modern-code-review-a-case-study-at-google/
- Nielsen and Morkes, 1997, primary page checked in cross-review: https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/
- Scott, *Radical Candor* (summary): https://gsb.stanford.edu/insights/radical-candor-communication-shift-can-transform-your-career
- *Crucial Conversations* vendor research (VitalSmarts): https://www.thecampbellinstitute.org/wp-content/uploads/2017/07/Grenny-Maxfield_0811Z.pdf
- Edmondson, ASQ 44(2), 1999 (secondary): https://yukaichou.com/gamification-analysis/psychological-safety-edmondson-team-learning/
- Majors, "The Engineer/Manager Pendulum," 2017-05-11 (not opened; read when choosing IC vs management): https://charity.wtf/2017/05/11/the-engineer-manager-pendulum/
- Doshi and Hauser, Science Advances, 2024-07-12: https://pmc.ncbi.nlm.nih.gov/articles/PMC11244532

**Local files read**: `AGENTS.md`; `knowledge/resume-tool-additions.md`;
`~/Documents/repos/job-seeking/` (research notes, record counts);
`~/Documents/repos/*` READMEs and `git shortlog` author counts.

**Not verified**: Fournier chapters beyond ch. 1; Reilly chapters beyond Part I
(ch. 2 title "Three Maps" and ch. 3 confirmed); Drasner's contents; Bryar and
Carr (book not read); Spolsky/Luu beyond the pages cited; any "search summary"
figure.
