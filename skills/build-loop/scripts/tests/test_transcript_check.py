"""Tests for scripts/transcript-check (W47-T pilot). Run: python3 -I -m unittest discover -s scripts/tests

Pilot rules: one or two cases per rule on small synthetic transcripts, no sweeps.
The transcript shapes below were read off real Claude Code sessions (2026-11):
a background Agent answers with "Async agent launched ... agentId: X" and finishes with a
<task-notification> user message (or a queued_command attachment when it lands mid-turn);
a delegate_task answers with {"taskId": ...} and finishes with "Delegated task <taskId> (...) [status]:".
"""
import contextlib
import importlib.machinery
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "transcript-check"
_loader = importlib.machinery.SourceFileLoader("transcript_check", str(SCRIPT))
_spec = importlib.util.spec_from_loader("transcript_check", _loader)
tc = importlib.util.module_from_spec(_spec)
_loader.exec_module(tc)


class Transcript:
    """Builds a JSONL transcript; every add_* returns the line number it wrote."""

    def __init__(self):
        self.rows, self.n = [], 0

    def add(self, obj):
        self.rows.append(obj)
        return len(self.rows)

    def tool_use(self, name, inp, tid=None):
        self.n += 1
        tid = tid or f"toolu_{self.n}"
        line = self.add({"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": tid, "name": name, "input": inp}]}})
        return line, tid

    def result(self, tid, text, tool_use_result=None, is_error=False):
        row = {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": tid, "content": [{"type": "text", "text": text}],
             "is_error": is_error}]}}
        if tool_use_result is not None:
            row["toolUseResult"] = tool_use_result
        return self.add(row)

    def say(self, text="ok"):
        return self.add({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}})

    def owner(self, text="next"):
        return self.add({"type": "user", "message": {"role": "user", "content": text}})

    def notify(self, tid, agent_id, status="completed"):
        text = (f"<task-notification>\n<task-id>{agent_id}</task-id>\n<tool-use-id>{tid}</tool-use-id>\n"
                f"<status>{status}</status>\n<summary>done</summary>\n</task-notification>")
        return self.add({"type": "user", "message": {"role": "user", "content": text}})

    def notify_attachment(self, tid, agent_id):
        text = (f"<task-notification>\n<task-id>{agent_id}</task-id>\n<tool-use-id>{tid}</tool-use-id>\n"
                "<status>completed</status>\n</task-notification>")
        return self.add({"type": "attachment", "attachment": {"type": "queued_command", "prompt": text}})

    def enqueue(self, tid, agent_id):
        text = (f"<task-notification>\n<task-id>{agent_id}</task-id>\n<tool-use-id>{tid}</tool-use-id>\n"
                "<status>completed</status>\n</task-notification>")
        return self.add({"type": "queue-operation", "operation": "enqueue", "content": text})

    def delegated_done(self, *task_ids, status="completed"):
        text = "\n".join(f"Delegated task {t} (title {t}) [{status}]:\nreport" for t in task_ids)
        return self.add({"type": "user", "message": {"role": "user", "content": text}})

    # launches
    def bg_agent(self, desc="work", agent_id=None, prompt="Implement the thing."):
        agent_id = agent_id or f"agent{self.n + 1}"
        line, tid = self.tool_use("Agent", {"description": desc, "prompt": prompt, "run_in_background": True})
        self.result(tid, f"Async agent launched successfully.\nagentId: {agent_id} (internal)",
                    {"isAsync": True, "status": "async_launched", "agentId": agent_id})
        return line, tid, agent_id

    def fg_agent(self, desc="work", prompt="Implement the thing."):
        line, tid = self.tool_use("Agent", {"description": desc, "prompt": prompt})
        end = self.result(tid, "Report text", {"status": "completed"})
        return line, end

    def delegate(self, provider, title="job", role="implementation", task="Implement the thing."):
        target = {"providerInstanceId": provider, "model": "claude-sonnet-5-5" if provider == "claudeAgent" else "gpt-6.1-sol"}
        line, tid = self.tool_use("mcp__t3-code__delegate_task",
                                  {"title": title, "role": role, "target": target, "task": task})
        task_id = f"node:delegated-task:{title.replace(' ', '-')}-{self.n}"
        self.result(tid, json.dumps({"taskId": task_id, "childThreadId": "thread:x"}))
        return line, task_id

    def bash(self, command, background=False):
        inp = {"command": command}
        if background:
            inp["run_in_background"] = True
        return self.tool_use("Bash", inp)

    def write(self, directory):
        path = Path(directory) / "t.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in self.rows) + "\n")
        return str(path)


def check(t):
    with tempfile.TemporaryDirectory() as d:
        path = t.write(d)
        findings, assumed = tc.check_file(path)
    return findings, assumed


def lines(findings, rule):
    return [f.line for f in findings if f.rule == rule]


class Cap(unittest.TestCase):
    def test_second_claude_agent_while_a_background_one_runs_is_flagged(self):
        """WHY: the cap is the most-broken rule; a background Agent is still working after its tool_result.
        catches: an implementation that treats every Agent tool_result as 'finished' (flags nothing)."""
        t = Transcript()
        t.owner("go")
        t.bg_agent("first")
        second, _, _ = t.bg_agent("second")
        t.say("waiting")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "CAP"), [second])

    def test_a_notification_frees_the_slot(self):
        """WHY: after the completion message the next launch is legal; a counter that never goes down would flag a whole session.
        catches: an implementation that counts total launches instead of unfinished ones."""
        t = Transcript()
        t.owner("go")
        _, tid, agent_id = t.bg_agent("first")
        t.notify(tid, agent_id)
        t.bg_agent("second")
        t.bash("vigil keepalive h --orchestrator", background=True)
        findings, _ = check(t)
        self.assertEqual(lines(findings, "CAP"), [])

    def test_a_queued_command_attachment_also_finishes_an_agent(self):
        """WHY: a notification that lands mid-turn is stored as a queued_command attachment, not a user message.
        catches: an implementation that reads completions from user messages only."""
        t = Transcript()
        t.owner("go")
        _, tid, agent_id = t.bg_agent("first")
        t.notify_attachment(tid, agent_id)
        t.bg_agent("second")
        t.bash("vigil keepalive h --orchestrator", background=True)
        findings, _ = check(t)
        self.assertEqual(lines(findings, "CAP"), [])

    def test_a_notification_queued_before_the_launch_counts_even_if_delivered_after(self):
        """WHY: the harness queues a completion when the agent ends and delivers it later; a launch between the two is no overlap.
        catches: an implementation that dates completions by delivery (flags a launch that overlapped nothing)."""
        t = Transcript()
        t.owner("go")
        _, tid, agent_id = t.bg_agent("first")
        t.enqueue(tid, agent_id)
        t.bg_agent("second")
        t.notify_attachment(tid, agent_id)
        t.bash("vigil keepalive h --orchestrator", background=True)
        findings, _ = check(t)
        self.assertEqual(lines(findings, "CAP"), [])

    def test_a_claude_delegate_counts_and_task_cancel_ends_it(self):
        """WHY: delegate_task to claudeAgent is a working Claude agent, and a cancelled one is no longer working.
        catches: an implementation that only looks at Agent/Task, or one that ignores task_cancel."""
        t = Transcript()
        t.owner("go")
        _, task_id = t.delegate("claudeAgent", "impl one")
        flagged, tid, agent_id = t.bg_agent("second")
        t.tool_use("mcp__t3-code__task_cancel", {"taskId": task_id})
        t.notify(tid, agent_id)
        t.bg_agent("third")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "CAP"), [flagged])

    def test_one_message_that_batches_two_completions_finishes_both(self):
        """WHY: real transcripts batch several 'Delegated task' blocks into one user message, and a report can quote another task's id.
        catches: an implementation that parses only the first block of a message."""
        t = Transcript()
        t.owner("go")
        _, first = t.delegate("claudeAgent", "impl one")
        t.delegated_done("node:some-other-task", first)
        t.delegate("claudeAgent", "impl two")
        t.bash("vigil keepalive h --orchestrator", background=True)
        findings, _ = check(t)
        self.assertEqual(lines(findings, "CAP"), [])

    def test_reviewers_have_their_own_cap_of_one(self):
        """WHY: one working agent plus one reviewer is legal; two reviewers are not.
        catches: an implementation that folds reviewers into the working cap, or never caps them."""
        t = Transcript()
        t.owner("go")
        t.bg_agent("implement")
        t.bg_agent("review round 1", prompt="Act as the review sub-agent.")
        second_reviewer, _, _ = t.bg_agent("review round 1 again", prompt="Review the diff.")
        t.bash("vigil keepalive h --orchestrator", background=True)
        findings, _ = check(t)
        self.assertEqual(lines(findings, "CAP"), [second_reviewer])
        self.assertIn("reviewer", findings[0].reason)

    def test_an_explicit_implementation_role_overrides_a_review_title(self):
        """WHY: fix-round implementers mention review in their title but still use the working-agent slot.
        catches: classifying a delegate by its title even when role says implementation."""
        t = Transcript()
        t.delegate("claudeAgent", "first worker")
        second, _ = t.delegate("claudeAgent", "Fix review round 1 findings", role="implementation")
        t.delegate("claudeAgent", "Inspect the patch", role="review")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "CAP"), [second])
        self.assertIn("working Claude agent", findings[0].reason)

    def test_codex_fan_out_is_tracked_but_never_flagged(self):
        """WHY: Sol/Codex runs are less strict than the Claude cap; four in parallel under a live hold is allowed.
        catches: an implementation that applies the cap to every delegate_task, whatever the provider."""
        t = Transcript()
        t.owner("go")
        for i in range(4):
            t.delegate("codex", f"sol job {i}")
        t.bash("vigil keepalive h --orchestrator", background=True)
        t.say("waiting")
        findings, _ = check(t)
        self.assertEqual(findings, [])

    def test_a_launch_with_no_announcement_is_assumed_finished_at_the_next_owner_message(self):
        """WHY: when no completion shows up anywhere, a launch must not block the cap for the rest of the file.
        catches: an implementation that keeps such a launch open forever (flags the next turn's launch)."""
        t = Transcript()
        t.owner("go")
        t.bg_agent("lost")
        t.bash("vigil keepalive h --orchestrator", background=True)
        t.owner("next")
        t.bg_agent("fresh")
        t.bash("vigil keepalive h --orchestrator", background=True)
        findings, assumed = check(t)
        self.assertEqual(lines(findings, "CAP"), [])
        self.assertEqual(assumed, 1)  # 'lost'; 'fresh' has no later owner message


class AsyncDetection(unittest.TestCase):
    def test_a_foreground_agent_whose_report_quotes_the_async_phrase_still_ends_at_its_result(self):
        """WHY: W49 r1 S1, a reviewer of transcript-check quoted "Async agent launched" in its report; the
        text test marked that finished foreground agent unfinished for the rest of the session (cap-guard denied).
        catches: deciding async from a substring of the report instead of the structured toolUseResult."""
        t = Transcript()
        t.owner("go")
        line, tid = t.tool_use("Agent", {"description": "review", "prompt": "Review only."})
        t.result(tid, "Report: the checker reads 'Async agent launched' as async.", {"status": "completed"})
        t.fg_agent("review again", prompt="Review only.")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "CAP"), [])

    def test_without_a_structured_result_only_a_leading_phrase_means_async(self):
        """WHY: older transcripts may lack toolUseResult; the harness's async answer starts with the phrase.
        catches: dropping the text fallback (a real async agent then ends at its launch result)."""
        t = Transcript()
        t.owner("go")
        _, tid = t.tool_use("Agent", {"description": "work", "prompt": "Implement.", "run_in_background": True})
        t.result(tid, "Async agent launched successfully.\nagentId: a1 (internal)")
        second, _ = t.tool_use("Agent", {"description": "more", "prompt": "Implement."})
        findings, _ = check(t)
        self.assertEqual(lines(findings, "CAP"), [second])


class ForegroundKeepalive(unittest.TestCase):
    def test_only_a_foreground_vigil_keepalive_command_is_flagged(self):
        """WHY: a foreground keepalive is interrupted by every owner message; the same words in a grep or --help are not a wait.
        catches: a substring match on 'vigil keepalive' (flags the greps, the commit message and --help), or one that ignores run_in_background."""
        t = Transcript()
        t.owner("go")
        flagged, _ = t.bash("vigil keepalive h --orchestrator")
        t.bash("vigil keepalive h --orchestrator", background=True)
        t.bash("grep -n 'vigil keepalive' SKILL.md")
        t.bash("vigil keepalive --help")
        t.bash("git grep -n -E \"vigil (hold|wait)|vigil keepalive\" -- skills")
        t.bash("git commit -m 'note: run vigil keepalive in the background'")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "FG-KEEPALIVE"), [flagged])

    def test_a_foreground_vigil_wait_is_flagged_too(self):
        """WHY: S11, `vigil wait` is a wait like a keepalive, so run in the foreground it blocks the main session the same way.
        catches: KEEPALIVE_RE that knows only `vigil keepalive` (the foreground wait goes unreported)."""
        t = Transcript()
        t.owner("go")
        flagged, _ = t.bash("vigil wait h")
        t.bash("vigil wait h", background=True)
        findings, _ = check(t)
        self.assertEqual(lines(findings, "FG-KEEPALIVE"), [flagged])

    def test_a_delegated_child_may_wait_in_the_foreground_with_bash_too(self):
        """WHY: S13, SKILL.md §10 says "Only subagents call it in the foreground"; the child exemption covered the MCP call only.
        catches: an exemption that skips the MCP form but still flags a Bash `vigil keepalive`/`vigil wait` in a child."""
        t = Transcript()
        t.owner("Act as the implementation sub-agent for this task.  Do the work.")
        t.bash("vigil keepalive h")
        t.bash("vigil wait h")
        t.tool_use("mcp__vigil__keepalive", {"watch_id": "h"})
        self.assertEqual(lines(check(t)[0], "FG-KEEPALIVE"), [])

    def test_a_harness_sidechain_log_may_wait_in_the_foreground(self):
        """WHY: S13, harness sub-agent logs (subagents/*.jsonl) have isSidechain true on every record and do not start with
        "Act as the ... sub-agent"; sweeping them flagged 152 waits that are not breaks.
        catches: a child test that reads only the first message text."""
        t = Transcript()
        t.owner("Review the diff in scripts/.")
        t.bash("vigil keepalive h")
        t.tool_use("mcp__vigil__keepalive", {"watch_id": "h"})
        for row in t.rows:
            row["isSidechain"] = True
        self.assertEqual(lines(check(t)[0], "FG-KEEPALIVE"), [])
        main = Transcript()
        main.owner("Review the diff in scripts/.")
        flagged, _ = main.bash("vigil keepalive h")
        self.assertEqual(lines(check(main)[0], "FG-KEEPALIVE"), [flagged])


class OwnerDecisions(unittest.TestCase):
    """Owner 2026-11-14 (via the orchestrator): the MCP keepalive tool blocks a main session like a foreground
    Bash call; a manual sleep tick is the allowed backup hold, reported apart from NO-HOLD."""

    def test_an_mcp_keepalive_in_a_main_session_is_flagged_but_not_in_a_delegated_child(self):
        """WHY: every owner message interrupts a foreground MCP keepalive in a main session; a delegated child has no
        background wake and must wait in the foreground (SKILL.md §10).
        catches: flagging the MCP call everywhere, or nowhere."""
        main = Transcript()
        main.owner("go")
        flagged, _ = main.tool_use("mcp__vigil__keepalive", {"watch_id": "h", "orchestrator": True})
        child = Transcript()
        child.owner("Act as the implementation sub-agent for this task.  Do the work.")
        child.tool_use("mcp__vigil__keepalive", {"watch_id": "h"})
        self.assertEqual(lines(check(main)[0], "FG-KEEPALIVE"), [flagged])
        self.assertEqual(lines(check(child)[0], "FG-KEEPALIVE"), [])

    def test_a_manual_tick_running_at_a_turn_end_is_manual_tick_not_no_hold(self):
        """WHY: the manual tick holds the session (allowed when vigil fails), so it is not a NO-HOLD break, but its use
        is worth counting apart.
        catches: ignoring ticks (NO-HOLD), or counting a tick as a vigil hold (no report at all)."""
        t = Transcript()
        t.owner("go")
        t.bg_agent("work")
        t.bash("sleep 270 && echo keepalive", background=True)
        last = t.say("waiting")
        t.owner("status?")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [])
        self.assertEqual(lines(findings, "MANUAL-TICK"), [last])

    def test_a_tick_that_already_fired_is_no_hold(self):
        """WHY: a tick holds only until it fires; one that fired before the turn ended holds nothing.
        catches: treating any tick started earlier as running forever."""
        t = Transcript()
        t.owner("go")
        t.bg_agent("work")
        _, tick = t.bash("sleep 270 && echo keepalive", background=True)
        t.notify(tick, "shell1")
        last = t.say("waiting")
        t.owner("status?")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [last])
        self.assertEqual(lines(findings, "MANUAL-TICK"), [])

    def test_a_tick_counts_only_within_its_sleep_plus_a_minute(self):
        """WHY: S12b, a tick with no completion record is not running for the rest of the file: `sleep 270` started 54 hours
        earlier holds nothing. It counts while the turn end is within N + 60 s of its start, or a timestamp is missing.
        catches: a tick that never expires when its completion record is absent (a lost tick hides every later NO-HOLD)."""
        for gap, rule in ((300, "MANUAL-TICK"), (330, "MANUAL-TICK"), (331, "NO-HOLD"), (54 * 3600, "NO-HOLD")):
            with self.subTest(gap=gap):
                t = Transcript()
                t.owner("go")
                t.bg_agent("work")
                t.bash("sleep 270 && echo keepalive", background=True)
                t.rows[-1]["timestamp"] = "2026-11-13T00:00:00Z"
                last = t.say("waiting")
                t.owner("status?")
                t.rows[-1]["timestamp"] = datetime.fromtimestamp(
                    datetime(2026, 11, 13, tzinfo=timezone.utc).timestamp() + gap, timezone.utc).isoformat()
                findings, _ = check(t)
                self.assertEqual(lines(findings, rule), [last])
                other = "NO-HOLD" if rule == "MANUAL-TICK" else "MANUAL-TICK"
                self.assertEqual(lines(findings, other), [])


class NoHold(unittest.TestCase):
    def test_an_owner_message_after_a_tool_result_does_not_end_the_turn(self):
        """WHY: S1, queued owner steering after a launch result arrives while the assistant is still working.
        catches: treating every owner message as a turn end and flagging the launch itself."""
        t = Transcript()
        t.owner("go")
        t.bg_agent("work")
        t.owner("also research this")
        last = t.say("I will wait for it.")
        t.owner("status?")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [last])

    def test_a_request_interrupted_message_is_not_an_owner_turn_end(self):
        """WHY: S1, the harness writes interruption markers as user messages without an owner reply.
        catches: counting '[Request interrupted by user]' as an owner message."""
        t = Transcript()
        t.bg_agent("work")
        t.say("waiting")
        t.owner("[Request interrupted by user]")
        findings, assumed = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [])
        self.assertEqual(assumed, 0)

    def test_an_owner_message_after_a_tool_call_is_still_mid_turn(self):
        """WHY: S1 requires an assistant reply without tool_use, even when the tool result is missing.
        catches: accepting any preceding assistant record as a turn end."""
        t = Transcript()
        t.bg_agent("work")
        t.bash("git status")
        t.add({"type": "attachment", "attachment": {"type": "hook"}})
        t.owner("also check the docs")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [])

    def test_a_turn_ending_with_a_background_agent_and_no_hold_is_flagged(self):
        """WHY: with nothing holding the session, the turn ends and nothing wakes the agent for the result.
        catches: an implementation that never inspects unfinished launches at a turn end."""
        t = Transcript()
        t.owner("go")
        t.bg_agent("work")
        last = t.say("I will wait for it.")
        t.owner("status?")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [last])

    def test_a_background_keepalive_started_in_the_turn_is_a_hold(self):
        """WHY: `vigil keepalive` in the background is the hold the rule asks for.
        catches: an implementation that ignores holds, or one that requires the hold to be a foreground call."""
        t = Transcript()
        t.owner("go")
        t.bg_agent("work")
        t.bash("vigil keepalive h --orchestrator", background=True)
        t.say("waiting")
        t.owner("status?")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [])

    def test_a_keepalive_from_an_earlier_turn_still_running_is_a_hold(self):
        """WHY: the rule says 'started in that turn or still running'; one keepalive can span several owner messages.
        catches: an implementation that only looks at the current turn."""
        t = Transcript()
        t.owner("go")
        t.bg_agent("work")
        t.bash("vigil keepalive h --orchestrator", background=True)
        t.owner("how is it going?")
        t.say("still running")
        t.owner("and now?")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [])

    def test_a_keepalive_that_already_returned_is_not_a_hold(self):
        """WHY: a finished keepalive holds nothing; the next one has to be started on the return.
        catches: an implementation that treats 'ever started a keepalive' as 'holding'."""
        t = Transcript()
        t.owner("go")
        t.bg_agent("work")
        _, ka = t.bash("vigil keepalive h --orchestrator", background=True)
        t.notify(ka, "bka")
        last = t.say("done, doing other things")
        t.owner("status?")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [last])

    def test_a_live_hold_alone_does_not_hold_the_session(self):
        """WHY: S12a, a hold is state inside vigil; only a background keepalive/wait returning wakes the session. After
        the keepalive's completion notice, the live hold passes nothing: the lapse is "on each return, start the next".
        catches: an implementation that treats a live `vigil hold` (CLI or MCP) as holding without a running wait."""
        for cli in (True, False):
            with self.subTest(cli=cli):
                t = Transcript()
                t.owner("go")
                if cli:
                    t.bash("vigil hold --id w-1")
                else:
                    t.tool_use("mcp__vigil__hold", {"id": "w-1"})
                t.bg_agent("work")
                _, ka = t.bash("vigil keepalive w-1 --orchestrator", background=True)
                t.notify(ka, "bka")
                last = t.say("done, doing other things")
                t.owner("status?")
                findings, _ = check(t)
                self.assertEqual(lines(findings, "NO-HOLD"), [last])

    def test_a_hold_with_no_keepalive_at_all_is_no_hold(self):
        """WHY: S12a, the plain shape of the lapse: hold made once, agent launched, turn ended, nothing running.
        catches: the same hold-alone pass, in the case with no keepalive ever started."""
        t = Transcript()
        t.owner("go")
        t.tool_use("mcp__vigil__hold", {"label": "session"})
        t.bg_agent("work")
        last = t.say("waiting")
        t.owner("status?")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [last])

    def test_a_background_vigil_wait_is_a_hold_like_a_keepalive(self):
        """WHY: S11, `vigil wait <id>` in the background wakes the session when it returns exactly like a keepalive; the
        three largest sessions ran it 132 times and were reported NO-HOLD.
        catches: KEEPALIVE_RE that knows only `vigil keepalive`."""
        t = Transcript()
        t.owner("go")
        t.bg_agent("work")
        t.bash("vigil wait h", background=True)
        t.say("waiting")
        t.owner("status?")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [])
        self.assertEqual(lines(findings, "MANUAL-TICK"), [])

    def test_a_vigil_wait_that_already_returned_is_not_a_hold(self):
        """WHY: S11, a returned `vigil wait` holds nothing, the same as a returned keepalive.
        catches: counting any `vigil wait` ever started as holding."""
        t = Transcript()
        t.owner("go")
        t.bg_agent("work")
        _, wait = t.bash("vigil wait h", background=True)
        t.notify(wait, "bw")
        last = t.say("done, doing other things")
        t.owner("status?")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [last])

    def test_cancel_ends_only_the_named_hold_and_a_new_hold_can_be_armed(self):
        """WHY: S2, a cancelled hold cannot cover later turns, but cancelling another watch must not end it.
        catches: ignoring CLI/MCP cancel, cancelling every hold, or keeping a cancelled id dead after rearming."""
        for cli in (True, False):
            with self.subTest(cli=cli):
                t = Transcript()
                t.bg_agent("work")
                t.bash("vigil hold --id h")
                t.bash("vigil keepalive h --orchestrator", background=True)
                if cli:
                    t.bash("vigil cancel other")
                else:
                    t.tool_use("mcp__vigil__watch_cancel", {"watch_id": "other"})
                t.say("still held")
                t.owner("status?")
                if cli:
                    t.bash("vigil cancel h")
                else:
                    t.tool_use("mcp__vigil__watch_cancel", {"watch_id": "h"})
                last = t.say("unheld")
                t.owner("status?")
                t.bash("vigil hold --id h")
                t.bash("vigil keepalive h --orchestrator", background=True)
                t.say("held again")
                t.owner("status?")
                findings, _ = check(t)
                self.assertEqual(lines(findings, "NO-HOLD"), [last])

    def test_a_hold_expires_at_its_deadline_using_record_timestamps(self):
        """WHY: S2, a hold created at 00:00:00 for 10 seconds is live at :09 and expired at :10.
        catches: immortal holds, ignoring MCP deadline_s, or comparing the deadline with the host clock."""
        for command in ("vigil hold --id h --deadline-s 10", "vigil hold --id h --deadline-s=10", None):
            with self.subTest(command=command):
                t = Transcript()
                t.bg_agent("work")
                if command:
                    t.bash(command)
                else:
                    t.tool_use("mcp__vigil__hold", {"id": "h", "deadline_s": 10})
                t.rows[-1]["timestamp"] = "2026-11-13T00:00:00Z"
                t.bash("vigil keepalive h --orchestrator", background=True)
                t.say("held")
                t.owner("status?")
                t.rows[-1]["timestamp"] = "2026-11-13T00:00:09Z"
                last = t.say("expired")
                t.owner("status?")
                t.rows[-1]["timestamp"] = "2026-11-12T17:00:10-07:00"
                findings, _ = check(t)
                self.assertEqual(lines(findings, "NO-HOLD"), [last])

    def test_hold_help_does_not_create_an_immortal_hold(self):
        """WHY: S2's real deadline repro first runs hold --help, which must not mask the later hold's expiry.
        catches: treating a successful help command as creation of a bare seven-day hold."""
        for flag in ("--help", "-h"):
            with self.subTest(flag=flag):
                t = Transcript()
                t.bg_agent("work")
                t.bash(f"vigil hold {flag} 2>&1 | head -30")
                t.rows[-1]["timestamp"] = "2026-11-13T00:00:00Z"
                last = t.say("unheld")
                t.owner("status?")
                t.rows[-1]["timestamp"] = "2026-11-13T00:00:10Z"
                findings, _ = check(t)
                self.assertEqual(lines(findings, "NO-HOLD"), [last])

    def test_vigil_cold_ends_a_hold(self):
        """WHY: going cold releases a hold; its earlier creation must not cover the next turn.
        catches: ignoring COLD_RE or the MCP cold tool."""
        for cli in (True, False):
            with self.subTest(cli=cli):
                t = Transcript()
                t.bg_agent("work")
                t.bash("vigil hold --id h")
                if cli:
                    t.bash("vigil cold h")
                else:
                    t.tool_use("mcp__vigil__cold", {"watch_ids": ["h"]})
                last = t.say("unheld")
                t.owner("status?")
                findings, _ = check(t)
                self.assertEqual(lines(findings, "NO-HOLD"), [last])

    def test_a_returned_keepalive_release_event_ends_its_hold(self):
        """WHY: S2, all items ending releases the hold even without cold or cancel.
        catches: treating a hold as live after a keepalive result reports 'hold released'."""
        for cli in (True, False):
            with self.subTest(cli=cli):
                t = Transcript()
                t.bg_agent("work")
                t.bash("vigil hold --id h")
                if cli:
                    _, ka = t.bash("vigil keepalive h --orchestrator", background=True)
                else:
                    _, ka = t.tool_use("mcp__vigil__keepalive", {"watch_id": "h"})
                t.result(ka, '{"status":"fired","events":[{"watch_id":"h","input":"hold",'
                             '"summary":"hold released: 1 item ended (build)"}]}')
                last = t.say("unheld")
                t.owner("status?")
                findings, _ = check(t)
                self.assertEqual(lines(findings, "NO-HOLD"), [last])

    def test_a_background_keepalive_cannot_outlive_its_cancelled_or_expired_hold(self):
        """WHY: S2, a stale keepalive with no completion notice must not resurrect an ended hold.
        catches: checking hold deadlines/cancellation but accepting its old background keepalive forever."""
        for cancel in (True, False):
            with self.subTest(cancel=cancel):
                t = Transcript()
                t.bg_agent("work")
                t.bash("vigil hold --id h --deadline-s 10")
                t.rows[-1]["timestamp"] = "2026-11-13T00:00:00Z"
                t.bash("vigil keepalive h --orchestrator", background=True)
                if cancel:
                    t.bash("vigil cancel h")
                last = t.say("unheld")
                t.owner("status?")
                t.rows[-1]["timestamp"] = "2026-11-13T00:00:10Z"
                findings, _ = check(t)
                self.assertEqual(lines(findings, "NO-HOLD"), [last])

    def test_a_release_in_task_output_retires_a_hold_with_a_generated_id(self):
        """WHY: S2, background Bash returns a task id first; its release event is read later through TaskOutput.
        catches: reading only the initial keepalive result, or ignoring a hold id supplied by its result."""
        t = Transcript()
        t.bg_agent("work")
        _, hold = t.tool_use("mcp__vigil__hold", {"label": "session"})
        t.result(hold, '{"watch_id":"generated","status":"pending"}')
        _, ka = t.bash("vigil keepalive generated --orchestrator", background=True)
        t.result(ka, "Command running in background with ID: bka", {"backgroundTaskId": "bka"})
        _, output = t.tool_use("TaskOutput", {"task_id": "bka", "block": True})
        t.result(output, '<output>{"status":"fired","events":[{"watch_id":"generated",'
                         '"summary":"hold released: 1 item ended (build)"}]}</output>')
        last = t.say("unheld")
        t.owner("status?")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [last])

    def test_a_codex_run_left_unheld_is_flagged_too(self):
        """WHY: Codex runs escape the cap, not the hold: an unwatched Sol run is just as unattended.
        catches: an implementation that drops Codex launches from the tracked set."""
        t = Transcript()
        t.owner("go")
        t.delegate("codex", "sol review", role="review")
        last = t.say("waiting")
        t.owner("status?")
        findings, _ = check(t)
        self.assertEqual(lines(findings, "NO-HOLD"), [last])


class CleanAndCli(unittest.TestCase):
    def clean(self):
        t = Transcript()
        t.owner("build it")
        t.fg_agent("red tests")
        t.fg_agent("green phase")
        _, tid, agent_id = t.bg_agent("fix round")
        _, ka = t.bash("vigil keepalive h --orchestrator", background=True)
        t.notify(ka, "bka")
        t.notify(tid, agent_id)
        t.delegate("claudeAgent", "last fix")
        t.bash("vigil keepalive h --orchestrator", background=True)
        t.owner("thanks")
        return t

    def test_a_clean_transcript_has_no_findings(self):
        """WHY: the checker earns trust only if a well-run session reports nothing: sequential foreground agents, a background
        agent finished before the next launch, a hold across the owner message.
        catches: an implementation that flags every launch, or every owner message."""
        findings, assumed = check(self.clean())
        self.assertEqual(findings, [])

    def test_report_lines_json_and_exit_status(self):
        """WHY: the report is read by people and scripts; it is a report, so findings never change the exit status.
        catches: an implementation that exits 1 on findings, drops the line number, or emits counts the lines do not match."""
        t = Transcript()
        t.owner("go")
        flagged, _ = t.bash("vigil keepalive h --orchestrator")
        with tempfile.TemporaryDirectory() as d:
            path = t.write(d)
            plain = subprocess.run([sys.executable, "-I", str(SCRIPT), path, "/nonexistent.jsonl"],
                                   capture_output=True, text=True)
            as_json = subprocess.run([sys.executable, "-I", str(SCRIPT), "--json", path], capture_output=True, text=True)
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertIn(f"{path}:{flagged}: FG-KEEPALIVE:", plain.stdout)
        self.assertIn("FG-KEEPALIVE=1", plain.stdout)
        self.assertIn("unreadable", plain.stdout)
        report = json.loads(as_json.stdout)
        self.assertEqual(as_json.returncode, 0)
        self.assertEqual(report["counts"], {"CAP": 0, "FG-KEEPALIVE": 1, "NO-HOLD": 0, "MANUAL-TICK": 0})
        self.assertEqual(report["findings"][0]["line"], flagged)

    def test_findings_copied_into_a_continued_session_are_counted_once(self):
        """WHY: a continued session copies the earlier history, uuids and tool_use ids included; the same call must not be
        reported once per file.
        catches: summing per-file findings without deduplicating by (rule, tool_use id)."""
        t = Transcript()
        t.owner("go")
        t.bg_agent("first")
        t.bg_agent("second")
        t.bash("vigil keepalive h --orchestrator")
        t.tool_use("mcp__vigil__keepalive", {"watch_id": "h", "orchestrator": True})
        t.say("waiting")
        t.owner("status?")
        for i, row in enumerate(t.rows):
            row["uuid"] = f"u{i}"
        with tempfile.TemporaryDirectory() as d:
            one = t.write(d)
            other = Path(d) / "copy.jsonl"
            other.write_text(Path(one).read_text())
            alone = subprocess.run([sys.executable, "-I", str(SCRIPT), "--json", one], capture_output=True, text=True)
            both = subprocess.run([sys.executable, "-I", str(SCRIPT), "--json", one, str(other)], capture_output=True, text=True)
        self.assertEqual(json.loads(both.stdout)["counts"], json.loads(alone.stdout)["counts"])
        self.assertEqual(json.loads(alone.stdout)["counts"], {"CAP": 1, "FG-KEEPALIVE": 2, "NO-HOLD": 1, "MANUAL-TICK": 0})


if __name__ == "__main__":
    unittest.main()
