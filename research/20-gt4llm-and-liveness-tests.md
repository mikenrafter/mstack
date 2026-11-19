# 20. gt4llm in detail, and vacuous "when X, then Y" tests

Written 2026-11-19 on nixed. Read only: nothing was posted, starred or
opened upstream. This report builds on [18](18-girba-wayne-oreilly.md) (first
pass over gt4llm and Hillel Wayne), [11](11-moldable-components.md) and
[12](12-paneweft-v1-in-code-views.md) (paneweft design). It corrects two
statements in 18.

Sources read: a clone of `feenkcom/gt4llm` at `0c846c7` (2026-11-19 00:25
+0100, 2,910 commits), treated as untrusted data and never run; the 109
commits that touch `src/Gt4Llm-ACP`; eight Glamorous Toolkit (GT) book pages
on the LLM integration; the GT YouTube channel feed; the feenk Medium feed;
the GT release API; Wayne's posts of 2026-02-11 and 2026-03-10 in full;
paneweft at `2c7b9e2` (2026-11-12); `skills/test-quality/SKILL.md` and
`skills/build-loop/references/phases.md`. I wrote and ran six small Python
test files (Hypothesis 6.151.10, pytest 9.0.3) to check every claim in part 2
about which tests pass and which mutations flip them.

## Top findings

1. **18 misread the `<gtLlmView>` pragma.** gt4llm has three pragmas.
   `<gtLlmDataView>` (104 files) builds the JSON the model receives.
   `<gtLlmView>` (89 files) and `<gtLlmMessageView>` (32 files) pick which
   ordinary inspector views a *person* sees inside chat and session panes.
   The model never reads a `<gtLlmView>` directly. Grade C (code read).
2. **The model's tool set is about 35 typed tools grouped by job** (search,
   code change, refactoring, Lepiter pages, example runs, object execution).
   Each tool returns a domain object, and the object's `<gtLlmDataView>`
   methods decide what the model sees. Missing objects come back as typed
   error objects instead of exceptions. Grade C.
3. **Stored objects carry a reason that points at the tool call that made
   them.** The store is an in-memory dictionary keyed by UUID and is wiped
   when the chat is compacted. Grade C.
4. **ACP support started on 2026-10-27, not 2026-11-05 as 18 said.** ACP is
   the Agent Client Protocol, a JSON-RPC protocol for driving coding agents
   from an editor. Work since 2026-11-05 added session and turn state
   machines, "input needed" notifications, a context-window gauge, reading
   stored Claude Code and Codex sessions from disk, a Bash view of tool
   calls, and system prompts taken from Lepiter pages. Stored transcripts are
   read for metadata only. To see a session's content, GT replays it through
   the agent's ACP adapter. Grade C.
5. **Running GT locally on nixed is blocked by disk, not by architecture.**
   feenk ships a Linux aarch64 build every day (v1.1.693, 243 MB zip, 1,022
   MB unpacked). The root filesystem has 1.5 GB free. Browsing your own
   stored sessions needs no API key. Driving Claude Code or Codex uses their
   own sign-in. Plain gt4llm chats need an OpenAI or Anthropic key, or a
   local Ollama. Grade: measured 2026-11-19.
6. **Wayne's vacuity trap reproduces in a few lines of Hypothesis.** A
   leads-to property ("a worker in retry eventually leaves retry") passed,
   and kept passing with retry made permanent, because the generator never
   produced a transient error. `hypothesis.find` on the same strategy raises
   `NoSuchExample`, which is Wayne's check that the trigger is reachable.
   Grade C (reproducible demo below).
7. **test-quality already catches the example-test form of vacuity but not
   the property form.** "Conditional assertions" (§8) and "empty the list"
   (§6.3) cover `if row: assert ...`. Nothing covers a generator, a test-only
   configuration or a refactor that never reaches the trigger. The
   build-loop spot mutation finds it by accident: break the consequent and
   the test stays green. But the skill does not say what that green means.
   Grade C.
8. **`# catches:` accepts Wayne's tautology.** A truth-table test of
   `can_import` names a real wrong implementation of the predicate. Both
   system-level mutations I tried (skip the check; read a stale policy) left
   it green. A two-step property over the store caught both. Grade C.
9. **LLM-written properties are "obvious", and Wayne could not get Claude to
   write a liveness property even when told to (March 2026).** Your red phase
   is written by agents, so the property that matters most is the one least
   likely to appear unprompted. Grade C, one practitioner, model unnamed.

---

## Part 1. gt4llm

### 1.1 How views are marked for the model

There are three pragmas. A pragma is a Smalltalk method annotation such as
`<gtView>`, which GT collects by reflection.

| Pragma | Who sees the result | Where it is consumed | Count |
|---|---|---|---|
| `<gtLlmDataView>` | The model. Methods build a `GtLDataView` (JSON object, Magritte-described object, document, image, or a forward to another object). | `ProtoObject>>llmDataViewsInContext:` collects them through `GtLDataViewsCollector` (`defaultPragmaNames` is `#(#gtLlmDataView)`). `GtLWrappedModel>>computeMainDataView` and `TGtLWithInputDataBlocks` serialize them with `serializeToLlmPrimiteData`. | 104 files |
| `<gtLlmView>` | A person, inside an LLM chat or ACP session pane. It sits on an ordinary `<gtView>`, often a graphical one such as a `GtCoderElement`. | `GtLSettings class>>messageViewPragmaNames` returns `#(gtLlmMessageView gtLlmView)`. `GtLStoredObject>>gtViewsInContext:`, `GtLACPSession>>summarizerViewsFor:inContext:` and the session tool elements pass that list to `GtPhlowViewsCollector`. | 89 files |
| `<gtLlmMessageView>` | Same as above, for views specific to chat messages. | Same list. | 32 files |

Example: `GtLSmaCCParserReference` (in `src/Gt4Llm-SmaCC/`) has
`gtClassCoderViewFor:` marked `<gtView> <gtLlmView>`, which renders a live
code editor for a person. Its `llmRawDataViewFor:` is marked
`<gtLlmDataView>` and returns `aDataView magritteObject: [ self ]`, which
becomes JSON for the model.

The model can still reach any ordinary inspector view by name.
`getViewContent(objectId, viewSelector)` (`GtLToolForObjectView`) looks the
object up in storage and runs `GtLObjectPhlowViewExtractor`. That extractor
returns the rendered view *and the source code of the view method*
(`GtLPhlowViewDomainObject phlowView:viewMethodClassName:viewMethodSourceCode:`).
So the model learns how a view was computed, which fits Gîrba's
"explainable" rule. `getClassViews` (`GtLToolForClassViews`) lists a class's
`<gtView>` methods, but it is not in any default tool group. Only its
examples use it.

Correction to 18 (finding 1, table row "Views for the model", idea G4):
`<gtLlmView>` does not mark which views the model may read. It marks which
views a person sees next to the chat. The model-facing opt-in is
`<gtLlmDataView>`, and it is a different method from the human view.

### 1.2 The tool set the model gets

`GtLTools class>>gt` (`src/Gt4LlmCore/GtLTools.class.st`) is the default for
`GtLAgentExecutionBuilder`, `GtLChatRegistry` and `GtLOnDemandMcpServer`. It
concatenates seven groups. Model-facing names come from each class's `name`
method.

| Group | Tool names |
|---|---|
| `gtSearch` | `searchForClasses`, `classSubclasses`, `lookupClass`, `classReferences`, `methodReferences`, `getImplementors`, `getCodeOfMethods`, `packageClasses`, `substringLiteralSearch` |
| `leSearch` | `lepiterKnowledgeBases`, `searchForLepiterPages`, `getLepiterPageContents` |
| `gtCodeChange` | `createClassesAndTraits`, `changeClassOrTraitSignature`, `changeClassOrTraitComment`, `compileMethods`, `removeMethods`, `removeClass` |
| `gtCodeRefactoring` | `listTransformations`, `previewRefactoring`, `applyRefactoring`, `previewRewrite` |
| `leChange` | `createLepiterPage`, `removeLepiterPage`, `editLepiterSnippet`, `createLepiterSnippets`, `removeLepiterSnippets` |
| `gtExamplesRun` | `exampleMethodRun`, `examplesInClassesRun` |
| `gtObjectsExecution` | `smalltalkCodeEvaluation`, `getViewContent`, `listObjectStorage`, `getObjectStorageValue`, `getObjectStorageSlotValue` |

Separate groups exist for files, git, SUnit tests (`testMethodRun`), SmaCC
parsers, `startAgent` and `worldScreenshot`.

Each tool subclasses `GtLAbstractMagritteFunctionTool`. Magritte is GT's
metadata framework: parameter descriptions become the JSON Schema the model
sees. `performToolCall:inContext:` validates the raw arguments against that
schema, returns the first validation error as a result object, runs
`privatePerformToolCall:inContext:`, and wraps the domain object in a
`GtLWrappedObjectModel`. Failures are domain objects too
(`GtLMissingDomainObject`, `GtLMissingInformationDomainObject`,
`GtLExceptionDomainObject freeze:`), so the model gets a typed, viewable
error instead of a stack dump. The same tools are offered to outside agents
over MCP through `GtLMcpServer`.

### 1.3 Stored objects, ids and reasons

`GtLObjectStorage` (`src/Gt4LlmCore/`) holds a `Dictionary` from UUID to
`GtLStoredObject`. `addNewObject:reason:` makes a new UUID, stores the value
with its reason, announces `GtLObjectStorageObjectAddedAnnouncement` (so the
UI updates), and returns the id as a base-36 string. It does not check for
duplicates ("TODO: extend to check that the UUID does not exist").

Reasons are objects, not strings:

| Class | Holds | `asReasonString` |
|---|---|---|
| `GtLStoredObjectStringReason` | free text (for example `'Initial object'` from the "Chat about this object" action in `Object.extension.st`) | the text |
| `GtLStoredObjectToolBasedReason` (abstract) | the `toolCall` itself | |
| `GtLStoredObjectExampleMethodReason` | the call to `exampleMethodRun` | the example method, rebuilt from the call's `className`, `methodName`, `classSide` |
| `GtLStoredObjectCodeExecutionReason` | the call to `smalltalkCodeEvaluation` | the code that ran |

Because a reason keeps the tool call, a person inspecting a stored object
can open the call that produced it (`gtInspectorTargetModels`). The model
sees `objectId`, value and reason through `listObjectStorage`. Code
evaluation can bind script variables to stored ids
(`GtLMagritteToolForSmalltalkCodeEvaluation>>bindingsDescription`), which is
GT's "contextual playground" for the model. The book walks through this with
an icon-drawing task graded by `getViewContent`
([Working with objects][b-objects]).

Two limits. The store lives in memory with the chat. And
`purgeRedundantObjectsForChat:` clears it after compaction ("Assume that the
summary doesn't reference objects"). An id the model wrote into its summary
then points at nothing.

### 1.4 How examples are run and reported

`exampleMethodRun` (`GtLToolForExampleMethodRun`) takes an
`exampleReference`. It checks that the method is a `<gtExample>`, runs it
with `asExampleWithResult`, and on an exception returns
`GtLExceptionDomainObject` with a description. On success it stores the
return value with an example-method reason and returns `GtLExampleWithResult`.
That object has two `<gtLlmDataView>` methods. One gives the example
reference plus `exampleStatus`. The other forwards to
`GtLObjectStorageValueResult`, which carries the object id, a
`playgroundPageReference` (a Lepiter page for notes about that object), a
generic Magritte view of the result and a forward to the result's own
`<gtLlmDataView>` methods. The tool's description tells the model to read all
returned views and to use the id in later calls. `examplesInClassesRun`
reports a `GtLExampleExecutionSummary` of successes and failures.

### 1.5 Claude Code and Codex sessions as views (ACP)

`src/Gt4Llm-ACP` has 183 class files. Gîrba wrote nearly all of its 109
commits, starting with "a rough first version of the ACP support" on
2026-10-27. Work up to 2026-11-04 built the chat, subagents, work badges, a
work graph across agents, commands and skills with completion, a session
registry, and a link from each ACP tool call to the matching GT MCP tool
call. Commits since 2026-11-05:

| Date | Commit | Change |
|---|---|---|
| 11-05 | `a487deaf`, `a6cc060f`, `f65a0b67`, `cecf8c48`, `082dc4a9` | Sessions registry tool; user questions; permissions and elicitations handled as one kind of request; "input needed" notifications inside the chat; badges that scroll to the request |
| 11-05, 06 | `8ba05e02`, `2e7248bb`, `11728d61` | `GtLACPContextWindow`: context occupancy from ACP usage updates ("not cumulative token consumption or a monetary budget"), shown per session |
| 11-07, 09 | `135152e9`, `fb0868b0` | `GtLACPExternalSessionStore` reads stored sessions; a menu to load one; session types per client |
| 11-08 | `b29f5b6d` | Explicit state classes: 13 for a prompt turn (idle, running, cancelling, cancelled, completed, failed, disconnected, replayed, observed, ...) and 12 for a session (new, starting, loading, ready, prompting, closed, reopening, ...) |
| 11-08 to 11 | `67f271fa`, `c045820a` | Reopen closed sessions; turns in the conversation tree |
| 11-15 | `dc7f6e10`, `8a212ae6` | "Load script" view: an editable snippet that reloads the session; context window per message and turn |
| 11-16 | `388aeabe` | Rewritten readers, 2,395 lines added: `GtLACPClaudeCodeStoredSession`, title and transcript records, Codex index, rollout and compressed-rollout records, with fixtures and examples |
| 11-17 | `8e19c97e` (Andrei Chiș) | `GtLACPBashReport`: a Bash view (command, description, recorded output) and an Input view on each tool call |
| 11-17, 18 | `4fa71770`, `10550c79` | System prompt in append or override mode; Lepiter pages as instructions |

**How the readers work.** `GtLACPClaudeCodeSessionStore` uses
`CLAUDE_CONFIG_DIR` or `~/.claude`. It scans `projects/*/*.jsonl` and skips
files containing `.orphaned-` or `.superseded-`. The session id is the file
name. The project directory comes from a record's recorded `cwd`; the
comment says it never reverses the encoded folder name. Records are scanned
as bytes and only metadata lines are decoded: "message bodies are not
retained" (`GtLACPClaudeCodeTranscriptRecord`). Titles follow a precedence
(`GtLACPClaudeCodeTitleRecord>>priority`): an explicit `customTitle` (40 in
the transcript, 35 from a sidecar), then `aiTitle` (30), then `summary` (20).
The latest record wins a tie. `GtLACPCodexSessionStore` uses `CODEX_HOME` or
`~/.codex`. It reads `session_index.jsonl`, rollout headers (`session_meta`)
and `.jsonl.zst` rollouts, and hides internal and delegated subagents from
the default list while keeping them in an "Agent origins" view.

**The views explain their own evidence.** Every view method in the new
readers starts with the question it answers, as a comment. `gtTitlesFor:`
("Which title is selected, and why were other candidates not selected?")
lists every title candidate with a Decision column: Selected, Lower
priority, Superseded by later record, Different session, Missing or invalid
text. `gtIssuesFor:` ("What prevented metadata from being read...?") lists
read problems by file and line. `gtRecordsFor:` shows which record supplied
the directory and why. The Bash view's comment states that opening it never
runs the command.

**Content comes from replay.** `GtLACPStoredSession>>load` refuses if the
recorded directory is unknown or gone. Otherwise it starts the agent's ACP
adapter in that directory and calls `loadSession:`. The adapters are npm
packages run with `npx`: `@agentclientprotocol/claude-agent-acp` and
`@agentclientprotocol/codex-acp` (a Python `claude-code-acp==0.5.1` adapter
also exists). The agent replays the conversation as ACP updates, which land
in turns in the "replayed" state. So GT shows a stored session's tool calls
only through the agent's own replay. It does not parse message bodies
itself. Correction to 18 (finding 2): GT lists sessions from the transcript
files and shows their content through ACP replay.

When GT's MCP server is set up, an ACP session shares its object storage
(`GtLACPSession>>objectStorage`), and summarizers run over the MCP tool
messages that the agent sent back into GT (`mcpToolMessagesFor:in:`). A
Claude Code session driven from GT can therefore run GT examples and read
views by object id. The session's views (`gtChatFor:`,
`gtConversationTreeFor:`, `gtCommandsFor:`, `gtConfigurationOptionsFor:`)
are all marked `<gtLlmView>`, and
`GtLACPSessionRegistryExamples` asserts that every view in the registry tool
carries that pragma.

### 1.6 What feenk has published about it

- **GT book**, version v1.1.692, pages undated, read 2026-11-19. The index
  page [gt4llm: Working with LLMs][b-index] links a "Moldable Agent Harness"
  tutorial in 11 steps ([tutorial][b-tutorial]), [Working with
  objects][b-objects], [Loading ACP sessions from disk][b-acp-load],
  [Setting up Claude Code through ACP][b-acp-claude] and [Codex][b-acp-codex].
  "Working with deterministic summarizers" is a one-word page: "DRAFT". The
  tutorial gives the stance in three steps: "Define the context, Specify the
  intent, Understand the output", with views and examples serving the first
  and third.
- **YouTube**, Glamorous Toolkit channel (`UClLZHVq_-2D2-iI4rA2O8Ug`):
  "GT Live: Moldable Chat" (2026-03-02, 693 views), "Showcasing MCP support
  in Glamorous Toolkit" (2025-07-13), "Exploring documentation generation
  with gt4llm" (2025-07-30), "Topic Mining with gt4llm" (2025-07-21),
  "Building an LLM tool with (and for) GT" (2025-04-14). I read the
  descriptions only, not the videos. No video covers ACP yet.
- **Medium** (`medium.com/feed/feenk`): nothing on gt4llm itself. The newest
  item is Rewilding chapter 6 (2026-01-16), covered in 18.
- **lepiter.io/feenk** returned a 1 KB shell page with no posts.
- `youtube.com/@feenk` is an unrelated gaming channel. Do not add it to
  practice-watch.

### 1.7 What paneweft would gain from each idea

Paneweft at `2c7b9e2` already has: a `question` on every view record,
evidence with `provenance` (read, parsed, compiled, observed) and `runId`,
typed `paneweft.error/1` replies with repair hints, byte budgets and
cursors, examples that publish views via `collect`, and MCP tools including
`list_views_for_type`, `view_result` and `explain_failure`.

| gt4llm idea | Paneweft today | Gain if adopted | Verdict |
|---|---|---|---|
| Separate model-facing data view from human view (`<gtLlmDataView>` vs `<gtView>`) | One view record; text and browser render the same facts by design (12 §6) | Little. Paneweft's single source keeps the agent and the person looking at the same facts, which GT's split gives up. | Skip. Replace 18's G4 (`audience` field) with "skip until a type has more views than an agent should list". |
| A person-facing filter of which views appear beside the chat (`<gtLlmView>`) | No chat pane | None now | Skip |
| Every stored object has an id and a reason pointing at the producing call | Objects come only from example runs; `runId` plus example id is the reason | Needed once objects come from somewhere else (a transcript adapter, an agent note). Then add `reason: {kind, ref}` to object records. | Cheap now while the schema is young (18's G5 stands). |
| `exampleMethodRun` returns status, views, object id and a notes page | `collect`, `collection_status`, `view_result`, `explain_failure`; v0 notebooks exist | A link from an example to its notebook page in `view_result`, so notes about an object travel with it | Small, worth it |
| `getViewContent` returns the view method's source with the result | View records carry source locations | Return the view function's source span in `view_result` when asked, so an agent can check how a number was computed | Small, worth it |
| Views whose comment states a question, plus "decision" views that show rejected candidates and why | `question` field exists | A view pattern for the `paneweft-views` skill: when a view picks one value from several sources, add a sibling view listing every candidate and its decision | Cheap, high value for review |
| Session store over `~/.claude` and `~/.codex` with read-issue views | None | A transcript adapter, so the one-off analyses in reports 06 and 07 become views you can rerun. Borrow the file rules from 1.5. | Medium cost; do it if 06/07 recur |
| Summarizers built from tool calls (code changed, examples run) | None | A "session" type with views of files changed and tests run, generated from tool calls (18's G7) | Medium |
| Code evaluation with bindings to stored ids | Out of scope by design (snapshots, no live attachment) | Not compatible with immutable records | Not transferable |
| Driving agents over ACP | T3 Code already drives your agents | Duplicate | Not transferable |
| Clearing object storage on compaction | Immutable session directory | GT's choice breaks ids after compaction | Do not copy |

### 1.8 What you could try in a day

1. **Free disk first.** nixed's `/` is at 100% with 1.5 GB free. The
   aarch64 zip is 243 MB and unpacks to 1,022 MB (image 354 MB, changes file
   85 MB, `libWinit` 123 MB twice, `libSkia` 73 MB), measured from the zip's
   central directory on 2026-11-19. Plan on 1.5 GB plus image growth.
2. **Use the upstream zip, not nixpkgs.** nixpkgs has `glamoroustoolkit`
   1.1.58, built for `x86_64-linux` only. feenk's release v1.1.693
   (2026-11-19) includes `GlamorousToolkit-Linux-aarch64-v1.1.693.zip` with
   a `.sha256`. phoe-nix enables `programs.nix-ld` in `hosts/core.nix`, which
   lets the bundled ELF binaries start. They will likely need graphics and
   font libraries added to `programs.nix-ld.libraries` [unverified: I did not
   unpack the binaries to list their dependencies]. Memory use on an 8 GB host
   is unmeasured; follow `low-ram-hosts`.
3. **Browse your own sessions, no key needed.** In a playground run
   `GtLACPClaudeCodeSessionStore new read` and
   `GtLACPCodexSessionStore new read`. You get the Sessions, Title evidence,
   Record kinds and Read problems views over your real transcripts. This is
   the fastest way to judge whether a paneweft transcript adapter is worth
   building.
4. **Load one session through ACP.** Needs Node with `npx` visible to GT and
   your existing `claude` or `codex` sign-in. No API key is entered in GT.
   Loading starts the agent in the recorded project directory, so pick a
   scratch project.
5. **Optional: a gt4llm chat.** `GtL gt sendMarkdown: '...'` needs an
   Anthropic or OpenAI API key, or Ollama running locally (book:
   [setup][b-connections]).

Write down which views you wished existed. That list is the input for
paneweft's next views, and is the part of this exercise that transfers.

### 1.9 What does not transfer

- Live objects in one image. GT can bind a script variable to an object the
  model created a minute ago. Paneweft records snapshots from separate test
  processes on purpose.
- Pragmas as the discovery mechanism. Paneweft's attribute macros and
  `linkme` registration already do the same job in Rust.
- Magritte-generated tool schemas. Paneweft's JSON Schemas are the source of
  truth already.
- Lepiter pages as system prompts. Skills fill this role in your setup.
- The ACP front end itself, which overlaps T3 Code.

---

## Part 2. Vacuous "when X, then Y" properties

### 2.1 What Wayne says

**[Proving What's Possible, 2026-02-11][w-possible].** Wayne uses `A(x)`
("always x") and `E(x)` ("eventually x"). `A(x => E(y))` says that whenever x
holds, y follows later; this is a liveness (leads-to) property. A third kind,
`P(x)`, says x *can* happen. His main use for it is a sense check:
`A(state == 'Retry' => E(state != 'Retry'))` "holds" of any system that never
reaches Retry, "in which case the expression is trivially true." You cannot
use `E` to check reachability, because that would demand every run retries.
Alloy and TLA+ lack `P`, so he checks `P(x)` by asserting `A(!x)` and
expecting a counterexample. Two caveats: this only shows x is reachable from
*some* starting state, and refinement (narrowing the allowed behaviours, which
is what an implementation or a refactor does) does not preserve possibility.

**[LLMs are bad at vibing specifications, 2026-03-10][w-vibing].** 4% of
public GitHub TLA+ specs mention "Claude". In an AI-written Alloy spec, the
file did not compile (it used `Bool` without `open util/boolean`), so nobody
ran it. Its two assertions restate the predicate: `canImport` is defined as
`P or Q`, and the assertions check `not P and not Q implies not canImport`
and `Q implies canImport`. "These are tautologically true! If they do
anything at all, it is only checking that canImport was defined correctly."
The TLA+ spec had the same shape: an action sets `decision' = "block"`
whenever it sets `gadgetDetected' = TRUE`, and the property is
`gadgetDetected => decision = "block"`. Such "obvious" properties catch a
missing guard. They do not catch failures from concurrency, nondeterminism or
steps far apart. With a client, he "tried to get Claude to generate a good
liveness or action property instead of a standard obvious invariant, and it
just couldn't." He dates this "as of March 2026."

### 2.2 Which failure modes your rules catch

| Wayne's failure mode | Your rule | Caught? |
|---|---|---|
| Spec never run (did not compile) | Red gate: tests fail on assertions, not on compile errors (`phases.md` §4); test-quality §11 "confirm each new test fails" | Yes |
| Property restates the predicate's definition (`canImport`) | §5 asks "can this expression be false given any implementation?" Mode 5 (mirrored implementation). "Pins dead code or the wrong layer" (§8). `# catches:` | Partly. The assertion *can* be false for a wrong `can_import`, so §5 and `# catches:` pass it. The wrong-layer check in §6.2 ("delete the call site") catches it if the reviewer runs it. Demo G2 below. |
| Only single-step "obvious" properties | §3 model-based state machines generate command sequences | Partly. The technique is there; nothing requires a property that spans two or more steps, and agents write the red tests. |
| Antecedent never fires (vacuous truth) | §8 "Conditional assertions"; §6.3 "empty the list" | Example tests only. Generated runs, filtered strategies (`assume`, `prop_assume!`) and model states the generator never reaches are not covered. Demo G1. |
| Trigger reachable only under test settings, or removed by a refactor (refinement drops possibility) | §8 "Test-only configuration" | Partly. That entry targets thresholds, not reachability, and no rule asks for a witness under shipped defaults. Demo G3. |
| Reachable from one start state but not another | none | No. Minor; covered by running the witness once per shipped profile. |
| Liveness on a finite trace | none | No. A generated trace that ends inside X neither passes nor fails cleanly unless the test drains the system first. |

**What the spot mutation does today.** In build-loop, the orchestrator
applies 2-3 of the named `# catches:` wrong implementations after green and
checks the tests go red. For a vacuous leads-to test, the named wrong
implementation is "tick forgets to leave retry". Applying it leaves the test
green (G1 below), so the spot mutation does flag the problem. But only if
that test is among the 2-3 sampled, only inside build-loop, and only once.
The skill also does not say what the surviving mutant means, so the likely
response is a stronger assertion, when the fix belongs in the generator.

### 2.3 One example per gap

All three ran under pytest with the results in the table at the end of this
section. A shared worker model:

```python
# worker.py
TRANSIENT = {503, 504}
DEFAULT_MAX_RETRIES = 3

class Worker:
    def __init__(self, max_retries=None):
        self.max_retries = DEFAULT_MAX_RETRIES if max_retries is None else max_retries
        self.state, self.attempts = "idle", 0
    def start(self):
        if self.state == "idle": self.state = "running"
    def fail(self, code):
        if self.state != "running": return
        if code in TRANSIENT and self.attempts < self.max_retries:
            self.state = "retry"
        else:
            self.state = "dead"
    def tick(self):
        if self.state == "retry":
            self.attempts += 1
            self.state = "running"

def run(ops, worker=None):
    w, states = worker or Worker(), []
    for op in ops:
        w.fail(op[1]) if op[0] == "fail" else getattr(w, op[0])()
        states.append(w.state)
    return states
```

**G1. The antecedent never fires.** The generator picks plausible error
codes, none of them transient, so `retry` never occurs.

```python
ops = st.lists(st.one_of(
    st.just(("start",)), st.just(("tick",)),
    st.tuples(st.just("fail"), st.sampled_from([400, 404, 500])),
), max_size=30)

@given(ops)
def test_retry_leads_to_exit(ops):
    # why: a worker stuck in retry never finishes its job (leads-to)
    # catches: tick() forgets to move retry back to running
    states = run(ops + [("tick",)] * 5)      # drain before checking "eventually"
    for i, s in enumerate(states):
        if s == "retry":
            assert any(t != "retry" for t in states[i + 1:])
```

It passes. With `tick()` made a no-op in retry (the exact `# catches:`
mutation) it still passes. The fix adds transient codes to the generator and
a reachability check that fails when the generator cannot reach the trigger:

```python
def test_retry_is_reachable_by_the_generator():
    # why: test_retry_leads_to_exit is vacuous unless state == retry occurs in
    #      generated runs. find() is Wayne's P(x): it raises NoSuchExample
    #      exactly when A(not retry) holds for everything the strategy makes.
    # catches: a generator or refactor that never produces a transient failure
    find(ops, lambda o: "retry" in run(o), settings=settings(max_examples=2000))
```

On the original strategy, `find` raised `NoSuchExample`. With the fixed
strategy both tests pass, and the sticky-retry mutation turns the property
red. In Haskell QuickCheck the same check is built in: `cover` declares a
required percentage and `checkCoverage` fails the property when it is not met
([docs][qc]). Hypothesis's `event()` only prints statistics and never fails.
For Rust `proptest` I found no coverage assertion; count the antecedent in an
`AtomicUsize` inside the property and assert it is above zero in a following
test, or keep a deterministic witness.

**G2. The property restates the predicate.** Wayne's `canImport` in Python:

```python
def can_import(policy, snap):
    return policy.allow_unsigned or snap.signed

def test_unsigned_import_denied():
    # catches: can_import ignores the signed flag
    assert not can_import(Policy(allow_unsigned=False), Snapshot(signed=False))
```

The `# catches:` line names a real wrong implementation, so the red gate
accepts it. Two system bugs leave it green: `Store.import_snapshot` skipping
the check, and `import_snapshot` reading the policy cached at construction.
The fix states the invariant the predicate exists for, over the store's
state, across policy changes:

```python
@given(st.booleans(), steps)   # steps: random set_policy / import_snapshot calls
def test_store_never_holds_unsigned_import_that_policy_forbade(start, steps):
    # why: the rule can_import exists for, checked on the store across policy
    #      changes, not on the predicate alone
    # catches: import_snapshot skips can_import; import reads a cached policy
    store = Store(Policy(start))
    for kind, x in steps:
        store.set_policy(x) if kind == "policy" else store.import_snapshot(x)
    for snap, policy_then in store.items:
        assert snap.signed or policy_then.allow_unsigned
```

Both mutations turn it red. The stale-policy bug needs two steps (change the
policy, then import), which is Wayne's "subtle" kind.

**G3. Reachable in tests, unreachable in production.** The suite builds
`Worker(max_retries=3)` everywhere, including a deterministic witness
(`assert "retry" in run([("start",), ("fail", 503)], Worker(max_retries=3))`).
A refactor sets `DEFAULT_MAX_RETRIES = 0`. Every test stays green, and
production can no longer retry. The fix is a witness through the shipped
default:

```python
def test_retry_reachable_with_shipped_defaults():
    # why: every "when retry, then ..." property is vacuous in production if
    #      the shipped configuration cannot reach retry
    # catches: DEFAULT_MAX_RETRIES set to 0; TRANSIENT emptied by a refactor
    assert "retry" in run([("start",), ("fail", 503)], Worker())
```

Results (`MUTANT` selects the mutation; each row is one pytest run):

| Test file | Mutation | Result |
|---|---|---|
| G1 before | none | 1 passed |
| G1 before | sticky retry | 1 passed (vacuous) |
| G1 after | none | 2 passed |
| G1 after | sticky retry | 1 failed, 1 passed |
| G2 before | none / skip check / stale policy | 2 passed in all three |
| G2 after | none | 1 passed |
| G2 after | skip check | 1 failed |
| G2 after | stale policy | 1 failed |
| G3 before | none / default 0 | 2 passed in both |
| G3 after | none | 1 passed |
| G3 after | default 0 | 1 failed |

### 2.4 Proposed text for test-quality

One rule for §3, one question for §5, one item for §6 and one entry for §8.

**§3, new subsection after "State machines":**

```markdown
### Conditional and leads-to properties
A property shaped *when X, then Y* passes for free when X never happens; so
does *when X, eventually Y*. Give each one a witness:
- a test that drives the system into X through the production entry point,
  with shipped defaults, and asserts it got there;
- for generated runs, a check that the generator reaches X: Hypothesis
  `find(strategy, reaches_x)`, QuickCheck `cover` with `checkCoverage`, or a
  counter asserted above zero (proptest has no built-in).
For *eventually*, end each generated trace with a bounded drain (tick or run
until idle) before checking. The `# catches:` mutation breaks Y; if the
property stays green, suspect X before the assertion.
```

**§5, append:**

```markdown
For an implication, also ask: *can the premise be true?* For a property of a
predicate, ask whether it restates the predicate's definition (`P ⇒ P ∨ Q`);
if so, assert the rule the predicate protects on the system's state instead.
```

**§6, new item 6:**

```markdown
6. Make X unreachable (delete the transition into it, set the limit to 0,
   empty the trigger set). The *when X* properties stay green, as expected;
   the witness must go red. Nothing red? The suite cannot tell a system that
   handles X from one that never reaches it.
```

**§8, new entry:**

```markdown
**Vacuous antecedent.** A property checks *when X, then Y*
(`if state == RETRY: assert ...`, `prop_assume!(x)`, a filtered strategy) and
X never occurs: the generator never makes the triggering input, the test
builds the object with non-shipped settings, or a refactor removed the only
path into X. It stays green with Y broken. Hillel Wayne's example: "a worker
in Retry eventually leaves Retry" holds for any worker that never retries.
Detect: break Y; still green means X never fired. Fix: a witness that
reaches X through production with shipped defaults, plus a generator check
(§3).
```

**Optional, `build-loop/references/phases.md` §4 red gate, one bullet:**

```markdown
- a test of the form *when X, then Y* names its witness:
  `# reaches: <test that drives the system into X>`.
```

---

## Where your setup differs

- **test-quality** treats vacuity as an emptiness problem (empty list,
  `if row != null`). Wayne treats it as a reachability problem. Your rules
  have no notion of a witness, so a property test whose trigger never fires
  passes every gate except a lucky spot mutation. §3 recommends model-based
  state machines but sets no requirement that every model state is reached.
- **`# catches:` (build-loop `phases.md` §4)** checks that a test has *some*
  wrong implementation it rejects. Wayne's tautologies pass that check,
  because a wrong predicate fails them. The check does not ask whether the
  wrong implementation is one the system could ship with.
- **The red phase is agent-written.** Wayne's report that Claude would not
  write a liveness property even on request (March 2026) means the
  leads-to and multi-step properties will mostly be missing unless the
  designer asks for one by name (18's W2 still stands).
- **paneweft vs gt4llm.** Paneweft keeps one set of facts for agent and
  person; gt4llm writes separate methods for each. Paneweft records are
  immutable and survive the process; gt4llm's object store is wiped on
  compaction. gt4llm is ahead on views that explain how a value was chosen
  (title evidence, read problems) and on views over agent sessions.
- **Report 18** needs two corrections: `<gtLlmView>` (finding 1, idea G4)
  and the ACP start date and transcript reading (finding 2). The `audience`
  field it recommends for paneweft (action 8) rests on the misreading; keep
  `reason`, drop `audience` for now.

## Candidate actions

Ranked by expected value over cost.

1. **Add the §3 rule, §5 question, §6 item and §8 entry above to
   test-quality.** About 30 lines. Each one closes a hole shown by a running
   demo.
2. **Add `# reaches:` to the build-loop red gate.** One bullet. It makes the
   witness part of the gate that agents already follow.
3. **Add a "decision view" pattern to the `paneweft-views` skill.** When a
   view picks one value from several sources, a sibling view lists every
   candidate and why it lost. Cheap, and it makes review of derived values
   faster.
4. **Fix report 18's two errors** (one line each in findings 1 and 2, and
   drop the `audience` half of action 8).
5. **Spend one session browsing your transcripts in GT** (part 1.8), after
   freeing 2 GB on nixed. It settles whether a paneweft transcript adapter is
   worth its medium cost.
6. **Add `reason` to paneweft object records** before a second object source
   exists.
7. **Return a view function's source span from `view_result` on request**,
   as `getViewContent` does. Small; lets an agent check how a number was
   computed.

## Sources

feenk and GT
- [gt4llm]: https://github.com/feenkcom/gt4llm cloned 2026-11-19 at `0c846c7`; files cited by path above
- [b-index]: https://book.gtoolkit.com/gt4llm--working-with-llms-270ytb3y5mi1voswipfyc5hti undated, book v1.1.692, read 2026-11-19
- [b-tutorial]: https://book.gtoolkit.com/moldable-agent-harness--a-step-by-step-tut-bbu6tutrk7amb3bwvrw0c06jg undated
- [b-objects]: https://book.gtoolkit.com/moldable-agent-harness--working-with-objec-a509rrm60ymi17yaqozxh46bw undated
- [b-acp-load]: https://book.gtoolkit.com/loading-acp-sessions-from-disk-7jqc0545o7jbm9omq37acfp0t undated
- [b-acp-claude]: https://book.gtoolkit.com/setting-up-claude-code-through-acp-dhbs465f5e3unoq4otgasrrma undated
- [b-acp-codex]: https://book.gtoolkit.com/setting-up-codex-through-acp-wqbb9bpkkvgs8v6qdiyeg1py undated
- [b-connections]: https://book.gtoolkit.com/how-to-setup-llm-connections-for-the-molda-46kmvr47kgm3d5j4jbwibt5yf undated
- [gt-release]: https://github.com/feenkcom/gtoolkit/releases/tag/v1.1.693 published 2026-11-19; asset sizes from the GitHub API
- [yt-gt]: https://www.youtube.com/feeds/videos.xml?channel_id=UClLZHVq_-2D2-iI4rA2O8Ug Glamorous Toolkit channel feed, read 2026-11-19 ("GT Live: Moldable Chat" https://www.youtube.com/watch?v=y0FQrVq74BI 2026-03-02; MCP showcase https://www.youtube.com/watch?v=GugejZ5Fris 2025-07-13)
- https://medium.com/feed/feenk read 2026-11-19, newest item 2026-01-16
- nixpkgs `glamoroustoolkit` 1.1.58, `meta.platforms = x86_64-linux`, evaluated locally 2026-11-19

Wayne and property testing
- [w-possible]: https://buttondown.com/hillelwayne/archive/proving-whats-possible/ 2026-02-11
- [w-vibing]: https://buttondown.com/hillelwayne/archive/llms-are-bad-at-vibing-specifications/ 2026-03-10
- [qc]: https://hackage.haskell.org/package/QuickCheck/docs/Test-QuickCheck.html `cover`, `checkCoverage`, read 2026-11-19
- Hypothesis `find` and `NoSuchExample`: observed in Hypothesis 6.151.10, 2026-11-19

Local
- `/home/mini/Documents/repos/paneweft` at `2c7b9e2`: `README.md`, `src/schemas/v1/object-graph.schema.json`, `src/schemas/v1/tools/`
- `/home/mini/Documents/repos/mstack/skills/test-quality/SKILL.md`, `skills/build-loop/references/phases.md`
- `/home/mini/Documents/repos/phoe-nix/hosts/core.nix` line 58 (`programs.nix-ld.enable`)
- Demo files (scratch, may be cleared): `/tmp/claude-1001/-home-mini-Documents-repos-mstack/d7ce0254-1b6e-4b0d-a457-f4ce662b065b/scratchpad/examples/`
