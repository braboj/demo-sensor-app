# Engineering know-how

A generic, reusable reference of software-engineering patterns distilled from a
multi-service web application (a Python/Flask API, a single-page frontend, a
relational database, and a provisioned dashboard service, deployed on a managed
platform). Every entry is written to be lifted without knowing what the source
computes: names are placeholders, paths are illustrative, and the domain is
stripped out. Each pattern states the lesson, the minimal mechanism, when it
pays off, and (where the source recorded one) the alternative that was
rejected.

The document is organized by a standard engineering-template taxonomy (core,
language, infrastructure, security, workflow, data, backend, frontend,
platform), so each pattern sits where it would be contributed upstream. A
free-form section at the end collects patterns that map to no category yet: the
upstream-candidate queue.

## Contents

- [Core](#core)
- [Language (Python)](#language-python)
- [Infrastructure](#infrastructure)
- [Security](#security)
- [Workflow](#workflow)
- [Data](#data)
- [Backend](#backend)
- [Frontend](#frontend)
- [Platform](#platform)
- [Free-form: upstream-candidate queue](#free-form-upstream-candidate-queue)
- [Highest-leverage takeaways](#highest-leverage-takeaways)

## Core

Repository, documentation, configuration, quality, testing, and review hygiene.

### Fail safe: the default config is the most restrictive environment

Resolve the active configuration so that a missing or unknown selector yields
the production (locked-down) environment, never a permissive one. A forgotten
or misspelled env var then fails safe instead of shipping debug mode.

```python
# config.py
CONFIG_MAP: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
DEFAULT_CONFIG = "production"

def get_config(name=None):
    selected = name or os.getenv("APP_CONFIG") or DEFAULT_CONFIG
    return CONFIG_MAP.get(selected, ProductionConfig)  # unknown -> production
```

Pays off whenever a deploy target sets configuration through the environment:
the worst-case typo lands on the safe environment. Rejected alternative:
defaulting to development for convenience, which turns one missing variable
into a debugger exposed in production.

### No real value as a production default

A required production setting has no fallback. If it is unset, the process must
fail loudly rather than degrade to a throwaway local default that silently
masks a misconfiguration.

```python
# config.py: no default -> a missing secret stays None and surfaces early
SECRET_KEY = os.getenv("SECRET_KEY")
```

A `getenv("DATABASE_URL", "sqlite:///local.db")` style fallback is the
anti-pattern: a production box with the variable unset comes up pointed at a
local throwaway store and looks healthy. Pays off for any secret or connection
string that only has a correct value in a real deployment.

### Config by subclass with a name to class map

Keep a `BaseConfig` of shared settings and subclass per environment, overriding
only the deltas. A typed `dict[str, type[BaseConfig]]` maps a selector string
to a class. Small, readable, and type-checked, versus a sprawl of `if env ==
...` branches.

### Record the rejected alternatives, not just the decision

A decision record earns its keep by capturing the forces and the paths not
taken. "We chose X" is far less useful later than "we chose X over Y because Y
breaks under constraint Z." The rejected alternative is what makes the record
teachable and stops the same option being re-proposed.

```
decision record
├── context / forces (including platform constraints)
├── decision
├── rejected alternatives + why       <- the load-bearing part
└── tripwire: the condition that flips this decision
```

### Treat the decision record as living: supersede, do not delete

When a later decision reverses an earlier one, mark the old record superseded
and keep it. The abandoned path and its reasoning are exactly what prevent
re-litigating a settled question. A register of superseded records is a
feature.

### Every accepted trade-off names its tripwire

A trade-off is only safe to live with if the record states the exact future
condition that flips it. "We relax control A because the asset behind it is
low-value; revisit the moment the asset gains W" is a decision you can safely
forget, because the tripwire will remind you. Without it, the relaxation
quietly outlives its justification.

### Rationale-in-config is powerful but must be maintained

Comments that explain a non-obvious flag, pin, or cap are excellent
documentation right up until the code changes and the comment does not. A stale
rationale comment is worse than none: it asserts a fact readers trust. When you
change what a comment describes, change the comment in the same commit, and
treat a config comment as a claim that can rot.

### Review in priority order, deviations explicit

Review a change in a fixed priority order (security, then correctness, then
clarity, then conventions) so the expensive-to-miss issues get attention first.
Any deliberate deviation from a convention is called out in the change, never
left silent for a reviewer to rediscover.

## Language (Python)

Package structure, typing, and idioms.

### src layout, importable in tests without an editable install

Put the package under `src/` and point the test runner's path at it, so tests
import the package by its real name without a `pip install -e .` step and
without accidentally importing from the working directory.

```toml
# pyproject.toml
[tool.pytest.ini_options]
pythonpath = ["src"]
```

Pays off in CI and in containers: the import path is identical to production,
and "works on my machine because I ran from the repo root" bugs disappear.

### Give the ORM a typed base so a strict type checker sees real types

When a framework types its model base as `Any`, annotations on models buy
nothing. Define an explicit typed base and construct the ORM against it, then
subclass that base directly with typed columns. Instance attributes now carry
real types under a strict checker, and the change is schema-compatible (no
migration).

```python
# extensions.py
class Base(DeclarativeBase): ...
db = SQLAlchemy(model_class=Base)

# models.py
class Record(Base):
    __tablename__ = "record"
    id: Mapped[int] = mapped_column(primary_key=True)
    created: Mapped[datetime] = mapped_column(index=True, default=func.current_timestamp())
```

Rejected alternative: sprinkling casts or loosening strictness globally to
silence the `Any`. Adopt the framework's own modern typed idiom instead of
defeating the checker.

### Silence untyped third-party libs per module, not globally

When a dependency ships no types, scope the suppression to that module rather
than weakening strictness across your own code.

```toml
# pyproject.toml
[[tool.mypy.overrides]]
module = ["thirdparty_a", "thirdparty_b"]
ignore_missing_imports = true
```

Keeps the strict guarantee on everything you wrote while accommodating what you
cannot control. Prefer one scoped, commented ignore over a blanket relaxation.

### `bool` is a subclass of `int`

`isinstance(True, int)` is `True`, so an integer check silently accepts `True`
and `False`. Where you mean a plain integer, reject bools explicitly. Related
ordering rule: validate a value after you normalize or cast it, not before, or
valid inputs that only pass post-cast get wrongly rejected.

## Infrastructure

Build, CI/CD mechanics, and containers.

### Multi-stage build: ship the artifact, not the toolchain

Install dependencies into an isolated prefix in a builder stage, then copy only
that prefix into a slim runtime stage. Build tooling and package caches never
reach the shipped image, which shrinks it and reduces attack surface.

```dockerfile
# Dockerfile
FROM python:3.12-slim AS builder
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /install /usr/local     # artifacts only
COPY . .
```

```
builder stage                 runtime stage
[ pip + caches + compilers ]  [ slim base ]
        | build                       ^
        v                             | COPY --from=builder /install
[ /install prefix ] ------------------+   (no pip, no caches, no compilers)
```

For a compiled frontend the same shape applies: compile in a toolchain image,
copy only the emitted static bundle into a web-server image. The runtime image
needs a server, not a build toolchain.

### Order build layers by change frequency

Copy dependency manifests and install before copying source, so an edit to
source does not invalidate the cached dependency-install layer. Excluding the
installed tree in the ignore file also forces a clean, lockfile-exact install
inside the image rather than copying a host-built tree.

```dockerfile
COPY requirements.txt .        # changes rarely -> cached
RUN pip install ...
COPY . .                       # changes often -> only this layer rebuilds
```

### Run as a non-root user with a high fixed UID

Create an unprivileged user with a high, fixed UID and switch to it. The high
UID keeps the image friendly to platforms that run containers under an
arbitrary user. Pair it with interpreter flags that suit a read-only, non-root
rootfs.

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --no-create-home --uid 10001 appuser && chown -R appuser /app
USER appuser
```

### Pin base images and record the reason inline

Pin exact minor tags instead of floating `latest`, so builds are reproducible,
and leave a short inline note for a non-obvious pin (for example, why a base
was bumped off an end-of-life version). Pin the same tool identically across
every place it appears so environments stay in parity.

### Compose: gate dependents on readiness, not process-up

Express real startup dependencies declaratively, and gate them on a readiness
probe (can it serve?) rather than mere process liveness. Run schema migration
as a discrete one-shot service that dependents wait on, so nothing starts
against an unmigrated schema.

```yaml
# compose file
services:
  api:
    depends_on:
      db:      { condition: service_healthy }
      migrate: { condition: service_completed_successfully }
  migrate:
    image: same-as-api          # reuse the app image
    command: <run migrations>
    restart: "no"               # a job, not a daemon
```

Also: do not publish the database port to the host (reach it in-network only),
and match the restart policy to the lifecycle (`unless-stopped` for daemons,
`"no"` for the one-shot job).

### CI: parallel jobs, least privilege, cache on the lockfile

Split CI into independent per-stack jobs that run in parallel and localize
failures. Default the token to read-only at the workflow level and escalate
scopes only in the single job that needs them. Cache dependencies keyed on the
lockfile hash, install deterministically from the lockfile, and cancel
superseded runs on the same ref.

```yaml
# CI workflow
permissions:
  contents: read                # least privilege by default
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
jobs:
  backend:   # lint -> typecheck -> test
  frontend:  # lint -> format-check -> build -> test
  secret-scan:
  sast:      # matrix over languages, also on a weekly cron
```

```
push / PR
   ├── backend  (lint, typecheck, test)   ┐
   ├── frontend (lint, build, test)       ├── all block the merge
   ├── secret scan (full history)         │
   └── SAST matrix (+ weekly cron)        ┘
```

The build itself is a gate for a compiled frontend. Run the secret scanner over
full history, and run static analysis both on change and on a schedule so newly
disclosed rules reach unchanged code.

### A CI job name is an API

If branch protection references a required check by name, that name is a
contract. Changing what a job does is fine, but renaming the job breaks every
merge until the protection rule is updated. Rename the job and update the
protection rule in one atomic change. Corollary: a job named for two of its
steps can quietly grow a third, so trust the job body, not its label.

### One image, every environment, via injected port and concurrency

Read the bind port and worker count from the environment with compose-friendly
defaults, so the exact same image runs locally and on a platform that injects
its own port. No per-environment image variants.

```python
# server config
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = int(os.getenv("WEB_CONCURRENCY", "1"))
```

## Security

SAST, secrets, supply chain, and defensive defaults.

### Never ship the interactive debugger or dev server

The framework's debug server enables an interactive console that is remote code
execution if reachable. It must never be the container entry point. Default
debug off, gate it behind an explicit env flag, bind the dev server to
loopback, and make the production entry point the real WSGI server.

```
MVP anti-pattern:  CMD ["python", "run.py"]  ->  app.run(debug=True, host="0.0.0.0")
Fixed:             CMD ["gunicorn", "-c", "gunicorn.conf.py", "mypkg:create_app()"]
                   debug is env-gated, default off, dev host 127.0.0.1
```

### Secrets flow through env or platform generation, with scanning as a backstop

No literal secret in source or config. Interpolate from the environment with
local-only defaults, let the platform generate values it can generate, and
reference managed connection strings by handle. Enforce it with a secret
scanner in two layers: locally (pre-commit) and in CI (over full history).

### Relaxing a security default requires a compensating control and a tripwire

When you disable a protective default (say, to allow embedding, or anonymous
read), pair it with the control that keeps the asset safe (read-only, no
sign-up) and record the exact condition under which the relaxation becomes
unsafe, plus the tighter control to switch to then. A security control is only
worth its protection relative to the asset behind it.

### Verify large-file removal at the history level

Removing a large or sensitive file from the working tree does not remove it
from history, from which one command can resurrect it. Verify removal by
sweeping reachable history for large blobs, not by looking at the current tree.

```
# working-tree clean is NOT proof; sweep the object graph
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' \
  | awk '$1=="blob" && $2 > 1000000'
```

### Escape output even for static strings

Wrap even a hardcoded response string in the template escaper as a defensive
habit, so a later edit that interpolates user input does not silently become a
reflection bug.

## Workflow

Quality gates, dependency automation, and session discipline.

### Phase in a gate only when it is green; never allow-fail

A required check is only valuable if red always means a real regression. If a
gate cannot pass yet, do not add it with a continue-on-error escape hatch that
launders noise as coverage and trains everyone to ignore red. Land the enabling
work first, then turn the gate on as a one-line change. Record the deferral so
the gap is not mistaken for coverage.

```
add the capability  ->  gate goes green  ->  turn the gate on (blocking)
      NOT:  add a gate that is allowed to fail
```

### `ruff check` is not `ruff format` (a linter is not a formatter)

Lint, type, and test gates can all be green while formatting drifts, because
the format check is a separate tool. Wire both the linter and the formatter, in
both CI and pre-commit. Generalizes: verify each tool in a toolchain family is
actually invoked; one being green does not imply the others run.

### Shift-left with pre-commit that mirrors CI

Run the same gates locally that CI enforces, so red CI is rare. For tools with
project-specific config, invoke the project's own pinned toolchain from a local
hook rather than a hook-manager mirror, so local and CI versions are identical.
Pin every hook revision.

```yaml
# pre-commit config: a local hook reuses the project's pinned tool
- id: typecheck
  language: system
  entry: bash -c 'cd backend && mypy src'
  pass_filenames: false
```

### Dependency automation: group lockstep families, cap with lift conditions

Configure the update bot so it cannot propose incoherent partial upgrades.

- Group tightly-coupled package families (a framework plus its build tooling)
  so a coordinated bump arrives as one PR, not N isolated PRs that fail peer
  resolution. Batch routine minor and patch bumps; keep majors individual for
  review.
- Cap a dependency ceiling against the thing it must stay compatible with (a
  framework or runtime major), and state the condition to lift the cap in a
  comment. Caps with an expiry condition, not silent freezes.
- Permanently ignore framework majors that require a migration tool to apply.
  An isolated framework major from a bot just fails the build; do those by hand
  and then lift the coupled caps.

```yaml
# dependency-bot config
groups:
  framework:            # move in lockstep -> one coordinated PR
    patterns: ["@framework/*", "@framework-build/*"]
ignore:
  - dependency-name: "typescript"
    versions: [">=6.1"]              # capped to the framework's peer range; lift on upgrade
  - dependency-name: "@framework/*"
    update-types: ["version-update:semver-major"]   # deliberate migration, not a bump
```

### When you need several majors of a transitive dep, promote it to direct

A lockfile regenerator drops deeply peer-nested nodes, so a build tool that
peers a newer major of a shared transitive dependency can make every
regenerated lockfile fail a clean install. If several majors of that transitive
are legitimately required (so no single pin or override works), declare it as a
direct dependency. A direct entry hoists one top-level copy that survives
regeneration; a purely transitive one does not.

```
transitive-only:  bot regen drops the peer-nested copy  ->  clean install fails
direct devDep:    one hoisted top-level copy survives    ->  clean install passes
```

### Reproduce the tool to prove a tool-specific bug is fixed

Some ecosystems offer no on-demand way to trigger the automation you are
debugging. Do not declare a bot-specific bug fixed on the strength of a local
check that approximates the bot. Run the bot's own updater in its own
environment (a containerized copy of the tool) and confirm the artifact it
produces is correct. Reproduce the tool, not an approximation.

### Reuse a decision's problem statement, not its mechanism

Before copying a solution from a sibling project, decompose it into its
individual drivers and check each against your context. Adopt only the parts
whose forces you actually share, and record the scale or condition at which the
rejected parts would become worth adopting. The durable thing is the problem
statement ("deploys must be gated and observable"); the specific mechanism is
disposable and often wrong at a different scale.

### Sequence structural change before line-level change

In a large refactor, reshape the structure once (layout, module boundaries, the
test harness) before layering behavioral changes onto the new shape, to avoid
redoing line-level work against a moving target. Make the code testable before
you automate the tests, because CI gates on green tests. Package the containers
last, after behavior is stable.

### "Fixed" means proven in the environment that failed

Downgrade a claim to the level of evidence you hold. If something failed in CI
or in production, reproduce the fix in that same environment before calling it
done, a local pass is not proof. Track "not verified here yet" as an explicit
carried- forward risk rather than assuming.

### Keep pull requests small, gated, and base-first

One concern per PR, each gated by CI, each closing its tracked issue. This is
what makes a long refactor auditable and reversible. When PRs are stacked,
deleting a merged parent's branch orphans its open children (a child whose base
branch is gone cannot be reopened): retarget children to the trunk before
merging the parent, and delete branches last.

## Data

Schema, migrations, and serialization.

### Own the schema with migrations, never create-all at runtime

Runtime table creation is non-versioned, non-reversible, and races multi-worker
startup. Route every schema change through a reversible migration with a
working down step, applied once before serving (a one-shot migration step, or a
migrate call at the top of the entry script).

### Guard against committing an empty autogenerated migration

Autogeneration can emit an empty revision when nothing changed, which then
clutters history. Register a hook that drops a revision whose operations are
empty and logs that it found no changes.

```python
# migration env
def process_revision_directives(context, revision, directives):
    script = directives[0]
    if script.upgrade_ops.is_empty():
        directives[:] = []
        logger.info("No changes in schema detected.")
```

### Index the column the query actually orders by; default in the database

Add an index because a query orders or filters by that column, and say so in a
comment, rather than indexing reflexively. Set column defaults in the database
(`func.current_timestamp()`), not in application code, so every writer gets
them.

### Roll back on failure so the session is never poisoned

A failed write leaves the session in a state that breaks the next operation.
Wrap the write, roll back on failure, and re-raise for the caller to log. A
long-running writer can then catch, log, and keep going without one bad write
killing it.

```python
try:
    db.session.add(row)
    db.session.commit()
except Exception:
    db.session.rollback()   # do not leave a poisoned session
    raise
```

### Serialize timestamps as explicit ISO-8601 UTC

Returning a raw datetime lets the framework pick a lossy default format, and a
naive local value can be mislabeled. Tag naive values as UTC and emit ISO-8601,
so the wire format is unambiguous.

```python
def _iso_utc(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()   # -> ...+00:00
```

## Backend

Application structure, the HTTP boundary, observability, and streaming.

### The application factory does wiring only

The factory loads config, configures logging, binds extensions, registers
blueprints and error handlers, and nothing else. No module-global app, no
threads, no table creation, no network calls. The factory is imported by tests
and forked by the server, so any side effect runs once per import and once per
worker.

```python
# app factory
def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(get_config())      # safe default env
    if test_config is not None:
        app.config.from_mapping(test_config)  # tests overlay surgically
    if not app.config.get("TESTING"):
        configure_logging()                   # skip under tests -> keep capture
    CORS(app, resources={r"/api/*": {"origins": split_origins(app.config.get("CORS_ORIGINS"))}})
    app.register_blueprint(api)
    app.register_blueprint(health)
    register_error_handlers(app)
    db.init_app(app); migrate.init_app(app, db)
    return app
```

Pays off as import-safety, test-safety, and fork-safety at once. Rejected
alternative: starting a background producer thread in the factory, which then
runs during every test, duplicates under multi-worker serving, and doubles
under the dev reloader.

### Break the extension-to-factory import cycle with a bind step

Construct extensions at module scope in a standalone module, then bind them to
the app inside the factory. Models and blueprints import the extension without
importing the factory, so there is no import cycle. This is the reason the
two-phase `init_app` pattern exists.

```
extensions.py:  db = ORM();  migrate = Migrate()   (no app)
   ^ imported by            ^ imported by
models.py, blueprints           app factory  ->  db.init_app(app)
```

### Thin route, service owns logic, schema owns the edge

A route parses and validates input, calls a service, and serializes the result.
It owns none of the three. Validation and serialization live in a schema
module; the query lives in a stateless service.

```python
# route: three lines
limit = parse_limit(request.args.get("limit"))
rows = Service.fetch(limit)
return jsonify([serialize(row) for row in rows])
```

```
request -> [parse/validate] -> [service: query] -> [serialize] -> response
              schema.py           service.py         schema.py
```

### Validate at the boundary; a bounded param, 400 not a silent default

A type-coercing query parser (`get(key, type=int)`) returns the default on bad
input, so `?limit=abc` and `?limit=3.5` silently become the default instead of
an error. Validate explicitly: absent means default, malformed or out-of-range
means 400, with named bounds. The bound also caps result-set size, a cheap
protection.

```python
DEFAULT, LOW, HIGH = 100, 1, 100
def parse_limit(raw):
    if raw is None:
        return DEFAULT
    try:
        value = int(raw)
    except (TypeError, ValueError):
        abort(400, description="must be an integer")   # not a silent default
    if value < LOW or value > HIGH:
        abort(400, description=f"must be between {LOW} and {HIGH}")
    return value
```

### A JSON API errors in JSON, not framework HTML

Register error handlers that render every failure (aborts, 404s, uncaught
exceptions) as a structured problem object with the problem media type, rather
than the framework's default HTML page. Log an internal error once at the
handler and return a generic detail so internal context never leaks to the
client.

```python
def _problem(title, status, detail):
    resp = jsonify({"title": title, "status": status, "detail": detail})
    resp.status_code = status
    resp.content_type = "application/problem+json"
    return resp

@app.errorhandler(HTTPException)
def handle_http(exc):        # aborts / 404 / 405 -> JSON
    return _problem(exc.name, exc.code or 500, exc.description)

@app.errorhandler(AppError)
def handle_internal(exc):    # log once, return generic detail
    log.error("unhandled error: %s", exc)
    return _problem("Internal Server Error", 500, "An internal error occurred.")
```

### Split liveness from readiness, and wire each orchestrator to the right one

Liveness answers "is the process up?" with no dependencies and no auth, so an
orchestrator never restarts a healthy process because a dependency blipped.
Readiness answers "can it serve?" with the cheapest possible dependency probe,
returning 503 when it cannot. Different orchestrators consume different probes.

```python
@health.route("/health")     # liveness: no dependency, no auth
def liveness():
    return jsonify(status="ok"), 200

@health.route("/ready")      # readiness: cheapest dependency probe
def readiness():
    try:
        db.session.execute(select(literal(1)))
    except Exception:
        return jsonify(status="unavailable"), 503
    return jsonify(status="ready"), 200
```

```
container orchestrator (restart policy)  -> /health   (shallow, no deps)
service mesh / dependents (route traffic) -> /ready    (deep, probes the DB)
```

### Structured JSON logs, with caller extras surfaced and idempotent install

Emit one JSON object per log line to stdout for the runtime to collect. Diff
each record against the standard log-record attributes and promote anything a
caller attached via `extra={...}` to a top-level field, so structured context
needs no bespoke formatter per call site. Install the handler idempotently
(replace, do not append) so building the app more than once never double-logs,
and fall back to a default level on an unknown level name instead of raising.

```python
# on install: replace so repeated builds never double-log
root = logging.getLogger()
root.handlers = [handler]
root.setLevel(level_value)
```

### Server-sent events for one-way live data

For server-to-client-only updates, prefer SSE over a bidirectional socket: it
is plain HTTP, needs no client library, reconnects automatically, and adds no
new cross-origin surface behind a same-origin proxy. Rejected alternatives:
repeated full-list polling (wasteful), a bidirectional socket (more operational
weight than a one-way flow needs, kept as the upgrade path if commands ever
flow back), and a database pub/sub channel (infrastructure not warranted at
small scale).

The generator has three correctness details worth copying:

```python
# stream generator: manages its own short-lived context, primes then polls
def event_stream(app):                 # app captured in the handler, outlives the request
    last_id = 0
    with app.app_context():            # own context per poll, released at the yield
        latest = Service.fetch(limit=1)
        if latest:
            last_id = latest[0].id
            yield _sse(latest[0])       # prime: render immediately on connect
    while True:
        with app.app_context():
            rows = Service.since(last_id)   # keyset cursor: rows newer than last_id
            events = [_sse(r) for r in rows]
            if rows:
                last_id = rows[-1].id
        if events:
            yield from events
        else:
            yield ": keep-alive\n\n"     # heartbeat: also detects a dead client
        time.sleep(POLL_SECONDS)
```

Build the payload string inside the context and yield it outside, so no context
is held open while the generator is suspended at a yield. On the response,
disable caching and proxy buffering so each event flushes immediately.

```python
resp.headers["Cache-Control"] = "no-cache"
resp.headers["X-Accel-Buffering"] = "no"   # honored by common reverse proxies
```

### A cooperative worker is only as cooperative as its least-cooperative library

A long-lived connection (a stream) pins a synchronous worker, so serve it under
a cooperative worker class. But cooperation is end-to-end: a blocking C driver
in the request path blocks the cooperative hub during a call. That is
acceptable only when those calls are short, and the upgrade path (a cooperative
driver shim) should be named in advance. Understand your async model all the
way down; the least cooperative library sets the real ceiling.

## Frontend

Framework-upgrade and build-config hygiene for a single-page app.

### A framework default flip can break behavior silently

A major framework version can change a default (for example, the
change-detection or reactivity strategy) that silently breaks components
relying on the old default. Let the upgrade's migration tool preserve the old
behavior first, disable the lint rule that pushes the new default, and adopt
the new default deliberately as tracked follow-up work rather than in the
upgrade commit.

### Step a major upgrade one version at a time and verify after each

Upgrade across major versions one step at a time, running lint, build, and
tests after each step, not jumping several majors at once. Intermediate steps
are often no-ops (the code already matches the new baseline), which localizes
the one step that actually applies migrations.

### A static SPA takes some config at build time, not runtime

A compiled single-page bundle cannot read a runtime container env var; config
like the API base URL is baked in at build time. Wire it through the build
command (an environment file plus a prebuild step), and know which settings can
only be set before the bundle is emitted.

```
runtime env var  --X-->  already-compiled SPA bundle
build-time step  ------>  bundle emitted with the value baked in
```

### Local build pass is not CI test pass when toolchains differ

Two bundlers can treat the same config differently: a setting that a fast dev
bundler tolerates during a build can break a different bundler used by the test
runner. When CI catches something the local build missed, reproduce the
CI-specific path before declaring it fixed, not on the strength of the local
pass.

### Dead scaffolding survives refactors; grep for the specific artifact

A single stray line in a bootstrap file (a testing-support provider, a tutorial
import) can survive an entire refactor and ship in every bundle. After a
cleanup pass, grep for the specific flagged artifact to confirm it is actually
gone, rather than assuming the pass caught it.

## Platform

Deploying onto a constrained managed platform.

### Treat platform and free-tier limits as first-class architectural forces

The sharpest constraints often come from the hosting tier: no background
worker, no persistent disk, only a connection string (not host and port), a
single instance, cold starts. Put these in the context of a decision, not as
afterthoughts. Most non-obvious choices in a constrained deployment trace
directly to one of them.

### Keep the canonical architecture; make the platform hack an opt-in flag

When a platform constraint forces you to violate a clean design, encode the
violation as an opt-in flag that is off by default, so the clean architecture
stays the default everywhere else and the escape hatch is one config change to
remove on a better tier. Example: the canonical design runs a producer as its
own process; the constrained tier runs the same loop in-process behind a
default-off flag.

### Never start a thread before a fork (start it in the worker)

A pre-fork process manager copies only the calling thread on fork but inherits
all lock state, so a background thread started in the master leaves forked
children holding locks mid-operation, which deadlocks them. Start the thread in
the post-fork worker hook instead. The worker is a leaf process, so nothing
forks after the thread starts. You cannot catch this by reading config; you
have to run the fork path.

```
master starts thread ---fork---> worker inherits a held lock  ->  DEADLOCK
worker starts thread  (post-fork hook, leaf process)          ->  safe
```

```python
def post_worker_init(worker):            # runs inside the forked worker
    if _enabled(os.getenv("RUN_INPROCESS_PRODUCER")):
        from mypkg.worker import run_producer
        threading.Thread(target=run_producer, daemon=True).start()
```

### On diskless infrastructure, bake config into the image

A stock service that stores config on disk loses it on every restart of a
diskless tier. Bake the provisioning (datasources, dashboards, config) into the
image so it reloads from the image on every boot, and disable UI editing so the
image stays the single source of truth. Keep one provisioning tree and deliver
it two ways (bind-mount in local compose, copied into the image for the
platform).

### Adapt a platform's config shape in a thin entrypoint

When a platform exposes a value in a shape your tool cannot consume (a single
connection string where the tool wants discrete host and port), parse and
re-export it in a small entrypoint using shell parameter expansion (no extra
tooling), and default any platform-specific requirement (like requiring TLS).
Skip the block when the discrete vars are already set, so the same entrypoint
serves both environments. Parameterize one config artifact across environments
instead of maintaining per-environment copies.

### A framework's engine floor is a hidden deploy dependency

A build tool can hard-fail on an unsupported runtime version with its own
nonzero exit code, before your build even runs. If the runtime is pinned in
some places (CI) but not others (the deploy platform), the deploy breaks while
CI stays green. Distinguish the failing-commit trigger from the cause: a
nonzero exit before your build starts points at the toolchain or engine, not
your code. A runtime bump now has several sync points (the package manifest's
engines field, CI, and the deploy manifest); bump them together.

### Collapse to a single origin in production

Serve the SPA and reverse-proxy the API under one origin (a web server that
serves static files and proxies the API path to the backend), so the browser
stays same-origin and CORS is no longer a runtime concern (kept only as defense
in depth). Push environment-specific config to the edge (relative URLs plus a
proxy) rather than baking hostnames into the client. Know your proxy's DNS
semantics: some resolve the upstream once at startup and need a reload or a
resolver directive when the backend's address changes.

### The right deploy trigger is a function of fleet size

Per-service deploy hooks are the correct degenerate case for a few services
with no change detection. The same principle (deploys are CI-triggered and
observable, not fire-on-push) generalizes to a manifest-driven matrix (one
credential, a change-detection step, one matrix leg per changed service) once
the fleet grows, and to full GitOps beyond that. Pick the degenerate case
deliberately and record the threshold that forces the next tier. Notice which
past rationales invert at that threshold (a reason to skip
build-once-promote-a-digest at small scale becomes a reason to require it at
large scale).

## Free-form: upstream-candidate queue

Patterns that map to no existing template category cleanly. These are
candidates to contribute upstream; each notes where it would live and why it is
generic.

### Fork-after-thread safety as a named concurrency pattern

"Start background threads in the post-fork worker, never in the pre-fork
master" is a specific, reusable concurrency rule for any pre-fork process
manager, with a crisp failure mode (inherited-lock deadlock). It currently
reads as folklore rather than a documented pattern. Home: a backend concurrency
file, or a new process-model area.

### Promote a transitive dependency to direct to survive lockfile regeneration

The rule "when an automated updater drops peer-nested nodes, hoist the required
transitive to a direct dependency" is a generic packaging pattern for any
ecosystem with a lockfile regenerator, independent of the specific tools. Home:
a packaging or dependency-management file.

### Reproduce the tool in its own environment to prove a tool-specific bug

"Do not declare a bot-specific bug fixed on a local approximation; run the
bot's own updater in a container and check its output" generalizes to any
automation you cannot trigger on demand. Home: a workflow or CI file.

### Adapt a platform's config shape with a POSIX entrypoint shim

Parsing a connection string into discrete config vars (or otherwise reshaping
platform-provided config) in a small, dependency-free entrypoint is a portable
deployment technique. Home: a containers or deployment file.

### One artifact, two delivery mechanisms

Keeping a single source-of-truth config tree and delivering it by different
mechanisms per environment (bind-mount locally, baked into the image on a
diskless platform) is a generic infra pattern. Home: a containers or
configuration file.

## Highest-leverage takeaways

1. The application factory does wiring only. Import-safe, test-safe, fork-safe.
   Anything stateful, timed, or singleton lives outside it.
2. Never start a thread before a fork. Start background threads in the
   post-fork worker, or inherited locks deadlock the children.
3. Fail safe by default. The default config is the most restrictive
   environment; required production settings have no fallback and fail loudly.
4. Validate at the boundary, error in the API's own format. Bounded params, 400
   on malformed input, structured problem responses, not framework HTML.
5. A gate is only valuable if red always means a regression. Phase gates in
   when green; never allow-fail. Land the capability, then turn the gate on.
6. Own the schema with reversible migrations, never runtime table creation, and
   roll back on failure so the session is never poisoned.
7. Record the rejected alternatives and the tripwire. A decision without its
   forces and its expiry condition gets re-litigated or silently outlives its
   reason.
