# build-loop reference: running Sol (§7)

1. **T3 first.** Call `orchestrator_capabilities`, pick the latest Sol unless
   the user named a version, and use `delegate_task` (`role: "review"` or
   `"implement"`, `mode: "async"`). New `clientRequestId` each round; save
   `taskId`. Do not use `t3_thread_send`, `create_threads` or
   `t3_thread_launch` for review. T3 children get no history, so each brief is
   self-contained.
2. **Fallback when T3 is unavailable.** Run the `codex` binary directly:
   `codex exec -m <sol model> -c model_reasoning_effort=high -s workspace-write - < prompt`
   (read-only for pure review). Or use a project wrapper script that also
   enables network (local test servers) and adds writable dirs (for example
   `edge.research/bin/sol <worktree> <prompt> <log>`).
3. **No Sol route:** report the blocker. Do not substitute a model.
4. **Commits.** Codex mounts every `.git` read-only. The implementer commits in
   `git clone --shared <worktree> /tmp/<name>.git` and leaves a bundle. The
   orchestrator runs `git bundle unbundle` and `git reset --mixed <head>` in
   the worktree.
5. **Paths.** Pass absolute paths; wrappers often `cd` into the worktree.
6. **Prompts** for implementers that run long tests must say: "During long test runs keep your
   session alive: start the run in the background, then poll with single
   `sleep 270 && echo keepalive` ticks (one per command, no loops) and check the run
   between ticks; never end your turn while a test run is still going." Read-only
   review prompts keep "Do not use the manual-keepalive skill or any sleep loops."
