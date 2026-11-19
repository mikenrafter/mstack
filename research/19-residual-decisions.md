# 19. Decisions and avoid lists as first-class records in residual

Written 2026-11-18 from `residual-cli` at `32c0836` (branch `view-landscape`)
and research/17. Design proposal only; nothing in residual-cli was changed.

## Recommendation

Yes, make decisions (ADRs) first-class in residual, and add an avoid list to
its lexicon. A plain `docs/adr/` folder records why. Residual can also tell
you when that why has gone stale, because it already knows which forces press
on which components. No markdown folder can do that.

## What residual has today

- Lexicon terms: `term`, `definition`, `domain`, `aliases`
  (`src/structure/definition/lexicon.rs`). Aliases are accepted synonyms; they
  count toward the continuity check that every force shortname and outcome
  uses a lexicon word.
- Forces, attractors, components, residues (force ↔ component), iterations
  as markdown snapshots, source-comment tags with dangling-tag warnings
  (`src/tags.rs`, `src/verify.rs`).
- An ATAM lens for trade-offs, but no record of the decision a trade-off
  produced.

## Proposed model

**Decision record**: `decisions/NNNN-slug.md`, markdown with TOML front
matter, stored where the project's residual config stores metadata (inline or
the sidecar branch).

```toml
id = "ADR-0007"
title = "Thumbnail diagrams are separate from diagrams"
status = "accepted"          # proposed | accepted | superseded | deprecated
date = "2026-11-18"
door = "two-way"             # from pr-stacks
forces = ["F12", "F15"]      # the pressures that drove it
components = ["thumbnails", "diagram-store"]
residues = ["R40"]
supersedes = []
owner_ok = "thumbnail diagram is fine as long as an ADR says it's not a diagram"
```

Body: context, decision, alternatives considered and why each was dropped,
consequences. The dropped paths stay, as the mstack README asks.

**Avoid list**: a new lexicon column, `avoid`, pipe-separated like `aliases`.
Different meaning: aliases are allowed, avoid words are not.

## What residual can do with them

1. `residual why <component|path>`: decisions and forces touching it. The
   question to ask before removing a fence.
2. `verify`:
   - dangling force, component or residue ids in a decision;
   - a superseded decision without a successor;
   - **stale decision**: an accepted decision whose forces or components
     changed after its date (dates from the sidecar's git history). This is
     the check a markdown ADR folder cannot make;
   - avoid words in force shortnames, outcomes and decision titles;
   - `ADR-NNNN` source tags (from `comment-audit`) that point at no decision,
     using the existing dangling-tag warning.
3. Skill context: the grill (`question-everything` §1a) receives the decisions
   and lexicon entries for the components a feature touches.
4. `residual export glossary`: writes `GLOSSARY.md` (term, definition, avoid,
   lives) for agents and projects that do not run residual.

## Update, 2026-11-19

The owner's rule: the agent holds a strong opinion about when a decision
deserves a record and proposes it unprompted, then writes it once the owner
confirms. Every record must be defensible from its own text (context,
options, why this one, what would change it). The avoid list belongs to residual's lexicon, as the
negative counterpart to aliases, the way stressors pair with purposes. The
minimal spec is `residual-cli.research/specs/lexicon-avoid-scenarios-decisions.md`.

## Limits carried over from research/10

Review comments are never turned into decisions automatically.
Residues remain authored coupling, not extracted dependencies.

## Size and order

One build loop, run as a pilot: the decision record, the `avoid` column,
`verify` for dangling ids and avoid words, and `residual why`. The second
stage adds stale-decision detection, `ADR-NNNN` tags and the glossary export.

Open question for the owner: should decisions live next to iterations
(authored snapshots), or in their own directory the CLI owns? This note
assumes their own directory.
