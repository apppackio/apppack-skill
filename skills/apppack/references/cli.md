# AppPack CLI reference

Full command surface, verified against the CLI source. The CLI itself is authoritative — run
`apppack <command> --help` when in doubt. Regenerate the upstream docs with `apppack docgen`
(hidden command, `-d/--directory`, defaults to `./docs`); that output is what powers
<https://docs.apppack.io/command-line-reference/>.

## Global flags

Registered on the root command, valid everywhere:

| Flag | Meaning |
|---|---|
| `--debug` | Enable debug logging |
| `--json` | Machine-readable output (supported by `ps`, `config list`, `auth apps`, `build list`, …) |
| `-h`, `--help` | Help for any command |

**Not global**, despite appearing on many commands:

- `--aws-credentials` — use local AWS credentials rather than AppPack federation. On: `access`,
  `admins`, `build`, `config`, `create`, `dash`, `db`, `destroy`, `events`, `logs`, `open`, `ps`,
  `reviewapps`, `scheduled-tasks`, `shell`, `stacks`, `upgrade`. **Absent** on `auth`, `modify`,
  `version`, `aws-exec`.
- `-c/--account` — on `create`, `destroy`, `upgrade`, `stacks`, `access`, `admins`, `modify app`,
  and `reviewapps` (hidden there; accepted but ignored with a warning).
- `--region` — a shorter list than `--account`: only `create`, `destroy`, `upgrade`, `access`.
  **Not** on `stacks`, `admins`, or `modify app`.
- `-a/--app-name` — persistent on 12 groups, **required** on 11: `access`, `aws-exec`, `build`,
  `config`, `dash`, `db`, `events`, `logs`, `open`, `ps`, `shell`. `scheduled-tasks` accepts it
  but does not mark it required. No env-var fallback.

## auth

```bash
apppack auth login [--no-browser]
apppack auth logout
apppack auth whoami
apppack auth accounts              # accounts you administer
apppack auth apps                  # apps you can access
```

## config

Environment variables, stored in SSM Parameter Store. `-a/--app-name` required.

```bash
apppack config list -a <app> [--json]
apppack config get -a <app> <VAR>
apppack config set -a <app> <VAR>=<value>
apppack config unset -a <app> <VAR>
apppack config export -a <app> [--all]        # JSON output; --all includes AppPack-managed vars (DATABASE_URL, REDIS_URL, …)
apppack config import -a <app> <file> [--overwrite]   # file is a JSON {"KEY":"VALUE"} map
```

Also accepts `--aws-credentials`.

## ps

`-a/--app-name` is persistent on `ps` and required.

```bash
apppack ps -a <app> [--json]
apppack ps scale -a <app> <process_type> <count>     # e.g. web 2
apppack ps scale -a <app> <process_type> <min>-<max> # e.g. web 1-5, CPU autoscaling
apppack ps resize -a <app> <process_type> --cpu <cores> --memory <size>  # both required
apppack ps restart -a <app> <process_type> [--force]
apppack ps exec -a <app> -- <command>                # no process-type argument
```

`--cpu` is **CPU cores** as a float (default `0.5`) — `2`, `0.5`, not `512`. `--memory` is a
string that **must end in `M`/`MB`/`G`/`GB`** (default `1G`); a bare number is rejected with
`unexpected memory format`. Example from the source: `apppack -a my-app ps resize web --cpu 2 --memory 4G`.

`ps exec` also accepts `-r/--root`, `-l/--live`, `--cpu`, `--memory` — same semantics as `shell`.

## build

```bash
apppack build start -a <app> [-w|--watch] [--ref <git-ref>]   # --wait is a deprecated alias for -w
apppack build list -a <app> [--json]
apppack build watch -a <app> [<build-number>]
apppack build status -a <app> [<build-number>] [--json]
apppack build wait -a <app>      # REMOVED — stub that always exits with an error; use watch
```

## logs

```bash
apppack logs -a <app> [flags]
apppack logs open -a <app>       # open CloudWatch in a browser
```

Flags below are on `logs` only and are **not** inherited by `logs open`, which takes just `-a`
and `--aws-credentials`:

| Flag | Notes |
|---|---|
| `-f, --follow` | Tail |
| `--start <when>` | Default `5m`; RFC3339 or relative `s`/`m`/`h`/`d` |
| `--stop <when>` | Default `now`; same formats |
| `--filter <pattern>` | Filter pattern |
| `--prefix <value>` | **Takes a value** — log group prefix, e.g. `web`, `worker` |
| `--raw`, `--rawString`, `--expand`, `--invert` | Output shaping (booleans) |

## db

```bash
apppack db shell -a <app>
apppack db dump  -a <app> [-o|--output <file>]
apppack db load  -a <app> <dumpfile> [-j|--jobs <n>]   # dumpfile: local path or s3://…; --jobs is pg_restore only, default 2
```

## shell / exec / open

```bash
apppack shell -a <app> [-r|--root] [-l|--live] [--cpu <units>] [--memory <MB>]
apppack open -a <app>
apppack aws-exec -a <app> -- <command>    # run a local command with AppPack-federated AWS creds
```

## events / dash

```bash
apppack events -a <app> <service> [-w|--wait-for-steady]   # <service> required
apppack dash -a <app>
```

## create

Persistent flags on all `create` subcommands: `-c/--account`, `--region`, `--aws-credentials`,
`--check`, `--non-interactive`.

```bash
apppack create app <name> [flags]
```

| Flag | Notes |
|---|---|
| `-r, --repository <url>` | Source repository |
| `-b, --branch <branch>` | Branch for continuous deployment |
| `-d, --domain <domain>` | Custom domain |
| `--healthcheck-path <path>` | Default `/` |
| `--cluster <name>` | Default `apppack` |
| `--ec2` | Run on EC2 instances rather than Fargate |
| `--addon-database` | Attach an **existing** database — create it first. No-op before v4.8.1 |
| `--addon-database-name <name>` | Implies `--addon-database`; required on CLIs < v4.8.1 |
| `--addon-redis` | Attach an **existing** Redis — create it first. No-op before v4.8.1 |
| `--addon-redis-name <name>` | Implies `--addon-redis`; required on CLIs < v4.8.1 |
| `--addon-public-s3` / `--addon-private-s3` | S3 bucket |
| `--addon-sqs` | SQS queue |
| `--addon-ses` / `--addon-ses-domain <domain>` | SES |
| `-u, --users <emails>` | Comma-separated |
| `--disable-build-webhook` | Skip webhook creation |

```bash
apppack create pipeline <name> [flags]   # ~same flags as create app, minus --branch/--domain/--disable-build-webhook

apppack create cluster [name] [--domain <domain>] [--cidr <cidr>] [--create-region]
  # --cidr defaults to 10.100.0.0/16. ALWAYS set it explicitly — the default collides with
  # existing VPCs. Audit first:
  #   aws ec2 describe-vpcs --query 'Vpcs[*].[CidrBlock,Tags[?Key==`Name`].Value|[0]]' --output table
  # Set --domain as well; omitting it risks wildcard DNS conflicts between clusters.

apppack create database [name] [flags]
  -e, --engine <engine>            # postgres (default), mysql, aurora-mysql, aurora-postgresql
  -i, --instance-class <class>     # default db.t4g.medium
  --allocated-storage <GB>         # default 50
  --max-allocated-storage <GB>     # default 500
  --multi-az
  --cluster <name>                 # default apppack

apppack create redis [name] [--instance-class <class>] [--multi-az] [--cluster <name>]
  # --instance-class default cache.t4g.micro

apppack create custom-domain <domain> [<alt-domain>...]   # 1-6 domains: one primary + up to 5 alternates
apppack create region
```

## modify

Change an existing app or pipeline stack. Admin only. Note: no `--aws-credentials`.

```bash
apppack modify app <name> [flags]
  -r, --repository <url>
  -b, --branch <branch>
  -d, --domains <domain,...>     # list, note the plural
  --healthcheck-path <path>
  -c, --account <id>
```

## reviewapps

Per-pull-request apps spawned from a pipeline.

```bash
apppack reviewapps <pipeline>
apppack reviewapps create <pipeline:pr-number> [--release <release>]
apppack reviewapps destroy <pipeline:pr-number>
```

Flags: `--aws-credentials`; `-c/--account` is present but hidden and ignored with a warning.
`reviewapps create` exposes `--release` (visibly, due to an upstream bug in which the
`MarkHidden` call targets the wrong command).

## scheduled-tasks

```bash
apppack scheduled-tasks -a <app> [--json]
apppack scheduled-tasks create -a <app> -s "<cron>" "<command>"
apppack scheduled-tasks delete -a <app> [<index>]
```

`-a/--app-name` and `--aws-credentials` are persistent on the group. `-s/--schedule` is on
`create` **only** — it is not valid on `delete`. The schedule must be exactly 6 space-separated
fields or the command errors.

## access / admins

All four `add`/`remove` commands accept **one or more** emails.

```bash
apppack access -a <app>
apppack access add -a <app> <email>...      # e.g. user1@example.com user2@example.com
apppack access remove -a <app> <email>...
apppack admins
apppack admins add <email>...
apppack admins remove <email>...
```

Flags: `-c/--account`, `--aws-credentials`; `access` also takes `--region`.

## upgrade

Persistent flags: `-c/--account`, `--region`, `--aws-credentials`, `--check` (dry run — creates a
CloudFormation change set without applying). Note `destroy` has **no** `--check`.

```bash
apppack upgrade app <name>
apppack upgrade pipeline <name>
apppack upgrade cluster <name>
apppack upgrade database <name>
apppack upgrade redis <name>
apppack upgrade account
apppack upgrade region
```

## destroy

**Irreversible. Requires account administrator permissions.** Confirm the target before running.

```bash
apppack destroy app <name>
apppack destroy pipeline <name>
apppack destroy cluster <name>
apppack destroy database <name>
apppack destroy redis <name>
apppack destroy custom-domain <name>
apppack destroy region
apppack destroy account
```

Flags: `-c/--account`, `--region`, `--aws-credentials`.

## misc

```bash
apppack stacks [-c <account>]
apppack version
apppack version check
apppack version update [-f|--force]
apppack completion [bash|zsh|fish|powershell]
apppack docgen [-d <directory>]    # hidden; regenerates the Markdown command reference
```
