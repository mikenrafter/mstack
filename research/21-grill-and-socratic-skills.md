# 21. Grill, Socratic and sparring-partner skills compared

Written 2026-11-19. You asked how to make `question-everything` an active
sparring partner, one that holds and defends its own positions, instead of a
rubber duck that only asks. This file compares eleven public skills and
prompts that do a similar job, your own earlier "Socratic" wording, and the
research on sycophancy (a model agreeing with you because you said it) and
on its opposite, stubbornness. Nothing was posted or opened anywhere. The
void host is offline, so its transcripts are missing from the search in §1.

## Top findings

1. **Almost every interview prompt keeps the model in the asker's seat.**
   Harper Reed's prompt, Anthropic's "interview me" guidance, Thariq's
   AskUserQuestion prompt and spec-kit `/clarify` tell the model to ask and
   never to hold a view of the whole design. A per-question recommended
   answer (Pocock, spec-kit, yours) commits the model only on small
   questions. Grade D (prompt text read directly).
2. **Only two sources tell the model to argue.** pstack's poteto-mode says
   "No is an acceptable answer… Agreement is not the default, candor over
   sycophancy." BMAD says "Push back on thin answers, harder at higher
   stakes, hardest on unexamined assumptions". Your skill pushes back only on
   answers that leave something undefined, which checks completeness, not
   whether the answer is right. Grade D.
3. **Proposal-first designs are the most forthcoming without becoming
   stubborn.** superpowers v7 ("A proposal they can correct, plus your reason
   for it, often beats a question"), Kiro and HumanLayer write a draft before
   asking. superpowers is the only interview skill with numbers: in
   blind-graded runs the reason behind the request came out before any
   approach in 33 of 33 conversations, against 19 of 33 for v6.4.2. Grade C
   (internal eval; the harness is not published).
4. **Only a critic that argues live helped in a controlled study.** Of four
   LLM devil's-advocate designs, only the interactive one arguing against the
   AI's recommendation raised group accuracy (β = 0.135, p = 0.047; 350
   people, GPT-3.5, now obsolete). A one-off list of critiques did not.
   Grade A, small effect.
5. **Models cave most when you push back, and most of all when the pushback
   cites sources.** Sycophancy in Claude guidance chats doubled when the user
   pushed back (18% against 9%; Anthropic, ~38k conversations, Grade B).
   Citation-backed rebuttals caused the most flips to wrong answers, and a
   model that caved kept the caved answer 78.5% of the time (SycEval, Grade A,
   GPT-4o, Claude Sonnet and Gemini 1.5).
6. **Telling a model to disagree more makes it reject correct input.** Models
   trained against sycophancy accepted only 27.4–46.7% of valid user
   corrections (SMART, EMNLP 2025, Grade A, LLaMA2-era models). A 2026 paper
   finds that bad caving and good updating share the same internal machinery,
   so suppressing one hurts the other. The fix is a rule for *when* to change
   position (new information, yes; pressure, no), not a louder "push back".
   Grade A (abstracts only).
7. **Your "Socratic" never meant Socrates.** Your 2026-10-27 instruction was
   "ask what their first and second order desires for having the feature are
   so that you can debate it Socratically, arrive at a better solution". That
   is debate. Classical Socratic method is the opposite stance: Socrates
   claimed to know nothing and only asked. residual's skills use "Socratic" to
   mean "read freely, write only with approval", a permission rule. The word
   carries three meanings in your setup, and only one of them is the one you
   want. Grade D.
8. **A pure question-asker gets abandoned.** In a randomised trial in 18
   Tennessee middle schools, students mostly declined Khanmigo's
   question-only help ("most students declined it most of the time"). That is
   a different population, but it is the only outcome data on a
   question-only partner. Grade A via a press summary (the NBER paper was not
   read).

## 1. Your earlier Socratic version

Searched case-insensitively for "socratic" in `~/.claude/projects/*/*.jsonl`
(30 files), `~/.codex/sessions` (about 30 files), the repo `skills/`
directories, `phoe-nix`, `residual-cli/src/skills` and the `*.research`
directories. Only messages you typed are quoted; skill text injected into
sessions is excluded.

What you wrote:

- **2026-10-27, edge session `1459dd51`** (the origin): "When discussing
  features with the user, always ask whether there's a simple alternative to
  what the user is requesting. ask what their first and second order desires
  for having the feature are so that you can debate it Socratically, arrive at
  a better solution before any engineering efforts spent." The same message
  says: "be courteous with the user, but when they ask you to be bold, be very
  bold, and even when they don't ask, be bold." Earlier that day: "Socratically,
  question me to find out how to disambiguate these things."
- That became build-loop step 3 in phoe-nix commit `d85c6c46` (2026-10-27):
  "**Debate Socratically.** Question assumptions, offer counter-cases and
  cheaper options, until you reach a better solution than the first draft."
  The mstack copy (`skills/build-loop/references/front.md` §1) has since lost
  "until you reach a better solution than the first draft".
- **2026-11-07, phoe-nix `d87e4d7f`**, praise: "I like how you've asked me,
  Socratically, whether my intent behind the fix is solved by something else
  simpler, I would like to keep that moving forward".
- **2026-10-22, edge `99ded3ee`**: "let's go over these things in detail,
  come up with a plan and get some initial mock-ups ready. Let's get this done
  socratically."
- **2026-11-05, edge `883e50fb`**: "let's socratically arrive at a style of
  text and connection methodology that systematically prevents this issue".
- **2026-11-12, phoe-nix `4040da30`**: product and architecture review "end
  up as a Socratic discussion at the beginning, interplaying with residual".
- **2026-11-15, edge `50e1af19`**: "Give me some mock-ups of these things.
  Ask me follow-up questions. Don't dig too deep into these things. Propose
  alternatives. Let's be a little Socratic here".
- **2026-11-16, Codex `rollout-2026-11-16T00-54-23`**, on orchestrator and
  implementer exchanges: you contrasted "taking the implemented biases" with
  the "socratic and thoughtful and planning-based approach", and wanted the
  orchestrator to ask "two to three questions" and then push back "and
  settle the ambiguity".

What you disliked: no transcript on this host complains about a passive
grill in so many words. Searches for "rubber duck", "backseat",
"forthcoming", "sparring", "devil's advocate", "steelman" and "too many
questions" found nothing you wrote on the subject. The complaint lives in
this task's framing (2026-11-19): you want "an active sparring partner with
its own positions, not a backseat rubber duck that only asks". The
transcripts point the same way. Every time you said "Socratic" you also asked
for proposals, alternatives, mock-ups or debate, and you often ask "what do
you think?" (edge, 2026-11-15 and 2026-11-18).

residual-cli's skills (`src/skills/definitions/*/SKILL.md`, last change
`32c0836`, 2026-09-28) open every lens with "This skill is Socratic.",
defined as "**Gather freely**… **Act only with approval**". That is a
permission split, not a stance. One line does build in a critic:
`purpose_walk` says "Push back until vagueness is resolved… Demand
specifics" and "Every 3 turns, step into a critic role and adversarially
challenge all stated purposes for hidden assumptions, missing actors, or
unmeasurable outcomes." The residual README calls the agent "a Socratic
partner".

## 2. What "Socratic" means in the literature

The Stanford Encyclopedia entry on Socrates (revised 2022-05-26) describes
Socratic irony as "saying that he knew nothing of importance" while keeping
"the upper hand in every discussion", and his method as midwifery: drawing
the answer out of the other person. In the elenchus (Vlastos's term for the
refutation), Socrates gets the other person to agree to premises and then
shows that the premises contradict their claim. He never states a thesis of
his own. That is the rubber-duck stance. The entry also notes that modern
classroom "Socratic" questioning "implies no effort... to sting like a gadfly
or to expose a disquieting truth". The gadfly, who stings and exposes, is the
half you want.

Advait Sarkar (Microsoft Research, CACM, October 2024) argues for the
gadfly: "Let's transform our robot secretaries into Socratic gadflies." His
"AI as provocateur" "engages in discussions, offers counterarguments, and
asks questions". Grade D (essay). Irving, Christiano and Amodei's "AI safety
via debate" (2018) is the formal version: two agents argue opposite sides and
a judge decides. In their MNIST toy, a judge that saw only 6 pixels rose from
59.4% to 88.9% accuracy with debaters revealing them. Grade A for the toy.

**Use:** when a skill says "Socratic", it should say which half it means. For
you it is "state a position, then test both yours and theirs".

## 3. The skills and prompts compared

Read at these commits: mattpocock/skills `5863806`, cursor/plugins `35a9094`,
obra/superpowers `22f0b46`, humanlayer/humanlayer `2f5b58d`, github/spec-kit
`617e9a0`, BMAD-METHOD `e435a22`. Star counts are from 2026-11-19.

### 3.1 Summary table

| Source | Asks | Own position? | Told to push back? | Ends when | Artifact |
|---|---|---|---|---|---|
| Pocock `grilling` | Whole frontier per round (was one at a time until 2026-07-31) | Recommended answer per question | No (only `domain-modeling`: contradictions with code or glossary) | Frontier empty, user confirms | None; `grill-with-docs` adds glossary and ADRs |
| pstack poteto-mode | Prototypes instead of asking | Yes, "real judgment" | Yes, "No is an acceptable answer" | User says go | Multi-phase plan |
| superpowers `brainstorming` v7 | One at a time; playback alternates with questions | Yes, "your call and your reason as a proposal" | Soft: "say so plainly" | User approves doc (hard gate) | Design doc, builder check |
| HumanLayer `create-design-discussion` | Draft first, open questions in doc | Recommends, may not resolve | Old `create_plan`: "Be Skeptical" | User resolves every question | Design-discussion doc |
| spec-kit `/clarify` | Exactly one at a time, max 5 | `**Recommended:** Option X` | No | 5 questions, or "done" | Clarifications section in spec |
| BMAD facilitate (Mary, John) | Brain dump, then one at a time; fast path drafts | Recommends between named options only | Yes, scaled by stakes | Remaining questions would not change the doc | Brief or PRD, assumptions log |
| Kiro spec mode | Draft requirements first, then iterate | Implicit in the draft | Only via "Analyze Requirements" | User confirms each phase | requirements, design, tasks |
| Anthropic feature-dev | One batch of questions | Recommendation when asked, and per architecture | No | User approves | Architecture choice |
| oh-my-claudecode deep-interview | One at a time, ambiguity score | Recommended answer | Scheduled modes: contrarian at round 4 | Ambiguity ≤ 0.2 or 20 rounds | Spec file |
| Harper Reed idea-honing | One at a time | No | No | User says so | Spec via a second prompt |
| Anthropic / Thariq "interview me" | Many, via AskUserQuestion | No | No | "until it's complete" | SPEC.md |
| `question-everything` (yours) | Frontier rounds, "one at a time" on request | Recommended answer per question | Only on undefined states, edges, failures | Open list empty or user says so | Intent, glossary, ADRs, spec, stack plan |

### 3.2 Pocock, `grilling` (2026-10-29), `grill-me`, `grill-with-docs` (2026-08-15)

https://github.com/mattpocock/skills/blob/5863806/skills/productivity/grilling/SKILL.md

- Stance: "Interview the user relentlessly until you reach a shared
  understanding. Map this as a **design tree**".
- Position: "number each question and give your recommended answer";
  "Word each question so "yes" accepts your recommended answer."
- Cadence: "Ask the whole frontier in one round". Commit `a4b2009`
  (2026-07-31) replaced "Ask the questions one at a time… Asking multiple
  questions at once is bewildering."
- Facts and decisions: "Finding _facts_ is your job, never the user's…
  dispatch a sub-agent with a fresh context window… The _decisions_ are the
  user's".
- Push-back lives in `domain-modeling`: "When the user states how something
  works, check whether the code agrees. If you find a contradiction, surface
  it".
- End: "Do not act on it until the user confirms you have reached a shared
  understanding."
- Evidence: the docs claim "Thirteen questions typically land in about three
  rounds rather than thirteen", with no data. Grade D. Report 17 covers how
  it behaved in his video.

The model is forthcoming only one question at a time. It never says "I would
build this differently". In report 17's video run, "yes, yes, yes" could mean
agreement or fatigue.

### 3.3 pstack poteto-mode, `sharpen`, guide (2026-11-15/16)

https://github.com/cursor/plugins/tree/35a9094/harness/pstack

- "**No is an acceptable answer.** Asked whether to do something, invited to
  add scope, or shown an approach, reply with your real judgment. Decline,
  push back, or say "this doesn't earn its place" when true. A recommendation
  is a judgment, not a validation. Agreement is not the default, candor over
  sycophancy."
- "pstack has no planning skill, on purpose." "A fork you could settle by
  running something → prototype it… instead of asking." `sharpen`: "Leave
  product or preference choices that no experiment can settle for me to
  make."
- "Don't ask "should I do X?" Do X, explain why."
- Evidence: Grade D.

This is the strongest stance text in the survey. It also draws the line the
research supports: facts get settled by experiment, preferences go to the
human.

### 3.4 superpowers `brainstorming` v7.0.2 (2026-11-03), `writing-plans` (2026-09-25)

https://github.com/obra/superpowers/blob/22f0b46/skills/brainstorming/SKILL.md

- Stance: "You build what you believe your human partner wants, and that
  belief is usually thinner than it feels."
- "Ask Socratically, the way a sharp colleague would: build each question on
  their last answer or on something you found, so it helps them think through
  a consequence or a case they may have missed".
- Position: "state your call and your reason as a proposal they can correct";
  "A proposal they can correct, plus your reason for it, often beats a
  question." On approaches, sketch "two or three… Recommend one and say why".
- Ownership: "Any choice you make goes in the design as your call, never as
  something they agreed to."
- Playback: "Play back as you go… describe that part back in about 200-300
  words, then return to questions about the next part. Playback and questions
  alternate… Only what they said goes in as theirs. Anything you filled in
  goes in as your proposal, with your reason. End each chunk by asking what's
  wrong or missing."
- Push-back is soft: if you found "a constraint, a conflict, or a cheaper
  path, say so plainly."
- End: a `<HARD-GATE>`, "Nothing gets built until your human partner approves
  the design doc". A fresh subagent then reads the doc as the builder would,
  and only questions only the human can answer go back, in one round.
- Evidence: release notes for v7.0.2 report blind-graded runs. Filler
  questions fell from 41 to 23. The reason behind the request came out before
  any approach in 33 of 33 conversations, against 28 of 33 for v7.0.1 and 19
  of 33 for v6.4.2. Grade C. The eval harness is not in the repo.

This is the closest public design to what you asked for. Two of its moves
are missing from `question-everything`: the "theirs versus my call" marking,
and playback that alternates with questions.

### 3.5 HumanLayer: old `create_plan` (2025-11-12), `create-design-discussion` (2026-10-22)

https://github.com/humanlayer/humanlayer (the riptide-rpi plugin; old
`.claude/commands/create_plan.md` at blob `77c7fe9`)

- Old: "You should be skeptical, thorough, and work collaboratively"; "**Be
  Skeptical**: Question vague requirements… Ask "why" and "what about"";
  "**Be Interactive**: Don't write the full plan in one shot." When corrected:
  "DO NOT just accept the correction… Only proceed once you've verified the
  facts yourself."
- New: "For each major design choice, present options with pros/cons. Make
  recommendations based on codebase conventions." "You may recommend an
  option, but you must NOT resolve or close a question yourself."
- Research is kept blind to the ticket so it stays factual: questions must
  "NEVER [be] NORMATIVE".
- Evidence: Grade D.

"Don't just accept the correction" is the only rule in the survey about
*user* pushback. It applies to facts: check the code before conceding.

### 3.6 spec-kit `/clarify` (2026-09-15) and `/specify` (2026-10-29)

https://github.com/github/spec-kit/blob/617e9a0/templates/commands/clarify.md

- "Maximum of 5 total questions across the whole session"; "Present EXACTLY
  ONE question at a time"; ranked by "(Impact * Uncertainty)".
- "`**Recommended:** Option [X] - <reasoning>`"; the user may answer "yes".
- Each answer is written into the spec at once; the model must "leave no
  obsolete contradictory text".
- `/specify`: "Make informed guesses… LIMIT: Maximum 3 [NEEDS
  CLARIFICATION] markers total".
- Evidence: Grade D.

The useful idea: draft with guesses, then ask only about the few guesses that
matter. The cap of 5 is too low for your features.

### 3.7 BMAD analyst (Mary), PM (John), `bmad-facilitate`, advanced elicitation (2026-11-11)

https://github.com/bmad-code-org/BMAD-METHOD/tree/e435a22/skills

- John: "Detective's 'why?' relentless. Direct, data-sharp, cuts through
  fluff."
- Engine: "Coach, do not quiz… Push back on thin answers, harder at higher
  stakes, hardest on unexamined assumptions, less as the document firms up
  or the user tires."
- Consent: "a yes to a group, such as "your recommendations", accepts
  nothing, because they did not weigh each one".
- Fast path: ask up to three things, "Draft the whole document, defaulting
  the rest and logging each default as an assumption", then walk the
  assumptions.
- Elicitation menu (48 methods) includes "Pre-mortem: Assume it failed,
  explain why", "Red Team: Attack it as an adversary would", "Devil's
  Advocate: Press the case against, hardest where the draft is weakest", run
  by fresh "cold reader" subagents; "A finding that rejects the premise of
  the target is shown as a decision for the user."
- Evidence: rubric eval cases are in the repo, but no results are published.
  Grade D.

Two ideas stand out. Push-back scales with stakes and falls off as the user
tires. And a blanket "yes to all" accepts nothing, which goes straight at the
"yes, yes, yes" problem.

### 3.8 Kiro spec mode (docs updated 2026-08-04 to 2026-11-12)

https://kiro.dev/docs/specs/feature-specs/

- "Kiro generates a `requirements.md` document based on your prompt", in
  EARS form ("WHEN [condition/event] THE SYSTEM SHALL [expected behavior]").
  EARS is a fixed sentence pattern for requirements.
- The user iterates and must "Confirm when requirements meet your needs".
- "Analyze Requirements" finds requirements that are "individually sensible
  but collectively impossible", each with "suggested fixes you can select".
- Evidence: Grade D (vendor docs).

Kiro drafts first and critiques second. The model's view is the draft
itself.

### 3.9 Anthropic: feature-dev plugin (2025-11-20), Claude Code docs, constitution

- feature-dev Phase 3: "**Present all questions to the user in a clear,
  organized list**… If the user says "whatever you think is best", provide
  your recommendation and get explicit confirmation." Phase 4: "your
  recommendation with reasoning". Grade D.
  (anthropics/claude-plugins-official, `plugins/feature-dev/commands/feature-dev.md`)
- Claude Code best practices (https://code.claude.com/docs/en/best-practices,
  undated): "Interview me until you could write the spec, then write it to
  SPEC.md." Questions only. Grade D.
- Thariq (Claude Code team), 2025-12-28: "interview me in detail using the
  AskUserQuestionTool about literally anything… continue interviewing me until
  it's complete." [Wording via velvetshark.com, 2026-01-02; not checked
  against the tweet.] That post reports 20–30 questions per interview and a
  32-question run giving a 157-line spec. Grade C.
- Claude's constitution (https://www.anthropic.com/constitution, January 2026
  [exact date unverified]): "Claude should be diplomatically honest rather
  than dishonestly diplomatic." "Epistemic cowardice—giving deliberately vague
  or noncommittal answers to avoid controversy or to placate people—violates
  honesty norms." "Claude can comply with a request while honestly expressing
  disagreement or concerns about it". The model's default already leans
  toward stating disagreement. A skill that only asks suppresses that.

### 3.10 Practitioner prompts

- **Harper Reed** (https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/,
  2025-02-16): "Ask me one question at a time so we can develop a thorough,
  step-by-step spec for this idea. Each question should build on my previous
  answers… Remember, only one question at a time." Critique comes later and
  outside the interview: "asking a reasoning model to poke holes in the idea".
  Run on GPT-4o and o3, both superseded. Grade C (reproducible, no numbers).
- **Addy Osmani `interview-me`**
  (https://tessl.io/registry/skills/github/addyosmani/agent-skills/interview-me,
  date unknown): before each question it states "a best guess and a
  confidence percentage", and it stops when it can "predict the user's
  reaction to the next three questions". [Seen through a registry listing;
  the repo was not read.] Grade D.
- **ctoth's global CLAUDE.md**
  (https://gist.github.com/ctoth/d8e629209ff1d9748185b9830fa4e79f,
  2025-11-30): "Aumann agreement: if you disagree, someone has information the
  other lacks. Share it." "Push back when: Concrete evidence the approach won't
  work / Request contradicts something Q said matters / You see downstream
  effects Q likely hasn't modeled". "State concern concretely / Share what you
  know that Q might not / Propose alternative if you have one / Then defer to
  Q's decision". (Aumann's theorem: two rational people who share the same
  information cannot agree to disagree.) Grade D, but it is the most precise
  rule for when to push back that this survey found.
- **oh-my-claudecode `deep-interview`** (2026-10-30, 40.9k stars): schedules
  stances: "Round 4: CONTRARIAN mode… challenge the user's core assumption.
  Ask "What if the opposite were true?"", then a simplifier at round 6.
  Ambiguity is scored as `1 - (goal × 0.40 + constraints × 0.30 + criteria ×
  0.30)` and the interview stops at 0.2. Its planner requires "the strongest
  steelman antithesis" and a three-scenario pre-mortem. Grade D.
- Complaints that anti-sycophancy rules fade after a turn or two of
  conversation exist in Claude Code issues (#37254, #44803) [unverified; the
  mirror did not load]. The Register covered "You're absolutely right"
  appearing "about everything" (2025-08-13). Grade C.

## 4. Research on sycophancy and stubbornness

| Study | Finding | Grade, caveat |
|---|---|---|
| Sharma et al. 2023, arXiv 2310.13548 | When asked "Are you sure?", models wrongly admitted mistakes on 42% (GPT-4) to 98% (Claude 1.3) of questions | A; all five models obsolete |
| Laban et al. 2023, FlipFlop, arXiv 2311.08596 | 10 models flipped 46% of the time on a challenge; accuracy fell 17% | A; mostly obsolete |
| Fanous et al. 2025, SycEval, arXiv 2502.08177 | 58.19% sycophancy. Citation-backed rebuttals caused the most flips to wrong answers; a caved model kept the caved answer 78.5% of the time | A; GPT-4o, Claude Sonnet, Gemini 1.5 |
| Hong et al. 2025, SYCON-Bench, arXiv 2505.23840 | Measures turns until a flip in multi-turn debate. "You are an independent thinker who values honesty and critical reasoning" and a third-person persona ("You are Andrew…") help; the headline "up to 63.8%" [unverified against Table 4] | A for the benchmark, weak for the prompts; the pushback turns carry no arguments, so holding firm always scores well |
| Cheng et al. 2025, ELEPHANT, arXiv 2505.13995 | Models protect the user's self-image 45 points more than humans do; shown both sides of a conflict, they "affirm both sides" in 48% of cases | A |
| SMART, arXiv 2509.16742 | Anti-sycophancy fine-tuning made models accept only 27.4–46.7% of valid inputs | A; LLaMA2-era |
| Ma et al. 2026, arXiv 2608.26511 | Caving without support and updating on evidence share an internal substrate; suppressing one impairs the other | A; abstract only |
| He et al. 2026, arXiv 2610.04329 | Attention steering cut caving to pressure by 18.8 points and raised updating on evidence by 5.5 points against the best baseline | A; abstract only, not usable by prompt |
| Anthropic 2025-12-18, well-being post | Opus 4.5 corrected an earlier sycophantic turn only 10% of the time (Haiku 4.5: 37%); harder pushback "can sometimes feel excessive to the user" | A/B, internal |
| Anthropic 2026-04-30, personal guidance | 9% sycophancy overall, 18% when the user pushed back | B, ~38k conversations |
| Chiang et al. IUI 2024 | Only the interactive devil's advocate arguing against the AI improved accuracy | A, GPT-3.5, modest |
| OpenAI 2025-04-29 and 2025-05-02 postmortems | A thumbs-up reward signal and memory pushed GPT-4o toward flattery. The patch prompt was "Be direct; avoid ungrounded or sycophantic flattery." | C |
| OpenAI Model Spec 2025-12-18 | "should not change its stance solely to agree with the user"; "a firm sounding board… rather than a sponge that doles out praise" | D |

What follows for a grill:

1. **The risky moment is your second message on a topic, not the first
   question.** Caving doubles under pushback. Your pushback in a grill tends
   to cite the code or a past decision, which SycEval found to be the most
   persuasive kind, right or wrong.
2. **The rule has to separate information from pressure.** A blanket "push
   back harder" trades sycophancy for stubbornness (SMART, Ma). ctoth's
   Aumann rule and the Model Spec's "not… solely to agree" both say the same
   thing. Change position when the other person brings information you
   lacked, and say which piece moved you.
3. **Facts and preferences need different rules.** On facts, both sides can
   check (HumanLayer: "Don't assume - verify with code"). On taste, scope and
   risk appetite, the owner decides, and arguing a second time is noise
   (pstack, BMAD "less as… the user tires").
4. **Interactive critique beats a list.** A pre-mortem pasted at the end is
   the static devil's advocate that did nothing in Chiang's study.
   Objections need to come up during the grill, where you can answer them.
5. **Prompt-only persona tricks are weakly measured.** "Independent thinker"
   framing has the only measured wording, and its effects in SYCON-Bench are
   small and uneven. Structure (when to state a position, what to record)
   likely matters more than tone, though nobody has measured that directly
   [inference].

## 5. Design options for `question-everything`

Ranked by expected value for cost. Each has proposed wording in the skill's
voice and a control-flow sketch.

### Option A. Open with a position (propose first)

Before round 1, after reading the code, the model sends one message with its
understanding, the design it would build, the strongest objection to that
design and to the request, and the simplest alternative. Questions then
follow from that proposal. This brings back what your 2026-10-27 instruction
asked for ("simple alternative… first and second order desires… debate"),
which build-loop front §1 now treats as a separate step most grills skip.

Sources: superpowers ("A proposal… often beats a question"), Kiro and
HumanLayer (draft first), BMAD fast path, pstack ("Do X, explain why").
Evidence: C (superpowers numbers) plus A for live critique (Chiang).

```
read code (facts) ─► POSITION message ─► owner reacts ─► round 1 (frontier,
  intent / my design /                    (may reject        each Q with
  strongest objection /                    the whole          recommendation)
  simpler alternative                      design here)
```

Risk: the draft anchors the owner. Mitigation: always pair it with the
strongest objection and the simpler alternative, and ask for the
second-order desire before the owner answers detail questions.

### Option B. Disagree with evidence, update on information only

When an answer conflicts with the code, a doc, the glossary, an ADR or an
earlier answer, the model says so once, with the evidence and its
recommendation. It changes position only for new information or a stated
preference, and it says which one moved it. If the owner holds their answer,
the model records the owner's decision with its objection beside it. This is
the guard against both failure modes in §4.

Sources: ctoth (Aumann), HumanLayer ("DO NOT just accept the correction"),
Pocock `domain-modeling` (surface contradictions), OpenAI Model Spec,
SycEval and Anthropic data on caving under pushback. Evidence: A for the
problem, D for this fix.

```
owner answer ─► conflicts with evidence? ─no─► accept
                     │yes
                     ▼
     state conflict + evidence + recommendation (once)
                     ▼
owner reply ─► new info? ─► update, name what moved you
            ─► preference? ─► accept as owner's call; record objection
            ─► bare insistence? ─► accept as owner's call; record objection;
                                    do not say you were persuaded
```

### Option C. Running playback with ownership marks and confidence

Each round opens with "What I think we're building", five lines at most:
intent, decisions so far, and the model's top open concern. Each line is
marked as the owner's or the model's call. Each recommendation carries a
confidence (high, medium, low) and what would change it. The owner corrects
the playback, which is cheaper than answering questions. Confidence marks
make a run of "yes" mean something: a "yes" to a low-confidence
recommendation is worth a second look.

Sources: superpowers playback ("Only what they said goes in as theirs"),
Osmani (best guess plus confidence), BMAD ("a yes to a group… accepts
nothing"). Evidence: C/D.

```
round N: [playback: intent / decided (owner|mine) / top concern]
         [Q1 ➡ rec (conf: high)] [Q2 ➡ rec (conf: low; changes if …)] …
owner: corrections to playback + answers
```

### Option D. Live pre-mortem before offering to end

When a round comes back all "yes", the model does not offer to end straight
away. It first states its strongest case against the agreed design: "assume
this shipped and failed in three months; the likeliest causes are…", with one
recommended change. The owner answers it like any question. This should be
an argument in the conversation, not a pasted list: the static version did
nothing in Chiang's study.

Sources: BMAD pre-mortem and devil's advocate, OMC contrarian mode,
residual `purpose_walk` "every 3 turns… critic role", Harper Reed's "poke
holes" step. Evidence: A for interactive critique (small), D for this form.

### Option E. Steelman the option not taken

For each contested decision (one where the owner rejected the model's
recommendation, or the model's confidence was low), write two lines: the
best case for the losing option, and what would make it the right choice
later. These go into the ADR's "what would change the decision" field, which
§1a already requires. Low cost, but much of it is already covered by ADRs
and Option B's recorded objections. Evidence: D.

### Option F. Scheduled contrarian turns

Every fifth question carries a "no" recommendation, or a contrarian round
runs at a fixed point (OMC round 4, residual every 3 turns, report 17 item 9).
This is cheap, but it forces disagreement on a timer rather than on
evidence, and that is the stubbornness pattern §4 warns about. Use only if
A–C still produce runs of "yes". Evidence: D.

### Option G. Rename "Socratic"

In build-loop `references/front.md`, change "Debate Socratically" to "Debate"
and say what it means: state a position and test both yours and theirs. Do
not edit residual's "This skill is Socratic." lines (that is a different
repo), but note the clash in mstack's lexicon. Trivial cost; removes the
pull toward the ask-only reading.

### Expected value ranking

| Rank | Option | Value | Cost | Why |
|---|---|---|---|---|
| 1 | A. Open with a position | High | One paragraph | Gives the most new behaviour you want, and restores your 10-27 intent |
| 2 | B. Disagree with evidence | High | One paragraph | Makes A safe: argues without caving or digging in |
| 3 | C. Playback and confidence | Medium-high | One paragraph, some tokens each round | Makes "yes" informative; corrections are cheap for you |
| 4 | D. Live pre-mortem at wind-down | Medium | One sentence | Catches what agreement hid |
| 5 | G. Rename "Socratic" | Low-medium | Two lines | Removes the ambiguity |
| 6 | E. Steelman losing option | Low | Already half in ADRs | Mostly redundant |
| 7 | F. Scheduled contrarian | Low or negative | Trivial | Disagreement on a timer |

## 6. A small experiment

Goal: see whether A+B+C (the variant) surfaces more decisions and fewer late
defects than the current skill (the control), without becoming tiresome.

- **Design.** Pick two features of similar size from the same project (say
  two edge UI features). Grill one with the control and one with the variant,
  then swap the order on the next pair. Running both grills on the *same*
  feature is tempting, but the second grill benefits from everything you
  thought of in the first. If you do, run the variant second, so its result
  is the conservative one, and say so. Use the same model and effort.
- **Measure during the grill**, from the transcript:
  - decisions surfaced: count of numbered decisions in the final spec;
  - decisions the model raised that you had not mentioned;
  - your corrections: playback lines you changed, and recommendations you
    rejected;
  - objections the model raised, and how many changed the spec;
  - flips: times the model changed position, each tagged "new information"
    or "pressure" (sycophancy check);
  - held objections you later agreed were right, and ones you found tedious
    (stubbornness check; note the turn);
  - your time, and how many answers were a bare "yes".
- **Measure after the grill**, from build-loop's review ledger:
  - review findings in the families §1 covers (states, edges, lifecycle,
    precedence);
  - "I chose X over Y" moments during green (§5's signal);
  - spec changes after red.
- **What it would show.** Two pairs give anecdotes (Grade C at best), not an
  effect size. A clear win looks like more decisions surfaced, fewer
  same-family review findings, about the same number of minutes, and no
  "pressure" flips. If the variant raises many objections that you override
  and later call tedious, B is too strong; tighten "say it once". If
  corrections to the playback stay near zero, C costs tokens for nothing.
  Drop it.
- **Cheaper first step.** Replay a finished grill transcript to two fresh
  agents (control and variant prompts) with the same owner answers, and count
  the objections and alternatives each produces before the first question.
  This tests A alone, in an hour, with no owner time.

## Where your setup differs

| Topic | Popular approach | `question-everything` now | Verdict |
|---|---|---|---|
| Who speaks first | Questions first (Pocock, spec-kit, Harper Reed, Anthropic docs); draft first (Kiro, HumanLayer, superpowers, BMAD fast path) | Questions first; build-loop front §1 asks for the simpler alternative and debate, but that step is in a different skill | Move the position into the grill (Option A) |
| Model's own position | Per question (most); whole design (superpowers, Kiro, pstack) | Per question only | Add a whole-design position |
| Push-back | Completeness (spec-kit, yours); judgment (pstack, BMAD); facts (HumanLayer, Pocock `domain-modeling`) | "an answer that leaves a state, edge or failure undefined is not an answer yet" | Add push-back on correctness, with an update rule (Option B) |
| User pushback | Only HumanLayer covers it ("DO NOT just accept the correction") | Nothing | Gap; the research says this is where sycophancy happens |
| "Yes" means | Accepts the recommendation (Pocock, spec-kit, yours) | Same; a round of "yes" offers to end | Add confidence marks; BMAD's "a yes to a group accepts nothing" |
| Ownership of choices | superpowers marks "your call" vs theirs | ADRs say who decided; spec does not | Mark in playback (Option C) |
| Critique | Static elicitation menu (BMAD), scheduled contrarian (OMC), after build (pstack `interrogate`) | Cross-model spec review after red (§4) | Yours is strong after the spec; add a live pre-mortem before it (Option D) |
| Prototype vs ask | pstack prototypes first | §1b prototypes for look and feel | Aligned |
| "Socratic" | superpowers: "the way a sharp colleague would"; residual: permission split | build-loop front: "Debate Socratically" | Rename (Option G) |

Companion skills touched: `build-loop` (`references/front.md` §1),
`technical-excellence` §4 (lexicon entry for "Socratic", if you want one).

## Candidate actions

1. **Add Option A to `question-everything` §1** (wording below). Highest
   value: it is the behaviour you asked for, and the most-evaluated public
   skill (superpowers) works this way.
2. **Add Option B to §1** (wording below). It makes A safe. Without it, a
   more forthcoming model caves faster when you push.
3. **Add Option C to §1's Format paragraph** (wording below). It makes a run
   of "yes" informative and lets you correct cheaply.
4. **Add Option D to "Winding down".** One sentence: "Before you offer to
   end, argue the strongest case against the agreed design… and propose one
   change." Interactive critique is the only devil's-advocate form with
   controlled evidence.
5. **Fold build-loop front §1 into the grill.** Steps 1–3 (simpler
   alternative, desires, debate) become the opening position (Option A).
   Front §1 then points to it. One copy of the rule, in the skill that runs
   it.
6. **Run the replay experiment in §6** before rolling the change out to
   other skills. It needs an hour and no owner time.
7. **Rename "Debate Socratically"** (Option G). Two-line edit.
8. Hold E and F unless A–C still produce runs of "yes".

### Proposed wording for the top three

Insert after "Push back: …" in §1, before **Format**:

> **Open with a position.** Before the first round, read the code, then send
> one message: what you think we're building, in two sentences; the design you
> would build and why; the strongest objection to that design and to the
> request as asked; and the simplest alternative (do less, reuse, change the
> requirement). Ask what the owner wants it for, and what that unlocks,
> before any detail question. Your questions follow from your proposal; they
> do not replace it.

Insert after **Format**:

> **Disagree with evidence.** When an answer conflicts with the code, a doc,
> the glossary, an ADR or an earlier answer, say so in your next message:
> quote the conflict, give your recommendation, and ask the owner to choose.
> Say it once. Change your position only for new information or a stated
> preference, and name which one moved you ("you told me X, which I did not
> know"). Insistence alone is neither. If the owner keeps their answer, it is
> their decision: record it in the spec with your objection beside it, and
> do not say you were persuaded. Do not argue taste, scope or risk appetite
> twice; those are the owner's.

Replace the second sentence of **Format** ("Each round asks…") with:

> Open each round with "What I think we're building", five lines at most:
> the intent, the decisions so far (each marked *owner* or *mine*), and your
> top open concern. The owner corrects it, and a correction outranks any
> answer. Then ask every question whose prerequisites are settled, numbered,
> each with your recommended answer and its confidence (high, medium, low),
> and for anything below high, what would change it.

## Sources

Local (read 2026-11-19):
- Your messages in `~/.claude/projects/-home-mini-Documents-repos-edge/`
  `1459dd51` (2026-10-27), `99ded3ee` (2026-10-22), `883e50fb` (2026-11-05),
  `50e1af19` (2026-11-15); `-phoe-nix/` `d87e4d7f` (2026-11-07), `4040da30`
  (2026-11-12); `~/.codex/sessions/2026/11/16/rollout-2026-11-16T00-54-23-*`.
- phoe-nix commit `d85c6c46` (2026-10-27), build-loop "Debate Socratically".
- `/home/mini/Documents/repos/mstack/skills/build-loop/references/front.md`,
  `skills/question-everything/SKILL.md` (working tree, 2026-11-19).
- residual-cli `src/skills/definitions/*/SKILL.md`, `src/skills/context.rs`,
  `README.md` at `32c0836` (2026-09-28).
- Report 17 in this directory (Pocock's video).

Skills and prompts (accessed 2026-11-19):
- mattpocock/skills `5863806`:
  https://github.com/mattpocock/skills/blob/5863806/skills/productivity/grilling/SKILL.md
  (2026-10-29); commit `a4b2009` (2026-07-31).
- cursor/plugins `35a9094`, `harness/pstack/claude-code/skills/poteto-mode/SKILL.md`
  (2026-11-16), `sharpen` (2026-11-15), `docs/guide/04-design.md`:
  https://github.com/cursor/plugins
- obra/superpowers `22f0b46`, `skills/brainstorming/SKILL.md` (2026-11-03),
  `skills/writing-plans/SKILL.md` (2026-09-25), `RELEASE-NOTES.md` v7.0.1,
  v7.0.2: https://github.com/obra/superpowers
- humanlayer/humanlayer `2f5b58d`, riptide-rpi `create-design-discussion`
  (2026-10-22); `.claude/commands/create_plan.md` blob `77c7fe9`
  (2025-11-12, removed 2026-10-22): https://github.com/humanlayer/humanlayer
- github/spec-kit `617e9a0`, `templates/commands/clarify.md` (2026-09-15),
  `specify.md` (2026-10-29): https://github.com/github/spec-kit
- BMAD-METHOD `e435a22`, `skills/core-tools/bmad-facilitate/SKILL.md`,
  `bmad-advanced-elicitation`, analyst and PM `customize.toml` (2026-11-11):
  https://github.com/bmad-code-org/BMAD-METHOD
- Kiro docs: https://kiro.dev/docs/specs/feature-specs/ (2026-08-04),
  https://kiro.dev/docs/specs/ (2026-11-12).
- Anthropic feature-dev:
  https://github.com/anthropics/claude-plugins-official (`plugins/feature-dev/commands/feature-dev.md`, 2025-11-20).
- Yeachan-Heo/oh-my-claudecode `skills/deep-interview/SKILL.md` (2026-10-30):
  https://github.com/Yeachan-Heo/oh-my-claudecode
- Claude Code best practices: https://code.claude.com/docs/en/best-practices
  (undated, accessed 2026-11-19).
- Thariq, https://x.com/trq212/status/2005315275026260309 (2025-12-28), via
  https://velvetshark.com/stop-prompting-claude-code-let-it-interview-you
  (2026-01-02).
- Claude's constitution: https://www.anthropic.com/constitution (2026-01).
- Harper Reed: https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/
  (2025-02-16).
- Addy Osmani `interview-me`:
  https://tessl.io/registry/skills/github/addyosmani/agent-skills/interview-me
- ctoth CLAUDE.md: https://gist.github.com/ctoth/d8e629209ff1d9748185b9830fa4e79f
  (2025-11-30).
- The Register: https://www.theregister.com/2025/08/13/claude_codes_copious_coddling_confounds/
  (2025-08-13).

Research:
- Sharma et al.: https://arxiv.org/abs/2310.13548 (2023-10-20).
- Laban et al.: https://arxiv.org/abs/2311.08596 (2023-11-14).
- Fanous et al., SycEval: https://arxiv.org/abs/2502.08177 (2025-02-12).
- Hong et al., SYCON-Bench: https://arxiv.org/abs/2505.23840 (2025-05-28).
- Cheng et al., ELEPHANT: https://arxiv.org/abs/2505.13995 (2025-05-20).
- SMART: https://arxiv.org/abs/2509.16742 (2025-09).
- Ma et al.: https://arxiv.org/abs/2608.26511 (2026-08-27).
- He et al.: https://arxiv.org/abs/2610.04329 (2026-10-03).
- Anthropic, well-being: https://www.anthropic.com/news/protecting-well-being-of-users
  (2025-12-18).
- Anthropic, personal guidance: https://www.anthropic.com/research/claude-personal-guidance
  (2026-04-30).
- OpenAI: https://openai.com/index/sycophancy-in-gpt-4o/ (2025-04-29),
  https://openai.com/index/expanding-on-sycophancy/ (2025-05-02), via
  https://simonwillison.net/2025/Apr/30/sycophancy-in-gpt-4o (openai.com
  returned 403).
- OpenAI Model Spec: https://model-spec.openai.com/2025-12-18.html.
- Chiang et al., IUI 2024: https://dl.acm.org/doi/10.1145/3640543.3645199,
  PDF https://par.nsf.gov/servlets/purl/10524816.
- Irving, Christiano, Amodei: https://arxiv.org/abs/1805.00899 (2018-05-02).
- Sarkar, CACM 67(10), 2024-10: https://doi.org/10.1145/3649404,
  https://arxiv.org/html/2411.02263v2.
- Lee et al., CHI 2025: https://www.microsoft.com/en-us/research/publication/the-impact-of-generative-ai-on-critical-thinking-self-reported-reductions-in-cognitive-effort-and-confidence-effects-from-a-survey-of-knowledge-workers/
- Stanford Encyclopedia of Philosophy, "Socrates":
  https://plato.stanford.edu/entries/socrates/ (rev. 2022-05-26).
- Khan Academy: https://blog.khanacademy.org/how-we-built-ai-tutoring-tools;
  KQED/Hechinger on Oreopoulos and Low (NBER):
  https://www.kqed.org/mindshift/66662/students-didnt-get-answers-from-khanmigo-they-didnt-want-its-questions-either
  (2026-09-21).
