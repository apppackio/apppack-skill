<!-- GENERATED FILE — DO NOT EDIT.
     Regenerate with `just cli-docs`.
     Source: apppack docgen (4.8.2). -->

# AppPack CLI reference

Every command and flag in the AppPack CLI, generated from `apppack docgen` (4.8.2). Operational guidance and version history that docgen cannot know live in `SKILL.md`, not here.

**A shown default does not mean a flag is optional.** cobra allows a flag to have a default *and* be required, and docgen cannot express the difference — `ps resize` shows `--cpu` defaulting to 0.5 yet rejects the command if you omit it. Where `SKILL.md` marks a flag required, believe it over the default shown here.

## Truly global flags

Registered on the root command, valid everywhere:

- `--debug` — enable debug logging
- `--json` — output as JSON
- `-h, --help` — help for any command

## Scoped flags — NOT global

These look global but are registered per command group. Using one outside its group fails:

| Flag | Valid on |
|---|---|
| `--account` | `access`, `admins`, `create`, `destroy`, `modify`, `stacks`, `upgrade` |
| `--app-name` | `access`, `aws-exec`, `build`, `config`, `dash`, `db`, `events`, `logs`, `open`, `ps`, `scheduled-tasks`, `shell` |
| `--aws-credentials` | `access`, `admins`, `build`, `config`, `create`, `dash`, `db`, `destroy`, `events`, `logs`, `open`, `ps`, `reviewapps`, `scheduled-tasks`, `shell`, `stacks`, `upgrade` |
| `--region` | `access`, `create`, `destroy`, `upgrade` |

## Commands

### access

list users with access to the app

```
apppack access
```

- `-c, --account <string>` — AWS account ID or alias (not needed if you are only the administrator of one account)
- `-a, --app-name <string>` — app name (required)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation
- `--region <string>` — AWS region to use (defaults to the region of the account)

```
apppack access add <email>...
```

add access for users to the app

- `--region <string>` — AWS region of app

Example:

```bash
apppack -a my-app access add user1@example.com user2@example.com
```

```
apppack access remove <email>...
```

remove access for users to the app

- `--region <string>` — AWS region of app

Example:

```bash
apppack -a my-app access remove user1@example.com user2@example.com
```

### admins

list the administrators for an account

```
apppack admins
```

- `-c, --account <string>` — AWS account ID or alias (not needed if you are only the administrator of one account)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation

```
apppack admins add <email>...
```

add administrators to the account

Example:

```bash
apppack admins add user1@example.com user2@example.com
```

```
apppack admins remove <email>...
```

remove administrators from the account

Example:

```bash
apppack admins remove user1@example.com user2@example.com
```

### auth

authenticate with AppPack.io

```
apppack auth
```

```
apppack auth accounts
```

list the accounts you have administrator access to

```
apppack auth apps
```

list the apps you have access to

```
apppack auth login
```

login to AppPack.io on this device

- `--no-browser` — print the URL instead of opening a browser window

```
apppack auth logout
```

logout of AppPack.io on this device

```
apppack auth whoami
```

show login information for the current user

### aws-exec

run a local command with AWS credentials

```
apppack aws-exec -- <command>...
```

- `-a, --app-name <string>` — app name (required)

### build

work with AppPack builds

```
apppack build
```

- `-a, --app-name <string>` — app name (required)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation

```
apppack build list
```

list recent builds

```
apppack build start
```

start a new build from the latest commit on the branch defined in AppPack

- `--ref <string>` — git reference (branch, tag, or commit hash) to build
- `-w, --watch` — watch build process

```
apppack build status [<build-number>]
```

show the status of the most recent build

```
apppack build wait
```

wait is deprecated -- use `watch` instead

```
apppack build watch [<build-number>]
```

watch the progress of the most recent build

### completion

Generate the autocompletion script for the specified shell

```
apppack completion
```

```
apppack completion bash
```

Generate the autocompletion script for bash

- `--no-descriptions` — disable completion descriptions

```
apppack completion fish [flags]
```

Generate the autocompletion script for fish

- `--no-descriptions` — disable completion descriptions

```
apppack completion powershell [flags]
```

Generate the autocompletion script for powershell

- `--no-descriptions` — disable completion descriptions

```
apppack completion zsh [flags]
```

Generate the autocompletion script for zsh

- `--no-descriptions` — disable completion descriptions

### config

manage app configuration (environment variables/secrets)

```
apppack config
```

- `-a, --app-name <string>` — app name (required)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation

```
apppack config export
```

export the config variables to JSON

- `--all` — include AppPack managed variables (e.g. DATABASE_URL)

```
apppack config get <variable>
```

show the value of a single config variable

```
apppack config import <file>
```

import config variables from a JSON file

- `--overwrite` — overwrite variables if they already exist

```
apppack config list
```

list all config variables and values

```
apppack config set <variable>=<value>
```

set the value of a single config variable

Example:

```bash
apppack -a my-app config set ENVIRONMENT=production
```

```
apppack config unset <variable>
```

remove a config variable

### create

create AppPack resources in your AWS account

```
apppack create
```

- `-c, --account <string>` — AWS account ID or alias (not needed if you are only the administrator of one account)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation
- `--check` — check stack in Cloudformation before creating
- `--non-interactive` — do not prompt for missing flags
- `--region <string>` — AWS region to create resources in

```
apppack create app <name>
```

create an AppPack application

- `--cluster <string>` — Cluster name (default "apppack")
- `--ec2` — run on EC2 instances (requires EC2 enabled cluster)
- `-r, --repository <string>` — repository URL, e.g. https://github.com/apppackio/apppack-demo-python.git
- `-b, --branch <string>` — branch to setup for continuous deployment
- `-d, --domain <string>` — custom domain to route to app (optional)
- `--healthcheck-path <string>` — path which will return a 200 status code for healthchecks (default "/")
- `--addon-private-s3` — setup private S3 bucket add-on
- `--addon-public-s3` — setup public S3 bucket add-on
- `--addon-database-name <string>` — database instance name to install add-on (implies --addon-database)
- `--addon-redis-name <string>` — Redis instance name to install add-on (implies --addon-redis)
- `--addon-sqs` — setup SQS Queue add-on
- `--addon-ses` — setup SES (Email) add-on (requires manual approval of domain at SES)
- `--addon-ses-domain <string>` — domain approved for sending via SES add-on. Use '*' for all domains. (default "*")
- `-u, --users <strings>` — email addresses for users who can manage the app (comma separated)
- `--disable-build-webhook` — disable creation of a webhook on the repo to automatically trigger builds on push

```
apppack create cluster [<name>]
```

setup resources for an AppPack Cluster

- `--cidr <string>` — network CIDR for VPC (default "10.100.0.0/16")
- `--create-region` — also create the region stack if it does not exist
- `--domain <string>` — cluster domain name

```
apppack create custom-domain <domain-name>...
```

setup TLS certificate and point one or more domains to an AppPack Cluster

Example:

```bash
apppack create custom-domain example.com www.example.com
```

```
apppack create database [<name>]
```

setup resources for an AppPack Database

- `--allocated-storage <int>` — initial storage allocated in GB (does not apply to Aurora engines) (default 50)
- `--cluster <string>` — cluster name (default "apppack")
- `-e, --engine <string>` — engine -- one of mysql, postgres, aurora-mysql, aurora-postgresql (default "postgres")
- `-i, --instance-class <string>` — instance class -- see https://aws.amazon.com/rds/postgresql/pricing/?pg=pr&loc=3 (default "db.t4g.medium")
- `--max-allocated-storage <int>` — maximum storage allocated on-demand in GB (does not apply to Aurora engines) (default 500)
- `--multi-az` — enable multi-AZ -- see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html

```
apppack create pipeline <name>
```

create an AppPack pipeline

- `--cluster <string>` — Cluster name (default "apppack")
- `--ec2` — run on EC2 instances (requires EC2 enabled cluster)
- `-r, --repository <string>` — repository URL, e.g. https://github.com/apppackio/apppack-demo-python.git
- `--healthcheck-path <string>` — path which will return a 200 status code for healthchecks (default "/")
- `--addon-private-s3` — setup private S3 bucket add-on
- `--addon-public-s3` — setup public S3 bucket add-on
- `--addon-database-name <string>` — database instance name to install add-on (implies --addon-database)
- `--addon-redis-name <string>` — Redis instance name to install add-on (implies --addon-redis)
- `--addon-sqs` — setup SQS Queue add-on
- `--addon-ses` — setup SES (Email) add-on (requires manual approval of domain at SES)
- `--addon-ses-domain <string>` — domain approved for sending via SES add-on. Use '*' for all domains. (default "*")
- `-u, --users <strings>` — email addresses for users who can manage the app (comma separated)

```
apppack create redis [<name>]
```

setup resources for an AppPack Redis instance

- `--cluster <string>` — cluster name (default "apppack")
- `--instance-class <string>` — instance class -- see https://aws.amazon.com/elasticache/pricing/#On-Demand_Nodes (default "cache.t4g.micro")
- `--multi-az` — enable multi-AZ -- see https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/AutoFailover.html

```
apppack create region
```

setup AppPack resources for an AWS region

### dash

app metrics dashboard

```
apppack dash
```

- `-a, --app-name <string>` — app name (required)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation

### db

tools to manage your database on AppPack

```
apppack db
```

- `-a, --app-name <string>` — app name (required)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation

```
apppack db dump
```

dump the database to a local file

- `-o, --output <string>` — path to output file -- default will be <app-name> with the appropriate extension for the database

```
apppack db load <dumpfile>
```

load a dump file into the remote database

- `-j, --jobs <int>` — number of jobs to use for the load (passed through as --jobs to pg_restore -- Postgres only) (default 2)

```
apppack db shell
```

open an interactive shell prompt to the app database

### destroy

destroy AWS resources used by AppPack

```
apppack destroy
```

- `-c, --account <string>` — AWS account ID or alias (not needed if you are only the administrator of one account)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation
- `--region <string>` — AWS region to destroy resources in

```
apppack destroy account
```

destroy AWS resources used by your AppPack account

```
apppack destroy app <name>
```

destroy AWS resources used by the AppPack app

```
apppack destroy cluster <name>
```

destroy AWS resources used by the AppPack Cluster

```
apppack destroy custom-domain <domain>
```

destroy AWS resources used by the custom domain

```
apppack destroy database <name>
```

destroy AWS resources used by an AppPack Database

```
apppack destroy pipeline <name>
```

destroy AWS resources used by the AppPack pipeline

```
apppack destroy redis <name>
```

destroy AWS resources used by an AppPack Redis instance

```
apppack destroy region
```

destroy AWS resources used by an AppPack region

### events

show recent events for the given service

```
apppack events <service> [flags]
```

- `-a, --app-name <string>` — app name (required)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation
- `-w, --wait-for-steady` — wait for service to reach a steady state

Example:

```bash
apppack -a my-app events web
```

### logs

access application logs from Cloudwatch Logs

```
apppack logs
```

- `-a, --app-name <string>` — app name (required)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation
- `--expand` — indent JSON log messages
- `--filter <string>` — event filter pattern
- `-f, --follow` — Stream logs to console
- `--invert` — invert colors for light terminal themes
- `--prefix <string>` — log group prefix filter
- `--raw` — no timestamp, log group or colors
- `--rawString` — print JSON strings without escaping
- `--start <string>` — start getting the logs from this point
- `--stop <string>` — stop getting the logs at this point

```
apppack logs open
```

open logs in the AWS web console

### modify

modify AppPack resources

```
apppack modify
```

```
apppack modify app <name>
```

modify an AppPack application

- `-c, --account <string>` — AWS account ID or alias (not needed if you are only the administrator of one account)
- `-b, --branch <string>` — branch name
- `-d, --domains <strings>` — custom domains (comma-separated)
- `--healthcheck-path <string>` — healthcheck path
- `-r, --repository <string>` — repository URL

Example:

```bash
# Interactive mode - prompts for all modifiable parameters
  apppack modify app my-app

  # Update specific parameters with flags
  apppack modify app my-app --branch develop
  apppack modify app my-app --repository https://github.com/org/new-repo.git --branch main
  apppack modify app my-app --domains example.com,www.example.com
```

### open

open the app in a browser

```
apppack open [flags]
```

- `-a, --app-name <string>` — app name (required)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation

### ps

show running processes

```
apppack ps
```

- `-a, --app-name <string>` — app name (required)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation

```
apppack ps exec -- <command>
```

run an interactive command in the remote environment

- `--cpu <float>` — CPU cores available for task (default 0.5)
- `-l, --live` — connect to a live process
- `--memory <string>` — memory (e.g. '2G', '512M') available for task (default "1G")
- `-r, --root` — open shell as root user

```
apppack ps resize <process_type>
```

resize (CPU/memory) the process for a given type

- `--cpu <float>` — CPU cores available for process (default 0.5)
- `--memory <string>` — memory (e.g. '2G', '512M') available for process (default "1G")

Example:

```bash
apppack -a my-app ps resize web --cpu 2 --memory 4G
```

```
apppack ps restart <process_type>
```

restart the process for a given type

- `--force` — forcefully restart by killing running containers instead of a graceful rolling restart

Example:

```bash
apppack -a my-app ps restart web          # graceful rolling restart
apppack -a my-app ps restart web --force  # kill running containers (forced restart)
```

```
apppack ps scale <process_type> <process_count>
```

scale the number of processes that run for a specific process type

Example:

```bash
apppack -a my-app ps scale web 3  # run 3 web processes
apppack -a my-app ps scale worker 1-4  # autoscale worker service from 1 to 4 processes
```

### reviewapps

list deployed review apps

```
apppack reviewapps <pipeline>
```

- `--aws-credentials` — use AWS credentials instead of AppPack.io federation

```
apppack reviewapps create <pipeline:pr-number>
```

create a review app

- `--release <string>` — Specify a specific pre-release stack

```
apppack reviewapps destroy <pipeline:pr-number>
```

destroys the review app

### scheduled-tasks

list scheduled tasks

```
apppack scheduled-tasks
```

- `-a, --app-name <string>` — app name (required)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation

```
apppack scheduled-tasks create --schedule "<min> <hr> <day-mon> <mon> <day-wk> <yr>" "<command>"
```

schedule a task

- `-s, --schedule <string>` — cron-like schedule. See https://docs.aws.amazon.com/eventbridge/latest/userguide/scheduled-events.html#cron-expressions

Example:

```bash
apppack -a my-app scheduled-tasks create --schedule "0 0 * * ? *" "your-command --args"  # run daily at midnight UTC
apppack -a my-app scheduled-tasks create --schedule "0/10 * * * ? *" "your-command --args"  # run every 10 minutes
```

```
apppack scheduled-tasks delete [<index>]
```

delete an existing scheduled task

### shell

open an interactive shell in the remote environment

```
apppack shell
```

- `-a, --app-name <string>` — app name (required)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation
- `--cpu <float>` — CPU cores available for task (default 0.5)
- `-l, --live` — connect to a live process
- `--memory <string>` — memory (e.g. '2G', '512M') available for task (default "1G")
- `-r, --root` — open shell as root user

### stacks

list the stacks installed at AWS

```
apppack stacks
```

- `-c, --account <string>` — AWS account ID or alias (not needed if you are only the administrator of one account)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation

### upgrade

upgrade AppPack stacks

```
apppack upgrade
```

- `-c, --account <string>` — AWS account ID or alias (not needed if you are only the administrator of one account)
- `--aws-credentials` — use AWS credentials instead of AppPack.io federation
- `--check` — check stack in Cloudformation before creating
- `--region <string>` — AWS region to upgrade resources in

```
apppack upgrade account
```

upgrade your AppPack account stack

```
apppack upgrade app <name>
```

upgrade an application AppPack stack

```
apppack upgrade cluster <name>
```

upgrade a cluster AppPack stack

```
apppack upgrade database <name>
```

upgrade a database AppPack stack

```
apppack upgrade pipeline <name>
```

upgrade a pipeline AppPack stack

```
apppack upgrade redis <name>
```

upgrade a Redis AppPack stack

```
apppack upgrade region
```

upgrade your AppPack region stack

### version

show the version of the apppack command

```
apppack version
```

```
apppack version check
```

check if a newer version is available

```
apppack version update
```

update apppack to the latest version

- `-f, --force` — force update even if already on latest version
