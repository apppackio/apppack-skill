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

- **Correct command signatures.** The reference is verified against the CLI source, including
  the places where the CLI surprises people: `ps resize` takes CPU *cores* and a memory suffix,
  `events` requires a service argument, `config export` emits JSON rather than shell exports,
  and `build wait` is a stub that always errors.
- **Which flags are actually global.** Only `--debug` and `--json` are. `--aws-credentials`,
  `-c/--account`, and `--region` are per-command, and `-a/--app-name` is required on eleven
  command groups with no environment-variable fallback.
- **Where state lives.** AppPack reads no `apppack.toml` or `Procfile`; config is in SSM and app
  shape is in CloudFormation stack parameters. The skill corrects the Heroku/Fly assumption.
- **Guardrails.** `destroy` is irreversible and admin-only; secrets from `config get` never get
  echoed into a transcript.

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
