# Top findings

- **C:** Moldable development makes a specific question cheap to answer by adding a small, contextual tool. Published examples establish feasibility; they do not establish a general productivity multiplier. [Chiş et al., 2016-07-18][exemplifying]
- **B for the underlying problem:** A field study of 78 professionals across seven projects and 3,148 working hours attributed about 58% of time to comprehension. It did not test moldable development. [Xia et al., 2018-10][comprehension]
- **C:** GT's August 2024 image contained over 3,600 custom-view methods across over 1,800 classes, averaging under 12 lines. This measures customization size and adoption inside GT, not time saved. [Nierstrasz and Gîrba, 2024-09-27][patterns]
- **C:** Example-driven development makes a passing test return an inspectable example. Tests, exploration, and documentation can share that example. This idea already has a Java precedent. [Nierstrasz, Chiş, and Gîrba, 2024-08-31][edd]
- **C for capabilities:** Clerk, Portal, IPython, evcxr, and editor APIs demonstrate that custom representations are portable. Reproducing Pharo's continuous access to live objects requires additional runtime infrastructure. [Official documentation, undated, accessed 2026-11-10][clerk]; [GT PythonBridge, same access date][pythonbridge]
- **C for the reported experiment:** A 2026 essay compares an LLM dependency inventory against a deterministic inventory. Its missing model/version and trial accounting prevent conclusions about current agents generally. [Gîrba and Wardley, 2026-01-16][rewild6]
- **D, proposed design:** Your best first experiment is a revision-pinned evidence bundle with both human views and agent queries. Measure correctness and context cost before building a universal visual environment. Integration with your newest review-tool drafts remains **[unverified]** because void is offline and the local project directories contain no readable files.

## Scope and evidence

Researched on 2026-11-10. Grades follow the brief: A means a controlled study or benchmark with published method and data; B means substantial observational data with a stated sample; C means a practitioner report with concrete numbers or a reproducible demonstration; D means opinion, anecdote, or an untested proposal. A tool's documented capability can earn C while a claim that it improves decisions remains D.

I inspected the local skills and attempted to inspect `/home/mini/Documents/repos/diff-core` and `/home/mini/Documents/repos/residual-cli`, including hidden files. Both project paths contain directory skeletons but no readable files; neither has usable Git metadata. Their READMEs, `diff-core/residual/research`, and `residual-cli/research` therefore could not be skimmed. The project-fit discussion uses your requested direction and the [brief, inspected 2026-11-10](BRIEF.md). The newest drafts and transcripts on offline void are unavailable. No existing project interface is assumed below.

## What moldable development contributes

### Questions attached to working tools

Chiş and colleagues describe two requirements: extensions must be inexpensive to create, and the tool must discover when they apply. An activation predicate decides whether an extension fits the current artifact or task. Their compiler and parser demonstrations connect domain views to inspection, search, and debugging. A grammar view, for example, exposes productions directly instead of asking you to reconstruct them through implementation fields. **Grade C.** [2016-07-18][exemplifying]

The useful unit is a question attached to an entity. "Which callers can receive this error?" suggests an error-flow view of a function. "Why did this parser stop here?" suggests a view of the input position and grammar. My inference is that a repository-wide diagram will often be too coarse. You need views that appear when you inspect a relevant module, operation, change, or example. That is a design recommendation, **grade D** until tested.

The patterns paper describes a project diary, composed narratives, wrappers for external data, throwaway analysis tools, and contextual playgrounds. A playground evaluates snippets against the entity you are investigating. The resulting objects open further tools, so exploration becomes a chain you can preserve and revisit. Its stakeholder/facilitator distinction separates asking useful domain questions from implementing the tools that answer them. **Grade C for the demonstrated patterns.** [Nierstrasz and Gîrba, 2024-09-27][patterns]

"Explainable" here means a system can answer questions about its own domain and operation. It is broader than explaining an AI prediction. The important design consequence is traceability: a displayed answer should retain the entities, inputs, and operations that produced it. That consequence is my interpretation, not a reported experimental result.

Oscar Nierstrasz's related work also includes Moose. Nierstrasz, Stéphane Ducasse, and Gîrba describe a language-independent software model with shared services for querying, grouping, metrics, and visualization. The paper traces an environment evolved through reengineering work, **grade C**. Its relevance is practical: reusable extracted models can support many small analyses even when the analyzed language differs from the tool's implementation language. The proposed spec follows that separation. [2005-09][moose]

The later *Moldable Exceptions* paper attaches contextual debugger views and actions to raised exceptions. Its examples offer another **grade C** mechanism for making domain meaning available exactly when a failure occurs. That suggests retaining structured error context in runtime probes, subject to the target runtime's capabilities. [Chiş, Gîrba, and Nierstrasz, 2024-08-31][exceptions]

### Rewilding and the decision loop

Tudor Gîrba and Simon Wardley's *Rewilding Software Engineering* frames engineering as decision-making about changing systems too large to hold in your head. The opening chapter advocates changing how understanding is produced. Its audience observations and broad improvement claims are **grade D**, with no controlled comparison. [2025-02-06][rewild1]

Chapter 2 gives a legacy data-pipeline case in which contextual analysis exposes information needed for modernization. Treat it as a practitioner case, **grade C**, with limited independent reproducibility. The case motivates recovering the model actually encoded in the system before deciding how to change it. [2025-02-06][rewild2]

Chapter 3 names time to answer, `ttA`, and time to question, `ttQ`. Faster answers can let you ask better follow-up questions. It also requires answers to be accurate, explainable, and representative. The proposed loop is **grade D** as a general practice; the chapter does not establish causal improvements through a controlled study. [2025-02-06][rewild3]

Chapter 5 uses a restaurant communication model to connect business questions to executable representations. It explicitly describes its restaurant observations as qualitative. The demonstration supports feasibility, **grade C**; claims that shared representations improve organizational decisions remain **grade D**. [2025-05-22][rewild5]

The newest relevant chapter reports a deterministic GT inventory of 194 components and 396 dependencies. One LLM result found 154 and 243; prompt variations reportedly left roughly 5–30% missing, alongside invented relationships. This is a concrete **grade C** practitioner comparison. The model, version, complete trial count, and general benchmark procedure are not specified in the inspected account. Model age and transfer to your current models are **[unverified]**. The same chapter's retailer case reports two people spending one month reconstructing dependencies after six months of unsuccessful understanding work. Neither case establishes a general multiplier. [2026-01-16][rewild6]

### Example-driven development

An example method performs assertions and returns an interesting fixture. Other examples can reuse it, and a notebook can embed it. The 2024 paper demonstrates a game, an interpreter, and a layout algorithm, and points to JExample's adaptation of JUnit. Its stronger workflow starts by exploring an example and extracting assertions as understanding develops. **Grade C for the demonstrations; D for general superiority over test-driven development.** [Nierstrasz, Chiş, and Gîrba, 2024-08-31][edd]

For your projects, the portable adaptation is a scenario factory that returns a versioned observation after assertions pass. A denied APK request could return the decision and its inputs; a review example could return an evidence bundle. Rust's ordinary test runner need not retain arbitrary live fixtures. Export a bounded snapshot, or keep a separate inspection process. Keep independently derived expectations: making an implementation's output visible does not establish that the output is correct.

### What the evidence establishes

The foundational inspector paper used 16 interviews and a survey with 62 respondents to identify inspection needs. This is useful observational evidence about demand, but too small and targeted to call large-scale B evidence under this brief; I grade it **C**. The paper explicitly leaves effectiveness evaluation open. It also identifies the maintenance problem of updating views as represented objects evolve. [Chiş et al., 2015-10][inspector]

The comprehension field study provides **B** evidence that understanding consumes substantial effort. Its activity classifications include tools beyond editors. It provides no estimate of how much of that effort a particular visualization can remove. It predates current coding agents and measured no language model, so extrapolating its percentage to agent work would be unjustified. [Xia et al., 2018-10][comprehension]

I found no controlled A-grade moldable-development productivity study in the core publications inspected. The strongest direct evidence consists of working artifacts, small extensions, and contextual investigations. Plausible benefits are fewer navigation steps, preserved domain distinctions, and repeatable answers. Unresolved costs include learning the tooling, validating extractors, maintaining views, and noticing omitted behavior. These are evaluation questions for your prototype, not established effect sizes.

## What depends on a live-object environment

GT's examples run on Pharo, with notebooks, inspectors, and development tools accessing live objects. Its Python bridge goes across a process boundary, transferring some values and otherwise returning proxies to Python objects. The book separately documents Python source editing through LSP and pyright. **Grade C.** [EDD, 2024-08-31][edd]; [GT documentation, undated, accessed 2026-11-10][pythonbridge]; [LSP example, same access date][gtlsp]

The following portability judgments are design inferences, **grade D**, informed by those mechanisms.

| Idea | Portable implementation | What you must replace outside a shared live image |
|---|---|---|
| Contextual view discovery | Predicates over symbols, paths, schemas, capabilities | Object annotations become repository descriptors or registry entries |
| Inspector navigation | Stable entity IDs, relations, source anchors | Direct object pointers become snapshot references or remote handles |
| Domain-specific views | Pure transformations over typed facts | Access to arbitrary implementation state becomes an extractor contract |
| Executable examples | Scenario factories and tested snapshots | Long-lived fixtures need explicit lifecycle and cleanup |
| Composed narratives | Ordered questions, views, claims, evidence | Notebook object links become durable references |
| Live exploration and repair | REPL, debug adapter, instrumentation, rebuild | Uniform object identity, reflection, and immediate code changes require language-specific machinery |

A serialized snapshot can preserve an explanation while losing mutation, object identity, and some navigation. A remote handle preserves more interaction but expires when its process exits. Support both and expose the distinction. Do not promise that static extraction reproduces the full GT experience.

GT also demonstrates analyzing a JavaScript/React Native project and inspecting wrapped Rust objects. These demonstrate cross-language analysis and interoperation, not complete live-development parity for those languages. **Grade C.** [GT case studies, undated, accessed 2026-11-10][gtjs]; [wrapped Rust example, same access date][gtrust]

## Non-Smalltalk implementations and relatives

All capability descriptions below are **grade C** demonstrations or documented mechanisms. The final column is my design inference, **grade D**. Undated documentation was accessed on 2026-11-10; a retrieval date is not a release date.

| System and dated primary source | Demonstrated mechanism | Useful boundary for your design |
|---|---|---|
| [Clerk, undated][clerk] | Clojure source becomes notebooks; value predicates select custom viewers; dependency analysis supports incremental computation and static publishing | Closest explicit relative. Separate value selection, transformation, and rendering |
| [Portal custom-viewer example, undated][portal] | A predicate and Reagent component register a viewer; metadata selects defaults; the example uses `tap>` | Preserve an inspector's navigation and live value stream, alongside durable export |
| [Nextjournal, undated][nextjournal] | Polyglot notebooks use container runtimes, including Clojure, with file-based value exchange and environment reuse | Preserve environment identity across languages; extraction and architecture semantics still need implementation |
| [Observable documentation, undated][observable] | Reactive notebooks combine computation and interactive visualization | Reactive dataflow can refresh evidence panels; notebook dependencies do not themselves describe application architecture |
| [IPython rich display, undated][ipython] | `_repr_html_`, other rich representations, MIME bundles, and third-party formatters customize objects | Keep a structured representation alongside HTML so agents need not interpret rendered markup |
| [evcxr Jupyter, undated][evcxr] | `evcxr_display` emits MIME-typed output blocks, including HTML and images, from Rust | Useful for inspected examples; serialized observations remain easier to archive and compare |
| [VS Code custom editors][vscustom] and [notebooks][vsnotebook], undated | Custom editors pair a document model with a webview; notebook APIs separate serialization, execution, and output rendering | Build one host adapter, then reuse declarative render plans across segment-specific views |
| [CodeSee overview, undated][codesee] | Codebase maps, annotations, tours, and review maps expose change context | A close review precedent. Docs establish the design; current service availability and productivity gains are **[unverified]** |
| [Sourcegraph precise navigation, undated][sourcegraph] | SCIP indexes provide language-independent symbol navigation, including TS, Rust, Python, and Kotlin | Reuse indexed identity and reference facts. Domain meaning requires additional modeling |
| [LSP 3.17 specification, undated][lsp] and [tree-sitter queries, undated][treesitter] | Language-service requests and syntax-tree patterns expose different levels of structure | Capability negotiation matters. Syntax matches do not prove runtime calls or complete dependency closure |
| [Bret Victor, 2012-09][victor] | Interactive demonstrations expose values, execution flow, and time | Use timelines and scenario replay. The essay's learning and design arguments do not establish industrial productivity |

An especially relevant current precedent is React's experimental `react-devtools-cdt-mcp`. Official docs expose component trees, props, hooks, owners, source locations, and render timing to agents, and warn of development-time overhead and unstable interfaces. **Grade C for capability; no demonstrated token or review-quality gain.** [Undated, accessed 2026-11-10][reactagents]

## Spec: a language-agnostic moldable-view system

This section is an original proposal, **grade D**, not an implemented standard or a claimed description of your review tools. The unit is a named question about a selected codebase segment, backed by reproducible facts. A segment can be a crate, package, service, component family, configuration, scenario, or cross-language boundary.

### Descriptor and evidence model

Store descriptors beside the code they explain, with shared templates for recurring structures. Serialize them as JSON; TypeScript below describes the proposed wire format. The descriptor selects data, records how to extract it, and declares how to present it. It contains no executable rendering script.

```typescript
type Json = null | boolean | number | string | Json[] |
  { [key: string]: Json };
type Ref = string;
type Query =
  | { op: "facts"; relation: string }
  | { op: "filter"; input: Query; field: string; equals: Json }
  | { op: "walk"; input: Query; relation: string;
      direction: "out" | "in"; depth: number }
  | { op: "project"; input: Query; fields: string[] }
  | { op: "join"; left: Query; right: Query; on: [string, string] }
  | { op: "groupCount"; input: Query; by: string[] };
type Render =
  | { kind: "tree"; rows: Ref; id: string; parent: string }
  | { kind: "graph"; nodes: Ref; edges: Ref;
      source: string; target: string; groupBy?: string }
  | { kind: "table"; rows: Ref; columns: string[] }
  | { kind: "timeline"; rows: Ref; time: string; lane: string;
      clock: "monotonic" | "wall"; unit: "ns" | "ms" }
  | { kind: "diff"; base: Ref; head: Ref; keys: string[] }
  | { kind: "story"; steps: Array<{
      question: string; view: Ref; claimIds: string[] }> };
interface ViewDescriptor {
  schema: "moldable.view/1";
  id: string;
  owner: string;
  question: string;
  segment: { roots: string[]; languages: string[];
    entityKinds: string[]; exclude: string[] };
  activate: { allCapabilities: string[]; tags: string[] };
  parametersSchema: Json;
  extract: Array<{
    id: string;
    provider: "tree-sitter" | "lsp" | "compiler" |
      "manifest" | "runtime";
    adapter: string;
    digest: string;
    config: Json;
    needs: string[];
    required: boolean;
    outputSchema: Ref;
    permissions: Array<"read-workspace" | "execute" | "network">;
    limits: { timeoutMs: number; memoryMiB: number; maxFacts: number };
  }>;
  datasets: Record<string, Query>;
  render: Render[];
  navigation: Array<{ dataset: Ref; entityField: string }>;
  validation: { fixtureRefs: Ref[]; invariantRefs: Ref[] };
  agent: { defaultDataset: Ref; maxBytes: number; sourceExpansion: true };
}
interface Fact {
  id: string;
  relation: string;
  subject: Ref;
  object: Json;
  basis: "syntax" | "resolved" | "observed" | "inferred";
  evidenceIds: Ref[];
}
interface Evidence {
  id: Ref;
  snapshot: Ref;
  extractor: Ref;
  source: { path: string; blobHash: string;
    byteRange?: [number, number] };
  observation?: { runId: string; scenario: Ref; configHash: string };
}
type ExtractionOutcome =
  | { kind: "complete"; artifact: Ref }
  | { kind: "partial"; artifact: Ref; gaps: string[] }
  | { kind: "unsupported"; capability: string }
  | { kind: "refused"; permission: string }
  | { kind: "failed"; code: string; retryable: boolean };
```

`Ref` values resolve inside a manifest, with an explicit namespace for datasets, artifacts, entities, and evidence. A published implementation must provide JSON Schema for descriptors, provider configurations, and relation records. Validate query field types and rendering bindings before extraction. Preserve unknown extension fields only within namespaced extension objects; reject unknown required operations.

Each relation has a registered meaning and typed columns. Distinguish `imports`, `jsxReferences`, `declaresRequirement`, `implements`, `mayCall`, `observedCall`, `convertsError`, and `assertsClaim`. An edge named `dependsOn` without a defined meaning is insufficient. Entity records contain kind, qualified name, language, source anchors, and tool-native identifiers when available. Facts about unavailable destinations point to explicit external or unresolved entities.

An extraction manifest records repository identity, commit, dirty-tree content digest, descriptor digest, lockfile digest, toolchain, adapter versions, target, features, environment allowlist, and extraction time. Its coverage lists included and excluded inputs, unresolved symbols, and limits reached. A complete result means the declared extraction contract completed within that scope. It does not prove that the model captures every behavior.

Freshness is separate from extraction outcome. A successfully generated artifact becomes stale when an input changes; it does not become an empty result. An empty complete dataset is valid only when the extractor actually examined the declared scope. Renderers must display gaps and freshness, and agent responses must include them.

### Extractor interface and execution

Use a subprocess protocol over standard input/output with JSON-RPC messages, allowing adapters in any implementation language. `describe` returns versions, supported relations, schemas, configuration needs, and capabilities. `extract` receives an immutable snapshot reference, segment, parameters, grants, and cancellation token. It returns an outcome plus a content-addressed artifact. `resolveEvidence` retrieves a bounded source slice or observation by ID. Progress and diagnostics are separate messages; duplicate completion messages are rejected.

Run extraction in dependency order, with `needs` forming an acyclic plan. A missing required provider blocks publication as complete. Missing optional runtime data produces a partial view with a named gap. Negotiate capabilities before selecting a template, rather than treating an unavailable LSP request as an empty response.

Tree-sitter queries match syntax patterns, while LSP offers language-service operations through negotiated capabilities. These are different evidence levels. **Grade C for those mechanisms.** [Official query documentation, undated, accessed 2026-11-10][treesitter]; [LSP 3.17 specification, same access date][lsp]

The proposed adapters use syntax extraction for cheap candidates, language services or compiler metadata for resolution, and bounded probes for observations. A runtime probe identifies its scenario and input digest. It cannot establish that an unobserved edge never executes. Contradictory sources remain visible as separate facts with diagnostics; no generic "highest confidence wins" rule discards them.

Read-only is an execution policy, not a descriptor promise. Runtime probes, compiler plugins, build scripts, and macro execution may run repository code. Grant execution separately, deny network by default, bound resources, and redact secrets before serialization. A descriptor from a repository cannot grant itself permissions. Treat labels, comments, and generated stories as data, including when an agent consumes them.

Cache by the complete input manifest and content hashes. Invalidate a syntax adapter on changed files, a semantic adapter on relevant configuration or dependency changes, and runtime observations on scenario or executable changes. If dependency tracking cannot prove a cached result is reusable, re-extract the segment. Keep stable symbol identities within a snapshot; across snapshots, record rename/move candidates and ambiguity instead of forcing identity matches.

### Generate views per segment and compile them into tools

Generation begins with a question inventory. Inspect manifests, entry points, existing claims, test scenarios, and segment boundaries. Instantiate templates such as component ownership, typed failures, option provenance, and queue lifecycle. A person or agent can propose a new descriptor, but publication requires schema validation, extractor checks, and inspection of a small example. Language-specific adapters remain explicit dependencies of a language-independent descriptor.

Apply activation predicates to both capability and context. A React component activates JSX and observed-component views; a Rust public function returning `Result` activates error-flow views. Segment-specific annotations may refine the question. A single dependency map must not be mistaken for a complete architecture. Let you retain a useful throwaway query or delete it after answering the question.

The compiler produces a normalized render plan containing datasets, encodings, filters, navigation, and provenance. Host adapters consume this plan. They do not regenerate facts. Initial targets should be a CLI, a browser component embedded in an existing application, and a notebook output adapter. VS Code's documented custom-editor and notebook APIs offer suitable hosting mechanisms, **grade C**. [Undated, accessed 2026-11-10][vscustom]; [notebook API, same access date][vsnotebook]

A CLI returns canonical JSON, compact tables, or a text story. A web component implements linked selection between graphs, tables, and source anchors. A notebook wraps the same bundle in a MIME representation; Portal or Clerk integration can come later. Unsupported rendering falls back to a table with a visible explanation. Keep selection, filters, layout, and navigation history as user state, separate from extracted evidence. All navigation must work through entity IDs without requiring screen coordinates.

### Worked TypeScript example

Consider a hypothetical segment containing `UserPanel`, `useUser`, and `loadUser`. Effect v3 documentation describes `Effect<Success, Error, Requirements>` as a lazy program description with typed failures and required context. Its error type describes expected failures, so it must not be advertised as every possible runtime failure. **Grade C for the type model.** [Undated, accessed 2026-11-10][effect]; [error documentation, same access date][effecterrors]

```typescript
declare const loadUser:
  (id: string) => Effect.Effect<User, NetworkError | DecodeError, Api>;
```

Propose `ts.user-loading/1`, activated for `src/users/**` with React and the pinned Effect version. Required adapters extract JSX references, resolve imported symbols, inspect inferred signatures and Effect type arguments, and identify explicit service provision. An optional scenario adapter records a failed request and the resulting rendered state. TypeScript's compiler API exposes a program and type checker; its API is version-sensitive, so record and pin the compiler adapter. **Grade C.** [Official compiler API guide, undated, accessed 2026-11-10][tscompiler]

The resulting datasets should separate four questions:

- A component graph shows `UserPanel` referencing child components and the hook symbol. Imported aliases resolve to their declarations; conditional JSX edges remain possible relationships.
- A service graph shows `loadUser` requiring `Api`, with provision sites recorded separately. A type requirement alone does not identify which runtime implementation will be selected.
- An error table lists `NetworkError` and `DecodeError`, source signatures, recognized handling sites, and unresolved consumers.
- A scenario timeline records the request failure and observed UI response, with a named fixture and run ID.

Connect `useUser` to `loadUser` only through a resolved reference or an explicit, cited adapter rule. An agent's guess about the hook's meaning becomes an inferred edge. Lazy imports, higher-order components, and dynamically selected implementations create named gaps until better extraction or instrumentation resolves them.

A hypothetical change adds `Unauthorized` to `loadUser`'s expected errors. The semantic diff adds a failure alternative, identifies affected consumers and handlers, and opens the error-state example. A story asks whether the UI shows reauthentication, retries, or an unclassified failure. It makes no claim that a displayed signature proves behavior. A compiler diagnostic and an observed scenario are separate supporting evidence.

### Worked Rust example

Consider another hypothetical segment:

```rust
trait Repository {
    fn load(&self, id: u64) -> Result<User, StoreError>;
}
enum ApiError { Storage(StoreError) }
fn get_user<R: Repository>(repo: &R, id: u64) -> Result<User, ApiError> {
    repo.load(id).map_err(ApiError::Storage)
}
```

Propose `rust.user-errors/1`, activated for the handler crate and its repository boundary. Cargo metadata supplies workspace members and resolved dependency information; request its explicit format version. **Grade C.** [Cargo Book, undated, accessed 2026-11-10][cargo]

Use that information for the crate graph. Use source parsing plus semantic resolution for traits, implementations, signatures, `?` sites, and conversion expressions. Optional rustdoc JSON can enrich public API facts, but its unstable format requires toolchain and format pinning. It must not be assumed to expose complete function-body error flow. **Grade C for documented metadata capabilities.** [rustdoc-types documentation, undated, accessed 2026-11-10][rustdoctypes]; [docs.rs JSON service, same access date][rustdocjson]

The graph shows the trait declaration, known implementations, and `get_user`'s generic requirement. A known implementation is a candidate, not evidence that a particular request selected it. Record target triples and feature sets; different configurations produce separate snapshots. Generated and macro-expanded symbols need source mappings or explicit gaps.

The error view follows the example's explicit `StoreError` to `ApiError::Storage` conversion. If a downstream adapter maps that variant to HTTP 500, display the mapping with its match arm as evidence. A scenario can demonstrate an unavailable store reaching that response. New error variants, changed `From` implementations, `map_err` erasure, or a new catch-all branch should appear as changed relations. Panics, cancellation, opaque dynamic errors, and foreign calls remain separate limits on the analysis.

For a review, show the changed conversion, unchanged callers that can receive it, and the scenario demonstrating the boundary behavior. A trait/crate overview locates the architectural change; the error-flow table exposes its operational consequence. You can then inspect the exact expression and test without rereading the entire crate.

### Secondary language adapters

These are proposed contracts, **grade D**, not claims of completed integrations:

| Language | Initial extraction | Useful contextual view | Required limitation |
|---|---|---|---|
| Nix | Parse imports/options, then optionally evaluate a selected host and export declaration/definition locations | Host/module tree, option provenance, before/after configuration | Respect your host-only evaluation rule; syntax imports cannot establish evaluated module behavior |
| Python | Syntax and language-service symbols, optional instrumented fixtures | Import graph, exception observations, data transformations | Dynamic imports, decorators, monkey patching, and execution-specific types remain gaps |
| Kotlin | Gradle metadata plus a pinned compiler or language-service adapter | Module/trait-like interface relationships, coroutine scenarios, error handling | Build variants, generated code, and runtime dispatch require explicit configuration and evidence |

## Feeding a story and architecture review tool

The integration below is **grade D**, a proposed fit to your request. I cannot identify existing extension points in `diff-core` or `residual-cli` from this machine. Treat both as potential consumers of an evidence-bundle interface until the missing drafts can be read.

Run extraction on the exact base and head snapshots under equivalent configurations. Compute semantic changes by relation and entity identity. Keep deleted entities and their base evidence available. Report ambiguous rename matches instead of silently merging them. Configuration changes may explain an apparent architecture change; expose them beside the delta.

Group review work into questions about behavior and boundaries. A story might read: "User loading now distinguishes expired credentials. This changes the service's failure contract, the hook's classification, and the panel's recovery action." Each clause has claim IDs and cited facts. The story contains proposed intent, extracted changes, affected unchanged entities, scenario evidence, remaining questions, and links to exact source changes. An LLM can propose the grouping and wording; deterministic checks validate that referenced facts and source anchors exist.

Architecture adds another dimension. A segment annotation might declare that UI code reaches storage through a service boundary. A new direct edge can then trigger a question even when functional tests pass. Store intended architecture as authored policy and observed/extracted architecture as evidence. Their difference is review material. An inferred naming convention cannot silently become a mandatory policy.

A review finding needs a concrete condition, a violated claim or policy, supporting evidence, and unresolved assumptions. A graph's appearance alone does not prove a defect. Likewise, a pleasing story must not hide an unrelated change: maintain a changed-entity and hunk coverage ledger, allowing one hunk in several stories and showing unassigned changes. Keep a path back to line-level inspection for deletions, boundary expressions, and details the extractors cannot model.

The first integration artifact should therefore be a versioned bundle file plus a CLI command that selects a question, returns bounded JSON, and expands cited evidence. Either review project could ingest it without sharing a UI or model provider. An archive of base/head bundles would also make review experiments repeatable. Whether either project's offline draft already supplies this abstraction is **[unverified]**.

## Making the codebase legible to agents

The proposed benefit is reusable computation. A typed service inventory or conversion path lets an agent retrieve relevant structure without repeatedly reconstructing it from source files. Stable IDs connect claims, tests, scenarios, and affected callers. Content hashes tell the agent which observations survived a change. These are **grade D** hypotheses about agent cost and correctness, not measured improvements.

Provide operations equivalent to `listViews(segment)`, `query(view, parameters, cursor)`, `expandEvidence(ids, byteBudget)`, and `compare(base, head, relation)`. A response includes the question, snapshot, coverage, relevant facts, source pointers, next-page cursor, and omissions caused by its budget. Use deterministic ordering and continuation tokens tied to a snapshot. Never truncate silently or report a truncated graph as exhaustive.

Agents should receive compact typed records first, then request the source slices necessary for their decision. Humans inspect the same facts through linked views. This can reduce rereading without requiring a separate agent-only architecture description that drifts from the human one. Keep source expansion available because an extractor's abstraction can omit the very detail a bug depends on.

Measure the whole cost, including extraction, failed queries, repair, and source expansion. For example, a smaller first response may cause more follow-up calls. Token savings without correct answers would be a regression.

## Where your setup differs

These comparisons use repository skills inspected on 2026-11-10. The skills are local instructions, not evidence that the workflow produces particular outcomes.

Your [question-everything](../skills/question-everything/SKILL.md) already makes questions, missing states, and explicit unknowns part of design. Moldable practice suggests preserving executable ways to answer those questions. The prototype should carry its questions into descriptors and expose partial, refused, and stale states.

Your [technical-excellence](../skills/technical-excellence/SKILL.md) connects claims to sources and proof through stable IDs. Make those IDs navigable in views, with independent evidence behind them. This provides more structure than an automatically narrated graph whose assertions cannot be traced.

Your [test-quality](../skills/test-quality/SKILL.md) requires independent expectations and mutation checks. That addresses a weakness of exploratory examples: assertions can accidentally bless observed behavior. Preserve your standard when adding inspectable outputs. A generated view and its extractor cannot serve as each other's only oracle.

Your [rg-implement](../skills/rg-implement/SKILL.md) and [build-loop](../skills/build-loop/SKILL.md) specify red tests and verification gates. Example-driven exploration can precede a settled assertion; that differs from the prescribed red-first sequence. Keep exploration explicitly marked as discovery, then run your existing gates once the claim is defined. Views can support reviewers between phases, but they do not establish that those gates are unnecessary.

Your tea (private source; not included) already preserves otherwise-lost pipeline input. A moldable wrapper could link a command, captured bytes, parsed records, and the question that caused the analysis. Reuse that capture instead of rerunning an expensive operation. Your host rules (private evidence; not included) also favor bounded segments: Nix views must respect host-specific evaluation and resource limits.

## Candidate actions

All actions below are **grade D** proposals, ranked by expected value relative to cost.

1. **Highest value, low cost:** Pick one TS error-contract change and one Rust conversion change as manually reviewed fixtures. They define useful questions before you invest in a view platform.
2. **High value, moderate cost:** Implement the manifest, fact/evidence records, partial-result handling, and CLI export. They let human and agent consumers share trustworthy inputs.
3. **High value, moderate cost:** Build only the TS error/service view and Rust crate/error view, with a table renderer first. They exercise semantic extraction without a large graph UI.
4. **High value, moderate cost:** Compare ordinary review against review with bundles on at least 12 distinct seeded tasks, balanced across TS and Rust. Counterbalance task allocation; record correctness, missed defects, false findings, time, tokens, extractor cost, and rereads. Pin model/version, prompts, budgets, toolchains, and inputs. Publish all trials and uncertainty; this pilot would not justify broad productivity claims.
5. **Medium value, moderate cost:** Test aliases, renamed symbols, stale caches, cfg changes, unavailable providers, and denied execution against independent fixtures. Mutate a relation and verify the review question changes. This checks whether views preserve the distinctions they advertise.
6. **Medium value, low cost after access returns:** Read the newest void drafts before selecting a `diff-core` or `residual-cli` integration point. Avoid designing against an obsolete local interface.
7. **Lower immediate value, high cost:** Add live probes, notebook adapters, and secondary languages only after the pilot shows correct answers at an acceptable total cost.

## Sources

Dates below are publication dates where available. "Undated" means the source exposes no verified publication date; all such sources were accessed 2026-11-10. Capability documentation is not a controlled outcome study.

- [The Moldable Inspector][inspector], Chiş, Nierstrasz, Syrel, and Gîrba, Onward! 2015-10. Interviews, survey, prototype, and explicit evaluation limitation.
- [Exemplifying Moldable Development][exemplifying], Chiş et al., PX 2016-07-18. Compiler/parser demonstrations.
- [The Story of Moose][moose], Nierstrasz, Ducasse, and Gîrba, ESEC/FSE 2005-09. Language-independent reengineering models.
- [Moldable Development Patterns][patterns], Nierstrasz and Gîrba, preprint 2024-09-27. Patterns and GT view counts.
- [Moldable Exceptions][exceptions], Chiş, Gîrba, and Nierstrasz, preprint 2024-08-31, Onward! 2024. Contextual debugging.
- [Example-driven development][edd], Nierstrasz, Chiş, and Gîrba, preprint 2024-08-31, LIVE 2024. Tested factories and live documentation.
- [Measuring Program Comprehension][comprehension], Xia et al., journal publication 2018-10. Observational field study.
- [Rewilding chapter 1][rewild1], [chapter 2][rewild2], and [chapter 3][rewild3], Gîrba and Wardley, 2025-02-06.
- [Rewilding chapter 5][rewild5], Gîrba and Wardley, 2025-05-22; [chapter 6][rewild6], 2026-01-16.
- [feenk research index](https://feenk.com/labs), undated. Links the book and research program.
- [GT PythonBridge][pythonbridge], [Python through LSP][gtlsp], [React Native analysis][gtjs], and [wrapped Rust objects][gtrust], undated.
- [Clerk][clerk], [Portal custom-viewer example][portal], and [Nextjournal][nextjournal], undated.
- [Observable notebooks][observable], [IPython rich display][ipython], and [evcxr Jupyter][evcxr], undated.
- [VS Code custom editors][vscustom] and [notebook API][vsnotebook], undated.
- [CodeSee overview][codesee] and [Sourcegraph precise navigation][sourcegraph], undated.
- [LSP 3.17][lsp], [tree-sitter queries][treesitter], and [TypeScript compiler API][tscompiler], undated.
- [Learnable Programming][victor], Bret Victor, 2012-09.
- [React DevTools for agents][reactagents], experimental documentation, undated.
- [Effect v3 type model][effect] and [expected errors][effecterrors], undated, version-specific documentation.
- [Cargo metadata][cargo], [rustdoc-types][rustdoctypes], and [docs.rs JSON][rustdocjson], undated. The last source states JSON hosting began 2025-05-23.
- Local [brief](BRIEF.md), AGENTS.md (private evidence; not included), and skills linked above, inspected 2026-11-10. Requested sibling project files were unavailable.

[inspector]: https://scg.unibe.ch/archive/papers/Chis15a-MoldableInspector.pdf
[exemplifying]: https://scg.unibe.ch/archive/papers/Chis16b-ExemplifyingMoldableDevelopment.pdf
[moose]: https://scg.unibe.ch/archive/papers/Nier05cStoryOfMoose.pdf
[exceptions]: https://arxiv.org/abs/2409.00465
[patterns]: https://arxiv.org/html/2409.18811v1
[edd]: https://arxiv.org/html/2409.00514v1
[comprehension]: https://research.monash.edu/en/publications/measuring-program-comprehension-a-large-scale-field-study-with-pr/
[rewild1]: https://medium.com/feenk/rewilding-software-engineering-900ca95ebc8c
[rewild2]: https://medium.com/feenk/rewilding-software-engineering-083b86c81c43
[rewild3]: https://medium.com/feenk/rewilding-software-engineering-f758ec97ddb2
[rewild5]: https://medium.com/feenk/chapter-5-different-folks-for-different-strokes-70d24a750dff
[rewild6]: https://medium.com/feenk/rewilding-software-engineering-ca3ad1e612d8
[pythonbridge]: https://book.gtoolkit.com/pythonbridge-d44mtgb6jzpvc9khii80twwmv
[gtlsp]: https://book.gtoolkit.com/editing-python-sources-through-the-languag-6lcodb2a1g9eedqqu467kqr9m
[gtjs]: https://book.gtoolkit.com/analyzing-javascript-react-native--the-zoo-6zpcqog4adclo0n9k49xy014x
[gtrust]: https://book.gtoolkit.com/identifying-an-editor-bug-by-inspecting-wr-b8yxhb2g48gene8jdbcdlyu2l
[clerk]: https://clerk.vision/
[portal]: https://github.com/djblue/portal/blob/master/examples/portal-present/README.md
[nextjournal]: https://nextjournal.com/
[observable]: https://old.observablehq.com/
[ipython]: https://ipython.readthedocs.io/en/stable/config/integrating.html
[evcxr]: https://github.com/evcxr/evcxr/blob/main/evcxr_jupyter/README.md
[vscustom]: https://code.visualstudio.com/api/extension-guides/custom-editors
[vsnotebook]: https://code.visualstudio.com/api/extension-guides/notebook
[codesee]: https://docs.codesee.io/docs/getting-started
[sourcegraph]: https://sourcegraph.com/docs/code-navigation/precise-code-navigation
[lsp]: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
[treesitter]: https://tree-sitter.github.io/tree-sitter/using-parsers/queries/1-syntax.html
[tscompiler]: https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API
[victor]: https://worrydream.com/LearnableProgramming/
[reactagents]: https://react.dev/reference/dev-tools/react-devtools-cdt-mcp
[effect]: https://effect.website/docs/v3/getting-started/the-effect-type
[effecterrors]: https://effect.website/docs/v3/error-management/expected-errors
[cargo]: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
[rustdoctypes]: https://docs.rs/crate/rustdoc-types/latest
[rustdocjson]: https://docs.rs/about/rustdoc-json


