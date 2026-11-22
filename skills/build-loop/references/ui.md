# build-loop reference: UI work (briefs, inheritance, fidelity)

Source: edge alarms/timelines pilot (owner, 2026-11-19, m233). The implementer had the signed-off
mock-ups but rebuilt toggles, list rows, chart annotations and the hypnogram from scratch. The app
and two earlier pilots already did all of these correctly. The owner caught it from screenshots.

## The rule

UI work inherits before it builds. A UI brief names every source the screen inherits from, and
the implementer reuses that code. New code covers only what the mock-up adds.

## Who makes the mock-up

The orchestrator, always (owner, 2026-11-21). It writes and revises every mock-up version itself,
shows it with the T3 Code tools, collapsed in a `<details>` element whose summary names the
mock-up and version (owner, 2026-11-21), and gets sign-off. Never put a mock-up step in an implementer or
reviewer brief; an implementer that needs a design change asks the orchestrator.

**Neon reads each mock-up round (owner, 2026-11-21).** Neon (Gemini Neon, `delegate_task`) lays out
output very legibly, and reading even a little of it makes the orchestrator write to the owner more
clearly. So before showing the owner a mock-up version, send Neon the HTML path and the note you
plan to send. Neon writes and edits nothing. It returns:

1. what a first-time reader sees first, second and third, and what they will miss;
2. labels, copy or groupings it found unclear, each with a rewrite;
3. its own version of the note to the owner.

Read all of it before revising. Take what is right, revise the mock-up yourself, and write the note
in your own words; Neon's version is input, not the message. The pass is advisory and runs alongside
the Claude agent cap. Skip it, and say so in the note, when vigil advice shows the Antigravity
budget past 90% or Neon has not answered within about 10 minutes. Neon does not write mock-ups
(rule above), and its brief carries the Neon brief lines in `quirks.md`.

## The brief (checked by `scripts/ui-brief-check`)

Any brief that creates or changes a screen, widget, chart or page is a UI brief. Write it to a
file and run `ui-brief-check <brief.md>` before delegating; it exits 1 until the brief has:

```
## UI inheritance
| Source | Path or SHA | Take from it |
|---|---|---|
| Mock-up (signed off) | mockups/…/x-v22.html | layout, copy, order, sizes |
| Original screen | lib/…/alarm.dart @ <sha> | toggles, rows, buttons, theme |
| Prior pilot / landed feature | pilot/day-timeline @ c6b764aae | annotations, list, day row |

## Fidelity check
Screenshot pairs (mock-up | build), same viewport: <dir>
```

- **Mock-up:** the signed-off version, never an earlier one. Read its CSS for sizes and colours.
- **Original screen:** the screen this replaces or extends, at the base SHA.
- **Prior pilots and landed features:** search for them; don't rely on memory. `git branch -a
  | grep -i pilot`, and `git log --all -i --grep=<feature>` for each control the mock-up shows
  (chart, toggle, list row, editor). Name each one, or write `none found: <what you searched>`.
- **Take from it:** the concrete widgets, painters or styles to reuse.

## Implementer duties

1. Before writing UI code, list in the report which widget or painter from each source it will
   reuse. If it won't reuse one, it says why.
2. Never theme around the app: no local `ThemeData`/colour-scheme overrides that change how shared
   controls draw.
3. Before handing back, it takes screenshots of the mock-up and the build at the same viewport,
   puts each pair side by side, and lists every visible difference. That covers layout, order,
   controls, copy, colours, chart marks, and the default state on open. Fix the differences or
   list them as deferred.
4. If the mock-up can't be rendered (no browser), say so, and compare against its CSS and markup
   line by line.

## Gate before the owner sees it

A UI handoff (screenshots, iteration build, APK) is blocked until a fidelity pass has run. A
different model from the author compares the screenshot pairs against the mock-up and the
inheritance table, and writes `fidelity-review.md`. It ranks differences by how much the owner
would notice. Fix the top ones before the owner looks. The orchestrator compares at least one pair
itself, and never forwards screenshots it hasn't compared.
