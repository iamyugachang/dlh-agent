<!-- GSD:project-start source:PROJECT.md -->
## Project

**trino-agent**

A set of Claude Code skills (markdown) and Python scripts that let users query a Trino/Iceberg cluster using natural language — no SQL knowledge required. Users drop the skills into their Claude Code setup and immediately start exploring schemas, running queries, and inspecting tables by just describing what they want.

**Core Value:** A non-technical user can ask a plain English question and get results from Trino — without writing a single line of SQL.

### Constraints

- **Tech stack**: Python 3.10+, LangGraph, Anthropic SDK, trino Python client — no substitutions
- **Harness**: Claude Code only for v1 — skills are markdown, not MCP
- **Auth**: Username/password via env vars — no OAuth or SSO in v1
- **Execution model**: Auto-execute (generate SQL, run, return results) — no confirmation step
- **Distribution**: Skills distributed as files users drop in place — no package manager required
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Runtime
| Layer | Library | Version (pin at) | Confidence | Rationale |
|-------|---------|-----------------|------------|-----------|
| Python runtime | Python | `>=3.10,<3.13` | HIGH | LangGraph and trino client both require 3.10+; 3.12 is the 2025 stable release with best ecosystem support |
| Trino connectivity | `trino` | `>=0.330.0` | MEDIUM | Official Python client maintained by Trinodb; `0.330.x` series added stable `auth.BasicAuthentication` and cursor row iteration improvements; username/password via `trino.auth.BasicAuthentication` |
| LLM orchestration | `langgraph` | `>=0.2.0,<0.3.0` | MEDIUM | `0.2.x` is the stable series as of mid-2025; introduced `StateGraph` with typed state, interrupt/resume, and proper tool-call loop primitives — exactly what an agentic NL→SQL loop needs |
| LangChain core (required by LangGraph) | `langchain-core` | `>=0.3.0` | MEDIUM | LangGraph 0.2.x depends on langchain-core 0.3.x; pin together |
| Anthropic tool-use binding | `langchain-anthropic` | `>=0.3.0` | MEDIUM | Wraps Anthropic API in LangChain's `BaseChatModel` interface; enables LangGraph tool-call nodes with Claude models; supports `claude-3-5-sonnet` and `claude-3-7-sonnet` |
| Anthropic SDK (direct) | `anthropic` | `>=0.40.0` | MEDIUM | Used when bypassing LangChain wrapper for direct API calls or streaming; `0.40+` has stable tool_use support and streaming with `with client.messages.stream()` |
| Environment config | `python-dotenv` | `>=1.0.0` | HIGH | Industry standard for `.env` loading; zero dependencies; non-technical users can configure with a text file |
### Schema Introspection
| Layer | Library | Version | Confidence | Rationale |
|-------|---------|---------|------------|-----------|
| Schema discovery (primary) | `trino` client (built-in) | same as above | HIGH | `cursor.execute("SHOW SCHEMAS IN catalog")`, `SHOW TABLES`, `DESCRIBE table` — no extra library needed; Trino's information_schema views are the correct interface |
| Schema discovery (secondary) | `sqlalchemy` + `trino-sqlalchemy` | `sqlalchemy>=2.0`, `trino>=0.330` | MEDIUM | `trino` installs a SQLAlchemy dialect (`sqlalchemy://`); enables `inspect(engine).get_table_names()` and reflection — useful if you want SQLAlchemy-style introspection over raw SQL; NOT required for v1 |
### Output & Formatting
| Layer | Library | Version | Confidence | Rationale |
|-------|---------|---------|------------|-----------|
| Result formatting | `tabulate` | `>=0.9.0` | HIGH | Lightweight; produces markdown-friendly table output from cursor results; no pandas required; `tabulate(rows, headers=col_names, tablefmt="pipe")` renders inside Claude Code responses |
| JSON handling | stdlib `json` | stdlib | HIGH | Cursor metadata (column types, Iceberg partition specs) is JSON-serializable with stdlib; no extra library |
### Development & Quality
| Layer | Library | Version | Confidence | Rationale |
|-------|---------|---------|------------|-----------|
| Dependency management | `pip` + `requirements.txt` | stdlib | HIGH | Consistent with "drop files in place" distribution; no Poetry or uv required for v1; a single `pip install -r requirements.txt` is the install story |
| Testing | `pytest` | `>=8.0` | HIGH | Standard; `pytest-asyncio` needed if any async LangGraph nodes are tested |
| Async support (optional) | `asyncio` | stdlib | HIGH | LangGraph supports both sync and async graph execution; async preferred for streaming output but sync is fine for v1 auto-execute |
## Model Choice
| Model | Recommendation | Rationale |
|-------|---------------|-----------|
| `claude-3-5-sonnet-20241022` | **Primary** (HIGH confidence) | Best SQL generation accuracy in the claude-3.5 generation; strong instruction-following for schema-constrained SQL; available via `langchain-anthropic` and direct SDK |
| `claude-3-7-sonnet-20250219` | Secondary / upgrade path | Released early 2025; stronger reasoning for complex multi-join queries; use if 3-5-sonnet produces incorrect SQL on complex schemas |
| `claude-3-haiku-*` | NOT for SQL generation | Fast and cheap but weaker at schema-constrained SQL synthesis; reserve for schema browsing summarization if needed |
## LangGraph Architecture Choice
- ReAct loops require the model to decide when to call `execute_sql` — unnecessary indirection when auto-execute is the spec
- A linear `StateGraph` is simpler, deterministic, and easier to debug
- Tool-calling loop adds latency (extra round-trips to Claude) for no benefit in auto-execute mode
- `StateGraph` gives you free retry/branching without manual try/except orchestration
- State typing (TypedDict) makes the SQL→result handoff explicit
- Future milestone (FastAPI server) can reuse the graph as-is
## Alternatives Considered
| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Orchestration | `langgraph` | `langchain` LCEL chains | LangGraph's graph model handles retry/branching cleanly; LCEL chains are linear pipelines, awkward for conditional SQL retry |
| Orchestration | `langgraph` | raw `anthropic` SDK loop | Viable but loses typed state, retry primitives, and future compatibility with FastAPI milestone |
| Trino client | `trino` (official) | `PyHive` | PyHive is HiveServer2-native; Trino has its own HTTP/REST protocol; `trino` client speaks the correct Trino REST API |
| Trino client | `trino` (official) | `sqlalchemy` dialect alone | SQLAlchemy adds complexity; raw `trino.dbapi` gives full cursor control for row streaming and column metadata |
| Result formatting | `tabulate` | `pandas` | pandas is 30 MB of dependency for what is ultimately `tabulate(rows, headers=cols)`; avoid for a "drop files in place" tool |
| Result formatting | `tabulate` | `rich` | rich is excellent but outputs ANSI; Claude Code renders markdown, not terminal ANSI — `tablefmt="pipe"` from tabulate is correct |
| Config | `python-dotenv` | `pydantic-settings` | pydantic-settings is excellent but adds pydantic as a dependency; for v1 env-var-only config, dotenv is sufficient |
| Schema introspection | raw SQL via `trino` client | `sqlalchemy` reflection | SQLAlchemy reflection on large Iceberg catalogs can be slow (scans all tables); targeted `SHOW SCHEMAS / SHOW TABLES` queries are faster and require no extra library |
## What NOT to Use
| Library | Reason to Avoid |
|---------|----------------|
| `MCP` / any MCP SDK | Explicitly out of scope per PROJECT.md; MCP server is deferred to a future milestone |
| `FastAPI` / `uvicorn` | Web server stack deferred to future milestone; v1 is CLI/script execution only |
| `SQLAlchemy` (as primary interface) | Adds unnecessary abstraction; `trino.dbapi` cursor is the correct interface for programmatic query execution; SQLAlchemy dialect fine as optional add-on |
| `pandas` | Heavy dependency for a "drop files" tool; tabulate handles display; if users need DataFrames they can wrap results themselves |
| `PyHive` / `pyhive` | Wrong protocol — speaks HiveServer2 Thrift, not Trino's REST API |
| `openai` SDK | Project is Anthropic-only; `langchain-anthropic` is the correct binding |
| `llama-index` / `LlamaIndex` | Full RAG framework; massive overkill for NL→SQL with a known schema; adds 50+ transitive dependencies |
| `langchain` LCEL (standalone) | LangGraph supersedes LCEL for agentic flows in 2025; LCEL still used internally by LangGraph but don't write raw LCEL chains for the agent |
| `Kerberos` / `requests-kerberos` | Out of scope per PROJECT.md; username/password auth is the v1 requirement |
| `aiotrino` | Async Trino client; Trino's official async story is not mature; synchronous `trino.dbapi` is stable and sufficient for v1 |
## Installation
# Create virtualenv (recommended)
# Core agent dependencies
# Dev / test
## Environment Variables (config contract)
# .env
## Confidence Summary
| Area | Confidence | Notes |
|------|------------|-------|
| Stack choices (which libraries) | HIGH | These are the correct tools for each job; no ambiguity |
| Version numbers | MEDIUM | Based on training data through Aug 2025; verify with `pip install --dry-run` before pinning |
| LangGraph graph topology | HIGH | StateGraph with linear nodes is the correct 2025 pattern for deterministic agentic SQL |
| Model choice | HIGH | claude-3-5-sonnet-20241022 is the established SQL generation model in the claude-3 family |
| Trino auth method | HIGH | `trino.auth.BasicAuthentication` is the documented username/password mechanism |
## Sources
- Trino Python client docs: https://github.com/trinodb/trino-python-client
- LangGraph documentation: https://langchain-ai.github.io/langgraph/
- Anthropic tool use guide: https://docs.anthropic.com/en/docs/tool-use
- langchain-anthropic package: https://python.langchain.com/docs/integrations/chat/anthropic/
- Note: version numbers not verified via live PyPI due to network tool restrictions in this research session; treat as MEDIUM confidence and pin after local verification
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
