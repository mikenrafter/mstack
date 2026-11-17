"""RED tests for bin/usage-budget-probe (spec D1, R7). Lives here because
`unittest discover -s skills/build-loop/scripts/tests` is the only discovery the module has.
The probe is Python 3 stdlib and runs `uw status --json` from PATH. These tests put a fake `uw` script
first (and only) on PATH, so the real uw is never called and no env override exists. The fake logs its
arguments. The document shape was captured from the real `uw status --json` on 2026-11-13 (nine-digit
fractional timestamps, `provider` is a string or {"Other": name}, windows carry pct/exceeded/window)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROBE = Path(__file__).resolve().parents[4] / "bin" / "usage-budget-probe"

T_OK = "2026-11-13T08:59:04.436505623Z"
T_OLD = "2026-10-24T10:51:56.330390623Z"
T_NEW = "2026-11-13T08:59:02.675796412Z"


def window(pct, exceeded=False):
    return {"pct": pct, "exceeded": exceeded, "window": {"Rolling": {"minutes": 300}}}


def healthy(provider):
    return {"provider": provider, "consecutive_failures": 0, "last_error": None,
            "last_attempt_at": T_OK, "last_success_at": T_OK}


def failing(provider, error="adapter error: missing window duration"):
    return {"provider": provider, "consecutive_failures": 2285, "last_error": error,
            "last_attempt_at": T_NEW, "last_success_at": T_OLD}


def doc(usage, status):
    """usage: {provider: [windows]}; status: provider_status entries. An unrelated {"Other"} provider is always present."""
    return {"keepalive_active_count": 0, "last_updated": T_OK,
            "provider_status": status + [{**failing({"Other": "t3code"}, "unsupported"), "last_success_at": None}],
            "usage": [{"provider": p, "plan": "Max", "account": None, "windows": w} for p, w in usage.items()]}


class Probe(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.bin = Path(self.tmp.name) / "bin"
        self.bin.mkdir()
        self.log = Path(self.tmp.name) / "args.log"

    def fake_uw(self, document=None, text=None, code=0):
        body = text if text is not None else json.dumps(document)
        data = Path(self.tmp.name) / "uw-out.json"
        data.write_text(body)
        script = self.bin / "uw"
        script.write_text(f"#!{sys.executable}\nimport sys, json\n"
                          f"open({str(self.log)!r}, 'a').write(json.dumps(sys.argv[1:]) + '\\n')\n"
                          f"sys.stdout.write(open({str(data)!r}).read())\n"
                          f"sys.stderr.write('uw: boom\\n' if {code} else '')\n"
                          f"sys.exit({code})\n")
        script.chmod(0o755)

    def run_probe(self, provider, extra_env=None, window_name=None):
        env = {"PATH": str(self.bin), **(extra_env or {})}  # no UW_STATUS_JSON, no real uw
        args = [sys.executable, "-I", str(PROBE), provider]
        if window_name is not None:
            args += ["--window", window_name]
        return subprocess.run(args, env=env,
                              capture_output=True, text=True, timeout=30)

    def probe(self, provider, document, **kw):
        self.fake_uw(document)
        return self.run_probe(provider, **kw)

    def assertAvailable(self, r, pct_left, on_credits):
        self.assertEqual(r.returncode, 0, r.stderr)
        result = json.loads(r.stdout)
        self.assertEqual({key: result[key] for key in ("pct_left", "on_credits")},
                         {"pct_left": pct_left, "on_credits": on_credits})

    def assertUnavailable(self, r, *reason):
        self.assertEqual(r.returncode, 3, (r.stdout, r.stderr))
        self.assertIn("unavailable:", r.stderr)
        for word in reason:
            self.assertIn(word, r.stderr)
        self.assertEqual(r.stdout.strip(), "")

    # ---- available: the number ----

    def test_pct_left_is_100_minus_the_highest_window_wherever_it_sits(self):
        # why: pct_left feeds the claude-budget advisory (pct <= 15 means low); the worst window decides (D1, S24).
        # proves: D1 (S24)
        # catches: using the first window (69), the last (60), or the average (62.2) instead of the max (85.5 -> 14.5)
        for pcts in ([85.5, 31.0, 40.0], [31.0, 85.5, 40.0], [31.0, 40.0, 85.5]):
            with self.subTest(pcts=pcts):
                r = self.probe("ClaudeCode", doc({"ClaudeCode": [window(p) for p in pcts]}, [healthy("ClaudeCode")]))
                self.assertAvailable(r, 14.5, False)  # 100 - 85.5

    def test_a_single_window_preserves_compatibility_keys_and_exit_0(self):
        # why: one window is the common case; the original keys must remain (D1, S26).
        # proves: D1 (S26)
        # catches: an implementation that needs two windows, drops the original keys, or prints non-JSON text
        r = self.probe("ClaudeCode", doc({"ClaudeCode": [window(46.0)]}, [healthy("ClaudeCode")]))
        self.assertAvailable(r, 54.0, False)  # 100 - 46
        self.assertTrue({"pct_left", "on_credits"} <= set(json.loads(r.stdout)))

    def test_exceeded_flag_on_a_later_non_max_window_means_on_credits(self):
        # why: any exceeded window means Claude spends credits, wherever it sits (D1, B5, S25).
        # proves: D1 (S25)
        # catches: reading only the first window's flag, or only the max-pct window's flag, or a constant False
        for flags in ((False, False, True), (True, False, False)):
            with self.subTest(flags=flags):
                w = [window(20.0, flags[0]), window(60.0, flags[1]), window(30.0, flags[2])]
                self.assertAvailable(self.probe("ClaudeCode", doc({"ClaudeCode": w}, [healthy("ClaudeCode")])), 40.0, True)

    def test_healthy_codex_next_to_claudecode_is_read_on_its_own(self):
        # why: both providers are asked for by name; a healthy Codex yields its own number (D1, S27).
        # proves: D1 (S27)
        # catches: a probe that only knows ClaudeCode, or takes the max over all providers' windows
        d = doc({"ClaudeCode": [window(10.0)], "Codex": [window(70.0, True), window(25.0)]},
                [healthy("ClaudeCode"), healthy("Codex")])
        self.assertAvailable(self.probe("Codex", d), 30.0, True)  # 100 - 70
        self.assertAvailable(self.probe("ClaudeCode", d), 90.0, False)  # Codex does not leak in

    def test_probe_runs_uw_status_json_from_path_and_ignores_an_env_override(self):
        # why: R7: the probe's only input is `uw status --json` on PATH; there is no env hook (S24, S28).
        # proves: R7
        # catches: a probe that runs another uw subcommand, calls uw twice, or reads UW_STATUS_JSON
        decoy = Path(self.tmp.name) / "decoy.json"
        decoy.write_text(json.dumps(doc({"ClaudeCode": [window(99.0)]}, [healthy("ClaudeCode")])))
        self.fake_uw(doc({"ClaudeCode": [window(46.0)]}, [healthy("ClaudeCode")]))
        r = self.run_probe("ClaudeCode", extra_env={"UW_STATUS_JSON": str(decoy)})
        self.assertAvailable(r, 54.0, False)
        calls = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertEqual(calls, [["status", "--json"]])

    # ---- available: past failure does not matter when the latest attempt succeeded ----

    def test_provider_that_failed_before_but_whose_latest_attempt_succeeded_is_available(self):
        # why: R7: only the latest attempt counts; a stale last_error or old failure count must not hide good data (S28).
        # proves: R7 (S28)
        # catches: treating consecutive_failures > 0 or any last_error as failing, or comparing timestamps as strings of different lengths
        w = {"ClaudeCode": [window(46.0)]}
        cases = {
            "error cleared": {**healthy("ClaudeCode")},
            "stale error, success == attempt (nine-digit equal)": {**healthy("ClaudeCode"), "last_error": "old error",
                                                                  "consecutive_failures": 3},
            "stale error, success after attempt": {**healthy("ClaudeCode"), "last_error": "old error",
                                                  "last_attempt_at": "2026-11-13T08:59:04.4Z",
                                                  "last_success_at": "2026-11-13T08:59:04.436505623Z"},
        }
        for label, status in cases.items():
            with self.subTest(label):
                self.assertAvailable(self.probe("ClaudeCode", doc(w, [status])), 54.0, False)

    # ---- unavailable: exit 3 with `unavailable: <reason>` on stderr, nothing on stdout ----

    def test_latest_attempt_failed_is_unavailable_with_the_adapter_error(self):
        # why: a failing adapter (Codex since 2026-10-24) must read as `unavailable`, not as a stale number (D1, D3, R7).
        # proves: D1, R7
        # catches: printing the last known usage (pct 47) with exit 0, or exiting 1 instead of 3
        d = doc({"Codex": [window(47.0, True)]}, [failing("Codex")])
        self.assertUnavailable(self.probe("Codex", d), "missing window duration")

    def test_failed_attempt_with_no_success_ever_is_unavailable(self):
        # why: last_success_at null means never worked; a null must not crash or count as success (R7).
        # proves: R7
        # catches: comparing a null timestamp (TypeError, exit 1) or treating null as success
        bad = {**failing("Codex", "unsupported"), "last_success_at": None}
        self.assertUnavailable(self.probe("Codex", doc({"Codex": [window(47.0)]}, [bad])), "unsupported")

    def test_provider_absent_or_without_windows_is_unavailable(self):
        # why: nothing to measure is not "100% left" (R7, S26).
        # proves: R7 (S26)
        # catches: defaulting the max of no windows to 0 and printing pct_left 100
        absent = doc({"ClaudeCode": [window(10.0)]}, [healthy("ClaudeCode"), healthy("Codex")])
        self.assertUnavailable(self.probe("Codex", absent))
        empty = doc({"Codex": []}, [healthy("Codex")])
        self.assertUnavailable(self.probe("Codex", empty))

    def test_uw_missing_from_path_is_unavailable(self):
        # why: R7: uw missing reads as unavailable, not as a crash (S28).
        # proves: R7 (S28)
        # catches: an uncaught FileNotFoundError (exit 1, traceback) or a fallback to a canned number
        r = self.run_probe("ClaudeCode")  # bin/ is empty: no uw
        self.assertUnavailable(r)

    def test_uw_exiting_nonzero_is_unavailable(self):
        # why: R7: a failing uw (daemon down) reads as unavailable even if it printed a parseable document (S28).
        # proves: R7 (S28)
        # catches: ignoring uw's exit code and trusting its stdout
        self.fake_uw(doc({"ClaudeCode": [window(46.0)]}, [healthy("ClaudeCode")]), code=1)
        self.assertUnavailable(self.run_probe("ClaudeCode"))


    def test_each_provider_is_judged_by_its_own_status_entry_in_either_order(self):
        # why: a probe asked about Codex must read Codex's status entry, not the first one (R7, Sol r2 S31).
        # proves: R7 (S31)
        # catches: `status = document["provider_status"][0]` while windows are picked by provider
        w = {"ClaudeCode": [window(47.0)], "Codex": [window(30.0)]}
        for order in ((healthy("ClaudeCode"), failing("Codex")), (failing("Codex"), healthy("ClaudeCode"))):
            with self.subTest(first=order[0]["provider"]):
                d = doc(w, list(order))
                self.assertUnavailable(self.probe("Codex", d), "missing window duration")
                self.assertAvailable(self.probe("ClaudeCode", d), 53.0, False)
        for order in ((healthy("Codex"), failing("ClaudeCode")), (failing("ClaudeCode"), healthy("Codex"))):
            with self.subTest(first=str(order[0]["provider"]), flipped=True):
                d = doc(w, list(order))
                self.assertUnavailable(self.probe("ClaudeCode", d), "missing window duration")
                self.assertAvailable(self.probe("Codex", d), 70.0, False)


    def test_a_provider_listed_twice_is_judged_by_its_latest_attempt(self):
        # why: after a daemon restart `uw status` lists a stale failing entry and a fresh healthy one for the
        #      same provider (seen live 2026-11-13); only the latest attempt says whether the adapter works.
        # proves: R7 (live finding after deploy 2)
        # catches: taking the first matching status entry, or failing if any entry failed
        stale = failing("Codex")
        fresh = {**healthy("Codex"), "last_attempt_at": "2026-11-13T15:16:07.000000001Z",
                 "last_success_at": "2026-11-13T15:16:07.000000001Z", "consecutive_failures": 0}
        w = {"Codex": [window(91.0)]}
        for order in ((stale, fresh), (fresh, stale)):
            with self.subTest(first_failing=order[0] is stale):
                self.assertAvailable(self.probe("Codex", doc(w, list(order))), 9.0, False)
        newer_failure = {**failing("Codex"), "last_attempt_at": "2026-11-13T15:20:00.000000000Z"}
        self.assertUnavailable(self.probe("Codex", doc(w, [fresh, newer_failure])), "missing window duration")
        never = {**healthy("Codex"), "last_attempt_at": None, "last_success_at": None}
        self.assertAvailable(self.probe("Codex", doc(w, [never, fresh])), 9.0, False)  # an entry with no attempt never wins


    def fixture(self, provider):
        return json.loads((Path(__file__).parent / "fixtures/usage-budget" / f"{provider}.json").read_text())

    def test_claude_fixture_reports_both_windows_and_preserves_resets(self):
        # WHY/CLAIM(budget-windows): 37% in 5h and 86% weekly are both correct.
        # catches: dropping one window, swapping names, or inventing reset times.
        reply = self.probe("ClaudeCode", self.fixture("ClaudeCode"))
        self.assertAvailable(reply, 37, False)
        self.assertEqual(json.loads(reply.stdout)["windows"], [
            {"name": "5h", "minutes": 300, "window": {"Rolling": {"minutes": 300}},
             "pct_left": 37, "on_credits": False, "resets_at": "2026-11-15T14:00:00Z"},
            {"name": "weekly", "minutes": 10080, "window": {"Rolling": {"minutes": 10080}},
             "pct_left": 86, "on_credits": False, "resets_at": "2026-11-21T07:00:00Z"}])

    def test_selection_follows_duration_in_either_order_and_scopes_credits(self):
        # WHY/CLAIM(budget-windows): weekly headroom must not inherit the 5h limit or credits.
        # catches: selecting by position or continuing to use all-window max/any.
        document = self.fixture("ClaudeCode")
        windows = document["usage"][0]["windows"]
        windows[0]["exceeded"] = True
        for order in (windows, list(reversed(windows))):
            document["usage"][0]["windows"] = order
            for name, pct, credits, reset in [("5h", 37, True, "2026-11-15T14:00:00Z"),
                                               ("weekly", 86, False, "2026-11-21T07:00:00Z")]:
                with self.subTest(order=order, name=name):
                    reply = self.probe("ClaudeCode", document, window_name=name)
                    self.assertAvailable(reply, pct, credits)
                    result = json.loads(reply.stdout)
                    self.assertEqual(result["name"], name)
                    self.assertEqual(result["resets_at"], reset)
                    self.assertEqual([w["name"] for w in result["windows"]], [name])

    def test_codex_fixture_has_weekly_and_no_five_hour_window(self):
        # WHY/CLAIM(budget-windows): this Codex plan has only a weekly limit.
        # catches: assuming every provider has 5h or returning the weekly value for 5h.
        document = self.fixture("Codex")
        reply = self.probe("Codex", document, window_name="weekly")
        self.assertAvailable(reply, 84, False)
        self.assertEqual(json.loads(reply.stdout)["resets_at"], "2026-11-21T07:17:04Z")
        self.assertUnavailable(self.probe("Codex", document, window_name="5h"), "no such window", "5h", "Codex")
        self.assertAvailable(self.probe("Codex", document), 84, False)

    def test_unknown_window_is_preserved_and_missing_reset_stays_null(self):
        # WHY/CLAIM(budget-windows): unknown durations/names must not masquerade as a supported limit.
        # catches: naming every rolling window 5h, or fabricating reset times.
        document = self.fixture("Codex")
        document["usage"][0]["windows"] = [
            {"window": {"Rolling": {"minutes": 60}}, "pct": 20},
            {"window": {"Custom": "daily"}, "pct": 30}]
        reply = self.probe("Codex", document)
        self.assertAvailable(reply, 70, False)
        rows = json.loads(reply.stdout)["windows"]
        self.assertEqual([row["name"] for row in rows], ["60m", "Custom:daily"])
        self.assertEqual([row["resets_at"] for row in rows], [None, None])
        self.assertUnavailable(self.probe("Codex", document, window_name="weekly"), "no such window")

    def test_empty_windows_cannot_satisfy_a_selector(self):
        # WHY/CLAIM(budget-windows): an empty provider cannot supply weekly headroom.
        # catches: a generic absence error that conceals which window was requested.
        document = self.fixture("Codex")
        document["usage"][0]["windows"] = []
        self.assertUnavailable(self.probe("Codex", document, window_name="weekly"), "no such window", "weekly")

    def test_invalid_window_metadata_is_unavailable(self):
        # WHY/CLAIM(budget-windows): invalid durations must never be assigned a supported name.
        # catches: coercing true to 1 or silently accepting missing/invalid metadata.
        for descriptor in ({}, {"Rolling": {}}, {"Rolling": {"minutes": True}},
                           {"Rolling": {"minutes": -300}}, {"Rolling": {"minutes": "300"}}):
            with self.subTest(descriptor=descriptor):
                document = self.fixture("Codex")
                document["usage"][0]["windows"][0]["window"] = descriptor
                self.assertUnavailable(self.probe("Codex", document))

if __name__ == "__main__":
    unittest.main()
