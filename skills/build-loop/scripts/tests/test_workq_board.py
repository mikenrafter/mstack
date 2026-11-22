"""workq board: snapshot, page and hand-back command cases.

The page script is the shipped implementation of the hand-back commands, so the
command cases run that real script under node. Without node they skip, and fail
when CI is set (test-quality: silently skipped fixtures).
"""
import itertools
import json
import os
import re
import runpy
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
from pathlib import Path

from test_workq import BIN, WorkqCase

NODE = shutil.which("node")
HOSTILE = "</script><!--<script>alert(1)</script>"
FIELDS = {"n", "order", "text", "m", "status", "note", "why", "t"}


def needs_node(test):
    if NODE or os.environ.get("CI"):
        return test
    return unittest.skip("node is not installed; the page script cannot run")(test)


def state_block(html):
    match = re.search(r'<script id="workq-state" type="application/json">(.*?)</script>', html, re.S)
    assert match, "no workq-state block"
    return json.loads(match[1])


def page_script(html):
    match = re.search(r'<script id="workq-board">(.*?)</script>', html, re.S)
    assert match, "no workq-board script"
    return match[1]


class BoardCase(WorkqCase):
    def seed(self):
        """Queue [5 open, 1 open, 2 running, 3 done+note, 4 dropped+why], 1 and 2 from m1."""
        self.cli("on")
        self.hook()
        self.cli("add", "--from", "m1", "alpha", "beta")
        self.cli("add", "gamma", "delta", "epsilon")
        self.cli("start", "2")
        self.cli("done", "3", "--note", "shipped in abc123")
        self.cli("drop", "4", "--why", "deferred: budget")
        self.cli("move", "5", "--after", "0")

    def board(self, *args, code=0):
        return self.cli("board", *args, code=code)

    def page(self):
        path = self.home / "board.html"
        self.board("--html", str(path))
        return path.read_text(encoding="utf-8")

    def stored(self):
        return {p.name: p.read_bytes() for p in sorted(self.queue.iterdir())}


class BoardSnapshot(BoardCase):
    def test_json_lists_every_field_in_queue_order(self):
        """WHY/CLAIM(board-snapshot): the snapshot is the whole queue, in order, with reasons."""
        # catches: dropping done notes or drop reasons, listing in add order, hiding closed items
        self.seed()
        before = time.time()
        snapshot = json.loads(self.board("--json"))
        after = time.time()
        self.assertEqual(set(snapshot), {"workq", "generated_at", "items"})
        self.assertEqual(snapshot["workq"], 1)
        self.assertTrue(before <= snapshot["generated_at"] <= after)
        # Hand-derived: add 1..5, move 5 to the front -> order 5,1,2,3,4.
        expected = [
            (1, 5, "epsilon", None, "open", None, None),
            (2, 1, "alpha", "m1", "open", None, None),
            (3, 2, "beta", "m1", "running", None, None),
            (4, 3, "gamma", None, "done", "shipped in abc123", None),
            (5, 4, "delta", None, "dropped", None, "deferred: budget"),
        ]
        self.assertEqual(len(snapshot["items"]), 5)
        for row, (order, n, text, source, status, note, why) in zip(snapshot["items"], expected):
            self.assertEqual(set(row), FIELDS)
            self.assertEqual((row["order"], row["n"], row["text"], row["m"], row["status"],
                              row["note"], row["why"]), (order, n, text, source, status, note, why))
            self.assertIsInstance(row["t"], float)

    def test_reopen_clears_the_closing_reason(self):
        """WHY/CLAIM(board-snapshot): a reopened item must not keep a stale done note."""
        # catches: leaving note/why set after reopen or start
        self.cli("on")
        self.cli("add", "one")
        self.cli("done", "1", "--note", "first try")
        self.cli("reopen", "1")
        item = json.loads(self.board("--json"))["items"][0]
        self.assertEqual((item["status"], item["note"], item["why"]), ("open", None, None))

    def test_board_is_read_only(self):
        """WHY/CLAIM(board-readonly): looking at the board never changes the queue."""
        # catches: appending an event or touching the inbox while rendering
        self.seed()
        before = self.stored()
        self.board("--json")
        self.board()
        self.board("--html", str(self.home / "board.html"))
        self.assertEqual(self.stored(), before)
        self.cli("add", "positive control")
        self.assertNotEqual(self.stored(), before, "probe cannot see a real write")

    def test_html_writes_only_its_path(self):
        """WHY/CLAIM(board-readonly): --html touches nothing but its target."""
        # catches: writing the page into the state directory or the working directory
        self.seed()
        target = self.home / "out" / "board.html"
        target.parent.mkdir()
        before = {p for p in self.home.rglob("*")}
        self.board("--html", str(target))
        self.assertEqual({p for p in self.home.rglob("*")} - before, {target})

    def test_no_queue_and_session_rules_match_list(self):
        """WHY/CLAIM(session): board resolves the session exactly as list does."""
        # catches: creating a queue, or ignoring -s
        self.board(code=1)
        self.assertFalse(self.queue.exists())
        self.cli("-s", "explicit", "on")
        self.cli("-s", "explicit", "add", "elsewhere")
        env = {k: v for k, v in self.env.items() if k != "WORKQ_SESSION"}
        out = self.cli("-s", "explicit", "board", "--json", env=env)
        self.assertEqual([i["text"] for i in json.loads(out)["items"]], ["elsewhere"])
        self.cli("board", "--json", env=env, code=1)

    def test_plain_board_is_a_summary(self):
        """WHY/CLAIM(board-snapshot): the bare command gives counts then every item."""
        # catches: printing only open items or no counts
        self.seed()
        lines = self.board().splitlines()
        self.assertEqual(lines[0], "2 open · 1 running · 1 done · 1 dropped")
        self.assertEqual(len(lines), 6)
        self.assertRegex(lines[1], r"^#5 \[open ")
        self.assertRegex(lines[5], r"^#4 \[dropped ")


class BoardPage(BoardCase):
    def test_html_embeds_the_json_snapshot(self):
        """WHY/CLAIM(board-snapshot): the page and --json show the same queue."""
        # catches: a second serializer that drifts from --json
        self.seed()
        from_cli = json.loads(self.board("--json"))
        before = time.time()
        embedded = state_block(self.page())
        self.assertTrue(before <= embedded.pop("generated_at") <= time.time())
        from_cli.pop("generated_at")
        self.assertEqual(embedded, from_cli)
        self.assertEqual(len(embedded["items"]), 5)

    def test_hostile_text_cannot_break_out_of_the_data_block(self):
        """WHY/CLAIM(board-escape): item text is data, never markup."""
        # catches: embedding the JSON with raw '</script>' or '<!--'
        self.cli("on")
        self.cli("add", HOSTILE)
        html = self.page()
        self.assertNotIn(HOSTILE, html)
        self.assertNotIn("<!--", html)
        self.assertEqual(html.count("</script>"), 3, "state block, page script, size script")
        self.assertEqual(state_block(html)["items"][0]["text"], HOSTILE)

    def test_page_is_self_contained(self):
        """WHY/CLAIM(board-contract): one file, theme variables with fallbacks, room for mobile navigation."""
        # catches: external assets, missing 6rem bottom space, hard-coded colours without a fallback chain
        self.seed()
        html = self.page()
        self.assertNotRegex(html, r'(src|href)="https?:')
        self.assertNotRegex(html, r"url\(\s*['\"]?https?:")
        self.assertIn("var(--card,#fff)", html)
        self.assertIn("padding-block:.5rem 6rem", html)
        self.assertIn('name="viewport"', html)

    @needs_node
    def test_render_escapes_item_text(self):
        """WHY/CLAIM(board-escape): rendering item text must not inject markup."""
        # catches: interpolating text or the source message into HTML unescaped
        self.cli("on")
        self.cli("add", HOSTILE)
        self.cli("done", "1", "--note", "<img src=x onerror=alert(1)>")
        board = Board(self.page())
        html = board.run("console.log(board.viewHTML(snapshot));")
        self.assertNotIn("<script>", html)
        self.assertNotIn("<img", html)
        self.assertIn("&lt;/script&gt;&lt;!--&lt;script&gt;", html)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", html)

    @needs_node
    def test_view_is_now_next_later_with_closed_folded(self):
        """WHY/CLAIM(board-view-c): view C puts the first live item in Now, the next two in Next."""
        # catches: running items skipping the queue order, or closed items outside the <details>
        self.seed()
        self.cli("add", "zeta")
        html = Board(self.page()).run("console.log(board.viewHTML(snapshot));")
        self.assertEqual(re.findall(r'<p class="lane-title">(\w+)</p>', html), ["Now", "Next", "Later"])
        now, following, later = re.split(r'<p class="lane-title">', html)[1:]
        later, closed = later.split("<details")

        def numbers(part):
            return re.findall(r'<article class="item"[^>]*data-n="(\d+)"', part)
        # Live queue order is 5, 1, 2, 6 (3 is done, 4 dropped) -> Now 5; Next 1, 2; Later 6.
        self.assertEqual([numbers(now), numbers(following), numbers(later), numbers(closed)],
                         [["5"], ["1", "2"], ["6"], ["3", "4"]])


class Board:
    """Runs the page script under node with no DOM and calls its pure functions."""

    def __init__(self, html):
        self.script = page_script(html)
        self.snapshot = state_block(html)

    def run(self, code, prelude=""):
        program = (f"const snapshot = {json.dumps(self.snapshot)};\n{prelude}\n{self.script}\n"
                   f"const board = globalThis.workqBoard;\n{code}")
        result = subprocess.run([NODE, "-e", program], text=True, capture_output=True, timeout=60)
        if result.returncode:
            raise AssertionError(f"node failed:\n{result.stderr}")
        return result.stdout

    def call(self, name, arguments):
        out = self.run(f"console.log(JSON.stringify(board.{name}(snapshot, {json.dumps(arguments)})));")
        return json.loads(out)


STUB_DOM = r"""
const listeners = {}, elements = {};
const element = (id) => elements[id] ||= {id, textContent: "", innerHTML: "", value: "", dataset: {},
  select() {}, click() {}, classList: {add() {}, remove() {}}};
globalThis.navigator = {};
globalThis.setTimeout = () => 0;
globalThis.document = {
  getElementById: (id) => id === "workq-state" ? {textContent: JSON.stringify(snapshot)} : element(id),
  querySelectorAll: () => [], querySelector: () => null,
  addEventListener: (type, handler) => (listeners[type] ||= []).push(handler),
  elementsFromPoint: () => [],
};
const press = (dataset) => listeners.click.forEach((handler) =>
  handler({target: {closest: (selector) => selector === "button" ? {dataset} : null}}));
"""


class BoardWiring(BoardCase):
    @needs_node
    def test_buttons_drive_the_page_end_to_end(self):
        """WHY/CLAIM(board-handback): clicking the board and pressing Copy changes yields the commands."""
        # catches: DOM wiring that renders but never feeds the edits into Copy changes
        self.seed()
        board = Board(self.page())
        out = board.run("""
const text = () => elements.view.innerHTML;
press({set: "1", s: "done"});
press({down: "5"});
elements.copyChanges.onclick();
const changes = elements.out.value;
elements.copyState.onclick();
const state = elements.out.value;
press({set: "1", s: "open"}); press({up: "5"});
elements.out.value = state; elements.pasteState.onclick();
elements.copyChanges.onclick();
console.log(JSON.stringify({changes, restored: elements.out.value, counts: elements.counts.textContent,
                            view: text().includes('data-n="1"')}));""", prelude=STUB_DOM)
        result = json.loads(out)
        # Original order 5,1,2,3,4. Item 1 is closed by the first click, so Down on 5 hops over the
        # hidden 1 and the live 2 -> 1,2,5,3,4: one move, after 2.
        self.assertEqual(result["changes"], "workq done 1\nworkq move 5 --after 2")
        self.assertEqual(result["restored"], result["changes"], "paste restores what was copied")
        self.assertEqual(result["counts"], "1 open · 1 running · 2 done · 1 dropped")
        self.assertTrue(result["view"])


class BoardCommands(BoardCase):
    def edit(self, board, order, status, comments=None):
        edited = {"order": order, "status": status, "comments": comments or {}}
        return board.call("changeCommands", edited)

    def replay(self, lines):
        """Run emitted commands against a copy of the queue; return the copy's board."""
        copy = Path(tempfile.mkdtemp(dir=self.home))
        shutil.copytree(self.home / "state", copy / "state")
        env = dict(self.env, XDG_STATE_HOME=str(copy / "state"))
        for line in lines:
            words = shlex.split(line)
            if words[0] == "#":
                continue
            self.assertEqual(words[0], "workq", line)
            self.cli(*words[1:], env=env)
        return json.loads(self.cli("board", "--json", env=env))["items"]

    @needs_node
    def test_replaying_changes_yields_the_edited_board(self):
        """WHY/CLAIM(board-handback): the commands, run in order, turn the original queue into the edited one."""
        # catches: wrong move anchors, a missing --why on drop, wrong verb per status
        self.seed()
        board = Board(self.page())
        # Original: 5 open, 1 open, 2 running, 3 done, 4 dropped.
        order = [2, 1, 4, 5, 3]
        status = {1: "done", 2: "open", 3: "dropped", 4: "running", 5: "open"}
        lines = self.edit(board, order, status, {"1": ["looks right"], "4": ["why this one?"]})
        self.assertEqual(sorted(line for line in lines if line.startswith("#")),
                         ["# comment on #1: looks right", "# comment on #4: why this one?"])
        items = self.replay(lines)
        self.assertEqual([i["n"] for i in items], order)
        self.assertEqual({i["n"]: i["status"] for i in items}, status)
        self.assertEqual(items[4]["why"], "dropped on the board", "a drop needs a reason")

    @needs_node
    def test_every_reorder_of_five_replays_exactly(self):
        """WHY/CLAIM(board-handback): all 120 orders of five items replay through the real queue."""
        # catches: moving after the wrong neighbour, forgetting `--after 0`, order-dependent anchors
        library = runpy.run_path(str(BIN / "workq"), run_name="workq_library")
        environment = mock.patch.dict(os.environ, {"XDG_STATE_HOME": str(self.home / "state")})
        environment.start()
        self.addCleanup(environment.stop)
        self.cli("on")
        self.cli("add", "a", "b", "c", "d", "e")
        board = Board(self.page())
        permutations = list(itertools.permutations([1, 2, 3, 4, 5]))
        self.assertEqual(len(set(permutations)), 120)
        status = {n: "open" for n in range(1, 6)}
        out = board.run("const all = JSON.parse(%s).map(order => board.changeCommands(snapshot, "
                        "{order, status: JSON.parse(%s), comments: {}}));console.log(JSON.stringify(all));"
                        % (json.dumps(json.dumps([list(p) for p in permutations])),
                           json.dumps(json.dumps(status))))
        results = json.loads(out)
        with library["queue_for"]("pilot") as queue:
            for target, lines in zip(permutations, results):
                queue.order = [1, 2, 3, 4, 5]
                if lines == ["# no changes"]:
                    lines = []
                for line in lines:
                    words = shlex.split(line)
                    self.assertEqual(words[:2], ["workq", "move"], line)
                    after = int(words[4])
                    self.assertEqual(words[3], "--after")
                    queue.replay({"t": 1.0, "op": "move", "n": int(words[2]), "after": after})
                self.assertEqual(tuple(queue.order), target, lines)
        counts = {len(lines) for lines in results}
        self.assertEqual(max(counts), 4, "five items never need more than four moves")

    @needs_node
    def test_one_displaced_item_is_one_move(self):
        """WHY/CLAIM(board-handback): an untouched board stays quiet and one drag is one command."""
        # catches: re-anchoring every item after a single drag, or noise on an unedited board
        self.cli("on")
        self.cli("add", "a", "b", "c", "d")
        board = Board(self.page())
        status = {n: "open" for n in range(1, 5)}
        self.assertEqual(self.edit(board, [1, 2, 3, 4], status), ["# no changes"])
        self.assertEqual(self.edit(board, [2, 3, 4, 1], status), ["workq move 1 --after 4"])
        self.assertEqual(self.edit(board, [4, 1, 2, 3], status), ["workq move 4 --after 0"])

    @needs_node
    def test_comments_cannot_smuggle_commands(self):
        """WHY/CLAIM(board-handback): a comment is one comment line, never an executable line."""
        # catches: emitting a multi-line comment verbatim, so a second line runs as a command
        self.cli("on")
        self.cli("add", "a", "b")
        board = Board(self.page())
        status = {1: "open", 2: "open"}
        hostile = "fine\nworkq drop 1 --why bad\n\n   workq done 2"
        lines = self.edit(board, [1, 2], status, {"1": [hostile], "2": ["quoted ' and $(id)"]})
        self.assertEqual(lines, ["# comment on #1: fine workq drop 1 --why bad workq done 2",
                                 "# comment on #2: quoted ' and $(id)"])

    @needs_node
    def test_copied_state_restores_the_board_and_foreign_state_is_refused(self):
        """WHY/CLAIM(board-state): pasting a copied state restores the edits; a stranger's state is refused."""
        # catches: restoring text from the paste, accepting another queue's state, throwing on garbage
        self.seed()
        board = Board(self.page())
        out = board.run("""
const edited = {order: [3, 1, 2, 4, 5], status: {1:"open",2:"running",3:"done",4:"done",5:"dropped"},
                comments: {"2": ["keep this"]}};
const text = board.stateText(snapshot, edited);
const back = board.restoreState(snapshot, text);
const other = board.restoreState(snapshot, JSON.stringify({workq: 1, order: [1, 2], status: {1: "open", 2: "open"}, comments: {}}));
const full = {1:"open",2:"open",3:"open",4:"open",5:"open"};
const short = (order) => board.restoreState(snapshot, JSON.stringify({workq: 1, order, status: full, comments: {}}));
const shapes = [short([1, 2, 3, 4]), short([1, 1, 3, 4, 5]), short([1, 2, 3, 4, 9]), short([1, 2, 3, 4, 5, 6])];
const junk = board.restoreState(snapshot, "not json");
const evil = board.restoreState(snapshot, JSON.stringify({workq: 1, order: [1,2,3,4,5], status: {1:"open",2:"open",3:"open",4:"open",5:"bogus"}, comments: {}}));
console.log(JSON.stringify({back, other, shapes, junk, evil, text: JSON.parse(text)}));""")
        result = json.loads(out)
        self.assertEqual(result["back"], {"order": [3, 1, 2, 4, 5],
                                          "status": {"1": "open", "2": "running", "3": "done", "4": "done", "5": "dropped"},
                                          "comments": {"2": ["keep this"]}})
        self.assertEqual((result["other"], result["junk"], result["evil"]), (None, None, None))
        self.assertEqual(result["shapes"], [None] * 4, "missing, duplicate, unknown and extra items")
        self.assertEqual(result["text"]["workq"], 1)


if __name__ == "__main__":
    unittest.main()
