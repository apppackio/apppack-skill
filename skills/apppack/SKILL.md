---
name: apppack
description: Expert assistant for AppPack PaaS tasks. Use when working with AppPack CLI commands, deploying apps, configuring addons (databases, Redis, S3), managing clusters, pipelines, review apps, scheduled tasks, or troubleshooting AppPack deployments on AWS.
---

# AppPack

AppPack is a PaaS built on AWS. It provisions and manages CloudFormation stacks in your own
AWS account — ECS services, RDS, ElastiCache, CodeBuild, SSM Parameter Store — behind a single
CLI.

## Concepts

- **App** — a set of independently scalable **services** (process types), backed by a
  CloudFormation stack. Built either with Cloud Native Buildpacks (default) or from a
  Dockerfile; both are fully supported and the choice changes how you configure the app.
- **Cluster** — a VPC + ECS cluster + shared Application Load Balancer, in **one AWS region**.
  Crucially it owns a **domain**: every app is automatically served at
  `<appname>.<cluster_domain>`. Default cluster name is `apppack`. Compute is Fargate by
  default, EC2 optional.
- **Pipeline** — a special app tied to a repository rather than a branch. It runs **no services
  of its own**; it holds shared resources (CodeBuild project, config, IAM roles) and defines the
  add-ons that each review app inherits.
- **Review app** — a temporary app built from a pull request. **Not created automatically** —
  you run `apppack reviewapps create <pipeline>:<pr-number>` explicitly, and address it as
  `-a <pipeline>:<pr-number>`. Served at `https://pr<pr>-<pipeline>.<cluster_domain>`.
- **Addon** — a managed AWS resource. The sharing model differs and it matters:
  - **Database / Redis** — **cluster-level instances shared by many apps.** An admin creates the
    instance once; enabling the addon gives the app its own DB+user (or Redis user + key
    prefix) on it.
  - **S3 (public or private) / SQS / SES** — genuinely per-app resources.
- **Account** — an AWS account AppPack manages. Selected with `-c/--account` on admin commands.

## Where configuration lives

Three files in the repository root configure an app. They are read **server-side at build time**
by the AppPack builder, not by the `apppack` CLI — so grepping the CLI source for them finds
nothing. That is a fact about where the parsing happens, not evidence they are unused.

**`Procfile`** — declares services for buildpack apps, in Heroku's `name: command` format, one
per line. It is **not YAML** — do not quote or escape as if it were; commands routinely contain
`:` and `*` that would be invalid YAML.

```
web: gunicorn --bind=0.0.0.0:$PORT myapp:application
worker: celery --app myapp.celery.app worker
release: python manage.py migrate --noinput
```

Strictly it is *optional* — buildpacks can contribute default process types via the CNB
lifecycle — but in practice you want one, and you almost always need a `web` service (see
reserved process types below).

**`apppack.toml`** — build, test and deploy configuration. Full reference:
<https://docs.apppack.io/how-to/apps/apppack_toml/>

| Key | Purpose |
|---|---|
| `build.system` | `dockerfile`, or omit for buildpacks. **Matched as an exact string against `dockerfile`** — anything else (`Dockerfile`, `docker`, a typo) silently produces a *buildpack* build with no error |
| `build.buildpacks` / `build.builder` | Explicit buildpacks instead of autodetection |
| `build.dockerfile` | Dockerfile path (default `Dockerfile`) |
| `test.command` / `test.env` | Test command, and env vars for **building *and* testing** — `test.env` is the only documented way to set build-time variables |
| `deploy.release_command` | Release task — **Dockerfile builds only**; buildpack apps use the `Procfile` `release` key |
| `review_app.initialize_command` | Review-app setup (Heroku's `postdeploy`) |
| `review_app.predestroy_command` | Review-app teardown (Heroku's `pr-predestroy`). **Note the spelling** — see below |
| `[services.<name>].command` | Service definitions for **Dockerfile builds only**; buildpack apps use the `Procfile` |

> **`predestroy_command`, not `pre_destroy_command`.** The published docs show
> `pre_destroy_command`, but the orchestrator's model only accepts `predestroy_command` and
> silently discards unknown keys — so the documented spelling parses without error and the
> command never runs. Use `predestroy_command`.

**`app.json`** — partial Heroku compatibility (`buildpacks`, `environments.test`, `scripts`,
`stack`). **Ignored entirely if `apppack.toml` exists.**

## Reserved process types

Six names are special. **Do not use them for your own services** — collisions fail silently
rather than erroring:

| Name | Role |
|---|---|
| `web` | Gets the load balancer. Effectively **required**: config-var and scaling changes are keyed off the `web` task definition, so an app without one silently stops processing `config set` and `ps scale`. Bind the port given in `$PORT`. |
| `release` | One-shot task before each deploy. Failure halts the deploy. |
| `shell` | Backs `ps exec` and `db shell`. Always registered — a *user* process named `shell` is force-scaled to **zero tasks**. |
| `scheduler` | Runs `scheduled-tasks` commands. Always registered — a user process named `scheduler` collides with it. |
| `postdeploy` | Runs `review_app.initialize_command`. |
| `pr-predestroy` | Runs `review_app.predestroy_command`. |

None of these is backed by a long-running service; their task definitions are registered at run
time. Two consequences worth knowing:

- **`apppack ps` won't list them** until one is actually running. That is normal, not a fault.
- **`apppack ps resize` works on them ahead of time**, storing CPU/memory for the next run. This
  is how you give a migration or a `shell` session more memory.

`[test]` is not a process type at all — it runs inside the build container, so it never appears
in `ps`.

On Ruby buildpack apps, the process types `console` and `rake` are dropped automatically.

## Where the rest of the state lives

| What | Where | Changed by |
|---|---|---|
| Env vars / secrets | SSM Parameter Store | `apppack config set` |
| App shape (repo, branch, domains, healthcheck) | CloudFormation stack parameters | `apppack create app`, `apppack modify app` |
| **Scaling** (counts, CPU/memory) | **SSM**, not CloudFormation | `apppack ps scale` / `ps resize` |
| **Scheduled tasks** | **EventBridge rules**, driven from SSM | `apppack scheduled-tasks` |

Scaling and scheduled-task changes are SSM writes that an external orchestrator reacts to, which
is why those commands return before anything has visibly happened.

Local disk holds only an auth/version cache in the OS user cache directory under `io.apppack`
(`~/Library/Caches/io.apppack` on macOS, `$XDG_CACHE_HOME/io.apppack` or `~/.cache/io.apppack`
on Linux).

## Flags: get these right

Only **two** flags are registered on the root command, so only these are truly global (plus
cobra's built-in `-h/--help`):

- `--debug` — verbose logging
- `--json` — machine-readable output. Supported by `ps`, `config list`, `auth apps`,
  `build list`, `build status`, `scheduled-tasks`, and others. Prefer it when parsing output.

Everything else is **per-command**, including four that are routinely mistaken for global:
`--aws-credentials`, `-c/--account`, `--region`, and `-a/--app-name`. Passing one to a command
that doesn't register it is an error. `references/cli.md` has the authoritative
"Scoped flags — NOT global" table listing exactly which groups accept each — consult it rather
than assuming, and rather than trusting any list written here.

`-a/--app-name` is required on most app-scoped commands and has **no environment-variable
fallback** — pass it explicitly every time:

```bash
apppack config set -a my-app DEBUG=false
apppack ps scale -a my-app web 2
```

## Common commands

```bash
# Auth
apppack auth login [--no-browser]
apppack auth apps                          # apps you can access

# Config (env vars live in SSM)
apppack config list -a my-app [--json]
apppack config set -a my-app KEY=value
apppack config export -a my-app [--all]    # emits JSON, not shell exports; --all includes DATABASE_URL etc.
apppack config import -a my-app vars.json  # positional file required

# Processes
apppack ps -a my-app                       # current state
apppack ps scale -a my-app web 2           # fixed count
apppack ps scale -a my-app web 1-5         # CPU autoscaling
apppack ps resize -a my-app web --cpu 2 --memory 4G       # --cpu is CORES (float); --memory needs M/MB/G/GB suffix. Both required.
apppack ps restart -a my-app web [--force]
apppack ps exec -a my-app -- ./manage.py migrate          # no process-type argument

# Builds & deploys
apppack build start -a my-app [-w] [--ref <git-ref>]
apppack build list -a my-app [--json]
apppack build watch -a my-app [<build-number>]
apppack build status -a my-app [<build-number>] [--json]

# Observability
apppack logs -a my-app [-f] [--start 5m] [--filter <pattern>]
apppack events -a my-app <service>         # <service> is required
apppack dash -a my-app

# Database
apppack db shell -a my-app
apppack db dump -a my-app -o dump.sql
apppack db load -a my-app dump.sql         # positional dumpfile required (local path or s3://)

# Escape hatch: run any local command with AppPack-federated AWS creds
apppack aws-exec -a my-app -- aws s3 ls
```

Two reference files ship with this skill — read them rather than guessing:

- **`references/cli.md`** — the complete command and flag surface, generated from
  `apppack docgen`. Use it for `create`, `destroy`, `upgrade`, `modify`, `reviewapps`,
  `scheduled-tasks`, `access`, `admins`, and the full flag list of everything above.
- **`references/platform.md`** — how the platform behaves around the commands: the full
  environment-variable model, what a Dockerfile image must contain for `ps exec` to work, the
  build/release/deploy sequence, domains and TLS, review-app specifics, regions, healthchecks,
  and cost.

## Gotchas

- `build wait` is a **stub that always exits with an error** — not merely deprecated. Use
  `build watch`. (`build start --wait` still works as a deprecated alias for `-w/--watch`.)
- `ps resize`/`ps exec`/`shell` take `--cpu` in **cores** (`2`, `0.5`) and `--memory` with a
  **unit suffix** (`4G`, `512M`). A bare `--memory 1024` is rejected.
- On `ps resize`, `--cpu` and `--memory` are **both mandatory** despite `references/cli.md`
  showing defaults for them — cobra permits a flag to have a default and still be required, and
  docgen cannot show that. Omitting either gives
  `Error: required flag(s) "cpu", "memory" not set`.
- `--addon-database` / `--addon-redis` on `create app` and `create pipeline` **attach to an
  existing instance — they do not provision one.** Run `apppack create database` /
  `apppack create redis` first. These flags were silently **no-ops before CLI v4.8.1**
  (apppackio/apppack#163, fixed by #164). From v4.8.1 they auto-select when exactly one instance
  exists on the cluster and error with the choices when several do; `--addon-database-name` /
  `--addon-redis-name` disambiguate. On older CLIs the `-name` variants are mandatory.
- **Always pass `--cidr` to `create cluster`.** It defaults to `10.100.0.0/16`, which collides
  with an existing VPC more often than you'd think. Check first:

  ```bash
  aws ec2 describe-vpcs --query 'Vpcs[*].[CidrBlock,Tags[?Key==`Name`].Value|[0]]' --output table
  ```

- `create cluster` also needs `--domain`. This is not hygiene — the cluster domain is its
  identity for DNS and TLS, and is what gives every app its `<app>.<cluster_domain>` URL.
- Most `destroy` and `upgrade` subcommands take a required `<name>` argument.
- `create custom-domain` accepts **1 to 6** domains — one primary plus up to five alternates.
  More than six is rejected.
- **`destroy app` erases addon *data*, not just the stack** — the database, S3 bucket and its
  files, and the SQS queue all go. Redis data is the one documented exception. This is
  irreversible and admin-only; confirm the exact target with the user before running it.
- **Administrator access is needed for more than `destroy`**: `create app`, `create database`,
  `create redis` and `create custom-domain` all require it. Creating and destroying *review
  apps* is the deliberate exception — any user with Pipeline access can do it.
- **`config set` triggers a full redeploy** of every service. It is not a passive write, so
  batch changes rather than setting variables one at a time.
- Scaling `web 1-5` is CPU-based autoscaling; a bare integer is a fixed count. **Review apps
  support neither autoscaling nor scheduled tasks.**

## Working with this skill

1. Prefer this file and the two reference files. `references/cli.md` is generated from the CLI
   itself; the conceptual material is verified against the AppPack docs and the orchestrator
   implementation.
2. Run `apppack <command> --help` to confirm a signature before running anything destructive or
   unfamiliar. The CLI is the source of truth; this skill can lag it.
3. WebFetch `https://docs.apppack.io/` for conceptual guides and anything not covered here:
   - CLI reference: `https://docs.apppack.io/command-line-reference/apppack_<command>_<subcommand>/`
   - How-to guides, tutorials, and "Under the Hood" architecture notes live off the root.
4. Never echo secret values pulled from `config get`/`config export` into a transcript or commit.
