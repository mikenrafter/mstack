# build-loop reference: front sequence (§1b) and compaction (§10a)

Source: owner, 2026-11-18, after Matt Pocock's spec → tickets → compact →
build flow (research/17). At session start, run `pr-stacks`
`scripts/pr-size report` and show the owner any skipped size limits.

## 1. Feature discussion, steps 1-3

Follow `question-everything` §1, **Open with a position**, for these steps:

1. **Simpler alternative.**
2. **Desires and threat model.** Include who can reach it, untrusted inputs
   and what it holds.
3. **Debate.** Use §1's **Disagree with evidence** when answers conflict.

Then write the agreed intent in 1-2 sentences: the review brief's Intent.

## 1b. Front sequence

Before red, in order. Each step may be skipped only when its question is
already answered.

1. **Grill** (`question-everything` §1–§1a): alignment with the owner;
   glossary terms, ADRs the owner approves.
2. **Prototype or mockup** (`question-everything` §1b) when the answer depends
   on look, feel or unpredictable behaviour. Throwaway; never merged.
3. **Pilot** (`references/scoping.md`) when the open question is whether the
   approach works on real cases.
4. **Spec and stack plan** (`question-everything` §6, `pr-stacks` §2): one
   ticket per stack line, each labelled two-way or one-way.
5. **Compaction point.** Everything that matters is now in files. Compact
   here if the session is large (§10a), then reread SKILL.md.

Then run §3–§6 per PR in the stack, in order. Adjacent two-way PRs that share
tests may share one red run; each test lands in the PR whose code makes it
pass.

## 10a. Compaction is your call

Auto-compact cuts wherever the window fills, often mid-step, and the summary
drops what it did not know mattered. Choose the moment yourself, at a phase
boundary where every decision and open question is already in a file or the
ledger: the end of the grill (§1b step 5), after the spec and
stack plan, after a PR merges, between review rounds. Then send `/compact next: <what comes next>` to your own thread with
`t3_thread_send` (`threadId` from `$T3CODE_THREAD_ID`, `mode: "queue"`) and
end the turn; outside T3, `uw-agent compact ask` (`uw-agent` skill).
Above 500k tokens a hook (`bin/compact-advice-hook`) reminds you with your
session id. Subagent, Sol and peer runs keep going through a compaction
and report back as usual, so they are no reason to wait. Auto-compact stays on as a backstop
only. After any compaction, reread SKILL.md (its header rule).

