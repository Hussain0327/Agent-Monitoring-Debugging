# SDK Source Files

Every file in `sdk/src/vigil/` explained in plain language.

## `__init__.py` — The Front Door
The public API of the SDK. When you write `import vigil`, this file decides what you can access. It re-exports `init`, `shutdown`, `trace`, `span`, and the data types so you never need to import from internal modules.

## `_config.py` — The Settings Panel
A frozen dataclass that holds all SDK configuration (endpoint, API key, batch size, etc.). "Frozen" means once created, settings can't be changed — this prevents accidental mutations. It also computes derived values like the full ingest URL and auth headers.

## `_types.py` — The Data Shapes
Pydantic models defining what a Trace, Span, and Event look like. Think of these as blueprints: a Span has an ID, name, kind (LLM/tool/chain), timing info, and optional input/output data. The `SpanKind` and `SpanStatus` enums constrain values to valid options.

## `_context.py` — The Thread of Conversation
Uses Python's `contextvars` to track which trace and span are "active" right now. This is like a thread-local variable but also works with async code. When you nest `@span` inside `@trace`, the context keeps track of parent-child relationships automatically.

## `_client.py` — The Orchestrator
`VigilClient` is the brain of the SDK. It manages the lifecycle (start/shutdown), creates traces and spans, links them via context, and hands completed spans to the exporter. There's a global singleton so decorators can find the client without you passing it around.

## `_exporter.py` — The Mail Carrier
`BatchSpanExporter` collects finished spans into batches — like putting letters into a mailbag. When the bag is full (`batch_size`) or enough time passes (`flush_interval_ms`), it sends everything to the server in one HTTP POST. If delivery fails, spans go back in the bag for retry.

## `decorators.py` — The Easy Buttons
`@trace` and `@span` are decorators that automatically wrap your functions. They detect whether your function is sync or async, start the appropriate trace/span, capture errors, and clean up afterward. You get observability by adding one line above your function.

## `integrations/__init__.py` — The Plugin Registry
A simple registry pattern: integrations register themselves by name, and you activate them with `activate("openai")`. This keeps the core SDK lightweight — integrations are optional.

## `integrations/openai.py` — The OpenAI Interceptor
Monkey-patches `openai.Completions.create` (and the async variant) to automatically create LLM spans. Every OpenAI call gets its model, messages, and token usage captured without changing your code.

## `integrations/anthropic.py` — The Anthropic Interceptor
Same pattern as the OpenAI integration but for Anthropic's `Messages.create`. Captures model, messages, token usage, and stop reasons.
