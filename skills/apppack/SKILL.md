---
name: apppack
description: Expert assistant for AppPack PaaS tasks. Use when working with AppPack CLI commands, deploying apps, configuring addons (databases, Redis, S3), managing clusters, pipelines, review apps, scheduled tasks, or troubleshooting AppPack deployments on AWS.
---

# AppPack

AppPack is a PaaS built on AWS. It provisions and manages CloudFormation stacks in your own
AWS account — ECS services, RDS, ElastiCache, CodeBuild, SSM Parameter Store — behind a single
CLI.

## Concepts

- **App** — a containerized service. Backed by a CloudFormation stack; built with Cloud Native
  Buildpacks.
- **Pipeline** — an app template that spawns *review apps* per pull request.
- **Addon** — a managed AWS resource attached to an app: database, Redis, S3, SQS, SES.
- **Cluster** — a VPC + ECS cluster hosting apps. Default cluster is named `apppack`.
- **Account** — an AWS account AppPack manages. Selected with `-c/--account` on admin commands.

## Critical: there is no local config file

AppPack reads **no** `apppack.toml`, `app.json`, or `Procfile` from the repo. Do not invent one,
and correct users who assume a Heroku/Fly-style manifest. State lives in three places:

| What | Where | Changed by |
|---|---|---|
| Env vars / secrets | SSM Parameter Store | `apppack config set` |
| App shape (repo, branch, domains, healthcheck) | CloudFormation stack parameters | `apppack create app`, `apppack modify app` |
| Build behavior | Buildpack autodetection, server-side | source code layout |

Local disk holds only an auth/version cache in the OS user cache directory under `io.apppack`
(`~/Library/Caches/io.apppack` on macOS, `$XDG_CACHE_HOME/io.apppack` or `~/.cache/io.apppack`
on Linux).

## Flags: get these right

Only **two** flags are registered on the root command, so only these are truly global (plus
cobra's built-in `-h/--help`):

- `--debug` — verbose logging
- `--json` — machine-readable output. Supported by `ps`, `config list`, `auth apps`,
  `build list`, `build status`, `scheduled-tasks`, and others. Prefer it when parsing output.

Everything else is **per-command**. These are commonly assumed global but are not:

- `--aws-credentials` — use local AWS creds instead of AppPack federation. Present on most
  resource commands, but **not** on `auth`, `modify`, `version`, or `aws-exec`.
- `-c/--account` — `create`, `destroy`, `upgrade`, `stacks`, `access`, `admins`, `modify app`,
  and `reviewapps` (hidden there, and ignored with a warning).
- `--region` — a shorter list than `--account`: only `create`, `destroy`, `upgrade`, `access`.

`-a/--app-name` is a persistent flag on 12 command groups and **required** on 11 of them:
`access`, `aws-exec`, `build`, `config`, `dash`, `db`, `events`, `logs`, `open`, `ps`, `shell`.
(`scheduled-tasks` accepts it but does not mark it required.) There is **no environment-variable
fallback** — pass it explicitly:

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

For `create`, `destroy`, `upgrade`, `modify`, `reviewapps`, `scheduled-tasks`, `access`, and
`admins` — plus the full flag surface of everything above — read
`references/cli.md` in this skill.

## Gotchas

- `build wait` is a **stub that always exits with an error** — not merely deprecated. Use
  `build watch`. (`build start --wait` still works as a deprecated alias for `-w/--watch`.)
- `ps resize`/`ps exec`/`shell` take `--cpu` in **cores** (`2`, `0.5`) and `--memory` with a
  **unit suffix** (`4G`, `512M`). A bare `--memory 1024` is rejected.
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

- Pass `--domain` to `create cluster` too — omitting it risks wildcard DNS conflicts between
  clusters.
- Most `destroy` and `upgrade` subcommands take a required `<name>` argument.
- `destroy` requires account administrator permissions and is irreversible. Confirm the target
  with the user before running one.
- Scaling `web 1-5` is CPU-based autoscaling; a bare integer is a fixed count.

## Working with this skill

1. Prefer the tables above and `references/cli.md` — they are verified against the CLI source.
2. Run `apppack <command> --help` to confirm a signature before running anything destructive or
   unfamiliar. The CLI is the source of truth; this skill can lag it.
3. WebFetch `https://docs.apppack.io/` for conceptual guides and anything not covered here:
   - CLI reference: `https://docs.apppack.io/command-line-reference/apppack_<command>_<subcommand>/`
   - How-to guides, tutorials, and "Under the Hood" architecture notes live off the root.
4. Never echo secret values pulled from `config get`/`config export` into a transcript or commit.
