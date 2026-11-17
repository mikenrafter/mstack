---
name: handling-ambiguous-work
description: Recover a T3 thread after an explicit provider cyber error. Transfer unaffected work to the original model and provider, then independently assess the flagged request and report the outcome.
---

The owner authorized this recovery workflow. Your first responsibility is to
keep unaffected work moving, including when you decline the flagged portion.
A provider flag establishes that a session failed, not whether the underlying
task is harmful or permitted. Assess the actual request and evidence yourself.

## Preserve the work before assessing the disputed request

Read the incident manifest supplied by the daemon. Read the source with
`t3_thread_read`, paging through messages and relevant activity and expanding
truncated items. The failed session may be unable to compact. Produce a durable
handoff summary yourself from its saved transcript and latest work instead.

Recover the owner's current objective and corrections, completed and remaining
tasks, skill names and paths, applicable AGENTS.md instructions, decisions,
approval gates, artifact locations, branch/worktree, dirty files and verification
results. Read the latest child reports and identify still-running agents and
their ownership. Reuse their work; do not launch duplicates or cancel agents
merely because their parent failed. Distinguish verified facts from old reports.
Identify skills through the actual skill reads in activity as well as summaries.
Record unavailable skills and missing context explicitly; do not silently omit
them. Never copy credentials into a handoff.

Write `handoff.md` beside the incident manifest. Explain the split using actual
tasks and dependencies. Keep the original refusal and disputed request accessible
in the source thread and manifest. Do not claim to know the classifier's precise
reason unless the provider supplied it. A concise maintenance brief can omit
unrelated research details without concealing a dependency or relevant risk.

Write a separate `worker-handoff.md` for the continuation. Give it only the
concrete unaffected tasks, their necessary inputs, applicable instructions and
skills, approval gates, dependencies, output locations and acceptance criteria.
The audit handoff and worker brief have different readers. Keep the disputed
task and gray security assessment with the recovery agent. For a mixed request
for root access, CVE assessment, hostname and store size, the independent worker
gets hostname and store size; recovery owns the security assessment.

Do not embed the source transcript, refusal discussion, fallback question,
assessment or incident manifest in an independent worker's brief. Do not ask it
to read `handoff.md`, `manifest.json`, `assessment.md` or `outcome.json`. Keep
those available to the owner and recovery agent for audit. Pass required
workspace/artifact paths directly instead of sending the worker to the audit
record to discover them. Carry only relevant prior work and task-specific skills.
If a task depends on disputed work or a material risk, keep that dependency
explicit and retain the task with recovery or ask the owner; do not relabel
disputed work as routine or omit context needed to assess the worker's task.

Launch the unaffected-work continuation **before investigating the flagged
portion**, using `t3_thread_launch`:

- Use the manifest's `continuationRequestId` as `clientRequestId`. Reuse it after
  an error or lost response. Before retrying, check `continuation.json` and read
  an already recorded thread instead of creating another.
- Create a top-level thread, using the source project, exact failed-run
  `modelSelection`, source `runtimeMode` and `interactionMode`. Preserve provider
  options, including effort settings. Never substitute a provider/model.
- Bind an existing repository worktree with `workspaceStrategy` of
  `existing_worktree`; otherwise use `root`. For a source inside T3's Scratch
  directory, use `scratch: true` and omit `projectId` and `workspaceStrategy`.
  T3 rejects Scratch folders as existing Git worktrees. Transfer absolute artifact
  paths, repository locations and the original working directory in the handoff;
  files remain in those original locations. Read the launch tool's contract.
- Title it `Work continuation: <original thread title>`, using its readable title
  rather than an ID. Keep source IDs and links in the audit record. Include the task-scoped worker
  brief inline or point only to `worker-handoff.md`. Give it your contact details
  and any unresolved dependencies relevant to its work. An independent inventory
  task needs no explanation of the unrelated assessment or provider flag.
- Start its first message with `T3_RECOVERY_CHILD <continuationRequestId>`, using
  the actual manifest value. This durable marker prevents recursive recovery if
  the title changes before you record the launch response.
- Save the returned thread ID, link and run ID to `continuation.json` beside the
  manifest immediately, and announce the link to the owner. Follow the launch
  tool's returned next instruction. Unaffected work can continue independently;
  do not wait for all of it to finish before reporting your assessment.

If no unaffected work remains, still create the requested continuation, with an
honest empty-work summary and any pending integration. Tell it to end its turn
when there is nothing actionable. If launching fails, preserve the handoff and
report that exact failure. Do not claim the transfer succeeded.

## Assess and close your part

Assess the flagged task under your own applicable rules, using the original
request and refusal. Perform work you independently permit. If the evidence is
ambiguous, ask a focused question while the continuation handles independent
tasks. Do not start with a requirement to prove the original provider wrong.

If you decline, explain the scoped reason and leave the unaffected-work
continuation running. Do not try another provider or ask the continuation to do
the declined task. Never strip a refusal from context to obtain compliance.

Send a completion report through `t3_thread_send` only if the continuation needs
your deliverables to integrate its work. Include the necessary paths/commits,
verification, dependencies, relevant uncertainty and integration instructions.
Do not send the independent inventory worker security assessment prose or ask
it to reopen audit records. If no dependency exists, send no completion message;
report the assessment directly to the owner. Preserve material risks and all
approval gates when a real dependency requires context.

Write `outcome.json` beside the manifest with your continuation thread ID,
artifact paths, reason, `assessmentStatus` of `completed`, `declined` or
`needs_input`, and `integrationStatus` of `pending`, `completed` or `needs_input`.
Use top-level `status: handed_off` after dispatch while continuation results are
unverified, even when your assessment is finished or declined. Dispatch means a
thread was created; it does not prove that unaffected work or integration finished.

Use `status: completed` and `integrationStatus: completed` only after reading
the continuation's current completed run and verifying the requested deliverables.
Record that exact run ID in `verifiedContinuationRunId`. If it fails or stops,
record `status: needs_input`, `integrationStatus: needs_input` and the observed
failure. Do not retry, create another continuation or switch providers. The daemon
also checks the current continuation run, overrides early success claims when it
fails, and reports unverified completed turns as `awaiting_verification`.

Report dispatch, assessment and verified completion separately to the owner,
with both thread links. Once your part is complete or declined, go cold: end
your turn, with no polling or scheduled self-resume. You may leave integration
pending; say so. A later owner-requested check can verify results and update the
outcome. A blocked provider invocation that cannot execute this skill is a
recovery failure, not a successful handoff.
