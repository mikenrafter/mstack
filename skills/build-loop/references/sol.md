# build-loop reference: running Sol (§7)

1. **T3 first.** Call `orchestrator_capabilities`, pick the latest Sol unless
   the user named a version, and use `delegate_task` (`role: "review"` or
   `"implement"`, `mode: "async"`). New `clientRequestId` each round; save
   `taskId`. Do not use `t3_thread_send`, `create_threads` or
   `t3_thread_launch` for review. Every argument, pivot, cull or recheck uses a fresh
   delegate containing the prior review, ledger and objections. T3 children
   get no history, so every brief is self-contained. Before native Sol
   delegation, follow the harness routing instructions when applicable.
   Sol is the usual red implementer, and takes green or fix rounds when Sonnet wrote red (B1): pass `--author sol`
   to the ledger and do not let it review that diff.
2. **Fallback when T3 is unavailable.** Run the `codex` binary directly:
   `codex exec -m <sol model> -c model_reasoning_effort=<B6 effort> -s workspace-write - < prompt`
   (read-only for pure review). Or use a project wrapper script that also
   enables network (local test servers) and adds writable dirs (for example
   `edge.research/bin/sol <worktree> <prompt> <log>`).
3. **No Sol route:** report the blocker. Do not substitute a model.
4. **Commits.** Codex mounts every `.git` read-only. The implementer commits in
   `git clone --shared <worktree> /tmp/<name>.git` and leaves a bundle. The
   orchestrator runs `git bundle unbundle` and `git reset --mixed <head>` in
   the worktree.
5. **Paths.** Pass absolute paths; wrappers often `cd` into the worktree.
6. **Prompts.** Require the five-minute implementation check-in and every-reviewer argument
   minimum from `dialogue.md`. Give every agent the round focus. For long
   commands use qex/Boat and vigil per their skills; subagents never use
   orchestrator mode or sleep loops. Reviewer work stays read-only, with
   checks run in a disposable copy when needed.
7. **Quirks.** Sol's known quirks and the defined responses are in `quirks.md`. On an
   `item overdue` for a Sol review, read the child once for a `VERDICT:` line before waiting longer.
