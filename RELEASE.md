# Initial publication, 2026-11-16

This release publishes the 2026-11-12 collection as a research and workflow snapshot. It makes no claim that the skills are portable without adaptation or that the proposed workflow has been validated as a whole.

## Publication checks

- MIT license selected by the owner.
- README identifies the audience, first commands, dependencies and snapshot status.
- Both helper scripts expose working help; all 158 script tests pass.
- Local skill links resolve to bundled files where available. Private evidence is marked unavailable instead of linked to personal filesystem paths.
- The dossier reader fetches the Markdown files at their actual locations.
- Tracked content and the initial commit were checked for common credential patterns. Raw transcripts and private usage artifacts remain excluded. A pattern scan cannot prove that every possible secret is absent.

## Open decisions and research

1. **Source ownership and export.** Decide when mstack becomes the canonical home for the skills. Until then, the live phoe-nix copies and this publication can diverge. A repeatable, reviewed export should include provenance, companion dependencies and publication checks.
2. **Portability.** Separate general guidance from host policies and provider-specific orchestration. Supply or replace the private wrappers before promising an install-and-run workflow.
3. **Workflow effectiveness.** Compare a small review against the full loop at equal cost. Measure escaped defects, owner time, elapsed time and reverts. Numeric review scores are conventions, not validated quality measures.
4. **Agent context and waiting.** Measure fresh child versus resumed child, compaction thresholds and keepalive cadence, including delivery, recovery and cost. Current savings estimates are modeled, not demonstrated.
5. **Review policy.** Validate maturity-based review bars, realistic threat models, and the treatment of deferred hardening and minor findings. The design is in [15-bars-by-maturity-spec.md](research/15-bars-by-maturity-spec.md); this snapshot does not imply that all proposed behavior is implemented.
6. **Learning and views.** Test whether code views, walkthroughs and teaching checkpoints improve understanding and retention. Paneweft and residual work have their own release timelines.
7. **Reproducibility.** Design a shareable, redacted measurement dataset or synthetic fixtures with a repeatable analysis. This release withholds the underlying private corpus, so readers cannot independently reproduce its usage figures.

These are follow-up projects. They do not prevent publishing the collection with its limits stated. The older [workstream plan](research/PLAN.md) retains the fuller context and dated owner decisions.
