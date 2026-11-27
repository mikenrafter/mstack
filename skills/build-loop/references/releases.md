# build-loop reference: developer releases under a deadline

Moved from `scoping.md` (2026-11-27) to keep each reference within one read. Read it when the owner
sets a deadline for a developer release.

## Developer releases: deadlines (owner, 2026-11-20)

A developer release is anything the owner is waiting on: a pilot APK, an upstream PR, a fork release. These get a
deadline; slow-burn work nobody is waiting on does not (an artificial date thins review and burns budget).

- **Build ledger (owner, 2026-11-22).** Keep one ledger per project (edge: `edge.research/builds/ledger.json`)
  of what each build the owner runs contains, by feature or pilot, with evidence; which pilots the owner wants;
  and the next build's recipe (base, branches to merge) and checks. Plan builds, ETAs and merge rules from it, not
  from git ancestry: pilots get squashed, rebuilt and reworked, so patch or ancestor matching undercounts. Record
  the owner's statements about their phone as evidence, flag where they and the code disagree, and update the
  ledger at every build.
- **Version checklist for every build the owner installs (owner, 2026-11-22).** Version metadata is how the owner,
  a crash log and the ledger agree on which build ran. Before handing over a build:
  1. The build number (Android `versionCode`) is higher than the last build you handed over, every time, and comes
     from a counter in the repo that the build reads, never from memory or a hand edit. Same application id and
     signing key, so it installs over the last one. Never reuse a number for different contents.
  2. The version name keeps the project's base name and adds the short commit and `-dirty` when the tree has
     uncommitted changes, so a crash report header (name and code) points at a commit.
  3. Read the numbers back from the built file (`aapt2 dump badging`: package, versionCode, versionName), not from
     the source, and compare them with the counter.
  4. The file name carries the base, the feature set and the build number.
  5. The delivery message gives package, build number, version name, size and sha256, says "replaces build N", and
     says whether it should install over the current one. Tell the owner to compare the number on their phone.
  6. The ledger entry records number, sha256, base commit, contents and evidence. If a log or screenshot from the
     owner shows a number you did not hand over, or the same number for different contents, fix the counter first.
- **ETA means the owner's deliverable.** An ETA question asks about something the owner will use (an APK on
  their phone, a PR they will read). If you cannot say why the deliverable matters to them directly, it is the
  wrong one; ask.
- **Give an estimate when asked, then plan to it.** State it in Mountain time (America/Denver) first, then UTC, and say what
  would make it slip. Report a slip when it becomes likely, not at the deadline.
- **Internal cutoffs in every brief:** "pushed by HH:MM UTC", with the priority order inside the run ("naps before
  the log storm") and "push what is done and list the rest" if the cutoff hits. Leave at least one hour between the
  last cutoff and the promised delivery for the merge, the combined tests and the build.
- **Integrate early:** merge and test each branch as it lands, not all at the end; parallel branches conflict where
  they share a widget or painter, and early merges leave time to resolve them.
- **Scope freeze at the cutoff (Parkinson's law):** a request that arrives after the cutoff goes to the next build
  by default. Say so in one line and offer the exception; take it only when the owner says it must make this build.
  When the owner moves the deadline out, do not refill the slack with new scope unless they ask.
- **Keep the independent check:** a deadline may move fidelity review to the orchestrator, but never skips it.
  Write follow-ups for the flaws you let through.
- **Budget:** parallel runs under a deadline spend the weekly windows faster; check them at each cutoff and move
  work between providers before one runs out.
