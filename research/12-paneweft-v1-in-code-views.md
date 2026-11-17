# Paneweft v1: permanent views written in the codebase

Design and research date: 2026-11-11. Owner direction from the same date takes precedence over the v0 design. This is a proposal, with researched mechanisms distinguished from proposed APIs. None of the SDKs, macros, adapters, or commands introduced here has been implemented or run during this read-only task.

Paneweft should let an agent answer a recurring question by adding a small, tested view beside the code that owns the answer. A vigil watch should know how to show its status and events. A ContainMarks mapping should know how to show its original index, current container ID, and backup name. Running examples should publish those views automatically. The useful result of the agent's work is checked-in instrumentation that the next agent can discover and run.

Agent integration is the first product requirement. The browser and bounded text must expose the same collected facts, and an agent must be able to discover, author, test, repair, and retain a view without an editor extension. Humans use the same SDK and commands. Python, Kotlin, and Nix follow Rust and TypeScript. The SDKs live as packages in the paneweft monorepo. V1 records snapshots; live process attachment is outside its scope. Repo-owned custom renderers run in sandboxed iframes. SDK hooks are development-only.

## 1. What GT does outside Pharo

Glamorous Toolkit, GT, already separates the runtime that owns an object from the inspector that displays it. PythonBridge executes Python in another process. Primitive results can cross as values; other results normally cross as proxies backed by Python-side object IDs. This is stronger than asking an external process to print JSON. The inspector can keep referring to the same remote object. [PythonBridge, undated, accessed 2026-11-11](https://book.gtoolkit.com/pythonbridge-d44mtgb6jzpvc9khii80twwmv).

Python objects can declare views in Python. The documented `@gtView` decorator identifies methods that receive a builder and return a view. Builders include lists, columned lists, columned trees, text editors, forwarding, and an empty result. Item and child functions execute against Python values. The documented list accessor can choose the object inspected when a row is selected. [Phlow for Python, undated, accessed 2026-11-11](https://book.gtoolkit.com/phlow-for-python-dyl98a2rcczf8f4tdf7e1pstj).

JSLink connects Pharo to Node. Its own README describes remote proxies and a playground whose `this` refers to the remote object. The JavaScript implementation also supports declarations in JavaScript: its example class has `gtViewList`, `gtViewColumnedList`, and `gtViewString` methods. These methods call builders over `this.collectionOfObjects` and `this.string`. This source uses a method-name convention, not Python's decorator or Pharo's pragma. [JSLink README, undated](https://github.com/feenkcom/JSLink); [JavaScript declarations, revision committed 2026-04-29](https://github.com/feenkcom/JSLink/blob/a35d1cdaf47fe513d7393b3e3eafd8d9c11e34fb/js/src/gtoolkit/gtdeclarativetestinspectable.js). Both accessed 2026-11-11.

The JavaScript `GtViewedObject` wrapper discovers prototype methods beginning with `gtView`, adds Raw and Print views, invokes the selected method, and exports its declaration. Its `sentItem` method runs the view's accessor to obtain the selected value. The list implementation calls the items callback and formats values in Node before exporting data. This establishes remote-side view computation in the inspected implementation; it does not establish that every JavaScript builder has the same capabilities as Phlow in Pharo. [Viewed-object source](https://github.com/feenkcom/JSLink/blob/a35d1cdaf47fe513d7393b3e3eafd8d9c11e34fb/js/src/gtoolkit/gt.js), [list source](https://github.com/feenkcom/JSLink/blob/a35d1cdaf47fe513d7393b3e3eafd8d9c11e34fb/js/src/gtoolkit/phlow/view_list.js), revision committed 2026-04-29, accessed 2026-11-11.

Remote Phlow transfers view declarations while a data source retains access to the remote view. Its documented list specification can retrieve a range of items, ask for a count, and retrieve the object sent by a selection. The local specification delegates these operations to its data source. The transport documentation describes a viewed-object wrapper around an ID-backed object proxy, including Python's `getRemoteInspectorProxy`. These are distinct responsibilities: identity names the object, a declaration describes its views, and a data source computes their content. [Specifications and views in Remote Phlow](https://book.gtoolkit.com/specifications-and-views-in-remote-phlow-46q0vxcbktxg7dsjwcda9p0v7), [transferring remote views](https://book.gtoolkit.com/transferring-remote-views-buhedm0ks7gau5xf36n0jg3iq), undated, accessed 2026-11-11.

`<gtExample>` marks an ordinary method as an executable example. An example can assert facts and return the object under test; another example can call it to build a further example. The returned value gives testing, inspection, and documentation a shared fixture. This is a useful mechanism to port, without assuming that arbitrary Python or JavaScript functions automatically participate in GT's example runner. [GT example tutorial, undated](https://book.gtoolkit.com/example-driven-development-by-example-wmr9ggp9fan2j19g4z4crz0m); [Nierstrasz, Chiş, and Gîrba, preprint 2024-08-31](https://arxiv.org/html/2409.00514v1), accessed 2026-11-11.

Lepiter already hosts Python and JavaScript snippets through PythonBridge and JSLink. Values encodable by the protocol can be shared between snippets on a page. These are persistent execution environments with lifecycle constraints: the documentation warns that restarting the runtime invalidates object-registry references held by evaluated pages. Paneweft should initially link notebook blocks to reproducible examples and their stored objects. Multi-language notebook execution would require a separate lifecycle design. [Python snippet](https://book.gtoolkit.com/python-snippet-9buo5kotm456xgsqrbrq5xpq3), [JavaScript snippet](https://book.gtoolkit.com/javascript-snippet-94jgbip23xvy0f5mhx9bjayhu), undated, accessed 2026-11-11.

The portable mechanisms are therefore code-defined view methods, explicit registration, computation where the values exist, reusable examples, and selection that names another object. Paneweft v1 substitutes immutable object records for GT's retained remote proxies. That substitution preserves inspection after the test process exits and makes the boundary of each observation explicit.

### Other precedents and their consequences

The following sources describe capabilities, not evidence of a productivity multiplier. All were accessed 2026-11-11; documentation without a verified publication date is marked undated.

| Prior art | Verified mechanism | Consequence for paneweft |
|---|---|---|
| [IPython display protocol](https://ipython.readthedocs.io/en/stable/config/integrating.html), undated | A type supplies `_repr_html_` or `_repr_mimebundle_`; external formatters can support third-party types. A representation can decline applicability. | Make a view an ordinary typed function, support external adapters, and have an explicit unsupported result. Arbitrary HTML remains outside the ordinary data protocol. |
| [Clerk's viewer documentation](https://github.com/nextjournal/clerk/blob/main/book.clj), undated | Predicates choose viewers; `:transform-fn` presents values on the JVM and `:render-fn` renders in the browser. Presentation has budgets and supports partial loading. | Separate computing a view from rendering it. Keep collection limits distinct from display limits. V1 uses explicit type tokens instead of unrestricted predicate discovery. |
| [Portal](https://github.com/djblue/portal), undated | `add-tap` can connect `tap>` publication to Portal. Its README warns that retained inspected objects prevent garbage collection until cleared. | Provide `inspect(value)` at useful execution points, snapshot before returning, and retain no application objects after the capture. |
| [Rust `Debug`](https://doc.rust-lang.org/std/fmt/trait.Debug.html), undated | A trait and derive provide programmer-facing representations. Derived formatting is not a stable wire format. | Borrow its ergonomics, but use typed builders and schemas for machine-readable output. Never parse `Debug` strings into domain facts. |
| [evcxr custom output](https://github.com/evcxr/evcxr/blob/main/evcxr_jupyter/README.md#custom-output), undated | An `evcxr_display` method emits MIME-framed output, with Debug as the ordinary fallback. | Small opt-in methods are workable in Rust. Use dedicated artifacts instead of framing data in test stdout, where concurrent output can interleave. |
| [Storybook stories](https://storybook.js.org/docs/writing-stories), [interaction tests](https://storybook.js.org/docs/writing-tests/interaction-testing), undated | Named component states are reusable examples; `play` functions perform interactions and assertions. | An example owns a meaningful state, assertions, and a result. A screenshot alone does not prove the domain behavior. |
| [Vitest reporters](https://vitest.dev/guide/advanced/reporters), [Jest reporter configuration](https://jestjs.io/docs/configuration#reporters-arraymodulename--modulename-options), undated | Runners expose test-result reporting hooks. Vitest cautions that advanced reporting interfaces can change. | Pin supported versions. Capture values inside the test worker; use reporters to reconcile final outcomes. A reporter cannot recover arbitrary local variables. |
| [Cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html), [Rust custom-test-framework documentation](https://doc.rust-lang.org/unstable-book/language-features/custom-test-frameworks.html), undated | Cargo supports `harness = false` with an application-owned `main`; compiler-level custom test frameworks remain unstable in the inspected docs. | Keep stable libtest for the first adapter. Generate normal test wrappers. A separate custom runner can come later if its benefit is demonstrated. |
| [inventory](https://docs.rs/inventory/latest/inventory/), [linkme](https://docs.rs/linkme/latest/linkme/), undated | Both register items distributed across linked code. Inventory iteration has no guaranteed order; linkme gathers static entries through linker sections without runtime initialization. | Use linkme for native Rust descriptors, sort explicitly, and verify actual linkage. Neither library discovers source that was never linked. |
| [React DevTools for agents](https://react.dev/reference/dev-tools/react-devtools-cdt-mcp), undated, experimental | An imported library exposes component identity, props, hooks, source, and timing to agents through Chrome DevTools MCP. IDs survive re-renders but not reloads. | Instrument once and let agents query the instrumented model. Scope identities to a lifecycle. Paneweft's first lifecycle is a capture, with no React dependency or live attachment. |
| [MCP tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools), revision 2025-11-25; [annotation guidance](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/), 2026-03-16 | Tools have named schemas, discovery, and recoverable tool errors. Annotations are hints, not authorization enforcement. | Supply task-sized tools, bounded results, and repairable failures. Enforce collection permissions in the host. |

## 2. SDK architecture

Keep the current TypeScript host. Add Rust crates under `crates/paneweft`, `crates/paneweft-macros`, and `crates/paneweft-wire`, and TypeScript packages under `packages/sdk`, `packages/vitest`, and `packages/jest`. The host, CLI, viewer, MCP server, and wire contracts remain in paneweft. Start without moving all existing host files into packages. SDKs generate objects conforming to the canonical JSON Schemas under `src/schemas`; generated Rust and TypeScript wire types are derivatives of those schemas.

An SDK has two layers. The authoring layer accepts domain values, typed columns, fields, object references, and a capture context. The encoding layer supplies envelope IDs, evidence, run sources, source hashes, completeness, and immutable graph records. A view function returns `ViewResult`, either a built view or an explicit unsupported reason. Limits can turn a view into a partial result with named gaps. Ordinary programming errors and schema violations become diagnostics, never a successful empty view.

Existing list, tree, graph, source, shape, notebook, and example components remain the common output language. Pleasant helpers such as `details()` lower into the existing shape component. This does not constrain a repository to those renderers: a view can also produce a typed custom payload and a required standard-component fallback, described in section 5.

A capture context represents an observation of actual values. It automatically attaches a run source to observed rows. A declared type inventory or a source-code claim must explicitly select compiled, parsed, or read evidence instead. The SDK must not mark every statement emitted during a test as observed truth about every possible execution.

### Rust declarations

The base contract is a small `Inspectable` trait. It supplies a stable repository-owned type ID, metadata, and `views(&self, &mut Context) -> ViewSetResult`. It must work on a borrowed value. It must not require the whole value to implement `Serialize`, be `'static`, or cross a thread boundary. `ViewSetResult` can retain successful views alongside per-view diagnostics. A manual implementation is supported; attributes provide the normal concise form.

`#[paneweft::views(type_id = "...")]` on an inherent impl collects its annotated methods and generates the trait implementation and static discovery descriptors. Method metadata includes a stable ID, title, question, component, priority, and source location. Adding a view does not require editing the viewer. `#[derive(paneweft::Inspect)]` (an opt-in field/shape view for simple types with skip/redact annotations) was proposed here and is NOT shipped: week one defers it (S1), and the shipped SDK has no such derive. A type that needs a shape view writes it with `#[paneweft::views]`. More elaborate composition can wait.

This proposed code belongs beside `WatchFile` in vigil's `src/watch.rs`. The fields and methods used here exist in the inspected source. `Event` gets a small hand-written `#[paneweft::views]` view in the same change (`event.details`), explicitly selecting only `event_id`, `tick`, and `redelivered`. In particular, omit `summary` because it can contain log content. The code below is the API the SDK ships (field-test fix F30): it is the `WatchFile` and `Event` instrumentation of `fixtures/crates/watchfile` in the paneweft repository, which the test suite compiles and runs with real cargo. `cx.details()` returns a builder and `details.field(..)` / `details.finish()` end it; `cx.table()` returns a builder, rows are added with `table.row(..)`, and `table.finish()` ends it; a row's `target` comes from `cx.reference_keyed(event, &event.event_id)?` because two redelivered events share a domain id and must stay two objects.

```rust
#[cfg(feature = "paneweft")]
#[paneweft::views(type_id = "vigil::watch::WatchFile")]
impl WatchFile {
    #[paneweft::view(
        id = "watch.status", title = "Status", component = "shape", priority = 10,
        question = "What state did this watch reach?"
    )]
    fn status_view(&self, cx: &mut paneweft::Context) -> paneweft::ViewResult {
        let mut details = cx.details();
        details.field("status", format!("{:?}", self.status));
        details.field("tick", self.tick);
        details.field("judge status", format!("{:?}", self.judge_status));
        details.field("event count", self.events.len());
        details.finish()
    }

    #[paneweft::view(
        id = "watch.events", title = "Events", component = "list", priority = 20,
        question = "Which events were retained, and were they redelivered?"
    )]
    fn events_view(&self, cx: &mut paneweft::Context) -> paneweft::ViewResult {
        let mut table = cx.table()
            .text_column("event", "Event")
            .number_column("tick", "Tick")
            .boolean_column("redelivered", "Redelivered")
            .order_by("event", paneweft::Ascending);
        for (index, event) in self.events.iter().enumerate() {
            let target = cx.reference_keyed(event, &event.event_id)?;
            table.row(paneweft::Row::new(format!("event-{index}"))
                .cell("event", event.event_id.as_str())
                .cell("tick", event.tick)
                .cell("redelivered", event.redelivered)
                .target(target));
        }
        table.finish()
    }
}
```

The row ID is an occurrence, not the event's domain ID. Vigil explicitly documents that save failures can produce repeated `event_id` values with different contents on redelivery. A view must retain both occurrences and their object records. The label still shows the domain ID. A snapshot-scoped identity policy must not silently deduplicate them.

Use linkme for native descriptors behind the SDK feature. Records contain type/view/example metadata and function pointers where callable without a value. The typed trait dispatches views over borrowed receivers; avoid forcing all values through `Any` merely to list them. The initial macro supports concrete types; generic instantiations require explicit registration. A manual descriptor slice is the fallback for an unsupported linker target. Inventory is a viable alternative if target testing exposes linkme problems, but switching libraries does not remove the need to sort, reject duplicate IDs, and ensure registration modules are linked.

One `paneweft::test_adapter!()` invocation in each participating test binary emits a reserved catalogue-export test. The cargo adapter runs only those reserved tests in catalogue mode. They enumerate descriptors without executing example bodies. Registrations in another unlinked crate or an unselected Cargo target are outside that catalogue's scope. Discovery reports the target and feature set so absence is not mistaken for repository-wide coverage.

For source-level hooks outside tests, vigil would add this feature wiring. The path is development setup for the proposed monorepo crate, not an existing package publication.

```toml
[features]
paneweft = ["dep:paneweft"]

[dependencies.paneweft]
path = "../../../paneweft/crates/paneweft"
optional = true
```

Gate the whole instrumentation impl or module with `cfg(feature = "paneweft")`. Tests use `cfg(all(test, feature = "paneweft"))`. A release recipe excludes this feature, and package metadata lets CI check the resolved dependency graph. `debug_assertions` alone is insufficient because developers can build optimized instrumented binaries. Cargo features are additive, so a release check must catch accidental activation through a dependency. [Cargo features, undated, accessed 2026-11-11](https://doc.rust-lang.org/cargo/reference/features.html).

### TypeScript declarations

TypeScript interfaces disappear at runtime. Use an explicit `defineType<T>()` token with a stable type ID and source reference. `inspect(value, TypeToken)` works for plain records without modifying their shape or guessing their type from property names. A class can implement `Inspectable` through a symbol method, ``paneweftViews``, returning the same registered definitions. A future `@view` decorator is syntax sugar over those definitions, not a separate discovery system. Standard and legacy TypeScript decorators differ; the first SDK should avoid imposing either on a project. [TypeScript 5.0 decorator documentation, undated, accessed 2026-11-11](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html).

ContainMarks already has `ContainerMappingRecord` with the three fields below. This proposed sibling module, `src/mappings/containerMappings.paneweft.ts`, is imported only by tests and an optional development entry point. It needs no Firefox process or API mocks to present an existing record.

```ts
import { defineType } from '@paneweft/sdk'
import type { ContainerMappingRecord } from '../models'

export const Mapping = defineType<ContainerMappingRecord>({
  id: 'containmarks::ContainerMappingRecord',
  source: { path: 'src/models.ts', symbol: 'ContainerMappingRecord' }
})

export const mappingDetails = Mapping.view({
  id: 'mapping.details',
  title: 'Container mapping',
  question: 'Which original index and container does this mapping preserve?',
  priority: 10,
  component: 'shape',
  render(mapping, view) {
    return view.details()
      .field('original index', mapping.firstSeenIndex)
      .field('container ID', mapping.cookieStoreId)
      .field('backup name', mapping.backupName)
      .done()
  }
})
```

A view definition's `render` here computes a schema value in the application runtime. It does not touch the browser DOM. The builder owns provenance and bounds; the function owns the domain question and field selection. A third-party class uses the same external token API, so adoption does not require monkey-patching it.

Use an explicit `paneweft.views.ts` manifest to import/export view modules and example definitions. Side-effect registration is acceptable within that manifest, but arbitrary filesystem-wide imports are not discovery. The manifest declares source locations, supported runners, and module exports; a compiled catalogue resolves them. A view's symbol method can select instance-specific content, while its static descriptor makes it discoverable before an instance exists.

`@paneweft/sdk` is a dev dependency in ContainMarks. The production esbuild entry points never import the manifest or sibling instrumentation files. An application that deliberately instruments development runs uses a separate development entry or a build-time constant with verified dead-code removal. Installing a dev dependency alone does not strip an imported library from a bundle. Inspect the actual production bundle dependency graph in CI; do not claim removal from an environment variable's name.

Later Python support should offer a decorator plus a pytest helper, Kotlin an interface or extension adapter plus JUnit integration, and Nix pure functions exporting views of selected evaluated values. They share the wire and capture contracts. Nix observations must identify which host and evaluation ran and follow the host-only evaluation rule; a syntax parse cannot stand in for an evaluated option value.

## 3. Examples belong in the test workflow

An example is a named factory with assertions and an inspectable result. Its definition is permanent source; each execution is a separate run. A Rust attribute preserves the original callable function and generates a normal libtest test that calls it, captures its result while borrowed, publishes views, and preserves assertion failures. It also registers the definition for discovery. A function returning `Result<T, E>` publishes `T` on success and a structured diagnostic on error.

The first Rust adapter uses ordinary stable tests. It does not scrape arbitrary return values from libtest, require nightly `custom_test_frameworks`, or replace every test target with `harness = false`. The latter is a supported future escape hatch for a repository that wants a dedicated runner. Generated wrappers capture panics in unwind builds, write the failure artifact, then resume the panic so cargo still fails. Process aborts and kills are handled as missing completion records by the parent collector.

For vigil, these proposed functions live in a feature-gated test module in `watch.rs`, where the existing `testing::at` and `change_request` helpers are accessible. They call the actual `WatchFile::finish` method. Fixed dates and paths avoid a clock, filesystem watcher, or judge dependency.

```rust
#[paneweft::example(id = "watch.pending", claims = ["VW1"])]
fn pending_watch() -> WatchFile {
    let spec = WatchSpec::parse(crate::testing::change_request(
        "example", std::path::Path::new("/tmp/paneweft-example.log"), 20,
    )).unwrap();
    let watch = WatchFile::new(spec, crate::testing::at("2026-11-11T12:00:00Z"));
    paneweft::check_eq!("VW1", watch.status, WatchStatus::Pending);
    watch
}

#[paneweft::example(id = "watch.cancelled", claims = ["VW2", "VW2-empty"])]
fn cancelled_watch() -> WatchFile {
    let mut watch = pending_watch();
    watch.finish(Terminal {
        status: TerminalStatus::Cancelled,
        finished_at: crate::testing::at("2026-11-11T12:00:01Z"),
        events: Vec::new(),
        digest: "no changes".into(),
    }).unwrap();
    paneweft::check_eq!("VW2", watch.status, WatchStatus::Cancelled);
    paneweft::check!("VW2-empty", watch.events.is_empty());
    watch
}
```

The second example composes the first through its normal function call, as `<gtExample>` factories do. Macro-generated guards record nested invocation IDs and parent edges, even for direct calls. Each call constructs a fresh value; v1 does not memoize mutable fixtures. The pending value is captured before it is changed by its caller. A dependency failure gives the child its actual failure and the parent a blocked-by-dependency outcome. Recursive example calls stop with the invocation path and a bounded recursion diagnostic. Async Rust functions are deferred in the first week; their later adapter must use the repository's runtime and retain test context across awaits.

Vitest and Jest helpers wrap the runner's ordinary test API. They cannot retrieve local objects merely by installing a reporter. The helper captures an explicitly returned or published value inside the worker, and the reporter finalizes its outcome after hooks and teardown have finished. This proposed ContainMarks example uses a literal URL supported by existing tests.

```ts
import { expect } from 'vitest'
import { example, exampleTest } from '@paneweft/vitest'
import { parseContainerMappingUrl } from '../src/mappings/containerMappings'
import { Mapping } from '../src/mappings/containerMappings.paneweft'

export const workMapping = example({
  id: 'mapping.work',
  type: Mapping,
  claims: ['CM1'],
  run(cx) {
    const mapping = parseContainerMappingUrl('about:4:firefox-container-3:Work')
    cx.check('CM1', () => {
      expect(mapping).toEqual({
        firstSeenIndex: 4,
        cookieStoreId: 'firefox-container-3',
        backupName: 'Work'
      })
    })
    return mapping!
  }
})

exampleTest(workMapping)

export const renamedMapping = example({
  id: 'mapping.renamed',
  type: Mapping,
  claims: ['CM2'],
  async run(cx) {
    const mapping = await cx.use(workMapping)
    const renamed = { ...mapping, backupName: 'Research' }
    cx.check('CM2', () => {
      expect(renamed.cookieStoreId).toBe('firefox-container-3')
    })
    return renamed
  }
})

exampleTest(renamedMapping)
```

Jest exposes the same `example` and `exampleTest` API from `@paneweft/jest`, with its own context and reporter adapter. The shared factory is runner-neutral; assertions remain native to the chosen runner. The first cycle proves Vitest on ContainMarks and a minimal Jest compatibility fixture in paneweft. Support a pinned Vitest 3 adapter for ContainMarks and a separately tested Vitest 5 adapter for paneweft itself; do not assume the newest reporter hook signatures work in both.

Ordinary `cargo test --features paneweft` and configured Vitest/Jest suites write bounded per-worker artifacts when collection is enabled. `paneweft collect` supplies the run identity and staging directory, invokes the runner, reconciles reports, and imports a session. A suite run without a collector still executes assertions; it neither starts a server nor creates a global session. An explicit artifact-output option lets CI collect later.

The run records runner identity/version, type and view IDs, source/lock/config hashes, test selector, attempt, timestamps, assertions, result object references, diagnostics, and parent example invocations. A successful assertion-bearing execution and its captured values have `observed` provenance tied to that run. Rust `check_eq!` and `check!` invoke native assertions and record their outcome under a claim ID. TS `cx.check` invokes the supplied native assertion callback and records whether it completed; async checks must be awaited. They work as assertions even without a collector. This avoids pretending that a reporter can count arbitrary native assertions or see which branches executed. Other native assertions still fail the test normally. The reporter records final test-and-hook completion separately. Without an executed recorded domain check, an invocation is exploratory and cannot count as a verified example, even when its test process exits zero.

Keep execution origin separate from provenance. The host stamps collections it actually launched as `host_collected`; external runner imports and agent submissions remain `external_recorded` or `agent_submitted`. This stamp is session metadata outside the submitted payload. Existing v0 `observed` declarations retain their meaning as reported observations, without gaining host-execution verification through import. The SDK can automate evidence bookkeeping, but trusted repository code can still make a false assertion about its own behavior.

Keep native outcome and capture outcome separate. A test may pass while its view fails validation; that yields a passed test plus a failed capture and a failing collection command. A test body may return a useful object before teardown fails; the reporter must mark the run failed and retain that object as diagnostic evidence. Retries have distinct attempt IDs and retain prior failures. Skipped, filtered, cancelled, failed, error, and passed are distinct outcomes. A suite with zero selected examples reports zero coverage, never a successful demonstration.

## 4. Publishing and navigating objects

`inspect(&watch)` in Rust and `inspect(mapping, Mapping)` in TypeScript publish at an execution point. The Rust call borrows without moving the value. The TypeScript call uses a token for records or the symbol protocol for a class. In a capture, it returns an `ObjectRef` usable by rows and relations. With no active collector, a compiled development hook returns an explicit inactive result and does no traversal. Production builds omit the call and its imports through the feature/module gates.

Publication first assigns an object ID and enters it into the capture's visited map, then computes bounded views and follows declared child references. A cycle can therefore refer back to a registered object without recursively expanding it. Multiple rows can target the same object, while row IDs remain distinct occurrences. Tree renderers still reject cycles in their occurrence hierarchy; object references can contain cycles.

IDs are stable within an observation graph and across all views of that observation. TypeScript uses object-reference identity through a WeakMap. Rust may use typed addresses only while a borrowed traversal is active; it cannot retain an address as identity across calls, moves, frees, or zero-sized values. Across separate `inspect` calls, sharing requires an explicit capture-local identity token or declared domain key. Unkeyed calls create new observations. Wire IDs contain opaque capture-scoped identifiers, never memory addresses.

A domain key, such as a watch ID, provides an optional logical-identity link across captures. It does not replace the observation ID or content hash. Publishing a mutated watch produces a new observation. Conflicting versions with the same domain key stay visible, and redelivered vigil events are not collapsed merely because their `event_id` strings match. Cross-run comparison uses domain keys when declared, and labels other matching as uncertain.

V1 captures all requested child/view computations before the owning function returns. Rust child closures borrow only for that operation. TypeScript snapshotting is synchronous over selected fields, avoiding a retained reference that later changes before encoding. User code must take a consistent domain snapshot under its own lock when other threads mutate state. If a view performs separate reads without such a guarantee, record its consistency as best-effort. No generic SDK can promise an atomic snapshot of an arbitrary concurrent object graph.

Lazy children in v1 mean lazy delivery of already captured data. The collector stores bounded child pages as content-addressed artifacts; the viewer and agent fetch pages on demand. A capture-time child provider can avoid computing unselected branches, but no provider closure survives process exit. An uncaptured branch is `not_captured` with a reason and a collection selector. Expanding it requires an explicit recollection into a new snapshot. A page cannot call a dead process or silently change its snapshot. This makes the distinction between `stored_page` and `not_captured` essential.

Default hard limits are depth 4, 1,000 objects, 4,000 references, 2 MiB of encoded records per root, 16 KiB per string, and 100 rows per stored page. Bound the whole collection too, initially 32 MiB and 100 published roots. Apply limits while building, not after constructing an unbounded intermediate value. Record omitted counts when known; otherwise say the count is unknown. Redacted, null, absent, unsupported, truncated, and not-captured values are distinct tagged states. Each view selects fields; raw reflective dumping is opt-in, and arbitrary JavaScript getters are never evaluated by default.

Builders check a cooperative computation budget, initially 100 ms per view. This is a diagnostic budget, not preemption of arbitrary Rust or JavaScript code. The collection process has a separate wall-clock deadline and a cancellable process group. Locks and side effects remain application concerns. Document that view functions should compute from their receiver and supplied context, with no network access, filesystem mutation, or hidden retries.

An object record maps to an entity kind and `EntityRef` plus graph metadata. A row's target resolves to an exact captured object in the same snapshot. Existing `open_entity` and `navigate` then open its stored views in a neighboring pane. Backlinks show aliases and cycles without duplicating the graph. A missing target yields a bounded missing-capture explanation. Navigation cannot evaluate code, perform domain mutations, or resolve an object by looking it up in today's mutable application state.

## 5. Repo-owned custom renderers

GT's `explicit` builder motivates an escape hatch for a domain representation that a table or graph cannot express well. Add `component: "custom"` in the versioned v1 envelope, with a payload naming a renderer ID, API version, payload schema digest, bundled asset digest, object references, and a required ordinary component fallback. Validate that fallback using its existing component schema and the payload using the locally registered renderer schema. Permit bounded local schema references only, with no network schema loading. Renderer source and its schema belong in the repository. A reviewed example and tests travel with them. A renderer can use SVG, canvas, or its own UI library inside the frame; the host should not prescribe a universal chart grammar.

There are three trust boundaries. Agent-submitted JSON is untrusted data and cannot grant execution rights. Repository renderer code is executable code allowed by the session owner's local policy. The host itself has the viewer token, session access, and repository roots. A renderer never receives those host capabilities. A collected reference to a renderer does not authorize it, even if an agent labels its payload `observed`.

Renderer installation is a local CLI action that resolves files under an already registered repository root and records an allowlisted content digest. It does not run npm lifecycle scripts. `paneweft renderers trust --repo containmarks --id mapping-card --digest SHA256` is the proposed explicit trust operation. Source edits invalidate the digest; refresh trust as part of the owner's existing executable-code policy. An agent can author the renderer and prepare its artifact under an authorized coding task. Importing a foreign session or invoking `render` must never trust its code automatically. The trust store lives outside the submitted bundle and is not writable through MCP.

Serve the bundled renderer in an iframe with `sandbox="allow-scripts"`, omitting `allow-same-origin`, forms, popups, downloads, and top-navigation permissions. Set `referrerpolicy="no-referrer"`. Use a self-contained document with a restrictive Content Security Policy: `default-src 'none'`, hash-authorized script, local inline styling, `connect-src 'none'`, `form-action 'none'`, and `base-uri 'none'`. No remote modules, fonts, or image URLs are needed for the proof. Escape embedded data independently of the renderer's source. These restrictions block the declared resource/fetch paths and top-level navigation; sandboxing does not prevent a frame from navigating itself. Treat self-navigation as a trusted-code risk, revoke the port on an unexpected frame load, and do not promise that CSP provides complete network isolation. [Iframe sandbox documentation, undated, accessed 2026-11-11](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe).

The versioned postMessage contract starts with a per-frame random capability nonce and a transferred MessagePort. The parent checks the iframe window identity and handshake state, because a sandboxed frame has an opaque origin and origin text alone cannot identify it. Bootstrap may require `targetOrigin: "*"` for that opaque frame; use it only for the specific frame window, then communicate over the private port. Every message carries protocol version, frame/view/snapshot identity, request ID, and a monotonic sequence number. Close the port when the frame is replaced. [postMessage documentation, undated, accessed 2026-11-11](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage).

The host sends `init` with immutable payload metadata, theme, locale and accessible label, followed by bounded payload and permitted-ID pages. It may send `selection_changed`, a requested stored page, and `dispose`. The renderer may send `ready`, `resize`, `select_item`, `open_object`, `request_page`, and `render_error`. The host validates message shape and checks referenced IDs against this view before acting. `open_object` uses the existing pane navigation operation. There is no arbitrary URL, fetch proxy, file read, command, eval, or MCP forwarding message. Cap each message at 64 KiB, rate-limit requests, bound frame size, and fail visibly on protocol errors.

The standard fallback is generated by the SDK from the same capture and is always available to agents. The plugin's own text cannot overwrite provenance or completeness. The host shows its errors and offers the fallback when assets are absent, denied, incompatible, or fail to load. Preserve keyboard access and the question in both presentations. View tests verify the fallback's domain facts; renderer tests verify selection, labels, and navigation against those captured IDs.

An iframe is not a complete CPU or memory isolation boundary; a renderer can still freeze its browsing context, and browser process placement is implementation-dependent. The default therefore accepts renderer code only from an explicitly trusted repo digest. This design does not claim safe execution of arbitrary agent-supplied JavaScript. Test the enumerated sandbox restrictions in a real browser, including blocked fetch, sockets, image loads, parent access and top-level navigation, instead of treating jsdom's behavior as proof.

## 6. Agent integration is the priority

The agent's normal task is to leave a reusable way to answer a question in the repository. A permanent view consists of its declaration, source-owned computation, example, assertions about the view output, and discovery registration. The host supplies collection, storage, rendering, and bounded queries. Requiring agents to reassemble runtime values into JSON on each investigation would lose the owner's intended benefit.

### The working loop

Start with a question and a type. For vigil: "Which events remain after this watch finishes, including redelivery?" Read its existing views and examples before inventing another representation. Discovery must show which type IDs exist, where they are defined, which views apply, and which examples return them. It also says what was compiled, which target/configuration supplied the catalogue, and whether the catalogue is fresh. A missing result in an outdated catalogue must never look like proof that no view exists.

Choose to reuse, extend, or create a view. The agent scaffolds from a typed template and edits the repository with its ordinary code tools. The scaffold supplies the type import, function signature, stable IDs, a source pointer, registration changes, and a failing output test for the stated question. It must not guess field names or emit invented facts. For a type not yet catalogued, accept an explicit source path and symbol as a candidate, then require the compiler to validate it. An unknown or ambiguous symbol returns candidate locations, not an arbitrary match.

Keep the first implementation narrow. A mapping details view reads the record's fields; it does not reread Firefox storage to reconstruct the record. A watch events view traverses the captured watch's actual event list; it does not shell out to vigil and combine loosely related log files. If the necessary domain operation has no inspectable result, add an explicit observation point or an adapter to the operation's return value. That source change is part of making the codebase instrument itself.

Write the expected behavior before implementing the projection. Test an empty collection, a normal instance, duplicate domain IDs, a cycle or shared child where applicable, and the truncation boundary relevant to this view. Tests should call the exported view function through an in-memory capture context and examine normalized component data and object targets. They should not need a running viewer. The scaffold initially returns unsupported with a TODO reason; a test expecting the specified fields fails on an assertion. This fits the build-loop red gate without an import error or a fake passing example.

Collect the focused examples through the registered cargo or Vitest adapter. The command compiles/typechecks instrumentation, exports the actual catalogue, runs the selected tests, captures values inside those executions, validates artifacts, and commits an immutable session snapshot. A compile error points to the field or match arm in the view; a duplicate registration names both declarations; a missing type registration identifies the omitted manifest import or target. Collection must preserve failed test artifacts and must not call a failure successful merely because a valid bundle was imported.

Read the result in both forms. `view_result` returns the stored view's bounded text, completeness, provenance, source anchors, object and run IDs, and browser link if a viewer is running. A person can open that URL; an agent can inspect the same snapshot through typed operations. For visual judgments, use the available browser automation to inspect the real rendered result. Text parity alone proves facts and navigation targets, not legibility or layout. If no browser can be exercised, record that limitation and the exact visual check still needed.

Iterate on a named failure. `explain_failure` classifies compiler, typecheck, assertion, view exception, output-schema, reference, limit, registration, renderer, and runner failures. It includes the offending view/example ID, source span, JSON pointer when applicable, violated invariant, expected/actual value when available, and a concrete next action. It offers evidence and a fix location, not model-generated diagnosis presented as observed fact. The agent changes source, reruns the focused suite, and reads the new snapshot. Old snapshots remain available to explain the difference.

Finish by retaining declarations and tests in the repository, documenting the question in the catalogue, and attaching the exact run/snapshot IDs to the implementation report. Check production stripping. Run the repository's required checks, including the full example inventory check. Passing a focused selection is not proof that all views remain registered. The next agent should be able to start with discovery and rerun a named example without reading a prior conversation.

### MCP and CLI contract

Keep the current MCP tool set small by adding task-sized operations, not one MCP tool per view. All tools use repository IDs, stable type/view/example IDs, and constrained selectors. The CLI uses kebab-case command words and maps to the same request handlers and errors. Each command accepts `--args-file`, `--format json|text`, and the existing byte budget where it returns a reply. Examples below are proposed commands, not existing v0 syntax.

| MCP tool | CLI form | Input and useful output |
|---|---|---|
| `list_types` | `paneweft types --repo ID` | Optional language/query; returns type IDs, source symbols, known views/examples, catalogue digest, coverage and freshness. |
| `list_views_for_type` | `paneweft views --repo ID --type TYPE` | Type ID plus optional target; returns definitions, questions, source locations, output components, renderer requirements, example IDs, last capture and stale reasons. It reads the catalogue and never executes code. |
| `list_examples` | `paneweft examples --repo ID --type TYPE` | Optional type/view/tag filter; returns definition IDs, return types, claim IDs, composition links, supported runner, selector and last outcomes. |
| `scaffold_view` | `paneweft scaffold view --repo ID --type TYPE --question TEXT` | Component/template and optional source candidate; returns a bounded source patch, output-test template, required imports/manifest changes and collection recipe. It writes nothing and never overwrites a file. |
| `scaffold_example` | `paneweft scaffold example --repo ID --type TYPE` | Existing factory or empty template; returns a test/example patch with an explicit unimplemented assertion. |
| `collect` | `paneweft collect --repo ID --adapter ID --example EXAMPLE` | Registered adapter, exact example IDs or suite selection, optional view filter and limits; starts a job and returns its ID, selector, configuration and progress link. No raw argv or shell text. |
| `collection_status` | `paneweft collection status JOB` | Job ID plus bounded log cursor or wait duration up to 30 seconds; returns progress, compile/test/capture counts, diagnostic IDs and terminal snapshot IDs. |
| `cancel_collection` | `paneweft collection cancel JOB` | Job ID; cancels its process group and records cancellation, preserving valid diagnostic artifacts. |
| `view_result` | `paneweft result --run RUN --view VIEW` | Exact run or job plus view/observation selector; returns a bounded stored result, fallback text for custom renderers, object refs and viewer URL when available. Ambiguity lists candidates. |
| `explain_failure` | `paneweft failure DIAGNOSTIC` | Stored diagnostic ID and optional evidence page; returns cause category, source/pointer, captured stderr slice, repair hint and repeatable selector. Never executes a repair. |

Existing `open_entity`, `navigate`, `inspect_view`, `search`, and notebook operations serve the collected objects as they do v0 entities. `view_result` selects the correct stored result and delegates to those readers. Optional image capture is a separate bounded artifact operation for browser-equipped clients, not a mandatory base64 image in every MCP reply. The collection job is durable across MCP client disconnects. A second request with the same request ID returns the existing job; a deliberate rerun uses a new request ID.

Use default replies of 8,192 bytes and the current supported range of 2,048 to 32,768 bytes. Include the same header and cursor semantics as v0. Tool descriptions say when to call the tool, whether it executes code, and the next useful operation. MCP initialization instructions teach the SDK-first loop before the JSON fallback. Read tools carry read-only annotations; collection is explicitly a code-executing operation. Annotations do not grant access. Keep one bounded text content block as v0 currently does; changing to structuredContent can be a separate compatibility decision.

Scaffolding is read-only generation. If a patch exceeds the requested reply budget, return a template ID and separate file patches with cursors, never a clipped patch that appears complete. Applying it happens through the coding agent's existing edit capability and normal repository authorization. No new server-side general file-write API is needed.

### Execution authorization without slowing the loop

V0 deliberately forbids process execution over MCP. V1 changes that rule only for collection. A session owner configures a registered repository and an allowed adapter outside submitted documents. The adapter record pins executable identity, workspace root, supported runner versions, argv grammar, feature set, time/output limits, and any queue wrapper. The checked-in manifest supplies declarations and test selectors; it cannot replace the executable, add shell fragments, change the root, or install a runner through a view payload.

A coding session already authorized to execute that repository's tests can be configured once to use its adapter. It should not require a new approval for every example or ordinary view edit. New repositories, renderer execution, and changing an adapter's executable capability follow the owner's existing trust policy. `collect` rejects an unregistered adapter with a specific setup command. Registering an adapter remains CLI-only. Discovery can read stale metadata without enabling execution.

Trusted tests are still repository code and can perform whatever operations the coding environment allows. The adapter is not a sandbox for a hostile checkout. The policy prevents an imported view document from becoming a command channel; it does not make running untrusted tests safe. Network, credentials, and resource limits remain the environment's responsibility. On sonic and nixed, configure collection through the existing qex queue and its resource policy. CLI waiting and MCP status should follow the queue's completion mechanism rather than start duplicate work or hide logs.

Compiler and runner output streams continuously to a bounded log artifact. MCP progress reports the current target/test and counts, while status requests retrieve slices. Cancellation reaches child processes, not only the cargo/npm parent. Do not hold the session write lock while tests run; validate the private staging directory first, then acquire the lock for the atomic import. Concurrent jobs get separate run and staging IDs.

### Keeping views current

Compilation catches a renamed Rust field or a TypeScript property whose typed access changed. It does not prove the view still asks the right question, and it cannot detect a forgotten manifest import by itself. Tie three checks to the normal test workflow.

First, compile/typecheck all registered instrumentation with its declared feature set. TS collection explicitly runs `tsc --noEmit` against the instrumentation configuration before Vitest; Vitest's transformation alone does not provide that check. Rust release and collection features are tested separately. Exhaustive matches in view code should omit catch-all arms when every variant matters, so a new variant forces review.

Second, compare the current compiled catalogue with a small checked-in inventory of stable view/example IDs and owning modules. Removed IDs, a missing module, a duplicate, or an example that no longer returns its declared type fails the inventory check. Intentional removal updates that inventory in the same reviewed change. It stores definitions, not generated runtime facts. Report `declared`, `linked`, `exercised`, and `passing` counts separately; a discoverable view with no exercised example is a named gap.

Third, bind captured results to exact inputs. The collection fingerprint includes relevant source bytes, view/example source, manifests, lockfiles, runner/SDK versions, compiler options, Cargo features and target, and declared external fixture inputs. Capture hashes before and after execution; a changing checkout makes the run mixed-input and unfit to mark fresh. Start with conservative package-wide invalidation where exact dependency tracking is unavailable. A new commit is not the only stale trigger; dirty file edits also matter.

Old results remain inspectable with stale reasons and the exact recollection command. Listing can report freshness `unverified` when roots or inputs are unavailable. A successful recompile alone never relabels an old runtime capture as fresh. An observation of an external system is historical even if its source files are unchanged; encode its capture time and declared external inputs. V1 makes no automatic claim that today's external system still has that state.

### Proving that a view answers its question

Tests over view output belong beside the view under the repository's test conventions. For `mapping.details`, build the view from a literal record and assert the exact field paths, values, order, observed evidence linkage, and absence of undeclared sensitive fields. For `watch.events`, publish two events with the same domain ID and distinct contents, then assert two rows and distinct targets. Open one target through the session reader to prove the link reaches the corresponding event, not a same-looking row in another capture.

Use expected values derived from the question and a small reviewed fixture. Do not derive expected output by calling the view builder itself, compare a value to itself, or regenerate a golden until it passes. Schema validation proves shape; a passing domain test proves its own behavior; independent projection assertions prove that the representation retained the intended facts. These are different checks.

Keep reviewed structure goldens for a few representative browser and text renderings. Verify selected fields, target identity, empty/partial/error states, and keyboard navigation. Normalize only capture timestamps and opaque IDs in goldens, preserving their relationships. Custom renderer tests assert labels and the actual `open_object` message for an item. The host checks text and browser selection against one literal captured graph.

During review, perform a few focused mutations: drop an event, merge duplicate keys, swap mapping fields, or remove the manifest import. The relevant test must fail. Record the mutation and failing test in the verification report, then revert the mutation. These checks fit the owner's [test-quality](../skills/test-quality/SKILL.md) and [technical-excellence](../skills/technical-excellence/SKILL.md) requirements for independent expectations and cited claims.

### The agent skill to ship

Ship `skills/paneweft-views/SKILL.md` in the paneweft repo, with Rust/TS recipes and compact troubleshooting references. Install it through the owner's normal agent-integration mechanism when that integration work is authorized. The file below is proposed skill content, included here rather than written as a second artifact.

```markdown
---
name: paneweft-views
description: Author and maintain permanent typed views and executable examples in a repository.
---

Use this when a recurring development question needs an inspectable answer.
Read the repo instructions and paneweft manifest. State the question and type.
1. Call list_types, list_views_for_type, and list_examples. Check freshness,
   target, features, and coverage. Reuse a useful view or example first.
2. For a new view, call scaffold_view. Apply its patch using your normal code
   editor. Put typed computation beside the owning code or in a sibling dev
   module. Add registration and a focused example. Do not guess field names.
3. Write an output test with a WHY and a CLAIM id. Use independently expected
   values. Run it red before implementing the projection. Follow build-loop
   gates when that workflow is active.
4. Implement over real values. Select fields deliberately. Preserve object
   targets, partial states, and evidence. Keep hooks out of release builds.
5. Call collect with a registered adapter and exact example selector. Follow
   its job until terminal. Use explain_failure for named diagnostics.
6. Call view_result. Inspect text and, when available, the browser rendering.
   Test facts, navigation, empty/error states, and relevant limits. A browser
   link alone is not evidence that the rendering was checked.
7. Update the view inventory and docs, run the repo's required checks, and
   retain declarations/tests. Report commands, run/snapshot IDs, stale gaps,
   renderer trust needs, and any visual check that could not run.

Use the JSON fallback for an unsupported language, a read-only codebase, an
external historical artifact, a cross-repo narrative, or a one-off question
that does not justify permanent instrumentation. Name that reason and use
list_components -> describe_component -> validate -> render. Preserve the
actual provenance. Never replace a broken existing SDK view with hand-written
observed results. Repair the view or report its failure.
```

When the owner uses [build-loop](../skills/build-loop/SKILL.md), include the question, type IDs, IV claims, and independent output tests in its spec/red review. Implement in bounded phases, verify between them, then include source diff, collection evidence, text/browser results, stale checks, and stripping evidence in code review. Apply its normal tiered review and ledger rules. A beautiful view is not a reason to waive the assertion-based red gate. This design task does not start that implementation workflow or its agents.

### Exactly when JSON is the fallback

Use v0's existing JSON submission path when the source language has no SDK yet, the repo is read-only or cannot accept a dependency, the question concerns captured external data that cannot be republished by its original process, or the artifact is a cross-repository notebook combining already recorded evidence. A short-lived one-off analysis is also reasonable when no recurring type-level question exists. Record that choice and its provenance.

If an SDK and a modifiable codebase exist and the question will recur, prefer permanent instrumentation even when submitting JSON would be faster once. Repeated fallback for the same type is a signal to add an adapter. During a broken build, an agent can submit a read/parsed diagnostic view of the compile error, but cannot fabricate an observed example result or replace the failing view's last snapshot. Fallback payloads cannot install renderers or adapters, invoke collection, or grant themselves source-root access.

## 7. The human developer path

A person follows the same sequence with the CLI: list a type's views, add a short typed function, add an example and output assertion, run the focused collection, and open the result in the browser. IDE integration is low priority. A later editor adapter can translate a symbol selection into `views --type` and open the existing viewer, without owning a second registry or test workflow.

Documentation should start with a runnable ten-minute example in each language, using the exact SDK version in the monorepo. Explain the difference between a type, a value observation, a view definition, an example definition, and an example invocation. Show both a plain record and a third-party-type adapter. Keep method completions useful, infer column types where possible, and return errors naming the author-facing method and source location before exposing a wire pointer.

Manual authoring must remain comfortable. No agent service is required to use the SDK, and a repository does not need decorators, generated domain classes, a new test framework, or a custom renderer for its first useful view. Put the explicit advanced controls, including provenance overrides, graph identity, and renderer schemas, behind ordinary helper defaults. Document how to remove instrumentation cleanly and how to keep release builds free of it.

## 8. Changes to the v0 host

The inspected paneweft root is `/home/mini/Documents/repos/paneweft`, HEAD `021216706ee56f93b885e2eeca0256cef86e8e3e`. There is no root `schemas/` directory in this checkout; canonical schemas are under `src/schemas/`. The working tree had existing changes in `src/viewer/app.ts` and `src/viewer/server.ts`; this task did not alter them. Host details below rely on the schema, core, MCP, CLI, and viewer-source files read during this task, not on a claim that the checkout was clean.

Add explicit versioned contracts instead of quietly adding unknown members to strict `/1` envelopes. Preserve reading/importing all existing v0 fixtures. A proposed `paneweft.capture/1` bundle holds the catalogue reference, collection metadata, object graph, view envelopes, example invocations, diagnostics, and stored child-page references. Ordinary component data stays on its current schema where possible. Use `paneweft.view/2`, `definition/2`, and `run/2` only where their structures need the additions, with explicit dispatch and compatibility adapters. Never rewrite stored `/1` objects in place.

The object graph needs capture-scoped identity, stable type ID, optional logical key, object-to-entity mapping, alias/cycle edges, view references, redaction/truncation tags, and stored-page versus not-captured states. Example runs need definition/invocation/parent IDs, runner and attempt, selected/exercised coverage, native-test and capture outcomes, result observations, claims/assertions, timestamps, exact input fingerprint, and diagnostics. Custom views need registered renderer/schema/asset digests and an ordinary fallback. A checked catalogue records source locations and linked scope separately from runtime observations.

| Existing part | Required change |
|---|---|
| `src/schemas`, generated `src/core/wire.ts`, validators | Add the contracts above and generated SDK wire types. Validate cross-object references, exact snapshot binding, IDs, limits, and custom payloads. Keep schemas authoritative across languages. |
| `src/core/session.ts` | Atomically import a collection and its graph/pages/runs. Extend manifest indexes for captures, types, examples, and catalogue digests. Keep content hashes and immutable storage. Read legacy sessions without migration writes. |
| `src/core/example-runs.ts` | Preserve the current single effective-read path for recorded runs, including notice of invalid recordings. Extend reconciliation to suite/attempt records without turning old envelopes mutable. |
| `src/core/runner.ts` | Introduce a collection lifecycle using private per-job staging, streaming bounded logs, cancellation, process-group timeouts, and artifact import even when tests exit nonzero. Its current runner discards stdout/stderr and rejects nonzero exits before reading output; reusing it unchanged would hide failing examples. |
| New cargo/Vitest/Jest adapters | Capture in test workers, reconcile completion, export catalogues, preserve assertions and native exit status, and normalize diagnostics. Never parse arbitrary application stdout as the wire protocol. |
| `src/core/registry.ts` | Retain deterministic priority and exact-kind selection. Add type/capture metadata and distinguish a declared view with no captured instance from an available one. Definitions alone cannot make uncaptured data usable. |
| `src/core/operations.ts`, CLI, MCP | Add discovery, scaffold, collection jobs, results and diagnostics through shared handlers. Change MCP's current no-code-execution instructions and tests to the narrow registered-collection rule. Keep root/adapter/trust setup CLI-only. |
| Viewer source/HTTP API, pager and components | Add object references, stored child-page loading, per-example failure panes, custom-frame host, and visible fallback/error/stale states. Validate new HTTP messages through the same contracts. |
| Search and summaries | Index type/view/example definitions and observations; bound text over the same captured graph used by the browser. Return plugin fallback facts without running plugin code in the agent path. |

Keep the immutable session store, source confinement, provenance vocabulary, explicit completeness, snapshot-bound navigation, content-bound cursors, byte budgets, notebook revisions, loopback authenticated viewer, current built-in components, CLI/MCP parity, and JSON fallback. Keep the host TypeScript implementation and the browser-first delivery. No new desktop shell, language server, or distributed object server is required.

Collection imports occur after runner completion and artifact validation. A nonzero test exit still produces a recorded failed collection with useful objects; the command returns failure. Invalid artifacts remain quarantined with diagnostics and cannot become a fresh successful snapshot. On partial runner crashes, import only complete validated records as an explicitly incomplete collection, with missing worker/test counts. No stale staging file from another run can satisfy a new run ID.

## 9. First build-loop cycle, about one week

One week is a planning constraint, not a measured delivery promise. Ship one complete path in each language, including agent tools and renderer extensibility. The demonstrations are vigil and ContainMarks. Residual's `EntityDetail` and selection model are good follow-on TS examples, but its current web tests import `bun:test`; quietly treating that package as Vitest would create unrelated migration work.

Day 1 settles the capture/catalogue/object/run contracts, the lexicon, and IV1–IV22 below. Commit independent literal fixtures and assertion-failing red tests for this scope. Include spec/red review under build-loop before green. Check existing v0 guards and record any pre-existing failures.

Days 2 and 3 build the two SDKs and worker capture. Rust delivers the borrowed trait, concrete-type `views`/`view` attributes, simple opt-in `Inspect` derive, `example` macro with stable libtest wrappers, linkme catalogue and explicit-slice fallback, details/list builders, object references, limits and feature gates. TS delivers typed record tokens, the symbol interface, details/list builders, the explicit manifest, runner-neutral examples, in-worker capture, Vitest integration, and a small Jest fixture. General decorators, generic Rust auto-registration, and async Rust examples are deferred. Emit the existing remaining component payloads through typed low-level builders; ergonomic helpers for every component need not all ship this week.

Day 4 joins cargo and Vitest collection to the host. Add durable jobs, actionable compile/test/schema diagnostics, failed-run import, graph storage, lazy stored pages, freshness/inventory checks, and a result read path. Provide commands and MCP tools for type/view/example discovery, read-only scaffolding, collection/status/cancel, results and failure explanation. Deliver the agent skill and execute its exact command recipe against a fresh local session. The acceptance test follows the agent path; manually assembling a final bundle does not satisfy it.

Day 5 implements one repo-owned custom renderer proof. Use a ContainMarks mapping card with a small diagram connecting original index, current container ID, and backup name. Selecting its mapping opens the captured record in another pane. The renderer's fallback is the typed details view from the same object. Demonstrate denied/untrusted state, explicit local trust, successful sandbox rendering, keyboard selection, and wrong-ID/protocol rejection. A sandboxed static picture that cannot navigate does not complete the proof.

The remaining days exercise both codebases and finish review. Vigil gets the status and events views, pending/cancelled examples, a fixture showing retained/redelivered events, output tests and a registered cargo recipe. ContainMarks gets the mapping details view, parsed/renamed examples, Vitest recipe, renderer and output tests. Run their real tests plus the host checks, inspect the browser/text results, and verify release stripping. Deliver source changes, reviewed fixture outputs, exact run/snapshot IDs, documented commands, and a short report of failure repairs and remaining limits. Example adapter source inspection alone is not an observed demonstration.

If time slips, reduce the number of domain views, leave Jest at the compatibility fixture, or defer decorative renderer features and higher-level component helpers. Preserve both Rust and TS working examples, compile/test integration, agent discovery/scaffolding/repair, graph navigation, failure evidence, and the one sandbox renderer proof. A release with only SDK syntax and hand-produced JSON misses the agreed scope.

Suggested demonstration commands, after the future adapters are registered locally:

```sh
paneweft --session .paneweft-session views --repo vigil --type vigil::watch::WatchFile
paneweft --session .paneweft-session collect --repo vigil --adapter cargo --example watch.cancelled
paneweft --session .paneweft-session views --repo containmarks --type containmarks::ContainerMappingRecord
paneweft --session .paneweft-session collect --repo containmarks --adapter vitest --example mapping.work
paneweft --session .paneweft-session serve
```

The status/result commands consume the job/run IDs returned by collection. Internally, the cargo recipe runs stable `cargo test --features paneweft` on the selected target with generated-wrapper filters; the TS recipe runs typecheck and the pinned local Vitest executable with its adapter configuration. Test adapters verify selectors as data and never evaluate a user-supplied shell command.

## 10. Red-test claims and decisions

Each red test needs a WHY, the claim ID, an independent expected result, and an assertion failure representing a missing behavior. Compile-fail tests below are deliberate compiler contract tests with fixture diagnostics; they do not replace the assertion-based red gate for implementation behavior. Literal cross-language fixtures must be reviewed independently of either encoder.

| Claim | Required evidence |
|---|---|
| IV1 | A borrowed vigil value produces a validated details/list view with exact independently expected cells and run evidence, without serializing the whole domain struct. |
| IV2 | A TS plain record uses its explicit type token; a class uses the symbol contract. An erased interface name alone never selects a runtime adapter. |
| IV3 | Registration in separately linked Rust modules and explicitly imported TS modules yields the same sorted catalogue regardless of registration order. Duplicate IDs report both sources. Missing links/imports fail the inventory check. |
| IV4 | Feature-disabled Rust and production TS bundles contain no SDK/runtime registration or capture hooks. Verify compiled dependency/bundle artifacts, including accidental feature/import activation controls. |
| IV5 | A Rust example runs under stable libtest, remains callable by another example, returns the asserted value, and publishes its actual views. A failing assertion keeps cargo nonzero and records failure. |
| IV6 | A Vitest worker captures the returned object and a reporter reconciles native result plus teardown. A Jest fixture proves the same contract. A teardown failure cannot leave a passed example record, and a zero-check invocation remains exploratory. |
| IV7 | Nested example calls produce parent/invocation edges and fresh fixture instances. Dependency failures and recursive calls yield explicit bounded outcomes rather than cached success or a hang. |
| IV8 | Successful test observations carry the actual run ID and input fingerprint. Imports cannot acquire the host-collected execution stamp, and source claims retain their declared evidence category. A stale or foreign run artifact is rejected. |
| IV9 | Shared child references converge on one captured object; cycles terminate. Repeated domain keys with differing observations remain distinct. Depth, object, byte, string and root limits report omissions and never silently drop content. |
| IV10 | Every stored child page can be read after the source process exits. A not-captured branch gives a recollection selector, never a live callback or a changed old snapshot. |
| IV11 | Selecting a row opens the exact object and its applicable view in another pane. Browser and text paths agree across aliases, cycles and separate captures; a cross-snapshot substitution is rejected. |
| IV12 | A custom renderer works only for an allowlisted asset digest. Foreign JSON cannot authorize code. Real-browser checks deny fetch/sockets/images, parent DOM/token access, forms and top-level navigation; bad window/nonce/IDs/messages are rejected. Unexpected frame reloads revoke the message port. |
| IV13 | A custom renderer supplies a valid standard fallback. Denial, missing assets, incompatible versions, startup failure and protocol errors remain inspectable by agents and humans with the same facts. |
| IV14 | MCP and CLI discovery return types, definitions, example links, source locations, linked scope, freshness and explicit missing-capture states. An outdated catalogue never asserts repository-wide absence. |
| IV15 | Scaffolding writes no files, does not invent fields, and returns complete bounded patches or paged patches plus an assertion-failing output test and recipe. Ambiguous source symbols require disambiguation. |
| IV16 | Registered collection executes only the allowed adapter/selectors in its configured root. Unregistered IDs, argv-shaped injection, escaping paths and payload-installed runners fail before execution. |
| IV17 | Failed tests retain valid objects and diagnostics; compile error, capture error, skipped/filtered test, retry, crash, timeout and cancellation are distinct. Process-group cancellation ends children. Logs stream while work runs. |
| IV18 | A renamed field fails Rust compile/TS typecheck. Missing registration fails catalogue checks. Changed source/config/fixtures makes results stale; mid-run edits make them mixed-input. Recompile alone cannot refresh observations. |
| IV19 | Agent result/error replies stay within the existing byte budget with complete headers and content-bound cursors. CLI/MCP read handlers produce the same facts, omissions and actionable pointers. |
| IV20 | Existing v0 bundles/sessions still validate, import, navigate, page and show recorded runs. Capture import is atomic under concurrent writers and preserves immutable content hashes. |
| IV21 | Domain output tests reject dropped vigil events, duplicated-key collapse and swapped mapping fields. Selection targets and fallback content are independently asserted, with focused mutations shown to fail. |
| IV22 | A fresh agent following the shipped skill discovers a type, adds a permanent view/example, collects, reads its browser/text result, repairs a seeded error, and repeats after a type change in vigil and ContainMarks. Record commands and IDs; do not substitute JSON handwork. |

The following owner decisions are settled: Rust and TS first; SDK packages in the paneweft monorepo; no live attach in v1; repo-owned sandboxed iframe renderers; development-only hooks; browser viewer first; agent integration before IDE integration. They are not open questions to ask again.

Open implementation questions have these proposed defaults:

1. How much identity survives across runs? Keep observation identity capture-local. Use explicit logical keys only for comparison and links, retaining conflicts. Never promise address stability or deduplicate by display label.
2. Does laziness require a running process? No. Ship stored pages plus explicit not-captured branches. Recollect missing branches into a new snapshot. Live handles need a later protocol with lifetime, cancellation and authorization.
3. Which registration mechanism ships? Linkme for native Rust, explicit slices for other targets, and a TS import manifest. Verify aarch64 Linux and x86_64 Linux linking first. No filesystem reflection scanner.
4. How much macro magic is justified? Support concrete Rust types, one trait implementation path per type, sync examples and clear expanded diagnostics. Keep generic automatic registration and async Rust examples out of the first week. TS decorators are later syntax sugar; the token/symbol API is sufficient.
5. Must a person approve every test run? No. Reuse coding-session authorization through a locally configured adapter. Keep runner installation and renderer digest trust out of data submission and MCP. Do not claim the adapter sandboxes hostile repo code.
6. What counts as a valid example? Assertions plus an inspectable result and final runner completion. Assertion-free exploration is recorded separately. Retain all retry attempts; display the final attempt and prior failures, not a green-only history.
7. What freshness guarantee is achievable in a week? Conservative package input hashing, before/after checks, compiled catalogue checks and explicit external-input declarations. Dependency-perfect incremental invalidation is later. Unknown freshness stays unverified.
8. What are the limits? Use section 4's capture bounds and v0's reply byte range. Make owner configuration able to lower them. Larger limits require an explicit collection setting and remain visible in completeness metadata.
9. How are values outside JSON represented? Use tagged values for nonfinite numbers, big integers, bytes, redaction and absence. Encode Rust integers outside JavaScript's safe range as typed decimal strings; reject lossy numeric conversion. Display cells can format them, while object records retain the tag.
10. What if rendering a value is expensive or panics? Isolate the failure to that view when unwinding is possible, preserve other captured views, and mark capture failed. Cooperative budgets cannot preempt arbitrary code; the parent collection deadline ends a hung process group. No unsafe Rust thread killing.
11. Where do generated captures go? Private per-run staging, then the existing local session store. Git tracks view/example source, renderer source, small reviewed fixtures and definition inventory. Large runtime sessions remain ignored artifacts. Do not upload them automatically.
12. How is agent speed judged? Time an end-to-end seeded task, counting discovery, edits, collection, repairs and result queries. Record successful reuse by a fresh agent, bytes returned and correctness. Do not claim a speed multiplier from fewer JSON tokens or a single attractive demo.

## Local evidence and verification limits

Local inspection occurred on nixed on 2026-11-11. The host entry and `hosts/nixed.nix` were read for orientation. No builds, tests, examples, Firefox session, or paneweft browser were run in this task. The first-cycle commands above describe required future verification. No SDK code or repository configuration was edited, and no outreach was performed.

The context includes [note 03](03-moldable-development.md), researched 2026-11-10, [note 11](11-moldable-components.md), researched 2026-11-11, and paneweft's `docs/design.md`, README, schemas, core session/registry/runner/readers, viewer component/source code, CLI and MCP adapter. Build-loop was read to align the proposed authoring and review cycle, with test-quality and technical-excellence supplying test and interface criteria. These local workflow files describe desired practice, not measured outcomes.

The phoe-nix HEAD inspected was `d064373a15139b969599ee05bc7b156b1d5b8ed7`; ContainMarks was `d2a3d7624d5e21afc0714f63888642a869d2c70f`; residual-cli was `32c0836283dad8c22431b3025ec910b4b5759e90`. Local working files can differ from HEAD, so the selected byte hashes below pin the observations used in this design. Existing unrelated phoe-nix lockfile edits were left untouched.

| Root and relative file | SHA-256 of inspected bytes |
|---|---|
| paneweft `src/schemas/envelope.schema.json` | `890244ce122f1d3d8d19e0c36b2a3618d592654354941c41fd4f5500dc3c9e18` |
| paneweft `src/core/session.ts` | `019d9a699bdbfcd7de786ebfa2c440e884354c60a014f22ca12d884d088e8c95` |
| paneweft `src/core/runner.ts` | `0071d6243495512c12f26b67e88478d1c106b9547f90e6ab21907b31692befa9` |
| paneweft `src/mcp/server.ts` | `81a950b62a21ab005102d65bb5cb34ee73aaf42307d800c01280c73eab73c4b4` |
| paneweft `src/viewer/components.ts` | `1ec840f8144ad5b72d93b724a61bb120fbe668d266d57b2da115a5fcc162a9e2` |
| vigil `src/watch.rs` | `62f0229b71d3984a5187787780f9a2b26bfc592277281c8ed02b66802e451742` |
| ContainMarks `src/models.ts` | `28b6efb371b8f72fd5ab5caa4a9cf58120dfe2cccc53c01071ca0b7972ee432e` |
| ContainMarks `src/mappings/containerMappings.ts` | `b97a3fd30a00ac873bf7ab834a4f84be13b9ea7e41d91c0b01cbbadda49ac8ba` |
| ContainMarks `tests/containerMappings.test.ts` | `87b26bdd182b751fb27c2d68f1b569e1348cdd6b7058f62121b981df5e4dd2cd` |
| residual-cli `web/src/landscape-selection.ts` | `38418e62f565f9f32020068263e5344cb9759a39c17523d6832198f5933e0795` |
| residual-cli `web/src/landscape-selection.test.ts` | `4501f07ddfac618e0bda556c0005cebad300aa6c45c1b0af20df5d2ccff05771` |

The JSLink source cited in section 1 was pinned through the GitHub API to revision `a35d1cdaf47fe513d7393b3e3eafd8d9c11e34fb`, committed 2026-04-29. Other web documentation is linked at the claim it supports with access/publication dates. The proposed SDK signatures, capture contracts, limits, security policy and delivery schedule are design decisions, not claims that those APIs or guarantees already exist in GT or paneweft.

## Additions from the "views that teach" direction (orchestrator, 2026-11-11)

These come from [13](13-research-direction-views-that-teach.md) and are part of the v1 spec for review:

- **Decision trail component.** Ordered entries linked to type/view/example IDs and source anchors: question, options tried, outcome, evidence, decision; abandoned options stay visible with a reason (superseded, failed, too costly). Declared in code beside the views (`#[paneweft::trail]` / a TS trail builder) and importable from a build-loop review ledger. A dead end can keep a runnable example that demonstrates why it failed.
- **Teaching benchmark harness.** A small runner that assigns teacher, blind question author, no-file-access student (Opus or Sol), examiner and grader roles; feeds the student a view's text form and/or screenshots; records accuracy by question kind, confidence calibration, planted-error detection, cost and durability across commits. First-week scope: the harness skeleton plus one pilot topic on vigil; the full condition matrix is later.
- **Sidecar placement.** The same views, examples and trails can live beside a repository instead of in it (sidecar branch `refs/paneweft/*`, the sibling `<repo>.research/` directory, or a separate repository), pinned to the commit they describe, with stale detection. First-class in-repo placement stays the default; sidecar is required for repositories the owner does not control.

## Amendments after spec review round 1 (Sol 6/10, bar 9; orchestrator, 2026-11-11)

- **S1 week-one cut.** Week one delivers: Rust `Inspectable` + `#[paneweft::views]`/`#[paneweft::view]` + `#[paneweft::example]` (sync, concrete types) with linkme and the explicit-slice fallback; TS symbol interface + import manifest + Vitest integration; cargo and Vitest `collect`; the agent tools `list_types`, `list_views_for_type`, `list_examples`, `scaffold_view`, `collect`, `collection_status`, `cancel_collection`, `view_result`, `explain_failure` (`scaffold_example` may slip); one repo-owned renderer proof on ContainMarks; a trail builder that lowers to notebook blocks; the deterministic benchmark harness. Deferred: `derive(Inspect)`, Jest, TS decorators, generic auto-registration, async Rust examples, higher-level component builders beyond details/list/table, trail ledger import, sidecar placement, the model-run benchmark pilot. Every IV claim is tagged week-1 or later.
- **S2 cancellation through qex.** A collection job stores its qex job ID. `cancel_collection` cancels queued work with `qex cancel` and running work with `qex kill` (process group); it never assumes killing a waiter stops the job. Tests: cancel before dispatch, during execution, and after the MCP client disconnects, proving descendants stop.
- **S3 job lifecycle.** qex is the supervisor that outlives MCP clients. Job record in the session: requested → queued → running → importing → succeeded | failed | cancelled. Request dedupe: an atomic create (O_EXCL) of `jobs/<request-id>`; the same request ID with identical parameters returns the existing job, different parameters fail with CONFLICT. Import is idempotent by run ID under the write lock; a crash in `importing` is resumed or rolled back on the next status call. Crash-point tests prove one execution and one terminal import.
- **S4 renderer delivery.** Renderer documents are served by the viewer server at `/renderer/<digest>/…` with their own response headers: `Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'` and the iframe uses `sandbox="allow-scripts"` without `allow-same-origin` (opaque origin). The parent page CSP gains `frame-src 'self'`. Asset requests carry a per-frame capability token in the path (short-lived, scoped to one renderer digest), since the sandboxed frame cannot send the session bearer. The frame talks only through the postMessage contract; no HTTP route or frame message can start a collection. Tests run under the production headers.
- **S5 bounded builders.** View builders are context-owned and bounded (`cx.table(...).row(...)` returns `Bounded` and stops accepting rows at the limit); exhaustion yields partial output with retained rows and an omission count, never a failed view. `cx.reference()` beyond bounds returns a not-captured reference, not an error. The flagship examples are rewritten accordingly.
- **S6 outcomes.** Four levels, recorded separately: invocation (one attempt), example (all attempts retained; the final attempt decides), suite (setup/teardown such as Vitest `afterAll` or Rust test-binary failures; attached to the suite and shown on its examples as "suite failed after" without changing their own result), collection (exit status, timeouts, cancellation). Rust `Result::Err` and panics are failures. Composed examples: a failed child blocks its parent ("blocked by"), not "failed". Literal outcome fixtures for both adapters.
- **S7 sidecar deferred.** Not in v1 week one. When built: TS/JSON sidecar first; Rust sidecar through borrowed newtype adapters over public APIs only (coherence forbids foreign inherent impls), documented limits, explicit sidecar root registration, both source sets fingerprinted.
- **S8 trail contract.** Entry: stable ID, order, question, options[{id, status: chosen | abandoned | superseded | failed, reason, evidence refs (provenance as in v0)}], decision, snapshot-bound links to type/view/example IDs and source anchors; supersession by explicit ID. Lowered to existing notebook blocks in week one. A dead-end example has kind `dead-end` and passes when the documented failure reproduces (an expected-failure assertion); reproducing a rejected design is therefore green.
- **S9 benchmark week one.** Deterministic harness only: role orchestration with mocked models, schemas for questions, answer keys, answers, confidence (0–100) and scores, enforcement that the student context has no tools and no file access, planted-error fixtures detectable from the supplied evidence, and why-not keys that cite trail entries or other recorded evidence (not code alone). Pinned pilot topic: vigil "where can a keepalive result stop being delivered?". The model pilot is a separate recorded run after week one.
- **S10 freshness wording.** Before/after hashing is "sampled consistency", not proof the inputs never changed mid-run. Package membership: tracked files under the crate/package root plus declared extra inputs; exclusions explicit. Tests for added and deleted files; a mid-run edit that is restored is documented as undetectable.
- **S11 claims.** Add red claims for tagged non-JSON values (big integers, nonfinite floats, bytes, absence, redaction) with cross-language fixtures, alias/shared-reference behaviour, the job lifecycle, the trail contract and the harness. IV22 (scored agent exercise) is separated from deterministic red tests.
- **S12 text completeness.** Text results must carry all domain facts (e.g. vigil event tick and redelivery, ContainMarks mapping fields) within the byte budget, with continuations or declared omissions; asserted literally in both browser and text output (v0 bug W19 #13 is being fixed now).

## Defaults after spec review round 2 (final; Sol 7/10; orchestrator, 2026-11-11)

- **N1 submission atomicity.** Two-phase: (1) atomically create `jobs/<request-id>/intent.json` (O_EXCL, fsync, contains parameters and a generated dedupe key `paneweft:<request-id>`); (2) `qex submit --dedupe-key paneweft:<request-id> --dedupe-window 24h --id-file jobs/<request-id>/qex.id …`; (3) record `submitted` with the qex ID. Recovery: an intent without a qex ID is reconciled through `qex list --json` by that dedupe key; if found, adopt it; if provably absent and the intent is unsubmitted, submit once; otherwise report state `indeterminate` with the evidence and never resubmit automatically. Partial intent files (failed fsync) are treated as never created. Crash tests before and after the qex acknowledgement.
- **N2 cancellation.** `cancel_collection` issues `qex cancel`; if qex refuses because the job is `starting`/`running`, it issues `qex kill`; it then waits (bounded) for a terminal qex state and only then reports `cancelled`. Cancellation during `importing` lets the atomic import finish and reports `cancel-too-late` with the terminal outcome; cancellation after completion is a no-op returning the terminal state. Tests cover queued, starting, running, importing and completed.
- **N3 renderer loading.** Renderers ship as one external classic-script bundle plus external CSS (no ES modules in the frame), served from capability-validated routes; `script-src 'self'` from the response URL applies. Tested under production headers.
- **N4 expected failures.** A dead-end example wraps the failing call in `expect_failure(matcher, || …)` (Rust) / `expectFailure(matcher, fn)` (TS). Inside the boundary a child failure is captured, not propagated as "blocked by"; the example passes only when the failure matches; unexpected success and unrelated errors fail. Diagnostics of the reproduced failure are kept. Controls for all three cases.
- **N5 freshness membership.** Package inputs = tracked files plus untracked, non-ignored files under the package root (`git ls-files --others --exclude-standard`) plus declared extras. Tests for edits to and deletion of an imported untracked module.
- **S1 tags.** The red phase tags every IV claim `week-1` or `later`.
