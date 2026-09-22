# AppPack platform reference

Hand-curated platform behaviour that `apppack docgen` cannot know. Verified against the AppPack
documentation and the orchestrator/formations implementation, 2026-09-22.

`cli.md` is the generated command surface; this file is the surrounding model — what happens
after you run the command.

## Environment variables

Three different sources, and only the first is visible to `apppack config`.

**1. Yours, in SSM** — set with `config set`, listed by `config list`.

**2. AppPack-managed, also in SSM** — written by CloudFormation when you enable an addon. Shown
by `config export --all` but not by plain `config list`.

| Variable | From |
|---|---|
| `DATABASE_URL` | database addon |
| `REDIS_URL`, `REDIS_PREFIX` | Redis addon |
| `QUEUE_URL` | SQS addon — note it is **not** `SQS_URL` |
| `PUBLIC_S3_BUCKET_NAME`, `PUBLIC_S3_BUCKET_PREFIX` | public S3 addon |
| `PRIVATE_S3_BUCKET_NAME`, `PRIVATE_S3_BUCKET_PREFIX` | private S3 addon |
| `REVIEW_APP` | review apps, as `pr/<n>` |

SES sets no variables.

**3. Injected at runtime, not in SSM at all** — invisible to `config list` and `config export`,
which surprises people debugging a missing variable:

- `APPPACK_APPNAME` — always set
- `PORT` — on `web` tasks
- `AWS_REGION`, `AWS_DEFAULT_REGION` — unless you have set them yourself in SSM

**Build-time variables.** `test.env` in `apppack.toml` is the documented way to set variables
for building and testing. AppPack also supplies CI metadata when available: `CI_COMMIT_REF`,
`CI_COMMIT_SHA`, `CI_BUILD_STARTED_AT`, `CI_REPOSITORY_URL`. For Dockerfile builds these arrive
as `--build-arg`, so the Dockerfile must declare a matching `ARG` to see them; buildpack builds
get them as ordinary environment variables.

## Dockerfile builds: required container contents

A minimal image (scratch, distroless, bare Alpine) will build and serve traffic but **silently
breaks `apppack shell`, `ps exec`, and the `release` task**. The image must contain:

`bash`, `sh`, `date`, `sleep`, `pgrep`, `test`

On Debian/Ubuntu these come from `bash`, `coreutils` and `procps`; on Alpine, `bash` plus
`procps`. If `ps exec` hangs or exits oddly on a Dockerfile app, check this first.

Also note `[services.web]` is required for Dockerfile builds — the `Procfile` is ignored.

## Deploy pipeline

```
Build → Test (optional) → Finalize → Release → Deploy
```

- A failing **release** halts the deploy; no services are updated.
- The release task runs **while the previous version is still serving**. Migrations must
  therefore be backward-compatible with the running code.
- Tests run inside the build container, not as a process type.

`apppack build watch` narrates these phases; `build status` reports where it got to.

## How changes actually apply

AppPack's control plane is external to your AWS account and reacts to EventBridge events from
CodeBuild, ECS and SSM. CLI commands generally return as soon as the write lands, before the
effect is visible:

| Command | Mechanism |
|---|---|
| `config set` | SSM write → orchestrator redeploys **all** services |
| `ps scale` / `ps resize` | SSM write → orchestrator updates ECS / App Autoscaling |
| `scheduled-tasks` | SSM write → orchestrator updates EventBridge rules |
| `create` / `modify` / `destroy` | CloudFormation stack operations |

AppPack can read the *names* of your config variables but not decrypt their values.

## Domains and TLS

Every app is served at `<appname>.<cluster_domain>` with TLS, from the cluster's wildcard
certificate. Custom domains are two steps:

1. Tell the app to answer for the domain — `--domain` at `create app`, or `apppack modify app`.
2. Provide DNS and TLS — `apppack create custom-domain` handles it automatically for zones in
   Route53; otherwise request an ACM certificate, attach it to the cluster's load balancer, and
   CNAME the domain to `<app>.<cluster_domain>`.

A CNAME cannot sit at a zone apex — use a subdomain, or an apex-alias feature if your DNS
provider has one.

## Regions

AppPack runs in nine regions: `us-east-1`, `us-east-2`, `us-west-2`, `ap-northeast-2`,
`ap-south-1`, `ap-southeast-1`, `ap-southeast-2`, `eu-north-1`, `eu-west-2`. Others by request
to support@apppack.io. A cluster lives in exactly one region, and there is a region-level stack
between the account and its clusters.

## Review apps

- Created and destroyed explicitly: `apppack reviewapps create <pipeline>:<pr-number>`.
- Addressed like any app but with the compound name: `apppack -a <pipeline>:<pr> shell`.
- URL: `https://pr<pr>-<pipeline>.<cluster_domain>`.
- Config is inherited from the Pipeline, with per-review-app overrides.
- Addons come from the Pipeline. Each review app gets an isolated database and Redis namespace,
  but **S3 is one shared bucket with a per-review-app prefix** — application code must respect
  `PUBLIC_S3_BUCKET_PREFIX` / `PRIVATE_S3_BUCKET_PREFIX` or review apps will read and overwrite
  each other's files.
- No custom domains, no autoscaling, no scheduled tasks.
- No administrator access required, unlike most `create`/`destroy` operations.

## Storage

AppPack apps are **stateless** — there is no persistent filesystem and no EFS or volume option.
Anything that must survive a deploy goes in S3 (via the addon) or the database. Files written to
the container's disk disappear when the task is replaced.

## Healthchecks

The load balancer polls the healthcheck path and kills tasks that do not return 200. `/` is a
poor default and commonly causes restart loops when it:

- redirects to a login page
- redirects HTTP → HTTPS
- rejects the load balancer's IP-based `Host` header
- is slow because it renders a full dynamic page

Use a dedicated lightweight endpoint that returns 200 unauthenticated, and set it with
`--healthcheck-path`.

## Buildpacks

- Heroku's official buildpacks work directly.
- Third-party buildpacks must be shimmed: `https://cnb-shim.herokuapp.com/v1/<namespace>/<name>`.
- Multiple buildpacks run in order — e.g. `["heroku/nodejs", "heroku/python"]` to compile
  frontend assets before a Python app.
- `build.builder` defaults to `heroku-20`; `heroku-22` is also available.

## Cost

Standing per-cluster costs are the Application Load Balancer and CloudWatch Container Insights
custom metrics — these accrue even with no apps running, so idle clusters are not free.
`--multi-az` roughly doubles a database or Redis instance cost. All resources are tagged
`apppack:*` for cost allocation.

## Naming

App names must match `^[a-z0-9\-]+$` — lowercase letters, digits and hyphens only.
