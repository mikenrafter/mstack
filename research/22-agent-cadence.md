# 22. Does one agent change how another talks?

Date: 2026-11-21. Question from the owner: after reading Neon output, the orchestrator writes more
coherently; after Sol, less coherently, though Sol's insight is valuable. Has anyone measured how one
model's output shifts another model's style? Grades follow [BRIEF.md](BRIEF.md). Sources were read
from abstracts and search summaries, not full papers.

## What is published

- **Models converge strongly toward whatever is in their context.** Blevins and colleagues frame it
  as communication accommodation and find that models adapt their output style to their
  conversational partner, some features more than others
  ([arXiv 2508.03276](https://arxiv.org/abs/2508.03276), 2025). Grade B (observational, controlled
  prompts). A follow-up on WildChat logs in eight languages finds models *over*-converge toward users
  on function words and open-class words, while humans converge at human-to-human rates
  ([arXiv 2605.29278](https://arxiv.org/abs/2605.29278), 2026). Grade B.
- **Model-to-model, convergence is uneven: some models anchor, others absorb.** 7,500 simulated
  multi-round discussions between different LLMs doing qualitative coding showed rising lexical and
  semantic convergence. Stable "anchor" models (Gemma, Llama 3.3) shaped their peers' output; others
  (DeepSeek) took on outside framing ([arXiv 2512.00047](https://arxiv.org/abs/2512.00047),
  BlackboxNLP 2025). Grade B. This is the closest match to the owner's observation.
- **Long discussions drift.** Work on multi-agent conversational task solving reports alignment
  collapse as agents discuss for longer
  ([ResearchGate 385386800](https://www.researchgate.net/publication/385386800)). Grade C
  `[unverified]`: only the summary was seen.
- **Imitation on purpose is weaker than drift by accident.** Asked to imitate a user from a few
  samples, models manage structured genres (news, email) and fall back to a generic web style on
  informal ones ([arXiv 2509.14543](https://arxiv.org/abs/2509.14543), 2025). Grade B.

Nothing found measures *coherence* (as opposed to lexical similarity) moving with the partner model,
or an orchestrator that reads one sub-agent's report and then writes to a human.

## What it suggests for us

The owner's observation fits the published pattern: the orchestrator accommodates toward whatever
it read last. If that holds, *which* model's text the orchestrator reads last before writing to the
owner is a lever. That is why build-loop now gives Neon a legibility pass on each mock-up round
(`skills/build-loop/references/ui.md`). A Sol report read right before an owner message is the
opposite case; summarise it in your own words before writing, rather than writing straight after it.

## A measurement we could run (proposed, not run)

1. From T3 threads and Claude transcripts, take orchestrator messages to the owner and label each by
   the last sub-agent text the orchestrator read before it (Neon, Sol, Claude, none).
2. Score each message with deterministic measures: mean sentence length, readability grade, share
   of lines that are lists or tables, how often each model's habitual words appear. Score coherence
   with a blind Opus judge that sees no model labels.
3. Compare groups; check the effect fades with turns since the read. Confound: tasks that use Neon
   differ from tasks that use Sol. Pair messages within the same thread where possible.

Grade of our own claim today: D (the owner's impression). The measurement would lift it to C.
