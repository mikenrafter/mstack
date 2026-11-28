# Holdouts for red/green slices

Red writes holdouts from the same agreed behavior before green starts, alongside
the visible tests. The green brief explains why the holdouts exist and asks for
the behavior across its stated range. Holdouts are hidden for the implementation
round only, unless the brief says otherwise.

## Storage

Red writes the holdouts in its own scratch directory, never in the checkout, and
seals them with `scripts/holdout seal <dir> --project <checkout> --feature <f>
--slice <NN>`. That encrypts them with age to
`<project>.research/holdouts/<f>/<NN>.tar.age` and removes the plaintext, so
grepping the sidecar finds only ciphertext. To run them, red or the orchestrator
extracts them into a scratch directory outside the checkout (`holdout extract
... --into <dir>`), runs them against the slice revision, and deletes the
directory afterwards. Do not mention the holdout key's path in a green brief.

The key is `~/.local/share/mstack/holdout-age-key.txt`, and the sops file
`/etc/secrets/nixed.yaml` (`holdout_age_key`) holds a copy. Every file is also
encrypted to the hosts' sops age keys listed in
`~/.config/mstack/holdout-recipients.txt`, so a host's root key can still decrypt
them if the holdout key is lost. Never delete or rotate the key without
resealing every holdout first.

## The implementation round

Set a failed-round limit in the slice brief (two by default). Before the limit,
report only the failed behavior or invariant. Log the revision, round, and outcome
in the shared slice log. At the limit, stop the retries and notify the
orchestrator. The orchestrator gives guidance or releases the cases if the
concern bar permits. For concern bar 9 or above, never show the holdouts or
revealing output to the implementer during implementation. If guidance is
insufficient, leave the slice blocked and record the reason.

## The review round

When the slice moves to review, always add the holdouts to the checkout as
ordinary tests (`holdout extract ... --into <checkout test dir>`), whatever the
concern bar, and commit them with the slice. Reviewers see them like any other
test. Keep the sealed file as the record of what was held back.
