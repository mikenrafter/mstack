# Exact coverage in historical inspection pools

[C, descriptive reproduction, 2026-11-17] Additional inspectors increase mean detection of the study's reference faults, with diminishing returns. Seven of eight complete pools still miss listed faults. These curves cannot choose a current code-review stopping count.

All 65,528 nonempty teams in the eight public matrices were enumerated. Each unordered team receives equal weight within its size; the table shows mean reference-fault coverage. All matrices are retained.

| Matrix | Pool size | One inspector | Two | Three | Full pool | Faults never found |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atm_nov | 12 | 25.0% | 41.6% | 52.9% | 86.2% | 4 |
| atm_jun | 14 | 26.4% | 42.8% | 54.1% | 82.8% | 5 |
| pg_nov | 12 | 20.1% | 33.6% | 44.0% | 85.2% | 4 |
| pg_jun | 14 | 31.2% | 50.1% | 62.4% | 96.3% | 1 |
| a_nov | 12 | 13.9% | 23.7% | 31.1% | 66.7% | 6 |
| a_jun | 13 | 48.7% | 71.8% | 83.5% | 100.0% | 0 |
| b_nov | 12 | 12.8% | 22.7% | 30.6% | 66.7% | 5 |
| b_jun | 13 | 49.7% | 72.5% | 82.9% | 93.3% | 1 |

The normalized source contains fixed human requirements documents with seeded or reintroduced study faults. Its reference lists are not an exhaustive census of natural defects. Pools include different reading techniques, and participant IDs recur within cohorts. Overlapping teams are not independent samples. The graph's 5th/95th team percentiles describe the finite pool; they are not confidence intervals for new reviewers.

Every mean was checked against a separate hypergeometric counting expression. An independent audit recomputed all teams with set unions and checked exact rational means and quantiles. Three focused tests and three deliberate mutations check coverage accounting; see the [audit](MATRIX-AUDIT.md), [protocol](COVERAGE-PROTOCOL.md), [complete results](coverage-results.json) and [interactive chart](coverage.html).

These are individual inspection records on fixed artifacts, not sequential rounds with edits, shared findings or changing scopes. The result motivates measuring complementary detection and persistent blind spots. It does not transfer the numerical curves to LLMs or establish that a particular extra review is cost effective.
