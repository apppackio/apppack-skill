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
  SKILL.md                        # loaded when the skill triggers
  references/cli.md               # full command surface, loaded on demand
```

`SKILL.md` is deliberately short — it holds concepts, the commands people actually run, and the
gotchas. The exhaustive flag-by-flag reference lives in `references/cli.md` so it costs nothing
until Claude needs it.

## Contributing

The CLI is the source of truth. When a command changes, update `references/cli.md`, and
`SKILL.md` too if it's something a user hits often. `apppack docgen` (a hidden command) emits the
Markdown tree that powers <https://docs.apppack.io/command-line-reference/> and is the best way
to diff the real surface against these docs.

Validate manifests before opening a PR — CI runs the same check:

```bash
claude plugin validate .
```

## Links

- [AppPack](https://apppack.io) · [docs](https://docs.apppack.io/) ·
  [CLI reference](https://docs.apppack.io/command-line-reference/)
- [Claude Code skills](https://code.claude.com/docs/en/skills) ·
  [plugins](https://code.claude.com/docs/en/plugins)
