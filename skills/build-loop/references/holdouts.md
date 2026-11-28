# Holdouts for red/green slices

Red writes holdouts from the same agreed behavior before green starts, alongside
the visible tests. The green brief explains why the holdouts exist and asks for
the behavior across its stated range. Keep holdouts and detailed results outside
the implementer's checkout and readable workspace. Run them against the slice
revision from the red or orchestrator environment.

Set a failed-round limit in the slice brief (two by default). Before the limit,
report only the failed behavior or invariant. Log the revision, round, and outcome
in the shared slice log. At the limit, stop the retries and notify the
orchestrator. The orchestrator gives guidance or releases the cases if the
concern bar permits. For concern bar 9 or above, never show the holdouts or
revealing output to the implementer. If guidance is insufficient, leave the
slice blocked and record the reason.
