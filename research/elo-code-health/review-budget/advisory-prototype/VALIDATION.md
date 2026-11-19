# Prototype validation

`collector.py` implements an object-only evidence capture and a shadow structural-fix candidate. It always disables execution and leaves allocation unresolved. The collector SHA256 after validation is `32224f39659bb8663c226e4ad1de99fc39856fcfad2ceeecce381b710b43b2a2`.

The frozen protocol and nine initial CLI tests preceded implementation. Qex job `e1649a7d-f974-4288-8edf-e7254f853aa3` failed all nine at the absent collector entrypoint. Implementation then passed those tests. Additional negative and race tests were added in response to the parent's concrete challenges.

Final focused run `bbb6baa1-6432-4bfa-a85c-467626f2887b` passed 16 tests, with zero skipped. It used 28.7 MB and 2.8 CPU seconds. The tests exercise the actual installed canonical script against synthetic pinned ledger copies, pending required review, cap exhaustion, stale reviewed objects despite supplied verification flags, absent triggers, bad patch/artifact hashes, a real later non-ancestor fix, symlink/outside-root refusal, malformed input/history, replacement-object refusal, append-only records, and separate unobserved outcomes. The synthetic ledgers retain completed one-exchange and two-Fable-exchange requirements. They do not suppress dialogue requirements to manufacture a passing gate.

An independent audit identified that duplicate or reordered round IDs could masquerade as three distinct passing rounds. A new regression first failed for all five variants: duplicate IDs, reordered IDs, nonpositive ID, backward phases, and a future phase. Red qex job `780387cb-cf04-4992-a1d1-249bdc1987a1` recorded those assertion failures. The collector now rejects nonpositive/nonincreasing IDs and nonmonotonic or future phases. It does not require contiguous IDs or reconstruct policy history. The replacement-object test includes a positive control showing ordinary Git substitutes a different tree, then verifies the collector retains the original named object's tree.

Policy-hash refusal occurs before subprocess execution. A canonical-seam test runs the actual policy while changing source ledger bytes, then checks capture refusal. Another simulates a changed second policy read without modifying the installed script. Unknown canonical stdout is refused. These mocks inject faults at I/O boundaries; the canonical state machine is not mocked in the main CLI cases.

Three isolated mutants were each caught by their intended assertion, final qex job `55ec84da-c18d-4f5a-bfd7-fb6ebc7bde04`:

- Ignore the exact reviewed-object comparison.
- Erase the root restriction for source reads.
- Report a required canonical gate as an additional-review recommendation.

An earlier narrower mutation bypassed only the first trigger-artifact read's root restriction. It survived because the after-read recheck independently applied the restriction. The stronger all-source-read mutation then failed the intended assertion. No source was modified by mutation testing; each variant lived in its own temporary directory. `mutation-results.json` records the final three results.

The real read-only smoke used `phoe-nix.research/w49.ledger.json` and Git commit `4b397f979b8ba308e55e371ed1f8ab142dd6d219`. The canonical script returned `ROUND`, requesting its already-required fresh Fable tier-2 pass. The collector returned `required-review-still-pending`, `execution_allowed=false`, object-only scope, unsupported working-tree coverage, and unknown historical optional-boundary status. The final capture is `smoke-records/observation-3329b5b6982026312359dca4bc85e90ecd8cb04af8b0706511b31c6d72848b46.json`. Earlier captures are retained separately rather than overwritten. Every final capture records UTC collection time, collector hash, and explicit supplied-ledger provenance. An observed boundary means the current canonical result on the supplied ledger and object, not proof of a historical decision or authentic past review execution.

The implementation intentionally narrows the design's interface. It supports schema-2 ledgers, exact reviewed Git objects, single-parent ancestor fix facts, and bounded source artifacts. Live dirty-tree coverage, parent-verified final fixes, legacy-policy equivalence, executable review allocation, semantic verification of a supplied trigger category, and independent confirmation of acceptance are unsupported. Input fact category and acceptance are explicitly reported as supplied assertions. Matching hashes establish bytes and ancestry only.

Records are content addressed and created exclusively, with existing bytes checked rather than replaced. Files are read-only by default. This is integrity within a trusted local-user workflow, not authentication against the machine owner or a hostile concurrent writer. Conflicting outcomes remain distinct records; no mutable registry chooses a winner. A reported review never becomes an inferred clean negative. No subject repository, live policy, actual review process, or external service was changed.
