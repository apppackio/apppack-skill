# AppPack skill for Claude Code

A [Claude Code](https://code.claude.com) skill that teaches Claude how to drive
[AppPack](https://apppack.io) — a PaaS that runs containerized apps on your own AWS account.

Claude loads it automatically when a conversation turns to AppPack apps, addons, clusters,
pipelines, review apps, or the `apppack` CLI.

## Install

```
/plugin marketplace add apppackio/apppack-skill
/plugin install apppack@apppack-skill
```

That's it — the skill is available in every session. Claude Code checks for updates in the
background; to pull them immediately:

```
/plugin marketplace update apppack-skill
```

### Without the marketplace

To run it from a local checkout — useful when developing the skill:

```bash
git clone https://github.com/apppackio/apppack-skill
claude --plugin-dir ./apppack-skill
```

## What it covers

Ask Claude to scale a process, wire up a database, chase a failing build, or explain what a
cluster actually is, and it answers from this skill rather than from half-remembered Heroku
habits.

**The whole command surface.** Every command and flag, rendered straight from the CLI's own
`apppack docgen` output. It describes the version that shipped, not whatever was true the last
time someone hand-edited a Markdown file.

**How an app is configured.** The `Procfile`, `apppack.toml` and `app.json` in your repo — what
each one controls, which wins when both exist, and which keys apply only to Dockerfile builds
versus buildpack builds. Plus the parts that live outside the repo: config in SSM Parameter
Store, app shape in CloudFormation stack parameters.

**The traps.** Places where AppPack does something other than what you'd guess: flags that look
global but are registered per command, a memory flag that rejects a bare number, a subcommand
that now exists only to tell you it was replaced. These are the mistakes that cost an afternoon,
and they're why the reference is generated rather than written by hand.

**Care around the sharp edges.** `destroy` is irreversible and admin-only, so Claude confirms the
target before running one, and secrets read out of `config` don't get echoed into your scrollback.

## Layout

```
.claude-plugin/
  plugin.json                     # plugin manifest
  marketplace.json                # self-hosted marketplace entry
skills/apppack/
  SKILL.md                        # curated; loaded when the skill triggers
  references/cli.md               # GENERATED; full command surface, loaded on demand
scripts/gen_cli_reference.py      # docgen output -> references/cli.md
Justfile                          # just cli-docs / check-cli-docs / validate
```

`SKILL.md` is deliberately short — concepts, the commands people actually run, and the gotchas.
The exhaustive flag-by-flag reference lives in `references/cli.md` so it costs nothing until
Claude needs it.

## Contributing

**`skills/apppack/references/cli.md` is generated — do not hand-edit it.** It is rendered from
`apppack docgen`, which is the CLI's own cobra command tree and therefore cannot drift. Regenerate
after a CLI change:

```bash
just cli-docs
```

CI runs `just check-cli-docs` on every PR and weekly against the latest CLI release; it fails if
the committed reference no longer matches, so a new flag can't ship undocumented.

Curated knowledge that docgen *cannot* know — version history, operational advice, why a default
is dangerous — belongs in `SKILL.md`, not in the generated file. Avoid restating generated facts
(flag lists, defaults) in `SKILL.md`: duplicated facts drift, which is the problem this setup
exists to prevent.

Before opening a PR:

```bash
just check    # validate manifests + CLI reference freshness
```

## Links

- [AppPack](https://apppack.io) · [docs](https://docs.apppack.io/) ·
  [CLI reference](https://docs.apppack.io/command-line-reference/)
- [Claude Code skills](https://code.claude.com/docs/en/skills) ·
  [plugins](https://code.claude.com/docs/en/plugins)
